"""spec/07 4.9 — anggaran biaya per pengguna per hari: *melewati batas → turun ke model
kecil, bukan gagal*.

Hari = hari LOKAL pengguna (zona waktu profilnya; pengguna uji tinggal di
Asia/Jakarta). Biaya lampau ditanam sebagai run yang sudah ditutup — anggaran membaca
jejak `agent_runs` yang sama dengan audit, bukan penghitung tersendiri yang bisa
menyimpang darinya.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

import psycopg
import pytest
from _bantuan_agent import HARGA_BESAR, REGISTRI, run, runtime_uji
from _bantuan_db import ApiUji, psycopg_dsn

from hvx.modules import agents

pytestmark = pytest.mark.integration

JAKARTA = ZoneInfo("Asia/Jakarta")


def _biaya_lampau(api: ApiUji, uid: UUID, biaya: str, saat: datetime) -> None:
    """Run yang sudah ditutup `saat`, berbiaya `biaya` — ditulis pemilik tabel."""
    coach = REGISTRI.agent["coach-agent"]
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        k.execute(
            "INSERT INTO agent_runs (user_id, agent_id, agent_version, trigger, status, cost_usd,"
            " started_at, finished_at) VALUES (%s, %s, %s, 'user', 'succeeded', %s, %s, %s)",
            (uid, coach.id_katalog, coach.version, Decimal(biaya), saat, saat),
        )


async def _jawab(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    jawaban = await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu fakta"])
    return agents.Keputusan(jawaban.teks, Decimal("0.5"), ("uji",), {"action": "reply"})


async def _jawab_dua_kali(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    await k.model(tugas="jawab", pertanyaan=pesan, bahan=["satu fakta"])
    return await _jawab(k, pesan)


async def _run(api: ApiUji, uid: UUID, anggaran: str, program: Any = _jawab) -> dict[str, Any]:
    hasil = await runtime_uji(api, {"coach-agent": program}, anggaran=Decimal(anggaran)).jalankan(
        uid, "coach-agent", "halo", pemicu="user"
    )
    assert hasil.keputusan.teks, "run dengan anggaran habis tidak menjawab"
    return run(api, hasil.run_id)


async def test_di_bawah_anggaran_memakai_model_kelasnya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    r = await _run(api_bersama, uid, "1")

    assert r["model_used"] == "uji/besar"
    assert "model_downgraded" not in r["decision"]


async def test_anggaran_habis_turun_ke_model_kecil_bukan_gagal(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, uid, "0.60", datetime.now(JAKARTA))

    r = await _run(api_bersama, uid, "0.50")

    assert r["status"] == "succeeded", "anggaran habis menggagalkan run"
    assert r["model_used"] == "uji/kecil", "anggaran habis tidak menurunkan kelas model"
    assert r["decision"].get("model_downgraded") is True, "turun kelas tidak tercatat di jejaknya"


# SATU saat yang dipilih: 24 Sep 18.30 UTC = 25 Sep 01.30 WIB. Hari lokal pengguna mulai
# 24 Sep 17.00 UTC; hari UTC mulai 24 Sep 00.00 UTC — keduanya berbeda di saat ini.
SAAT = datetime(2026, 9, 24, 18, 30, tzinfo=UTC)
HARI_INI_LOKAL = datetime(2026, 9, 24, 17, 30, tzinfo=UTC)  # 25 Sep 00.30 WIB
KEMARIN_LOKAL = datetime(2026, 9, 24, 16, 30, tzinfo=UTC)  # 24 Sep 23.30 WIB — hari UTC yang sama


async def _run_pada(api: ApiUji, uid: UUID, anggaran: str) -> dict[str, Any]:
    hasil = await runtime_uji(
        api, {"coach-agent": _jawab}, anggaran=Decimal(anggaran), jam=lambda: SAAT
    ).jalankan(uid, "coach-agent", "halo", pemicu="user")
    return run(api, hasil.run_id)


async def test_biaya_kemarin_waktu_lokal_tidak_dihitung(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, uid, "5", KEMARIN_LOKAL)

    r = await _run_pada(api_bersama, uid, "0.50")

    assert r["model_used"] == "uji/besar", "biaya hari kemarin (waktu lokal) ikut dihitung"


async def test_hari_anggaran_adalah_hari_lokal_bukan_hari_utc(api_bersama: ApiUji) -> None:
    """Dua run sama mahal: satu hari ini waktu Jakarta, satu kemarin — keduanya hari UTC yang
    sama. Hanya yang pertama dihitung; anggaran belum habis."""
    uid, _token = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, uid, "0.30", HARI_INI_LOKAL)
    _biaya_lampau(api_bersama, uid, "0.30", KEMARIN_LOKAL)

    r = await _run_pada(api_bersama, uid, "0.50")

    assert r["model_used"] == "uji/besar", "anggaran dihitung per hari UTC, bukan hari pengguna"


async def test_biaya_pengguna_lain_tidak_dihitung(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    lain, _t = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, lain, "5", datetime.now(JAKARTA))

    r = await _run(api_bersama, uid, "0.50")

    assert r["model_used"] == "uji/besar", "biaya pengguna lain menghabiskan anggaran"


async def test_panggilan_kedua_satu_run_melihat_biaya_yang_pertama(api_bersama: ApiUji) -> None:
    """Anggaran = biaya satu panggilan besar: yang pertama besar, yang kedua sudah kecil."""
    uid, _token = await api_bersama.pengguna_baru()
    satu_panggilan = HARGA_BESAR.biaya(1 + 1 + 2, 2)

    r = await _run(api_bersama, uid, str(satu_panggilan), _jawab_dua_kali)

    assert r["model_used"] == "uji/besar,uji/kecil", (
        f"biaya run yang sedang berjalan tidak dihitung: {r['model_used']}"
    )


async def test_anggaran_nol_selalu_model_kecil(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    r = await _run(api_bersama, uid, "0")

    assert r["model_used"] == "uji/kecil"
