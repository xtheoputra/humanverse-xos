"""Sumber daya proses yang dipasang lifespan `hvx.main` — dibaca rute lewat `Request`.

Satu tempat, supaya modul tidak menebak nama atribut `app.state` sendiri-sendiri
dan supaya rute yang dipanggil tanpa lifespan gagal dengan pesan yang jelas.
"""

from __future__ import annotations

import hashlib
import hmac

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from .config import Settings


def _ambil(request: Request, nama: str) -> object:
    try:
        return getattr(request.app.state, nama)
    except AttributeError:
        raise RuntimeError(
            f"app.state.{nama} tidak ada — aplikasi dijalankan tanpa lifespan hvx.main?"
        ) from None


def engine_dari(request: Request) -> AsyncEngine:
    engine = _ambil(request, "engine")
    if not isinstance(engine, AsyncEngine):
        raise TypeError(f"app.state.engine: {type(engine).__name__}")
    return engine


def redis_dari(request: Request) -> Redis:
    redis = _ambil(request, "redis")
    if not isinstance(redis, Redis):
        raise TypeError(f"app.state.redis: {type(redis).__name__}")
    return redis


def settings_dari(request: Request) -> Settings:
    settings = _ambil(request, "settings")
    if not isinstance(settings, Settings):
        raise TypeError(f"app.state.settings: {type(settings).__name__}")
    return settings


def sidik_ip(request: Request) -> str | None:
    """HMAC-SHA256 atas IP klien dengan `HVX_IP_HASH_KEY` — untuk audit & batas laju.

    IP mentah tidak pernah disimpan (spec/01 `audit_logs.ip_hash`). IP di balik
    proksi dibaca uvicorn `--proxy-headers` hanya dari proksi tepercaya
    (`FORWARDED_ALLOW_IPS`), bukan dari header yang bisa dikarang klien.
    """
    if request.client is None or not request.client.host:
        return None
    kunci = settings_dari(request).ip_hash_key.get_secret_value().encode()
    return hmac.new(kunci, request.client.host.encode(), hashlib.sha256).hexdigest()
