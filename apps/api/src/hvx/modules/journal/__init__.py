"""`journal` — apa yang ditulis pengguna untuk dirinya sendiri.

Memiliki tabel: journal_entries (spec/06).
Dikerjakan: Sprint 3 (3.4) — spec/07.

Modul domain. `GET /journal` tidak pernah mengembalikan `body` (spec/04).
`memory` (lapisan di atasnya, K-17) membaca isinya untuk ekstraksi (3.6) lewat
`isi_untuk_ekstraksi` — satu-satunya jalan isi jurnal keluar dari modul ini — dan
menyelaraskan memorinya saat jurnal diubah atau dihapus lewat
`PendengarJurnalBerubah` yang dipasang titik rakit (K-23).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .privasi import BAGIAN_PRIVASI, PENGHAPUS_PRIVASI
from .routes import router
from .schemas import Jurnal, RingkasanJurnal
from .service import PendengarJurnalBerubah, isi_untuk_ekstraksi

__all__ = [
    "BAGIAN_PRIVASI",
    "PENGHAPUS_PRIVASI",
    "Jurnal",
    "PendengarJurnalBerubah",
    "RingkasanJurnal",
    "isi_untuk_ekstraksi",
    "router",
]
