"""Amplop galat spec/04 untuk SEMUA jawaban galat: `{"error": {"code", "message", "details"?}}`.

Galat 500 dirender middleware log (tugas 0.5) — `ServerErrorMiddleware`
Starlette berada di luar middleware pengguna. Berkas ini menangani sisanya:
galat yang dilempar kode (`GalatApi`), `HTTPException` Starlette (404, 405),
dan galat validasi permintaan.

🔴 **Galat validasi tidak pernah memantulkan masukan.** Bawaan FastAPI
mengembalikan `{"detail": [{"input": …}]}` — untuk `POST /v1/auth/login`
itu berarti sandi yang salah bentuk dikirim balik ke klien, dan tercatat di
log mana pun yang menyimpan jawaban. Rincian di sini hanya `loc`, `msg`,
dan `type`.

Kode status mengikuti spec/04: `400` bentuk salah · `401` belum masuk ·
`403` izin ditolak · `404` · `409` bentrok · `422` aturan bisnis · `429`
batas laju.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

_KODE_BAWAAN: dict[int, str] = {
    400: "invalid_request",
    401: "unauthenticated",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "unprocessable",
    429: "rate_limited",
}


class GalatApi(Exception):
    """Galat yang sengaja dikembalikan ke klien — pesannya aman dibaca siapa pun."""

    def __init__(
        self,
        status: int,
        kode: str,
        pesan: str,
        *,
        rincian: Any | None = None,
        header: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(pesan)
        self.status = status
        self.kode = kode
        self.pesan = pesan
        self.rincian = rincian
        self.header = dict(header or {})


def jawaban_galat(
    status: int,
    kode: str,
    pesan: str,
    rincian: Any | None = None,
    header: Mapping[str, str] | None = None,
) -> JSONResponse:
    isi: dict[str, Any] = {"code": kode, "message": pesan}
    if rincian is not None:
        isi["details"] = rincian
    return JSONResponse(status_code=status, content={"error": isi}, headers=dict(header or {}))


def _rincian_validasi(galat: Sequence[Any]) -> list[dict[str, Any]]:
    return [
        {
            "loc": [str(bagian) for bagian in g.get("loc", ())],
            "msg": g.get("msg"),
            "type": g.get("type"),
        }
        for g in galat
    ]


async def _tangani_galat_api(_request: Request, galat: Exception) -> JSONResponse:
    if not isinstance(galat, GalatApi):  # pragma: no cover - dipasang hanya untuk tipe ini
        raise TypeError(type(galat).__name__)
    return jawaban_galat(galat.status, galat.kode, galat.pesan, galat.rincian, galat.header)


async def _tangani_http(_request: Request, galat: Exception) -> JSONResponse:
    if not isinstance(
        galat, StarletteHTTPException
    ):  # pragma: no cover - dipasang hanya untuk tipe ini
        raise TypeError(type(galat).__name__)
    kode = _KODE_BAWAAN.get(galat.status_code, f"http_{galat.status_code}")
    try:
        pesan = HTTPStatus(galat.status_code).phrase
    except ValueError:
        pesan = "Galat"
    return jawaban_galat(galat.status_code, kode, pesan, header=galat.headers)


async def _tangani_validasi(_request: Request, galat: Exception) -> JSONResponse:
    if not isinstance(
        galat, RequestValidationError
    ):  # pragma: no cover - dipasang hanya untuk tipe ini
        raise TypeError(type(galat).__name__)
    return jawaban_galat(
        400, "invalid_request", "Bentuk permintaan tidak sah.", _rincian_validasi(galat.errors())
    )


def pasang_penangan_galat(app: FastAPI) -> None:
    app.add_exception_handler(GalatApi, _tangani_galat_api)
    app.add_exception_handler(StarletteHTTPException, _tangani_http)
    app.add_exception_handler(RequestValidationError, _tangani_validasi)
