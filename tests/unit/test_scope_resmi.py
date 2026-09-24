"""spec/05 *Daftar scope resmi V0* (E-180) == `identity.SCOPE_RESMI` — satu daftar, dua tempat.

Tinjauan kontrak Sprint 3 (K8): AGENTS.md menuntut scope baru masuk spec/05 DAN kode
di PR yang sama — tetapi tidak ada yang membacanya. Menambah `"health"` ke kode saja
lolos seluruh suite. Seperti `test_kontrak_event.py` untuk spec/03, tabel di dokumen
adalah pembandingnya.
"""

from __future__ import annotations

import re
from pathlib import Path

from hvx.modules.identity import SCOPE_RESMI

SPEC05 = Path(__file__).resolve().parents[2] / "spec" / "05-AGENT-CONTRACTS.md"


def _tabel_spec05() -> dict[str, bool]:
    teks = SPEC05.read_text(encoding="utf-8")
    bagian = teks.split("## 🔧 Daftar scope resmi V0", 1)[1].split("\n## ", 1)[0]
    baris = re.findall(r"^\| `([a-z_]+)` \|[^|]*\| ([^|]*) \|", bagian, re.M)
    return {nama: "✅" in sensitif for nama, sensitif in baris}


def test_daftar_scope_resmi_spec05_sama_dengan_kode() -> None:
    di_spec = _tabel_spec05()

    assert di_spec, "tabel Daftar scope resmi spec/05 tidak terbaca — pembanding buta?"
    assert di_spec == {n: s.sensitif for n, s in SCOPE_RESMI.items()}, (
        f"spec/05 ≠ identity.SCOPE_RESMI: spec {di_spec} · kode "
        f"{ {n: s.sensitif for n, s in SCOPE_RESMI.items()} }"
    )
