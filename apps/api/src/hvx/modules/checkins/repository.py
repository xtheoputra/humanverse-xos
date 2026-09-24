"""SQL modul `checkins` — hanya tabel miliknya: daily_checkins · mood_entries (spec/06 aturan 5).

SQL statis seluruhnya (lihat `profile/repository.py`). Tiap fungsi menerima
koneksi dari lapisan layanan, di dalam `platform.transaksi_pengguna`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Checkin

# spec/07 2.5 — upsert per tanggal: `UNIQUE (user_id, for_date)` + `DO UPDATE`.
# PUT = GANTI: tiap kolom diambil dari badan (EXCLUDED), termasuk yang kosong.
# `xmax = 0` membedakan baris yang baru disisipkan dari yang diperbarui — tanpa
# kueri kedua, dan tanpa membaca-lalu-menulis yang kalah balapan.
_SIMPAN = text(
    """
    INSERT INTO daily_checkins (user_id, for_date, energy, focus, sleep_hours, note)
    VALUES (:user_id, :for_date, CAST(:energy AS smallint), CAST(:focus AS smallint),
            CAST(:sleep_hours AS numeric), CAST(:note AS text))
    ON CONFLICT (user_id, for_date) DO UPDATE SET
      energy = EXCLUDED.energy,
      focus = EXCLUDED.focus,
      sleep_hours = EXCLUDED.sleep_hours,
      note = EXCLUDED.note
    RETURNING id, for_date, energy, focus, sleep_hours, note, created_at, updated_at,
              (xmax = 0) AS baru
    """
)

_RENTANG = text(
    """
    SELECT id, for_date, energy, focus, sleep_hours, note, created_at, updated_at
    FROM daily_checkins
    WHERE user_id = :user_id AND for_date BETWEEN :dari AND :sampai
    ORDER BY for_date DESC
    """
)

_TERAKHIR = text(
    """
    SELECT id, for_date, energy, focus, sleep_hours, note, created_at, updated_at
    FROM daily_checkins
    WHERE user_id = :user_id
    ORDER BY for_date DESC
    LIMIT :batas
    """
)

_ENERGI_PADA = text(
    "SELECT energy FROM daily_checkins WHERE user_id = :user_id AND for_date = :for_date"
)


@dataclass(frozen=True)
class HasilSimpan:
    checkin: Checkin
    baru: bool


def _checkin(baris: RowMapping) -> Checkin:
    return Checkin.model_validate({k: v for k, v in baris.items() if k != "baru"})


async def simpan(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    for_date: date,
    energy: int | None,
    focus: int | None,
    sleep_hours: Decimal | None,
    note: str | None,
) -> HasilSimpan:
    baris = (
        (
            await conn.execute(
                _SIMPAN,
                {
                    "user_id": user_id,
                    "for_date": for_date,
                    "energy": energy,
                    "focus": focus,
                    "sleep_hours": sleep_hours,
                    "note": note,
                },
            )
        )
        .mappings()
        .one()
    )
    return HasilSimpan(_checkin(baris), baru=bool(baris["baru"]))


async def rentang(
    conn: AsyncConnection, *, user_id: UUID, dari: date, sampai: date
) -> list[Checkin]:
    hasil = await conn.execute(_RENTANG, {"user_id": user_id, "dari": dari, "sampai": sampai})
    return [_checkin(b) for b in hasil.mappings()]


async def terakhir(conn: AsyncConnection, *, user_id: UUID, batas: int) -> list[Checkin]:
    hasil = await conn.execute(_TERAKHIR, {"user_id": user_id, "batas": batas})
    return [_checkin(b) for b in hasil.mappings()]


async def energi_pada(conn: AsyncConnection, user_id: UUID, for_date: date) -> int | None:
    """Energi check-in pengguna pada tanggal LOKAL itu — dipasang `hvx.main` sebagai
    `pembaca_energi` (K-23): tier habit yang disarankan (spec/07 2.2, naskah 4 §34).

    Berjalan di koneksi PEMANGGIL — transaksi dan RLS-nya sama.
    """
    nilai = (
        await conn.execute(_ENERGI_PADA, {"user_id": user_id, "for_date": for_date})
    ).scalar_one_or_none()
    return int(nilai) if nilai is not None else None
