"""spec/07 1.1 — argon2id."""

from __future__ import annotations

import threading
from typing import Any

import pytest
from argon2 import PasswordHasher

from hvx.modules.identity import sandi


def test_hash_adalah_argon2id_dan_bisa_diverifikasi() -> None:
    h = sandi.hash_sandi("kuda-baterai-staples-benar")

    assert h.startswith("$argon2id$")
    assert sandi.cocokkan(h, "kuda-baterai-staples-benar")
    assert not sandi.cocokkan(h, "kuda-baterai-staples-salah")


class _HasherDihitung:
    """Membungkus hasher asli — `PasswordHasher` tidak bisa ditambal per atribut."""

    def __init__(self, asli: PasswordHasher) -> None:
        self._asli = asli
        self.verifikasi = 0

    def verify(self, hash_: str, kata_sandi: str) -> bool:
        self.verifikasi += 1
        return self._asli.verify(hash_, kata_sandi)

    def __getattr__(self, nama: str) -> Any:
        return getattr(self._asli, nama)


def test_akun_tak_dikenal_tetap_menjalankan_satu_verifikasi_argon2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """🔴 Tinjauan Sprint 1: uji versi pertama hanya menuntut hasilnya `False` —
    jalan pintas `if hash is None: return False` lulus, dan jawaban untuk email
    tak terdaftar ±40 ms lebih cepat daripada sandi salah."""
    sandi._hash_pengalih()  # dibuat sekali di luar hitungan
    hasher = _HasherDihitung(sandi._hasher)
    monkeypatch.setattr(sandi, "_hasher", hasher)

    assert not sandi.cocokkan(None, "apa-pun-yang-dikirim-penyerang")
    assert hasher.verifikasi == 1, (
        "akun tak dikenal tidak diverifikasi argon2 — waktunya membocorkan keberadaan akun"
    )


async def test_argon2_dijalankan_di_thread_bukan_di_event_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Satu hash ≈ 50 ms CPU: di event loop ia menahan SEMUA permintaan lain."""
    utas: list[int] = []
    hash_asli, cocokkan_asli = sandi.hash_sandi, sandi.cocokkan

    def hash_diamati(kata_sandi: str) -> str:
        utas.append(threading.get_ident())
        return hash_asli(kata_sandi)

    def cocokkan_diamati(hash_tersimpan: str | None, kata_sandi: str) -> bool:
        utas.append(threading.get_ident())
        return cocokkan_asli(hash_tersimpan, kata_sandi)

    monkeypatch.setattr(sandi, "hash_sandi", hash_diamati)
    monkeypatch.setattr(sandi, "cocokkan", cocokkan_diamati)

    h = await sandi.hash_sandi_async("kuda-baterai-staples-benar")
    assert await sandi.cocokkan_async(h, "kuda-baterai-staples-benar")

    assert len(utas) == 2
    assert threading.get_ident() not in utas, "argon2 dijalankan di event loop, bukan di thread"


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
    # Arah sebaliknya: yang DIDAFTARKAN dari perangkat berbentuk-dua-kode. Versi
    # pertama uji ini hanya menguji satu arah — hash tanpa NFKC tetap lulus.
    assert sandi.cocokkan(sandi.hash_sandi(dua_kode), satu_kode), (
        "sandi yang didaftarkan dari perangkat lain tidak bisa dipakai masuk — "
        "NFKC tidak diterapkan saat hashing"
    )


@pytest.mark.parametrize(
    ("kata_sandi", "alasan"),
    [
        ("passwordpassword", "repetitive"),
        ("aaaaaaaaaaaaaaaa", "repetitive"),
        ("ab-ab-ab-ab-ab-ab-ab", "repetitive"),
        ("!!!!!!!!!!!!!!!!", "repetitive"),
        ("passwordpassword!", "repetitive"),  # kerangka huruf-angkanya berulang
        ("!@#$%^&*()_+!@#$", "sequential"),  # baris angka papan ketik dengan Shift
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
    [
        pytest.param("kuda-baterai-staples-benar", id="kata"),
        pytest.param("sandi-panjang-uji-2026", id="kata-angka"),
        pytest.param("蜡烛 在 窗边 慢慢 燃烧 着", id="aksara-lain"),
        # 🔴 Tinjauan Sprint 1: pengulangan dinilai dari kerangka huruf-angka saja,
        # jadi sandi tanpa huruf/angka selalu "repetitive" — aturan komposisi
        # terselubung, yang dilarang NIST SP 800-63B-4 dan K-22.
        pytest.param("!@#$%^&*()_+{}|:<>?", id="simbol"),
        pytest.param("🌧🌧☕📚🎧🌙🔥🌊🍀🌻🐢🎲🧩🪁🛶", id="emoji"),
    ],
)
def test_sandi_yang_wajar_lolos_daftar_tolak(kata_sandi: str) -> None:
    alasan = sandi.alasan_ditolak(kata_sandi, email="nadia.putri@contoh.id", nama="Nadia Putri")

    assert alasan is None, f"sandi yang wajar ditolak sebagai {alasan!r} — aturan komposisi"
