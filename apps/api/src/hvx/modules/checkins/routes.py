"""Rute `checkins` — spec/04 *Catatan harian* (spec/07 2.5–2.6).

`PUT /checkins/{for_date}` idempoten dengan sendirinya (PUT = ganti) — spec/04
menjanjikan `Idempotency-Key` untuk `POST`/`PATCH`, bukan `PUT`.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import Checkin, DaftarCheckin, IsiCheckin

router = APIRouter(prefix="/v1", tags=["checkins"])

# `from` kata kunci Python — namanya di URL tetap `from` (spec/04).
Dari = Annotated[date | None, Query(alias="from")]
Sampai = Annotated[date | None, Query(alias="to")]


@router.get("/checkins", response_model=DaftarCheckin)
async def daftar_checkin(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    dari: Dari = None,
    sampai: Sampai = None,
) -> DaftarCheckin:
    return await service.daftar(
        platform.engine_dari(request), pengguna.user_id, dari=dari, sampai=sampai
    )


@router.put(
    "/checkins/{for_date}",
    response_model=Checkin,
    responses={201: {"model": Checkin, "description": "check-in tanggal itu baru dibuat"}},
)
async def simpan_checkin(
    request: Request, for_date: date, badan: IsiCheckin, pengguna: identity.PenggunaDiperlukan
) -> JSONResponse:
    hasil = await service.simpan(platform.engine_dari(request), pengguna.user_id, for_date, badan)
    return JSONResponse(
        status_code=201 if hasil.baru else 200, content=jsonable_encoder(hasil.checkin)
    )
