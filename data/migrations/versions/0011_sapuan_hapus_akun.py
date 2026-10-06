"""sapuan hapus akun tahap 3–6 — tiga fungsi hvx_pekerja; penyelaras melewati akun pending_deletion.

Revision ID: 0011
Revises: 0010
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0011"
down_revision: str | None = "0010"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0011_sapuan_hapus_akun.up.sql")


def downgrade() -> None:
    _jalankan("0011_sapuan_hapus_akun.down.sql")
