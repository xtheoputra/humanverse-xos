"""`Idempotency-Key` untuk tulisan domain — spec/04 *Aturan lintas endpoint* (E-165).

`POST`/`PATCH` domain menerima header `Idempotency-Key`: kunci yang sama
mengembalikan hasil yang sama — status dan badan jawaban PERTAMA diputar
ulang, bertanda `Idempotent-Replayed: true`. Bentuknya mengikuti draf IETF
*The Idempotency-Key HTTP Header Field*:

* kunci yang sama dengan permintaan BERBEDA (metode, jalur, atau badan) →
  `422 idempotency_key_reused` — bukan diputar ulang diam-diam: permintaan
  kedua itu permintaan lain, dan jawaban pertama bukan jawabannya;
* kunci yang sama saat permintaan pertama MASIH berjalan →
  `409 idempotency_in_progress` — dua tulisan serentak tidak bisa keduanya jalan;
* hanya jawaban 2xx yang disimpan: galat diulang dengan menjalankan ulang
  permintaannya, supaya 429 atau galat sesaat tidak terkunci sebagai jawaban.

🔒 **Kunci milik PENGGUNA** — `user_id` bagian dari nama kunci Redis. Kunci
yang sama dari dua pengguna tidak pernah saling memutar ulang jawaban: itu
bukan salah hitung, itu data pengguna A dikirim ke pengguna B (H-27).

⚠️ **Batas yang diakui:** jawaban disimpan di Redis SESUDAH transaksi basis
data commit. Proses yang mati di antara keduanya meninggalkan penanda
"sedang berjalan" yang kedaluwarsa sendiri (`_UMUR_PROSES_S`); ulangan
sesudahnya menjalankan tulisan lagi. Untuk `POST` yang membuat baris, id
buatan klien (spec/04 — dukungan luring) membuat ulangan itu `409`, bukan
baris kedua — klien luring wajib membuat id-nya sendiri.

`/v1/auth/*` sengaja TIDAK memakainya (K-21): jawabannya memuat token, dan
memutar ulang jawaban berarti menyimpan token mentah.

Dipakai sebagai dependensi, bukan dipanggil diam-diam di badan rute:
`tests/unit/test_idempotensi_terpasang.py` memeriksa TIAP rute `POST`/`PATCH`
domain menyatakannya — rute baru yang lupa tidak bisa lolos.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from .galat import GalatApi
from .keadaan import redis_dari, settings_dari

HEADER_KUNCI = "Idempotency-Key"
HEADER_DIPUTAR_ULANG = "Idempotent-Replayed"
POLA_KUNCI = r"^[A-Za-z0-9_.:=-]{1,128}$"

# Umur penanda "sedang berjalan": tulisan domain selesai dalam milidetik; penanda
# yang yatim karena proses mati tidak menahan kunci itu lebih lama dari ini.
_UMUR_PROSES_S = 60
# Umur jawaban yang disimpan — cukup untuk klien luring yang mengulang besok pagi.
UMUR_JAWABAN_S = 86_400

# Hapus penanda HANYA bila isinya masih penanda milik permintaan ini — penanda
# yang sudah kedaluwarsa dan diambil permintaan lain tidak ikut terhapus.
_HAPUS_JIKA_SAMA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
"""


@dataclass(frozen=True)
class Jawaban:
    """Hasil kerja sebuah rute tulis: kode status dan isi yang bisa di-JSON-kan."""

    status: int
    isi: Any


def _sidik_permintaan(metode: str, jalur: str, kueri: str, badan: bytes) -> str:
    """Sidik isi permintaan — badan JSON dinormalkan, supaya spasi tidak mengubahnya."""
    try:
        isi = json.dumps(json.loads(badan), sort_keys=True, separators=(",", ":")).encode()
    except (ValueError, UnicodeDecodeError):
        isi = badan
    h = hashlib.sha256()
    for bagian in (metode.encode(), jalur.encode(), kueri.encode(), isi):
        h.update(bagian)
        h.update(b"\x00")
    return h.hexdigest()


def _dipakai_ulang() -> GalatApi:
    return GalatApi(
        422,
        "idempotency_key_reused",
        "Idempotency-Key ini sudah dipakai untuk permintaan lain. Pakai kunci baru.",
    )


def _sedang_berjalan() -> GalatApi:
    return GalatApi(
        409,
        "idempotency_in_progress",
        "Permintaan dengan Idempotency-Key ini masih diproses. Coba lagi sebentar.",
        header={"Retry-After": "1"},
    )


class Idempotensi:
    def __init__(self, redis: Redis, awalan: str, kunci: str | None, sidik_permintaan: str) -> None:
        self._r = redis
        self._awalan = awalan
        self._kunci = kunci
        self._sidik = sidik_permintaan
        self._hapus = redis.register_script(_HAPUS_JIKA_SAMA)

    @property
    def kunci(self) -> str | None:
        return self._kunci

    def _k(self, user_id: UUID) -> str:
        # Kunci klien bebas bentuk (sepanjang pola); disidik supaya panjang nama
        # kunci Redis tetap dan `:` di dalamnya tidak bisa meniru bagian lain.
        sidik = hashlib.sha256(str(self._kunci).encode()).hexdigest()
        return f"{self._awalan}:idem:{user_id}:{sidik}"

    async def jalankan(
        self, user_id: UUID, kerja: Callable[[], Awaitable[Jawaban]]
    ) -> JSONResponse:
        """Jalankan `kerja` SEKALI per (pengguna, kunci) — ulangan menerima jawaban yang sama."""
        if not isinstance(user_id, UUID):
            raise TypeError(f"user_id wajib uuid.UUID, bukan {type(user_id).__name__}")
        if self._kunci is None:
            hasil = await kerja()
            return JSONResponse(status_code=hasil.status, content=jsonable_encoder(hasil.isi))

        k = self._k(user_id)
        penanda = json.dumps({"sidik": self._sidik, "sedang": True})
        if not await self._r.set(k, penanda, nx=True, ex=_UMUR_PROSES_S):
            return await self._putar_ulang(k)
        try:
            hasil = await kerja()
        except BaseException:
            await self._hapus(keys=[k], args=[penanda])
            raise
        badan = jsonable_encoder(hasil.isi)
        if 200 <= hasil.status < 300:
            await self._r.set(
                k,
                json.dumps({"sidik": self._sidik, "status": hasil.status, "badan": badan}),
                ex=UMUR_JAWABAN_S,
            )
        else:
            await self._hapus(keys=[k], args=[penanda])
        return JSONResponse(status_code=hasil.status, content=badan)

    async def _putar_ulang(self, k: str) -> JSONResponse:
        nilai = await self._r.get(k)
        if nilai is None:
            # penanda kedaluwarsa di antara SET NX dan GET — jarang; klien mengulang
            raise _sedang_berjalan()
        tersimpan = json.loads(nilai)
        if tersimpan.get("sidik") != self._sidik:
            raise _dipakai_ulang()
        if tersimpan.get("sedang"):
            raise _sedang_berjalan()
        return JSONResponse(
            status_code=int(tersimpan["status"]),
            content=tersimpan["badan"],
            headers={HEADER_DIPUTAR_ULANG: "true"},
        )


async def idempotensi(
    request: Request,
    kunci: Annotated[
        str | None,
        Header(
            alias=HEADER_KUNCI,
            pattern=POLA_KUNCI,
            description="Kunci buatan klien; kunci yang sama mengembalikan hasil yang sama.",
        ),
    ] = None,
) -> Idempotensi:
    """Dependensi tiap rute `POST`/`PATCH` domain (spec/04) — lihat docstring modul."""
    badan = await request.body()
    sidik = _sidik_permintaan(request.method, request.url.path, request.url.query, badan)
    return Idempotensi(redis_dari(request), settings_dari(request).redis_prefix, kunci, sidik)


# Yang dinyatakan rute tulis domain di tanda tangannya: `idem: platform.Idempoten`.
Idempoten = Annotated[Idempotensi, Depends(idempotensi)]
