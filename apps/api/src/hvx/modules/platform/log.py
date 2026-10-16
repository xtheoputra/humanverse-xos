"""Log terstruktur + `request_id` — spec/07 tugas 0.5.

Selesai bila: tiap baris log punya `request_id`, `user_id?`, `latency_ms`.

Tafsiran yang dipakai, dan kenapa: `request_id` dan `user_id` ada di **setiap**
baris (`None` di luar permintaan HTTP), sebab keduanya yang dipakai untuk
menelusuri. `latency_ms` hanya berarti pada baris **penutup** permintaan
(`request.completed`) — baris lain di tengah permintaan belum punya latensi
untuk dilaporkan, dan mengisinya dengan angka sementara akan menyesatkan.

Middleware ditulis sebagai ASGI murni, bukan `BaseHTTPMiddleware`: yang kedua
menjalankan aplikasi di tugas terpisah, sehingga `user_id` yang diikat
dependensi autentikasi (Sprint 1) tidak akan pernah terlihat di baris penutup,
dan ia menahan respons streaming yang dibutuhkan SSE (tugas 4.8).

🔴 **Galat yang tak tertangani dirender DI SINI, bukan oleh Starlette.**
`ServerErrorMiddleware` Starlette selalu berada di LUAR middleware pengguna, dan
ia mengirim 500 lewat `send` aslinya — jadi 500 versi pertama tidak pernah
membawa `X-Request-ID`, tepat pada respons yang paling perlu ditelusuri, dan
uvicorn mencatat traceback kedua dengan `request_id: null`. Akibatnya bagi
Sprint 1+: handler `app.exception_handler(Exception)` **tidak akan pernah
terpanggil** untuk galat yang sampai ke sini; amplop galat 500 spec/04 dibuat
oleh `_jawaban_galat_internal`.

🔒 **Galat basis data dicatat TANPA pesannya** (`_galat_basis_data_tanpa_isi`).
Pesan PostgreSQL membawa isi baris — `DETAIL: Key (email)=(…)`, `Failing row
contains (…)` — dan tidak ada yang bisa mengaturnya dari kode ini. Diukur di
tinjauan Sprint 1: email dan hash sandi sampai ke `request.failed`; begitu
tabel jurnal ditulis, isi jurnal pun akan sampai. Yang tetap dicatat: jejak
tumpukan, jenis galat, SQLSTATE, nama constraint · tabel · kolom, dan SQL
statis — cukup untuk menelusuri, tanpa satu nilai pun milik pengguna.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
import time
import traceback
import uuid
from collections.abc import MutableMapping
from typing import Any, TextIO

import structlog
from sqlalchemy.exc import StatementError
from starlette.types import ASGIApp, Message, Receive, Scope, Send

HEADER_REQUEST_ID = "x-request-id"
_POLA_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
# /health dipanggil pemeriksa kesehatan tiap beberapa detik; barisnya DEBUG
# supaya tidak menenggelamkan log yang dibaca manusia.
_JALUR_SENYAP = frozenset({"/health"})

log = structlog.get_logger("hvx.request")


def _pastikan_kunci_penelusuran(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    event_dict.setdefault("request_id", None)
    event_dict.setdefault("user_id", None)
    return event_dict


def _galat_dari(exc_info: Any) -> BaseException | None:
    """Bentuk `exc_info` yang diterima structlog: galat · tuple `sys.exc_info()` · `True`."""
    if isinstance(exc_info, BaseException):
        return exc_info
    if isinstance(exc_info, tuple):
        return exc_info[1] if len(exc_info) == 3 else None
    return sys.exc_info()[1] if exc_info else None


def _rantai(galat: BaseException) -> list[BaseException]:
    """Rantai `__cause__`/`__context__`, sebab paling awal dulu — urutan cetak traceback."""
    rantai: list[BaseException] = []
    g: BaseException | None = galat
    while g is not None and all(g is not r for r in rantai):
        rantai.append(g)
        if g.__cause__ is not None:
            g = g.__cause__
        else:
            g = None if g.__suppress_context__ else g.__context__
    return rantai[::-1]


def _dari_basis_data(g: BaseException) -> bool:
    # SQLAlchemy membungkus galat driver; galat driver (asyncpg · psycopg) membawa SQLSTATE.
    return isinstance(g, StatementError) or hasattr(g, "sqlstate")


def _anggota(g: BaseException) -> tuple[BaseException, ...]:
    """Isi kelompok galat (`asyncio.TaskGroup`, `except*`) — kosong bagi galat biasa.

    🔴 Tinjauan Sprint 1: penyaring versi pertama hanya menelusuri
    `__cause__`/`__context__`, jadi galat UNIQUE di dalam TaskGroup — bentuk yang
    dipakai SSE FastAPI (tugas 4.8) — tercetak lengkap dengan `DETAIL`-nya.
    """
    return tuple(g.exceptions) if isinstance(g, BaseExceptionGroup) else ()


def _menyentuh_basis_data(galat: BaseException) -> bool:
    return any(
        _dari_basis_data(g) or any(_menyentuh_basis_data(a) for a in _anggota(g))
        for g in _rantai(galat)
    )


def _jejak_tanpa_isi(galat: BaseException) -> str:
    bagian: list[str] = []
    for i, g in enumerate(_rantai(galat)):
        if i:
            bagian.append("\nGalat di atas menyebabkan galat berikut:\n\n")
        if g.__traceback__ is not None:
            bagian.append("Traceback (most recent call last):\n")
            bagian.extend(traceback.format_tb(g.__traceback__))
        bagian.append(_ringkas_tanpa_isi(g) + "\n")
        anggota = _anggota(g)
        for n, a in enumerate(anggota, 1):
            bagian.append(f"+-- galat {n} dari {len(anggota)} di dalam kelompok:\n")
            bagian.extend("| " + b for b in _jejak_tanpa_isi(a).splitlines(True))
    return "".join(bagian)


def _ringkas_tanpa_isi(g: BaseException) -> str:
    """Jenis galat + pengenal yang bukan nilai: SQLSTATE, constraint/tabel/kolom, SQL statis."""
    nama = f"{type(g).__module__}.{type(g).__qualname__}"
    if not _dari_basis_data(g):
        return f"{nama}: <pesan tidak dicatat — rantai galat basis data>"
    asal = getattr(g, "orig", None)
    rincian = {
        "sqlstate": getattr(g, "sqlstate", None) or getattr(asal, "sqlstate", None),
        "constraint": getattr(g, "constraint_name", None),
        "tabel": getattr(g, "table_name", None),
        "kolom": getattr(g, "column_name", None),
        # SQL statis repo (bandit menolak SQL rakitan); parameternya tidak pernah di sini
        "sql": " ".join(str(g.statement).split())[:300] if isinstance(g, StatementError) else None,
    }
    isi = " ".join(f"{k}={v}" for k, v in rincian.items() if v)
    return f"{nama}: <pesan tidak dicatat> {isi}".rstrip()


def _galat_basis_data_tanpa_isi(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Ganti `exc_info` galat basis data dengan jejak tanpa pesan — lihat docstring modul."""
    galat = _galat_dari(event_dict.get("exc_info"))
    if galat is None or not _menyentuh_basis_data(galat):
        return event_dict
    event_dict.pop("exc_info", None)
    event_dict["exception"] = _jejak_tanpa_isi(galat)
    return event_dict


def konfigurasi_log(level: str = "INFO", json: bool = True, stream: TextIO | None = None) -> None:
    """Satu jalur keluaran untuk structlog DAN logging bawaan (uvicorn, alembic).

    `stream` bawaannya stdout proses (12-factor: log adalah aliran, bukan berkas).
    """
    praproses: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _pastikan_kunci_penelusuran,
    ]
    penyaji: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer()
    )

    # Galat dirender di SATU tempat untuk kedua jalur (structlog & logging
    # bawaan), dan galat basis data disaring SEBELUM dirender.
    jejak: list[structlog.types.Processor] = [
        _galat_basis_data_tanpa_isi,
        structlog.processors.format_exc_info,
    ]
    structlog.configure(
        processors=[
            *praproses,
            *jejak,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=praproses,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            *jejak,
            penyaji,
        ],
    )
    handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    handler.setFormatter(formatter)

    akar = logging.getLogger()
    akar.handlers[:] = [handler]
    akar.setLevel(level)
    # Baris akses uvicorn digantikan `request.completed`, yang membawa
    # request_id; dua baris untuk satu permintaan hanya menggandakan volume.
    logging.getLogger("uvicorn.access").disabled = True
    for nama in ("uvicorn", "uvicorn.error"):
        pencatat = logging.getLogger(nama)
        pencatat.handlers.clear()
        pencatat.propagate = True
        # dictConfig uvicorn menyetel INFO pada pencatatnya sendiri; tanpa ini
        # HVX_LOG_LEVEL=WARNING tetap meloloskan baris INFO uvicorn.
        pencatat.setLevel(logging.NOTSET)


def ikat_pengguna(user_id: str) -> None:
    """Dipanggil dependensi autentikasi (Sprint 1) begitu pengguna dikenali.

    🛑 **Wajib dipanggil dari `async def`.** FastAPI menjalankan dependensi dan
    endpoint `def` di threadpool dengan SALINAN contextvars: ikatan di sana
    hilang dari baris lain — dari dependensi sinkron, bahkan dari endpoint yang
    memakainya. Diukur, bukan diduga. Maka pemanggilan tanpa event loop
    **ditolak**, bukan dibiarkan diam-diam tidak berefek.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        raise RuntimeError(
            "ikat_pengguna() harus dipanggil dari `async def`: dependensi/endpoint sinkron "
            "berjalan di threadpool dengan salinan contextvars, dan user_id-nya akan hilang"
        ) from None
    structlog.contextvars.bind_contextvars(user_id=user_id)


def _request_id_dari(scope: Scope) -> str:
    for kunci, nilai in scope.get("headers", []):
        if kunci == HEADER_REQUEST_ID.encode():
            calon = str(nilai.decode("latin-1"))
            # Nilai dari klien masuk log apa adanya; yang tidak berbentuk id
            # (spasi, baris baru, 10 kB) diganti, bukan dipercaya.
            if _POLA_REQUEST_ID.fullmatch(calon):
                return calon
            break
    return uuid.uuid4().hex


def _jawaban_galat_internal() -> tuple[bytes, list[tuple[bytes, bytes]]]:
    """Amplop galat spec/04 — tanpa rincian galat: rincian hanya ke log."""
    badan = json.dumps(
        {"error": {"code": "internal_error", "message": "Terjadi galat internal."}}
    ).encode()
    return badan, [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(badan)).encode()),
    ]


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _request_id_dari(scope)
        token = structlog.contextvars.bind_contextvars(request_id=request_id, user_id=None)
        mulai = time.perf_counter()
        status = 500
        sudah_mulai = False

        async def kirim(message: Message) -> None:
            nonlocal status, sudah_mulai
            if message["type"] == "http.response.start":
                sudah_mulai = True
                status = message["status"]
                headers = list(message.get("headers", []))
                headers.append((HEADER_REQUEST_ID.encode(), request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, kirim)
        except Exception:
            log.exception("request.failed", method=scope["method"], path=scope["path"])
            if sudah_mulai:
                # Respons sudah setengah terkirim (mis. streaming): tidak ada
                # yang bisa diperbaiki di sini; serahkan ke server.
                raise
            badan, headers = _jawaban_galat_internal()
            await kirim({"type": "http.response.start", "status": 500, "headers": headers})
            await kirim({"type": "http.response.body", "body": badan})
        finally:
            latency_ms = round((time.perf_counter() - mulai) * 1000, 2)
            tulis = log.debug if scope["path"] in _JALUR_SENYAP else log.info
            tulis(
                "request.completed",
                method=scope["method"],
                path=scope["path"],
                status=status,
                latency_ms=latency_ms,
            )
            structlog.contextvars.reset_contextvars(**token)
