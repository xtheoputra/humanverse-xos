"""AI Gateway + Model Router — spec/07 4.1: *“catat mood” **tidak** memanggil model besar*.

Naskah 5 §22: *“Tidak semua request membutuhkan model paling mahal”* — dan
*“Catat mood saya”* dirutekan ke **deterministic**: mencatat mood adalah
`INSERT`, bukan inferensi. Tiga rute V0:

* `deterministic` — **tidak ada model sama sekali**; perintah berbentuk tetap
  dijalankan layanan biasa. Gerbang ini bahkan tidak disentuh;
* `simple` — model kecil;
* `reasoning` — model besar.

(`vision` · `embedding` di manifest spec/05: V0 tidak punya penglihatan, dan
sematan memori punya jalurnya sendiri — K-26.)

**Gerbang ini satu-satunya jalan ke model** (B-2): penyedia hanya di
`platform`, dan tiap panggilan membawa pulang yang dibutuhkan jejak audit —
model, token masuk & keluar, latensi, biaya (naskah 4 §48 *AI Cost Engine*;
spec/01 `ai_messages.cost_usd`). Model yang harganya tidak diketahui DITOLAK
saat gerbang dirakit: biaya yang tidak bisa dihitung tidak bisa dibatasi (4.9).

**Penyedia V0 = `lokal`** (K-28): tanpa jaringan, tanpa biaya, deterministik.
Penyedia berbayar — dan ke mana data pengguna boleh dikirim — keputusan
pemilik (A-6/#18, arch/05 §6). Penyedia lokal tidak MENALAR: ia merangkai
`bahan` yang disiapkan agent (kalimat fakta yang dipakai, masing-masing dengan
sumbernya) menjadi jawaban, dan **tidak menambah satu fakta pun** — tanpa
bahan, jawabannya menyatakan bahwa datanya belum ada (arch/08 Pasal 8:
*dilarang mengarang data*). Yang nyata di V0 adalah jalurnya: rute, pilihan
model, token, biaya, aliran token — supaya penyedia sungguhan kelak masuk
tanpa mengubah satu agent pun.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Mapping
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, Protocol

from .config import Settings

Rute = Literal["deterministic", "simple", "reasoning"]
KelasModel = Literal["simple", "reasoning"]
KELAS_MODEL: tuple[KelasModel, ...] = ("simple", "reasoning")

# Kalimat penutup rantai degradasi (arch/08 Pasal 8) — bukan tebakan.
TANPA_DATA = "Belum ada data yang cukup untuk menjawabnya."

_SEPERSEJUTA = Decimal(1_000_000)
_SEN_MIKRO = Decimal("0.000001")  # skala numeric(12,6) `cost_usd` spec/01


class GalatModel(RuntimeError):
    """Gerbang model tidak bisa dirakit atau dipanggil — pesan tanpa isi permintaan."""


@dataclass(frozen=True)
class PermintaanModel:
    """Yang dikirim ke model: tugas, pertanyaan, dan BAHAN — bukan riwayat mentah.

    `bahan` adalah satu-satunya fakta yang boleh dipakai jawaban; agent yang
    menyiapkannya sudah melewati gerbang izin untuk tiap sumbernya.
    """

    kelas: KelasModel
    tugas: str
    pertanyaan: str
    bahan: tuple[str, ...] = ()
    maks_token: int = 400


@dataclass(frozen=True)
class JawabanModel:
    teks: str
    model: str  # "penyedia/nama" — dicatat apa adanya di agent_runs.model_used
    token_masuk: int
    token_keluar: int
    biaya_usd: Decimal
    latensi_ms: int


@dataclass(frozen=True)
class HargaModel:
    """USD per SEJUTA token — tarif penyedia apa adanya."""

    masuk: Decimal
    keluar: Decimal

    def biaya(self, token_masuk: int, token_keluar: int) -> Decimal:
        mentah = (Decimal(token_masuk) * self.masuk + Decimal(token_keluar) * self.keluar) / (
            _SEPERSEJUTA
        )
        return mentah.quantize(_SEN_MIKRO, rounding=ROUND_HALF_UP)


GRATIS = HargaModel(Decimal(0), Decimal(0))


class Penyedia(Protocol):
    """Satu penyedia model. `nama` = awalan id model (`lokal/…`)."""

    nama: str

    def hitung_token(self, teks: str) -> int: ...

    def alirkan(self, model: str, permintaan: PermintaanModel) -> AsyncIterator[str]: ...


class PenyediaLokal:
    """Penyedia V0 tanpa jaringan dan tanpa bobot model (K-28) — lihat docstring modul.

    Token = kata. Rute `reasoning` merangkai bahan sebagai daftar (satu fakta per
    baris, urutannya dijaga); `simple` sebagai satu paragraf. Tidak ada yang acak:
    permintaan yang sama selalu dijawab sama — itu yang membuat uji agent mungkin.
    """

    nama = "lokal"

    def hitung_token(self, teks: str) -> int:
        return len(teks.split())

    async def alirkan(self, model: str, permintaan: PermintaanModel) -> AsyncIterator[str]:
        if not permintaan.bahan:
            teks = TANPA_DATA
        elif permintaan.kelas == "reasoning":
            teks = "\n".join(f"• {b}" for b in permintaan.bahan)
        else:
            teks = " ".join(permintaan.bahan)
        kata = teks.split(" ")
        dipakai = 0
        for i, potongan in enumerate(kata):
            dipakai += self.hitung_token(potongan)
            if dipakai > permintaan.maks_token:
                return
            yield potongan if i == 0 else " " + potongan
            await asyncio.sleep(0)  # token mengalir: beri giliran pada penulis SSE


@dataclass
class AliranModel:
    """Satu panggilan model yang mengalir. `jawaban` terisi sesudah aliran habis — ATAU
    sesudah ditutup di tengah jalan (`aclose`, pembatalan): token yang sudah keluar sudah
    dibayar, jadi tetap dihitung (spec/07 4.4 · 4.9)."""

    _potongan: AsyncIterator[str]
    _selesai: Callable[[str], JawabanModel]
    jawaban: JawabanModel | None = field(default=None, init=False)

    def __aiter__(self) -> AsyncGenerator[str, None]:
        return self._alir()

    async def _alir(self) -> AsyncGenerator[str, None]:
        bagian: list[str] = []
        try:
            async for p in self._potongan:
                bagian.append(p)
                yield p
        finally:
            self.jawaban = self._selesai("".join(bagian))


class GerbangModel:
    """AI Gateway: kelas → model (Model Router) → penyedia, dengan token & biaya tiap panggilan."""

    def __init__(
        self,
        penyedia: Mapping[str, Penyedia],
        model_per_kelas: Mapping[KelasModel, str],
        harga: Mapping[str, HargaModel],
    ) -> None:
        self._penyedia = dict(penyedia)
        self._model = dict(model_per_kelas)
        self._harga = dict(harga)
        for kelas in KELAS_MODEL:
            model = self._model.get(kelas)
            if model is None:
                raise GalatModel(f"kelas {kelas} tanpa model")
            nama_penyedia = model.split("/", 1)[0]
            if nama_penyedia not in self._penyedia:
                raise GalatModel(f"model {model}: penyedia {nama_penyedia!r} tidak dikenal")
            if model not in self._harga and nama_penyedia != PenyediaLokal.nama:
                # Biaya yang tidak bisa dihitung tidak bisa dibatasi (spec/07 4.9).
                raise GalatModel(f"model {model} tanpa harga — anggaran tidak bisa dihitung")

    def model_untuk(self, kelas: KelasModel) -> str:
        return self._model[kelas]

    def pilih_kelas(self, kelas: KelasModel, *, anggaran_habis: bool) -> KelasModel:
        """Model Router: anggaran harian habis → turun ke model KECIL, bukan gagal (4.9)."""
        return "simple" if anggaran_habis else kelas

    def alirkan(self, permintaan: PermintaanModel) -> AliranModel:
        model = self._model[permintaan.kelas]
        penyedia = self._penyedia[model.split("/", 1)[0]]
        harga = self._harga.get(model, GRATIS)
        mulai = time.perf_counter()
        token_masuk = penyedia.hitung_token(
            " ".join((permintaan.tugas, permintaan.pertanyaan, *permintaan.bahan))
        )

        def selesai(teks: str) -> JawabanModel:
            token_keluar = penyedia.hitung_token(teks)
            return JawabanModel(
                teks=teks,
                model=model,
                token_masuk=token_masuk,
                token_keluar=token_keluar,
                biaya_usd=harga.biaya(token_masuk, token_keluar),
                latensi_ms=round((time.perf_counter() - mulai) * 1000),
            )

        return AliranModel(penyedia.alirkan(model, permintaan), selesai)

    async def hasilkan(self, permintaan: PermintaanModel) -> JawabanModel:
        aliran = self.alirkan(permintaan)
        async for _ in aliran:
            pass
        if aliran.jawaban is None:  # pragma: no cover - aliran yang habis selalu mengisinya
            raise GalatModel("aliran model berhenti tanpa jawaban")
        return aliran.jawaban


def gerbang_model_dari(settings: Settings) -> GerbangModel:
    """Gerbang model proses ini — V0 hanya penyedia `lokal` (K-28)."""
    return GerbangModel(
        {PenyediaLokal.nama: PenyediaLokal()},
        {"simple": settings.model_simple, "reasoning": settings.model_reasoning},
        {
            model: HargaModel(Decimal(masuk), Decimal(keluar))
            for model, (masuk, keluar) in settings.model_harga.items()
        },
    )
