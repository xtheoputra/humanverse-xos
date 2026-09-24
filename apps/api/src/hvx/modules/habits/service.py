"""Aturan `habits` — spec/07 2.2–2.4.

* **2.2** habit + jadwal + `adaptive_tiers` — *“tier turun saat energi rendah”*
  (`tier.py`). `period` × `target_count` × `schedule` diperiksa bersama —
  juga saat `PATCH` mengubah salah satunya saja, terhadap baris yang tersimpan.
* Tautan ke goal: `habits` tidak boleh membaca tabel `goals` (spec/06 aturan
  5), jadi titik rakit menyerahkan `goals.kunci_goal_hidup` (K-23). FK komposit
  `(goal_id, user_id)` (B-41) saja tidak cukup: FK tidak melihat `deleted_at`,
  dan goal yang dihapus-lunak dulu tetap bisa ditaut (tinjauan kontrak Sprint 2,
  F2). Goal dikunci SEBELUM baris habit — urutan kunci yang sama dengan hapus
  goal (goal, lalu habits lewat `lepas_goal`), jadi keduanya tidak saling kunci.
* Paling banyak `repository.DAFTAR_MAKS` habit hidup per pengguna (K-24).
* Hapus = hapus-lunak (spec/01 `deleted_at`); penyelesaiannya tetap tersimpan.
* **2.3** penyelesaian idempoten per tanggal: kirim ulang `for_date` yang sama
  → `200` dengan baris yang sudah ada, bukan baris kedua dan bukan `409`
  (spec/04). `for_date` adalah tanggal LOKAL perangkat (spec/01) — ditolak
  hanya bila belum terjadi di tempat mana pun di Bumi
  (`platform.tanggal_paling_maju`), sebab perangkat yang sedang bepergian bisa
  berada di zona lain dari `profiles.timezone`.
* **2.4** rentetan & tingkat penyelesaian — `rentetan.py`. "Hari ini" butuh
  zona waktu pengguna, milik `profile`: `habits` tidak boleh mengimpornya
  (aturan 3) maupun membaca tabelnya (aturan 5), jadi titik rakit `hvx.main`
  menyerahkan pembacanya (**K-23**, pola pendengar pendaftaran K-17).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from . import repository
from .rentetan import awal_riwayat, hitung_rentetan
from .schemas import (
    BuatHabit,
    CatatPenyelesaian,
    DaftarHabit,
    Habit,
    HabitHari,
    HariHabit,
    JawabanRentetan,
    Penyelesaian,
    UbahHabit,
    periksa_jadwal,
    periksa_target,
)
from .tier import tier_untuk_energi

# (koneksi pemanggil, user_id) → zona IANA dari profil, atau None — K-23.
PembacaZonaWaktu = Callable[[AsyncConnection, UUID], Awaitable[str | None]]
# (koneksi pemanggil, user_id, tanggal lokal) → energi check-in 1–5, atau None — K-23.
PembacaEnergi = Callable[[AsyncConnection, UUID, date], Awaitable[int | None]]
# (koneksi pemanggil, goal_id) → goal hidup & kini terkunci berbagi? — K-23.
PembacaGoalHidup = Callable[[AsyncConnection, UUID], Awaitable[bool]]
ZONA_BAWAAN = "UTC"  # spec/01 profiles.timezone DEFAULT 'UTC'


def _tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Habit tidak ditemukan.")


def _goal_tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(422, "goal_not_found", "Goal tidak ditemukan.")


def _galat_integritas(galat: IntegrityError) -> platform.GalatApi | None:
    p = platform.rincian_pelanggaran(galat)
    if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "habits_pkey":
        return platform.GalatApi(409, "already_exists", "Habit dengan id ini sudah ada.")
    if p.sqlstate == platform.FOREIGN_KEY_VIOLATION:
        # FK komposit ke goals: goal dihapus-keras di antara pemeriksaan dan tulisan.
        return _goal_tidak_ditemukan()
    return None


async def daftar(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    status: str | None,
    for_date: date | None = None,
    pembaca_energi: PembacaEnergi | None = None,
) -> DaftarHabit:
    """Daftar habit; dengan `for_date`, tiap habit membawa keadaannya pada tanggal itu —
    penyelesaiannya dan tier yang disarankan dari energi check-in (spec/07 2.2, naskah 4 §34).
    """
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        habit = await repository.daftar(conn, user_id=user_id, status=status)
        if for_date is None:
            return DaftarHabit(items=[HabitHari(**h.model_dump()) for h in habit])
        if pembaca_energi is None:
            raise RuntimeError("pembaca_energi wajib untuk daftar habit ber-for_date (K-23)")
        energi = await pembaca_energi(conn, user_id, for_date)
        selesai = await repository.selesai_tanggal(conn, user_id, for_date)
    return DaftarHabit(
        items=[
            HabitHari(
                **h.model_dump(),
                day=HariHabit(
                    for_date=for_date,
                    completion=selesai.get(h.id),
                    energy=energi,
                    suggested_tier=tier_untuk_energi(len(h.adaptive_tiers), energi),
                ),
            )
            for h in habit
        ]
    )


async def baca_habit(engine: AsyncEngine, user_id: UUID, habit_id: UUID) -> Habit | None:
    """Habit itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi, E-171)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.ambil(conn, habit_id)


async def baca_penyelesaian(
    engine: AsyncEngine, user_id: UUID, completion_id: UUID
) -> Penyelesaian | None:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.selesai_id(conn, completion_id)


async def buat(
    engine: AsyncEngine, user_id: UUID, badan: BuatHabit, *, goal_hidup: PembacaGoalHidup
) -> Habit:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            if badan.goal_id is not None and not await goal_hidup(conn, badan.goal_id):
                raise _goal_tidak_ditemukan()
            if await repository.jumlah_serial(conn, user_id) >= repository.DAFTAR_MAKS:
                raise platform.GalatApi(
                    422, "habit_limit_reached", f"Paling banyak {repository.DAFTAR_MAKS} habit."
                )
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


async def ubah(
    engine: AsyncEngine,
    user_id: UUID,
    habit_id: UUID,
    badan: UbahHabit,
    *,
    goal_hidup: PembacaGoalHidup,
) -> Habit:
    perubahan = _perubahan(badan)
    goal_baru = perubahan.get("goal_id")
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            # Goal lebih dulu, baru baris habit — urutan kunci hapus goal (lihat docstring).
            if goal_baru is not None and not await goal_hidup(conn, goal_baru):
                raise _goal_tidak_ditemukan()
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


async def lepas_goal(conn: AsyncConnection, goal_id: UUID) -> None:
    """Pendengar `goals` (K-23): goal yang dihapus-lunak tidak ditaut habit mana pun lagi.

    Berjalan di transaksi PENGHAPUS goal — RLS-nya sama, dan habit yang ditaut
    sesudah goal itu dikunci hidup sudah terlihat (READ COMMITTED).
    """
    await repository.lepas_goal(conn, goal_id)


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
        # Tanggal yang sudah tercatat → baris LAMA, sebelum aturan apa pun diperiksa
        # ulang (spec/04: kirim ulang selalu aman). Dulu tier diperiksa lebih dulu:
        # ulangan identik sesudah tier habit dikurangi menjadi 422 (tinjauan
        # kontrak Sprint 2, F3) — perangkat luring tidak bisa menuntaskan antreannya.
        ada = await repository.selesai_pada(conn, habit_id, badan.for_date)
        if ada is not None:
            return HasilCatat(ada, baru=False)
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


# ── spec/07 2.4 — rentetan ───────────────────────────────────────────────────


async def rentetan(
    engine: AsyncEngine,
    user_id: UUID,
    habit_id: UUID,
    *,
    pembaca_zona_waktu: PembacaZonaWaktu,
) -> JawabanRentetan:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        habit = await repository.ambil(conn, habit_id)
        if habit is None:
            raise _tidak_ditemukan()
        zona = await pembaca_zona_waktu(conn, user_id) or ZONA_BAWAAN
        hari_ini = await platform.hari_ini_di(conn, zona)
        mulai = await repository.mulai_lokal(conn, habit_id, zona) or hari_ini
        riwayat = await repository.riwayat(conn, habit_id, sejak=awal_riwayat(hari_ini))
    hasil = hitung_rentetan(
        period=habit.period,
        target_count=habit.target_count,
        weekdays=habit.schedule.get("weekdays"),
        mulai=mulai,
        hari_ini=hari_ini,
        penyelesaian=riwayat,
    )
    return JawabanRentetan(
        current=hasil.current,
        longest=hasil.longest,
        completion_rate_30d=hasil.completion_rate_30d,
    )
