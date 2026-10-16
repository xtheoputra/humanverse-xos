"""`tools/uji_mutasi_kode.py` — mutasi tidak meninggalkan bytecode basi.

Gerbang penuh Sprint 3: mutasi berukuran SAMA (`ge=1` → `ge=0`) yang dipulihkan di
detik yang sama meninggalkan `.pyc` yang cocok dengan berkas aslinya — Python hanya
memeriksa detik mtime dan ukuran — dan tahap `pytest` sesudahnya menjalankan kode
mutan: `valence 0` lolos uji admisi, padahal sumbernya benar.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from test_jangkar_mutasi import _alat

_DETIK = 1_700_000_000  # mtime yang SAMA untuk mutan dan pemulihannya


def test_mutasi_ukuran_sama_tidak_meninggalkan_bytecode_basi(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Uji ini sendiri bisa berjalan DI DALAM uji mutasi, yang lingkungannya sudah tanpa
    # bytecode — yang diuji hanya yang ditambahkan `lingkungan_mutasi()` sendiri.
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    alat = _alat()
    modul = tmp_path / "modul_basi.py"
    modul.write_bytes(b"NILAI = 0\n")  # mutan — ukurannya sama dengan aslinya
    os.utime(modul, (_DETIK, _DETIK))
    kode, _ = alat.jalankan_terbatas(
        [sys.executable, "-c", "import modul_basi"], tmp_path, alat.lingkungan_mutasi()
    )
    assert kode == 0
    modul.write_bytes(b"NILAI = 1\n")  # dipulihkan, di detik yang sama
    os.utime(modul, (_DETIK, _DETIK))

    kode, keluaran = alat.jalankan_terbatas(
        [sys.executable, "-c", "import modul_basi; print(modul_basi.NILAI)"],
        tmp_path,
        dict(os.environ),
    )

    assert keluaran.strip() == "1", "bytecode mutan dipakai sesudah berkasnya dipulihkan"


def test_pemulihan_membuang_bytecode_berkas_yang_dimutasi(tmp_path: Path) -> None:
    alat = _alat()
    modul = tmp_path / "modul_pulih.py"
    modul.write_bytes(b"NILAI = 0\n")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    basi = cache / "modul_pulih.cpython-312.pyc"
    basi.write_bytes(b"mutan")
    lain = cache / "modul_lain.cpython-312.pyc"
    lain.write_bytes(b"tidak disentuh")

    alat._pulihkan({modul: b"NILAI = 1\n"}, [])

    assert modul.read_bytes() == b"NILAI = 1\n"
    assert not basi.exists(), "bytecode berkas yang dimutasi tertinggal"
    assert lain.exists(), "bytecode berkas lain ikut dibuang"
