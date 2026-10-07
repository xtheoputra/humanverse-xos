"""Privacy Center: hapus event milik pengguna yang dilayani; sapuan mengosongkan `ip_hash` (6.4).

Revision ID: 0013
Revises: 0012
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0013"
down_revision: str | None = "0012"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0013_privacy_center.up.sql")


def downgrade() -> None:
    _jalankan("0013_privacy_center.down.sql")
