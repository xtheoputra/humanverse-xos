"""Titik rakit `hvx.main` — yang bisa diuji tanpa layanan."""

from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI

from hvx.main import DOKUMENTASI_TERBUKA, create_app
from hvx.modules.platform import Lingkungan, Settings

JALUR_DOKUMENTASI = ("/docs", "/redoc", "/openapi.json")


def _app(env: Lingkungan) -> FastAPI:
    return create_app(Settings(database_url="postgresql://x", redis_url="redis://x", env=env))


async def _status(env: Lingkungan, jalur: str) -> int:
    # Tanpa lifespan: rute dokumentasi tidak menyentuh basis data.
    transport = httpx.ASGITransport(app=_app(env))
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as klien:
        return (await klien.get(jalur)).status_code


@pytest.mark.parametrize("jalur", JALUR_DOKUMENTASI)
async def test_dokumentasi_interaktif_tertutup_di_produksi_lewat_http(jalur: str) -> None:
    assert await _status("production", jalur) == 404


async def test_skema_openapi_terbuka_di_lokal_supaya_uji_di_atas_tidak_lulus_kebetulan() -> None:
    assert await _status("local", "/openapi.json") == 200


def test_dokumentasi_memakai_daftar_izin_bukan_daftar_tolak() -> None:
    """Lingkungan baru yang lupa ditambahkan jatuh ke sisi TERTUTUP."""
    assert "production" not in DOKUMENTASI_TERBUKA
    assert DOKUMENTASI_TERBUKA.issubset({"local", "test", "ci"})


def test_titik_rakit_memasang_pembaca_lintas_modul() -> None:
    """K-23 — `habits` membaca zona waktu profil lewat titik rakit, bukan lewat impor.

    Rute rentetan MENOLAK berjalan tanpa pembaca ini (bukan jatuh ke UTC diam-diam),
    jadi titik rakit yang lupa memasangnya akan terlihat di sini dulu.
    """
    from hvx.modules import checkins, profile

    app = _app("test")
    assert getattr(app.state, "pembaca_zona_waktu", None) is profile.zona_waktu, (
        "hvx.main tidak memasang pembaca_zona_waktu dari profile"
    )
    assert getattr(app.state, "pembaca_energi", None) is checkins.energi_pada, (
        "hvx.main tidak memasang pembaca_energi dari checkins"
    )
