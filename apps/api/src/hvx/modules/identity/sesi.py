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
* **Tiap operasi yang MEMBACA catatan sesi lalu MENULISNYA adalah satu skrip
  Lua** — Redis tidak menjalankan perintah lain di tengahnya. 🔴 Versi pertama
  membaca lalu menulis dalam MULTI terpisah: keluar yang jatuh di celah itu
  dihidupkan kembali oleh penyegaran — token baru sah, catatan sesi tanpa
  `user_id`, dan sesi itu tidak bisa dicabut lagi; pencabutan karena token
  bekas melewatkan pasangan yang diputar pencuri di celah yang sama (tinjauan
  Sprint 1 — `test_sesi.py` menyela tiap celah antarperintah).

Skrip menyentuh kunci yang namanya baru diketahui di dalamnya (sidik token di
catatan sesi): sah untuk satu Redis (arch/09), tidak untuk Redis Cluster — di
sana kunci satu sesi wajib berbagi hash tag.

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

_DIPUTAR, _BEKAS = 1, 2

# KEYS[1] segar:<sidik lama> · KEYS[2] bekas:<sidik lama>
# ARGV[1] awalan sesi · ARGV[2] sidik akses baru · ARGV[3] sidik segar baru
# ARGV[4] umur akses (dtk) · ARGV[5] umur segar (dtk)
# → {1, isi} diputar · {2, isi} token BEKAS dipakai lagi · {0, ''} tak dikenal atau dicabut
_PUTAR = """
local isi = redis.call('GETDEL', KEYS[1])
if not isi then
  local bekas = redis.call('GET', KEYS[2])
  if bekas then return {2, bekas} end
  return {0, ''}
end
local pisah = string.find(isi, ':', 1, true)
local user_id, sesi_id = string.sub(isi, 1, pisah - 1), string.sub(isi, pisah + 1)
local k_sesi = ARGV[1] .. ':' .. sesi_id
local c = redis.call('HMGET', k_sesi, 'user_id', 'akses')
if not (c[1] and c[2]) then
  -- dicabut, atau catatan rusak (tanpa user_id, bentuk yang dibuat versi pertama):
  -- tidak diputar — dan token aksesnya ikut dimatikan
  if c[2] then redis.call('DEL', ARGV[1] .. ':akses:' .. c[2]) end
  redis.call('DEL', k_sesi)
  redis.call('SREM', ARGV[1] .. ':pengguna:' .. user_id, sesi_id)
  return {0, ''}
end
local k_pengguna = ARGV[1] .. ':pengguna:' .. user_id
redis.call('DEL', ARGV[1] .. ':akses:' .. c[2])
redis.call('SET', KEYS[2], isi, 'EX', ARGV[5])
redis.call('SET', ARGV[1] .. ':akses:' .. ARGV[2], isi, 'EX', ARGV[4])
redis.call('SET', ARGV[1] .. ':segar:' .. ARGV[3], isi, 'EX', ARGV[5])
redis.call('HSET', k_sesi, 'akses', ARGV[2], 'segar', ARGV[3])
redis.call('EXPIRE', k_sesi, ARGV[5])
redis.call('SADD', k_pengguna, sesi_id)
redis.call('EXPIRE', k_pengguna, ARGV[5])
return {1, isi}
"""

# KEYS[1] catatan sesi · ARGV[1] awalan sesi · ARGV[2] sesi_id → 1 dicabut · 0 sudah tidak ada
# Catatan tanpa `user_id` (rusak) tetap dicabut token-tokennya — hanya SREM yang dilewati.
_CABUT = """
local c = redis.call('HMGET', KEYS[1], 'user_id', 'akses', 'segar')
if not (c[1] or c[2] or c[3]) then return 0 end
local kunci = {KEYS[1]}
if c[2] then table.insert(kunci, ARGV[1] .. ':akses:' .. c[2]) end
if c[3] then table.insert(kunci, ARGV[1] .. ':segar:' .. c[3]) end
redis.call('DEL', unpack(kunci))
if c[1] then redis.call('SREM', ARGV[1] .. ':pengguna:' .. c[1], ARGV[2]) end
return 1
"""


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
        self._putar = redis.register_script(_PUTAR)
        self._cabut = redis.register_script(_CABUT)

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

    async def pemilik_token_segar(self, token_segar: str) -> SesiAktif | None:
        """Sesi pemilik token segar yang masih sah — TANPA memakainya.

        Hanya untuk keputusan yang bukan soal sah-tidaknya token (status akun
        sebelum rotasi, tugas 1.1); sahnya token tetap diputuskan `segarkan`,
        atomik — pembacaan ini boleh basi sedetik kemudian.
        """
        if not token_segar.startswith(AWALAN_SEGAR):
            return None
        nilai = await self._r.get(self._k_segar(sidik(token_segar)))
        return _pisah(nilai) if nilai else None

    async def segarkan(self, token_segar: str) -> HasilPenyegaran:
        if not token_segar.startswith(AWALAN_SEGAR):
            return HasilPenyegaran(None)
        lama = sidik(token_segar)
        akses, segar = self._pasangan_baru()
        hasil, isi = await self._putar(
            keys=[self._k_segar(lama), self._k_bekas(lama)],
            args=[self._p, sidik(akses), sidik(segar), self._ttl_akses, self._ttl_segar],
        )
        if hasil == _BEKAS:
            curian = _pisah(isi)
            # Skrip terpisah, tetap aman: `_CABUT` membaca catatan sesi saat itu
            # juga, jadi pasangan yang diputar pencuri sesudah deteksi ikut mati.
            await self.cabut(curian.sesi_id)
            return HasilPenyegaran(None, dipakai_ulang=curian)
        if hasil != _DIPUTAR:
            return HasilPenyegaran(None)
        return HasilPenyegaran(Token(akses, segar, self._ttl_akses))

    async def cabut(self, sesi_id: UUID) -> None:
        await self._cabut(keys=[self._k_sesi(sesi_id)], args=[self._p, str(sesi_id)])

    async def cabut_semua(self, user_id: UUID) -> int:
        anggota = cast(set[str], await self._r.smembers(self._k_pengguna(user_id)))
        for sesi in anggota:
            await self.cabut(UUID(sesi))
        if anggota:
            # Hanya anggota yang sudah dicabut — BUKAN `DEL` seluruh himpunan: sesi
            # yang lahir di sela SMEMBERS tetap tercatat untuk "cabut semua" berikutnya.
            await self._r.srem(self._k_pengguna(user_id), *anggota)
        return len(anggota)
