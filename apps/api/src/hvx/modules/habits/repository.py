"""SQL modul `habits` — hanya tabel miliknya: habits · habit_completions (spec/06 aturan 5).

SQL statis seluruhnya (lihat `profile/repository.py`). Tiap fungsi menerima
koneksi dari lapisan layanan, di dalam `platform.transaksi_pengguna` — RLS
(spec/01 §11) membatasi tiap kueri pada pengguna yang dilayani.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Habit, Penyelesaian

# Batas atas daftar habit — habit bukan aliran data; seribu habit aktif bukan
# pemakaian yang V0 layani, dan jawaban tanpa batas bukan jawaban.
DAFTAR_MAKS = 500

_SISIP = text(
    """
    INSERT INTO habits (id, user_id, goal_id, title, period, target_count, schedule,
                        adaptive_tiers)
    VALUES (COALESCE(CAST(:id AS uuid), gen_random_uuid()), :user_id, CAST(:goal_id AS uuid),
            :title, :period, :target_count, CAST(:schedule AS jsonb),
            CAST(:adaptive_tiers AS jsonb))
    RETURNING id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
              created_at, updated_at
    """
)

_AMBIL = text(
    """
    SELECT id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
           created_at, updated_at
    FROM habits
    WHERE id = :id AND deleted_at IS NULL
    """
)

_AMBIL_UNTUK_UBAH = text(
    """
    SELECT id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
           created_at, updated_at
    FROM habits
    WHERE id = :id AND deleted_at IS NULL
    FOR UPDATE
    """
)

_DAFTAR = text(
    """
    SELECT id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
           created_at, updated_at
    FROM habits
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
    ORDER BY created_at, id
    LIMIT :batas
    """
)

_UBAH = text(
    """
    UPDATE habits SET
      title = CASE WHEN :ubah_title THEN CAST(:title AS text) ELSE title END,
      period = CASE WHEN :ubah_period THEN CAST(:period AS text) ELSE period END,
      target_count = CASE WHEN :ubah_target_count THEN CAST(:target_count AS smallint)
                          ELSE target_count END,
      schedule = CASE WHEN :ubah_schedule THEN CAST(:schedule AS jsonb) ELSE schedule END,
      goal_id = CASE WHEN :ubah_goal_id THEN CAST(:goal_id AS uuid) ELSE goal_id END,
      adaptive_tiers = CASE WHEN :ubah_adaptive_tiers THEN CAST(:adaptive_tiers AS jsonb)
                            ELSE adaptive_tiers END,
      status = CASE WHEN :ubah_status THEN CAST(:status AS text) ELSE status END
    WHERE id = :id AND deleted_at IS NULL
    RETURNING id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
              created_at, updated_at
    """
)

_HAPUS = text(
    "UPDATE habits SET deleted_at = now() WHERE id = :id AND deleted_at IS NULL RETURNING id"
)

# ── spec/07 2.3 — penyelesaian ───────────────────────────────────────────────

# Habit dikunci BERBAGI selama penyelesaian dicatat: tier yang diperiksa tidak
# bisa berubah (PATCH menunggu) sebelum penyelesaiannya tersimpan.
_AMBIL_UNTUK_CATAT = text(
    """
    SELECT id, goal_id, title, period, target_count, schedule, adaptive_tiers, status,
           created_at, updated_at
    FROM habits
    WHERE id = :id AND deleted_at IS NULL
    FOR SHARE
    """
)

# `UNIQUE (habit_id, for_date)` + `DO NOTHING`: kirim ulang tanggal yang sama
# tidak menulis baris kedua dan tidak menjadi galat (spec/04 — pencatatan dari
# perangkat luring harus selalu aman diulang). `user_id` dari baris habitnya.
_SISIP_SELESAI = text(
    """
    INSERT INTO habit_completions (habit_id, user_id, for_date, status, tier_used, note)
    SELECT h.id, h.user_id, :for_date, :status, CAST(:tier_used AS smallint),
           CAST(:note AS text)
    FROM habits h
    WHERE h.id = :habit_id AND h.deleted_at IS NULL
    ON CONFLICT (habit_id, for_date) DO NOTHING
    RETURNING id, habit_id, for_date, status, tier_used, note, source, completed_at, created_at
    """
)

_SELESAI_PADA = text(
    """
    SELECT id, habit_id, for_date, status, tier_used, note, source, completed_at, created_at
    FROM habit_completions
    WHERE habit_id = :habit_id AND for_date = :for_date
    """
)

_HAPUS_SELESAI = text(
    "DELETE FROM habit_completions WHERE habit_id = :habit_id AND for_date = :for_date"
)

_BISA_DIUBAH = (
    "title",
    "period",
    "target_count",
    "schedule",
    "goal_id",
    "adaptive_tiers",
    "status",
)
_JSONB = frozenset({"schedule", "adaptive_tiers"})


def _habit(baris: RowMapping) -> Habit:
    return Habit.model_validate(dict(baris))


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    id_: UUID | None,
    goal_id: UUID | None,
    title: str,
    period: str,
    target_count: int,
    schedule: Mapping[str, Any],
    adaptive_tiers: list[Mapping[str, Any]],
) -> Habit:
    baris = (
        (
            await conn.execute(
                _SISIP,
                {
                    "id": id_,
                    "user_id": user_id,
                    "goal_id": goal_id,
                    "title": title,
                    "period": period,
                    "target_count": target_count,
                    "schedule": json.dumps(dict(schedule)),
                    "adaptive_tiers": json.dumps([dict(t) for t in adaptive_tiers]),
                },
            )
        )
        .mappings()
        .one()
    )
    return _habit(baris)


async def ambil(conn: AsyncConnection, habit_id: UUID) -> Habit | None:
    baris = (await conn.execute(_AMBIL, {"id": habit_id})).mappings().first()
    return _habit(baris) if baris else None


async def ambil_untuk_ubah(conn: AsyncConnection, habit_id: UUID) -> Habit | None:
    """Baris dikunci sampai transaksi selesai — dua `PATCH` serentak tidak bisa bersama
    menghasilkan paduan `period` × `target_count` yang tidak pernah diperiksa utuh."""
    baris = (await conn.execute(_AMBIL_UNTUK_UBAH, {"id": habit_id})).mappings().first()
    return _habit(baris) if baris else None


async def daftar(conn: AsyncConnection, *, user_id: UUID, status: str | None) -> list[Habit]:
    hasil = await conn.execute(
        _DAFTAR, {"user_id": user_id, "status": status, "batas": DAFTAR_MAKS}
    )
    return [_habit(b) for b in hasil.mappings()]


async def ubah(conn: AsyncConnection, habit_id: UUID, perubahan: Mapping[str, Any]) -> Habit | None:
    tak_dikenal = sorted(set(perubahan) - set(_BISA_DIUBAH))
    if tak_dikenal:
        raise ValueError(f"kolom habit yang tidak bisa diubah: {tak_dikenal}")
    nilai: dict[str, Any] = {"id": habit_id}
    for k in _BISA_DIUBAH:
        nilai[f"ubah_{k}"] = k in perubahan
        v = perubahan.get(k)
        nilai[k] = json.dumps(v) if k in _JSONB and k in perubahan else v
    baris = (await conn.execute(_UBAH, nilai)).mappings().first()
    return _habit(baris) if baris else None


async def hapus(conn: AsyncConnection, habit_id: UUID) -> bool:
    return (await conn.execute(_HAPUS, {"id": habit_id})).first() is not None


def _penyelesaian(baris: RowMapping) -> Penyelesaian:
    return Penyelesaian.model_validate(dict(baris))


async def ambil_untuk_catat(conn: AsyncConnection, habit_id: UUID) -> Habit | None:
    baris = (await conn.execute(_AMBIL_UNTUK_CATAT, {"id": habit_id})).mappings().first()
    return _habit(baris) if baris else None


async def sisip_selesai(
    conn: AsyncConnection,
    *,
    habit_id: UUID,
    for_date: date,
    status: str,
    tier_used: int | None,
    note: str | None,
) -> Penyelesaian | None:
    """Baris BARU — atau `None` bila tanggal itu sudah tercatat (atau habit-nya tidak ada)."""
    baris = (
        (
            await conn.execute(
                _SISIP_SELESAI,
                {
                    "habit_id": habit_id,
                    "for_date": for_date,
                    "status": status,
                    "tier_used": tier_used,
                    "note": note,
                },
            )
        )
        .mappings()
        .first()
    )
    return _penyelesaian(baris) if baris else None


async def selesai_pada(
    conn: AsyncConnection, habit_id: UUID, for_date: date
) -> Penyelesaian | None:
    baris = (
        (await conn.execute(_SELESAI_PADA, {"habit_id": habit_id, "for_date": for_date}))
        .mappings()
        .first()
    )
    return _penyelesaian(baris) if baris else None


async def hapus_selesai(conn: AsyncConnection, habit_id: UUID, for_date: date) -> None:
    await conn.execute(_HAPUS_SELESAI, {"habit_id": habit_id, "for_date": for_date})
