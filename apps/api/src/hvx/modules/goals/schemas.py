"""Bentuk data `goals` — spec/04 *Goals & habits* (spec/07 2.1)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hvx.modules import platform

# Sama dengan CHECK spec/01 — ditolak di sini supaya salah ketik menjadi 400, bukan 500.
Domain = Literal["career", "health", "finance", "learning", "social", "lifestyle", "other"]
StatusGoal = Literal["active", "paused", "achieved", "dropped"]
StatusMilestone = Literal["pending", "in_progress", "done", "skipped"]

Judul = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=200)]
Uraian = Annotated[platform.TeksTanpaNul, Field(max_length=4000)]


class Goal(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    parent_id: UUID | None
    title: str
    description: str | None
    domain: Domain | None
    status: StatusGoal
    target_date: date | None
    achieved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class Milestone(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    goal_id: UUID
    title: str
    position: int
    status: StatusMilestone
    due_date: date | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class GoalRinci(Goal):
    """`GET /goals/{id}` — spec/04: *memuat milestones[]*."""

    milestones: list[Milestone]


class SimpulPohon(Goal):
    """`GET /goals/{id}/tree` — goal dan seluruh keturunannya (Goal Graph naskah 4 §9)."""

    children: list[SimpulPohon]


class HalamanGoal(BaseModel):
    items: list[Goal]
    next_cursor: str | None


def _tolak_null(model: BaseModel, boleh_null: frozenset[str]) -> None:
    # Kolom NOT NULL di spec/01: `null` eksplisit = bentuk salah (400), bukan
    # diteruskan menjadi galat 500 — pola yang sama dengan PATCH /me/profile.
    kosong = sorted(
        f for f in model.model_fields_set if f not in boleh_null and getattr(model, f) is None
    )
    if kosong:
        raise ValueError(f"tidak boleh null: {', '.join(kosong)}")


class BuatGoal(BaseModel):
    """`POST /goals` — `id` boleh dibuat klien (spec/04: dukungan luring)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    title: Judul
    description: Uraian | None = None
    domain: Domain | None = None
    parent_id: UUID | None = None
    target_date: date | None = None

    @model_validator(mode="after")
    def _bukan_induk_dirinya(self) -> BuatGoal:
        # Juga dijaga CHECK `goals_parent_not_self` (migrasi 0004): baris yang
        # menunjuk dirinya sendiri lolos FK komposit, sebab FK diperiksa SESUDAH
        # barisnya ada — dan pohonnya menjadi lingkaran.
        if self.id is not None and self.id == self.parent_id:
            raise ValueError("goal tidak boleh menjadi induk dirinya sendiri")
        return self


class UbahGoal(BaseModel):
    """`PATCH /goals/{id}` — spec/04: `{ title?, status?, target_date? }`; medan lain DITOLAK."""

    model_config = ConfigDict(extra="forbid")

    title: Judul | None = None
    status: StatusGoal | None = None
    target_date: date | None = None  # null = hapus tanggal target

    @model_validator(mode="after")
    def _yang_dikirim_tidak_null(self) -> UbahGoal:
        _tolak_null(self, frozenset({"target_date"}))
        return self


class BuatMilestone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Judul
    position: int | None = Field(default=None, ge=0, le=10_000)
    due_date: date | None = None


class UbahMilestone(BaseModel):
    """`PATCH /milestones/{id}` — spec/04: `{ status?, title?, due_date? }`."""

    model_config = ConfigDict(extra="forbid")

    status: StatusMilestone | None = None
    title: Judul | None = None
    due_date: date | None = None  # null = hapus tanggal

    @model_validator(mode="after")
    def _yang_dikirim_tidak_null(self) -> UbahMilestone:
        _tolak_null(self, frozenset({"due_date"}))
        return self
