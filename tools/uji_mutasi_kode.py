#!/usr/bin/env python3
"""Uji mutasi untuk penegak yang membaca KODE — kontrak `import-linter`, larangan
ruff, peta penegak `arch/11` §6, dan uji integrasi migrasi. Kembaran
`uji_mutasi.py` (yang membaca dokumen).

Alasannya sama, dan diulang karena ia yang membuat keduanya perlu ada:

    Kontrak yang "KEPT" tidak berarti apa pun sampai tiap kontrak terbukti
    SANGGUP "BROKEN". Kontrak `protected` dengan pola yang tidak cocok dengan
    modul mana pun, atau lapisan yang salah eja, memulangkan KEPT dengan tenang.

Cara kerjanya: rusak SATU hal yang sebuah penegak klaim tangkap (sisipkan
impor terlarang, buat siklus, ubah satu kolom migrasi), jalankan penegak itu
saja, tuntut ia gagal DENGAN ALASAN YANG DIMAKSUD, lalu kembalikan semuanya
byte demi byte — termasuk bila prosesnya gagal di tengah.

    uv run python tools/uji_mutasi_kode.py              # semua
    uv run python tools/uji_mutasi_kode.py --tanpa-db   # tanpa mutasi migrasi (tahap lint)
    uv run python tools/uji_mutasi_kode.py --hanya-db   # hanya mutasi migrasi (tahap test)
    uv run python tools/uji_mutasi_kode.py --hanya-docker   # hanya pemindai rahasia (tahap scan)

Mutasi migrasi butuh `HVX_TEST_DATABASE_URL`. Tanpa itu — dan tanpa
`--tanpa-db` yang MENYATAKAN bahwa bagian itu tidak dijalankan — berkas ini
keluar 1: bagian yang tidak dijalankan tidak boleh terbaca sebagai lulus.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AKAR = Path(__file__).resolve().parent.parent
MODUL = "apps/api/src/hvx/modules"
MIGRASI = "data/migrations/versions"
UJI_MIGRASI = "tests/integration/test_migrasi.py"
NL = "\n"


@dataclass
class Sunting:
    """Satu perubahan pada satu berkas. `lama=None` berarti berkas BARU."""

    berkas: str
    lama: str | None
    baru: str


@dataclass
class Mutasi:
    kode: str
    maksud: str
    suntingan: list[Sunting]
    perintah: list[str]
    # Kode keluar 1 saja tidak cukup: uji yang gagal karena galat lingkungan
    # juga keluar 1. Keluarannya WAJIB memuat alasan yang dimaksud mutasi.
    harus_memuat: str
    kode_tertangkap: set[int] = field(default_factory=lambda: {1})
    # lint (bawaan) · db (butuh HVX_TEST_DATABASE_URL) · docker (butuh daemon Docker)
    kelompok: str = "lint"


def _lint(kontrak: str) -> list[str]:
    return ["lint-imports", "--no-cache", "--contract", kontrak]


def _pytest(nodeid: str) -> list[str]:
    return [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", nodeid]


def _ruff(berkas: str) -> list[str]:
    return [sys.executable, "-m", "ruff", "check", "--no-cache", "--select", "TID251", berkas]


def _pindai_rahasia() -> list[str]:
    """Perintah pemindai rahasia DIAMBIL dari tools/ci_lokal.py — bukan disalin."""
    sys.path.insert(0, str(AKAR / "tools"))
    try:
        from ci_lokal import perintah_pindai_rahasia
    finally:
        sys.path.pop(0)
    return perintah_pindai_rahasia(AKAR)


def _sisip(berkas: str, baris: str) -> Sunting:
    return Sunting(berkas, "", NL + baris + NL)


def _mutasi_m2() -> list[Mutasi]:
    """Satu mutasi per modul, DARI ISI DIREKTORI — bukan dari pola kontraknya.

    🔴 Versi pertama hanya membuktikan 2 dari 12 kontrak M-2, dan uji peta
    penegak menghitungnya per KODE (M-2), bukan per id kontrak. Kontrak
    `protected` yang polanya salah eja (`hvx.modules.gaols.*`) tetap KEPT
    sambil pelanggaran nyata terjadi — diukur di tinjauan Sprint 0. Nama modul
    diambil dari direktori, supaya salah eja di kontrak tidak ikut tersalin ke
    mutasinya.
    """
    hasil = []
    for d in sorted((AKAR / MODUL).iterdir()):
        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue
        hasil.append(
            Mutasi(
                "M-2",
                f"hvx.main masuk ke `{d.name}` lewat berkas dalam",
                [
                    Sunting(f"{MODUL}/{d.name}/_mutasi_dalam.py", None, '"""sementara."""' + NL),
                    _sisip(
                        "apps/api/src/hvx/main.py",
                        f"from hvx.modules.{d.name} import _mutasi_dalam  # noqa",
                    ),
                ],
                _lint(f"m2-{d.name}"),
                harus_memuat=f"hvx.main -> hvx.modules.{d.name}._mutasi_dalam",
            )
        )
    return hasil


TRIGGER_HABITS = (
    "CREATE TRIGGER habits_set_updated_at            BEFORE UPDATE ON habits"
    "            FOR EACH ROW EXECUTE FUNCTION set_updated_at();"
)
UJI_KEPEMILIKAN = "tests/integration/test_kepemilikan_data.py"
FK_MILESTONE = (
    "  FOREIGN KEY (goal_id, user_id) REFERENCES goals (id, user_id) ON DELETE CASCADE" + NL + ");"
)
RLS_JURNAL = "ALTER TABLE journal_entries         ENABLE ROW LEVEL SECURITY;" + NL
KEBIJAKAN_MEMORI = "ON memories                USING (user_id = app_current_user_id())"
GRANT_AGENT_RUNS = "GRANT SELECT, INSERT, UPDATE ON agent_runs TO hvx_app;"

MUTASI: list[Mutasi] = [
    # ── import-linter: lapisan & siklus ──────────────────────────────────
    Mutasi(
        "M-1",
        "platform (lapisan terbawah) mengimpor agents",
        [_sisip(f"{MODUL}/platform/config.py", "from hvx.modules import agents  # noqa")],
        _lint("m1-m3-lapisan"),
        harus_memuat="hvx.modules.platform is not allowed to import hvx.modules.agents",
    ),
    Mutasi(
        "M-3",
        "modul domain mengimpor modul domain lain",
        [_sisip(f"{MODUL}/habits/__init__.py", "from hvx.modules import goals  # noqa")],
        _lint("m1-m3-lapisan"),
        harus_memuat="hvx.modules.habits -> hvx.modules.goals",
    ),
    Mutasi(
        "M-1",
        "modul ke-13 yang tidak diberi lapisan",
        [
            Sunting(
                f"{MODUL}/_modul_baru/__init__.py",
                None,
                "from hvx.modules import agents, habits  # noqa" + NL,
            )
        ],
        _lint("m1-m3-lapisan"),
        harus_memuat="_modul_baru",
    ),
    Mutasi(
        "M-1",
        "impor melingkar di dalam satu modul",
        [
            Sunting(f"{MODUL}/platform/_siklus_a.py", None, "from . import _siklus_b  # noqa" + NL),
            Sunting(f"{MODUL}/platform/_siklus_b.py", None, "from . import _siklus_a  # noqa" + NL),
        ],
        _lint("m1-siklus-dalam"),
        harus_memuat="_siklus_",
    ),
    # ── import-linter: pintu keluar modul (satu per kontrak) ─────────────
    *_mutasi_m2(),
    # ── B-2: jalur keluar ────────────────────────────────────────────────
    Mutasi(
        "B-2",
        "modul domain mengimpor klien HTTP sendiri",
        [_sisip(f"{MODUL}/identity/__init__.py", "import httpx  # noqa")],
        _lint("b2-jalur-keluar"),
        harus_memuat="hvx.modules.identity -> httpx",
    ),
    Mutasi(
        "B-2",
        "klien jaringan bawaan Python di modul domain",
        [_sisip(f"{MODUL}/goals/__init__.py", "import urllib.request  # noqa")],
        _lint("b2-jalur-keluar"),
        harus_memuat="hvx.modules.goals -> urllib",
    ),
    Mutasi(
        "B-2",
        "berkas baru di luar hvx.modules mengimpor klien HTTP",
        [Sunting("apps/api/src/hvx/_pekerja_baru.py", None, "import httpx  # noqa" + NL)],
        _lint("b2-jalur-keluar"),
        harus_memuat="hvx._pekerja_baru -> httpx",
    ),
    Mutasi(
        "B-2",
        "impor dinamis yang tidak terlihat graf impor (ruff)",
        [
            Sunting(
                f"{MODUL}/journal/_dinamis.py",
                None,
                "from importlib import import_module"
                + NL
                + NL
                + "klien = import_module('httpx')"
                + NL,
            )
        ],
        _ruff(f"{MODUL}/journal/_dinamis.py"),
        harus_memuat="TID251",
    ),
    # ── spec/06 aturan 5: SQL modul hanya menyebut tabel miliknya ────────
    Mutasi(
        "06.5",
        "repository identity menyebut tabel milik modul goals",
        [
            _sisip(
                f"{MODUL}/identity/repository.py",
                '_KUERI_LIAR = "SELECT id FROM goals WHERE user_id = :u"',
            )
        ],
        _pytest("tests/unit/test_batas_tabel.py"),
        harus_memuat="`identity` menyebut `goals`",
    ),
    # ── sesi (spec/07 1.2): dicabut → 401 seketika ───────────────────────
    Mutasi(
        "1.2",
        "cabut sesi lupa menghapus token akses — hidup sampai kedaluwarsa",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "            p.delete("
                + NL
                + '                self._k_akses(catatan["akses"]),'
                + NL,
                "            p.delete(" + NL,
            )
        ],
        _pytest("tests/integration/test_sesi.py::test_sesi_dicabut_401_seketika"),
        harus_memuat="assert 200 == 401",
        kelompok="db",
    ),
    Mutasi(
        "1.3",
        "timezone profil diterima sebagai teks bebas — 'Mars/Olympus_Mons' tersimpan",
        [
            Sunting(
                f"{MODUL}/profile/schemas.py",
                "    timezone: platform.ZonaWaktuIANA | None = None",
                "    timezone: str | None = None",
            )
        ],
        _pytest("tests/integration/test_profil.py::test_timezone_bukan_iana_ditolak_400"),
        harus_memuat="assert 200 == 400",
        kelompok="db",
    ),
    Mutasi(
        "1.4",
        "pembatasan tujuan lupa memeriksa cakupan data — persetujuan 'habits' meloloskan 'journal'",
        [
            Sunting(
                f"{MODUL}/identity/persetujuan.py",
                "if not (diberikan and masih_berlaku and cakupan <= cakupan_disetujui):",
                "if not (diberikan and masih_berlaku):",
            )
        ],
        _pytest(
            "tests/integration/test_persetujuan.py"
            "::test_tujuan_dan_cakupan_harus_tercakup_persetujuan_terakhir"
        ),
        harus_memuat="assert not True",
        kelompok="db",
    ),
    # ── identity (spec/07 1.1): argon2id · rotasi · fungsi SECURITY DEFINER ─
    Mutasi(
        "1.1",
        "sandi di-hash argon2i, bukan argon2id",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                "_hasher = PasswordHasher()",
                "_hasher = PasswordHasher(type=__import__('argon2').Type.I)",
            )
        ],
        _pytest("tests/unit/test_sandi.py::test_hash_adalah_argon2id_dan_bisa_diverifikasi"),
        harus_memuat="startswith",
    ),
    Mutasi(
        "1.1",
        "token segar dibaca GET, bukan GETDEL — token lama tetap hidup sesudah rotasi",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "nilai = await self._r.getdel(self._k_segar(lama))",
                "nilai = await self._r.get(self._k_segar(lama))",
            )
        ],
        _pytest(
            "tests/integration/test_auth.py::test_segarkan_merotasi_dan_token_bekas_mencabut_sesi"
        ),
        harus_memuat="assert 200 == 401",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "EXECUTE fungsi login tidak dicabut dari PUBLIC (spec/01 DAN migrasi)",
        [
            Sunting(
                berkas, "REVOKE ALL ON FUNCTION auth_lookup_for_login(citext) FROM PUBLIC;" + NL, ""
            )
            for berkas in ("spec/01-DATABASE-SCHEMA.md", f"{MIGRASI}/0003_pencarian_masuk.up.sql")
        ],
        _pytest(
            f"{UJI_KEPEMILIKAN}"
            "::test_fungsi_security_definer_hanya_daftar_izin_terpatok_dan_bukan_untuk_public"
        ),
        harus_memuat="public_boleh=True",
        kelompok="db",
    ),
    # ── peta penegak arch/11 §6 ──────────────────────────────────────────
    Mutasi(
        "§6",
        "kontrak import-linter tidak dicatat di blok penegak",
        [
            Sunting(
                "arch/11-PENEGAKAN.md",
                "B-2     JALAN       import-linter:b2-jalur-keluar" + NL,
                "B-2     MENUNGGU    —                                                dicabut uji mutasi"
                + NL,
            )
        ],
        _pytest("tests/unit/test_penegak.py"),
        harus_memuat="kontrak yatim",
    ),
    Mutasi(
        "§6",
        "pemeriksaan wajib diturunkan jadi hanya-dilaporkan",
        [
            Sunting("tools/ci_lokal.py", '"A-1", "A-2", "A-3", "G-1",', '"A-1", "A-2", "A-3",'),
            Sunting(
                "tools/ci_lokal.py",
                '[PY, "tools/periksa_dokumen.py", "R-1"],',
                '[PY, "tools/periksa_dokumen.py", "R-1", "G-1"],',
            ),
        ],
        _pytest("tests/unit/test_penegak.py"),
        harus_memuat="hanya dilaporkan: ['G-1']",
    ),
    Mutasi(
        "§6",
        "pemeriksaan dokumen dicabut dari CI",
        [Sunting("tools/ci_lokal.py", '"A-1", "A-2", "A-3", "G-1",', '"A-1", "A-2", "A-3",')],
        _pytest("tests/unit/test_penegak.py"),
        harus_memuat="tidak dijalankan tools/ci_lokal.py: ['G-1']",
    ),
    # ── rantai pasok & kunci dependensi ──────────────────────────────────
    Mutasi(
        "RP",
        "citra dasar dipatok TAG, bukan digest",
        [
            Sunting(
                "infrastructure/docker/api.Dockerfile",
                "ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:",
                "ARG PYTHON_IMAGE=python:3.12-slim-bookworm  # @sha256:",
            )
        ],
        _pytest("tests/unit/test_rantai_pasok.py"),
        harus_memuat="citra dipatok TAG, bukan digest",
    ),
    Mutasi(
        "RP",
        "aksi GitHub dipatok TAG, bukan SHA commit",
        [
            Sunting(
                ".github/workflows/periksa-dokumen.yml",
                "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0",
                "actions/setup-python@v7",
            )
        ],
        _pytest("tests/unit/test_rantai_pasok.py"),
        harus_memuat="aksi dipatok TAG, bukan SHA commit",
    ),
    Mutasi(
        "RP",
        "pemicu otomatis Actions dinyalakan lagi — tiap PR menagih (H-26)",
        [
            Sunting(
                ".github/workflows/ci.yml",
                "on:" + NL + "  workflow_dispatch:" + NL,
                "on:" + NL + "  pull_request:" + NL + "  workflow_dispatch:" + NL,
            )
        ],
        _pytest("tests/unit/test_rantai_pasok.py"),
        harus_memuat="pemicu otomatis ['pull_request', 'workflow_dispatch']",
    ),
    Mutasi(
        "RP",
        "dependensi diubah tanpa mengunci ulang uv.lock",
        [
            Sunting(
                "apps/api/pyproject.toml",
                '  "structlog>=24.4",',
                '  "structlog>=24.4",' + NL + '  "six>=1.16",',
            )
        ],
        [os.environ.get("UV") or shutil.which("uv") or "uv", "lock", "--check"],
        harus_memuat="needs to be updated",
    ),
    Mutasi(
        "RP",
        "token rahasia tertanam di berkas repo",
        [
            Sunting(
                "apps/api/src/hvx/_rahasia_mutasi.py",
                None,
                # Disusun saat berjalan: literal token di berkas INI akan membuat
                # pemindai rahasia menuduh perkakasnya sendiri.
                "TOKEN = '" + "ghp_" + (uuid.uuid4().hex + uuid.uuid4().hex)[:36] + "'" + NL,
            )
        ],
        _pindai_rahasia(),
        harus_memuat="github-pat",
        kelompok="docker",
    ),
    # ── uji integrasi migrasi (butuh basis data) ─────────────────────────
    Mutasi(
        "0.4",
        "migrasi menyimpang satu kolom dari spec/01",
        [
            Sunting(
                f"{MIGRASI}/0001_v0_skema.up.sql",
                "  display_name text NOT NULL,",
                "  display_name text,",
            )
        ],
        _pytest(f"{UJI_MIGRASI}::test_migrasi_menghasilkan_skema_yang_sama_persis_dengan_spec01"),
        harus_memuat="hanya di spec/01 : ('profiles', 3, 'display_name'",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "pemicu dimatikan di migrasi — katalog pertama buta terhadapnya",
        [
            Sunting(
                f"{MIGRASI}/0001_v0_skema.up.sql",
                TRIGGER_HABITS,
                TRIGGER_HABITS + NL + "ALTER TABLE habits DISABLE TRIGGER habits_set_updated_at;",
            )
        ],
        _pytest(f"{UJI_MIGRASI}::test_migrasi_menghasilkan_skema_yang_sama_persis_dengan_spec01"),
        harus_memuat="habits_set_updated_at",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "hak akses kolom ditambahkan di migrasi",
        [
            Sunting(
                f"{MIGRASI}/0001_v0_skema.up.sql",
                "REVOKE UPDATE, DELETE ON audit_logs FROM PUBLIC;",
                "REVOKE UPDATE, DELETE ON audit_logs FROM PUBLIC;"
                + NL
                + "GRANT UPDATE (metadata) ON audit_logs TO PUBLIC;",
            )
        ],
        _pytest(f"{UJI_MIGRASI}::test_migrasi_menghasilkan_skema_yang_sama_persis_dengan_spec01"),
        harus_memuat="hak_akses_kolom",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "turun meninggalkan fungsi set_updated_at",
        [Sunting(f"{MIGRASI}/0001_v0_skema.down.sql", "DROP FUNCTION set_updated_at();", "")],
        _pytest(
            f"{UJI_MIGRASI}::test_migrasi_turun_kembali_ke_basis_data_kosong_lalu_naik_lagi_identik"
        ),
        harus_memuat="turun meninggalkan fungsi",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "tabel ber-updated_at tanpa pemicu (spec/01 DAN migrasi)",
        [
            Sunting("spec/01-DATABASE-SCHEMA.md", TRIGGER_HABITS + NL, ""),
            Sunting(f"{MIGRASI}/0001_v0_skema.up.sql", TRIGGER_HABITS + NL, ""),
        ],
        _pytest(f"{UJI_MIGRASI}::test_tiap_tabel_ber_updated_at_punya_pemicunya"),
        harus_memuat="tanpa pemicu yang benar: ['habits']",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "pemicu AFTER — ada, tetapi tidak memperbarui apa pun (spec/01 DAN migrasi)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                TRIGGER_HABITS,
                TRIGGER_HABITS.replace("BEFORE UPDATE", "AFTER UPDATE "),
            ),
            Sunting(
                f"{MIGRASI}/0001_v0_skema.up.sql",
                TRIGGER_HABITS,
                TRIGGER_HABITS.replace("BEFORE UPDATE", "AFTER UPDATE "),
            ),
        ],
        _pytest(f"{UJI_MIGRASI}::test_tiap_tabel_ber_updated_at_punya_pemicunya"),
        harus_memuat="tanpa pemicu yang benar: ['habits']",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "tabel migrasi yang tidak terbaca parser P-1..P-3",
        [
            Sunting(
                f"{MIGRASI}/0001_v0_skema.up.sql",
                "-- dipakai semua tabel yang punya updated_at",
                # Nama berkutip dengan spasi: ejaan sah yang pola kepala tabel
                # tidak baca — sengaja, supaya ujinya membuktikan pembanding
                # KATALOG, bukan kelonggaran regex.
                'CREATE TABLE "catatan liar" (id uuid PRIMARY KEY);'
                + NL
                + NL
                + "-- dipakai semua tabel yang punya updated_at",
            ),
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "CREATE EXTENSION IF NOT EXISTS citext;",
                "CREATE EXTENSION IF NOT EXISTS citext;"
                + NL
                + 'CREATE TABLE "catatan liar" (id uuid PRIMARY KEY);',
            ),
        ],
        _pytest(f"{UJI_MIGRASI}::test_parser_ddl_membaca_tepat_tabel_yang_ada_di_katalog"),
        harus_memuat="catatan liar",
        kelompok="db",
    ),
    Mutasi(
        "0.4",
        "pagar ```sql spec/01 kembali tidak ditutup",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "  ON agents (name) WHERE status = 'active';" + NL + "```" + NL,
                "  ON agents (name) WHERE status = 'active';" + NL,
            )
        ],
        _pytest(f"{UJI_MIGRASI}::test_migrasi_menghasilkan_skema_yang_sama_persis_dengan_spec01"),
        harus_memuat="baris markdown di DALAM blok",
        kelompok="db",
    ),
    # ── H-27 · data tiap pengguna milik pribadinya (B-40 · B-41 · RLS) ───
    # spec/01 DAN migrasi dirusak bersama: yang diuji penegak kepemilikan,
    # bukan uji kesamaan spec/01 == migrasi.
    Mutasi(
        "B-41",
        "FK goal_milestones kembali satu kolom — anak B boleh menunjuk goal A",
        [
            Sunting(
                berkas,
                FK_MILESTONE,
                FK_MILESTONE.replace(
                    "(goal_id, user_id) REFERENCES goals (id, user_id)",
                    "(goal_id) REFERENCES goals (id)",
                ),
            )
            for berkas in ("spec/01-DATABASE-SCHEMA.md", f"{MIGRASI}/0001_v0_skema.up.sql")
        ],
        _pytest(
            f"{UJI_KEPEMILIKAN}::test_tiap_fk_antar_tabel_milik_pengguna_membawa_user_id_berpasangan"
        ),
        harus_memuat="goal_milestones.goal_milestones_goal_id_fkey",
        kelompok="db",
    ),
    Mutasi(
        "RLS",
        "RLS journal_entries dimatikan — tulisan paling pribadi terbuka lintas pengguna",
        [
            Sunting(berkas, RLS_JURNAL, "")
            for berkas in ("spec/01-DATABASE-SCHEMA.md", f"{MIGRASI}/0001_v0_skema.up.sql")
        ],
        _pytest(
            f"{UJI_KEPEMILIKAN}::test_tiap_tabel_milik_pengguna_dilindungi_rls_dan_katalog_sistem_tidak"
        ),
        harus_memuat="['journal_entries']",
        kelompok="db",
    ),
    Mutasi(
        "RLS",
        "kebijakan memories dilonggarkan jadi USING (true) — ada, tetapi membuka semuanya",
        [
            Sunting(
                berkas,
                KEBIJAKAN_MEMORI,
                KEBIJAKAN_MEMORI.replace("USING (user_id = app_current_user_id())", "USING (true)"),
            )
            for berkas in ("spec/01-DATABASE-SCHEMA.md", f"{MIGRASI}/0001_v0_skema.up.sql")
        ],
        _pytest(
            f"{UJI_KEPEMILIKAN}::test_isi_tiap_kebijakan_rls_membatasi_pada_pengguna_yang_dilayani"
        ),
        harus_memuat="memories: [('memories_own_rows'",
        kelompok="db",
    ),
    Mutasi(
        "B-40",
        "peran aplikasi diberi UPDATE audit_logs — jejak audit bisa dipalsukan",
        [
            Sunting(
                berkas,
                GRANT_AGENT_RUNS,
                GRANT_AGENT_RUNS + NL + "GRANT UPDATE ON audit_logs TO hvx_app;",
            )
            for berkas in ("spec/01-DATABASE-SCHEMA.md", f"{MIGRASI}/0001_v0_skema.up.sql")
        ],
        _pytest(f"{UJI_KEPEMILIKAN}::test_hak_akses_peran_aplikasi_sesempit_yang_dinyatakan"),
        harus_memuat="audit_logs: hanya-tambah, tetapi UPDATE=True",
        kelompok="db",
    ),
    Mutasi(
        "B-40",
        "api tidak lagi memeriksa perannya — mulai sebagai superuser pemilik tabel",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "            await platform.pastikan_peran_aplikasi(engine)" + NL,
                "            pass" + NL,
            )
        ],
        _pytest(
            "tests/integration/test_aplikasi_hidup.py::test_api_menolak_mulai_sebagai_superuser_pemilik"
        ),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "RLS",
        "pengguna transaksi disetel untuk seluruh SESI — bocor ke koneksi pool berikutnya",
        [
            Sunting(
                f"{MODUL}/platform/db.py",
                "text(\"SELECT set_config('hvx.user_id', :user_id, true)\")",
                "text(\"SELECT set_config('hvx.user_id', :user_id, false)\")",
            )
        ],
        _pytest(
            f"{UJI_KEPEMILIKAN}::test_transaksi_pengguna_membatasi_kueri_dan_tidak_bocor_ke_koneksi_berikutnya"
        ),
        harus_memuat="bocor ke koneksi berikutnya dari pool",
        kelompok="db",
    ),
]


def _terapkan(s: Sunting, cadangan: dict[Path, bytes | None], dir_baru: list[Path]) -> None:
    p = AKAR / s.berkas
    if not p.parent.exists():
        puncak = p.parent
        while not puncak.parent.exists():
            puncak = puncak.parent
        p.parent.mkdir(parents=True)
        dir_baru.append(puncak)
    if p not in cadangan:
        cadangan[p] = p.read_bytes() if p.exists() else None
    if s.lama is None:
        if cadangan[p] is not None:
            raise RuntimeError(f"berkas mutasi sudah ada: {s.berkas}")
        p.write_bytes(s.baru.encode("utf-8"))
        return
    asli = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in asli
    teks = asli.replace("\r\n", "\n")
    if s.lama == "":
        teks += s.baru  # sisip di akhir berkas
    else:
        if teks.count(s.lama) != 1:
            raise RuntimeError(f"pola mutasi tidak unik ({teks.count(s.lama)}) di {s.berkas}")
        teks = teks.replace(s.lama, s.baru)
    p.write_bytes((teks.replace("\n", "\r\n") if crlf else teks).encode("utf-8"))


def _pulihkan(cadangan: dict[Path, bytes | None], dir_baru: list[Path]) -> None:
    for p, isi in cadangan.items():
        if isi is None:
            p.unlink(missing_ok=True)
        else:
            p.write_bytes(isi)
    for d in dir_baru:
        shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(AKAR / ".import_linter_cache", ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    pilih = ap.add_mutually_exclusive_group()
    pilih.add_argument(
        "--tanpa-db",
        action="store_true",
        help="kelompok lint saja (db & docker DINYATAKAN dilewati)",
    )
    pilih.add_argument("--hanya-db", action="store_true", help="kelompok db saja (tahap `test`)")
    pilih.add_argument(
        "--hanya-docker", action="store_true", help="kelompok docker saja (tahap `scan`)"
    )
    a = ap.parse_args()
    if a.tanpa_db:
        jalan = {"lint"}
    elif a.hanya_db:
        jalan = {"db"}
    elif a.hanya_docker:
        jalan = {"docker"}
    else:
        jalan = {"lint", "db", "docker"}

    if "db" in jalan and not os.environ.get("HVX_TEST_DATABASE_URL"):
        print("🛑 HVX_TEST_DATABASE_URL tidak diisi — mutasi migrasi tidak bisa dibuktikan.")
        print(
            "   Isi variabelnya, atau jalankan dengan --tanpa-db untuk MENYATAKAN bagian itu dilewati."
        )
        return 1

    lemah: list[str] = []
    dilewati: dict[str, int] = {}
    lingkungan = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    for m in MUTASI:
        label = f"{m.kode:4s} {m.maksud:64s}"
        if m.kelompok not in jalan:
            dilewati[m.kelompok] = dilewati.get(m.kelompok, 0) + 1
            if a.tanpa_db:
                print(f"  ⏭️  {label} → TIDAK DIJALANKAN (kelompok {m.kelompok})")
            continue
        cadangan: dict[Path, bytes | None] = {}
        dir_baru: list[Path] = []
        try:
            for s in m.suntingan:
                _terapkan(s, cadangan, dir_baru)
            r = subprocess.run(
                m.perintah,
                cwd=AKAR,
                env=lingkungan,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        finally:
            _pulihkan(cadangan, dir_baru)
        keluaran = r.stdout + r.stderr
        tertangkap = r.returncode in m.kode_tertangkap and m.harus_memuat in keluaran
        print(
            f"  {'✅' if tertangkap else '🛑'} {label} → "
            f"{'BERBUNYI' if tertangkap else f'DIAM/SALAH ALASAN (keluar {r.returncode})'}"
        )
        if not tertangkap:
            lemah.append(m.kode)
            print(f"      dituntut memuat: {m.harus_memuat!r}")
            print("\n".join("      " + b for b in keluaran.splitlines()[-15:]))

    dijalankan = len(MUTASI) - sum(dilewati.values())
    print()
    print(f"mutasi dijalankan : {dijalankan} dari {len(MUTASI)}")
    print(f"terbukti berbunyi : {dijalankan - len(lemah)}")
    for kelompok, n in sorted(dilewati.items()):
        print(
            f"⏭️  kelompok {kelompok}: {n} tidak dijalankan di sini — "
            "dijalankan tahap CI lain, atau belum terbukti"
        )
    if lemah:
        print(f"🛑 DIAM saat dirusak: {' '.join(lemah)}")
    return 1 if lemah else 0


if __name__ == "__main__":
    sys.exit(main())
