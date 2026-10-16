"""`events` — apa yang terjadi, sebagai sumber kebenaran perilaku.

Memiliki tabel: events (spec/06).
Dikerjakan: Sprint 3 (3.1–3.3) — spec/07.

Modul domain mengimpornya untuk MENERBITKAN (spec/06 aturan 6: tiap tulisan
domain menerbitkan event), di transaksi yang sama dengan tulisannya. Proses
`hvx.pekerja` memakainya untuk MENYALURKAN: relay kotak keluar → Redis Streams,
dan grup konsumen yang membaca isi event di bawah RLS pemiliknya (3.3).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .kontrak import REGISTRY, SUMBER, EventTidakSah, Sumber, payload_sah
from .penerbit import HasilTerbit, terbitkan
from .proyeksi import cari_penyelesaian, riwayat_habit, untuk_proyeksi
from .relay import LIHAT_BELAKANG_S, Relay, Rujukan, kunci_stream
from .stream import UMUR_MATI_S, EventMasuk, KonsumenStream, Penangan, kunci_mati, pangkas_mati

__all__ = [
    "LIHAT_BELAKANG_S",
    "REGISTRY",
    "SUMBER",
    "UMUR_MATI_S",
    "EventMasuk",
    "EventTidakSah",
    "HasilTerbit",
    "KonsumenStream",
    "Penangan",
    "Relay",
    "Rujukan",
    "Sumber",
    "cari_penyelesaian",
    "kunci_mati",
    "kunci_stream",
    "pangkas_mati",
    "payload_sah",
    "riwayat_habit",
    "terbitkan",
    "untuk_proyeksi",
]
