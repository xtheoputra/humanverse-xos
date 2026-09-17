"""Perlengkapan uji integrasi basis data: basis data sekali pakai dan peran aplikasi uji."""

from __future__ import annotations

import secrets
import uuid
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager

import psycopg
import pytest
from _bantuan_db import (
    BUAT_HVX_APP,
    PERAN_APLIKASI_UJI,
    BasisDataV0,
    alembic,
    dsn_ke,
    nama_db,
    psycopg_dsn,
)
from alembic import command
from psycopg import sql


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
