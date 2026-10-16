"""Proses pekerja — relay event, konsumen stream, penyelaras vektor, sapuan hapus akun
(spec/07 3.3 · 3.5 · 3.6 · 6.5).

    python -m hvx.pekerja

Citra yang sama dengan api (arch/09 §5 aturan 1), proses terpisah: relay dan
konsumen berulang tanpa henti dan memblokir (`XREADGROUP BLOCK`) — di proses
api mereka bersaing dengan permintaan HTTP, dan tiap replika api akan
menjalankan relay-nya sendiri. Klien Redis-nya sendiri, dengan batas waktu
soket lebih panjang dari BLOCK (`platform/redis_store.py`).

Empat jenis tugas, masing-masing berulang sendiri — satu yang gagal tidak
menghentikan yang lain:

* **relay** — kotak keluar `events` → stream Redis (3.3);
* **konsumen** — satu per grup spec/03 *Consumer V0* (`rakit_konsumen`);
* **penyelaras vektor** — `memories` → Qdrant (3.5), HANYA bila `HVX_QDRANT_URL`
  diisi. Tanpanya memori tetap diekstrak ke PostgreSQL dan disemat begitu
  Qdrant diisi; tidak ada yang hilang;
* **sapuan hapus akun** — akun yang tenggang 30 harinya habis: titik Qdrant dibuang,
  jejak audit dianonimkan, akunnya dihapus (6.5, tahap 3–6). Pekerja yang menjalankannya
  karena hanya peran ini yang memegang fungsi sapuan (`hvx_pekerja`, spec/01 §12) —
  `hvx_app` sengaja tidak punya `DELETE` atas `users`.

Seperti `hvx.main`, berkas ini berada di luar `hvx.modules` dan hanya menyambung
modul lewat pintu keluarnya.
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
from collections.abc import Awaitable, Callable
from functools import partial

import structlog
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import events, identity, intelligence, memory, platform

log = structlog.get_logger("hvx.pekerja")

JEDA_RELAY_S = 1.0
JEDA_SELARAS_S = 2.0
PANGKAS_TIAP = 60  # putaran relay — ±1 menit
# Tenggang hapus akun 30 hari (spec/01): lima menit telatnya tidak terasa siapa pun, dan
# sapuan yang sepi hanya satu kueri berbatas.
JEDA_SAPUAN_HAPUS_S = 300.0
_SOKET_S = 10.0  # > BLOCK konsumen (2 dtk), lihat platform/redis_store.py


def rakit_konsumen(
    engine: AsyncEngine, redis: Redis, settings: platform.Settings
) -> list[events.KonsumenStream]:
    """Grup konsumen V0 (spec/03 *Consumer V0*) — ditambah tugas yang membangunnya.

    Nama konsumen = nama hos: pekerja yang dimulai ulang di wadah yang sama
    memakai nama yang sama; pesan konsumen yang mati diklaim `XAUTOCLAIM`.
    """
    hos = platform.nama_hos()
    return [
        # Behavior projector (5.1) — SEMUA event, wajib (spec/03). Proyektornya total
        # & idempoten: kegagalan hanya transien (basis data/Redis), yang diulang
        # menyelesaikannya — bukan event yang dijatuhkan diam-diam.
        events.KonsumenStream(
            engine=engine,
            redis=redis,
            awalan=settings.redis_prefix,
            grup="proyektor",
            nama=f"proyektor-{hos}",
            jenis=intelligence.JENIS_EVENT,
            tangani=intelligence.proyeksikan_perilaku,
        ),
        # Pola perilaku (5.2) — konsumen `habit.*` (spec/03 "Habit streak"): hitung
        # ulang pola hari/waktu/konsistensi habit → memori behavioral. Idempoten
        # (upsert per pola), jadi diulang aman.
        events.KonsumenStream(
            engine=engine,
            redis=redis,
            awalan=settings.redis_prefix,
            grup="pola",
            nama=f"pola-{hos}",
            jenis=intelligence.JENIS_POLA,
            tangani=intelligence.deteksi_pola_habit,
        ),
        # Human State (5.3) — konsumen `checkin.logged`: metrik harian {value,
        # confidence, evidence_count} → human_states. Idempoten (upsert per hari).
        events.KonsumenStream(
            engine=engine,
            redis=redis,
            awalan=settings.redis_prefix,
            grup="human-state",
            nama=f"human-state-{hos}",
            jenis=intelligence.JENIS_KEADAAN,
            tangani=intelligence.hitung_human_state,
        ),
        # Recommendation engine (5.5) — `habit.skipped` membuat rekomendasi berskor,
        # `checkin.logged` menyegarkan konteks energinya (spec/03 Recommendation trigger,
        # boleh gagal). Idempoten (id per habit+tanggal, ON CONFLICT DO NOTHING).
        events.KonsumenStream(
            engine=engine,
            redis=redis,
            awalan=settings.redis_prefix,
            grup="rekomendasi",
            nama=f"rekomendasi-{hos}",
            jenis=intelligence.JENIS_REKOMENDASI,
            tangani=intelligence.sarankan,
        ),
        # Memory extractor (3.6) — `journal.created`, `mood.logged`; boleh gagal & diulang.
        events.KonsumenStream(
            engine=engine,
            redis=redis,
            awalan=settings.redis_prefix,
            grup="memori",
            nama=f"memori-{hos}",
            jenis=memory.JENIS_EVENT,
            tangani=memory.ekstrak,
        ),
    ]


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
    vektor = platform.klien_vektor_dari(settings)
    try:
        # B-40 · S4: pekerja membaca event SEMUA pengguna lewat fungsi sempit — sebagai
        # anggota hvx_app DAN hvx_pekerja; api sebaliknya menolak peran ini.
        await platform.pastikan_peran_aplikasi(engine, pekerja=True)
        relay = events.Relay(engine, redis, settings.redis_prefix)
        konsumen = rakit_konsumen(engine, redis, settings)
        for k in konsumen:
            await k.siapkan()
        penyelaras = (
            memory.PenyelarasVektor(
                engine, vektor, platform.penyemat_dari(settings), settings.qdrant_koleksi
            )
            if vektor
            else None
        )
        # Sesi yang lahir selama tenggang (login untuk membatalkan) dicabut sesudah akunnya
        # terhapus; titik Qdrant dibuang hanya bila Qdrant dipasang di proses ini.
        sesi = identity.PenyimpanSesi(
            redis, settings.redis_prefix, settings.access_token_ttl_s, settings.refresh_token_ttl_s
        )
        buang_titik = (
            partial(memory.buang_titik_pengguna, vektor, settings.qdrant_koleksi)
            if vektor
            else None
        )

        async def sapu_hapus_akun() -> int:
            return await identity.sapu_akun_jatuh_tempo(
                engine,
                settings,
                sesi=sesi,
                buang_titik=buang_titik,
                sesudah=(partial(platform.lupakan_idempotensi, redis, settings.redis_prefix),),
            )

        putaran = 0

        async def relay_sekali() -> None:
            nonlocal putaran
            await relay.putaran()
            putaran += 1
            if putaran % PANGKAS_TIAP == 0:
                await relay.pangkas()
                await events.pangkas_mati(redis, settings.redis_prefix)

        tugas = [asyncio.create_task(_ulang("relay", relay_sekali, JEDA_RELAY_S, berhenti))]
        tugas += [
            asyncio.create_task(_ulang(f"konsumen:{k.grup}", k.putaran, 0.0, berhenti))
            for k in konsumen
        ]
        tugas.append(
            asyncio.create_task(
                _ulang("sapuan-hapus-akun", sapu_hapus_akun, JEDA_SAPUAN_HAPUS_S, berhenti)
            )
        )
        if penyelaras:
            tugas.append(
                asyncio.create_task(
                    _ulang("penyelaras-vektor", penyelaras.putaran, JEDA_SELARAS_S, berhenti)
                )
            )
        else:
            log.warning("pekerja.tanpa_vektor", alasan="HVX_QDRANT_URL kosong — memori tak disemat")
        log.info(
            "pekerja.mulai",
            konsumen=[k.grup for k in konsumen],
            vektor=penyelaras is not None,
            sapuan_hapus_akun=True,
        )
        await berhenti.wait()
        for t in tugas:
            t.cancel()
        await asyncio.gather(*tugas, return_exceptions=True)
    finally:
        if vektor:
            await vektor.tutup()
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
