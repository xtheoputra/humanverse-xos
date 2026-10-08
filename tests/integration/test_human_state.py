"""spec/07 5.3 — Human State lewat `hvx.pekerja`: check-in harian → `human_states`.

Ujung-ke-ujung: check-in dibuat/diubah lewat HTTP (event sungguhan), konsumen
`human-state` di pekerja menghitung metrik, dan baris diperiksa dari sesi lain.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg.rows import dict_row

from hvx import pekerja
from hvx.modules import events, intelligence
from hvx.modules.platform import Settings, transaksi_pengguna

pytestmark = pytest.mark.integration

_TANGGAL = "2026-09-20"


def _human_state(api: ApiUji, uid: Any, for_date: str) -> tuple[Any, ...] | None:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT metrics, model_version FROM human_states WHERE user_id = %s AND for_date = %s",
            (uid, for_date),
        ).fetchone()


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 20) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


async def test_pekerja_menghitung_human_state_dari_checkin_lalu_memperbaruinya(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
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

    async def energi_075() -> bool:
        b = _human_state(api_bersama, uid, _TANGGAL)
        return b is not None and b[0].get("energy", {}).get("value") == 0.75

    try:
        await _tunggu(energi_075, "pekerja tidak menulis human_state dari check-in")
        metrics, model = _human_state(api_bersama, uid, _TANGGAL)
        assert model == "human-state@v1"
        assert metrics["energy"] == {"value": 0.75, "confidence": 1.0, "evidence_count": 1}
        assert metrics["focus"] == {"value": 0.25, "confidence": 1.0, "evidence_count": 1}

        # Ubah check-in → human_state dihitung ulang (upsert, bukan baris kedua).
        u = await api_bersama.klien.put(
            f"/v1/checkins/{_TANGGAL}", json={"energy": 5, "focus": 5}, headers=auth(token)
        )
        assert u.status_code == 200, u.text

        async def energi_1() -> bool:
            b = _human_state(api_bersama, uid, _TANGGAL)
            return b is not None and b[0].get("energy", {}).get("value") == 1.0

        await _tunggu(energi_1, "human_state tidak diperbarui setelah check-in diubah")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
    assert tugas.exception() is None

    # Tepat satu baris untuk (pengguna, tanggal, versi) — upsert, bukan tumpukan.
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (n,) = k.execute(
            "SELECT count(*) FROM human_states WHERE user_id = %s AND for_date = %s",
            (uid, _TANGGAL),
        ).fetchone()
    assert n == 1


# ── Tinjauan penegak buta S5–6: penangan dipanggil LANGSUNG (tanpa pekerja) ──────────


def _computed_at(api: ApiUji, uid: Any, for_date: str) -> Any:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        (nilai,) = k.execute(
            "SELECT computed_at FROM human_states WHERE user_id = %s AND for_date = %s",
            (uid, for_date),
        ).fetchone() or (None,)
    return nilai


async def _checkin(api: ApiUji, token: str, for_date: str, **isi: Any) -> None:
    r = await api.klien.put(f"/v1/checkins/{for_date}", json=isi, headers=auth(token))
    assert r.status_code in (200, 201), r.text


async def _hitung(api: ApiUji, uid: UUID, for_date: str, **payload: Any) -> None:
    """Satu `checkin.logged` → penangan human_state. `payload` = isi event saat DITERBITKAN
    — bisa basi dibanding check-in sekarang (penyaluran ulang sesudah koreksi)."""
    sekarang = datetime.now(UTC)
    event = events.EventMasuk(
        id=uuid4(),
        user_id=uid,
        event_type="checkin.logged",
        schema_version=1,
        occurred_at=sekarang,
        recorded_at=sekarang,
        source="app",
        subject_type=None,
        subject_id=None,
        payload={"for_date": for_date, **payload},
    )
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await intelligence.hitung_human_state(conn, event)


async def test_event_basi_tidak_memundurkan_human_state(api_bersama: ApiUji) -> None:
    """Konvergen: dihitung dari check-in OTORITATIF, bukan payload event. Event lama yang
    disalurkan ulang SESUDAH koreksi tidak mengembalikan nilai lama."""
    uid, token = await api_bersama.pengguna_baru()
    await _checkin(api_bersama, token, _TANGGAL, energy=4)
    await _checkin(api_bersama, token, _TANGGAL, energy=5)
    await _hitung(api_bersama, uid, _TANGGAL, energy=5)
    pertama = _computed_at(api_bersama, uid, _TANGGAL)

    await _hitung(api_bersama, uid, _TANGGAL, energy=4)  # event lama, tiba terlambat
    metrics, _model = _human_state(api_bersama, uid, _TANGGAL) or (None, None)
    assert metrics["energy"]["value"] == 1.0, (
        "human_state dihitung dari payload event basi, bukan check-in otoritatif"
    )
    assert _computed_at(api_bersama, uid, _TANGGAL) > pertama, (
        "hitung ulang human_state tidak memperbarui computed_at"
    )


async def test_checkin_tanpa_energi_dan_fokus_tidak_menyatakan_keadaan(api_bersama: ApiUji) -> None:
    """Check-in yang hanya tidur: tidak ada metrik, jadi tidak ada baris — dan penangannya
    tidak gagal (konsumen yang gagal mengulang event itu tanpa henti)."""
    uid, token = await api_bersama.pengguna_baru()
    await _checkin(api_bersama, token, _TANGGAL, sleep_hours=7.5)
    await _hitung(api_bersama, uid, _TANGGAL, sleep_hours=7.5)
    assert _human_state(api_bersama, uid, _TANGGAL) is None, "human_state ditulis tanpa metrik"


async def test_koreksi_checkin_tanpa_metrik_tidak_meninggalkan_keadaan_basi(
    api_bersama: ApiUji,
) -> None:
    """PUT = ganti (2.5): check-in yang dikoreksi menjadi hanya-tidur tidak lagi punya energi
    atau fokus — human_state hari itu tidak boleh terus menyatakan energi lamanya."""
    uid, token = await api_bersama.pengguna_baru()
    await _checkin(api_bersama, token, _TANGGAL, energy=4, focus=2)
    await _hitung(api_bersama, uid, _TANGGAL, energy=4, focus=2)
    assert _human_state(api_bersama, uid, _TANGGAL) is not None

    await _checkin(api_bersama, token, _TANGGAL, sleep_hours=7.5)
    await _hitung(api_bersama, uid, _TANGGAL, sleep_hours=7.5)
    tersisa = _human_state(api_bersama, uid, _TANGGAL)
    assert tersisa is None, f"human_state basi bertahan sesudah check-in dikoreksi: {tersisa}"


async def test_dashboard_menyajikan_hari_terbaru(api_bersama: ApiUji) -> None:
    """Dua hari check-in → dashboard dari human_state TERBARU (for_date), bukan yang lama."""
    uid, token = await api_bersama.pengguna_baru()
    await _checkin(api_bersama, token, "2026-09-21", energy=5)
    await _hitung(api_bersama, uid, "2026-09-21")
    await _checkin(api_bersama, token, "2026-09-20", energy=1)  # dicatat belakangan
    await _hitung(api_bersama, uid, "2026-09-20")

    d = (await api_bersama.klien.get("/v1/dashboard", headers=auth(token))).json()
    assert d["as_of"] == "2026-09-21", f"dashboard tidak menyajikan hari terbaru: {d['as_of']}"
    assert {x["key"]: x["value"] for x in d["dimensions"]} == {"energy": 1.0}


# ── Tinjauan kontrak Sprint 5–6 (8 Okt 2026) ─────────────────────────────────


def _event_checkin_terakhir(api: ApiUji, uid: Any, for_date: str) -> events.EventMasuk:
    """`checkin.logged` terbaru untuk satu tanggal — dibaca pemilik skema, apa adanya."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        baris = k.execute(
            "SELECT id, user_id, event_type, schema_version, occurred_at, recorded_at, source, "
            "subject_type, subject_id, payload FROM events "
            "WHERE user_id = %s AND event_type = 'checkin.logged' "
            "AND payload ->> 'for_date' = %s ORDER BY recorded_at DESC, id DESC LIMIT 1",
            (uid, for_date),
        ).fetchone()
    assert baris is not None, "check-in tidak menerbitkan checkin.logged"
    return events.EventMasuk(**baris)


async def _proses_keadaan(api: ApiUji, uid: Any, for_date: str) -> None:
    ev = _event_checkin_terakhir(api, uid, for_date)
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await intelligence.hitung_human_state(conn, ev)


async def test_checkin_diganti_tanpa_energi_dan_fokus_tidak_meninggalkan_keadaan_lama(
    api_bersama: ApiUji,
) -> None:
    """K-35 (1)·(5): keadaan hari itu dihitung dari check-in OTORITATIF, dan check-in tanpa
    energi & fokus = tidak ada baris. `PUT /checkins` MENGGANTI (spec/04): sesudah pengguna
    mengganti check-in-nya tanpa energi/fokus, energi lamanya tidak boleh tetap dinyatakan
    — di `human_states` maupun di dashboard (*“yang kamu laporkan sendiri”*, 6.1)."""
    uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.put(
        f"/v1/checkins/{_TANGGAL}", json={"energy": 4, "focus": 2}, headers=auth(token)
    )
    assert r.status_code == 201, r.text
    await _proses_keadaan(api_bersama, uid, _TANGGAL)
    assert _human_state(api_bersama, uid, _TANGGAL) is not None

    u = await api_bersama.klien.put(
        f"/v1/checkins/{_TANGGAL}", json={"sleep_hours": 7.5}, headers=auth(token)
    )
    assert u.status_code == 200, u.text
    await _proses_keadaan(api_bersama, uid, _TANGGAL)

    assert _human_state(api_bersama, uid, _TANGGAL) is None, (
        "human_state menyatakan energi/fokus yang sudah diganti pemiliknya (K-35)"
    )
    d = await api_bersama.klien.get("/v1/dashboard", headers=auth(token))
    assert d.status_code == 200, d.text
    assert d.json() == {"as_of": None, "dimensions": []}, (
        f"dashboard menampilkan laporan yang sudah diganti: {d.json()}"
    )
