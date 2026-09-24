"""SQL modul `activities` — hanya tabel miliknya: activities (spec/06 aturan 5).

`source` ditulis dari PARAMETER fungsi, tidak pernah dari badan permintaan:
rute HTTP memanggil dengan `manual`, jalur sistem (`catat_disimpulkan`) dengan
`inferred` — tidak ada satu jalur pun yang memilih keduanya dari masukan klien.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Aktivitas

_SISIP = text(
    """
    INSERT INTO activities (id, user_id, kind, occurred_at, ended_at, duration_seconds,
                            source, payload)
    VALUES (COALESCE(CAST(:id AS uuid), gen_random_uuid()), :user_id, :kind, :occurred_at,
            CAST(:ended_at AS timestamptz), CAST(:duration_seconds AS integer), :source,
            CAST(:payload AS jsonb))
    RETURNING id, kind, occurred_at, ended_at, duration_seconds, source, payload, created_at
    """
)

_AMBIL = text(
    """
    SELECT id, kind, occurred_at, ended_at, duration_seconds, source, payload, created_at
    FROM activities
    WHERE id = :id AND deleted_at IS NULL
    """
)

_DAFTAR = text(
    """
    SELECT id, kind, occurred_at, ended_at, duration_seconds, source, payload, created_at
    FROM activities
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:kind AS text) IS NULL OR kind = CAST(:kind AS text))
      AND (CAST(:source AS text) IS NULL OR source = CAST(:source AS text))
      AND (CAST(:dari AS timestamptz) IS NULL OR occurred_at >= CAST(:dari AS timestamptz))
      AND (CAST(:sampai AS timestamptz) IS NULL OR occurred_at < CAST(:sampai AS timestamptz))
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (occurred_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY occurred_at DESC, id DESC
    LIMIT :batas
    """
)


async def ambil(conn: AsyncConnection, aktivitas_id: UUID) -> Aktivitas | None:
    baris = (await conn.execute(_AMBIL, {"id": aktivitas_id})).mappings().first()
    return Aktivitas.model_validate(dict(baris)) if baris else None


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    id_: UUID | None,
    kind: str,
    occurred_at: datetime,
    ended_at: datetime | None,
    duration_seconds: int | None,
    source: str,
    payload: dict[str, Any],
) -> Aktivitas:
    baris = (
        (
            await conn.execute(
                _SISIP,
                {
                    "id": id_,
                    "user_id": user_id,
                    "kind": kind,
                    "occurred_at": occurred_at,
                    "ended_at": ended_at,
                    "duration_seconds": duration_seconds,
                    "source": source,
                    "payload": json.dumps(payload),
                },
            )
        )
        .mappings()
        .one()
    )
    return Aktivitas.model_validate(dict(baris))


async def daftar(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    kind: str | None,
    source: str | None,
    dari: datetime | None,
    sampai: datetime | None,
    sesudah: tuple[datetime, UUID] | None,
    batas: int,
) -> list[Aktivitas]:
    hasil = await conn.execute(
        _DAFTAR,
        {
            "user_id": user_id,
            "kind": kind,
            "source": source,
            "dari": dari,
            "sampai": sampai,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [Aktivitas.model_validate(dict(b)) for b in hasil.mappings()]
