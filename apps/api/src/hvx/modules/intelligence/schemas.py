"""Bentuk data umpan balik rekomendasi — spec/04 `POST /recommendations/{id}/feedback`.

`action` persis lima nilai `recommendation_feedback.action` (spec/01). `modified`
dan `snoozed` ada DI SINI, sejajar `accepted`/`rejected`, karena memilih B setelah
disarankan A bukan penolakan, dan menunda bukan mengabaikan (naskah 4 §24) — peta
status yang menegakkannya ada di [`umpan_balik`].
"""

from __future__ import annotations

import json
from datetime import datetime
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
