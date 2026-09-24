"""spec/04 — bentuk salah → `400`, tidak dikoersi diam-diam (E-170).

Kasus di sini kasus yang tinjauan kontrak Sprint 2 kirim ke api hidup, dan
yang semuanya dijawab `201`: `true` sebagai valensi mood terburuk, `"3"`
sebagai target, detik Unix sebagai `for_date` UTC, persetujuan pelatihan model
dari string `"on"`. Penjaga strukturalnya `tests/unit/test_masukan_ketat_semua_rute.py`;
yang di sini membuktikan jawabannya lewat HTTP — dan bahwa tidak ada baris
yang sempat tertulis.
"""

from __future__ import annotations

from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg import sql

pytestmark = pytest.mark.integration

UNIX = 1758672000  # 2025-09-24T00:00:00Z


def _jumlah(api: ApiUji, tabel: str, user_id: Any) -> int:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            sql.SQL("SELECT count(*) FROM {} WHERE user_id = %s").format(sql.Identifier(tabel)),
            (user_id,),
        ).fetchone()
    assert baris is not None
    return int(baris[0])


@pytest.mark.parametrize(
    ("tabel", "metode", "jalur", "isi"),
    [
        ("mood_entries", "POST", "/v1/moods", {"valence": True}),
        ("mood_entries", "POST", "/v1/moods", {"valence": "3"}),
        ("mood_entries", "POST", "/v1/moods", {"valence": 3.0}),
        ("mood_entries", "POST", "/v1/moods", {"valence": 3, "occurred_at": UNIX}),
        ("mood_entries", "POST", "/v1/moods", {"valence": 3, "occurred_at": str(UNIX)}),
        ("mood_entries", "POST", "/v1/moods", {"valence": 3, "occurred_at": "0001-01-01T00:00Z"}),
        (
            "mood_entries",
            "POST",
            "/v1/moods",
            {"valence": 3, "occurred_at": "0001-01-01T00:00:00+14:00"},
        ),
        ("daily_checkins", "PUT", "/v1/checkins/2026-09-01", {"energy": True}),
        ("daily_checkins", "PUT", "/v1/checkins/2026-09-01", {"sleep_hours": "7.5"}),
        ("daily_checkins", "PUT", "/v1/checkins/2026-09-01", {"sleep_hours": True}),
        ("daily_checkins", "PUT", f"/v1/checkins/{UNIX}", {}),
        ("daily_checkins", "PUT", "/v1/checkins/0001-01-01", {}),
        ("daily_checkins", "PUT", "/v1/checkins/9999-12-31", {}),
        ("habits", "POST", "/v1/habits", {"title": "x", "period": "week", "target_count": True}),
        ("habits", "POST", "/v1/habits", {"title": "x", "period": "week", "target_count": "3"}),
        (
            "habits",
            "POST",
            "/v1/habits",
            {"title": "x", "period": "day", "target_count": 1, "schedule": {"weekdays": [True]}},
        ),
        (
            "habits",
            "POST",
            "/v1/habits",
            {
                "title": "x",
                "period": "day",
                "target_count": 1,
                "adaptive_tiers": [{"label": "a", "minutes": "10"}],
            },
        ),
        ("goals", "POST", "/v1/goals", {"title": "x", "target_date": "2026-09-24T00:00:00Z"}),
        ("goals", "POST", "/v1/goals", {"title": "x", "target_date": UNIX}),
        ("goals", "POST", "/v1/goals", {"title": "x", "target_date": "0001-01-01"}),
    ],
)
async def test_badan_yang_dikoersi_pydantic_longgar_ditolak_400(
    api_bersama: ApiUji, tabel: str, metode: str, jalur: str, isi: dict[str, Any]
) -> None:
    uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.request(metode, jalur, json=isi, headers=auth(token))

    assert r.status_code == 400, r.text
    assert _jumlah(api_bersama, tabel, uid) == 0


@pytest.mark.parametrize(
    "jalur",
    [
        f"/v1/habits?for_date={UNIX}",
        "/v1/habits?for_date=2026-09-24T00:00:00Z",
        f"/v1/checkins?from={UNIX}&to={UNIX}",
        f"/v1/moods?from={UNIX}",
        "/v1/moods?to=0001-01-01T00:00:00%2B14:00",
    ],
)
async def test_kueri_bertanggal_hanya_iso(api_bersama: ApiUji, jalur: str) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.get(jalur, headers=auth(token))

    assert r.status_code == 400, r.text


async def test_penyelesaian_for_date_dan_tier_ketat(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    habit = (
        await k.post(
            "/v1/habits",
            json={
                "title": "Lari",
                "period": "day",
                "target_count": 1,
                "adaptive_tiers": [{"label": "penuh"}, {"label": "ringan"}],
            },
            headers=auth(token),
        )
    ).json()
    selesai = f"/v1/habits/{habit['id']}/completions"

    unix = await k.post(selesai, json={"for_date": UNIX, "status": "done"}, headers=auth(token))
    bool_tier = await k.post(
        selesai,
        json={"for_date": "2026-09-01", "status": "done", "tier_used": False},
        headers=auth(token),
    )
    hapus_unix = await k.delete(f"{selesai}/{UNIX}", headers=auth(token))

    assert unix.status_code == bool_tier.status_code == hapus_unix.status_code == 400
    assert _jumlah(api_bersama, "habit_completions", uid) == 0


async def test_tier_di_luar_adaptive_tiers_selalu_422_invalid_tier(api_bersama: ApiUji) -> None:
    """spec/04: `422 invalid_tier` — dulu 3 menjadi 422 tetapi 7 menjadi 400 (E-170)."""
    _uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    habit = (
        await k.post(
            "/v1/habits",
            json={
                "title": "Baca",
                "period": "day",
                "target_count": 1,
                "adaptive_tiers": [{"label": "a"}, {"label": "b"}, {"label": "c"}],
            },
            headers=auth(token),
        )
    ).json()

    kode = []
    for tier in (3, 7, 10_000):
        r = await k.post(
            f"/v1/habits/{habit['id']}/completions",
            json={"for_date": "2026-09-01", "status": "done", "tier_used": tier},
            headers=auth(token),
        )
        kode.append((r.status_code, r.json()["error"]["code"]))

    assert kode == [(422, "invalid_tier")] * 3, f"tier di luar adaptive_tiers dijawab {kode}"


async def test_persetujuan_hanya_dari_boolean_json(api_bersama: ApiUji) -> None:
    """Persetujuan pelatihan model yang tercatat dari string `"on"` bukan persetujuan."""
    r = await api_bersama.klien.post(
        "/v1/auth/register",
        json={
            "email": "ketat-persetujuan@uji.id",
            "password": "kata-sandi-panjang-sekali-123",
            "display_name": "Uji",
            "timezone": "Asia/Jakarta",
            "consents": {
                "policy_version": "draf-v0",
                "terms": 1,
                "privacy": "yes",
                "model_training": {"granted": "on", "data_scopes": ["habits"]},
            },
        },
    )

    assert r.status_code == 400, r.text
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        ada = k.execute(
            "SELECT count(*) FROM users WHERE email = 'ketat-persetujuan@uji.id'"
        ).fetchone()
    assert ada == (0,)


async def test_jam_tidur_angka_json_masuk_dan_keluar(api_bersama: ApiUji) -> None:
    """spec/04: `sleep_hours` angka — dulu masuk 7.5, keluar `"7.5"` (E-170)."""
    _uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien

    simpan = await k.put(
        "/v1/checkins/2026-09-01", json={"energy": 3, "sleep_hours": 7.5}, headers=auth(token)
    )
    daftar = await k.get(
        "/v1/checkins", params={"from": "2026-09-01", "to": "2026-09-01"}, headers=auth(token)
    )
    bulat = await k.put("/v1/checkins/2026-09-02", json={"sleep_hours": 8}, headers=auth(token))

    assert simpan.status_code == 201, simpan.text
    assert simpan.json()["sleep_hours"] == 7.5
    assert isinstance(simpan.json()["sleep_hours"], float)
    assert daftar.json()["items"][0]["sleep_hours"] == 7.5
    assert bulat.json()["sleep_hours"] == 8


async def test_badan_terlalu_besar_413_sebelum_autentikasi(api_bersama: ApiUji) -> None:
    """FastAPI membaca badan utuh SEBELUM dependensi autentikasi — tanpa batas, permintaan
    tanpa akun mengisi memori api (tinjauan keamanan Sprint 2, D1)."""
    from hvx.modules.platform import MAKS_BADAN_BYTE

    besar = b'{"email":"' + b"a" * MAKS_BADAN_BYTE + b'"}'

    r = await api_bersama.klien.post(
        "/v1/auth/login", content=besar, headers={"Content-Type": "application/json"}
    )

    assert r.status_code == 413, f"badan 1 MiB+ tidak ditolak 413: {r.status_code}"
    assert r.json()["error"]["code"] == "payload_too_large"
    assert r.headers.get("X-Request-ID"), "413 tidak tercatat seperti jawaban lain"
