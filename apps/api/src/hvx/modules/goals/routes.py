"""Rute `goals` — spec/04 *Goals & habits* (spec/07 2.1).

Tiap rute tulis `POST`/`PATCH` menyatakan `platform.Idempoten` (spec/04,
E-165) — dijaga `tests/unit/test_idempotensi_terpasang.py`.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import (
    BuatGoal,
    BuatMilestone,
    Goal,
    GoalRinci,
    HalamanGoal,
    Milestone,
    SimpulPohon,
    StatusGoal,
    UbahGoal,
    UbahMilestone,
)

router = APIRouter(prefix="/v1", tags=["goals"])


@router.get("/goals", response_model=HalamanGoal)
async def daftar_goal(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    status: StatusGoal | None = None,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanGoal:
    return await service.daftar(
        platform.engine_dari(request), pengguna.user_id, status=status, batas=limit, kursor=cursor
    )


@router.post("/goals", status_code=201, response_model=Goal)
async def buat_goal(
    request: Request,
    badan: BuatGoal,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        goal = await service.buat(platform.engine_dari(request), pengguna.user_id, badan)
        return platform.Jawaban(201, goal)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.get("/goals/{goal_id}", response_model=GoalRinci)
async def ambil_goal(
    request: Request, goal_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> GoalRinci:
    return await service.ambil(platform.engine_dari(request), pengguna.user_id, goal_id)


@router.get("/goals/{goal_id}/tree", response_model=SimpulPohon)
async def pohon_goal(
    request: Request, goal_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> SimpulPohon:
    return await service.pohon(platform.engine_dari(request), pengguna.user_id, goal_id)


@router.patch("/goals/{goal_id}", response_model=Goal)
async def ubah_goal(
    request: Request,
    goal_id: UUID,
    badan: UbahGoal,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        goal = await service.ubah(platform.engine_dari(request), pengguna.user_id, goal_id, badan)
        return platform.Jawaban(200, goal)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.delete("/goals/{goal_id}", status_code=204, response_class=Response)
async def hapus_goal(
    request: Request, goal_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Response:
    await service.hapus(platform.engine_dari(request), pengguna.user_id, goal_id)
    return Response(status_code=204)


@router.post("/goals/{goal_id}/milestones", status_code=201, response_model=Milestone)
async def buat_milestone(
    request: Request,
    goal_id: UUID,
    badan: BuatMilestone,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        milestone = await service.buat_milestone(
            platform.engine_dari(request), pengguna.user_id, goal_id, badan
        )
        return platform.Jawaban(201, milestone)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.patch("/milestones/{milestone_id}", response_model=Milestone)
async def ubah_milestone(
    request: Request,
    milestone_id: UUID,
    badan: UbahMilestone,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        milestone = await service.ubah_milestone(
            platform.engine_dari(request), pengguna.user_id, milestone_id, badan
        )
        return platform.Jawaban(200, milestone)

    return await idem.jalankan(pengguna.user_id, kerja)
