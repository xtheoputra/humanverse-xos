"""spec/07 3.3 · 3.5 · 3.6 — proses `hvx.pekerja`: relay, konsumen memori, penyelaras
vektor berjalan sendiri, lalu berhenti bersih.

Uji relay, konsumen, dan penyelaras (`test_relay.py`, `test_memori.py`) memanggil
satu putaran; yang ini menjalankan PROSESNYA — titik rakit pekerja yang lupa
menyalakan salah satunya tidak akan terlihat di tempat lain.
"""

from __future__ import annotations

import asyncio
import os
import sys
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
        return k.execute(
            "SELECT embedding_model FROM memories WHERE user_id = %s", (uid,)
        ).fetchall()


async def test_pekerja_menyalurkan_mengekstrak_dan_menyemat_lalu_berhenti_bersih(
    api_bersama: ApiUji, url_redis_uji: str, url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 3}, headers=auth(token))
    assert r.status_code == 201
    koleksi = f"uji-pekerja-{uuid.uuid4().hex[:12]}"
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
        qdrant_url=url_qdrant_uji,
        qdrant_koleksi=koleksi,
        sematan_key="s" * 32,
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
    menunggu disemat (`embedding_model` NULL) begitu Qdrant diisi."""
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 4}, headers=auth(token))
    assert r.status_code == 201
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
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


async def test_pekerja_memangkas_stream_yang_sudah_selesai(
    api_bersama: ApiUji, url_redis_uji: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tanpa pangkas, stream (dan stream mati) tumbuh selamanya di Redis `noeviction`
    yang sama dengan sesi — tinjauan penegak buta Sprint 3."""
    _uid, token = await api_bersama.pengguna_baru()
    for valensi in (1, 2):
        r = await api_bersama.klien.post(
            "/v1/moods", json={"valence": valensi}, headers=auth(token)
        )
        assert r.status_code == 201
    monkeypatch.setattr(pekerja, "PANGKAS_TIAP", 1)
    awalan = f"uji-pangkas-{uuid.uuid4().hex[:10]}"
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=awalan,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))
    redis = api_bersama.app.state.redis
    stream = events.kunci_stream(awalan)

    async def dipangkas() -> bool:
        if not await redis.exists(stream):
            return False
        info = await redis.xinfo_stream(stream)
        # Lebih sedikit dari yang pernah ditambahkan = ada yang dipangkas.
        return int(info["entries-added"]) >= 2 and int(info["length"]) < int(info["entries-added"])

    try:
        await _tunggu(dipangkas, "pekerja tidak pernah memangkas stream yang sudah selesai", 30)
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)

    assert tugas.exception() is None


async def test_python_m_hvx_pekerja_sebagai_proses_sungguhan(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    """Tinjauan kontrak Sprint 3 (K8): uji di atas memanggil `jalankan()` di proses uji —
    `main()` yang tidak memanggil apa pun lolos seluruh suite. Yang ini menjalankan
    `python -m hvx.pekerja` sebagai proses, dari lingkungan HVX_* seperti wadah compose."""
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post("/v1/moods", json={"valence": 2}, headers=auth(token))
    assert r.status_code == 201
    awalan = f"uji-proses-{uuid.uuid4().hex[:10]}"
    lingkungan = {
        **{k: v for k, v in os.environ.items() if not k.startswith("HVX_")},
        "HVX_ENV": "test",
        "HVX_DATABASE_URL": api_bersama.db.dsn_pekerja,
        "HVX_REDIS_URL": url_redis_uji,
        "HVX_REDIS_PREFIX": awalan,
        "HVX_IP_HASH_KEY": "k" * 32,
        "HVX_LOG_JSON": "true",
    }
    proses = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "hvx.pekerja",
        env=lingkungan,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    redis = api_bersama.app.state.redis
    stream = events.kunci_stream(awalan)

    async def tersalur() -> bool:
        return any(p["event_type"] == "mood.logged" for _i, p in await redis.xrange(stream))

    try:
        await _tunggu(tersalur, "proses `python -m hvx.pekerja` tidak menyalurkan event", 30)
        assert proses.returncode is None, "proses pekerja berhenti sendiri"
    finally:
        proses.terminate()
        _keluar, galat = await asyncio.wait_for(proses.communicate(), timeout=30)
    assert b"Traceback" not in galat, galat.decode(errors="replace")[-2000:]
