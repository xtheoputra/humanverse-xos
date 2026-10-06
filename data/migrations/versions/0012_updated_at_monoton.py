"""set_updated_at() naik ketat per baris — identitas versi baris untuk kunci event (E-223).

Revision ID: 0012
Revises: 0011
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0012"
down_revision: str | None = "0011"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0012_updated_at_monoton.up.sql")


def downgrade() -> None:
    _jalankan("0012_updated_at_monoton.down.sql")
