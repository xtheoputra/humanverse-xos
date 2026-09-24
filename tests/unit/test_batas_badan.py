"""Batas ukuran badan — `413` sebelum apa pun membacanya (tinjauan keamanan Sprint 2, D1)."""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from hvx.modules.platform import BatasBadanMiddleware

MAKS = 1000


def _app() -> tuple[Starlette, list[int]]:
    dibaca: list[int] = []

    async def terima(request: Request) -> JSONResponse:
        badan = await request.body()
        dibaca.append(len(badan))
        return JSONResponse({"panjang": len(badan)})

    app = Starlette(routes=[Route("/", terima, methods=["GET", "POST"])])
    app.add_middleware(BatasBadanMiddleware, maks=MAKS)
    return app, dibaca


async def _kirim(**kw: object) -> tuple[httpx.Response, list[int]]:
    app, dibaca = _app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as k:
        return await k.request(kw.pop("metode", "POST"), "/", **kw), dibaca  # type: ignore[arg-type]


async def _potongan(jumlah: int, besar: int) -> AsyncIterator[bytes]:
    for _ in range(jumlah):
        yield b"x" * besar


async def test_content_length_di_atas_batas_413_tanpa_dibaca() -> None:
    r, dibaca = await _kirim(content=b"x" * (MAKS + 1))

    assert r.status_code == 413
    assert r.json()["error"]["code"] == "payload_too_large"
    assert dibaca == [], "aplikasi sempat membaca badan yang ditolak"


async def test_chunked_di_atas_batas_413() -> None:
    r, dibaca = await _kirim(content=_potongan(5, 300))

    assert r.status_code == 413, f"badan chunked di atas batas dijawab {r.status_code}"
    assert dibaca == []


async def test_chunked_di_bawah_batas_sampai_utuh() -> None:
    r, dibaca = await _kirim(content=_potongan(3, 300))

    assert r.status_code == 200
    assert dibaca == [900]


async def test_tepat_di_batas_dan_tanpa_badan_lolos() -> None:
    tepat, _ = await _kirim(content=b"x" * MAKS)
    kosong, _ = await _kirim(metode="GET")

    assert tepat.status_code == kosong.status_code == 200
    assert tepat.json() == {"panjang": MAKS}
