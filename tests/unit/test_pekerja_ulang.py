"""`hvx.pekerja` tanpa layanan — pengulangan tugasnya (tinjauan penegak buta Sprint 3)."""

from __future__ import annotations

import asyncio

from hvx import pekerja


async def test_putaran_yang_gagal_dijeda_sebelum_diulang() -> None:
    """Konsumen berulang tanpa jeda (`jeda_s=0`): Redis yang mati membuat tiap putaran
    langsung gagal — tanpa jeda minimum, pekerja memutar CPU dan membanjiri log."""
    percobaan = 0

    async def gagal() -> None:
        nonlocal percobaan
        percobaan += 1
        await asyncio.sleep(0)
        raise RuntimeError("redis mati")

    berhenti = asyncio.Event()
    tugas = asyncio.create_task(pekerja._ulang("uji", gagal, 0.0, berhenti))
    await asyncio.sleep(0.3)
    berhenti.set()
    await tugas

    assert percobaan <= 2, f"{percobaan} putaran gagal dalam 0,3 dtk"
