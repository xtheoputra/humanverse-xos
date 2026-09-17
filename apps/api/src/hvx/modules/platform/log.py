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
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
import time
import uuid
from collections.abc import MutableMapping
from typing import Any, TextIO

import structlog
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

    structlog.configure(
        processors=[
            *praproses,
            structlog.processors.format_exc_info,
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
            structlog.processors.format_exc_info,
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
