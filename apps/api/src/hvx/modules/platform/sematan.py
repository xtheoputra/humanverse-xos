"""Penyemat teks → vektor — spec/07 3.5–3.7 (memori di Qdrant, ADR-003).

🔧 **V0 memakai penyemat LOKAL yang deterministik (`hvx-hash-v1`), bukan model
bahasa** — dan itu keputusan yang dinyatakan, bukan penghematan diam-diam (K-26):

* **Penyedia model milik pemilik** (arch/05 §6, A-6/#18 — tarif & bagi hasil):
  memilih API sematan berbayar di sini berarti mengambil keputusan itu.
* **CI tanpa tagihan** (H-26): uji dan gerbang tidak boleh memanggil layanan
  berbayar, dan hasil uji tidak boleh bergantung pada jaringan.
* **Hasilnya sama di tiap proses dan tiap mesin** — `blake2b`, bukan `hash()`
  Python yang diacak per proses.
* 🔒 **Berkunci** (`HVX_SEMATAN_KEY`). *Feature hashing* tanpa kunci bisa
  DIBALIK dengan kamus: siapa pun yang memegang vektornya menghitung hash tiap
  kata calon dan membaca kata mana yang ada — isi jurnal (Level 3 *Sensitive*,
  naskah `docs/133`) terbaca dari Qdrant, yang tidak punya RLS. Sidik kunci ikut
  di `nama`: vektor dari kunci lain tidak pernah dibandingkan, dan penyelaras
  menyemat ulang memori yang `embedding_model`-nya berbeda.
* 🔒 **Satu ruang vektor per pengguna**: kunci tiap pengguna diturunkan dari
  kunci proses (`untuk(user_id)`), dan penyemat proses sendiri TIDAK menyemat.
  🔴 Versi pertama memakai satu kunci untuk semua: penyerang yang bisa membaca
  Qdrant cukup membuat akun biasa, menulis kata-kata kamus sebagai jurnalnya
  sendiri, dan membandingkan vektor yang disemat server dengan vektor korban —
  kuncinya tidak pernah ia sentuh (tinjauan keamanan Sprint 3, S1). Dengan kunci
  turunan, vektor dua pengguna tidak sebanding sama sekali.

Yang dihasilkannya: kemiripan **leksikal** yang tahan salah ketik — kata,
pasangan kata, dan trigram huruf di-hash ke 384 dimensi bertanda, lalu
dinormalkan (kosinus = hasil kali titik). ⚠️ Itu BUKAN kemiripan makna:
*“lelah”* dan *“capek”* tidak berdekatan. Antarmuka `Penyemat` memisahkan
pemanggilnya dari pilihan ini — model sungguhan (lokal atau penyedia) masuk
lewat kelas lain dengan `nama` lain, dan `memories.embedding_model` mencatat
dengan apa tiap memori disemat, supaya penggantian tidak mencampur ruang vektor.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import re
import unicodedata
from itertools import pairwise
from typing import Protocol
from uuid import UUID

from .config import Settings

_KATA = re.compile(r"[^\W_]+", re.UNICODE)


class SematanPengguna(Protocol):
    """Penyemat SATU pengguna — vektornya hanya sebanding dengan vektor pengguna yang sama."""

    @property
    def nama(self) -> str: ...

    @property
    def dimensi(self) -> int: ...

    def semat(self, teks: str) -> list[float]: ...


class Penyemat(Protocol):
    """Penyemat proses — tidak menyemat sendiri; tiap pengguna mendapat ruang vektornya."""

    @property
    def nama(self) -> str: ...

    @property
    def dimensi(self) -> int: ...

    def untuk(self, user_id: UUID) -> SematanPengguna: ...


def _periksa(kunci: bytes, dimensi: int) -> None:
    if not isinstance(kunci, bytes) or not 32 <= len(kunci) <= 64:
        raise ValueError("kunci penyemat wajib 32–64 byte")
    if dimensi < 16:
        raise ValueError("dimensi sematan terlalu kecil")


class PenyematHash:
    """Feature hashing bertanda BERKUNCI — kunci proses, dari sana kunci tiap pengguna."""

    def __init__(self, kunci: bytes, dimensi: int = 384) -> None:
        _periksa(kunci, dimensi)
        self._kunci = kunci
        self._dimensi = dimensi
        sidik = hashlib.blake2b(b"hvx-sematan-sidik", key=kunci, digest_size=4).hexdigest()
        self._nama = f"hvx-hash-v1-{dimensi}-{sidik}"

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def dimensi(self) -> int:
        return self._dimensi

    def untuk(self, user_id: UUID) -> SematanPengguna:
        if not isinstance(user_id, UUID):
            raise TypeError("penyemat wajib diturunkan untuk satu user_id (S1, H-27)")
        turunan = hmac.new(
            self._kunci, b"hvx-sematan-pengguna:" + user_id.bytes, hashlib.sha256
        ).digest()
        return _SematanHash(turunan, self._dimensi, self._nama)


class _SematanHash:
    """Feature hashing bertanda atas kata · pasangan kata · trigram huruf, satu kunci."""

    def __init__(self, kunci: bytes, dimensi: int, nama: str) -> None:
        _periksa(kunci, dimensi)
        self._kunci = kunci
        self._dimensi = dimensi
        self._nama = nama

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def dimensi(self) -> int:
        return self._dimensi

    def _fitur(self, teks: str) -> list[tuple[str, float]]:
        normal = unicodedata.normalize("NFKC", teks).casefold()
        kata = _KATA.findall(normal)
        fitur: list[tuple[str, float]] = [(f"k:{k}", 1.0) for k in kata]
        fitur += [(f"p:{a} {b}", 0.7) for a, b in pairwise(kata)]
        for k in kata:
            bingkai = f"^{k}$"
            fitur += [(f"t:{bingkai[i : i + 3]}", 0.3) for i in range(len(bingkai) - 2)]
        return fitur

    def semat(self, teks: str) -> list[float]:
        vektor = [0.0] * self._dimensi
        for fitur, bobot in self._fitur(teks):
            cerna = hashlib.blake2b(fitur.encode(), digest_size=8, key=self._kunci).digest()
            indeks = int.from_bytes(cerna[:4], "little") % self._dimensi
            tanda = 1.0 if cerna[4] & 1 else -1.0
            vektor[indeks] += tanda * bobot
        panjang = math.sqrt(sum(v * v for v in vektor))
        if panjang == 0:
            return vektor  # teks tanpa satu kata pun — vektor nol, tidak mirip apa pun
        return [v / panjang for v in vektor]


def penyemat_dari(settings: Settings) -> PenyematHash:
    """Penyemat proses ini — `HVX_SEMATAN_KEY` wajib (tanpa kunci, vektor bisa dibalik)."""
    if settings.sematan_key is None:
        raise RuntimeError("HVX_SEMATAN_KEY wajib untuk menyemat memori (K-26)")
    return PenyematHash(hashlib.sha256(settings.sematan_key.get_secret_value().encode()).digest())
