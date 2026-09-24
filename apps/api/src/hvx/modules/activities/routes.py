"""Rute `activities` — spec/04 *Catatan harian* (spec/07 3.8)."""

from __future__ import annotations

from functools import partial
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import Aktivitas, CatatAktivitas, HalamanAktivitas, Jenis, Sumber

router = APIRouter(prefix="/v1", tags=["activities"])

DariWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="from")]
SampaiWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="to")]


@router.get("/activities", response_model=HalamanAktivitas)
async def daftar_aktivitas(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    kind: Jenis | None = None,
    source: Sumber | None = None,
    dari: DariWaktu = None,
    sampai: SampaiWaktu = None,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanAktivitas:
    return await service.daftar(
        platform.engine_dari(request),
        pengguna.user_id,
        kind=kind,
        source=source,
        dari=dari,
        sampai=sampai,
        batas=limit,
        kursor=cursor,
    )


@router.post("/activities", status_code=201, response_model=Aktivitas)
async def catat_aktivitas(
    request: Request,
    badan: CatatAktivitas,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    engine = platform.engine_dari(request)

    async def kerja() -> platform.Jawaban:
        aktivitas = await service.catat(engine, pengguna.user_id, badan)
        return platform.Jawaban(201, aktivitas, aktivitas.id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(service.baca_aktivitas, engine, pengguna.user_id)
    )
