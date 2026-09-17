"""Bentuk data publik `identity` — spec/04 bagian Identity."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PenggunaRingkas(BaseModel):
    """`user` di jawaban spec/04 — tanpa `password_hash`, selamanya."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    email: str
    status: str
    email_verified_at: datetime | None
    created_at: datetime
