"""Relay kotak keluar → Redis Streams — spec/07 3.3.

Tabel `events` adalah kotak keluar (3.1): tulisan domain dan event-nya commit
bersama. Relay — dijalankan proses `hvx.pekerja`, bukan api — menyalin
**RUJUKAN** tiap event yang sudah commit (id · pemilik · jenis) ke satu stream
Redis. Isi event tidak pernah ke Redis: konsumen membacanya dari PostgreSQL di
bawah RLS pemiliknya (`stream.KonsumenStream`) — prinsip yang sama dengan
`Idempotency-Key` (E-171), dan hapus akun tidak meninggalkan payload di Redis.

* **Kursor `(recorded_at, id)`** disimpan di Redis; tiap putaran maju dari sana,
  lewat fungsi sempit `events_untuk_relay` (spec/01 §12) — relay melihat event
  SEMUA pengguna tanpa melonggarkan RLS.
* **Menoleh ke belakang `LIHAT_BELAKANG_S`.** Transaksi yang lebih dulu
  menyisip bisa lebih akhir commit: event-nya punya `recorded_at` DI BELAKANG
  kursor yang sudah lewat, dan relay yang hanya maju melompatinya selamanya.
  Tiap putaran memindai ulang jendela itu.
* **Tidak pernah terkirim dua kali**: penanda (`ZADD NX` ke satu himpunan
  terurut, skornya `recorded_at`) dan `XADD` dalam SATU skrip Lua — relay yang
  mati di antara keduanya tidak ada, dan pemindaian ulang jendela belakang tidak
  menggandakan apa pun.
* **Penanda berbatas jendela belakang**, bukan waktu: begitu kursor maju, penanda
  event yang `recorded_at`-nya lebih tua dari kursor − `LIHAT_BELAKANG_S` dibuang —
  tidak ada putaran yang akan memindainya lagi. 🔴 Versi pertama: satu kunci per
  event, umur 24 jam — batas laju per pengguna meninggalkan ±50 MB per akun sehari
  di Redis `noeviction` yang sama dengan sesi (tinjauan keamanan Sprint 3, S3).
  Relay yang berhenti lama pun tidak menggandakan: penanda dibuang menurut kursor,
  bukan menurut jam.
* **Pangkas aman**: stream dipangkas hanya sampai pesan tertua yang masih
  ditunggu SATU pun grup konsumen (belum dibaca atau belum di-ACK) — memori
  Redis berbatas tanpa membuang event yang belum selesai diproses.

⚠️ **Batas yang diakui:** transaksi yang commit lebih dari `LIHAT_BELAKANG_S`
sesudah menyisip event-nya tidak terkirim (tulisan api selesai dalam
milidetik); dan jendela belakang dibaca paling banyak `BATAS_BELAKANG` event.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

log = structlog.get_logger("hvx.relay")

LIHAT_BELAKANG_S = 60
BATAS_PUTARAN = 500
BATAS_BELAKANG = 1_000
_NOL = UUID(int=0)
_AWAL = datetime(1900, 1, 1, tzinfo=UTC)

_UNTUK_RELAY = text(
    "SELECT id, user_id, event_type, recorded_at FROM "
    "events_untuk_relay(CAST(:sesudah AS timestamptz), CAST(:sesudah_id AS uuid), :batas)"
)

# KEYS[1] himpunan penanda (skor = recorded_at ms) · KEYS[2] stream
# ARGV[1] skor · ARGV[2..4] rujukan
_KIRIM = """
if redis.call('ZADD', KEYS[1], 'NX', ARGV[1], ARGV[2]) == 1 then
  return redis.call('XADD', KEYS[2], '*', 'id', ARGV[2], 'user_id', ARGV[3],
                    'event_type', ARGV[4])
end
return false
"""


@dataclass(frozen=True)
class Rujukan:
    id: UUID
    user_id: UUID
    event_type: str
    recorded_at: datetime


def kunci_stream(awalan: str) -> str:
    return f"{awalan}:events"


class Relay:
    def __init__(self, engine: AsyncEngine, redis: Redis, awalan: str) -> None:
        self._engine = engine
        self._r = redis
        self._awalan = awalan
        self._kirim = redis.register_script(_KIRIM)

    @property
    def stream(self) -> str:
        return kunci_stream(self._awalan)

    def _k_posisi(self) -> str:
        return f"{self._awalan}:relay:posisi"

    def _k_terkirim(self) -> str:
        return f"{self._awalan}:relay:terkirim"

    async def _posisi(self) -> tuple[datetime, UUID] | None:
        nilai = await self._r.get(self._k_posisi())
        if not nilai:
            return None
        waktu, id_ = str(nilai).split("|", 1)
        return datetime.fromisoformat(waktu), UUID(id_)

    async def _baca(self, sesudah: tuple[datetime, UUID], batas: int) -> list[Rujukan]:
        async with platform.transaksi_sistem(self._engine) as conn:
            hasil = await conn.execute(
                _UNTUK_RELAY, {"sesudah": sesudah[0], "sesudah_id": sesudah[1], "batas": batas}
            )
            return [Rujukan(b.id, b.user_id, b.event_type, b.recorded_at) for b in hasil]

    async def _kirim_semua(self, rujukan: list[Rujukan]) -> int:
        terkirim = 0
        for r in rujukan:
            hasil = await self._kirim(
                keys=[self._k_terkirim(), self.stream],
                args=[_ms(r.recorded_at), str(r.id), str(r.user_id), r.event_type],
            )
            terkirim += 1 if hasil else 0
        return terkirim

    async def putaran(self) -> int:
        """Satu putaran relay — jumlah event yang BARU terkirim ke stream."""
        posisi = await self._posisi()
        terkirim = 0
        if posisi is not None:
            belakang = (posisi[0] - timedelta(seconds=LIHAT_BELAKANG_S), _NOL)
            terkirim += await self._kirim_semua(await self._baca(belakang, BATAS_BELAKANG))
        maju = posisi or (_AWAL, _NOL)
        while True:
            rujukan = await self._baca(maju, BATAS_PUTARAN)
            if not rujukan:
                break
            terkirim += await self._kirim_semua(rujukan)
            maju = (rujukan[-1].recorded_at, rujukan[-1].id)
            await self._r.set(self._k_posisi(), f"{maju[0].isoformat()}|{maju[1]}")
            if len(rujukan) < BATAS_PUTARAN:
                break
        # Pindaian berikutnya tidak pernah menoleh lebih jauh dari kursor − jendela belakang.
        batas = _ms(maju[0] - timedelta(seconds=LIHAT_BELAKANG_S))
        await self._r.zremrangebyscore(self._k_terkirim(), "-inf", f"({batas}")
        if terkirim:
            log.info("relay.terkirim", jumlah=terkirim)
        return terkirim

    async def pangkas(self) -> int:
        """Buang pesan yang sudah selesai bagi SEMUA grup — jumlah yang dibuang."""
        try:
            grup = await self._r.xinfo_groups(self.stream)
        except Exception:  # stream belum ada
            return 0
        if not grup:
            return 0
        batas: list[str] = []
        for g in grup:
            batas.append(str(g["last-delivered-id"]))
            ringkas = await self._r.xpending(self.stream, g["name"])
            if int(ringkas["pending"]) > 0:
                batas.append(str(ringkas["min"]))
        paling_awal = min(batas, key=_urutan_id)
        if paling_awal == "0-0":
            return 0
        # Tepat, bukan `~`: pemangkasan kira-kira hanya membuang simpul radix utuh
        # (±100 entri), jadi stream kecil tidak pernah terpangkas sama sekali.
        return int(await self._r.xtrim(self.stream, minid=paling_awal, approximate=False))


def _ms(saat: datetime) -> int:
    return int(saat.timestamp() * 1000)


def _urutan_id(id_pesan: str) -> tuple[int, int]:
    ms, seq = id_pesan.split("-", 1)
    return int(ms), int(seq)
