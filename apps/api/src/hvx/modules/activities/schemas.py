"""Bentuk data `activities` — spec/04 *Catatan harian* (spec/07 3.8).

`CatatAktivitas` sengaja TIDAK punya medan `source`: klien tidak bisa menyatakan
aktivitasnya "disimpulkan", dan sistem tidak bisa menyamar sebagai manusia lewat
rute yang sama. spec/01: *“tanpa itu, mesin akan belajar dari tebakannya
sendiri.”*
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

from hvx.modules import platform

Sumber = Literal["manual", "wearable", "integration", "inferred"]
# 'workout' · 'meal' · 'learning' · 'meeting' (spec/01) — kosakatanya belum
# ditutup, bentuknya dijaga.
Jenis = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")]
_PAYLOAD_MAKS_BYTE = 16_000
_DURASI_MAKS_S = 7 * 86_400


def _payload_wajar(nilai: dict[str, Any]) -> dict[str, Any]:
    if len(json.dumps(nilai, ensure_ascii=False).encode()) > _PAYLOAD_MAKS_BYTE:
        raise ValueError(f"payload maksimal {_PAYLOAD_MAKS_BYTE} byte")
    platform.tanpa_nul_bersarang(nilai)
    return nilai


Payload = Annotated[dict[str, Any], AfterValidator(_payload_wajar)]


class Aktivitas(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    kind: str
    occurred_at: datetime
    ended_at: datetime | None
    duration_seconds: int | None
    source: Sumber
    payload: dict[str, Any]
    created_at: datetime


class HalamanAktivitas(BaseModel):
    items: list[Aktivitas]
    next_cursor: str | None


class CatatAktivitas(BaseModel):
    """`POST /activities` — spec/04 `{ id?, kind, occurred_at, ended_at?, duration_seconds?,
    payload? }`."""

    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    kind: Jenis
    occurred_at: platform.WaktuBerzona
    ended_at: platform.WaktuBerzona | None = None
    duration_seconds: platform.Bulat | None = Field(default=None, ge=0, le=_DURASI_MAKS_S)
    payload: Payload = Field(default_factory=dict)

    @model_validator(mode="after")
    def _berakhir_sesudah_mulai(self) -> CatatAktivitas:
        # Sama dengan CHECK spec/01 — 400, bukan 500 dari basis data.
        if self.ended_at is not None and self.ended_at < self.occurred_at:
            raise ValueError("ended_at tidak boleh sebelum occurred_at")
        # `ended_at` dan `duration_seconds` dua fakta tentang SATU rentang: yang saling
        # membantah semula tersimpan apa adanya (tinjauan kontrak Sprint 3, K5).
        if self.ended_at is not None:
            rentang = (self.ended_at - self.occurred_at).total_seconds()
            if rentang > _DURASI_MAKS_S:
                raise ValueError(f"rentang aktivitas maksimal {_DURASI_MAKS_S} detik")
            if self.duration_seconds is not None and abs(self.duration_seconds - rentang) > 1:
                raise ValueError("duration_seconds tidak cocok dengan occurred_at–ended_at")
        return self
