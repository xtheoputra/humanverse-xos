"""spec/07 3.3 — proses `hvx.pekerja`: relay berjalan sendiri, lalu berhenti bersih.

Uji relay dan konsumen (`test_relay.py`) memanggil satu putaran; yang ini
menjalankan PROSESNYA — titik rakit pekerja yang lupa menyalakan relay tidak
akan terlihat di tempat lain.
"""

from __future__ import annotations

import asyncio

import pytest
from _bantuan_db import ApiUji, auth

from hvx import pekerja
from hvx.modules import events
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration


async def test_pekerja_menyalurkan_event_lalu_berhenti_bersih(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 3}, headers=auth(token))
    assert r.status_code == 201
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_aplikasi,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))
    redis = api_bersama.app.state.redis
    stream = events.kunci_stream(api_bersama.awalan_redis)
    try:
        for _ in range(200):
            isi = [p for _i, p in await redis.xrange(stream) if p["event_type"] == "mood.logged"]
            if isi:
                break
            await asyncio.sleep(0.05)
        else:
            pytest.fail("pekerja tidak menyalurkan event dalam 10 detik")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)

    assert tugas.exception() is None
