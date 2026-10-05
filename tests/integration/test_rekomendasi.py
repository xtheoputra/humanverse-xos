"""spec/07 5.5 — Recommendation engine lewat `hvx.pekerja`: event → `recommendations` berskor.

Ujung-ke-ujung: habit dilewati lewat HTTP (event sungguhan), konsumen `rekomendasi`
di pekerja menyekor dan menulis baris; check-in yang diperbarui menyegarkan skornya.
Baris diperiksa dari sesi lain (pemilik skema), bukan hanya kode status.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import buat_habit
from test_penyelesaian import _catat, _hari_ini_di

from hvx import pekerja
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration


def _rekomendasi(api: ApiUji, uid: Any) -> list[dict[str, Any]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT domain, subject_type, subject_id, score, scoring_version, "
            "score_breakdown, rationale, confidence, status "
            "FROM recommendations WHERE user_id = %s ORDER BY created_at",
            (uid,),
        ).fetchall()
    kolom = (
        "domain",
        "subject_type",
        "subject_id",
        "score",
        "scoring_version",
        "score_breakdown",
        "rationale",
        "confidence",
        "status",
    )
    return [dict(zip(kolom, b, strict=True)) for b in baris]


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 20) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


async def test_pekerja_menyekor_rekomendasi_dari_skip_lalu_menyegarkannya_dari_checkin(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    hari = _hari_ini_di(api_bersama, "UTC").isoformat()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")

    # Check-in energi rendah lalu habit dilewati — dua event pemicu mesin.
    r = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 2}, headers=auth(token))
    assert r.status_code in (200, 201), r.text
    s = await _catat(api_bersama, token, habit["id"], for_date=hari, status="skipped")
    assert s.status_code == 201, s.text

    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))

    async def skor_025() -> bool:
        baris = _rekomendasi(api_bersama, uid)
        return bool(baris) and float(baris[0]["score"]) == 0.25

    try:
        await _tunggu(skor_025, "pekerja tidak menyekor rekomendasi dari habit yang dilewati")
        (rec,) = _rekomendasi(api_bersama, uid)
        assert rec["domain"] == "habit"
        assert rec["subject_type"] == "habit"
        assert str(rec["subject_id"]) == habit["id"]
        assert rec["scoring_version"] == "v1"
        assert rec["score_breakdown"] == {"context": 0.25, "weights": "equal"}
        assert rec["rationale"], "rationale rekomendasi kosong (spec/07 5.5)"
        assert rec["confidence"] is None, "skor mesin bukan confidence agent (K-36)"
        assert rec["status"] == "pending"

        # Check-in diperbarui (energi naik) → konteksnya disegarkan, skornya naik.
        u = await api_bersama.klien.put(
            f"/v1/checkins/{hari}", json={"energy": 5}, headers=auth(token)
        )
        assert u.status_code == 200, u.text

        async def skor_10() -> bool:
            baris = _rekomendasi(api_bersama, uid)
            return bool(baris) and float(baris[0]["score"]) == 1.0

        await _tunggu(skor_10, "check-in yang diperbarui tidak menyegarkan skor rekomendasi")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
    assert tugas.exception() is None

    # Tepat satu baris — idempoten (id per habit+tanggal, ON CONFLICT DO NOTHING),
    # dan check-in yang menyegarkan tidak melahirkan baris kedua.
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (n,) = k.execute(
            "SELECT count(*) FROM recommendations WHERE user_id = %s", (uid,)
        ).fetchone()
    assert n == 1
