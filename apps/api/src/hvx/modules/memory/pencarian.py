"""Pencarian memori — spec/07 3.7: *“agent tanpa izin scope **tidak** menerima barisnya”*.

Tiga saringan berlapis, dan tiap lapis sanggup menahan sendiri:

1. **Manifest** — scope yang diminta pemanggil (manifest `memory.read`, spec/05)
   wajib ada di daftar resmi `identity.SCOPE_RESMI`; di luar itu DITOLAK
   (`ValueError`), bukan diabaikan — manifest salah ketik adalah galat.
2. **Keputusan pengguna** — `identity.MesinIzin.cek(user, agent, scope, "read")`
   dengan bawaan risk 0 (`memory.search` di tool registry spec/05) = `allow`;
   scope sensitif tidak pernah terbuka karena bawaan (E-180). `deny` → tidak
   dicari. `ask` → tidak dicari DAN dilaporkan di `perlu_izin`: gerbang risiko
   (4.5) yang meminta izin, bukan pencarian yang diam-diam melewatinya.
3. **Baris PostgreSQL** — titik dari Qdrant hanya KANDIDAT. Tiap hasil dibaca
   ulang di bawah RLS pemiliknya, dan scope, hapus-lunak, serta `valid_until`
   diperiksa di barisnya: payload Qdrant bisa basi, dan Qdrant tidak punya RLS.

Tidak satu scope pun diizinkan → Qdrant tidak ditanya sama sekali.
Hanya titik yang disemat penyemat yang sama (`model`) yang dibandingkan —
kosinus antar-ruang vektor tidak bermakna.
"""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import identity, platform

from . import repository
from .schemas import HasilCariMemori, MemoriDitemukan

MAKS_HASIL = 50
# Kandidat dari Qdrant per hasil yang diminta: titik yang barisnya sudah tidak
# boleh diserahkan (basi, terhapus) tidak mengurangi jumlah hasil yang sah.
_KANDIDAT_PER_HASIL = 3
# `memory.search` — risk 0 di tool registry spec/05, dan bawaan V0 risk 0 = `allow`.
_BAWAAN_RISK_0: identity.Keputusan = "allow"


class PencariMemori:
    def __init__(
        self,
        engine: AsyncEngine,
        izin: identity.MesinIzin,
        vektor: platform.KlienVektor,
        penyemat: platform.Penyemat,
        koleksi: str,
    ) -> None:
        self._engine = engine
        self._izin = izin
        self._vektor = vektor
        self._penyemat = penyemat
        self._koleksi = koleksi

    async def cari(
        self,
        *,
        user_id: UUID,
        agent: str,
        scope_manifest: Iterable[str],
        kueri: str,
        batas: int = 10,
    ) -> HasilCariMemori:
        if not isinstance(kueri, str) or not kueri.strip():
            raise ValueError("kueri pencarian memori kosong")
        if isinstance(batas, bool) or not isinstance(batas, int) or not 1 <= batas <= MAKS_HASIL:
            raise ValueError(f"batas pencarian memori 1–{MAKS_HASIL}")
        diminta = frozenset(scope_manifest)
        asing = sorted(diminta - identity.SCOPE_RESMI.keys())
        if asing:
            raise ValueError(f"scope di luar daftar resmi spec/05: {asing}")

        subjek = identity.Subjek("agent", agent)
        dipakai: list[str] = []
        perlu_izin: list[str] = []
        for scope in sorted(diminta):
            keputusan = await self._izin.cek(user_id, subjek, scope, "read", bawaan=_BAWAAN_RISK_0)
            if keputusan == "allow":
                dipakai.append(scope)
            elif keputusan == "ask":
                perlu_izin.append(scope)
        if not dipakai:
            return HasilCariMemori([], [], perlu_izin)

        vektor = self._penyemat.semat(kueri)
        if not any(vektor):
            # Kueri tanpa satu kata pun: vektor nol "berjarak" 0 ke SEMUA titik, dan
            # Qdrant mengembalikan semuanya dengan skor 0 — itu bukan kecocokan.
            return HasilCariMemori([], dipakai, perlu_izin)
        kandidat = [
            k
            for k in await self._vektor.cari(
                self._koleksi,
                vektor,
                user_id=user_id,
                saring={"scope": dipakai, "model": [self._penyemat.nama]},
                batas=batas * _KANDIDAT_PER_HASIL,
            )
            if k.skor > 0  # kosinus ≤ 0 bukan kemiripan
        ]
        if not kandidat:
            return HasilCariMemori([], dipakai, perlu_izin)
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            baris = await repository.hidup_menurut_id(conn, [k.id for k in kandidat], dipakai)
        items = [MemoriDitemukan(baris[k.id], k.skor) for k in kandidat if k.id in baris]
        return HasilCariMemori(items[:batas], dipakai, perlu_izin)
