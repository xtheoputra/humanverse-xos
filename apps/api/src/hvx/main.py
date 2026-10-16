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
from hvx.modules import (
    activities,
    agents,
    checkins,
    events,
    goals,
    habits,
    identity,
    intelligence,
    journal,
    memory,
    platform,
    profile,
)

DOKUMENTASI_TERBUKA: frozenset[str] = frozenset({"local", "test", "ci"})


def create_app(settings: platform.Settings | None = None) -> FastAPI:
    settings = settings or platform.Settings()  # dari lingkungan (HVX_*)
    platform.konfigurasi_log(level=settings.log_level, json=settings.log_json)
    # spec/07 4.2: manifest & tool registry divalidasi SEBELUM api bisa dibuat —
    # satu pelanggaran aturan spec/05 dan tidak ada yang melayani (K-29).
    registri = agents.muat_registri()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = platform.buat_engine(settings.database_url)
        try:
            # B-40: api tidak pernah melayani sebagai peran yang melewati RLS.
            await platform.pastikan_peran_aplikasi(engine)
            # K-29: katalog `agents` (dikelola migrasi) == manifest yang divalidasi.
            await agents.pastikan_katalog(engine, registri)
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
        # spec/07 4.3–4.8: agent hanya lewat runtime ini — tool lewat pelaksana (registry,
        # manifest, masukan, batas laju, gerbang risiko), model lewat AI Gateway.
        mesin_izin = identity.MesinIzin(
            engine, redis, settings.redis_prefix, settings.permission_cache_ttl_s
        )
        tanda = agents.TokenKonfirmasi(partial(platform.sidik, settings, "konfirmasi-agent"))
        vektor = platform.klien_vektor_dari(settings)
        pencari = (
            memory.PencariMemori(
                engine,
                mesin_izin,
                vektor,
                platform.penyemat_dari(settings),
                settings.qdrant_koleksi,
            )
            if vektor
            else None
        )
        runtime = agents.RuntimeAgent(
            engine,
            registri,
            agents.PROGRAM_V0,
            agents.PelaksanaAlat(
                registri,
                agents.IMPLEMENTASI,
                agents.GerbangRisiko(engine, mesin_izin, tanda),
                platform.PembatasLaju(redis, settings.redis_prefix),
            ),
            platform.gerbang_model_dari(settings),
            pencari,
            anggaran_harian_usd=settings.ai_anggaran_harian_usd,
        )
        app.state.percakapan = agents.LayananPercakapan(
            engine, runtime, agents.AliranPercakapan(), mesin_izin, tanda
        )
        try:
            yield
        finally:
            await app.state.percakapan.tutup()
            if vektor:
                await vektor.tutup()
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
    app.state.registri_agent = registri
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
    # Jurnal diubah/dihapus → memori episodiknya mengikuti, di transaksi yang sama
    # (spec/07 3.6): kalimat yang dihapus pemiliknya tidak hidup terus di memori.
    app.state.pendengar_jurnal_berubah = (memory.selaraskan_jurnal,)
    # Privacy Center (spec/07 6.4, K-41 · K-42): tiap modul menyatakan tabelnya sendiri dan
    # turunan yang ikut terhapus bersama sumbernya; `identity` meringkas, mengekspor, dan
    # menghapus tanpa mengimpor satu pun. Tiap tabel ber-`user_id` spec/01 tepat sekali —
    # `tests/unit/test_cakupan_privasi.py`.
    app.state.bagian_privasi = (
        *identity.BAGIAN_PRIVASI,
        *profile.BAGIAN_PRIVASI,
        *goals.BAGIAN_PRIVASI,
        *habits.BAGIAN_PRIVASI,
        *checkins.BAGIAN_PRIVASI,
        *journal.BAGIAN_PRIVASI,
        *activities.BAGIAN_PRIVASI,
        *events.BAGIAN_PRIVASI,
        *memory.BAGIAN_PRIVASI,
        *intelligence.BAGIAN_PRIVASI,
        *agents.BAGIAN_PRIVASI,
    )
    app.state.penghapus_privasi = (
        *goals.PENGHAPUS_PRIVASI,
        *habits.PENGHAPUS_PRIVASI,
        *checkins.PENGHAPUS_PRIVASI,
        *journal.PENGHAPUS_PRIVASI,
        *activities.PENGHAPUS_PRIVASI,
        *profile.PENGHAPUS_PRIVASI,
        *events.PENGHAPUS_PRIVASI,
        *memory.PENGHAPUS_PRIVASI,
        *intelligence.PENGHAPUS_PRIVASI,
        *agents.PENGHAPUS_PRIVASI,
    )
    # …dan izin per agent dari registry yang SAMA dengan yang ditegakkan gerbang risiko.
    app.state.katalog_izin_agent = agents.izin_diminta(registri)
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
            expose_headers=[
                "Retry-After",
                "X-Request-ID",
                "Idempotent-Replayed",
                "Content-Disposition",  # nama berkas ekspor Privacy Center (6.4)
            ],
            allow_credentials=False,
            max_age=600,
        )
    app.include_router(platform.router)
    app.include_router(identity.router)
    app.include_router(identity.router_akun)
    app.include_router(identity.router_privasi)
    app.include_router(profile.router)
    app.include_router(goals.router)
    app.include_router(habits.router)
    app.include_router(checkins.router)
    app.include_router(journal.router)
    app.include_router(activities.router)
    app.include_router(intelligence.router)
    app.include_router(agents.router)
    return app
