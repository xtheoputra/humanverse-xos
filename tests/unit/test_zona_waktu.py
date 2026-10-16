"""spec/07 1.3 — nama zona waktu IANA dari `tzdata`, peka huruf besar-kecil."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from hvx.modules.platform import ZonaWaktuIANA, zona_waktu_sah

_ZONA = TypeAdapter(ZonaWaktuIANA)


@pytest.mark.parametrize("nama", ["Asia/Jakarta", "Asia/Makassar", "Asia/Jayapura", "UTC"])
def test_nama_iana_diterima(nama: str) -> None:
    assert _ZONA.validate_python(nama) == nama


@pytest.mark.parametrize(
    "nama",
    # `localtime`, `posixrules`, `Factory`: nama berkas di /usr/share/zoneinfo Debian
    # yang `zoneinfo.available_timezones()` ikut terima — bukan zona tempat orang
    # tinggal (tinjauan keamanan Sprint 2).
    [
        "asia/jakarta",
        "WIB",
        "GMT+7",
        "Asia/Jakarta ",
        "",
        "../etc",
        "localtime",
        "posixrules",
        "Factory",
    ],
)
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


def test_daftar_dari_berkas_zones_tzdata_bukan_sistem_operasi() -> None:
    """Satu sumber di semua mesin: daftar `tzdata/zones`, tanpa nama semu."""
    from importlib.resources import files

    from hvx.modules.platform import nama_zona_sah

    tzdata = set(files("tzdata").joinpath("zones").read_text(encoding="utf-8").split())
    assert nama_zona_sah() == tzdata - {"Factory"}
    assert len(nama_zona_sah()) > 500


async def test_tanggal_paling_maju_bertanya_ke_zona_berselisih_terbesar() -> None:
    """Tidak bergantung jam uji dijalankan (tinjauan penegak buta Sprint 2): pukul
    00:00–09:59 UTC, Kiritimati dan UTC bertanggal sama — uji lewat HTTP tidak bisa
    membedakan `ZONA_PALING_MAJU = "UTC"`. Yang diperiksa di sini zona yang DITANYAKAN."""
    from datetime import UTC, date, datetime
    from typing import Any
    from zoneinfo import ZoneInfo

    from hvx.modules.platform import nama_zona_sah, tanggal_paling_maju

    class _Hasil:
        def scalar_one(self) -> date:
            return date(2026, 9, 24)

    class _Koneksi:
        zona: str | None = None

        async def execute(self, _sql: Any, param: dict[str, Any]) -> _Hasil:
            self.zona = param["zona"]
            return _Hasil()

    conn = _Koneksi()
    await tanggal_paling_maju(conn)  # type: ignore[arg-type]
    kini = datetime.now(UTC)
    terbesar = max(ZoneInfo(z).utcoffset(kini) for z in nama_zona_sah())

    assert conn.zona is not None
    assert ZoneInfo(conn.zona).utcoffset(kini) == terbesar, (
        f"tanggal paling maju ditanyakan ke {conn.zona}, bukan zona UTC{terbesar}"
    )
