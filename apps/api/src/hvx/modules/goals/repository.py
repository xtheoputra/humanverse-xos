"""SQL modul `goals` — hanya tabel miliknya: goals · goal_milestones (spec/06 aturan 5).

SQL STATIS seluruhnya (lihat `profile/repository.py`): bendera `ubah_*` memilih
kolom yang diubah, bukan nama kolom yang dirakit dari string. Tiap fungsi
menerima koneksi dari lapisan layanan — di dalam `platform.transaksi_pengguna`,
jadi RLS (spec/01 §11) membatasi tiap kueri pada pengguna yang dilayani.
`user_id = :user_id` tetap ditulis di kueri daftar: supaya indeks terpakai,
bukan sebagai satu-satunya penjaga.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Goal, Milestone

_SISIP = text(
    """
    INSERT INTO goals (id, user_id, parent_id, title, description, domain, target_date)
    VALUES (COALESCE(CAST(:id AS uuid), gen_random_uuid()), :user_id, CAST(:parent_id AS uuid),
            :title, CAST(:description AS text), CAST(:domain AS text),
            CAST(:target_date AS date))
    RETURNING id, parent_id, title, description, domain, status, target_date, achieved_at,
              created_at, updated_at
    """
)

_AMBIL = text(
    """
    SELECT id, parent_id, title, description, domain, status, target_date, achieved_at,
           created_at, updated_at
    FROM goals
    WHERE id = :id AND deleted_at IS NULL
    """
)

_DAFTAR = text(
    """
    SELECT id, parent_id, title, description, domain, status, target_date, achieved_at,
           created_at, updated_at
    FROM goals
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:status AS text) IS NULL OR status = CAST(:status AS text))
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (created_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY created_at DESC, id DESC
    LIMIT :batas
    """
)

# Jarak goal `:id` dari akarnya — NULL bila goal itu tidak ada atau terhapus.
# `:batas` menghentikan rekursi apa pun yang terjadi pada datanya.
_KEDALAMAN = text(
    """
    WITH RECURSIVE naik AS (
      SELECT id, parent_id, 0 AS jarak
      FROM goals
      WHERE id = :id AND deleted_at IS NULL
      UNION ALL
      SELECT g.id, g.parent_id, n.jarak + 1
      FROM goals g
      JOIN naik n ON g.id = n.parent_id
      WHERE g.deleted_at IS NULL AND n.jarak < :batas
    )
    SELECT max(jarak) FROM naik
    """
)

# spec/07 2.1 — pohon goal terbaca dalam SATU kueri: CTE rekursif, bukan satu
# kueri per tingkat. `jalur` menolak lingkaran apa pun bentuk datanya, dan
# `:batas` membatasi kedalamannya.
_POHON = text(
    """
    WITH RECURSIVE pohon AS (
      SELECT g.id, g.parent_id, g.title, g.description, g.domain, g.status, g.target_date,
             g.achieved_at, g.created_at, g.updated_at, 0 AS kedalaman, ARRAY[g.id] AS jalur
      FROM goals g
      WHERE g.id = :id AND g.deleted_at IS NULL
      UNION ALL
      SELECT c.id, c.parent_id, c.title, c.description, c.domain, c.status, c.target_date,
             c.achieved_at, c.created_at, c.updated_at, p.kedalaman + 1, p.jalur || c.id
      FROM goals c
      JOIN pohon p ON c.parent_id = p.id
      WHERE c.deleted_at IS NULL AND p.kedalaman < :batas AND c.id <> ALL (p.jalur)
    )
    SELECT id, parent_id, title, description, domain, status, target_date, achieved_at,
           created_at, updated_at, kedalaman
    FROM pohon
    ORDER BY kedalaman, created_at, id
    """
)

_UBAH = text(
    """
    WITH lama AS (
      SELECT id, status FROM goals WHERE id = :id AND deleted_at IS NULL FOR UPDATE
    )
    UPDATE goals g SET
      title = CASE WHEN :ubah_title THEN CAST(:title AS text) ELSE g.title END,
      status = CASE WHEN :ubah_status THEN CAST(:status AS text) ELSE g.status END,
      achieved_at = CASE
        WHEN NOT :ubah_status THEN g.achieved_at
        WHEN CAST(:status AS text) = 'achieved' THEN COALESCE(g.achieved_at, now())
        ELSE NULL
      END,
      target_date = CASE WHEN :ubah_target_date THEN CAST(:target_date AS date)
                         ELSE g.target_date END
    FROM lama
    WHERE g.id = lama.id
    RETURNING g.id, g.parent_id, g.title, g.description, g.domain, g.status, g.target_date,
              g.achieved_at, g.created_at, g.updated_at, lama.status AS status_lama
    """
)

_HAPUS = text(
    "UPDATE goals SET deleted_at = now() WHERE id = :id AND deleted_at IS NULL RETURNING id"
)

# Hapus-lunak meniru hapus-keras spec/01: `ON DELETE SET NULL (parent_id)` —
# anak goal yang dihapus naik menjadi akar, tidak ikut hilang.
_LEPAS_ANAK = text("UPDATE goals SET parent_id = NULL WHERE parent_id = :id")

_MILESTONE_GOAL = text(
    """
    SELECT id, goal_id, title, position, status, due_date, completed_at, created_at, updated_at
    FROM goal_milestones
    WHERE goal_id = :goal_id
    ORDER BY position, created_at, id
    """
)

_AMBIL_MILESTONE = text(
    """
    SELECT m.id, m.goal_id, m.title, m.position, m.status, m.due_date, m.completed_at,
           m.created_at, m.updated_at
    FROM goal_milestones m
    JOIN goals g ON g.id = m.goal_id
    WHERE m.id = :id AND g.deleted_at IS NULL
    """
)

# `user_id` diambil dari baris goal-nya, bukan dari parameter: milestone selalu
# milik pemilik goal — FK komposit (B-41) menolak yang lain, di sini ia tidak
# pernah sempat dicoba.
_SISIP_MILESTONE = text(
    """
    INSERT INTO goal_milestones (goal_id, user_id, title, position, due_date)
    SELECT g.id, g.user_id, :title,
           COALESCE(CAST(:position AS integer),
                    (SELECT COALESCE(max(m.position) + 1, 0)
                     FROM goal_milestones m WHERE m.goal_id = g.id)),
           CAST(:due_date AS date)
    FROM goals g
    WHERE g.id = :goal_id AND g.deleted_at IS NULL
    RETURNING id, goal_id, title, position, status, due_date, completed_at, created_at,
              updated_at
    """
)

_UBAH_MILESTONE = text(
    """
    UPDATE goal_milestones m SET
      title = CASE WHEN :ubah_title THEN CAST(:title AS text) ELSE m.title END,
      status = CASE WHEN :ubah_status THEN CAST(:status AS text) ELSE m.status END,
      completed_at = CASE
        WHEN NOT :ubah_status THEN m.completed_at
        WHEN CAST(:status AS text) = 'done' THEN COALESCE(m.completed_at, now())
        ELSE NULL
      END,
      due_date = CASE WHEN :ubah_due_date THEN CAST(:due_date AS date) ELSE m.due_date END
    FROM goals g
    WHERE m.id = :id AND g.id = m.goal_id AND g.deleted_at IS NULL
    RETURNING m.id, m.goal_id, m.title, m.position, m.status, m.due_date, m.completed_at,
              m.created_at, m.updated_at
    """
)


@dataclass(frozen=True)
class HasilUbah:
    goal: Goal
    status_lama: str


def _goal(baris: RowMapping) -> Goal:
    return Goal.model_validate(dict(baris))


async def sisip(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    id_: UUID | None,
    parent_id: UUID | None,
    title: str,
    description: str | None,
    domain: str | None,
    target_date: date | None,
) -> Goal:
    baris = (
        (
            await conn.execute(
                _SISIP,
                {
                    "id": id_,
                    "user_id": user_id,
                    "parent_id": parent_id,
                    "title": title,
                    "description": description,
                    "domain": domain,
                    "target_date": target_date,
                },
            )
        )
        .mappings()
        .one()
    )
    return _goal(baris)


async def ambil(conn: AsyncConnection, goal_id: UUID) -> Goal | None:
    baris = (await conn.execute(_AMBIL, {"id": goal_id})).mappings().first()
    return _goal(baris) if baris else None


async def daftar(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    status: str | None,
    batas: int,
    sesudah: tuple[datetime, UUID] | None,
) -> list[Goal]:
    hasil = await conn.execute(
        _DAFTAR,
        {
            "user_id": user_id,
            "status": status,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [_goal(b) for b in hasil.mappings()]


async def kedalaman(conn: AsyncConnection, goal_id: UUID, batas: int) -> int | None:
    nilai = (await conn.execute(_KEDALAMAN, {"id": goal_id, "batas": batas})).scalar_one()
    return int(nilai) if nilai is not None else None


async def pohon(conn: AsyncConnection, goal_id: UUID, batas: int) -> list[tuple[Goal, int]]:
    """(goal, kedalaman) — akar lebih dulu, lalu per tingkat. Satu kueri."""
    hasil = await conn.execute(_POHON, {"id": goal_id, "batas": batas})
    return [(_goal(b), int(b["kedalaman"])) for b in hasil.mappings()]


async def ubah(
    conn: AsyncConnection, goal_id: UUID, perubahan: Mapping[str, Any]
) -> HasilUbah | None:
    nilai: dict[str, Any] = {"id": goal_id}
    for k in ("title", "status", "target_date"):
        nilai[f"ubah_{k}"] = k in perubahan
        nilai[k] = perubahan.get(k)
    baris = (await conn.execute(_UBAH, nilai)).mappings().first()
    if baris is None:
        return None
    isi = dict(baris)
    status_lama = str(isi.pop("status_lama"))
    return HasilUbah(Goal.model_validate(isi), status_lama)


async def hapus(conn: AsyncConnection, goal_id: UUID) -> bool:
    terhapus = (await conn.execute(_HAPUS, {"id": goal_id})).first() is not None
    if terhapus:
        await conn.execute(_LEPAS_ANAK, {"id": goal_id})
    return terhapus


async def milestone_goal(conn: AsyncConnection, goal_id: UUID) -> list[Milestone]:
    hasil = await conn.execute(_MILESTONE_GOAL, {"goal_id": goal_id})
    return [Milestone.model_validate(dict(b)) for b in hasil.mappings()]


async def sisip_milestone(
    conn: AsyncConnection,
    *,
    goal_id: UUID,
    title: str,
    position: int | None,
    due_date: date | None,
) -> Milestone | None:
    baris = (
        (
            await conn.execute(
                _SISIP_MILESTONE,
                {"goal_id": goal_id, "title": title, "position": position, "due_date": due_date},
            )
        )
        .mappings()
        .first()
    )
    return Milestone.model_validate(dict(baris)) if baris else None


async def ambil_milestone(conn: AsyncConnection, milestone_id: UUID) -> Milestone | None:
    baris = (await conn.execute(_AMBIL_MILESTONE, {"id": milestone_id})).mappings().first()
    return Milestone.model_validate(dict(baris)) if baris else None


async def ubah_milestone(
    conn: AsyncConnection, milestone_id: UUID, perubahan: Mapping[str, Any]
) -> Milestone | None:
    nilai: dict[str, Any] = {"id": milestone_id}
    for k in ("title", "status", "due_date"):
        nilai[f"ubah_{k}"] = k in perubahan
        nilai[k] = perubahan.get(k)
    baris = (await conn.execute(_UBAH_MILESTONE, nilai)).mappings().first()
    return Milestone.model_validate(dict(baris)) if baris else None
