"""`memory.write` — spec/05 (tool R2): memori yang pengguna MINTA diingat.

`kind='semantic'` — fakta yang pengguna nyatakan tentang dirinya (naskah 15), keyakinan
1.000 dengan alasan yang sama dengan K-27: yang diyakini adalah BAHWA pengguna
menyatakannya, bukan bahwa isinya benar. Ditulis **hanya bila belum diingat**: isi yang
sama (spasinya dirapikan) di scope yang sama tidak melahirkan baris kedua — penilaian
kecil itulah yang membuat `memory-agent` agent, bukan service (arch/08 §2.2).

Modul ini hanya menjaga scope RESMI; scope mana yang boleh ditulis sebuah agent adalah
urusan manifest dan gerbang risiko (`agents`, 4.5) — `memory` tidak mengenal agent.
Vektornya disusul penyelaras (3.5), seperti memori episodik.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import identity, platform

from . import repository
from .ekstraksi import KEYAKINAN_LAPORAN_SENDIRI

ISI_MAKS = 4_000  # sama dengan catatan bebas lain (spec/04 `note`)


@dataclass(frozen=True)
class HasilIngat:
    id: UUID
    baru: bool  # False = isi yang sama sudah diingat di scope itu


async def ingat(
    engine: AsyncEngine, user_id: UUID, *, scope: str, isi: str, penulis: str
) -> HasilIngat:
    """`penulis` = agent dan versinya (`memory-agent@1.0.0`) — dicatat di `model_version`:
    CARA memori ini lahir, tempat ambang keyakinan #34 kelak membaca."""
    if scope not in identity.SCOPE_RESMI:
        raise ValueError("scope di luar daftar resmi spec/05")
    rapi = " ".join(isi.split())
    if not rapi or len(rapi) > ISI_MAKS:
        raise ValueError(f"isi memori wajib 1–{ISI_MAKS} karakter")
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        id_, baru = await repository.ingat(
            conn,
            user_id=user_id,
            scope=scope,
            content=rapi,
            confidence=KEYAKINAN_LAPORAN_SENDIRI,
            model_version=penulis,
        )
    return HasilIngat(id_, baru)
