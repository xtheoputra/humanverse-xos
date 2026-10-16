"""spec/07 4.3 — 9 tool V0 terhadap PostgreSQL, Redis, dan Qdrant sungguhan.

Tiap tool memakai layanan yang sama dengan rute HTTP-nya, di bawah RLS pengguna yang
dilayani run itu — datanya disiapkan lewat HTTP, dibaca balik lewat tool. Yang dijaga
di luar kontrak spec/04: catatan bebas pengguna (`note` check-in & mood) tidak pernah
keluar dari tool coach (C-32), dan tool yang menulis melewati jalur yang sama —
dengan event-nya — seperti tulisan HTTP.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_agent import runtime_uji
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import buat_habit
from test_memori import (  # noqa: F401 - koleksi: fixture
    COACH,
    _awalan,
    _ekstrak_semua,
    _izin,
    _pencari,
    _penyelaras,
    _post,
    _siapkan_pengguna,
    _sql_pemilik,
    koleksi,
)

from hvx.modules import agents, identity, intelligence, memory, platform

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
    # di luar manifest coach — 🔧 id keluaran tool berbentuk teks: membandingkan UUID
    # dengan daftar teks selalu lolos (tinjauan penegak buta Sprint 4).
    assert str(ids["journal_raw"]) not in [x["id"] for x in hasil["items"]]
    # Yang DIIZINKAN, bukan yang diminta manifest: `goals` ditolak pengguna.
    assert coach.scope_dipakai == set(REGISTRI.agent["coach-agent"].memory.read) - {"goals"}, (
        f"scope yang dicatat run: {sorted(coach.scope_dipakai)}"
    )
    assert tanpa_qdrant == {"items": [], "perlu_izin": []}


async def _jam_redis_ms(api: ApiUji) -> int:
    detik, mikro = await api.app.state.redis.time()
    return int(detik) * 1000 + int(mikro) // 1000


async def test_batas_laju_tool_per_pengguna(api_bersama: ApiUji) -> None:
    """goal.list `60/min/user` — pengguna lain tidak ikut terhitung.

    🔧 Uji ini dulu menuntut panggilan KE-61 ditolak — benar hanya bila 61 panggilan selesai
    dalam SATU detik jam Redis: GCRA mengisi kembali satu jatah tiap 60 dtk / 60. Di mesin
    yang sibuk 60 panggilan makan 2,9 dtk jam Redis, dan yang ke-61 lolos (berkedip —
    diukur tinjauan penegak buta Sprint 4; jam Redis TIDAK mundur di sana, dan langkah
    mundur justru memperketat). Kini: ledakan 60 wajib lolos, lalu penolakan wajib datang
    sebelum melewati jatah yang terisi selama uji itu sendiri — diukur dengan jam Redis,
    jam yang dipakai pembatasnya.
    """
    a, _ta = await api_bersama.pengguna_baru()
    b, _tb = await api_bersama.pengguna_baru()
    pembatas = platform.PembatasLaju(api_bersama.app.state.redis, f"uji-{uuid4().hex[:10]}")
    p = _pelaksana(pembatas)

    async def goal_list(uid: UUID) -> dict[str, Any]:
        j = _jalannya("coach-agent", uid)
        return await _panggil(api_bersama, j, "goal.list", {}, pelaksana=p)

    jam_lolos: list[int] = []  # jam Redis sesudah tiap panggilan yang lolos di luar ledakan

    async def sampai_ditolak() -> None:
        for _ in range(60):  # jauh di atas jatah yang terisi selama uji ini
            await goal_list(a)
            jam_lolos.append(await _jam_redis_ms(api_bersama))

    mulai = await _jam_redis_ms(api_bersama)
    for _ in range(60):  # ledakan penuh
        await goal_list(a)
    with pytest.raises(agents.AlatDitolak) as galat:
        await sampai_ditolak()
    lain = await goal_list(b)

    assert galat.value.kode == "terlalu_sering", "batas laju tool tidak ditegakkan"
    # satu jatah per 1.000 ms jam Redis sejak panggilan pertama — tidak lebih
    terisi, akhir = len(jam_lolos), max(jam_lolos, default=mulai)
    assert terisi * 1000 <= akhir - mulai, (
        f"{60 + terisi} panggilan lolos dalam {akhir - mulai} ms — batasnya bukan 60/min"
    )
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


# ── Tinjauan penegak buta Sprint 4 (G4): janji tool yang dulu tidak dijaga uji mana pun ──


async def test_memory_search_tidak_melebar_ke_luar_manifest_pemanggil(
    api_bersama: ApiUji,
    koleksi: tuple[platform.KlienVektor, str],  # noqa: F811
) -> None:
    """spec/05 aturan 2 — `memory.search` mencari HANYA di `memory.read` manifest pemanggil.
    `journal_raw` di luar manifest coach (DENY naskah 5 §15): izinnya tidak ditanyakan
    (`perlu_izin` MENGUNDANG pengguna membukanya), dan izin yang pernah diberikan pengguna
    pun tidak melebarkan manifest."""
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    layanan = agents.LayananAlat(pencari_memori=_pencari(api_bersama, koleksi))

    async def cari() -> dict[str, Any]:
        coach = _jalannya("coach-agent", uid)
        return await _panggil(
            api_bersama, coach, "memory.search", {"kueri": "rapat"}, layanan=layanan
        )

    belum = await cari()
    await _izin(api_bersama).tetapkan(uid, COACH, "journal_raw", "read", "allow")
    sesudah = await cari()

    assert "journal_raw" not in belum["perlu_izin"], (
        "memory.search menanyakan izin journal_raw — scope di luar manifest coach"
    )
    assert [x["id"] for x in sesudah["items"]] == [str(ids["mood"])], (
        "izin pengguna melebarkan manifest coach ke journal_raw"
    )


async def test_habit_list_hanya_habit_aktif(api_bersama: ApiUji) -> None:
    """`habit.list` = habit AKTIF. Habit yang diarsipkan pengguna tidak disebut coach dan
    tidak bisa ditandai habit-agent — sasaran *“tandai …”* dicari di daftar ini."""
    uid, token = await api_bersama.pengguna_baru()
    aktif = await buat_habit(api_bersama, token, title="Lari pagi")
    arsip = await buat_habit(api_bersama, token, title="Meditasi")
    r = await api_bersama.klien.patch(
        f"/v1/habits/{arsip['id']}", json={"status": "archived"}, headers=auth(token)
    )
    assert r.status_code == 200, r.text

    daftar = await _panggil(api_bersama, _jalannya("coach-agent", uid), "habit.list", {})

    assert [x["id"] for x in daftar["items"]] == [aktif["id"]], (
        "habit.list menyertakan habit yang diarsipkan"
    )


async def test_goal_list_menyaring_status(api_bersama: ApiUji) -> None:
    """Coach meminta `{'status': 'active'}` lalu berkata *“N goal aktif”* — goal yang sudah
    tercapai atau ditinggalkan bukan goal aktif."""
    uid, token = await api_bersama.pengguna_baru()
    h, k = auth(token), api_bersama.klien
    await k.post("/v1/goals", json={"title": "Lari 10K", "domain": "health"}, headers=h)
    r = await k.post("/v1/goals", json={"title": "Tidur cukup", "domain": "health"}, headers=h)
    r = await k.patch(f"/v1/goals/{r.json()['id']}", json={"status": "achieved"}, headers=h)
    assert r.status_code == 200, r.text

    daftar = await _panggil(
        api_bersama, _jalannya("coach-agent", uid), "goal.list", {"status": "active"}
    )

    assert [g["title"] for g in daftar["items"]] == ["Lari 10K"], (
        "goal.list mengabaikan status — goal yang tercapai terbaca sebagai goal aktif"
    )


async def test_mood_recent_membaca_jendela_hari_yang_diminta(api_bersama: ApiUji) -> None:
    """`mood.recent {'hari': n}` — mood n hari terakhir, bukan jendela bawaan 7 hari."""
    uid, token = await api_bersama.pengguna_baru()
    tiga_hari_lalu = (datetime.now(UTC) - timedelta(days=3)).isoformat()
    r = await api_bersama.klien.post(
        "/v1/moods", json={"valence": 2, "occurred_at": tiga_hari_lalu}, headers=auth(token)
    )
    assert r.status_code == 201, r.text
    coach = _jalannya("coach-agent", uid)

    sehari = await _panggil(api_bersama, coach, "mood.recent", {"hari": 1})
    seminggu = await _panggil(api_bersama, coach, "mood.recent", {"hari": 7})

    assert sehari["items"] == [], (
        "mood.recent mengabaikan `hari` — mood 3 hari lalu terbaca di jendela 1 hari"
    )
    assert len(seminggu["items"]) == 1


async def test_memory_search_tanpa_batas_lima_hasil(
    api_bersama: ApiUji,
    koleksi: tuple[platform.KlienVektor, str],  # noqa: F811
) -> None:
    """Tanpa `batas`, `memory.search` menyerahkan lima yang paling mirip — tiap hasil menjadi
    satu fakta di bahan agent; bukan seluruh yang cocok sampai `memory.MAKS_HASIL`."""
    uid, token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "allow")  # C-32: mood sensitif
    for i in range(7):
        await _post(api_bersama, token, "/v1/moods", {"valence": 3, "note": f"rapat ke-{i}"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()

    hasil = await _panggil(
        api_bersama,
        _jalannya("coach-agent", uid),
        "memory.search",
        {"kueri": "rapat"},
        layanan=agents.LayananAlat(pencari_memori=_pencari(api_bersama, koleksi)),
    )

    assert len(hasil["items"]) == 5, (
        f"memory.search tanpa batas menyerahkan {len(hasil['items'])} hasil, bukan 5"
    )


@pytest.mark.parametrize(
    ("agent", "nama", "scope"),
    [
        ("memory-agent", "memory.write", {"mood"}),
        ("coach-agent", "recommendation.create", {"coaching_notes"}),
        ("coach-agent", "habit.streak", {"habits"}),
    ],
)
async def test_tool_mencatat_scope_yang_disentuhnya(
    api_bersama: ApiUji, agent: str, nama: str, scope: set[str]
) -> None:
    """4.4 — `agent_runs.memory_scopes` = scope yang BENAR-BENAR disentuh, dicatat tiap
    implementasi tool. Satu tool per run: tool lain yang kebetulan menyentuh scope yang sama
    (`habit.list` → habits) tidak menutupi implementasi yang lupa mencatatnya."""
    uid, token = await api_bersama.pengguna_baru()
    j = _jalannya(agent, uid)
    if nama == "habit.streak":
        masukan: dict[str, Any] = {"habit_id": (await buat_habit(api_bersama, token))["id"]}
    elif nama == "memory.write":  # scope dari masukannya — bukan tetap
        masukan = {"scope": "mood", "isi": "aku lebih tenang sesudah lari"}
    else:
        masukan = await _masukan_tulis(api_bersama, token, nama)

    await _panggil(api_bersama, j, nama, masukan)

    assert j.scope_dipakai == scope, (
        f"{nama} tidak mencatat scope yang disentuhnya: {sorted(j.scope_dipakai)}"
    )


# ── memory.write: “sudah diingat” hanya memori semantik yang HIDUP dan BERLAKU ─────────


async def _ingat(api: ApiUji, uid: UUID, scope: str, isi: str) -> dict[str, Any]:
    j = _jalannya("memory-agent", uid)
    return await _panggil(api, j, "memory.write", {"scope": scope, "isi": isi})


async def test_ingatan_yang_dihapus_bukan_sudah_diingat(api_bersama: ApiUji) -> None:
    """*“Sudah diingat”* dibaca dari memori HIDUP — penanda hapusnya sendiri yang menentukan,
    bukan kebetulan isinya sudah dikosongkan (`memory.lupakan` hari ini mengosongkan keduanya
    dalam satu pernyataan; penghapusan memori oleh pengguna belum ada di V0). Menjawab *“itu
    sudah kuingat”* atas baris yang dihapus tidak menulis apa pun — dan bohong."""
    uid, _token = await api_bersama.pengguna_baru()
    lama = await _ingat(api_bersama, uid, "coaching_notes", "aku alergi kacang")
    _sql_pemilik(api_bersama, "UPDATE memories SET deleted_at = now() WHERE id = %s", lama["id"])

    lagi = await _ingat(api_bersama, uid, "coaching_notes", "aku alergi kacang")

    assert (lagi["baru"], lagi["id"] != lama["id"]) == (True, True), (
        "ingatan yang dihapus dihitung “sudah diingat” — tidak ada yang ditulis"
    )


async def test_ingatan_kedaluwarsa_bukan_sudah_diingat(api_bersama: ApiUji) -> None:
    """Memori yang masa berlakunya lewat (`valid_until`) tidak lagi diserahkan pencarian
    (3.7) — menghitungnya *“sudah diingat”* menghilangkan permintaan mengingat tanpa bekas."""
    uid, _token = await api_bersama.pengguna_baru()
    lama = await _ingat(api_bersama, uid, "coaching_notes", "aku alergi kacang")
    _sql_pemilik(
        api_bersama,
        "UPDATE memories SET valid_from = now() - interval '2 days', "
        "valid_until = now() - interval '1 day' WHERE id = %s",
        lama["id"],
    )

    lagi = await _ingat(api_bersama, uid, "coaching_notes", "aku alergi kacang")

    assert (lagi["baru"], lagi["id"] != lama["id"]) == (True, True), (
        "ingatan yang kedaluwarsa dihitung “sudah diingat” — tidak ada yang ditulis"
    )


async def test_hanya_ingatan_semantik_yang_menghalangi_tulisan_ulang(api_bersama: ApiUji) -> None:
    """Memori EPISODIK adalah kejadian yang diturunkan dari sumbernya (3.6) — bukan fakta
    yang pengguna minta diingat. Isinya yang kebetulan sama tidak menggantikan permintaan
    *“ingat bahwa …”*."""
    uid, token = await api_bersama.pengguna_baru()
    await _post(api_bersama, token, "/v1/moods", {"valence": 4, "note": "tenang sesudah lari"})
    await _ekstrak_semua(api_bersama, _awalan())
    ((isi,),) = _sql(
        api_bersama,
        "SELECT content FROM memories WHERE user_id = %s AND kind = 'episodic'",
        uid,
    )

    tulis = await _ingat(api_bersama, uid, "mood", isi)

    assert tulis["baru"] is True, (
        "memori episodik dihitung “sudah diingat” — permintaan mengingat diabaikan"
    )


PERCOBAAN_SERENTAK = 10


async def test_ingat_serentak_tidak_melahirkan_dua_baris(api_bersama: ApiUji) -> None:
    """Dua *“ingat bahwa X”* serentak (dua perangkat, kirim ulang): pemeriksaan *“sudah
    diingat”* dan sisipannya dikunci per (pengguna, scope) — tanpa kunci keduanya membaca
    *“belum”* lalu sama-sama menulis. `asyncio.gather` di satu event loop menyelang-nyelingi
    kedua transaksi di tiap `await` basis data."""
    uid, _token = await api_bersama.pengguna_baru()

    for i in range(PERCOBAAN_SERENTAK):
        isi = f"fakta serentak ke-{i}"
        await asyncio.gather(*(_ingat(api_bersama, uid, "coaching_notes", isi) for _ in range(2)))

    ganda = _sql(
        api_bersama,
        "SELECT content, count(*) FROM memories WHERE user_id = %s"
        " GROUP BY content HAVING count(*) > 1 ORDER BY content",
        uid,
    )
    assert ganda == [], f"ingatan yang sama ditulis serentak dua kali: {ganda}"


# ── recommendation.create: batas pemiliknya, dan run yang membuatnya ────────────────────

_REKOMENDASI_DI_LUAR_BATAS = [
    ("judul 201 karakter", {"title": "t" * 201}),
    ("isi 2.001 karakter", {"body": "b" * 2001}),
    ("11 alasan", {"rationale": [f"alasan {i}" for i in range(11)]}),
    ("alasan tanpa isi", {"rationale": ["   "]}),
]


@pytest.mark.parametrize(
    ("maksud", "ganti"),
    _REKOMENDASI_DI_LUAR_BATAS,
    ids=["judul", "isi", "alasan-banyak", "alasan-kosong"],
)
async def test_rekomendasi_di_luar_batas_pemiliknya_ditolak_tanpa_baris(
    api_bersama: ApiUji, maksud: str, ganti: dict[str, Any]
) -> None:
    """Skema tool tidak membatasi panjang (`title`/`body` string, `rationale` array) dan
    `recommendations` tidak punya CHECK-nya: judul ≤ 200, isi ≤ 2.000, 1–10 alasan berisi
    hanya dijaga `intelligence.periksa_rekomendasi`. Ditolak — dan tidak ada baris."""
    uid, _token = await api_bersama.pengguna_baru()
    masukan = {
        "domain": "habit",
        "title": "Tidur awal",
        "confidence": 0.6,
        "rationale": ["Tidur 5 jam"],
        **ganti,
    }

    try:
        await _panggil(api_bersama, _jalannya("coach-agent", uid), "recommendation.create", masukan)
    except agents.AlatDitolak as galat:
        kode: str | None = galat.kode
    else:
        kode = None

    tersimpan = _sql(api_bersama, "SELECT count(*) FROM recommendations WHERE user_id = %s", uid)
    assert (kode, tersimpan) == ("masukan_salah", [(0,)]), (
        f"rekomendasi dengan {maksud} disimpan (kode {kode})"
    )


async def test_rekomendasi_terikat_run_yang_membuatnya(api_bersama: ApiUji) -> None:
    """`recommendations.agent_run_id` — dari run mana sebuah saran lahir: tanpa itu keyakinan
    dan alasannya tidak bisa ditelusuri ke tool, model, dan persetujuan di baliknya (4.4)."""
    uid, _token = await api_bersama.pengguna_baru()

    async def saran(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        await k.alat(
            "recommendation.create",
            {"domain": "habit", "title": "Tidur awal", "confidence": 0.6, "rationale": ["a"]},
        )
        return agents.Keputusan("Saran tersimpan.", Decimal("0.6"), ("a",), {"action": "recommend"})

    hasil = await runtime_uji(api_bersama, {"coach-agent": saran}).jalankan(
        uid, "coach-agent", "beri aku saran", pemicu="user"
    )

    assert _sql(
        api_bersama, "SELECT agent_run_id FROM recommendations WHERE user_id = %s", uid
    ) == [(hasil.run_id,)], "rekomendasi tidak terikat run yang membuatnya"


async def _rekomendasi_langsung(api: ApiUji, uid: UUID) -> None:
    await intelligence.buat_rekomendasi(
        api.app.state.engine,
        uid,
        agent_id=REGISTRI.agent["coach-agent"].id_katalog,
        agent_run_id=None,
        domain="keuangan",
        title="Kurangi jajan",
        body=None,
        confidence=Decimal("0.5"),
        rationale=["Belanja naik"],
    )


async def _ingat_langsung(api: ApiUji, uid: UUID) -> None:
    await memory.ingat(
        api.app.state.engine, uid, scope="location", isi="tinggal di Bandung", penulis="uji@1"
    )


@pytest.mark.parametrize(
    ("maksud", "tabel", "tulis"),
    [
        ("rekomendasi ber-domain 'keuangan'", "recommendations", _rekomendasi_langsung),
        ("memori ber-scope 'location'", "memories", _ingat_langsung),
    ],
    ids=["domain-rekomendasi", "scope-memori"],
)
async def test_layanan_tulis_menjaga_daftarnya_tanpa_skema_tool(
    api_bersama: ApiUji,
    maksud: str,
    tabel: str,
    tulis: Callable[[ApiUji, UUID], Awaitable[None]],
) -> None:
    """`enum` skema tool dan pagu manifest menjaga pemanggilan LEWAT AGENT. Layanan pemilik
    datanya juga dipanggil tanpa tool — mesin rekomendasi 5.5, ekstraksi — dan di sana hanya
    batasnya sendiri yang berlaku: domain spec/01, scope resmi spec/05."""
    uid, _token = await api_bersama.pengguna_baru()

    try:
        await tulis(api_bersama, uid)
    except ValueError:
        ditolak = True
    else:
        ditolak = False

    tersimpan = _sql(api_bersama, f"SELECT count(*) FROM {tabel} WHERE user_id = %s", uid)
    assert (ditolak, tersimpan) == (True, [(0,)]), f"{maksud} disimpan pemanggil langsung"
