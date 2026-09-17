"""spec/07 0.3 terhadap layanan NYATA — `create_app` + lifespan + /health."""

from __future__ import annotations

import httpx
import pytest
from asgi_lifespan import LifespanManager

from hvx import __version__
from hvx.main import create_app
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration


async def test_health_200_terhadap_postgres_dan_redis_sungguhan(
    dsn_admin_uji: str, url_redis_uji: str
) -> None:
    app = create_app(Settings(database_url=dsn_admin_uji, redis_url=url_redis_uji, env="test"))

    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        r = await klien.get("/health")

    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok", "version": __version__, "db": "ok", "redis": "ok"}
    assert r.headers["x-request-id"]


async def test_health_503_saat_redis_tidak_bisa_dihubungi(dsn_admin_uji: str) -> None:
    app = create_app(
        Settings(
            database_url=dsn_admin_uji,
            # port 1: dijamin tertutup — koneksi ditolak seketika
            redis_url="redis://127.0.0.1:1/0",
            env="test",
            health_timeout_s=0.5,
        )
    )

    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        r = await klien.get("/health")

    assert r.status_code == 503
    assert r.json()["db"] == "ok"
    assert r.json()["redis"] == "down"
