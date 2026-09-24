"""Rute `journal` — spec/04 *Catatan harian* (spec/07 3.4).

`GET /journal` → `HalamanJurnal` (ringkasan TANPA `body`); `GET /journal/{id}` →
`Jurnal` (dengan `body`). Tiap rute tulis `POST`/`PATCH` menyatakan
`platform.Idempoten` (spec/04, E-165).
"""

from __future__ import annotations

from functools import partial
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import BuatJurnal, HalamanJurnal, Jurnal, UbahJurnal

router = APIRouter(prefix="/v1", tags=["journal"])


DariWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="from")]
SampaiWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="to")]


@router.get("/journal", response_model=HalamanJurnal)
async def daftar_jurnal(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    dari: DariWaktu = None,
    sampai: SampaiWaktu = None,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanJurnal:
    return await service.daftar(
        platform.engine_dari(request),
        pengguna.user_id,
        dari=dari,
        sampai=sampai,
        batas=limit,
        kursor=cursor,
    )


@router.get("/journal/{jurnal_id}", response_model=Jurnal)
async def ambil_jurnal(
    request: Request, jurnal_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Jurnal:
    return await service.ambil(platform.engine_dari(request), pengguna.user_id, jurnal_id)


@router.post("/journal", status_code=201, response_model=Jurnal)
async def buat_jurnal(
    request: Request,
    badan: BuatJurnal,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    engine = platform.engine_dari(request)

    async def kerja() -> platform.Jawaban:
        jurnal = await service.buat(engine, pengguna.user_id, badan)
        return platform.Jawaban(201, jurnal, jurnal.id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(service.baca_jurnal, engine, pengguna.user_id)
    )


@router.patch("/journal/{jurnal_id}", response_model=Jurnal)
async def ubah_jurnal(
    request: Request,
    jurnal_id: UUID,
    badan: UbahJurnal,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    engine = platform.engine_dari(request)

    async def kerja() -> platform.Jawaban:
        jurnal = await service.ubah(engine, pengguna.user_id, jurnal_id, badan)
        return platform.Jawaban(200, jurnal, jurnal.id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(service.baca_jurnal, engine, pengguna.user_id)
    )


@router.delete("/journal/{jurnal_id}", status_code=204, response_class=Response)
async def hapus_jurnal(
    request: Request, jurnal_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Response:
    await service.hapus(platform.engine_dari(request), pengguna.user_id, jurnal_id)
    return Response(status_code=204)
