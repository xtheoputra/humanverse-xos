"""Rute `habits` — spec/04 *Goals & habits* (spec/07 2.2–2.4).

Tiap rute tulis `POST`/`PATCH` menyatakan `platform.Idempoten` (spec/04,
E-165) — dijaga `tests/unit/test_idempotensi_terpasang.py`.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import BuatHabit, DaftarHabit, Habit, StatusHabit, UbahHabit

router = APIRouter(prefix="/v1", tags=["habits"])


@router.get("/habits", response_model=DaftarHabit)
async def daftar_habit(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    status: StatusHabit | None = None,
) -> DaftarHabit:
    return await service.daftar(platform.engine_dari(request), pengguna.user_id, status=status)


@router.post("/habits", status_code=201, response_model=Habit)
async def buat_habit(
    request: Request,
    badan: BuatHabit,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        habit = await service.buat(platform.engine_dari(request), pengguna.user_id, badan)
        return platform.Jawaban(201, habit)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.patch("/habits/{habit_id}", response_model=Habit)
async def ubah_habit(
    request: Request,
    habit_id: UUID,
    badan: UbahHabit,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        habit = await service.ubah(platform.engine_dari(request), pengguna.user_id, habit_id, badan)
        return platform.Jawaban(200, habit)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.delete("/habits/{habit_id}", status_code=204, response_class=Response)
async def hapus_habit(
    request: Request, habit_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Response:
    await service.hapus(platform.engine_dari(request), pengguna.user_id, habit_id)
    return Response(status_code=204)
