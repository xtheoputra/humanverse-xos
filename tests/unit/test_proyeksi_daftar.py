"""spec/08 7.2 — *“proyeksi baru yang tidak didaftarkan → CI merah”*.

Konsumen dibaca dari perkabelan pekerja yang SUNGGUH dipakai (`rakit_konsumen`), bukan
dari daftar tulisan tangan: konsumen baru yang ditambahkan ke pekerja tanpa diputuskan
proyeksi atau bukan — merah di sini. Yang didaftarkan sebagai proyeksi diuji generik
`tests/integration/test_proyeksi_terdaftar.py`.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

from hvx import pekerja
from hvx.modules import intelligence


def _konsumen() -> dict[str, Any]:
    # `rakit_konsumen` hanya MERAKIT objek — engine & Redis tidak disentuh sebelum `putaran`.
    settings = cast(Any, SimpleNamespace(redis_prefix="uji"))
    return {k.grup: k for k in pekerja.rakit_konsumen(cast(Any, None), cast(Any, None), settings)}


def test_perkabelan_pekerja_terbaca() -> None:
    assert len(_konsumen()) >= 5, "konsumen pekerja tidak terbaca — pemeriksa buta"
    assert intelligence.PROYEKSI, "daftar proyeksi kosong — uji generik tidak menguji apa pun"


def test_tiap_konsumen_diputuskan_proyeksi_atau_bukan() -> None:
    grup = set(_konsumen())
    proyeksi, bukan = set(intelligence.PROYEKSI), set(intelligence.BUKAN_PROYEKSI)
    assert not proyeksi & bukan, f"proyeksi sekaligus bukan: {sorted(proyeksi & bukan)}"
    tanpa = grup - proyeksi - bukan
    assert not tanpa, f"konsumen tanpa keputusan proyeksi/bukan (spec/08 7.2): {sorted(tanpa)}"
    hantu = (proyeksi | bukan) - grup
    assert not hantu, f"terdaftar tetapi tidak dirakit pekerja: {sorted(hantu)}"


def test_bukan_proyeksi_menyebut_alasannya() -> None:
    kosong = [g for g, alasan in intelligence.BUKAN_PROYEKSI.items() if len(alasan) < 40]
    assert not kosong, f"BUKAN_PROYEKSI tanpa alasan yang bisa dibaca: {kosong}"


def test_proyeksi_terdaftar_sama_dengan_konsumennya() -> None:
    """Yang dibangun ulang = yang dialirkan: jenis & penangan dibaca dari konsumen pekerja."""
    konsumen = _konsumen()
    salah = [
        g
        for g, p in intelligence.PROYEKSI.items()
        if konsumen[g].jenis != p.jenis or konsumen[g].tangani is not p.tangani
    ]
    assert not salah, f"proyeksi terdaftar ≠ konsumen di pekerja: {salah}"
