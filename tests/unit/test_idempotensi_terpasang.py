"""spec/04 — tiap rute `POST`/`PATCH` domain menerima `Idempotency-Key` (E-165).

*“`POST`/`PATCH` domain menerima header `Idempotency-Key`”* adalah janji
kontrak API, dan janji yang ditepati satu rute demi satu rute akan dilupakan
di rute berikutnya. Uji ini membaca skema OpenAPI aplikasi yang SUNGGUH dirakit
`hvx.main` — kontrak yang diterbitkan, bukan susunan dalam FastAPI — jadi rute
baru yang lupa menyatakan `idem: platform.Idempoten` gagal di sini.

🔴 Versi pertama menelusuri `app.routes` mencari `APIRoute`, dan FastAPI 0.141
menyimpan rute ber-`include_router` sebagai `_IncludedRouter`: uji itu membaca
NOL rute tulis. Syarat populasi di bawah (`>= 4`) yang menangkapnya.
"""

from __future__ import annotations

from collections.abc import Iterator

from hvx.main import create_app
from hvx.modules import platform
from hvx.modules.platform import Settings

# Rute tulis domain yang sengaja TANPA Idempotency-Key — satu alasan per baris.
TANPA_IDEMPOTENSI: dict[tuple[str, str], str] = {
    ("PATCH", "/v1/me/profile"): "idempoten dengan sendirinya — spec/04",
}
# K-21: jawaban /auth/* memuat token; memutar ulangnya = menyimpan token mentah.
AWALAN_AUTH = "/v1/auth/"


def _operasi_tulis() -> Iterator[tuple[str, str, set[str]]]:
    """(metode, jalur, nama header yang diterima) tiap operasi POST/PATCH di bawah /v1."""
    app = create_app(Settings(database_url="postgresql://x", redis_url="redis://x", env="test"))
    for jalur, operasi in app.openapi()["paths"].items():
        for metode, isi in operasi.items():
            if metode.upper() in {"POST", "PATCH"} and jalur.startswith("/v1/"):
                header = {p["name"] for p in isi.get("parameters", []) if p["in"] == "header"}
                yield metode.upper(), jalur, header


def test_tiap_rute_tulis_domain_menerima_idempotency_key() -> None:
    domain = [
        (m, p, h)
        for m, p, h in _operasi_tulis()
        if not p.startswith(AWALAN_AUTH) and (m, p) not in TANPA_IDEMPOTENSI
    ]
    tanpa = [f"{m} {p}" for m, p, h in domain if platform.HEADER_KUNCI not in h]

    assert len(domain) >= 4, f"rute tulis domain yang terbaca: {[(m, p) for m, p, _ in domain]}"
    assert not tanpa, (
        "rute tulis domain tanpa `idem: platform.Idempoten` (spec/04, E-165):\n" + "\n".join(tanpa)
    )


def test_rute_auth_tidak_memutar_ulang_jawaban_bertoken() -> None:
    bertoken = [
        f"{m} {p}"
        for m, p, h in _operasi_tulis()
        if p.startswith(AWALAN_AUTH) and platform.HEADER_KUNCI in h
    ]
    auth = [p for _m, p, _h in _operasi_tulis() if p.startswith(AWALAN_AUTH)]

    assert len(auth) >= 3, f"rute /auth yang terbaca: {auth}"
    assert not bertoken, (
        f"/auth/* memakai Idempotency-Key — menyimpan token mentah (K-21): {bertoken}"
    )


def test_pengecualian_masih_menunjuk_rute_yang_ada() -> None:
    ada = {(m, p) for m, p, _ in _operasi_tulis()}
    basi = sorted(set(TANPA_IDEMPOTENSI) - ada)
    assert not basi, f"pengecualian untuk rute yang tidak ada lagi: {basi}"
