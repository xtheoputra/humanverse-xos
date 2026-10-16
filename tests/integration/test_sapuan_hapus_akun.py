"""spec/07 6.5 (Stage B) — sapuan hapus akun, tahap 3–6 (spec/01 "Prosedur hapus akun").

6.5 Selesai bila: *titik Qdrant ikut terhapus; semua sesi pengguna dicabut seketika.*

Stage A (`test_hapus_akun.py`) menjadwalkan. Berkas ini membuktikan yang SUNGGUH menghapus —
proses pekerja, sebagai `hvx_pekerja`, atas akun yang tenggang 30 harinya habis:

* data di SEMUA tabel milik pengguna hilang — dan tabel baru yang lupa CASCADE ketahuan
  dari katalog, bukan dari sebuah akun contoh;
* titik Qdrant ikut terbuang, titik orang lain tidak;
* jejak audit tetap, tanpa id aslinya di kolom mana pun;
* gagal di tengah (Qdrant mati) tidak mengubah apa pun, dan diulang di putaran berikutnya;
* akun yang belum waktunya TIDAK disentuh — oleh sapuan maupun oleh fungsi basis datanya;
* restore tertutup sesudah tenggang, dan sapuan menahan restore selagi Qdrant dibersihkan.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from datetime import date, timedelta
from functools import partial
from typing import Any, cast
from uuid import UUID

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg import sql
from test_auth import SANDI, _daftar_badan, _email
from test_hapus_akun import _akun, _daftar

from hvx import pekerja
from hvx.modules import identity, memory, platform
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration

PENYEMAT = platform.PenyematHash(b"k" * 32)
# Tabel yang HARUS terisi di akun contoh sebelum dihapus — kalau tidak, "tidak ada baris
# tersisa" tidak membuktikan apa pun.
TABEL_WAJIB_TERISI = {
    "profiles",
    "consents",
    "events",
    "goals",
    "habits",
    "habit_completions",
    "daily_checkins",
    "mood_entries",
    "journal_entries",
    "activities",
    "memories",
    "ai_conversations",
}


@pytest.fixture
async def koleksi(url_qdrant_uji: str) -> AsyncIterator[tuple[platform.KlienVektor, str]]:
    klien = platform.KlienVektor(url_qdrant_uji)
    nama = f"uji-hapus-{uuid.uuid4().hex[:12]}"
    await klien.pastikan_koleksi(nama, PENYEMAT.dimensi, list(memory.INDEKS_PAYLOAD))
    try:
        yield klien, nama
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()


# ─────────────────────────────────────────────────────────────── bantuan ──


def _pemilik(api: ApiUji) -> psycopg.Connection[Any]:
    """Peran pemilik skema — membaca dan menyiapkan keadaan di luar kode yang diuji."""
    return psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True)


def _tandai_hapus(api: ApiUji, uid: UUID | str, detik: int) -> None:
    """`pending_deletion` dengan jadwal `detik` dari sekarang (negatif = sudah lewat)."""
    with _pemilik(api) as k:
        k.execute(
            "UPDATE users SET status = 'pending_deletion', "
            "deletion_scheduled_at = now() + make_interval(secs => %s) WHERE id = %s",
            (detik, uid),
        )


def _ada_akun(api: ApiUji, uid: UUID | str) -> bool:
    with _pemilik(api) as k:
        return k.execute("SELECT 1 FROM users WHERE id = %s", (uid,)).fetchone() is not None


def _tabel_pengguna(api: ApiUji) -> list[str]:
    """Tiap tabel V0 ber-kolom `user_id` — dibaca dari katalog, bukan daftar tulisan tangan."""
    with _pemilik(api) as k:
        baris = k.execute(
            """
            SELECT c.relname FROM pg_class c
            JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'user_id'
                                AND NOT a.attisdropped
            WHERE c.relnamespace = 'public'::regnamespace AND c.relkind = 'r'
              AND c.relname <> 'audit_logs'
            ORDER BY c.relname
            """
        ).fetchall()
    return [b[0] for b in baris]


def _jumlah(api: ApiUji, tabel: str, uid: UUID | str) -> int:
    with _pemilik(api) as k:
        (n,) = k.execute(
            sql.SQL("SELECT count(*) FROM {} WHERE user_id = %s").format(sql.Identifier(tabel)),
            (uid,),
        ).fetchone() or (0,)
    return int(n)


def _jumlah_audit(api: ApiUji, uid: UUID | str, aksi: str | None = None) -> int:
    with _pemilik(api) as k:
        (n,) = k.execute(
            "SELECT count(*) FROM audit_logs "
            "WHERE user_id = %s AND (%s::text IS NULL OR action = %s)",
            (uid, aksi, aksi),
        ).fetchone() or (0,)
    return int(n)


def _sisip_memori(api: ApiUji, uid: UUID | str, *, tersemat: bool) -> UUID:
    """Baris memori; `tersemat` = sudah punya titik Qdrant (embedding_id terisi)."""
    with _pemilik(api) as k:
        (mid,) = k.execute(
            """
            WITH n AS (SELECT gen_random_uuid() AS i)
            INSERT INTO memories (id, user_id, kind, scope, content, embedding_id, embedding_model)
            SELECT i, %s, 'episodic', 'mood', 'catatan uji', CASE WHEN %s THEN i::text END,
                   CASE WHEN %s THEN %s END
            FROM n RETURNING id
            """,
            (uid, tersemat, tersemat, PENYEMAT.nama),
        ).fetchone() or (None,)
    assert isinstance(mid, UUID)
    return mid


async def _simpan_titik(
    koleksi: tuple[platform.KlienVektor, str], uid: UUID | str, memori_id: UUID
) -> None:
    klien, nama = koleksi
    vektor = PENYEMAT.untuk(UUID(str(uid))).semat("catatan uji")
    await klien.simpan(
        nama,
        [platform.Titik(memori_id, vektor, {"user_id": str(uid), "scope": "mood", "kind": "x"})],
    )


async def _titik_ada(url_qdrant: str, nama: str, memori_id: UUID) -> bool:
    async with httpx.AsyncClient(base_url=url_qdrant) as h:
        r = await h.post(f"/collections/{nama}/points", json={"ids": [str(memori_id)]})
    assert r.status_code == 200, r.text
    return bool(r.json()["result"])


async def _isi_data(api: ApiUji, token: str) -> None:
    """Tulisan lewat HTTP ke banyak modul — event, goal, habit, check-in, jurnal, percakapan."""
    k = api.klien
    kemarin = (date.today() - timedelta(days=1)).isoformat()
    for jalur, isi in (
        ("/v1/moods", {"valence": 3}),
        ("/v1/journal", {"body": "hari yang cukup baik"}),
        ("/v1/goals", {"title": "Sehat"}),
        ("/v1/activities", {"kind": "workout", "occurred_at": "2026-01-01T06:00:00+00:00"}),
        ("/v1/conversations", {}),
    ):
        r = await k.post(jalur, json=isi, headers=auth(token))
        assert r.status_code == 201, (jalur, r.text)
    h = await k.post(
        "/v1/habits",
        json={"title": "Workout", "period": "day", "target_count": 1},
        headers=auth(token),
    )
    assert h.status_code == 201, h.text
    r = await k.post(
        f"/v1/habits/{h.json()['id']}/completions",
        json={"status": "done", "for_date": kemarin},
        headers=auth(token),
    )
    assert r.status_code in (200, 201), r.text
    r = await k.put(f"/v1/checkins/{kemarin}", json={"energy": 4}, headers=auth(token))
    assert r.status_code in (200, 201), r.text
    # Tulisan ber-Idempotency-Key meninggalkan rujukan + kuota di Redis (24 jam).
    r = await k.post(
        "/v1/goals",
        json={"title": "Dengan kunci"},
        headers={**auth(token), "Idempotency-Key": f"k-{uuid.uuid4().hex}"},
    )
    assert r.status_code == 201, r.text


def _settings(api: ApiUji) -> Settings:
    settings = api.app.state.settings
    assert isinstance(settings, Settings)
    return settings


async def _kunci_redis(api: ApiUji, uid: UUID | str) -> list[str]:
    """Kunci idempotensi Redis (rujukan + kuota) milik satu pengguna."""
    awalan = _settings(api).redis_prefix
    return sorted(
        [str(k) async for k in api.app.state.redis.scan_iter(match=f"{awalan}:idem*:{uid}*")]
    )


async def _sapu(api: ApiUji, buang_titik: identity.PenghapusTitik | None) -> int:
    awalan = _settings(api).redis_prefix
    return await identity.sapu_akun_jatuh_tempo(
        api.engine_pekerja,
        _settings(api),
        sesi=api.penyimpan_sesi(),
        buang_titik=buang_titik,
        sesudah=(partial(platform.lupakan_idempotensi, api.app.state.redis, awalan),),
    )


async def _tunggu(syarat: Any, pesan: str, detik: float = 20) -> None:
    for _ in range(int(detik / 0.1)):
        if syarat():
            return
        await asyncio.sleep(0.1)
    pytest.fail(pesan)


# ───────────────────────────────────────────────────────── dari ujung ke ujung ──


async def test_sapuan_menghapus_semua_jejak_akun_dan_hanya_akun_itu(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    api = api_bersama
    _, uid_s, token = await _daftar(api)
    _, lain_s, token_lain = await _daftar(api)
    uid, lain = UUID(uid_s), UUID(lain_s)
    for t in (token, token_lain):
        await _isi_data(api, t)
    memori = _sisip_memori(api, uid, tersemat=True)
    memori_lain = _sisip_memori(api, lain, tersemat=True)
    await _simpan_titik(koleksi, uid, memori)
    await _simpan_titik(koleksi, lain, memori_lain)

    tabel = _tabel_pengguna(api)
    terisi = {t for t in tabel if _jumlah(api, t, uid) > 0}
    assert terisi >= TABEL_WAJIB_TERISI, (
        f"akun contoh tidak mengisi {sorted(TABEL_WAJIB_TERISI - terisi)} — uji tak membuktikan"
    )
    milik_lain = {t: _jumlah(api, t, lain) for t in tabel}
    audit_lain = _jumlah_audit(api, lain)
    semu = identity.id_semu(_settings(api), uid)

    # Tahap 1 lewat HTTP, lalu login selama tenggang (untuk membatalkan) → sesi BARU.
    email = _email_akun(api, uid)
    r = await api.klien.request("DELETE", "/v1/me", json={"password": SANDI}, headers=auth(token))
    assert r.status_code == 202, r.text
    masuk = await api.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    assert masuk.status_code == 200, masuk.text
    token_tenggang = masuk.json()["tokens"]["access_token"]
    assert (await api.klien.get("/v1/me", headers=auth(token_tenggang))).status_code == 200
    _tandai_hapus(api, uid, -60)
    audit_sebelum = _jumlah_audit(api, uid)  # termasuk jejak tahap 1 dan login tenggang
    kunci_lain = await _kunci_redis(api, lain)
    assert await _kunci_redis(api, uid), (
        "kontrol: tulisan ber-Idempotency-Key tak meninggalkan jejak"
    )
    assert kunci_lain, "kontrol: akun lain tak punya jejak idempotensi"
    assert audit_sebelum >= 4, "kontrol: akun contoh hampir tanpa jejak audit"
    with _pemilik(api) as k:
        (berjaringan,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE user_id = %s AND ip_hash IS NOT NULL", (uid,)
        ).fetchone() or (0,)
    assert berjaringan >= 1, "kontrol: tak satu jejak audit pun membawa ip_hash — uji C-34 buta"

    terhapus = await _sapu(api, partial(memory.buang_titik_pengguna, *koleksi))

    assert terhapus >= 1
    assert not _ada_akun(api, uid), "tahap 3: akun tidak dihapus"
    assert _ada_akun(api, lain), "akun orang lain ikut terhapus"
    sisa = {t: _jumlah(api, t, uid) for t in tabel if _jumlah(api, t, uid)}
    assert not sisa, f"data tertinggal sesudah akun dihapus (CASCADE): {sisa}"
    assert {t: _jumlah(api, t, lain) for t in tabel} == milik_lain, "data orang lain ikut berubah"
    # Tahap 4 — Qdrant tidak ikut CASCADE.
    assert not await _titik_ada(url_qdrant_uji, koleksi[1], memori), "titik Qdrant tertinggal"
    assert await _titik_ada(url_qdrant_uji, koleksi[1], memori_lain), "titik orang lain terbuang"
    # Sesi yang lahir selama tenggang ikut tercabut — bukan hanya yang dicabut tahap 1.
    sesudah = await api.klien.get("/v1/me", headers=auth(token_tenggang))
    assert sesudah.status_code == 401, "sesi yang lahir selama tenggang tidak dicabut"
    # Tahap 5 · 6 — jejak tetap, id aslinya lenyap dari kolom mana pun.
    assert _jumlah_audit(api, uid) == 0, "baris audit masih menunjuk id akun yang dihapus"
    assert _jumlah_audit(api, semu, "account.deleted") == 1
    assert _jumlah_audit(api, semu) == audit_sebelum + 1, "baris audit hilang atau bertambah"
    assert _jumlah_audit(api, lain) == audit_lain, "jejak orang lain ikut berubah"
    with _pemilik(api) as k:
        (bocor,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE audit_logs::text LIKE %s", (f"%{uid}%",)
        ).fetchone() or (0,)
    assert bocor == 0, "id asli akun yang dihapus masih terbaca di audit_logs"
    # C-34 (K-46): jejak yang dipertahankan tidak lagi bisa dipertemukan lewat jaringan.
    with _pemilik(api) as k:
        (jaringan,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE user_id = %s AND ip_hash IS NOT NULL", (semu,)
        ).fetchone() or (0,)
    assert jaringan == 0, "ip_hash tertinggal di jejak audit akun yang dihapus (C-34)"

    # Jejak idempotensi di Redis (rujukan + kuota) menunjuk pemiliknya 24 jam — ikut dibuang.
    assert await _kunci_redis(api, uid) == [], "jejak idempotensi akun yang dihapus tertinggal"
    assert await _kunci_redis(api, lain) == kunci_lain, "jejak idempotensi orang lain ikut terbuang"

    # Putaran kedua tidak menggandakan apa pun.
    await _sapu(api, partial(memory.buang_titik_pengguna, *koleksi))
    assert _jumlah_audit(api, semu, "account.deleted") == 1


def _email_akun(api: ApiUji, uid: UUID) -> str:
    with _pemilik(api) as k:
        (email,) = k.execute("SELECT email::text FROM users WHERE id = %s", (uid,)).fetchone() or (
            "",
        )
    assert email
    return str(email)


def test_tiap_tabel_milik_pengguna_ikut_terhapus_bersama_akunnya(api_bersama: ApiUji) -> None:
    """Penegak: tabel BARU ber-`user_id` yang lupa `ON DELETE CASCADE` merah di sini — bukan
    diam-diam menyisakan data orang yang sudah minta dihapus (tidak menunggu akun contoh
    yang kebetulan mengisinya). `audit_logs` satu-satunya pengecualian, dan sengaja:
    ia dianonimkan, bukan dihapus (spec/01 §8, C-9)."""
    with _pemilik(api_bersama) as k:
        tanpa_cascade = k.execute(
            """
            SELECT c.relname FROM pg_class c
            JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'user_id'
                                AND NOT a.attisdropped
            WHERE c.relnamespace = 'public'::regnamespace AND c.relkind = 'r'
              AND c.relname <> 'audit_logs'
              AND NOT EXISTS (
                SELECT 1 FROM pg_constraint f
                WHERE f.conrelid = c.oid AND f.contype = 'f'
                  AND f.confrelid = 'public.users'::regclass AND f.confdeltype = 'c'
                  AND f.conkey = ARRAY[a.attnum])
            ORDER BY c.relname
            """
        ).fetchall()
    assert not tanpa_cascade, (
        "tabel ber-user_id tanpa FK ke users(id) ON DELETE CASCADE — sapuan hapus akun akan "
        f"gagal atau menyisakan datanya: {[t[0] for t in tanpa_cascade]}"
    )


# ───────────────────────────────────────────────────────────── yang tidak disentuh ──


async def test_akun_aktif_dan_yang_belum_jatuh_tempo_tidak_disentuh(
    api_bersama: ApiUji,
) -> None:
    api = api_bersama
    aktif, _ = await api.pengguna_baru()
    belum, _ = await api.pengguna_baru()
    waktunya, _ = await api.pengguna_baru()
    _tandai_hapus(api, belum, 3600)
    _tandai_hapus(api, waktunya, -60)
    dipanggil: list[UUID] = []

    async def buang(user_id: UUID) -> None:
        dipanggil.append(user_id)

    await _sapu(api, buang)

    assert waktunya in dipanggil, "kontrol: sapuan tidak menyentuh akun yang jatuh tempo"
    assert not _ada_akun(api, waktunya), "kontrol: akun jatuh tempo tidak terhapus"
    assert aktif not in dipanggil, "titik akun aktif dibuang"
    assert _ada_akun(api, aktif), "akun aktif disapu"
    assert belum not in dipanggil, "titik akun dalam tenggang dibuang"
    assert _ada_akun(api, belum), "akun dalam tenggang disapu"


async def test_fungsi_basis_data_menolak_akun_yang_belum_jatuh_tempo(api_bersama: ApiUji) -> None:
    """Pekerja yang dibajak tidak boleh menghapus akun aktif lewat fungsi sapuan — dan
    penolakan itu ditegakkan basis data, bukan kode sapuan."""
    api = api_bersama
    aktif, _ = await api.pengguna_baru()
    belum, _ = await api.pengguna_baru()
    waktunya, _ = await api.pengguna_baru()
    _tandai_hapus(api, belum, 3600)
    _tandai_hapus(api, waktunya, -60)

    with psycopg.connect(psycopg_dsn(api.db.dsn_pekerja), autocommit=True) as k:
        for uid in (aktif, belum):
            terkunci = k.execute("SELECT kunci_akun_jatuh_tempo(%s)", (uid,)).fetchone()
            assert terkunci == (False,), "fungsi kunci menahan akun yang belum jatuh tempo"
            terhapus = k.execute(
                "SELECT hapus_akun_jatuh_tempo(%s, %s)", (uid, uuid.uuid4())
            ).fetchone()
            assert terhapus == (False,), "fungsi hapus menghapus akun yang belum jatuh tempo"
        assert k.execute("SELECT user_id FROM akun_jatuh_tempo(100)").fetchall()
        daftar = {b[0] for b in k.execute("SELECT user_id FROM akun_jatuh_tempo(100)").fetchall()}
        assert waktunya in daftar
        assert aktif not in daftar
        assert belum not in daftar
        # Id semu = id akun akan membuat anonimisasi tak berarti: ditolak SEBELUM menyentuh apa pun.
        with pytest.raises(psycopg.errors.RaiseException):
            k.execute("SELECT hapus_akun_jatuh_tempo(%s, %s)", (waktunya, waktunya))
    assert all(_ada_akun(api, u) for u in (aktif, belum, waktunya))


# ─────────────────────────────────────────────────────── gagal di tengah, diulang ──


async def test_qdrant_gagal_tidak_mengubah_apa_pun_dan_putaran_berikutnya_menyelesaikan(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    api = api_bersama
    _, uid_s, token = await _daftar(api)
    uid = UUID(uid_s)
    await _isi_data(api, token)
    _sisip_memori(api, uid, tersemat=True)
    _tandai_hapus(api, uid, -60)
    semu = identity.id_semu(_settings(api), uid)
    audit_sebelum = _jumlah_audit(api, uid)
    memori_sebelum = _jumlah(api, "memories", uid)

    async def qdrant_mati(user_id: UUID) -> None:
        raise platform.GalatVektor("qdrant tidak terjangkau: ConnectError")

    await _sapu(api, qdrant_mati)

    assert _ada_akun(api, uid), "akun terhapus padahal tahap 4 gagal"
    assert _akun(api, uid_s)[0] == "pending_deletion"
    assert _jumlah(api, "memories", uid) == memori_sebelum
    assert _jumlah_audit(api, uid) == audit_sebelum, "audit dianonimkan padahal tahap 4 gagal"
    assert _jumlah_audit(api, semu) == 0, "baris audit akun semu muncul padahal akun masih ada"

    assert await _sapu(api, partial(memory.buang_titik_pengguna, *koleksi)) >= 1
    assert not _ada_akun(api, uid)
    assert _jumlah_audit(api, semu, "account.deleted") == 1


async def test_tanpa_qdrant_akun_bertitik_ditunda_dan_yang_tak_bertitik_dihapus(
    api_bersama: ApiUji,
) -> None:
    """Menghapus baris akun yang titiknya masih ada meninggalkan titik itu selamanya (user_id-nya
    sudah tiada, tak ada yang bisa mencarinya). Maka: ditunda, bukan dihapus."""
    api = api_bersama
    bertitik, _ = await api.pengguna_baru()
    polos, _ = await api.pengguna_baru()
    _sisip_memori(api, bertitik, tersemat=True)
    _sisip_memori(api, polos, tersemat=False)
    _tandai_hapus(api, bertitik, -60)
    _tandai_hapus(api, polos, -60)

    await _sapu(api, None)

    assert _ada_akun(api, bertitik), "akun bertitik dihapus tanpa membuang titiknya"
    assert not _ada_akun(api, polos), "akun tanpa titik tertahan oleh Qdrant yang tidak dipasang"


# ─────────────────────────────────────────────────────────────── restore & kunci ──


async def test_restore_hanya_selama_tenggang(api_bersama: ApiUji) -> None:
    api = api_bersama
    email, uid, token = await _daftar(api)
    email2, uid2, token2 = await _daftar(api)
    for t in (token, token2):
        r = await api.klien.request("DELETE", "/v1/me", json={"password": SANDI}, headers=auth(t))
        assert r.status_code == 202, r.text
    masuk = await api.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    masuk2 = await api.klien.post("/v1/auth/login", json={"email": email2, "password": SANDI})
    baru, baru2 = (m.json()["tokens"]["access_token"] for m in (masuk, masuk2))
    _tandai_hapus(api, uid, -1)  # tenggang habis; sapuan belum lewat

    habis = await api.klien.post("/v1/me/restore", headers=auth(baru))
    dalam = await api.klien.post("/v1/me/restore", headers=auth(baru2))

    assert habis.status_code == 409, f"restore sesudah tenggang diizinkan: {habis.text}"
    assert habis.json()["error"]["code"] == "deletion_grace_expired"
    assert _akun(api, uid)[0] == "pending_deletion", "restore sesudah tenggang membatalkan hapus"
    assert dalam.status_code == 200, dalam.text
    assert _akun(api, uid2)[0] == "active"


async def test_kunci_sapuan_menahan_restore_tetapi_tidak_penulis_anak(api_bersama: ApiUji) -> None:
    """Tahap 4 (Qdrant) berjalan selagi baris akunnya terkunci: restore yang menyelip menunggu,
    dan sapuan yang kalah balapan berhenti sebelum menyentuh Qdrant. Kunci `FOR NO KEY UPDATE`
    — penulis anak (yang mengambil `FOR KEY SHARE` lewat FK) tidak ikut tertahan."""
    api = api_bersama
    uid, _ = await api.pengguna_baru()
    _tandai_hapus(api, uid, -60)

    with (
        psycopg.connect(psycopg_dsn(api.db.dsn_pekerja)) as sapuan,
        psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as lain,
    ):
        assert sapuan.execute("SELECT kunci_akun_jatuh_tempo(%s)", (uid,)).fetchone() == (True,)
        lain.execute("SET lock_timeout = '300ms'")
        with pytest.raises(psycopg.errors.LockNotAvailable):
            lain.execute(
                "UPDATE users SET status = 'active', deletion_scheduled_at = NULL WHERE id = %s",
                (uid,),
            )
        # FK anak mengambil FOR KEY SHARE — tidak bentrok dengan FOR NO KEY UPDATE.
        try:
            lain.execute("SELECT 1 FROM users WHERE id = %s FOR KEY SHARE", (uid,))
        except psycopg.errors.LockNotAvailable:
            pytest.fail("kunci sapuan menahan penulis anak (FOR UPDATE, bukan FOR NO KEY UPDATE)")
        sapuan.commit()
        # Restore menang sesudah kunci dilepas: sapuan berikutnya melihat akun aktif.
        lain.execute("SET lock_timeout = 0")
        lain.execute(
            "UPDATE users SET status = 'active', deletion_scheduled_at = NULL WHERE id = %s",
            (uid,),
        )
    with psycopg.connect(psycopg_dsn(api.db.dsn_pekerja), autocommit=True) as k:
        terkunci = k.execute("SELECT kunci_akun_jatuh_tempo(%s)", (uid,)).fetchone()
        assert terkunci == (False,), "kunci menahan akun yang sudah dipulihkan"
        terhapus = k.execute(
            "SELECT hapus_akun_jatuh_tempo(%s, %s)", (uid, uuid.uuid4())
        ).fetchone()
        assert terhapus == (False,), "akun yang sudah dipulihkan dihapus juga"
    assert _ada_akun(api, uid)


async def test_akun_dipulihkan_di_antara_daftar_dan_kunci_tidak_menyentuh_qdrant(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Daftar akun jatuh tempo dibaca di transaksi lain dari kuncinya. Yang dipulihkan di
    antaranya wajib dilewati SEBELUM `buang_titik` — titik yang sudah terbuang tidak kembali."""
    from hvx.modules.identity import penghapusan, repository

    api = api_bersama
    uid, _ = await api.pengguna_baru()
    _tandai_hapus(api, uid, -60)
    asli = repository.akun_jatuh_tempo

    async def daftar_lalu_pulihkan(conn: Any, batas: int) -> Any:
        hasil = await asli(conn, batas)
        with _pemilik(api) as k:  # restore menang tepat sesudah daftar dibaca
            k.execute(
                "UPDATE users SET status = 'active', deletion_scheduled_at = NULL WHERE id = %s",
                (uid,),
            )
        return hasil

    monkeypatch.setattr(penghapusan.repository, "akun_jatuh_tempo", daftar_lalu_pulihkan)
    dipanggil: list[UUID] = []

    async def buang(user_id: UUID) -> None:
        dipanggil.append(user_id)

    await _sapu(api, buang)

    assert uid not in dipanggil, "titik Qdrant dibuang untuk akun yang sudah dipulihkan"
    assert _ada_akun(api, uid)


# ───────────────────────────────────────────────── yang bergantung pada tenggang ──


async def test_penyelaras_vektor_melewati_akun_yang_menunggu_dihapus(api_bersama: ApiUji) -> None:
    """Penyematan ulang selama tenggang bisa menulis titik baru DI ANTARA tahap 4 dan commit
    tahap 3 — titik yatim tanpa pemilik. Akun yang menunggu dihapus tidak diselaraskan."""
    api = api_bersama
    uid, _ = await api.pengguna_baru()
    _sisip_memori(api, uid, tersemat=False)

    def terdaftar() -> bool:
        with psycopg.connect(psycopg_dsn(api.db.dsn_pekerja), autocommit=True) as k:
            baris = k.execute("SELECT user_id FROM memori_perlu_diselaraskan('m', 1000)").fetchall()
        return uid in {b[0] for b in baris}

    assert terdaftar(), "kontrol: pekerjaan penyelarasan tidak terdaftar sama sekali"
    _tandai_hapus(api, uid, 3600)
    assert not terdaftar(), "akun yang menunggu dihapus masih diselaraskan ke Qdrant"
    with _pemilik(api) as k:
        k.execute(
            "UPDATE users SET status = 'active', deletion_scheduled_at = NULL WHERE id = %s", (uid,)
        )
    assert terdaftar(), "restore tidak mengembalikan pekerjaan penyelarasan"


async def test_agent_berhenti_melayani_akun_yang_menunggu_dihapus(api_bersama: ApiUji) -> None:
    api = api_bersama
    email, uid, token = await _daftar(api)
    r = await api.klien.post("/v1/conversations", json={}, headers=auth(token))
    assert r.status_code == 201, r.text
    percakapan = r.json()["id"]
    await api.klien.request("DELETE", "/v1/me", json={"password": SANDI}, headers=auth(token))
    masuk = await api.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    baru = masuk.json()["tokens"]["access_token"]

    kepala = {**auth(baru), "Idempotency-Key": f"k-{uuid.uuid4().hex}"}
    pesan = await api.klien.post(
        f"/v1/conversations/{percakapan}/messages", json={"content": "catat mood 3"}, headers=kepala
    )
    jawab = await api.klien.post(
        f"/v1/conversations/{percakapan}/confirmations",
        json={"token": "bukan-token-sungguhan", "decision": "allow_once"},
        headers={**auth(baru), "Idempotency-Key": f"k-{uuid.uuid4().hex}"},
    )

    assert pesan.status_code == 403, f"agent melayani akun yang menunggu dihapus: {pesan.text}"
    assert pesan.json()["error"]["code"] == "account_pending_deletion"
    assert jawab.status_code == 403, (
        f"agent menerima jawaban konfirmasi dari akun itu: {jawab.text}"
    )
    assert jawab.json()["error"]["code"] == "account_pending_deletion"
    # Membaca tetap boleh — akun ini masih milik penggunanya sampai sapuan lewat.
    assert (await api.klien.get("/v1/conversations", headers=auth(baru))).status_code == 200
    with _pemilik(api) as k:  # tidak ada mood yang tertulis oleh perintah yang ditolak
        assert k.execute(
            "SELECT count(*) FROM mood_entries WHERE user_id = %s", (uid,)
        ).fetchone() == (0,)

    pulih = await api.klien.post("/v1/me/restore", headers=auth(baru))
    assert pulih.status_code == 200
    lagi = await api.klien.post(
        f"/v1/conversations/{percakapan}/messages",
        json={"content": "catat mood 3"},
        headers={**auth(baru), "Idempotency-Key": f"k-{uuid.uuid4().hex}"},
    )
    assert lagi.status_code == 202, lagi.text


# ────────────────────────────────────────────────────────────── proses pekerja ──


async def test_proses_pekerja_menjalankan_sapuan_sendiri_lalu_berhenti_bersih(
    api_bersama: ApiUji, url_redis_uji: str, url_qdrant_uji: str
) -> None:
    """Titik rakit pekerja yang lupa menyalakan sapuan tidak terlihat di uji fungsinya —
    yang ini menjalankan `pekerja.jalankan`, seperti `test_pekerja.py`."""
    api = api_bersama
    koleksi_nama = f"uji-pekerja-hapus-{uuid.uuid4().hex[:10]}"
    settings = Settings(
        env="test",
        database_url=api.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=f"uji-{uuid.uuid4().hex[:12]}",
        qdrant_url=url_qdrant_uji,
        qdrant_koleksi=koleksi_nama,
        sematan_key="s" * 32,
    )
    dimensi = platform.penyemat_dari(settings).dimensi
    klien = platform.KlienVektor(url_qdrant_uji)
    await klien.pastikan_koleksi(koleksi_nama, dimensi, list(memory.INDEKS_PAYLOAD))
    uid, _ = await api.pengguna_baru()
    memori = _sisip_memori(api, uid, tersemat=True)
    await klien.simpan(
        koleksi_nama,
        [platform.Titik(memori, [0.1] * dimensi, {"user_id": str(uid), "scope": "mood"})],
    )
    redis = api.app.state.redis
    kunci_idem = (
        f"{settings.redis_prefix}:idem:{uid}:abc",
        f"{settings.redis_prefix}:idem-kuota:{uid}",
    )
    for kunci in kunci_idem:
        await redis.set(kunci, "x", ex=600)
    _tandai_hapus(api, uid, -60)
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))
    try:
        await _tunggu(
            lambda: not _ada_akun(api, uid), "pekerja tidak menjalankan sapuan hapus akun"
        )
        assert not await _titik_ada(url_qdrant_uji, koleksi_nama, memori), "titik tertinggal"
        # Pembersihan Redis menyusul commit akunnya — beri waktu sepersekian detik.
        for _ in range(100):
            sisa = [k for k in kunci_idem if await redis.exists(k)]
            if not sisa:
                break
            await asyncio.sleep(0.1)
        assert not sisa, f"pekerja tidak membersihkan jejak idempotensi: {sisa}"
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{koleksi_nama}")
        await klien.tutup()

    assert tugas.exception() is None


async def test_buang_titik_pada_koleksi_yang_belum_ada_bukan_galat(url_qdrant_uji: str) -> None:
    """Pekerja yang baru menyala belum membuat koleksinya; akun tanpa memori tak boleh tertahan."""
    klien = platform.KlienVektor(url_qdrant_uji)
    try:
        await memory.buang_titik_pengguna(klien, f"tidak-ada-{uuid.uuid4().hex[:10]}", uuid.uuid4())
    finally:
        await klien.tutup()


async def test_token_segar_lama_sesudah_akun_dihapus_tidak_menghidupkan_id_aslinya(
    api_bersama: ApiUji,
) -> None:
    """Tinjauan keamanan S5–6 (S4): token segar yang sudah diputar meninggalkan penanda `bekas`
    di Redis selama umur token segar (30 hari) — dan penanda itu menyimpan `user_id` ASLI.
    Sesudah akun dihapus, siapa pun yang memegang token lama itu (perangkat lama yang
    mengulang penyegaran, K-21; atau pencurinya) memicu jejak `session.refresh_reused` atas
    id asli + `ip_hash` peminta — tiap kali dikirim ulang. Itu persis yang dibuang sapuan:
    K-39 (*id asli tidak terbaca di kolom mana pun*) dan C-34 (*tanpa jejak jaringan*)."""
    api = api_bersama
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(_email()))
    assert r.status_code == 201, r.text
    uid = UUID(r.json()["user"]["id"])
    lama = r.json()["tokens"]["refresh_token"]
    r = await api.klien.post("/v1/auth/refresh", json={"refresh_token": lama})
    assert r.status_code == 200, r.text  # `lama` kini token BEKAS

    _tandai_hapus(api, uid, -60)
    assert await _sapu(api, None) >= 1
    assert not _ada_akun(api, uid), "kontrol: akun tidak terhapus"
    assert _jumlah_audit(api, uid) == 0, "kontrol: sapuan meninggalkan id asli"

    for _ in range(2):
        ulang = await api.klien.post("/v1/auth/refresh", json={"refresh_token": lama})
        assert ulang.status_code == 401, ulang.text
    with _pemilik(api) as k:
        (bocor,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE audit_logs::text LIKE %s", (f"%{uid}%",)
        ).fetchone() or (0,)
    assert bocor == 0, "token segar lama menulis id asli akun yang sudah dihapus ke audit_logs"


class _SesiTakTerjangkau:
    """Redis jatuh tepat sesudah commit sapuan — pencabutan sesi gagal (dicatat, tak dilempar)."""

    async def cabut_semua(self, user_id: UUID) -> int:
        raise RuntimeError("redis tidak terjangkau")


@pytest.mark.parametrize("pintu", ["refresh", "logout"])
async def test_sesi_yang_lolos_pencabutan_sapuan_tidak_menghidupkan_id_aslinya(
    api_bersama: ApiUji, pintu: str
) -> None:
    """Tinjauan keamanan S5–6 (S4, jalur kedua): pencabutan sesi sesudah commit sapuan boleh
    gagal — *“token yang tersisa … mati di penyegaran pertama”* (penghapusan.py). Penyegaran
    itu memang menolak, tetapi lebih dulu menulis `session.revoked` atas id ASLI akun yang
    sudah dihapus, lengkap dengan `ip_hash` peminta (K-39 · C-34); `logout` dengan token
    akses yang tersisa menulis `session.logged_out` yang sama."""
    api = api_bersama
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(_email()))
    assert r.status_code == 201, r.text
    uid = UUID(r.json()["user"]["id"])
    segar = r.json()["tokens"]["refresh_token"]
    akses = r.json()["tokens"]["access_token"]

    _tandai_hapus(api, uid, -60)
    terhapus = await identity.sapu_akun_jatuh_tempo(
        api.engine_pekerja,
        _settings(api),
        sesi=cast(identity.PenyimpanSesi, _SesiTakTerjangkau()),
        buang_titik=None,
    )
    assert terhapus >= 1
    assert not _ada_akun(api, uid), "kontrol: akun tidak terhapus"

    if pintu == "refresh":
        jawab = await api.klien.post("/v1/auth/refresh", json={"refresh_token": segar})
        assert jawab.status_code == 401, jawab.text
    else:
        jawab = await api.klien.post("/v1/auth/logout", headers=auth(akses))
        assert jawab.status_code in (204, 401), jawab.text
    with _pemilik(api) as k:
        (bocor,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE audit_logs::text LIKE %s", (f"%{uid}%",)
        ).fetchone() or (0,)
    assert bocor == 0, f"{pintu} sesi yang lolos sapuan menulis id asli akun yang dihapus"
