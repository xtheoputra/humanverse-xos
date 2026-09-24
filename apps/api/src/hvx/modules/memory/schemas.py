"""Bentuk data `memory` — spec/01 §5 `memories`.

Belum ada rute HTTP memori di V0 (spec/04). Bentuk ini kontraknya.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Memori:
    """Satu memori — `kind` menjawab BAGAIMANA ia diambil, `scope` SIAPA boleh membacanya."""

    id: UUID
    kind: str
    scope: str
    content: str
    summary: str | None
    confidence: Decimal
    evidence_count: int
    model_version: str | None
    source_event_id: UUID | None
    valid_from: datetime
    valid_until: datetime | None
    created_at: datetime
