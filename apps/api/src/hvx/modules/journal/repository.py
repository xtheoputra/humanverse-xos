"""SQL modul `journal` — hanya tabel miliknya: journal_entries (spec/06 aturan 5).

🔒 Kueri DAFTAR tidak memilih `body` sama sekali (spec/04): isi tulisan pribadi
tidak pernah sampai ke memori proses untuk permintaan yang tidak membutuhkannya.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Jurnal, RingkasanJurnal

_SISIP = text(
    """
    INSERT INTO journal_entries (id, user_id, occurred_at, title, body, word_count)
    VALUES (COALESCE(CAST(:id AS uuid), gen_random_uuid()), :user_id,
            COALESCE(CAST(:occurred_at AS timestamptz), now()), CAST(:title AS text), :body,
            :word_count)
    RETURNING id, title, body, occurred_at, word_count, created_at, updated_at
    """
)

_AMBIL = text(
    """
    SELECT id, title, body, occurred_at, word_count, created_at, updated_at
    FROM journal_entries
    WHERE id = :id AND deleted_at IS NULL
    """
)

_DAFTAR = text(
    """
    SELECT id, title, occurred_at, word_count, created_at, updated_at
    FROM journal_entries
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:dari AS timestamptz) IS NULL OR occurred_at >= CAST(:dari AS timestamptz))
      AND (CAST(:sampai AS timestamptz) IS NULL OR occurred_at < CAST(:sampai AS timestamptz))
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (occurred_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY occurred_at DESC, id DESC
    LIMIT :batas
    """
)

_UBAH = text(
    """
    UPDATE journal_entries SET
      title = CASE WHEN :ubah_title THEN CAST(:title AS text) ELSE title END,
      body = CASE WHEN :ubah_body THEN CAST(:body AS text) ELSE body END,
      word_count = CASE WHEN :ubah_body THEN CAST(:word_count AS integer) ELSE word_count END,
      occurred_at = CASE WHEN :ubah_occurred_at THEN CAST(:occurred_at AS timestamptz)
                         ELSE occurred_at END
    WHERE id = :id AND deleted_at IS NULL
    RETURNING id, title, body, occurred_at, word_count, created_at, updated_at
    """
)

_HAPUS = text(
    """
    UPDATE journal_entries SET deleted_at = now()
    WHERE id = :id AND deleted_at IS NULL
    RETURNING id
    """
)


def _jurnal(baris: RowMapping) -> Jurnal:
    return Jurnal.model_validate(dict(baris))


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    id_: UUID | None,
    title: str | None,
    body: str,
    word_count: int,
    occurred_at: datetime | None,
) -> Jurnal:
    baris = (
        (
            await conn.execute(
                _SISIP,
                {
                    "id": id_,
                    "user_id": user_id,
                    "title": title,
                    "body": body,
                    "word_count": word_count,
                    "occurred_at": occurred_at,
                },
            )
        )
        .mappings()
        .one()
    )
    return _jurnal(baris)


async def ambil(conn: AsyncConnection, jurnal_id: UUID) -> Jurnal | None:
    baris = (await conn.execute(_AMBIL, {"id": jurnal_id})).mappings().first()
    return _jurnal(baris) if baris else None


async def daftar(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    dari: datetime | None,
    sampai: datetime | None,
    sesudah: tuple[datetime, UUID] | None,
    batas: int,
) -> list[RingkasanJurnal]:
    hasil = await conn.execute(
        _DAFTAR,
        {
            "user_id": user_id,
            "dari": dari,
            "sampai": sampai,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [RingkasanJurnal.model_validate(dict(b)) for b in hasil.mappings()]


async def ubah(
    conn: AsyncConnection, jurnal_id: UUID, perubahan: dict[str, Any], word_count: int | None
) -> Jurnal | None:
    nilai: dict[str, Any] = {"id": jurnal_id, "word_count": word_count}
    for k in ("title", "body", "occurred_at"):
        nilai[f"ubah_{k}"] = k in perubahan
        nilai[k] = perubahan.get(k)
    baris = (await conn.execute(_UBAH, nilai)).mappings().first()
    return _jurnal(baris) if baris else None


async def hapus(conn: AsyncConnection, jurnal_id: UUID) -> bool:
    return (await conn.execute(_HAPUS, {"id": jurnal_id})).first() is not None
