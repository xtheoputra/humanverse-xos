"""`memory.ekstrak` tanpa basis data — yang ditolak sebelum menyentuh apa pun."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from hvx.modules import events, memory


async def test_event_tanpa_subjek_menjadi_galat_bukan_dilewati() -> None:
    """Kontrak `mood.logged` & `journal.created` selalu bersubjek (3.2). Yang tidak
    bisa diekstrak harus GAGAL — berakhir terlihat di stream mati — bukan di-ACK
    diam-diam tanpa memori (tinjauan penegak buta Sprint 3)."""
    kini = datetime.now(UTC)
    ev = events.EventMasuk(
        id=uuid4(),
        user_id=uuid4(),
        event_type="mood.logged",
        schema_version=1,
        occurred_at=kini,
        recorded_at=kini,
        source="app",
        subject_type=None,
        subject_id=None,
        payload={"valence": 3},
    )

    with pytest.raises(ValueError, match="subject_id"):
        await memory.ekstrak(None, ev)  # type: ignore[arg-type]  # ditolak sebelum conn dipakai
