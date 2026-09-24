"""Aturan `checkins` — spec/07 2.5 (`daily_checkins`, upsert per tanggal) · 2.6 (`mood_entries`).

* **2.5** `PUT /checkins/{for_date}` dua kali → SATU baris: `UNIQUE (user_id,
  for_date)` + `ON CONFLICT DO UPDATE`, satu pernyataan — dua PUT serentak
  tidak bisa keduanya menyisipkan. PUT = ganti (lihat `IsiCheckin`).
* `for_date` tanggal lokal perangkat — batasnya tanggal paling maju di Bumi
  (`platform.tanggal_paling_maju`), sama dengan penyelesaian habit (2.3).
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository
from .repository import HasilSimpan
from .schemas import DaftarCheckin, IsiCheckin

# `GET /checkins` tanpa rentang: satu bulan terakhir yang tercatat.
TERAKHIR_BAWAAN = 31
# Rentang paling lebar yang dijawab sekaligus — satu tahun kabisat.
RENTANG_MAKS_HARI = 366


async def simpan(
    engine: AsyncEngine, user_id: UUID, for_date: date, isi: IsiCheckin
) -> HasilSimpan:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if for_date > await platform.tanggal_paling_maju(conn):
            raise platform.GalatApi(
                422, "for_date_in_future", "Tanggal itu belum terjadi di mana pun."
            )
        return await repository.simpan(
            conn,
            user_id=user_id,
            for_date=for_date,
            energy=isi.energy,
            focus=isi.focus,
            sleep_hours=isi.sleep_hours,
            note=isi.note,
        )


async def daftar(
    engine: AsyncEngine, user_id: UUID, *, dari: date | None, sampai: date | None
) -> DaftarCheckin:
    if (dari is None) != (sampai is None):
        # Setengah rentang ditolak, bukan ditebak ujung satunya.
        raise platform.GalatApi(400, "invalid_request", "`from` dan `to` dikirim bersama.")
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if dari is None or sampai is None:
            checkin = await repository.terakhir(conn, user_id=user_id, batas=TERAKHIR_BAWAAN)
        else:
            if dari > sampai or sampai - dari >= timedelta(days=RENTANG_MAKS_HARI):
                raise platform.GalatApi(
                    400,
                    "invalid_request",
                    f"Rentang tanggal wajib `from` ≤ `to`, paling lebar {RENTANG_MAKS_HARI} hari.",
                )
            checkin = await repository.rentang(conn, user_id=user_id, dari=dari, sampai=sampai)
    return DaftarCheckin(items=checkin)
