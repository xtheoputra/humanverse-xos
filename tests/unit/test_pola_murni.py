"""spec/07 5.2 — pola perilaku: *“keluarannya asosiatif, bukan kausal”* (naskah 4 §7).

Fungsi pola murni (tanpa basis data): bentuk keluaran, keyakinan, bukti, dan —
yang mengikat — tidak pernah mengklaim SEBAB.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest

from hvx.modules import habits, intelligence, memory


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


# ── Tinjauan penegak buta S5–6 ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("jam", "bagian"),
    [
        (4, "malam"),
        (5, "pagi"),
        (10, "pagi"),
        (11, "siang"),
        (14, "siang"),
        (15, "sore"),
        (18, "sore"),
        (19, "malam"),
        (23, "malam"),
        (0, "malam"),
    ],
)
def test_pola_waktu_batas_bagian_hari(jam: int, bagian: str) -> None:
    p = intelligence.pola_waktu("Meditasi", [jam])
    assert p is not None
    assert f"dicatat pada {bagian} hari" in p.content, f"jam {jam} bukan {bagian}: {p.content}"


@pytest.mark.parametrize(
    "kalimat",
    [
        "tidur pendek menyebabkan mood turun",
        "begadang adalah penyebab lelah",
        "sebab itu kamu lelah",
        "mood turun karena begadang",
        "lelah akibat begadang",
        "begadang mengakibatkan lelah",
        "begadang memicu olahraga terlewat",
        "olahraga membuat tidur nyenyak",
        "Karena begadang, mood turun",
        "OLAHRAGA MEMBUAT TIDUR NYENYAK",
    ],
)
def test_tanpa_klaim_kausal_menolak_tiap_kata_sebab(kalimat: str) -> None:
    assert not intelligence.tanpa_klaim_kausal(kalimat), f"klaim sebab lolos penjaga: {kalimat!r}"


def test_konsistensi_tanpa_penyelesaian_tidak_dinyatakan() -> None:
    """B1: periode jatuh tempo yang kosong memberi tingkat 0,0 — bukan alasan menyatakan
    pola ber-`evidence_count` 0 (Confidence Layer 5.4, sisi tulis)."""
    r = habits.Rentetan(current=0, longest=0, completion_rate_30d=0.0)
    assert intelligence.pola_konsistensi("Baca", "day", r, 0) is None, (
        "pola konsistensi dinyatakan dari nol penyelesaian"
    )
    satu = intelligence.pola_konsistensi("Baca", "day", r, 1)
    assert satu is not None
    assert satu.evidence_count == 1


class _TakBolehMenulis:
    """Koneksi palsu: pola yang SEHARUSNYA ditolak tidak boleh sampai ke basis data."""

    def __init__(self, pesan: str) -> None:
        self.pesan = pesan

    async def execute(self, *_: object, **__: object) -> None:
        raise AssertionError(self.pesan)


async def test_catat_pola_menolak_keyakinan_di_luar_0_sampai_1() -> None:
    for salah in (Decimal("1.5"), Decimal("-0.1"), Decimal("NaN")):
        with pytest.raises(ValueError, match="confidence"):
            await memory.catat_pola(
                cast(Any, _TakBolehMenulis(f"pola ber-confidence {salah} sampai ke basis data")),
                uuid4(),
                id_=uuid4(),
                scope="habits",
                content="pola",
                confidence=salah,
                evidence_count=1,
                model_version="uji",
            )


async def test_catat_pola_menolak_scope_di_luar_daftar_resmi() -> None:
    with pytest.raises(ValueError, match="scope"):
        await memory.catat_pola(
            cast(Any, _TakBolehMenulis("pola ber-scope tak resmi sampai ke basis data")),
            uuid4(),
            id_=uuid4(),
            scope="bukan_scope_resmi",
            content="pola",
            confidence=Decimal("0.5"),
            evidence_count=1,
            model_version="uji",
        )
