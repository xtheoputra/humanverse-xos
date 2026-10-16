"""`activities` — apa yang terjadi, dicatat atau disimpulkan.

Memiliki tabel: activities (spec/06).
Dikerjakan: Sprint 3 (3.8) — spec/07.

Modul domain. `source='inferred'` terpisah dari `manual` — mesin tidak boleh
belajar dari tebakannya sendiri: klien hanya bisa mencatat `manual`, dan
`catat_disimpulkan` (untuk Behavior Engine) hanya bisa mencatat `inferred`.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .routes import router
from .schemas import Aktivitas
from .service import catat_disimpulkan, catat_proyeksi, hapus_proyeksi, kosongkan_proyeksi

__all__ = [
    "Aktivitas",
    "catat_disimpulkan",
    "catat_proyeksi",
    "hapus_proyeksi",
    "kosongkan_proyeksi",
    "router",
]
