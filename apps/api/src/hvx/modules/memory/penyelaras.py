"""Penyelaras vektor memori — `memories` (PostgreSQL) → Qdrant, sesudah commit.

Qdrant tidak ikut transaksi PostgreSQL. Kalau ekstraksi, sunting jurnal, dan
hapus jurnal harus menulis ke keduanya sekaligus, tiap jalan itu gagal saat
Qdrant tersendat — atau lebih buruk, berhasil di satu sisi saja. Karena itu
PostgreSQL satu-satunya yang ditulis di jalan pengguna, dan penyelaras ini
(proses `hvx.pekerja`) menyusul:

* memori yang `embedding_model`-nya bukan penyemat ini (baru, isinya berubah,
  atau disemat penyemat/kunci lain) → disemat ke titik ber-id memori itu
  (`upsert` — menimpa vektor lama);
* memori terhapus (isinya sudah kosong) → titiknya dibuang, lalu barisnya.
  Naskah: *“tidak boleh hanya menghapus row di PostgreSQL”* (docs/139).

Tiga langkah, dan tidak satu pun menahan kunci baris selama Qdrant dipanggil:

1. **Baca** baris yang punya pekerjaan di transaksi PEMILIKNYA (RLS) — beserta
   sidik (`sha256`) isinya — lalu commit.
2. **Semat dan kirim** di luar transaksi: penyematan (CPU murni Python) di
   thread, bukan di event loop yang juga menjalankan relay dan konsumen; teks
   yang disemat paling panjang `MAKS_TEKS_SEMAT` karakter.
3. **Tandai** hanya baris yang isinya MASIH sama dengan sidiknya. Yang berubah
   di antaranya tetap belum tersemat, dan putaran berikutnya menyematnya ulang.

🔴 Versi pertama menyemat 200 baris di dalam transaksi `FOR UPDATE`, di event
loop: 40 jurnal 100 ribu karakter dari SATU pengguna menahan event loop pekerja
6,5 dtk (tinjauan keamanan Sprint 3, S2), dan `PATCH /journal` menunggu Qdrant
yang lambat (tinjauan kontrak Sprint 3, K3) — padahal Qdrant dijanjikan tidak
pernah ada di jalan pengguna.

Siapa yang punya pekerjaan ditanyakan lewat fungsi sempit
`memori_perlu_diselaraskan` (spec/01 §12) — hanya `user_id`. Payload titik hanya
`user_id` · `scope` · `kind` · `model` — tidak pernah isi. Vektor tiap pengguna
disemat dengan kuncinya sendiri (`Penyemat.untuk`, S1).
"""

from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository

INDEKS_PAYLOAD = ("user_id", "scope", "kind", "model")
BATAS_PENGGUNA = 100
BATAS_BARIS = 50
# Karakter pertama yang disemat per memori (K-26): ±3.000 kata. Isi tetap utuh
# di PostgreSQL; yang dipotong hanya bahan pencarian leksikalnya.
MAKS_TEKS_SEMAT = 20_000
# Satu putaran menghabiskan antrean sampai batas ini, lalu memberi jeda —
# penyematan ulang besar (kunci diganti) tidak memonopoli pekerja.
_MAKS_GELOMBANG = 10


class PenyelarasVektor:
    def __init__(
        self,
        engine: AsyncEngine,
        vektor: platform.KlienVektor,
        penyemat: platform.Penyemat,
        koleksi: str,
    ) -> None:
        self._engine = engine
        self._vektor = vektor
        self._penyemat = penyemat
        self._koleksi = koleksi
        self._siap = False

    async def siapkan(self) -> None:
        await self._vektor.pastikan_koleksi(
            self._koleksi, self._penyemat.dimensi, list(INDEKS_PAYLOAD)
        )
        self._siap = True

    async def putaran(self) -> int:
        """Jumlah memori yang diselaraskan. Qdrant yang mati melempar — pemanggil mengulang."""
        if not self._siap:
            await self.siapkan()  # di sini, bukan saat mulai: Qdrant boleh menyusul hidup
        selesai = 0
        for _ in range(_MAKS_GELOMBANG):
            async with platform.transaksi_sistem(self._engine) as conn:
                pengguna = await repository.pengguna_perlu_diselaraskan(
                    conn, self._penyemat.nama, BATAS_PENGGUNA
                )
            gelombang = 0
            for user_id in pengguna:
                gelombang += await self._selaraskan(user_id)
            selesai += gelombang
            if gelombang == 0:
                break
        return selesai

    async def _selaraskan(self, user_id: UUID) -> int:
        nama = self._penyemat.nama
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            baris = await repository.perlu_diselaraskan(conn, nama, BATAS_BARIS)
        if not baris:
            return 0
        buang = [b.id for b in baris if b.deleted_at is not None]
        semat = [b for b in baris if b.deleted_at is None]
        penyemat = self._penyemat.untuk(user_id)
        vektor = await asyncio.to_thread(
            lambda: [penyemat.semat(b.content[:MAKS_TEKS_SEMAT]) for b in semat]
        )
        await self._vektor.hapus(self._koleksi, buang)
        await self._vektor.simpan(
            self._koleksi,
            [
                platform.Titik(
                    b.id,
                    v,
                    {"user_id": str(b.user_id), "scope": b.scope, "kind": b.kind, "model": nama},
                )
                for b, v in zip(semat, vektor, strict=True)
            ],
        )
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            await repository.buang(conn, buang)
            await repository.tandai_tersemat(conn, semat, nama)
        return len(baris)
