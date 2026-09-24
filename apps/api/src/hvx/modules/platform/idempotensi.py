"""`Idempotency-Key` untuk tulisan domain — spec/04 *Aturan lintas endpoint* (E-165, E-171).

`POST`/`PATCH` domain menerima header `Idempotency-Key`: kunci yang sama
mengembalikan hasil yang sama — status PERTAMA dan sumber daya yang ditulisnya,
bertanda `Idempotent-Replayed: true`. Bentuknya mengikuti draf IETF
*The Idempotency-Key HTTP Header Field*:

* kunci yang sama dengan permintaan BERBEDA (metode, jalur, atau badan) →
  `422 idempotency_key_reused` — bukan diputar ulang diam-diam: permintaan
  kedua itu permintaan lain, dan jawaban pertama bukan jawabannya;
* kunci yang sama saat permintaan pertama MASIH berjalan →
  `409 idempotency_in_progress` — dua tulisan serentak tidak bisa keduanya jalan;
* hanya jawaban 2xx yang diingat: galat diulang dengan menjalankan ulang
  permintaannya, supaya 429 atau galat sesaat tidak terkunci sebagai jawaban;
* kuncinya `[A-Za-z0-9_.:=-]{1,128}`, telanjang atau sebagai sf-string
  bertanda kutip (`"8e03978e-…"`, bentuk draf IETF) — keduanya kunci yang sama.

🔒 **Redis hanya menyimpan RUJUKAN, tidak pernah isi** (tinjauan keamanan
Sprint 2, E-171). Versi pertama menyimpan badan jawaban utuh 24 jam: ~5 KiB
per permintaan 19 byte, di Redis `noeviction` yang sama dengan sesi — memori
yang bisa dihabiskan murah, dan catatan pengguna yang masih tinggal di Redis
dan AOF-nya sesudah hapus-keras. Kini yang disimpan hanya sidik permintaan
(HMAC berkunci), kode status, dan id sumber daya; pemutaran ulang MEMBACA ULANG
sumber daya itu dari PostgreSQL, di bawah RLS pengguna yang sama. Akibatnya
yang diakui: ulangan menerima keadaan sumber daya SEKARANG — `PATCH` lain di
antaranya ikut terlihat — dan sumber daya yang sudah dihapus menjawab `404`.
Tiap pengguna paling banyak `KUOTA_KUNCI` kunci baru per `JENDELA_KUOTA_S`
(`429` sesudahnya): memori Redis per pengguna berbatas, bukan per permintaan.

🔒 **Kunci milik PENGGUNA** — `user_id` bagian dari nama kunci Redis. Kunci
yang sama dari dua pengguna tidak pernah saling memutar ulang jawaban: itu
bukan salah hitung, itu data pengguna A dikirim ke pengguna B (H-27).

⚠️ **Batas yang diakui:** rujukan disimpan di Redis SESUDAH transaksi basis
data commit. Proses yang mati di antara keduanya meninggalkan penanda
"sedang berjalan" yang kedaluwarsa sendiri (`_UMUR_PROSES_S`); ulangan
sesudahnya menjalankan tulisan lagi. Untuk `POST` yang membuat baris, id
buatan klien (spec/04 — dukungan luring) membuat ulangan itu `409`, bukan
baris kedua — klien luring wajib membuat id-nya sendiri.

`/v1/auth/*` sengaja TIDAK memakainya (K-21): jawabannya memuat token.

Dipakai sebagai dependensi, bukan dipanggil diam-diam di badan rute:
`tests/unit/test_idempotensi_terpasang.py` memeriksa TIAP rute `POST`/`PATCH`
domain menyatakannya DAN memanggil `jalankan` — rute baru yang lupa tidak lolos.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

import structlog
from fastapi import Depends, Header, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from redis.exceptions import RedisError

from .batas_laju import HasilLaju, galat_terlalu_sering, sidik
from .galat import GalatApi
from .keadaan import redis_dari, settings_dari

log = structlog.get_logger("hvx.idempotensi")

HEADER_KUNCI = "Idempotency-Key"
HEADER_DIPUTAR_ULANG = "Idempotent-Replayed"
_POLA_ISI = r"[A-Za-z0-9_.:=-]{1,128}"
POLA_KUNCI = rf'^(?:{_POLA_ISI}|"{_POLA_ISI}")$'

# Umur penanda "sedang berjalan": tulisan domain selesai dalam milidetik; penanda
# yang yatim karena proses mati tidak menahan kunci itu lebih lama dari ini.
_UMUR_PROSES_S = 60
# Umur rujukan yang diingat — cukup untuk klien luring yang mengulang besok pagi.
UMUR_JAWABAN_S = 86_400
# Kunci BARU per pengguna per jendela (K-24). Batas laju per pengguna (300/60)
# mengizinkan 432 ribu tulisan sehari; tanpa kuota, tiap tulisan itu satu entri
# Redis selama 24 jam. Seribu tulisan berkunci sehari jauh di atas pemakaian
# manusia — antrean luring seminggu penuh pun puluhan.
KUOTA_KUNCI = 1_000
JENDELA_KUOTA_S = 86_400

# Satu langkah atomik: rujukan yang ADA dikembalikan (putar ulang); kalau belum
# ada, jatah kuota DIPAKAI lebih dulu (bukan ditanya lalu dihitung nanti —
# AGENTS.md §5), lalu penanda dipasang. Versi pertama memakai SET NX lalu GET
# terpisah: penanda yang kedaluwarsa di antaranya terbaca sebagai "tidak ada".
_AMBIL_ATAU_KUNCI = """
local ada = redis.call('GET', KEYS[1])
if ada then
  return {1, ada}
end
local n = redis.call('INCR', KEYS[2])
if redis.call('TTL', KEYS[2]) < 0 then
  redis.call('EXPIRE', KEYS[2], ARGV[4])
end
if n > tonumber(ARGV[3]) then
  return {2, tostring(redis.call('PTTL', KEYS[2]))}
end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
return {0, ''}
"""

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
    """Hasil kerja sebuah rute tulis: status, isi, dan id sumber daya yang ditulisnya.

    `rujukan` yang diingat — bukan `isi`: ulangan membaca ulang sumber daya itu.
    """

    status: int
    isi: Any
    rujukan: UUID


# id sumber daya → sumber daya itu SEKARANG (di bawah RLS pemilik), atau None.
PembacaUlang = Callable[[UUID], Awaitable[Any | None]]


def bahan_sidik(metode: str, jalur: str, kueri: str, badan: bytes) -> str:
    """Isi permintaan yang disidik — badan JSON dinormalkan, supaya spasi tidak mengubahnya.

    Sidiknya HMAC berkunci (`idempotensi()`), bukan sha256 polos: badan
    `{"valence":3}` hanya punya lima kemungkinan, dan sha256-nya bisa dibalik
    dengan mencoba kelimanya.
    """
    try:
        isi = json.dumps(json.loads(badan), sort_keys=True, separators=(",", ":"))
    except (ValueError, UnicodeDecodeError, RecursionError):
        # Bukan JSON — atau JSON bersarang ribuan tingkat (RecursionError bukan
        # ValueError; dulu lolos menjadi 500 — tinjauan keamanan Sprint 2).
        isi = badan.hex()
    return "\x00".join((metode, jalur, kueri, isi))


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


def _hasilnya_sudah_tidak_ada() -> GalatApi:
    return GalatApi(
        404,
        "not_found",
        "Sumber daya hasil permintaan ini sudah tidak ada.",
        header={HEADER_DIPUTAR_ULANG: "true"},
    )


def _normalkan_kunci(kunci: str | None) -> str | None:
    # sf-string `"abc"` dan token `abc` — isi yang sama, kunci yang sama.
    if kunci is not None and len(kunci) >= 2 and kunci[0] == kunci[-1] == '"':
        return kunci[1:-1]
    return kunci


class Idempotensi:
    def __init__(self, redis: Redis, awalan: str, kunci: str | None, sidik_permintaan: str) -> None:
        self._r = redis
        self._awalan = awalan
        self._kunci = _normalkan_kunci(kunci)
        self._sidik = sidik_permintaan
        self._ambil_atau_kunci = redis.register_script(_AMBIL_ATAU_KUNCI)
        self._hapus = redis.register_script(_HAPUS_JIKA_SAMA)

    @property
    def kunci(self) -> str | None:
        return self._kunci

    def _k(self, user_id: UUID) -> str:
        # Kunci klien bebas bentuk (sepanjang pola); disidik supaya panjang nama
        # kunci Redis tetap dan `:` di dalamnya tidak bisa meniru bagian lain.
        sidik_kunci = hashlib.sha256(str(self._kunci).encode()).hexdigest()
        return f"{self._awalan}:idem:{user_id}:{sidik_kunci}"

    def _k_kuota(self, user_id: UUID) -> str:
        return f"{self._awalan}:idem-kuota:{user_id}"

    async def jalankan(
        self,
        user_id: UUID,
        kerja: Callable[[], Awaitable[Jawaban]],
        baca_ulang: PembacaUlang,
    ) -> JSONResponse:
        """Jalankan `kerja` SEKALI per (pengguna, kunci) — ulangan menerima hasil yang sama."""
        if not isinstance(user_id, UUID):
            raise TypeError(f"user_id wajib uuid.UUID, bukan {type(user_id).__name__}")
        if self._kunci is None:
            hasil = await kerja()
            return JSONResponse(status_code=hasil.status, content=jsonable_encoder(hasil.isi))

        k = self._k(user_id)
        penanda = json.dumps({"s": self._sidik, "sedang": True})
        jenis, nilai = await self._ambil_atau_kunci(
            keys=[k, self._k_kuota(user_id)],
            args=[penanda, _UMUR_PROSES_S, KUOTA_KUNCI, JENDELA_KUOTA_S],
        )
        if int(jenis) == 1:
            return await self._putar_ulang(nilai, baca_ulang)
        if int(jenis) == 2:
            raise galat_terlalu_sering(HasilLaju(lolos=False, sisa=0, coba_lagi_ms=int(nilai)))

        try:
            hasil = await kerja()
        except BaseException:
            await self._hapus(keys=[k], args=[penanda])
            raise
        if 200 <= hasil.status < 300:
            rujukan = {"s": self._sidik, "st": hasil.status, "id": str(hasil.rujukan)}
            try:
                await self._r.set(k, json.dumps(rujukan), ex=UMUR_JAWABAN_S)
            except RedisError:
                # Tulisannya SUDAH commit: jawaban tetap dikirim. Penanda yatim
                # kedaluwarsa sendiri (batas yang diakui di docstring modul).
                log.warning("idempotensi.rujukan_gagal_disimpan")
        else:
            await self._hapus(keys=[k], args=[penanda])
        return JSONResponse(status_code=hasil.status, content=jsonable_encoder(hasil.isi))

    async def _putar_ulang(self, nilai: bytes | str, baca_ulang: PembacaUlang) -> JSONResponse:
        tersimpan = json.loads(nilai)
        if tersimpan.get("s") != self._sidik:
            raise _dipakai_ulang()
        if tersimpan.get("sedang"):
            raise _sedang_berjalan()
        isi = await baca_ulang(UUID(tersimpan["id"]))
        if isi is None:
            raise _hasilnya_sudah_tidak_ada()
        return JSONResponse(
            status_code=int(tersimpan["st"]),
            content=jsonable_encoder(isi),
            headers={HEADER_DIPUTAR_ULANG: "true"},
        )


async def idempotensi(
    request: Request,
    kunci: Annotated[
        str | None,
        Header(
            alias=HEADER_KUNCI,
            pattern=POLA_KUNCI,
            description=(
                "Kunci buatan klien — `[A-Za-z0-9_.:=-]{1,128}`, telanjang atau sf-string "
                "bertanda kutip; kunci yang sama mengembalikan hasil yang sama."
            ),
        ),
    ] = None,
) -> Idempotensi:
    """Dependensi tiap rute `POST`/`PATCH` domain (spec/04) — lihat docstring modul."""
    badan = await request.body()
    settings = settings_dari(request)
    bahan = bahan_sidik(request.method, request.url.path, request.url.query, badan)
    return Idempotensi(
        redis_dari(request), settings.redis_prefix, kunci, sidik(settings, "idempotensi", bahan)
    )


# Yang dinyatakan rute tulis domain di tanda tangannya: `idem: platform.Idempoten`.
Idempoten = Annotated[Idempotensi, Depends(idempotensi)]
