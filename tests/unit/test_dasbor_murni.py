"""spec/07 6.1 — dashboard: *beberapa dimensi, tiap skor punya Why* (naskah 4 §28).

Perakitan dimensi murni (tanpa basis data): tiap dimensi membawa Why, urut stabil,
dan "satu angka Life Score" yang pemilik tolak tidak pernah muncul.
"""

from __future__ import annotations

from datetime import date

from hvx.modules import intelligence

_METRIK = {
    "energy": {"value": 0.75, "confidence": 1.0, "evidence_count": 1},
    "focus": {"value": 0.25, "confidence": 1.0, "evidence_count": 1},
}


def test_tiap_dimensi_punya_why() -> None:
    dims = intelligence.dimensi_dari_metrik(_METRIK, date(2026, 9, 20))
    assert [d.key for d in dims] == ["energy", "focus"], "urut dimensi tidak stabil"
    assert all(d.why.strip() for d in dims), "ada dimensi tanpa Why (§28)"
    assert "2026-09-20" in dims[0].why, "Why tidak menyebut dari mana skornya"
    assert (dims[0].value, dims[0].confidence, dims[0].evidence_count) == (0.75, 1.0, 1)


def test_beberapa_dimensi_bukan_satu_angka() -> None:
    dims = intelligence.dimensi_dari_metrik(_METRIK, date(2026, 9, 20))
    assert len(dims) >= 2, "dashboard menyusut jadi satu angka — justru yang §28 tolak"


def test_tanpa_metrik_tanpa_dimensi() -> None:
    assert intelligence.dimensi_dari_metrik({}, date(2026, 9, 20)) == []


def test_why_memakai_label_manusiawi() -> None:
    dims = intelligence.dimensi_dari_metrik(_METRIK, date(2026, 9, 20))
    assert [d.why.split()[0] for d in dims] == ["Energi", "Fokus"], (
        "Why memakai key mentah, bukan label manusiawi"
    )
