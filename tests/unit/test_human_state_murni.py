"""spec/07 5.3 — metrik Human State: *“tiap metrik punya value, confidence, evidence_count”*.

Fungsi murni (tanpa basis data): normalisasi skala 1–5 → 0–1, dan bentuk metrik.
"""

from __future__ import annotations

from hvx.modules import intelligence


def test_metrik_harian_menormalkan_skala() -> None:
    m = intelligence.metrik_harian(energy=5, focus=1)
    assert m["energy"] == {"value": 1.0, "confidence": 1.0, "evidence_count": 1}
    assert m["focus"] == {"value": 0.0, "confidence": 1.0, "evidence_count": 1}


def test_metrik_harian_nilai_tengah() -> None:
    m = intelligence.metrik_harian(energy=3, focus=2)
    assert m["energy"]["value"] == 0.5
    assert m["focus"]["value"] == 0.25


def test_metrik_harian_hanya_medan_dilaporkan() -> None:
    assert intelligence.metrik_harian(energy=4, focus=None) == {
        "energy": {"value": 0.75, "confidence": 1.0, "evidence_count": 1}
    }
    assert intelligence.metrik_harian(energy=None, focus=None) == {}


def test_tiap_metrik_punya_value_confidence_evidence() -> None:
    for m in intelligence.metrik_harian(energy=3, focus=2).values():
        assert set(m) == {"value", "confidence", "evidence_count"}
