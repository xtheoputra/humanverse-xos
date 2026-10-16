"""SQL modul `intelligence` — hanya tabel miliknya: recommendations · recommendation_feedback."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import Row, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import RekomendasiRingkas, UmpanBalik

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


# ── Umpan balik (5.6): recommendation_feedback append-only + status rekomendasi ──

_STATUS_REKOMENDASI = text("SELECT status FROM recommendations WHERE id = :id")

_SISIP_UMPAN_BALIK = text(
    """
    INSERT INTO recommendation_feedback (recommendation_id, user_id, action, reason, outcome)
    VALUES (:recommendation_id, :user_id, :action, :reason, CAST(:outcome AS jsonb))
    RETURNING id, recommendation_id, action, reason, outcome, created_at
    """
)

_SET_STATUS = text(
    "UPDATE recommendations SET status = :status WHERE id = :id AND user_id = :user_id"
)

_UMPAN_BALIK_ID = text(
    """
    SELECT id, recommendation_id, action, reason, outcome, created_at
    FROM recommendation_feedback WHERE id = :id
    """
)


async def status_rekomendasi(conn: AsyncConnection, id_: UUID) -> str | None:
    """Status rekomendasi — `None` bila tak ada / bukan milik pengguna (RLS)."""
    baris = (await conn.execute(_STATUS_REKOMENDASI, {"id": id_})).first()
    return baris.status if baris else None


async def sisip_umpan_balik(
    conn: AsyncConnection,
    *,
    rekomendasi_id: UUID,
    user_id: UUID,
    action: str,
    reason: str | None,
    outcome: Mapping[str, Any],
) -> UmpanBalik:
    baris = (
        await conn.execute(
            _SISIP_UMPAN_BALIK,
            {
                "recommendation_id": rekomendasi_id,
                "user_id": user_id,
                "action": action,
                "reason": reason,
                "outcome": json.dumps(outcome, ensure_ascii=False),
            },
        )
    ).one()
    return _umpan_balik(baris)


async def set_status_rekomendasi(
    conn: AsyncConnection, id_: UUID, user_id: UUID, status: str
) -> None:
    await conn.execute(_SET_STATUS, {"id": id_, "user_id": user_id, "status": status})


async def umpan_balik_id(conn: AsyncConnection, id_: UUID) -> UmpanBalik | None:
    baris = (await conn.execute(_UMPAN_BALIK_ID, {"id": id_})).first()
    return _umpan_balik(baris) if baris else None


def _umpan_balik(baris: Row[Any]) -> UmpanBalik:
    return UmpanBalik(
        id=baris.id,
        recommendation_id=baris.recommendation_id,
        action=baris.action,
        reason=baris.reason,
        outcome=baris.outcome,
        created_at=baris.created_at,
    )


# ── Daftar rekomendasi & tandai terlihat (6.1 Dashboard, spec/04 Rekomendasi) ──

_DAFTAR_REKOMENDASI = text(
    """
    SELECT id, domain, subject_type, subject_id, title, body, score, scoring_version,
           score_breakdown, confidence, rationale, status, created_at
    FROM recommendations
    WHERE user_id = :user_id
      AND (CAST(:status AS text) IS NULL OR status = :status)
      AND (CAST(:domain AS text) IS NULL OR domain = :domain)
    ORDER BY created_at DESC, id DESC
    LIMIT :limit
    """
)

# pending → shown (sekali): rekomendasi yang sudah diubah pengguna tak ditarik mundur.
_TANDAI_TERLIHAT = text(
    """
    UPDATE recommendations SET status = 'shown', shown_at = now()
    WHERE id = :id AND user_id = :user_id AND status = 'pending'
    """
)


async def daftar_rekomendasi(
    conn: AsyncConnection,
    user_id: UUID,
    *,
    status: str | None,
    domain: str | None,
    limit: int,
) -> list[RekomendasiRingkas]:
    baris = (
        await conn.execute(
            _DAFTAR_REKOMENDASI,
            {"user_id": user_id, "status": status, "domain": domain, "limit": limit},
        )
    ).all()
    return [_rekomendasi_ringkas(b) for b in baris]


async def tandai_terlihat(conn: AsyncConnection, id_: UUID, user_id: UUID) -> None:
    """Tandai sebuah rekomendasi `shown` bila masih `pending` — no-op bila bukan."""
    await conn.execute(_TANDAI_TERLIHAT, {"id": id_, "user_id": user_id})


def _rekomendasi_ringkas(baris: Row[Any]) -> RekomendasiRingkas:
    return RekomendasiRingkas(
        id=baris.id,
        domain=baris.domain,
        subject_type=baris.subject_type,
        subject_id=baris.subject_id,
        title=baris.title,
        body=baris.body,
        score=float(baris.score) if baris.score is not None else None,
        scoring_version=baris.scoring_version,
        score_breakdown=baris.score_breakdown,
        confidence=float(baris.confidence) if baris.confidence is not None else None,
        rationale=baris.rationale,
        status=baris.status,
        created_at=baris.created_at,
    )
