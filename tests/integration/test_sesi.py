"""spec/07 1.2 — sesi di Redis + dependensi auth: token dicabut → 401 SEKETIKA.

Redis sungguhan; tiap uji memakai awalan kunci acak, jadi tidak ada sisa dari
uji lain yang bisa membuat hasil kebetulan benar.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI

from hvx.modules.identity import PenggunaDiperlukan, PenyimpanSesi, penyimpan_sesi
from hvx.modules.platform import Settings, buat_redis, pasang_penangan_galat

pytestmark = pytest.mark.integration


@pytest.fixture
async def app_sesi(url_redis_uji: str) -> AsyncIterator[FastAPI]:
    app = FastAPI()
    pasang_penangan_galat(app)
    app.state.settings = Settings(
        env="test",
        database_url="postgresql://tidak-dipakai",
        redis_url=url_redis_uji,
        redis_prefix=f"uji-{uuid.uuid4().hex[:12]}",
        access_token_ttl_s=120,
        refresh_token_ttl_s=3_600,
    )
    app.state.redis = buat_redis(url_redis_uji, socket_timeout_s=5, connect_timeout_s=2)

    @app.get("/rahasia")
    async def rahasia(pengguna: PenggunaDiperlukan) -> dict[str, str]:
        return {"user_id": str(pengguna.user_id)}

    try:
        yield app
    finally:
        await app.state.redis.aclose()


def _penyimpan(app: FastAPI) -> PenyimpanSesi:
    class _Permintaan:  # cukup untuk platform.redis_dari/settings_dari
        def __init__(self, app: FastAPI) -> None:
            self.app = app

    return penyimpan_sesi(_Permintaan(app))  # type: ignore[arg-type]


async def _get(app: FastAPI, token: str | None) -> httpx.Response:
    header = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://uji"
    ) as k:
        return await k.get("/rahasia", headers=header)


async def test_token_akses_yang_sah_meloloskan_pengguna_yang_benar(app_sesi: FastAPI) -> None:
    uid = uuid.uuid4()
    token = await _penyimpan(app_sesi).buat(uid)

    r = await _get(app_sesi, token.access_token)

    assert r.status_code == 200
    assert r.json() == {"user_id": str(uid)}
    assert token.access_token.startswith("hvxa_")
    assert token.refresh_token.startswith("hvxr_")


@pytest.mark.parametrize("token", [None, "hvxa_palsu", "bukan-token"])
async def test_tanpa_token_atau_token_palsu_401_beramplop(
    app_sesi: FastAPI, token: str | None
) -> None:
    r = await _get(app_sesi, token)

    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthenticated"
    assert r.headers["www-authenticate"].startswith("Bearer")


async def test_token_segar_tidak_bisa_dipakai_sebagai_token_akses(app_sesi: FastAPI) -> None:
    token = await _penyimpan(app_sesi).buat(uuid.uuid4())

    assert (await _get(app_sesi, token.refresh_token)).status_code == 401


async def test_sesi_dicabut_401_seketika(app_sesi: FastAPI) -> None:
    """DoD 1.2 — tidak menunggu kedaluwarsa token."""
    penyimpan = _penyimpan(app_sesi)
    uid = uuid.uuid4()
    token = await penyimpan.buat(uid)
    sesi = await penyimpan.periksa_akses(token.access_token)
    assert sesi is not None
    assert (await _get(app_sesi, token.access_token)).status_code == 200

    await penyimpan.cabut(sesi.sesi_id)

    assert (await _get(app_sesi, token.access_token)).status_code == 401
    assert (await penyimpan.segarkan(token.refresh_token)).token is None


async def test_penyegaran_merotasi_kedua_token(app_sesi: FastAPI) -> None:
    penyimpan = _penyimpan(app_sesi)
    lama = await penyimpan.buat(uuid.uuid4())

    hasil = await penyimpan.segarkan(lama.refresh_token)

    assert hasil.token is not None
    baru = hasil.token
    assert {baru.access_token, baru.refresh_token}.isdisjoint(
        {lama.access_token, lama.refresh_token}
    )
    assert (await _get(app_sesi, lama.access_token)).status_code == 401, "token akses lama hidup"
    assert (await _get(app_sesi, baru.access_token)).status_code == 200


async def test_token_segar_bekas_dipakai_lagi_mencabut_seluruh_sesi(app_sesi: FastAPI) -> None:
    """Pencuri memakai token segar lama sesudah pemiliknya merotasi: KEDUANYA kehilangan sesi."""
    penyimpan = _penyimpan(app_sesi)
    uid = uuid.uuid4()
    lama = await penyimpan.buat(uid)
    baru = (await penyimpan.segarkan(lama.refresh_token)).token
    assert baru is not None

    curian = await penyimpan.segarkan(lama.refresh_token)

    assert curian.token is None
    assert curian.dipakai_ulang is not None
    assert curian.dipakai_ulang.user_id == uid
    assert (await _get(app_sesi, baru.access_token)).status_code == 401
    assert (await penyimpan.segarkan(baru.refresh_token)).token is None


async def test_cabut_semua_mencabut_tiap_sesi_pengguna_saja(app_sesi: FastAPI) -> None:
    penyimpan = _penyimpan(app_sesi)
    a, b = uuid.uuid4(), uuid.uuid4()
    milik_a = [await penyimpan.buat(a) for _ in range(3)]
    milik_b = await penyimpan.buat(b)

    assert await penyimpan.cabut_semua(a) == 3

    for token in milik_a:
        assert (await _get(app_sesi, token.access_token)).status_code == 401
    assert (await _get(app_sesi, milik_b.access_token)).status_code == 200


async def test_redis_hanya_menyimpan_sidik_token(app_sesi: FastAPI) -> None:
    token = await _penyimpan(app_sesi).buat(uuid.uuid4())
    redis = app_sesi.state.redis
    awalan = app_sesi.state.settings.redis_prefix

    kunci = [k async for k in redis.scan_iter(match=f"{awalan}:*")]
    nilai = [await redis.get(k) for k in kunci if await redis.type(k) == "string"]
    semua = " ".join(kunci) + " " + " ".join(v for v in nilai if v)

    assert kunci
    assert token.access_token not in semua
    assert token.refresh_token not in semua
