"""spec/07 1.7 — bagian batas laju yang bisa diuji tanpa Redis."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hvx.modules.platform import BatasLaju, HasilLaju, Settings, jaringan_klien, sidik


def _settings(**ubah: str) -> Settings:
    return Settings(env="test", database_url="postgresql://x", redis_url="redis://x", **ubah)  # type: ignore[arg-type]


def test_teks_batas_diurai_jumlah_per_detik() -> None:
    assert BatasLaju.dari_teks("ip", "600/60") == BatasLaju("ip", 600, 60)
    assert BatasLaju("ip", 600, 60).interval_ms == 100


def test_interval_dibulatkan_ke_atas_supaya_tidak_pernah_lebih_longgar() -> None:
    assert BatasLaju("x", 7, 60).interval_ms == 8572  # 8571,43 → 8572


@pytest.mark.parametrize("teks", ["0/60", "60/0", "60", "banyak/60", "1000000/60", " 60/60"])
def test_teks_batas_berbentuk_salah_ditolak(teks: str) -> None:
    with pytest.raises(ValueError, match="jumlah/detik"):
        BatasLaju.dari_teks("ip", teks)


def test_batas_berbentuk_salah_ditolak_saat_proses_mulai() -> None:
    with pytest.raises(ValidationError):
        _settings(rate_limit_ip="banyak")


def test_retry_after_detik_bulat_ke_atas_dan_tidak_pernah_nol() -> None:
    assert HasilLaju(lolos=False, sisa=0, coba_lagi_ms=1).retry_after_s == 1
    assert HasilLaju(lolos=False, sisa=0, coba_lagi_ms=1001).retry_after_s == 2
    assert HasilLaju(lolos=False, sisa=0, coba_lagi_ms=0).retry_after_s == 1


def test_ipv6_dihitung_per_jaringan_64() -> None:
    assert jaringan_klien("2001:db8:1:2::1") == jaringan_klien(
        "2001:db8:1:2:ffff:ffff:ffff:ffff"
    ), "dua alamat dalam satu /64 dihitung terpisah"
    assert jaringan_klien("2001:db8:1:2::1") != jaringan_klien("2001:db8:1:3::1")


def test_ipv4_apa_adanya_dan_yang_dibungkus_ipv6_dibuka() -> None:
    assert jaringan_klien("203.0.113.7") == "203.0.113.7"
    assert jaringan_klien("::ffff:203.0.113.7") == "203.0.113.7"
    assert jaringan_klien("203.0.113.7") != jaringan_klien("203.0.113.8")
    assert jaringan_klien("klien-uji") == "klien-uji"


def test_sidik_berlabel_tidak_sama_antartujuan_dan_tidak_memuat_nilainya() -> None:
    s = _settings()
    ip = sidik(s, "laju-ip", "203.0.113.7")

    assert ip != sidik(s, "akun-masuk", "203.0.113.7")
    assert ip == sidik(s, "laju-ip", "203.0.113.7")
    assert "203.0.113.7" not in ip
