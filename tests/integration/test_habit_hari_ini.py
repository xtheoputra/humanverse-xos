"""spec/07 2.2 lewat HTTP — *“uji: tier turun saat energi rendah”* — sesudah check-in (2.5).

`GET /habits?for_date=` membawa, per habit, penyelesaiannya pada tanggal itu dan
tier yang disarankan dari energi check-in tanggal itu (naskah 4 §34). Energi
milik `checkins`; `habits` membacanya lewat pembaca yang dipasang titik rakit
(K-23), di transaksi yang sama — tanpa mengimpor `checkins`.
"""

from __future__ import annotations

from typing import Any

import pytest
from _bantuan_db import ApiUji, auth
from test_habits import TIGA_TIER, buat_habit

pytestmark = pytest.mark.integration


async def _hari(api: ApiUji, token: str, tanggal: str) -> list[dict[str, Any]]:
    r = await api.klien.get("/v1/habits", params={"for_date": tanggal}, headers=auth(token))
    assert r.status_code == 200, r.text
    items: list[dict[str, Any]] = r.json()["items"]
    return items


@pytest.mark.parametrize(
    ("energi", "tier"),
    [(5, 0), (3, 0), (2, 1), (1, 2)],
)
async def test_tier_turun_saat_energi_rendah(api_bersama: ApiUji, energi: int, tier: int) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    await api_bersama.klien.put(
        "/v1/checkins/2026-09-15", json={"energy": energi}, headers=auth(token)
    )

    (habit,) = await _hari(api_bersama, token, "2026-09-15")

    assert habit["day"]["energy"] == energi
    assert habit["day"]["suggested_tier"] == tier, (
        f"tier tidak turun saat energi rendah: energi {energi} → tier {habit['day']}"
    )


async def test_belum_check_in_tier_penuh_bukan_diturunkan(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    await buat_habit(api_bersama, token, title="Tanpa tier")

    habit = await _hari(api_bersama, token, "2026-09-16")

    assert [(h["day"]["energy"], h["day"]["suggested_tier"]) for h in habit] == [
        (None, 0),
        (None, None),
    ]


async def test_energi_dibaca_dari_tanggal_yang_diminta_saja(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    await api_bersama.klien.put("/v1/checkins/2026-09-17", json={"energy": 1}, headers=auth(token))

    (kemarin,) = await _hari(api_bersama, token, "2026-09-17")
    (hari_ini,) = await _hari(api_bersama, token, "2026-09-18")

    assert kemarin["day"]["suggested_tier"] == 2
    assert hari_ini["day"]["suggested_tier"] == 0


async def test_penyelesaian_tanggal_itu_ikut_terbaca(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    await api_bersama.klien.post(
        f"/v1/habits/{h['id']}/completions",
        json={"for_date": "2026-09-19", "status": "done", "tier_used": 1},
        headers=auth(token),
    )

    (tercatat,) = await _hari(api_bersama, token, "2026-09-19")
    (lain,) = await _hari(api_bersama, token, "2026-09-20")

    assert tercatat["day"]["completion"]["tier_used"] == 1
    assert lain["day"]["completion"] is None


async def test_energi_pengguna_lain_tidak_pernah_dipakai(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token_b, adaptive_tiers=TIGA_TIER)
    await api_bersama.klien.put(
        "/v1/checkins/2026-09-21", json={"energy": 1}, headers=auth(token_a)
    )

    (habit_b,) = await _hari(api_bersama, token_b, "2026-09-21")

    assert (habit_b["day"]["energy"], habit_b["day"]["suggested_tier"]) == (None, 0)


async def test_daftar_tanpa_tanggal_tidak_membawa_hari(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)

    r = await api_bersama.klien.get("/v1/habits", headers=auth(token))

    assert r.json()["items"][0]["day"] is None
