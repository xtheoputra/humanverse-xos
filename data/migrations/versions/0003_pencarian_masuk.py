"""auth_lookup_for_login(email) — login di bawah RLS (spec/07 1.1, spec/01 §12, K-19).

Revision ID: 0003
Revises: 0002
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0003_pencarian_masuk.up.sql")


def downgrade() -> None:
    _jalankan("0003_pencarian_masuk.down.sql")
