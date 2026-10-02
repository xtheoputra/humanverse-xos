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
from datetime import date
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx import pekerja
from hvx.modules import intelligence
from hvx.modules.platform import Settings

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
