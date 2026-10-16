"""Rute `profile` — spec/04: `GET /v1/me` · `PATCH /v1/me/profile` (1.3) · notifikasi (6.3)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from hvx.modules import identity, platform

from . import notifikasi, repository
from .schemas import JawabanSaya, Notifikasi, Profil, UbahNotifikasi, UbahProfil

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


def _notifikasi(tersimpan: dict[str, Any] | None) -> dict[str, Any]:
    pref = notifikasi.berlaku(tersimpan)
    return {
        "types": [
            {
                "key": k,
                "label": j.label,
                "enabled": pref["types"][k],
                "default": j.bawaan,
                "required": j.wajib,
            }
            for k, j in notifikasi.JENIS.items()
        ],
        "quiet_hours": pref["quiet_hours"],
        "daily_cap": notifikasi.PAGU_HARIAN,
        "delivery": "none",
    }


@router.get("/me/notifications", response_model=Notifikasi)
async def notifikasi_saya(
    request: Request, pengguna: identity.PenggunaDiperlukan
) -> dict[str, Any]:
    engine = platform.engine_dari(request)
    async with platform.transaksi_pengguna(engine, pengguna.user_id) as conn:
        return _notifikasi(await repository.notifikasi(conn, pengguna.user_id))


@router.patch("/me/notifications", response_model=Notifikasi)
async def ubah_notifikasi_saya(
    request: Request, badan: UbahNotifikasi, pengguna: identity.PenggunaDiperlukan
) -> dict[str, Any]:
    """spec/07 6.3 — *bisa dimatikan per jenis*. Idempoten dengan sendirinya."""
    jam = badan.quiet_hours.model_dump() if badan.quiet_hours else None
    engine = platform.engine_dari(request)
    async with platform.transaksi_pengguna(engine, pengguna.user_id) as conn:
        lama = await repository.notifikasi_untuk_ubah(conn, pengguna.user_id)
        try:
            baru = notifikasi.gabungkan(
                lama, badan.types, jam, ubah_jam_tenang="quiet_hours" in badan.model_fields_set
            )
        except notifikasi.PreferensiTidakSah as galat:
            raise platform.GalatApi(422, galat.kode, str(galat)) from None
        await repository.simpan_notifikasi(conn, pengguna.user_id, baru)
    return _notifikasi(baru)
