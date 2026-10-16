"""spec/07 3.5 — Qdrant + koleksi memori, lewat `platform.KlienVektor` (REST, B-2).

Qdrant tidak punya RLS: yang menjaga **data tiap pengguna milik pribadinya**
(H-27) di sisi vektor adalah saringan `user_id` yang WAJIB di tiap pencarian.
Uji ini membuktikannya terhadap Qdrant sungguhan — bukan tiruan yang menerima
saringan apa pun.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import httpx
import pytest

from hvx.modules.platform import GalatVektor, KlienVektor, PenyematHash, Titik

pytestmark = pytest.mark.integration

PENYEMAT = PenyematHash(b"k" * 32)


@pytest.fixture
async def vektor(url_qdrant_uji: str) -> AsyncIterator[tuple[KlienVektor, str]]:
    klien = KlienVektor(url_qdrant_uji)
    nama = f"uji-{uuid.uuid4().hex[:12]}"
    await klien.pastikan_koleksi(nama, PENYEMAT.dimensi, ["user_id", "scope", "kind"])
    try:
        yield klien, nama
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()


def _titik(user_id: UUID, scope: str, teks: str) -> Titik:
    vektor = PENYEMAT.untuk(user_id).semat(teks)
    return Titik(uuid4(), vektor, {"user_id": str(user_id), "scope": scope, "kind": "episodic"})


async def test_koleksi_dipastikan_berulang_tanpa_galat(vektor: tuple[KlienVektor, str]) -> None:
    klien, nama = vektor

    await klien.pastikan_koleksi(nama, PENYEMAT.dimensi, ["user_id", "scope", "kind"])
    await klien.ping()


async def test_pencarian_hanya_titik_milik_pengguna_itu(vektor: tuple[KlienVektor, str]) -> None:
    klien, nama = vektor
    a, b = uuid4(), uuid4()
    await klien.simpan(
        nama, [_titik(a, "mood", "lari pagi bikin lega"), _titik(b, "mood", "lari pagi")]
    )

    hasil_b = await klien.cari(
        nama, PENYEMAT.untuk(b).semat("lari pagi"), user_id=b, saring={"scope": ["mood"]}, batas=10
    )

    assert {h.payload["user_id"] for h in hasil_b} == {str(b)}, "titik pengguna lain ikut"
    assert len(hasil_b) == 1


async def test_saringan_scope_dan_scope_kosong_tidak_berarti_semua(
    vektor: tuple[KlienVektor, str],
) -> None:
    klien, nama = vektor
    a = uuid4()
    await klien.simpan(
        nama, [_titik(a, "mood", "cemas kerja"), _titik(a, "journal_raw", "cemas kerja lembur")]
    )

    mood = await klien.cari(
        nama,
        PENYEMAT.untuk(a).semat("cemas kerja"),
        user_id=a,
        saring={"scope": ["mood"]},
        batas=10,
    )
    kosong = await klien.cari(
        nama, PENYEMAT.untuk(a).semat("cemas kerja"), user_id=a, saring={"scope": []}, batas=10
    )

    assert [h.payload["scope"] for h in mood] == ["mood"], "scope yang tidak diizinkan ikut"
    assert kosong == [], "tanpa scope yang diizinkan, pencarian mengembalikan sesuatu"


async def test_pencarian_tanpa_pengguna_ditolak_sebelum_ke_qdrant(
    vektor: tuple[KlienVektor, str],
) -> None:
    klien, nama = vektor

    with pytest.raises(TypeError, match="H-27"):
        await klien.cari(
            nama,
            PENYEMAT.untuk(uuid4()).semat("x"),
            user_id=None,  # type: ignore[arg-type]
            saring={},
            batas=1,
        )


async def test_hapus_milik_menghapus_titik_satu_pengguna_saja(
    vektor: tuple[KlienVektor, str],
) -> None:
    klien, nama = vektor
    a, b = uuid4(), uuid4()
    await klien.simpan(nama, [_titik(a, "mood", "tidur cukup"), _titik(b, "mood", "tidur cukup")])

    await klien.hapus_milik(nama, a)

    kueri_a = PENYEMAT.untuk(a).semat("tidur cukup")
    kueri_b = PENYEMAT.untuk(b).semat("tidur cukup")
    assert await klien.cari(nama, kueri_a, user_id=a, saring={}, batas=5) == []
    assert len(await klien.cari(nama, kueri_b, user_id=b, saring={}, batas=5)) == 1, (
        "titik pengguna lain ikut terhapus"
    )


async def test_galat_qdrant_tidak_memantulkan_isi_permintaan(
    vektor: tuple[KlienVektor, str],
) -> None:
    """Badan galat Qdrant MEMANTULKAN masukan (mis. id titik yang tidak sah) — pesan
    `GalatVektor` hanya metode, jalur, dan kode status; ia berakhir di log."""
    klien, nama = vektor
    titik = Titik("rahasia-sekali", PENYEMAT.untuk(uuid4()).semat("x"), {})  # type: ignore[arg-type]

    with pytest.raises(GalatVektor) as galat:
        await klien.simpan(nama, [titik])

    assert "rahasia" not in str(galat.value), f"badan galat Qdrant ikut: {galat.value}"


async def test_qdrant_tak_terjangkau_menjadi_galat_tanpa_isi() -> None:
    klien = KlienVektor("http://127.0.0.1:9", timeout_s=0.5)
    try:
        with pytest.raises(GalatVektor) as galat:
            await klien.simpan("x", [_titik(uuid4(), "mood", "rahasia-sekali")])
    finally:
        await klien.tutup()

    assert "rahasia" not in str(galat.value)


async def test_koleksi_berjarak_lain_ditolak_bukan_dipakai(url_qdrant_uji: str) -> None:
    """Skor dibaca sebagai KOSINUS — `> 0` = mirip, terbesar dulu. Koleksi `Euclid`
    berdimensi sama menjawab JARAK: semua "mirip", dan urutannya terbalik
    (tinjauan penegak buta Sprint 3)."""
    nama = f"uji-{uuid.uuid4().hex[:12]}"
    async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
        r = await h.put(
            f"/collections/{nama}",
            json={"vectors": {"size": PENYEMAT.dimensi, "distance": "Euclid"}},
        )
        assert r.status_code == 200, r.text
    klien = KlienVektor(url_qdrant_uji)
    try:
        with pytest.raises(GalatVektor, match="bukan kosinus"):
            await klien.pastikan_koleksi(nama, PENYEMAT.dimensi, ["user_id"])
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()


async def test_koleksi_berdimensi_lain_ditolak_bukan_dipakai(url_qdrant_uji: str) -> None:
    """Penyemat yang berganti diam-diam: tiap `simpan` gagal satu per satu sampai stream mati."""
    klien = KlienVektor(url_qdrant_uji)
    nama = f"uji-{uuid.uuid4().hex[:12]}"
    try:
        await klien.pastikan_koleksi(nama, 8, ["user_id"])
        with pytest.raises(GalatVektor, match="berdimensi 384"):
            await klien.pastikan_koleksi(nama, PENYEMAT.dimensi, ["user_id"])
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()
