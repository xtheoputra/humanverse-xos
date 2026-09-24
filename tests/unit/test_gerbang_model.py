"""spec/07 4.1 — AI Gateway + Model Router, tanpa jaringan (K-28).

Yang diperiksa adalah jalurnya: kelas → model → penyedia, token & biaya tiap
panggilan, aliran token, dan penyedia lokal yang tidak mengarang fakta.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal

import pytest

from hvx.modules.platform import (
    TANPA_DATA,
    GalatModel,
    GerbangModel,
    HargaModel,
    PenyediaLokal,
    PermintaanModel,
)

MODEL = {"simple": "lokal/hvx-ringkas-v1", "reasoning": "lokal/hvx-nalar-v1"}


def _gerbang(harga: dict[str, HargaModel] | None = None) -> GerbangModel:
    return GerbangModel({"lokal": PenyediaLokal()}, MODEL, harga or {})


def _minta(kelas: str = "simple", *bahan: str, maks_token: int = 400) -> PermintaanModel:
    return PermintaanModel(
        kelas=kelas,  # type: ignore[arg-type]
        tugas="coach-agent",
        pertanyaan="bagaimana tidurku?",
        bahan=bahan,
        maks_token=maks_token,
    )


async def test_kelas_menentukan_model_dan_jejaknya_lengkap() -> None:
    gerbang = _gerbang({"lokal/hvx-nalar-v1": HargaModel(Decimal(3), Decimal(15))})

    kecil = await gerbang.hasilkan(_minta("simple", "Tidur 7 jam semalam."))
    besar = await gerbang.hasilkan(_minta("reasoning", "Tidur 5 jam.", "Workout terlewat 2x."))

    assert (kecil.model, besar.model) == ("lokal/hvx-ringkas-v1", "lokal/hvx-nalar-v1")
    assert kecil.teks == "Tidur 7 jam semalam."
    assert besar.teks == "• Tidur 5 jam.\n• Workout terlewat 2x."
    assert (kecil.token_masuk, kecil.token_keluar) == (7, 4)
    assert kecil.biaya_usd == Decimal("0.000000"), "model lokal tanpa harga = gratis"
    # (masuk × 3 + keluar × 15) / 1.000.000, skala numeric(12,6) spec/01
    harapan = (Decimal(besar.token_masuk) * 3 + Decimal(besar.token_keluar) * 15) / 1_000_000
    assert besar.biaya_usd == harapan.quantize(Decimal("0.000001")), (
        f"biaya {besar.biaya_usd} ≠ tarif × token masuk & keluar"
    )
    assert besar.biaya_usd > 0
    assert besar.latensi_ms >= 0


async def test_tanpa_bahan_tidak_mengarang() -> None:
    """arch/08 Pasal 8 — rantai degradasi berakhir di “belum ada data”, bukan tebakan."""
    jawaban = await _gerbang().hasilkan(_minta("reasoning"))

    assert jawaban.teks == TANPA_DATA, f"jawaban tanpa bahan: {jawaban.teks!r}"


async def test_token_mengalir_satu_per_satu_lalu_jawabannya_utuh() -> None:
    aliran = _gerbang().alirkan(_minta("simple", "Satu dua tiga empat."))

    potongan = [p async for p in aliran]

    assert len(potongan) == 4, potongan
    assert aliran.jawaban is not None
    assert "".join(potongan) == aliran.jawaban.teks == "Satu dua tiga empat."


async def test_jawaban_berhenti_di_maks_token() -> None:
    jawaban = await _gerbang().hasilkan(_minta("simple", "a b c d e f", maks_token=3))

    assert jawaban.teks == "a b c"
    assert jawaban.token_keluar == 3


def test_model_router_turun_ke_model_kecil_saat_anggaran_habis() -> None:
    gerbang = _gerbang()

    assert gerbang.pilih_kelas("reasoning", anggaran_habis=False) == "reasoning"
    assert gerbang.pilih_kelas("reasoning", anggaran_habis=True) == "simple", (
        "anggaran habis, tetap model besar"
    )
    assert gerbang.pilih_kelas("simple", anggaran_habis=True) == "simple"


class _PenyediaLuar:
    nama = "luar"

    def hitung_token(self, teks: str) -> int:
        return len(teks)

    async def alirkan(self, model: str, permintaan: PermintaanModel) -> AsyncIterator[str]:
        yield "x"


def test_model_berbayar_tanpa_harga_ditolak_saat_dirakit() -> None:
    """Biaya yang tidak bisa dihitung tidak bisa dibatasi (spec/07 4.9)."""
    model = {"simple": "lokal/hvx-ringkas-v1", "reasoning": "luar/besar"}
    penyedia = {"lokal": PenyediaLokal(), "luar": _PenyediaLuar()}

    with pytest.raises(GalatModel, match="tanpa harga"):
        GerbangModel(penyedia, model, {})  # type: ignore[arg-type]
    GerbangModel(penyedia, model, {"luar/besar": HargaModel(Decimal(1), Decimal(2))})  # type: ignore[arg-type]


def test_penyedia_tak_dikenal_ditolak_saat_dirakit() -> None:
    with pytest.raises(GalatModel, match="penyedia 'hilang'"):
        GerbangModel({"lokal": PenyediaLokal()}, {**MODEL, "reasoning": "hilang/x"}, {})
