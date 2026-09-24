"""Bentuk data publik `identity` — spec/04 bagian Identity."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, model_validator

from hvx.modules import platform

from .sandi import PANJANG_MAKS, PANJANG_MIN


class PenggunaRingkas(BaseModel):
    """`user` di jawaban spec/04 — tanpa `password_hash`, selamanya."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    email: str
    status: str
    email_verified_at: datetime | None
    created_at: datetime


# ── spec/07 1.1 · 1.4 — permintaan & jawaban /v1/auth ─────────────────────────

_POLA_SNAKE = r"^[a-z][a-z0-9_]{0,62}$"


class PersetujuanPelatihan(BaseModel):
    """`model_training` (B-22): persetujuan TERSENDIRI — bawaannya DITOLAK.

    Menolaknya tidak mengurangi layanan (#59). Menyetujuinya wajib menyebut data
    apa yang boleh dipakai: persetujuan tanpa cakupan tidak mengizinkan apa pun.
    """

    model_config = ConfigDict(extra="forbid")

    granted: bool = False
    data_scopes: list[Annotated[str, Field(pattern=_POLA_SNAKE)]] = Field(
        default_factory=list, max_length=32
    )

    @model_validator(mode="after")
    def _disetujui_wajib_bercakupan(self) -> PersetujuanPelatihan:
        if self.granted and not self.data_scopes:
            raise ValueError("model_training yang disetujui wajib menyebut data_scopes")
        return self


class PersetujuanPendaftaran(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_version: platform.TeksTanpaNul = Field(min_length=1, max_length=64)
    terms: bool
    privacy: bool
    model_training: PersetujuanPelatihan = Field(default_factory=PersetujuanPelatihan)


class PermintaanDaftar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=254)
    password: SecretStr = Field(min_length=PANJANG_MIN, max_length=PANJANG_MAKS)
    display_name: platform.TeksTanpaNul = Field(min_length=1, max_length=100)
    timezone: platform.ZonaWaktuIANA
    consents: PersetujuanPendaftaran


class PermintaanMasuk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr = Field(max_length=254)
    # Tanpa batas minimal di sini: kebijakan panjang milik PENDAFTARAN — login
    # yang menolak sandi pendek hanya memberi tahu penebak aturan sandinya.
    password: SecretStr = Field(min_length=1, max_length=PANJANG_MAKS)


class PermintaanSegarkan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=1, max_length=200)


class JawabanToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class JawabanAkun(BaseModel):
    user: PenggunaRingkas
    tokens: JawabanToken


class JawabanSegarkan(BaseModel):
    tokens: JawabanToken
