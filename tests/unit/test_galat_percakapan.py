"""spec/04 SSE `error.code` — kode API berbahasa Inggris, bukan kode internal (E-203).

AGENTS.md §7: *galat ke klien: `kode` snake_case berbahasa Inggris*. Pelaksana tool dan
runtime memakai kode internal (`terlalu_sering`, `masukan_salah`, …) di jejak auditnya;
yang sampai ke klien dipetakan di SATU tempat.
"""

from __future__ import annotations

import asyncio

import pytest

from hvx.modules import agents, platform
from hvx.modules.agents.percakapan import _kode

KASUS = [
    (platform.GalatApi(409, "turn_in_progress", "x"), "turn_in_progress"),
    (asyncio.CancelledError(), "cancelled"),
    (agents.AlatDitolak("terlalu_sering", "x"), "rate_limited"),
    (agents.AlatDitolak("masukan_salah", "x"), "agent_error"),
    (agents.AlatDitolak("bukan_alat_agent", "x"), "agent_error"),
    (agents.AlatDitolak("tidak_terdaftar", "x"), "agent_error"),
    (agents.AlatDitolak("scope_di_luar_manifest", "x"), "agent_error"),
    (agents.AlatGagal("not_found", "x"), "not_found"),
    (agents.KeputusanTidakSah("x"), "agent_error"),
    (platform.GalatModel("x"), "model_unavailable"),
    (ValueError("x"), "internal_error"),
]


@pytest.mark.parametrize(("galat", "kode"), KASUS, ids=[k for _g, k in KASUS])
def test_kode_galat_sse_adalah_kode_api(galat: BaseException, kode: str) -> None:
    assert _kode(galat) == kode, f"SSE error.code {_kode(galat)!r}, harapan {kode!r}"
