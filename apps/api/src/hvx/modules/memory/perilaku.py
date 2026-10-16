"""Memori pola perilaku — spec/07 5.2: deteksi pola → `memories(kind='behavioral')`.

Behavior Engine (modul `intelligence`, lapisan di atas `memory`) menghitung pola
dari event lalu menuliskannya di sini. `memory` tidak tahu POLA apa — ia menjaga
bentuknya: scope resmi, keyakinan 0–1, isi berisi. Keyakinan + `evidence_count`
adalah Confidence Layer (§19): keduanya disimpan apa adanya, dan AMBANG kapan
sistem menyatakan vs bertanya adalah milik pemilik (#34, tugas 5.4) — bukan di sini.

Idempoten & menguatkan: id deterministik per pola, jadi menghitung ulang menimpa
baris yang sama, bukan menumpuk.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import identity

from . import repository

ISI_POLA_MAKS = 1_000


def _periksa(scope: str, content: str, confidence: Decimal) -> str:
    if scope not in identity.SCOPE_RESMI:
        raise ValueError("scope di luar daftar resmi spec/05")
    rapi = " ".join(content.split())
    if not rapi or len(rapi) > ISI_POLA_MAKS:
        raise ValueError(f"isi pola wajib 1–{ISI_POLA_MAKS} karakter")
    if not confidence.is_finite() or not Decimal(0) <= confidence <= Decimal(1):
        raise ValueError("confidence wajib 0–1")
    return rapi


async def catat_pola(
    conn: AsyncConnection,
    user_id: UUID,
    *,
    id_: UUID,
    scope: str,
    content: str,
    confidence: Decimal,
    evidence_count: int,
    model_version: str,
) -> None:
    """Simpan/kuatkan satu memori pola (`kind='behavioral'`), di transaksi pemanggil."""
    if evidence_count < 0:
        raise ValueError("evidence_count wajib ≥ 0")
    rapi = _periksa(scope, content, confidence)
    await repository.pola_upsert(
        conn,
        id_=id_,
        user_id=user_id,
        scope=scope,
        content=rapi,
        confidence=confidence.quantize(Decimal("0.001")),
        evidence_count=evidence_count,
        model_version=model_version,
    )


async def luruhkan_pola(conn: AsyncConnection, user_id: UUID, id_: UUID) -> None:
    """Tandai pola tak lagi berlaku (data tak lagi mendukungnya) — idempoten, tak menghapus."""
    await repository.pola_luruh(conn, id_=id_, user_id=user_id)
