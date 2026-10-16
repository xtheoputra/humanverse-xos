"""spec/07 5.3 — metrik Human State: *“tiap metrik punya value, confidence, evidence_count”*.

Fungsi murni (tanpa basis data): normalisasi skala 1–5 → 0–1, dan bentuk metrik.
"""

from __future__ import annotations

from datetime import date
from typing import Any, cast
from uuid import uuid4

import pytest

from hvx.modules import intelligence, profile


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


# ── Tinjauan penegak buta S5–6: penjaga bentuk di pintu tulis `profile` ─────────────


class _TakBolehMenulis:
    """Koneksi palsu: human_state yang SEHARUSNYA ditolak tidak boleh sampai ke basis data."""

    def __init__(self, pesan: str) -> None:
        self.pesan = pesan

    async def execute(self, *_: object, **__: object) -> None:
        raise AssertionError(self.pesan)


@pytest.mark.parametrize(
    "metrik",
    [
        {"energy": {"value": 0.5, "evidence_count": 1}},  # tanpa confidence
        {"energy": {"value": 0.5, "confidence": 1.0}},  # tanpa evidence_count
        {"energy": {"value": 0.5, "confidence": 1.0, "evidence_count": 1, "tebakan": True}},
    ],
)
async def test_simpan_human_state_menolak_metrik_tanpa_bentuk_lengkap(
    metrik: dict[str, dict[str, Any]],
) -> None:
    with pytest.raises(ValueError, match="wajib tepat"):
        await profile.simpan_human_state(
            cast(Any, _TakBolehMenulis("metrik tanpa {value,confidence,evidence_count} ditulis")),
            uuid4(),
            for_date=date(2026, 9, 20),
            metrics=metrik,
            model_version="uji",
        )


async def test_simpan_human_state_menolak_tanpa_metrik() -> None:
    with pytest.raises(ValueError, match="tanpa metrik"):
        await profile.simpan_human_state(
            cast(Any, _TakBolehMenulis("human_state tanpa metrik ditulis")),
            uuid4(),
            for_date=date(2026, 9, 20),
            metrics={},
            model_version="uji",
        )
