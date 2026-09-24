"""events_untuk_relay(): kotak keluar event → Redis Streams (spec/07 3.3, spec/01 §12, K-19).

Revision ID: 0005
Revises: 0004
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0005"
down_revision: str | None = "0004"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0005_relay_event.up.sql")


def downgrade() -> None:
    _jalankan("0005_relay_event.down.sql")
