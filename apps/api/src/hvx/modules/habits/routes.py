"""Rute `habits` — spec/04 *Goals & habits* (spec/07 2.2–2.4).

Tiap rute tulis `POST`/`PATCH` menyatakan `platform.Idempoten` (spec/04,
E-165) — dijaga `tests/unit/test_idempotensi_terpasang.py`.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from hvx.modules import identity, platform

from . import service
from .schemas import (
    BuatHabit,
    CatatPenyelesaian,
    DaftarHabit,
    Habit,
    JawabanRentetan,
    Penyelesaian,
    StatusHabit,
    UbahHabit,
)

router = APIRouter(prefix="/v1", tags=["habits"])


def _pembaca_zona_waktu(request: Request) -> service.PembacaZonaWaktu:
    """Dipasang titik rakit `hvx.main` (K-23) — `habits` tidak tahu siapa pemiliknya.

    Tidak ada jatuh-balik diam-diam ke UTC kalau titik rakit lupa memasangnya:
    "hari ini" yang salah zona memutus rentetan orang tanpa ada yang tahu.
    """
    pembaca = getattr(request.app.state, "pembaca_zona_waktu", None)
    if pembaca is None:
        raise RuntimeError("hvx.main tidak memasang app.state.pembaca_zona_waktu (K-23)")
    return pembaca  # type: ignore[no-any-return]


def _pembaca_energi(request: Request) -> service.PembacaEnergi:
    """Dipasang titik rakit `hvx.main` (K-23): energi check-in milik `checkins`."""
    pembaca = getattr(request.app.state, "pembaca_energi", None)
    if pembaca is None:
        raise RuntimeError("hvx.main tidak memasang app.state.pembaca_energi (K-23)")
    return pembaca  # type: ignore[no-any-return]


@router.get("/habits", response_model=DaftarHabit)
async def daftar_habit(
    request: Request,
    pengguna: identity.PenggunaDiperlukan,
    status: StatusHabit | None = None,
    for_date: date | None = None,
) -> DaftarHabit:
    return await service.daftar(
        platform.engine_dari(request),
        pengguna.user_id,
        status=status,
        for_date=for_date,
        pembaca_energi=_pembaca_energi(request) if for_date is not None else None,
    )


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


@router.post(
    "/habits/{habit_id}/completions",
    status_code=201,
    response_model=Penyelesaian,
    responses={200: {"model": Penyelesaian, "description": "tanggal itu sudah tercatat"}},
)
async def catat_penyelesaian(
    request: Request,
    habit_id: UUID,
    badan: CatatPenyelesaian,
    pengguna: identity.PenggunaDiperlukan,
    idem: platform.Idempoten,
) -> JSONResponse:
    async def kerja() -> platform.Jawaban:
        hasil = await service.catat(
            platform.engine_dari(request), pengguna.user_id, habit_id, badan
        )
        return platform.Jawaban(201 if hasil.baru else 200, hasil.penyelesaian)

    return await idem.jalankan(pengguna.user_id, kerja)


@router.delete(
    "/habits/{habit_id}/completions/{for_date}", status_code=204, response_class=Response
)
async def hapus_penyelesaian(
    request: Request, habit_id: UUID, for_date: date, pengguna: identity.PenggunaDiperlukan
) -> Response:
    await service.hapus_catatan(platform.engine_dari(request), pengguna.user_id, habit_id, for_date)
    return Response(status_code=204)


@router.get("/habits/{habit_id}/streak", response_model=JawabanRentetan)
async def rentetan_habit(
    request: Request, habit_id: UUID, pengguna: identity.PenggunaDiperlukan
) -> JawabanRentetan:
    return await service.rentetan(
        platform.engine_dari(request),
        pengguna.user_id,
        habit_id,
        pembaca_zona_waktu=_pembaca_zona_waktu(request),
    )
