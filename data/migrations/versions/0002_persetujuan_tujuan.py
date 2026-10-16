"""consents.purpose · data_scopes · expires_at — spec/07 1.4, B-22 (#59), naskah 12 §8.9.

Revision ID: 0002
Revises: 0001
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0002_persetujuan_tujuan.up.sql")


def downgrade() -> None:
    _jalankan("0002_persetujuan_tujuan.down.sql")
