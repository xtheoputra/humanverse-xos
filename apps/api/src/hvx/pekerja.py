"""Proses pekerja — relay event dan konsumen stream (spec/07 3.3 · 3.6).

    python -m hvx.pekerja

Citra yang sama dengan api (arch/09 §5 aturan 1), proses terpisah: relay dan
konsumen berulang tanpa henti dan memblokir (`XREADGROUP BLOCK`) — di proses
api mereka bersaing dengan permintaan HTTP, dan tiap replika api akan
menjalankan relay-nya sendiri. Klien Redis-nya sendiri, dengan batas waktu
soket lebih panjang dari BLOCK (`platform/redis_store.py`).

Seperti `hvx.main`, berkas ini berada di luar `hvx.modules` dan hanya menyambung
modul lewat pintu keluarnya.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
from collections.abc import Awaitable, Callable

import structlog
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import events, platform

log = structlog.get_logger("hvx.pekerja")

JEDA_RELAY_S = 1.0
PANGKAS_TIAP = 60  # putaran relay — ±1 menit
_SOKET_S = 10.0  # > BLOCK konsumen (2 dtk), lihat platform/redis_store.py


def rakit_konsumen(
    engine: AsyncEngine, redis: Redis, settings: platform.Settings
) -> list[events.KonsumenStream]:
    """Grup konsumen V0 (spec/03 *Consumer V0*) — ditambah tugas yang membangunnya."""
    return []


async def _ulang(
    nama: str, kerja: Callable[[], Awaitable[object]], jeda_s: float, berhenti: asyncio.Event
) -> None:
    while not berhenti.is_set():
        try:
            await kerja()
        except Exception:
            log.exception("pekerja.putaran_gagal", tugas=nama)
            jeda = max(jeda_s, 1.0)  # galat berulang tidak memutar CPU
        else:
            jeda = jeda_s
        if jeda:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(berhenti.wait(), timeout=jeda)


async def jalankan(settings: platform.Settings, berhenti: asyncio.Event) -> None:
    """Relay + konsumen sampai `berhenti` diset — lalu menutup koneksinya."""
    engine = platform.buat_engine(settings.database_url)
    redis = platform.buat_redis(
        settings.redis_url,
        socket_timeout_s=max(_SOKET_S, settings.redis_socket_timeout_s),
        connect_timeout_s=settings.redis_connect_timeout_s,
    )
    try:
        # B-40: pekerja membaca event SEMUA pengguna — lewat fungsi sempit, sebagai hvx_app.
        await platform.pastikan_peran_aplikasi(engine)
        relay = events.Relay(engine, redis, settings.redis_prefix)
        konsumen = rakit_konsumen(engine, redis, settings)
        for k in konsumen:
            await k.siapkan()
        putaran = 0

        async def relay_sekali() -> None:
            nonlocal putaran
            await relay.putaran()
            putaran += 1
            if putaran % PANGKAS_TIAP == 0:
                await relay.pangkas()

        tugas = [asyncio.create_task(_ulang("relay", relay_sekali, JEDA_RELAY_S, berhenti))]
        tugas += [
            asyncio.create_task(_ulang(f"konsumen:{k.grup}", k.putaran, 0.0, berhenti))
            for k in konsumen
        ]
        log.info("pekerja.mulai", konsumen=[k.grup for k in konsumen])
        await berhenti.wait()
        for t in tugas:
            t.cancel()
        await asyncio.gather(*tugas, return_exceptions=True)
    finally:
        await redis.aclose()
        await engine.dispose()
        log.info("pekerja.berhenti")


async def _utama() -> None:
    settings = platform.Settings()  # dari lingkungan (HVX_*), sama dengan api
    platform.konfigurasi_log(level=settings.log_level, json=settings.log_json)
    berhenti = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sinyal in (signal.SIGTERM, signal.SIGINT):
        # Windows tidak mendukungnya — Ctrl+C tetap menghentikan asyncio.run.
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sinyal, berhenti.set)
    await jalankan(settings, berhenti)


def main() -> None:
    asyncio.run(_utama())


if __name__ == "__main__":
    main()
