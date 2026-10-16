"""spec/07 4.4 — *tiap run mencatat tools, scope, decision, confidence, cost*.

Baris `agent_runs` dibaca sebagai pemilik tabel sesudah run selesai — yang diuji
adalah yang TERSIMPAN, termasuk untuk run yang gagal, ditahan gerbang, atau
dibatalkan di tengah aliran model: jejak audit yang hanya ada untuk run yang
berhasil tidak menjawab pertanyaan audit mana pun.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

import pytest
from _bantuan_agent import (
    HARGA_BESAR,
    REGISTRI,
    PenyediaUji,
    gerbang_model_uji,
    run,
    runtime_uji,
)
from _bantuan_db import ApiUji
from test_habits import buat_habit

from hvx.modules import agents, platform

pytestmark = pytest.mark.integration

COACH = REGISTRI.agent["coach-agent"]


async def _coach(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    daftar = await k.alat("habit.list", {"for_date": "2026-09-20"})
    await k.alat("checkin.get", {"for_date": "2026-09-20"})
    jawaban = await k.model(
        tugas="jawab", pertanyaan=pesan, bahan=[f"{len(daftar['items'])} habit aktif hari ini"]
    )
    return agents.Keputusan(
        jawaban.teks,
        Decimal("0.7"),
        ("Daftar habit 2026-09-20",),
        {"action": "reply", "habits": len(daftar["items"])},
    )


async def test_run_mencatat_tools_scope_decision_confidence_cost(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await buat_habit(api_bersama, token)
    peristiwa: list[tuple[str, dict[str, Any]]] = []

    async def pendengar(jenis: str, data: Any) -> None:
        peristiwa.append((jenis, dict(data)))

    hasil = await runtime_uji(api_bersama, {"coach-agent": _coach}).jalankan(
        uid, "coach-agent", "bagaimana hariku?", pemicu="user", pendengar=pendengar
    )
    r = run(api_bersama, hasil.run_id)

    # Token = kata: 1 tugas + 2 pertanyaan + 5 bahan masuk, 5 keluar — harga model besar
    # (coach-agent `model.class: reasoning`).
    biaya = HARGA_BESAR.biaya(1 + 2 + 5, 5)
    assert (r["status"], r["trigger"], r["parent_run_id"]) == ("succeeded", "user", None)
    assert (r["agent_id"], r["agent_version"]) == (COACH.id_katalog, COACH.version)
    assert r["tools_used"] == ["habit.list", "checkin.get"], "tool yang dipakai tidak tercatat"
    assert r["memory_scopes"] == ["checkins", "habits"], "scope yang disentuh tidak tercatat"
    assert r["decision"] == {"action": "reply", "habits": 1}, "keputusan tidak tercatat"
    assert r["confidence"] == Decimal("0.700"), "keyakinan tidak tercatat"
    assert (r["model_used"], r["tokens_in"], r["tokens_out"]) == ("uji/besar", 8, 5), (
        "model tidak tercatat"
    )
    assert r["cost_usd"] == biaya == hasil.biaya_usd > 0, "biaya tidak tercatat"
    assert (r["risk_level"], r["confirmed_by_user"], r["error"]) == (0, None, None)
    assert r["finished_at"] >= r["started_at"]
    assert r["latency_ms"] >= 0
    alat = [d for jenis, d in peristiwa if jenis == "tool_call"]
    assert alat == [
        {"tool": "habit.list", "agent": "coach-agent"},
        {"tool": "checkin.get", "agent": "coach-agent"},
    ], "peristiwa tool_call tidak mengalir"
    token = "".join(d["text"] for jenis, d in peristiwa if jenis == "token")
    assert token == hasil.keputusan.teks, "token tidak mengalir"


async def test_run_yang_gagal_tetap_ditutup_tanpa_isi_galat(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    ids: list[Any] = []

    async def rusak(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        await k.alat("goal.list", {})
        raise RuntimeError(f"galat yang mengutip pesan pengguna: {pesan}")

    with pytest.raises(RuntimeError):
        await runtime_uji(api_bersama, {"coach-agent": rusak}).jalankan(
            uid, "coach-agent", "rahasia-pengguna", pemicu="user"
        )
    r = run(api_bersama, ids[0])

    assert r["status"] == "failed", "run yang gagal dibiarkan `running`"
    assert "rahasia" not in str(r), "isi galat — dan pesan pengguna — masuk jejak audit"
    assert r["error"] == {"code": "internal", "type": "RuntimeError"}
    assert r["tools_used"] == ["goal.list"]
    assert r["finished_at"] is not None


async def test_keputusan_tanpa_alasan_menggagalkan_run(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    ids: list[Any] = []

    async def tanpa_alasan(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        return agents.Keputusan("Jawaban tanpa dasar.", Decimal("0.9"), (), {"action": "reply"})

    with pytest.raises(agents.KeputusanTidakSah):
        await runtime_uji(api_bersama, {"coach-agent": tanpa_alasan}).jalankan(
            uid, "coach-agent", "halo", pemicu="user"
        )

    r = run(api_bersama, ids[0])
    assert (r["status"], r["error"]["code"]) == ("failed", "keputusan_tidak_sah"), (
        "balasan tanpa alasan tercatat berhasil"
    )
    assert (r["confidence"], r["decision"]) == (None, {"action": "failed"})


class _GerbangMenahan:
    async def periksa(self, j: agents.Jalannya, alat: agents.Alat, m: Any) -> None:
        raise agents.AlatDitolak("perlu_izin", f"{alat.name} menunggu izin pengguna")


async def test_run_yang_ditahan_gerbang_blocked_bukan_failed(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    ids: list[Any] = []

    async def tandai(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        await k.alat("habit.list", {})
        raise AssertionError("gerbang tidak menahan")

    with pytest.raises(agents.AlatDitolak):
        await runtime_uji(api_bersama, {"habit-agent": tandai}, gerbang=_GerbangMenahan()).jalankan(
            uid, "habit-agent", "tandai lari", pemicu="user"
        )

    r = run(api_bersama, ids[0])
    assert r["status"] == "blocked", "run yang menunggu manusia tercatat sebagai kegagalan"
    assert r["error"] == {"code": "perlu_izin", "type": "AlatDitolak"}
    assert r["tools_used"] == [], "tool yang ditahan gerbang tercatat sebagai dipakai"


async def test_run_yang_dibatalkan_di_tengah_aliran_tetap_ditutup_dan_dibayar(
    api_bersama: ApiUji,
) -> None:
    """Api berhenti di tengah jawaban (giliran dibatalkan): run ditutup `cancelled`, token
    yang sudah keluar tetap tercatat — sudah dibayar, dan tetap dihitung anggaran (4.9)."""
    uid, _token = await api_bersama.pengguna_baru()
    penyedia = PenyediaUji(jeda_s=0.5)
    ids: list[Any] = []

    async def lambat(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        await k.alat("goal.list", {})
        await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu dua tiga empat lima enam"])
        raise AssertionError("aliran tidak terputus")

    runtime = runtime_uji(
        api_bersama, {"coach-agent": lambat}, gerbang_model=gerbang_model_uji(penyedia)
    )
    tugas = asyncio.create_task(runtime.jalankan(uid, "coach-agent", "halo", pemicu="user"))
    await asyncio.wait_for(penyedia.token_keluar.wait(), timeout=10)
    tugas.cancel()
    with pytest.raises(asyncio.CancelledError):
        await tugas

    r = run(api_bersama, ids[0])
    assert r["status"] == "cancelled", "run yang dibatalkan tidak ditutup"
    assert r["error"] == {"code": "cancelled", "type": "CancelledError"}
    assert r["finished_at"] is not None
    assert r["tools_used"] == ["goal.list"]
    assert r["tokens_out"] >= 1, "token aliran yang terputus tidak tercatat"
    assert r["cost_usd"] > 0, f"token aliran yang terputus tidak dibayar: {r['cost_usd']}"


async def test_klien_lambat_yang_dibatalkan_tokennya_tetap_tercatat(api_bersama: ApiUji) -> None:
    """Pembatalan jatuh saat PENDENGAR menunggu (penulis SSE yang lambat), bukan di dalam
    aliran model: aliran sedang tertahan di `yield`, dan hanya ditutup bila runtime
    menutupnya — tanpa itu token yang sudah keluar tidak pernah tercatat."""
    uid, _token = await api_bersama.pengguna_baru()
    diterima = asyncio.Event()
    ids: list[Any] = []

    async def macet(jenis: str, data: Any) -> None:
        if jenis == "token":
            diterima.set()
            await asyncio.Event().wait()  # klien tidak pernah membaca lagi

    async def jawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu dua tiga"])
        raise AssertionError("pendengar tidak menahan")

    runtime = runtime_uji(api_bersama, {"coach-agent": jawab})
    tugas = asyncio.create_task(
        runtime.jalankan(uid, "coach-agent", "halo", pemicu="user", pendengar=macet)
    )
    await asyncio.wait_for(diterima.wait(), timeout=10)
    tugas.cancel()
    with pytest.raises(asyncio.CancelledError):
        await tugas

    r = run(api_bersama, ids[0])
    assert r["status"] == "cancelled"
    assert r["tokens_out"] >= 1, "token aliran yang ditinggal klien tidak tercatat"
    assert r["cost_usd"] > 0


async def test_run_tidak_bisa_ditutup_dua_kali(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    async def jawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        return agents.Keputusan("ok", Decimal("0.5"), ("uji",), {"action": "reply"})

    runtime = runtime_uji(api_bersama, {"coach-agent": jawab})
    j = await runtime.mulai(uid, "coach-agent", pemicu="user")
    await runtime.lanjutkan(j, "halo")

    with pytest.raises(RuntimeError, match="sudah ditutup"):
        await runtime.lanjutkan(j, "halo lagi")
    assert run(api_bersama, j.id)["decision"] == {"action": "reply"}


async def test_run_anak_tidak_bisa_menunjuk_run_pengguna_lain(api_bersama: ApiUji) -> None:
    a, _ta = await api_bersama.pengguna_baru()
    b, _tb = await api_bersama.pengguna_baru()

    async def jawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        return agents.Keputusan("ok", Decimal("0.5"), ("uji",), {"action": "reply"})

    runtime = runtime_uji(api_bersama, {"coach-agent": jawab, "orchestrator-agent": jawab})
    induk_a = await runtime.mulai(a, "orchestrator-agent", pemicu="user")

    with pytest.raises(ValueError, match="pengguna lain"):
        await runtime.mulai(b, "coach-agent", pemicu="agent", induk=induk_a)
    with pytest.raises(ValueError, match="tidak punya program"):
        await runtime.mulai(b, "habit-agent", pemicu="user")


# ── Penegak buta Sprint 4 (G3): yang dicatat run = yang TERJADI, seluruhnya ──────────


async def test_habit_complete_sendiri_mencatat_scope_habits(api_bersama: ApiUji) -> None:
    """Di alur V0 habit-agent membaca `habit.list` lebih dulu, dan scope itu menutupi
    `habit.complete` yang lupa mencatat dirinya. Tool yang dipanggil sendiri — program
    lain, pemanggilan ulang sesudah konfirmasi — meninggalkan run yang menyentuh habit
    tanpa `habits` di `memory_scopes`."""
    uid, token = await api_bersama.pengguna_baru()
    habit = await buat_habit(api_bersama, token)

    async def tandai(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        await k.alat(
            "habit.complete", {"habit_id": habit["id"], "for_date": "2026-09-20", "status": "done"}
        )
        return agents.Keputusan("Ditandai.", Decimal("0.9"), ("uji",), {"action": "reply"})

    hasil = await runtime_uji(api_bersama, {"habit-agent": tandai}).jalankan(
        uid, "habit-agent", "tandai", pemicu="user"
    )
    r = run(api_bersama, hasil.run_id)

    assert r["tools_used"] == ["habit.complete"]
    assert r["memory_scopes"] == ["habits"], (
        f"scope yang disentuh habit.complete tidak tercatat: {r['memory_scopes']}"
    )


async def _jawab_dua_kali(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu fakta"])
    kedua = await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu dua tiga"])
    return agents.Keputusan(kedua.teks, Decimal("0.5"), ("uji",), {"action": "reply"})


async def test_token_dan_biaya_run_jumlah_seluruh_panggilan_model(api_bersama: ApiUji) -> None:
    """spec/07 4.4 · 4.9 — `tokens_in`/`tokens_out`/`cost_usd` run = JUMLAH seluruh
    panggilan modelnya. Hanya yang terakhir = tagihan dan anggaran yang kurang hitung."""
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await runtime_uji(api_bersama, {"coach-agent": _jawab_dua_kali}).jalankan(
        uid, "coach-agent", "halo", pemicu="user"
    )
    r = run(api_bersama, hasil.run_id)

    # "jawab halo satu fakta" 4 masuk, 2 keluar; "jawab halo satu dua tiga" 5 masuk, 3 keluar
    assert (r["tokens_in"], r["tokens_out"]) == (4 + 5, 2 + 3), (
        f"token run hanya panggilan model terakhir: {r['tokens_in']}/{r['tokens_out']}"
    )
    biaya = HARGA_BESAR.biaya(4, 2) + HARGA_BESAR.biaya(5, 3)
    assert r["cost_usd"] == biaya == hasil.biaya_usd, (
        f"biaya run hanya panggilan model terakhir: {r['cost_usd']} ≠ {biaya}"
    )


class _PenyediaMati(PenyediaUji):
    """AI Gateway yang gagal sebelum token pertama — galat model, bukan galat program."""

    async def alirkan(self, model: str, p: platform.PermintaanModel) -> AsyncIterator[str]:
        self.dipanggil.append(model)
        if self.dipanggil:
            raise platform.GalatModel("penyedia tidak menjawab")
        yield ""  # pragma: no cover - tetap generator async


async def test_galat_model_tercatat_model_gagal(api_bersama: ApiUji) -> None:
    """spec/01 §8 `error.code`: kegagalan AI Gateway dibedakan dari cacat program
    (`internal`) — yang pertama urusan penyedia, yang kedua urusan kita."""
    uid, _token = await api_bersama.pengguna_baru()
    ids: list[Any] = []

    async def jawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        ids.append(k.jalannya.id)
        await k.model(tugas="jawab", pertanyaan=pesan)
        raise AssertionError("penyedia tidak gagal")

    runtime = runtime_uji(
        api_bersama, {"coach-agent": jawab}, gerbang_model=gerbang_model_uji(_PenyediaMati())
    )
    with pytest.raises(platform.GalatModel):
        await runtime.jalankan(uid, "coach-agent", "halo", pemicu="user")
    r = run(api_bersama, ids[0])

    assert r["status"] == "failed"
    assert r["error"] == {"code": "model_gagal", "type": "GalatModel"}, (
        f"galat AI Gateway tercatat dengan kode lain: {r['error']}"
    )


async def test_latency_ms_mengukur_lamanya_run(api_bersama: ApiUji) -> None:
    """spec/07 4.4 — `latency_ms` adalah lamanya run, bukan sekadar `>= 0`: angka yang
    selalu nol lolos semua uji yang hanya memeriksa tandanya."""
    uid, _token = await api_bersama.pengguna_baru()

    async def lambat(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        await asyncio.sleep(0.1)
        return agents.Keputusan("ok", Decimal("0.5"), ("uji",), {"action": "reply"})

    hasil = await runtime_uji(api_bersama, {"coach-agent": lambat}).jalankan(
        uid, "coach-agent", "halo", pemicu="user"
    )

    # 50, bukan 100: jam asyncio di Windows boleh membangunkan sedikit lebih awal.
    latensi = run(api_bersama, hasil.run_id)["latency_ms"]
    assert latensi >= 50, f"latency_ms tidak mengukur lamanya run: {latensi} ms untuk ≥100 ms"


async def test_hari_ini_agent_menurut_zona_waktu_profil_bukan_utc(api_bersama: ApiUji) -> None:
    """*“Tandai lari selesai”* pukul 01.30 WIB adalah hari itu di Jakarta — `tanggal_lokal`
    membaca zona waktu profil, bukan jam server. Dulu tidak dijaga uji mana pun: seluruh
    suite berjalan saat tanggal UTC kebetulan sama dengan tanggal Jakarta."""
    from datetime import UTC, datetime

    uid, _token = await api_bersama.pengguna_baru()  # Asia/Jakarta
    saat = datetime(2026, 9, 24, 18, 30, tzinfo=UTC)  # = 25 Sep 01.30 WIB

    async def hari(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        tanggal = (await k.tanggal_lokal()).isoformat()
        aksi = {"action": "reply", "hari": tanggal}
        return agents.Keputusan("ok", Decimal("0.5"), ("uji",), aksi)

    hasil = await runtime_uji(api_bersama, {"coach-agent": hari}, jam=lambda: saat).jalankan(
        uid, "coach-agent", "halo", pemicu="user"
    )

    assert hasil.keputusan.aksi["hari"] == "2026-09-25", (
        f"hari ini agent bukan tanggal zona waktu profil: {hasil.keputusan.aksi['hari']}"
    )
