"""Bentuk data `memory` — spec/01 §5 `memories`.

Belum ada rute HTTP memori di V0 (spec/04): pembacanya tool `memory.search`
(Sprint 4) lewat `PencariMemori`. Bentuk ini kontraknya.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class MemoriDitemukan:
    memori: Memori
    # Kosinus penyemat `memori.model_version` — hanya bermakna di antara hasil satu kueri.
    skor: float


@dataclass(frozen=True)
class HasilCariMemori:
    """`items` — terurut skor turun. `perlu_izin` — scope manifest yang menunggu
    keputusan pengguna (`ask`): pemanggil (gerbang risiko 4.5) yang memintanya,
    bukan pencarian yang diam-diam melewatinya."""

    items: list[MemoriDitemukan]
    scope_dipakai: list[str] = field(default_factory=list)
    perlu_izin: list[str] = field(default_factory=list)
