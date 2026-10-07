"""spec/07 6.3 notifikasi (*bisa dimatikan per jenis*) dan 6.2 tinjauan mingguan (*menjawab 5
pertanyaan naskah 4 §31*) — lewat HTTP, lawan PostgreSQL sungguhan (K-44 · K-45)."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

pytestmark = pytest.mark.integration

ZONA = ZoneInfo("Asia/Jakarta")  # zona `ApiUji.pengguna_baru`


def _jenis(isi: dict[str, Any]) -> dict[str, bool]:
    return {t["key"]: t["enabled"] for t in isi["types"]}


# ───────────────────────────────────────────────────────────── 6.3 notifikasi ──


async def test_notifikasi_bawaan_dan_jujur_bahwa_v0_tidak_mengirim(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.get("/v1/me/notifications", headers=auth(token))

    assert r.status_code == 200, r.text
    isi = r.json()
    assert _jenis(isi) == {
        "habit_reminder": False,
        "weekly_review": True,
        "recommendation": False,
        "account_security": True,
    }
    assert [t["key"] for t in isi["types"] if t["required"]] == ["account_security"]
    assert isi["quiet_hours"] == {"start": "22:00", "end": "07:00"}
    assert isi["daily_cap"] == 10
    assert isi["delivery"] == "none", "klien dijanjikan notifikasi yang tidak pernah dikirim (A-28)"


async def test_tiap_jenis_dimatikan_sendiri_dan_tersimpan(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    k, h = api_bersama.klien, auth(token)

    r = await k.patch(
        "/v1/me/notifications",
        json={"types": {"habit_reminder": True, "weekly_review": False}},
        headers=h,
    )
    assert r.status_code == 200, r.text
    lagi = (await k.get("/v1/me/notifications", headers=h)).json()
    assert _jenis(lagi) == {
        "habit_reminder": True,
        "weekly_review": False,
        "recommendation": False,
        "account_security": True,
    }, "pilihan per jenis tidak tersimpan atau menyeret jenis lain"
    assert lagi["quiet_hours"] == {"start": "22:00", "end": "07:00"}, "jam tenang ikut berubah"

    r = await k.patch("/v1/me/notifications", json={"quiet_hours": None}, headers=h)
    assert r.json()["quiet_hours"] is None
    assert _jenis(r.json())["habit_reminder"] is True, "mengubah jam tenang menghapus pilihan"


async def test_profil_tidak_menimpa_pilihan_notifikasi(api_bersama: ApiUji) -> None:
    """`PATCH /me/profile` mengganti `preferences` UTUH — tanpa penjaga, preferensi lama yang
    dikirim perangkat lain menghapus pilihan notifikasi yang baru disimpan (K-44)."""
    uid, token = await api_bersama.pengguna_baru()
    k, h = api_bersama.klien, auth(token)
    await k.patch("/v1/me/notifications", json={"types": {"recommendation": True}}, headers=h)

    r = await k.patch("/v1/me/profile", json={"preferences": {"tema": "gelap"}}, headers=h)
    assert r.status_code == 200, r.text
    assert _jenis((await k.get("/v1/me/notifications", headers=h)).json())["recommendation"]
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as p:
        (pref,) = p.execute(
            "SELECT preferences FROM profiles WHERE user_id = %s", (uid,)
        ).fetchone()
    assert pref["tema"] == "gelap"

    lewat_profil = await k.patch(
        "/v1/me/profile",
        json={"preferences": {"notifications": {"types": {"recommendation": False}}}},
        headers=h,
    )
    assert lewat_profil.status_code == 400, "dua penulis untuk satu kunci preferensi"


@pytest.mark.parametrize(
    ("badan", "status", "kode"),
    [
        ({"types": {"account_security": False}}, 422, "notification_required"),
        ({"types": {"promo": True}}, 422, "unknown_notification_type"),
        ({"types": {"weekly_review": "off"}}, 400, None),
        ({"types": {"weekly_review": 0}}, 400, None),
        ({"quiet_hours": {"start": "25:00", "end": "07:00"}}, 400, None),
        ({"quiet_hours": {"start": "22:00", "end": "22:00"}}, 422, "invalid_quiet_hours"),
        ({"quiet_hours": {"start": "22:00"}}, 400, None),
        ({"jenis": {}}, 400, None),
    ],
)
async def test_preferensi_notifikasi_cacat_ditolak(
    api_bersama: ApiUji, badan: dict[str, Any], status: int, kode: str | None
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.patch("/v1/me/notifications", json=badan, headers=auth(token))

    assert r.status_code == status, r.text
    if kode:
        assert r.json()["error"]["code"] == kode
    sesudah = (await api_bersama.klien.get("/v1/me/notifications", headers=auth(token))).json()
    assert _jenis(sesudah)["account_security"] is True


async def test_dua_perubahan_serentak_tidak_saling_menimpa(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    k, h = api_bersama.klien, auth(token)

    await asyncio.gather(
        *(
            k.patch("/v1/me/notifications", json={"types": {jenis: True}}, headers=h)
            for jenis in ("habit_reminder", "recommendation")
        )
    )

    akhir = _jenis((await k.get("/v1/me/notifications", headers=h)).json())
    assert akhir["habit_reminder"], "perubahan serentak hilang (baca-ubah-tulis tanpa kunci)"
    assert akhir["recommendation"], "perubahan serentak hilang (baca-ubah-tulis tanpa kunci)"


# ──────────────────────────────────────────────────────── 6.2 tinjauan mingguan ──


def _hari_ini(api: ApiUji) -> date:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as p:
        (d,) = p.execute("SELECT (now() AT TIME ZONE 'Asia/Jakarta')::date").fetchone()
    assert isinstance(d, date)
    return d


def _minggu(senin: date) -> str:
    tahun, minggu, _ = senin.isocalendar()
    return f"{tahun}-W{minggu:02d}"


async def test_tinjauan_tanpa_data_bertanya_di_kelima_pertanyaan(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.get("/v1/reviews/weekly", headers=auth(token))

    assert r.status_code == 200, r.text
    t = r.json()
    hari_ini = _hari_ini(api_bersama)
    assert t["start"] == (hari_ini - timedelta(days=hari_ini.weekday())).isoformat()
    assert t["timezone"] == "Asia/Jakarta"
    assert [q["key"] for q in t["questions"]] == [
        "went_well",
        "changed",
        "failed",
        "why",
        "change_next_week",
    ]
    assert all(q["stance"] == "ask" for q in t["questions"]), "tanpa data sistem menyatakan"
    assert t["axes"] == []


async def test_tinjauan_minggu_lalu_dari_data_sungguhan(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k, h = api_bersama.klien, auth(token)
    hari_ini = _hari_ini(api_bersama)
    senin = hari_ini - timedelta(days=hari_ini.weekday() + 7)  # minggu lalu — sudah selesai
    habit = (
        await k.post(
            "/v1/habits",
            json={
                "title": "Meditasi",
                "period": "day",
                "target_count": 1,
                "adaptive_tiers": [
                    {"label": "Meditasi 20 menit", "minutes": 20},
                    {"label": "Tarik napas 1 menit", "minutes": 1},
                ],
            },
            headers=h,
        )
    ).json()
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as p:
        p.execute(
            "UPDATE habits SET created_at = now() - interval '40 days' WHERE id = %s",
            (habit["id"],),
        )
    jalur = f"/v1/habits/{habit['id']}/completions"
    for i, status, catatan in ((0, "done", None), (1, "done", None), (2, "skipped", "lembur")):
        isi: dict[str, Any] = {"for_date": (senin + timedelta(days=i)).isoformat()}
        isi |= {"status": status} | ({"note": catatan} if catatan else {})
        r = await k.post(jalur, json=isi, headers=h)
        assert r.status_code == 201, r.text
    for i, energi in ((0, 4), (1, 5), (3, 2), (4, 1), (5, 2)):
        tanggal = (senin + timedelta(days=i)).isoformat()
        r = await k.put(f"/v1/checkins/{tanggal}", json={"energy": energi}, headers=h)
        assert r.status_code == 201, r.text

    r = await k.get(f"/v1/reviews/weekly?week={_minggu(senin)}", headers=h)
    assert r.status_code == 200, r.text
    t = r.json()
    assert t["complete"] is True
    sumbu = {s["key"]: s for s in t["axes"]}
    assert sumbu["habits"]["value"] == pytest.approx(2 / 6, abs=1e-3)
    assert sumbu["energy"]["value"] == 2.8
    q = {x["key"]: x for x in t["questions"]}
    assert [b["text"] for b in q["failed"]["items"]] == [
        "“Meditasi” belum terpenuhi di 4 dari 6 hari."
    ]
    kenapa = " ".join(b["text"] for b in q["why"]["items"])
    assert q["why"]["stance"] == "ask"
    assert "“lembur”" in kenapa, "alasan yang dicatat pengguna tidak disodorkan"
    assert "Tarik napas 1 menit" in " ".join(b["text"] for b in q["change_next_week"]["items"])

    _lain, token_lain = await api_bersama.pengguna_baru()
    lain = await k.get(f"/v1/reviews/weekly?week={_minggu(senin)}", headers=auth(token_lain))
    assert lain.json()["axes"] == [], "tinjauan B memuat data A (H-27)"
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as p:
        (n,) = p.execute("SELECT count(*) FROM audit_logs WHERE user_id = %s", (uid,)).fetchone()
    assert n == 0, "membaca tinjauan menulis sesuatu — tinjauan tidak disimpan (K-45)"


@pytest.mark.parametrize(
    ("minggu", "status", "kode"),
    [
        ("2026-40", 400, None),
        ("2026-W54", 400, None),
        ("2027-W53", 400, "invalid_week"),
        ("2999-W01", 422, "week_in_future"),
    ],
)
async def test_minggu_cacat_atau_belum_dimulai_ditolak(
    api_bersama: ApiUji, minggu: str, status: int, kode: str | None
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    r = await api_bersama.klien.get(f"/v1/reviews/weekly?week={minggu}", headers=auth(token))

    assert r.status_code == status, r.text
    if kode:
        assert r.json()["error"]["code"] == kode
