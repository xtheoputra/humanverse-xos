"""spec/07 5.4 — Confidence Layer (issue #34): *evidence_count rendah → sistem bertanya*.

Aturan murni (tanpa basis data). V0 menetapkan SATU ambang — nol bukti tidak boleh
jadi pernyataan — dan sengaja TIDAK menetapkan pita High/Medium/Low di atasnya
(milik pemilik, #34). Uji ini menjaga batas itu: ia tidak boleh diam-diam bergeser
ke "butuh dua bukti" atau ke "nol pun boleh dinyatakan".
"""

from __future__ import annotations

import pytest

from hvx.modules import intelligence
from hvx.modules.intelligence import Sikap


def test_nol_bukti_bertanya() -> None:
    assert intelligence.sikap(0) is Sikap.BERTANYA, "nol bukti harus BERTANYA"
    assert not intelligence.cukup_untuk_menyatakan(0), "nol bukti tidak cukup untuk menyatakan"


def test_satu_bukti_cukup_untuk_menyatakan() -> None:
    # Ambang V0 = 1: satu bukti sudah boleh dinyatakan. Apakah SATU cukup untuk
    # diyakini adalah pertanyaan pita (#34) — bukan pertanyaan sikap nol/bukan-nol.
    assert intelligence.sikap(1) is Sikap.MENYATAKAN, (
        "satu bukti harus boleh MENYATAKAN (ambang V0 = 1)"
    )
    assert intelligence.cukup_untuk_menyatakan(1)
    assert intelligence.BUKTI_MINIMUM == 1


@pytest.mark.parametrize("n", [2, 5, 18, 1000])
def test_bukti_banyak_tetap_menyatakan(n: int) -> None:
    assert intelligence.cukup_untuk_menyatakan(n)


def test_negatif_yang_mustahil_tetap_bertanya() -> None:
    # evidence_count integer tak pernah negatif (spec/01 CHECK >= 0); kalaupun begitu,
    # sisi amannya BERTANYA — bukan menyatakan dari bukti yang tak ada.
    assert intelligence.sikap(-1) is Sikap.BERTANYA, (
        "bukti negatif harus BERTANYA, bukan menyatakan"
    )
