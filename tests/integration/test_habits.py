"""spec/07 2.2 — modul `habits` + jadwal + `adaptive_tiers`, lewat HTTP sebagai peran aplikasi.

Tier yang turun saat energi rendah diuji di dua tempat: aturannya sendiri di
`tests/unit/test_tier.py`, dan sesudah check-in (2.5) lewat HTTP di
`test_habit_hari_ini.py`.
"""

from __future__ import annotations

from typing import Any

import pytest
from _bantuan_db import ApiUji, auth

pytestmark = pytest.mark.integration

TIGA_TIER = [
    {"label": "Workout 60 menit", "minutes": 60},
    {"label": "Workout 30 menit", "minutes": 30},
    {"label": "Mobility 10 menit", "minutes": 10},
]


async def buat_habit(api: ApiUji, token: str, **isi: Any) -> dict[str, Any]:
    isi.setdefault("title", "Workout")
    isi.setdefault("period", "day")
    isi.setdefault("target_count", 1)
    r = await api.klien.post("/v1/habits", json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def test_habit_dibuat_dengan_jadwal_dan_tier_lalu_terbaca(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    h = await buat_habit(
        api_bersama,
        token,
        schedule={"weekdays": [1, 3, 5], "time": "18:00"},
        adaptive_tiers=TIGA_TIER,
    )
    daftar = (await api_bersama.klien.get("/v1/habits", headers=auth(token))).json()["items"]

    assert h["schedule"] == {"weekdays": [1, 3, 5], "time": "18:00"}
    assert h["adaptive_tiers"] == TIGA_TIER
    assert h["status"] == "active"
    assert [x["id"] for x in daftar] == [h["id"]]


@pytest.mark.parametrize(
    "badan",
    [
        {"period": "day", "target_count": 2},  # satu tanggal satu penyelesaian
        {"period": "week", "target_count": 8},
        {"period": "month", "target_count": 0},
        {"period": "week", "target_count": 3, "schedule": {"weekdays": [1, 3]}},
        {"schedule": {"weekdays": [3, 1]}},
        {"schedule": {"weekdays": [1, 1]}},
        {"schedule": {"weekdays": [0]}},
        {"schedule": {"weekdays": [8]}},
        {"schedule": {"time": "25:00"}},
        {"schedule": {"hari": [1]}},
        {"adaptive_tiers": [{"label": f"T{i}"} for i in range(6)]},
        {"adaptive_tiers": [{"label": "   "}]},
        {"adaptive_tiers": [{"label": "x", "minutes": 0}]},
        {"title": "   "},
        {"period": "year"},
        {"user_id": "00000000-0000-0000-0000-000000000000"},
    ],
)
async def test_habit_berbentuk_salah_ditolak_400(
    api_bersama: ApiUji, badan: dict[str, Any]
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    isi = {"title": "Habit", "period": "day", "target_count": 1, **badan}

    r = await api_bersama.klien.post("/v1/habits", json=isi, headers=auth(token))

    assert r.status_code == 400, r.text
    assert (await api_bersama.klien.get("/v1/habits", headers=auth(token))).json()["items"] == []


async def test_patch_yang_membuat_paduan_periode_tidak_sah_ditolak_422(
    api_bersama: ApiUji,
) -> None:
    """Badannya sah sendiri — yang salah paduannya dengan baris tersimpan."""
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token, period="week", target_count=3)

    r = await api_bersama.klien.patch(
        f"/v1/habits/{h['id']}", json={"period": "day"}, headers=auth(token)
    )

    assert r.status_code == 422, "paduan period × target_count yang tidak sah tersimpan: " + r.text
    assert r.json()["error"]["code"] == "invalid_habit"
    tetap = (await api_bersama.klien.get("/v1/habits", headers=auth(token))).json()["items"][0]
    assert (tetap["period"], tetap["target_count"]) == ("week", 3)


async def test_patch_mengubah_hanya_medan_yang_dikirim(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)

    r = await api_bersama.klien.patch(
        f"/v1/habits/{h['id']}",
        json={"title": "Lari", "status": "paused", "period": "week", "target_count": 4},
        headers=auth(token),
    )

    assert r.status_code == 200, r.text
    baru = r.json()
    assert (baru["title"], baru["status"], baru["period"], baru["target_count"]) == (
        "Lari",
        "paused",
        "week",
        4,
    )
    assert baru["adaptive_tiers"] == TIGA_TIER
    aktif = await api_bersama.klien.get(
        "/v1/habits", params={"status": "active"}, headers=auth(token)
    )
    assert aktif.json()["items"] == []


async def test_habit_bisa_ditautkan_ke_goal_sendiri_dan_dilepas(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    goal = (
        await api_bersama.klien.post("/v1/goals", json={"title": "Sehat"}, headers=auth(token))
    ).json()

    h = await buat_habit(api_bersama, token, goal_id=goal["id"])
    lepas = await api_bersama.klien.patch(
        f"/v1/habits/{h['id']}", json={"goal_id": None}, headers=auth(token)
    )

    assert h["goal_id"] == goal["id"]
    assert lepas.json()["goal_id"] is None


async def test_goal_milik_pengguna_lain_tidak_bisa_ditautkan(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    goal_a = (
        await api_bersama.klien.post("/v1/goals", json={"title": "Milik A"}, headers=auth(token_a))
    ).json()

    buat = await api_bersama.klien.post(
        "/v1/habits",
        json={"title": "X", "period": "day", "target_count": 1, "goal_id": goal_a["id"]},
        headers=auth(token_b),
    )
    h = await buat_habit(api_bersama, token_b)
    ubah = await api_bersama.klien.patch(
        f"/v1/habits/{h['id']}", json={"goal_id": goal_a["id"]}, headers=auth(token_b)
    )

    assert buat.status_code == 422, buat.text
    assert buat.json()["error"]["code"] == "goal_not_found"
    assert ubah.status_code == 422, ubah.text


async def test_habit_pengguna_lain_tidak_bisa_diubah_atau_dihapus(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token_a, title="Milik A")
    k = api_bersama.klien

    ubah = await k.patch(f"/v1/habits/{h['id']}", json={"title": "B"}, headers=auth(token_b))
    hapus = await k.delete(f"/v1/habits/{h['id']}", headers=auth(token_b))

    assert (ubah.status_code, hapus.status_code) == (404, 404)
    assert (await k.get("/v1/habits", headers=auth(token_b))).json()["items"] == []
    milik_a = (await k.get("/v1/habits", headers=auth(token_a))).json()["items"]
    assert [x["title"] for x in milik_a] == ["Milik A"]


async def test_hapus_lunak_menyembunyikan_habit(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)

    pertama = await api_bersama.klien.delete(f"/v1/habits/{h['id']}", headers=auth(token))
    kedua = await api_bersama.klien.delete(f"/v1/habits/{h['id']}", headers=auth(token))

    assert (pertama.status_code, kedua.status_code) == (204, 404)
    assert (await api_bersama.klien.get("/v1/habits", headers=auth(token))).json()["items"] == []
