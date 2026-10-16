"""arch/11 §6 — tiap pemeriksaan punya penegak yang NYATA, atau pemicu yang disebut namanya.

Pelajaran yang membuat berkas ini ada (arch/11 §1): aturan yang dinyatakan
tetapi tidak dijaga akan dilanggar. Blok ```penegak adalah pernyataan; uji ini
yang berkata *tidak* ketika pernyataannya berhenti benar — kontrak yang
diganti nama, pemeriksaan yang dicabut dari CI, atau kontrak baru yang tidak
pernah dicatat.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path
from types import ModuleType

AKAR = Path(__file__).resolve().parents[2]
ARCH11 = AKAR / "arch" / "11-PENEGAKAN.md"


def _modul(nama: str) -> ModuleType:
    nama_modul = f"_alat_{nama}"
    if nama_modul in sys.modules:
        return sys.modules[nama_modul]
    spec = importlib.util.spec_from_file_location(nama_modul, AKAR / "tools" / f"{nama}.py")
    assert spec is not None
    assert spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    # @dataclass mencari modulnya di sys.modules saat kelas dibuat.
    sys.modules[nama_modul] = modul
    spec.loader.exec_module(modul)
    return modul


def _blok_penegak() -> dict[str, tuple[str, list[str], str]]:
    teks = ARCH11.read_text(encoding="utf-8")
    m = re.search(r"```penegak\n(.*?)```", teks, re.S)
    assert m, "arch/11 tanpa blok ```penegak — peta penegak hilang"
    baris: dict[str, tuple[str, list[str], str]] = {}
    for b in m.group(1).splitlines():
        if not b.strip() or b.startswith("#"):
            continue
        kode, status, sisa = b.split(maxsplit=2) if len(b.split()) > 2 else (*b.split(), "")
        token = sisa.split()
        penegak = [t for t in token if t.startswith(("import-linter:", "periksa_dokumen:"))]
        catatan = " ".join(t for t in token if t not in penegak and t != "—")
        assert kode not in baris, f"{kode} muncul dua kali di blok penegak"
        baris[kode] = (status, penegak, catatan)
    return baris


def _kode_bagian3() -> set[str]:
    teks = ARCH11.read_text(encoding="utf-8")
    bagian3 = teks.split("## §3", 1)[1].split("## §4", 1)[0]
    return set(re.findall(r"^\| \*\*([BMPEAGR]-\d)\*\*", bagian3, re.M))


def _kontrak_import_linter() -> set[str]:
    konfig = tomllib.loads((AKAR / "pyproject.toml").read_text(encoding="utf-8"))
    return {k["id"] for k in konfig["tool"]["importlinter"]["contracts"]}


def test_blok_penegak_memuat_tepat_himpunan_pemeriksaan_bagian3() -> None:
    kode3 = _kode_bagian3()
    blok = set(_blok_penegak())

    assert len(kode3) == 26, f"§3 memuat {len(kode3)} pemeriksaan, bukan 26"
    assert blok == kode3, (
        f"tanpa baris: {sorted(kode3 - blok)} · tak dikenal: {sorted(blok - kode3)}"
    )


def test_status_hanya_jalan_atau_menunggu_dengan_pemicu() -> None:
    for kode, (status, penegak, catatan) in _blok_penegak().items():
        assert status in {"JALAN", "MENUNGGU"}, f"{kode}: status `{status}`"
        if status == "JALAN":
            assert penegak, f"{kode} JALAN tanpa penegak"
        else:
            assert not penegak, f"{kode} MENUNGGU tetapi menyebut penegak {penegak}"
            assert catatan, f"{kode} MENUNGGU tanpa pemicu yang disebut namanya"


def test_tiap_kontrak_import_linter_yang_disebut_ada_dan_tidak_ada_yang_yatim() -> None:
    ada = _kontrak_import_linter()
    disebut = {
        p.split(":", 1)[1]
        for _s, penegak, _c in _blok_penegak().values()
        for p in penegak
        if p.startswith("import-linter:")
    }

    assert disebut <= ada, f"disebut tetapi tidak ada di pyproject.toml: {sorted(disebut - ada)}"
    assert ada <= disebut, f"kontrak yatim — tidak dicatat di arch/11: {sorted(ada - disebut)}"


def test_tiap_pemeriksaan_dokumen_yang_disebut_ada_dan_dijalankan_ci() -> None:
    periksa = _modul("periksa_dokumen")
    ci = _modul("ci_lokal")
    # Kode yang diberikan kepada periksa_dokumen.py oleh sebuah langkah CI —
    # dipisah menurut apakah langkahnya WAJIB (merah = CI gagal) atau hanya
    # dilaporkan. 🔴 Versi pertama menggabungkan keduanya: memindahkan G-1 ke
    # langkah R-1 yang hanya-dilaporkan membuatnya "dijalankan CI" tetapi tidak
    # pernah bisa menggagalkannya, dan uji ini tetap hijau.
    wajib_ci: set[str] = set()
    lapor_ci: set[str] = set()
    for tahap in ci.TAHAP.values():
        for _nama, perintah, wajib in tahap:
            if isinstance(perintah, list) and "tools/periksa_dokumen.py" in perintah:
                kode = set(perintah[perintah.index("tools/periksa_dokumen.py") + 1 :])
                (wajib_ci if wajib else lapor_ci).update(kode)
    dijalankan_ci = wajib_ci | lapor_ci
    disebut = {
        p.split(":", 1)[1]
        for _s, penegak, _c in _blok_penegak().values()
        for p in penegak
        if p.startswith("periksa_dokumen:")
    }

    assert disebut <= set(periksa.PEMERIKSAAN), sorted(disebut - set(periksa.PEMERIKSAAN))
    assert set(periksa.PEMERIKSAAN) <= disebut, (
        f"pemeriksaan tanpa baris penegak: {sorted(set(periksa.PEMERIKSAAN) - disebut)}"
    )
    assert disebut <= dijalankan_ci, (
        f"ada di periksa_dokumen.py tetapi tidak dijalankan tools/ci_lokal.py: "
        f"{sorted(disebut - dijalankan_ci)}"
    )
    diturunkan = (disebut - wajib_ci) - BOLEH_DILAPORKAN
    assert not diturunkan, f"hanya dilaporkan: {sorted(diturunkan)}"
    assert lapor_ci <= BOLEH_DILAPORKAN, f"hanya dilaporkan: {sorted(lapor_ci - BOLEH_DILAPORKAN)}"


# R-1 merah karena keputusan CAKUPAN pemilik (arch/11 §4) — satu-satunya
# pemeriksaan yang boleh dijalankan CI tanpa menggagalkannya.
BOLEH_DILAPORKAN = frozenset({"R-1"})


def test_lint_imports_adalah_langkah_wajib() -> None:
    ci = _modul("ci_lokal")
    langkah = [
        wajib
        for tahap in ci.TAHAP.values()
        for _n, perintah, wajib in tahap
        if isinstance(perintah, list) and perintah and perintah[0] == "lint-imports"
    ]
    assert langkah == [True], f"lint-imports di CI: {langkah} — wajib tepat satu langkah wajib"


def _kontrak() -> list[dict[str, object]]:
    return list(
        tomllib.loads((AKAR / "pyproject.toml").read_text(encoding="utf-8"))["tool"][
            "importlinter"
        ]["contracts"]
    )


def test_tiap_kontrak_import_linter_punya_mutasi_yang_menyasar_idnya() -> None:
    """Per id kontrak, bukan per kode arch/11 — satu mutasi M-2 semula dianggap
    membuktikan kedua belas kontrak M-2."""
    disasar = set()
    for m in _modul("uji_mutasi_kode").MUTASI:
        if "--contract" in m.perintah:
            disasar.add(m.perintah[m.perintah.index("--contract") + 1])
    ada = {str(k["id"]) for k in _kontrak()}

    assert ada <= disasar, (
        f"kontrak tanpa mutasi yang membuktikan merahnya: {sorted(ada - disasar)}"
    )


def test_modul_di_disk_sama_dengan_lapisan_dan_kontrak_pintu_keluar() -> None:
    """Modul baru yang tidak dicatat di kontrak = modul tanpa batas."""
    di_disk = {
        d.name
        for d in (AKAR / "apps/api/src/hvx/modules").iterdir()
        if d.is_dir() and not d.name.startswith(("_", "."))
    }
    lapisan = next(k for k in _kontrak() if k["id"] == "m1-m3-lapisan")
    di_lapisan = {nama.strip() for baris in lapisan["layers"] for nama in str(baris).split("|")}
    di_m2 = {str(k["id"]).removeprefix("m2-") for k in _kontrak() if str(k["id"]).startswith("m2-")}

    assert lapisan.get("exhaustive") is True, "kontrak lapisan tanpa `exhaustive = true`"
    assert di_disk == di_lapisan, f"disk ≠ lapisan: {sorted(di_disk ^ di_lapisan)}"
    assert di_disk == di_m2, f"disk ≠ kontrak M-2: {sorted(di_disk ^ di_m2)}"


def test_tiap_penegak_yang_jalan_terbukti_sanggup_gagal() -> None:
    """Pemeriksaan yang tidak pernah merah tidak dihitung ada (arch/11 §2)."""
    dokumen = {kode for kode, *_ in _modul("uji_mutasi").MUTASI} | {
        kode for kode, *_ in _modul("uji_mutasi").MUTASI_DIREKTORI
    }
    kode = {m.kode for m in _modul("uji_mutasi_kode").MUTASI}
    termutasi = dokumen | kode

    jalan = {k for k, (s, _p, _c) in _blok_penegak().items() if s == "JALAN"}

    assert jalan <= termutasi, (
        f"JALAN tanpa mutasi yang membuktikan merahnya: {sorted(jalan - termutasi)}"
    )


def test_alasan_mutasi_pytest_hanya_dibaca_dari_baris_galat() -> None:
    """🔴 Tinjauan Sprint 1: pytest mencetak SUMBER uji sampai baris yang gagal — pesan
    `assert` yang LULUS ikut tercetak, dan galat lingkungan sesudahnya terhitung
    "berbunyi dengan alasan yang dimaksud"."""
    alat = _modul("uji_mutasi_kode")
    uji = alat.Mutasi("x", "x", [], [sys.executable, "-m", "pytest", "t.py"], "pesan dimaksud")
    hanya_sumber = '>       assert lolos, "pesan dimaksud"\nE       ConnectionError: redis mati\n'

    assert not alat.alasan_terbaca(uji, hanya_sumber), "pesan di sumber uji terhitung alasan galat"
    assert alat.alasan_terbaca(uji, "E       AssertionError: pesan dimaksud\n")
    # alat selain pytest tidak punya baris `E` — seluruh keluarannya dibaca
    lint = alat.Mutasi("x", "x", [], ["lint-imports"], "hvx.main -> hvx.modules.goals._dalam")
    assert alat.alasan_terbaca(lint, "Broken: hvx.main -> hvx.modules.goals._dalam (l.3)")
