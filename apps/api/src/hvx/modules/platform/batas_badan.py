"""Batas ukuran badan permintaan — `413` sebelum apa pun membacanya (E-171).

FastAPI membaca badan UTUH ke memori sebelum dependensi berjalan — termasuk
autentikasi: badan dibutuhkan untuk memvalidasi parameter badan, dan
`platform.idempotensi` menyidiknya. Tanpa batas, satu permintaan TANPA akun
bisa mengirim satu gigabita ke memori proses api, 600 kali semenit dari satu IP
(tinjauan keamanan Sprint 2, dugaan D1). Batas laju menghitung permintaan,
bukan ukurannya.

`Content-Length` di atas batas ditolak tanpa membaca satu byte pun. Badan
ber-*chunked* (tanpa `Content-Length`) dihitung sambil dibaca, dan ditolak
begitu melewati batas — yang tersangga paling banyak `maks` byte.

Satu mebibita jauh di atas tulisan V0 terbesar (jurnal: teks, spec/01 `body
text`); yang butuh lebih — lampiran, suara — bukan badan JSON (spec/07 *Yang
TIDAK ada di backlog ini*).
"""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .galat import jawaban_galat

MAKS_BADAN_BYTE = 1_048_576


def _terlalu_besar(maks: int) -> JSONResponse:
    return jawaban_galat(413, "payload_too_large", f"Badan permintaan paling besar {maks} byte.")


class BatasBadanMiddleware:
    def __init__(self, app: ASGIApp, maks: int = MAKS_BADAN_BYTE) -> None:
        self.app = app
        self.maks = maks

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        panjang = dict(scope["headers"]).get(b"content-length")
        if panjang is not None:
            try:
                besar = int(panjang)
            except ValueError:
                besar = self.maks + 1  # Content-Length yang bukan angka: tolak, jangan tebak
            if besar > self.maks:
                await _terlalu_besar(self.maks)(scope, receive, send)
                return
            await self.app(scope, receive, send)
            return

        # Tanpa Content-Length: sangga sambil menghitung, lalu putar ulang ke aplikasi.
        tersangga: list[Message] = []
        terbaca = 0
        while True:
            pesan = await receive()
            tersangga.append(pesan)
            if pesan["type"] != "http.request":
                break
            terbaca += len(pesan.get("body", b""))
            if terbaca > self.maks:
                await _terlalu_besar(self.maks)(scope, receive, send)
                return
            if not pesan.get("more_body", False):
                break

        async def putar_ulang() -> Message:
            if tersangga:
                return tersangga.pop(0)
            return await receive()

        await self.app(scope, putar_ulang, send)
