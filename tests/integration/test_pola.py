"""spec/07 5.2 — pola perilaku lewat `hvx.pekerja`: penyelesaian habit → memori
`behavioral`, lalu diluruhkan saat datanya hilang.

Ujung-ke-ujung: habit & penyelesaian dibuat lewat HTTP (event sungguhan), konsumen
`pola` di pekerja menghitung pola, dan hasilnya diperiksa dari sesi lain — bukan
dari keadaan dalam proses.
"""

from __future__ import annotations

import asyncio
from collections import Counter
from collections.abc import Awaitable, Callable
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx import pekerja
from hvx.modules import events, intelligence, memory
from hvx.modules.platform import Settings, transaksi_pengguna

pytestmark = pytest.mark.integration

_HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")
# Tiga tanggal berselang 7 hari (satu hari-dalam-minggu yang sama) + satu berbeda.
_TANGGAL = ["2026-09-11", "2026-09-18", "2026-09-25", "2026-09-23"]


def _behavioral(api: ApiUji, uid: Any) -> list[tuple[Any, ...]]:
    """Memori behavioral AKTIF (berlaku) pengguna — dibaca pemilik tabel."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT content, confidence, evidence_count, scope, model_version "
            "FROM memories WHERE user_id = %s AND kind = 'behavioral' "
            "AND deleted_at IS NULL AND valid_until IS NULL "
            "ORDER BY content",
            (uid,),
        ).fetchall()


async def _tunggu(syarat: Callable[[], Awaitable[bool]], pesan: str, detik: float = 20) -> None:
    for _ in range(int(detik / 0.05)):
        if await syarat():
            return
        await asyncio.sleep(0.05)
    pytest.fail(pesan)


async def test_pekerja_menulis_pola_lalu_meluruhkannya(
    api_bersama: ApiUji, url_redis_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    r = await k.post(
        "/v1/habits",
        json={"title": "Lari pagi", "period": "day", "target_count": 1},
        headers=auth(token),
    )
    assert r.status_code == 201, r.text
    habit_id = r.json()["id"]
    for t in _TANGGAL:
        c = await k.post(
            f"/v1/habits/{habit_id}/completions",
            json={"for_date": t, "status": "done"},
            headers=auth(token),
        )
        assert c.status_code == 201, c.text

    dom = Counter(date.fromisoformat(t).weekday() for t in _TANGGAL).most_common(1)[0][0]

    settings = Settings(
        env="test",
        database_url=api_bersama.db.dsn_pekerja,
        redis_url=url_redis_uji,
        redis_prefix=api_bersama.awalan_redis,
    )
    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja.jalankan(settings, berhenti))

    async def pola_hari_muncul() -> bool:
        return any("hari" in b[0] and b[2] == 4 for b in _behavioral(api_bersama, uid))

    try:
        await _tunggu(pola_hari_muncul, "pekerja tidak menulis pola hari dari penyelesaian habit")
        aktif = _behavioral(api_bersama, uid)
        # Semua memori behavioral asosiatif — tak satu pun mengklaim sebab (naskah 4 §7).
        assert all(intelligence.tanpa_klaim_kausal(b[0]) for b in aktif), aktif
        assert all(b[3] == "habits" and b[4] == "pola-perilaku@v1" for b in aktif)
        (hari,) = [b for b in aktif if "diselesaikan pada hari" in b[0]]
        assert _HARI[dom] in hari[0]
        assert "(3/4)" in hari[0]
        assert float(hari[1]) == 0.75
        assert hari[2] == 4

        # Hapus semua penyelesaian → riwayat kosong → pola diluruhkan (tak lagi aktif).
        for t in _TANGGAL:
            d = await k.delete(f"/v1/habits/{habit_id}/completions/{t}", headers=auth(token))
            assert d.status_code == 204, d.text

        async def pola_luruh() -> bool:
            return _behavioral(api_bersama, uid) == []

        await _tunggu(pola_luruh, "pola tidak diluruhkan setelah penyelesaiannya dihapus")
    finally:
        berhenti.set()
        await asyncio.wait_for(tugas, timeout=15)
    assert tugas.exception() is None


# ── Tinjauan penegak buta S5–6: penangan dipanggil LANGSUNG (tanpa pekerja) ──────────


def _pola(api: ApiUji, uid: Any, jenis: str) -> list[tuple[Any, ...]]:
    """(content, valid_until, evidence_count) memori behavioral satu jenis pola — termasuk
    yang SUDAH luruh. `jenis`: potongan isi yang khas tiap pola."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT content, valid_until, evidence_count FROM memories "
            "WHERE user_id = %s AND kind = 'behavioral' AND deleted_at IS NULL "
            "AND content LIKE %s ORDER BY content",
            (uid, f"%{jenis}%"),
        ).fetchall()


async def _picu(api: ApiUji, uid: UUID, habit_id: str) -> None:
    """Satu event `habit.*` untuk habit itu → penangan pola, di transaksi pemiliknya."""
    sekarang = datetime.now(UTC)
    event = events.EventMasuk(
        id=uuid4(),
        user_id=uid,
        event_type="habit.completed",
        schema_version=1,
        occurred_at=sekarang,
        recorded_at=sekarang,
        source="app",
        subject_type="habit",
        subject_id=UUID(habit_id),
        payload={},
    )
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        await intelligence.deteksi_pola_habit(conn, event)


async def _habit(api: ApiUji, token: str, title: str = "Lari pagi") -> str:
    r = await api.klien.post(
        "/v1/habits",
        json={"title": title, "period": "day", "target_count": 1},
        headers=auth(token),
    )
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


async def _selesai(api: ApiUji, token: str, habit_id: str, for_date: str) -> None:
    c = await api.klien.post(
        f"/v1/habits/{habit_id}/completions",
        json={"for_date": for_date, "status": "done"},
        headers=auth(token),
    )
    assert c.status_code == 201, c.text


async def _cabut(api: ApiUji, token: str, habit_id: str, for_date: str) -> None:
    d = await api.klien.delete(f"/v1/habits/{habit_id}/completions/{for_date}", headers=auth(token))
    assert d.status_code == 204, d.text


async def test_pola_luruh_sekali_lalu_hidup_lagi_saat_dikuatkan(api_bersama: ApiUji) -> None:
    """`valid_until` = KAPAN pola berhenti berlaku: hitung ulang tanpa data baru tidak
    menggesernya (sejarah tetap), dan pola yang didukung data lagi berlaku kembali."""
    uid, token = await api_bersama.pengguna_baru()
    hid = await _habit(api_bersama, token)
    await _selesai(api_bersama, token, hid, "2026-09-11")
    await _picu(api_bersama, uid, hid)
    ((_, berlaku, _),) = _pola(api_bersama, uid, "diselesaikan pada hari")
    assert berlaku is None

    await _cabut(api_bersama, token, hid, "2026-09-11")
    await _picu(api_bersama, uid, hid)
    ((_, luruh_pertama, _),) = _pola(api_bersama, uid, "diselesaikan pada hari")
    assert luruh_pertama is not None, "pola tanpa data tidak diluruhkan"

    await _picu(api_bersama, uid, hid)  # hitung ulang, data tetap kosong
    ((_, luruh_kedua, _),) = _pola(api_bersama, uid, "diselesaikan pada hari")
    assert luruh_kedua == luruh_pertama, "luruh berulang menggeser valid_until (sejarah bergeser)"

    await _selesai(api_bersama, token, hid, "2026-09-18")
    await _picu(api_bersama, uid, hid)
    ((isi, berlaku_lagi, bukti),) = _pola(api_bersama, uid, "diselesaikan pada hari")
    assert berlaku_lagi is None, (
        "pola yang dikuatkan lagi tetap luruh (valid_until tak dikosongkan)"
    )
    assert bukti == 1
    assert "(1/1)" in isi


async def test_pola_waktu_dihitung_di_zona_profil(api_bersama: ApiUji) -> None:
    """Bagian hari dari jam LOKAL profil (Asia/Jakarta, UTC+7): 23:30 UTC = 06:30 pagi."""
    uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    hid = await _habit(api_bersama, token)
    for i in range(3):
        async with transaksi_pengguna(api_bersama.app.state.engine, uid) as conn:
            cid = uuid4()
            await events.terbitkan(
                conn,
                user_id=uid,
                event_type="habit.completed",
                occurred_at=datetime(2026, 9, 1 + i, 23, 30, tzinfo=UTC),
                idempotency_key=f"habit-completion:{cid}",
                subject_type="habit",
                subject_id=UUID(hid),
                payload={"status": "done", "for_date": date(2026, 9, 2 + i), "completion_id": cid},
            )
    await _picu(api_bersama, uid, hid)
    ((isi, _, bukti),) = _pola(api_bersama, uid, "dicatat pada")
    assert bukti == 3
    assert "dicatat pada pagi hari (3/3)" in isi, f"pola waktu tidak memakai zona profil: {isi}"


async def test_habit_dihapus_meluruhkan_semua_polanya(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    hid = await _habit(api_bersama, token)
    await _selesai(api_bersama, token, hid, "2026-09-11")
    await _picu(api_bersama, uid, hid)
    assert _behavioral(api_bersama, uid), "tidak ada pola untuk diluruhkan"

    h = await api_bersama.klien.delete(f"/v1/habits/{hid}", headers=auth(token))
    assert h.status_code == 204, h.text
    await _picu(api_bersama, uid, hid)
    assert _behavioral(api_bersama, uid) == [], "habit dihapus, polanya masih berlaku"


async def test_pola_dua_habit_tidak_saling_menimpa(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    lari = await _habit(api_bersama, token, "Lari pagi")
    baca = await _habit(api_bersama, token, "Baca buku")
    await _selesai(api_bersama, token, lari, "2026-09-11")
    await _selesai(api_bersama, token, baca, "2026-09-12")
    await _picu(api_bersama, uid, lari)
    await _picu(api_bersama, uid, baca)

    hari = [b[0] for b in _pola(api_bersama, uid, "diselesaikan pada hari") if b[1] is None]
    assert len(hari) == 2, f"pola satu habit menimpa pola habit lain: {hari}"
    assert any("Lari pagi" in h for h in hari)
    assert any("Baca buku" in h for h in hari)


async def test_habit_tanpa_penyelesaian_tidak_menyatakan_konsistensi(api_bersama: ApiUji) -> None:
    """Confidence Layer (5.4) di sisi TULIS: tanpa satu pun penyelesaian tidak ada pola
    yang DINYATAKAN — juga konsistensi "0%" dari periode yang jatuh tempo kosong."""
    uid, token = await api_bersama.pengguna_baru()
    hid = await _habit(api_bersama, token)
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        k.execute("UPDATE habits SET created_at = now() - interval '10 days' WHERE id = %s", (hid,))
        k.commit()
    hari_ini = datetime.now(UTC).date().isoformat()
    await _selesai(api_bersama, token, hid, hari_ini)
    await _picu(api_bersama, uid, hid)
    assert _pola(api_bersama, uid, "dipenuhi"), "pola konsistensi tidak ditulis"

    await _cabut(api_bersama, token, hid, hari_ini)
    await _picu(api_bersama, uid, hid)
    aktif = [b for b in _pola(api_bersama, uid, "dipenuhi") if b[1] is None]
    assert aktif == [], f"pola dinyatakan dari nol penyelesaian (evidence_count 0): {aktif}"


async def test_pola_tidak_mengisi_ulang_memori_yang_dilupakan(api_bersama: ApiUji) -> None:
    """Melupakan = isi dikosongkan SEKARANG (Privacy Center, memory/privasi.py); sampai
    penyelaras membuang barisnya, hitung ulang pola tidak boleh menulis isinya kembali."""
    uid, _token = await api_bersama.pengguna_baru()
    mid = uuid4()

    async def catat(isi: str) -> None:
        async with transaksi_pengguna(api_bersama.app.state.engine, uid) as conn:
            await memory.catat_pola(
                conn,
                uid,
                id_=mid,
                scope="habits",
                content=isi,
                confidence=Decimal("0.5"),
                evidence_count=2,
                model_version="pola-perilaku@v1",
            )

    await catat("pola sebelum dilupakan")
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        k.execute(
            "UPDATE memories SET content = '', summary = NULL, deleted_at = now() WHERE id = %s",
            (mid,),
        )
        k.commit()
    await catat("pola sesudah dilupakan")

    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        isi, dihapus = k.execute(
            "SELECT content, deleted_at FROM memories WHERE id = %s", (mid,)
        ).fetchone() or (None, None)
    assert dihapus is not None
    assert isi == "", f"pola mengisi ulang memori yang sudah dilupakan: {isi!r}"
