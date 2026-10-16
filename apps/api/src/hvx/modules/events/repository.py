"""SQL modul `events` — hanya tabel miliknya: events (spec/06 aturan 5).

`events` HANYA-TAMBAH bagi peran aplikasi (spec/01 §10, spec/02 aturan C):
berkas ini tidak punya satu pun `UPDATE` atau `DELETE`, dan basis data menolaknya
kalaupun ada.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncConnection

# `recorded_at = clock_timestamp()`, bukan bawaan `now()`: now() membeku di awal
# transaksi, jadi event yang disisipkan di ujung transaksi panjang tercatat
# "diterima" sebelum event transaksi lain yang sudah lebih dulu commit — dan
# relay yang membaca menurut `recorded_at` (tugas 3.3) melompatinya.
# `ON CONFLICT DO NOTHING`: event ganda DITELAN (spec/03 aturan 1) — kunci yang
# sama untuk pengguna yang sama tidak menulis baris kedua dan tidak menjadi galat.
_SISIP = text(
    """
    INSERT INTO events (user_id, event_type, schema_version, occurred_at, recorded_at,
                        source, idempotency_key, subject_type, subject_id, payload)
    VALUES (:user_id, :event_type, :schema_version, :occurred_at, clock_timestamp(),
            :source, :kunci, CAST(:subject_type AS text), CAST(:subject_id AS uuid),
            CAST(:payload AS jsonb))
    ON CONFLICT (user_id, idempotency_key) DO NOTHING
    RETURNING id
    """
)

_MENURUT_KUNCI = text(
    """
    SELECT id, event_type, subject_type, subject_id, payload
    FROM events
    WHERE user_id = :user_id AND idempotency_key = :kunci
    """
)


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    event_type: str,
    schema_version: int,
    occurred_at: datetime,
    source: str,
    kunci: str,
    subject_type: str | None,
    subject_id: UUID | None,
    payload: dict[str, Any],
) -> UUID | None:
    """id event BARU — atau `None` bila kunci itu sudah pernah diterbitkan."""
    nilai = (
        await conn.execute(
            _SISIP,
            {
                "user_id": user_id,
                "event_type": event_type,
                "schema_version": schema_version,
                "occurred_at": occurred_at,
                "source": source,
                "kunci": kunci,
                "subject_type": subject_type,
                "subject_id": subject_id,
                "payload": json.dumps(payload, sort_keys=True),
            },
        )
    ).scalar_one_or_none()
    return nilai if isinstance(nilai, UUID) else None


async def menurut_kunci(conn: AsyncConnection, user_id: UUID, kunci: str) -> Row[Any] | None:
    return (await conn.execute(_MENURUT_KUNCI, {"user_id": user_id, "kunci": kunci})).first()
