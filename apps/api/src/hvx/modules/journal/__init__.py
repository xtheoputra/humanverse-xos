"""`journal` — apa yang ditulis pengguna untuk dirinya sendiri.

Memiliki tabel: journal_entries (spec/06).
Dikerjakan: Sprint 3 (3.4) — spec/07.

Modul domain. `GET /journal` tidak pernah mengembalikan `body` (spec/04).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .routes import router
from .schemas import Jurnal, RingkasanJurnal

__all__ = ["Jurnal", "RingkasanJurnal", "router"]
