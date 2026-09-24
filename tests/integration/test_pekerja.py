"""spec/07 3.3 · 3.5 · 3.6 — proses `hvx.pekerja`: relay, konsumen memori, penyelaras
vektor berjalan sendiri, lalu berhenti bersih.

Uji relay, konsumen, dan penyelaras (`test_relay.py`, `test_memori.py`) memanggil
satu putaran; yang ini menjalankan PROSESNYA — titik rakit pekerja yang lupa
menyalakan salah satunya tidak akan terlihat di tempat lain.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx import pekerja
from hvx.modules import events, platform
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 15) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


def _model_memori(api: ApiUji, uid: uuid.UUID) -> list[tuple[str | None]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute("SELECT model_version FROM memories WHERE user_id = %s", (uid,)).fetchall()


async def test_pekerja_menyalurkan_mengekstrak_dan_menyemat_lalu_berhenti_bersih(
    api_bersama: ApiUji, url_redis_uji: str, url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 3}, headers=auth(token))
    assert r.status_code == 201
    koleksi = f"uji-pekerja-{uuid.uuid4().hex[:12]}"
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_aplikasi,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
        qdrant_url=url_qdrant_uji,
        qdrant_koleksi=koleksi,
        sematan_key="s" * 32,  # type: ignore[arg-type]
    )
    model = platform.penyemat_dari(settings).nama
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))
    redis = api_bersama.app.state.redis
    stream = events.kunci_stream(api_bersama.awalan_redis)

    async def tersalur() -> bool:
        return any(p["event_type"] == "mood.logged" for _i, p in await redis.xrange(stream))

    async def terekstrak() -> bool:
        return len(_model_memori(api_bersama, uid)) == 1

    async def tersemat() -> bool:
        return _model_memori(api_bersama, uid) == [(model,)]

    try:
        await _tunggu(tersalur, "pekerja tidak menyalurkan event dalam 15 detik")
        await _tunggu(terekstrak, "pekerja tidak mengekstrak memori dari mood")
        await _tunggu(tersemat, "pekerja tidak menyemat memori ke Qdrant")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{koleksi}")

    assert tugas.exception() is None


async def test_pekerja_tanpa_qdrant_tetap_mengekstrak(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    """Qdrant bukan ketergantungan ekstraksi: tanpa `HVX_QDRANT_URL` memori tetap lahir,
    menunggu disemat (`model_version` NULL) begitu Qdrant diisi."""
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 4}, headers=auth(token))
    assert r.status_code == 201
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_aplikasi,
        redis_url=url_redis_uji,
        redis_prefix=f"uji-{uuid.uuid4().hex[:12]}",
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))

    async def terekstrak() -> bool:
        return _model_memori(api_bersama, uid) == [(None,)]

    try:
        await _tunggu(terekstrak, "tanpa Qdrant, memori tidak diekstrak")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)

    assert tugas.exception() is None
