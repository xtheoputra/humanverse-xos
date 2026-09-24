"""Bentuk data `checkins` — spec/04 *Catatan harian* (spec/07 2.5–2.6)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from hvx.modules import platform

Skala = Annotated[int, Field(ge=1, le=5)]
Catatan = Annotated[platform.TeksTanpaNul, Field(max_length=4000)]


class Checkin(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    for_date: date
    energy: int | None
    focus: int | None
    sleep_hours: Decimal | None
    note: str | None
    created_at: datetime
    updated_at: datetime


class DaftarCheckin(BaseModel):
    items: list[Checkin]


class IsiCheckin(BaseModel):
    """`PUT /checkins/{for_date}` — badan ADALAH check-in tanggal itu (PUT = ganti).

    Medan yang tidak dikirim menjadi kosong: dua `PUT` yang sama menghasilkan
    baris yang sama, apa pun isi baris sebelumnya. Klien yang ingin menambah
    satu medan mengirim check-in utuhnya.
    """

    model_config = ConfigDict(extra="forbid")

    energy: Skala | None = None
    focus: Skala | None = None
    # numeric(3,1) spec/01: satu angka desimal — 7,25 DITOLAK, tidak dibulatkan diam-diam.
    sleep_hours: Decimal | None = Field(default=None, ge=0, le=24, decimal_places=1)
    note: Catatan | None = None


# ── spec/07 2.6 — mood_entries ────────────────────────────────────────────────


class Mood(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    occurred_at: datetime
    valence: int
    label: str | None
    note: str | None
    created_at: datetime


class HalamanMood(BaseModel):
    items: list[Mood]
    next_cursor: str | None


class CatatMood(BaseModel):
    """`POST /moods` — mood DILAPORKAN pengguna (spec/01: bukan ditaksir sistem, E-34)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    valence: Skala
    label: Annotated[platform.TeksBerisi, Field(min_length=1, max_length=50)] | None = None
    note: Catatan | None = None
    # Wajib berzona waktu: `2026-09-24T06:30` tanpa zona adalah jam yang berbeda di
    # tiap negara, dan menebak zonanya berarti menebak kapan perasaan itu terjadi.
    occurred_at: AwareDatetime | None = None
