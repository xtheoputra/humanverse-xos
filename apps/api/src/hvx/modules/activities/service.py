"""Aturan `activities` — spec/07 3.8: *“`source='inferred'` terpisah dari `manual`”*.

* **Rute HTTP hanya menulis `manual`** — `CatatAktivitas` tidak punya medan
  `source`, dan repository menerima sumbernya dari parameter, bukan dari badan.
* **`inferred` hanya lewat `catat_disimpulkan`** — dipanggil Behavior Engine
  (Sprint 5), di transaksinya sendiri, dan TIDAK pernah dianggap fakta perilaku:
  spec/01, *“tanpa itu, mesin akan belajar dari tebakannya sendiri”*.
* **Tanpa event V0** (peta aturan 6, spec/06): spec/03 belum punya jenis ✅
  untuk aktivitas umum, dan jenis per `kind` (`workout.completed`, …) belum V0.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from . import repository
from .schemas import Aktivitas, CatatAktivitas, HalamanAktivitas

LONGGAR_JAM_S = 300
_BATAS_WAKTU = text("SELECT now() + make_interval(secs => :longgar)")


async def baca_aktivitas(
    engine: AsyncEngine, user_id: UUID, aktivitas_id: UUID
) -> Aktivitas | None:
    """Aktivitas itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.ambil(conn, aktivitas_id)


async def catat(engine: AsyncEngine, user_id: UUID, badan: CatatAktivitas) -> Aktivitas:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            batas = (await conn.execute(_BATAS_WAKTU, {"longgar": LONGGAR_JAM_S})).scalar_one()
            if badan.occurred_at > batas:
                raise platform.GalatApi(
                    422, "occurred_at_in_future", "Waktu aktivitas itu belum terjadi."
                )
            if badan.ended_at is not None and badan.ended_at > batas:
                raise platform.GalatApi(422, "ended_at_in_future", "Aktivitas itu belum selesai.")
            return await repository.sisip(
                conn,
                user_id=user_id,
                id_=badan.id,
                kind=badan.kind,
                occurred_at=badan.occurred_at,
                ended_at=badan.ended_at,
                duration_seconds=badan.duration_seconds,
                source="manual",
                payload=badan.payload,
            )
    except IntegrityError as galat:
        p = platform.rincian_pelanggaran(galat)
        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "activities_pkey":
            raise platform.GalatApi(
                409, "already_exists", "Aktivitas dengan id ini sudah ada."
            ) from None
        raise


async def catat_disimpulkan(
    conn: AsyncConnection,
    user_id: UUID,
    *,
    kind: str,
    occurred_at: datetime,
    ended_at: datetime | None = None,
    duration_seconds: int | None = None,
    payload: dict[str, Any] | None = None,
) -> Aktivitas:
    """Aktivitas yang DITEBAK sistem — selalu `source='inferred'` (spec/07 3.8)."""
    return await repository.sisip(
        conn,
        user_id=user_id,
        id_=None,
        kind=kind,
        occurred_at=occurred_at,
        ended_at=ended_at,
        duration_seconds=duration_seconds,
        source="inferred",
        payload=payload or {},
    )


async def daftar(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    kind: str | None,
    source: str | None,
    dari: datetime | None,
    sampai: datetime | None,
    batas: int,
    kursor: str | None,
) -> HalamanAktivitas:
    if dari is not None and sampai is not None and dari >= sampai:
        raise platform.GalatApi(400, "invalid_request", "`from` wajib sebelum `to`.")
    sesudah = platform.baca_kursor_waktu("activities", kursor)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        aktivitas = await repository.daftar(
            conn,
            user_id=user_id,
            kind=kind,
            source=source,
            dari=dari,
            sampai=sampai,
            sesudah=sesudah,
            batas=batas + 1,
        )
    lanjut = None
    if len(aktivitas) > batas:
        aktivitas = aktivitas[:batas]
        lanjut = platform.kursor_waktu("activities", aktivitas[-1].occurred_at, aktivitas[-1].id)
    return HalamanAktivitas(items=aktivitas, next_cursor=lanjut)
