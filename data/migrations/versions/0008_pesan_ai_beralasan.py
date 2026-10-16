"""ai_messages.confidence + rationale — tiap balasan AI membawa keduanya (spec/07 4.8, E-194).

Revision ID: 0008
Revises: 0007
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0008"
down_revision: str | None = "0007"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0008_pesan_ai_beralasan.up.sql")


def downgrade() -> None:
    _jalankan("0008_pesan_ai_beralasan.down.sql")
