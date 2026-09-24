"""Bentuk API percakapan — spec/04 *AI* (spec/07 4.8)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from hvx.modules import platform

Judul = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=200)]
IsiPesan = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=4000)]
StatusGiliran = Literal["processing", "completed"]
# spec/04: jawaban atas `confirmation_required` — kode API berbahasa Inggris.
KeputusanKonfirmasi = Literal["allow_always", "allow_once", "reject"]


class BuatPercakapan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None  # spec/04: klien boleh membuat id sendiri (luring)
    title: Judul | None = None


class Percakapan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    title: str | None
    started_at: datetime
    last_message_at: datetime | None
    message_count: int


class HalamanPercakapan(BaseModel):
    items: list[Percakapan]
    next_cursor: str | None


class KirimPesan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    content: IsiPesan


class Pesan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    role: Literal["user", "assistant", "tool", "system"]
    content: str
    agent_run_id: UUID | None
    # Tiap balasan AI membawa keduanya — juga saat dibaca ulang (spec/04, E-194).
    confidence: float | None
    rationale: list[str]
    cost_usd: float | None
    created_at: datetime


class HalamanPesan(BaseModel):
    items: list[Pesan]
    next_cursor: str | None


class TerimaPesan(BaseModel):
    """`202` spec/04 — balasannya lewat `GET …/stream`."""

    message_id: UUID
    agent_run_id: UUID | None  # None: perintah deterministik, tanpa agent (4.1)
    status: StatusGiliran


class JawabKonfirmasi(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: Annotated[platform.TeksTanpaNul, Field(min_length=1, max_length=2000)]
    decision: KeputusanKonfirmasi


class TerimaKonfirmasi(BaseModel):
    agent_run_id: UUID
    status: StatusGiliran
