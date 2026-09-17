"""spec/07 1.7 — batas laju per pengguna & per IP: `429` dengan `Retry-After`.

Aplikasi utuh (create_app + lifespan) sebagai peran aplikasi, Redis sungguhan.
Batasnya dikecilkan lewat Settings supaya uji tidak mengirim ratusan
permintaan; tiap aplikasi memakai awalan Redis acak.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import AsyncExitStack

import httpx
import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from hvx.main import create_app
from hvx.modules.identity import PenyimpanSesi
from hvx.modules.platform import BatasLaju, PembatasLaju, Settings, buat_redis

pytestmark = pytest.mark.integration

SANDI = "sandi-panjang-uji-2026"
LONGGAR = "10000/60"

PembuatApi = Callable[..., Awaitable[FastAPI]]


@pytest.fixture
async def buat_api(v0_bersama: BasisDataV0, url_redis_uji: str) -> AsyncIterator[PembuatApi]:
    async with AsyncExitStack() as tumpukan:

        async def _buat(**batas: str) -> FastAPI:
            batas = {
                "rate_limit_ip": LONGGAR,
                "rate_limit_user": LONGGAR,
                "rate_limit_auth_ip": LONGGAR,
                "rate_limit_login_failures": LONGGAR,
                **batas,
            }
            app = create_app(
                Settings(
                    env="test",
                    database_url=v0_bersama.dsn_aplikasi,
                    redis_url=url_redis_uji,
                    redis_prefix=f"uji-{uuid.uuid4().hex[:12]}",
                    **batas,  # type: ignore[arg-type]
                )
            )
            await tumpukan.enter_async_context(LifespanManager(app))
            return app

        yield _buat


def _klien(app: FastAPI, ip: str = "203.0.113.7") -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, client=(ip, 50_000))
    return httpx.AsyncClient(transport=transport, base_url="http://uji")


async def _pengguna(app: FastAPI, db: BasisDataV0) -> str:
    """Pengguna + profil ditulis pemilik skema; token akses sah dari penyimpan sesi app."""
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
        (uid,) = k.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
            (f"{uuid.uuid4().hex}@uji.id",),
        ).fetchone() or (None,)
        k.execute(
            "INSERT INTO profiles (user_id, display_name, timezone) VALUES (%s, 'U', 'UTC')",
            (uid,),
        )
    assert isinstance(uid, uuid.UUID)
    s = app.state.settings
    sesi = PenyimpanSesi(
        app.state.redis, s.redis_prefix, s.access_token_ttl_s, s.refresh_token_ttl_s
    )
    return (await sesi.buat(uid)).access_token


def _periksa_429(r: httpx.Response, paling_lama_s: int) -> None:
    assert r.status_code == 429, r.text
    assert r.json() == {
        "error": {"code": "rate_limited", "message": "Terlalu banyak permintaan. Coba lagi nanti."}
    }
    nilai = r.headers.get("retry-after", "")
    assert nilai.isdigit(), "429 tanpa Retry-After"
    assert 1 <= int(nilai) <= paling_lama_s, nilai


async def test_mekanisme_meledak_sampai_batas_lalu_terisi_satu_per_interval(
    url_redis_uji: str,
) -> None:
    redis = buat_redis(url_redis_uji, socket_timeout_s=5, connect_timeout_s=2)
    pembatas = PembatasLaju(redis, f"uji-{uuid.uuid4().hex[:12]}")
    batas = BatasLaju("uji", 5, 1)  # satu jatah tiap 200 ms
    try:
        # bertanya tanpa mencatat tidak memakai jatah
        for _ in range(10):
            assert (await pembatas.ambil(batas, "s", catat=False)).lolos

        sisa = [(await pembatas.ambil(batas, "s")).sisa for _ in range(5)]
        ditolak = await pembatas.ambil(batas, "s")

        assert sisa == [4, 3, 2, 1, 0]
        assert not ditolak.lolos
        assert 0 < ditolak.coba_lagi_ms <= 200
        assert (await pembatas.ambil(batas, "subjek-lain")).lolos

        await asyncio.sleep(0.25)
        assert (await pembatas.ambil(batas, "s")).lolos

        await pembatas.lupakan(batas, "s")
        assert (await pembatas.ambil(batas, "s")).sisa == 4
    finally:
        await redis.aclose()


async def test_batas_ip_menjawab_429_dengan_retry_after_di_seluruh_v1(buat_api: PembuatApi) -> None:
    app = await buat_api(rate_limit_ip="3/60")  # satu jatah tiap 20 dtk
    async with _klien(app) as klien, _klien(app, "198.51.100.9") as tetangga:
        for _ in range(3):
            assert (await klien.get("/v1/me")).status_code == 401

        r = await klien.get("/v1/me")
        _periksa_429(r, paling_lama_s=20)
        assert r.headers.get("x-request-id"), (
            "429 tanpa X-Request-ID — middleware terpasang di luar"
        )
        # rute tak dikenal di bawah /v1 pun dihitung; IP lain tidak terkena
        assert (await klien.post("/v1/tidak-ada")).status_code == 429
        assert (await tetangga.get("/v1/me")).status_code == 401
        # /health di luar permukaan /v1 — pemeriksa kesehatan tidak pernah dijawab 429
        for _ in range(5):
            assert (await klien.get("/health")).status_code == 200


async def test_ipv6_satu_jaringan_64_berbagi_satu_jatah(buat_api: PembuatApi) -> None:
    app = await buat_api(rate_limit_ip="2/60")
    async with (
        _klien(app, "2001:db8:1:2::1") as a,
        _klien(app, "2001:db8:1:2::ffff") as a_ganti_alamat,
        _klien(app, "2001:db8:1:3::1") as jaringan_lain,
    ):
        assert (await a.get("/v1/me")).status_code == 401
        assert (await a.get("/v1/me")).status_code == 401

        assert (await a_ganti_alamat.get("/v1/me")).status_code == 429
        assert (await jaringan_lain.get("/v1/me")).status_code == 401


async def test_batas_per_pengguna_tidak_mengenai_pengguna_lain_di_ip_yang_sama(
    buat_api: PembuatApi, v0_bersama: BasisDataV0
) -> None:
    app = await buat_api(rate_limit_user="2/60")
    token_a, token_b = await _pengguna(app, v0_bersama), await _pengguna(app, v0_bersama)
    a = {"Authorization": f"Bearer {token_a}"}
    b = {"Authorization": f"Bearer {token_b}"}
    async with _klien(app) as klien:
        assert (await klien.get("/v1/me", headers=a)).status_code == 200
        assert (await klien.get("/v1/me", headers=a)).status_code == 200

        _periksa_429(await klien.get("/v1/me", headers=a), paling_lama_s=30)
        assert (await klien.get("/v1/me", headers=b)).status_code == 200


def _daftar(email: str) -> dict[str, object]:
    return {
        "email": email,
        "password": SANDI,
        "display_name": "Nadia",
        "timezone": "Asia/Jakarta",
        "consents": {"policy_version": "2026-09-17", "terms": True, "privacy": True},
    }


async def test_daftar_dan_masuk_berbagi_batas_per_ip_yang_lebih_ketat(buat_api: PembuatApi) -> None:
    app = await buat_api(rate_limit_auth_ip="2/600")
    email = f"{uuid.uuid4().hex[:12]}@uji.id"
    async with _klien(app) as klien, _klien(app, "198.51.100.9") as tetangga:
        assert (await klien.post("/v1/auth/register", json=_daftar(email))).status_code == 201
        salah = {"email": email, "password": "sandi-yang-keliru-sekali"}
        assert (await klien.post("/v1/auth/login", json=salah)).status_code == 401

        benar = {"email": email, "password": SANDI}
        _periksa_429(await klien.post("/v1/auth/login", json=benar), paling_lama_s=300)
        # refresh tidak ikut: klien di balik satu NAT menyegarkan dari IP yang sama
        for _ in range(3):
            segar = await klien.post("/v1/auth/refresh", json={"refresh_token": "hvxr_palsu"})
            assert segar.status_code == 401
        assert (await tetangga.post("/v1/auth/login", json=benar)).status_code == 200


async def test_login_gagal_dibatasi_per_akun_dan_berhasil_menghapus_hitungannya(
    buat_api: PembuatApi,
) -> None:
    app = await buat_api(rate_limit_login_failures="2/86400")
    email = f"{uuid.uuid4().hex[:12]}@uji.id"
    benar = {"email": email, "password": SANDI}
    salah = {"email": email, "password": "sandi-yang-keliru-sekali"}
    async with _klien(app) as klien, _klien(app, "198.51.100.9") as ip_lain:
        assert (await klien.post("/v1/auth/register", json=_daftar(email))).status_code == 201

        assert (await klien.post("/v1/auth/login", json=salah)).status_code == 401
        assert (await klien.post("/v1/auth/login", json=benar)).status_code == 200
        # berhasil masuk menghapus hitungan: dua kegagalan berikut masih dijawab 401
        assert (await klien.post("/v1/auth/login", json=salah)).status_code == 401
        assert (await klien.post("/v1/auth/login", json=salah)).status_code == 401

        # jatah habis: sandi BENAR pun ditolak — dari IP mana pun, huruf apa pun
        _periksa_429(await klien.post("/v1/auth/login", json=benar), paling_lama_s=43_200)
        huruf_besar = {"email": email.upper(), "password": SANDI}
        assert (await ip_lain.post("/v1/auth/login", json=huruf_besar)).status_code == 429

        # email tak terdaftar diperlakukan sama — 429 tidak membocorkan keberadaan akun
        asing = {"email": f"{uuid.uuid4().hex[:12]}@uji.id", "password": "sandi-yang-keliru-sekali"}
        assert [(await klien.post("/v1/auth/login", json=asing)).status_code for _ in range(3)] == [
            401,
            401,
            429,
        ]
