"""spec/07 3.3 — Redis Streams + consumer group + retry.

Selesai bila: *consumer mati → event tidak hilang saat hidup lagi.*

Diuji terhadap PostgreSQL dan Redis sungguhan: event diterbitkan lewat HTTP
(tulisan domain sungguhan, 3.2), relay menyalinnya ke stream, dan konsumen
membaca isinya di bawah RLS pemiliknya. Waktu "menganggur" konsumen diukur
dengan jam REDIS — jam hos dan jam VM Docker bisa berselisih (mesin-lokal).
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any
from uuid import UUID

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import events

pytestmark = pytest.mark.integration


async def _mood(api: ApiUji, token: str, **isi: Any) -> dict[str, Any]:
    isi.setdefault("valence", 3)
    r = await api.klien.post("/v1/moods", json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


def _event_id(api: ApiUji, user_id: UUID, kunci: str) -> UUID:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT id FROM events WHERE user_id = %s AND idempotency_key = %s", (user_id, kunci)
        ).fetchone()
    assert baris is not None, f"event {kunci} tidak diterbitkan"
    hasil: UUID = baris[0]
    return hasil


async def _pesan_untuk(redis: Any, stream: str, event_id: UUID) -> list[dict[str, str]]:
    return [isi for _id, isi in await redis.xrange(stream) if isi.get("id") == str(event_id)]


def _relay(api: ApiUji, awalan: str) -> events.Relay:
    return events.Relay(api.app.state.engine, api.app.state.redis, awalan)


def _konsumen(api: ApiUji, awalan: str, **kw: Any) -> events.KonsumenStream:
    kw.setdefault("grup", "uji")
    kw.setdefault("nama", "k1")
    kw.setdefault("jenis", frozenset({"mood.logged"}))
    kw.setdefault("blok_ms", 50)
    kw.setdefault("jumlah", 1000)  # seluruh stream uji dalam satu putaran
    return events.KonsumenStream(
        engine=api.app.state.engine, redis=api.app.state.redis, awalan=awalan, **kw
    )


async def _tunggu_jam_redis(redis: Any, ms: int) -> None:
    mulai = await redis.time()
    while True:
        kini = await redis.time()
        if (kini[0] - mulai[0]) * 1000 + (kini[1] - mulai[1]) // 1000 >= ms:
            return
        await asyncio.sleep(0.02)


def _awalan() -> str:
    return f"uji-relay-{uuid.uuid4().hex[:10]}"


# ───────────────────────────────────────────────────────────── relay ──


async def test_relay_menyalin_rujukan_sekali_tanpa_payload(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token, note="rahasia-pribadi-xyz")
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    relay = _relay(api_bersama, awalan)
    r = api_bersama.app.state.redis

    await relay.putaran()
    await relay.putaran()  # jendela belakang dipindai ulang — tidak menggandakan

    pesan = await _pesan_untuk(r, relay.stream, eid)
    assert pesan == [{"id": str(eid), "user_id": str(uid), "event_type": "mood.logged"}], (
        f"event terkirim {len(pesan)} kali"
    )
    semua = str(await r.xrange(relay.stream))
    assert "rahasia-pribadi-xyz" not in semua, "isi event sampai ke Redis"


async def test_event_yang_commit_belakangan_tetap_terkirim(api_bersama: ApiUji) -> None:
    """Transaksi yang lebih dulu menyisip bisa lebih akhir commit: `recorded_at`-nya di
    belakang kursor yang sudah lewat. Tanpa jendela belakang, event itu hilang selamanya."""
    uid, token = await api_bersama.pengguna_baru()
    awalan = _awalan()
    relay = _relay(api_bersama, awalan)
    await _mood(api_bersama, token)
    await relay.putaran()  # kursor maju sampai event terakhir

    telat = await _mood(api_bersama, token)
    eid = _event_id(api_bersama, uid, f"mood:{telat['id']}")
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        # "Menyisip" 30 detik lalu, commit sekarang — di belakang kursor.
        k.execute(
            "UPDATE events SET recorded_at = now() - interval '30 seconds' WHERE id = %s",
            (eid,),
        )
    await relay.putaran()

    assert len(await _pesan_untuk(api_bersama.app.state.redis, relay.stream, eid)) == 1, (
        "event yang commit di belakang kursor tidak pernah terkirim"
    )


# ─────────────────────────────────────────────────────────── konsumen ──


async def test_konsumen_mati_event_tidak_hilang_saat_hidup_lagi(api_bersama: ApiUji) -> None:
    """spec/07 3.3 Selesai bila — dibaca konsumen lalu konsumennya mati sebelum ACK."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token, valence=2)
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    r = api_bersama.app.state.redis
    diproses: list[UUID] = []

    async def tangani(_conn: AsyncConnection, ev: events.EventMasuk) -> None:
        diproses.append(ev.id)

    lama = _konsumen(api_bersama, awalan, tangani=tangani, nama="mati", min_idle_ms=200)
    await lama.siapkan()
    # Konsumen "mati": pesan diserahkan kepadanya, lalu prosesnya berhenti tanpa ACK.
    await r.xreadgroup("uji", "mati", {lama.stream: ">"}, count=1000)
    assert diproses == []

    hidup = _konsumen(api_bersama, awalan, tangani=tangani, nama="hidup", min_idle_ms=200)
    await _tunggu_jam_redis(r, 250)
    await hidup.putaran()

    assert eid in diproses, "event milik konsumen yang mati hilang"
    tertunda = await r.xpending(hidup.stream, "uji")
    assert int(tertunda["pending"]) == 0, "event yang sudah diproses masih menggantung"


async def test_penangan_menerima_isi_dari_postgresql_dan_jenis_lain_dilewati(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token, valence=4, label="lega")
    await api_bersama.klien.post("/v1/goals", json={"title": "Bukan mood"}, headers=auth(token))
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    diterima: list[events.EventMasuk] = []

    async def tangani(_conn: AsyncConnection, ev: events.EventMasuk) -> None:
        if ev.user_id == uid:
            diterima.append(ev)

    k = _konsumen(api_bersama, awalan, tangani=tangani)
    await k.siapkan()
    for _ in range(3):
        await k.putaran()

    assert [e.event_type for e in diterima] == ["mood.logged"], "jenis lain sampai ke penangan"
    assert diterima[0].payload["valence"] == 4
    assert diterima[0].subject_id == UUID(mood["id"])
    tertunda = await api_bersama.app.state.redis.xpending(k.stream, "uji")
    assert int(tertunda["pending"]) == 0, "goal.created tidak di-ACK — menggantung selamanya"


async def test_penangan_yang_selalu_gagal_pindah_ke_stream_mati(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token)
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    r = api_bersama.app.state.redis
    percobaan = 0

    async def tangani(_conn: AsyncConnection, ev: events.EventMasuk) -> None:
        nonlocal percobaan
        if ev.id == eid:
            percobaan += 1
            raise RuntimeError("penangan uji selalu gagal")

    k = _konsumen(api_bersama, awalan, tangani=tangani, min_idle_ms=0, maks_kirim=3)
    await k.siapkan()
    for _ in range(6):
        await k.putaran()

    mati = [isi for _i, isi in await r.xrange(events.kunci_mati(awalan))]
    assert [m["id"] for m in mati] == [str(eid)], f"dead letter: {mati}"
    assert percobaan == 3, f"dicoba {percobaan} kali, bukan 3"
    assert int((await r.xpending(k.stream, "uji"))["pending"]) == 0


# ───────────────────────────────────────────────────────────── pangkas ──


async def test_pangkas_tidak_membuang_yang_masih_ditunggu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for v in (1, 2, 3):
        await _mood(api_bersama, token, valence=v)
    awalan = _awalan()
    relay = _relay(api_bersama, awalan)
    await relay.putaran()
    r = api_bersama.app.state.redis

    async def diam(_conn: AsyncConnection, _ev: events.EventMasuk) -> None:
        return None

    k = _konsumen(api_bersama, awalan, tangani=diam)
    await k.siapkan()
    # Dua pesan diserahkan; yang KEDUA selesai, yang pertama masih dikerjakan —
    # `last-delivered-id` grup sudah melewatinya, jadi hanya daftar tunggu yang tahu.
    ((_s, (pertama, kedua)),) = await r.xreadgroup("uji", "lambat", {relay.stream: ">"}, count=2)
    await r.xack(relay.stream, "uji", kedua[0])
    await relay.pangkas()
    assert await r.xrange(relay.stream, min=pertama[0], max=pertama[0]), (
        "pesan yang belum di-ACK dibuang dari stream"
    )

    await r.xack(relay.stream, "uji", pertama[0])
    for _ in range(3):
        await k.putaran()
    dibuang = await relay.pangkas()

    assert dibuang > 0
    assert await r.xlen(relay.stream) <= 1
