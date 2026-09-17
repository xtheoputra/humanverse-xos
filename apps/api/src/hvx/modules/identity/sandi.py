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
* **Daftar tolak** (§3.1.1.2 yang sama — *SHALL*): kata dari konteks (nama
  layanan, email, nama tampilan), pengulangan, dan urutan papan ketik/angka
  ditolak. Panjang 15 saja meloloskan `passwordpassword`. 🔴 Pengulangan dinilai
  dari yang DIKETIK, bukan hanya kerangka huruf-angkanya: versi pertama
  menolak `!@#$%^&*()_+{}|:<>?` dan sandi emoji sebagai "repetitive" — aturan
  komposisi terselubung, yang pasal yang sama larang (tinjauan Sprint 1).
* **NFKC sebelum hashing** (§3.1.1.2 — *SHOULD*): "é" yang diketik sebagai satu
  kode di satu perangkat dan dua kode di perangkat lain adalah sandi yang sama.
  Diterapkan sebelum baris akun pertama — mengubahnya sesudah itu mematahkan
  hash yang sudah ada.
"""

from __future__ import annotations

import asyncio
import re
import secrets
import unicodedata
from functools import cache
from typing import Literal

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

PANJANG_MIN = 15
PANJANG_MAKS = 128

_hasher = PasswordHasher()

AlasanTolak = Literal["context", "repetitive", "sequential"]

# Kata konteks yang selalu ditolak, di luar email & nama pengguna itu sendiri.
_KATA_LAYANAN = ("humanverse", "humanversexos")
_URUTAN = (
    "0123456789",
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiopasdfghjklzxcvbnm",
    "1234567890qwertyuiop",
    "!@#$%^&*()_+",  # baris angka dengan Shift
)
_BUKAN_ALNUM = re.compile(r"[\W_]+")
_KATA_MIN = 4  # kata konteks yang lebih pendek terlalu umum untuk ditolak
_URUTAN_MIN = 8


def normalisasi(sandi: str) -> str:
    return unicodedata.normalize("NFKC", sandi)


def _inti(teks: str) -> str:
    return _BUKAN_ALNUM.sub("", normalisasi(teks).casefold())


def _berulang(teks: str) -> bool:
    """Sedikit karakter berbeda, atau satu potongan diulang utuh."""
    return len(set(teks)) < 4 or (teks + teks).find(teks, 1) < len(teks)


def _berurutan(teks: str) -> bool:
    return len(teks) >= _URUTAN_MIN and any(
        teks in arah * (len(teks) // len(arah) + 2) for u in _URUTAN for arah in (u, u[::-1])
    )


def alasan_ditolak(sandi: str, *, email: str, nama: str) -> AlasanTolak | None:
    """Kenapa sandi ini terlalu mudah ditebak — atau `None`. Tidak pernah mengutip sandinya.

    Dua bacaan atas sandi yang sama: yang DIKETIK (`penuh`), dan kerangka
    huruf-angkanya (`inti`) — `p.a.s.s.w.o.r.d` dan `password!!` berkerangka
    sama. Keduanya hanya bisa MENOLAK: kerangka yang kosong (sandi simbol atau
    emoji) tidak pernah menjadi alasan.
    """
    penuh = normalisasi(sandi).casefold()
    inti = _inti(sandi)
    lokal, _, domain = email.partition("@")
    kata = {*_KATA_LAYANAN, _inti(lokal), _inti(domain.split(".", 1)[0])}
    kata |= {_inti(k) for k in re.split(r"\s+", nama)}
    if any(len(k) >= _KATA_MIN and k in inti for k in kata):
        return "context"
    if _berulang(penuh) or (len(inti) >= _URUTAN_MIN and _berulang(inti)):
        return "repetitive"
    if _berurutan(penuh) or _berurutan(inti):
        return "sequential"
    return None


@cache
def _hash_pengalih() -> str:
    return _hasher.hash(secrets.token_urlsafe(32))


def hash_sandi(sandi: str) -> str:
    return _hasher.hash(normalisasi(sandi))


def cocokkan(hash_tersimpan: str | None, sandi: str) -> bool:
    """Selalu menjalankan satu verifikasi argon2 — juga untuk akun yang tidak ada."""
    try:
        return (
            _hasher.verify(hash_tersimpan or _hash_pengalih(), normalisasi(sandi))
            and hash_tersimpan is not None
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
