"""spec/07 2.2 — *“uji: tier turun saat energi rendah”* (naskah 4 §34, Adaptive Habit Engine).

| naskah 4 §34 | energi | tier |
|---|---|---|
| Normal — Workout 60 menit | 3–5 / belum check-in | 0 |
| Energi rendah — Workout 30 menit | 2 | 1 |
| Energi sangat rendah — Mobility 10 menit | 1 | terakhir |
"""

from __future__ import annotations

import pytest

from hvx.modules.habits import tier_untuk_energi

# Contoh naskah 4 §34 apa adanya: tiga tingkat.
TIGA_TIER = 3


@pytest.mark.parametrize(
    ("energi", "tier"),
    [(None, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 2)],
)
def test_contoh_naskah_4_bagian_34(energi: int | None, tier: int) -> None:
    assert tier_untuk_energi(TIGA_TIER, energi) == tier


def test_tier_turun_saat_energi_rendah() -> None:
    normal = tier_untuk_energi(TIGA_TIER, 3)
    rendah = tier_untuk_energi(TIGA_TIER, 2)
    sangat_rendah = tier_untuk_energi(TIGA_TIER, 1)

    assert normal is not None
    assert rendah is not None
    assert sangat_rendah is not None
    assert normal < rendah < sangat_rendah, (
        f"tier tidak turun saat energi rendah: normal={normal} rendah={rendah} "
        f"sangat_rendah={sangat_rendah}"
    )


@pytest.mark.parametrize("jumlah", [1, 2, 3, 4, 5])
def test_energi_lebih_rendah_tidak_pernah_menyarankan_tier_lebih_berat(jumlah: int) -> None:
    saran = [tier_untuk_energi(jumlah, e) for e in (5, 4, 3, 2, 1)]
    angka = [s for s in saran if s is not None]

    assert len(angka) == 5
    assert angka == sorted(angka), f"{jumlah} tier: {saran}"
    assert all(0 <= s < jumlah for s in angka), f"tier di luar daftar: {saran}"


def test_sangat_rendah_memilih_tier_paling_ringan_juga_bila_tier_lebih_dari_tiga() -> None:
    assert tier_untuk_energi(5, 1) == 4
    assert tier_untuk_energi(5, 2) == 1


def test_satu_tier_selalu_tier_itu_dan_tanpa_tier_tanpa_saran() -> None:
    assert [tier_untuk_energi(1, e) for e in (None, 1, 2, 3)] == [0, 0, 0, 0]
    assert tier_untuk_energi(0, 1) is None


@pytest.mark.parametrize("energi", [0, 6, -1])
def test_energi_di_luar_skala_check_in_ditolak(energi: int) -> None:
    with pytest.raises(ValueError, match="1–5"):
        tier_untuk_energi(TIGA_TIER, energi)
