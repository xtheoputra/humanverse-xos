"""Konsumen Redis Streams — spec/07 3.3: *“consumer mati → event tidak hilang saat hidup lagi”*.

Tiap konsumen V0 (spec/03 *Consumer V0*) adalah satu **grup konsumen** atas
stream relay. Sebuah pesan baru di-ACK SESUDAH penangannya selesai dan
transaksinya commit; sampai itu ia tinggal di daftar tunggu (PEL) grup:

* **Konsumen mati di tengah** — pesan tetap di PEL. Konsumen yang hidup lagi
  (atau konsumen lain di grup yang sama) mengklaimnya dengan `XAUTOCLAIM`
  sesudah menganggur `min_idle_ms`, lalu memprosesnya — tidak ada yang hilang.
* **Penangan gagal** — pesan TIDAK di-ACK; ia diklaim dan dicoba lagi pada
  putaran berikutnya yang lewat `min_idle_ms`. Sesudah `maks_kirim` kali
  diserahkan, ia pindah ke stream **mati** (dead letter) dan di-ACK: satu
  event yang selalu gagal tidak menahan grupnya selamanya.
* **Isi event dibaca dari PostgreSQL, di bawah RLS pemiliknya** — stream hanya
  membawa rujukan (`relay.py`). Penangan menerima koneksi transaksi itu:
  tulisan penangan dan pembacaan event commit bersama, atau batal bersama.
* Konsumen yang "boleh gagal & diulang" (spec/03) WAJIB idempoten — pesan yang
  diklaim bisa sudah separuh diproses konsumen yang mati.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast
from uuid import UUID

import structlog
from redis.asyncio import Redis
from redis.exceptions import ResponseError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from .relay import kunci_stream

log = structlog.get_logger("hvx.konsumen")

_MENURUT_ID = text(
    """
    SELECT id, user_id, event_type, schema_version, occurred_at, recorded_at, source,
           subject_type, subject_id, payload
    FROM events
    WHERE id = :id
    """
)


@dataclass(frozen=True)
class EventMasuk:
    """Event yang diserahkan ke penangan — dibaca dari PostgreSQL, bukan dari Redis."""

    id: UUID
    user_id: UUID
    event_type: str
    schema_version: int
    occurred_at: datetime
    recorded_at: datetime
    source: str
    subject_type: str | None
    subject_id: UUID | None
    payload: dict[str, Any]


# (koneksi transaksi pemilik event, event) → selesai tanpa galat = di-ACK.
Penangan = Callable[[AsyncConnection, EventMasuk], Awaitable[None]]


# Rujukan di stream mati (grup · pesan · pengguna · event) disimpan selama ini —
# cukup untuk memeriksa kenapa sebuah event gagal, bukan selamanya (K-25). Versi
# pertama tidak pernah memangkasnya: rujukan hidup juga sesudah akunnya dihapus.
UMUR_MATI_S = 7 * 86_400


def kunci_mati(awalan: str) -> str:
    return f"{awalan}:events:mati"


async def pangkas_mati(redis: Redis, awalan: str) -> int:
    """Buang pesan stream mati yang lebih tua dari `UMUR_MATI_S` — menurut jam REDIS
    (id pesan = milidetik jam Redis), bukan jam proses ini."""
    detik, mikro = await redis.time()
    batas_ms = detik * 1000 + mikro // 1000 - UMUR_MATI_S * 1000
    return int(await redis.xtrim(kunci_mati(awalan), minid=f"{batas_ms}-0", approximate=False))


class KonsumenStream:
    def __init__(
        self,
        *,
        engine: AsyncEngine,
        redis: Redis,
        awalan: str,
        grup: str,
        nama: str,
        jenis: frozenset[str],
        tangani: Penangan,
        min_idle_ms: int = 30_000,
        maks_kirim: int = 5,
        blok_ms: int = 2_000,
        jumlah: int = 50,
    ) -> None:
        self._engine = engine
        self._r = redis
        self._awalan = awalan
        self.grup = grup
        self.nama = nama
        self._jenis = jenis
        self._tangani = tangani
        self._min_idle_ms = min_idle_ms
        self._maks_kirim = maks_kirim
        self._blok_ms = blok_ms
        self._jumlah = jumlah

    @property
    def stream(self) -> str:
        return kunci_stream(self._awalan)

    async def siapkan(self) -> None:
        """Grup dibuat dari AWAL stream (`0`): konsumen baru memproses riwayat yang ada."""
        try:
            await self._r.xgroup_create(self.stream, self.grup, id="0", mkstream=True)
        except ResponseError as galat:
            if "BUSYGROUP" not in str(galat):
                raise

    async def putaran(self) -> int:
        """Klaim yang menggantung, lalu baca yang baru — jumlah event yang SELESAI diproses."""
        selesai = 0
        mulai = "0-0"
        while True:
            berikut, pesan, *_ = await self._r.xautoclaim(
                self.stream,
                self.grup,
                self.nama,
                min_idle_time=self._min_idle_ms,
                start_id=mulai,
                count=self._jumlah,
            )
            for id_pesan, isi in pesan:
                selesai += await self._proses(str(id_pesan), isi, diklaim=True)
            if str(berikut) == "0-0":
                break
            mulai = str(berikut)
        baru = cast(
            "list[tuple[str, list[tuple[str, dict[str, Any]]]]] | None",
            await self._r.xreadgroup(
                self.grup, self.nama, {self.stream: ">"}, count=self._jumlah, block=self._blok_ms
            ),
        )
        for _stream, pesan in baru or []:
            for id_pesan, isi in pesan:
                selesai += await self._proses(str(id_pesan), isi, diklaim=False)
        return selesai

    async def _kali_diserahkan(self, id_pesan: str) -> int:
        rinci = await self._r.xpending_range(
            self.stream, self.grup, min=id_pesan, max=id_pesan, count=1
        )
        return int(rinci[0]["times_delivered"]) if rinci else 0

    async def _proses(self, id_pesan: str, isi: dict[str, Any], *, diklaim: bool) -> int:
        if diklaim and await self._kali_diserahkan(id_pesan) > self._maks_kirim:
            await self._r.xadd(
                kunci_mati(self._awalan),
                {"grup": self.grup, "pesan": id_pesan, **{k: isi[k] for k in isi}},
            )
            await self._r.xack(self.stream, self.grup, id_pesan)
            log.warning("konsumen.mati", grup=self.grup, pesan=id_pesan)
            return 0
        if isi.get("event_type") not in self._jenis:
            await self._r.xack(self.stream, self.grup, id_pesan)
            return 0
        try:
            async with platform.transaksi_pengguna(self._engine, UUID(isi["user_id"])) as conn:
                # Penangan MENURUNKAN data: hapus kategori menunggu commit-nya (S3).
                await platform.kunci_turunan(conn, UUID(isi["user_id"]))
                baris = (await conn.execute(_MENURUT_ID, {"id": UUID(isi["id"])})).first()
                if baris is not None:
                    await self._tangani(conn, EventMasuk(**baris._asdict()))
        except Exception:
            # Hanya jenis galat dan rujukan — isi event milik pengguna, bukan milik log.
            log.exception("konsumen.gagal", grup=self.grup, pesan=id_pesan)
            return 0
        # Event yang sudah tidak ada (akun dihapus) juga selesai: tidak ada yang diulang.
        await self._r.xack(self.stream, self.grup, id_pesan)
        return 1 if baris is not None else 0
