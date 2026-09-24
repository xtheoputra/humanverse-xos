"""Titik rakit aplikasi — satu-satunya tempat keduabelas modul disambungkan.

Dijalankan sebagai pabrik supaya mengimpor berkas ini tidak menuntut
lingkungan lengkap:

    uvicorn hvx.main:create_app --factory

`hvx.main` berada di luar `hvx.modules`, jadi ia boleh mengimpor modul mana
pun — tetapi hanya lewat pintu keluarnya (`hvx.modules.<modul>`), sama seperti
modul lain (kontrak `M-2` di pyproject.toml).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import partial

from fastapi import FastAPI

from hvx import __version__
from hvx.modules import goals, habits, identity, platform, profile

DOKUMENTASI_TERBUKA: frozenset[str] = frozenset({"local", "test", "ci"})


def create_app(settings: platform.Settings | None = None) -> FastAPI:
    settings = settings or platform.Settings()  # dari lingkungan (HVX_*)
    platform.konfigurasi_log(level=settings.log_level, json=settings.log_json)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = platform.buat_engine(settings.database_url)
        try:
            # B-40: api tidak pernah melayani sebagai peran yang melewati RLS.
            await platform.pastikan_peran_aplikasi(engine)
        except BaseException:
            await engine.dispose()
            raise
        redis = platform.buat_redis(
            settings.redis_url,
            socket_timeout_s=settings.redis_socket_timeout_s,
            connect_timeout_s=settings.redis_connect_timeout_s,
        )
        app.state.engine = engine
        app.state.redis = redis
        app.state.pemeriksaan_kesehatan = {
            "db": partial(platform.ping_db, engine),
            "redis": partial(platform.ping_redis, redis),
        }
        try:
            yield
        finally:
            await redis.aclose()
            await engine.dispose()

    # Dokumentasi interaktif hanya di lingkungan yang DISEBUT — daftar izin,
    # bukan daftar tolak: lingkungan baru yang lupa ditambahkan jatuh ke sisi tertutup.
    dokumentasi = settings.env in DOKUMENTASI_TERBUKA
    app = FastAPI(
        title="HumanVerse XOS API",
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs" if dokumentasi else None,
        redoc_url=None,
        openapi_url="/openapi.json" if dokumentasi else None,
    )
    app.state.settings = settings
    app.state.versi = __version__
    # Titik rakit menyambung modul yang tidak boleh saling impor (K-17): identity
    # mengumumkan pendaftaran, profile membuat profil — di transaksi yang sama.
    app.state.pendengar_pendaftaran = (profile.buat_profil_awal,)
    platform.pasang_penangan_galat(app)
    # Yang ditambahkan TERAKHIR paling luar: 429 batas laju tetap membawa
    # X-Request-ID dan tercatat di baris `request.completed`.
    app.add_middleware(platform.BatasLajuIpMiddleware)
    app.add_middleware(platform.RequestContextMiddleware)
    app.include_router(platform.router)
    app.include_router(identity.router)
    app.include_router(profile.router)
    app.include_router(goals.router)
    app.include_router(habits.router)
    return app
