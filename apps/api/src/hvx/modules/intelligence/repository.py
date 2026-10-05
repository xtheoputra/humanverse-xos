"""SQL modul `intelligence` — hanya tabel miliknya: recommendations · recommendation_feedback."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncConnection

_SISIP = text(
    """
    INSERT INTO recommendations (user_id, agent_id, agent_run_id, domain, title, body,
                                 confidence, rationale)
    VALUES (:user_id, :agent_id, :agent_run_id, :domain, :title, :body, :confidence,
            CAST(:rationale AS jsonb))
    RETURNING id
    """
)


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    agent_id: UUID,
    agent_run_id: UUID | None,
    domain: str,
    title: str,
    body: str | None,
    confidence: Decimal,
    rationale: list[str],
) -> UUID:
    baris = (
        await conn.execute(
            _SISIP,
            {
                "user_id": user_id,
                "agent_id": agent_id,
                "agent_run_id": agent_run_id,
                "domain": domain,
                "title": title,
                "body": body,
                "confidence": confidence,
                "rationale": json.dumps(rationale, ensure_ascii=False),
            },
        )
    ).one()
    hasil: UUID = baris.id
    return hasil


# Jalur MESIN (5.5): rekomendasi bersistem dengan `score` terhitung — bukan dari agent,
# jadi `agent_id`/`confidence` dibiarkan kosong. `id` deterministik + ON CONFLICT DO
# NOTHING: event yang disalurkan ulang tidak menumpuk, status pengguna tidak tertimpa.
_SISIP_MESIN = text(
    """
    INSERT INTO recommendations
      (id, user_id, domain, subject_type, subject_id, title, body,
       score, scoring_version, score_breakdown, rationale, context_snapshot)
    VALUES
      (:id, :user_id, :domain, :subject_type, :subject_id, :title, :body,
       :score, :scoring_version, CAST(:score_breakdown AS jsonb),
       CAST(:rationale AS jsonb), CAST(:context_snapshot AS jsonb))
    ON CONFLICT (id) DO NOTHING
    RETURNING id
    """
)

_PENDING_MESIN = text(
    """
    SELECT id, subject_id, context_snapshot
    FROM recommendations
    WHERE user_id = :user_id
      AND scoring_version = :scoring_version
      AND status = 'pending'
      AND subject_type = 'habit'
      AND context_snapshot->>'for_date' = :for_date
    """
)

_PERBARUI_SKOR = text(
    """
    UPDATE recommendations
    SET score = :score,
        score_breakdown = CAST(:score_breakdown AS jsonb),
        context_snapshot = CAST(:context_snapshot AS jsonb)
    WHERE id = :id AND user_id = :user_id AND status = 'pending'
    """
)


async def sisip_mesin(
    conn: AsyncConnection,
    *,
    id_: UUID,
    user_id: UUID,
    domain: str,
    subject_type: str,
    subject_id: UUID,
    title: str,
    body: str | None,
    score: Decimal,
    scoring_version: str,
    score_breakdown: Mapping[str, Any],
    rationale: Sequence[str],
    context_snapshot: Mapping[str, Any],
) -> UUID | None:
    """Sisip rekomendasi mesin; `None` bila sudah ada (idempoten, ON CONFLICT DO NOTHING)."""
    baris = (
        await conn.execute(
            _SISIP_MESIN,
            {
                "id": id_,
                "user_id": user_id,
                "domain": domain,
                "subject_type": subject_type,
                "subject_id": subject_id,
                "title": title,
                "body": body,
                "score": score,
                "scoring_version": scoring_version,
                "score_breakdown": json.dumps(score_breakdown, ensure_ascii=False),
                "rationale": json.dumps(list(rationale), ensure_ascii=False),
                "context_snapshot": json.dumps(context_snapshot, ensure_ascii=False),
            },
        )
    ).first()
    return baris.id if baris else None


async def pending_mesin(
    conn: AsyncConnection, user_id: UUID, scoring_version: str, for_date: str
) -> Sequence[Row[Any]]:
    """Rekomendasi mesin yang MASIH pending untuk (pengguna, versi, tanggal)."""
    return (
        await conn.execute(
            _PENDING_MESIN,
            {"user_id": user_id, "scoring_version": scoring_version, "for_date": for_date},
        )
    ).all()


async def perbarui_skor(
    conn: AsyncConnection,
    id_: UUID,
    user_id: UUID,
    *,
    score: Decimal,
    score_breakdown: Mapping[str, Any],
    context_snapshot: Mapping[str, Any],
) -> None:
    """Hitung ulang skor sebuah rekomendasi yang masih pending — status tidak disentuh."""
    await conn.execute(
        _PERBARUI_SKOR,
        {
            "id": id_,
            "user_id": user_id,
            "score": score,
            "score_breakdown": json.dumps(score_breakdown, ensure_ascii=False),
            "context_snapshot": json.dumps(context_snapshot, ensure_ascii=False),
        },
    )
