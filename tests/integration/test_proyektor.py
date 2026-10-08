"""spec/07 5.1 — Behavior projector: *“proyeksi bisa dibangun ulang dari nol dan
hasilnya sama”*.

`events` adalah sumber kebenaran (spec/02 aturan D); lajur `activities`
(`source='inferred'`) adalah proyeksinya. Uji ini menuntut tiga hal:

* aliran langsung lewat `hvx.pekerja` memproyeksikan `habit.completed` → satu
  aktivitas `inferred` (konsumen wajib spec/03 terpasang di pekerja);
* membangun ulang DARI NOL (`bangun_ulang_proyeksi`) menghasilkan baris yang
  **identik** — id, kind, occurred_at, payload — dengan aliran langsung;
* penyelesaian yang DICABUT tidak terproyeksi, dan urutan tiba / putar ulang
  tidak pernah menghidupkannya kembali (projector konvergen, bukan sisip/hapus).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, psycopg_dsn

from hvx import pekerja
from hvx.modules import events, intelligence
from hvx.modules.platform import Settings, transaksi_pengguna

pytestmark = pytest.mark.integration

_T0 = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)


async def _terbit_selesai(
    api: ApiUji,
    uid: UUID,
    *,
    completion_id: UUID,
    habit_id: UUID,
    for_date: date,
    status: str = "done",
    tier_used: int | None = None,
    occurred_at: datetime,
) -> None:
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await events.terbitkan(
            conn,
            user_id=uid,
            event_type="habit.completed",
            occurred_at=occurred_at,
            idempotency_key=f"habit-completion:{completion_id}",
            subject_type="habit",
            subject_id=habit_id,
            payload={
                "status": status,
                "tier_used": tier_used,
                "for_date": for_date,
                "completion_id": completion_id,
            },
        )


async def _terbit_dicabut(
    api: ApiUji,
    uid: UUID,
    *,
    completion_id: UUID,
    habit_id: UUID,
    for_date: date,
    occurred_at: datetime,
) -> None:
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await events.terbitkan(
            conn,
            user_id=uid,
            event_type="habit.completion_retracted",
            occurred_at=occurred_at,
            idempotency_key=f"habit-completion:{completion_id}:retracted",
            subject_type="habit",
            subject_id=habit_id,
            payload={"for_date": for_date, "completion_id": completion_id},
        )


def _inferred(api: ApiUji, uid: UUID) -> list[tuple[Any, ...]]:
    """Baris proyeksi HIDUP seorang pengguna — dibaca pemilik tabel (lewat RLS) untuk
    membandingkan dua pembangunan."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT id, kind, occurred_at, payload FROM activities "
            "WHERE user_id = %s AND source = 'inferred' AND deleted_at IS NULL "
            "ORDER BY occurred_at, id",
            (uid,),
        ).fetchall()


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 15) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


async def test_pekerja_memproyeksikan_habit_selesai_menjadi_aktivitas_inferred(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    """Aliran langsung: event di kotak keluar → relay → konsumen `proyektor` → aktivitas."""
    uid, _token = await api_bersama.pengguna_baru()
    cid, hid = uuid4(), uuid4()
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=cid,
        habit_id=hid,
        for_date=date(2026, 9, 1),
        occurred_at=_T0,
    )
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))

    async def terproyeksi() -> bool:
        return len(_inferred(api_bersama, uid)) == 1

    try:
        await _tunggu(terproyeksi, "pekerja tidak memproyeksikan habit.completed jadi aktivitas")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)

    assert tugas.exception() is None
    (baris,) = _inferred(api_bersama, uid)
    _id, kind, _waktu, payload = baris
    assert kind == "habit"
    assert payload == {"completion_id": str(cid), "for_date": "2026-09-01", "status": "done"}


async def test_bangun_ulang_dari_nol_identik_dan_tanpa_duplikat(api_bersama: ApiUji) -> None:
    """*Selesai bila* 5.1: membangun ulang dari `events` memberi baris yang sama,
    dan memutarnya ulang tidak menggandakan apa pun."""
    uid, _token = await api_bersama.pengguna_baru()
    a, b, c = uuid4(), uuid4(), uuid4()
    hid = uuid4()
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=a,
        habit_id=hid,
        for_date=date(2026, 9, 1),
        status="done",
        tier_used=2,
        occurred_at=_T0,
    )
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=b,
        habit_id=hid,
        for_date=date(2026, 9, 2),
        status="partial",
        occurred_at=_T0 + timedelta(days=1),
    )
    # Penyelesaian c dicatat lalu DICABUT — tidak boleh terproyeksi.
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=c,
        habit_id=hid,
        for_date=date(2026, 9, 3),
        occurred_at=_T0 + timedelta(days=2),
    )
    await _terbit_dicabut(
        api_bersama,
        uid,
        completion_id=c,
        habit_id=hid,
        for_date=date(2026, 9, 3),
        occurred_at=_T0 + timedelta(days=2, hours=1),
    )

    diputar = await intelligence.bangun_ulang_proyeksi(api_bersama.app.state.engine, uid)
    assert diputar == 4  # empat event dibaca
    pertama = _inferred(api_bersama, uid)

    # Dua penyelesaian hidup; yang dicabut tidak ada.
    assert len(pertama) == 2
    assert {p[3]["completion_id"] for p in pertama} == {str(a), str(b)}
    assert pertama[1][3] == {"completion_id": str(b), "for_date": "2026-09-02", "status": "partial"}
    assert pertama[0][3]["tier_used"] == 2

    # Bangun ulang LAGI (mengosongkan + memutar ulang) → identik, bukan tergandakan.
    await intelligence.bangun_ulang_proyeksi(api_bersama.app.state.engine, uid)
    kedua = _inferred(api_bersama, uid)
    assert kedua == pertama


async def test_cabut_sesudah_proyeksi_menghapusnya_dan_putar_ulang_tak_menghidupkannya(
    api_bersama: ApiUji,
) -> None:
    """Projector konvergen: sekali dicabut, aktivitasnya hilang — dan memproses ulang
    event `completed` (celah ACK stream) tidak boleh menghidupkannya kembali."""
    uid, _token = await api_bersama.pengguna_baru()
    cid, hid = uuid4(), uuid4()
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=cid,
        habit_id=hid,
        for_date=date(2026, 9, 1),
        occurred_at=_T0,
    )
    await intelligence.bangun_ulang_proyeksi(api_bersama.app.state.engine, uid)
    assert len(_inferred(api_bersama, uid)) == 1

    await _terbit_dicabut(
        api_bersama,
        uid,
        completion_id=cid,
        habit_id=hid,
        for_date=date(2026, 9, 1),
        occurred_at=_T0 + timedelta(hours=1),
    )

    # Simulasikan penyaluran ulang event `completed` SENDIRI sesudah pencabutan —
    # yang pada projector sisip/hapus naif akan menghidupkan kembali barisnya.
    async with transaksi_pengguna(api_bersama.app.state.engine, uid) as conn:
        completed = await events.cari_penyelesaian(
            conn, uid, event_type="habit.completed", completion_id=cid
        )
        assert completed is not None
        await intelligence.proyeksikan_perilaku(conn, completed)
    assert _inferred(api_bersama, uid) == [], (
        "event completed yang disalurkan ulang menghidupkan baris dicabut"
    )


# ── Tinjauan kontrak Sprint 5–6 (8 Okt 2026) ─────────────────────────────────


async def test_konsumen_wajib_menahan_event_bukan_membuangnya_ke_stream_mati(
    api_bersama: ApiUji,
) -> None:
    """spec/03 *Consumer V0*: Behavior projector *“✅ wajib — kegagalannya menahan event”*,
    Habit streak *“✅ wajib”*. Konsumen yang *boleh gagal* memindahkan pesan ke stream mati
    sesudah 5 kali diserahkan (K-25 (3)); konsumen WAJIB tidak boleh — event yang terbuang
    di sana tidak pernah diproyeksikan, dan proyeksinya tidak lagi sama dengan yang dibangun
    ulang dari `events` (5.1). Pesan yang sudah berkali-kali gagal (mis. basis data mati
    beberapa menit) tetap diproses begitu penangannya bisa. Konsumennya diambil dari
    perkabelan pekerja yang sungguh dipakai (`pekerja.rakit_konsumen`), dengan bawaannya."""
    uid, _token = await api_bersama.pengguna_baru()
    cid, hid = uuid4(), uuid4()
    await _terbit_selesai(
        api_bersama,
        uid,
        completion_id=cid,
        habit_id=hid,
        for_date=date(2026, 9, 1),
        occurred_at=_T0,
    )
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (eid,) = k.execute(
            "SELECT id FROM events WHERE user_id = %s AND idempotency_key = %s",
            (uid, f"habit-completion:{cid}"),
        ).fetchone()
    awalan = f"uji-wajib-{uuid4().hex[:10]}"
    r = api_bersama.app.state.redis
    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url="redis://tidak-dipakai",
        redis_prefix=awalan,
    )
    konsumen = {k.grup: k for k in pekerja.rakit_konsumen(api_bersama.engine_pekerja, r, settings)}
    await events.Relay(api_bersama.engine_pekerja, r, awalan).putaran()
    stream = events.kunci_stream(awalan)

    for grup in ("proyektor", "pola"):
        k = konsumen[grup]
        await k.siapkan()
        # Grup sudah menyelesaikan semua pesan lain; pesan uji sudah diserahkan 10 kali dan
        # gagal — menganggur sejam di daftar tunggu (PEL).
        sasaran = None
        for _s, pesan in await r.xreadgroup(grup, "gagal", {stream: ">"}, count=1_000_000):
            for id_pesan, isi in pesan:
                if isi.get("id") == str(eid):
                    sasaran = id_pesan
                else:
                    await r.xack(stream, grup, id_pesan)
        assert sasaran is not None, "relay tidak menyalin event uji"
        await r.xclaim(stream, grup, "gagal", 0, [sasaran], idle=3_600_000, retrycount=10)

        await k.putaran()

        mati = [
            isi.get("id")
            for _i, isi in await r.xrange(events.kunci_mati(awalan))
            if isi.get("grup") == grup
        ]
        assert str(eid) not in mati, (
            f"konsumen wajib `{grup}` membuang event ke stream mati (spec/03 Consumer V0)"
        )
        assert int((await r.xpending(stream, grup))["pending"]) == 0, (
            f"konsumen wajib `{grup}` tidak menyelesaikan event yang ditahannya"
        )

    assert len(_inferred(api_bersama, uid)) == 1, "event yang ditahan tidak pernah diproyeksikan"
