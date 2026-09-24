"""spec/07 1.3 — nama zona waktu IANA dari `tzdata`, peka huruf besar-kecil."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from hvx.modules.platform import ZonaWaktuIANA, zona_waktu_sah

_ZONA = TypeAdapter(ZonaWaktuIANA)


@pytest.mark.parametrize("nama", ["Asia/Jakarta", "Asia/Makassar", "Asia/Jayapura", "UTC"])
def test_nama_iana_diterima(nama: str) -> None:
    assert _ZONA.validate_python(nama) == nama


@pytest.mark.parametrize("nama", ["asia/jakarta", "WIB", "GMT+7", "Asia/Jakarta ", "", "../etc"])
def test_bukan_nama_iana_ditolak_tanpa_memantulkan_masukan(nama: str) -> None:
    with pytest.raises(ValidationError) as galat:
        _ZONA.validate_python(nama)

    pesan = galat.value.errors()[0]["msg"]
    assert "IANA" in pesan
    if nama.strip():
        assert nama not in pesan


def test_daftar_nama_tidak_kosong() -> None:
    """Pemeriksa yang tidak punya daftar akan menolak SEMUANYA — atau, lebih buruk, tidak ada."""
    assert zona_waktu_sah("Europe/Amsterdam")
    assert not zona_waktu_sah("Europe/Atlantis")
