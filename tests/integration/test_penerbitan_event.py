"""spec/07 3.2 — penerbitan event dari `habits`, `checkins`, `goals` (spec/06 aturan 6).

Selesai bila: tiap tulisan menerbitkan event — di sini: tiap baris PETA aturan 6
(spec/06), lewat HTTP sebagai peran aplikasi. Event dibaca di basis data sebagai
pemilik skema. Tiga hal yang diuji di tiap baris, sebab ketiganya yang membuat
aturan D spec/02 (*tabel domain adalah proyeksi event*) benar:

1. tulisan yang MELAHIRKAN fakta perilaku menerbitkan tepat satu event;
2. kirim ulang (luring, Idempotency-Key, PUT yang sama) tidak menerbitkan apa pun;
3. koreksi (batal lalu catat lagi, A → B → A) menerbitkan event BARU — tidak
   ditelan sebagai kirim ulang (E-177).
"""

from __future__ import annotations

from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import TIGA_TIER, buat_habit

from hvx.modules import events

pytestmark = pytest.mark.integration


def _event(api: ApiUji, user_id: Any) -> list[dict[str, Any]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT event_type, idempotency_key, subject_type, subject_id::text, payload, source "
            "FROM events WHERE user_id = %s ORDER BY recorded_at, event_type",
            (user_id,),
        ).fetchall()
    return [
        dict(zip(("jenis", "kunci", "subjek", "subjek_id", "payload", "sumber"), b, strict=True))
        for b in baris
    ]


def _jenis(api: ApiUji, user_id: Any) -> list[str]:
    return [e["jenis"] for e in _event(api, user_id)]


# ─────────────────────────────────────────────────────────────── goals ──


async def test_goal_dibuat_menerbitkan_goal_created_sekali(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = {**auth(token), "Idempotency-Key": "goal-sekali"}

    r = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Lari 10K", "domain": "health"}, headers=h
    )
    await api_bersama.klien.post(
        "/v1/goals", json={"title": "Lari 10K", "domain": "health"}, headers=h
    )

    ev = _event(api_bersama, uid)
    assert len(ev) == 1, f"POST /goals tidak menerbitkan tepat satu goal.created: {ev}"
    (e,) = ev
    assert (e["jenis"], e["subjek"], e["subjek_id"]) == ("goal.created", "goal", r.json()["id"])
    assert e["kunci"] == f"goal:{r.json()['id']}:created"
    assert e["payload"] == {"title": "Lari 10K", "domain": "health"}
    assert e["sumber"] == "app"


async def test_goal_tercapai_hanya_saat_status_berubah(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    g = (await api_bersama.klien.post("/v1/goals", json={"title": "G"}, headers=auth(token))).json()
    k = api_bersama.klien

    async def patch(isi: dict[str, Any]) -> None:
        r = await k.patch(f"/v1/goals/{g['id']}", json=isi, headers=auth(token))
        assert r.status_code == 200, r.text

    await patch({"status": "achieved"})
    await patch({"status": "achieved"})  # bukan perubahan
    await patch({"title": "Judul baru"})  # konfigurasi — tanpa event
    await patch({"status": "active"})  # dibuka lagi — tanpa event (spec/06, diakui)
    await patch({"status": "achieved"})  # tercapai LAGI — kejadian baru

    jenis = _jenis(api_bersama, uid)
    assert jenis == ["goal.created", "goal.completed", "goal.completed"], jenis
    selesai = [e for e in _event(api_bersama, uid) if e["jenis"] == "goal.completed"]
    assert selesai[0]["kunci"] != selesai[1]["kunci"], (
        "goal tercapai lagi ditelan sebagai kirim ulang"
    )
    assert selesai[0]["payload"] == {"days_taken": 0}


# ─────────────────────────────────────────────────────────────── habits ──


async def test_habit_dibuat_menerbitkan_habit_created(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()

    h = await buat_habit(api_bersama, token, period="week", target_count=3)

    ev = _event(api_bersama, uid)
    assert len(ev) == 1, f"POST /habits tidak menerbitkan tepat satu habit.created: {ev}"
    (e,) = ev
    assert (e["jenis"], e["kunci"]) == ("habit.created", f"habit:{h['id']}:created")
    assert e["payload"] == {"title": "Workout", "period": "week", "target_count": 3}


async def test_penyelesaian_kirim_ulang_batal_dan_koreksi(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = await buat_habit(api_bersama, token, adaptive_tiers=TIGA_TIER)
    k = api_bersama.klien
    jalur = f"/v1/habits/{h['id']}/completions"

    selesai = {"for_date": "2026-09-10", "status": "done", "tier_used": 1}
    pertama = await k.post(jalur, json=selesai, headers=auth(token))
    await k.post(jalur, json={"for_date": "2026-09-10", "status": "done"}, headers=auth(token))
    await k.delete(f"{jalur}/2026-09-10", headers=auth(token))
    await k.delete(f"{jalur}/2026-09-10", headers=auth(token))  # sudah tidak ada — tanpa event
    lewat = {"for_date": "2026-09-10", "status": "skipped", "note": "sakit"}
    kedua = await k.post(jalur, json=lewat, headers=auth(token))

    ev = [e for e in _event(api_bersama, uid) if e["jenis"] != "habit.created"]
    assert [e["jenis"] for e in ev] == [
        "habit.completed",
        "habit.completion_retracted",
        "habit.skipped",
    ], f"peta aturan 6 tidak ditepati: {[e['jenis'] for e in ev]}"
    id1, id2 = pertama.json()["id"], kedua.json()["id"]
    assert ev[0]["payload"] == {
        "status": "done",
        "tier_used": 1,
        "for_date": "2026-09-10",
        "completion_id": id1,
    }
    assert ev[0]["kunci"] == f"habit-completion:{id1}"
    assert ev[1]["payload"] == {"for_date": "2026-09-10", "completion_id": id1}
    assert ev[2]["payload"] == {"reason": "sakit", "for_date": "2026-09-10", "completion_id": id2}
    assert all(e["subjek"] == "habit" and e["subjek_id"] == h["id"] for e in ev)


# ─────────────────────────────────────────────────────────── checkins ──


async def test_check_in_diterbitkan_hanya_saat_isinya_berubah_dan_koreksi_tidak_ditelan(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien

    async def put(isi: dict[str, Any]) -> None:
        r = await k.put("/v1/checkins/2026-09-11", json=isi, headers=auth(token))
        assert r.status_code in (200, 201), r.text

    await put({"energy": 3})
    await put({"energy": 3})  # sama persis — tanpa event
    await put({"energy": 3, "note": "catatan saja"})  # isi event sama — tanpa event
    await put({"energy": 2})
    await put({"energy": 3})  # A → B → A

    ev = _event(api_bersama, uid)
    assert [e["payload"].get("energy") for e in ev] == [3, 2, 3], (
        f"event check-in tidak mengikuti perubahan isinya: {[e['payload'] for e in ev]}"
    )
    assert len({e["kunci"] for e in ev}) == 3
    assert all(e["jenis"] == "checkin.logged" for e in ev)
    assert ev[-1]["payload"] == {"energy": 3, "for_date": "2026-09-11"}


# ─────────────────────────────────────────────────────────────── moods ──


async def test_dua_mood_dalam_satu_menit_dua_event(api_bersama: ApiUji) -> None:
    """E-177 — kunci lama `mood:<user>:<menit>` menelan mood kedua."""
    uid, token = await api_bersama.pengguna_baru()
    waktu = "2026-09-12T08:00:10Z"

    a = await api_bersama.klien.post(
        "/v1/moods", json={"valence": 2, "occurred_at": waktu}, headers=auth(token)
    )
    b = await api_bersama.klien.post(
        "/v1/moods", json={"valence": 4, "label": "lega", "occurred_at": waktu}, headers=auth(token)
    )

    assert (a.status_code, b.status_code) == (201, 201), (
        f"mood kedua dalam menit yang sama gagal: {b.text}"
    )
    ev = _event(api_bersama, uid)
    assert [e["kunci"] for e in ev] == [f"mood:{a.json()['id']}", f"mood:{b.json()['id']}"]
    assert [e["payload"] for e in ev] == [{"valence": 2}, {"valence": 4, "label": "lega"}]


# ───────────────────────────────────────────────────────── atomisitas ──


async def test_event_yang_gagal_terbit_membatalkan_tulisannya(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tulisan domain dan event-nya satu transaksi — tidak ada fakta tanpa event."""
    _uid, token = await api_bersama.pengguna_baru()

    async def gagal(*_a: Any, **_k: Any) -> events.HasilTerbit:
        raise events.EventTidakSah("dipaksa gagal")

    monkeypatch.setattr(events, "terbitkan", gagal)

    r = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Tanpa event"}, headers=auth(token)
    )

    assert (await api_bersama.klien.get("/v1/goals", headers=auth(token))).json()["items"] == [], (
        "goal tersimpan tanpa event-nya"
    )
    assert r.status_code == 500
