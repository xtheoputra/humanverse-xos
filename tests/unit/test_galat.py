"""Amplop galat spec/04 — dan galat validasi yang tidak pernah memantulkan masukan."""

from __future__ import annotations

from uuid import UUID, uuid4

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from hvx.modules.platform import GalatApi, pasang_penangan_galat


class _Masuk(BaseModel):
    email: str
    password: str
    umur: int


def _app() -> FastAPI:
    app = FastAPI()
    pasang_penangan_galat(app)

    @app.post("/masuk")
    async def masuk(badan: _Masuk) -> dict[str, str]:
        return {"ok": badan.email}

    @app.get("/bentrok")
    async def bentrok() -> None:
        raise GalatApi(409, "conflict", "Email sudah terdaftar.", header={"X-Uji": "1"})

    return app


async def _minta(metode: str, jalur: str, **kw: object) -> httpx.Response:
    transport = httpx.ASGITransport(app=_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as k:
        return await k.request(metode, jalur, **kw)  # type: ignore[arg-type]


async def test_galat_validasi_400_beramplop_tanpa_memantulkan_sandi() -> None:
    r = await _minta(
        "POST", "/masuk", json={"email": "a@b.id", "password": "rahasia-sekali-123", "umur": "tua"}
    )

    assert r.status_code == 400
    galat = r.json()["error"]
    assert galat["code"] == "invalid_request"
    assert galat["details"] == [
        {"loc": ["body", "umur"], "msg": galat["details"][0]["msg"], "type": "int_parsing"}
    ]
    assert "rahasia-sekali-123" not in r.text
    assert "tua" not in r.text, "nilai masukan dipantulkan kembali"


async def test_galat_api_beramplop_dengan_header() -> None:
    r = await _minta("GET", "/bentrok")

    assert r.status_code == 409
    assert r.json() == {"error": {"code": "conflict", "message": "Email sudah terdaftar."}}
    assert r.headers["x-uji"] == "1"


async def test_rute_tak_dikenal_404_beramplop() -> None:
    r = await _minta("GET", "/tidak-ada")

    assert r.status_code == 404
    assert r.json() == {"error": {"code": "not_found", "message": "Not Found"}}


class _Buat(BaseModel):
    model_config = {"extra": "forbid"}

    id: UUID
    judul: str


def _app_buat() -> FastAPI:
    app = FastAPI()
    pasang_penangan_galat(app)

    @app.post("/buat/{induk_id}")
    async def buat(induk_id: UUID, badan: _Buat) -> dict[str, str]:
        return {"ok": str(induk_id)}

    return app


async def _minta_buat(jalur: str, isi: object) -> httpx.Response:
    transport = httpx.ASGITransport(app=_app_buat())
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as k:
        return await k.post(jalur, json=isi)


async def test_uuid_salah_tidak_mengutip_karakter_masukan() -> None:
    """Tinjauan Sprint 2 (E-174): pesan `uuid_parsing` bawaan pydantic berbunyi
    ``found `z` at 1`` — karakter masukan, dikutip balik."""
    r = await _minta_buat("/buat/zzzz-rahasia", {"id": "q-rahasia-123", "judul": "x"})

    assert r.status_code == 400
    assert "rahasia" not in r.text
    assert "`z`" not in r.text, "pesan galat mengutip masukan"
    assert "`q`" not in r.text, "pesan galat mengutip masukan"
    jenis = {d["type"] for d in r.json()["error"]["details"]}
    assert jenis == {"uuid_parsing"}


async def test_kunci_tak_dikenal_tidak_dipantulkan_di_loc() -> None:
    """Nama kunci yang dikirim klien adalah masukan — `loc` hanya memuat nama milik api."""
    r = await _minta_buat(
        f"/buat/{uuid4()}",
        {"id": str(uuid4()), "judul": "x", "kata_sandi_saya_Hunter2": 1},
    )

    assert r.status_code == 400
    assert "Hunter2" not in r.text, "loc galat memantulkan nama kunci dari klien"
    assert r.json()["error"]["details"] == [
        {"loc": ["body", "*"], "msg": "Extra inputs are not permitted", "type": "extra_forbidden"}
    ]


async def test_nama_medan_milik_api_tetap_disebut() -> None:
    r = await _minta_buat(f"/buat/{uuid4()}", {"id": str(uuid4())})

    assert r.json()["error"]["details"] == [
        {"loc": ["body", "judul"], "msg": "Field required", "type": "missing"}
    ]
