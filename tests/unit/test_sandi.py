"""spec/07 1.1 — argon2id."""

from __future__ import annotations

import pytest
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


def test_sandi_dinormalisasi_nfkc_sebelum_hashing() -> None:
    satu_kode = "café-di-pagi-hari-2026"  # é sebagai satu kode
    dua_kode = "café-di-pagi-hari-2026"  # e + tanda aksen gabungan

    assert satu_kode != dua_kode
    assert sandi.cocokkan(sandi.hash_sandi(satu_kode), dua_kode), (
        "sandi yang sama dari perangkat lain ditolak — NFKC tidak diterapkan"
    )


@pytest.mark.parametrize(
    ("kata_sandi", "alasan"),
    [
        ("passwordpassword", "repetitive"),
        ("aaaaaaaaaaaaaaaa", "repetitive"),
        ("ab-ab-ab-ab-ab-ab-ab", "repetitive"),
        ("!!!!!!!!!!!!!!!!", "repetitive"),
        ("1234567890123456", "sequential"),
        ("9876543210987654", "sequential"),
        ("qwertyuiopasdfghjk", "sequential"),
        ("abcdefghijklmnopq", "sequential"),
        ("nadiaputri-kopi-pagi", "context"),  # bagian lokal email
        ("Putri Senang Sekali 7", "context"),  # nama tampilan
        ("aku-suka-HumanVerse-99", "context"),  # nama layanan
    ],
)
def test_daftar_tolak_konteks_pengulangan_dan_urutan(kata_sandi: str, alasan: str) -> None:
    assert (
        sandi.alasan_ditolak(kata_sandi, email="nadia.putri@contoh.id", nama="Nadia Putri")
        == alasan
    )


@pytest.mark.parametrize(
    "kata_sandi",
    ["kuda-baterai-staples-benar", "sandi-panjang-uji-2026", "蜡烛 在 窗边 慢慢 燃烧 着"],
)
def test_sandi_yang_wajar_lolos_daftar_tolak(kata_sandi: str) -> None:
    assert (
        sandi.alasan_ditolak(kata_sandi, email="nadia.putri@contoh.id", nama="Nadia Putri") is None
    )
