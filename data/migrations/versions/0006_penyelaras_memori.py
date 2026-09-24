"""memori_perlu_diselaraskan(): memories → Qdrant (spec/07 3.5–3.7, spec/01 §12, K-19).

Revision ID: 0006
Revises: 0005
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0006"
down_revision: str | None = "0005"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0006_penyelaras_memori.up.sql")


def downgrade() -> None:
    _jalankan("0006_penyelaras_memori.down.sql")
