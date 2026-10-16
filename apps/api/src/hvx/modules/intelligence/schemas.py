"""Bentuk data umpan balik rekomendasi — spec/04 `POST /recommendations/{id}/feedback`.

`action` persis lima nilai `recommendation_feedback.action` (spec/01). `modified`
dan `snoozed` ada DI SINI, sejajar `accepted`/`rejected`, karena memilih B setelah
disarankan A bukan penolakan, dan menunda bukan mengabaikan (naskah 4 §24) — peta
status yang menegakkannya ada di [`umpan_balik`].
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from hvx.modules import platform

Aksi = Literal["accepted", "rejected", "ignored", "modified", "snoozed"]
Alasan = Annotated[platform.TeksTanpaNul, Field(max_length=2000)]
_OUTCOME_MAKS_BYTE = 4_000


def _outcome_wajar(nilai: dict[str, Any]) -> dict[str, Any]:
    if len(json.dumps(nilai, ensure_ascii=False).encode()) > _OUTCOME_MAKS_BYTE:
        raise ValueError(f"outcome maksimal {_OUTCOME_MAKS_BYTE} byte")
    platform.tanpa_nul_bersarang(nilai)
    return nilai


Outcome = Annotated[dict[str, Any], AfterValidator(_outcome_wajar)]


class CatatUmpanBalik(BaseModel):
    """`POST /recommendations/{id}/feedback` — `{ action, reason?, outcome? }`."""

    model_config = ConfigDict(extra="forbid")

    action: Aksi
    reason: Alasan | None = None
    outcome: Outcome = Field(default_factory=dict)


class UmpanBalik(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    recommendation_id: UUID
    action: Aksi
    reason: str | None
    outcome: dict[str, Any]
    created_at: datetime


# ── Dashboard (6.1) & daftar rekomendasi (spec/04 Rekomendasi) ──


class Dimensi(BaseModel):
    """Satu dimensi dashboard (naskah 4 §28) — skor PLUS Why-nya. Bukan satu angka hidup."""

    model_config = ConfigDict(frozen=True)

    key: str
    value: float
    confidence: float
    evidence_count: int
    why: str


class Dasbor(BaseModel):
    """Beberapa dimensi, tiap skor punya Why (§28) — **hanya yang V0 ukur**.

    Sumbu yang belum punya ukuran disepakati (Finance/Social/Career/…, A-19/B-38)
    sengaja TIDAK ditampilkan: menyajikannya sebagai angka berarti mengambil posisi
    dalam model yang belum diputuskan pemilik. `dimensions` kosong = belum ada
    check-in (cold start)."""

    model_config = ConfigDict(frozen=True)

    as_of: date | None
    dimensions: list[Dimensi]


class RekomendasiRingkas(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    domain: str
    subject_type: str | None
    subject_id: UUID | None
    title: str
    body: str | None
    score: float | None
    scoring_version: str
    score_breakdown: dict[str, Any]
    confidence: float | None
    rationale: list[str]
    status: str
    created_at: datetime


class DaftarRekomendasi(BaseModel):
    items: list[RekomendasiRingkas]
    next_cursor: str | None  # spec/04 *Halaman* — `null` di halaman terakhir


# ── spec/07 6.2 — tinjauan mingguan (naskah 4 §31, K-45) ─────────────────────


class SumbuTinjauan(BaseModel):
    key: str
    label: str
    value: float
    previous: float | None  # minggu sebelumnya; None = tak ada data pembanding
    unit: Literal["0-1", "1-5", "jam"]
    evidence_count: int
    why: str


class ButirTinjauan(BaseModel):
    text: str
    evidence_count: int


class PertanyaanTinjauan(BaseModel):
    key: Literal["went_well", "changed", "failed", "why", "change_next_week"]
    question: str
    stance: Literal["state", "ask"]  # Confidence Layer 5.4 — tanpa butir, sistem bertanya
    items: list[ButirTinjauan]
    prompt: str


class TakDiukur(BaseModel):
    key: str
    label: str


class TinjauanMingguan(BaseModel):
    week: str
    start: date
    end: date
    complete: bool
    timezone: str
    axes: list[SumbuTinjauan]
    not_measured: list[TakDiukur]
    questions: list[PertanyaanTinjauan]
    review_version: str
