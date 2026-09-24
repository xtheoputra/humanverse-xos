"""Aturan `habits` — spec/07 2.2–2.4.

* **2.2** habit + jadwal + `adaptive_tiers` — *“tier turun saat energi rendah”*
  (`tier.py`). `period` × `target_count` × `schedule` diperiksa bersama —
  juga saat `PATCH` mengubah salah satunya saja, terhadap baris yang tersimpan.
* Tautan ke goal dijaga FK komposit `(goal_id, user_id)` (B-41): `habits`
  tidak boleh membaca tabel `goals` (spec/06 aturan 5), jadi goal yang tidak
  ada — atau milik pengguna lain — dikenali dari penolakan basis data.
* Hapus = hapus-lunak (spec/01 `deleted_at`); penyelesaiannya tetap tersimpan.
* **2.3** penyelesaian idempoten per tanggal: kirim ulang `for_date` yang sama
  → `200` dengan baris yang sudah ada, bukan baris kedua dan bukan `409`
  (spec/04). `for_date` adalah tanggal LOKAL perangkat (spec/01) — ditolak
  hanya bila belum terjadi di tempat mana pun di Bumi
  (`platform.tanggal_paling_maju`), sebab perangkat yang sedang bepergian bisa
  berada di zona lain dari `profiles.timezone`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository
from .schemas import (
    BuatHabit,
    CatatPenyelesaian,
    DaftarHabit,
    Habit,
    Penyelesaian,
    UbahHabit,
    periksa_jadwal,
    periksa_target,
)


def _tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Habit tidak ditemukan.")


def _galat_integritas(galat: IntegrityError) -> platform.GalatApi | None:
    p = platform.rincian_pelanggaran(galat)
    if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "habits_pkey":
        return platform.GalatApi(409, "already_exists", "Habit dengan id ini sudah ada.")
    if p.sqlstate == platform.FOREIGN_KEY_VIOLATION:
        # FK komposit ke goals: goal tidak ada ATAU milik pengguna lain — jawabannya sama.
        return platform.GalatApi(422, "goal_not_found", "Goal tidak ditemukan.")
    return None


async def daftar(engine: AsyncEngine, user_id: UUID, *, status: str | None) -> DaftarHabit:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        habit = await repository.daftar(conn, user_id=user_id, status=status)
    return DaftarHabit(items=habit)


async def buat(engine: AsyncEngine, user_id: UUID, badan: BuatHabit) -> Habit:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            return await repository.sisip(
                conn,
                user_id=user_id,
                id_=badan.id,
                goal_id=badan.goal_id,
                title=badan.title,
                period=badan.period,
                target_count=badan.target_count,
                schedule=badan.schedule.model_dump(exclude_none=True),
                adaptive_tiers=[t.model_dump(exclude_none=True) for t in badan.adaptive_tiers],
            )
    except IntegrityError as galat:
        dikenali = _galat_integritas(galat)
        if dikenali is None:
            raise
        raise dikenali from None


def _perubahan(badan: UbahHabit) -> dict[str, Any]:
    perubahan: dict[str, Any] = {}
    for medan in badan.model_fields_set:
        nilai = getattr(badan, medan)
        if medan == "schedule":
            nilai = nilai.model_dump(exclude_none=True)
        elif medan == "adaptive_tiers":
            nilai = [t.model_dump(exclude_none=True) for t in nilai]
        perubahan[medan] = nilai
    return perubahan


async def ubah(engine: AsyncEngine, user_id: UUID, habit_id: UUID, badan: UbahHabit) -> Habit:
    perubahan = _perubahan(badan)
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            kini = await repository.ambil_untuk_ubah(conn, habit_id)
            if kini is None:
                raise _tidak_ditemukan()
            if not perubahan:  # `PATCH {}` tidak menyentuh baris — updated_at tetap
                return kini
            period = perubahan.get("period", kini.period)
            try:
                periksa_target(period, perubahan.get("target_count", kini.target_count))
                periksa_jadwal(period, perubahan.get("schedule", kini.schedule))
            except ValueError as salah:
                # Badannya sah sendiri; yang salah paduannya dengan baris tersimpan.
                raise platform.GalatApi(422, "invalid_habit", str(salah)) from None
            habit = await repository.ubah(conn, habit_id, perubahan)
    except IntegrityError as galat:
        dikenali = _galat_integritas(galat)
        if dikenali is None:
            raise
        raise dikenali from None
    if habit is None:  # pragma: no cover - baris terkunci di transaksi yang sama
        raise _tidak_ditemukan()
    return habit


async def hapus(engine: AsyncEngine, user_id: UUID, habit_id: UUID) -> None:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if not await repository.hapus(conn, habit_id):
            raise _tidak_ditemukan()


# ── spec/07 2.3 — penyelesaian ───────────────────────────────────────────────


@dataclass(frozen=True)
class HasilCatat:
    penyelesaian: Penyelesaian
    baru: bool  # False = tanggal itu sudah tercatat; baris lama yang dikembalikan


async def catat(
    engine: AsyncEngine, user_id: UUID, habit_id: UUID, badan: CatatPenyelesaian
) -> HasilCatat:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        habit = await repository.ambil_untuk_catat(conn, habit_id)
        if habit is None:
            raise _tidak_ditemukan()
        if badan.tier_used is not None and badan.tier_used >= len(habit.adaptive_tiers):
            raise platform.GalatApi(
                422, "invalid_tier", "tier_used di luar adaptive_tiers habit ini."
            )
        if badan.for_date > await platform.tanggal_paling_maju(conn):
            raise platform.GalatApi(
                422, "for_date_in_future", "Tanggal itu belum terjadi di mana pun."
            )
        baru = await repository.sisip_selesai(
            conn,
            habit_id=habit_id,
            for_date=badan.for_date,
            status=badan.status,
            tier_used=badan.tier_used,
            note=badan.note,
        )
        if baru is not None:
            return HasilCatat(baru, baru=True)
        ada = await repository.selesai_pada(conn, habit_id, badan.for_date)
    if ada is None:  # pragma: no cover - habit terkunci, dan DO NOTHING berarti barisnya ada
        raise _tidak_ditemukan()
    return HasilCatat(ada, baru=False)


async def hapus_catatan(engine: AsyncEngine, user_id: UUID, habit_id: UUID, for_date: date) -> None:
    """Idempoten: tanggal yang tidak tercatat tetap `204` — "batalkan" dari perangkat
    luring yang terkirim dua kali tidak berubah menjadi galat."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if await repository.ambil_untuk_catat(conn, habit_id) is None:
            raise _tidak_ditemukan()
        await repository.hapus_selesai(conn, habit_id, for_date)
