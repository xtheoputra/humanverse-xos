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


def _wajib(nama: str) -> str:
    nilai = os.environ.get(nama)
    if not nilai:
        pytest.fail(
            f"{nama} tidak diisi. Uji integrasi butuh layanan nyata:\n"
            "  docker compose up -d --wait postgres redis\n"
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
