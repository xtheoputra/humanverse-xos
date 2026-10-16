"""users.deletion_scheduled_at — penanda tenggang 30 hari alur hapus akun (spec/07 6.5).

Revision ID: 0010
Revises: 0009
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0010"
down_revision: str | None = "0009"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0010_jadwal_hapus_akun.up.sql")


def downgrade() -> None:
    _jalankan("0010_jadwal_hapus_akun.down.sql")
