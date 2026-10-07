"""SQL modul `habits` — hanya tabel miliknya: habits · habit_completions (spec/06 aturan 5).

SQL statis seluruhnya (lihat `profile/repository.py`). Tiap fungsi menerima
koneksi dari lapisan layanan, di dalam `platform.transaksi_pengguna` — RLS
(spec/01 §11) membatasi tiap kueri pada pengguna yang dilayani.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Habit, Penyelesaian

# Batas habit hidup per pengguna (K-24) — ditegakkan SAAT MENULIS
# (`service.buat`), sehingga `GET /habits` tidak pernah memotong daftarnya diam-
# diam (tinjauan kontrak Sprint 2, F9: habit ke-501 hilang dari daftar).
DAFTAR_MAKS = 500

# Batas per pengguna diperiksa SERIAL — lihat goals/repository.py `_KUNCI_HITUNG`.
_KUNCI_HITUNG = text("SELECT pg_advisory_xact_lock(hashtextextended(:kunci, 0))")
_JUMLAH = text("SELECT count(*) FROM habits WHERE user_id = :user_id AND deleted_at IS NULL")

# Goal yang menaut dihapus (lunak) — tautannya dilepas, sama dengan hapus-keras
# spec/01 `ON DELETE SET NULL (goal_id)`. Dipanggil lewat pendengar titik rakit
# (K-23) di transaksi penghapus goal.
_LEPAS_GOAL = text("UPDATE habits SET goal_id = NULL WHERE goal_id = :goal_id")

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

# Penyelesaian menurut id — hanya selama habit-nya belum dihapus.
_SELESAI_ID = text(
    """
    SELECT c.id, c.habit_id, c.for_date, c.status, c.tier_used, c.note, c.source,
           c.completed_at, c.created_at
    FROM habit_completions c
    JOIN habits h ON h.id = c.habit_id
    WHERE c.id = :id AND h.deleted_at IS NULL
    """
)

_SELESAI_TANGGAL = text(
    """
    SELECT id, habit_id, for_date, status, tier_used, note, source, completed_at, created_at
    FROM habit_completions
    WHERE user_id = :user_id AND for_date = :for_date
    """
)

# Baris yang dihapus dipulangkan — pembatalannya diterbitkan sebagai event
# (`habit.completion_retracted`, spec/07 3.2) dengan id baris itu sendiri.
_HAPUS_SELESAI = text(
    """
    DELETE FROM habit_completions
    WHERE habit_id = :habit_id AND for_date = :for_date
    RETURNING id, for_date, clock_timestamp() AS dicabut_pada
    """
)

# ── spec/07 2.4 — rentetan ───────────────────────────────────────────────────

# Tanggal LOKAL habit dibuat, menurut zona profil saat ini — satu-satunya tempat
# cap waktu diubah menjadi tanggal, dan hanya untuk awal habit (hari pertama).
_MULAI_LOKAL = text(
    """
    SELECT (created_at AT TIME ZONE :zona)::date
    FROM habits
    WHERE id = :id AND deleted_at IS NULL
    """
)

# `for_date`, tidak pernah `completed_at`: tanggal lokal saat habit DIJALANKAN
# (spec/01) — lihat rentetan.py. Hanya sejak `:sejak`: rentetan menelusuri paling
# jauh `RIWAYAT_MAKS_HARI` ke belakang, dan membaca SEMUA baris — satu per
# tanggal, sampai tahun 1900 — adalah biaya yang tidak dibatasi apa pun
# (tinjauan keamanan Sprint 2).
_RIWAYAT = text(
    """
    SELECT for_date, status
    FROM habit_completions
    WHERE habit_id = :habit_id AND for_date >= :sejak
    ORDER BY for_date
    """
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


async def jumlah_serial(conn: AsyncConnection, user_id: UUID) -> int:
    """Habit hidup pengguna — sesudah mengambil kunci hitung habit miliknya."""
    await conn.execute(_KUNCI_HITUNG, {"kunci": f"habits:{user_id}"})
    return int((await conn.execute(_JUMLAH, {"user_id": user_id})).scalar_one())


async def lepas_goal(conn: AsyncConnection, goal_id: UUID) -> None:
    await conn.execute(_LEPAS_GOAL, {"goal_id": goal_id})


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


async def selesai_id(conn: AsyncConnection, completion_id: UUID) -> Penyelesaian | None:
    baris = (await conn.execute(_SELESAI_ID, {"id": completion_id})).mappings().first()
    return _penyelesaian(baris) if baris else None


@dataclass(frozen=True)
class SelesaiDicabut:
    id: UUID
    for_date: date
    dicabut_pada: datetime


async def hapus_selesai(
    conn: AsyncConnection, habit_id: UUID, for_date: date
) -> SelesaiDicabut | None:
    """Baris yang dihapus — atau `None` bila tanggal itu memang tidak tercatat."""
    b = (await conn.execute(_HAPUS_SELESAI, {"habit_id": habit_id, "for_date": for_date})).first()
    return SelesaiDicabut(b.id, b.for_date, b.dicabut_pada) if b else None


async def mulai_lokal(conn: AsyncConnection, habit_id: UUID, zona: str) -> date | None:
    nilai = (await conn.execute(_MULAI_LOKAL, {"id": habit_id, "zona": zona})).scalar_one_or_none()
    return nilai if isinstance(nilai, date) else None


async def riwayat(conn: AsyncConnection, habit_id: UUID, sejak: date) -> dict[date, str]:
    hasil = await conn.execute(_RIWAYAT, {"habit_id": habit_id, "sejak": sejak})
    return {b.for_date: str(b.status) for b in hasil}


async def selesai_tanggal(
    conn: AsyncConnection, user_id: UUID, for_date: date
) -> dict[UUID, Penyelesaian]:
    """{habit_id: penyelesaian} semua habit pengguna pada tanggal itu — SATU kueri."""
    hasil = await conn.execute(_SELESAI_TANGGAL, {"user_id": user_id, "for_date": for_date})
    return {p.habit_id: p for p in (_penyelesaian(b) for b in hasil.mappings())}


# ── spec/07 6.2 — tinjauan mingguan (dibaca `intelligence`, di transaksi pemanggil) ──


@dataclass(frozen=True)
class HabitDalamRentang:
    """Satu habit hidup dan catatannya di sebuah rentang tanggal LOKAL."""

    id: UUID
    title: str
    period: str
    target_count: int
    weekdays: tuple[int, ...] | None  # `schedule.weekdays` — None = tiap hari
    status: str
    mulai: date  # tanggal lokal habit dibuat (zona profil SAAT INI)
    adaptive_tiers: tuple[str, ...]  # label tier, berat → ringan
    # {for_date: (status, catatan pengguna)} — catatan `skipped` adalah alasan dari pemiliknya
    catatan: Mapping[date, tuple[str, str | None]]


_HABIT_RENTANG = text(
    """
    SELECT h.id, h.title, h.period, h.target_count, h.schedule, h.adaptive_tiers, h.status,
           (h.created_at AT TIME ZONE :zona)::date AS mulai,
           c.for_date, c.status AS status_catatan, c.note
    FROM habits h
    LEFT JOIN habit_completions c
      ON c.habit_id = h.id AND c.for_date BETWEEN :dari AND :sampai
    WHERE h.user_id = :user_id AND h.deleted_at IS NULL
    ORDER BY h.created_at, h.id, c.for_date
    """
)


async def habit_rentang(
    conn: AsyncConnection, user_id: UUID, dari: date, sampai: date, zona: str
) -> list[HabitDalamRentang]:
    """Habit hidup pengguna beserta catatannya di [dari, sampai] — SATU kueri."""
    hasil = await conn.execute(
        _HABIT_RENTANG, {"user_id": user_id, "dari": dari, "sampai": sampai, "zona": zona}
    )
    urut: dict[UUID, dict[str, Any]] = {}
    for b in hasil.mappings():
        h = urut.setdefault(
            b["id"],
            {
                "id": b["id"],
                "title": b["title"],
                "period": b["period"],
                "target_count": int(b["target_count"]),
                "weekdays": tuple(b["schedule"].get("weekdays") or ()) or None,
                "status": b["status"],
                "mulai": b["mulai"],
                "adaptive_tiers": tuple(
                    str(t.get("label", "")) for t in (b["adaptive_tiers"] or [])
                ),
                "catatan": {},
            },
        )
        if b["for_date"] is not None:
            h["catatan"][b["for_date"]] = (str(b["status_catatan"]), b["note"])
    return [HabitDalamRentang(**h) for h in urut.values()]
