"""Perlengkapan uji bersama.

Uji integrasi (`@pytest.mark.integration`) butuh PostgreSQL & Redis sungguhan.
Kalau `HVX_TEST_DATABASE_URL` / `HVX_TEST_REDIS_URL` tidak diisi, uji itu
**GAGAL** — tidak dilewati. Uji yang dilewati diam-diam memulangkan hijau
untuk sesuatu yang tidak pernah diperiksa, dan itu persis kegagalan yang
arch/11 dibangun untuk menutupnya.

Putaran cepat tanpa layanan:  pytest -m "not integration"
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

AKAR = Path(__file__).resolve().parent.parent

# HVX_IP_HASH_KEY wajib bagi Settings (tanpa bawaan, sengaja). Uji yang TIDAK
# sedang menguji kunci itu memakai kunci uji ini; test_config menguji bahwa
# ketiadaannya menggagalkan proses.
os.environ.setdefault("HVX_IP_HASH_KEY", "uji-kunci-hmac-ip-bukan-rahasia-" + "0" * 16)


def _wajib(nama: str) -> str:
    nilai = os.environ.get(nama)
    if not nilai:
        pytest.fail(
            f"{nama} tidak diisi. Uji integrasi butuh layanan nyata:\n"
            "  docker compose up -d --wait postgres redis qdrant\n"
            f"  {nama}=... pytest\n"
            'atau jalankan hanya uji unit: pytest -m "not integration"',
            pytrace=False,
        )
    return nilai


@pytest.fixture(scope="session")
def dsn_admin_uji() -> str:
    """DSN ke server PostgreSQL yang boleh CREATE DATABASE (basis data sekali pakai)."""
    return _wajib("HVX_TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def url_redis_uji() -> str:
    return _wajib("HVX_TEST_REDIS_URL")


@pytest.fixture(scope="session")
def url_qdrant_uji() -> str:
    """Qdrant sungguhan (spec/07 3.5) — `docker compose up -d --wait qdrant`."""
    return _wajib("HVX_TEST_QDRANT_URL")
