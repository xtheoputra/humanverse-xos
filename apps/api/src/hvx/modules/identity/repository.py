"""SQL modul `identity` — hanya tabel miliknya: users · consents · permissions · audit_logs.

spec/06 aturan 5, dijaga `tests/unit/test_batas_tabel.py`: berkas di modul ini
tidak boleh menyebut tabel milik modul lain.

Tiap fungsi menerima `AsyncConnection` dari pemanggil — transaksinya milik
lapisan layanan (`platform.transaksi_pengguna`), bukan milik repository, supaya
satu tindakan pengguna bisa menulis beberapa tabel secara atomik.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import PenggunaRingkas

_SISIP_AUDIT = text(
    """
    INSERT INTO audit_logs
      (data_subject, actor_type, actor_id, user_id, action,
       subject_type, subject_id, request_id, ip_hash, metadata)
    VALUES
      (:data_subject, :actor_type, :actor_id, :user_id, :action,
       :subject_type, :subject_id, :request_id, :ip_hash, CAST(:metadata AS jsonb))
    """
)


async def tambah_audit(
    conn: AsyncConnection,
    *,
    data_subject: str,
    aktor_tipe: str,
    aktor_id: str,
    user_id: UUID | None,
    aksi: str,
    subjek_tipe: str | None,
    subjek_id: str | None,
    request_id: str | None,
    ip_hash: str | None,
    metadata: Mapping[str, object],
) -> None:
    await conn.execute(
        _SISIP_AUDIT,
        {
            "data_subject": data_subject,
            "actor_type": aktor_tipe,
            "actor_id": aktor_id,
            "user_id": user_id,
            "action": aksi,
            "subject_type": subjek_tipe,
            "subject_id": subjek_id,
            "request_id": request_id,
            "ip_hash": ip_hash,
            "metadata": json.dumps(dict(metadata)),
        },
    )


_PENGGUNA = text(
    """
    SELECT id, email::text AS email, status, email_verified_at, created_at
    FROM users
    WHERE id = :user_id AND deleted_at IS NULL
    """
)


async def ambil_pengguna(conn: AsyncConnection, user_id: UUID) -> PenggunaRingkas | None:
    baris = (await conn.execute(_PENGGUNA, {"user_id": user_id})).mappings().first()
    return PenggunaRingkas.model_validate(dict(baris)) if baris else None
