"""Aliran satu giliran percakapan ke SSE — spec/07 4.8: *token mengalir; `done` memuat `cost_usd`*.

Di dalam proses, bukan di Redis: token adalah kalimat yang ditulis untuk pengguna —
isi, bukan rujukan — dan K-25 menjaga Redis hanya membawa rujukan. Harganya dinyatakan
(K-31): klien yang tersambung ke proses api LAIN tidak menerima alirannya, dan
membaca balasan yang sudah tersimpan (`GET …/messages`) sebagai gantinya.

Satu giliran per percakapan pada satu waktu. Peristiwanya disimpan sampai giliran
selesai dan `SIMPAN_S` sesudahnya, supaya klien yang menyambung SESUDAH `POST
…/messages` — urutan yang wajar di jaringan seluler — tetap menerima seluruh
aliran dari token pertama, bukan separuhnya.

🔧 **Permintaan yang ditolak bukan giliran** (E-202): giliran yang batal SEBELUM ada
yang terjadi — jawaban konfirmasi yang sudah dijawab, pesan ber-id kembar — di-
`urungkan`, dan aliran kembali ke giliran sebelumnya. Dulu penolakannya mengirim
`error` ke giliran baru yang kosong: klien yang menyambung ulang kehilangan `done`
giliran yang sungguh terjadi.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from functools import partial
from typing import Any
from uuid import UUID

SIMPAN_S = 60.0
PERISTIWA_AKHIR = frozenset({"done", "error"})


class GiliranBerjalan(RuntimeError):
    """Percakapan ini sedang menjalankan giliran lain."""


@dataclass
class Giliran:
    peristiwa: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    selesai: bool = False
    kondisi: asyncio.Condition = field(default_factory=asyncio.Condition)
    buang_pada: float | None = None  # jam loop saat giliran yang selesai dibuang


def _ada_yang_baru(g: Giliran, dibaca: int) -> bool:
    return dibaca < len(g.peristiwa) or g.selesai


class AliranPercakapan:
    def __init__(self, simpan_s: float = SIMPAN_S) -> None:
        self._simpan_s = simpan_s
        self._giliran: dict[UUID, Giliran] = {}

    def sibuk(self, percakapan_id: UUID) -> bool:
        g = self._giliran.get(percakapan_id)
        return g is not None and not g.selesai

    def mulai(self, percakapan_id: UUID) -> Giliran | None:
        """Giliran baru — `GiliranBerjalan` bila yang sebelumnya belum selesai. Yang
        dikembalikan: giliran sebelumnya, untuk `urungkan`."""
        if self.sibuk(percakapan_id):
            raise GiliranBerjalan("percakapan ini sedang menjawab")
        lama = self._giliran.get(percakapan_id)
        self._giliran[percakapan_id] = Giliran()
        return lama

    async def urungkan(self, percakapan_id: UUID, lama: Giliran | None) -> None:
        """Giliran yang batal sebelum mengirim satu peristiwa pun: aliran kembali ke `lama`."""
        g = self._giliran.get(percakapan_id)
        if g is None or g.peristiwa or g.selesai:
            return
        async with g.kondisi:
            g.selesai = True  # pengikut yang terlanjur menunggu giliran kosong ini berhenti
            g.kondisi.notify_all()
        loop = asyncio.get_running_loop()
        if lama is None or lama.buang_pada is None or loop.time() >= lama.buang_pada:
            del self._giliran[percakapan_id]
            return
        self._giliran[percakapan_id] = lama
        loop.call_at(lama.buang_pada, self._buang, percakapan_id, lama)

    async def kirim(self, percakapan_id: UUID, jenis: str, data: Mapping[str, Any]) -> None:
        g = self._giliran.get(percakapan_id)
        if g is None or g.selesai:
            return  # giliran yang sudah ditutup tidak menerima peristiwa lagi
        async with g.kondisi:
            g.peristiwa.append((jenis, dict(data)))
            if jenis in PERISTIWA_AKHIR:
                g.selesai = True
                loop = asyncio.get_running_loop()
                g.buang_pada = loop.time() + self._simpan_s
                loop.call_at(g.buang_pada, self._buang, percakapan_id, g)
            g.kondisi.notify_all()

    def _buang(self, percakapan_id: UUID, g: Giliran) -> None:
        if self._giliran.get(percakapan_id) is g:
            del self._giliran[percakapan_id]

    def ada(self, percakapan_id: UUID) -> bool:
        return percakapan_id in self._giliran

    async def ikuti(self, percakapan_id: UUID) -> AsyncIterator[tuple[str, dict[str, Any]]]:
        """Seluruh peristiwa giliran terakhir, dari yang pertama, sampai `done`/`error`."""
        g = self._giliran.get(percakapan_id)
        if g is None:
            return
        i = 0
        while True:
            async with g.kondisi:
                await g.kondisi.wait_for(partial(_ada_yang_baru, g, i))
                baru, i = g.peristiwa[i:], len(g.peristiwa)
                tamat = g.selesai
            for p in baru:
                yield p
            if tamat and i == len(g.peristiwa):
                return
