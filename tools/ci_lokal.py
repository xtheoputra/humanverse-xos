#!/usr/bin/env python3
"""CI HumanVerse XOS — SATU sumber urutan tahap, untuk mesin lokal DAN Actions.

spec/07 tugas 0.7: `lint → typecheck → test → build → scan`, dan PR gagal
kalau salah satunya merah.

Kenapa urutannya hidup di sini dan bukan di `.github/workflows/ci.yml`:
pemilik memutuskan CI **tanpa tagihan** (H-26, 17 Sep 2026) — GitHub Actions
untuk repo privat memakai menit berbayar, dan akun ini sudah terhalang
tagihan (#160). Gerbang yang sungguh berjalan adalah mesin pengembang, dan
hasilnya ditempel ke commit sebagai status `ci-lokal` (`--lapor-github`).
Kalau daftar perintahnya ditulis dua kali — sekali di YAML, sekali untuk
lokal — keduanya akan menyimpang tanpa ada yang tahu, persis pola yang
arch/11 §1 daftar enam kali. Karena itu `ci.yml` hanya memanggil berkas ini.

    uv run --locked python tools/ci_lokal.py                 # kelima tahap
    uv run --locked python tools/ci_lokal.py lint typecheck  # sebagian
    uv run --locked python tools/ci_lokal.py --daftar        # cetak perintahnya saja
    uv run --locked python tools/ci_lokal.py --lapor-github  # kelima tahap + status di PR

`--locked` di perintah di atas bukan hiasan: `uv run` biasa MENULIS ULANG
`uv.lock` yang basi sebelum berkas ini sempat memeriksanya.

Tahap `test` butuh HVX_TEST_DATABASE_URL & HVX_TEST_REDIS_URL. Tahap `build`
dan `scan` butuh Docker; `scan` selalu didahului `build` di pemanggilan yang
sama, supaya yang dipindai adalah citra yang baru dibangun dan diuji asap —
bukan tag yang kebetulan sedang ada. Tahap pertama yang merah menghentikan
sisanya.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AKAR = Path(__file__).resolve().parent.parent
PY = sys.executable
# Tag KHUSUS CI — terpisah dari `hvx-api:local` milik tumpukan pengembangan,
# yang bisa berpindah kapan saja oleh `docker compose build` lain.
CITRA = "hvx-api:ci"
TRIVY = (
    "aquasec/trivy:0.74.0@sha256:62b1e65e8869bc4b4c6aa4fa2b21595256c7c2f6018a9d9ad61caf87187c1969"
)
# `uv run` mengisi UV dengan jalur binernya sendiri; di luar itu cari di PATH.
_UV = [os.environ.get("UV") or shutil.which("uv") or "uv"]
# Direktori yang tidak dipindai rahasia: lingkungan terpasang & cache alat.
_LEWATI_PINDAI = [".git", ".venv", "node_modules", ".mypy_cache", ".ruff_cache", ".pytest_cache"]

# Kecuali R-1: enam roadmap fase GAGAL R-1 hari ini, dan mengurutkannya ulang
# adalah keputusan CAKUPAN milik pemilik (#99 #111 #116 #121 #131 #144).
# R-1 dilaporkan, tidak menggagalkan — sama seperti periksa-dokumen.yml.
PERIKSA_WAJIB = [
    "B-6", "M-4", "P-1", "P-2", "P-3", "E-1", "E-2", "E-3", "E-4", "E-5",
    "A-1", "A-2", "A-3", "G-1",
]  # fmt: skip

Langkah = tuple[str, list[str] | Callable[[], int], bool]  # (nama, perintah, wajib)


def _smoke_compose() -> int:
    """Jalankan tumpukan compose penuh DARI CITRA CI, tuntut /health 200, lalu bongkar."""
    proyek = ["docker", "compose", "-p", "hvx-ci-smoke"]
    env = {
        **os.environ,
        "HVX_API_IMAGE": CITRA,
        "HVX_API_PORT": os.environ.get("HVX_CI_API_PORT", "18000"),
        "HVX_POSTGRES_PORT": os.environ.get("HVX_CI_POSTGRES_PORT", "15432"),
        "HVX_REDIS_PORT": os.environ.get("HVX_CI_REDIS_PORT", "16379"),
    }
    try:
        r = subprocess.run(
            [*proyek, "up", "-d", "--no-build", "--wait", "--wait-timeout", "180"],
            cwd=AKAR,
            env=env,
        )
        if r.returncode != 0:
            subprocess.run([*proyek, "logs", "--no-color", "--tail", "80"], cwd=AKAR, env=env)
            return r.returncode
        url = f"http://127.0.0.1:{env['HVX_API_PORT']}/health"
        for _ in range(10):
            try:
                with urllib.request.urlopen(url, timeout=3) as jawab:
                    badan = jawab.read().decode()
                    print(f"  {url} → {jawab.status} {badan}")
                    if jawab.status == 200 and '"status":"ok"' in badan.replace(" ", ""):
                        return 0
            except OSError as galat:
                print(f"  {url} → {galat}")
            time.sleep(2)
        return 1
    finally:
        subprocess.run([*proyek, "down", "-v", "--remove-orphans"], cwd=AKAR, env=env)


def _pip_audit() -> int:
    """Audit dependensi PRODUKSI yang terkunci — bukan lingkungan pengembang.

    🔴 Penanda lingkungan (`; sys_platform != 'win32'`) DIBUANG sebelum audit.
    pip-audit menilai penanda terhadap mesin yang menjalankannya dan membuang
    paket yang tidak cocok TANPA jejak: di mesin Windows, `uvloop` — yang ikut
    ke citra Linux — tidak pernah diaudit.
    """
    with tempfile.TemporaryDirectory() as tmp:
        keluar = Path(tmp) / "persyaratan.txt"
        r = subprocess.run(
            [
                *_UV,
                "export",
                "--locked",
                "--no-dev",
                "--package",
                "hvx-api",
                "--no-emit-workspace",
                "--format",
                "requirements-txt",
                "-o",
                str(keluar),
            ],
            cwd=AKAR,
        )
        if r.returncode != 0:
            return r.returncode
        teks = keluar.read_text(encoding="utf-8")
        keluar.write_text(re.sub(r" ; [^\\\n]*?(?= \\$|$)", "", teks, flags=re.M), encoding="utf-8")
        return subprocess.run(
            [PY, "-m", "pip_audit", "--strict", "--disable-pip", "--no-deps", "-r", str(keluar)],
            cwd=AKAR,
        ).returncode


def _trivy_citra() -> int:
    """Pindai citra CI TANPA memberi pemindai soket Docker.

    🔴 Versi pertama me-mount `/var/run/docker.sock` ke kontainer trivy —
    kendali penuh atas daemon Docker, diberikan kepada citra pihak ketiga yang
    dipatok TAG. Kini citra disimpan ke tar dan diberikan hanya-baca.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tar = Path(tmp) / "citra.tar"
        r = subprocess.run(["docker", "save", CITRA, "-o", str(tar)], cwd=AKAR)
        if r.returncode != 0:
            return r.returncode
        return subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{tmp}:/pindai:ro",
                "-v", "hvx-trivy-cache:/root/.cache/trivy",
                TRIVY, "image", "--input", "/pindai/citra.tar",
                "--exit-code", "1", "--severity", "HIGH,CRITICAL", "--ignore-unfixed",
                "--no-progress",
            ],
            cwd=AKAR,
        ).returncode  # fmt: skip


def perintah_pindai_rahasia(akar: Path) -> list[str]:
    lewati = [a for d in _LEWATI_PINDAI for a in ("--skip-dirs", f"/src/{d}")]
    return [
        "docker", "run", "--rm",
        "-v", f"{akar}:/src:ro",
        "-v", "hvx-trivy-cache:/root/.cache/trivy",
        TRIVY, "fs", "--scanners", "secret", "--exit-code", "1", "--no-progress",
        *lewati, "/src",
    ]  # fmt: skip


TAHAP: dict[str, list[Langkah]] = {
    "lint": [
        ("uv.lock cocok dengan pyproject", [*_UV, "lock", "--check"], True),
        ("ruff check", [PY, "-m", "ruff", "check", "."], True),
        ("ruff format", [PY, "-m", "ruff", "format", "--check", "."], True),
        ("import-linter (M-1 M-2 M-3 B-2)", ["lint-imports", "--no-cache"], True),
        ("periksa_dokumen (wajib hijau)", [PY, "tools/periksa_dokumen.py", *PERIKSA_WAJIB], True),
        ("uji_mutasi dokumen", [PY, "tools/uji_mutasi.py"], True),
        (
            "uji_mutasi kode — tanpa basis data",
            [PY, "tools/uji_mutasi_kode.py", "--tanpa-db"],
            True,
        ),
        (
            "R-1 (dilaporkan, keputusan cakupan pemilik)",
            [PY, "tools/periksa_dokumen.py", "R-1"],
            False,
        ),
    ],
    "typecheck": [
        ("mypy --strict", [PY, "-m", "mypy"], True),
    ],
    "test": [
        ("pytest + cakupan ≥ 70 %", [PY, "-m", "pytest", "--cov", "--cov-report=term"], True),
        ("uji_mutasi kode — migrasi", [PY, "tools/uji_mutasi_kode.py", "--hanya-db"], True),
    ],
    "build": [
        (
            "docker build (citra CI)",
            # --pull: patokan digest diperiksa ulang ke registry
            [
                "docker",
                "build",
                "--pull",
                "-f",
                "infrastructure/docker/api.Dockerfile",
                "-t",
                CITRA,
                ".",
            ],
            True,
        ),
        ("compose up → /health 200", _smoke_compose, True),
    ],
    "scan": [
        ("pip-audit (dependensi produksi, semua platform)", _pip_audit, True),
        ("bandit", [PY, "-m", "bandit", "-q", "-r", "apps/api/src", "-c", "pyproject.toml"], True),
        ("trivy citra (HIGH/CRITICAL yang sudah ada perbaikannya)", _trivy_citra, True),
        ("trivy rahasia di berkas repo", perintah_pindai_rahasia(AKAR), True),
        (
            "uji_mutasi kode — pemindai rahasia",
            [PY, "tools/uji_mutasi_kode.py", "--hanya-docker"],
            True,
        ),
    ],
}


def _jalankan(perintah: list[str] | Callable[[], int]) -> int:
    if callable(perintah):
        return perintah()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(perintah, cwd=AKAR, env=env).returncode


# ──────────────────────────────────────────── laporan status ke GitHub ──
#
# 🔑 Pengganti GitHub Actions yang TIDAK PERNAH menagih (H-26). Gerbangnya
#    berjalan di mesin ini; hasilnya ditempel ke commit sebagai *commit status*
#    `ci-lokal` lewat API GitHub — fitur dasar repo, bukan Actions, jadi tidak
#    memakai menit dan tidak bergantung pada tagihan akun. PR menampilkan
#    hijau/merahnya di samping commit, seperti cek CI biasa.
#
# 🛑 Status hanya bermakna kalau ia menempel pada pohon yang BENAR-BENAR diuji.
#    Maka laporan ditolak untuk gerbang sebagian, pohon kerja yang kotor, dan
#    commit yang belum ada di remote — dan keadaan repo diperiksa ULANG sesudah
#    gerbang selesai, sebab uji mutasi merusak lalu memulihkan berkas di tempat.

KONTEKS_STATUS = "ci-lokal"


def _git(*argumen: str) -> str:
    return subprocess.run(
        ["git", *argumen], cwd=AKAR, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout.strip()


def keadaan_repo() -> tuple[str, str]:
    """(sha HEAD, keluaran `git status --porcelain`) — berkas yang diabaikan git tidak dihitung."""
    return _git("rev-parse", "HEAD"), _git("status", "--porcelain")


def alasan_menolak_lapor(sha: str, kotor: str, sha_remote: str | None, cabang: str) -> str | None:
    """Kenapa hasil gerbang TIDAK boleh ditempel ke `sha` — atau None kalau boleh."""
    if kotor:
        return "pohon kerja kotor — yang diuji bukan isi commit mana pun:\n" + kotor
    if sha_remote != sha:
        return (
            f"{sha[:7]} belum menjadi ujung origin/{cabang} — push dulu, supaya status "
            "menempel pada commit yang dilihat PR"
        )
    return None


def prasyarat_lapor() -> tuple[str, str]:
    """(slug repo `pemilik/nama`, sha HEAD) — atau SystemExit dengan alasannya."""
    sha, kotor = keadaan_repo()
    cabang = _git("rev-parse", "--abbrev-ref", "HEAD")
    remote = _git("ls-remote", "origin", f"refs/heads/{cabang}").split()
    alasan = alasan_menolak_lapor(sha, kotor, remote[0] if remote else None, cabang)
    if alasan:
        raise SystemExit(f"🛑 --lapor-github ditolak: {alasan}")
    slug = subprocess.run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        cwd=AKAR, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.strip()  # fmt: skip
    return slug, sha


def perintah_lapor_status(slug: str, sha: str, keadaan: str, uraian: str) -> list[str]:
    """Batas GitHub untuk `description` 140 karakter — dipotong di sini, bukan ditolak di sana."""
    if keadaan not in {"pending", "success", "failure", "error"}:
        raise ValueError(f"keadaan status tak dikenal: {keadaan}")
    return [
        "gh", "api", "--method", "POST", f"repos/{slug}/statuses/{sha}",
        "-f", f"state={keadaan}",
        "-f", f"context={KONTEKS_STATUS}",
        "-f", f"description={uraian[:140]}",
    ]  # fmt: skip


def lapor_status(slug: str, sha: str, keadaan: str, uraian: str) -> None:
    subprocess.run(
        perintah_lapor_status(slug, sha, keadaan, uraian),
        cwd=AKAR, capture_output=True, text=True, encoding="utf-8", check=True,
    )  # fmt: skip
    print(f"📮 status `{KONTEKS_STATUS}` → {sha[:7]}: {keadaan} — {uraian[:140]}", flush=True)


# ──────────────────────────────────────────────────────────── gerbang ──


def _jalankan_gerbang(pilih: list[str], daftar: bool) -> tuple[int, str | None, int]:
    """(kode keluar, langkah wajib pertama yang merah, jumlah langkah wajib yang hijau)."""
    ringkas: list[tuple[str, str, str]] = []
    hijau = 0
    for tahap in pilih:
        for nama, perintah, wajib in TAHAP[tahap]:
            teks = perintah.__name__ if callable(perintah) else " ".join(perintah)
            if daftar:
                print(f"{tahap:10s} {'wajib ' if wajib else 'lapor '} {nama:52s} {teks}")
                continue
            print(f"\n━━━ {tahap} · {nama}\n    $ {teks}", flush=True)
            mulai = time.monotonic()
            kembali = _jalankan(perintah)
            lama = f"{time.monotonic() - mulai:5.1f} dtk"
            if kembali == 0:
                if wajib:
                    hijau += 1
                ringkas.append((tahap, nama, f"✅ {lama}"))
            elif wajib:
                ringkas.append((tahap, nama, f"🛑 keluar {kembali} · {lama}"))
                _cetak(ringkas)
                return 1, f"{tahap} · {nama}", hijau
            else:
                ringkas.append((tahap, nama, f"⚠️ keluar {kembali} (dilaporkan) · {lama}"))
    if not daftar:
        _cetak(ringkas)
    return 0, None, hijau


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("tahap", nargs="*", help=" · ".join(TAHAP) + " (kosong = semua, berurutan)")
    ap.add_argument("--daftar", action="store_true", help="cetak langkah tanpa menjalankan")
    ap.add_argument(
        "--lapor-github",
        action="store_true",
        help=f"tempel hasil gerbang PENUH ke commit HEAD sebagai status `{KONTEKS_STATUS}` "
        "(gratis — API status commit, bukan Actions)",
    )
    a = ap.parse_args(argv)
    tak_dikenal = [t for t in a.tahap if t not in TAHAP]
    if tak_dikenal:
        ap.error(f"tahap tak dikenal: {' '.join(tak_dikenal)}")
    pilih = [t for t in TAHAP if t in a.tahap] or list(TAHAP)
    if a.lapor_github and (a.daftar or pilih != list(TAHAP)):
        ap.error(
            "--lapor-github hanya untuk gerbang PENUH (kelima tahap, tanpa --daftar): "
            "status hijau dari gerbang sebagian akan terbaca sebagai lulus penuh"
        )
    if "scan" in pilih and "build" not in pilih:
        pilih.insert(pilih.index("scan"), "build")
        print("ℹ️  `scan` didahului `build` — yang dipindai wajib citra yang baru dibangun.")

    lapor = prasyarat_lapor() if a.lapor_github else None
    if lapor:
        lapor_status(*lapor, "pending", "gerbang lint → typecheck → test → build → scan berjalan")
    mulai = time.monotonic()
    selesai = False
    try:
        kembali, merah, hijau = _jalankan_gerbang(pilih, a.daftar)
        selesai = True
    finally:
        if lapor and not selesai:
            lapor_status(*lapor, "error", "gerbang terhenti sebelum selesai — tidak ada hasil")
    if not lapor:
        return kembali

    slug, sha = lapor
    sha_kini, kotor = keadaan_repo()
    if sha_kini != sha or kotor:
        lapor_status(slug, sha, "error", "repo berubah selama gerbang berjalan — hasil tidak sah")
        print("🛑 repo berubah selama gerbang berjalan:\n" + (kotor or f"HEAD kini {sha_kini}"))
        return 1
    menit, detik = divmod(round(time.monotonic() - mulai), 60)
    if kembali == 0:
        lapor_status(slug, sha, "success", f"{hijau} langkah wajib hijau · {menit} mnt {detik} dtk")
    else:
        lapor_status(slug, sha, "failure", f"merah di {merah}")
    return kembali


def _cetak(ringkas: list[tuple[str, str, str]]) -> None:
    print("\n" + "═" * 84)
    for tahap, nama, hasil in ringkas:
        print(f"  {tahap:10s} {nama:56s} {hasil}")
    print("═" * 84)


if __name__ == "__main__":
    sys.exit(main())
