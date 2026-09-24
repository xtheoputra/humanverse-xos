"""spec/07 2.3 — `habit_completions` + idempotensi tanggal.

Selesai bila: kirim ulang `for_date` sama → 200, bukan baris kedua. BARIS
dihitung di basis data (sebagai pemilik skema, di luar RLS), bukan hanya kode
status yang dibaca — jawaban 200 yang diam-diam menulis baris kedua tetap merah.
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Any
from uuid import UUID

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import TIGA_TIER, buat_habit

pytestmark = pytest.mark.integration


def _baris(api: ApiUji, habit_id: str) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT for_date, status FROM habit_completions WHERE habit_id = %s ORDER BY for_date",
            (habit_id,),
        ).fetchall()


def _hari_ini_di(api: ApiUji, zona: str) -> date:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute("SELECT (now() AT TIME ZONE %s)::date", (zona,)).fetchone()
    assert baris is not None
    hasil: date = baris[0]
    return hasil


async def _catat(api: ApiUji, token: str, habit_id: str, **isi: Any) -> Any:
    isi.setdefault("status", "done")
    return await api.klien.post(f"/v1/habits/{habit_id}/completions", json=isi, headers=auth(token))


async def test_kirim_ulang_tanggal_sama_200_bukan_baris_kedua(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)

    pertama = await _catat(api_bersama, token, h["id"], for_date="2026-09-01")
    kedua = await _catat(api_bersama, token, h["id"], for_date="2026-09-01")

    assert pertama.status_code == 201, pertama.text
    assert kedua.status_code == 200, "kirim ulang for_date yang sama bukan 200: " + kedua.text
    assert kedua.json() == pertama.json()
    assert _baris(api_bersama, h["id"]) == [(date(2026, 9, 1), "done")], (
        "kirim ulang menulis baris kedua"
    )


async def test_kirim_ulang_mengembalikan_baris_lama_apa_adanya(api_bersama: ApiUji) -> None:
    """Ulangan dari perangkat luring tidak menimpa — untuk mengganti: hapus, lalu catat."""
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)

    await _catat(api_bersama, token, h["id"], for_date="2026-09-02", status="done")
    ulang = await _catat(api_bersama, token, h["id"], for_date="2026-09-02", status="skipped")

    assert ulang.status_code == 200
    assert ulang.json()["status"] == "done"


async def test_catatan_serentak_tanggal_sama_satu_baris_tanpa_galat(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)

    hasil = await asyncio.gather(
        *(_catat(api_bersama, token, h["id"], for_date="2026-09-03") for _ in range(6))
    )

    kode = sorted(r.status_code for r in hasil)
    assert kode == [200, 200, 200, 200, 200, 201], f"catatan serentak tanggal sama: {kode}"
    assert len({r.json()["id"] for r in hasil}) == 1
    assert len(_baris(api_bersama, h["id"])) == 1


async def test_hapus_lalu_catat_lagi_membuat_baris_baru(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)
    k = api_bersama.klien

    lama = await _catat(api_bersama, token, h["id"], for_date="2026-09-04", status="done")
    hapus = await k.delete(f"/v1/habits/{h['id']}/completions/2026-09-04", headers=auth(token))
    hapus_lagi = await k.delete(f"/v1/habits/{h['id']}/completions/2026-09-04", headers=auth(token))
    baru = await _catat(api_bersama, token, h["id"], for_date="2026-09-04", status="skipped")

    assert (hapus.status_code, hapus_lagi.status_code) == (204, 204)
    assert baru.status_code == 201
    assert baru.json()["id"] != lama.json()["id"]
    assert _baris(api_bersama, h["id"]) == [(date(2026, 9, 4), "skipped")]


async def test_tier_di_luar_adaptive_tiers_ditolak_422(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    bertier = await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    tanpa_tier = await buat_habit(api_bersama, token, title="Tanpa tier")

    sah = await _catat(api_bersama, token, bertier["id"], for_date="2026-09-05", tier_used=2)
    lewat = await _catat(api_bersama, token, bertier["id"], for_date="2026-09-06", tier_used=3)
    tanpa = await _catat(api_bersama, token, tanpa_tier["id"], for_date="2026-09-06", tier_used=0)

    assert sah.status_code == 201, sah.text
    assert sah.json()["tier_used"] == 2
    assert lewat.status_code == 422, "tier di luar adaptive_tiers tersimpan: " + lewat.text
    assert lewat.json()["error"]["code"] == "invalid_tier"
    assert tanpa.status_code == 422, tanpa.text


@pytest.mark.parametrize(
    "isi",
    [
        {"for_date": "2026-09-07", "status": "skipped", "tier_used": 0},
        {"for_date": "2026-09-07", "status": "selesai"},
        {"for_date": "07-09-2026", "status": "done"},
        {"status": "done"},
        {"for_date": "2026-09-07", "status": "done", "note": "a\u0000b"},
        {"for_date": "2026-09-07", "status": "done", "source": "import"},
    ],
)
async def test_penyelesaian_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)

    r = await api_bersama.klien.post(
        f"/v1/habits/{h['id']}/completions", json=isi, headers=auth(token)
    )

    assert r.status_code == 400, r.text
    assert _baris(api_bersama, h["id"]) == []


async def test_tanggal_yang_belum_terjadi_di_mana_pun_ditolak(api_bersama: ApiUji) -> None:
    """Batasnya tanggal paling maju di Bumi (UTC+14), bukan zona profil pengguna."""
    _uid, token = await api_bersama.pengguna_baru(timezone="Pacific/Pago_Pago")
    h = await buat_habit(api_bersama, token)
    paling_maju = _hari_ini_di(api_bersama, "Pacific/Kiritimati")

    di_kiritimati = await _catat(api_bersama, token, h["id"], for_date=paling_maju.isoformat())
    besok = await _catat(
        api_bersama, token, h["id"], for_date=(paling_maju + timedelta(days=1)).isoformat()
    )

    assert di_kiritimati.status_code == 201, (
        "tanggal hari ini di UTC+14 ditolak untuk pengguna UTC−11: " + di_kiritimati.text
    )
    assert besok.status_code == 422, "tanggal masa depan tersimpan: " + besok.text
    assert besok.json()["error"]["code"] == "for_date_in_future"


async def test_habit_pengguna_lain_atau_terhapus_404(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token_a)
    k = api_bersama.klien

    orang_lain = await _catat(api_bersama, token_b, h["id"], for_date="2026-09-08")
    hapus_lain = await k.delete(
        f"/v1/habits/{h['id']}/completions/2026-09-08", headers=auth(token_b)
    )
    await k.delete(f"/v1/habits/{h['id']}", headers=auth(token_a))
    terhapus = await _catat(api_bersama, token_a, h["id"], for_date="2026-09-08")

    assert (orang_lain.status_code, hapus_lain.status_code, terhapus.status_code) == (
        404,
        404,
        404,
    )
    assert _baris(api_bersama, h["id"]) == []


async def test_penyelesaian_milik_pemilik_habit(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token)

    await _catat(api_bersama, token, h["id"], for_date="2026-09-09")

    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        pemilik = k.execute(
            "SELECT user_id, source FROM habit_completions WHERE habit_id = %s", (h["id"],)
        ).fetchone()
    assert pemilik == (UUID(str(uid)), "manual")
