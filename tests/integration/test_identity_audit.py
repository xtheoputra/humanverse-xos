"""spec/07 1.6 — `audit()` terhadap PostgreSQL sungguhan, sebagai peran aplikasi."""

from __future__ import annotations

import uuid
from collections.abc import Callable

import psycopg
import pytest
import structlog
from _bantuan_db import BasisDataV0, psycopg_dsn
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from hvx.modules.identity import audit
from hvx.modules.platform import buat_engine, transaksi_pengguna

pytestmark = pytest.mark.integration


async def test_audit_menulis_baris_pengguna_dan_sistem_dengan_request_id(
    basis_data_termigrasi: Callable[[str], BasisDataV0],
) -> None:
    db = basis_data_termigrasi("audit")
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
        (uid,) = k.execute(
            "INSERT INTO users (email, password_hash) VALUES ('a@uji.id', 'x') RETURNING id"
        ).fetchone() or (None,)
    assert isinstance(uid, uuid.UUID)

    engine = buat_engine(db.dsn_aplikasi)
    token = structlog.contextvars.bind_contextvars(request_id="rid-uji-audit")
    try:
        async with transaksi_pengguna(engine, uid) as conn:
            await audit(
                conn,
                aksi="session.login_succeeded",
                aktor_tipe="user",
                aktor_id=str(uid),
                user_id=uid,
                ip_hash="h" * 64,
                metadata={"metode": "sandi"},
            )
            await audit(conn, aksi="uji.sistem", aktor_tipe="system", aktor_id="uji", user_id=None)
            terlihat = (
                await conn.execute(text("SELECT action, data_subject, request_id FROM audit_logs"))
            ).all()
    finally:
        structlog.contextvars.reset_contextvars(**token)
        await engine.dispose()

    # RLS: yang melayani pengguna ini hanya membaca baris MILIKNYA, bukan baris sistem.
    assert [tuple(r) for r in terlihat] == [("session.login_succeeded", "user", "rid-uji-audit")]
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik)) as k:
        semua = k.execute(
            "SELECT action, data_subject, user_id, request_id, metadata FROM audit_logs ORDER BY id"
        ).fetchall()
    assert semua == [
        ("session.login_succeeded", "user", uid, "rid-uji-audit", {"metode": "sandi"}),
        ("uji.sistem", "system", None, "rid-uji-audit", {}),
    ]


async def test_baris_audit_yang_sudah_ditulis_tidak_bisa_diubah_aplikasi(
    basis_data_termigrasi: Callable[[str], BasisDataV0],
) -> None:
    """DoD 1.6 — `UPDATE`/`DELETE` ditolak, diuji sebagai peran yang MEMAKAI audit()."""
    db = basis_data_termigrasi("auditubah")
    engine = buat_engine(db.dsn_aplikasi)
    try:
        for perintah in ("UPDATE audit_logs SET action = 'dipalsukan'", "DELETE FROM audit_logs"):
            with pytest.raises(DBAPIError) as galat:
                async with engine.begin() as conn:
                    await conn.execute(text(perintah))
            # 42501 insufficient_privilege — ditolak GRANT, bukan kebetulan nol baris.
            assert getattr(galat.value.orig, "pgcode", None) == "42501", galat.value
    finally:
        await engine.dispose()
