"""Tugas terjadwal per jam lokal pengguna — spec/08 7.3.

Tugas malam V1 — agregat (8.x), hasil prediksi (10.1), Weekly Review Minggu 20:00 (11.4,
naskah `138` §7.21) — berjalan pada jam **lokal** tiap pengguna, bukan jam server, dan
**tepat sekali** per pengguna per hari lokal.

* **Tepat sekali dijamin basis data, bukan pekerja.** Klaim `(user_id, task, for_date)`
  ditulis ke `scheduled_runs` di transaksi yang SAMA dengan kerjanya: kerja yang gagal
  membatalkan klaimnya (dicoba lagi putaran berikutnya); pekerja kedua yang serentak
  tertahan indeks unik sampai yang pertama selesai, lalu `ON CONFLICT DO NOTHING`.
* **Jam lokal, dua hari ke belakang.** `tugas_jatuh_tempo` (spec/01 §12) melihat hari ini
  dan kemarin menurut `profiles.timezone`, tidak pernah sebelum hari akunnya dibuat.
  Pindah zona ke timur (hari lokal melompat) tidak melewatkan hari; pindah ke barat
  (hari lokal mundur ke yang sudah dikerjakan) tidak menggandakannya — kunci primer.
* **Satu pengguna yang gagal tidak menahan yang lain.** Galatnya dicatat tanpa isi
  (`platform` menyaring galat basis data), lalu putaran lanjut ke pengguna berikutnya —
  dan ke HALAMAN berikutnya: jatuh tempo dibaca per halaman dengan kursor
  `(for_date, user_id)`. 🔴 Versi pertama membaca satu halaman `LIMIT batas`; klaim yang
  gagal batal, jadi baris yang sama kembali di depan tiap putaran, dan `batas` pengguna
  yang selalu gagal menahan semua pengguna di belakangnya (tinjauan kontrak S7, K2).

Daftar tugasnya `TUGAS_TERJADWAL` — dirakit `hvx.pekerja`, satu putaran per tugas.
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from uuid import UUID

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

log = structlog.get_logger("hvx.terjadwal")

_POLA_NAMA = re.compile(r"^[a-z][a-z0-9-]{0,39}$")  # = CHECK scheduled_runs.task

_JATUH_TEMPO = text(
    "SELECT user_id, for_date FROM tugas_jatuh_tempo(:tugas, :menit, :batas, :tanggal, :user)"
)
_KLAIM = text(
    "INSERT INTO scheduled_runs (user_id, task, for_date) VALUES (:user_id, :tugas, :for_date) "
    "ON CONFLICT DO NOTHING RETURNING for_date"
)


@dataclass(frozen=True)
class TugasTerjadwal:
    """Satu tugas: namanya, menit sejak tengah malam LOKAL saat ia jatuh tempo, dan kerjanya.

    `kerjakan(conn, user_id, for_date)` berjalan di transaksi pengguna yang sama dengan
    klaimnya — ia tidak boleh membuka transaksinya sendiri, atau *tepat sekali* hilang.
    """

    nama: str
    menit_lokal: int
    kerjakan: Callable[[AsyncConnection, UUID, date], Awaitable[None]]

    def __post_init__(self) -> None:
        if not _POLA_NAMA.fullmatch(self.nama):
            raise ValueError(f"nama tugas terjadwal wajib kebab-case pendek: {self.nama!r}")
        if not 0 <= self.menit_lokal < 24 * 60:
            raise ValueError(f"menit_lokal di luar satu hari: {self.menit_lokal}")


# Belum ada tugas di Sprint 7 — pengisinya spec/08 8.1 (agregat malam), 10.1 (hasil
# prediksi), 11.4 (Weekly Review Minggu 20:00). Gerbangnya lebih dulu (arch/10 §1).
TUGAS_TERJADWAL: tuple[TugasTerjadwal, ...] = ()


async def jalankan_jatuh_tempo(
    engine: AsyncEngine, tugas: TugasTerjadwal, *, batas: int = 100
) -> int:
    """Kerjakan `tugas` untuk tiap (pengguna, hari lokal) yang jatuh tempo — jumlah yang selesai.

    `engine` = engine proses pekerja (anggota `hvx_pekerja`): hanya peran itu yang boleh
    memanggil `tugas_jatuh_tempo`. `batas` = ukuran satu halaman; satu panggilan membaca
    halaman demi halaman sampai habis, jadi yang gagal tidak menutupi yang di belakangnya.
    """
    selesai = 0
    setelah: tuple[date, UUID] | None = None
    while True:
        async with platform.transaksi_sistem(engine) as conn:
            hasil = await conn.execute(
                _JATUH_TEMPO,
                {
                    "tugas": tugas.nama,
                    "menit": tugas.menit_lokal,
                    "batas": batas,
                    "tanggal": setelah[0] if setelah else date.min,
                    "user": setelah[1] if setelah else UUID(int=0),
                },
            )
            halaman = [(b.user_id, b.for_date) for b in hasil]
        for user_id, for_date in halaman:
            if await _kerjakan_satu(engine, tugas, user_id, for_date):
                selesai += 1
        if len(halaman) < max(1, min(batas, 500)):  # = LIMIT fungsi
            return selesai
        berikut = (halaman[-1][1], halaman[-1][0])
        if setelah is not None and berikut <= setelah:  # kursor tak maju: jangan berputar
            log.error("terjadwal.kursor_macet", tugas=tugas.nama)
            return selesai
        setelah = berikut


async def _kerjakan_satu(
    engine: AsyncEngine, tugas: TugasTerjadwal, user_id: UUID, for_date: date
) -> bool:
    """Klaim + kerja satu (pengguna, hari) dalam SATU transaksi — `True` bila selesai di sini.

    Tugas malam MENURUNKAN data, maka memegang kunci turunan pengguna seperti konsumen
    (`platform.kunci_turunan`, S3): hapus kategori Privacy Center yang sedang berjalan
    ditunggu. 🔴 Tinjauan kontrak S7 (K8): versi pertama tidak memegangnya."""
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            await platform.kunci_turunan(conn, user_id)
            klaim = await conn.execute(
                _KLAIM, {"user_id": user_id, "tugas": tugas.nama, "for_date": for_date}
            )
            if klaim.first() is None:  # pekerja lain lebih dulu — dan sudah commit
                return False
            await tugas.kerjakan(conn, user_id, for_date)
    except Exception:
        log.exception("terjadwal.gagal", tugas=tugas.nama, user_id=str(user_id))
        return False
    return True
