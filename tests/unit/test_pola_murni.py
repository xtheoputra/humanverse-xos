"""spec/07 5.2 — pola perilaku: *“keluarannya asosiatif, bukan kausal”* (naskah 4 §7).

Fungsi pola murni (tanpa basis data): bentuk keluaran, keyakinan, bukti, dan —
yang mengikat — tidak pernah mengklaim SEBAB.
"""

from __future__ import annotations

from decimal import Decimal

from hvx.modules import habits, intelligence


def test_pola_hari_menyebut_hari_terpusat_dan_asosiatif() -> None:
    # weekday(): 5 = Sabtu (3×), 2 = Rabu (1×)
    p = intelligence.pola_hari("Lari pagi", [5, 5, 5, 2])
    assert p is not None
    assert "Sabtu" in p.content
    assert "(3/4)" in p.content
    assert "paling sering" in p.content
    assert p.confidence == Decimal(3) / Decimal(4)
    assert p.evidence_count == 4
    assert intelligence.tanpa_klaim_kausal(p.content)


def test_pola_hari_tanpa_data_none() -> None:
    assert intelligence.pola_hari("Lari", []) is None


def test_pola_waktu_mengelompokkan_jam_lokal() -> None:
    # 8,9,9 → pagi (3×); 20 → malam (1×)
    p = intelligence.pola_waktu("Meditasi", [8, 9, 9, 20])
    assert p is not None
    assert "pagi" in p.content
    assert "(3/4)" in p.content
    assert "dicatat" in p.content
    assert p.confidence == Decimal(3) / Decimal(4)
    assert intelligence.tanpa_klaim_kausal(p.content)


def test_pola_konsistensi_dari_rentetan() -> None:
    r = habits.Rentetan(current=3, longest=5, completion_rate_30d=0.8)
    p = intelligence.pola_konsistensi("Baca buku", "day", r, 12)
    assert p is not None
    assert "80%" in p.content
    assert "berjalan 3" in p.content
    assert "terpanjang 5" in p.content
    assert p.confidence == Decimal("0.8")
    assert p.evidence_count == 12
    assert intelligence.tanpa_klaim_kausal(p.content)


def test_pola_konsistensi_tanpa_periode_jatuh_tempo_none() -> None:
    r = habits.Rentetan(current=0, longest=0, completion_rate_30d=None)
    assert intelligence.pola_konsistensi("Baca", "day", r, 0) is None
    assert intelligence.pola_konsistensi("Baca", "day", None, 0) is None


def test_tanpa_klaim_kausal_menolak_kata_sebab() -> None:
    assert intelligence.tanpa_klaim_kausal("paling sering diselesaikan pada hari Sabtu")
    assert not intelligence.tanpa_klaim_kausal("tidur pendek menyebabkan mood turun")
    assert not intelligence.tanpa_klaim_kausal("mood turun karena begadang")
    assert not intelligence.tanpa_klaim_kausal("begadang memicu olahraga terlewat")
