"""Rute operasional. Sengaja TANPA awalan `/v1`: `/health` dibaca mesin
penjalan (Docker, penyeimbang beban), bukan kontrak API produk (spec/04)."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .health import laporan_kesehatan

router = APIRouter(tags=["platform"])


class JawabanKesehatan(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    db: Literal["ok", "down"]
    redis: Literal["ok", "down"]


@router.get(
    "/health",
    response_model=JawabanKesehatan,
    responses={503: {"model": JawabanKesehatan, "description": "ketergantungan mati"}},
)
async def health(request: Request) -> JSONResponse:
    state = request.app.state
    kode, badan = await laporan_kesehatan(
        versi=state.versi,
        pemeriksaan=state.pemeriksaan_kesehatan,
        timeout_s=state.settings.health_timeout_s,
    )
    jawaban = JawabanKesehatan.model_validate(badan)
    return JSONResponse(status_code=kode, content=jawaban.model_dump())
