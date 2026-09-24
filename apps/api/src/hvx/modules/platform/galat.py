"""Amplop galat spec/04 untuk SEMUA jawaban galat: `{"error": {"code", "message", "details"?}}`.

Galat 500 dirender middleware log (tugas 0.5) — `ServerErrorMiddleware`
Starlette berada di luar middleware pengguna. Berkas ini menangani sisanya:
galat yang dilempar kode (`GalatApi`), `HTTPException` Starlette (404, 405),
dan galat validasi permintaan.

🔴 **Galat validasi tidak pernah memantulkan masukan.** Bawaan FastAPI
mengembalikan `{"detail": [{"input": …}]}` — untuk `POST /v1/auth/login`
itu berarti sandi yang salah bentuk dikirim balik ke klien, dan tercatat di
log mana pun yang menyimpan jawaban. Rincian di sini hanya `loc`, `msg`,
dan `type` — dan keduanya pun disaring (tinjauan Sprint 2, E-174):

* `msg` bawaan pydantic dipakai HANYA untuk jenis galat yang pesannya tidak
  memuat masukan (`_PESAN_AMAN`). `uuid_parsing` misalnya mengutip karakter
  yang salah — ``found `z` at 1`` — dan jenis yang belum dikenal jatuh ke
  pesan tetap. Gagal-tertutup: jenis baru di versi pydantic berikutnya tidak
  diam-diam mulai memantulkan.
* `loc` hanya memuat nama yang DINYATAKAN api (properti skema dan parameter di
  OpenAPI) dan indeks daftar. Kunci tak dikenal (`extra_forbidden`) adalah
  masukan klien — `{"kata_sandi_saya_Hunter2": 1}` — dan menjadi `*`.

Kode status mengikuti spec/04: `400` bentuk salah · `401` belum masuk ·
`403` izin ditolak · `404` · `409` bentrok · `422` aturan bisnis · `429`
batas laju.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from http import HTTPStatus
from typing import Any, cast

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


# Jenis galat pydantic yang pesan bawaannya dirakit HANYA dari batas milik api
# (panjang, pola, pilihan) — bukan dari isi masukan. Pesan `value_error` ditulis
# kode kita sendiri, yang tidak pernah mengutip nilai (AGENTS.md §7).
_PESAN_AMAN = frozenset(
    {
        "bool_parsing",
        "bool_type",
        "date_from_datetime_inexact",
        "date_from_datetime_parsing",
        "date_parsing",
        "date_type",
        "datetime_from_date_parsing",
        "datetime_parsing",
        "datetime_type",
        "decimal_max_digits",
        "decimal_max_places",
        "decimal_parsing",
        "decimal_type",
        "decimal_whole_digits",
        "dict_type",
        "enum",
        "extra_forbidden",
        "finite_number",
        "float_parsing",
        "float_type",
        "greater_than",
        "greater_than_equal",
        "int_from_float",
        "int_parsing",
        "int_type",
        "json_invalid",
        "less_than",
        "less_than_equal",
        "list_type",
        "literal_error",
        "missing",
        "model_attributes_type",
        "model_type",
        "string_pattern_mismatch",
        "string_too_long",
        "string_too_short",
        "string_type",
        "timezone_aware",
        "too_long",
        "too_short",
        "uuid_type",
        "value_error",
    }
)
_PESAN_TETAP = "Nilai tidak sah."
_TEMPAT = frozenset({"body", "query", "path", "header", "cookie"})


def _nama_dikenal(app: Any) -> frozenset[str]:
    """Nama medan dan parameter yang DINYATAKAN api — dibaca sekali dari OpenAPI-nya."""
    ada = getattr(app.state, "nama_masukan_dikenal", None)
    if ada is not None:
        return cast("frozenset[str]", ada)
    nama: set[str] = set(_TEMPAT)

    def jelajah(node: Any) -> None:
        if isinstance(node, dict):
            properti = node.get("properties")
            if isinstance(properti, dict):
                nama.update(properti)
            for isi in node.values():
                jelajah(isi)
        elif isinstance(node, list):
            for isi in node:
                jelajah(isi)

    skema = app.openapi()
    jelajah(skema.get("components", {}))
    for operasi in skema.get("paths", {}).values():
        for isi in operasi.values():
            if isinstance(isi, dict):
                nama.update(p["name"] for p in isi.get("parameters", []))
                jelajah(isi.get("requestBody", {}))
    hasil = frozenset(nama)
    app.state.nama_masukan_dikenal = hasil
    return hasil


def _rincian_validasi(galat: Sequence[Any], dikenal: frozenset[str]) -> list[dict[str, Any]]:
    rincian = []
    for g in galat:
        jenis = str(g.get("type", ""))
        loc = [
            bagian if isinstance(bagian, int) or bagian in dikenal else "*"
            for bagian in g.get("loc", ())
        ]
        rincian.append(
            {
                "loc": [str(bagian) for bagian in loc],
                "msg": g.get("msg") if jenis in _PESAN_AMAN else _PESAN_TETAP,
                "type": jenis,
            }
        )
    return rincian


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


async def _tangani_validasi(request: Request, galat: Exception) -> JSONResponse:
    if not isinstance(
        galat, RequestValidationError
    ):  # pragma: no cover - dipasang hanya untuk tipe ini
        raise TypeError(type(galat).__name__)
    rincian = _rincian_validasi(galat.errors(), _nama_dikenal(request.app))
    return jawaban_galat(400, "invalid_request", "Bentuk permintaan tidak sah.", rincian)


def pasang_penangan_galat(app: FastAPI) -> None:
    app.add_exception_handler(GalatApi, _tangani_galat_api)
    app.add_exception_handler(StarletteHTTPException, _tangani_http)
    app.add_exception_handler(RequestValidationError, _tangani_validasi)
