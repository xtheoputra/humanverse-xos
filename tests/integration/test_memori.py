"""spec/07 3.6 · 3.7 — ekstraksi memori dari jurnal & mood, dan pencarian bersaring scope.

3.6 Selesai bila: *tiap memori punya `kind`, `scope`, `confidence`,
`evidence_count`, `source_event_id`.*
3.7 Selesai bila: *agent tanpa izin scope **tidak** menerima barisnya.*

Jalannya sungguhan dari ujung ke ujung: tulisan lewat HTTP → event (3.2) →
relay → stream → konsumen `memori` (3.3) → baris `memories` → penyelaras →
Qdrant (3.5) → `PencariMemori`. Tiap uji memakai koleksi Qdrant sekali pakai.
"""

from __future__ import annotations

import asyncio
import random
import string
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg.rows import dict_row

from hvx.modules import events, identity, memory, platform

pytestmark = pytest.mark.integration

PENYEMAT = platform.PenyematHash(b"k" * 32)
# spec/05 — `memory.read` coach-agent.
SCOPE_COACH = ["habits", "goals", "checkins", "mood", "coaching_notes"]
COACH = identity.Subjek("agent", "coach-agent")


@pytest.fixture
async def koleksi(url_qdrant_uji: str) -> AsyncIterator[tuple[platform.KlienVektor, str]]:
    klien = platform.KlienVektor(url_qdrant_uji)
    nama = f"uji-memori-{uuid.uuid4().hex[:12]}"
    try:
        yield klien, nama
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()


def _awalan() -> str:
    return f"uji-memori-{uuid.uuid4().hex[:10]}"


async def _ekstrak_semua(api: ApiUji, awalan: str) -> None:
    """Relay → stream → konsumen `memori`, sampai stream habis."""
    await events.Relay(api.engine_pekerja, api.app.state.redis, awalan).putaran()
    k = events.KonsumenStream(
        engine=api.engine_pekerja,
        redis=api.app.state.redis,
        awalan=awalan,
        grup="memori",
        nama="uji",
        jenis=memory.JENIS_EVENT,
        tangani=memory.ekstrak,
        blok_ms=50,
        jumlah=1000,
    )
    await k.siapkan()
    for _ in range(3):
        await k.putaran()


def _penyelaras(api: ApiUji, koleksi: tuple[platform.KlienVektor, str]) -> memory.PenyelarasVektor:
    return memory.PenyelarasVektor(api.engine_pekerja, koleksi[0], PENYEMAT, koleksi[1])


def _izin(api: ApiUji) -> identity.MesinIzin:
    s = api.app.state.settings
    return identity.MesinIzin(
        api.app.state.engine, api.app.state.redis, s.redis_prefix, s.permission_cache_ttl_s
    )


def _pencari(api: ApiUji, koleksi: tuple[platform.KlienVektor, str]) -> memory.PencariMemori:
    return memory.PencariMemori(api.app.state.engine, _izin(api), koleksi[0], PENYEMAT, koleksi[1])


def _memori_milik(api: ApiUji, uid: UUID) -> list[dict[str, Any]]:
    """Dibaca PEMILIK skema — bukan lewat kode yang diuji."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        return k.execute(
            """
            SELECT m.*, e.event_type AS jenis_sumber, e.subject_id AS subjek_sumber
            FROM memories m LEFT JOIN events e ON e.id = m.source_event_id
            WHERE m.user_id = %s ORDER BY m.valid_from
            """,
            (uid,),
        ).fetchall()


def _sql_pemilik(api: ApiUji, sql: str, *param: object) -> None:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        k.execute(sql, param)


def _event(api: ApiUji, kunci: str) -> events.EventMasuk:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        baris = k.execute(
            """
            SELECT id, user_id, event_type, schema_version, occurred_at, recorded_at, source,
                   subject_type, subject_id, payload
            FROM events WHERE idempotency_key = %s
            """,
            (kunci,),
        ).fetchone()
    assert baris is not None, f"event {kunci} tidak diterbitkan"
    return events.EventMasuk(**baris)


async def _post(api: ApiUji, token: str, jalur: str, isi: dict[str, Any]) -> dict[str, Any]:
    r = await api.klien.post(jalur, json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def _titik(url_qdrant: str, nama: str, id_: UUID) -> dict[str, Any] | None:
    """Titik Qdrant apa adanya — payload DAN vektornya."""
    async with httpx.AsyncClient(base_url=url_qdrant) as h:
        r = await h.post(
            f"/collections/{nama}/points",
            json={"ids": [str(id_)], "with_payload": True, "with_vector": True},
        )
    assert r.status_code == 200, r.text
    titik: list[dict[str, Any]] = r.json()["result"]
    return titik[0] if titik else None


def _kosinus(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


# ────────────────────────────────────────────────────────────── 3.6 ──


async def test_tiap_memori_punya_kind_scope_confidence_bukti_dan_event_sumber(
    api_bersama: ApiUji,
) -> None:
    """spec/07 3.6 Selesai bila — dua mood dan satu jurnal, tiga memori, lima medan."""
    uid, token = await api_bersama.pengguna_baru()
    m1 = await _post(api_bersama, token, "/v1/moods", {"valence": 2, "label": "cemas"})
    m2 = await _post(api_bersama, token, "/v1/moods", {"valence": 4, "note": "lega"})
    j = await _post(api_bersama, token, "/v1/journal", {"title": "Senin", "body": "Rapat lagi."})

    await _ekstrak_semua(api_bersama, _awalan())

    memori = _memori_milik(api_bersama, uid)
    assert len(memori) == 3, f"memori: {memori}"
    for m in memori:
        assert m["kind"] == "episodic"
        assert m["scope"] in {"mood", "journal_raw"}
        assert m["confidence"] == Decimal("1.000")
        assert m["evidence_count"] == 1
        assert m["source_event_id"] is not None, "memori tanpa event sumber"
    sumber = {(m["jenis_sumber"], m["subjek_sumber"], m["scope"]) for m in memori}
    assert sumber == {
        ("mood.logged", UUID(m1["id"]), "mood"),
        ("mood.logged", UUID(m2["id"]), "mood"),
        ("journal.created", UUID(j["id"]), "journal_raw"),
    }


async def test_isi_memori_dari_sumbernya_bukan_dari_event(api_bersama: ApiUji) -> None:
    """`note` mood dan isi jurnal tidak pernah masuk event (spec/03) — dibaca dari barisnya."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _post(
        api_bersama,
        token,
        "/v1/moods",
        {"valence": 2, "label": "cemas", "note": "capek sesudah rapat"},
    )
    await _post(api_bersama, token, "/v1/journal", {"title": "Selasa", "body": "Isi pribadi."})

    await _ekstrak_semua(api_bersama, _awalan())

    isi = {m["scope"]: m for m in _memori_milik(api_bersama, uid)}
    assert isi["mood"]["content"] == "Mood dilaporkan 2/5 (cemas): capek sesudah rapat"
    assert isi["mood"]["valid_from"].isoformat() == mood["occurred_at"].replace("Z", "+00:00")
    assert isi["journal_raw"]["content"] == "Selasa\n\nIsi pribadi."
    assert isi["mood"]["embedding_model"] is None, "ekstraksi menyemat sendiri — Qdrant di jalurnya"
    assert isi["mood"]["model_version"] == memory.VERSI_EKSTRAKSI, "cara memori lahir tak tercatat"


async def test_event_yang_diserahkan_lagi_tidak_menggandakan_memori(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mood = await _post(api_bersama, token, "/v1/moods", {"valence": 3})
    ev = _event(api_bersama, f"mood:{mood['id']}")

    for _ in range(2):
        async with platform.transaksi_pengguna(api_bersama.engine_pekerja, uid) as conn:
            await memory.ekstrak(conn, ev)

    assert len(_memori_milik(api_bersama, uid)) == 1, "memori ganda untuk satu event"


async def test_jurnal_yang_dihapus_sebelum_diekstrak_tidak_diingat(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "Tulisan yang disesali."})
    r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    assert r.status_code == 204

    await _ekstrak_semua(api_bersama, _awalan())

    assert _memori_milik(api_bersama, uid) == [], "jurnal terhapus tetap diingat"


async def test_sunting_jurnal_menunggu_ekstraksi_yang_sedang_membacanya(
    api_bersama: ApiUji,
) -> None:
    """Ekstraksi membaca isi lama; `PATCH` serentak mengganti isinya. Tanpa kunci BAGI,
    pendengar `PATCH` tidak melihat memori yang belum commit — lalu ekstraksi commit
    isi LAMA, dan kalimat yang sudah dihapus pemiliknya hidup terus di memori."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "kalimat yang akan dihapus"})
    ev = _event(api_bersama, f"journal:{j['id']}")

    async with platform.transaksi_pengguna(api_bersama.engine_pekerja, uid) as conn:
        await memory.ekstrak(conn, ev)
        sunting = asyncio.create_task(
            api_bersama.klien.patch(
                f"/v1/journal/{j['id']}", json={"body": "isi baru"}, headers=auth(token)
            )
        )
        await asyncio.sleep(0.5)
        assert not sunting.done(), "PATCH tidak menunggu ekstraksi yang sedang membaca jurnal"
    assert (await sunting).status_code == 200

    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "isi baru", f"memori memuat isi lama: {m['content']!r}"


async def test_waktu_jurnal_yang_dikoreksi_menggeser_memorinya(api_bersama: ApiUji) -> None:
    """`valid_from` memori = waktu KEJADIAN jurnalnya. Koreksi pemiliknya diikuti —
    sesudah diekstrak (pendengar), dan sebelumnya: ekstraksi membaca barisnya, bukan
    `occurred_at` event yang terbit saat jurnal ditulis (tinjauan penegak buta Sprint 3)."""
    uid, token = await api_bersama.pengguna_baru()
    awal = {"occurred_at": "2026-09-01T08:00:00Z"}
    koreksi = {"occurred_at": "2026-09-02T08:00:00Z"}
    sesudah = await _post(api_bersama, token, "/v1/journal", {"body": "sesudah", **awal})
    sebelum = await _post(api_bersama, token, "/v1/journal", {"body": "sebelum", **awal})
    r = await api_bersama.klien.patch(
        f"/v1/journal/{sebelum['id']}", json=koreksi, headers=auth(token)
    )
    assert r.status_code == 200, r.text
    await _ekstrak_semua(api_bersama, _awalan())
    r = await api_bersama.klien.patch(
        f"/v1/journal/{sesudah['id']}", json=koreksi, headers=auth(token)
    )
    assert r.status_code == 200, r.text

    waktu = {m["content"]: m["valid_from"] for m in _memori_milik(api_bersama, uid)}
    dikoreksi = datetime(2026, 9, 2, 8, tzinfo=UTC)
    assert waktu == {"sesudah": dikoreksi, "sebelum": dikoreksi}, (
        f"memori tidak mengikuti waktu yang dikoreksi pemiliknya: {waktu}"
    )


async def test_ubah_judul_saja_memori_mengikuti(api_bersama: ApiUji) -> None:
    """Judul bagian dari isi memori jurnal (`teks_jurnal`) — judul yang diganti pemiliknya
    tidak boleh tertinggal di memori (tinjauan penegak buta Sprint 3)."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"title": "Rahasia kantor", "body": "isi"})
    await _ekstrak_semua(api_bersama, _awalan())

    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"title": "Catatan"}, headers=auth(token)
    )

    assert r.status_code == 200, r.text
    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "Catatan\n\nisi", f"judul lama tetap di memori: {m['content']!r}"


async def test_hapus_jurnal_mengosongkan_ringkasan_memorinya(api_bersama: ApiUji) -> None:
    """`summary` turunan isinya — isi yang dicabut tidak boleh hidup di ringkasannya."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "rahasia untuk diringkas"})
    await _ekstrak_semua(api_bersama, _awalan())
    (m,) = _memori_milik(api_bersama, uid)
    # V0 belum menulis ringkasan (AI Gateway, Sprint 4) — ditulis langsung di sini.
    _sql_pemilik(
        api_bersama, "UPDATE memories SET summary = 'ringkasan: rahasia' WHERE id = %s", m["id"]
    )

    r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))

    assert r.status_code == 204
    (m,) = _memori_milik(api_bersama, uid)
    assert m["summary"] is None, "ringkasan isi jurnal yang dihapus tetap tersimpan"


# ─────────────────────────────────────── 3.5 penyelaras memories → Qdrant ──


async def test_penyelaras_menyemat_tanpa_isi_di_payload(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await _post(api_bersama, token, "/v1/moods", {"valence": 2, "note": "rahasia-kecil-xyz"})
    await _ekstrak_semua(api_bersama, _awalan())

    assert await _penyelaras(api_bersama, koleksi).putaran() >= 1

    (m,) = _memori_milik(api_bersama, uid)
    assert m["embedding_model"] == PENYEMAT.nama
    assert m["embedding_id"] == str(m["id"])
    assert m["model_version"] == memory.VERSI_EKSTRAKSI, "penyelaras menimpa model_version (K4)"
    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    assert titik is not None, "memori tersemat tanpa titik"
    assert titik["payload"] == {
        "user_id": str(uid),
        "scope": "mood",
        "kind": "episodic",
        "model": PENYEMAT.nama,
    }, "payload Qdrant memuat lebih dari rujukan"


async def test_jurnal_disunting_memori_dan_vektornya_mengikuti(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "bertengkar dengan atasan"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()

    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"body": "berdamai dengan atasan"}, headers=auth(token)
    )
    assert r.status_code == 200
    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "berdamai dengan atasan"
    assert m["embedding_model"] is None, "isi berubah, vektor lama dianggap masih cocok"
    await _penyelaras(api_bersama, koleksi).putaran()

    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    assert titik is not None
    assert _kosinus(titik["vector"], PENYEMAT.untuk(uid).semat("berdamai dengan atasan")) > 0.999, (
        "vektor isi lama tertinggal di Qdrant"
    )


async def test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    """Naskah (docs/139): *“tidak boleh hanya menghapus row di PostgreSQL”*."""
    uid, token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "journal_raw", "read", "allow")
    j = await _post(api_bersama, token, "/v1/journal", {"body": "rahasia yang dicabut"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()
    (m,) = _memori_milik(api_bersama, uid)
    assert await _titik(url_qdrant_uji, koleksi[1], m["id"]) is not None

    r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    assert r.status_code == 204

    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "", "isi jurnal terhapus tetap di memori sampai penyelaras lewat"
    assert m["deleted_at"] is not None
    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rahasia"
    )
    assert hasil.items == [], "memori terhapus diserahkan karena titiknya masih ada"

    await _penyelaras(api_bersama, koleksi).putaran()
    assert _memori_milik(api_bersama, uid) == []
    assert await _titik(url_qdrant_uji, koleksi[1], m["id"]) is None, "titik vektornya tertinggal"


async def test_akun_biasa_tidak_bisa_menyemat_kamus_untuk_vektor_orang_lain(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    """Tinjauan keamanan Sprint 3 (S1): dengan SATU kunci penyemat untuk semua pengguna,
    penyerang yang bisa membaca Qdrant (tanpa RLS — ancaman K-26) cukup membuat akun
    biasa, menulis kata-kata kamus sebagai jurnalnya sendiri, dan membandingkan vektor
    yang disemat server dengan vektor korban. Kunci tidak pernah ia sentuh."""
    korban, tk = await api_bersama.pengguna_baru()
    penyerang, tp = await api_bersama.pengguna_baru()
    for token in (tk, tp):  # "kamus" penyerang: teks korban persis
        await _post(api_bersama, token, "/v1/journal", {"body": "ingin berhenti"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()

    (mk,) = _memori_milik(api_bersama, korban)
    (mp,) = _memori_milik(api_bersama, penyerang)
    tk_ = await _titik(url_qdrant_uji, koleksi[1], mk["id"])
    tp_ = await _titik(url_qdrant_uji, koleksi[1], mp["id"])
    assert tk_ is not None
    assert tp_ is not None
    kemiripan = _kosinus(tk_["vector"], tp_["vector"])
    assert abs(kemiripan) < 0.3, (
        f"teks yang sama dari dua akun berkosinus {kemiripan:.3f} — akun biasa bisa "
        "menyemat kamus untuk membaca vektor pengguna lain"
    )


class _QdrantLambat:
    """Qdrant sungguhan yang `simpan`-nya lambat untuk SATU pengguna — penyelaras sedang
    menunggu Qdrant tepat ketika pemiliknya menyunting jurnal."""

    def __init__(self, klien: platform.KlienVektor, detik: float, user_id: UUID) -> None:
        self._k = klien
        self._detik = detik
        self._uid = str(user_id)
        self.menunggu = asyncio.Event()

    async def pastikan_koleksi(self, *a: Any, **k: Any) -> None:
        await self._k.pastikan_koleksi(*a, **k)

    async def hapus(self, *a: Any, **k: Any) -> None:
        await self._k.hapus(*a, **k)

    async def simpan(self, nama: str, titik: list[platform.Titik]) -> None:
        if any(t.payload.get("user_id") == self._uid for t in titik):
            self.menunggu.set()
            await asyncio.sleep(self._detik)
        await self._k.simpan(nama, titik)


async def test_sunting_jurnal_tidak_menunggu_qdrant_yang_lambat(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    """Tinjauan kontrak Sprint 3 (K3): penyelaras versi pertama memegang kunci baris
    memori selama memanggil Qdrant — `PATCH /journal` menunggu Qdrant, padahal Qdrant
    dijanjikan tidak pernah ada di jalan pengguna. Dan vektor isi LAMA tidak boleh
    ditandai cocok dengan isi yang disunting selama Qdrant ditunggu."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "isi pertama"})
    await _ekstrak_semua(api_bersama, _awalan())
    lambat = _QdrantLambat(koleksi[0], 2.0, uid)
    penyelaras = memory.PenyelarasVektor(
        api_bersama.engine_pekerja,
        lambat,  # type: ignore[arg-type]
        PENYEMAT,
        koleksi[1],
    )
    tugas = asyncio.create_task(penyelaras.putaran())
    await asyncio.wait_for(lambat.menunggu.wait(), timeout=15)

    loop = asyncio.get_running_loop()
    mulai = loop.time()
    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"body": "isi kedua"}, headers=auth(token)
    )
    lama = loop.time() - mulai
    await tugas

    assert r.status_code == 200, r.text
    assert lama < 1.0, f"PATCH /journal menunggu Qdrant {lama:.1f} dtk"
    await _penyelaras(api_bersama, koleksi).putaran()
    (m,) = _memori_milik(api_bersama, uid)
    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    assert titik is not None
    assert m["embedding_model"] == PENYEMAT.nama
    assert _kosinus(titik["vector"], PENYEMAT.untuk(uid).semat("isi kedua")) > 0.999, (
        "vektor isi LAMA ditandai cocok dengan isi yang disunting selama Qdrant ditunggu"
    )


def _tulisan_besar(benih: int) -> str:
    acak = random.Random(benih)  # noqa: S311 - teks uji, bukan rahasia
    kata = [
        "".join(acak.choice(string.ascii_lowercase) for _ in range(acak.randint(2, 9)))
        for _ in range(20_000)
    ]
    return " ".join(kata)[:100_000]


async def test_penyelaras_tidak_menahan_event_loop_pekerja(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Tinjauan keamanan Sprint 3 (S2): relay, konsumen, dan penyelaras berbagi SATU
    event loop. Jurnal 100 ribu karakter dari satu pengguna yang disemat di event loop
    menahan relay dan konsumen SEMUA pengguna selama itu."""
    _uid, token = await api_bersama.pengguna_baru()
    for i in range(8):
        await _post(api_bersama, token, "/v1/journal", {"body": _tulisan_besar(i)})
    await _ekstrak_semua(api_bersama, _awalan())
    loop = asyncio.get_running_loop()
    jeda_maks = 0.0
    selesai = asyncio.Event()

    async def detak() -> None:  # tugas lain di event loop pekerja: relay, konsumen
        nonlocal jeda_maks
        t = loop.time()
        while not selesai.is_set():
            await asyncio.sleep(0.01)
            s = loop.time()
            jeda_maks = max(jeda_maks, s - t)
            t = s

    tugas = asyncio.create_task(detak())
    await asyncio.sleep(0.05)
    await _penyelaras(api_bersama, koleksi).putaran()
    selesai.set()
    await tugas

    assert jeda_maks < 0.3, f"penyelaras menahan event loop pekerja {jeda_maks:.2f} dtk"


async def test_penyelaras_hanya_menyemat_awal_teks_panjang(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    """S2: biaya menyemat SATU memori berbatas — hanya `MAKS_TEKS_SEMAT` karakter pertama
    yang disemat; isinya tetap utuh di PostgreSQL."""
    uid, token = await api_bersama.pengguna_baru()
    isi = _tulisan_besar(99)
    await _post(api_bersama, token, "/v1/journal", {"body": isi})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()

    (m,) = _memori_milik(api_bersama, uid)
    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    awal = PENYEMAT.untuk(uid).semat(isi[: memory.MAKS_TEKS_SEMAT])
    assert titik is not None
    assert m["content"] == isi, "isi memori ikut terpotong"
    assert _kosinus(titik["vector"], awal) > 0.999, "teks yang disemat tidak dibatasi"


async def test_penyemat_lain_disemat_ulang_bukan_dicampur(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Kunci penyemat diganti (K-26): vektor lama tidak sebanding dengan kueri baru."""
    uid, token = await api_bersama.pengguna_baru()
    await _post(api_bersama, token, "/v1/moods", {"valence": 3, "note": "jalan sore"})
    await _ekstrak_semua(api_bersama, _awalan())
    lain = platform.PenyematHash(b"z" * 32)
    await memory.PenyelarasVektor(
        api_bersama.engine_pekerja, koleksi[0], lain, koleksi[1]
    ).putaran()

    await _penyelaras(api_bersama, koleksi).putaran()

    (m,) = _memori_milik(api_bersama, uid)
    assert m["embedding_model"] == PENYEMAT.nama, "memori penyemat lama tidak disemat ulang"


# ────────────────────────────────────────────────────────────── 3.7 ──


async def _siapkan_pengguna(
    api: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> tuple[UUID, dict[str, UUID]]:
    """Satu mood dan satu jurnal yang sama-sama menyebut "rapat", sudah tersemat."""
    uid, token = await api.pengguna_baru()
    # C-32: mood sensitif — coach membacanya hanya dengan `allow` yang disimpan pengguna.
    await _izin(api).tetapkan(uid, COACH, "mood", "read", "allow")
    await _post(api, token, "/v1/moods", {"valence": 2, "note": "capek sesudah rapat"})
    await _post(api, token, "/v1/journal", {"body": "rapat itu membuatku ingin berhenti"})
    await _ekstrak_semua(api, _awalan())
    await _penyelaras(api, koleksi).putaran()
    return uid, {m["scope"]: m["id"] for m in _memori_milik(api, uid)}


async def test_agent_berizin_menemukan_memorinya_secara_semantik(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert [h.memori.id for h in hasil.items] == [ids["mood"]]
    assert hasil.items[0].skor > 0
    assert hasil.scope_dipakai == sorted(SCOPE_COACH)
    assert hasil.perlu_izin == []


async def test_agent_tanpa_izin_scope_tidak_menerima_barisnya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """spec/07 3.7 Selesai bila — tiga jalan "tanpa izin", satu bukti bahwa izinlah pembedanya."""
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    cari = _pencari(api_bersama, koleksi)
    izin = _izin(api_bersama)

    # 1 · scope sensitif di manifest, tanpa `allow` yang disimpan pengguna
    tanpa = await cari.cari(
        user_id=uid, agent="uji-agent", scope_manifest=["mood", "journal_raw"], kueri="rapat"
    )
    assert ids["journal_raw"] not in [h.memori.id for h in tanpa.items], (
        "journal_raw terbuka tanpa izin"
    )
    assert tanpa.perlu_izin == ["journal_raw", "mood"], (
        "scope sensitif (journal_raw · mood — C-32) terbuka tanpa allow tersimpan"
    )

    # 2 · pengguna MENOLAK scope yang ada di manifest coach
    await izin.tetapkan(uid, COACH, "mood", "read", "deny")
    ditolak = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )
    assert ditolak.items == [], "scope yang ditolak pengguna tetap diserahkan"
    assert "mood" not in ditolak.scope_dipakai
    assert "mood" not in ditolak.perlu_izin, (
        "scope yang DITOLAK dilaporkan perlu izin — ditanya lagi"
    )

    # 3 · scope yang tidak diminta manifest — izin pengguna tidak melebarkan manifest
    await izin.tetapkan(uid, COACH, "journal_raw", "read", "allow")
    di_luar = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )
    assert di_luar.items == [], "izin pengguna melebarkan manifest"

    # bukti: dengan manifest DAN izin, baris yang sama diserahkan
    diizinkan = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rapat"
    )
    assert [h.memori.id for h in diizinkan.items] == [ids["journal_raw"]]


async def test_kata_yang_dihapus_dari_jurnal_tidak_cocok_sebelum_penyelaras_lewat(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Tinjauan kontrak Sprint 3 (K2a): sesudah `PATCH /journal`, vektor LAMA tetap di
    Qdrant sampai penyelaras lewat — dan pencarian yang hanya memeriksa scope & hapus
    di barisnya masih mencocokkan kata yang sudah dihapus pemiliknya."""
    uid, token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "journal_raw", "read", "allow")
    j = await _post(api_bersama, token, "/v1/journal", {"body": "daftar belanja sayur dan buah"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()
    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"body": "rapat anggaran kuartal"}, headers=auth(token)
    )
    assert r.status_code == 200, r.text
    cari = _pencari(api_bersama, koleksi)

    lama = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="belanja sayur"
    )
    await _penyelaras(api_bersama, koleksi).putaran()
    baru = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rapat anggaran"
    )

    assert lama.items == [], (
        f"kata yang dihapus pemiliknya masih cocok: {[h.memori.content for h in lama.items]}"
    )
    assert len(baru.items) == 1


async def test_titik_memori_terhapus_tidak_menyingkirkan_hasil_yang_sah(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Tinjauan kontrak Sprint 3 (K2b): kandidat dari Qdrant diambil 3× `batas` sekali saja —
    titik memori yang sudah dihapus (penyelaras belum lewat) memakan jatah itu, dan hasil
    yang sah tidak pernah sampai ke pemanggil. Enam titik basi: lebih dari dua halaman —
    dan lebih dari `_MAKS_HALAMAN` halaman bila kandidat per hasil turun ke 1× (tinjauan
    penegak buta Sprint 3)."""
    uid, token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "journal_raw", "read", "allow")
    dihapus = [
        await _post(api_bersama, token, "/v1/journal", {"body": "rapat rapat rapat"})
        for _ in range(6)
    ]
    await _post(api_bersama, token, "/v1/journal", {"body": "rapat pagi ini"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()
    for j in dihapus:
        r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))
        assert r.status_code == 204
    (hidup,) = [m for m in _memori_milik(api_bersama, uid) if m["deleted_at"] is None]

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rapat", batas=1
    )

    assert [h.memori.id for h in hasil.items] == [hidup["id"]], (
        f"hasil sah tersingkir oleh titik memori terhapus: {hasil.items}"
    )


async def test_payload_qdrant_basi_tidak_meloloskan_scope(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Qdrant tidak punya RLS dan payload-nya bisa basi — barisnya yang memutuskan."""
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    _sql_pemilik(
        api_bersama, "UPDATE memories SET scope = 'journal_raw' WHERE id = %s", ids["mood"]
    )

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert hasil.items == [], "scope di payload Qdrant menang atas scope di baris"


async def test_pencarian_hanya_memori_pemiliknya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    a, ids_a = await _siapkan_pengguna(api_bersama, koleksi)
    b, ids_b = await _siapkan_pengguna(api_bersama, koleksi)

    hasil_b = await _pencari(api_bersama, koleksi).cari(
        user_id=b, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert [h.memori.id for h in hasil_b.items] == [ids_b["mood"]], "memori pengguna lain ikut"
    assert ids_a["mood"] not in [h.memori.id for h in hasil_b.items]
    assert a != b


async def test_memori_yang_masa_berlakunya_lewat_tidak_diserahkan(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    _sql_pemilik(
        api_bersama,
        "UPDATE memories SET valid_from = now() - interval '2 days', "
        "valid_until = now() - interval '1 day' WHERE id = %s",
        ids["mood"],
    )

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert hasil.items == [], "memori yang valid_until-nya lewat tetap diserahkan"


async def test_hasil_dibatasi_dan_terurut_dari_yang_paling_mirip(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "allow")  # C-32: mood sensitif
    for catatan in ("rapat pagi", "rapat siang panjang sekali", "rapat"):
        await _post(api_bersama, token, "/v1/moods", {"valence": 3, "note": catatan})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()
    cari = _pencari(api_bersama, koleksi)

    satu = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["mood"], kueri="rapat", batas=1
    )
    semua = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["mood"], kueri="rapat", batas=3
    )

    assert len(satu.items) == 1, f"batas 1, diserahkan {len(satu.items)}"
    skor = [h.skor for h in semua.items]
    assert len(skor) == 3
    assert skor == sorted(skor, reverse=True), f"tidak terurut dari yang paling mirip: {skor}"
    assert satu.items[0].memori.id == semua.items[0].memori.id


class _QdrantPerekam:
    """Mencatat saringan tiap pencarian — Qdrant sungguhan tidak memperlihatkannya."""

    def __init__(self) -> None:
        self.saringan: list[dict[str, list[str]]] = []

    async def cari(
        self, *_a: object, saring: dict[str, list[str]], **_k: object
    ) -> list[platform.HasilCari]:
        self.saringan.append(saring)
        return []


async def test_qdrant_hanya_ditanya_titik_penyemat_ini_di_scope_yang_diizinkan(
    api_bersama: ApiUji,
) -> None:
    """Saringan di Qdrant, bukan hanya di barisnya: titik penyemat lain (kunci diganti,
    K-26) yang menunggu disemat ulang tidak memakan halaman kandidat, dan scope yang
    belum diizinkan tidak ditanyakan sama sekali (tinjauan penegak buta Sprint 3)."""
    uid, _token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "allow")  # C-32: mood sensitif
    rekam = _QdrantPerekam()
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        rekam,  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["mood", "journal_raw"], kueri="rapat"
    )

    assert rekam.saringan == [{"scope": ["mood"], "model": [PENYEMAT.nama]}], (
        f"saringan Qdrant: {rekam.saringan}"
    )


class _QdrantTakBolehDitanya:
    async def cari(self, *_a: object, **_k: object) -> list[platform.HasilCari]:
        raise AssertionError("Qdrant ditanya padahal jawabannya sudah pasti kosong")


class _QdrantSkorNol:
    """Kandidat yang tidak mirip sama sekali — kosinus 0."""

    def __init__(self, ids: list[UUID]) -> None:
        self._ids = ids

    async def cari(self, *_a: object, **_k: object) -> list[platform.HasilCari]:
        return [platform.HasilCari(i, 0.0, {}) for i in self._ids]


async def test_kueri_tanpa_kata_tidak_menanyai_qdrant(api_bersama: ApiUji) -> None:
    """Vektor nol "berjarak" 0 ke SEMUA titik, dan Qdrant mengembalikan semuanya."""
    uid, _token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "allow")
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["mood"], kueri="... ?!"
    )

    assert hasil.items == []
    assert hasil.scope_dipakai == ["mood"]


async def test_kandidat_berskor_nol_bukan_kecocokan(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantSkorNol([ids["mood"]]),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )

    assert hasil.items == [], "kandidat berskor 0 diserahkan sebagai kecocokan"


async def test_tanpa_scope_diizinkan_qdrant_tidak_ditanya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="uji-agent", scope_manifest=["journal_raw"], kueri="apa saja"
    )

    assert hasil.items == []
    assert hasil.perlu_izin == ["journal_raw"]


@pytest.mark.parametrize(
    ("manifest", "kueri", "batas", "pesan"),
    [
        (["habit"], "rapat", 5, "daftar resmi"),  # salah ketik — bukan scope resmi
        (["mood"], "   ", 5, "kosong"),
        (["mood"], "rapat", 0, "batas"),
        (["mood"], "rapat", memory.MAKS_HASIL + 1, "batas"),
    ],
)
async def test_permintaan_yang_salah_bentuk_ditolak(
    api_bersama: ApiUji, manifest: list[str], kueri: str, batas: int, pesan: str
) -> None:
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    with pytest.raises(ValueError, match=pesan):
        await cari.cari(
            user_id=uuid.uuid4(),
            agent="coach-agent",
            scope_manifest=manifest,
            kueri=kueri,
            batas=batas,
        )
