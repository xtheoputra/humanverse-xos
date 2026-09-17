"""Sandi — argon2id (spec/07 tugas 1.1; spec/01 `users.password_hash -- argon2id`).

* **argon2id dengan profil bawaan argon2-cffi** (RFC 9106, profil memori
  rendah: t=3 · m=64 MiB · p=4). Parameter tidak disetel di sini: parameter
  yang disetel tangan cenderung tidak pernah dinaikkan lagi. Kalau bawaan
  pustaka naik, hash lama DIPERBARUI saat login berhasil (`perlu_hash_ulang`).
* **Dijalankan di thread**, bukan di event loop: satu hash ≈ 50 ms CPU, dan
  event loop yang tertahan 50 ms menahan SEMUA permintaan lain.
* **Akun tak dikenal tetap diverifikasi** terhadap hash pengalih, supaya waktu
  jawaban tidak membocorkan email mana yang terdaftar.
* **Panjang, bukan aturan komposisi** (NIST SP 800-63B-4 §3.1.1.2): minimal 15
  karakter untuk sandi sebagai faktor tunggal, tanpa aturan "wajib angka &
  simbol"; maksimal 128 supaya hashing tidak bisa dijadikan alat DoS.
"""

from __future__ import annotations

import asyncio
import secrets
from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

PANJANG_MIN = 15
PANJANG_MAKS = 128

_hasher = PasswordHasher()


@cache
def _hash_pengalih() -> str:
    return _hasher.hash(secrets.token_urlsafe(32))


def hash_sandi(sandi: str) -> str:
    return _hasher.hash(sandi)


def cocokkan(hash_tersimpan: str | None, sandi: str) -> bool:
    """Selalu menjalankan satu verifikasi argon2 — juga untuk akun yang tidak ada."""
    try:
        return (
            _hasher.verify(hash_tersimpan or _hash_pengalih(), sandi) and hash_tersimpan is not None
        )
    except (VerificationError, InvalidHashError):
        return False


def perlu_hash_ulang(hash_tersimpan: str) -> bool:
    try:
        return _hasher.check_needs_rehash(hash_tersimpan)
    except InvalidHashError:
        return True


async def hash_sandi_async(sandi: str) -> str:
    return await asyncio.to_thread(hash_sandi, sandi)


async def cocokkan_async(hash_tersimpan: str | None, sandi: str) -> bool:
    return await asyncio.to_thread(cocokkan, hash_tersimpan, sandi)
