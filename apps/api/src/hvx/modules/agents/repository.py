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
# Jawaban pengguna atas run yang ditahan gerbang (4.5) — SEKALI: hanya run `blocked`
# yang belum dijawab.
_JAWAB_RUN = text(
    """
    UPDATE agent_runs SET confirmed_by_user = :setuju
    WHERE id = :id AND status = 'blocked' AND confirmed_by_user IS NULL
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


async def jawab_run(conn: AsyncConnection, run_id: UUID, setuju: bool) -> bool:
    """False = run itu tidak menunggu jawaban (sudah dijawab, tidak ditahan, bukan miliknya)."""
    hasil = await conn.execute(_JAWAB_RUN, {"id": run_id, "setuju": setuju})
    return hasil.rowcount == 1


# ── Percakapan (spec/07 4.8) — ai_conversations · ai_messages ─────────────────
# `user_id = :user_id` di tiap kueri DI SAMPING RLS — pertahanan kedua, sama dengan
# modul domain lain. Pesan bercap `clock_timestamp()`: dua pesan satu transaksi
# (pesan pengguna + balasan deterministik) tidak berbagi waktu `now()`. 🔧 E-213: cap itu
# MONOTON per percakapan — `GREATEST(clock_timestamp(), last_message_at + 1 µs)`, di bawah
# kunci `FOR UPDATE` percakapannya (`kunci_percakapan`). Jam basis data bisa melangkah
# mundur (VM Docker: ±3 dtk tiap ±28 dtk, diukur tinjauan Sprint 4) — dulu balasan tampil
# LEBIH TUA dari pertanyaannya di riwayat yang terurut `(created_at, id)`.

_BUAT_PERCAKAPAN = text(
    """
    INSERT INTO ai_conversations (id, user_id, title) VALUES (:id, :user_id, :title)
    RETURNING id, title, started_at, last_message_at, message_count, created_at
    """
)
_BACA_PERCAKAPAN = text(
    """
    SELECT id, title, started_at, last_message_at, message_count, created_at FROM ai_conversations
    WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
    """
)
# Giliran baru mengunci percakapannya — dua pesan serentak tidak berebut satu giliran.
_KUNCI_PERCAKAPAN = text(
    """
    SELECT id FROM ai_conversations
    WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
    FOR UPDATE
    """
)
_DAFTAR_PERCAKAPAN = text(
    """
    SELECT id, title, started_at, last_message_at, message_count, created_at FROM ai_conversations
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (created_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY created_at DESC, id DESC
    LIMIT :batas
    """
)
_SENTUH_PERCAKAPAN = text(
    """
    UPDATE ai_conversations
    SET last_message_at = :waktu, message_count = message_count + 1
    WHERE id = :id AND user_id = :user_id
    """
)
_SISIP_PESAN = text(
    """
    INSERT INTO ai_messages (id, conversation_id, user_id, role, content, agent_run_id, model,
                             tokens_in, tokens_out, latency_ms, cost_usd, confidence, rationale,
                             created_at)
    VALUES (:id, :conversation_id, :user_id, :role, :content, :agent_run_id, :model,
            :tokens_in, :tokens_out, :latency_ms, :cost_usd, :confidence,
            CAST(:rationale AS jsonb),
            GREATEST(clock_timestamp(),
                     (SELECT last_message_at + interval '1 microsecond' FROM ai_conversations
                      WHERE id = :conversation_id AND user_id = :user_id)))
    RETURNING id, conversation_id, role, content, agent_run_id, model, tokens_in, tokens_out,
           latency_ms, cost_usd, confidence, rationale, created_at
    """
)
_BACA_PESAN = text(
    """
    SELECT id, conversation_id, role, content, agent_run_id, model, tokens_in, tokens_out,
           latency_ms, cost_usd, confidence, rationale, created_at
    FROM ai_messages WHERE id = :id AND user_id = :user_id
    """
)
_DAFTAR_PESAN = text(
    """
    SELECT id, conversation_id, role, content, agent_run_id, model, tokens_in, tokens_out,
           latency_ms, cost_usd, confidence, rationale, created_at FROM ai_messages
    WHERE conversation_id = :conversation_id AND user_id = :user_id
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (created_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY created_at DESC, id DESC
    LIMIT :batas
    """
)
# Pesan satu giliran berbagi run AKARNYA: pesan pengguna dan balasannya.
_PESAN_RUN = text(
    """
    SELECT id, conversation_id, role, content, agent_run_id, model, tokens_in, tokens_out,
           latency_ms, cost_usd, confidence, rationale, created_at FROM ai_messages
    WHERE agent_run_id = :run_id AND user_id = :user_id AND role = :role
    ORDER BY created_at DESC LIMIT 1
    """
)
_AKAR_RUN = text(
    """
    WITH RECURSIVE naik AS (
      SELECT id, parent_run_id, conversation_id FROM agent_runs
      WHERE id = :run_id AND user_id = :user_id
      UNION ALL
      SELECT a.id, a.parent_run_id, a.conversation_id
      FROM agent_runs a JOIN naik n ON a.id = n.parent_run_id
    )
    SELECT id, conversation_id FROM naik WHERE parent_run_id IS NULL
    """
)


@dataclass(frozen=True)
class BarisPercakapan:
    id: UUID
    title: str | None
    started_at: datetime
    last_message_at: datetime | None
    message_count: int
    created_at: datetime


@dataclass(frozen=True)
class BarisPesan:
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    agent_run_id: UUID | None
    model: str | None
    tokens_in: int | None
    tokens_out: int | None
    latency_ms: int | None
    cost_usd: Decimal | None
    confidence: Decimal | None
    rationale: list[str]
    created_at: datetime


async def buat_percakapan(
    conn: AsyncConnection, *, id: UUID, user_id: UUID, title: str | None
) -> BarisPercakapan:
    hasil = await conn.execute(_BUAT_PERCAKAPAN, {"id": id, "user_id": user_id, "title": title})
    return BarisPercakapan(**hasil.mappings().one())


async def baca_percakapan(
    conn: AsyncConnection, user_id: UUID, percakapan_id: UUID
) -> BarisPercakapan | None:
    hasil = await conn.execute(_BACA_PERCAKAPAN, {"id": percakapan_id, "user_id": user_id})
    baris = hasil.mappings().first()
    return None if baris is None else BarisPercakapan(**baris)


async def kunci_percakapan(conn: AsyncConnection, user_id: UUID, percakapan_id: UUID) -> bool:
    hasil = await conn.execute(_KUNCI_PERCAKAPAN, {"id": percakapan_id, "user_id": user_id})
    return hasil.first() is not None


async def daftar_percakapan(
    conn: AsyncConnection, user_id: UUID, *, batas: int, sesudah: tuple[datetime, UUID] | None
) -> list[BarisPercakapan]:
    hasil = await conn.execute(
        _DAFTAR_PERCAKAPAN,
        {
            "user_id": user_id,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [BarisPercakapan(**b) for b in hasil.mappings()]


async def sisip_pesan(
    conn: AsyncConnection,
    *,
    id: UUID,
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    agent_run_id: UUID | None = None,
    model: str | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    latency_ms: int | None = None,
    cost_usd: Decimal | None = None,
    confidence: Decimal | None = None,
    rationale: Sequence[str] = (),
) -> BarisPesan:
    hasil = await conn.execute(
        _SISIP_PESAN,
        {
            "id": id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "agent_run_id": agent_run_id,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "confidence": confidence,
            "rationale": json.dumps(list(rationale), ensure_ascii=False),
        },
    )
    pesan = BarisPesan(**hasil.mappings().one())
    await conn.execute(
        _SENTUH_PERCAKAPAN, {"id": conversation_id, "user_id": user_id, "waktu": pesan.created_at}
    )
    return pesan


async def baca_pesan(conn: AsyncConnection, user_id: UUID, pesan_id: UUID) -> BarisPesan | None:
    hasil = await conn.execute(_BACA_PESAN, {"id": pesan_id, "user_id": user_id})
    baris = hasil.mappings().first()
    return None if baris is None else BarisPesan(**baris)


async def daftar_pesan(
    conn: AsyncConnection,
    user_id: UUID,
    percakapan_id: UUID,
    *,
    batas: int,
    sesudah: tuple[datetime, UUID] | None,
) -> list[BarisPesan]:
    hasil = await conn.execute(
        _DAFTAR_PESAN,
        {
            "conversation_id": percakapan_id,
            "user_id": user_id,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [BarisPesan(**b) for b in hasil.mappings()]


async def pesan_run(
    conn: AsyncConnection, user_id: UUID, run_id: UUID, role: str
) -> BarisPesan | None:
    """Pesan `role` giliran yang run akarnya `run_id` — pesan pengguna atau balasannya."""
    hasil = await conn.execute(_PESAN_RUN, {"run_id": run_id, "user_id": user_id, "role": role})
    baris = hasil.mappings().first()
    return None if baris is None else BarisPesan(**baris)


async def akar_run(
    conn: AsyncConnection, user_id: UUID, run_id: UUID
) -> tuple[UUID, UUID | None] | None:
    """(id run akar, percakapannya) — pohon eksekusi ditelusuri naik dari `run_id`."""
    baris = (await conn.execute(_AKAR_RUN, {"run_id": run_id, "user_id": user_id})).first()
    return None if baris is None else (baris.id, baris.conversation_id)


# Yang dibayar satu giliran = seluruh pohon run-nya (SSE `done`, spec/04) — dibaca dari
# baris yang SUDAH ditutup, jadi run anak yang ditahan gerbang pun ikut terhitung.
_RINGKAS_POHON = text(
    """
    WITH RECURSIVE pohon AS (
      SELECT id, model_used, tokens_in, tokens_out, cost_usd FROM agent_runs
      WHERE id = :run_id AND user_id = :user_id
      UNION ALL
      SELECT a.id, a.model_used, a.tokens_in, a.tokens_out, a.cost_usd
      FROM agent_runs a JOIN pohon p ON a.parent_run_id = p.id
    )
    SELECT coalesce(sum(cost_usd), 0) AS biaya, coalesce(sum(tokens_in), 0) AS masuk,
           coalesce(sum(tokens_out), 0) AS keluar, string_agg(DISTINCT model_used, ',') AS model
    FROM pohon
    """
)


@dataclass(frozen=True)
class RingkasanPohon:
    biaya: Decimal
    masuk: int
    keluar: int
    model: str | None


async def ringkas_pohon(conn: AsyncConnection, user_id: UUID, run_id: UUID) -> RingkasanPohon:
    baris = (await conn.execute(_RINGKAS_POHON, {"run_id": run_id, "user_id": user_id})).one()
    return RingkasanPohon(Decimal(baris.biaya), int(baris.masuk), int(baris.keluar), baris.model)


# Anggaran (4.9, K-32): biaya run pengguna sejak `sejak` — yang sudah ditutup (biaya akhirnya)
# DAN yang masih berjalan (biaya sejauh ini + jatah panggilan model yang sedang berjalan,
# `catat_biaya_berjalan`). Dibaca di bawah `kunci_anggaran`: giliran serentak di percakapan
# atau perangkat lain melihat jatah satu sama lain (E-201).
_BIAYA_SEJAK = text(
    """
    SELECT coalesce(sum(cost_usd), 0) FROM agent_runs
    WHERE user_id = :user_id AND started_at >= :sejak
    """
)
_KUNCI_ANGGARAN = text("SELECT pg_advisory_xact_lock(hashtextextended(:kunci, 0))")
# Hanya run yang masih berjalan — run yang sudah ditutup memegang biaya akhirnya.
_BIAYA_BERJALAN = text(
    "UPDATE agent_runs SET cost_usd = :biaya WHERE id = :id AND status = 'running'"
)


async def biaya_sejak(conn: AsyncConnection, user_id: UUID, sejak: datetime) -> Decimal:
    hasil = await conn.execute(_BIAYA_SEJAK, {"user_id": user_id, "sejak": sejak})
    return Decimal(hasil.scalar_one())


async def kunci_anggaran(conn: AsyncConnection, user_id: UUID) -> None:
    """Anggaran satu pengguna dibaca dan dipesan SERIAL — sampai transaksi ini selesai."""
    await conn.execute(_KUNCI_ANGGARAN, {"kunci": f"anggaran-ai:{user_id}"})


async def catat_biaya_berjalan(conn: AsyncConnection, run_id: UUID, biaya: Decimal) -> None:
    await conn.execute(_BIAYA_BERJALAN, {"id": run_id, "biaya": biaya})
