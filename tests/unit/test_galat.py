"""Amplop galat spec/04 — dan galat validasi yang tidak pernah memantulkan masukan."""

from __future__ import annotations

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from hvx.modules.platform import GalatApi, pasang_penangan_galat


class _Masuk(BaseModel):
    email: str
    password: str
    umur: int


def _app() -> FastAPI:
    app = FastAPI()
    pasang_penangan_galat(app)

    @app.post("/masuk")
    async def masuk(badan: _Masuk) -> dict[str, str]:
        return {"ok": badan.email}

    @app.get("/bentrok")
    async def bentrok() -> None:
        raise GalatApi(409, "conflict", "Email sudah terdaftar.", header={"X-Uji": "1"})

    return app


async def _minta(metode: str, jalur: str, **kw: object) -> httpx.Response:
    transport = httpx.ASGITransport(app=_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as k:
        return await k.request(metode, jalur, **kw)  # type: ignore[arg-type]


async def test_galat_validasi_400_beramplop_tanpa_memantulkan_sandi() -> None:
    r = await _minta(
        "POST", "/masuk", json={"email": "a@b.id", "password": "rahasia-sekali-123", "umur": "tua"}
    )

    assert r.status_code == 400
    galat = r.json()["error"]
    assert galat["code"] == "invalid_request"
    assert galat["details"] == [
        {"loc": ["body", "umur"], "msg": galat["details"][0]["msg"], "type": "int_parsing"}
    ]
    assert "rahasia-sekali-123" not in r.text
    assert "tua" not in r.text, "nilai masukan dipantulkan kembali"


async def test_galat_api_beramplop_dengan_header() -> None:
    r = await _minta("GET", "/bentrok")

    assert r.status_code == 409
    assert r.json() == {"error": {"code": "conflict", "message": "Email sudah terdaftar."}}
    assert r.headers["x-uji"] == "1"


async def test_rute_tak_dikenal_404_beramplop() -> None:
    r = await _minta("GET", "/tidak-ada")

    assert r.status_code == 404
    assert r.json() == {"error": {"code": "not_found", "message": "Not Found"}}
