"""Lingkungan Alembic.

Urutan sumber URL: opsi `sqlalchemy.url` yang diset pemanggil (uji) →
`HVX_MIGRATION_DATABASE_URL`. Kalau keduanya kosong, migrasi GAGAL — tidak ada
basis data bawaan untuk "kebetulan" dimigrasikan.

🔑 **Bukan `HVX_DATABASE_URL`** (B-40). Migrasi berjalan sebagai PEMILIK
skema; api berjalan sebagai anggota `hvx_app` dan menolak mulai kalau
perannya pemilik tabel. Dua nama variabel membuat keduanya tidak bisa
tertukar diam-diam — dan tidak ada jatuh-balik dari satu ke yang lain.

Tiap revisi berjalan di transaksinya sendiri (`transaction_per_migration`):
PostgreSQL mendukung DDL transaksional, jadi migrasi yang gagal di tengah
tidak meninggalkan skema setengah jadi.
"""

from __future__ import annotations

import os

from alembic import context
from sqlalchemy import create_engine, pool

from hvx.modules.platform import konfigurasi_log, url_sync


def _url() -> str:
    dsn = context.config.get_main_option("sqlalchemy.url") or os.environ.get(
        "HVX_MIGRATION_DATABASE_URL"
    )
    if not dsn:
        raise RuntimeError(
            "HVX_MIGRATION_DATABASE_URL tidak diisi — migrasi tidak punya basis data tujuan. "
            "Isinya DSN peran PEMILIK skema, bukan peran api (B-40)."
        )
    return url_sync(dsn)


def _jalankan_online() -> None:
    engine = create_engine(_url(), poolclass=pool.NullPool)
    try:
        with engine.connect() as koneksi:
            context.configure(connection=koneksi, transaction_per_migration=True)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


# Dari CLI (kontainer `migrate`), log migrasi keluar sebagai JSON yang sama
# dengan api. Pemanggil dalam-proses (uji) mematikannya lewat atribut, supaya
# migrasi tidak mengganti handler log milik pemanggil.
if context.config.attributes.get("konfigurasi_log", True):
    konfigurasi_log(level=os.environ.get("HVX_LOG_LEVEL", "INFO"))

if context.is_offline_mode():
    # Revisi menjalankan berkas SQL lewat koneksi driver sungguhan (banyak
    # pernyataan sekaligus), dan itu tidak ada di mode --sql. Versi pertama
    # punya jalur offline yang tidak pernah bisa bekerja; lebih jujur menolak.
    raise RuntimeError(
        "mode offline (--sql) tidak didukung: SQL migrasi sudah tersedia apa adanya "
        "di data/migrations/versions/*.up.sql dan *.down.sql"
    )
_jalankan_online()
