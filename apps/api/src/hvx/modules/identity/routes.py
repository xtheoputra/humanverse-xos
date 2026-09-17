"""Rute identity — spec/04: `POST /v1/auth/register · login · refresh · logout` (spec/07 1.1)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from hvx.modules import platform

from . import service
from .dependensi import PenggunaDiperlukan, penyimpan_sesi
from .laju import batasi_kredensial_ip, penjaga_gagal_masuk
from .schemas import (
    JawabanAkun,
    JawabanSegarkan,
    JawabanToken,
    PermintaanDaftar,
    PermintaanMasuk,
    PermintaanSegarkan,
)
from .sesi import PenyimpanSesi, Token

router = APIRouter(prefix="/v1/auth", tags=["identity"])

Sesi = Annotated[PenyimpanSesi, Depends(penyimpan_sesi)]
# Daftar & masuk: batas per IP yang lebih ketat daripada permukaan umum (spec/07 1.7).
_KREDENSIAL = [Depends(batasi_kredensial_ip)]


def _pendengar(request: Request) -> Sequence[service.PendengarPendaftaran]:
    """Dipasang titik rakit `hvx.main` — identity tidak tahu siapa yang mendengar."""
    return tuple(getattr(request.app.state, "pendengar_pendaftaran", ()))


def _token(t: Token) -> JawabanToken:
    return JawabanToken(
        access_token=t.access_token,
        refresh_token=t.refresh_token,
        token_type=t.token_type,
        expires_in=t.expires_in,
    )


@router.post("/register", status_code=201, response_model=JawabanAkun, dependencies=_KREDENSIAL)
async def daftar(request: Request, badan: PermintaanDaftar, sesi: Sesi) -> JawabanAkun:
    akun, token = await service.daftar(
        platform.engine_dari(request),
        sesi,
        badan,
        pendengar=_pendengar(request),
        ip_hash=platform.sidik_ip(request),
    )
    return JawabanAkun(user=akun, tokens=_token(token))


@router.post("/login", response_model=JawabanAkun, dependencies=_KREDENSIAL)
async def masuk(request: Request, badan: PermintaanMasuk, sesi: Sesi) -> JawabanAkun:
    akun, token = await service.masuk(
        platform.engine_dari(request),
        sesi,
        badan.email,
        badan.password.get_secret_value(),
        ip_hash=platform.sidik_ip(request),
        penjaga=penjaga_gagal_masuk(request, badan.email),
    )
    return JawabanAkun(user=akun, tokens=_token(token))


@router.post("/refresh", response_model=JawabanSegarkan)
async def segarkan(request: Request, badan: PermintaanSegarkan, sesi: Sesi) -> JawabanSegarkan:
    token = await service.segarkan(
        platform.engine_dari(request), sesi, badan.refresh_token, ip_hash=platform.sidik_ip(request)
    )
    return JawabanSegarkan(tokens=_token(token))


@router.post("/logout", status_code=204, response_class=Response)
async def keluar(request: Request, pengguna: PenggunaDiperlukan, sesi: Sesi) -> Response:
    await service.keluar(
        platform.engine_dari(request), sesi, pengguna, ip_hash=platform.sidik_ip(request)
    )
    return Response(status_code=204)
