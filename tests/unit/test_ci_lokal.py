"""`tools/ci_lokal.py --lapor-github` — status `ci-lokal` hanya menempel pada pohon yang diuji.

Pengganti Actions yang gratis (H-26) hanya sama kuatnya dengan kejujuran
statusnya: hijau yang ditempel ke commit yang tidak diuji lebih buruk daripada
tidak ada status sama sekali.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

AKAR = Path(__file__).resolve().parents[2]


def _ci() -> ModuleType:
    nama = "_alat_ci_lokal"
    if nama in sys.modules:
        return sys.modules[nama]
    spec = importlib.util.spec_from_file_location(nama, AKAR / "tools" / "ci_lokal.py")
    assert spec is not None
    assert spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    sys.modules[nama] = modul
    spec.loader.exec_module(modul)
    return modul


SHA = "a" * 40


def test_lapor_diizinkan_untuk_pohon_bersih_yang_sudah_di_remote() -> None:
    assert _ci().alasan_menolak_lapor(SHA, "", SHA, "v0/sprint-0-foundation") is None


def test_lapor_ditolak_untuk_pohon_kerja_kotor() -> None:
    alasan = _ci().alasan_menolak_lapor(SHA, " M tools/ci_lokal.py", SHA, "cabang")

    assert alasan is not None
    assert "kotor" in alasan
    assert "tools/ci_lokal.py" in alasan


@pytest.mark.parametrize("remote", [None, "b" * 40])
def test_lapor_ditolak_untuk_commit_yang_bukan_ujung_remote(remote: str | None) -> None:
    alasan = _ci().alasan_menolak_lapor(SHA, "", remote, "cabang")

    assert alasan is not None
    assert "push dulu" in alasan


@pytest.mark.parametrize("argumen", [["lint"], ["lint", "typecheck", "test"], ["--daftar"]])
def test_lapor_ditolak_untuk_gerbang_sebagian(argumen: list[str]) -> None:
    """Status hijau dari `lint` saja akan terbaca di PR sebagai lulus penuh."""
    with pytest.raises(SystemExit) as keluar:
        _ci().main([*argumen, "--lapor-github"])

    assert keluar.value.code == 2


def test_perintah_status_memakai_api_status_commit_bukan_actions() -> None:
    perintah = _ci().perintah_lapor_status("pemilik/repo", SHA, "success", "x" * 500)

    assert perintah[:5] == ["gh", "api", "--method", "POST", f"repos/pemilik/repo/statuses/{SHA}"]
    assert "context=ci-lokal" in perintah
    uraian = next(p for p in perintah if p.startswith("description="))
    assert len(uraian.removeprefix("description=")) == 140


def test_keadaan_status_di_luar_empat_yang_dikenal_github_ditolak() -> None:
    with pytest.raises(ValueError, match="keadaan"):
        _ci().perintah_lapor_status("pemilik/repo", SHA, "passed", "x")
