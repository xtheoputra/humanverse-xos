"""spec/07 2.4 — rentetan benar melintasi zona waktu; pengguna yang pindah negara.

"Hari ini" diambil dari jam BASIS DATA di zona yang diuji — bukan dari jam uji
ini: jam VM Docker bisa tertinggal dari jam hos, dan uji yang menebak tanggal
dengan jam sendiri berkedip di sekitar tengah malam.

🔑 Dua pengguna di dua ujung zona waktu Bumi — Pacific/Kiritimati (UTC+14) dan
Pacific/Pago_Pago (UTC−11), terpaut 25 jam — membuat uji "hari ini menurut
zona profil" TIDAK bergantung jam berapa ia dijalankan: pada jam UTC berapa pun,
setidaknya satu dari keduanya menjawab lain kalau "hari ini" dihitung di UTC.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import buat_habit

pytestmark = pytest.mark.integration

KIRITIMATI = "Pacific/Kiritimati"  # UTC+14
PAGO_PAGO = "Pacific/Pago_Pago"  # UTC−11


def _hari_ini_di(api: ApiUji, zona: str) -> date:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute("SELECT (now() AT TIME ZONE %s)::date", (zona,)).fetchone()
    assert baris is not None
    hasil: date = baris[0]
    return hasil


async def _catat(
    api: ApiUji, token: str, habit_id: str, tanggal: date, status: str = "done"
) -> None:
    r = await api.klien.post(
        f"/v1/habits/{habit_id}/completions",
        json={"for_date": tanggal.isoformat(), "status": status},
        headers=auth(token),
    )
    assert r.status_code in (200, 201), r.text


async def _rentetan(api: ApiUji, token: str, habit_id: str) -> dict[str, Any]:
    r = await api.klien.get(f"/v1/habits/{habit_id}/streak", headers=auth(token))
    assert r.status_code == 200, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def test_rentetan_dari_for_date_bukan_dari_waktu_dicatat(api_bersama: ApiUji) -> None:
    """Lima tanggal lokal berturut-turut, dicatat SEKALIGUS sekarang (sinkron luring)."""
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    h = await buat_habit(api_bersama, token)
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")

    for mundur in range(4, -1, -1):
        await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=mundur))

    r = await _rentetan(api_bersama, token, h["id"])
    assert (r["current"], r["longest"]) == (5, 5), f"rentetan dihitung dari waktu catat: {r}"
    assert r["completion_rate_30d"] == 1.0


async def test_hari_ini_menurut_zona_profil_bukan_utc(api_bersama: ApiUji) -> None:
    _k, token_k = await api_bersama.pengguna_baru(timezone=KIRITIMATI)
    _p, token_p = await api_bersama.pengguna_baru(timezone=PAGO_PAGO)
    habit_k = await buat_habit(api_bersama, token_k)
    habit_p = await buat_habit(api_bersama, token_p)
    hari_k = _hari_ini_di(api_bersama, KIRITIMATI)
    hari_p = _hari_ini_di(api_bersama, PAGO_PAGO)

    await _catat(api_bersama, token_k, habit_k["id"], hari_k - timedelta(days=2))  # kemarin kosong
    await _catat(api_bersama, token_p, habit_p["id"], hari_p - timedelta(days=1))  # kemarin ada

    di_kiritimati = await _rentetan(api_bersama, token_k, habit_k["id"])
    di_pago_pago = await _rentetan(api_bersama, token_p, habit_p["id"])
    assert di_kiritimati["current"] == 0, (
        f"hari ini bukan menurut zona profil (UTC+14): {di_kiritimati}"
    )
    assert di_pago_pago["current"] == 1, (
        f"hari ini bukan menurut zona profil (UTC−11): {di_pago_pago}"
    )


async def test_pengguna_pindah_negara_riwayat_utuh_dan_hari_ini_ikut_zona_baru(
    api_bersama: ApiUji,
) -> None:
    """Pago Pago → Kiritimati: 25 jam ke timur — "hari ini" melompat 1 atau 2 tanggal."""
    _uid, token = await api_bersama.pengguna_baru(timezone=PAGO_PAGO)
    h = await buat_habit(api_bersama, token)
    hari_p = _hari_ini_di(api_bersama, PAGO_PAGO)
    await _catat(api_bersama, token, h["id"], hari_p - timedelta(days=1))
    await _catat(api_bersama, token, h["id"], hari_p)
    sebelum = await _rentetan(api_bersama, token, h["id"])

    pindah = await api_bersama.klien.patch(
        "/v1/me/profile", json={"timezone": KIRITIMATI}, headers=auth(token)
    )
    hari_k = _hari_ini_di(api_bersama, KIRITIMATI)
    sesudah_pindah = await _rentetan(api_bersama, token, h["id"])

    assert pindah.status_code == 200, pindah.text
    assert (sebelum["current"], sebelum["longest"]) == (2, 2), sebelum
    lompat = (hari_k - hari_p).days
    assert lompat in (1, 2), lompat
    # Lompat 1: kemarin (menurut zona baru) tercatat — rentetan hidup.
    # Lompat 2: satu tanggal dilompati penerbangan dan belum dicatat — putus.
    assert sesudah_pindah["current"] == (2 if lompat == 1 else 0), (
        f"hari ini tidak mengikuti zona baru sesudah pindah (lompat {lompat}): {sesudah_pindah}"
    )
    assert sesudah_pindah["longest"] == 2, "riwayat bergeser saat zona waktu berganti"

    # Tanggal yang dilompati dicatat mundur dari perangkat, lalu hari ini dijalankan.
    for tanggal in range(1, lompat):
        await _catat(api_bersama, token, h["id"], hari_p + timedelta(days=tanggal))
    await _catat(api_bersama, token, h["id"], hari_k)
    akhir = await _rentetan(api_bersama, token, h["id"])

    panjang = (hari_k - (hari_p - timedelta(days=1))).days + 1
    assert (akhir["current"], akhir["longest"]) == (panjang, panjang), akhir


def _mundurkan_pembuatan(api: ApiUji, habit_id: str, hari: int) -> None:
    """Habit "dibuat" `hari` lalu — API tidak bisa memundurkan `created_at`, pemilik skema bisa."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        k.execute(
            "UPDATE habits SET created_at = created_at - make_interval(days => %s) WHERE id = %s",
            (hari, habit_id),
        )


async def test_tingkat_penyelesaian_mengabaikan_skip_dan_hari_ini(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    h = await buat_habit(api_bersama, token)
    _mundurkan_pembuatan(api_bersama, h["id"], 10)  # hari yang terlewat SESUDAH habit ada
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")

    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=5))
    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=4))
    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=3), "skipped")
    # hari_ini − 2 terlewat
    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=1), "partial")

    r = await _rentetan(api_bersama, token, h["id"])
    assert (r["current"], r["longest"]) == (1, 2), r
    # 3 terpenuhi / 9 jatuh tempo: hari −10…−6 dan −2 terlewat sesudah habit ada;
    # −3 `skipped` dan hari ini tidak masuk penyebut.
    assert r["completion_rate_30d"] == round(3 / 9, 3), r


async def test_tingkat_tidak_menyalahkan_hari_sebelum_habit_dibuat(api_bersama: ApiUji) -> None:
    """Tinjauan kontrak Sprint 2, F8 — habit dibuat hari ini + satu catatan mundur."""
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    h = await buat_habit(api_bersama, token)
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")

    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=10))

    r = await _rentetan(api_bersama, token, h["id"])
    assert r["completion_rate_30d"] == 1.0, r  # dulu 0,1: sembilan hari sebelum habit ada


async def test_rentetan_mingguan_menurut_minggu_iso_zona_profil(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    h = await buat_habit(api_bersama, token, period="week", target_count=2)
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")
    senin_ini = hari_ini - timedelta(days=hari_ini.weekday())

    for minggu in (1, 2):
        senin = senin_ini - timedelta(weeks=minggu)
        await _catat(api_bersama, token, h["id"], senin)
        await _catat(api_bersama, token, h["id"], senin + timedelta(days=6))

    r = await _rentetan(api_bersama, token, h["id"])
    assert (r["current"], r["longest"]) == (2, 2), r


async def test_rentetan_habit_pengguna_lain_404(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token_a)

    r = await api_bersama.klien.get(f"/v1/habits/{h['id']}/streak", headers=auth(token_b))

    assert r.status_code == 404


# ── tinjauan penegak buta Sprint 2: layanan (bukan hanya fungsi murni) ───────


async def test_rentetan_lewat_http_mengikuti_hari_terjadwal(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    hari_ini = _hari_ini_di(api_bersama, "Asia/Jakarta")
    h = await buat_habit(api_bersama, token, schedule={"weekdays": [hari_ini.isoweekday()]})
    await _catat(api_bersama, token, h["id"], hari_ini - timedelta(days=7))
    await _catat(api_bersama, token, h["id"], hari_ini)

    r = await _rentetan(api_bersama, token, h["id"])

    assert (r["current"], r["completion_rate_30d"]) == (2, 1.0), (
        f"layanan tidak meneruskan schedule.weekdays: {r}"
    )


async def test_tingkat_menghitung_hari_sejak_habit_dibuat(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru(timezone="Asia/Jakarta")
    h = await buat_habit(api_bersama, token)
    _mundurkan_pembuatan(api_bersama, h["id"], 5)
    await _catat(api_bersama, token, h["id"], _hari_ini_di(api_bersama, "Asia/Jakarta"))

    r = await _rentetan(api_bersama, token, h["id"])

    assert r["completion_rate_30d"] == round(1 / 6, 3), f"awal habit diabaikan: {r}"


async def test_awal_habit_menurut_zona_profil_bukan_utc(api_bersama: ApiUji) -> None:
    """Dibuat 00:30 waktu Kiritimati = 10:30 UTC sehari sebelumnya."""
    _uid, token = await api_bersama.pengguna_baru(timezone=KIRITIMATI)
    hari_k = _hari_ini_di(api_bersama, KIRITIMATI)
    h = await buat_habit(api_bersama, token)
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        k.execute(
            "UPDATE habits SET created_at = (%s::date + time '00:30') AT TIME ZONE %s "
            "WHERE id = %s",
            (hari_k - timedelta(days=3), KIRITIMATI, h["id"]),
        )
    for mundur in range(3, -1, -1):
        await _catat(api_bersama, token, h["id"], hari_k - timedelta(days=mundur))

    r = await _rentetan(api_bersama, token, h["id"])

    assert (r["current"], r["completion_rate_30d"]) == (4, 1.0), f"awal habit di UTC: {r}"
