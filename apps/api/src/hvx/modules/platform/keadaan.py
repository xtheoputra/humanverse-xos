"""Sumber daya proses yang dipasang lifespan `hvx.main` — dibaca rute lewat `Request`.

Satu tempat, supaya modul tidak menebak nama atribut `app.state` sendiri-sendiri
dan supaya rute yang dipanggil tanpa lifespan gagal dengan pesan yang jelas.
"""

from __future__ import annotations

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
