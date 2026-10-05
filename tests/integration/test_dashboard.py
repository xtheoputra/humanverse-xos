"""spec/07 6.1 — Dashboard & daftar rekomendasi (spec/04 *Rekomendasi*).

`GET /dashboard` menyajikan dimensi dari human_state (dihitung pekerja dari check-in),
tiap skor ber-Why. `GET /recommendations` menyaring per status; `POST …/shown`
memindahkan pending → shown.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx import pekerja
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration

_TANGGAL = "2026-09-20"


def _buat_rekomendasi(api: ApiUji, uid: Any, *, status: str, domain: str = "habit") -> str:
    rid = uuid.uuid4()
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        k.execute(
            "INSERT INTO recommendations (id, user_id, domain, title, status, score, rationale) "
            "VALUES (%s, %s, %s, 'Lari pagi', %s, 0.5, '[\"karena\"]'::jsonb)",
            (rid, uid, domain, status),
        )
        k.commit()
    return str(rid)


def _status(api: ApiUji, rid: str) -> str:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        (s,) = k.execute("SELECT status FROM recommendations WHERE id = %s", (rid,)).fetchone()
    return s


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 20) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


async def test_dashboard_kosong_saat_belum_ada_checkin(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.get("/v1/dashboard", headers=auth(token))
    assert r.status_code == 200, r.text
    assert r.json() == {"as_of": None, "dimensions": []}, "cold start bukan dashboard kosong"


async def test_dashboard_menyajikan_dimensi_berwhy_dari_checkin(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.put(
        f"/v1/checkins/{_TANGGAL}", json={"energy": 4, "focus": 2}, headers=auth(token)
    )
    assert r.status_code in (200, 201), r.text

    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))

    async def ada_dimensi() -> bool:
        d = (await api_bersama.klien.get("/v1/dashboard", headers=auth(token))).json()
        return bool(d["dimensions"])

    try:
        await _tunggu(ada_dimensi, "pekerja tidak menghasilkan dimensi dashboard dari check-in")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
    assert tugas.exception() is None

    d = (await api_bersama.klien.get("/v1/dashboard", headers=auth(token))).json()
    assert d["as_of"] == _TANGGAL
    dims = {x["key"]: x for x in d["dimensions"]}
    assert set(dims) == {"energy", "focus"}, "dashboard bukan beberapa dimensi V0"
    assert dims["energy"]["value"] == 0.75
    assert dims["focus"]["value"] == 0.25
    assert all(x["why"].strip() for x in d["dimensions"]), "ada skor tanpa Why (§28)"
    assert _TANGGAL in dims["energy"]["why"]


async def test_daftar_rekomendasi_menyaring_status(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    pend = _buat_rekomendasi(api_bersama, uid, status="pending")
    _buat_rekomendasi(api_bersama, uid, status="accepted")

    semua = (await api_bersama.klien.get("/v1/recommendations", headers=auth(token))).json()
    assert len(semua["items"]) == 2
    assert pend in {r["id"] for r in semua["items"]}

    hanya_pending = (
        await api_bersama.klien.get("/v1/recommendations?status=pending", headers=auth(token))
    ).json()
    assert [r["id"] for r in hanya_pending["items"]] == [pend]
    (satu,) = hanya_pending["items"]
    assert satu["score"] == 0.5
    assert satu["rationale"] == ["karena"]

    r = await api_bersama.klien.get("/v1/recommendations?status=bukan-status", headers=auth(token))
    assert r.status_code == 400, r.text


async def test_tandai_shown_memindahkan_pending_ke_shown(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid, status="pending")

    r = await api_bersama.klien.post(f"/v1/recommendations/{rid}/shown", headers=auth(token))
    assert r.status_code == 204, r.text
    assert _status(api_bersama, rid) == "shown"

    # Idempoten: menandai lagi tetap 204, tetap shown.
    lagi = await api_bersama.klien.post(f"/v1/recommendations/{rid}/shown", headers=auth(token))
    assert lagi.status_code == 204
    assert _status(api_bersama, rid) == "shown"


async def test_tandai_shown_rekomendasi_tak_dikenal_404(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.post(
        f"/v1/recommendations/{uuid.uuid4()}/shown", headers=auth(token)
    )
    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "recommendation_not_found"
