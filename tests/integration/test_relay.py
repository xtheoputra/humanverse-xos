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
    return events.Relay(api.engine_pekerja, api.app.state.redis, awalan)


def _konsumen(api: ApiUji, awalan: str, **kw: Any) -> events.KonsumenStream:
    kw.setdefault("grup", "uji")
    kw.setdefault("nama", "k1")
    kw.setdefault("jenis", frozenset({"mood.logged"}))
    kw.setdefault("blok_ms", 50)
    kw.setdefault("jumlah", 1000)  # seluruh stream uji dalam satu putaran
    return events.KonsumenStream(
        engine=api.engine_pekerja, redis=api.app.state.redis, awalan=awalan, **kw
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


async def _penanda(redis: Any, awalan: str) -> set[str]:
    """Id event yang ditandai terkirim — apa pun bentuk penyimpanannya di Redis."""
    ada: set[str] = set()
    async for kunci in redis.scan_iter(f"{awalan}:relay:terkirim*"):
        if await redis.type(kunci) == "zset":
            ada |= set(await redis.zrange(kunci, 0, -1))
        else:
            ada.add(str(kunci).rsplit(":", 1)[-1])
    return ada


async def test_penanda_relay_dipangkas_di_luar_jendela_belakang(api_bersama: ApiUji) -> None:
    """Tinjauan keamanan Sprint 3 (S3): satu kunci penanda per event hidup 24 jam, padahal
    jendela belakang yang membacanya 60 dtk — batas laju per pengguna (432 ribu event
    sehari) meninggalkan ±50 MB per akun di Redis `noeviction` yang sama dengan sesi
    (K-24 d menolak persis pola ini). Penanda tidak dibutuhkan lagi begitu kursor
    melewati jendela belakangnya."""
    uid, token = await api_bersama.pengguna_baru()
    lama = [await _mood(api_bersama, token) for _ in range(3)]
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        k.execute(
            "UPDATE events SET recorded_at = now() - interval '10 minutes' WHERE user_id = %s",
            (uid,),
        )
    id_lama = {str(_event_id(api_bersama, uid, f"mood:{m['id']}")) for m in lama}
    awalan = _awalan()
    relay = _relay(api_bersama, awalan)
    await relay.putaran()
    baru = await _mood(api_bersama, token)
    await relay.putaran()
    await relay.putaran()

    penanda = await _penanda(api_bersama.app.state.redis, awalan)
    eid_baru = _event_id(api_bersama, uid, f"mood:{baru['id']}")
    assert not id_lama & penanda, "penanda event di luar jendela belakang tidak dipangkas"
    assert str(eid_baru) in penanda, "event di jendela belakang kehilangan penandanya"
    pesan = await _pesan_untuk(api_bersama.app.state.redis, relay.stream, eid_baru)
    assert len(pesan) == 1, f"event di jendela belakang terkirim {len(pesan)} kali"
    for eid_lama in id_lama:
        # Penandanya sudah dibuang — hanya kursor yang TERSIMPAN yang mencegahnya
        # dikirim ulang (tinjauan penegak buta Sprint 3).
        lama_terkirim = await _pesan_untuk(
            api_bersama.app.state.redis, relay.stream, UUID(eid_lama)
        )
        assert len(lama_terkirim) == 1, f"event lama terkirim {len(lama_terkirim)} kali"


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


async def test_konsumen_dimulai_ulang_grupnya_tidak_dibuat_ulang(api_bersama: ApiUji) -> None:
    """Pekerja yang dimulai ulang memanggil `siapkan()` lagi: grupnya sudah ada
    (BUSYGROUP) — bukan galat, dan posisinya tidak diulang dari awal stream."""
    uid, token = await api_bersama.pengguna_baru()
    await _mood(api_bersama, token)
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    diproses: list[UUID] = []

    async def tangani(_conn: AsyncConnection, ev: events.EventMasuk) -> None:
        if ev.user_id == uid:
            diproses.append(ev.id)

    k = _konsumen(api_bersama, awalan, tangani=tangani)
    await k.siapkan()
    await k.putaran()
    await k.siapkan()  # dimulai ulang
    await k.putaran()

    assert len(diproses) == 1, f"event diproses {len(diproses)} kali"


def _gagal_untuk(eid: UUID) -> tuple[list[int], events.Penangan]:
    percobaan = [0]

    async def tangani(_conn: AsyncConnection, ev: events.EventMasuk) -> None:
        if ev.id == eid:
            percobaan[0] += 1
            raise RuntimeError("penangan uji selalu gagal")

    return percobaan, tangani


async def test_bawaan_konsumen_tidak_mencoba_ulang_sebelum_menganggur_30_dtk(
    api_bersama: ApiUji,
) -> None:
    """spec/03: pesan diklaim ulang sesudah MENGANGGUR 30 dtk — bawaan yang dipakai
    `pekerja.rakit_konsumen`. Tanpanya, pesan yang masih dikerjakan konsumen lain
    direbut, dan yang gagal dicoba ulang seketika."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token)
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    percobaan, tangani = _gagal_untuk(eid)

    k = _konsumen(api_bersama, awalan, tangani=tangani)
    await k.siapkan()
    for _ in range(3):
        await k.putaran()

    assert percobaan == [1], f"dicoba {percobaan[0]} kali tanpa menunggu 30 dtk"


async def test_bawaan_konsumen_stream_mati_sesudah_5_kali(api_bersama: ApiUji) -> None:
    """spec/03: sesudah 5 kali diserahkan → stream mati. Bawaan yang dipakai pekerja."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token)
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    percobaan, tangani = _gagal_untuk(eid)

    k = _konsumen(api_bersama, awalan, tangani=tangani, min_idle_ms=0)
    await k.siapkan()
    for _ in range(8):
        await k.putaran()

    mati = [
        isi["id"] for _i, isi in await api_bersama.app.state.redis.xrange(events.kunci_mati(awalan))
    ]
    assert (percobaan, mati) == ([5], [str(eid)]), f"dicoba {percobaan[0]} kali · mati {mati}"


async def test_event_akun_yang_dihapus_selesai_bukan_ke_stream_mati(api_bersama: ApiUji) -> None:
    """Akun dihapus di antara relay dan konsumen: barisnya hilang (CASCADE). Pesannya
    SELESAI — bukan dicoba ulang sampai stream mati menyimpan rujukan akun yang sudah
    tidak ada (tinjauan penegak buta Sprint 3)."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _mood(api_bersama, token)
    eid = _event_id(api_bersama, uid, f"mood:{mood['id']}")
    awalan = _awalan()
    await _relay(api_bersama, awalan).putaran()
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        k.execute("DELETE FROM users WHERE id = %s", (uid,))
    r = api_bersama.app.state.redis

    async def diam(_conn: AsyncConnection, _ev: events.EventMasuk) -> None:
        return None

    konsumen = _konsumen(api_bersama, awalan, tangani=diam, min_idle_ms=0, maks_kirim=1)
    await konsumen.siapkan()
    for _ in range(3):
        await konsumen.putaran()

    mati = [isi["id"] for _i, isi in await r.xrange(events.kunci_mati(awalan))]
    assert str(eid) not in mati, "rujukan event akun yang dihapus menumpuk di stream mati"
    assert int((await r.xpending(konsumen.stream, "uji"))["pending"]) == 0


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


async def test_stream_mati_dipangkas_menurut_umur(api_bersama: ApiUji) -> None:
    """Tinjauan kontrak Sprint 3: stream mati tidak pernah dipangkas — rujukan
    (pengguna · event) hidup selamanya, juga sesudah akunnya dihapus. Kini hanya
    `events.UMUR_MATI_S` terakhir yang disimpan."""
    r = api_bersama.app.state.redis
    awalan = _awalan()
    detik, mikro = await r.time()
    kini_ms = detik * 1000 + mikro // 1000
    tua = f"{kini_ms - (events.UMUR_MATI_S + 3600) * 1000}-0"
    await r.xadd(events.kunci_mati(awalan), {"pesan": "tua"}, id=tua)
    await r.xadd(events.kunci_mati(awalan), {"pesan": "baru"})

    dibuang = await events.pangkas_mati(r, awalan)

    tersisa = [isi["pesan"] for _i, isi in await r.xrange(events.kunci_mati(awalan))]
    assert tersisa == ["baru"], f"stream mati tidak dipangkas menurut umur: {tersisa}"
    assert dibuang == 1


async def test_pangkas_membandingkan_id_pesan_sebagai_angka(api_bersama: ApiUji) -> None:
    """`5-10` sesudah `5-9` — sebagai teks sebaliknya, dan pangkas membuang pesan yang
    masih ditunggu (tinjauan penegak buta Sprint 3)."""
    relay = _relay(api_bersama, _awalan())
    r, stream = api_bersama.app.state.redis, relay.stream
    for urutan in range(1, 11):
        await r.xadd(stream, {"id": "x"}, id=f"5-{urutan}")
    await r.xgroup_create(stream, "g", id="0")
    await r.xreadgroup("g", "c", {stream: ">"}, count=10)
    for urutan in range(1, 11):
        if urutan != 9:
            await r.xack(stream, "g", f"5-{urutan}")

    await relay.pangkas()

    assert await r.xrange(stream, min="5-9", max="5-9"), "pesan yang belum di-ACK dibuang"


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
