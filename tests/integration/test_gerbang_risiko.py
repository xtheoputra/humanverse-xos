"""spec/07 4.5 — *risk 2 minta izin sekali; risk 3 minta setiap kali*.

Gerbang sungguhan di atas mesin izin sungguhan (PostgreSQL + Redis), lewat runtime
yang sama dengan percakapan: run yang ditahan, jawaban pengguna, lalu giliran yang
diulang dengan persetujuannya. Tool V0 paling tinggi R2 — R3 dan R4 diuji dengan
registry yang menaikkan `habit.complete` (dan pagu agent yang memanggilnya, aturan 3 ·
K-14), lulus validator yang sama.
"""

from __future__ import annotations

import copy
import time
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
MEMORY = identity.Subjek("agent", "memory-agent")
ORKESTRATOR = identity.Subjek("agent", "orchestrator-agent")
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
    return await agents.jawab_konfirmasi(_izin(api), _tanda(api), uid, p.token, jawaban)


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
        "kind": "permission",
    }, f"decision run yang ditahan: {ditahan['decision']}"
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
        "SELECT action, subject_id FROM audit_logs WHERE user_id = %s AND action LIKE 'agent.%%'"
        " ORDER BY id",
        uid,
    ) == [
        ("agent.action_approved", "habit.complete"),
        ("agent.tool_executed", "habit.complete"),  # tulisan agent berjejak (E-205)
    ], "jawaban pengguna atau tulisan agent tidak tercatat"


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
    # R4 adalah penolakan GERBANG — run `blocked`, dan percakapan membalas *“Tidak
    # dijalankan”*; run `failed` membuat percakapan mengirim `error` (percakapan.py).
    assert sql(api_bersama, "SELECT status, decision FROM agent_runs WHERE user_id = %s", uid) == [
        ("blocked", {"action": "denied", "tool": "habit.complete", "code": "risiko_terlarang"})
    ], "R4 tercatat sebagai kegagalan, bukan penolakan gerbang"


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
    assert sql(
        api_bersama,
        "SELECT action, subject_id FROM audit_logs WHERE user_id = %s AND action LIKE 'agent.%%'",
        uid,
    ) == [("agent.action_rejected", "habit.complete")], (
        "penolakan pengguna tercatat sebagai persetujuan — jejak audit bohong"
    )


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
    await agents.jawab_konfirmasi(_izin(api), _tanda(api), uid, token, "tolak")


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


@pytest.mark.parametrize("risiko", [2, 3])
async def test_delegasi_tidak_ditanya_dua_kali(api_bersama: ApiUji, risiko: int) -> None:
    """Orchestrator → agent.habit (R) → habit.complete (R): SATU pertanyaan, di tulisannya —
    juga di R3: delegasi tidak dikonfirmasi sendiri, konfirmasinya milik tulisan itu (E-192).

    Pertanyaannya menunjuk run ANAK yang ditahan — satu-satunya yang menyimpan jawabannya
    (`confirmed_by_user`); run induk hanya ikut berhenti."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    registri = REGISTRI if risiko == 2 else _registri_dengan_risiko(risiko)

    async def orkestrator(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        balasan = await k.alat("agent.habit", {"pesan": pesan})
        return agents.Keputusan(
            balasan["teks"],
            Decimal(str(balasan["confidence"])),
            tuple(balasan["rationale"]),
            {"action": "delegate", "agent": "habit-agent"},
        )

    runtime = _runtime(
        api_bersama, {"orchestrator-agent": orkestrator, "habit-agent": _tandai()}, registri
    )
    p = await _ditahan(runtime, uid, "orchestrator-agent")
    assert (p.agent, p.alat) == ("habit-agent", "habit.complete"), (
        f"delegasi ditanyakan sendiri: {p.agent} → {p.alat}"
    )
    (ditahan,) = _anak(api_bersama, uid)
    assert p.run_id == ditahan[0], "permintaan menunjuk run induk, bukan run anak yang DITAHAN"
    persetujuan = await _jawab(api_bersama, uid, p, "izinkan_sekali")
    assert run(api_bersama, ditahan[0])["confirmed_by_user"] is True, (
        "run anak yang ditahan tidak tercatat dijawab"
    )
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


async def test_izin_selalu_disimpan_bersama_jawabannya_atau_tidak_sama_sekali(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dulu jawaban dicatat dan di-commit LEBIH DULU, izinnya disimpan sesudahnya: izin
    yang gagal disimpan meninggalkan token terpakai tanpa izin — jawaban kedua `409`, dan
    pengguna ditanya lagi di giliran berikutnya. Kini satu transaksi (`MesinIzin.ubah`)."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    p = await _ditahan(_runtime(api_bersama, {"habit-agent": _tandai()}), uid)

    async def gagal(*_a: Any, **_k: Any) -> None:
        raise RuntimeError("izin gagal disimpan")

    monkeypatch.setattr(identity.UbahanIzin, "tetapkan", gagal)
    with pytest.raises(RuntimeError, match="izin gagal disimpan"):
        await _jawab(api_bersama, uid, p, "izinkan_selalu")
    monkeypatch.undo()

    assert run(api_bersama, p.run_id)["confirmed_by_user"] is None, "jawaban tercatat tanpa izin"
    assert sql(
        api_bersama,
        "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action LIKE 'agent.%%'",
        uid,
    ) == [(0,)]
    assert await _jawab(api_bersama, uid, p, "izinkan_selalu") is not None, (
        "jawaban yang gagal tidak bisa diulang"
    )
    assert await _izin(api_bersama).cek(uid, HABIT, "habits", "write") == "allow"


# ── Tinjauan penegak buta Sprint 4: janji gerbang yang dulu tidak dijaga uji mana pun ──


async def _coba(
    runtime: agents.RuntimeAgent, uid: UUID, agent: str, pesan: str, **kw: Any
) -> agents.HasilRun | agents.AlatDitolak:
    """Hasil satu giliran — atau penolakan/penahanan gerbangnya, sebagai nilai."""
    try:
        return await runtime.jalankan(uid, agent, pesan, pemicu="user", **kw)
    except agents.AlatDitolak as galat:
        return galat


def _ringkas(h: agents.HasilRun | agents.AlatDitolak) -> tuple[str, str | None, bool] | str:
    """`(kode, tool, ditahan?)` sebuah penolakan gerbang — atau `"dijalankan"`."""
    if isinstance(h, agents.HasilRun):
        return "dijalankan"
    return (h.kode, h.alat, h.konfirmasi is not None)


def _permintaan(h: agents.HasilRun | agents.AlatDitolak) -> agents.PermintaanKonfirmasi:
    assert isinstance(h, agents.AlatDitolak), "gerbang tidak menahan — dijalankan tanpa bertanya"
    assert h.konfirmasi is not None, f"ditolak ({h.kode}), bukan ditahan"
    return h.konfirmasi


async def _penjawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    """coach-agent tiruan tanpa tool — yang diuji di sini gerbang DELEGASINYA."""
    return agents.Keputusan("dijawab coach", Decimal("0.5"), ("alasan coach",), {"action": "reply"})


def _delegasi(api: ApiUji) -> agents.RuntimeAgent:
    """`orchestrator-agent` sungguhan: *“bagaimana hariku?”* → `agent.coach` (lima scope),
    *“tandai lari selesai”* → `agent.habit`."""
    return _runtime(
        api,
        {
            "orchestrator-agent": agents.orkestrator,
            "coach-agent": _penjawab,
            "habit-agent": _tandai(),
        },
    )


def _anak(api: ApiUji, uid: UUID) -> list[tuple[Any, ...]]:
    """Run anak (`parent_run_id` terisi) milik pengguna — `(id, confirmed_by_user)`."""
    return sql(
        api,
        "SELECT id, confirmed_by_user FROM agent_runs"
        " WHERE user_id = %s AND parent_run_id IS NOT NULL",
        uid,
    )


async def test_deny_mendahului_konfirmasi_r3(api_bersama: ApiUji) -> None:
    """spec/05 gerbang V0 (2): `deny` ditolak & dicatat SEBELUM konfirmasi R3. Aksi yang
    pengguna larang tidak boleh berubah menjadi pertanyaan — tombol *izinkan* di layar
    konfirmasi membukanya kembali dengan satu ketukan."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    await _izin(api_bersama).tetapkan(uid, HABIT, "habits", "write", "deny")
    runtime = _runtime(api_bersama, {"habit-agent": _tandai()}, _registri_dengan_risiko(3))

    hasil = await _coba(runtime, uid, "habit-agent", "tandai")

    assert _ringkas(hasil) == ("ditolak_pengguna", "habit.complete", False), (
        f"deny pengguna atas R3 ditanyakan sebagai konfirmasi: {_ringkas(hasil)}"
    )
    assert sql(
        api_bersama,
        "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action = 'agent.tool_denied'",
        uid,
    ) == [(1,)]
    assert _selesai(api_bersama, uid) == 0


async def test_deny_di_scope_mana_pun_menolak_delegasi(api_bersama: ApiUji) -> None:
    """`agent.coach` menyentuh lima scope; `deny` pengguna di scope KEEMPAT (`mood`) menolak
    delegasinya — bukan hanya keputusan scope pertama yang dibaca (spec/05 gerbang V0 (2))."""
    uid, _token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, ORKESTRATOR, "mood", "execute", "deny")

    hasil = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "bagaimana hariku?")

    assert _ringkas(hasil) == ("ditolak_pengguna", "agent.coach", False), (
        f"deny pengguna di scope selain yang pertama diabaikan: {_ringkas(hasil)}"
    )
    assert _anak(api_bersama, uid) == [], "agent yang delegasinya ditolak tetap dijalankan"


async def test_tanya_aku_di_scope_mana_pun_menahan_delegasi(api_bersama: ApiUji) -> None:
    """*“Tanya aku”* pengguna di scope KEDUA (`goals`) delegasi ke coach menahannya."""
    uid, _token = await api_bersama.pengguna_baru()
    await _izin(api_bersama).tetapkan(uid, ORKESTRATOR, "goals", "execute", "ask")

    hasil = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "bagaimana hariku?")

    assert _ringkas(hasil) == ("perlu_izin", "agent.coach", True), (
        f"ask pengguna di scope selain yang pertama dilewati: {_ringkas(hasil)}"
    )
    assert _anak(api_bersama, uid) == []


async def test_izinkan_selalu_mengingat_seluruh_scope_permintaan(api_bersama: ApiUji) -> None:
    """Satu jawaban *izinkan selalu* atas permintaan lima scope = lima izin tersimpan; yang
    hanya menyimpan sebagian menanyakan hal yang sama lagi di giliran berikutnya."""
    uid, _token = await api_bersama.pengguna_baru()
    izin = _izin(api_bersama)
    for scope in ("goals", "mood"):
        await izin.tetapkan(uid, ORKESTRATOR, scope, "execute", "ask")
    runtime = _delegasi(api_bersama)

    p = _permintaan(await _coba(runtime, uid, "orchestrator-agent", "bagaimana hariku?"))
    await _jawab(api_bersama, uid, p, "izinkan_selalu")
    berikutnya = await _coba(runtime, uid, "orchestrator-agent", "bagaimana hariku?")
    tersimpan = [await izin.cek(uid, ORKESTRATOR, s, "execute") for s in p.scopes]

    assert _ringkas(berikutnya) == "dijalankan", (
        "izinkan_selalu hanya mengingat sebagian scope permintaan — ditanya lagi: "
        f"{_ringkas(berikutnya)}"
    )
    assert tersimpan == ["allow"] * 5, f"izin yang diingat per scope: {tersimpan}"


async def test_permintaan_izin_hanya_scope_pemanggilannya(api_bersama: ApiUji) -> None:
    """E-195: `memory.write` ke `coaching_notes` menanyakan `coaching_notes` — bukan kelima
    scope tool itu. Izin yang diingat dari jawabannya tidak melebar ke `habits` tanpa
    pernah dilihat pengguna."""
    uid, _token = await api_bersama.pengguna_baru()
    runtime = _runtime(api_bersama, {"memory-agent": agents.PROGRAM_V0["memory-agent"]})

    p = _permintaan(await _coba(runtime, uid, "memory-agent", "ingat bahwa aku alergi kacang"))
    await _jawab(api_bersama, uid, p, "izinkan_selalu")

    assert (p.alat, p.scopes) == ("memory.write", ("coaching_notes",)), (
        f"permintaan izin memuat scope yang tidak disentuh pemanggilannya: {p.scopes}"
    )
    assert await _izin(api_bersama).cek(uid, MEMORY, "habits", "write") == "ask"


async def test_r1_yang_belum_diputuskan_jalan_tanpa_bertanya(api_bersama: ApiUji) -> None:
    """Tabel bawaan spec/05: R1 = `allow` bila pengguna belum memutuskan — coach menyimpan
    rekomendasinya (`recommendation.create`, satu-satunya tool R1) tanpa bertanya."""
    uid, _token = await api_bersama.pengguna_baru()

    async def sarankan(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        await k.alat(
            "recommendation.create",
            {"domain": "habit", "title": "Tidur lebih awal", "confidence": 0.6,
             "rationale": ["Tidur rata-rata 5 jam"]},
        )  # fmt: skip
        return agents.Keputusan("Disarankan.", Decimal("0.6"), ("Tidur",), {"action": "reply"})

    hasil = await _coba(_runtime(api_bersama, {"coach-agent": sarankan}), uid, "coach-agent", "?")

    assert _ringkas(hasil) == "dijalankan", (
        f"R1 yang belum diputuskan pengguna ditanyakan: {_ringkas(hasil)}"
    )
    assert sql(api_bersama, "SELECT count(*) FROM recommendations WHERE user_id = %s", uid) == [
        (1,)
    ]


async def test_persetujuan_terikat_agentnya(api_bersama: ApiUji) -> None:
    """4.5: persetujuan = agent + tool + sidik masukan. Persetujuan milik coach-agent atas
    tool dan masukan yang SAMA tidak meloloskan habit-agent."""
    uid, p = await _satu_permintaan(api_bersama)
    milik_lain = agents.PersetujuanAksi("coach-agent", p.alat, p.sidik)

    hasil = await _coba(
        _runtime(api_bersama, {"habit-agent": _tandai()}),
        uid,
        "habit-agent",
        "tandai",
        persetujuan=frozenset({milik_lain}),
    )

    assert _ringkas(hasil) == ("perlu_izin", "habit.complete", True), (
        f"persetujuan untuk agent lain meloloskan pemanggilan ini: {_ringkas(hasil)}"
    )
    assert _selesai(api_bersama, uid) == 0


async def test_delegasi_ditanyakan_sebagai_izin_execute(api_bersama: ApiUji) -> None:
    """`AKSI_IZIN`: delegasi (`kind: agent`) = `execute`. *Jangan biarkan orchestrator
    menyerahkan ke habit-agent* adalah `deny` `execute` — dan itu yang ditanyakan gerbang;
    `deny` `read` bukan larangan menyerahkan."""
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token, title="Lari")
    izin = _izin(api_bersama)
    await izin.tetapkan(uid, ORKESTRATOR, "habits", "read", "deny")
    await izin.tetapkan(uid, HABIT, "habits", "write", "allow")

    boleh = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "tandai lari selesai")
    await izin.tetapkan(uid, ORKESTRATOR, "habits", "execute", "deny")
    dilarang = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "tandai lari selesai")

    assert _ringkas(boleh) == "dijalankan", (
        f"deny read menghalangi delegasi — aksi delegasi bukan execute: {_ringkas(boleh)}"
    )
    assert _ringkas(dilarang) == ("ditolak_pengguna", "agent.habit", False), (
        f"deny execute pengguna atas delegasi tidak berlaku: {_ringkas(dilarang)}"
    )


async def test_token_konfirmasi_berumur_15_menit(api_bersama: ApiUji) -> None:
    """Lebih lama dari itu, pengguna menjawab keadaan yang sudah lewat. Diperiksa pada
    penanda yang DIRAKIT aplikasi (`hvx.main`), bukan pada konstantanya."""
    _uid, p = await _satu_permintaan(api_bersama)

    dirakit = api_bersama.app.state.percakapan._tanda.buat(**_isi(p))
    sisa = dirakit.kedaluwarsa - time.time()

    assert 14 * 60 < sisa <= 15 * 60, f"token konfirmasi berumur {sisa:.0f} dtk, bukan 15 menit"


# ── C-32 (K-46) · E-227: `mood` sensitif — yang MEMBACA ditanya, delegasinya tidak ──


async def _baca_mood(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    """coach-agent tiruan yang hanya membaca mood (`mood.recent`, R0)."""
    await k.alat("mood.recent", {"hari": 7})
    return agents.Keputusan("mood dibaca", Decimal("0.5"), ("mood",), {"action": "reply"})


async def test_coach_ditanya_sebelum_membaca_mood_walau_risk_0(api_bersama: ApiUji) -> None:
    """C-32: mood = data kesehatan jiwa (GDPR Art. 9, UU PDP Pasal 4(2)) — R0 tidak lagi
    membukanya karena bawaan; hanya `allow` yang disimpan pengguna."""
    uid, _token = await api_bersama.pengguna_baru()
    runtime = _runtime(api_bersama, {"coach-agent": _baca_mood})

    belum = await _coba(runtime, uid, "coach-agent", "?")
    assert _ringkas(belum) == ("perlu_izin", "mood.recent", True), (
        f"coach membaca mood tanpa izin tersimpan (C-32): {_ringkas(belum)}"
    )
    assert _permintaan(belum).scopes == ("mood",)

    await _izin(api_bersama).tetapkan(uid, COACH, "mood", "read", "allow")
    assert _ringkas(await _coba(runtime, uid, "coach-agent", "?")) == "dijalankan"


async def test_delegasi_ke_coach_tidak_ditanya_untuk_mood(api_bersama: ApiUji) -> None:
    """E-227: delegasi tidak membaca mood — memaksanya `ask` membuat tiap giliran orkestrator
    ditahan, lalu tool coach di dalamnya ditanya LAGI. Keputusan yang DISIMPAN pengguna atas
    delegasinya tetap menang."""
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "bagaimana hariku?")
    assert _ringkas(hasil) == "dijalankan", (
        f"delegasi ke coach ditahan untuk scope sensitif yang tidak dibacanya: {_ringkas(hasil)}"
    )

    await _izin(api_bersama).tetapkan(uid, ORKESTRATOR, "mood", "execute", "ask")
    ditahan = await _coba(_delegasi(api_bersama), uid, "orchestrator-agent", "bagaimana hariku?")
    assert _ringkas(ditahan) == ("perlu_izin", "agent.coach", True), (
        "“tanya aku” yang disimpan pengguna atas delegasi diabaikan"
    )
