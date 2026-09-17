"""Pemeriksaan kesehatan — `/health` menyebut ketergantungannya (arch/09 §5 aturan 4).

Tiap ketergantungan diperiksa **serentak** dengan batas waktu masing-masing,
jadi satu ketergantungan yang menggantung tidak menahan jawaban untuk yang
lain.

Keputusan bentuk yang perlu dinyatakan: spesifikasi (spec/07 0.3) menuliskan
jalur sehatnya — `200 {status, version, db, redis}`. Kalau salah satu
ketergantungan mati, jawabannya **503** dengan bentuk yang sama dan
`status: "degraded"`. Pemeriksa kesehatan (Docker, penyeimbang beban) hanya
membaca kode status; `200` untuk basis data yang mati berarti tidak ada yang
pernah tahu.

🔴 **Kenapa bukan `asyncio.wait_for`.** Versi pertama memakainya, dan ia
menunggu PEMBATALAN pemeriksaan selesai sebelum kembali. Pembatalan ping
asyncpg yang tersangkut membuka koneksi BARU untuk mengirim CancelRequest —
tanpa batas waktu dari sisi klien. Diukur saat PostgreSQL berhenti menjawab:
`HVX_HEALTH_TIMEOUT_S=1`, jawaban `/health` datang sesudah **60 detik**, dan
Redis ikut menunggu. Sekarang pemeriksaan yang lewat waktu dibatalkan **di
belakang**; laporannya tidak menunggu pembersihan itu.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from typing import Literal

import structlog

KeadaanKetergantungan = Literal["ok", "down"]
Pemeriksaan = Callable[[], Awaitable[None]]

log = structlog.get_logger(__name__)

# Tugas yang sudah dibatalkan tetapi pembersihannya belum selesai. Rujukan kuat
# ini mencegah tugasnya dikumpulkan sampah di tengah jalan.
_tertinggal: set[asyncio.Task[None]] = set()


def _lepas(tugas: asyncio.Task[None]) -> None:
    _tertinggal.discard(tugas)
    if not tugas.cancelled():
        tugas.exception()  # dibaca supaya asyncio tidak mengeluh "never retrieved"


async def _jalankan(nama: str, periksa: Pemeriksaan, timeout_s: float) -> KeadaanKetergantungan:
    async def _bungkus() -> None:
        await periksa()

    tugas = asyncio.ensure_future(_bungkus())
    selesai, _ = await asyncio.wait({tugas}, timeout=timeout_s)
    if tugas not in selesai:
        tugas.cancel()
        _tertinggal.add(tugas)
        tugas.add_done_callback(_lepas)
        log.warning("health.dependency_timeout", dependency=nama, timeout_s=timeout_s)
        return "down"
    if tugas.cancelled():
        log.warning("health.dependency_cancelled", dependency=nama)
        return "down"
    galat = tugas.exception()
    if galat is not None:
        # Pesan galat TIDAK masuk ke jawaban HTTP (bisa memuat DSN atau host
        # internal) — hanya ke log, dan hanya jenisnya.
        log.warning("health.dependency_down", dependency=nama, error_type=type(galat).__name__)
        return "down"
    return "ok"


async def laporan_kesehatan(
    versi: str,
    pemeriksaan: Mapping[str, Pemeriksaan],
    timeout_s: float,
) -> tuple[int, dict[str, str]]:
    nama = list(pemeriksaan)
    hasil = await asyncio.gather(*(_jalankan(n, pemeriksaan[n], timeout_s) for n in nama))
    keadaan = dict(zip(nama, hasil, strict=True))
    sehat = all(k == "ok" for k in keadaan.values())
    badan: dict[str, str] = {"status": "ok" if sehat else "degraded", "version": versi}
    badan.update(keadaan)
    return (200 if sehat else 503), badan
