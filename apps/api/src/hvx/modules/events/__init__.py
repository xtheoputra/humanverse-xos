"""`events` — apa yang terjadi, sebagai sumber kebenaran perilaku.

Memiliki tabel: events (spec/06).
Dikerjakan: Sprint 3 (3.1–3.3) — spec/07.

Modul domain mengimpornya untuk MENERBITKAN (spec/06 aturan 6: tiap tulisan
domain menerbitkan event), di transaksi yang sama dengan tulisannya. Proses
`hvx.pekerja` memakainya untuk MENYALURKAN: relay kotak keluar → Redis Streams,
dan grup konsumen yang membaca isi event di bawah RLS pemiliknya (3.3).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .kontrak import (
    ADMISI,
    REGISTRY,
    SUMBER,
    Admisi,
    EventTidakSah,
    Sumber,
    admisi_sah,
    payload_sah,
)
from .penerbit import HasilTerbit, terbitkan
from .privasi import (
    BAGIAN_PRIVASI,
    KATEGORI_EVENT,
    PENGHAPUS_PRIVASI,
    hapus_riwayat,
    hapus_riwayat_subjek,
    jenis_untuk,
)
from .proyeksi import cari_penyelesaian, riwayat_habit, untuk_proyeksi
from .relay import LIHAT_BELAKANG_S, Relay, Rujukan, kunci_stream
from .stream import (
    UMUR_MATI_S,
    EventMasuk,
    HasilPutarUlang,
    KonsumenStream,
    Penangan,
    daftar_mati,
    kunci_mati,
    pangkas_mati,
    putar_ulang_mati,
)

__all__ = [
    "ADMISI",
    "BAGIAN_PRIVASI",
    "KATEGORI_EVENT",
    "LIHAT_BELAKANG_S",
    "PENGHAPUS_PRIVASI",
    "REGISTRY",
    "SUMBER",
    "UMUR_MATI_S",
    "Admisi",
    "EventMasuk",
    "EventTidakSah",
    "HasilPutarUlang",
    "HasilTerbit",
    "KonsumenStream",
    "Penangan",
    "Relay",
    "Rujukan",
    "Sumber",
    "admisi_sah",
    "cari_penyelesaian",
    "daftar_mati",
    "hapus_riwayat",
    "hapus_riwayat_subjek",
    "jenis_untuk",
    "kunci_mati",
    "kunci_stream",
    "pangkas_mati",
    "payload_sah",
    "putar_ulang_mati",
    "riwayat_habit",
    "terbitkan",
    "untuk_proyeksi",
]
