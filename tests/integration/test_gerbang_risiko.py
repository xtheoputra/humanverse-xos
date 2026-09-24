"""spec/07 4.5 — *risk 2 minta izin sekali; risk 3 minta setiap kali*.

Gerbang sungguhan di atas mesin izin sungguhan (PostgreSQL + Redis), lewat runtime
yang sama dengan percakapan: run yang ditahan, jawaban pengguna, lalu giliran yang
diulang dengan persetujuannya. Tool V0 paling tinggi R2 — R3 dan R4 diuji dengan
registry yang menaikkan `habit.complete` (dan pagu agent yang memanggilnya, aturan 3 ·
K-14), lulus validator yang sama.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from decimal import Decimal
from importlib import resources
from typing import Any
from uuid import UUID

import pytest
import yaml
from _bantuan_agent import REGISTRI, gerbang_model_uji, run, sql
from _bantuan_db import ApiUji
from test_habits import buat_habit
from test_memori import _izin

from hvx.modules import agents, identity, platform

pytestmark = pytest.mark.integration

HABIT = identity.Subjek("agent", "habit-agent")
COACH = identity.Subjek("agent", "coach-agent")
HARI = "2026-09-20"


def _baca(sub: str) -> dict[str, dict[str, Any]]:
    akar = resources.files("hvx.modules.agents").joinpath(sub)
    return {
        b.name.removesuffix(".yaml"): yaml.safe_load(b.read_text(encoding="utf-8"))
        for b in akar.iterdir()
        if b.name.endswith(".yaml")
    }


def _registri_dengan_risiko(r: int) -> agents.RegistriAgent:
    """`habit.complete` ber-risiko `r` — lewat validator yang sama (aturan 3 · K-14)."""
    alat, manifest = copy.deepcopy(_baca("alat")), copy.deepcopy(_baca("manifest"))
    alat["habit.complete"]["risk_level"] = r
    alat["agent.habit"]["risk_level"] = r
    manifest["habit-agent"]["max_risk"] = f"R{r}"
    manifest["orchestrator-agent"]["max_risk"] = f"R{r}"
    return agents.validasi_registri(alat, manifest)


def _tanda(api: ApiUji, umur_s: int = agents.UMUR_TOKEN_S) -> agents.TokenKonfirmasi:
    s = api.app.state.settings
    return agents.TokenKonfirmasi(lambda isi: platform.sidik(s, "konfirmasi-agent", isi), umur_s)


def _tandai(pilih: Callable[[list[dict[str, Any]]], dict[str, Any]] = lambda d: d[0]) -> Any:
    async def program(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        daftar = await k.alat("habit.list", {})
        habit = pilih(daftar["items"])
        await k.alat(
            "habit.complete", {"habit_id": habit["id"], "for_date": HARI, "status": "done"}
        )
        return agents.Keputusan(
            f"{habit['title']} ditandai selesai.",
            Decimal("0.9"),
            ("Habit aktif yang judulnya cocok",),
            {"action": "habit.complete", "habit_id": habit["id"]},
        )

    return program


def _runtime(
    api: ApiUji, program: dict[str, Any], registri: agents.RegistriAgent = REGISTRI
) -> agents.RuntimeAgent:
    gerbang = agents.GerbangRisiko(api.app.state.engine, _izin(api), _tanda(api))
    return agents.RuntimeAgent(
        api.app.state.engine,
        registri,
        program,
        agents.PelaksanaAlat(registri, agents.IMPLEMENTASI, gerbang, None),
        gerbang_model_uji(),
    )


async def _ditahan(
    runtime: agents.RuntimeAgent, uid: UUID, agent: str = "habit-agent", **kw: Any
) -> agents.PermintaanKonfirmasi:
    try:
        await runtime.jalankan(uid, agent, "tandai", pemicu="user", **kw)
    except agents.AlatDitolak as galat:
        tertahan = galat
    else:
        raise AssertionError("gerbang tidak menahan — dijalankan tanpa bertanya")
    assert tertahan.konfirmasi is not None, f"ditolak ({tertahan.kode}), bukan ditahan"
    return tertahan.konfirmasi


def _selesai(api: ApiUji, uid: UUID) -> int:
    return sql(api, "SELECT count(*) FROM habit_completions WHERE user_id = %s", uid)[0][0]


async def _jawab(
    api: ApiUji, uid: UUID, p: agents.PermintaanKonfirmasi, jawaban: agents.JawabanKonfirmasi
) -> agents.PersetujuanAksi | None:
    return await agents.jawab_konfirmasi(
        api.app.state.engine, _izin(api), _tanda(api), uid, p.token, jawaban
    )


async def test_risk_2_minta_izin_sekali(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    runtime = _runtime(api_bersama, {"habit-agent": _tandai()})

    p = await _ditahan(runtime, uid)
    ditahan = run(api_bersama, p.run_id)
    assert (p.jenis, p.alat, p.risk_level, p.scopes) == ("izin", "habit.complete", 2, ("habits",))
    assert ditahan["status"] == "blocked"
    assert ditahan["decision"] == {
        "action": "awaiting_confirmation",
        "tool": "habit.complete",
        "agent": "habit-agent",
        "risk_level": 2,
        "jenis": "izin",
    }
    assert _selesai(api_bersama, uid) == 0, "tulisan R2 dijalankan sebelum diizinkan"

    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_selalu")
    diulang = await runtime.jalankan(
        uid, "habit-agent", "tandai", pemicu="user", persetujuan=frozenset({persetujuan})
    )
    berikutnya = await runtime.jalankan(uid, "habit-agent", "tandai", pemicu="user")

    assert run(api_bersama, p.run_id)["confirmed_by_user"] is True
    assert run(api_bersama, diulang.run_id)["confirmed_by_user"] is True
    assert _selesai(api_bersama, uid) == 1
    assert run(api_bersama, berikutnya.run_id)["status"] == "succeeded", (
        "izin R2 yang diingat ditanyakan lagi"
    )
    assert await _izin(api_bersama).cek(uid, HABIT, "habits", "write") == "allow"
    assert sql(
        api_bersama,
        "SELECT action, subject_id FROM audit_logs WHERE user_id = %s AND action LIKE 'agent.%%'",
        uid,
    ) == [("agent.action_approved", "habit.complete")], "jawaban pengguna tidak tercatat"


async def test_risk_2_izinkan_sekali_tidak_diingat(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    runtime = _runtime(api_bersama, {"habit-agent": _tandai()})

    p = await _ditahan(runtime, uid)
    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_sekali")
    await runtime.jalankan(
        uid, "habit-agent", "tandai", pemicu="user", persetujuan=frozenset({persetujuan})
    )
    lagi = await _ditahan(runtime, uid)

    assert _selesai(api_bersama, uid) == 1
    assert lagi.jenis == "izin", "izin sekali pakai ikut diingat"
    assert await _izin(api_bersama).cek(uid, HABIT, "habits", "write") == "ask"


async def test_risk_3_minta_setiap_kali(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    # Izin tersimpan `allow` tidak membuka R3 — konfirmasi manusia tetap wajib (H-15).
    await _izin(api_bersama).tetapkan(uid, HABIT, "habits", "write", "allow")
    runtime = _runtime(api_bersama, {"habit-agent": _tandai()}, _registri_dengan_risiko(3))

    p = await _ditahan(runtime, uid)
    with pytest.raises(agents.KonfirmasiTidakSah, match="tidak bisa diingat"):
        await _jawab(api_bersama, uid, p, "izinkan_selalu")
    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_sekali")
    diulang = await runtime.jalankan(
        uid, "habit-agent", "tandai", pemicu="user", persetujuan=frozenset({persetujuan})
    )
    lagi = await _ditahan(runtime, uid)

    assert (p.jenis, lagi.jenis) == ("konfirmasi", "konfirmasi"), "R3 tidak dikonfirmasi tiap kali"
    assert run(api_bersama, diulang.run_id)["confirmed_by_user"] is True, (
        "konfirmasi pengguna tidak tercatat di run"
    )
    assert _selesai(api_bersama, uid) == 1


async def test_deny_ditolak_dan_dicatat(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    await _izin(api_bersama).tetapkan(uid, HABIT, "habits", "write", "deny")
    ids: list[UUID] = []

    async def pencatat(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        return await _tandai()(k, pesan)

    runtime = _runtime(api_bersama, {"habit-agent": pencatat})
    with pytest.raises(agents.AlatDitolak) as galat:
        await runtime.jalankan(uid, "habit-agent", "tandai", pemicu="user")

    assert (galat.value.kode, galat.value.konfirmasi) == ("ditolak_pengguna", None)
    assert _selesai(api_bersama, uid) == 0
    r = run(api_bersama, ids[0])
    assert (r["status"], r["decision"]) == (
        "blocked",
        {"action": "denied", "tool": "habit.complete", "code": "ditolak_pengguna"},
    )
    assert sql(
        api_bersama,
        "SELECT action, actor_type, actor_id, subject_id, metadata->>'kode' FROM audit_logs "
        "WHERE user_id = %s AND action = 'agent.tool_denied'",
        uid,
    ) == [("agent.tool_denied", "agent", "habit-agent", "habit.complete", "ditolak_pengguna")], (
        "penolakan tidak tercatat"
    )


async def test_risk_4_ditolak_tanpa_bertanya(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    await _izin(api_bersama).tetapkan(uid, HABIT, "habits", "write", "allow")
    runtime = _runtime(api_bersama, {"habit-agent": _tandai()}, _registri_dengan_risiko(4))

    with pytest.raises(agents.AlatDitolak) as galat:
        await runtime.jalankan(uid, "habit-agent", "tandai", pemicu="user")

    assert (galat.value.kode, galat.value.konfirmasi) == ("risiko_terlarang", None), (
        "R4 bisa dikonfirmasi"
    )
    assert _selesai(api_bersama, uid) == 0


async def test_r0_jalan_tanpa_bertanya_kecuali_pengguna_minta_ditanya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    async def daftar_goal(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        g = await k.alat("goal.list", {})
        return agents.Keputusan(
            f"{len(g['items'])} goal.", Decimal("1"), ("Daftar goal",), {"action": "reply"}
        )

    runtime = _runtime(api_bersama, {"coach-agent": daftar_goal})
    await runtime.jalankan(uid, "coach-agent", "goal?", pemicu="user")
    await _izin(api_bersama).tetapkan(uid, COACH, "goals", "read", "ask")
    p = await _ditahan(runtime, uid, "coach-agent")

    assert (p.jenis, p.alat, p.risk_level) == ("izin", "goal.list", 0), (
        "“tanya aku” yang disetel pengguna dilewati untuk R0"
    )


async def test_persetujuan_tidak_berpindah_ke_pemanggilan_lain(api_bersama: ApiUji) -> None:
    """Disetujui: tandai habit A. Giliran yang diulang menandai habit B — ditanya lagi."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    await buat_habit(api_bersama, token)

    p = await _ditahan(_runtime(api_bersama, {"habit-agent": _tandai(lambda d: d[0])}), uid)
    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_sekali")
    lain = _runtime(api_bersama, {"habit-agent": _tandai(lambda d: d[1])})
    lagi = await _ditahan(lain, uid, persetujuan=frozenset({persetujuan}))

    assert lagi.sidik != p.sidik
    assert _selesai(api_bersama, uid) == 0, "persetujuan untuk habit A menandai habit B"


async def _satu_permintaan(api: ApiUji) -> tuple[UUID, agents.PermintaanKonfirmasi]:
    uid, token = await api.pengguna_baru()
    await buat_habit(api, token)
    return uid, await _ditahan(_runtime(api, {"habit-agent": _tandai()}), uid)


async def _ditolak_token(api: ApiUji, uid: UUID, token: str) -> str | None:
    """Pesan penolakan token — atau None bila token itu DITERIMA."""
    try:
        await _jawab_token(api, uid, token)
    except agents.KonfirmasiTidakSah as galat:
        return str(galat)
    return None


async def test_jawaban_sekali_pakai(api_bersama: ApiUji) -> None:
    uid, p = await _satu_permintaan(api_bersama)

    assert await _jawab(api_bersama, uid, p, "tolak") is None
    with pytest.raises(agents.KonfirmasiTerjawab):
        await _jawab(api_bersama, uid, p, "izinkan_sekali")

    assert run(api_bersama, p.run_id)["confirmed_by_user"] is False
    assert _selesai(api_bersama, uid) == 0


async def test_token_milik_pengguna_lain_ditolak(api_bersama: ApiUji) -> None:
    _uid, p = await _satu_permintaan(api_bersama)
    lain, _t = await api_bersama.pengguna_baru()

    pesan = await _ditolak_token(api_bersama, lain, p.token)

    assert pesan is not None, "pengguna lain menjawab permintaan konfirmasi orang lain"
    assert "pengguna lain" in pesan


async def test_token_yang_diubah_ditolak(api_bersama: ApiUji) -> None:
    uid, p = await _satu_permintaan(api_bersama)
    isi, tanda = p.token.split(".")
    rusak = tanda[:-1] + ("1" if tanda[-1] == "0" else "0")

    pesan = await _ditolak_token(api_bersama, uid, f"{isi}.{rusak}")

    assert pesan is not None, "token yang tanda tangannya diubah diterima"
    assert "rusak" in pesan


async def test_token_kedaluwarsa_ditolak(api_bersama: ApiUji) -> None:
    uid, p = await _satu_permintaan(api_bersama)
    basi = _tanda(api_bersama, umur_s=-1).buat(**_isi(p)).token

    pesan = await _ditolak_token(api_bersama, uid, basi)

    assert pesan is not None, "token kedaluwarsa diterima"
    assert "kedaluwarsa" in pesan


async def _jawab_token(api: ApiUji, uid: UUID, token: str) -> None:
    await agents.jawab_konfirmasi(
        api.app.state.engine, _izin(api), _tanda(api), uid, token, "tolak"
    )


def _isi(p: agents.PermintaanKonfirmasi) -> dict[str, Any]:
    return {
        "jenis": p.jenis,
        "user_id": p.user_id,
        "run_id": p.run_id,
        "agent": p.agent,
        "alat": p.alat,
        "risk_level": p.risk_level,
        "scopes": p.scopes,
        "aksi": p.aksi,
        "sidik": p.sidik,
    }


async def test_delegasi_tidak_ditanya_dua_kali(api_bersama: ApiUji) -> None:
    """Orchestrator → agent.habit (R2) → habit.complete (R2): SATU pertanyaan, di tulisannya."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)

    async def orkestrator(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        balasan = await k.alat("agent.habit", {"pesan": pesan})
        return agents.Keputusan(
            balasan["teks"],
            Decimal(str(balasan["confidence"])),
            tuple(balasan["rationale"]),
            {"action": "delegate", "agent": "habit-agent"},
        )

    runtime = _runtime(api_bersama, {"orchestrator-agent": orkestrator, "habit-agent": _tandai()})
    p = await _ditahan(runtime, uid, "orchestrator-agent")
    assert (p.agent, p.alat) == ("habit-agent", "habit.complete"), (
        f"delegasi ditanyakan sendiri: {p.agent} → {p.alat}"
    )
    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_sekali")
    hasil = await runtime.jalankan(
        uid, "orchestrator-agent", "tandai", pemicu="user", persetujuan=frozenset({persetujuan})
    )

    assert run(api_bersama, hasil.run_id)["status"] == "succeeded"
    anak = sql(
        api_bersama,
        "SELECT confirmed_by_user FROM agent_runs WHERE parent_run_id = %s",
        hasil.run_id,
    )
    assert anak == [(True,)], "persetujuan giliran tidak sampai ke run anak"
    assert _selesai(api_bersama, uid) == 1
