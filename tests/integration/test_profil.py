"""spec/07 1.3 — `GET /v1/me`, `PATCH /v1/me/profile`: timezone IANA divalidasi."""

from __future__ import annotations

import pytest
from _bantuan_db import ApiUji

pytestmark = pytest.mark.integration


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_me_mengembalikan_akun_dan_profil_milik_pemegang_token(api_uji: ApiUji) -> None:
    uid, token = await api_uji.pengguna_baru(display_name="Nadia")
    _uid_lain, _ = await api_uji.pengguna_baru(display_name="Orang Lain")

    r = await api_uji.klien.get("/v1/me", headers=_auth(token))

    assert r.status_code == 200, r.text
    isi = r.json()
    assert isi["user"]["id"] == str(uid)
    assert "password_hash" not in isi["user"]
    assert isi["profile"]["display_name"] == "Nadia"
    assert isi["profile"]["timezone"] == "Asia/Jakarta"


async def test_me_tanpa_token_401(api_uji: ApiUji) -> None:
    r = await api_uji.klien.get("/v1/me")

    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthenticated"


@pytest.mark.parametrize(
    "zona", ["Mars/Olympus_Mons", "asia/jakarta", "GMT+7", "", "Asia/Jakarta "]
)
async def test_timezone_bukan_iana_ditolak_400(api_uji: ApiUji, zona: str) -> None:
    _uid, token = await api_uji.pengguna_baru()

    r = await api_uji.klien.patch("/v1/me/profile", json={"timezone": zona}, headers=_auth(token))

    assert r.status_code == 400, r.text
    assert r.json()["error"]["details"][0]["loc"] == ["body", "timezone"]
    tetap = (await api_uji.klien.get("/v1/me", headers=_auth(token))).json()["profile"]
    assert tetap["timezone"] == "Asia/Jakarta"


@pytest.mark.parametrize("zona", ["UTC", "America/Argentina/Buenos_Aires", "Asia/Makassar"])
async def test_timezone_iana_diterima_dan_tersimpan(api_uji: ApiUji, zona: str) -> None:
    _uid, token = await api_uji.pengguna_baru()

    r = await api_uji.klien.patch("/v1/me/profile", json={"timezone": zona}, headers=_auth(token))

    assert r.status_code == 200, r.text
    assert r.json()["timezone"] == zona
    assert (await api_uji.klien.get("/v1/me", headers=_auth(token))).json()["profile"][
        "timezone"
    ] == zona


async def test_patch_hanya_mengubah_medan_yang_dikirim(api_uji: ApiUji) -> None:
    _uid, token = await api_uji.pengguna_baru(display_name="Awal", timezone="Asia/Jayapura")

    r = await api_uji.klien.patch(
        "/v1/me/profile",
        json={"display_name": "Baru", "preferences": {"tema": "gelap"}},
        headers=_auth(token),
    )

    assert r.status_code == 200, r.text
    assert r.json()["display_name"] == "Baru"
    assert r.json()["timezone"] == "Asia/Jayapura"
    assert r.json()["preferences"] == {"tema": "gelap"}


def _bersarang(dalam: int) -> dict[str, object]:
    isi: object = "x"
    for _ in range(dalam):
        isi = {"a": isi}
    return {"a": isi}


@pytest.mark.parametrize(
    "badan",
    [
        {"user_id": "00000000-0000-0000-0000-000000000000"},
        {"display_name": None},
        {"locale": "Indonesia"},
        {"preferences": {"x": "y" * 17_000}},
        # PostgreSQL menolak NUL di text dan jsonb — tanpa penjaga: 500, bukan 400
        # (tinjauan Sprint 1)
        {"display_name": "Te\u0000tap"},
        {"preferences": {"catatan": "a\u0000b"}},
        {"preferences": {"ku\u0000nci": "nilai"}},
        {"preferences": {"daftar": [{"dalam": "\u0000"}]}},
        # Bersarang lebih dalam dari platform.KEDALAMAN_JSON_MAKS (tinjauan Sprint 3, S5):
        # tersimpan, lalu tiap GET /v1/me menjadi 500 — serialisasi melewati batasnya.
        {"preferences": _bersarang(33)},
        {"preferences": {"daftar": [_bersarang(40)]}},
    ],
)
async def test_patch_yang_tidak_sah_ditolak_400_dan_tidak_menyentuh_apa_pun(
    api_uji: ApiUji, badan: dict[str, object]
) -> None:
    _uid, token = await api_uji.pengguna_baru(display_name="Tetap")

    r = await api_uji.klien.patch("/v1/me/profile", json=badan, headers=_auth(token))

    assert r.status_code == 400, r.text
    assert (await api_uji.klien.get("/v1/me", headers=_auth(token))).json()["profile"][
        "display_name"
    ] == "Tetap"
