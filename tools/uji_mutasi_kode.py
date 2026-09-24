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
APLIKASI = "apps/mobile"
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
    # Direktori kerja perintah, relatif terhadap akar repo — `flutter test` wajib
    # dijalankan dari akar aplikasinya.
    cwd: str | None = None


def _lint(kontrak: str) -> list[str]:
    return ["lint-imports", "--no-cache", "--contract", kontrak]


def _pytest(nodeid: str) -> list[str]:
    return [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", nodeid]


def _ruff(berkas: str) -> list[str]:
    return [sys.executable, "-m", "ruff", "check", "--no-cache", "--select", "TID251", berkas]


def _flutter_uji(berkas: str, nama: str) -> list[str]:
    """`flutter test` satu uji — biner diambil dari tools/ci_lokal.py, bukan disalin."""
    sys.path.insert(0, str(AKAR / "tools"))
    try:
        from ci_lokal import _FLUTTER
    finally:
        sys.path.pop(0)
    return [_FLUTTER, "test", berkas, "--plain-name", nama]


def _tz_flutter() -> str:
    """Zona mesin yang `ci_lokal.py` pakai untuk Flutter — mutasi `toUtc()` hanya
    terlihat di mesin yang tidak berzona UTC."""
    sys.path.insert(0, str(AKAR / "tools"))
    try:
        from ci_lokal import TZ_FLUTTER
    finally:
        sys.path.pop(0)
    return TZ_FLUTTER


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
UJI_IZIN = "tests/integration/test_izin.py"
UJI_LAJU = "tests/integration/test_batas_laju.py"
UJI_AUTH = "tests/integration/test_auth.py"
UJI_SESI = "tests/integration/test_sesi.py"
UJI_PERSETUJUAN = "tests/integration/test_persetujuan.py"
UJI_GALAT_DB = "tests/integration/test_galat_basis_data.py"
UJI_SANDI = "tests/unit/test_sandi.py"
UJI_CONFIG = "tests/unit/test_config.py"
UJI_GOALS = "tests/integration/test_goals.py"
UJI_IDEM = "tests/integration/test_idempotensi.py"
UJI_IDEM_RUTE = "tests/unit/test_idempotensi_terpasang.py"
UJI_HABITS = "tests/integration/test_habits.py"
UJI_SELESAI = "tests/integration/test_penyelesaian.py"
UJI_RENTETAN = "tests/integration/test_rentetan.py"
UJI_CHECKIN = "tests/integration/test_checkin.py"
UJI_HARI = "tests/integration/test_habit_hari_ini.py"
UJI_MOOD = "tests/integration/test_mood.py"
UJI_KETAT = "tests/integration/test_masukan_ketat.py"
_UJI_SERENTAK = (
    "401 SERENTAK → SATU penyegaran; token segar yang sudah dirotasi tidak dipakai ulang"
)
_UJI_DIALOG_ID = "Simpan lagi sesudah jaringan putus mengirim id YANG SAMA; isian diubah → id baru"
_UJI_DILEWATI = "habit yang DILEWATI tampil lain dan ketukan membatalkannya"
_UJI_AKSES_BARU = "ulangan sesudah 401 membawa token BARU — bukan tanpa token"
_UJI_CATATAN_LAMA = "simpan energi ikut mengirim catatan check-in lama"
_UJI_LAYAR_LAMA = "energi disimpan BERSAMA check-in lama — PUT mengganti"
_UJI_TANGGAL_LOKAL = "tanggal lokal perangkat, bukan tanggal UTC"
_UJI_TANDA_SARAN = 'tanda "Disarankan hari ini" di tier yang disarankan server'
_UJI_KELUAR = "keluar mencabut sesi di SERVER dengan token yang sedang dipakai"
_UJI_TARGET_MINGGUAN = "habit mingguan memakai jumlah per minggu yang dipilih"
_UJI_PELATIHAN_KLIEN = "daftar dengan izin pelatihan: granted true + cakupan data"
_UJI_PELATIHAN_LAYAR = "centang pelatihan model sampai ke layanan"
_UJI_TENGAH_MALAM = "layar yang terbuka melewati tengah malam memakai tanggal BARU"
# Blok CORS `hvx.main` apa adanya — mutasi memindahkannya ke dalam batas laju.
_CORS_BLOK = (
    "    if settings.asal_cors:"
    + NL
    + "        # Paling luar: jawaban 401/429 pun membawa header CORS, supaya aplikasi"
    + NL
    + '        # web membaca galatnya alih-alih "network error". Tanpa kredensial'
    + NL
    + "        # peramban (cookie) — autentikasi V0 token bearer (K-21)."
    + NL
    + "        app.add_middleware("
    + NL
    + "            CORSMiddleware,"
    + NL
    + "            allow_origins=list(settings.asal_cors),"
    + NL
    + '            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],'
    + NL
    + '            allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],'
    + NL
    + '            expose_headers=["Retry-After", "X-Request-ID", "Idempotent-Replayed"],'
    + NL
    + "            allow_credentials=False,"
    + NL
    + "            max_age=600,"
    + NL
    + "        )"
    + NL
)
_UJI_ID_SAMA = (
    "membuat habit: id buatan pemanggil = id badan = Idempotency-Key, SAMA di tiap percobaan"
)
UJI_KETAT_RUTE = "tests/unit/test_masukan_ketat_semua_rute.py"
UJI_BALAPAN = "tests/integration/test_batas_dan_balapan.py"
UJI_BADAN = "tests/unit/test_batas_badan.py"
FK_MILESTONE = (
    "  FOREIGN KEY (goal_id, user_id) REFERENCES goals (id, user_id) ON DELETE CASCADE" + NL + ");"
)
RLS_JURNAL = "ALTER TABLE journal_entries         ENABLE ROW LEVEL SECURITY;" + NL
KEBIJAKAN_MEMORI = "ON memories                USING (user_id = app_current_user_id())"
GRANT_AGENT_RUNS = "GRANT SELECT, INSERT, UPDATE ON agent_runs TO hvx_app;"

UJI_SESI_CELAH = (
    "tests/integration/test_sesi.py::test_sesi_yang_dicabut_tidak_hidup_lagi_di_celah_mana_pun"
)
# sesi.py sebelum tinjauan Sprint 1: catatan sesi DIBACA, lalu ditulis di MULTI terpisah.
SEGARKAN_ATOMIK = """\
        hasil, isi = await self._putar(
            keys=[self._k_segar(lama), self._k_bekas(lama)],
            args=[self._p, sidik(akses), sidik(segar), self._ttl_akses, self._ttl_segar],
        )
"""
SEGARKAN_TAK_ATOMIK = """\
        isi = await self._r.getdel(self._k_segar(lama))
        if isi is None:
            bekas = await self._r.get(self._k_bekas(lama))
            hasil, isi = (_BEKAS, bekas) if bekas else (0, "")
        else:
            lawas = _pisah(isi)
            catatan = await self._r.hgetall(self._k_sesi(lawas.sesi_id))
            hasil = _DIPUTAR if catatan else 0
            if catatan:
                async with self._r.pipeline(transaction=True) as p:
                    p.delete(self._k_akses(catatan["akses"]))
                    p.set(self._k_bekas(lama), isi, ex=self._ttl_segar)
                    p.set(self._k_akses(sidik(akses)), isi, ex=self._ttl_akses)
                    p.set(self._k_segar(sidik(segar)), isi, ex=self._ttl_segar)
                    p.hset(
                        self._k_sesi(lawas.sesi_id),
                        mapping={"akses": sidik(akses), "segar": sidik(segar)},
                    )
                    p.expire(self._k_sesi(lawas.sesi_id), self._ttl_segar)
                    await p.execute()
"""
CABUT_ATOMIK = """\
        await self._cabut(keys=[self._k_sesi(sesi_id)], args=[self._p, str(sesi_id)])
"""
CABUT_TAK_ATOMIK = """\
        catatan = await self._r.hgetall(self._k_sesi(sesi_id))
        if catatan:
            async with self._r.pipeline(transaction=True) as p:
                p.delete(
                    self._k_akses(catatan["akses"]),
                    self._k_segar(catatan["segar"]),
                    self._k_sesi(sesi_id),
                )
                p.srem(self._k_pengguna(UUID(catatan["user_id"])), str(sesi_id))
                await p.execute()
"""

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
    # ── sidik IP (spec/01 audit_logs.ip_hash): hash, bukan IP mentah ─────
    Mutasi(
        "1.1",
        "sidik IP sha256 polos tanpa kunci — IPv4 bisa dibalik dengan mencoba 2³² alamat",
        [
            Sunting(
                f"{MODUL}/platform/keadaan.py",
                "hmac.new(kunci, request.client.host.encode(), hashlib.sha256).hexdigest()",
                "hashlib.sha256(request.client.host.encode()).hexdigest()",
            )
        ],
        _pytest("tests/unit/test_sidik_ip.py::test_sidik_ip_berkunci_bukan_sha256_polos"),
        harus_memuat="sidik IP bisa dibalik tanpa kunci",
    ),
    # ── sesi (spec/07 1.2): dicabut → 401 seketika ───────────────────────
    Mutasi(
        "1.2",
        "cabut sesi lupa menghapus token akses — hidup sampai kedaluwarsa",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "if c[2] then table.insert(kunci, ARGV[1] .. ':akses:' .. c[2]) end" + NL,
                "",
            )
        ],
        _pytest("tests/integration/test_sesi.py::test_sesi_dicabut_401_seketika"),
        harus_memuat="assert 200 == 401",
        kelompok="db",
    ),
    # 🔴 Tinjauan Sprint 1: baca catatan sesi lalu tulis di MULTI terpisah — tiap
    # mutasi di bawah mengembalikan SATU operasi ke bentuk versi pertamanya.
    Mutasi(
        "1.2",
        "penyegaran baca-lalu-tulis tak atomik — keluar di celahnya dihidupkan lagi",
        [Sunting(f"{MODUL}/identity/sesi.py", SEGARKAN_ATOMIK, SEGARKAN_TAK_ATOMIK)],
        _pytest(f"{UJI_SESI_CELAH}[segarkan-diselingi-keluar]"),
        harus_memuat="sesi yang dicabut hidup lagi — segarkan-diselingi-keluar",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "keluar baca-lalu-hapus tak atomik — pasangan hasil penyegaran di celahnya selamat",
        [Sunting(f"{MODUL}/identity/sesi.py", CABUT_ATOMIK, CABUT_TAK_ATOMIK)],
        _pytest(f"{UJI_SESI_CELAH}[keluar-diselingi-segarkan]"),
        harus_memuat="sesi yang dicabut hidup lagi — keluar-diselingi-segarkan",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "token bekas mencabut dengan catatan lama — pasangan terbaru pencuri selamat",
        [Sunting(f"{MODUL}/identity/sesi.py", CABUT_ATOMIK, CABUT_TAK_ATOMIK)],
        _pytest(f"{UJI_SESI_CELAH}[pencurian-diselingi-penyegaran-pencuri]"),
        harus_memuat="sesi yang dicabut hidup lagi — pencurian-diselingi-penyegaran-pencuri",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "cabut semua menghapus seluruh himpunan — sesi yang lahir di sela tak tercatat",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "            await self._r.srem(self._k_pengguna(user_id), *anggota)" + NL,
                "            await self._r.delete(self._k_pengguna(user_id))" + NL,
            )
        ],
        _pytest(f"{UJI_SESI_CELAH}[cabut-semua-diselingi-masuk]"),
        harus_memuat="sesi yang dicabut hidup lagi — cabut-semua-diselingi-masuk",
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
                "if not (p.granted and p.masih_berlaku and cakupan <= p.data_scopes):",
                "if not (p.granted and p.masih_berlaku):",
            )
        ],
        _pytest(
            "tests/integration/test_persetujuan.py"
            "::test_tujuan_dan_cakupan_harus_tercakup_persetujuan_terakhir"
        ),
        harus_memuat="assert not True",
        kelompok="db",
    ),
    Mutasi(
        "1.4",
        "persetujuan terakhir dibaca per tujuan saja — setuju syarat baru menutupi cabut privasi",
        [
            Sunting(
                f"{MODUL}/identity/repository.py",
                "SELECT DISTINCT ON (purpose, kind) purpose, kind,",
                "SELECT DISTINCT ON (purpose) purpose, kind,",
            ),
            Sunting(
                f"{MODUL}/identity/repository.py",
                "ORDER BY purpose, kind, created_at DESC",
                "ORDER BY purpose, created_at DESC",
            ),
        ],
        _pytest(
            "tests/integration/test_persetujuan.py"
            "::test_pencabutan_satu_jenis_tidak_ditutupi_jenis_lain_bertujuan_sama"
        ),
        harus_memuat="persetujuan jenis lain menutupi pencabutan privacy",
        kelompok="db",
    ),
    # ── mesin izin (spec/07 1.5): default ask · kedaluwarsa · cache yang jujur ─
    Mutasi(
        "1.5",
        "tanpa keputusan tersimpan dijawab allow — agent lolos tanpa pernah ditanya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "        if baris is None:" + NL + "            return None, self._ttl_ms" + NL,
                "        if baris is None:" + NL + '            return "allow", self._ttl_ms' + NL,
            )
        ],
        _pytest(f"{UJI_IZIN}::test_tanpa_keputusan_tersimpan_jawabannya_ask"),
        harus_memuat="assert 'allow' == 'ask'",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "izin kedaluwarsa tetap berlaku — 'izinkan sekali' menjadi izin permanen",
        [Sunting(f"{MODUL}/identity/izin.py", "        if sisa_ms <= 0:", "        if False:")],
        _pytest(f"{UJI_IZIN}::test_izin_kedaluwarsa_kembali_ke_ask"),
        harus_memuat="assert 'allow' == 'ask'",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "cache izin sementara berumur penuh — hidup melewati expires_at izinnya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "min(self._ttl_ms, sisa_ms - _MARGIN_KEDALUWARSA_MS)",
                "self._ttl_ms",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_cache_izin_sementara_tidak_hidup_lebih_lama_dari_izinnya"),
        harus_memuat="cache hidup lebih lama dari izinnya",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "cache izin sementara tanpa margin — ditulis sesudah commit, hidup melewati izinnya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "sisa_ms - _MARGIN_KEDALUWARSA_MS)",
                "sisa_ms)",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_cache_izin_sementara_tidak_hidup_lebih_lama_dari_izinnya"),
        harus_memuat="cache hidup lebih lama dari izinnya",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "generasi tak diganti sesudah commit — pembaca lambat menghidupkan izin yang dicabut",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "ditinggalkan." + NL + "        await self._ganti_generasi(user_id)" + NL,
                "ditinggalkan." + NL,
            )
        ],
        _pytest(f"{UJI_IZIN}::test_pembaca_di_tengah_pencabutan_tidak_menghidupkan_kembali_izin"),
        harus_memuat="pembaca lambat menghidupkan kembali izin yang dicabut",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "generasi tak diganti sebelum commit — Redis putus meninggalkan izin lama di cache",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "        await self._ganti_generasi(user_id)"
                + NL
                + "        async with platform.transaksi_pengguna(",
                "        async with platform.transaksi_pengguna(",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_redis_putus_sesudah_commit_tidak_meninggalkan_izin_lama"),
        harus_memuat="izin yang dicabut masih dijawab cache lama",
        kelompok="db",
    ),
    # ── batas laju (spec/07 1.7): per IP · per pengguna · per akun, 429 + Retry-After ─
    Mutasi(
        "1.7",
        "middleware batas laju IP tidak dipasang — /v1/* tanpa batas per IP",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.add_middleware(platform.BatasLajuIpMiddleware)" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_LAJU}::test_batas_ip_menjawab_429_dengan_retry_after_di_seluruh_v1"),
        harus_memuat="assert 401 == 429",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "429 tanpa Retry-After — klien tidak tahu kapan boleh mencoba lagi",
        [
            Sunting(
                f"{MODUL}/platform/batas_laju.py",
                'header={"Retry-After": str(hasil.retry_after_s)}',
                "header={}",
            )
        ],
        _pytest(f"{UJI_LAJU}::test_batas_ip_menjawab_429_dengan_retry_after_di_seluruh_v1"),
        harus_memuat="429 tanpa Retry-After",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "skrip GCRA tidak pernah mencatat — jatah tidak pernah habis",
        [
            Sunting(
                f"{MODUL}/platform/batas_laju.py",
                "redis.call('HSET', KEYS[1], 'tat', tat_baru, 't', sekarang)" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_LAJU}::test_mekanisme_meledak_sampai_batas_lalu_terisi_satu_per_interval"),
        harus_memuat="assert [4, 4, 4, 4, 4] == [4, 3, 2, 1, 0]",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "IPv6 dihitung per alamat — berganti alamat di /64 sendiri melewati batas",
        [
            Sunting(
                f"{MODUL}/platform/batas_laju.py",
                "return str(ipaddress.IPv6Network((alamat, 64), strict=False))",
                "return str(alamat)",
            )
        ],
        _pytest("tests/unit/test_batas_laju_bentuk.py::test_ipv6_dihitung_per_jaringan_64"),
        harus_memuat="dua alamat dalam satu /64 dihitung terpisah",
    ),
    Mutasi(
        "1.7",
        "dependensi autentikasi lupa batas per pengguna",
        [
            Sunting(
                f"{MODUL}/identity/dependensi.py",
                "    await batasi_pengguna(request, sesi.user_id)  # spec/07 1.7" + NL,
                "",
            )
        ],
        _pytest(
            f"{UJI_LAJU}::test_batas_per_pengguna_tidak_mengenai_pengguna_lain_di_ip_yang_sama"
        ),
        harus_memuat="assert 200 == 429",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "login tanpa batas kredensial per IP — hanya batas umum /v1",
        [
            Sunting(
                f"{MODUL}/identity/routes.py",
                '@router.post("/login", response_model=JawabanAkun, dependencies=_KREDENSIAL)',
                '@router.post("/login", response_model=JawabanAkun)',
            )
        ],
        _pytest(f"{UJI_LAJU}::test_daftar_dan_masuk_berbagi_batas_per_ip_yang_lebih_ketat"),
        harus_memuat="assert 200 == 429",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "berhasil masuk tidak menghapus hitungan gagal — akun terkunci oleh salah ketik lama",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "    await penjaga.berhasil(kunci)  # masuk yang berhasil mengosongkan hitungan gagal akun ini"
                + NL,
                "",
            )
        ],
        _pytest(
            f"{UJI_LAJU}::test_login_gagal_dibatasi_per_akun_dan_berhasil_menghapus_hitungannya"
        ),
        harus_memuat="assert 429 == 401",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "jatah gagal per akun dipakai SESUDAH argon2 — tebakan serentak lolos bersama",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "    await penjaga.pakai(kunci)  # SEBELUM argon2",
                "    pass  # (mutasi) jatah dipakai sesudah gagal",
            ),
            Sunting(
                f"{MODUL}/identity/service.py",
                "    if akun is None or not cocok:" + NL,
                "    if akun is None or not cocok:"
                + NL
                + "        await penjaga.pakai(kunci)"
                + NL,
            ),
        ],
        _pytest(f"{UJI_LAJU}::test_tebakan_serentak_tidak_dicocokkan_melewati_batas_per_akun"),
        harus_memuat="tebakan serentak dicocokkan melewati batas per akun",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "kunci per akun dari lower() Python — 'vİctim@' mendapat hitungan sendiri",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "akun, kunci = dicari.akun, dicari.kunci",
                "akun, kunci = dicari.akun, email.strip().lower()",
            )
        ],
        _pytest(f"{UJI_LAJU}::test_varian_huruf_unicode_satu_email_berbagi_hitungan_gagal"),
        harus_memuat="varian huruf Unicode satu email mendapat hitungan gagal sendiri",
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
        "daftar tolak sandi tidak ditegakkan saat daftar — 'passwordpassword' diterima",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "    if alasan is not None:  # NIST SP 800-63B-4 §3.1.1.2 — daftar tolak",
                "    if False:",
            )
        ],
        _pytest(
            "tests/integration/test_auth.py"
            "::test_sandi_yang_mudah_ditebak_422_dengan_alasan_tanpa_mengutipnya"
        ),
        harus_memuat="assert 201 == 422",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "sandi tidak dinormalisasi NFKC — 'é' dari perangkat lain ditolak",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                'return unicodedata.normalize("NFKC", sandi)',
                "return sandi",
            )
        ],
        _pytest("tests/unit/test_sandi.py::test_sandi_dinormalisasi_nfkc_sebelum_hashing"),
        harus_memuat="NFKC tidak diterapkan",
    ),
    Mutasi(
        "1.1",
        "token segar dibaca GET, bukan GETDEL — token lama tetap hidup sesudah rotasi",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "local isi = redis.call('GETDEL', KEYS[1])",
                "local isi = redis.call('GET', KEYS[1])",
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
        "penyegaran tidak membaca status akun — akun ditangguhkan memperpanjang sesinya",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                '        aktif = akun is not None and akun.status == "active"',
                "        aktif = True",
            )
        ],
        _pytest(
            "tests/integration/test_auth.py"
            "::test_akun_yang_tidak_lagi_aktif_tidak_bisa_memperpanjang_sesinya"
        ),
        harus_memuat="akun yang ditangguhkan memperpanjang sesinya sendiri",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "gagal masuk akun tak dikenal satu kueri lebih sedikit — waktunya membocorkan akun",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "        async with platform.transaksi_sistem(engine) as conn:",
                "        async with engine.begin() as conn:",
            )
        ],
        _pytest(
            "tests/integration/test_auth.py"
            "::test_gagal_masuk_akun_ada_dan_tidak_ada_menjalankan_kueri_yang_sama"
        ),
        harus_memuat="gagal masuk akun yang ada menjalankan kueri berbeda",
        kelompok="db",
    ),
    # ── galat basis data tanpa nilai milik pengguna (spec/07 0.5 · H-27) ─
    Mutasi(
        "0.5",
        "engine tanpa hide_parameters — email & hash sandi di teks galat",
        [Sunting(f"{MODUL}/platform/db.py", "        hide_parameters=True," + NL, "")],
        _pytest(
            "tests/integration/test_galat_basis_data.py"
            "::test_teks_galat_basis_data_tidak_membawa_parameter_kueri"
        ),
        harus_memuat="parameter kueri ikut di teks galat basis data",
        kelompok="db",
    ),
    Mutasi(
        "0.5",
        "penyaring galat basis data dicabut dari log — DETAIL membawa isi baris",
        [Sunting(f"{MODUL}/platform/log.py", "        _galat_basis_data_tanpa_isi," + NL, "")],
        _pytest(
            "tests/integration/test_galat_basis_data.py"
            "::test_galat_basis_data_dicatat_tanpa_isi_baris_tetapi_tetap_bisa_ditelusuri"
        ),
        harus_memuat="isi baris pengguna tertulis ke log",
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
    # ── tinjauan Sprint 1, lensa kedua: verifikator · kontrak · penegak buta ─
    Mutasi(
        "1.1",
        "status akun dibaca SESUDAH token diputar — galat basis data membakar token",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "    pemilik = await sesi.pemilik_token_segar(token_segar)" + NL,
                "    pemilik = await sesi.pemilik_token_segar(token_segar)"
                + NL
                + "    hasil = await sesi.segarkan(token_segar)"
                + NL,
            ),
            Sunting(
                f"{MODUL}/identity/service.py",
                "    hasil = await sesi.segarkan(token_segar)"
                + NL
                + "    if hasil.dipakai_ulang is not None:",
                "    if hasil.dipakai_ulang is not None:",
            ),
        ],
        _pytest(
            f"{UJI_AUTH}::test_basis_data_tersendat_saat_penyegaran_tidak_membakar_token_segar"
        ),
        harus_memuat="penyegaran yang gagal membakar token segar",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "akun tidak aktif hanya mencabut sesi yang disegarkan — sesi lainnya jalan terus",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "        await sesi.cabut_semua(pemilik.user_id)",
                "        await sesi.cabut(pemilik.sesi_id)",
            )
        ],
        _pytest(f"{UJI_AUTH}::test_akun_yang_tidak_lagi_aktif_tidak_bisa_memperpanjang_sesinya"),
        harus_memuat="sesi lain akun yang ditangguhkan tetap memakai API",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "pendengar pendaftaran yang gagal ditelan — akun tanpa profil tercipta",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                "            for p in pendengar:" + NL + "                await p(conn, baru)" + NL,
                "            for p in pendengar:"
                + NL
                + "                try:"
                + NL
                + "                    await p(conn, baru)"
                + NL
                + "                except Exception:"
                + NL
                + "                    pass"
                + NL,
            )
        ],
        _pytest(
            f"{UJI_AUTH}::test_pendengar_pendaftaran_yang_gagal_menggagalkan_seluruh_pendaftaran"
        ),
        harus_memuat="pendaftaran setengah jadi tersimpan",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "keluar tidak tercatat di audit",
        [
            Sunting(
                f"{MODUL}/identity/service.py",
                'aksi="session.logged_out",',
                'aksi="session.tidak_tercatat",',
            )
        ],
        _pytest(f"{UJI_AUTH}::test_keluar_204_dan_token_akses_401_seketika"),
        harus_memuat="keluar tidak tercatat di audit",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "sandi 129 karakter diterima",
        [Sunting(f"{MODUL}/identity/sandi.py", "PANJANG_MAKS = 128", "PANJANG_MAKS = 129")],
        _pytest(f"{UJI_AUTH}::test_sandi_128_karakter_diterima_129_ditolak"),
        harus_memuat="sandi 129 karakter diterima",
        kelompok="db",
    ),
    Mutasi(
        "1.1",
        "ip_hash audit berisi IP mentah",
        [
            Sunting(
                f"{MODUL}/platform/keadaan.py",
                "hmac.new(kunci, request.client.host.encode(), hashlib.sha256).hexdigest()",
                "request.client.host",
            )
        ],
        _pytest(f"{UJI_AUTH}::test_ip_dan_email_tidak_pernah_disimpan_mentah"),
        harus_memuat="audit_logs.ip_hash bukan sidik HMAC",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "kunci batas laju per IP berisi IP mentah",
        [
            Sunting(
                f"{MODUL}/platform/batas_laju.py",
                '    return sidik(settings_dari(request), "laju-ip", jaringan_klien(host))',
                "    return jaringan_klien(host)",
            )
        ],
        _pytest(f"{UJI_AUTH}::test_ip_dan_email_tidak_pernah_disimpan_mentah"),
        harus_memuat="IP atau email mentah di kunci Redis",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "kunci gagal masuk per akun berisi email mentah",
        [
            Sunting(
                f"{MODUL}/identity/laju.py",
                '        return platform.sidik(self.settings, "akun-masuk", kunci_akun)',
                "        return kunci_akun",
            )
        ],
        _pytest(f"{UJI_AUTH}::test_ip_dan_email_tidak_pernah_disimpan_mentah"),
        harus_memuat="IP atau email mentah di kunci Redis",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "catatan sesi tanpa user_id masih bisa diputar",
        [Sunting(f"{MODUL}/identity/sesi.py", "if not (c[1] and c[2]) then", "if not c[2] then")],
        _pytest(
            f"{UJI_SESI}::test_catatan_sesi_tanpa_user_id_tidak_bisa_diputar_dan_tetap_bisa_dicabut"
        ),
        harus_memuat="catatan sesi tanpa user_id masih bisa diputar",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "catatan sesi tanpa user_id tidak bisa dicabut",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "if not (c[1] or c[2] or c[3]) then return 0 end",
                "if not c[1] then return 0 end",
            )
        ],
        _pytest(
            f"{UJI_SESI}::test_catatan_sesi_tanpa_user_id_tidak_bisa_diputar_dan_tetap_bisa_dicabut"
        ),
        harus_memuat="catatan sesi tanpa user_id tidak bisa dicabut",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "token akses hasil rotasi berumur token segar — 30 hari",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "redis.call('SET', ARGV[1] .. ':akses:' .. ARGV[2], isi, 'EX', ARGV[4])",
                "redis.call('SET', ARGV[1] .. ':akses:' .. ARGV[2], isi, 'EX', ARGV[5])",
            )
        ],
        _pytest(f"{UJI_SESI}::test_umur_token_akses_dan_segar_sesuai_pengaturan"),
        harus_memuat="token akses diputar hidup",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "token akses baru berumur token segar",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                "p.set(self._k_akses(sidik(akses)), nilai, ex=self._ttl_akses)",
                "p.set(self._k_akses(sidik(akses)), nilai, ex=self._ttl_segar)",
            )
        ],
        _pytest(f"{UJI_SESI}::test_umur_token_akses_dan_segar_sesuai_pengaturan"),
        harus_memuat="token akses dibuat hidup",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "token segar mentah di catatan sesi (hash) — pemindai lama hanya membaca string",
        [
            Sunting(
                f"{MODUL}/identity/sesi.py",
                '"akses": sidik(akses), "segar": sidik(segar)},',
                '"akses": sidik(akses), "segar": segar},',
            )
        ],
        _pytest(f"{UJI_SESI}::test_redis_hanya_menyimpan_sidik_token"),
        harus_memuat="token mentah tersimpan di Redis",
        kelompok="db",
    ),
    Mutasi(
        "1.2",
        "token akses boleh hidup lebih lama dari catatan sesinya",
        [
            Sunting(
                f"{MODUL}/platform/config.py",
                "        if self.access_token_ttl_s > self.refresh_token_ttl_s:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_CONFIG}::test_token_akses_tidak_boleh_hidup_lebih_lama_dari_sesinya"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "1.1",
        "kunci HMAC sidik IP satu karakter diterima",
        [
            Sunting(
                f"{MODUL}/platform/config.py",
                "    ip_hash_key: SecretStr = Field(min_length=32)",
                "    ip_hash_key: SecretStr = Field(min_length=1)",
            )
        ],
        _pytest(f"{UJI_CONFIG}::test_kunci_sidik_ip_pendek_ditolak"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "1.7",
        "bawaan gagal masuk per akun 1000 tebakan sekaligus",
        [
            Sunting(
                f"{MODUL}/platform/config.py",
                'rate_limit_login_failures: str = Field(default="100/86400"',
                'rate_limit_login_failures: str = Field(default="1000/86400"',
            )
        ],
        _pytest(f"{UJI_CONFIG}::test_bawaan_gagal_masuk_per_akun_tidak_meledak_lebih_dari_100"),
        harus_memuat="bawaan batas gagal masuk per akun",
    ),
    Mutasi(
        "1.1",
        "akun tak dikenal tidak diverifikasi argon2 — jawabannya ±40 ms lebih cepat",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                'juga untuk akun yang tidak ada."""' + NL + "    try:",
                'juga untuk akun yang tidak ada."""'
                + NL
                + "    if hash_tersimpan is None:"
                + NL
                + "        return False"
                + NL
                + "    try:",
            )
        ],
        _pytest(f"{UJI_SANDI}::test_akun_tak_dikenal_tetap_menjalankan_satu_verifikasi_argon2"),
        harus_memuat="akun tak dikenal tidak diverifikasi argon2",
    ),
    Mutasi(
        "1.1",
        "hash sandi tanpa NFKC — yang didaftarkan dari perangkat lain tak bisa masuk",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                "    return _hasher.hash(normalisasi(sandi))",
                "    return _hasher.hash(sandi)",
            )
        ],
        _pytest(f"{UJI_SANDI}::test_sandi_dinormalisasi_nfkc_sebelum_hashing"),
        harus_memuat="NFKC tidak diterapkan saat hashing",
    ),
    Mutasi(
        "1.1",
        "hash argon2 di event loop — satu pendaftaran menahan semua permintaan",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                "    return await asyncio.to_thread(hash_sandi, sandi)",
                "    return hash_sandi(sandi)",
            )
        ],
        _pytest(f"{UJI_SANDI}::test_argon2_dijalankan_di_thread_bukan_di_event_loop"),
        harus_memuat="argon2 dijalankan di event loop",
    ),
    Mutasi(
        "1.1",
        "verifikasi argon2 di event loop — tebakan sandi menahan semua permintaan",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                "    return await asyncio.to_thread(cocokkan, hash_tersimpan, sandi)",
                "    return cocokkan(hash_tersimpan, sandi)",
            )
        ],
        _pytest(f"{UJI_SANDI}::test_argon2_dijalankan_di_thread_bukan_di_event_loop"),
        harus_memuat="argon2 dijalankan di event loop",
    ),
    Mutasi(
        "1.1",
        "pengulangan dinilai dari kerangka huruf-angka saja — sandi simbol ditolak",
        [
            Sunting(
                f"{MODUL}/identity/sandi.py",
                "    if _berulang(penuh) or (len(inti) >= _URUTAN_MIN and _berulang(inti)):",
                "    if _berulang(inti):",
            )
        ],
        _pytest(f"{UJI_SANDI}::test_sandi_yang_wajar_lolos_daftar_tolak[simbol]"),
        harus_memuat="sandi yang wajar ditolak sebagai 'repetitive'",
    ),
    Mutasi(
        "1.4",
        "riwayat persetujuan satu transaksi berwaktu sama — now(), bukan clock_timestamp()",
        [
            Sunting(
                f"{MODUL}/identity/repository.py",
                ":expires_at, clock_timestamp())",
                ":expires_at, now())",
            )
        ],
        _pytest(f"{UJI_PERSETUJUAN}::test_riwayat_dalam_satu_transaksi_tetap_berurutan"),
        harus_memuat="riwayat satu transaksi berwaktu sama",
        kelompok="db",
    ),
    Mutasi(
        "1.6",
        "persetujuan di-commit sebelum jejak auditnya",
        [
            Sunting(
                f"{MODUL}/identity/persetujuan.py",
                "    await _tambah(conn, user_id, persetujuan, dicabut=False)" + NL,
                "    await _tambah(conn, user_id, persetujuan, dicabut=False)"
                + NL
                + "    await conn.commit()"
                + NL,
            )
        ],
        _pytest(f"{UJI_PERSETUJUAN}::test_persetujuan_tidak_tersimpan_tanpa_jejak_audit"),
        harus_memuat="persetujuan tersimpan tanpa jejak audit",
        kelompok="db",
    ),
    Mutasi(
        "1.6",
        "izin di-commit sebelum jejak auditnya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "            await audit("
                + NL
                + "                conn,"
                + NL
                + "                aksi=_AKSI_AUDIT[keputusan],",
                "            await conn.commit()"
                + NL
                + "            await audit("
                + NL
                + "                conn,"
                + NL
                + "                aksi=_AKSI_AUDIT[keputusan],",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_perubahan_izin_tidak_tersimpan_tanpa_jejak_audit"),
        harus_memuat="izin tersimpan tanpa jejak audit",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "bawaan satu pemanggil tercache untuk pemanggil berikutnya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "await self._r.set(kunci, keputusan or _TANPA_KEPUTUSAN, px=umur_ms)",
                "await self._r.set(kunci, keputusan or bawaan, px=umur_ms)",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_bawaan_pemanggil_hanya_untuk_yang_tanpa_keputusan_tersimpan"),
        harus_memuat="bawaan satu pemanggil tercache untuk pemanggil lain",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "ask eksplisit dianggap tanpa keputusan — bawaan risiko menimpa pilihan pengguna",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "            return cast(Keputusan, baris.decision), self._ttl_ms",
                '            return (None if baris.decision == "ask" else '
                "cast(Keputusan, baris.decision)), self._ttl_ms",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_bawaan_pemanggil_hanya_untuk_yang_tanpa_keputusan_tersimpan"),
        harus_memuat="bawaan pemanggil menimpa pilihan eksplisit pengguna",
        kelompok="db",
    ),
    Mutasi(
        "0.5",
        "penyaring log tidak menelusuri isi kelompok galat (TaskGroup · except*)",
        [
            Sunting(
                f"{MODUL}/platform/log.py",
                "    return tuple(g.exceptions) if isinstance(g, BaseExceptionGroup) else ()",
                "    return ()",
            )
        ],
        _pytest(f"{UJI_GALAT_DB}::test_galat_basis_data_di_dalam_kelompok_galat_juga_tanpa_isi"),
        harus_memuat="isi baris dari galat di dalam kelompok tertulis ke log",
        kelompok="db",
    ),
    Mutasi(
        "06.5",
        "SQL identity menyebut goals di daftar FROM berkoma — pemindai lama hanya membaca satu",
        [
            _sisip(
                f"{MODUL}/identity/repository.py",
                '_KUERI_LIAR = "SELECT 1 FROM users u, goals g WHERE g.user_id = u.id"',
            )
        ],
        _pytest(
            "tests/unit/test_batas_tabel.py::test_sql_tiap_modul_hanya_menyebut_tabel_miliknya"
        ),
        harus_memuat="`identity` menyebut `goals`",
    ),
    Mutasi(
        "06.5",
        "SQL identity menyebut goals lewat DELETE … USING",
        [
            _sisip(
                f"{MODUL}/identity/repository.py",
                '_KUERI_LIAR = "DELETE FROM consents c USING goals g WHERE c.user_id = g.user_id"',
            )
        ],
        _pytest(
            "tests/unit/test_batas_tabel.py::test_sql_tiap_modul_hanya_menyebut_tabel_miliknya"
        ),
        harus_memuat="`identity` menyebut `goals`",
    ),
    Mutasi(
        "§6",
        "alasan mutasi pytest dibaca dari seluruh keluaran — pesan di sumber uji terhitung",
        [
            # Disambung NL: pola utuhnya hanya ada di fungsinya, tidak di literal ini.
            Sunting(
                "tools/uji_mutasi_kode.py",
                '    if "pytest" in m.perintah:' + NL + "        keluaran = NL.join(",
                "    if False:" + NL + "        keluaran = NL.join(",
            )
        ],
        _pytest(
            "tests/unit/test_penegak.py::test_alasan_mutasi_pytest_hanya_dibaca_dari_baris_galat"
        ),
        harus_memuat="pesan di sumber uji terhitung alasan galat",
    ),
    Mutasi(
        "1.1",
        "NUL di teks bebas lolos validasi — PostgreSQL menolaknya sebagai 500",
        [Sunting(f"{MODUL}/platform/teks.py", "    if _NUL in nilai:", "    if False:")],
        _pytest(f"{UJI_AUTH}::test_nul_di_teks_bebas_ditolak_400_bukan_500[nama]"),
        harus_memuat="NUL lolos validasi sampai basis data",
        kelompok="db",
    ),
    Mutasi(
        "1.3",
        "NUL di preferences (jsonb) lolos validasi — 500, bukan 400",
        [
            Sunting(
                f"{MODUL}/profile/schemas.py",
                "    platform.tanpa_nul_bersarang(nilai)" + NL,
                "",
            )
        ],
        _pytest(
            "tests/integration/test_profil.py"
            "::test_patch_yang_tidak_sah_ditolak_400_dan_tidak_menyentuh_apa_pun[badan5]"
        ),
        harus_memuat="assert 500 == 400",
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
    # ── Sprint 2 · 2.1 goals + Idempotency-Key tulisan domain (E-165) ─────
    Mutasi(
        "2.1",
        "pohon goal dibaca DUA kueri — akar dulu, baru keturunannya",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "        baris = await repository.pohon(conn, goal_id, MAKS_KEDALAMAN)" + NL,
                "        await repository.ambil(conn, goal_id)"
                + NL
                + "        baris = await repository.pohon(conn, goal_id, MAKS_KEDALAMAN)"
                + NL,
            )
        ],
        _pytest(f"{UJI_GOALS}::test_pohon_goal_tiga_tingkat_terbaca_dalam_satu_kueri"),
        harus_memuat="pohon goal tidak terbaca dalam satu kueri",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "CHECK goals_parent_not_self dicabut (spec/01 DAN migrasi 0004)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "    ON DELETE SET NULL (parent_id)," + NL,
                "    ON DELETE SET NULL (parent_id)" + NL,
            ),
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "  CONSTRAINT goals_parent_not_self CHECK (parent_id <> id)" + NL,
                "",
            ),
            Sunting(
                f"{MIGRASI}/0004_goal_bukan_induk_dirinya.up.sql",
                "  ADD CONSTRAINT goals_parent_not_self CHECK (parent_id <> id);",
                "  ALTER COLUMN title SET NOT NULL;",
            ),
        ],
        _pytest(f"{UJI_GOALS}::test_basis_data_menolak_goal_yang_menjadi_induk_dirinya"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "kedalaman pohon tidak diperiksa saat menulis — tingkat ke-11 diterima",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "                if jarak + 1 > MAKS_KEDALAMAN:",
                "                if jarak + 1 > MAKS_KEDALAMAN * 100:",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_pohon_lebih_dari_sepuluh_tingkat_ditolak_saat_menulis"),
        harus_memuat="goal tingkat ke-11 diterima",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "hapus-lunak tidak menaikkan anak menjadi akar",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                '        await conn.execute(_LEPAS_ANAK, {"id": goal_id})' + NL,
                "        pass" + NL,
            )
        ],
        _pytest(f"{UJI_GOALS}::test_hapus_lunak_menaikkan_anak_menjadi_akar"),
        harus_memuat="anak goal yang dihapus tidak naik menjadi akar",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "kursor bertanggal tanpa zona diterima",
        [
            Sunting(
                f"{MODUL}/platform/halaman.py",
                "        if saat.utcoffset() is None or not WAKTU_MIN",
                "        if saat.utcoffset() is not None and not WAKTU_MIN",
            )
        ],
        _pytest("tests/unit/test_halaman.py::test_kursor_rusak_menjadi_galat_400[tanpa-zona]"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "E-165",
        "rute tulis domain BARU tanpa `idem: platform.Idempoten`",
        [
            _sisip(
                f"{MODUL}/goals/routes.py",
                '@router.post("/goals/{goal_id}/mutasi", status_code=204)'
                + NL
                + "async def _mutasi(goal_id: UUID) -> None:"
                + NL
                + "    return None",
            )
        ],
        _pytest(f"{UJI_IDEM_RUTE}::test_tiap_rute_tulis_domain_menerima_idempotency_key"),
        harus_memuat="POST /v1/goals/{goal_id}/mutasi",
    ),
    Mutasi(
        "E-165",
        "kunci idempotensi tanpa user_id — jawaban A diputar ulang untuk B",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                '        return f"{self._awalan}:idem:{user_id}:{sidik_kunci}"',
                '        return f"{self._awalan}:idem:{sidik_kunci}"',
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kunci_yang_sama_milik_dua_pengguna_tidak_saling_memutar_ulang"),
        harus_memuat="jawaban pengguna A diputar ulang untuk B",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "kunci yang sama dengan badan lain diputar ulang diam-diam",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                '        if tersimpan.get("s") != self._sidik:'
                + NL
                + "            raise _dipakai_ulang()"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kunci_sama_dengan_badan_lain_422_bukan_diputar_ulang"),
        harus_memuat="kunci yang sama dengan badan lain diputar ulang",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "penanda 'sedang berjalan' tidak diperiksa — permintaan serentak semuanya menulis",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "local ada = redis.call('GET', KEYS[1])",
                "local ada = false",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_permintaan_serentak_dengan_kunci_sama_hanya_satu_yang_jalan"),
        harus_memuat="serentak:",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "galat 4xx disimpan sebagai jawaban — ulangan tidak pernah dijalankan lagi",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "        except BaseException:"
                + NL
                + "            await self._hapus(keys=[k], args=[penanda])"
                + NL
                + "            raise"
                + NL,
                "        except GalatApi as g:"
                + NL
                + '            await self._r.set(k, json.dumps({"s": self._sidik, "st": g.status, "id": "00000000-0000-0000-0000-000000000000"}))'
                + NL
                + "            raise"
                + NL,
            )
        ],
        _pytest(f"{UJI_IDEM}::test_galat_tidak_disimpan_sebagai_jawaban"),
        harus_memuat="galat disimpan sebagai jawaban",
        kelompok="db",
    ),
    # ── Sprint 2 · 2.2 habits + jadwal + adaptive_tiers ──────────────────
    Mutasi(
        "2.2",
        "energi rendah (2) diperlakukan normal — tier tidak turun",
        [
            Sunting(
                f"{MODUL}/habits/tier.py",
                "    if energi is None or energi > ENERGI_RENDAH:",
                "    if energi is None or energi >= ENERGI_RENDAH:",
            )
        ],
        _pytest("tests/unit/test_tier.py::test_tier_turun_saat_energi_rendah"),
        harus_memuat="tier tidak turun saat energi rendah",
    ),
    Mutasi(
        "2.2",
        "PATCH tidak memeriksa paduan period × target_count dengan baris tersimpan",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                '                periksa_target(period, perubahan.get("target_count", kini.target_count))'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_HABITS}::test_patch_yang_membuat_paduan_periode_tidak_sah_ditolak_422"),
        harus_memuat="paduan period × target_count yang tidak sah tersimpan",
        kelompok="db",
    ),
    Mutasi(
        "2.2",
        "habit harian boleh target 7 — satu tanggal hanya satu penyelesaian",
        [Sunting(f"{MODUL}/habits/schemas.py", '{"day": 1, ', '{"day": 7, ')],
        # Dipatok ke kasusnya: `assert 201 == 400` cocok dengan parameter mana pun.
        _pytest(f"{UJI_HABITS}::test_habit_berbentuk_salah_ditolak_400[badan0]"),
        harus_memuat="assert 201 == 400",
        kelompok="db",
    ),
    # ── Sprint 2 · 2.3 habit_completions + idempotensi tanggal ───────────
    Mutasi(
        "2.3",
        # Kirim ulang BERURUTAN kini menemukan baris lamanya sebelum INSERT (E-173);
        # yang dijaga ON CONFLICT tinggal dua catatan SERENTAK di celah keduanya.
        "INSERT penyelesaian tanpa ON CONFLICT — catatan serentak tanggal sama menjadi galat",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                "    ON CONFLICT (habit_id, for_date) DO NOTHING" + NL,
                "",
            )
        ],
        # Deterministik: B menyisip saat INSERT A belum commit — bukan untung-untungan
        # jadwal event loop (uji serentak lewat HTTP berbunyi satu putaran, diam
        # putaran berikutnya — tinjauan penegak buta Sprint 2).
        _pytest(f"{UJI_SELESAI}::test_dua_transaksi_menyisip_tanggal_sama_yang_kedua_tanpa_galat"),
        harus_memuat="UniqueViolationError",
        kelompok="db",
    ),
    Mutasi(
        "2.3",
        "tier_used tidak dicocokkan dengan adaptive_tiers habit",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        if badan.tier_used is not None and badan.tier_used >= len(habit.adaptive_tiers):",
                "        if badan.tier_used is not None and badan.tier_used > 99:",
            )
        ],
        _pytest(f"{UJI_SELESAI}::test_tier_di_luar_adaptive_tiers_ditolak_422"),
        harus_memuat="tier di luar adaptive_tiers tersimpan",
        kelompok="db",
    ),
    Mutasi(
        "2.3",
        "for_date masa depan tidak diperiksa",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        if badan.for_date > await platform.tanggal_paling_maju(conn):",
                "        if badan.for_date > date.max:",
            )
        ],
        _pytest(f"{UJI_SELESAI}::test_tanggal_yang_belum_terjadi_di_mana_pun_ditolak"),
        harus_memuat="tanggal masa depan tersimpan",
        kelompok="db",
    ),
    Mutasi(
        "2.3",
        "batas for_date memakai zona paling BELAKANG — hari ini di UTC+14 ditolak",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        if badan.for_date > await platform.tanggal_paling_maju(conn):",
                '        if badan.for_date > await platform.hari_ini_di(conn, "Pacific/Pago_Pago"):',
            )
        ],
        _pytest(f"{UJI_SELESAI}::test_tanggal_yang_belum_terjadi_di_mana_pun_ditolak"),
        harus_memuat="tanggal hari ini di UTC+14 ditolak untuk pengguna UTC−11",
        kelompok="db",
    ),
    # ── Sprint 2 · 2.4 rentetan melintasi zona waktu ─────────────────────
    Mutasi(
        "2.4",
        "hari ini dihitung di UTC, bukan di zona profil",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        hari_ini = await platform.hari_ini_di(conn, zona)",
                '        hari_ini = await platform.hari_ini_di(conn, "UTC")',
            )
        ],
        _pytest(f"{UJI_RENTETAN}::test_hari_ini_menurut_zona_profil_bukan_utc"),
        harus_memuat="hari ini bukan menurut zona profil",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "rentetan dari tanggal completed_at (UTC), bukan for_date",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                "    SELECT for_date, status\n",
                "    SELECT (completed_at AT TIME ZONE 'UTC')::date AS for_date, status\n",
            )
        ],
        _pytest(f"{UJI_RENTETAN}::test_rentetan_dari_for_date_bukan_dari_waktu_dicatat"),
        harus_memuat="rentetan dihitung dari waktu catat",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "skipped memutus rentetan",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                '            if status == "skipped":' + NL + '                return "dimaafkan"',
                '            if status == "skipped":' + NL + '                return "kosong"',
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py::test_skipped_netral_tidak_menambah_dan_tidak_memutus"
        ),
        harus_memuat="skipped memutus rentetan",
    ),
    Mutasi(
        "2.4",
        "hari ini yang belum dijalankan dihitung terlewat",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                '        return "belum" if p >= periode_kini else "kosong"',
                '        return "belum" if p > periode_kini else "kosong"',
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py"
            "::test_hari_ini_yang_belum_dijalankan_tidak_memutus_rentetan"
        ),
        harus_memuat="hari ini yang belum berakhir memutus rentetan",
    ),
    Mutasi(
        "2.4",
        "schedule.weekdays diabaikan — hari tak terjadwal ikut dihitung",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                "            if terjadwal is not None and p.isoweekday() not in terjadwal:",
                "            if False:",
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py::test_jadwal_hari_terjadwal_yang_terlewat_memutus"
        ),
        harus_memuat="penyelesaian hari Selasa menutupi Rabu yang terlewat",
    ),
    Mutasi(
        "2.4",
        "titik rakit tidak memasang pembaca zona waktu profil (K-23)",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.state.pembaca_zona_waktu = profile.zona_waktu" + NL,
                "",
            )
        ],
        _pytest("tests/unit/test_main.py::test_titik_rakit_memasang_pembaca_lintas_modul"),
        harus_memuat="hvx.main tidak memasang pembaca_zona_waktu dari profile",
    ),
    # ── Sprint 2 · 2.5 daily_checkins (upsert per tanggal) + tier dari energi ─
    Mutasi(
        "2.5",
        "check-in tanpa ON CONFLICT — PUT kedua menjadi galat",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "    ON CONFLICT (user_id, for_date) DO UPDATE SET"
                + NL
                + "      energy = EXCLUDED.energy,"
                + NL
                + "      focus = EXCLUDED.focus,"
                + NL
                + "      sleep_hours = EXCLUDED.sleep_hours,"
                + NL
                + "      note = EXCLUDED.note"
                + NL
                + "    WHERE (daily_checkins.energy, daily_checkins.focus, daily_checkins.sleep_hours,"
                + NL
                + "           daily_checkins.note)"
                + NL
                + "          IS DISTINCT FROM (EXCLUDED.energy, EXCLUDED.focus, EXCLUDED.sleep_hours,"
                + NL
                + "                            EXCLUDED.note)"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_put_dua_kali_satu_baris"),
        harus_memuat="PUT kedua bukan 200",
        kelompok="db",
    ),
    Mutasi(
        "2.5",
        "PUT check-in menambal (COALESCE), bukan mengganti",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "      energy = EXCLUDED.energy,",
                "      energy = COALESCE(EXCLUDED.energy, daily_checkins.energy),",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_put_mengganti_medan_yang_tidak_dikirim_menjadi_kosong"),
        harus_memuat="PUT menambal, bukan mengganti",
        kelompok="db",
    ),
    Mutasi(
        "2.2",
        "tier yang disarankan tidak membaca energi check-in",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "suggested_tier=tier_untuk_energi(len(h.adaptive_tiers), energi),",
                "suggested_tier=tier_untuk_energi(len(h.adaptive_tiers), None),",
            )
        ],
        _pytest(f"{UJI_HARI}::test_tier_turun_saat_energi_rendah"),
        harus_memuat="tier tidak turun saat energi rendah",
        kelompok="db",
    ),
    Mutasi(
        "2.5",
        "titik rakit tidak memasang pembaca energi check-in (K-23)",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.state.pembaca_energi = checkins.energi_pada" + NL,
                "",
            )
        ],
        _pytest("tests/unit/test_main.py::test_titik_rakit_memasang_pembaca_lintas_modul"),
        harus_memuat="hvx.main tidak memasang pembaca_energi dari checkins",
    ),
    # ── Sprint 2 · 2.6 mood_entries ──────────────────────────────────────
    Mutasi(
        "2.6",
        "occurred_at mood di masa depan tidak diperiksa",
        [
            Sunting(
                f"{MODUL}/checkins/service.py",
                "            if badan.occurred_at is not None and badan.occurred_at > (",
                # `False and …`, bukan `is None and …`: yang kedua menambah jalur
                # TypeError (`None > datetime`) — mutasinya tidak bersih.
                "            if False and badan.occurred_at is not None and badan.occurred_at > (",
            )
        ],
        _pytest(
            f"{UJI_MOOD}"
            "::test_mood_di_masa_depan_ditolak_tetapi_jam_perangkat_sedikit_maju_diterima"
        ),
        harus_memuat="mood masa depan tersimpan",
        kelompok="db",
    ),
    Mutasi(
        "2.6",
        "kursor mood inklusif — baris batas halaman terulang",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "           OR (occurred_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))",
                "           OR (occurred_at, id) <= (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))",
            )
        ],
        _pytest(f"{UJI_MOOD}::test_halaman_berkursor_tanpa_ganda_dan_rentang_waktu"),
        harus_memuat="halaman mood mengulang atau melompati baris",
        kelompok="db",
    ),
    Mutasi(
        "2.6",
        "`to` rentang mood inklusif",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "OR occurred_at < CAST(:sampai AS timestamptz))",
                "OR occurred_at <= CAST(:sampai AS timestamptz))",
            )
        ],
        _pytest(f"{UJI_MOOD}::test_halaman_berkursor_tanpa_ganda_dan_rentang_waktu"),
        harus_memuat="`to` tidak eksklusif",
        kelompok="db",
    ),
    # ── Sprint 2 · 2.7 layar V0 pertama (Flutter, apps/mobile) ───────────
    Mutasi(
        "2.7",
        "pembuatan habit dengan Idempotency-Key acak BARU per percobaan (F19)",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "      kunciIdempotensi: id,",
                "      kunciIdempotensi: idBaru(),",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_ID_SAMA),
        harus_memuat=_UJI_ID_SAMA + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "layar tidak mengirim tier yang dipilih pengguna",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "      () => widget.layanan.tandaiSelesai(h.id, _tanggal, tier: tier),",
                "      () => widget.layanan.tandaiSelesai(h.id, _tanggal, tier: null),",
            )
        ],
        _flutter_uji(
            "test/layar/habit_hari_ini_test.dart",
            "habit bertier: saran dari energi ditampilkan beserta alasannya, tier dipilih",
        ),
        harus_memuat="tier dipilih [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "energi disimpan tanpa medan check-in lama — PUT mengganti, fokus & tidur hilang",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "    final badan = lama?.keJsonDenganEnergi(energi) ?? {'energy': energi};",
                "    final badan = {'energy': energi};",
            )
        ],
        _flutter_uji(
            "test/api/klien_test.dart",
            "simpan energi mengirim check-in UTUH — PUT mengganti, medan lama ikut",
        ),
        harus_memuat="medan lama ikut [E]",
        cwd=APLIKASI,
    ),
    # ── Tinjauan Sprint 2 · E-170 masukan ketat (F4 · F5 · F6 · rentang S5/S6) ─
    Mutasi(
        "E-170",
        "platform.Bulat longgar — `true` diterima sebagai 1",
        [
            Sunting(
                f"{MODUL}/platform/masukan.py", "Bulat = Annotated[int, Strict()]", "Bulat = int"
            )
        ],
        _pytest(f"{UJI_KETAT_RUTE}::test_badan_kueri_dan_jalur_tidak_mengoersi_diam_diam"),
        harus_memuat="masukan yang dikoersi diam-diam",
    ),
    Mutasi(
        "E-170",
        "platform.Benar longgar — persetujuan dari string 'on'",
        [
            Sunting(
                f"{MODUL}/platform/masukan.py", "Benar = Annotated[bool, Strict()]", "Benar = bool"
            )
        ],
        _pytest(f"{UJI_KETAT_RUTE}::test_badan_kueri_dan_jalur_tidak_mengoersi_diam_diam"),
        harus_memuat="consents.terms",
    ),
    Mutasi(
        "E-170",
        "medan skala check-in kembali `int` biasa",
        [
            Sunting(
                f"{MODUL}/checkins/schemas.py",
                "Skala = Annotated[platform.Bulat, Field(ge=1, le=5)]",
                "Skala = Annotated[int, Field(ge=1, le=5)]",
            )
        ],
        _pytest(f"{UJI_KETAT_RUTE}::test_badan_kueri_dan_jalur_tidak_mengoersi_diam_diam"),
        harus_memuat="badan.energy",
    ),
    Mutasi(
        "E-170",
        "platform.Tanggal tanpa penjaga ISO — detik Unix menjadi tanggal UTC",
        [
            Sunting(
                f"{MODUL}/platform/masukan.py",
                "Tanggal = Annotated[date, BeforeValidator(_tanggal_iso), "
                "AfterValidator(_tanggal_dalam_rentang)]",
                "Tanggal = Annotated[date, AfterValidator(_tanggal_dalam_rentang)]",
            )
        ],
        _pytest(f"{UJI_KETAT_RUTE}::test_badan_kueri_dan_jalur_tidak_mengoersi_diam_diam"),
        harus_memuat="tanpa platform.Tanggal/WaktuBerzona",
    ),
    Mutasi(
        "E-170",
        "rentang tanggal tidak diperiksa — 0001-01-01 tersimpan sebagai -infinity",
        [
            Sunting(
                f"{MODUL}/platform/masukan.py",
                "    if not TANGGAL_MIN <= nilai <= TANGGAL_MAKS:",
                "    if False:",
            )
        ],
        _pytest(f"{UJI_KETAT_RUTE}::test_tanggal_hanya_string_iso_dalam_rentang"),
        harus_memuat="diterima: '0001-01-01'",
    ),
    Mutasi(
        "E-170",
        "tier_used dibatasi skema lagi — tier 7 menjadi 400, tier 3 menjadi 422 (F5)",
        [
            Sunting(
                f"{MODUL}/habits/schemas.py",
                "    tier_used: platform.Bulat | None = Field(default=None, ge=0)",
                "    tier_used: platform.Bulat | None = Field(default=None, ge=0, le=TIER_MAKS - 1)",
            )
        ],
        _pytest(f"{UJI_KETAT}::test_tier_di_luar_adaptive_tiers_selalu_422_invalid_tier"),
        harus_memuat="tier di luar adaptive_tiers dijawab",
        kelompok="db",
    ),
    Mutasi(
        "E-170",
        "sleep_hours keluar sebagai string desimal lagi (F6)",
        [
            Sunting(
                f"{MODUL}/checkins/schemas.py",
                "from datetime import date, datetime" + NL,
                "from datetime import date, datetime" + NL + "from decimal import Decimal" + NL,
            ),
            Sunting(
                f"{MODUL}/checkins/schemas.py",
                "    sleep_hours: float | None",
                "    sleep_hours: Decimal | None",
            ),
        ],
        _pytest(f"{UJI_KETAT}::test_jam_tidur_angka_json_masuk_dan_keluar"),
        harus_memuat="'7.5' == 7.5",
        kelompok="db",
    ),
    # ── E-171 Idempotency-Key: rujukan, kuota, sf-string · batas badan ────────
    Mutasi(
        "E-171",
        "badan jawaban utuh disimpan di Redis lagi (S1 · S3)",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                '            rujukan = {"s": self._sidik, "st": hasil.status, "id": str(hasil.rujukan)}',
                '            rujukan = {"s": self._sidik, "st": hasil.status, "id": str(hasil.rujukan),'
                ' "badan": jsonable_encoder(hasil.isi)}',
            )
        ],
        _pytest(f"{UJI_IDEM}::test_redis_hanya_menyimpan_rujukan_tanpa_isi_tulisan"),
        harus_memuat="Rahasia",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "kuota kunci per pengguna tidak ditegakkan",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "if n > tonumber(ARGV[3]) then",
                "if false then",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kuota_kunci_per_pengguna_429_dan_ulangan_tetap_jalan"),
        harus_memuat="kuota kunci tidak ditegakkan",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "ulangan kunci lama ikut memakai kuota — tulisan yang sudah terjadi ditolak 429",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "local ada = redis.call('GET', KEYS[1])" + NL + "if ada then" + NL,
                "local ada = redis.call('GET', KEYS[1])"
                + NL
                + "local n0 = redis.call('INCR', KEYS[2])"
                + NL
                + "if ada and n0 <= tonumber(ARGV[3]) then"
                + NL,
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kuota_kunci_per_pengguna_429_dan_ulangan_tetap_jalan"),
        harus_memuat="ulangan kunci LAMA ikut terhitung kuota",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "kunci sf-string bertanda kutip tidak dinormalkan (F12)",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "    if kunci is not None and len(kunci) >= 2 and kunci[0] == kunci[-1] == '\"':",
                "    if False:",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kunci_sf_string_bertanda_kutip_sama_dengan_telanjang"),
        harus_memuat="kunci bertanda kutip dan telanjang dianggap kunci berbeda",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "RecursionError JSON bersarang tidak ditangkap saat menyidik — 500",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "    except (ValueError, UnicodeDecodeError, RecursionError):",
                "    except (ValueError, UnicodeDecodeError):",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_badan_bersarang_dalam_bukan_json_tidak_500"),
        harus_memuat="badan bersarang dalam dijawab 500",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "batas ukuran badan tidak dipasang titik rakit — 1 MiB+ dibaca sebelum autentikasi",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.add_middleware(platform.BatasBadanMiddleware)" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_KETAT}::test_badan_terlalu_besar_413_sebelum_autentikasi"),
        harus_memuat="badan 1 MiB+ tidak ditolak 413",
        kelompok="db",
    ),
    Mutasi(
        "E-171",
        "badan chunked tidak dihitung — batas ukuran dilewati tanpa Content-Length",
        [
            Sunting(
                f"{MODUL}/platform/batas_badan.py",
                "            if terbaca > self.maks:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_BADAN}::test_chunked_di_atas_batas_413"),
        harus_memuat="badan chunked di atas batas dijawab",
    ),
    Mutasi(
        "E-171",
        "rute menyatakan Idempotency-Key tetapi tidak memanggil jalankan (D4)",
        [
            Sunting(
                f"{MODUL}/goals/routes.py",
                "    return await idem.jalankan("
                + NL
                + "        pengguna.user_id, kerja, partial(service.baca_goal, engine, pengguna.user_id)"
                + NL
                + "    )"
                + NL
                + NL
                + NL
                + '@router.get("/goals/{goal_id}"',
                "    hasil = await kerja()"
                + NL
                + "    return JSONResponse(status_code=hasil.status, content=hasil.isi.model_dump(mode='json'))"
                + NL
                + NL
                + NL
                + '@router.get("/goals/{goal_id}"',
            )
        ],
        _pytest(f"{UJI_IDEM_RUTE}::test_rute_yang_menyatakan_idempotensi_juga_memanggil_jalankan"),
        harus_memuat="rute menyatakan Idempotency-Key tanpa memanggil jalankan",
    ),
    # ── E-172 balapan & batas (F1 · F2 · F9 · F13 · S2) ────────────────────────
    Mutasi(
        "E-172",
        "induk/goal tidak dikunci FOR SHARE — anak yang dibuat serentak dengan hapus induk yatim",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                '_KUNCI_HIDUP = text("SELECT id FROM goals WHERE id = :id AND deleted_at IS NULL FOR SHARE")',
                '_KUNCI_HIDUP = text("SELECT id FROM goals WHERE id = :id AND deleted_at IS NULL")',
            )
        ],
        _pytest(f"{UJI_BALAPAN}::test_anak_yang_dibuat_serentak_dengan_hapus_induk_tidak_yatim"),
        harus_memuat="goal hidup berinduk goal terhapus",
        kelompok="db",
    ),
    Mutasi(
        "E-172",
        "habit menaut goal tanpa memeriksa hidupnya — FK tidak melihat hapus-lunak (F2)",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "            if badan.goal_id is not None and not await goal_hidup(conn, badan.goal_id):",
                "            if False:",
            )
        ],
        _pytest(
            f"{UJI_BALAPAN}::test_goal_terhapus_tidak_bisa_ditaut_dan_hapus_goal_melepas_habitnya"
        ),
        harus_memuat="habit baru ditaut ke goal yang sudah dihapus",
        kelompok="db",
    ),
    Mutasi(
        "E-172",
        "hapus goal tidak melepas habit yang menautnya (K-23)",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.state.pendengar_goal_dihapus = (habits.lepas_goal,)",
                "    app.state.pendengar_goal_dihapus = ()",
            )
        ],
        _pytest("tests/unit/test_main.py::test_titik_rakit_memasang_pembaca_lintas_modul"),
        harus_memuat="hapus goal tidak melepas habit yang menautnya",
    ),
    Mutasi(
        "E-172",
        "batas goal per pengguna tidak ditegakkan (K-24)",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "            if await repository.jumlah_goal_serial(conn, user_id) >= MAKS_GOAL:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_BALAPAN}::test_batas_goal_per_pengguna_ditegakkan_serial"),
        harus_memuat="batas goal dilewati",
        kelompok="db",
    ),
    Mutasi(
        "E-172",
        "batas habit dihitung tanpa kunci — tulisan serentak bersama melewatinya (F9)",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                '    await conn.execute(_KUNCI_HITUNG, {"kunci": f"habits:{user_id}"})' + NL,
                "",
            )
        ],
        _pytest(f"{UJI_BALAPAN}::test_batas_habit_per_pengguna_dan_daftar_tidak_terpotong"),
        harus_memuat="batas habit dilewati",
        kelompok="db",
    ),
    Mutasi(
        "E-172",
        "batas milestone per goal tidak ditegakkan",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "            if await repository.jumlah_milestone_serial(conn, goal_id) >= MAKS_MILESTONE:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_BALAPAN}::test_batas_milestone_per_goal"),
        harus_memuat="batas milestone dilewati",
        kelompok="db",
    ),
    Mutasi(
        "E-172",
        "id milestone buatan klien diabaikan (F13)",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "    SELECT COALESCE(CAST(:id AS uuid), gen_random_uuid()), g.id, g.user_id, :title,",
                "    SELECT gen_random_uuid(), g.id, g.user_id, :title,",
            )
        ],
        _pytest(f"{UJI_BALAPAN}::test_milestone_dengan_id_buatan_klien_dan_id_sama_409"),
        harus_memuat="id milestone buatan klien diabaikan",
        kelompok="db",
    ),
    # ── E-173 arti rentetan & kirim ulang (F3 · F7 · F8) ──────────────────────
    Mutasi(
        "E-173",
        "skipped diabaikan pada habit mingguan — minggu yang dimaafkan memutus (F7)",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                "            if maaf_per_periode[p] and penuh + maaf_per_periode[p] >= target_count:",
                "            if False:",
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py"
            "::test_mingguan_skipped_memaafkan_satu_kali_dan_tidak_memutus"
        ),
        harus_memuat="skipped memutus rentetan mingguan",
    ),
    Mutasi(
        "E-173",
        "hari sebelum habit dibuat masuk penyebut sebagai gagal (F8)",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                '        elif k == "kosong" and p >= mulai:',
                '        elif k == "kosong":',
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py"
            "::test_tingkat_hari_sebelum_habit_dibuat_hanya_dihitung_bila_terpenuhi"
        ),
        harus_memuat="hari sebelum habit ada dihitung gagal",
    ),
    Mutasi(
        "E-173",
        "tier diperiksa sebelum baris lama dicari — kirim ulang ditolak 422 (F3)",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        ada = await repository.selesai_pada(conn, habit_id, badan.for_date)"
                + NL
                + "        if ada is not None:"
                + NL
                + "            return HasilCatat(ada, baru=False)"
                + NL
                + "        if badan.tier_used",
                "        if badan.tier_used",
            )
        ],
        _pytest(
            f"{UJI_BALAPAN}::test_kirim_ulang_sesudah_tier_habit_dikurangi_tetap_200_baris_lama"
        ),
        harus_memuat="kirim ulang sesudah tier dikurangi",
        kelompok="db",
    ),
    # ── E-174 galat validasi · kursor · zona waktu ───────────────────────────
    Mutasi(
        "E-174",
        "pesan galat pydantic diteruskan apa adanya — uuid_parsing mengutip masukan",
        [
            Sunting(
                f"{MODUL}/platform/galat.py",
                '                "msg": g.get("msg") if jenis in _PESAN_AMAN else _PESAN_TETAP,',
                '                "msg": g.get("msg"),',
            )
        ],
        _pytest("tests/unit/test_galat.py::test_uuid_salah_tidak_mengutip_karakter_masukan"),
        harus_memuat="pesan galat mengutip masukan",
    ),
    Mutasi(
        "E-174",
        "loc galat memuat nama kunci dari klien",
        [
            Sunting(
                f"{MODUL}/platform/galat.py",
                '            bagian if isinstance(bagian, int) or bagian in dikenal else "*"',
                "            bagian",
            )
        ],
        _pytest("tests/unit/test_galat.py::test_kunci_tak_dikenal_tidak_dipantulkan_di_loc"),
        harus_memuat="loc galat memantulkan nama kunci dari klien",
    ),
    Mutasi(
        "E-174",
        "bentuk kursor tidak diperiksa — id angka menjadi AttributeError 500",
        [
            Sunting(
                f"{MODUL}/platform/halaman.py",
                "    if not (isinstance(isi, list) and len(isi) == 3 and all(isinstance(x, str) for x in isi)):",
                "    if not isinstance(isi, list) or len(isi) != 3:",
            )
        ],
        _pytest("tests/unit/test_halaman.py::test_kursor_rusak_menjadi_galat_400[id-angka]"),
        harus_memuat="AttributeError",
    ),
    Mutasi(
        "E-174",
        "kursor daftar lain diterima (D5)",
        [Sunting(f"{MODUL}/platform/halaman.py", "    if jenis_kursor != jenis:", "    if False:")],
        _pytest("tests/unit/test_halaman.py::test_kursor_daftar_lain_ditolak"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "E-174",
        "zona semu `Factory` diterima sebagai zona waktu pengguna",
        [
            Sunting(
                f"{MODUL}/platform/zona_waktu.py",
                "    return frozenset(daftar.split()) - _BUKAN_ZONA_PENGGUNA",
                "    return frozenset(daftar.split())",
            )
        ],
        _pytest(
            "tests/unit/test_zona_waktu.py"
            "::test_bukan_nama_iana_ditolak_tanpa_memantulkan_masukan[Factory]"
        ),
        harus_memuat="DID NOT RAISE",
    ),
    # ── E-175 klien Flutter (S4 · S8/F19 · D5) ─────────────────────────────────
    Mutasi(
        "E-175",
        "penyegaran token per permintaan — 401 serentak memakai token segar yang sudah dirotasi",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "      _penyegaran ??= _segarkanSekali().whenComplete(() => _penyegaran = null);",
                "      _segarkanSekali();",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_SERENTAK),
        harus_memuat=_UJI_SERENTAK + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "E-175",
        "dialog membuat id habit baru tiap ketukan Simpan — coba lagi membuat habit kedua",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "        id: _idUntuk(jsonEncode(isi)),",
                "        id: idBaru() + jsonEncode(isi).substring(0, 0),",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_DIALOG_ID),
        harus_memuat=_UJI_DIALOG_ID + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "E-175",
        "habit yang dilewati diketuk → POST done yang tidak mengubah apa pun (D5)",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "    if (h.tercatatHariItu) {",
                "    if (h.selesaiHariItu) {",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_DILEWATI),
        harus_memuat=_UJI_DILEWATI + " [E]",
        cwd=APLIKASI,
    ),
    # ── E-176 kontrak kecil (F11) ─────────────────────────────────────────────
    Mutasi(
        "E-176",
        "PUT check-in identik menulis ulang baris — updated_at bergeser (F11)",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "    WHERE (daily_checkins.energy, daily_checkins.focus, daily_checkins.sleep_hours,"
                + NL
                + "           daily_checkins.note)"
                + NL
                + "          IS DISTINCT FROM (EXCLUDED.energy, EXCLUDED.focus, EXCLUDED.sleep_hours,"
                + NL
                + "                            EXCLUDED.note)"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_put_identik_tidak_menulis_ulang_baris"),
        harus_memuat="PUT identik menggeser updated_at",
        kelompok="db",
    ),
    # ── Tinjauan PENEGAK BUTA Sprint 2 — mutasi yang dulu lolos seluruh suite ──
    Mutasi(
        "2.1",
        "pohon memuat keturunan yang dihapus-lunak",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "      WHERE c.deleted_at IS NULL AND p.kedalaman < :batas",
                "      WHERE p.kedalaman < :batas",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_pohon_tidak_memuat_keturunan_yang_dihapus"),
        harus_memuat="goal terhapus ikut di pohon",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "pohon dibaca 3 tingkat — tingkat ke-4…10 dipotong diam-diam",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "        baris = await repository.pohon(conn, goal_id, MAKS_KEDALAMAN)",
                "        baris = await repository.pohon(conn, goal_id, 2)",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_pohon_sepuluh_tingkat_terbaca_utuh"),
        harus_memuat="pohon dipotong diam-diam saat dibaca",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "anak pohon diurutkan menurut judul, bukan waktu dibuat",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "    ORDER BY kedalaman, created_at, id",
                "    ORDER BY kedalaman, title, id",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_anak_pohon_menurut_waktu_dibuat_bukan_judul"),
        harus_memuat="urutan anak pohon bukan urutan dibuat",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "PATCH goal yang sudah dihapus-lunak berhasil",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "      SELECT id, status FROM goals WHERE id = :id AND deleted_at IS NULL FOR UPDATE",
                "      SELECT id, status FROM goals WHERE id = :id FOR UPDATE",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_goal_terhapus_tidak_bisa_diubah_dan_milestonenya_404"),
        harus_memuat="PATCH goal terhapus",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "PATCH {} milestone dari goal terhapus menjawab 200",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "    WHERE m.id = :id AND g.deleted_at IS NULL",
                "    WHERE m.id = :id",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_goal_terhapus_tidak_bisa_diubah_dan_milestonenya_404"),
        harus_memuat="PATCH {} milestone goal terhapus",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "milestone baru di goal terhapus — syarat goal hidup dicabut di kedua lapis",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "            if not await repository.kunci_hidup(conn, goal_id):",
                "            if False:",
            ),
            Sunting(
                f"{MODUL}/goals/repository.py",
                "    WHERE g.id = :goal_id AND g.deleted_at IS NULL",
                "    WHERE g.id = :goal_id",
            ),
        ],
        _pytest(f"{UJI_GOALS}::test_goal_terhapus_tidak_bisa_diubah_dan_milestonenya_404"),
        harus_memuat="milestone baru di goal terhapus",
        kelompok="db",
    ),
    Mutasi(
        "2.1",
        "kursor daftar goal tanpa pemecah seri id — goal ber-created_at sama dilompati",
        [
            Sunting(
                f"{MODUL}/goals/repository.py",
                "           OR (created_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))",
                "           OR created_at < CAST(:k_waktu AS timestamptz))",
            )
        ],
        _pytest(f"{UJI_GOALS}::test_halaman_goal_dengan_created_at_kembar_tidak_melompat"),
        harus_memuat="goal kembar dilompati",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "sidik permintaan tanpa JALUR — kunci & badan sama di rute lain diputar ulang",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                '    return "\\x00".join((metode, jalur, kueri, isi))',
                '    return "\\x00".join((metode, kueri, isi))',
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kunci_dan_badan_sama_di_rute_lain_bukan_ulangan"),
        harus_memuat="rute lain diputar ulang",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "POST /habits menjalankan kerja langsung — Idempotency-Key diterima lalu diabaikan",
        [
            Sunting(
                f"{MODUL}/habits/routes.py",
                "    return await idem.jalankan("
                + NL
                + "        pengguna.user_id, kerja, partial(service.baca_habit, engine, pengguna.user_id)"
                + NL
                + "    )"
                + NL
                + NL
                + NL
                + '@router.patch("/habits/{habit_id}"',
                "    hasil = await kerja()"
                + NL
                + "    return JSONResponse(status_code=hasil.status, content=hasil.isi.model_dump(mode='json'))"
                + NL
                + NL
                + NL
                + '@router.patch("/habits/{habit_id}"',
            )
        ],
        _pytest(f"{UJI_IDEM}::test_kunci_sama_di_post_habits_satu_baris"),
        harus_memuat="Idempotency-Key diabaikan: habit ganda",
        kelompok="db",
    ),
    Mutasi(
        "E-165",
        "rujukan idempoten diingat 60 detik, bukan 24 jam",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "                await self._r.set(k, json.dumps(rujukan), ex=UMUR_JAWABAN_S)",
                "                await self._r.set(k, json.dumps(rujukan), ex=_UMUR_PROSES_S)",
            )
        ],
        _pytest(f"{UJI_IDEM}::test_rujukan_diingat_dua_puluh_empat_jam"),
        harus_memuat="rujukan idempoten hanya diingat",
        kelompok="db",
    ),
    Mutasi(
        "2.2",
        "PATCH habit tidak memeriksa jadwal TERSIMPAN terhadap period baru",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                '                periksa_jadwal(period, perubahan.get("schedule", kini.schedule))',
                '                periksa_jadwal(period, perubahan.get("schedule", {}))',
            )
        ],
        _pytest(
            f"{UJI_HABITS}::test_patch_jadwal_dan_periode_diperiksa_terhadap_baris_tersimpan"
            "[awal0-ubah0]"
        ),
        harus_memuat="paduan jadwal × periode tak sah diterima",
        kelompok="db",
    ),
    Mutasi(
        "2.2",
        "PATCH habit tanpa periksa_jadwal sama sekali",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                '                periksa_jadwal(period, perubahan.get("schedule", kini.schedule))'
                + NL,
                "",
            )
        ],
        _pytest(
            f"{UJI_HABITS}::test_patch_jadwal_dan_periode_diperiksa_terhadap_baris_tersimpan"
            "[awal1-ubah1]"
        ),
        harus_memuat="paduan jadwal × periode tak sah diterima",
        kelompok="db",
    ),
    Mutasi(
        "2.2",
        "energi rendah pada habit 2 tier tetap menyarankan versi penuh",
        [
            Sunting(
                f"{MODUL}/habits/tier.py",
                "        return min(1, jumlah_tier - 1)",
                "        return jumlah_tier // 3",
            )
        ],
        _pytest("tests/unit/test_tier.py::test_dua_dan_empat_tier_pada_energi_rendah"),
        harus_memuat="[0, 0, 0, 1] == [0, 0, 1, 1]",
    ),
    Mutasi(
        "2.2",
        "habit ber-for_date membaca penyelesaian satu kueri per habit (N+1)",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        selesai = await repository.selesai_tanggal(conn, user_id, for_date)",
                "        selesai = {"
                + NL
                + "            h.id: p"
                + NL
                + "            for h in habit"
                + NL
                + "            if (p := await repository.selesai_pada(conn, h.id, for_date))"
                + NL
                + "        }",
            )
        ],
        _pytest(f"{UJI_HARI}::test_habit_ber_for_date_jumlah_kueri_tidak_tumbuh_bersama_habit"),
        harus_memuat="N+1:",
        kelompok="db",
    ),
    Mutasi(
        "2.3",
        "tanggal paling maju ditanyakan ke UTC, bukan UTC+14 — lolos HTTP pukul 00–09 UTC",
        [
            Sunting(
                f"{MODUL}/platform/zona_waktu.py",
                'ZONA_PALING_MAJU = "Pacific/Kiritimati"',
                'ZONA_PALING_MAJU = "UTC"',
            )
        ],
        _pytest(
            "tests/unit/test_zona_waktu.py"
            "::test_tanggal_paling_maju_bertanya_ke_zona_berselisih_terbesar"
        ),
        harus_memuat="tanggal paling maju ditanyakan ke UTC",
    ),
    Mutasi(
        "2.5",
        "batas for_date check-in `>=` — hari ini di UTC+14 ditolak",
        [
            Sunting(
                f"{MODUL}/checkins/service.py",
                "        if for_date > await platform.tanggal_paling_maju(conn):",
                "        if for_date >= await platform.tanggal_paling_maju(conn):",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_check_in_hari_ini_di_zona_paling_maju_diterima"),
        harus_memuat="hari ini di UTC+14 ditolak",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "layanan rentetan tidak meneruskan schedule.weekdays",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                '        weekdays=habit.schedule.get("weekdays"),',
                "        weekdays=None,",
            )
        ],
        _pytest(f"{UJI_RENTETAN}::test_rentetan_lewat_http_mengikuti_hari_terjadwal"),
        harus_memuat="layanan tidak meneruskan schedule.weekdays",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "layanan rentetan memakai hari ini sebagai awal habit",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        mulai = await repository.mulai_lokal(conn, habit_id, zona) or hari_ini",
                "        mulai = hari_ini",
            )
        ],
        _pytest(f"{UJI_RENTETAN}::test_tingkat_menghitung_hari_sejak_habit_dibuat"),
        harus_memuat="awal habit diabaikan",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "tanggal awal habit dihitung di UTC, bukan zona profil",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                "    SELECT (created_at AT TIME ZONE :zona)::date",
                "    SELECT (created_at AT TIME ZONE COALESCE(NULLIF(:zona, :zona), 'UTC'))::date",
            )
        ],
        _pytest(f"{UJI_RENTETAN}::test_awal_habit_menurut_zona_profil_bukan_utc"),
        harus_memuat="awal habit di UTC",
        kelompok="db",
    ),
    Mutasi(
        "2.4",
        "awal rentetan = catatan pertama — awal habit diabaikan",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                "    awal = max(min([mulai, *penyelesaian]), hari_ini - timedelta(days=RIWAYAT_MAKS_HARI))",
                "    awal = max(min(penyelesaian, default=mulai), hari_ini - timedelta(days=RIWAYAT_MAKS_HARI))",
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py"
            "::test_awal_habit_lebih_awal_dari_catatan_pertama_tetap_dihitung"
        ),
        harus_memuat="awal habit diganti catatan pertama",
    ),
    Mutasi(
        "2.4",
        "riwayat rentetan dipotong 90 hari — rentetan terpanjang lama terpotong",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py", "RIWAYAT_MAKS_HARI = 3660", "RIWAYAT_MAKS_HARI = 90"
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py"
            "::test_terpanjang_dari_riwayat_berbulan_bulan_tetap_terhitung"
        ),
        harus_memuat="rentetan terpanjang 250 hari lalu terpotong",
    ),
    Mutasi(
        "2.4",
        "batas riwayat dicabut — satu for_date tahun 1900 menelusuri 46 ribu hari",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py",
                "    awal = max(min([mulai, *penyelesaian]), hari_ini - timedelta(days=RIWAYAT_MAKS_HARI))",
                "    awal = min([mulai, *penyelesaian])",
            )
        ],
        _pytest("tests/unit/test_rentetan_murni.py::test_riwayat_lama_ditelusuri_terbatas"),
        harus_memuat="langkah untuk satu permintaan",
    ),
    Mutasi(
        "2.4",
        "tingkat penyelesaian mingguan: jendela tidak diratakan ke awal minggu",
        [
            Sunting(
                f"{MODUL}/habits/rentetan.py", "    p = awal_periode(period, dari)", "    p = dari"
            )
        ],
        _pytest(
            "tests/unit/test_rentetan_murni.py::test_tingkat_mingguan_jendela_dimulai_dari_awal_minggu"
        ),
        harus_memuat="minggu yang selalu terpenuhi",
    ),
    Mutasi(
        "2.4",
        "rentetan habit yang dihapus-lunak tetap 200",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                # Jangkar: `_AMBIL` satu-satunya yang diikuti `_AMBIL_UNTUK_UBAH`.
                "    WHERE id = :id AND deleted_at IS NULL"
                + NL
                + '    """'
                + NL
                + ")"
                + NL
                + NL
                + "_AMBIL_UNTUK_UBAH = text(",
                "    WHERE id = :id"
                + NL
                + '    """'
                + NL
                + ")"
                + NL
                + NL
                + "_AMBIL_UNTUK_UBAH = text(",
            )
        ],
        _pytest(f"{UJI_HABITS}::test_rentetan_habit_terhapus_404"),
        harus_memuat="rentetan habit terhapus",
        kelompok="db",
    ),
    Mutasi(
        "2.3",
        "catatan habit terhapus bisa dihapus lewat API",
        [
            Sunting(
                f"{MODUL}/habits/repository.py",
                "    WHERE id = :id AND deleted_at IS NULL" + NL + "    FOR SHARE",
                "    WHERE id = :id" + NL + "    FOR SHARE",
            )
        ],
        _pytest(f"{UJI_SELESAI}::test_penyelesaian_habit_terhapus_tidak_bisa_dihapus_lewat_api"),
        harus_memuat="catatan habit terhapus dihapus lewat API",
        kelompok="db",
    ),
    Mutasi(
        "2.5",
        "PUT check-in menambal sleep_hours (COALESCE)",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "      sleep_hours = EXCLUDED.sleep_hours,",
                "      sleep_hours = COALESCE(EXCLUDED.sleep_hours, daily_checkins.sleep_hours),",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_put_mengganti_tiap_medan_bukan_hanya_energi"),
        harus_memuat="PUT menambal focus/sleep_hours/note",
        kelompok="db",
    ),
    Mutasi(
        "2.5",
        "PUT check-in menambal focus (COALESCE)",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "      focus = EXCLUDED.focus,",
                "      focus = COALESCE(EXCLUDED.focus, daily_checkins.focus),",
            )
        ],
        _pytest(f"{UJI_CHECKIN}::test_put_mengganti_tiap_medan_bukan_hanya_energi"),
        harus_memuat="PUT menambal focus/sleep_hours/note",
        kelompok="db",
    ),
    Mutasi(
        "2.6",
        "kursor mood tanpa pemecah seri id — mood ber-occurred_at sama dilompati",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "           OR (occurred_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))",
                "           OR occurred_at < CAST(:k_waktu AS timestamptz))",
            )
        ],
        _pytest(f"{UJI_MOOD}::test_halaman_mood_dengan_occurred_at_kembar_tidak_melompat"),
        harus_memuat="mood kembar dilompati",
        kelompok="db",
    ),
    Mutasi(
        "2.6",
        "kelonggaran jam mood satu jam, bukan 5 menit (spec/04)",
        [Sunting(f"{MODUL}/checkins/service.py", "LONGGAR_JAM_S = 300", "LONGGAR_JAM_S = 3600")],
        _pytest(f"{UJI_MOOD}::test_mood_enam_menit_di_depan_jam_basis_data_ditolak"),
        harus_memuat="mood 6 menit di depan diterima",
        kelompok="db",
    ),
    Mutasi(
        "1.7",
        "langkah mundur jam Redis tidak diserap — 429 palsu di ujung ledakan",
        [
            Sunting(
                f"{MODUL}/platform/batas_laju.py",
                "if terakhir ~= nil and sekarang < terakhir and terakhir - sekarang <= tonumber(ARGV[3]) then",
                "if false then",
            )
        ],
        _pytest(f"{UJI_LAJU}::test_langkah_mundur_jam_redis_kecil_diserap_besar_tidak[1500-True]"),
        harus_memuat="langkah mundur 1500 ms",
        kelompok="db",
    ),
    Mutasi(
        "2.7",
        "CORS dipasang di DALAM batas laju — preflight asing dijawab 500, bukan oleh CORS",
        [
            Sunting("apps/api/src/hvx/main.py", _CORS_BLOK, ""),
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.add_middleware(platform.BatasBadanMiddleware)" + NL,
                _CORS_BLOK + "    app.add_middleware(platform.BatasBadanMiddleware)" + NL,
            ),
        ],
        _pytest("tests/unit/test_cors.py::test_asal_lain_tidak_diloloskan"),
        harus_memuat="bukan oleh CORS",
    ),
    # ── Tinjauan PENEGAK BUTA Sprint 2 — Flutter (apps/mobile) ──────────────
    Mutasi(
        "2.7",
        "token baru hasil penyegaran tidak disimpan — ulangan memakai token lama",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "    _simpanToken("
                + NL
                + "      (_json(jawaban) as Map<String, dynamic>)['tokens']"
                + NL
                + "          as Map<String, dynamic>,"
                + NL
                + "    );"
                + NL,
                "    _json(jawaban);" + NL,
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_AKSES_BARU),
        harus_memuat=_UJI_AKSES_BARU + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "catatan check-in lama hilang saat energi disimpan",
        [
            Sunting(
                f"{APLIKASI}/lib/api/model.dart",
                "    if (catatan != null) 'note': catatan," + NL,
                "",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_CATATAN_LAMA),
        harus_memuat=_UJI_CATATAN_LAMA + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "layar tidak mengirim check-in lama bersama energi",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "        lama: _checkin,",
                "        lama: null,",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_LAYAR_LAMA),
        harus_memuat=_UJI_LAYAR_LAMA + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "tanggal lokal diambil dari UTC — lolos di mesin berzona UTC tanpa TZ terpatok",
        [
            Sunting(
                f"{APLIKASI}/lib/api/model.dart",
                "  final t = waktu.toLocal();",
                "  final t = waktu.toUtc();",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_TANGGAL_LOKAL),
        harus_memuat=_UJI_TANGGAL_LOKAL + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        'tanda "Disarankan hari ini" selalu di tier pertama',
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "    final disarankan = h.hari?.tierDisarankan ?? 0;",
                "    final disarankan = h.hari == null ? 0 : 0;",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_TANDA_SARAN),
        harus_memuat=_UJI_TANDA_SARAN + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "keluar tidak mencabut sesi di server",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "      if (_akses != null) await _kirim('POST', '/v1/auth/logout');" + NL,
                "",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_KELUAR),
        harus_memuat=_UJI_KELUAR + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "pembuatan habit tanpa Idempotency-Key",
        [Sunting(f"{APLIKASI}/lib/api/klien.dart", "      kunciIdempotensi: id," + NL, "")],
        _flutter_uji("test/api/klien_test.dart", _UJI_ID_SAMA),
        harus_memuat=_UJI_ID_SAMA + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "habit mingguan selalu dibuat 1× seminggu",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "      final target = _periode == 'day' ? 1 : _target;",
                "      final target = _periode == 'day' ? 1 : 1;",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_TARGET_MINGGUAN),
        harus_memuat=_UJI_TARGET_MINGGUAN + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "klien selalu mengirim persetujuan pelatihan model = tidak",
        [
            Sunting(
                f"{APLIKASI}/lib/api/klien.dart",
                "          'model_training': izinkanPelatihanModel",
                "          'model_training': false && izinkanPelatihanModel",
            )
        ],
        _flutter_uji("test/api/klien_test.dart", _UJI_PELATIHAN_KLIEN),
        harus_memuat=_UJI_PELATIHAN_KLIEN + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "layar mengabaikan centang pelatihan model",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/masuk.dart",
                "          izinkanPelatihanModel: _izinkanPelatihan,",
                "          izinkanPelatihanModel: false && _izinkanPelatihan,",
            )
        ],
        _flutter_uji("test/layar/masuk_test.dart", _UJI_PELATIHAN_LAYAR),
        harus_memuat=_UJI_PELATIHAN_LAYAR + " [E]",
        cwd=APLIKASI,
    ),
    Mutasi(
        "2.7",
        "muat ulang tidak menghitung ulang tanggal — lewat tengah malam menandai kemarin",
        [
            Sunting(
                f"{APLIKASI}/lib/layar/habit_hari_ini.dart",
                "      _tanggal = tanggalLokal(widget.jam());" + NL,
                "",
            )
        ],
        _flutter_uji("test/layar/habit_hari_ini_test.dart", _UJI_TENGAH_MALAM),
        harus_memuat=_UJI_TENGAH_MALAM + " [E]",
        cwd=APLIKASI,
    ),
]


def alasan_terbaca(m: Mutasi, keluaran: str) -> bool:
    """`harus_memuat` ada di keluaran — untuk pytest, HANYA di baris galat (`E …`).

    🔴 Tinjauan Sprint 1: pytest mencetak sumber uji sampai baris yang gagal, jadi
    pesan `assert` yang LULUS ikut tercetak — dan galat lingkungan sesudahnya
    (Redis mati, sandi peran diganti proses lain) terhitung "berbunyi dengan
    alasan yang dimaksud".
    """
    if "pytest" in m.perintah:
        keluaran = NL.join(b for b in keluaran.splitlines() if b.startswith("E "))
    return m.harus_memuat in keluaran


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
                cwd=AKAR / m.cwd if m.cwd else AKAR,
                env={**lingkungan, "TZ": _tz_flutter()} if m.cwd == APLIKASI else lingkungan,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        finally:
            _pulihkan(cadangan, dir_baru)
        keluaran = r.stdout + r.stderr
        tertangkap = r.returncode in m.kode_tertangkap and alasan_terbaca(m, keluaran)
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
