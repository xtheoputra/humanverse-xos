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
from fastapi.middleware.cors import CORSMiddleware

from hvx import __version__
from hvx.modules import checkins, goals, habits, identity, platform, profile

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
    # K-23: bacaan lintas modul domain di transaksi pemanggil — habits butuh zona
    # waktu profil untuk "hari ini" rentetan (spec/07 2.4) tanpa mengimpor profile.
    app.state.pembaca_zona_waktu = profile.zona_waktu
    # …dan energi check-in untuk tier habit yang disarankan (spec/07 2.2, naskah 4 §34).
    app.state.pembaca_energi = checkins.energi_pada
    # …dan goal yang HIDUP saat habit menautnya (FK tidak melihat hapus-lunak);
    # goal yang dihapus melepas habit yang menautnya, di transaksi hapus yang sama.
    app.state.pembaca_goal_hidup = goals.kunci_goal_hidup
    app.state.pendengar_goal_dihapus = (habits.lepas_goal,)
    platform.pasang_penangan_galat(app)
    # Yang ditambahkan TERAKHIR paling luar: 429 batas laju tetap membawa
    # X-Request-ID dan tercatat di baris `request.completed`. Batas ukuran badan
    # di DALAM batas laju — banjir permintaan ditolak sebelum badannya dibaca.
    app.add_middleware(platform.BatasBadanMiddleware)
    app.add_middleware(platform.BatasLajuIpMiddleware)
    app.add_middleware(platform.RequestContextMiddleware)
    if settings.asal_cors:
        # Paling luar: jawaban 401/429 pun membawa header CORS, supaya aplikasi
        # web membaca galatnya alih-alih "network error". Tanpa kredensial
        # peramban (cookie) — autentikasi V0 token bearer (K-21).
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.asal_cors),
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
            expose_headers=["Retry-After", "X-Request-ID", "Idempotent-Replayed"],
            allow_credentials=False,
            max_age=600,
        )
    app.include_router(platform.router)
    app.include_router(identity.router)
    app.include_router(profile.router)
    app.include_router(goals.router)
    app.include_router(habits.router)
    app.include_router(checkins.router)
    return app
