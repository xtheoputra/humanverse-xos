"""Bantuan uji Sprint 4 — runtime agent di atas aplikasi uji bersama, penyedia model berharga.

Diawali garis bawah supaya pytest tidak mengumpulkannya sebagai berkas uji.

Penyedia V0 (`lokal`) gratis: biaya nol tidak membuktikan bahwa biaya dicatat. Uji
memakai penyedia `uji` yang merangkai bahan seperti penyedia lokal, tetapi BERHARGA —
dan bisa diperlambat per token untuk menguji aliran yang terputus.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Mapping
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import psycopg
from _bantuan_db import ApiUji, psycopg_dsn

from hvx.modules import agents, platform

REGISTRI = agents.muat_registri()

HARGA_KECIL = platform.HargaModel(Decimal("1"), Decimal("2"))  # USD per sejuta token
HARGA_BESAR = platform.HargaModel(Decimal("10"), Decimal("30"))


class PenyediaUji:
    """Seperti penyedia lokal — bahan dirangkai, tanpa jaringan — tetapi berharga."""

    nama = "uji"

    def __init__(self, jeda_s: float = 0.0) -> None:
        self.jeda_s = jeda_s
        self.dipanggil: list[str] = []
        self.token_keluar = asyncio.Event()

    def hitung_token(self, teks: str) -> int:
        return len(teks.split())

    async def alirkan(self, model: str, p: platform.PermintaanModel) -> AsyncIterator[str]:
        self.dipanggil.append(model)
        teks = " ".join(p.bahan) if p.bahan else platform.TANPA_DATA
        for i, kata in enumerate(teks.split(" ")):
            yield kata if i == 0 else " " + kata
            self.token_keluar.set()
            await asyncio.sleep(self.jeda_s)


def gerbang_model_uji(penyedia: PenyediaUji | None = None) -> platform.GerbangModel:
    return platform.GerbangModel(
        {"uji": penyedia or PenyediaUji()},
        {"simple": "uji/kecil", "reasoning": "uji/besar"},
        {"uji/kecil": HARGA_KECIL, "uji/besar": HARGA_BESAR},
    )


class GerbangBuka:
    """Gerbang yang selalu mengizinkan — gerbang risiko sungguhan diuji di 4.5."""

    async def periksa(self, j: agents.Jalannya, alat: agents.Alat, m: Mapping[str, Any]) -> None:
        return None


def runtime_uji(
    api: ApiUji,
    program: Mapping[str, agents.ProgramAgent],
    *,
    gerbang: agents.Gerbang | None = None,
    gerbang_model: platform.GerbangModel | None = None,
    anggaran: Decimal | None = None,
    jam: Callable[[], datetime] | None = None,
) -> agents.RuntimeAgent:
    return agents.RuntimeAgent(
        api.app.state.engine,
        REGISTRI,
        program,
        agents.PelaksanaAlat(REGISTRI, agents.IMPLEMENTASI, gerbang or GerbangBuka(), None),
        gerbang_model or gerbang_model_uji(),
        anggaran_harian_usd=anggaran,
        jam=jam,
    )


def sql(api: ApiUji, q: str, *p: object) -> list[tuple[Any, ...]]:
    """Dibaca sebagai pemilik tabel — di luar RLS, untuk memeriksa apa yang TERSIMPAN."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(q, p).fetchall()


def run(api: ApiUji, run_id: UUID) -> dict[str, Any]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        kursor = k.execute("SELECT * FROM agent_runs WHERE id = %s", (run_id,))
        kolom = [d.name for d in kursor.description or ()]
        baris = kursor.fetchone()
    assert baris is not None, f"run {run_id} tidak tersimpan"
    return dict(zip(kolom, baris, strict=True))


async def izinkan_mood(api: ApiUji, user_id: UUID) -> None:
    """C-32 (K-46): `mood` sensitif — coach & memory-agent membacanya hanya sesudah pengguna
    menyimpan `allow`. Uji yang menguji hal LAIN dari jawaban yang memuat mood memulai dari
    pengguna yang sudah mengizinkannya; yang menguji izinnya sendiri tidak memanggil ini."""
    from hvx.modules import identity

    s = api.app.state.settings
    izin = identity.MesinIzin(
        api.app.state.engine, api.app.state.redis, s.redis_prefix, s.permission_cache_ttl_s
    )
    for agent in ("coach-agent", "memory-agent"):
        await izin.tetapkan(user_id, identity.Subjek("agent", agent), "mood", "read", "allow")
