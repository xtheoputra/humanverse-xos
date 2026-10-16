"""Bentuk data `profile` — spec/04: `GET /me` · `PATCH /me/profile`."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from hvx.modules import identity, platform

# BCP 47 sesempit yang V0 butuhkan: bahasa + wilayah opsional (`id-ID`, `en`).
_POLA_LOCALE = r"^[a-z]{2,3}(-[A-Z]{2})?$"
_PREFERENSI_MAKS_BYTE = 16_000


# Kunci `preferences` yang dikelola rute sendiri — `PATCH /me/profile` tidak menyentuhnya.
KUNCI_NOTIFIKASI = "notifications"


def _preferensi_berukuran_wajar(nilai: dict[str, Any]) -> dict[str, Any]:
    # `preferences jsonb` sengaja lentur (spec/01, issue #2) — lentur tidak berarti
    # tempat menyimpan apa saja sebesar apa saja lewat satu PATCH, atau yang ditolak
    # `jsonb` sendiri (NUL → 500, tinjauan Sprint 1).
    if KUNCI_NOTIFIKASI in nilai:
        # 6.3 (K-44): satu penulis per kunci. `preferences` diganti UTUH oleh PATCH ini;
        # tanpa penolakan, klien yang mengirim preferensi lamanya menimpa pilihan notifikasi
        # yang baru disimpan perangkat lain.
        raise ValueError("preferences.notifications diubah lewat PATCH /me/notifications")
    if len(json.dumps(nilai, ensure_ascii=False).encode()) > _PREFERENSI_MAKS_BYTE:
        raise ValueError(f"preferences maksimal {_PREFERENSI_MAKS_BYTE} byte")
    platform.tanpa_nul_bersarang(nilai)
    return nilai


Preferensi = Annotated[dict[str, Any], AfterValidator(_preferensi_berukuran_wajar)]


class Profil(BaseModel):
    model_config = ConfigDict(frozen=True)

    display_name: str
    timezone: str
    locale: str
    birth_year: int | None
    avatar_url: str | None
    preferences: dict[str, Any]
    updated_at: datetime


class UbahProfil(BaseModel):
    """PATCH: hanya medan yang DIKIRIM yang diubah; medan tak dikenal DITOLAK.

    `extra="forbid"` bukan kerapian: tanpa itu `{"user_id": "…"}` diam-diam
    diabaikan, dan klien tidak pernah tahu permintaannya tidak berarti.
    """

    model_config = ConfigDict(extra="forbid")

    display_name: platform.TeksTanpaNul | None = Field(default=None, min_length=1, max_length=100)
    timezone: platform.ZonaWaktuIANA | None = None
    locale: str | None = Field(default=None, pattern=_POLA_LOCALE)
    preferences: Preferensi | None = None

    @model_validator(mode="after")
    def _yang_dikirim_tidak_null(self) -> UbahProfil:
        # Semua kolom yang bisa diubah NOT NULL di spec/01: `null` eksplisit
        # ditolak sebagai bentuk salah (400), bukan diteruskan jadi galat 500.
        kosong = sorted(f for f in self.model_fields_set if getattr(self, f) is None)
        if kosong:
            raise ValueError(f"tidak boleh null: {', '.join(kosong)}")
        return self


class JawabanSaya(BaseModel):
    user: identity.PenggunaRingkas
    profile: Profil


# ── spec/07 6.3 — notifikasi (K-44) ───────────────────────────────────────────

_POLA_JAM = r"^([01][0-9]|2[0-3]):[0-5][0-9]$"


class JamTenang(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start: str = Field(pattern=_POLA_JAM)
    end: str = Field(pattern=_POLA_JAM)


class UbahNotifikasi(BaseModel):
    """`PATCH /me/notifications` — jenis yang dikirim saja; `quiet_hours: null` = tanpa jam
    tenang; tanpa `quiet_hours` = jam tenang tidak diubah."""

    model_config = ConfigDict(extra="forbid")

    types: dict[str, platform.Benar] | None = Field(default=None, max_length=20)
    quiet_hours: JamTenang | None = None


class JenisBerlaku(BaseModel):
    key: str
    label: str
    enabled: bool
    default: bool
    required: bool


class Notifikasi(BaseModel):
    types: list[JenisBerlaku]
    quiet_hours: JamTenang | None
    daily_cap: int
    # V0 tidak mengirim notifikasi apa pun (A-28) — klien tidak boleh menjanjikannya.
    delivery: Literal["none"]
