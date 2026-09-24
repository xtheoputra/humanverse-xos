"""spec/07 4.7 — `coach-agent` + `habit-agent` + `memory-agent`: *tiap balasan membawa
`confidence` + `rationale`*.

Program V0 sungguhan di belakang `orchestrator-agent` sungguhan, dengan gerbang risiko
sungguhan (mesin izin di PostgreSQL + Redis): yang dipakai percakapan (4.8) adalah
rakitan yang sama. Penyedia model uji merangkai bahan seperti penyedia lokal V0 —
jadi yang terbaca di balasan adalah persis fakta yang disiapkan agent.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from _bantuan_agent import REGISTRI, gerbang_model_uji, run, sql
from _bantuan_db import ApiUji, auth
from test_habits import buat_habit
from test_memori import _izin

from hvx.modules import agents, identity, platform

pytestmark = pytest.mark.integration

COACH = identity.Subjek("agent", "coach-agent")


def _hari_ini() -> str:
    """Pengguna uji tinggal di Asia/Jakarta (`ApiUji.pengguna_baru`)."""
    return datetime.now(ZoneInfo("Asia/Jakarta")).date().isoformat()


def _runtime(api: ApiUji) -> agents.RuntimeAgent:
    s = api.app.state.settings
    tanda = agents.TokenKonfirmasi(lambda isi: platform.sidik(s, "konfirmasi-agent", isi))
    gerbang = agents.GerbangRisiko(api.app.state.engine, _izin(api), tanda)
    return agents.RuntimeAgent(
        api.app.state.engine,
        REGISTRI,
        agents.PROGRAM_V0,
        agents.PelaksanaAlat(REGISTRI, agents.IMPLEMENTASI, gerbang, None),
        gerbang_model_uji(),
    )


async def _giliran(
    api: ApiUji, uid: UUID, pesan: str, *, izinkan: agents.JawabanKonfirmasi | None = None
) -> agents.HasilRun:
    """Satu giliran lewat orchestrator; bila ditahan gerbang dan `izinkan` diberikan,
    jawab lalu ulangi — persis alur percakapan."""
    runtime = _runtime(api)
    try:
        return await runtime.jalankan(uid, "orchestrator-agent", pesan, pemicu="user")
    except agents.AlatDitolak as galat:
        if izinkan is None or galat.konfirmasi is None:
            raise
        permintaan = galat.konfirmasi
    s = api.app.state.settings
    tanda = agents.TokenKonfirmasi(lambda isi: platform.sidik(s, "konfirmasi-agent", isi))
    setuju = await agents.jawab_konfirmasi(
        api.app.state.engine, _izin(api), tanda, uid, permintaan.token, izinkan
    )
    assert setuju is not None
    return await runtime.jalankan(
        uid, "orchestrator-agent", pesan, pemicu="user", persetujuan=frozenset({setuju})
    )


def _anak(api: ApiUji, akar: UUID) -> dict[str, Any]:
    (anak,) = sql(api, "SELECT id FROM agent_runs WHERE parent_run_id = %s", akar)
    return run(api, anak[0])


async def test_coach_menjawab_dari_data_pengguna_tanpa_catatan_bebasnya(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h, k = auth(token), api_bersama.klien
    hari = _hari_ini()
    await buat_habit(api_bersama, token, title="Lari pagi")
    await k.put(f"/v1/checkins/{hari}", json={"energy": 2, "note": "rahasia-checkin"}, headers=h)
    await k.post(
        "/v1/moods", json={"valence": 2, "label": "cemas", "note": "rahasia-mood"}, headers=h
    )
    await k.post("/v1/goals", json={"title": "Lari 10K", "domain": "health"}, headers=h)

    hasil = await _giliran(api_bersama, uid, "bagaimana hariku?")
    b = hasil.keputusan

    assert f"Check-in {hari}: energi 2/5." in b.teks
    assert "Habit “Lari pagi” hari ini: belum dicatat" in b.teks
    assert "1 goal aktif: “Lari 10K”." in b.teks
    assert "rahasia" not in f"{b.teks}{b.rationale}", "catatan bebas pengguna sampai ke balasan"
    assert b.confidence == agents.KEYAKINAN_SUMBER[4], "keyakinan tidak mengikuti datanya"
    assert f"Check-in {hari}: energi 2/5." in b.rationale, "alasan bukan fakta yang dipakai"
    assert _anak(api_bersama, hasil.run_id)["decision"] == {
        "action": "reply",
        "sumber": 4,
        "dilewati": 0,
    }


async def test_coach_tanpa_data_mengatakannya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    b = (await _giliran(api_bersama, uid, "bagaimana hariku?")).keputusan

    assert b.teks == platform.TANPA_DATA, "coach mengarang jawaban tanpa data (Pasal 8)"
    assert (b.confidence, b.rationale) == (
        agents.KEYAKINAN_SUMBER[0],
        ("Belum ada habit, check-in, mood, goal, atau ingatan yang tercatat.",),
    )


async def test_coach_melewati_sumber_yang_ditolak_dan_mengatakannya(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await api_bersama.klien.post("/v1/moods", json={"valence": 4}, headers=auth(token))
    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "deny")

    b = (await _giliran(api_bersama, uid, "bagaimana hariku?")).keputusan

    assert "Mood" not in b.teks, "mood yang ditolak pengguna tetap dibaca"
    assert b.rationale[-1] == "Tidak dibaca karena kamu menolak aksesnya: mood.", (
        "sumber yang dilewati tidak dinyatakan"
    )


async def test_habit_agent_menandai_setelah_izin_sekali(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    lain = await buat_habit(api_bersama, token, title="Meditasi")
    hari = _hari_ini()

    with pytest.raises(agents.AlatDitolak) as galat:
        await _giliran(api_bersama, uid, "tandai lari pagi selesai")
    selesai = await _giliran(api_bersama, uid, "tandai lari pagi selesai", izinkan="izinkan_selalu")
    lewati = await _giliran(api_bersama, uid, "lewati meditasi")  # izin sudah diingat

    assert galat.value.kode == "perlu_izin"
    assert selesai.keputusan.teks == f"“Lari pagi” ditandai selesai untuk {hari}."
    assert selesai.keputusan.confidence == agents.KEYAKINAN_JUDUL_PERSIS, (
        "keyakinan tidak membedakan judul yang cocok persis"
    )
    assert lewati.keputusan.teks == f"“Meditasi” ditandai dilewati untuk {hari}.", (
        "“lewati” tidak dicatat sebagai dilewati"
    )
    assert sql(
        api_bersama,
        "SELECT habit_id::text, for_date::text, status FROM habit_completions "
        "WHERE user_id = %s ORDER BY status",
        uid,
    ) == [(habit["id"], hari, "done"), (lain["id"], hari, "skipped")], (
        "habit tidak ditandai pada tanggal lokal pengguna"
    )
    assert _anak(api_bersama, lewati.run_id)["decision"] == {
        "action": "habit.complete",
        "habit_id": lain["id"],
        "status": "skipped",
    }


async def test_habit_agent_tidak_mengaku_mengubah_yang_sudah_tercatat(api_bersama: ApiUji) -> None:
    """Tanggal yang sudah tercatat tidak diubah domain (spec/04) — balasannya mengatakannya,
    dan tidak ada izin yang ditanyakan untuk tulisan yang tidak akan terjadi."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    hari = _hari_ini()
    await api_bersama.klien.post(
        f"/v1/habits/{habit['id']}/completions",
        json={"for_date": hari, "status": "done"},
        headers=auth(token),
    )

    hasil = await _giliran(api_bersama, uid, "lewati lari pagi")  # tanpa izin tersimpan

    assert (
        hasil.keputusan.teks == f"“Lari pagi” sudah tercatat selesai untuk {hari} — tidak diubah."
    ), "habit agent mengaku mengubah catatan yang tidak berubah"
    assert _anak(api_bersama, hasil.run_id)["decision"]["action"] == "already_recorded"


@pytest.mark.parametrize(
    ("pesan", "aksi"),
    [("tandai lari selesai", "clarify"), ("tandai yoga selesai", "not_found")],
)
async def test_habit_agent_tidak_menebak(api_bersama: ApiUji, pesan: str, aksi: str) -> None:
    """Dua habit cocok, atau tidak satu pun: bertanya — tidak menulis, tidak minta izin."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token, title="Lari pagi")
    await buat_habit(api_bersama, token, title="Lari sore")

    hasil = await _giliran(api_bersama, uid, pesan)

    assert _anak(api_bersama, hasil.run_id)["decision"]["action"] == aksi, (
        f"“{pesan}” tidak dijawab dengan {aksi}"
    )
    assert sql(api_bersama, "SELECT count(*) FROM habit_completions WHERE user_id = %s", uid) == [
        (0,)
    ], "habit agent menebak lalu menulis"


async def test_memory_agent_mengingat_hanya_bila_belum_diingat(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    pertama = await _giliran(
        api_bersama, uid, "ingat bahwa aku alergi kacang", izinkan="izinkan_selalu"
    )
    kedua = await _giliran(api_bersama, uid, "ingat bahwa aku alergi kacang")

    assert pertama.keputusan.teks == "Baik, akan kuingat."
    assert kedua.keputusan.teks == "Itu sudah kuingat.", "memory-agent mengaku mengingat lagi"
    assert _anak(api_bersama, kedua.run_id)["decision"]["action"] == "already_remembered"
    assert sql(api_bersama, "SELECT scope, content FROM memories WHERE user_id = %s", uid) == [
        ("coaching_notes", "aku alergi kacang")
    ], "memory-agent mengingat dua kali"


async def test_memory_agent_tanpa_ingatan_mengatakannya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    b = (await _giliran(api_bersama, uid, "apa yang kamu ingat tentang kacang?")).keputusan

    assert (b.teks, b.confidence, b.rationale) == (
        platform.TANPA_DATA,
        agents.KEYAKINAN_INGATAN[0],
        ("0 ingatan yang cocok.",),
    )


@pytest.mark.parametrize(
    "pesan",
    [
        "halo",
        "kenapa aku capek terus minggu ini?",
        "tandai",
        "tandai yoga selesai",
        "apa yang kamu tahu",
        "ingat",
    ],
)
async def test_tiap_balasan_membawa_keyakinan_dan_alasan(api_bersama: ApiUji, pesan: str) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    b = (await _giliran(api_bersama, uid, pesan)).keputusan

    assert Decimal(0) <= b.confidence <= Decimal(1)
    assert b.rationale, f"balasan “{pesan}” tanpa alasan"
    assert all(a.strip() for a in b.rationale)


async def test_coach_bertanya_bila_pengguna_minta_ditanya(api_bersama: ApiUji) -> None:
    """`deny` melewati sumbernya; `ask` yang DISETEL pengguna tidak dilewati — ditanyakan."""
    uid, _token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, COACH, "habits", "read", "ask")

    with pytest.raises(agents.AlatDitolak) as galat:
        await _giliran(api_bersama, uid, "bagaimana hariku?")

    assert (galat.value.kode, galat.value.alat) == ("perlu_izin", "habit.list"), (
        "“tanya aku” pengguna dilewati coach"
    )


async def test_coach_tidak_tertahan_scope_ingatan_yang_belum_diputuskan(
    api_bersama: ApiUji,
) -> None:
    """E-193 — `memory.search` menyaring izin per scope sendiri (3.7). Gerbang yang ikut
    menanyakan tiap scope-nya menahan SETIAP jawaban coach pada `journal_raw` (sensitif,
    tidak pernah `allow` karena bawaan) — scope yang bahkan tidak diminta coach."""
    uid, _token = await api_bersama.pengguna_baru()
    # coaching_notes hanya dibaca coach LEWAT memory.search — `ask` di sini menyisihkan
    # scope itu dari hasil pencarian, bukan menahan jawabannya.
    await _izin(api_bersama).tetapkan(uid, COACH, "coaching_notes", "read", "ask")

    hasil = await _giliran(api_bersama, uid, "halo")

    assert run(api_bersama, _anak(api_bersama, hasil.run_id)["id"])["status"] == "succeeded"


async def test_habit_agent_jujur_bila_tanggalnya_tercatat_bersamaan(api_bersama: ApiUji) -> None:
    """Daftar habit dibaca kosong, lalu perangkat lain mencatat tanggal yang sama sebelum
    tulisan agent: tulisan itu mengembalikan baris LAMA — balasannya tidak boleh mengaku."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token, title="Lari pagi")
    hari = _hari_ini()
    await _izin(api_bersama).tetapkan(
        uid, identity.Subjek("agent", "habit-agent"), "habits", "write", "allow"
    )
    daftar_asli = agents.IMPLEMENTASI["habit.list"]

    async def daftar_basi(k: Any, m: dict[str, Any]) -> dict[str, Any]:
        hasil = await daftar_asli(k, m)
        await api_bersama.klien.post(  # perangkat lain, di antara membaca dan menulis
            f"/v1/habits/{habit['id']}/completions",
            json={"for_date": hari, "status": "done"},
            headers=auth(token),
        )
        return hasil

    runtime = _runtime(api_bersama)
    runtime.pelaksana = agents.PelaksanaAlat(
        REGISTRI,
        {**agents.IMPLEMENTASI, "habit.list": daftar_basi},
        runtime.pelaksana._gerbang,  # gerbang sungguhan yang sama
        None,
    )
    hasil = await runtime.jalankan(uid, "orchestrator-agent", "lewati lari pagi", pemicu="user")

    assert (
        hasil.keputusan.teks == f"“Lari pagi” sudah tercatat selesai untuk {hari} — tidak diubah."
    ), "habit agent mengaku melewati habit yang tercatat selesai"


def test_tiap_agent_aktif_punya_program() -> None:
    assert sorted(agents.PROGRAM_V0) == sorted(REGISTRI.agent), "agent aktif tanpa program"
