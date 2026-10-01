"""`recommendation.create` — spec/05 (tool R1, coach-agent): satu rekomendasi yang tercatat.

Sprint 5 (5.5) membangun mesin rekomendasinya — skor 0–1, `score_breakdown`,
`scoring_version`. Yang ada sejak 4.3 hanya jalur coach menyimpan SARAN-nya sendiri,
dengan dua hal yang tidak boleh kosong sejak baris pertama: **keyakinan** dan
**alasan** (Confidence Layer §19, Explainable AI naskah 4 §29). `score` sengaja
kosong: skor adalah keluaran mesin 5.5, bukan angka yang dikarang agent.
"""

from __future__ import annotations

import re
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository

# spec/01 `recommendations.domain` — contoh kolomnya: 'habit','goal','wellbeing'.
DOMAIN = frozenset({"habit", "goal", "wellbeing"})
JUDUL_MAKS = 200
ISI_MAKS = 2_000
ALASAN_MAKS = 10
_BERISI = re.compile(r"\S")


def periksa_rekomendasi(
    *, domain: str, title: str, body: str | None, confidence: Decimal, rationale: list[str]
) -> None:
    """`ValueError` bila rekomendasi ini akan ditolak — murni, tanpa basis data: pemanggil
    memeriksanya sebelum gerbang risiko (agents, E-204)."""
    if not confidence.is_finite():
        raise ValueError("confidence wajib bilangan hingga")
    if domain not in DOMAIN:
        raise ValueError(f"domain rekomendasi di luar {sorted(DOMAIN)}")
    if not _BERISI.search(title) or len(title) > JUDUL_MAKS:
        raise ValueError(f"judul rekomendasi wajib 1–{JUDUL_MAKS} karakter")
    if body is not None and len(body) > ISI_MAKS:
        raise ValueError(f"isi rekomendasi paling panjang {ISI_MAKS} karakter")
    if not Decimal(0) <= confidence <= Decimal(1):
        raise ValueError("confidence wajib 0–1")
    if (
        not rationale
        or len(rationale) > ALASAN_MAKS
        or not all(isinstance(a, str) and _BERISI.search(a) for a in rationale)
    ):
        raise ValueError(f"rationale wajib 1–{ALASAN_MAKS} alasan berisi")


async def buat_rekomendasi(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    agent_id: UUID,
    agent_run_id: UUID | None,
    domain: str,
    title: str,
    body: str | None,
    confidence: Decimal,
    rationale: list[str],
    jejak: platform.JejakTulisan | None = None,
) -> UUID:
    """`jejak` dijalankan di transaksi tulisannya (E-205)."""
    periksa_rekomendasi(
        domain=domain, title=title, body=body, confidence=confidence, rationale=rationale
    )
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        rid = await repository.sisip(
            conn,
            user_id=user_id,
            agent_id=agent_id,
            agent_run_id=agent_run_id,
            domain=domain,
            title=title,
            body=body,
            confidence=confidence.quantize(Decimal("0.001")),
            rationale=rationale,
        )
        if jejak is not None:
            await jejak(conn)
    return rid
