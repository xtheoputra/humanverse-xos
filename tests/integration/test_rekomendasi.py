"""spec/07 5.5 — Recommendation engine lewat `hvx.pekerja`: event → `recommendations` berskor.

Ujung-ke-ujung: habit dilewati lewat HTTP (event sungguhan), konsumen `rekomendasi`
di pekerja menyekor dan menulis baris; check-in yang diperbarui menyegarkan skornya.
Baris diperiksa dari sesi lain (pemilik skema), bukan hanya kode status.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg.rows import dict_row
from test_habits import buat_habit
from test_penyelesaian import _catat, _hari_ini_di

from hvx import pekerja
from hvx.modules import events, intelligence
from hvx.modules.platform import Settings, transaksi_pengguna

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


# ── Tinjauan penegak buta S5–6: penangan dipanggil LANGSUNG (tanpa pekerja) ──────────


async def _picu(api: ApiUji, uid: UUID, event_type: str, **isi: Any) -> None:
    """Satu event pemicu (`habit.skipped` / `checkin.logged`) → mesin rekomendasi."""
    sekarang = datetime.now(UTC)
    event = events.EventMasuk(
        id=uuid4(),
        user_id=uid,
        event_type=event_type,
        schema_version=1,
        occurred_at=sekarang,
        recorded_at=sekarang,
        source="app",
        subject_type="habit" if "habit_id" in isi else None,
        subject_id=UUID(isi.pop("habit_id")) if "habit_id" in isi else None,
        payload=isi,
    )
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await intelligence.sarankan(conn, event)


def _baris(api: ApiUji, uid: Any) -> list[dict[str, Any]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT id, status, score, score_breakdown, context_snapshot FROM recommendations "
            "WHERE user_id = %s ORDER BY context_snapshot->>'for_date'",
            (uid,),
        ).fetchall()
    kolom = ("id", "status", "score", "score_breakdown", "context_snapshot")
    return [dict(zip(kolom, b, strict=True)) for b in baris]


async def test_skip_disalurkan_ulang_tidak_menggandakan_dan_tidak_menimpa_status(
    api_bersama: ApiUji,
) -> None:
    """Idempoten per (habit, tanggal): id `uuid5` + `ON CONFLICT DO NOTHING` — event yang
    disalurkan ulang tidak menambah baris, tidak gagal, dan tidak mengembalikan pilihan
    pengguna ke `pending`."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    hari = "2026-09-20"
    r = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 2}, headers=auth(token))
    assert r.status_code in (200, 201), r.text

    await _picu(api_bersama, uid, "habit.skipped", habit_id=habit["id"], for_date=hari)
    await _picu(api_bersama, uid, "habit.skipped", habit_id=habit["id"], for_date=hari)
    assert len(_baris(api_bersama, uid)) == 1, "skip yang disalurkan ulang menggandakan rekomendasi"

    ((rec,),) = [_baris(api_bersama, uid)]
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        k.execute("UPDATE recommendations SET status = 'accepted' WHERE id = %s", (rec["id"],))
        k.commit()
    await _picu(api_bersama, uid, "habit.skipped", habit_id=habit["id"], for_date=hari)
    ((sesudah,),) = [_baris(api_bersama, uid)]
    assert sesudah["status"] == "accepted", "penyaluran ulang menimpa status pilihan pengguna"


async def test_checkin_hanya_menyegarkan_rekomendasi_hari_itu(api_bersama: ApiUji) -> None:
    """Energi baru hari D menyegarkan komponen `context` rekomendasi pending hari D saja —
    skor, `score_breakdown`, dan `context_snapshot`-nya; hari lain tak tersentuh."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    for hari in ("2026-09-20", "2026-09-21"):
        r = await api_bersama.klien.put(
            f"/v1/checkins/{hari}", json={"energy": 2}, headers=auth(token)
        )
        assert r.status_code in (200, 201), r.text
        await _picu(api_bersama, uid, "habit.skipped", habit_id=habit["id"], for_date=hari)

    await _picu(api_bersama, uid, "checkin.logged", for_date="2026-09-20", energy=5)

    d20, d21 = _baris(api_bersama, uid)
    assert float(d20["score"]) == 1.0
    assert d20["score_breakdown"] == {"context": 1.0, "weights": "equal"}
    assert d20["context_snapshot"] == {"for_date": "2026-09-20", "context": 1.0}, (
        "context_snapshot tidak mengikuti energi terbaru"
    )
    assert float(d21["score"]) == 0.25, "check-in satu hari menyegarkan rekomendasi hari lain"
    assert d21["context_snapshot"]["context"] == 0.25


async def test_history_ikut_dan_bertahan_saat_konteks_disegarkan(api_bersama: ApiUji) -> None:
    """Dua komponen V0: `history` (penyelesaian 30 hari) + `context` (energi). Menyegarkan
    `context` dari check-in mempertahankan `history` yang tersimpan."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        k.execute(
            "UPDATE habits SET created_at = now() - interval '10 days' WHERE id = %s",
            (habit["id"],),
        )
        k.commit()
    for mundur in (9, 8, 7, 6, 5):
        c = await _catat(
            api_bersama,
            token,
            habit["id"],
            for_date=(hari_ini - timedelta(days=mundur)).isoformat(),
        )
        assert c.status_code == 201, c.text
    r = await api_bersama.klien.put(
        f"/v1/checkins/{hari_ini.isoformat()}", json={"energy": 2}, headers=auth(token)
    )
    assert r.status_code in (200, 201), r.text

    await _picu(
        api_bersama, uid, "habit.skipped", habit_id=habit["id"], for_date=hari_ini.isoformat()
    )
    ((rec,),) = [_baris(api_bersama, uid)]
    riwayat = rec["score_breakdown"].get("history")
    assert riwayat is not None, f"komponen history tidak ikut dalam skor: {rec['score_breakdown']}"
    assert 0 < riwayat < 1, riwayat

    await _picu(api_bersama, uid, "checkin.logged", for_date=hari_ini.isoformat(), energy=5)
    ((segar,),) = [_baris(api_bersama, uid)]
    assert segar["score_breakdown"] == {"history": riwayat, "context": 1.0, "weights": "equal"}, (
        f"penyegaran check-in membuang komponen history: {segar['score_breakdown']}"
    )
    assert float(segar["score"]) == round((riwayat + 1.0) / 2, 3)


# ── Tinjauan kontrak Sprint 5–6 (8 Okt 2026) ─────────────────────────────────


def _event(api: ApiUji, uid: Any, jenis: str) -> list[events.EventMasuk]:
    """Event satu jenis milik pengguna, urut tiba — dibaca pemilik skema, apa adanya."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        baris = k.execute(
            "SELECT id, user_id, event_type, schema_version, occurred_at, recorded_at, source, "
            "subject_type, subject_id, payload FROM events "
            "WHERE user_id = %s AND event_type = %s ORDER BY recorded_at, id",
            (uid, jenis),
        ).fetchall()
    return [events.EventMasuk(**b) for b in baris]


async def _sarankan(api: ApiUji, uid: Any, ev: events.EventMasuk) -> None:
    """Satu penyerahan konsumen `rekomendasi` — di transaksi pemilik event, seperti pekerja."""
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await intelligence.sarankan(conn, ev)


async def test_penyegaran_konteks_dari_checkin_otoritatif_bukan_urutan_tiba(
    api_bersama: ApiUji,
) -> None:
    """K-36 (5) *“energi terakhir menang”* + spec/03 aturan 2 (*consumer tidak boleh
    mengandalkan urutan datang*): `checkin.logged` yang tiba TERLAMBAT — diklaim ulang
    sesudah 30 dtk menganggur, sesudah yang lebih baru selesai — tidak boleh memutar
    konteks rekomendasi kembali ke energi yang sudah diganti. K-35 (a) menolak payload
    event untuk alasan yang sama: payload bisa basi."""
    uid, token = await api_bersama.pengguna_baru()
    hari = _hari_ini_di(api_bersama, "UTC").isoformat()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    r = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 2}, headers=auth(token))
    assert r.status_code == 201, r.text
    s = await _catat(api_bersama, token, habit["id"], for_date=hari, status="skipped")
    assert s.status_code == 201, s.text
    (dilewati,) = _event(api_bersama, uid, "habit.skipped")
    await _sarankan(api_bersama, uid, dilewati)

    u = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 5}, headers=auth(token))
    assert u.status_code == 200, u.text
    lama, baru = _event(api_bersama, uid, "checkin.logged")
    await _sarankan(api_bersama, uid, baru)
    await _sarankan(api_bersama, uid, lama)  # penyerahan ulang yang terlambat

    (rec,) = _rekomendasi(api_bersama, uid)
    assert rec["score_breakdown"].get("context") == 1.0, (
        "konteks rekomendasi diputar kembali ke energi yang sudah diganti (urutan tiba): "
        f"{rec['score_breakdown']}"
    )


async def test_penyegaran_menulis_ulang_alasan_dan_saran_sesuai_skornya(
    api_bersama: ApiUji,
) -> None:
    """spec/01 §7: `rationale` = Explainable AI (naskah 4 §29), *“bisa ditampilkan apa
    adanya”*. Sesudah `checkin.logged` menyegarkan `context` (K-36 (5)), alasan yang
    tertampil wajib menyebut energi yang SUNGGUH dipakai skornya — bukan energi lama yang
    sudah diganti — dan saran tier-nya mengikuti energi yang sama (K-23)."""
    uid, token = await api_bersama.pengguna_baru()
    hari = _hari_ini_di(api_bersama, "UTC").isoformat()
    habit = await buat_habit(
        api_bersama,
        token,
        title="Lari pagi",
        adaptive_tiers=[{"label": "Lari 5 km"}, {"label": "Jalan 10 menit"}],
    )
    r = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 1}, headers=auth(token))
    assert r.status_code == 201, r.text
    s = await _catat(api_bersama, token, habit["id"], for_date=hari, status="skipped")
    assert s.status_code == 201, s.text
    (dilewati,) = _event(api_bersama, uid, "habit.skipped")
    await _sarankan(api_bersama, uid, dilewati)
    (awal,) = await _daftar(api_bersama, token)

    u = await api_bersama.klien.put(f"/v1/checkins/{hari}", json={"energy": 5}, headers=auth(token))
    assert u.status_code == 200, u.text
    _lama, baru = _event(api_bersama, uid, "checkin.logged")
    await _sarankan(api_bersama, uid, baru)

    (rec,) = await _daftar(api_bersama, token)
    assert rec["score_breakdown"]["context"] == 1.0
    assert f"Energi 5/5 pada {hari}." in rec["rationale"], (
        f"alasan tidak menyebut energi yang dipakai skornya: {rec['rationale']}"
    )
    assert not any("Energi 1/5" in a for a in rec["rationale"]), (
        f"alasan masih menyebut energi yang sudah diganti: {rec['rationale']}"
    )
    assert rec["body"] != awal["body"], (
        f"saran tier tidak mengikuti energi yang dipakai skornya: {rec['body']!r}"
    )


async def _daftar(api: ApiUji, token: str) -> list[dict[str, Any]]:
    r = await api.klien.get("/v1/recommendations", headers=auth(token))
    assert r.status_code == 200, r.text
    items: list[dict[str, Any]] = r.json()["items"]
    return items
