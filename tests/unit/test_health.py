"""spec/07 0.3 — `GET /health` → 200 `{status, version, db, redis}`."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

import httpx
from fastapi import FastAPI

from hvx import __version__
from hvx.modules.platform import Settings, laporan_kesehatan
from hvx.modules.platform import router as router_platform

Pemeriksaan = Callable[[], Awaitable[None]]


async def _sehat() -> None:
    return None


async def _mati() -> None:
    raise ConnectionRefusedError("postgresql://rahasia@10.0.0.7:5432 menolak")


async def _menggantung() -> None:
    await asyncio.sleep(60)


def _app(db: Pemeriksaan, redis: Pemeriksaan) -> FastAPI:
    app = FastAPI()
    app.state.settings = Settings(
        env="test",
        database_url="postgresql://tidak-dipakai",
        redis_url="redis://tidak-dipakai",
        health_timeout_s=0.05,
    )
    app.state.versi = __version__
    app.state.pemeriksaan_kesehatan = {"db": db, "redis": redis}
    app.include_router(router_platform)
    return app


def _klien(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji")


async def test_sehat_200_dengan_bentuk_spesifikasi() -> None:
    async with _klien(_app(_sehat, _sehat)) as klien:
        r = await klien.get("/health")

    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__, "db": "ok", "redis": "ok"}


async def test_ketergantungan_mati_503_dan_menyebut_yang_mati() -> None:
    async with _klien(_app(_sehat, _mati)) as klien:
        r = await klien.get("/health")

    assert r.status_code == 503
    assert r.json() == {"status": "degraded", "version": __version__, "db": "ok", "redis": "down"}


async def test_pesan_galat_tidak_bocor_ke_jawaban() -> None:
    async with _klien(_app(_mati, _sehat)) as klien:
        r = await klien.get("/health")

    assert "rahasia" not in r.text
    assert "10.0.0.7" not in r.text


async def test_ketergantungan_menggantung_dibatasi_waktu() -> None:
    kode, badan = await asyncio.wait_for(
        laporan_kesehatan(
            versi="x",
            pemeriksaan={"db": _menggantung, "redis": _sehat},
            timeout_s=0.05,
        ),
        timeout=2,
    )

    assert kode == 503
    assert badan["db"] == "down"
    assert badan["redis"] == "ok"


async def test_pemeriksaan_berjalan_serentak_bukan_berurutan() -> None:
    mulai = asyncio.get_running_loop().time()
    await laporan_kesehatan(
        versi="x", pemeriksaan={"db": _menggantung, "redis": _menggantung}, timeout_s=0.2
    )
    lama = asyncio.get_running_loop().time() - mulai

    assert lama < 0.35, f"dua batas waktu 0,2 dtk memakan {lama:.2f} dtk — berurutan?"


async def test_pembatalan_yang_lambat_tidak_menahan_laporan() -> None:
    """Bentuk kegagalan yang sesungguhnya diukur: ping asyncpg yang dibatalkan
    membuka koneksi baru untuk CancelRequest dan menunggunya tanpa batas.
    `asyncio.sleep(60)` biasa dibatalkan seketika, jadi ia tidak mewakili itu —
    pemeriksaan ini menunda pembatalannya sendiri."""
    pembersihan_selesai = asyncio.Event()

    async def _pembatalan_lambat() -> None:
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            await asyncio.shield(asyncio.sleep(1.5))
            pembersihan_selesai.set()
            raise

    mulai = asyncio.get_running_loop().time()
    kode, badan = await laporan_kesehatan(
        versi="x", pemeriksaan={"db": _pembatalan_lambat, "redis": _sehat}, timeout_s=0.1
    )
    lama = asyncio.get_running_loop().time() - mulai

    assert kode == 503
    assert badan["db"] == "down"
    assert lama < 0.5, f"laporan menunggu pembersihan pembatalan: {lama:.2f} dtk"
    await asyncio.wait_for(pembersihan_selesai.wait(), timeout=3)
