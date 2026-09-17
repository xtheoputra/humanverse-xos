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

🔑 **Dua DSN, dua peran (B-40).** `HVX_DATABASE_URL` milik api — peran login
anggota `hvx_app`, BUKAN pemilik tabel. `HVX_MIGRATION_DATABASE_URL` milik
migrasi — pemilik skema. api menolak mulai dengan peran yang melewati RLS
(`pastikan_peran_aplikasi`), dan tiap kueri berjalan di dalam
`transaksi_pengguna`, sebab RLS spec/01 §11 hanya meloloskan baris pengguna
yang sedang dilayani.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

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


class PeranTidakAman(RuntimeError):
    """B-40 — peran basis data api melewati RLS atau memiliki tabel; api menolak mulai."""


# `pg_has_role(..., 'USAGE')` juga menangkap peran yang MEWARISI pemilik tabel
# lewat keanggotaan — pemilik tidak terkena RLS, dan pewarisnya pun tidak.
_KUERI_PERAN = text(
    """
    SELECT r.rolname,
           r.rolsuper,
           r.rolbypassrls,
           ARRAY(
             SELECT c.relname::text FROM pg_class c
             WHERE c.relnamespace = 'public'::regnamespace
               AND c.relkind IN ('r', 'p')
               AND pg_has_role(current_user, c.relowner, 'USAGE')
             ORDER BY c.relname
           ) AS tabel_dimiliki
    FROM pg_roles r
    WHERE r.rolname = current_user
    """
)


async def pastikan_peran_aplikasi(engine: AsyncEngine) -> None:
    """Tolak peran yang membuat RLS dan hak akses spec/01 §10–§11 tidak berlaku.

    🔴 B-40: sampai 17 Sep 2026 api tersambung sebagai superuser pemilik tabel,
    dan `REVOKE UPDATE, DELETE ON audit_logs` tidak menghalangi apa pun. Aturan
    yang bergantung pada peran yang benar wajib memeriksa perannya sendiri —
    konfigurasi yang keliru harus gagal saat mulai, bukan diam-diam lolos.
    """
    async with engine.connect() as conn:
        peran = (await conn.execute(_KUERI_PERAN)).one()
    masalah = []
    if peran.rolsuper:
        masalah.append("superuser")
    if peran.rolbypassrls:
        masalah.append("BYPASSRLS")
    if peran.tabel_dimiliki:
        contoh = ", ".join(peran.tabel_dimiliki[:3])
        masalah.append(f"pemilik {len(peran.tabel_dimiliki)} tabel ({contoh}, …)")
    if masalah:
        raise PeranTidakAman(
            f"peran basis data `{peran.rolname}` tidak boleh dipakai api — {'; '.join(masalah)}. "
            "Keduanya melewati RLS. Pakai peran login anggota `hvx_app` "
            "(B-40, spec/01 §10); peran pemilik hanya untuk HVX_MIGRATION_DATABASE_URL."
        )


@asynccontextmanager
async def transaksi_pengguna(engine: AsyncEngine, user_id: UUID) -> AsyncIterator[AsyncConnection]:
    """Satu transaksi atas nama SATU pengguna — RLS spec/01 §11 membatasi tiap kueri di dalamnya.

    `set_config(..., true)` hanya berlaku sampai transaksi selesai: koneksi yang
    kembali ke pool tidak membawa pengguna ini ke permintaan berikutnya. Kueri
    di luar transaksi ini tidak melihat satu baris pun milik pengguna mana pun.
    """
    if not isinstance(user_id, UUID):
        # str "semua" atau "" di sini akan menjadi galat cast di basis data —
        # ditolak lebih awal, dengan nama yang jelas.
        raise TypeError(f"user_id wajib uuid.UUID, bukan {type(user_id).__name__}")
    async with engine.begin() as conn:
        await conn.execute(
            text("SELECT set_config('hvx.user_id', :user_id, true)"), {"user_id": str(user_id)}
        )
        yield conn
