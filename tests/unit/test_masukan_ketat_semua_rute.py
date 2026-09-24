"""spec/04 *Aturan lintas endpoint* — bentuk salah → `400`, tidak dikoersi diam-diam (E-170).

FastAPI memvalidasi badan dalam mode PYTHON pydantic, yang menerima `true`
sebagai 1, `"3"` sebagai 3, dan detik Unix sebagai tanggal UTC (lihat
`platform/masukan.py`). Uji ini menelusuri SKEMA INTI tiap rute yang dirakit
`hvx.main` — bukan daftar model yang ditulis tangan, yang akan lupa model
berikutnya:

* di BADAN: tiap node `int`/`bool`/`float`/`decimal` wajib ketat
  (`platform.Bulat`, `platform.Benar`) atau dijaga `platform.AngkaJson`;
* di badan, kueri, DAN jalur: tiap node `date`/`datetime` wajib dijaga
  `platform.Tanggal`/`platform.WaktuBerzona` — `?for_date=1758672000` adalah
  tanggal UTC yang sama salahnya dengan badan.

Angka di kueri/jalur (`?limit=`) sengaja longgar: di URL semuanya teks.

🔴 FastAPI 0.141 menyimpan rute ber-`include_router` sebagai `_IncludedRouter`
(`test_idempotensi_terpasang.py`) — syarat populasi di bawah menjaga uji ini
tidak diam-diam membaca nol rute.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.routing import APIRoute

from hvx.main import create_app
from hvx.modules import platform
from hvx.modules.platform import Settings

_ANGKA = frozenset({"int", "bool", "float", "decimal"})
_WAKTU = frozenset({"date", "datetime", "time", "timedelta"})
# Bukan bagian validasi masukan: skema keluaran dan catatan pydantic.
_BUKAN_MASUKAN = frozenset({"serialization", "metadata", "return_schema"})


def _rute() -> Iterator[APIRoute]:
    app = create_app(Settings(database_url="postgresql://x", redis_url="redis://x", env="test"))
    for r in app.router.routes:
        induk = getattr(r, "original_router", None)
        for rute in getattr(induk, "routes", [r]):
            if isinstance(rute, APIRoute):
                yield rute


def _parameter(rute: APIRoute) -> Iterator[tuple[str, Any]]:
    """(tempat, ModelField) tiap parameter kueri/jalur/header — termasuk dependensinya."""
    tumpukan = [rute.dependant]
    while tumpukan:
        d = tumpukan.pop()
        for tempat, daftar in (
            ("query", d.query_params),
            ("path", d.path_params),
            ("header", d.header_params),
            ("cookie", d.cookie_params),
        ):
            for p in daftar:
                yield tempat, p
        tumpukan.extend(d.dependencies)


def _temuan(skema: Any, *, badan: bool) -> list[str]:
    temuan: list[str] = []

    def jelajah(node: Any, jalur: str, dijaga: bool) -> None:
        if isinstance(node, list):
            for isi in node:
                jelajah(isi, jalur, False)
            return
        if not isinstance(node, dict):
            return
        jenis = node.get("type")
        if jenis == "function-before":
            penjaga = node["function"]["function"] in platform.PENJAGA_KETAT
            jelajah(node["schema"], jalur, penjaga)
            return
        if jenis in _WAKTU and not dijaga:
            temuan.append(f"{jalur}: `{jenis}` tanpa platform.Tanggal/WaktuBerzona")
        if badan and jenis in _ANGKA and not (dijaga or node.get("strict")):
            temuan.append(f"{jalur}: `{jenis}` longgar — pakai platform.Bulat/Benar/AngkaJson")
        for kunci, isi in node.items():
            if kunci in _BUKAN_MASUKAN:
                continue
            if kunci == "fields" and isinstance(isi, dict):
                for nama, medan in isi.items():
                    jelajah(medan, f"{jalur}.{nama}", False)
            else:
                jelajah(isi, jalur, False)

    jelajah(skema, "", False)
    return temuan


def test_badan_kueri_dan_jalur_tidak_mengoersi_diam_diam() -> None:
    salah: list[str] = []
    badan_diperiksa = tanggal_diperiksa = 0
    for rute in _rute():
        nama = f"{sorted(rute.methods)[0]} {rute.path}"
        if rute.body_field is not None:
            badan_diperiksa += 1
            skema = rute.body_field._type_adapter.core_schema
            salah += [f"{nama} badan{t}" for t in _temuan(skema, badan=True)]
        for tempat, p in _parameter(rute):
            skema = p._type_adapter.core_schema
            tanggal_diperiksa += "date" in repr(skema)
            salah += [f"{nama} {tempat} {p.name}{t}" for t in _temuan(skema, badan=False)]

    assert badan_diperiksa >= 12, f"badan yang terbaca: {badan_diperiksa}"
    assert tanggal_diperiksa >= 3, f"parameter bertanggal yang terbaca: {tanggal_diperiksa}"
    assert not salah, "masukan yang dikoersi diam-diam (spec/04, E-170):\n" + "\n".join(salah)


def test_penelusur_mengenali_tipe_longgar() -> None:
    """Penelusurnya sendiri: tipe longgar DITEMUKAN, tipe platform LOLOS."""
    from datetime import date

    from pydantic import TypeAdapter

    assert _temuan(TypeAdapter(int).core_schema, badan=True)
    assert _temuan(TypeAdapter(bool | None).core_schema, badan=True)
    assert _temuan(TypeAdapter(list[date]).core_schema, badan=False)
    assert not _temuan(TypeAdapter(int).core_schema, badan=False)
    assert not _temuan(TypeAdapter(platform.Bulat).core_schema, badan=True)
    assert not _temuan(TypeAdapter(platform.Benar | None).core_schema, badan=True)
    assert not _temuan(TypeAdapter(platform.Tanggal | None).core_schema, badan=True)
    assert not _temuan(TypeAdapter(list[platform.WaktuBerzona]).core_schema, badan=True)
    assert not _temuan(TypeAdapter(platform.AngkaJson).core_schema, badan=True)


# ───────────────────────────────────── tipe-tipe `platform.masukan` sendiri ──


def _diterima(tipe: Any, nilai: object) -> bool:
    from pydantic import TypeAdapter, ValidationError

    try:
        TypeAdapter(tipe).validate_python(nilai)
    except ValidationError:
        return False
    return True


def test_tanggal_hanya_string_iso_dalam_rentang() -> None:
    """Detik Unix → tanggal UTC; `date.min` → `-infinity` di asyncpg (tinjauan Sprint 2)."""
    for salah in (
        1758672000,
        "1758672000",
        "2026-09-24T00:00:00Z",
        "0001-01-01",
        "1899-12-31",
        "9999-12-31",
        "3000-01-01",
        True,
        None,
    ):
        assert not _diterima(platform.Tanggal, salah), f"diterima: {salah!r}"
    for benar in ("1900-01-01", "2026-09-24", "2999-12-31"):
        assert _diterima(platform.Tanggal, benar), f"ditolak: {benar!r}"


def test_waktu_hanya_iso_berzona_dalam_rentang_utc() -> None:
    for salah in (
        1758672000,
        "1758672000",
        "2026-09-24T06:30:00",  # tanpa zona
        "0001-01-01T00:00:00+14:00",  # meluap saat diubah ke UTC
        "9999-12-31T23:59:59-14:00",
        "1899-12-31T23:59:59Z",
        "2026-09-24",
    ):
        assert not _diterima(platform.WaktuBerzona, salah), f"diterima: {salah!r}"
    for benar in ("2026-09-24T06:30:00+07:00", "2026-09-24T06:30:00Z", "1900-01-01T00:00:00Z"):
        assert _diterima(platform.WaktuBerzona, benar), f"ditolak: {benar!r}"


def test_bulat_benar_dan_angka_json_tidak_dikoersi() -> None:
    for tipe, salah in (
        (platform.Bulat, True),
        (platform.Bulat, "3"),
        (platform.Bulat, 3.0),
        (platform.Benar, 1),
        (platform.Benar, "on"),
        (platform.Benar, "true"),
        (platform.AngkaJson, "7.5"),
        (platform.AngkaJson, True),
        (platform.AngkaJson, float("nan")),
    ):
        assert not _diterima(tipe, salah), f"diterima: {salah!r}"
    assert _diterima(platform.Bulat, 3)
    assert _diterima(platform.Benar, False)
    assert _diterima(platform.AngkaJson, 7.5)
