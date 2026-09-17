"""Sesi di Redis — spec/07 tugas 1.2: token dicabut → 401 SEKETIKA.

Kenapa token opak di Redis, bukan JWT yang ditandatangani: JWT sah sampai
kedaluwarsa, apa pun yang terjadi sesudah diterbitkan. "Dicabut → 401
seketika" menuntut pemeriksaan ke penyimpanan pada TIAP permintaan — dan
kalau pemeriksaan itu tetap dilakukan, tanda tangan JWT hanya menambah hal
yang bisa salah (algoritma, rotasi kunci) tanpa menghapus satu kueri pun.

Bentuk yang dipakai, dan kenapa:

* **Token acak 256 bit berawalan** (`hvxa_` akses, `hvxr_` segar): awalan
  membuat token yang bocor dikenali pemindai rahasia, dan token segar yang
  dikirim sebagai token akses ditolak tanpa satu pun kueri.
* **Hanya SIDIK (sha256) yang disimpan**: salinan Redis yang bocor tidak berisi
  satu token pun yang bisa dipakai. Tanpa garam, sebab entropi 256 bit
  membuat tabel pelangi tidak berarti.
* **Token segar BEROTASI** tiap dipakai, diambil dengan `GETDEL` — atomik,
  sehingga dua penyegaran serentak dengan token yang sama tidak bisa
  keduanya berhasil.
* **Token segar yang sudah dirotasi dan dipakai LAGI = dicuri**: seluruh sesi
  itu dicabut, termasuk pasangan token terbaru yang mungkin ada di tangan
  pencuri (RFC 9700 §4.14.2, refresh token rotation).

Klien Redis wajib `decode_responses=True` (`platform.buat_redis`): semua nilai
di sini teks.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import cast
from uuid import UUID, uuid4

from redis.asyncio import Redis

AWALAN_AKSES = "hvxa_"
AWALAN_SEGAR = "hvxr_"


def sidik(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Token:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"  # noqa: S105 — jenis token OAuth 2.0, bukan sandi


@dataclass(frozen=True)
class SesiAktif:
    user_id: UUID
    sesi_id: UUID


@dataclass(frozen=True)
class HasilPenyegaran:
    """`token` terisi kalau berhasil; `dipakai_ulang` terisi kalau pencurian terdeteksi."""

    token: Token | None
    dipakai_ulang: SesiAktif | None = None


def _gabung(user_id: UUID, sesi_id: UUID) -> str:
    return f"{user_id}:{sesi_id}"


def _pisah(nilai: bytes | str) -> SesiAktif:
    teks = nilai.decode() if isinstance(nilai, bytes) else nilai
    user_id, sesi_id = teks.split(":", 1)
    return SesiAktif(UUID(user_id), UUID(sesi_id))


class PenyimpanSesi:
    def __init__(self, redis: Redis, awalan: str, ttl_akses_s: int, ttl_segar_s: int) -> None:
        self._r = redis
        self._p = f"{awalan}:sesi"
        self._ttl_akses = ttl_akses_s
        self._ttl_segar = ttl_segar_s

    # ── kunci ────────────────────────────────────────────────────────────
    def _k_akses(self, sidik_token: str) -> str:
        return f"{self._p}:akses:{sidik_token}"

    def _k_segar(self, sidik_token: str) -> str:
        return f"{self._p}:segar:{sidik_token}"

    def _k_bekas(self, sidik_token: str) -> str:
        return f"{self._p}:bekas:{sidik_token}"

    def _k_sesi(self, sesi_id: UUID) -> str:
        return f"{self._p}:{sesi_id}"

    def _k_pengguna(self, user_id: UUID) -> str:
        return f"{self._p}:pengguna:{user_id}"

    # ── operasi ──────────────────────────────────────────────────────────
    def _pasangan_baru(self) -> tuple[str, str]:
        return AWALAN_AKSES + secrets.token_urlsafe(32), AWALAN_SEGAR + secrets.token_urlsafe(32)

    async def buat(self, user_id: UUID) -> Token:
        sesi_id = uuid4()
        akses, segar = self._pasangan_baru()
        nilai = _gabung(user_id, sesi_id)
        async with self._r.pipeline(transaction=True) as p:
            p.set(self._k_akses(sidik(akses)), nilai, ex=self._ttl_akses)
            p.set(self._k_segar(sidik(segar)), nilai, ex=self._ttl_segar)
            p.hset(
                self._k_sesi(sesi_id),
                mapping={"user_id": str(user_id), "akses": sidik(akses), "segar": sidik(segar)},
            )
            p.expire(self._k_sesi(sesi_id), self._ttl_segar)
            p.sadd(self._k_pengguna(user_id), str(sesi_id))
            p.expire(self._k_pengguna(user_id), self._ttl_segar)
            await p.execute()
        return Token(akses, segar, self._ttl_akses)

    async def periksa_akses(self, token: str) -> SesiAktif | None:
        if not token.startswith(AWALAN_AKSES):
            return None
        nilai = await self._r.get(self._k_akses(sidik(token)))
        return _pisah(nilai) if nilai else None

    async def segarkan(self, token_segar: str) -> HasilPenyegaran:
        if not token_segar.startswith(AWALAN_SEGAR):
            return HasilPenyegaran(None)
        lama = sidik(token_segar)
        nilai = await self._r.getdel(self._k_segar(lama))
        if nilai is None:
            sesi_bekas = await self._r.get(self._k_bekas(lama))
            if sesi_bekas is None:
                return HasilPenyegaran(None)
            curian = _pisah(sesi_bekas)
            await self.cabut(curian.sesi_id)
            return HasilPenyegaran(None, dipakai_ulang=curian)

        sesi = _pisah(nilai)
        catatan = cast(dict[str, str], await self._r.hgetall(self._k_sesi(sesi.sesi_id)))
        if not catatan:
            return HasilPenyegaran(None)  # sesi sudah dicabut di antara dua langkah
        akses, segar = self._pasangan_baru()
        isi = _gabung(sesi.user_id, sesi.sesi_id)
        async with self._r.pipeline(transaction=True) as p:
            p.delete(self._k_akses(catatan["akses"]))
            p.set(self._k_bekas(lama), isi, ex=self._ttl_segar)
            p.set(self._k_akses(sidik(akses)), isi, ex=self._ttl_akses)
            p.set(self._k_segar(sidik(segar)), isi, ex=self._ttl_segar)
            p.hset(
                self._k_sesi(sesi.sesi_id), mapping={"akses": sidik(akses), "segar": sidik(segar)}
            )
            p.expire(self._k_sesi(sesi.sesi_id), self._ttl_segar)
            p.expire(self._k_pengguna(sesi.user_id), self._ttl_segar)
            await p.execute()
        return HasilPenyegaran(Token(akses, segar, self._ttl_akses))

    async def cabut(self, sesi_id: UUID) -> None:
        catatan = cast(dict[str, str], await self._r.hgetall(self._k_sesi(sesi_id)))
        if not catatan:
            return
        async with self._r.pipeline(transaction=True) as p:
            p.delete(
                self._k_akses(catatan["akses"]),
                self._k_segar(catatan["segar"]),
                self._k_sesi(sesi_id),
            )
            p.srem(self._k_pengguna(UUID(catatan["user_id"])), str(sesi_id))
            await p.execute()

    async def cabut_semua(self, user_id: UUID) -> int:
        anggota = cast(set[str], await self._r.smembers(self._k_pengguna(user_id)))
        for sesi in anggota:
            await self.cabut(UUID(sesi))
        await self._r.delete(self._k_pengguna(user_id))
        return len(anggota)
