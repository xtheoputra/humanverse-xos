"""SQL modul `agents` — hanya tabel miliknya: agents · agent_tools · agent_runs ·
ai_conversations · ai_messages (spec/06 aturan 5).

Katalog (`agents`, `agent_tools`) dibaca `registri.pastikan_katalog`; yang di sini
adalah jejak tiap run (`agent_runs`, spec/07 4.4) — AI Audit Trail naskah 5 §24.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

_MULAI_RUN = text(
    """
    INSERT INTO agent_runs (id, user_id, agent_id, agent_version, conversation_id,
                            parent_run_id, trigger)
    VALUES (:id, :user_id, :agent_id, :agent_version, :conversation_id, :parent_run_id,
            :trigger)
    """
)
# Hanya run yang masih `running` yang bisa diselesaikan — sekali. Jam basis data:
# `started_at` juga dari sana (DEFAULT now()).
_SELESAI_RUN = text(
    """
    UPDATE agent_runs
    SET status = :status, tools_used = :tools_used, memory_scopes = :memory_scopes,
        model_used = :model_used, risk_level = :risk_level,
        confirmed_by_user = :confirmed_by_user, decision = CAST(:decision AS jsonb),
        confidence = :confidence, error = CAST(:error AS jsonb), tokens_in = :tokens_in,
        tokens_out = :tokens_out, cost_usd = :cost_usd, latency_ms = :latency_ms,
        finished_at = clock_timestamp()
    WHERE id = :id AND status = 'running'
    """
)
_BACA_RUN = text(
    """
    SELECT id, agent_id, agent_version, conversation_id, parent_run_id, trigger, status,
           tools_used, memory_scopes, model_used, risk_level, confirmed_by_user, decision,
           confidence, error, tokens_in, tokens_out, cost_usd, latency_ms, started_at,
           finished_at
    FROM agent_runs WHERE id = :id
    """
)


@dataclass(frozen=True)
class BarisRun:
    id: UUID
    agent_id: UUID
    agent_version: str
    conversation_id: UUID | None
    parent_run_id: UUID | None
    trigger: str
    status: str
    tools_used: list[str]
    memory_scopes: list[str]
    model_used: str | None
    risk_level: int | None
    confirmed_by_user: bool | None
    decision: dict[str, Any]
    confidence: Decimal | None
    error: dict[str, Any] | None
    tokens_in: int | None
    tokens_out: int | None
    cost_usd: Decimal | None
    latency_ms: int | None
    started_at: datetime
    finished_at: datetime | None


async def mulai_run(
    conn: AsyncConnection,
    *,
    id: UUID,
    user_id: UUID,
    agent_id: UUID,
    agent_version: str,
    conversation_id: UUID | None,
    parent_run_id: UUID | None,
    trigger: str,
) -> None:
    await conn.execute(
        _MULAI_RUN,
        {
            "id": id,
            "user_id": user_id,
            "agent_id": agent_id,
            "agent_version": agent_version,
            "conversation_id": conversation_id,
            "parent_run_id": parent_run_id,
            "trigger": trigger,
        },
    )


async def selesai_run(
    conn: AsyncConnection,
    *,
    id: UUID,
    status: str,
    tools_used: Sequence[str],
    memory_scopes: Sequence[str],
    model_used: str | None,
    risk_level: int | None,
    confirmed_by_user: bool | None,
    decision: Mapping[str, Any],
    confidence: Decimal | None,
    error: Mapping[str, Any] | None,
    tokens_in: int,
    tokens_out: int,
    cost_usd: Decimal,
    latency_ms: int,
) -> bool:
    """False = run itu sudah selesai (atau bukan milik pengguna transaksi ini)."""
    hasil = await conn.execute(
        _SELESAI_RUN,
        {
            "id": id,
            "status": status,
            "tools_used": list(tools_used),
            "memory_scopes": list(memory_scopes),
            "model_used": model_used,
            "risk_level": risk_level,
            "confirmed_by_user": confirmed_by_user,
            "decision": json.dumps(dict(decision), ensure_ascii=False),
            "confidence": confidence,
            "error": None if error is None else json.dumps(dict(error), ensure_ascii=False),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
        },
    )
    return hasil.rowcount == 1


async def baca_run(conn: AsyncConnection, run_id: UUID) -> BarisRun | None:
    baris = (await conn.execute(_BACA_RUN, {"id": run_id})).mappings().first()
    return None if baris is None else BarisRun(**baris)
