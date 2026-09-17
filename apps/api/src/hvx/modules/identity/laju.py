"""Kebijakan batas laju identity — spec/07 tugas 1.7. Mekanismenya di `platform`.

Tiga kunci, dan kenapa masing-masing ada:

* **per pengguna** — di dependensi autentikasi, jadi tiap rute bersesi
  terbatasi tanpa bisa lupa (batas per IP ada di middleware `platform`).
* **daftar & masuk per IP** — lebih ketat daripada permukaan umum: di situlah
  sandi ditebak dan akun dibuat massal. `refresh` sengaja TIDAK di sini: ia
  butuh token acak 256 bit, dan semua klien di balik satu NAT operator
  menyegarkan dari IP yang sama.
* **login gagal per akun** — NIST SP 800-63B-4 membatasi kegagalan beruntun
  per akun (≤100). Kuncinya HMAC email, jadi berlaku sama bagi email yang
  terdaftar maupun tidak: 429 tidak membocorkan keberadaan akun. Diperiksa
  SEBELUM argon2 (serangan tidak membakar CPU), dihitung hanya bila sandinya
  salah, dan dihapus begitu berhasil masuk — itu yang membuatnya "beruntun".
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
    subjek: str

    async def periksa(self) -> None:
        """Tanpa memakai jatah: masih bolehkah satu tebakan lagi?"""
        hasil = await self.pembatas.ambil(self.batas, self.subjek, catat=False)
        if not hasil.lolos:
            raise platform.galat_terlalu_sering(hasil)

    async def gagal(self) -> None:
        await self.pembatas.ambil(self.batas, self.subjek)

    async def berhasil(self) -> None:
        await self.pembatas.lupakan(self.batas, self.subjek)


def penjaga_gagal_masuk(request: Request, email: str) -> PenjagaGagalMasuk:
    settings = platform.settings_dari(request)
    return PenjagaGagalMasuk(
        platform.pembatas_laju(request),
        platform.BatasLaju.dari_teks("gagal-masuk", settings.rate_limit_login_failures),
        # `users.email` bertipe citext: huruf besar-kecil satu akun yang sama
        platform.sidik(settings, "akun-masuk", email.strip().lower()),
    )
