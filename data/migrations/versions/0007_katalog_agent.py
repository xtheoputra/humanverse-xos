"""Katalog agent V0 — agents + agent_tools (spec/07 4.2, spec/05, K-29).

Revision ID: 0007
Revises: 0006
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0007"
down_revision: str | None = "0006"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0007_katalog_agent.up.sql")


def downgrade() -> None:
    _jalankan("0007_katalog_agent.down.sql")
