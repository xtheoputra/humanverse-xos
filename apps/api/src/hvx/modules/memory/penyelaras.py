"""Penyelaras vektor memori — `memories` (PostgreSQL) → Qdrant, sesudah commit.

Qdrant tidak ikut transaksi PostgreSQL. Kalau ekstraksi, sunting jurnal, dan
hapus jurnal harus menulis ke keduanya sekaligus, tiap jalan itu gagal saat
Qdrant tersendat — atau lebih buruk, berhasil di satu sisi saja. Karena itu
PostgreSQL satu-satunya yang ditulis di jalan pengguna, dan penyelaras ini
(proses `hvx.pekerja`) menyusul:

* memori yang `model_version`-nya bukan penyemat ini (baru, isinya berubah,
  atau disemat penyemat/kunci lain) → disemat ke titik ber-id memori itu
  (`upsert` — menimpa vektor lama);
* memori terhapus (isinya sudah kosong) → titiknya dibuang, lalu barisnya.
  Naskah: *“tidak boleh hanya menghapus row di PostgreSQL”* (docs/139).

Siapa yang punya pekerjaan ditanyakan lewat fungsi sempit
`memori_perlu_diselaraskan` (spec/01 §12) — hanya `user_id`; barisnya dibaca
dan dikunci di transaksi PEMILIKNYA, di bawah RLS. Qdrant dipanggil di dalam
transaksi itu: kalau Qdrant gagal, tidak ada yang ditandai selesai, dan putaran
berikutnya mengulang (simpan dan hapus titik idempoten).

Payload titik hanya `user_id` · `scope` · `kind` · `model` — tidak pernah isi.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository

INDEKS_PAYLOAD = ("user_id", "scope", "kind", "model")
BATAS_PENGGUNA = 100
BATAS_BARIS = 200
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
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            baris = await repository.perlu_diselaraskan(conn, self._penyemat.nama, BATAS_BARIS)
            buang = [b.id for b in baris if b.deleted_at is not None]
            semat = [b for b in baris if b.deleted_at is None]
            await self._vektor.hapus(self._koleksi, buang)
            await repository.buang(conn, buang)
            await self._vektor.simpan(
                self._koleksi,
                [
                    platform.Titik(
                        b.id,
                        self._penyemat.semat(b.content),
                        {
                            "user_id": str(b.user_id),
                            "scope": b.scope,
                            "kind": b.kind,
                            "model": self._penyemat.nama,
                        },
                    )
                    for b in semat
                ],
            )
            await repository.tandai_tersemat(conn, [b.id for b in semat], self._penyemat.nama)
        return len(baris)
