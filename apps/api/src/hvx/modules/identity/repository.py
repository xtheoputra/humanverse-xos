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


# ── consents (spec/07 1.4) ──────────────────────────────────────────────────
# `created_at = clock_timestamp()`, bukan bawaan `now()`: now() membeku di awal
# transaksi, sehingga "cabut lalu setujui lagi" dalam satu transaksi akan punya
# waktu yang SAMA — dan urutan riwayat yang hanya-tambah jadi tak tentu.
_SISIP_PERSETUJUAN = text(
    """
    INSERT INTO consents
      (user_id, kind, purpose, data_scopes, granted, policy_version, source,
       granted_at, revoked_at, expires_at, created_at)
    VALUES
      (:user_id, :kind, :purpose, :data_scopes, :granted, :policy_version, :source,
       CASE WHEN :granted THEN clock_timestamp() END,
       CASE WHEN :dicabut THEN clock_timestamp() END,
       :expires_at, clock_timestamp())
    """
)

# Satu baris TERAKHIR per tujuan — riwayat hanya-tambah dibaca dari ujungnya.
_PERSETUJUAN_TERAKHIR = text(
    """
    SELECT DISTINCT ON (purpose) purpose, granted, data_scopes, expires_at,
           (expires_at IS NULL OR expires_at > now()) AS masih_berlaku
    FROM consents
    WHERE user_id = :user_id AND purpose = ANY(:tujuan)
    ORDER BY purpose, created_at DESC
    """
)


async def tambah_persetujuan(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    kind: str,
    purpose: str,
    data_scopes: list[str],
    granted: bool,
    dicabut: bool,
    policy_version: str,
    source: str,
    expires_at: object | None,
) -> None:
    await conn.execute(
        _SISIP_PERSETUJUAN,
        {
            "user_id": user_id,
            "kind": kind,
            "purpose": purpose,
            "data_scopes": data_scopes,
            "granted": granted,
            "dicabut": dicabut,
            "policy_version": policy_version,
            "source": source,
            "expires_at": expires_at,
        },
    )


async def persetujuan_terakhir(
    conn: AsyncConnection, user_id: UUID, tujuan: list[str]
) -> dict[str, tuple[bool, frozenset[str], bool]]:
    """{purpose: (granted, data_scopes, masih_berlaku)}; tujuan tanpa riwayat tidak muncul."""
    hasil = await conn.execute(_PERSETUJUAN_TERAKHIR, {"user_id": user_id, "tujuan": tujuan})
    return {
        b.purpose: (bool(b.granted), frozenset(b.data_scopes or ()), bool(b.masih_berlaku))
        for b in hasil
    }
