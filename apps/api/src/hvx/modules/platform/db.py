"""Koneksi PostgreSQL.

Satu DSN di konfigurasi (`postgresql://…`), dua driver:

* aplikasi memakai **asyncpg** (`postgresql+asyncpg://`);
* migrasi memakai **psycopg 3** sinkron (`postgresql+psycopg://`), sebab
  berkas migrasi berisi banyak pernyataan sekaligus dan hanya protokol kueri
  sederhana yang menerimanya.

🔴 **DSN tidak boleh membawa parameter kueri** (`?sslmode=…`,
`?connect_timeout=…`). Kedua driver menafsirkannya berbeda: asyncpg menolak
nama libpq seperti `sslmode` (`TypeError` di kueri pertama), psycopg menolak
`ssl` milik asyncpg. Diukur: migrasi berhasil, api mulai, lalu setiap kueri
gagal — dan `/health` hanya melaporkan `db: down`. Maka DSN berparameter
ditolak **saat mulai**. Opsi koneksi (TLS pada PostgreSQL terkelola, tahap D2)
diberikan lewat variabel libpq (`PGSSLMODE`, `PGSSLROOTCERT`, `PGCONNECT_TIMEOUT`,
`PGAPPNAME`), yang dihormati kedua driver.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

_SKEMA_POLOS = ("postgresql://", "postgres://")


def _ganti_driver(dsn: str, driver: str) -> str:
    if "?" in dsn:
        raise ValueError(
            "DSN basis data tidak boleh membawa parameter kueri (?…): asyncpg dan psycopg "
            "menafsirkannya berbeda. Pakai variabel libpq — PGSSLMODE, PGSSLROOTCERT, "
            "PGCONNECT_TIMEOUT, PGAPPNAME."
        )
    for awalan in _SKEMA_POLOS:
        if dsn.startswith(awalan):
            return f"postgresql+{driver}://" + dsn[len(awalan) :]
    if dsn.startswith("postgresql+"):
        _, sisa = dsn.split("://", 1)
        return f"postgresql+{driver}://" + sisa
    raise ValueError("DSN basis data wajib berskema postgresql:// atau postgres://")


def url_async(dsn: str) -> str:
    return _ganti_driver(dsn, "asyncpg")


def url_sync(dsn: str) -> str:
    return _ganti_driver(dsn, "psycopg")


def buat_engine(dsn: str) -> AsyncEngine:
    return create_async_engine(
        url_async(dsn),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=5,
    )


async def ping_db(engine: AsyncEngine) -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
