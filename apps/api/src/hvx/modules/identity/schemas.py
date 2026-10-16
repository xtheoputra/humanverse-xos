"""Bentuk data publik `identity` — spec/04 bagian Identity."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
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

    granted: platform.Benar = False
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
    terms: platform.Benar
    privacy: platform.Benar
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


class PermintaanHapusAkun(BaseModel):
    """`DELETE /me` — sandi diminta ulang (re-auth) sebelum penghapusan dijadwalkan."""

    model_config = ConfigDict(extra="forbid")

    password: SecretStr = Field(min_length=1, max_length=PANJANG_MAKS)


class JawabanHapusDijadwalkan(BaseModel):
    deletion_scheduled_at: datetime


class JawabanRestore(BaseModel):
    status: str = "active"


# ── spec/07 6.4 — Privacy Center (`/v1/privacy/*`, K-41…K-43) ─────────────────


class PermintaanSandiUlang(BaseModel):
    """Ekspor dan hapus data — sandi diminta ulang (OWASP ASVS V3.7.1), seperti `DELETE /me`."""

    model_config = ConfigDict(extra="forbid")

    password: SecretStr = Field(min_length=1, max_length=PANJANG_MAKS)


class TabelKategori(BaseModel):
    """Satu baris layar Privacy Center — jumlah, bukan isi (spec/04)."""

    key: str
    label: str
    count: int  # baris yang kamu catat
    derived_count: int  # baris yang sistem turunkan darinya
    tables: dict[str, int]
    deletable: bool
    retention: str
    why_not_deletable: str | None


class TakDikumpulkan(BaseModel):
    key: str
    label: str


class RingkasanPrivasi(BaseModel):
    categories: list[TabelKategori]
    not_collected: list[TakDikumpulkan]


class IzinBerlaku(BaseModel):
    scope: str
    action: str
    decision: Literal["allow", "deny", "ask"]
    source: Literal["user", "default"]
    expires_at: datetime | None
    sensitive: bool
    confirm_each_time: bool


class IzinAgent(BaseModel):
    subject_type: Literal["agent"]
    subject_id: str
    purpose: list[str]
    permissions: list[IzinBerlaku]


class DaftarIzinAgent(BaseModel):
    agents: list[IzinAgent]


class PermintaanIzin(BaseModel):
    """`PUT /privacy/permissions/{subject_type}/{subject_id}/{scope}` — `ask` = tanya lagi."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["read", "write", "execute", "share", "delete"]
    decision: Literal["allow", "deny", "ask"]
    expires_at: platform.WaktuBerzona | None = None


class JawabanEkspor(BaseModel):
    export_id: UUID
    status: Literal["ready", "downloaded"]
    expires_at: datetime
    download_url: str | None = None


class JawabanHapusData(BaseModel):
    category: str
    deleted: dict[str, int]  # tabel → baris yang dihapus, termasuk turunan
