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
* **Kunci turunan bersama sebelum klaim.** 🔴 Versi pertama tidak mengambilnya: hapus
  kategori yang berjalan selagi kerja belum commit tidak menunggunya, dan turunan dari
  sumber yang sudah dihapus hidup terus (tinjauan keamanan S7, S1 — sama dengan S3 S5–6).
* **Satu pengguna yang gagal tidak menahan yang lain.** Galatnya dicatat tanpa isi
  (`platform` menyaring galat basis data), lalu putaran lanjut ke pengguna berikutnya.

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
    "SELECT user_id, for_date "
    "FROM tugas_jatuh_tempo(:tugas, :menit, :batas, :setelah_tanggal, :setelah_id)"
)
_HALAMAN_MAKS = 500  # = LIMIT `tugas_jatuh_tempo`
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
    memanggil `tugas_jatuh_tempo`. `batas` = ukuran SATU halaman; satu putaran menelusuri
    semua halaman. 🔴 Versi pertama membaca satu halaman saja: kerja yang gagal membatalkan
    klaimnya, jadi pengguna yang selalu gagal kembali di urutan terdepan tiap putaran —
    sebanyak `batas` di antaranya menahan semua pengguna lain (tinjauan keamanan S7, S3).
    """
    halaman = max(1, min(batas, _HALAMAN_MAKS))
    setelah: tuple[date | None, UUID | None] = (None, None)
    selesai = 0
    while True:
        async with platform.transaksi_sistem(engine) as conn:
            hasil = await conn.execute(
                _JATUH_TEMPO,
                {
                    "tugas": tugas.nama,
                    "menit": tugas.menit_lokal,
                    "batas": halaman,
                    "setelah_tanggal": setelah[0],
                    "setelah_id": setelah[1],
                },
            )
            jatuh_tempo = [(b.user_id, b.for_date) for b in hasil]
        for user_id, for_date in jatuh_tempo:
            selesai += await _kerjakan_satu(engine, tugas, user_id, for_date)
        if len(jatuh_tempo) < halaman:
            return selesai
        setelah = (jatuh_tempo[-1][1], jatuh_tempo[-1][0])


async def _kerjakan_satu(
    engine: AsyncEngine, tugas: TugasTerjadwal, user_id: UUID, for_date: date
) -> int:
    """1 bila `tugas` selesai untuk (pengguna, hari) ini; 0 bila sudah diklaim atau gagal."""
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            # Kerja tugas malam MENURUNKAN data (agregat, prediksi, tinjauan) — seperti
            # konsumen pekerja: hapus kategori Privacy Center menunggu commit-nya, dan
            # kerja berikutnya menunggu hapusnya (tinjauan keamanan S7, S1).
            await platform.kunci_turunan(conn, user_id)
            klaim = await conn.execute(
                _KLAIM, {"user_id": user_id, "tugas": tugas.nama, "for_date": for_date}
            )
            if klaim.first() is None:  # pekerja lain lebih dulu — dan sudah commit
                return 0
            await tugas.kerjakan(conn, user_id, for_date)
    except Exception:
        log.exception("terjadwal.gagal", tugas=tugas.nama, user_id=str(user_id))
        return 0
    return 1
