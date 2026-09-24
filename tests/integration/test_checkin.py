"""spec/07 2.5 — `daily_checkins` (upsert per tanggal): `PUT` dua kali → satu baris.

Baris dihitung di basis data sebagai pemilik skema (di luar RLS) — jawaban 200
yang diam-diam menyisipkan baris kedua tetap merah.
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

pytestmark = pytest.mark.integration


def _baris(api: ApiUji, user_id: Any) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT for_date, energy, focus, sleep_hours::text, note FROM daily_checkins "
            "WHERE user_id = %s ORDER BY for_date",
            (user_id,),
        ).fetchall()


async def _put(api: ApiUji, token: str, tanggal: str, **isi: Any) -> Any:
    return await api.klien.put(f"/v1/checkins/{tanggal}", json=isi, headers=auth(token))


async def test_put_dua_kali_satu_baris(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()

    pertama = await _put(api_bersama, token, "2026-09-10", energy=3, focus=4, sleep_hours=7.5)
    kedua = await _put(api_bersama, token, "2026-09-10", energy=2, focus=4, sleep_hours=6)

    assert pertama.status_code == 201, pertama.text
    assert kedua.status_code == 200, "PUT kedua bukan 200: " + kedua.text
    assert kedua.json()["id"] == pertama.json()["id"]
    assert _baris(api_bersama, uid) == [(date(2026, 9, 10), 2, 4, "6.0", None)], (
        "PUT dua kali menulis baris kedua"
    )


async def test_put_mengganti_medan_yang_tidak_dikirim_menjadi_kosong(api_bersama: ApiUji) -> None:
    """PUT = ganti: badan ADALAH check-in tanggal itu, bukan tambalan."""
    uid, token = await api_bersama.pengguna_baru()

    await _put(api_bersama, token, "2026-09-11", energy=3, note="pagi")
    r = await _put(api_bersama, token, "2026-09-11", focus=5)

    assert r.status_code == 200
    assert (r.json()["energy"], r.json()["focus"], r.json()["note"]) == (None, 5, None), (
        "PUT menambal, bukan mengganti"
    )
    assert _baris(api_bersama, uid) == [(date(2026, 9, 11), None, 5, None, None)]


async def test_put_serentak_tanggal_sama_satu_baris(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()

    hasil = await asyncio.gather(
        *(_put(api_bersama, token, "2026-09-12", energy=e) for e in (1, 2, 3, 4, 5))
    )

    assert sorted(r.status_code for r in hasil) == [200, 200, 200, 200, 201]
    assert len(_baris(api_bersama, uid)) == 1


@pytest.mark.parametrize(
    "isi",
    [
        {"energy": 0},
        {"energy": 6},
        {"focus": 2.5},
        {"sleep_hours": 24.5},
        {"sleep_hours": -1},
        {"sleep_hours": 7.25},  # numeric(3,1): ditolak, tidak dibulatkan diam-diam
        {"note": "a\u0000b"},
        {"mood": 3},
    ],
)
async def test_check_in_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    uid, token = await api_bersama.pengguna_baru()

    r = await _put(api_bersama, token, "2026-09-13", **isi)

    assert r.status_code == 400, r.text
    assert _baris(api_bersama, uid) == []


async def test_tanggal_yang_belum_terjadi_di_mana_pun_422(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        baris = k.execute("SELECT (now() AT TIME ZONE 'Pacific/Kiritimati')::date").fetchone()
    assert baris is not None
    besok_di_mana_pun = baris[0] + timedelta(days=1)

    r = await _put(api_bersama, token, besok_di_mana_pun.isoformat(), energy=3)

    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "for_date_in_future"


async def test_daftar_rentang_inklusif_dan_terbaru_dulu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for hari in (1, 2, 3, 4):
        await _put(api_bersama, token, f"2026-08-0{hari}", energy=hari)

    r = await api_bersama.klien.get(
        "/v1/checkins", params={"from": "2026-08-02", "to": "2026-08-03"}, headers=auth(token)
    )
    semua = await api_bersama.klien.get("/v1/checkins", headers=auth(token))

    assert r.status_code == 200, r.text
    assert [c["for_date"] for c in r.json()["items"]] == ["2026-08-03", "2026-08-02"]
    assert [c["energy"] for c in semua.json()["items"]] == [4, 3, 2, 1]


@pytest.mark.parametrize(
    "param",
    [
        {"from": "2026-08-05", "to": "2026-08-01"},
        {"from": "2024-01-01", "to": "2025-01-01"},  # 367 tanggal — lebih dari 366
        {"from": "2026-08-01"},
        {"to": "2026-08-01"},
        {"from": "kemarin", "to": "2026-08-01"},
    ],
)
async def test_rentang_tidak_sah_400(api_bersama: ApiUji, param: dict[str, str]) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.get("/v1/checkins", params=param, headers=auth(token))

    assert r.status_code == 400, r.text


async def test_check_in_pengguna_lain_tidak_terlihat_dan_tidak_tertimpa(
    api_bersama: ApiUji,
) -> None:
    a, token_a = await api_bersama.pengguna_baru()
    b, token_b = await api_bersama.pengguna_baru()

    await _put(api_bersama, token_a, "2026-09-14", energy=5)
    r = await _put(api_bersama, token_b, "2026-09-14", energy=1)

    assert r.status_code == 201, "check-in B menimpa baris A"
    assert _baris(api_bersama, a) == [(date(2026, 9, 14), 5, None, None, None)]
    assert _baris(api_bersama, b) == [(date(2026, 9, 14), 1, None, None, None)]
    daftar_b = (await api_bersama.klien.get("/v1/checkins", headers=auth(token_b))).json()
    assert [c["energy"] for c in daftar_b["items"]] == [1]
