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
from .persetujuan import (
    TUJUAN_LAYANAN,
    TUJUAN_PELATIHAN_MODEL,
    Persetujuan,
    PersetujuanTidakSah,
    boleh_dipakai_untuk,
    cabut_persetujuan,
    catat_persetujuan,
)
from .repository import ambil_pengguna
from .routes import router
from .schemas import PenggunaRingkas
from .scope import SCOPE_RESMI, Scope
from .service import PendengarPendaftaran, PenggunaBaru
from .sesi import HasilPenyegaran, PenyimpanSesi, SesiAktif, Token

__all__ = [
    "SCOPE_RESMI",
    "TUJUAN_LAYANAN",
    "TUJUAN_PELATIHAN_MODEL",
    "Aksi",
    "AktorTipe",
    "AuditTidakSah",
    "HasilPenyegaran",
    "IzinTidakSah",
    "Keputusan",
    "MesinIzin",
    "PendengarPendaftaran",
    "PenggunaBaru",
    "PenggunaDiperlukan",
    "PenggunaMasuk",
    "PenggunaRingkas",
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
    "boleh_dipakai_untuk",
    "cabut_persetujuan",
    "catat_persetujuan",
    "mesin_izin",
    "pengguna_saat_ini",
    "penyimpan_sesi",
    "router",
]
