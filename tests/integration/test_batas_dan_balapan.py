"""Tinjauan Sprint 2 — balapan hapus/tulis, tautan ke goal terhapus, dan batas per pengguna.

* **F1** — goal anak yang dibuat SERENTAK dengan hapus induknya: tinjauan
  kontrak membuktikan 40 dari 40 menjadi yatim (hidup, induknya terhapus,
  tidak terjangkau dari pohon mana pun). Janji E-168: pohon tidak pernah
  dipotong diam-diam.
* **F2** — habit bisa ditaut ke goal yang sudah dihapus-lunak, dan tautannya
  bertahan sesudah goal dihapus — FK komposit tidak melihat `deleted_at`.
* **F3** — kirim ulang penyelesaian yang sama sesudah tier habit dikurangi
  menjadi 422, bukan 200 (spec/04: kirim ulang selalu aman).
* **F9 · keamanan S2** — `GET /habits` memotong di 500 tanpa tanda; `…/tree`
  dan `GET /goals/{id}` membaca tanpa batas. Batasnya kini SAAT MENULIS (K-24),
  dan diperiksa serial: tulisan serentak tidak bisa bersama melewatinya.
* **F13** — milestone menerima id buatan klien, seperti goal (spec/04).

Balapan diuji lewat `asyncio.gather` di satu event loop: transaksi keduanya
berselang-seling di tiap `await` basis data — cukup untuk mengulang F1 tanpa
kunci (dibuktikan mutasinya di `tools/uji_mutasi_kode.py`).
"""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx.modules import goals

pytestmark = pytest.mark.integration

PERCOBAAN = 15


async def _goal(api: ApiUji, token: str, **isi: Any) -> dict[str, Any]:
    isi.setdefault("title", "Goal uji")
    r = await api.klien.post("/v1/goals", json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


def _satu(api: ApiUji, sql: str, *param: Any) -> Any:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(sql, param).fetchone()  # type: ignore[arg-type]
    assert baris is not None
    return baris[0]


def _pemilik(api: ApiUji, sql: str, *param: Any) -> None:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        k.execute(sql, param)  # type: ignore[arg-type]


# ───────────────────────────────────────────────────────── F1 · F2 balapan ──


async def test_anak_yang_dibuat_serentak_dengan_hapus_induk_tidak_yatim(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    hasil_anak = []

    for _ in range(PERCOBAAN):
        induk = await _goal(api_bersama, token, title="Induk")
        hapus, anak = await asyncio.gather(
            k.delete(f"/v1/goals/{induk['id']}", headers=auth(token)),
            k.post(
                "/v1/goals", json={"title": "Anak", "parent_id": induk["id"]}, headers=auth(token)
            ),
        )
        assert hapus.status_code == 204
        assert anak.status_code in {201, 422}, anak.text
        hasil_anak.append(anak.status_code)

    yatim = _satu(
        api_bersama,
        """SELECT count(*) FROM goals c JOIN goals p ON p.id = c.parent_id
           WHERE c.user_id = %s AND c.deleted_at IS NULL AND p.deleted_at IS NOT NULL""",
        uid,
    )
    assert yatim == 0, f"{yatim} goal hidup berinduk goal terhapus — hasil: {hasil_anak}"


async def test_habit_yang_ditaut_serentak_dengan_hapus_goal_tidak_menaut_goal_terhapus(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien

    for i in range(PERCOBAAN):
        goal = await _goal(api_bersama, token, title=f"Goal {i}")
        hapus, habit = await asyncio.gather(
            k.delete(f"/v1/goals/{goal['id']}", headers=auth(token)),
            k.post(
                "/v1/habits",
                json={"title": "H", "period": "day", "target_count": 1, "goal_id": goal["id"]},
                headers=auth(token),
            ),
        )
        assert hapus.status_code == 204
        assert habit.status_code in {201, 422}, habit.text

    menaut_terhapus = _satu(
        api_bersama,
        """SELECT count(*) FROM habits h JOIN goals g ON g.id = h.goal_id
           WHERE h.user_id = %s AND g.deleted_at IS NOT NULL""",
        uid,
    )
    assert menaut_terhapus == 0


async def test_goal_terhapus_tidak_bisa_ditaut_dan_hapus_goal_melepas_habitnya(
    api_bersama: ApiUji,
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    hilang = await _goal(api_bersama, token, title="Dihapus dulu")
    await k.delete(f"/v1/goals/{hilang['id']}", headers=auth(token))
    tetap = await _goal(api_bersama, token, title="Dihapus nanti")
    isi = {"title": "Lari", "period": "day", "target_count": 1}

    buat_ke_terhapus = await k.post(
        "/v1/habits", json={**isi, "goal_id": hilang["id"]}, headers=auth(token)
    )
    habit = await k.post("/v1/habits", json={**isi, "goal_id": tetap["id"]}, headers=auth(token))
    ubah_ke_terhapus = await k.patch(
        f"/v1/habits/{habit.json()['id']}", json={"goal_id": hilang["id"]}, headers=auth(token)
    )
    await k.delete(f"/v1/goals/{tetap['id']}", headers=auth(token))
    daftar = (await k.get("/v1/habits", headers=auth(token))).json()["items"]

    assert buat_ke_terhapus.status_code == 422, "habit baru ditaut ke goal yang sudah dihapus"
    assert buat_ke_terhapus.json()["error"]["code"] == "goal_not_found"
    assert ubah_ke_terhapus.status_code == 422, "habit diubah menaut goal yang sudah dihapus"
    assert ubah_ke_terhapus.json()["error"]["code"] == "goal_not_found"
    assert habit.status_code == 201
    assert [h["goal_id"] for h in daftar] == [None], "habit tetap menaut goal yang dihapus"


# ───────────────────────────────────────────────────────────── F3 ulangan ──


async def test_kirim_ulang_sesudah_tier_habit_dikurangi_tetap_200_baris_lama(
    api_bersama: ApiUji,
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    habit = (
        await k.post(
            "/v1/habits",
            json={
                "title": "Baca",
                "period": "day",
                "target_count": 1,
                "adaptive_tiers": [{"label": "a"}, {"label": "b"}, {"label": "c"}],
            },
            headers=auth(token),
        )
    ).json()
    selesai = {"for_date": "2026-09-01", "status": "done", "tier_used": 2}
    jalur = f"/v1/habits/{habit['id']}/completions"

    pertama = await k.post(jalur, json=selesai, headers=auth(token))
    await k.patch(
        f"/v1/habits/{habit['id']}", json={"adaptive_tiers": [{"label": "a"}]}, headers=auth(token)
    )
    ulang = await k.post(jalur, json=selesai, headers=auth(token))

    assert pertama.status_code == 201
    assert ulang.status_code == 200, f"kirim ulang sesudah tier dikurangi: {ulang.status_code}"
    assert ulang.json() == pertama.json()


# ─────────────────────────────────────────────────── F9 · S2 batas (K-24) ──


async def test_batas_goal_per_pengguna_ditegakkan_serial(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    _pemilik(
        api_bersama,
        "INSERT INTO goals (user_id, title) SELECT %s, 'g' FROM generate_series(1, %s)",
        uid,
        goals.MAKS_GOAL - 5,
    )

    hasil = await asyncio.gather(
        *(
            api_bersama.klien.post("/v1/goals", json={"title": "x"}, headers=auth(token))
            for _ in range(10)
        )
    )

    kode = sorted(r.status_code for r in hasil)
    assert kode == [201] * 5 + [422] * 5, f"batas goal dilewati: {kode}"
    ditolak = next(r for r in hasil if r.status_code == 422)
    assert ditolak.json()["error"]["code"] == "goal_limit_reached"
    hidup = _satu(
        api_bersama, "SELECT count(*) FROM goals WHERE user_id = %s AND deleted_at IS NULL", uid
    )
    assert hidup == goals.MAKS_GOAL


async def test_batas_habit_per_pengguna_dan_daftar_tidak_terpotong(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    _pemilik(
        api_bersama,
        "INSERT INTO habits (user_id, title) SELECT %s, 'h' FROM generate_series(1, 495)",
        uid,
    )
    isi = {"title": "x", "period": "day", "target_count": 1}

    hasil = await asyncio.gather(
        *(api_bersama.klien.post("/v1/habits", json=isi, headers=auth(token)) for _ in range(10))
    )
    daftar = await api_bersama.klien.get("/v1/habits", headers=auth(token))

    kode = sorted(r.status_code for r in hasil)
    assert kode == [201] * 5 + [422] * 5, f"batas habit dilewati: {kode}"
    assert next(r for r in hasil if r.status_code == 422).json()["error"]["code"] == (
        "habit_limit_reached"
    )
    assert len(daftar.json()["items"]) == 500


async def test_batas_milestone_per_goal(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    goal = await _goal(api_bersama, token)
    _pemilik(
        api_bersama,
        """INSERT INTO goal_milestones (goal_id, user_id, title)
           SELECT g.id, g.user_id, 'm' FROM goals g, generate_series(1, %s) WHERE g.id = %s""",
        goals.MAKS_MILESTONE - 1,
        UUID(goal["id"]),
    )
    jalur = f"/v1/goals/{goal['id']}/milestones"

    hasil = await asyncio.gather(
        *(api_bersama.klien.post(jalur, json={"title": "m"}, headers=auth(token)) for _ in range(3))
    )
    rinci = await api_bersama.klien.get(f"/v1/goals/{goal['id']}", headers=auth(token))

    kode = sorted(r.status_code for r in hasil)
    assert kode == [201, 422, 422], f"batas milestone dilewati: {kode}"
    assert len(rinci.json()["milestones"]) == goals.MAKS_MILESTONE


# ───────────────────────────────────────────────────── F13 id milestone ──


async def test_milestone_dengan_id_buatan_klien_dan_id_sama_409(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    goal = await _goal(api_bersama, token)
    jalur = f"/v1/goals/{goal['id']}/milestones"
    id_ = str(uuid4())

    pertama = await api_bersama.klien.post(
        jalur, json={"id": id_, "title": "Luring"}, headers=auth(token)
    )
    kedua = await api_bersama.klien.post(
        jalur, json={"id": id_, "title": "Luring"}, headers=auth(token)
    )

    assert pertama.status_code == 201, pertama.text
    assert pertama.json()["id"] == id_, "id milestone buatan klien diabaikan"
    assert (kedua.status_code, kedua.json()["error"]["code"]) == (409, "already_exists")
