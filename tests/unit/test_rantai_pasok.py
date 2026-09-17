"""Rantai pasok — semua yang ditarik dari luar dipatok ke isi, bukan ke nama.

Tag Docker dan tag aksi GitHub bisa dipindahkan ke isi lain. Itu bukan
kemungkinan teoretis: citra pemindai yang dipakai tahap `scan` repo ini sendiri
pernah diterbitkan ulang di tag lama dengan pencuri kredensial (trivy, Maret
2026, GHSA-69fq-xp46-6x23). SECURITY.md menyatakan aturannya; berkas ini yang
berkata *tidak*.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

AKAR = Path(__file__).resolve().parents[2]
ALUR = sorted((AKAR / ".github" / "workflows").glob("*.yml"))
DIGEST = re.compile(r"@sha256:[0-9a-f]{64}$")
SHA_AKSI = re.compile(r"@[0-9a-f]{40}$")


def _ci_lokal() -> ModuleType:
    nama = "_alat_ci_lokal"
    if nama in sys.modules:
        return sys.modules[nama]
    spec = importlib.util.spec_from_file_location(nama, AKAR / "tools" / "ci_lokal.py")
    assert spec is not None
    assert spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    sys.modules[nama] = modul
    spec.loader.exec_module(modul)
    return modul


def _citra_luar() -> list[tuple[str, str]]:
    """[(asal, rujukan citra)] — setiap citra yang ditarik dari registry."""
    hasil: list[tuple[str, str]] = []
    dockerfile = (AKAR / "infrastructure/docker/api.Dockerfile").read_text(encoding="utf-8")
    tahap = set(re.findall(r"^FROM\s+\S+\s+AS\s+(\S+)", dockerfile, re.M | re.I))
    for m in re.finditer(r"^ARG\s+\w*IMAGE\w*=(\S+)", dockerfile, re.M):
        hasil.append(("api.Dockerfile ARG", m.group(1)))
    for m in re.finditer(r"^FROM\s+(\S+)", dockerfile, re.M | re.I):
        if not m.group(1).startswith("${") and m.group(1) not in tahap:
            hasil.append(("api.Dockerfile FROM", m.group(1)))
    for m in re.finditer(r"COPY\s+--from=(\S+)", dockerfile):
        if m.group(1) not in tahap:
            hasil.append(("api.Dockerfile COPY --from", m.group(1)))
    for berkas in [AKAR / "docker-compose.yml", *ALUR]:
        for m in re.finditer(r"^\s*image:\s*(\S+)", berkas.read_text(encoding="utf-8"), re.M):
            if not m.group(1).startswith("${HVX_API_IMAGE"):  # dibangun sendiri, bukan ditarik
                hasil.append((berkas.name, m.group(1)))
    hasil.append(("tools/ci_lokal.py TRIVY", _ci_lokal().TRIVY))
    return hasil


def test_populasi_citra_tidak_kosong() -> None:
    """Pemeriksa yang tidak menemukan apa pun untuk diperiksa bukan lulus."""
    asal = {a for a, _ in _citra_luar()}
    assert len(_citra_luar()) >= 6, _citra_luar()
    assert {"api.Dockerfile ARG", "api.Dockerfile COPY --from", "docker-compose.yml"} <= asal


def test_tiap_citra_luar_dipatok_digest() -> None:
    tanpa = [f"{asal}: {ref}" for asal, ref in _citra_luar() if not DIGEST.search(ref)]
    assert not tanpa, "citra dipatok TAG, bukan digest:\n" + "\n".join(tanpa)


def test_tiap_aksi_github_dipatok_sha_commit() -> None:
    tanpa = []
    total = 0
    for alur in ALUR:
        for m in re.finditer(r"^\s*-?\s*uses:\s*(\S+)", alur.read_text(encoding="utf-8"), re.M):
            ref = m.group(1)
            if ref.startswith(("./", "docker://")):
                continue
            total += 1
            if not SHA_AKSI.search(ref):
                tanpa.append(f"{alur.name}: {ref}")
    assert total > 0, "tidak ada satu pun `uses:` terbaca — pemeriksa buta"
    assert not tanpa, "aksi dipatok TAG, bukan SHA commit:\n" + "\n".join(tanpa)


def test_checkout_tidak_meninggalkan_token_dan_izin_dibatasi() -> None:
    for alur in ALUR:
        teks = alur.read_text(encoding="utf-8")
        checkout = len(re.findall(r"uses:\s*actions/checkout@", teks))
        tanpa_kredensial = len(re.findall(r"persist-credentials:\s*false", teks))
        assert checkout == tanpa_kredensial, (
            f"{alur.name}: {checkout} checkout, "
            f"{tanpa_kredensial} dengan persist-credentials: false"
        )
        assert re.search(r"^permissions:\s*\n\s+contents:\s*read", teks, re.M), (
            f"{alur.name}: tanpa `permissions: contents: read` di tingkat alur"
        )
