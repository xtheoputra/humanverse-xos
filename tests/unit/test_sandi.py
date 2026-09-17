"""spec/07 1.1 — argon2id."""

from __future__ import annotations

from argon2 import PasswordHasher

from hvx.modules.identity import sandi


def test_hash_adalah_argon2id_dan_bisa_diverifikasi() -> None:
    h = sandi.hash_sandi("kuda-baterai-staples-benar")

    assert h.startswith("$argon2id$")
    assert sandi.cocokkan(h, "kuda-baterai-staples-benar")
    assert not sandi.cocokkan(h, "kuda-baterai-staples-salah")


def test_akun_tak_dikenal_tetap_diverifikasi_dan_selalu_gagal() -> None:
    assert not sandi.cocokkan(None, "apa-pun-yang-dikirim-penyerang")


def test_hash_rusak_bukan_galat_melainkan_gagal() -> None:
    assert not sandi.cocokkan("$bukan$hash", "x")
    assert sandi.perlu_hash_ulang("$bukan$hash")


def test_hash_berparameter_lemah_perlu_dihash_ulang() -> None:
    lemah = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash("sandi-lama-panjang")

    assert sandi.perlu_hash_ulang(lemah)
    assert not sandi.perlu_hash_ulang(sandi.hash_sandi("sandi-baru-panjang"))
