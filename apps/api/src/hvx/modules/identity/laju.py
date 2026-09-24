"""Kebijakan batas laju identity — spec/07 tugas 1.7. Mekanismenya di `platform`.

Tiga kunci, dan kenapa masing-masing ada:

* **per pengguna** — di dependensi autentikasi, jadi tiap rute bersesi
  terbatasi tanpa bisa lupa (batas per IP ada di middleware `platform`).
* **daftar & masuk per IP** — lebih ketat daripada permukaan umum: di situlah
  sandi ditebak dan akun dibuat massal. `refresh` sengaja TIDAK di sini: ia
  butuh token acak 256 bit, dan semua klien di balik satu NAT operator
  menyegarkan dari IP yang sama.
* **login gagal per akun** — kuncinya HMAC email, jadi berlaku sama bagi email
  yang terdaftar maupun tidak: 429 tidak membocorkan keberadaan akun. Jatahnya
  DIPAKAI sebelum argon2 — satu perintah atomik, dan serangan yang ditolak
  tidak membakar CPU — lalu dikosongkan begitu berhasil masuk. ⚠️ Ini batas
  LAJU (≤ 100 sekaligus, lalu terisi kembali), **bukan** penguncian sesudah 100
  kegagalan beruntun yang NIST SP 800-63B-4 §3.2.2 tuntut — dan penyerang yang
  terus mencoba bisa menahan pemilik akun di 429 selama ia mau (B-42, K-22).

🔴 Dua hal yang versi pertama salah, keduanya ditemukan tinjauan Sprint 1:

1. **Diperiksa dulu, dihitung sesudah argon2.** Dua belas tebakan serentak
   semuanya lolos pemeriksaan sebelum satu pun dihitung — batas 3 meloloskan 12.
2. **Kuncinya `email.lower()` Python.** Basis data mengenali akun lewat
   `citext`, yang memakai `lower()` PostgreSQL: `'İ'` menjadi `i` di sana dan
   `i̇` di Python. `vİctim@…` masuk ke akun `victim@…` dengan hitungan baru —
   tiap `i` menggandakan jatah. Kini kuncinya dibentuk basis data sendiri
   (`repository.cari_untuk_masuk`).
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request

from hvx.modules import platform


async def batasi_pengguna(request: Request, user_id: UUID) -> None:
    settings = platform.settings_dari(request)
    batas = platform.BatasLaju.dari_teks("pengguna", settings.rate_limit_user)
    hasil = await platform.pembatas_laju(request).ambil(batas, str(user_id))
    if not hasil.lolos:
        raise platform.galat_terlalu_sering(hasil)


async def batasi_kredensial_ip(request: Request) -> None:
    """Dependensi rute `/register` dan `/login`."""
    settings = platform.settings_dari(request)
    batas = platform.BatasLaju.dari_teks("kredensial-ip", settings.rate_limit_auth_ip)
    hasil = await platform.pembatas_laju(request).ambil(batas, platform.sidik_jaringan(request))
    if not hasil.lolos:
        raise platform.galat_terlalu_sering(hasil)


@dataclass(frozen=True)
class PenjagaGagalMasuk:
    pembatas: platform.PembatasLaju
    batas: platform.BatasLaju
    settings: platform.Settings

    def _subjek(self, kunci_akun: str) -> str:
        return platform.sidik(self.settings, "akun-masuk", kunci_akun)

    async def pakai(self, kunci_akun: str) -> None:
        """Satu tebakan = satu jatah, dipakai SEBELUM sandinya dicocokkan."""
        hasil = await self.pembatas.ambil(self.batas, self._subjek(kunci_akun))
        if not hasil.lolos:
            raise platform.galat_terlalu_sering(hasil)

    async def berhasil(self, kunci_akun: str) -> None:
        await self.pembatas.lupakan(self.batas, self._subjek(kunci_akun))


def penjaga_gagal_masuk(request: Request) -> PenjagaGagalMasuk:
    settings = platform.settings_dari(request)
    return PenjagaGagalMasuk(
        platform.pembatas_laju(request),
        platform.BatasLaju.dari_teks("gagal-masuk", settings.rate_limit_login_failures),
        settings,
    )
