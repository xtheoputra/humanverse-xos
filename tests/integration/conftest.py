"""Perlengkapan uji integrasi basis data: basis data sekali pakai dan peran aplikasi uji."""

from __future__ import annotations

import secrets
import uuid
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import ExitStack, contextmanager

import httpx
import psycopg
import pytest
from _bantuan_db import (
    BUAT_HVX_APP,
    PERAN_APLIKASI_UJI,
    ApiUji,
    BasisDataV0,
    alembic,
    dsn_ke,
    nama_db,
    psycopg_dsn,
)
from alembic import command
from asgi_lifespan import LifespanManager
from psycopg import sql

from hvx.main import create_app
from hvx.modules.platform import Settings


@contextmanager
def _basis_data(dsn_admin: str, awalan: str) -> Iterator[str]:
    nama = f"hvx_uji_{awalan}_{uuid.uuid4().hex[:10]}"
    with psycopg.connect(psycopg_dsn(dsn_admin), autocommit=True) as k:
        k.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nama)))
    try:
        yield dsn_ke(dsn_admin, nama)
    finally:
        with psycopg.connect(psycopg_dsn(dsn_admin), autocommit=True) as k:
            k.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(nama))
            )


@pytest.fixture
def basis_data_sekali_pakai(dsn_admin_uji: str) -> Iterator[Callable[[str], str]]:
    """Pabrik basis data kosong; semuanya dihapus sesudah uji, lulus atau gagal."""
    with ExitStack() as tumpukan:
        yield lambda awalan: tumpukan.enter_context(_basis_data(dsn_admin_uji, awalan))


@pytest.fixture(scope="session")
def sandi_peran_aplikasi_uji(dsn_admin_uji: str) -> str:
    """Peran LOGIN `hvx_api_uji`, anggota `hvx_app` — dipaksa aman di tiap sesi uji."""
    sandi = secrets.token_urlsafe(24)
    peran = sql.Identifier(PERAN_APLIKASI_UJI)
    with psycopg.connect(psycopg_dsn(dsn_admin_uji), autocommit=True) as k:
        k.execute(BUAT_HVX_APP)
        if not k.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s", (PERAN_APLIKASI_UJI,)
        ).fetchone():
            k.execute(sql.SQL("CREATE ROLE {} LOGIN").format(peran))
        k.execute(
            sql.SQL(
                "ALTER ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS "
                "INHERIT PASSWORD {}"
            ).format(peran, sql.Literal(sandi))
        )
        k.execute(sql.SQL("GRANT hvx_app TO {}").format(peran))
    return sandi


@pytest.fixture
def basis_data_termigrasi(
    basis_data_sekali_pakai: Callable[[str], str],
    dsn_admin_uji: str,
    sandi_peran_aplikasi_uji: str,
) -> Callable[[str], BasisDataV0]:
    def _buat(awalan: str) -> BasisDataV0:
        dsn_pemilik = basis_data_sekali_pakai(awalan)
        command.upgrade(alembic(dsn_pemilik), "head")
        return BasisDataV0(
            dsn_pemilik=dsn_pemilik,
            dsn_aplikasi=dsn_ke(
                dsn_admin_uji, nama_db(dsn_pemilik), PERAN_APLIKASI_UJI, sandi_peran_aplikasi_uji
            ),
        )

    return _buat


@pytest.fixture(scope="module")
def v0_bersama(dsn_admin_uji: str, sandi_peran_aplikasi_uji: str) -> Iterator[BasisDataV0]:
    """Satu basis data termigrasi untuk seluruh uji satu berkas; tiap uji memakai pengguna baru."""
    with _basis_data(dsn_admin_uji, "bersama") as dsn_pemilik:
        command.upgrade(alembic(dsn_pemilik), "head")
        yield BasisDataV0(
            dsn_pemilik=dsn_pemilik,
            dsn_aplikasi=dsn_ke(
                dsn_admin_uji, nama_db(dsn_pemilik), PERAN_APLIKASI_UJI, sandi_peran_aplikasi_uji
            ),
        )


@pytest.fixture
async def api_uji(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> AsyncIterator[ApiUji]:
    """create_app + lifespan terhadap basis data termigrasi, sebagai peran aplikasi."""
    db = basis_data_termigrasi("api")
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=db.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        yield ApiUji(app=app, klien=klien, db=db, awalan_redis=awalan)


@pytest.fixture(scope="module")
async def api_bersama(v0_bersama: BasisDataV0, url_redis_uji: str) -> AsyncIterator[ApiUji]:
    """SATU aplikasi utuh untuk seluruh uji satu berkas — tiap uji memakai pengguna baru.

    Untuk uji fitur domain (Sprint 2+) yang tidak menguji skema itu sendiri:
    memigrasikan basis data baru per uji membuat ratusan uji menunggu migrasi,
    sementara pemisahnya — pengguna berbeda di bawah RLS — sudah yang diuji
    `test_kepemilikan_data.py`. Batas laju dilonggarkan: satu klien uji mengirim
    ratusan permintaan dari satu IP; batasnya sendiri diuji `test_batas_laju.py`.
    """
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=v0_bersama.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
            rate_limit_ip="100000/60",
            rate_limit_user="100000/60",
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        yield ApiUji(app=app, klien=klien, db=v0_bersama, awalan_redis=awalan)
