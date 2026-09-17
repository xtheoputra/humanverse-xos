"""spec/07 0.5 — tiap baris log punya `request_id`, `user_id?`, `latency_ms`.

Tafsiran yang diuji (lihat docstring `hvx.modules.platform.log`):
`request_id` & `user_id` di SETIAP baris; `latency_ms` di baris penutup
permintaan.
"""

from __future__ import annotations

import io
import json
import logging
import re
from collections.abc import Callable, Iterator
from typing import Annotated, Any

import httpx
import pytest
import structlog
from fastapi import Depends, FastAPI

from hvx.modules.platform import RequestContextMiddleware, ikat_pengguna, konfigurasi_log


@pytest.fixture
def baris_log() -> Iterator[Callable[[], list[dict[str, Any]]]]:
    aliran = io.StringIO()
    konfigurasi_log(level="DEBUG", json=True, stream=aliran)

    def _ambil() -> list[dict[str, Any]]:
        keluaran, _ = aliran.getvalue(), aliran.truncate(0)
        aliran.seek(0)
        # SETIAP baris wajib JSON — baris yang bukan JSON adalah kegagalan,
        # bukan sesuatu untuk disaring.
        return [json.loads(b) for b in keluaran.splitlines()]

    yield _ambil
    structlog.contextvars.clear_contextvars()
    logging.getLogger().handlers.clear()


def masuk_sinkron() -> str:
    """Dependensi `def` — FastAPI menjalankannya di threadpool.

    Di tingkat modul, bukan di dalam `_app`: dengan anotasi tertunda
    (`from __future__ import annotations`) FastAPI hanya bisa menyelesaikan
    nama global."""
    ikat_pengguna("u-sinkron")
    return "u-sinkron"


def _app() -> FastAPI:
    app = FastAPI()
    log = structlog.get_logger("uji")

    @app.get("/kerja")
    async def kerja() -> dict[str, str]:
        log.info("di.tengah.permintaan")
        logging.getLogger("pustaka.lain").warning("logging bawaan juga")
        return {"ok": "ya"}

    @app.get("/masuk")
    async def masuk() -> dict[str, str]:
        ikat_pengguna("u-123")
        log.info("pengguna.dikenali")
        return {"ok": "ya"}

    @app.get("/meledak")
    async def meledak() -> None:
        raise RuntimeError("bom rahasia-internal")

    @app.get("/masuk-sinkron")
    async def masuk_lewat_dependensi_sinkron(
        _u: Annotated[str, Depends(masuk_sinkron)],
    ) -> dict[str, str]:
        return {"ok": "ya"}

    app.add_middleware(RequestContextMiddleware)
    return app


def _klien(app: FastAPI) -> httpx.AsyncClient:
    # raise_app_exceptions=True (bawaan): kalau galat bocor keluar middleware,
    # uji ini meledak — middleware wajib merender 500-nya sendiri.
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji")


async def test_tiap_baris_membawa_request_id_dan_user_id(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        r = await klien.get("/kerja")

    baris = baris_log()
    rid = r.headers["x-request-id"]
    dalam_permintaan = [b for b in baris if b.get("request_id") == rid]

    assert len(dalam_permintaan) == 3, baris  # structlog · logging bawaan · penutup
    assert all("user_id" in b for b in baris)
    assert all("request_id" in b for b in baris)


async def test_baris_penutup_membawa_latency_status_dan_metode(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        await klien.get("/kerja")

    (penutup,) = [b for b in baris_log() if b["event"] == "request.completed"]

    assert isinstance(penutup["latency_ms"], int | float)
    assert penutup["latency_ms"] >= 0
    assert penutup["status"] == 200
    assert penutup["method"] == "GET"
    assert penutup["path"] == "/kerja"


async def test_user_id_yang_diikat_terlihat_sampai_baris_penutup(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        await klien.get("/masuk")

    baris = baris_log()
    (penutup,) = [b for b in baris if b["event"] == "request.completed"]

    assert penutup["user_id"] == "u-123"


async def test_konteks_tidak_bocor_ke_permintaan_berikutnya(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        await klien.get("/masuk")
        r2 = await klien.get("/kerja")

    rid2 = r2.headers["x-request-id"]
    kedua = [b for b in baris_log() if b.get("request_id") == rid2]

    assert kedua
    assert all(b["user_id"] is None for b in kedua)


async def test_request_id_klien_yang_sah_dipakai_ulang(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        r = await klien.get("/kerja", headers={"X-Request-ID": "jejak-klien.01"})

    assert r.headers["x-request-id"] == "jejak-klien.01"
    assert any(b.get("request_id") == "jejak-klien.01" for b in baris_log())


@pytest.mark.parametrize("buruk", ["ada spasi", "a" * 129, "baris\\nbaru", ""])
async def test_request_id_klien_yang_tidak_berbentuk_id_diganti(
    buruk: str, baris_log: Callable[[], list[dict[str, Any]]]
) -> None:
    async with _klien(_app()) as klien:
        r = await klien.get("/kerja", headers={"X-Request-ID": buruk})

    rid = r.headers["x-request-id"]
    assert rid != buruk
    assert re.fullmatch(r"[0-9a-f]{32}", rid)
    baris_log()


async def test_permintaan_yang_meledak_tetap_tercatat_dengan_status_500(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    async with _klien(_app()) as klien:
        r = await klien.get("/meledak", headers={"X-Request-ID": "klien-500"})

    assert r.status_code == 500
    # 500 versi pertama dikirim ServerErrorMiddleware Starlette di LUAR
    # middleware — tanpa X-Request-ID, tepat pada respons yang perlu ditelusuri.
    assert r.headers["x-request-id"] == "klien-500"
    assert r.json() == {"error": {"code": "internal_error", "message": "Terjadi galat internal."}}
    assert "rahasia-internal" not in r.text
    baris = baris_log()
    gagal = [b for b in baris if b["event"] == "request.failed"]
    (penutup,) = [b for b in baris if b["event"] == "request.completed"]
    assert gagal
    assert gagal[0]["request_id"] == "klien-500"
    assert "RuntimeError" in str(gagal[0].get("exception"))
    assert penutup["status"] == 500
    assert "latency_ms" in penutup


async def test_ikat_pengguna_dari_konteks_sinkron_ditolak_bukan_diam(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    """Dari dependensi `def`, ikatan contextvars hilang di threadpool — diukur.
    Karena itu ia GAGAL keras, bukan diam-diam tidak berefek."""
    async with _klien(_app()) as klien:
        r = await klien.get("/masuk-sinkron")

    assert r.status_code == 500
    gagal = [b for b in baris_log() if b["event"] == "request.failed"]
    assert "async def" in str(gagal[0].get("exception"))


def test_level_log_juga_berlaku_bagi_pencatat_uvicorn() -> None:
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)  # seperti dictConfig uvicorn
    aliran = io.StringIO()
    konfigurasi_log(level="WARNING", json=True, stream=aliran)

    logging.getLogger("uvicorn.error").info("Started server process")
    logging.getLogger("uvicorn.error").warning("peringatan tetap lolos")

    baris = [json.loads(b) for b in aliran.getvalue().splitlines()]
    assert [b["event"] for b in baris] == ["peringatan tetap lolos"]
    logging.getLogger().handlers.clear()


def test_baris_di_luar_permintaan_tetap_punya_kunci_penelusuran(
    baris_log: Callable[[], list[dict[str, Any]]],
) -> None:
    structlog.get_logger("uji").info("proses.mulai")

    (b,) = baris_log()
    assert b["request_id"] is None
    assert b["user_id"] is None
