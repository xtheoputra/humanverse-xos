"""Rute `checkins` — spec/04 *Catatan harian* (spec/07 2.5–2.6).

`PUT /checkins/{for_date}` idempoten dengan sendirinya (PUT = ganti) — spec/04
menjanjikan `Idempotency-Key` untuk `POST`/`PATCH`, bukan `PUT`.
"""

from __future__ import annotations

from functools import partial
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import CatatMood, Checkin, DaftarCheckin, HalamanMood, IsiCheckin, Mood

router = APIRouter(prefix="/v1", tags=["checkins"])

# `from` kata kunci Python — namanya di URL tetap `from` (spec/04).
Dari = Annotated[platform.Tanggal | None, Query(alias="from")]
Sampai = Annotated[platform.Tanggal | None, Query(alias="to")]
# Mood bercap waktu — `from`/`to` ISO-8601 berzona (spec/04: waktu UTC dengan `Z`).
DariWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="from")]
SampaiWaktu = Annotated[platform.WaktuBerzona | None, Query(alias="to")]


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
    request: Request,
    for_date: platform.Tanggal,
    badan: IsiCheckin,
    pengguna: identity.PenggunaDiperlukan,
) -> JSONResponse:
    hasil = await service.simpan(platform.engine_dari(request), pengguna.user_id, for_date, badan)
    return JSONResponse(
        status_code=201 if hasil.baru else 200, content=jsonable_encoder(hasil.checkin)
    )


@router.get("/moods", response_model=HalamanMood)
async def daftar_mood(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    dari: DariWaktu = None,
    sampai: SampaiWaktu = None,
    limit: platform.Batas = platform.BATAS_BAWAAN,
    cursor: platform.Kursor = None,
) -> HalamanMood:
    return await service.daftar_mood(
        platform.engine_dari(request),
        pengguna.user_id,
        dari=dari,
        sampai=sampai,
        batas=limit,
        kursor=cursor,
    )


@router.post("/moods", status_code=201, response_model=Mood)
async def catat_mood(
    request: Request,
    badan: CatatMood,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    engine = platform.engine_dari(request)

    async def kerja() -> platform.Jawaban:
        mood = await service.catat_mood(engine, pengguna.user_id, badan)
        return platform.Jawaban(201, mood, mood.id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(service.baca_mood, engine, pengguna.user_id)
    )
