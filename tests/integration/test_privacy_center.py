"""spec/07 6.4 — Privacy Center: `summary`, izin per agent, ekspor, hapus (naskah 5 §26).

Bentuknya K-41 · K-42 · K-43. Yang diuji di sini — lawan PostgreSQL & Redis sungguhan, data
ditulis lewat HTTP seperti pengguna menulisnya, dan diperiksa PEMILIK skema:

* ringkasan menghitung SEMUA yang tersimpan, per kategori, tanpa isi;
* hapus satu kategori menghapus tiap tabelnya DAN turunannya (event, memori, rekomendasi,
  human state) — tidak satu baris pun milik kategori lain, dan tidak satu pun milik orang lain;
* ekspor sekali pakai, butuh sandi ulang dan sesi pemiliknya, memuat isi tanpa `password_hash`;
* izin per agent = keputusan yang BERLAKU di gerbang, dan perubahannya berlaku seketika.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, BasisDataV0, auth, psycopg_dsn
from asgi_lifespan import LifespanManager
from test_auth import SANDI, _daftar_badan, _email

from hvx.main import create_app
from hvx.modules import identity, intelligence
from hvx.modules.platform import Settings, buat_engine

pytestmark = pytest.mark.integration

LALU = (datetime.now(UTC) - timedelta(days=2)).replace(microsecond=0)
TANGGAL = (datetime.now(UTC) - timedelta(days=2)).date().isoformat()

# Tabel yang BOLEH berubah di luar kategori yang dihapus — turunannya (K-42), plus jejak
# `data.deleted` di `audit_logs`. Selain ini, tidak satu baris pun berubah.
TURUNAN: dict[str, set[str]] = {
    "goals": {"events", "memories", "recommendations", "recommendation_feedback"},
    "habits": {"events", "memories", "recommendations", "recommendation_feedback", "activities"},
    "checkins": {
        "events",
        "memories",
        "recommendations",
        "recommendation_feedback",
        "human_states",
    },
    "moods": {"events", "memories", "recommendations", "recommendation_feedback"},
    "journal": {"events", "memories"},
    "activities": set(),
    "memories": set(),
    "conversations": set(),
    "recommendations": set(),
    "history": {"memories", "activities"},
}


@pytest.fixture(scope="module")
async def api_privasi(v0_bersama: BasisDataV0, url_redis_uji: str) -> AsyncIterator[ApiUji]:
    """`api_bersama` + pendaftaran per IP dilonggarkan: uji ini mendaftar SUNGGUHAN (hash
    argon2 asli untuk sandi ulang) puluhan kali dari satu IP; batasnya diuji test_batas_laju."""
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=v0_bersama.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
            rate_limit_ip="100000/60",
            rate_limit_user="100000/60",
            rate_limit_auth_ip="100000/60",
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as k,
    ):
        engine_pekerja = buat_engine(v0_bersama.dsn_pekerja)
        try:
            yield ApiUji(
                app=app, klien=k, db=v0_bersama, awalan_redis=awalan, engine_pekerja=engine_pekerja
            )
        finally:
            await engine_pekerja.dispose()


async def _daftar(api: ApiUji) -> tuple[str, str]:
    """(user_id, access_token) dari registrasi sungguhan — sandi argon2 asli untuk sandi ulang."""
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(_email()))
    assert r.status_code == 201, r.text
    return r.json()["user"]["id"], r.json()["tokens"]["access_token"]


def _pemilik(api: ApiUji) -> psycopg.Connection[Any]:
    return psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True)


def _satu(api: ApiUji, sql: str, *param: object) -> Any:
    with _pemilik(api) as k:
        baris = k.execute(sql, param).fetchone()
    return baris[0] if baris else None


async def _isi_semuanya(api: ApiUji, uid: str, token: str) -> None:
    """Satu dari tiap jenis data V0 — lewat HTTP bila ada rutenya, PEMILIK skema bila tidak."""
    k, h = api.klien, auth(token)
    goal = (await k.post("/v1/goals", json={"title": "Sehat"}, headers=h)).json()
    r = await k.post(f"/v1/goals/{goal['id']}/milestones", json={"title": "5 km"}, headers=h)
    assert r.status_code == 201, r.text
    habit = (
        await k.post(
            "/v1/habits",
            json={"title": "Lari pagi", "period": "day", "target_count": 1, "goal_id": goal["id"]},
            headers=h,
        )
    ).json()
    r = await k.post(
        f"/v1/habits/{habit['id']}/completions",
        json={"for_date": TANGGAL, "status": "skipped", "note": "kambuh"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    r = await k.put(f"/v1/checkins/{TANGGAL}", json={"energy": 2, "focus": 3}, headers=h)
    assert r.status_code == 201, r.text
    r = await k.post(
        "/v1/moods",
        json={"valence": 2, "label": "cemas", "occurred_at": LALU.isoformat()},
        headers=h,
    )
    assert r.status_code == 201, r.text
    r = await k.post("/v1/journal", json={"body": "tulisan paling pribadi"}, headers=h)
    assert r.status_code == 201, r.text
    r = await k.post(
        "/v1/activities", json={"kind": "workout", "occurred_at": LALU.isoformat()}, headers=h
    )
    assert r.status_code == 201, r.text

    with _pemilik(api) as p:
        coach = p.execute(
            "SELECT id FROM agents WHERE name = 'coach-agent' AND status = 'active'"
        ).fetchone()[0]
        for kind, scope in (
            ("episodic", "journal_raw"),
            ("episodic", "mood"),
            ("behavioral", "habits"),
            ("semantic", "goals"),
            ("semantic", "checkins"),
            ("semantic", "coaching_notes"),
        ):
            p.execute(
                "INSERT INTO memories (user_id, kind, scope, content) VALUES (%s, %s, %s, %s)",
                (uid, kind, scope, f"ingatan {scope}"),
            )
        p.execute(
            "INSERT INTO human_states (user_id, for_date, metrics, model_version) "
            "VALUES (%s, %s, '{\"energy\": {\"value\": 0.25}}', 'v1')",
            (uid, TANGGAL),
        )
        for domain, subjek, konteks, agent in (
            ("habit", "habit", "{}", None),
            ("goal", "goal", "{}", None),
            ("wellbeing", None, '{"context": 0.25}', None),
            ("wellbeing", None, "{}", coach),
            ("wellbeing", None, "{}", None),
        ):
            rid = p.execute(
                "INSERT INTO recommendations (user_id, domain, subject_type, title, "
                "context_snapshot, agent_id) VALUES (%s, %s, %s, 'saran', %s::jsonb, %s) "
                "RETURNING id",
                (uid, domain, subjek, konteks, agent),
            ).fetchone()[0]
            p.execute(
                "INSERT INTO recommendation_feedback (recommendation_id, user_id, action) "
                "VALUES (%s, %s, 'accepted')",
                (rid, uid),
            )
        cid = p.execute(
            "INSERT INTO ai_conversations (user_id, title) VALUES (%s, 'obrolan') RETURNING id",
            (uid,),
        ).fetchone()[0]
        p.execute(
            "INSERT INTO ai_messages (conversation_id, user_id, role, content) "
            "VALUES (%s, %s, 'user', 'pesan pribadi')",
            (cid, uid),
        )
        p.execute(
            "INSERT INTO agent_runs (user_id, agent_id, agent_version, trigger, conversation_id) "
            "VALUES (%s, %s, '1.0.0', 'user', %s)",
            (uid, coach, cid),
        )


async def _ringkasan(api: ApiUji, token: str) -> dict[str, dict[str, Any]]:
    r = await api.klien.get("/v1/privacy/summary", headers=auth(token))
    assert r.status_code == 200, r.text
    return {k["key"]: k for k in r.json()["categories"]}


def _per_tabel(ringkas: dict[str, dict[str, Any]]) -> dict[str, int]:
    return {t: n for k in ringkas.values() for t, n in k["tables"].items()}


async def _hapus(api: ApiUji, token: str, kategori: str, sandi: str = SANDI) -> Any:
    return await api.klien.request(
        "DELETE", f"/v1/privacy/data/{kategori}", json={"password": sandi}, headers=auth(token)
    )


# ───────────────────────────────────────────────────────────── ringkasan ──


async def test_ringkasan_menghitung_semua_kategori_tanpa_isi(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    r = await api_privasi.klien.get("/v1/privacy/summary", headers=auth(token))
    assert r.status_code == 200, r.text
    isi = r.json()
    assert "tulisan paling pribadi" not in r.text, "ringkasan menumpahkan isi (spec/04)"
    kat = {k["key"]: k for k in isi["categories"]}
    assert list(kat) == list(identity.KATEGORI), "kategori layar tidak lengkap/berurutan"
    assert kat["journal"]["count"] == 1
    assert kat["goals"]["tables"] == {"goals": 1, "goal_milestones": 1}
    assert kat["habits"]["tables"] == {"habits": 1, "habit_completions": 1}
    assert kat["checkins"]["count"] == 1, "baris turunan terhitung sebagai catatan pengguna"
    assert kat["checkins"]["derived_count"] == 1, "human state turunan tidak terhitung"
    assert kat["memories"]["count"] == 6
    # goal · habit · penyelesaian · check-in · mood · jurnal (milestone & aktivitas tanpa event V0)
    assert kat["history"]["count"] == 6, "event tiap tulisan tidak terhitung"
    assert kat["account"]["tables"]["users"] == 1
    assert kat["account"]["tables"]["consents"] >= 2
    assert kat["journal"]["deletable"]
    assert not kat["account"]["deletable"], "kategori yang tak bisa dihapus tampil bisa dihapus"
    assert kat["audit"]["why_not_deletable"], "kategori yang tak bisa dihapus tanpa alasan"
    assert all(k["retention"] for k in isi["categories"]), "ada kategori tanpa masa simpan"
    assert {t["key"] for t in isi["not_collected"]} == {
        "location",
        "calendar",
        "finance",
        "wearable",
    }


async def test_ringkasan_hanya_milik_pengguna_itu(api_privasi: ApiUji) -> None:
    uid_a, token_a = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid_a, token_a)
    _uid_b, token_b = await _daftar(api_privasi)

    kat = await _ringkasan(api_privasi, token_b)
    assert kat["journal"]["count"] == 0, "ringkasan B menghitung baris milik A (H-27)"
    assert kat["memories"]["count"] == 0, "ringkasan B menghitung baris milik A (H-27)"


# ─────────────────────────────────────────────────────── hapus per kategori ──


@pytest.mark.parametrize("kategori", sorted(TURUNAN))
async def test_hapus_kategori_membuang_tabelnya_dan_turunannya_saja(
    api_privasi: ApiUji, kategori: str
) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)
    uid_lain, token_lain = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid_lain, token_lain)
    sebelum = await _ringkasan(api_privasi, token)
    sebelum_lain = await _ringkasan(api_privasi, token_lain)

    r = await _hapus(api_privasi, token, kategori)
    assert r.status_code == 202, r.text
    assert r.json()["category"] == kategori

    sesudah = await _ringkasan(api_privasi, token)
    sisa = sesudah[kategori]["count"] + sesudah[kategori]["derived_count"]
    assert sisa == 0, f"hapus `{kategori}` meninggalkan baris: {sesudah[kategori]['tables']}"
    tabel_kategori = set(sebelum[kategori]["tables"])
    lama, baru = _per_tabel(sebelum), _per_tabel(sesudah)
    for tabel, n in lama.items():
        if tabel in tabel_kategori:
            continue
        if tabel in TURUNAN[kategori]:
            assert baru[tabel] <= n
        elif tabel == "audit_logs":
            assert baru[tabel] == n + 1, "hapus kategori tanpa jejak `data.deleted`"
        else:
            assert baru[tabel] == n, f"hapus `{kategori}` menyentuh `{tabel}`: {n} → {baru[tabel]}"
    assert await _ringkasan(api_privasi, token_lain) == sebelum_lain, (
        f"hapus `{kategori}` milik A mengubah data B (H-27)"
    )
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action = 'data.deleted' "
            "AND subject_id = %s",
            uid,
            kategori,
        )
        == 1
    )


async def test_hapus_jurnal_membawa_event_dan_memorinya_bukan_milik_mood(
    api_privasi: ApiUji,
) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    r = await _hapus(api_privasi, token, "journal")
    assert r.status_code == 202, r.text

    assert _satu(api_privasi, "SELECT count(*) FROM journal_entries WHERE user_id = %s", uid) == 0
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM events WHERE user_id = %s AND event_type = 'journal.created'",
            uid,
        )
        == 0
    ), "event jurnal yang dihapus tetap di riwayat (naskah 11 §7.25)"
    with _pemilik(api_privasi) as p:
        hidup = dict(
            p.execute(
                "SELECT scope, count(*) FROM memories WHERE user_id = %s AND deleted_at IS NULL "
                "GROUP BY scope",
                (uid,),
            ).fetchall()
        )
    assert "journal_raw" not in hidup, "memori jurnal tetap hidup sesudah jurnalnya dihapus"
    assert hidup.get("mood") == 1, "hapus jurnal ikut melupakan memori mood"
    terlupa = _satu(
        api_privasi,
        "SELECT content FROM memories WHERE user_id = %s AND scope = 'journal_raw'",
        uid,
    )
    assert terlupa == "", "isi memori jurnal menunggu penyelaras — harus kosong SEKARANG"
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM events WHERE user_id = %s AND event_type = 'mood.logged'",
            uid,
        )
        == 1
    ), "hapus jurnal membuang event mood"


async def test_hapus_mood_membuang_rekomendasi_agent_bukan_milik_mesin(
    api_privasi: ApiUji,
) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    assert (await _hapus(api_privasi, token, "moods")).status_code == 202
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM recommendations WHERE user_id = %s AND agent_id IS NOT NULL",
            uid,
        )
        == 0
    ), "rekomendasi agent (yang mungkin mengutip mood) tetap tersimpan"
    assert _satu(api_privasi, "SELECT count(*) FROM recommendations WHERE user_id = %s", uid) == 4


async def test_hapus_percakapan_menyisakan_jejak_run_tanpa_tautan(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    assert (await _hapus(api_privasi, token, "conversations")).status_code == 202
    assert _satu(api_privasi, "SELECT count(*) FROM ai_messages WHERE user_id = %s", uid) == 0
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM agent_runs WHERE user_id = %s AND conversation_id IS NULL",
            uid,
        )
        == 1
    ), "jejak kerja asisten (audit AI, naskah 5 §24) ikut hilang atau masih menaut"


async def test_hapus_kategori_butuh_sandi_yang_benar(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    r = await _hapus(api_privasi, token, "journal", sandi="bukan-sandinya-sama-sekali")
    assert r.status_code == 403, r.text
    assert r.json()["error"]["code"] == "invalid_credentials"
    assert _satu(api_privasi, "SELECT count(*) FROM journal_entries WHERE user_id = %s", uid) == 1
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM audit_logs WHERE user_id = %s "
            "AND action = 'data.deletion_rejected'",
            uid,
        )
        == 1
    )
    tanpa_badan = await api_privasi.klien.request(
        "DELETE", "/v1/privacy/data/journal", headers=auth(token)
    )
    assert tanpa_badan.status_code == 400, tanpa_badan.text


@pytest.mark.parametrize(
    ("kategori", "status", "kode"),
    [
        ("account", 409, "category_not_deletable"),
        ("profile", 409, "category_not_deletable"),
        ("audit", 409, "category_not_deletable"),
        ("bukan_kategori", 404, "unknown_category"),
    ],
)
async def test_kategori_yang_tidak_bisa_dihapus_ditolak_sebelum_sandi(
    api_privasi: ApiUji, kategori: str, status: int, kode: str
) -> None:
    _uid, token = await _daftar(api_privasi)
    r = await _hapus(api_privasi, token, kategori, sandi="sandi-salah-pun-tak-ditebak")
    assert r.status_code == status, f"`{kategori}` menebak sandi sebelum ditolak: {r.text}"
    assert r.json()["error"]["code"] == kode


@pytest.fixture
async def api_jatah_kecil(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> AsyncIterator[ApiUji]:
    """Aplikasi utuh dengan jatah login gagal 3/hari — batasnya sendiri, bukan angkanya."""
    db = basis_data_termigrasi("privasi")
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=db.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
            rate_limit_login_failures="3/86400",
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as k,
    ):
        yield ApiUji(app=app, klien=k, db=db, awalan_redis=awalan, engine_pekerja=None)


@pytest.mark.parametrize("pintu", ["hapus-data", "ekspor", "hapus-akun"])
async def test_tebakan_sandi_ulang_berbagi_jatah_dengan_login_gagal(
    api_jatah_kecil: ApiUji, pintu: str
) -> None:
    """E-226: token akses curian tidak boleh menjadi jalan menebak sandi tanpa batas — di
    pintu mana pun yang meminta sandi ulang, dan jatahnya SAMA dengan login gagal."""
    api = api_jatah_kecil
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(email := _email()))
    token = r.json()["tokens"]["access_token"]

    async def coba(sandi: str) -> Any:
        if pintu == "hapus-data":
            return await _hapus(api, token, "journal", sandi=sandi)
        if pintu == "ekspor":
            return await _minta_ekspor(api, token, sandi=sandi)
        return await api.klien.request(
            "DELETE", "/v1/me", json={"password": sandi}, headers=auth(token)
        )

    salah = await api.klien.post("/v1/auth/login", json={"email": email, "password": "x" * 12})
    assert salah.status_code == 401
    for _ in range(2):
        assert (await coba("tebakan-yang-salah-terus")).status_code == 403
    r = await coba(SANDI)
    assert r.status_code == 429, f"tebakan ke-4 (login + sandi ulang) tidak dibatasi: {r.text}"
    assert "Retry-After" in r.headers


# ─────────────────────────────────────────────────────────────── ekspor ──


async def _minta_ekspor(api: ApiUji, token: str, sandi: str = SANDI) -> Any:
    return await api.klien.post("/v1/privacy/export", json={"password": sandi}, headers=auth(token))


async def test_ekspor_sekali_pakai_memuat_isi_tanpa_hash_sandi(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)

    r = await _minta_ekspor(api_privasi, token)
    assert r.status_code == 202, r.text
    eid = r.json()["export_id"]
    assert r.json()["status"] == "ready"
    assert r.json()["download_url"] == f"/v1/privacy/export/{eid}/download", (
        "jawaban POST `ready` tanpa jalur unduh — beda dengan GET untuk status yang sama"
    )

    st = await api_privasi.klien.get(f"/v1/privacy/export/{eid}", headers=auth(token))
    assert st.status_code == 200, st.text
    jalur = st.json()["download_url"]
    assert jalur == f"/v1/privacy/export/{eid}/download", "tautan unduh membawa rahasia di URL"

    tanpa_sesi = await api_privasi.klien.get(jalur)
    assert tanpa_sesi.status_code == 401
    u = await api_privasi.klien.get(jalur, headers=auth(token))
    assert u.status_code == 200, u.text
    assert "attachment" in u.headers["content-disposition"]
    assert u.headers.get("cache-control") == "no-store", "unduhan ekspor boleh disimpan cache"
    dok = u.json()
    assert (dok["format"], dok["format_version"]) == ("humanverse-export", 1)
    assert dok["user_id"] == uid
    assert "password_hash" not in u.text, "ekspor memuat hash sandi"
    (jurnal,) = dok["categories"]["journal"]["journal_entries"]
    assert jurnal["body"] == "tulisan paling pribadi", "ekspor tanpa isi bukan salinan (Art. 15)"
    assert set(dok["categories"]) == set(identity.KATEGORI)
    assert dok["categories"]["account"]["users"][0]["email"].endswith("@uji.id")

    kedua = await api_privasi.klien.get(jalur, headers=auth(token))
    assert kedua.status_code == 410, "tautan ekspor bisa dipakai dua kali"
    st = await api_privasi.klien.get(f"/v1/privacy/export/{eid}", headers=auth(token))
    assert (st.json()["status"], st.json()["download_url"]) == ("downloaded", None)
    for aksi in ("data.export_requested", "data.exported"):
        assert (
            _satu(
                api_privasi,
                "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action = %s",
                uid,
                aksi,
            )
            == 1
        ), f"ekspor tanpa jejak `{aksi}`"


async def test_ekspor_milik_a_tidak_terlihat_dan_tidak_terunduh_oleh_b(
    api_privasi: ApiUji,
) -> None:
    _uid_a, token_a = await _daftar(api_privasi)
    _uid_b, token_b = await _daftar(api_privasi)
    eid = (await _minta_ekspor(api_privasi, token_a)).json()["export_id"]

    for jalur in (f"/v1/privacy/export/{eid}", f"/v1/privacy/export/{eid}/download"):
        r = await api_privasi.klien.get(jalur, headers=auth(token_b))
        assert r.status_code == 404, f"{jalur} milik A terbuka bagi B: {r.status_code}"
    r = await api_privasi.klien.get(f"/v1/privacy/export/{eid}/download", headers=auth(token_a))
    assert r.status_code == 200, "percobaan B membakar tautan sekali-pakai milik A"


async def test_ekspor_butuh_sandi_dan_dibatasi_per_jam(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    salah = await _minta_ekspor(api_privasi, token, sandi="bukan-sandinya-sama-sekali")
    assert salah.status_code == 403, salah.text
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM audit_logs "
            "WHERE user_id = %s AND action = 'data.export_rejected'",
            uid,
        )
        == 1
    )
    for _ in range(identity.BATAS_EKSPOR.jumlah - 1):  # tebakan salah tadi memakai satu jatah
        assert (await _minta_ekspor(api_privasi, token)).status_code == 202
    lebih = await _minta_ekspor(api_privasi, token)
    assert lebih.status_code == 429, "permintaan ekspor tanpa batas — tiap ekspor membaca semuanya"


async def test_ekspor_tak_dikenal_404(api_privasi: ApiUji) -> None:
    _uid, token = await _daftar(api_privasi)
    acak = uuid.uuid4()
    for jalur in (f"/v1/privacy/export/{acak}", f"/v1/privacy/export/{acak}/download"):
        r = await api_privasi.klien.get(jalur, headers=auth(token))
        assert r.status_code == 404, r.text
        assert r.json()["error"]["code"] == "export_not_found"


# ─────────────────────────────────────────────────────── izin per agent ──


async def _izin(api: ApiUji, token: str) -> dict[tuple[str, str, str], dict[str, Any]]:
    r = await api.klien.get("/v1/privacy/permissions", headers=auth(token))
    assert r.status_code == 200, r.text
    return {
        (a["subject_id"], i["scope"], i["action"]): i
        for a in r.json()["agents"]
        for i in a["permissions"]
    }


async def test_izin_per_agent_menampilkan_bawaan_gerbang(api_privasi: ApiUji) -> None:
    _uid, token = await _daftar(api_privasi)
    izin = await _izin(api_privasi, token)

    assert {a for a, _s, _x in izin} == {
        "coach-agent",
        "habit-agent",
        "memory-agent",
        "orchestrator-agent",
    }
    habits_baca = izin[("coach-agent", "habits", "read")]
    assert (habits_baca["decision"], habits_baca["source"]) == ("allow", "default")
    tulis = izin[("habit-agent", "habits", "write")]
    assert tulis["decision"] == "ask", "R2 (habit.complete) berbawaan allow di layar"
    assert izin[("coach-agent", "mood", "read")]["sensitive"] is True, "mood bukan sensitif (C-32)"
    assert izin[("coach-agent", "mood", "read")]["decision"] == "ask", (
        "layar menjanjikan `allow` atas scope sensitif yang gerbang tanyakan (E-180)"
    )
    assert ("orchestrator-agent", "mood", "execute") not in izin, (
        "layar menampilkan izin delegasi atas scope sensitif yang tidak dibacanya (E-227)"
    )


async def test_ubah_izin_berlaku_seketika_di_mesin_izin(api_privasi: ApiUji) -> None:
    uid, token = await _daftar(api_privasi)
    mesin = identity.MesinIzin(
        api_privasi.app.state.engine,
        api_privasi.app.state.redis,
        api_privasi.app.state.settings.redis_prefix,
        api_privasi.app.state.settings.permission_cache_ttl_s,
    )
    coach = identity.Subjek("agent", "coach-agent")
    uid_ = uuid.UUID(uid)
    assert await mesin.cek(uid_, coach, "habits", "read", bawaan="allow") == "allow"

    r = await api_privasi.klien.put(
        "/v1/privacy/permissions/agent/coach-agent/habits",
        json={"action": "read", "decision": "deny"},
        headers=auth(token),
    )
    assert r.status_code == 200, r.text
    assert (r.json()["decision"], r.json()["source"]) == ("deny", "user")
    assert await mesin.cek(uid_, coach, "habits", "read", bawaan="allow") == "deny", (
        "larangan di Privacy Center tidak sampai ke gerbang (cache basi?)"
    )
    assert (await _izin(api_privasi, token))[("coach-agent", "habits", "read")][
        "decision"
    ] == "deny"

    nanti = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    r = await api_privasi.klien.put(
        "/v1/privacy/permissions/agent/coach-agent/mood",
        json={"action": "read", "decision": "allow", "expires_at": nanti},
        headers=auth(token),
    )
    assert r.status_code == 200, r.text
    assert r.json()["expires_at"] is not None
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action LIKE 'permission.%%'",
            uid,
        )
        == 2
    ), "perubahan izin tanpa jejak audit (1.6)"


@pytest.mark.parametrize(
    ("jalur", "badan", "status", "kode"),
    [
        (
            "agent/coach-agent/journal_raw",
            {"action": "read", "decision": "allow"},
            404,
            "permission_not_requested",
        ),
        ("agent/agent-fiktif/habits", {"action": "read", "decision": "allow"}, 404, None),
        ("agent/coach-agent/habits", {"action": "delete", "decision": "allow"}, 404, None),
        ("tool/habit.list/habits", {"action": "read", "decision": "deny"}, 404, None),
        (
            "agent/coach-agent/habits",
            {"action": "read", "decision": "allow", "expires_at": "2020-01-01T00:00:00+07:00"},
            422,
            "expires_at_in_past",
        ),
        ("agent/coach-agent/habits", {"action": "read", "decision": "maybe"}, 400, None),
        ("agent/coach-agent/habits", {"action": "read", "decision": "allow", "x": 1}, 400, None),
    ],
)
async def test_izin_yang_tidak_diminta_atau_cacat_ditolak(
    api_privasi: ApiUji, jalur: str, badan: dict[str, Any], status: int, kode: str | None
) -> None:
    uid, token = await _daftar(api_privasi)
    r = await api_privasi.klien.put(
        f"/v1/privacy/permissions/{jalur}", json=badan, headers=auth(token)
    )
    assert r.status_code == status, f"izin yang tidak diminta/cacat diterima: {r.text}"
    if kode:
        assert r.json()["error"]["code"] == kode
    assert _satu(api_privasi, "SELECT count(*) FROM permissions WHERE user_id = %s", uid) == 0


# ───────────────────────────── tinjauan keamanan Sprint 5–6 (8 Okt 2026) ──


@pytest.mark.parametrize("kategori", ["habits", "history"])
async def test_hapus_sumber_membuang_proyeksi_perilaku_turunannya(
    api_privasi: ApiUji, kategori: str
) -> None:
    """Tinjauan keamanan S5–6 (S1): lajur `activities` `source='inferred'` adalah PROYEKSI
    event habit (Behavior projector 5.1) — `completion_id`, tanggal, status, dan tier tiap
    penyelesaian. Versi pertama tidak menyatakannya turunan siapa pun: hapus `habits` (atau
    seluruh riwayat kejadian) meninggalkan riwayat penyelesaian habit itu utuh di aktivitas,
    ikut terekspor dan tampil di `GET /activities` — persis *“nilai turunan tetap membawa
    jejak perilaku walau sumbernya hilang”* yang K-42 tolak (naskah 11 §7.25)."""
    uid, token = await _daftar(api_privasi)
    await _isi_semuanya(api_privasi, uid, token)
    k, h = api_privasi.klien, auth(token)
    habit = (
        await k.post(
            "/v1/habits", json={"title": "Baca buku", "period": "day", "target_count": 1}, headers=h
        )
    ).json()
    r = await k.post(
        f"/v1/habits/{habit['id']}/completions",
        json={"for_date": TANGGAL, "status": "done"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    # Behavior projector — di pekerja ia konsumen stream; di sini dijalankan langsung.
    await intelligence.bangun_ulang_proyeksi(api_privasi.app.state.engine, uuid.UUID(uid))
    proyeksi = "SELECT count(*) FROM activities WHERE user_id = %s AND source = 'inferred'"
    assert _satu(api_privasi, proyeksi, uid) == 1, "prasyarat: penyelesaian tidak terproyeksi"

    r = await _hapus(api_privasi, token, kategori)
    assert r.status_code == 202, r.text

    assert _satu(api_privasi, proyeksi, uid) == 0, (
        f"hapus `{kategori}` meninggalkan proyeksi penyelesaian habit di aktivitas"
    )
    assert (
        _satu(
            api_privasi,
            "SELECT count(*) FROM activities WHERE user_id = %s AND source = 'manual'",
            uid,
        )
        == 1
    ), f"hapus `{kategori}` membuang aktivitas yang DICATAT pengguna"


@pytest.fixture
async def api_kredensial_ip_kecil(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> AsyncIterator[ApiUji]:
    """Aplikasi utuh dengan batas pencocokan sandi per IP 3/10 menit — daftar memakai satu."""
    db = basis_data_termigrasi("privasi")
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=db.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
            rate_limit_auth_ip="3/600",
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as k,
    ):
        yield ApiUji(app=app, klien=k, db=db, awalan_redis=awalan, engine_pekerja=None)


@pytest.mark.parametrize("pintu", ["hapus-data", "ekspor", "hapus-akun"])
async def test_sandi_ulang_dibatasi_per_ip_seperti_login(
    api_kredensial_ip_kecil: ApiUji, pintu: str
) -> None:
    """Tinjauan keamanan S5–6 (S2): tiap sandi ulang menjalankan argon2id (64 MiB, di thread)
    — sama mahalnya dengan login. Login dibatasi per IP (`rate_limit_auth_ip`, 30/10 menit)
    justru karena itu; pintu sandi ulang hanya dibatasi per pengguna (300/menit) dan per
    akun — yang DIKOSONGKAN tiap kali sandinya benar. Satu akun cukup untuk memaksa ratusan
    argon2 per menit per IP: 100× batas login. Kini pencocokan sandi di pintu mana pun memakai
    jatah per IP yang sama, SEBELUM argon2 — juga untuk sandi yang benar."""
    api = api_kredensial_ip_kecil
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(_email()))
    assert r.status_code == 201, r.text
    token = r.json()["tokens"]["access_token"]

    async def coba(sandi: str) -> Any:
        if pintu == "hapus-data":
            return await _hapus(api, token, "journal", sandi=sandi)
        if pintu == "ekspor":
            return await _minta_ekspor(api, token, sandi=sandi)
        return await api.klien.request(
            "DELETE", "/v1/me", json={"password": sandi}, headers=auth(token)
        )

    for _ in range(2):
        assert (await coba("tebakan-yang-salah-terus")).status_code == 403
    r = await coba(SANDI)
    assert r.status_code == 429, (
        f"pencocokan sandi ke-4 dari IP yang sama (daftar + sandi ulang) tidak dibatasi: {r.text}"
    )
    assert "Retry-After" in r.headers
