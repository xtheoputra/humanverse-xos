"""Bentuk data `profile` — spec/04: `GET /me` · `PATCH /me/profile`."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from hvx.modules import identity, platform

# BCP 47 sesempit yang V0 butuhkan: bahasa + wilayah opsional (`id-ID`, `en`).
_POLA_LOCALE = r"^[a-z]{2,3}(-[A-Z]{2})?$"
_PREFERENSI_MAKS_BYTE = 16_000


def _preferensi_berukuran_wajar(nilai: dict[str, Any]) -> dict[str, Any]:
    # `preferences jsonb` sengaja lentur (spec/01, issue #2) — lentur tidak berarti
    # tempat menyimpan apa saja sebesar apa saja lewat satu PATCH.
    if len(json.dumps(nilai, ensure_ascii=False).encode()) > _PREFERENSI_MAKS_BYTE:
        raise ValueError(f"preferences maksimal {_PREFERENSI_MAKS_BYTE} byte")
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

    display_name: str | None = Field(default=None, min_length=1, max_length=100)
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
