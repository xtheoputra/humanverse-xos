"""spec/07 4.3 — 9 tool V0 terhadap PostgreSQL, Redis, dan Qdrant sungguhan.

Tiap tool memakai layanan yang sama dengan rute HTTP-nya, di bawah RLS pengguna yang
dilayani run itu — datanya disiapkan lewat HTTP, dibaca balik lewat tool. Yang dijaga
di luar kontrak spec/04: catatan bebas pengguna (`note` check-in & mood) tidak pernah
keluar dari tool coach (C-32), dan tool yang menulis melewati jalur yang sama —
dengan event-nya — seperti tulisan HTTP.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import buat_habit
from test_memori import COACH, _izin, _pencari, _siapkan_pengguna, koleksi  # noqa: F401 - fixture

from hvx.modules import agents, identity, platform

pytestmark = pytest.mark.integration

REGISTRI = agents.muat_registri()


class _GerbangBuka:
    """Gerbang yang selalu mengizinkan — gerbang sungguhan diuji di 4.5."""

    async def periksa(self, j: agents.Jalannya, alat: agents.Alat, m: Mapping[str, Any]) -> None:
        return None


def _pelaksana(pembatas: platform.PembatasLaju | None = None) -> agents.PelaksanaAlat:
    return agents.PelaksanaAlat(REGISTRI, agents.IMPLEMENTASI, _GerbangBuka(), pembatas)


def _jalannya(agent: str, uid: UUID) -> agents.Jalannya:
    return agents.Jalannya(uuid4(), uid, REGISTRI.agent[agent], "user")


async def _panggil(
    api: ApiUji,
    j: agents.Jalannya,
    nama: str,
    masukan: dict[str, Any],
    *,
    pelaksana: agents.PelaksanaAlat | None = None,
    layanan: agents.LayananAlat | None = None,
) -> dict[str, Any]:
    return await (pelaksana or _pelaksana()).panggil(
        api.app.state.engine, j, nama, masukan, layanan or agents.LayananAlat()
    )


def _sql(api: ApiUji, q: str, *p: object) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(q, p).fetchall()


async def test_alat_baca_coach_tanpa_catatan_bebas_pengguna(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h, k = auth(token), api_bersama.klien
    habit = await buat_habit(api_bersama, token)
    await k.post("/v1/goals", json={"title": "Lari 10K", "domain": "health"}, headers=h)
    await k.put("/v1/checkins/2026-09-20", json={"energy": 2, "note": "rahasia-checkin"}, headers=h)
    await k.post(
        "/v1/moods", json={"valence": 2, "label": "cemas", "note": "rahasia-mood"}, headers=h
    )
    coach = _jalannya("coach-agent", uid)

    daftar = await _panggil(api_bersama, coach, "habit.list", {"for_date": "2026-09-20"})
    goal = await _panggil(api_bersama, coach, "goal.list", {})
    checkin = await _panggil(api_bersama, coach, "checkin.get", {"for_date": "2026-09-20"})
    mood = await _panggil(api_bersama, coach, "mood.recent", {"hari": 7})
    rentetan = await _panggil(api_bersama, coach, "habit.streak", {"habit_id": habit["id"]})

    assert [x["id"] for x in daftar["items"]] == [habit["id"]]
    assert daftar["items"][0]["day"]["energy"] == 2
    assert [x["title"] for x in goal["items"]] == ["Lari 10K"]
    assert (goal["terpotong"], mood["terpotong"]) == (False, False)
    assert checkin["checkin"]["energy"] == 2
    assert [(x["valence"], x["label"]) for x in mood["items"]] == [(2, "cemas")]
    assert set(rentetan) == {"current", "longest", "completion_rate_30d"}
    semua = f"{daftar}{goal}{checkin}{mood}"
    assert "rahasia" not in semua, "catatan bebas pengguna keluar dari tool coach (C-32)"
    assert coach.scope_dipakai == {"habits", "goals", "checkins", "mood"}
    assert coach.alat_dipakai == [
        "habit.list",
        "goal.list",
        "checkin.get",
        "mood.recent",
        "habit.streak",
    ]


async def test_daftar_yang_terpotong_mengatakannya(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """K-24: daftar yang dipotong diam-diam adalah jawaban yang salah."""
    from hvx.modules.agents import alat_v0

    monkeypatch.setattr(alat_v0, "MOOD_MAKS", 1)
    monkeypatch.setattr(alat_v0, "GOAL_MAKS", 1)
    uid, token = await api_bersama.pengguna_baru()
    h, k = auth(token), api_bersama.klien
    for valensi in (2, 4):
        await k.post("/v1/moods", json={"valence": valensi}, headers=h)
    for judul in ("Lari 10K", "Tidur cukup"):
        await k.post("/v1/goals", json={"title": judul, "domain": "health"}, headers=h)
    coach = _jalannya("coach-agent", uid)

    mood = await _panggil(api_bersama, coach, "mood.recent", {})
    goal = await _panggil(api_bersama, coach, "goal.list", {})

    assert (len(mood["items"]), mood["terpotong"]) == (1, True), "mood terpotong diam-diam"
    assert (len(goal["items"]), goal["terpotong"]) == (1, True), "goal terpotong diam-diam"


async def test_habit_complete_menulis_seperti_jalur_http(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token)
    j = _jalannya("habit-agent", uid)
    masukan = {"habit_id": habit["id"], "for_date": "2026-09-20", "status": "done"}

    pertama = await _panggil(api_bersama, j, "habit.complete", masukan)
    kedua = await _panggil(api_bersama, j, "habit.complete", masukan)

    assert pertama == kedua, "kirim ulang lewat tool melahirkan baris kedua"
    assert pertama["status"] == "done"
    ev = _sql(
        api_bersama, "SELECT event_type FROM events WHERE user_id = %s ORDER BY recorded_at", uid
    )
    assert ev == [("habit.created",), ("habit.completed",)], f"event tulisan tool: {ev}"


async def test_habit_complete_untuk_habit_orang_lain_gagal_bukan_menulis(
    api_bersama: ApiUji,
) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    b, _token_b = await api_bersama.pengguna_baru()
    habit_a = await buat_habit(api_bersama, token_a)

    with pytest.raises(agents.AlatGagal) as galat:
        await _panggil(
            api_bersama,
            _jalannya("habit-agent", b),
            "habit.complete",
            {"habit_id": habit_a["id"], "for_date": "2026-09-20", "status": "done"},
        )

    assert galat.value.kode == "not_found"
    assert _sql(api_bersama, "SELECT count(*) FROM habit_completions WHERE user_id = %s", b) == [
        (0,)
    ]


async def test_memory_write_hanya_bila_belum_diingat_dan_di_scope_manifestnya(
    api_bersama: ApiUji,
) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    j = _jalannya("memory-agent", uid)

    a = await _panggil(
        api_bersama, j, "memory.write", {"scope": "coaching_notes", "isi": "alergi kacang"}
    )
    b = await _panggil(
        api_bersama, j, "memory.write", {"scope": "coaching_notes", "isi": "  alergi   kacang "}
    )
    with pytest.raises(agents.AlatDitolak) as galat:
        await _panggil(api_bersama, j, "memory.write", {"scope": "journal_raw", "isi": "x"})

    assert (a["baru"], b["baru"], a["id"] == b["id"]) == (True, False, True), "diingat dua kali"
    assert galat.value.kode == "scope_di_luar_manifest"
    assert _sql(
        api_bersama,
        "SELECT kind, scope, content, confidence, model_version, embedding_model FROM memories "
        "WHERE user_id = %s",
        uid,
    ) == [
        (
            "semantic",
            "coaching_notes",
            "alergi kacang",
            Decimal("1.000"),
            "memory-agent@1.0.0",
            None,
        )
    ]


async def test_recommendation_create_menyimpan_keyakinan_dan_alasan(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    coach = _jalannya("coach-agent", uid)

    r = await _panggil(
        api_bersama,
        coach,
        "recommendation.create",
        {
            "domain": "habit",
            "title": "Tidur lebih awal malam ini",
            "confidence": 0.62,
            "rationale": ["Tidur 5 jam tiga malam terakhir"],
        },
    )
    with pytest.raises(agents.AlatDitolak) as galat:
        await _panggil(
            api_bersama,
            coach,
            "recommendation.create",
            {"domain": "habit", "title": "Tanpa alasan", "confidence": 0.5, "rationale": []},
        )

    assert galat.value.kode == "masukan_salah", "rekomendasi tanpa alasan disimpan"
    assert _sql(
        api_bersama,
        "SELECT agent_id, domain, confidence, rationale, score, status FROM recommendations "
        "WHERE id = %s",
        r["id"],
    ) == [
        (
            REGISTRI.agent["coach-agent"].id_katalog,
            "habit",
            Decimal("0.620"),
            ["Tidur 5 jam tiga malam terakhir"],
            None,  # skor = keluaran mesin 5.5, bukan angka agent
            "pending",
        )
    ]


async def test_memory_search_hanya_scope_manifest_yang_diizinkan(
    api_bersama: ApiUji,
    koleksi: tuple[platform.KlienVektor, str],  # noqa: F811
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    await _izin(api_bersama).tetapkan(uid, COACH, "goals", "read", "deny")
    coach = _jalannya("coach-agent", uid)

    hasil = await _panggil(
        api_bersama,
        coach,
        "memory.search",
        {"kueri": "capek rapat"},
        layanan=agents.LayananAlat(pencari_memori=_pencari(api_bersama, koleksi)),
    )
    tanpa_qdrant = await _panggil(api_bersama, coach, "memory.search", {"kueri": "capek rapat"})

    assert [x["id"] for x in hasil["items"]] == [str(ids["mood"])]
    assert ids["journal_raw"] not in [x["id"] for x in hasil["items"]]  # di luar manifest coach
    # Yang DIIZINKAN, bukan yang diminta manifest: `goals` ditolak pengguna.
    assert coach.scope_dipakai == set(REGISTRI.agent["coach-agent"].memory.read) - {"goals"}, (
        f"scope yang dicatat run: {sorted(coach.scope_dipakai)}"
    )
    assert tanpa_qdrant == {"items": [], "perlu_izin": []}


async def test_batas_laju_tool_per_pengguna(api_bersama: ApiUji) -> None:
    """goal.list `60/min/user` — pengguna lain tidak ikut terhitung."""
    a, _ta = await api_bersama.pengguna_baru()
    b, _tb = await api_bersama.pengguna_baru()
    pembatas = platform.PembatasLaju(api_bersama.app.state.redis, f"uji-{uuid4().hex[:10]}")
    p = _pelaksana(pembatas)

    for _ in range(60):
        await _panggil(api_bersama, _jalannya("coach-agent", a), "goal.list", {}, pelaksana=p)
    with pytest.raises(agents.AlatDitolak) as galat:
        await _panggil(api_bersama, _jalannya("coach-agent", a), "goal.list", {}, pelaksana=p)
    lain = await _panggil(api_bersama, _jalannya("coach-agent", b), "goal.list", {}, pelaksana=p)

    assert galat.value.kode == "terlalu_sering", "batas laju tool tidak ditegakkan"
    assert lain == {"items": [], "terpotong": False}


# ── E-205: tulisan agent berjejak di audit_logs, di transaksi tulisannya ────────────

_TULIS = [
    ("habit-agent", "habit.complete"),
    ("memory-agent", "memory.write"),
    ("coach-agent", "recommendation.create"),
]


async def _masukan_tulis(api: ApiUji, token: str, nama: str) -> dict[str, Any]:
    if nama == "habit.complete":
        habit = await buat_habit(api, token)
        return {"habit_id": habit["id"], "for_date": "2026-09-20", "status": "done"}
    if nama == "memory.write":
        return {"scope": "coaching_notes", "isi": "aku alergi kacang"}
    return {"domain": "habit", "title": "Tidur awal", "confidence": 0.6, "rationale": ["a"]}


@pytest.mark.parametrize(("agent", "nama"), _TULIS)
async def test_tulisan_agent_meninggalkan_jejak_audit(
    api_bersama: ApiUji, agent: str, nama: str
) -> None:
    """spec/05 *Risk gate*: *jalankan · catat agent_runs · catat audit_logs* — dulu hanya
    penolakan dan jawaban konfirmasi yang tercatat, tulisan agentnya tidak (E-205)."""
    uid, token = await api_bersama.pengguna_baru()
    j = _jalannya(agent, uid)
    masukan = await _masukan_tulis(api_bersama, token, nama)

    await _panggil(api_bersama, j, nama, masukan)

    assert _sql(
        api_bersama,
        "SELECT actor_type, actor_id, subject_type, subject_id, metadata->>'run'"
        " FROM audit_logs WHERE user_id = %s AND action = 'agent.tool_executed'",
        uid,
    ) == [("agent", agent, "tool", nama, str(j.id))], f"tulisan agent tanpa jejak audit: {nama}"


async def test_tulisan_yang_tidak_mengubah_apa_pun_tidak_berjejak(api_bersama: ApiUji) -> None:
    """Kirim ulang yang mengembalikan baris lama — tidak ada yang berubah, tidak ada jejak."""
    uid, token = await api_bersama.pengguna_baru()
    for agent, nama in _TULIS[:2]:  # yang punya "sudah ada"
        masukan = await _masukan_tulis(api_bersama, token, nama)
        await _panggil(api_bersama, _jalannya(agent, uid), nama, masukan)
        await _panggil(api_bersama, _jalannya(agent, uid), nama, masukan)

    assert _sql(
        api_bersama,
        "SELECT subject_id, count(*) FROM audit_logs WHERE user_id = %s"
        " AND action = 'agent.tool_executed' GROUP BY subject_id ORDER BY subject_id",
        uid,
    ) == [("habit.complete", 1), ("memory.write", 1)], (
        "tulisan yang tidak mengubah apa pun berjejak"
    )


@pytest.mark.parametrize(("agent", "nama"), _TULIS)
async def test_jejak_yang_gagal_membatalkan_tulisannya(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch, agent: str, nama: str
) -> None:
    """Satu transaksi: tulisan tanpa jejak tidak bisa terjadi."""
    uid, token = await api_bersama.pengguna_baru()
    masukan = await _masukan_tulis(api_bersama, token, nama)

    async def gagal(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("audit gagal")

    monkeypatch.setattr(identity, "audit", gagal)
    with pytest.raises(RuntimeError, match="audit gagal"):
        await _panggil(api_bersama, _jalannya(agent, uid), nama, masukan)
    monkeypatch.undo()

    tabel = {
        "habit.complete": "habit_completions",
        "memory.write": "memories",
        "recommendation.create": "recommendations",
    }[nama]
    assert _sql(api_bersama, f"SELECT count(*) FROM {tabel} WHERE user_id = %s", uid) == [(0,)], (
        f"{nama} tersimpan tanpa jejak auditnya"
    )


async def test_event_tulisan_agent_bersumber_agent(api_bersama: ApiUji) -> None:
    """spec/03 `source`: `app` · `agent` … — `habit.completed` yang lahir dari agent dulu
    bersumber `app`: asal-usul tulisan agent hilang dari aliran event."""
    uid, token = await api_bersama.pengguna_baru()
    masukan = await _masukan_tulis(api_bersama, token, "habit.complete")

    await _panggil(api_bersama, _jalannya("habit-agent", uid), "habit.complete", masukan)

    assert _sql(
        api_bersama,
        "SELECT event_type, source FROM events WHERE user_id = %s ORDER BY recorded_at",
        uid,
    ) == [("habit.created", "app"), ("habit.completed", "agent")], (
        "event tulisan agent tidak bersumber agent"
    )


@pytest.mark.parametrize(("agent", "nama"), _TULIS)
async def test_jejak_ikut_batal_bersama_tulisannya(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch, agent: str, nama: str
) -> None:
    """Satu transaksi, arah sebaliknya: tulisan yang batal SESUDAH jejaknya ditulis tidak
    meninggalkan jejak — jejak tanpa tulisan tidak bisa terjadi."""
    uid, token = await api_bersama.pengguna_baru()
    masukan = await _masukan_tulis(api_bersama, token, nama)
    asli = agents.KonteksAlat.jejak

    async def lalu_gagal(self: agents.KonteksAlat, conn: Any) -> None:
        await asli(self, conn)
        raise RuntimeError("tulisan batal sesudah jejaknya")

    monkeypatch.setattr(agents.KonteksAlat, "jejak", lalu_gagal)
    with pytest.raises(RuntimeError, match="sesudah jejaknya"):
        await _panggil(api_bersama, _jalannya(agent, uid), nama, masukan)

    assert _sql(
        api_bersama,
        "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action = 'agent.tool_executed'",
        uid,
    ) == [(0,)], f"jejak audit tersimpan untuk tulisan yang dibatalkan: {nama}"
