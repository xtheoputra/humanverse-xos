"""V0 — 23 tabel spec/01, masing-masing dengan `data_subject` + anotasi retensi (K-16).

SQL-nya hidup di berkas `.up.sql` / `.down.sql` di sebelah berkas ini, bukan
di dalam Python: pemeriksa P-1 · P-2 · P-3 (`tools/periksa_dokumen.py`)
membaca anotasi `@retention` · `@who-can-set` · `@on-delete` dari komentar
SQL, dan komentar itu tidak bertahan kalau DDL dibangun lewat `op.create_table`.

Revision ID: 0001
Revises: -
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None

_DI_SINI = Path(__file__).resolve().parent


def _jalankan(berkas: str) -> None:
    sql = (_DI_SINI / berkas).read_text(encoding="utf-8")
    # Protokol kueri sederhana psycopg: banyak pernyataan dalam satu kirim,
    # tanpa parameter — tanda `%` di SQL tidak ditafsirkan sebagai placeholder.
    op.get_bind().connection.driver_connection.execute(sql)  # type: ignore[union-attr]


def upgrade() -> None:
    _jalankan("0001_v0_skema.up.sql")


def downgrade() -> None:
    _jalankan("0001_v0_skema.down.sql")
