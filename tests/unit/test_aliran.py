"""Aliran percakapan (K-31) — satu giliran per percakapan, di dalam proses api.

Giliran yang selesai disimpan `simpan_s` sesudahnya untuk klien yang menyambung
terlambat, lalu dibuang oleh pengatur waktu loop. Giliran BERIKUTNYA boleh dimulai
sebelum itu — jadi saat pembuangnya berjalan, yang tercatat untuk percakapan itu bisa
sudah giliran lain.
"""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from hvx.modules.agents import AliranPercakapan, GiliranBerjalan

SIMPAN_S = 0.05


async def test_pembuang_giliran_lama_tidak_menghapus_giliran_yang_sedang_berjalan() -> None:
    """Pembuang giliran ke-1 hanya menghapus giliran MILIKNYA. Bila ia menghapus apa pun
    yang tercatat, giliran ke-2 yang masih berjalan lenyap: giliran ke-3 bisa dimulai
    serentak dengannya (K-31), dan klien giliran ke-2 menerima `204` — alirannya hilang."""
    aliran = AliranPercakapan(simpan_s=SIMPAN_S)
    cid = uuid4()
    aliran.mulai(cid)
    await aliran.kirim(cid, "done", {"content": "pertama"})
    aliran.mulai(cid)  # giliran ke-2 — giliran ke-1 sudah selesai, belum dibuang
    await aliran.kirim(cid, "token", {"text": "kedua"})

    await asyncio.sleep(SIMPAN_S * 4)  # pembuang giliran ke-1 sudah berjalan

    assert aliran.sibuk(cid), "pembuang giliran lama menghapus giliran yang sedang berjalan"
    with pytest.raises(GiliranBerjalan):
        aliran.mulai(cid)


async def test_giliran_yang_selesai_dibuang_sesudah_masa_simpannya() -> None:
    """Pembanding: tanpa giliran baru, giliran yang selesai memang dibuang — `204` untuk
    klien yang menyambung sesudahnya, dan giliran berikutnya bisa dimulai."""
    aliran = AliranPercakapan(simpan_s=SIMPAN_S)
    cid = uuid4()
    aliran.mulai(cid)
    await aliran.kirim(cid, "done", {"content": "pertama"})
    assert aliran.ada(cid), "giliran yang baru selesai dibuang sebelum masa simpannya"

    await asyncio.sleep(SIMPAN_S * 4)

    assert not aliran.ada(cid), "giliran yang selesai tidak pernah dibuang"
