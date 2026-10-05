"""spec/07 5.5 — mesin rekomendasi: *“skor 0–1, scoring_version, rationale terisi”*.

Skornya murni (tanpa basis data): rata-rata komponen bobot sama (docs/87), dan
Confidence Layer (5.4) — tanpa komponen, tidak ada skor.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from hvx.modules import intelligence


def test_tanpa_komponen_none() -> None:
    # Nol bukti → None (Confidence Layer 5.4): mesin tak menyekor dari ketiadaan.
    assert intelligence.nilai_rekomendasi({}) is None


def test_satu_komponen_skor_komponen_itu() -> None:
    skor = intelligence.nilai_rekomendasi({"context": 0.25})
    assert skor is not None
    assert skor.score == Decimal("0.25")
    assert skor.breakdown == {"context": 0.25, "weights": "equal"}


def test_rata_rata_bobot_sama() -> None:
    skor = intelligence.nilai_rekomendasi({"history": 0.8, "context": 0.6})
    assert skor is not None
    assert skor.score == Decimal("0.7"), "skor bukan rata-rata komponen (docs/87)"
    assert skor.breakdown == {"history": 0.8, "context": 0.6, "weights": "equal"}


@pytest.mark.parametrize("komponen", [{"history": 0.0}, {"history": 1.0, "context": 1.0}])
def test_skor_selalu_0_sampai_1(komponen: dict[str, float]) -> None:
    skor = intelligence.nilai_rekomendasi(komponen)
    assert skor is not None
    assert Decimal(0) <= skor.score <= Decimal(1)
