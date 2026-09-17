"""Batas laju — spec/07 tugas 1.7: per pengguna & per IP, `429` dengan `Retry-After`.

Berkas ini hanya MEKANISME: berapa, untuk kunci apa, dan jawaban 429-nya.
Kebijakan yang tahu apa itu pengguna atau login tinggal di `identity`.

* **GCRA** (*generic cell rate algorithm*) di satu skrip Lua: satu kunci Redis
  per subjek, atomik, dan `Retry-After` yang TEPAT — bukan "coba lagi di awal
  menit berikutnya" seperti jendela tetap, yang juga meloloskan 2× batas di
  perbatasan dua jendela. `jumlah/jendela` berarti: boleh meledak sampai
  `jumlah` sekaligus, lalu terisi kembali satu tiap `jendela/jumlah`.
* **Jam Redis, bukan jam proses** (`TIME` di dalam skrip): semua instans api
  menghitung dengan satu jam.
* **IP tidak pernah disimpan mentah** — kuncinya HMAC dengan `HVX_IP_HASH_KEY`.
  **IPv6 dihitung per /64**: satu pelanggan biasa menerima satu /64 utuh, jadi
  batas per alamat dilewati cukup dengan berganti alamat di jaringannya sendiri.
* **Permukaan `/v1/*` seluruhnya**, sebagai middleware — rute baru tidak bisa
  lupa memasangnya. `/health` di luar permukaan itu sengaja: ia harus tetap
  menjawab *"redis mati"* saat Redis mati.
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
import math
import re
from dataclasses import dataclass

from fastapi import Request
from redis.asyncio import Redis
from starlette.types import ASGIApp, Receive, Scope, Send

from .config import POLA_BATAS, Settings
from .galat import GalatApi, jawaban_galat
from .keadaan import redis_dari, settings_dari

_POLA_NAMA = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
_PESAN = "Terlalu banyak permintaan. Coba lagi nanti."

# KEYS[1] kunci · ARGV[1] interval emisi (ms) · ARGV[2] toleransi (ms)
# → {lolos 0/1, coba lagi dalam ms, sisa}
_GCRA = """
local interval = tonumber(ARGV[1])
local toleransi = tonumber(ARGV[2])
local waktu = redis.call('TIME')
local sekarang = tonumber(waktu[1]) * 1000 + math.floor(tonumber(waktu[2]) / 1000)
local tat = tonumber(redis.call('GET', KEYS[1]))
if tat == nil or tat < sekarang then
  tat = sekarang
end
local tat_baru = tat + interval
local boleh_pada = tat_baru - toleransi
if sekarang < boleh_pada then
  return {0, boleh_pada - sekarang, 0}
end
redis.call('SET', KEYS[1], tat_baru, 'PX', tat_baru - sekarang)
return {1, 0, math.floor((sekarang - boleh_pada) / interval)}
"""


@dataclass(frozen=True)
class BatasLaju:
    """`jumlah` permintaan per `jendela_s` detik untuk satu jenis kunci (`nama`)."""

    nama: str
    jumlah: int
    jendela_s: int

    def __post_init__(self) -> None:
        if not _POLA_NAMA.fullmatch(self.nama):
            raise ValueError(f"nama batas laju tidak sah: {self.nama!r}")
        if self.jumlah < 1 or self.jendela_s < 1:
            raise ValueError("jumlah dan jendela batas laju wajib ≥ 1")

    @classmethod
    def dari_teks(cls, nama: str, teks: str) -> BatasLaju:
        """`"600/60"` → 600 permintaan per 60 detik."""
        if not re.fullmatch(POLA_BATAS, teks):
            raise ValueError(f"batas laju wajib berbentuk jumlah/detik, bukan {teks!r}")
        jumlah, jendela = teks.split("/")
        return cls(nama, int(jumlah), int(jendela))

    @property
    def interval_ms(self) -> int:
        # dibulatkan ke atas: batas yang dibulatkan tidak pernah lebih longgar
        return math.ceil(self.jendela_s * 1000 / self.jumlah)


@dataclass(frozen=True)
class HasilLaju:
    lolos: bool
    sisa: int
    coba_lagi_ms: int

    @property
    def retry_after_s(self) -> int:
        """Nilai header `Retry-After` — detik bulat, tidak pernah 0 untuk yang ditolak."""
        return max(1, math.ceil(self.coba_lagi_ms / 1000))


class PembatasLaju:
    def __init__(self, redis: Redis, awalan: str) -> None:
        self._r = redis
        self._awalan = awalan
        self._skrip = redis.register_script(_GCRA)

    def _kunci(self, batas: BatasLaju, subjek: str) -> str:
        return f"{self._awalan}:laju:{batas.nama}:{subjek}"

    async def ambil(self, batas: BatasLaju, subjek: str) -> HasilLaju:
        """Pakai satu jatah — bertanya dan memakai dalam SATU perintah atomik.

        🔴 Sengaja tidak ada mode "tanya dulu, pakai nanti". Versi pertama punya
        (`catat=False`) untuk login gagal per akun: dua belas tebakan serentak
        semuanya lolos pertanyaan sebelum satu pun dihitung (tinjauan Sprint 1).
        Yang perlu dikembalikan sesudah berhasil memakai `lupakan()`.
        """
        interval = batas.interval_ms
        lolos, coba_lagi, sisa = await self._skrip(
            keys=[self._kunci(batas, subjek)],
            args=[interval, interval * batas.jumlah],
        )
        return HasilLaju(lolos=bool(lolos), sisa=int(sisa), coba_lagi_ms=int(coba_lagi))

    async def lupakan(self, batas: BatasLaju, subjek: str) -> None:
        await self._r.delete(self._kunci(batas, subjek))


def pembatas_laju(request: Request) -> PembatasLaju:
    return PembatasLaju(redis_dari(request), settings_dari(request).redis_prefix)


def galat_terlalu_sering(hasil: HasilLaju) -> GalatApi:
    """SATU sumber jawaban 429 — dilempar dependensi, dirender middleware."""
    return GalatApi(429, "rate_limited", _PESAN, header={"Retry-After": str(hasil.retry_after_s)})


def sidik(settings: Settings, label: str, nilai: str) -> str:
    """HMAC berlabel — nilai yang sama di dua tujuan berbeda tidak menghasilkan sidik yang sama."""
    kunci = settings.ip_hash_key.get_secret_value().encode()
    return hmac.new(kunci, f"{label}\x00{nilai}".encode(), hashlib.sha256).hexdigest()


def jaringan_klien(host: str) -> str:
    """IPv4 apa adanya; IPv6 dipotong ke /64; IPv4 yang dibungkus IPv6 dibuka."""
    try:
        alamat = ipaddress.ip_address(host)
    except ValueError:
        return host
    if isinstance(alamat, ipaddress.IPv6Address):
        if alamat.ipv4_mapped is not None:
            return str(alamat.ipv4_mapped)
        return str(ipaddress.IPv6Network((alamat, 64), strict=False))
    return str(alamat)


def sidik_jaringan(request: Request) -> str:
    """Kunci batas laju per IP. Klien tanpa alamat berbagi SATU jatah — bukan tanpa batas."""
    host = request.client.host if request.client and request.client.host else "tanpa-alamat"
    return sidik(settings_dari(request), "laju-ip", jaringan_klien(host))


def _di_permukaan_api(jalur: str) -> bool:
    return jalur == "/v1" or jalur.startswith("/v1/")


class BatasLajuIpMiddleware:
    """Batas laju per IP untuk seluruh `/v1/*` — ASGI murni, sama dengan middleware log."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not _di_permukaan_api(scope["path"]):
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        batas = BatasLaju.dari_teks("ip", settings_dari(request).rate_limit_ip)
        hasil = await pembatas_laju(request).ambil(batas, sidik_jaringan(request))
        if not hasil.lolos:
            g = galat_terlalu_sering(hasil)
            await jawaban_galat(g.status, g.kode, g.pesan, g.rincian, g.header)(
                scope, receive, send
            )
            return
        await self.app(scope, receive, send)
