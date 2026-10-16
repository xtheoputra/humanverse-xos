"""`identity` — siapa pengguna ini, dan apa yang ia izinkan.

Memiliki tabel: users · consents · permissions · audit_logs (spec/06).
Dikerjakan: Sprint 1 (1.1–1.7) — spec/07.

Semua modul boleh mengimpornya untuk cek izin (spec/06). Pengguna MANUSIA —
identitas agent tinggal di `agents` (arch/03 §5).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .audit import AktorTipe, AuditTidakSah, audit
from .dependensi import PenggunaDiperlukan, PenggunaMasuk, pengguna_saat_ini, penyimpan_sesi
from .izin import (
    Aksi,
    IzinTidakSah,
    Keputusan,
    MesinIzin,
    Subjek,
    SubjekTipe,
    UbahanIzin,
    mesin_izin,
)
from .penghapusan import (
    BATAS_SAPUAN,
    PembersihSesudah,
    PenghapusTitik,
    id_semu,
    sapu_akun_jatuh_tempo,
)
from .persetujuan import (
    TUJUAN_LAYANAN,
    TUJUAN_PELATIHAN_MODEL,
    Persetujuan,
    PersetujuanTidakSah,
    boleh_dipakai_untuk,
    cabut_persetujuan,
    catat_persetujuan,
)
from .privasi import (
    BAGIAN_PRIVASI,
    BATAS_EKSPOR,
    KATEGORI,
    TIDAK_DIKUMPULKAN,
    BagianData,
    IzinDiminta,
    Kategori,
    Penghapus,
    bagian_sql,
    penghapus_sql,
)
from .repository import ambil_pengguna
from .routes import router, router_akun
from .routes_privasi import router_privasi
from .schemas import PenggunaRingkas
from .scope import SCOPE_RESMI, Scope
from .service import PendengarPendaftaran, PenggunaBaru, pastikan_akun_melayani
from .sesi import HasilPenyegaran, PenyimpanSesi, SesiAktif, Token

__all__ = [
    "BAGIAN_PRIVASI",
    "BATAS_EKSPOR",
    "BATAS_SAPUAN",
    "KATEGORI",
    "SCOPE_RESMI",
    "TIDAK_DIKUMPULKAN",
    "TUJUAN_LAYANAN",
    "TUJUAN_PELATIHAN_MODEL",
    "Aksi",
    "AktorTipe",
    "AuditTidakSah",
    "BagianData",
    "HasilPenyegaran",
    "IzinDiminta",
    "IzinTidakSah",
    "Kategori",
    "Keputusan",
    "MesinIzin",
    "PembersihSesudah",
    "PendengarPendaftaran",
    "PenggunaBaru",
    "PenggunaDiperlukan",
    "PenggunaMasuk",
    "PenggunaRingkas",
    "Penghapus",
    "PenghapusTitik",
    "PenyimpanSesi",
    "Persetujuan",
    "PersetujuanTidakSah",
    "Scope",
    "SesiAktif",
    "Subjek",
    "SubjekTipe",
    "Token",
    "UbahanIzin",
    "ambil_pengguna",
    "audit",
    "bagian_sql",
    "boleh_dipakai_untuk",
    "cabut_persetujuan",
    "catat_persetujuan",
    "id_semu",
    "mesin_izin",
    "pastikan_akun_melayani",
    "pengguna_saat_ini",
    "penghapus_sql",
    "penyimpan_sesi",
    "router",
    "router_akun",
    "router_privasi",
    "sapu_akun_jatuh_tempo",
]
