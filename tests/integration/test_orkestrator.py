"""spec/07 4.6 — *`parent_run_id` membentuk pohon eksekusi*.

`orchestrator-agent` sungguhan di atas runtime dan pelaksana tool sungguhan; agent
yang dipanggilnya di sini program tiruan yang hanya menjawab (program V0-nya diuji
4.7). Pohonnya dibaca dari `agent_runs` dengan kueri rekursif dari AKAR — bukti
bahwa satu permintaan bisa ditelusuri seutuhnya dari satu id.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest
from _bantuan_agent import HARGA_BESAR, REGISTRI, run, runtime_uji, sql
from _bantuan_db import ApiUji

from hvx.modules import agents

pytestmark = pytest.mark.integration

POHON = """
WITH RECURSIVE pohon AS (
  SELECT id, parent_run_id, agent_id, trigger, 0 AS dalam FROM agent_runs WHERE id = %s
  UNION ALL
  SELECT a.id, a.parent_run_id, a.agent_id, a.trigger, p.dalam + 1
  FROM agent_runs a JOIN pohon p ON a.parent_run_id = p.id
)
SELECT dalam, parent_run_id, agent_id, trigger FROM pohon ORDER BY dalam
"""


def _penjawab(nama: str) -> agents.ProgramAgent:
    async def program(k: agents.KonteksAgent, pesan: str) -> agents.Keputusan:
        jawaban = await k.model(tugas="jawab", pertanyaan=pesan, bahan=[f"dijawab {nama}"])
        return agents.Keputusan(
            jawaban.teks, Decimal("0.4"), (f"alasan {nama}",), {"action": "reply"}
        )

    return program


PROGRAM: dict[str, agents.ProgramAgent] = {
    "orchestrator-agent": agents.orkestrator,
    "coach-agent": _penjawab("coach"),
    "habit-agent": _penjawab("habit"),
    "memory-agent": _penjawab("memory"),
}


def _pohon(api: ApiUji, akar: UUID) -> list[tuple[Any, ...]]:
    return sql(api, POHON, akar)


async def test_parent_run_id_membentuk_pohon_eksekusi(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await runtime_uji(api_bersama, PROGRAM).jalankan(
        uid, "orchestrator-agent", "bagaimana tidurku?", pemicu="user"
    )
    pohon = _pohon(api_bersama, hasil.run_id)
    akar = run(api_bersama, hasil.run_id)

    assert pohon == [
        (0, None, REGISTRI.agent["orchestrator-agent"].id_katalog, "user"),
        (1, hasil.run_id, REGISTRI.agent["coach-agent"].id_katalog, "agent"),
    ], f"pohon eksekusi: {pohon}"
    assert akar["tools_used"] == ["agent.coach"]
    assert akar["decision"] == {"action": "delegate", "agent": "coach-agent"}
    assert akar["risk_level"] == 1, "pemanggilan agent tidak tercatat dengan risikonya (K-14)"


async def test_balasan_anak_sampai_tanpa_dikarang_ulang_dan_biayanya_ikut(
    api_bersama: ApiUji,
) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await runtime_uji(api_bersama, PROGRAM).jalankan(
        uid, "orchestrator-agent", "halo", pemicu="user"
    )
    akar = run(api_bersama, hasil.run_id)
    anak = sql(
        api_bersama, "SELECT cost_usd FROM agent_runs WHERE parent_run_id = %s", hasil.run_id
    )

    k = hasil.keputusan
    assert (k.teks, k.confidence, k.rationale) == (
        "dijawab coach",
        Decimal("0.4"),
        ("alasan coach",),
    ), "orchestrator mengubah balasan agent yang menjawab"
    assert akar["cost_usd"] == 0, "orchestrator memanggil model"
    # Biaya satu permintaan = seluruh pohon (SSE `done`): 4 kata masuk, 2 keluar — model
    # besar, sebab `model.class` coach-agent = reasoning.
    assert anak == [(HARGA_BESAR.biaya(1 + 1 + 2, 2),)]
    assert hasil.biaya_usd == anak[0][0] > 0, "biaya run anak tidak ikut dibayar permintaannya"


@pytest.mark.parametrize(
    ("pesan", "agent"),
    [
        ("tandai lari pagi selesai", "habit-agent"),
        ("ingat bahwa aku alergi kacang", "memory-agent"),
        ("apa yang kamu ingat tentang tidurku?", "memory-agent"),
        ("kenapa aku capek terus?", "coach-agent"),
    ],
)
async def test_niat_menentukan_agent_yang_dipanggil(
    api_bersama: ApiUji, pesan: str, agent: str
) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await runtime_uji(api_bersama, PROGRAM).jalankan(
        uid, "orchestrator-agent", pesan, pemicu="user"
    )

    anak = _pohon(api_bersama, hasil.run_id)[1:]
    assert [a[2] for a in anak] == [REGISTRI.agent[agent].id_katalog], (
        f"“{pesan}” diserahkan ke agent yang salah"
    )


async def test_perintah_deterministik_tidak_dijalankan_agent(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    runtime = runtime_uji(api_bersama, PROGRAM)

    with pytest.raises(ValueError, match="tidak dijalankan agent"):
        await runtime.jalankan(uid, "orchestrator-agent", "catat mood 3", pemicu="user")

    assert sql(
        api_bersama,
        "SELECT count(*) FROM agent_runs WHERE user_id = %s AND parent_run_id IS NOT NULL",
        uid,
    ) == [(0,)]
