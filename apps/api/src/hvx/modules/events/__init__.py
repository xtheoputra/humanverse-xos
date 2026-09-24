"""`events` — apa yang terjadi, sebagai sumber kebenaran perilaku.

Memiliki tabel: events (spec/06).
Dikerjakan: Sprint 3 (3.1–3.3) — spec/07.

Modul domain mengimpornya untuk MENERBITKAN (spec/06 aturan 6: tiap tulisan
domain menerbitkan event), di transaksi yang sama dengan tulisannya.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .kontrak import REGISTRY, SUMBER, EventTidakSah, Sumber, payload_sah
from .penerbit import HasilTerbit, terbitkan

__all__ = [
    "REGISTRY",
    "SUMBER",
    "EventTidakSah",
    "HasilTerbit",
    "Sumber",
    "payload_sah",
    "terbitkan",
]
