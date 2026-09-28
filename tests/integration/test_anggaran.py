"""spec/07 4.9 — anggaran biaya per pengguna per hari: *melewati batas → turun ke model
kecil, bukan gagal*.

Hari = **24 jam yang bergulir** (K-32, E-201) — bukan hari kalender: hari lokal bisa
digeser pengguna lewat zona waktu profilnya. Sebelum TIAP panggilan model, jatah
TERBURUKNYA (token masuk + `maks_token` keluar) dipesan di bawah kunci per pengguna —
giliran serentak di percakapan lain melihatnya. Biaya lampau ditanam sebagai run yang
sudah ditutup: anggaran membaca jejak `agent_runs` yang sama dengan audit, bukan
penghitung tersendiri yang bisa menyimpang darinya.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

import psycopg
import pytest
from _bantuan_agent import HARGA_BESAR, REGISTRI, PenyediaUji, gerbang_model_uji, run, runtime_uji
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx.modules import agents

pytestmark = pytest.mark.integration

JAKARTA = ZoneInfo("Asia/Jakarta")
# "jawab halo satu fakta" = 4 token masuk; "satu fakta" = 2 token keluar.
TOKEN_MASUK, TOKEN_KELUAR = 4, 2
SATU_PANGGILAN_BESAR = HARGA_BESAR.biaya(TOKEN_MASUK, TOKEN_KELUAR)


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


async def _jawab_pas(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    """`maks_token` = token yang sungguh keluar — jatah terburuk = biaya sebenarnya."""
    jawaban = await k.model(
        tugas="jawab", pertanyaan=pesan, bahan=["satu fakta"], maks_token=TOKEN_KELUAR
    )
    return agents.Keputusan(jawaban.teks, Decimal("0.5"), ("uji",), {"action": "reply"})


async def _jawab_dua_kali(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    await _jawab_pas(k, pesan)
    return await _jawab_pas(k, pesan)


async def _run(
    api: ApiUji,
    uid: UUID,
    anggaran: str,
    program: Any = _jawab,
    jam: Any = None,
) -> dict[str, Any]:
    hasil = await runtime_uji(
        api, {"coach-agent": program}, anggaran=Decimal(anggaran), jam=jam
    ).jalankan(uid, "coach-agent", "halo", pemicu="user")
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


# SATU saat yang dipilih: 24 Sep 18.30 UTC = 25 Sep 01.30 WIB — hari lokal DAN hari UTC
# sama-sama baru berganti beberapa jam lalu.
SAAT = datetime(2026, 9, 24, 18, 30, tzinfo=UTC)


async def test_biaya_lebih_dari_24_jam_lalu_tidak_dihitung(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, uid, "5", SAAT - timedelta(hours=24, minutes=1))

    r = await _run(api_bersama, uid, "0.50", jam=lambda: SAAT)

    assert r["model_used"] == "uji/besar", "biaya lebih dari 24 jam lalu ikut dihitung"


async def test_jendela_bergulir_tidak_diatur_ulang_tengah_malam(api_bersama: ApiUji) -> None:
    """23 jam lalu = KEMARIN menurut jam Jakarta maupun UTC — tetap dihitung."""
    uid, _token = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, uid, "0.60", SAAT - timedelta(hours=23))

    r = await _run(api_bersama, uid, "0.50", jam=lambda: SAAT)

    assert r["model_used"] == "uji/kecil", "anggaran diatur ulang oleh pergantian hari kalender"


async def test_ganti_zona_waktu_tidak_mengosongkan_anggaran(api_bersama: ApiUji) -> None:
    """E-201 (tinjauan keamanan Sprint 4): dengan hari LOKAL, pindah ke zona yang tengah
    malamnya baru lewat membuang biaya sejam terakhir — anggaran harian menjadi per jam."""
    uid, token = await api_bersama.pengguna_baru()  # Asia/Jakarta
    _biaya_lampau(api_bersama, uid, "0.60", SAAT - timedelta(hours=1))  # 25 Sep 00.30 WIB
    r = await api_bersama.klien.patch(
        "/v1/me/profile", json={"timezone": "Asia/Dhaka"}, headers=auth(token)
    )  # 25 Sep 00.30 WIB = 24 Sep 23.30 Dhaka — "kemarin" di zona barunya
    assert r.status_code == 200, r.text

    sesudah = await _run(api_bersama, uid, "0.50", jam=lambda: SAAT)

    assert sesudah["model_used"] == "uji/kecil", "ganti zona waktu mengosongkan anggaran"


async def test_biaya_pengguna_lain_tidak_dihitung(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    lain, _t = await api_bersama.pengguna_baru()
    _biaya_lampau(api_bersama, lain, "5", datetime.now(JAKARTA))

    r = await _run(api_bersama, uid, "0.50")

    assert r["model_used"] == "uji/besar", "biaya pengguna lain menghabiskan anggaran"


async def test_panggilan_kedua_satu_run_melihat_biaya_yang_pertama(api_bersama: ApiUji) -> None:
    """Anggaran = biaya satu panggilan besar: yang pertama besar, yang kedua sudah kecil."""
    uid, _token = await api_bersama.pengguna_baru()

    r = await _run(api_bersama, uid, str(SATU_PANGGILAN_BESAR), _jawab_dua_kali)

    assert r["model_used"] == "uji/besar,uji/kecil", (
        f"biaya run yang sedang berjalan tidak dihitung: {r['model_used']}"
    )


async def test_jatah_terburuk_dipesan_bukan_biaya_yang_diharapkan(api_bersama: ApiUji) -> None:
    """Sisa anggaran cukup untuk jawaban SEPENDEK ini, tetapi tidak untuk `maks_token`-nya:
    yang dipesan adalah yang BISA dibayar panggilan itu, bukan tebakan."""
    uid, _token = await api_bersama.pengguna_baru()
    cukup_untuk_sepuluh = HARGA_BESAR.biaya(TOKEN_MASUK, 10)  # maks_token bawaan 400

    r = await _run(api_bersama, uid, str(cukup_untuk_sepuluh))

    assert r["model_used"] == "uji/kecil", "panggilan yang bisa melewati anggaran tetap besar"
    assert r["decision"].get("model_downgraded") is True


async def test_giliran_serentak_tidak_melewati_anggaran(api_bersama: ApiUji) -> None:
    """E-201 (tinjauan keamanan Sprint 4): anggaran = tepat satu panggilan besar; empat
    giliran serentak (empat percakapan) — dulu keempatnya besar, sebab masing-masing
    hanya melihat pohonnya sendiri. Kini jatahnya dipesan di bawah kunci per pengguna."""
    uid, _token = await api_bersama.pengguna_baru()
    rt = runtime_uji(
        api_bersama,
        {"coach-agent": _jawab_pas},
        gerbang_model=gerbang_model_uji(PenyediaUji(jeda_s=0.2)),
        anggaran=SATU_PANGGILAN_BESAR,
    )

    hasil = await asyncio.gather(
        *(rt.jalankan(uid, "coach-agent", "halo", pemicu="user") for _ in range(4))
    )
    model = sorted(run(api_bersama, x.run_id)["model_used"] for x in hasil)

    assert model == ["uji/besar", "uji/kecil", "uji/kecil", "uji/kecil"], (
        f"giliran serentak melewati anggaran untuk satu panggilan besar: {model}"
    )


async def test_pemesanan_jatah_serial_di_bawah_kunci(
    api_bersama: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Jendela antara MEMBACA anggaran dan MEMESAN jatah dilebarkan: tanpa kunci per
    pengguna, dua giliran membaca anggaran yang sama lalu sama-sama memesan model besar."""
    from hvx.modules.agents import repository

    asli = repository.biaya_sejak

    async def lambat(conn: Any, user_id: UUID, sejak: datetime) -> Decimal:
        terpakai = await asli(conn, user_id, sejak)
        await asyncio.sleep(0.3)
        return terpakai

    monkeypatch.setattr(repository, "biaya_sejak", lambat)
    uid, _token = await api_bersama.pengguna_baru()
    rt = runtime_uji(api_bersama, {"coach-agent": _jawab_pas}, anggaran=SATU_PANGGILAN_BESAR)

    hasil = await asyncio.gather(
        *(rt.jalankan(uid, "coach-agent", "halo", pemicu="user") for _ in range(3))
    )
    model = sorted(run(api_bersama, x.run_id)["model_used"] for x in hasil)

    assert model == ["uji/besar", "uji/kecil", "uji/kecil"], (
        f"jatah dipesan tanpa kunci — giliran serentak membaca anggaran yang sama: {model}"
    )


async def test_jatah_terlihat_di_run_selama_panggilan_berjalan(api_bersama: ApiUji) -> None:
    """Yang membuat giliran lain melihatnya: `cost_usd` run yang MASIH berjalan = jatahnya;
    sesudah panggilan selesai = biaya sebenarnya."""
    uid, _token = await api_bersama.pengguna_baru()
    penyedia = PenyediaUji(jeda_s=0.3)
    rt = runtime_uji(
        api_bersama,
        {"coach-agent": _jawab},
        gerbang_model=gerbang_model_uji(penyedia),
        anggaran=Decimal("1"),
    )
    j = await rt.mulai(uid, "coach-agent", pemicu="user")
    tugas = asyncio.create_task(rt.lanjutkan(j, "halo"))
    await asyncio.wait_for(penyedia.token_keluar.wait(), timeout=10)
    saat_berjalan = run(api_bersama, j.id)
    await tugas
    sesudah = run(api_bersama, j.id)

    assert saat_berjalan["status"] == "running"
    assert saat_berjalan["cost_usd"] == HARGA_BESAR.biaya(TOKEN_MASUK, 400), (
        f"jatah panggilan yang berjalan tidak terlihat: {saat_berjalan['cost_usd']}"
    )
    assert sesudah["cost_usd"] == SATU_PANGGILAN_BESAR, "jatah tidak diganti biaya sebenarnya"


async def test_anggaran_nol_selalu_model_kecil(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    r = await _run(api_bersama, uid, "0")

    assert r["model_used"] == "uji/kecil"


async def _jawab_dua_kali_bawaan(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
    await _jawab(k, pesan)
    return await _jawab(k, pesan)


async def test_jatah_dilunasi_sesudah_panggilan(api_bersama: ApiUji) -> None:
    """Jatah TERBURUK diganti biaya sebenarnya begitu panggilan selesai — tanpa itu
    panggilan kedua satu run melihat jatah yang sudah tidak berlaku. Anggaran = satu
    jatah terburuk + satu panggilan sebenarnya: keduanya muat, bila jatah pertama dilunasi."""
    uid, _token = await api_bersama.pengguna_baru()
    anggaran = HARGA_BESAR.biaya(TOKEN_MASUK, 400) + SATU_PANGGILAN_BESAR

    r = await _run(api_bersama, uid, str(anggaran), _jawab_dua_kali_bawaan)

    assert r["model_used"] == "uji/besar", (
        f"jatah panggilan pertama tidak dilunasi — panggilan kedua turun kelas: {r['model_used']}"
    )
