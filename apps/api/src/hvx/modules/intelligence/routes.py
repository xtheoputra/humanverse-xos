"""Rute `intelligence` — spec/04 *Rekomendasi*. V0: umpan balik rekomendasi (5.6).

`GET /recommendations` dan `POST …/shown` menyusul bersama Dashboard (Sprint 6).
"""

from __future__ import annotations

from functools import partial
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import umpan_balik
from .schemas import CatatUmpanBalik, UmpanBalik

router = APIRouter(prefix="/v1", tags=["recommendations"])


@router.post(
    "/recommendations/{rekomendasi_id}/feedback", status_code=201, response_model=UmpanBalik
)
async def catat_umpan_balik(
    request: Request,
    rekomendasi_id: UUID,
    badan: CatatUmpanBalik,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    engine = platform.engine_dari(request)

    async def kerja() -> platform.Jawaban:
        hasil = await umpan_balik.catat_umpan_balik(engine, pengguna.user_id, rekomendasi_id, badan)
        return platform.Jawaban(201, hasil, hasil.id)

    return await idem.jalankan(
        pengguna.user_id, kerja, partial(umpan_balik.baca_umpan_balik, engine, pengguna.user_id)
    )
