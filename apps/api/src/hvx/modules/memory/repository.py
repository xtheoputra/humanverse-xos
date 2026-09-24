"""SQL modul `memory` — hanya tabel miliknya: memories (spec/06 aturan 5).

Isi event dan isi sumbernya (mood, jurnal) dibaca lewat pintu keluar modul
pemiliknya, di transaksi yang sama — tidak pernah dengan SQL dari sini.

Tiga kolom yang menyelaraskan memori dengan Qdrant (spec/01 §12, fungsi ke-3):

* `embedding_model` — penyemat yang vektornya COCOK dengan isi saat ini. `NULL`
  = belum disemat, atau isinya berubah sesudah disemat → penyelaras menyemat
  (ulang). 🔧 Bukan `model_version`: kolom itu tempat ambang keyakinan #34
  (arch/README — versi yang menghasilkan memori dan keyakinannya), dan versi
  pertama penyelaras menimpanya (tinjauan kontrak Sprint 3, K4).
* `embedding_id` — id titik Qdrant sesudah pertama disemat (= id memori).
* `deleted_at` — isi SUDAH dikosongkan; titik dan barisnya menunggu dibuang
  penyelaras. Memori tidak pernah langsung dihapus: titiknya bisa sudah ada
  meski `embedding_id` belum sempat tercatat (Qdrant tidak ikut transaksi).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Memori

# Id memori ekstraksi deterministik (`ekstraksi.id_memori`): kirim ulang event yang
# sama menabrak baris yang sudah ada dan tidak menulis apa pun.
_SISIP = text(
    """
    INSERT INTO memories (id, user_id, kind, scope, content, confidence, evidence_count,
                          model_version, source_event_id, valid_from)
    VALUES (:id, :user_id, :kind, :scope, :content, :confidence, :evidence_count,
            :model_version, :source_event_id, :valid_from)
    ON CONFLICT (id) DO NOTHING
    RETURNING id, kind, scope, content, summary, confidence, evidence_count, model_version,
              source_event_id, valid_from, valid_until, created_at
    """
)

# Baris yang boleh diserahkan pencarian: hidup, masih berlaku, scope-nya masih
# diizinkan, dan VEKTORNYA COCOK dengan isinya sekarang — MENURUT POSTGRESQL.
# Payload Qdrant bisa basi, dan vektor lama sesudah `PATCH /journal` masih
# mencocokkan kata yang sudah dihapus pemiliknya (tinjauan kontrak Sprint 3, K2).
_HIDUP_MENURUT_ID = text(
    """
    SELECT id, kind, scope, content, summary, confidence, evidence_count, model_version,
           source_event_id, valid_from, valid_until, created_at
    FROM memories
    WHERE id = ANY(CAST(:ids AS uuid[])) AND deleted_at IS NULL
      AND scope = ANY(CAST(:scope AS text[]))
      AND embedding_model = :model
      AND (valid_until IS NULL OR valid_until > now())
    """
)

# Sumbernya berubah: isi baru, dan vektor lama tidak lagi cocok (`embedding_model`
# NULL → penyelaras menyemat ulang ke titik yang sama). `valid_from` mengikuti
# waktu kejadian yang dikoreksi pemiliknya.
_GANTI_ISI = text(
    """
    UPDATE memories SET
      content = :content,
      valid_from = :valid_from,
      embedding_model = CASE WHEN content IS DISTINCT FROM :content THEN NULL
                             ELSE embedding_model END
    WHERE id = :id AND deleted_at IS NULL
      AND (content IS DISTINCT FROM :content OR valid_from IS DISTINCT FROM :valid_from)
    """
)

# Sumbernya dihapus: isi dikosongkan SEKARANG, di transaksi penghapusnya; titik
# Qdrant dan barisnya dibuang penyelaras sesudah commit.
_LUPAKAN = text(
    """
    UPDATE memories SET content = '', summary = NULL, deleted_at = now()
    WHERE id = :id AND deleted_at IS NULL
    """
)

_PENGGUNA_PERLU_DISELARASKAN = text("SELECT user_id FROM memori_perlu_diselaraskan(:model, :batas)")

# Di transaksi PEMILIKNYA (RLS), TANPA kunci baris: Qdrant dipanggil sesudah
# transaksi ini selesai, dan pendengar jurnal tidak pernah menunggu Qdrant
# (tinjauan kontrak Sprint 3, K3). `cerna` isi dibaca di sini, lalu dicocokkan
# lagi saat menandai — isi yang berubah di antaranya tidak ditandai tersemat.
_PERLU_DISELARASKAN = text(
    """
    SELECT id, user_id, kind, scope, content, deleted_at,
           encode(sha256(convert_to(content, 'UTF8')), 'hex') AS cerna
    FROM memories
    WHERE deleted_at IS NOT NULL OR embedding_model IS DISTINCT FROM :model
    ORDER BY updated_at, id
    LIMIT :batas
    """
)

_TANDAI_TERSEMAT = text(
    """
    UPDATE memories m
    SET embedding_id = CAST(m.id AS text), embedding_model = :model
    FROM unnest(CAST(:ids AS uuid[]), CAST(:cerna AS text[])) AS s(id, cerna)
    WHERE m.id = s.id AND m.deleted_at IS NULL
      AND encode(sha256(convert_to(m.content, 'UTF8')), 'hex') = s.cerna
    """
)

_BUANG = text(
    "DELETE FROM memories WHERE id = ANY(CAST(:ids AS uuid[])) AND deleted_at IS NOT NULL"
)


@dataclass(frozen=True)
class BarisSelaras:
    id: UUID
    user_id: UUID
    kind: str
    scope: str
    content: str
    deleted_at: datetime | None
    cerna: str  # sha256 isi saat dibaca — penanda "vektor ini cocok dengan isi INI"


def _memori(baris: RowMapping) -> Memori:
    return Memori(**dict(baris))


async def sisip(
    conn: AsyncConnection,
    *,
    id_: UUID,
    user_id: UUID,
    kind: str,
    scope: str,
    content: str,
    confidence: Decimal,
    evidence_count: int,
    model_version: str,
    source_event_id: UUID,
    valid_from: datetime,
) -> Memori | None:
    """Memori baru — `None` bila id itu sudah ada (event yang sama diproses lagi)."""
    baris = (
        (
            await conn.execute(
                _SISIP,
                {
                    "id": id_,
                    "user_id": user_id,
                    "kind": kind,
                    "scope": scope,
                    "content": content,
                    "confidence": confidence,
                    "evidence_count": evidence_count,
                    "model_version": model_version,
                    "source_event_id": source_event_id,
                    "valid_from": valid_from,
                },
            )
        )
        .mappings()
        .first()
    )
    return _memori(baris) if baris else None


async def hidup_menurut_id(
    conn: AsyncConnection, ids: Iterable[UUID], scope: Iterable[str], model: str
) -> dict[UUID, Memori]:
    hasil = await conn.execute(
        _HIDUP_MENURUT_ID, {"ids": list(ids), "scope": list(scope), "model": model}
    )
    return {b["id"]: _memori(b) for b in hasil.mappings()}


async def ganti_isi(conn: AsyncConnection, id_: UUID, content: str, valid_from: datetime) -> None:
    await conn.execute(_GANTI_ISI, {"id": id_, "content": content, "valid_from": valid_from})


async def lupakan(conn: AsyncConnection, id_: UUID) -> None:
    await conn.execute(_LUPAKAN, {"id": id_})


async def pengguna_perlu_diselaraskan(conn: AsyncConnection, model: str, batas: int) -> list[UUID]:
    hasil = await conn.execute(_PENGGUNA_PERLU_DISELARASKAN, {"model": model, "batas": batas})
    return [b.user_id for b in hasil]


async def perlu_diselaraskan(conn: AsyncConnection, model: str, batas: int) -> list[BarisSelaras]:
    hasil = await conn.execute(_PERLU_DISELARASKAN, {"model": model, "batas": batas})
    return [BarisSelaras(**dict(b)) for b in hasil.mappings()]


async def tandai_tersemat(conn: AsyncConnection, baris: list[BarisSelaras], model: str) -> None:
    if baris:
        await conn.execute(
            _TANDAI_TERSEMAT,
            {"ids": [b.id for b in baris], "cerna": [b.cerna for b in baris], "model": model},
        )


async def buang(conn: AsyncConnection, ids: list[UUID]) -> None:
    if ids:
        await conn.execute(_BUANG, {"ids": ids})
