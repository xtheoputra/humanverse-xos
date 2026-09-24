"""CORS untuk aplikasi Flutter web (spec/07 2.7) — hanya asal yang DISEBUT yang lolos.

Preflight dijawab `CORSMiddleware` sebelum permintaan menyentuh basis data atau
Redis, jadi uji ini tidak butuh layanan.
"""

from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from hvx.main import create_app
from hvx.modules.platform import Settings

ASAL = "http://localhost:5000"


def _settings(cors: str) -> Settings:
    return Settings(
        database_url="postgresql://x", redis_url="redis://x", env="test", cors_origins=cors
    )


async def _preflight(cors: str, asal: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=create_app(_settings(cors)))
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as klien:
        return await klien.options(
            "/v1/habits",
            headers={
                "Origin": asal,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization, content-type, idempotency-key",
            },
        )


async def test_asal_yang_disebut_lolos_preflight_dengan_header_tulis() -> None:
    r = await _preflight(f"{ASAL}, https://app.contoh.id", ASAL)

    assert r.status_code == 200, r.text
    assert r.headers["access-control-allow-origin"] == ASAL
    izin = r.headers["access-control-allow-headers"].lower()
    assert "idempotency-key" in izin
    assert "authorization" in izin
    assert "access-control-allow-credentials" not in r.headers


async def test_asal_lain_tidak_diloloskan() -> None:
    r = await _preflight(ASAL, "http://jahat.contoh")

    # 400 dari CORSMiddleware sendiri — bukan 500 dari lapisan di dalamnya (tanpa
    # Redis di uji ini). Tinjauan penegak buta Sprint 2: CORS yang dipasang di
    # DALAM batas laju menjawab 500, dan tanpa baris ini uji tetap lulus.
    assert r.status_code == 400, f"preflight asal asing dijawab {r.status_code}, bukan oleh CORS"
    assert r.text == "Disallowed CORS origin"
    assert "access-control-allow-origin" not in r.headers, "asal yang tidak disebut diloloskan"


async def test_tanpa_konfigurasi_tidak_ada_cors_sama_sekali() -> None:
    from fastapi.middleware.cors import CORSMiddleware

    app = create_app(_settings(""))
    r = await _preflight("", ASAL)

    assert all(m.cls is not CORSMiddleware for m in app.user_middleware), "CORS terpasang"
    assert "access-control-allow-origin" not in r.headers


def test_cors_paling_luar_supaya_galat_pun_membawa_header() -> None:
    """429/401 yang dijawab lapisan dalam tetap bisa dibaca aplikasi web."""
    from fastapi.middleware.cors import CORSMiddleware

    app = create_app(_settings(ASAL))

    assert app.user_middleware[0].cls is CORSMiddleware, [
        m.cls.__name__ for m in app.user_middleware
    ]


@pytest.mark.parametrize(
    "nilai",
    ["*", "http://localhost:5000/", "localhost:5000", "http://LOCALHOST:5000", "ftp://x.id"],
)
def test_asal_tidak_persis_ditolak_saat_mulai(nilai: str) -> None:
    with pytest.raises(ValidationError, match="HVX_CORS_ORIGINS"):
        _settings(nilai)
