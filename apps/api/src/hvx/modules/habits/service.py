"""Aturan `habits` — spec/07 2.2–2.4.

* **2.2** habit + jadwal + `adaptive_tiers` — *“tier turun saat energi rendah”*
  (`tier.py`). `period` × `target_count` × `schedule` diperiksa bersama —
  juga saat `PATCH` mengubah salah satunya saja, terhadap baris yang tersimpan.
* Tautan ke goal dijaga FK komposit `(goal_id, user_id)` (B-41): `habits`
  tidak boleh membaca tabel `goals` (spec/06 aturan 5), jadi goal yang tidak
  ada — atau milik pengguna lain — dikenali dari penolakan basis data.
* Hapus = hapus-lunak (spec/01 `deleted_at`); penyelesaiannya tetap tersimpan.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository
from .schemas import BuatHabit, DaftarHabit, Habit, UbahHabit, periksa_jadwal, periksa_target


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
