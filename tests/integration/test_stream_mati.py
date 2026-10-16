"""spec/08 7.4 — putar ulang stream mati.

*Selesai bila*: event di stream mati diputar ulang per id; memutar ulang dua kali **tidak**
menggandakan efek; event milik akun yang terhapus **tidak** diputar.

Event dibawa ke stream mati dengan cara yang sungguh terjadi (V0 3.3): penangan yang gagal
sampai `maks_kirim`. Lalu penangannya "dibetulkan", dan entrinya diputar ulang.
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

from hvx import stream_mati
from hvx.modules import events
from hvx.modules.platform import Settings

pytestmark = pytest.mark.integration


class _Penangan:
    """Penangan uji: gagal selama `rusak`; mencatat tiap event yang SELESAI ditangani."""

    def __init__(self) -> None:
        self.rusak = True
        self.ditangani: list[UUID] = []

    async def __call__(self, _conn: AsyncConnection, ev: events.EventMasuk) -> None:
        if self.rusak:
            raise RuntimeError("penangan uji rusak")
        self.ditangani.append(ev.id)


def _awalan() -> str:
    return f"uji-mati-{uuid.uuid4().hex[:10]}"


async def _ke_stream_mati(api: ApiUji, awalan: str, penangan: _Penangan) -> tuple[UUID, UUID, str]:
    """Satu mood → relay → konsumen yang gagal sampai event pindah ke stream mati.
    → (user_id, event_id, id entri stream mati)."""
    uid, token = await api.pengguna_baru()
    r = await api.klien.post("/v1/moods", json={"valence": 2}, headers=auth(token))
    assert r.status_code == 201, r.text
    await events.Relay(api.engine_pekerja, api.app.state.redis, awalan).putaran()
    k = _konsumen(api, awalan, penangan)
    await k.siapkan()
    for _ in range(4):
        await k.putaran()
    mati = await events.daftar_mati(api.app.state.redis, awalan)
    milik = [(i, isi) for i, isi in mati if isi["user_id"] == str(uid)]
    assert len(milik) == 1, f"event tidak sampai ke stream mati: {mati}"
    id_mati, isi = milik[0]
    return uid, UUID(isi["id"]), id_mati


async def _milik(api: ApiUji, awalan: str, uid: UUID) -> list[tuple[str, dict[str, Any]]]:
    """Entri stream mati milik `uid` — relay ber-awalan baru menyalurkan event SEMUA pengguna
    basis data berkas ini, jadi stream matinya memuat event uji lain juga."""
    return [
        (i, isi)
        for i, isi in await events.daftar_mati(api.app.state.redis, awalan)
        if isi["user_id"] == str(uid)
    ]


def _konsumen(api: ApiUji, awalan: str, penangan: _Penangan) -> events.KonsumenStream:
    return events.KonsumenStream(
        engine=api.engine_pekerja,
        redis=api.app.state.redis,
        awalan=awalan,
        grup="uji",
        nama="k1",
        jenis=frozenset({"mood.logged"}),
        tangani=penangan,
        min_idle_ms=0,
        maks_kirim=1,
        blok_ms=50,
    )


async def _putar(
    api: ApiUji, awalan: str, id_mati: str, penangan: _Penangan, *, redis: Any = None
) -> str:
    return await events.putar_ulang_mati(
        api.engine_pekerja,
        redis if redis is not None else api.app.state.redis,
        awalan,
        id_mati,
        {"uji": _konsumen(api, awalan, penangan)},
    )


class _HapusTertunda:
    """Redis yang menunda `XDEL` — semua pemutar serentak membaca entri SEBELUM satu pun
    menghapusnya. Tanpa ini balapannya tidak pernah terjadi di uji: pemutar kedua menunggu
    koneksi baru, dan yang pertama sudah selesai."""

    def __init__(self, redis: Any) -> None:
        self._r = redis

    def __getattr__(self, nama: str) -> Any:
        return getattr(self._r, nama)

    async def xdel(self, *argumen: Any) -> Any:
        await asyncio.sleep(0.2)
        return await self._r.xdel(*argumen)


async def test_entri_stream_mati_diputar_ulang_per_id(api_bersama: ApiUji) -> None:
    awalan, penangan = _awalan(), _Penangan()
    uid, eid, id_mati = await _ke_stream_mati(api_bersama, awalan, penangan)

    penangan.rusak = False  # penangannya dibetulkan
    assert await _putar(api_bersama, awalan, id_mati, penangan) == "diputar"

    assert penangan.ditangani == [eid]
    assert await _milik(api_bersama, awalan, uid) == [], (
        "entri yang sudah diputar tertinggal di stream mati"
    )


async def test_memutar_ulang_dua_kali_tidak_menggandakan_efek(api_bersama: ApiUji) -> None:
    awalan, penangan = _awalan(), _Penangan()
    _uid, eid, id_mati = await _ke_stream_mati(api_bersama, awalan, penangan)
    penangan.rusak = False

    lambat = _HapusTertunda(api_bersama.app.state.redis)
    serentak = await asyncio.gather(
        *(_putar(api_bersama, awalan, id_mati, penangan, redis=lambat) for _ in range(3))
    )
    lagi = await _putar(api_bersama, awalan, id_mati, penangan)

    assert penangan.ditangani == [eid], f"efek putar ulang tergandakan: {penangan.ditangani}"
    assert sorted(serentak) == ["diputar", "tidak_ada", "tidak_ada"], serentak
    assert lagi == "tidak_ada"


async def test_event_milik_akun_yang_terhapus_tidak_diputar(api_bersama: ApiUji) -> None:
    awalan, penangan = _awalan(), _Penangan()
    uid, _eid, id_mati = await _ke_stream_mati(api_bersama, awalan, penangan)
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        k.execute("DELETE FROM users WHERE id = %s", (uid,))  # tahap 3 hapus akun: cascade
    penangan.rusak = False

    assert await _putar(api_bersama, awalan, id_mati, penangan) == "event_hilang"
    assert penangan.ditangani == [], "event akun yang terhapus diputar ulang"
    assert await _milik(api_bersama, awalan, uid) == []


async def test_penangan_yang_masih_gagal_mengembalikan_entrinya(api_bersama: ApiUji) -> None:
    awalan, penangan = _awalan(), _Penangan()
    uid, eid, id_mati = await _ke_stream_mati(api_bersama, awalan, penangan)

    assert await _putar(api_bersama, awalan, id_mati, penangan) == "gagal"

    sisa = await _milik(api_bersama, awalan, uid)
    assert [isi["id"] for _i, isi in sisa] == [str(eid)], "entri yang gagal diputar HILANG"
    assert sisa[0][1]["grup"] == "uji"


async def test_grup_yang_tidak_dirakit_lagi_dibiarkan(api_bersama: ApiUji) -> None:
    awalan, penangan = _awalan(), _Penangan()
    uid, _eid, id_mati = await _ke_stream_mati(api_bersama, awalan, penangan)

    hasil = await events.putar_ulang_mati(
        api_bersama.engine_pekerja, api_bersama.app.state.redis, awalan, id_mati, {}
    )

    assert hasil == "grup_tak_dikenal"
    assert [i for i, _isi in await _milik(api_bersama, awalan, uid)] == [id_mati]


async def test_alat_operator_memutar_ulang_dengan_konsumen_pekerja(
    api_bersama: ApiUji, url_redis_uji: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """`python -m hvx.stream_mati` merakit konsumen PEKERJA: entri grup `human-state` yang
    diputar ulang menulis `human_states` lewat penangan sungguhan."""
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.put(
        "/v1/checkins/2026-09-10", json={"energy": 4}, headers=auth(token)
    )
    assert r.status_code == 201, r.text
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT id FROM events WHERE user_id = %s AND event_type = 'checkin.logged'", (uid,)
        ).fetchone()
    assert baris is not None
    awalan = _awalan()
    redis: Any = api_bersama.app.state.redis
    id_mati = await redis.xadd(
        events.kunci_mati(awalan),
        {
            "grup": "human-state",
            "pesan": "0-1",
            "id": str(baris[0]),
            "user_id": str(uid),
            "event_type": "checkin.logged",
        },
    )
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=awalan,
    )

    assert await stream_mati.jalankan(settings, "daftar", [], 100) == 0
    assert str(id_mati) in capsys.readouterr().out
    kode = await stream_mati.jalankan(settings, "putar", [str(id_mati)], 100)
    keluar = capsys.readouterr().out
    assert f"{id_mati}\tdiputar" in keluar, f"keluaran alat operator: {keluar!r}"
    assert kode == 0
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        n = k.execute("SELECT count(*) FROM human_states WHERE user_id = %s", (uid,)).fetchone()
    assert n == (1,), "penangan human-state pekerja tidak dijalankan alat operator"
    assert await stream_mati.jalankan(settings, "putar", [str(id_mati)], 100) == 1, (
        "entri yang sudah diputar tidak dilaporkan `tidak_ada`"
    )
