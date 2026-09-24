"""Adaptive Habit Engine — naskah 4 §34, spec/07 2.2: *“tier turun saat energi rendah”*.

| Kondisi (naskah 4 §34) | `daily_checkins.energy` (1–5) | Tier yang disarankan |
|---|---|---|
| Normal — *Workout 60 menit* | 3–5, atau belum check-in | 0 — versi penuh |
| Energi rendah — *Workout 30 menit* | 2 | 1 |
| Energi sangat rendah — *Mobility 10 menit* | 1 | tier **terakhir** — yang paling ringan |

*“Consistency > Perfection”* dan *“Bukan menyalahkan user”* (naskah 4 §33–§34):
tier yang lebih ringan adalah jalan untuk TETAP menjalankan habit di hari yang
berat, bukan hukuman — penyelesaian dengan `tier_used` > 0 tetap `done`, dan
tetap menyambung rentetan (`rentetan.py`).

🔧 **Pemetaan angka 1–5 ke tiga kondisi naskah adalah keputusan teknis (K-23)**:
naskah menyebut *rendah* dan *sangat rendah* tanpa skala; skala check-in V0
(`spec/01 daily_checkins.energy`) 1–5, dan 3 titik tengahnya. Belum check-in
= normal: sistem tidak menurunkan target seseorang karena ia belum menjawab.
"""

from __future__ import annotations

ENERGI_RENDAH = 2
ENERGI_SANGAT_RENDAH = 1


def tier_untuk_energi(jumlah_tier: int, energi: int | None) -> int | None:
    """Indeks tier yang disarankan — `None` bila habit tidak punya tier sama sekali."""
    if jumlah_tier < 0:
        raise ValueError("jumlah_tier tidak boleh negatif")
    if energi is not None and not 1 <= energi <= 5:
        raise ValueError("energi check-in wajib 1–5 (spec/01 daily_checkins.energy)")
    if jumlah_tier == 0:
        return None
    if energi is None or energi > ENERGI_RENDAH:
        return 0
    if energi == ENERGI_RENDAH:
        return min(1, jumlah_tier - 1)
    return jumlah_tier - 1
