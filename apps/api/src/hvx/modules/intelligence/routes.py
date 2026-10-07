"""Rute `intelligence` — spec/04 *Rekomendasi* & Dashboard (6.1).

`GET /dashboard` (§28), `GET /recommendations` + `POST …/shown` (spec/04), dan umpan
balik (5.6). `POST …/shown` idempoten dengan sendirinya — menandai `shown` dua kali
tetap `shown` — jadi tanpa `Idempotency-Key` (test_idempotensi_terpasang TANPA_IDEMPOTENSI).
"""

from __future__ import annotations

from functools import partial
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import rekomendasi, tinjauan, umpan_balik
from .dasbor import dasbor as bangun_dasbor
from .schemas import CatatUmpanBalik, DaftarRekomendasi, Dasbor, TinjauanMingguan, UmpanBalik

router = APIRouter(prefix="/v1", tags=["recommendations"])

# spec/01 `recommendations.status` yang boleh disaring klien.
_STATUS = frozenset({"pending", "shown", "accepted", "rejected", "expired"})
Status = Annotated[str | None, Query(max_length=20)]
Domain = Annotated[str | None, Query(max_length=40)]
Minggu = Annotated[str | None, Query(pattern=tinjauan.POLA_MINGGU)]


@router.get("/dashboard", response_model=Dasbor)
async def dashboard(request: Request, pengguna: identity.PenggunaDiperlukan) -> Dasbor:
    return await bangun_dasbor(platform.engine_dari(request), pengguna.user_id)


@router.get("/reviews/weekly", response_model=TinjauanMingguan)
async def tinjauan_mingguan(
    request: Request, pengguna: identity.PenggunaDiperlukan, week: Minggu = None
) -> dict[str, Any]:
    """spec/07 6.2 — lima pertanyaan naskah 4 §31; dihitung saat dibaca, tidak disimpan."""
    return await tinjauan.tinjauan_mingguan(platform.engine_dari(request), pengguna.user_id, week)


@router.get("/recommendations", response_model=DaftarRekomendasi)
async def daftar_rekomendasi(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    status: Status = None,
    domain: Domain = None,
) -> DaftarRekomendasi:
    if status is not None and status not in _STATUS:
        raise platform.GalatApi(400, "invalid_status", "status rekomendasi tak dikenal")
    items = await rekomendasi.daftar_rekomendasi(
        platform.engine_dari(request), pengguna.user_id, status=status, domain=domain
    )
    return DaftarRekomendasi(items=items)


@router.post("/recommendations/{rekomendasi_id}/shown", status_code=204)
async def tandai_terlihat(
    request: Request, rekomendasi_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> Response:
    await rekomendasi.tandai_terlihat(
        platform.engine_dari(request), pengguna.user_id, rekomendasi_id
    )
    return Response(status_code=204)


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
