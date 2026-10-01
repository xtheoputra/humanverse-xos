"""SQL modul `intelligence` — hanya tabel miliknya: recommendations · recommendation_feedback."""

from __future__ import annotations

import json
from decimal import Decimal
from uuid import UUID

from sqlalchemy import text
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
