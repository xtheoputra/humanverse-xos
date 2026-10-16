"""spec/07 5.6 — peta status umpan balik: *modified & snoozed bukan penolakan*.

Aturan murni (tanpa basis data): hanya `accepted`/`rejected` mengubah status
rekomendasi; `modified`/`snoozed`/`ignored` membiarkannya.
"""

from __future__ import annotations

import pytest

from hvx.modules import intelligence


@pytest.mark.parametrize(
    ("action", "awal", "harap"),
    [
        ("accepted", "shown", "accepted"),
        ("rejected", "shown", "rejected"),
        ("modified", "shown", "shown"),
        ("snoozed", "pending", "pending"),
        ("ignored", "shown", "shown"),
    ],
)
def test_status_sesudah(action: str, awal: str, harap: str) -> None:
    assert intelligence.status_sesudah(awal, action) == harap


@pytest.mark.parametrize("action", ["modified", "snoozed", "ignored"])
def test_modified_snoozed_ignored_bukan_penolakan(action: str) -> None:
    assert intelligence.status_sesudah("shown", action) != "rejected", (
        f"“{action}” diperlakukan sebagai penolakan (spec/07 5.6)"
    )
