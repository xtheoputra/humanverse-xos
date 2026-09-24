"""spec/07 4.4 — keputusan tiap run: keyakinan + alasan wajib; `decision` bukan penalaran.

Konstitusi Pasal 3 (arch/08 §4): *tiap keluaran agent wajib membawa `rationale` +
`confidence`*. Naskah 5 §24: jejak audit menyimpan metadata, **bukan hidden
chain-of-thought mentah** — `aksi` (kolom `decision`) hanya skalar pendek.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from hvx.modules.agents import Keputusan, KeputusanTidakSah, periksa_keputusan

SAH = Keputusan(
    "Tidurmu 6 jam semalam.", Decimal("0.7"), ("Check-in 2026-09-20",), {"action": "reply"}
)


def _dengan(**ganti: Any) -> Keputusan:
    return Keputusan(**{**SAH.__dict__, **ganti})


def test_keputusan_sah_diterima() -> None:
    periksa_keputusan(SAH)
    periksa_keputusan(_dengan(confidence=Decimal(0), aksi={"action": "reply", "habits": 2}))


RUSAK = [
    ("tanpa alasan", {"rationale": ()}),
    ("alasan kosong", {"rationale": ("  ",)}),
    ("alasan terlalu banyak", {"rationale": tuple(f"a{i}" for i in range(11))}),
    ("alasan sepanjang esai", {"rationale": ("x" * 301,)}),
    ("keyakinan di atas 1", {"confidence": Decimal("1.5")}),
    ("keyakinan float, bukan Decimal", {"confidence": 0.5}),
    ("balasan kosong", {"teks": " "}),
    ("aksi tanpa action", {"aksi": {"habits": 2}}),
    ("aksi bersarang — penalaran", {"aksi": {"action": "reply", "langkah": {"1": "pikir"}}}),
    ("aksi berisi tulisan panjang", {"aksi": {"action": "reply", "isi": "x" * 121}}),
    ("kunci aksi bukan snake_case", {"aksi": {"action": "reply", "Isi Pesan": 1}}),
]


@pytest.mark.parametrize(("maksud", "ganti"), RUSAK, ids=[r[0] for r in RUSAK])
def test_keputusan_rusak_ditolak(maksud: str, ganti: dict[str, Any]) -> None:
    try:
        periksa_keputusan(_dengan(**ganti))
    except KeputusanTidakSah:
        return
    raise AssertionError(f"keputusan rusak diterima — {maksud}")
