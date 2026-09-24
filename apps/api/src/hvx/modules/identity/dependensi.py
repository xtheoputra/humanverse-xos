"""Dependensi autentikasi — spec/07 tugas 1.2 (*“middleware auth”*).

Ditulis sebagai dependensi FastAPI, bukan middleware ASGI: rute yang tidak
butuh pengguna (`/health`, `/v1/auth/login`) tidak dipaksa membayar satu
panggilan Redis, dan rute yang butuh MENYATAKANNYA di tanda tangannya —
sehingga rute baru yang lupa meminta pengguna tidak punya `user_id` untuk
dipakai sama sekali, bukan diam-diam memakai milik orang lain.

🛑 **`async def`, selalu** (AGENTS.md §7): `platform.ikat_pengguna` menolak
dipanggil dari threadpool, tempat ikatan contextvars hilang.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from hvx.modules import platform

from .laju import batasi_pengguna
from .sesi import PenyimpanSesi

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class PenggunaMasuk:
    user_id: UUID
    sesi_id: UUID


def penyimpan_sesi(request: Request) -> PenyimpanSesi:
    settings = platform.settings_dari(request)
    return PenyimpanSesi(
        platform.redis_dari(request),
        awalan=settings.redis_prefix,
        ttl_akses_s=settings.access_token_ttl_s,
        ttl_segar_s=settings.refresh_token_ttl_s,
    )


def _tolak(alasan: str | None = None) -> platform.GalatApi:
    tantangan = "Bearer" if alasan is None else f'Bearer error="{alasan}"'
    return platform.GalatApi(
        401, "unauthenticated", "Belum masuk, atau sesi sudah berakhir.",
        header={"WWW-Authenticate": tantangan},
    )  # fmt: skip


async def pengguna_saat_ini(
    request: Request,
    kredensial: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> PenggunaMasuk:
    if kredensial is None:
        raise _tolak()
    sesi = await penyimpan_sesi(request).periksa_akses(kredensial.credentials)
    if sesi is None:
        # Tidak dibedakan: token palsu, kedaluwarsa, dan DICABUT jawabannya sama —
        # yang terakhir itulah yang membuat pencabutan berlaku seketika.
        raise _tolak("invalid_token")
    platform.ikat_pengguna(str(sesi.user_id))
    await batasi_pengguna(request, sesi.user_id)  # spec/07 1.7
    return PenggunaMasuk(sesi.user_id, sesi.sesi_id)


PenggunaDiperlukan = Annotated[PenggunaMasuk, Depends(pengguna_saat_ini)]
