"""Galat basis data tidak membawa nilai milik pengguna — ke teks galat maupun ke log.

🔴 Diukur di tinjauan Sprint 1, PostgreSQL & asyncpg sungguhan:

* SQLAlchemy menempelkan `[parameters: ('email@…', '$argon2id$…')]` ke teks
  galat;
* PostgreSQL sendiri mengirim `DETAIL: Key (email)=(…) already exists` dan
  `Failing row contains (…)` — seluruh baris, di pesan galatnya.

Keduanya sampai ke log `request.failed`. Hari ini: email dan hash sandi;
begitu tabel isi pribadi ditulis (jurnal, Sprint 2): isinya.
"""

from __future__ import annotations

import asyncio
import io
import json
import traceback

import pytest
import structlog
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from hvx.modules.platform import buat_engine, konfigurasi_log

pytestmark = pytest.mark.integration

EMAIL = "rahasia.orang@uji.id"


async def test_teks_galat_basis_data_tidak_membawa_parameter_kueri(dsn_admin_uji: str) -> None:
    engine = buat_engine(dsn_admin_uji)
    try:
        with pytest.raises(DBAPIError) as galat:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT CAST(:email AS text), 1 / 0"), {"email": EMAIL})
    finally:
        await engine.dispose()

    teks = "".join(traceback.format_exception(galat.value))
    assert "division by zero" in teks, teks  # galat yang dimaksud, bukan galat lain
    assert EMAIL not in teks, "parameter kueri ikut di teks galat basis data"


async def test_galat_basis_data_dicatat_tanpa_isi_baris_tetapi_tetap_bisa_ditelusuri(
    dsn_admin_uji: str,
) -> None:
    aliran = io.StringIO()
    konfigurasi_log(level="INFO", json=True, stream=aliran)
    log = structlog.get_logger("hvx.request")  # pencatat middleware `request.failed`
    engine = buat_engine(dsn_admin_uji)
    try:
        async with engine.connect() as conn:
            await conn.execute(
                text("CREATE TEMP TABLE akun_uji (email text UNIQUE, umur int CHECK (umur > 0))")
            )
            await conn.execute(text("INSERT INTO akun_uji VALUES (:email, 30)"), {"email": EMAIL})
            for sql, nilai in (
                ("INSERT INTO akun_uji VALUES (:email, 31)", {"email": EMAIL}),  # UNIQUE → DETAIL
                ("INSERT INTO akun_uji VALUES (:email, -1)", {"email": "lain." + EMAIL}),  # CHECK
            ):
                try:
                    async with conn.begin_nested():
                        await conn.execute(text(sql), nilai)
                except DBAPIError:
                    log.exception("request.failed")
    finally:
        await engine.dispose()

    keluaran = aliran.getvalue()
    baris = [json.loads(b) for b in keluaran.splitlines() if b.strip()]
    assert [b["event"] for b in baris] == ["request.failed", "request.failed"], keluaran
    assert EMAIL not in keluaran, f"isi baris pengguna tertulis ke log:\n{keluaran}"
    # tetap bisa ditelusuri: jejak tumpukan, SQLSTATE, dan nama constraint — bukan nilai
    unik, periksa = (b["exception"] for b in baris)
    assert "Traceback" in unik
    assert "23505" in unik
    assert "akun_uji_email_key" in unik
    assert "23514" in periksa
    assert "akun_uji_umur_check" in periksa


async def test_galat_basis_data_di_dalam_kelompok_galat_juga_tanpa_isi(dsn_admin_uji: str) -> None:
    """🔴 Tinjauan Sprint 1: penyaring hanya menelusuri `__cause__`/`__context__` —
    galat UNIQUE yang dilempar di dalam `asyncio.TaskGroup` (bentuk yang dipakai
    SSE FastAPI, tugas 4.8) tertulis ke log lengkap dengan `DETAIL`-nya."""
    aliran = io.StringIO()
    konfigurasi_log(level="INFO", json=True, stream=aliran)
    log = structlog.get_logger("hvx.request")
    engine = buat_engine(dsn_admin_uji)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("CREATE TEMP TABLE akun_grup (email text UNIQUE)"))
            await conn.execute(text("INSERT INTO akun_grup VALUES (:email)"), {"email": EMAIL})

            async def tulis_ganda() -> None:
                await conn.execute(text("INSERT INTO akun_grup VALUES (:email)"), {"email": EMAIL})

            try:
                async with asyncio.TaskGroup() as grup:
                    grup.create_task(tulis_ganda())
            except* DBAPIError:
                log.exception("request.failed")
    finally:
        await engine.dispose()

    keluaran = aliran.getvalue()
    assert "request.failed" in keluaran, "galat kelompok tidak tercatat — uji ini buta"
    assert EMAIL not in keluaran, (
        f"isi baris dari galat di dalam kelompok tertulis ke log:\n{keluaran}"
    )
    assert "23505" in keluaran, "galat di dalam kelompok dicatat tanpa SQLSTATE-nya"
