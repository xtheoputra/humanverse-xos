"""Rute `profile` — spec/04: `GET /v1/me` · `PATCH /v1/me/profile` (spec/07 1.3)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from hvx.modules import identity, platform

from . import repository
from .schemas import JawabanSaya, Profil, UbahProfil

router = APIRouter(prefix="/v1", tags=["profile"])


def _tanpa_profil() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Profil tidak ditemukan.")


@router.get("/me", response_model=JawabanSaya)
async def saya(request: Request, pengguna: identity.PenggunaDiperlukan) -> JawabanSaya:
    engine = platform.engine_dari(request)
    async with platform.transaksi_pengguna(engine, pengguna.user_id) as conn:
        akun = await identity.ambil_pengguna(conn, pengguna.user_id)
        profil = await repository.ambil_profil(conn, pengguna.user_id)
    if akun is None or profil is None:
        raise _tanpa_profil()
    return JawabanSaya(user=akun, profile=profil)


@router.patch("/me/profile", response_model=Profil)
async def ubah_profil_saya(
    request: Request, badan: UbahProfil, pengguna: identity.PenggunaDiperlukan
) -> Profil:
    engine = platform.engine_dari(request)
    perubahan = badan.model_dump(include=badan.model_fields_set)
    async with platform.transaksi_pengguna(engine, pengguna.user_id) as conn:
        profil = await repository.ubah_profil(conn, pengguna.user_id, perubahan)
    if profil is None:
        raise _tanpa_profil()
    return profil
