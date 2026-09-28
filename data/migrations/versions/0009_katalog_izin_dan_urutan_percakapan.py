"""agent_tools.permission menurut jenis tool + indeks daftar percakapan (tinjauan kontrak Sprint 4).

Revision ID: 0009
Revises: 0008
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0009"
down_revision: str | None = "0008"
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0009_katalog_izin_dan_urutan_percakapan.up.sql")


def downgrade() -> None:
    _jalankan("0009_katalog_izin_dan_urutan_percakapan.down.sql")
