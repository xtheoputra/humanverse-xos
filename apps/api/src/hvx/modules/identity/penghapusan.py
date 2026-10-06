"""Sapuan hapus akun, tahap 3–6 — spec/07 6.5 (Stage B), spec/01 "Prosedur hapus akun".

Tahap 1 (`DELETE /me`) hanya MENJADWALKAN. Yang sungguh menghapus adalah proses
pekerja, berkala, atas akun yang `deletion_scheduled_at <= now()`:

    kunci akun ─▶ tahap 4: buang titik Qdrant ─▶ tahap 5 · 3 · 6: satu transaksi ─▶ cabut sesi

* **Qdrant lebih dulu, sementara akunnya terkunci.** Urutan terbalik meninggalkan titik
  yatim tanpa pemilik yang tak bisa lagi ditemukan (user_id-nya sudah tidak ada).
  Urutan ini, bila gagal di tengah, hanya meninggalkan akun yang MASIH jatuh tempo dan
  dicoba lagi di putaran berikutnya — pembuangan titiknya menurut saringan `user_id`,
  jadi diulang aman. Kuncinya (`FOR NO KEY UPDATE`) menyerialkan `POST /me/restore`
  yang menyelip di batas waktu; restore sendiri sudah tertutup sesudah batas itu.
* **Tahap 5 · 3 · 6 satu transaksi** (fungsi `hapus_akun_jatuh_tempo`): jejak audit
  dialihkan ke id semu, akun dihapus (CASCADE), satu baris `account.deleted`.
* **Id semu = HMAC berkunci** (`platform.sidik`), bukan hash polos: id akun acak, tetapi
  siapa pun yang pernah melihatnya (cadangan, log lama) bisa mencocokkan hash polos.
  Tanpa kunci tak ada jalan balik; dengan kunci yang sama baris-baris audit satu akun
  tetap bisa dipertemukan — itulah gunanya jejak yang dipertahankan (C-9).
* **Tanpa Qdrant** (`buang_titik=None`): akun yang pernah punya titik DITUNDA, bukan
  dihapus — menghapus barisnya akan meninggalkan titiknya selamanya. Akun yang tak
  pernah disemat tetap dihapus.
* Sesi dicabut sesudah commit: login selama tenggang (untuk membatalkan) menciptakan
  sesi baru yang tidak ikut tercabut tahap 1. Pembersih lain (`sesudah`) berjalan di titik
  yang sama — jejak idempotensi di Redis, yang menunjuk pemiliknya selama 24 jam.

Satu akun gagal tidak menghentikan yang lain; yang gagal dicoba lagi putaran berikutnya.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository
from .sesi import PenyimpanSesi

log = structlog.get_logger("hvx.identity.penghapusan")

# Tahap 4 — dipasang titik rakit pekerja (identity tidak mengenal Qdrant, memory, atau
# siapa pun yang menyimpan turunan data pengguna di luar PostgreSQL).
PenghapusTitik = Callable[[UUID], Awaitable[None]]
# Pembersih SESUDAH commit — data turunan di luar PostgreSQL yang boleh gagal tanpa membatalkan
# penghapusan (jejak idempotensi di Redis). Akunnya sudah tiada: tak ada yang bisa diulang
# dari sini, jadi kegagalannya dicatat, tidak dilempar.
PembersihSesudah = Callable[[UUID], Awaitable[object]]

BATAS_SAPUAN = 20  # akun per putaran — tiap akun satu transaksi; sisanya putaran berikutnya


def id_semu(settings: platform.Settings, user_id: UUID) -> UUID:
    """Pengganti satu-arah `user_id` di jejak audit — tetap sama untuk akun yang sama."""
    return UUID(platform.sidik(settings, "akun-terhapus", str(user_id))[:32])


async def sapu_akun_jatuh_tempo(
    engine: AsyncEngine,
    settings: platform.Settings,
    *,
    sesi: PenyimpanSesi,
    buang_titik: PenghapusTitik | None,
    sesudah: Sequence[PembersihSesudah] = (),
    batas: int = BATAS_SAPUAN,
) -> int:
    """Hapus akun yang tenggangnya habis; jumlah akun yang terhapus putaran ini."""
    async with platform.transaksi_sistem(engine) as conn:
        jatuh_tempo = await repository.akun_jatuh_tempo(conn, batas)
    terhapus = 0
    for akun in jatuh_tempo:
        if akun.punya_titik and buang_titik is None:
            log.warning("hapus_akun.ditunda_tanpa_vektor", user_id=str(akun.user_id))
            continue
        try:
            async with platform.transaksi_sistem(engine) as conn:
                if not await repository.kunci_akun_jatuh_tempo(conn, akun.user_id):
                    continue  # dipulihkan di antara daftar dan kunci — bukan lagi jatuh tempo
                if buang_titik is not None:
                    await buang_titik(akun.user_id)
                dihapus = await repository.hapus_akun_jatuh_tempo(
                    conn, akun.user_id, id_semu(settings, akun.user_id)
                )
        except Exception:
            # Tahap yang gagal membatalkan transaksinya: akunnya utuh, dicoba lagi.
            log.exception("hapus_akun.gagal", user_id=str(akun.user_id))
            continue
        if not dihapus:
            continue
        terhapus += 1
        for bersihkan in (sesi.cabut_semua, *sesudah):
            try:
                await bersihkan(akun.user_id)
            except Exception:
                # Akunnya sudah tiada: token yang tersisa tidak melihat satu baris pun (RLS)
                # dan mati di penyegaran pertama; jejak Redis mati sendiri dalam 24 jam.
                log.exception("hapus_akun.pembersihan_gagal", user_id=str(akun.user_id))
    return terhapus
