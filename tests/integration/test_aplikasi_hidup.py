"""spec/07 0.3 terhadap layanan NYATA — `create_app` + lifespan + /health.

api selalu tersambung sebagai peran APLIKASI (`hvx_api_uji`, anggota `hvx_app`)
ke basis data termigrasi — seperti di compose. Uji yang tersambung sebagai
pemilik tabel akan lulus sambil membuktikan hal yang salah (B-40).
"""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager

import httpx
import psycopg
import pytest
from _bantuan_db import BasisDataV0, dsn_ke, nama_db, psycopg_dsn
from asgi_lifespan import LifespanManager
from psycopg import sql

from hvx import __version__, pekerja
from hvx.main import create_app
from hvx.modules.platform import PeranTidakAman, Settings

pytestmark = pytest.mark.integration


async def test_health_200_terhadap_postgres_dan_redis_sungguhan(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> None:
    db = basis_data_termigrasi("hidup")
    app = create_app(Settings(database_url=db.dsn_aplikasi, redis_url=url_redis_uji, env="test"))

    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        r = await klien.get("/health")

    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok", "version": __version__, "db": "ok", "redis": "ok"}
    assert r.headers["x-request-id"]


async def test_health_503_saat_redis_tidak_bisa_dihubungi(
    basis_data_termigrasi: Callable[[str], BasisDataV0],
) -> None:
    db = basis_data_termigrasi("redismati")
    app = create_app(
        Settings(
            database_url=db.dsn_aplikasi,
            # port 1: dijamin tertutup — koneksi ditolak seketika
            redis_url="redis://127.0.0.1:1/0",
            env="test",
            health_timeout_s=0.5,
        )
    )

    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        r = await klien.get("/health")

    assert r.status_code == 503
    assert r.json()["db"] == "ok"
    assert r.json()["redis"] == "down"


@contextmanager
def _peran_sementara(dsn_admin: str, atribut: str) -> Iterator[tuple[str, str]]:
    """Peran LOGIN sekali pakai dengan `atribut` tertentu; dilepas sesudah uji."""
    nama, sandi = f"hvx_uji_peran_{secrets.token_hex(4)}", secrets.token_urlsafe(18)
    with psycopg.connect(psycopg_dsn(dsn_admin), autocommit=True) as k:
        k.execute(
            sql.SQL("CREATE ROLE {} LOGIN {} PASSWORD {}").format(
                sql.Identifier(nama), sql.SQL(atribut), sql.Literal(sandi)
            )
        )
    try:
        yield nama, sandi
    finally:
        with psycopg.connect(psycopg_dsn(dsn_admin), autocommit=True) as k:
            k.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(nama)))


async def _mulai(dsn: str, url_redis: str) -> None:
    app = create_app(Settings(database_url=dsn, redis_url=url_redis, env="test"))
    async with LifespanManager(app):
        pass


async def test_api_menolak_mulai_sebagai_superuser_pemilik(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> None:
    """B-40 — peran yang dipakai api sebelum 17 Sep 2026."""
    db = basis_data_termigrasi("superuser")

    with pytest.raises(PeranTidakAman, match="superuser"):
        await _mulai(db.dsn_pemilik, url_redis_uji)


async def test_api_menolak_mulai_sebagai_peran_bypassrls(
    basis_data_termigrasi: Callable[[str], BasisDataV0], dsn_admin_uji: str, url_redis_uji: str
) -> None:
    db = basis_data_termigrasi("bypassrls")

    with _peran_sementara(dsn_admin_uji, "NOSUPERUSER BYPASSRLS") as (nama, sandi):
        dsn = dsn_ke(dsn_admin_uji, nama_db(db.dsn_pemilik), nama, sandi)
        with pytest.raises(PeranTidakAman, match="BYPASSRLS"):
            await _mulai(dsn, url_redis_uji)


async def test_api_menolak_mulai_sebagai_pemilik_tabel_yang_bukan_superuser(
    basis_data_termigrasi: Callable[[str], BasisDataV0], dsn_admin_uji: str, url_redis_uji: str
) -> None:
    """Pemilik tabel tidak terkena RLS walau bukan superuser — B-40 yang lebih sulit dilihat."""
    db = basis_data_termigrasi("pemilik")

    with _peran_sementara(dsn_admin_uji, "NOSUPERUSER NOBYPASSRLS") as (nama, sandi):
        with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
            k.execute(
                sql.SQL("ALTER TABLE journal_entries OWNER TO {}").format(sql.Identifier(nama))
            )
        try:
            dsn = dsn_ke(dsn_admin_uji, nama_db(db.dsn_pemilik), nama, sandi)
            with pytest.raises(PeranTidakAman, match=r"pemilik 1 tabel \(journal_entries"):
                await _mulai(dsn, url_redis_uji)
        finally:
            with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
                k.execute("ALTER TABLE journal_entries OWNER TO CURRENT_USER")


async def test_api_menolak_mulai_sebagai_peran_pekerja(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str
) -> None:
    """S4 — api menghadap internet: peran yang bisa memanggil fungsi relay & penyelaras
    (linimasa semua pengguna di luar RLS) tidak boleh menjadi perannya."""
    db = basis_data_termigrasi("api-pekerja")

    with pytest.raises(PeranTidakAman, match="hvx_pekerja"):
        await _mulai(db.dsn_pekerja, url_redis_uji)


@pytest.mark.parametrize(
    ("peran", "alasan"),
    [
        # Kebalikan uji di atas: relay yang tidak bisa memanggil fungsinya gagal di
        # tiap putaran, diam-diam di log — lebih baik pekerja menolak mulai.
        ("dsn_aplikasi", "hvx_pekerja"),
        # B-40 berlaku juga bagi pekerja: konsumen membaca event di bawah RLS pemiliknya.
        ("dsn_pemilik", "superuser"),
    ],
)
async def test_pekerja_menolak_mulai_dengan_peran_yang_salah(
    basis_data_termigrasi: Callable[[str], BasisDataV0],
    url_redis_uji: str,
    peran: str,
    alasan: str,
) -> None:
    db = basis_data_termigrasi("pekerja-peran")
    settings = Settings(database_url=getattr(db, peran), redis_url=url_redis_uji, env="test")
    berhenti = asyncio.Event()
    # Pekerja yang TIDAK menolak berjalan terus. Ia dihentikan sesudah 10 dtk, jadi
    # pemeriksaan yang hilang terbaca "DID NOT RAISE" — bukan uji yang menggantung
    # (tinjauan Sprint 3: mutasinya menahan seluruh uji mutasi tanpa batas).
    henti = asyncio.get_running_loop().call_later(10, berhenti.set)
    try:
        with pytest.raises(PeranTidakAman, match=alasan):
            await pekerja.jalankan(settings, berhenti)
    finally:
        henti.cancel()
