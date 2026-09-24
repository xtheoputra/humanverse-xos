"""goals: CHECK goal bukan induk dirinya sendiri (spec/07 2.1, spec/01 §2).

Revision ID: 0004
Revises: 0003
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0004_goal_bukan_induk_dirinya.up.sql")


def downgrade() -> None:
    _jalankan("0004_goal_bukan_induk_dirinya.down.sql")
