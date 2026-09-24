"""Aturan `goals` — spec/07 2.1: goal + milestone + `parent_id` (Goal Graph naskah 4 §9).

Selesai bila: pohon goal 3 tingkat terbaca dalam satu query.

* **Pohon dibaca SATU kueri** (`repository.pohon`, CTE rekursif) — bukan satu
  kueri per anak: goal *LIFE GOAL → Career → Skills → Learning* sudah empat
  tingkat, dan N+1 kueri per tingkat tumbuh bersama pohonnya.
* **Kedalaman dibatasi SAAT MENULIS**, bukan dipotong diam-diam saat membaca:
  goal yang akan menjadi tingkat ke-11 ditolak `422`, sehingga `GET …/tree`
  tidak pernah menyembunyikan goal yang ada.
* **`parent_id` tidak bisa diubah** (spec/04 `PATCH /goals/{id}`: `title?`,
  `status?`, `target_date?`) — lingkaran tidak bisa terbentuk lewat API; satu-
  satunya lingkaran yang mungkin, goal yang menjadi induk dirinya sendiri,
  ditolak skema DAN CHECK basis data.
* **Hapus = hapus-lunak** (spec/04 `204 (soft delete)`); anaknya naik menjadi
  akar — sama dengan hapus-keras spec/01 (`ON DELETE SET NULL (parent_id)`) —
  dan habit yang menautnya dilepas lewat pendengar yang dipasang titik rakit
  (`pendengar_goal_dihapus`, K-23): `habits.goal_id` juga `ON DELETE SET NULL`.
* **Induk dan goal milestone dikunci berbagi** sebelum anak/milestone ditulis
  (`repository.kunci_hidup`) — hapus-lunak serentak tidak meninggalkan yatim.
* **Batas per pengguna** (K-24): `MAKS_GOAL` goal hidup dan `MAKS_MILESTONE`
  milestone per goal — `GET …/tree` dan `GET /goals/{id}` membaca SEMUANYA dalam
  satu jawaban, jadi ukurannya dibatasi SAAT MENULIS (tinjauan keamanan Sprint 2:
  20 ribu goal = 86 MB dan event loop tertahan), sama seperti kedalaman.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from . import repository
from .schemas import (
    BuatGoal,
    BuatMilestone,
    Goal,
    GoalRinci,
    HalamanGoal,
    Milestone,
    SimpulPohon,
    UbahGoal,
    UbahMilestone,
)

# Akar = kedalaman 0 → paling banyak sepuluh tingkat. Naskah 4 §9 menggambar
# lima (LIFE GOAL → Career → Skills → Learning → Habit, dan habit bukan goal).
MAKS_KEDALAMAN = 9
# K-24 — seribu goal hidup dan seratus milestone per goal jauh di atas rencana
# hidup satu orang; di atasnya, satu jawaban `…/tree` bukan lagi jawaban.
MAKS_GOAL = 1_000
MAKS_MILESTONE = 100

# (koneksi penghapus, goal_id) — dipasang titik rakit (K-23): modul yang menaut
# goal melepas tautannya di transaksi hapus yang sama.
PendengarGoalDihapus = Callable[[AsyncConnection, UUID], Awaitable[None]]


def _tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Goal tidak ditemukan.")


def _milestone_tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Milestone tidak ditemukan.")


def _induk_tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(422, "parent_not_found", "Goal induk tidak ditemukan.")


async def daftar(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    status: str | None,
    batas: int,
    kursor: str | None,
) -> HalamanGoal:
    sesudah = platform.baca_kursor_waktu("goals", kursor)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        goal = await repository.daftar(
            conn, user_id=user_id, status=status, batas=batas + 1, sesudah=sesudah
        )
    lanjut = None
    if len(goal) > batas:
        goal = goal[:batas]
        lanjut = platform.kursor_waktu("goals", goal[-1].created_at, goal[-1].id)
    return HalamanGoal(items=goal, next_cursor=lanjut)


async def buat(engine: AsyncEngine, user_id: UUID, badan: BuatGoal) -> Goal:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            if badan.parent_id is not None and not await repository.kunci_hidup(
                conn, badan.parent_id
            ):
                raise _induk_tidak_ditemukan()
            if await repository.jumlah_goal_serial(conn, user_id) >= MAKS_GOAL:
                raise platform.GalatApi(
                    422, "goal_limit_reached", f"Paling banyak {MAKS_GOAL} goal."
                )
            if badan.parent_id is not None:
                jarak = await repository.kedalaman(conn, badan.parent_id, MAKS_KEDALAMAN + 1)
                if jarak is None:
                    raise _induk_tidak_ditemukan()
                if jarak + 1 > MAKS_KEDALAMAN:
                    raise platform.GalatApi(
                        422,
                        "goal_tree_too_deep",
                        f"Pohon goal paling dalam {MAKS_KEDALAMAN + 1} tingkat.",
                    )
            return await repository.sisip(
                conn,
                user_id=user_id,
                id_=badan.id,
                parent_id=badan.parent_id,
                title=badan.title,
                description=badan.description,
                domain=badan.domain,
                target_date=badan.target_date,
            )
    except IntegrityError as galat:
        p = platform.rincian_pelanggaran(galat)
        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "goals_pkey":
            raise platform.GalatApi(
                409, "already_exists", "Goal dengan id ini sudah ada."
            ) from None
        if p.sqlstate == platform.FOREIGN_KEY_VIOLATION:
            # induk dihapus-keras di antara pemeriksaan dan INSERT
            raise _induk_tidak_ditemukan() from None
        raise


async def baca_goal(engine: AsyncEngine, user_id: UUID, goal_id: UUID) -> Goal | None:
    """Goal itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi, E-171)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.ambil(conn, goal_id)


async def baca_milestone(
    engine: AsyncEngine, user_id: UUID, milestone_id: UUID
) -> Milestone | None:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.ambil_milestone(conn, milestone_id)


async def ambil(engine: AsyncEngine, user_id: UUID, goal_id: UUID) -> GoalRinci:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        goal = await repository.ambil(conn, goal_id)
        if goal is None:
            raise _tidak_ditemukan()
        milestone = await repository.milestone_goal(conn, goal_id)
    return GoalRinci(**goal.model_dump(), milestones=milestone)


async def pohon(engine: AsyncEngine, user_id: UUID, goal_id: UUID) -> SimpulPohon:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        baris = await repository.pohon(conn, goal_id, MAKS_KEDALAMAN)
    if not baris:
        raise _tidak_ditemukan()
    return susun_pohon([g for g, _ in baris])


def susun_pohon(goal: list[Goal]) -> SimpulPohon:
    """Pohon bersarang dari baris datar — akar di indeks 0 (urutan `repository.pohon`)."""
    anak: dict[UUID | None, list[Goal]] = {}
    for g in goal[1:]:
        anak.setdefault(g.parent_id, []).append(g)

    def bangun(g: Goal) -> SimpulPohon:
        # Dibangun dari daun ke atas: pydantic menyalin daftar saat validasi, jadi
        # anak yang ditambahkan SESUDAH induknya dibuat tidak akan terlihat.
        return SimpulPohon(**g.model_dump(), children=[bangun(c) for c in anak.get(g.id, [])])

    return bangun(goal[0])


async def ubah(engine: AsyncEngine, user_id: UUID, goal_id: UUID, badan: UbahGoal) -> Goal:
    perubahan: Mapping[str, Any] = badan.model_dump(include=badan.model_fields_set)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if not perubahan:  # `PATCH {}` tidak menyentuh baris — updated_at tetap
            goal = await repository.ambil(conn, goal_id)
            if goal is None:
                raise _tidak_ditemukan()
            return goal
        hasil = await repository.ubah(conn, goal_id, perubahan)
    if hasil is None:
        raise _tidak_ditemukan()
    return hasil.goal


async def hapus(
    engine: AsyncEngine,
    user_id: UUID,
    goal_id: UUID,
    *,
    pendengar: Sequence[PendengarGoalDihapus],
) -> None:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if not await repository.hapus(conn, goal_id):
            raise _tidak_ditemukan()
        for dengar in pendengar:
            await dengar(conn, goal_id)


async def kunci_goal_hidup(conn: AsyncConnection, goal_id: UUID) -> bool:
    """Pintu keluar untuk modul yang MENAUT goal (habits) — dipasang titik rakit (K-23).

    True bila goal ada, belum dihapus, dan terlihat oleh pengguna transaksi ini
    (RLS) — dan goal itu kini terkunci berbagi sampai transaksi pemanggil selesai,
    sehingga hapus-lunak serentak menunggu lalu melepas tautan barunya.
    """
    return await repository.kunci_hidup(conn, goal_id)


async def buat_milestone(
    engine: AsyncEngine, user_id: UUID, goal_id: UUID, badan: BuatMilestone
) -> Milestone:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            if not await repository.kunci_hidup(conn, goal_id):
                raise _tidak_ditemukan()
            if await repository.jumlah_milestone_serial(conn, goal_id) >= MAKS_MILESTONE:
                raise platform.GalatApi(
                    422,
                    "milestone_limit_reached",
                    f"Paling banyak {MAKS_MILESTONE} milestone per goal.",
                )
            milestone = await repository.sisip_milestone(
                conn,
                id_=badan.id,
                goal_id=goal_id,
                title=badan.title,
                position=badan.position,
                due_date=badan.due_date,
            )
    except IntegrityError as galat:
        p = platform.rincian_pelanggaran(galat)
        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "goal_milestones_pkey":
            raise platform.GalatApi(
                409, "already_exists", "Milestone dengan id ini sudah ada."
            ) from None
        raise
    if milestone is None:  # pragma: no cover - goal terkunci hidup di transaksi yang sama
        raise _tidak_ditemukan()
    return milestone


async def ubah_milestone(
    engine: AsyncEngine, user_id: UUID, milestone_id: UUID, badan: UbahMilestone
) -> Milestone:
    perubahan: Mapping[str, Any] = badan.model_dump(include=badan.model_fields_set)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if perubahan:
            milestone = await repository.ubah_milestone(conn, milestone_id, perubahan)
        else:
            # `PATCH {}` tidak menyentuh baris: UPDATE apa pun menggerakkan updated_at.
            milestone = await repository.ambil_milestone(conn, milestone_id)
    if milestone is None:
        raise _milestone_tidak_ditemukan()
    return milestone
