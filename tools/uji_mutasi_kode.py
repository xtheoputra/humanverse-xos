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

Mutasi migrasi butuh `HVX_TEST_DATABASE_URL` (dan `HVX_TEST_QDRANT_URL` sejak
memori vektor 3.5). Tanpa itu — dan tanpa
`--tanpa-db` yang MENYATAKAN bahwa bagian itu tidak dijalankan — berkas ini
keluar 1: bagian yang tidak dijalankan tidak boleh terbaca sebagai lulus.

Tiap mutasi dihentikan — beserta seluruh proses turunannya — sesudah
`BATAS_DETIK_MUTASI`, dan terhitung DIAM: kerusakan yang membuat ujinya
menggantung tidak menahan gerbang tanpa batas.

Mutasi tidak meninggalkan **bytecode basi**: perintahnya berjalan tanpa menulis
`__pycache__`, dan pemulihan membuang bytecode tiap berkas yang dimutasi. 🔴 Tanpa
itu, mutasi berukuran SAMA (`ge=1` → `ge=0`) yang dipulihkan di DETIK yang sama
meninggalkan `.pyc` yang cocok dengan berkas aslinya (Python memeriksa detik mtime
dan ukuran) — dan tahap `pytest` berikutnya menjalankan kode mutan (gerbang penuh
Sprint 3: `valence 0` lolos uji admisi di tahap uji, kode sumbernya benar).
"""

from __future__ import annotations

import argparse
import os
import shutil
import signal
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
    # lint (bawaan) · db (butuh HVX_TEST_DATABASE_URL · _QDRANT_URL) · docker (daemon Docker)
    kelompok: str = "lint"
    # Direktori kerja perintah, relatif terhadap akar repo — `flutter test` wajib
    # dijalankan dari akar aplikasinya.
    cwd: str | None = None


# Satu mutasi — mutasi paling lambat (uji pekerja) selesai < 1 menit.
BATAS_DETIK_MUTASI = 600


def jalankan_terbatas(
    perintah: list[str], cwd: Path, env: dict[str, str], batas_s: float = BATAS_DETIK_MUTASI
) -> tuple[int, str]:
    """(kode keluar, keluaran) — dihentikan beserta proses turunannya sesudah `batas_s`.

    🔴 Tinjauan Sprint 3: mutasi yang membuat ujinya menggantung (pekerja yang tidak
    menolak peran yang salah berjalan terus) menahan seluruh uji mutasi — dan
    gerbangnya — tanpa batas. Menghentikan proses langsungnya saja tidak cukup: di
    Windows `python.exe` venv meluncurkan interpreter sebagai proses ANAK, dan anak
    itu tetap memegang pipa keluaran, jadi `communicate()` ikut menunggunya.
    """
    proses = subprocess.Popen(
        perintah,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=os.name != "nt",
    )
    try:
        keluaran, _ = proses.communicate(timeout=batas_s)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proses.pid)], capture_output=True, check=False
            )
        else:
            os.killpg(proses.pid, signal.SIGKILL)
        keluaran, _ = proses.communicate()
        return -1, f"{keluaran or ''}\nMENGGANTUNG — dihentikan sesudah {batas_s:g} dtk"
    return proses.returncode, keluaran or ""


def lingkungan_mutasi() -> dict[str, str]:
    """Lingkungan perintah tiap mutasi — tanpa menulis bytecode (lihat docstring modul)."""
    return {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}


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
UJI_EVENT = "tests/integration/test_event.py"
UJI_RELAY = "tests/integration/test_relay.py"
UJI_VEKTOR = "tests/integration/test_vektor.py"
UJI_MEMORI = "tests/integration/test_memori.py"
UJI_JURNAL = "tests/integration/test_jurnal.py"
UJI_AKTIVITAS = "tests/integration/test_aktivitas.py"
UJI_PEKERJA = "tests/integration/test_pekerja.py"
_UJI_PEKERJA_PENUH = "test_pekerja_menyalurkan_mengekstrak_dan_menyemat_lalu_berhenti_bersih"
UJI_TERBIT = "tests/integration/test_penerbitan_event.py"
UJI_NIAT = "tests/unit/test_niat.py"
UJI_GERBANG_MODEL = "tests/unit/test_gerbang_model.py"
UJI_RUTE = "tests/integration/test_rute_model.py"
UJI_REGISTRI = "tests/unit/test_registri_agent.py::test_manifest_yang_melanggar_ditolak"
UJI_KATALOG = "tests/integration/test_katalog_agent.py"
UJI_PELAKSANA = "tests/unit/test_pelaksana_alat.py"
UJI_ALAT = "tests/integration/test_alat_v0.py"
UJI_KEPUTUSAN = "tests/unit/test_keputusan_agent.py::test_keputusan_rusak_ditolak"
UJI_RUNTIME = "tests/integration/test_runtime_agent.py"
UJI_GERBANG = "tests/integration/test_gerbang_risiko.py"
UJI_ORKESTRATOR = "tests/integration/test_orkestrator.py"
UJI_AGENT_V0 = "tests/integration/test_agent_v0.py"
UJI_PERCAKAPAN = "tests/integration/test_percakapan.py"
UJI_ANGGARAN = "tests/integration/test_anggaran.py"
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
                "        if baris is None:"
                + NL
                + "            return None, _UmurCache(px=self._ttl_ms)"
                + NL,
                "        if baris is None:"
                + NL
                + '            return "allow", _UmurCache(px=self._ttl_ms)'
                + NL,
            )
        ],
        _pytest(f"{UJI_IZIN}::test_tanpa_keputusan_tersimpan_jawabannya_ask"),
        harus_memuat="assert 'allow' == 'ask'",
        kelompok="db",
    ),
    Mutasi(
        "1.5",
        "izin kedaluwarsa tetap berlaku — 'izinkan sekali' menjadi izin permanen",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "        if baris.habis_ms <= baris.kini_ms:",
                "        if False:",
            )
        ],
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
                "        habis = min(baris.kini_ms + self._ttl_ms, baris.habis_ms - _MARGIN_KEDALUWARSA_MS)",
                "        habis = baris.kini_ms + self._ttl_ms",
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
                "baris.habis_ms - _MARGIN_KEDALUWARSA_MS)",
                "baris.habis_ms)",
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
                "await self._r.set(kunci, keputusan or _TANPA_KEPUTUSAN, px=umur.px, pxat=umur.pxat)",
                "await self._r.set(kunci, keputusan or bawaan, px=umur.px, pxat=umur.pxat)",
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
                "            return cast(Keputusan, baris.decision), _UmurCache(px=self._ttl_ms)",
                '            return (None if baris.decision == "ask" else '
                "cast(Keputusan, baris.decision)), _UmurCache(px=self._ttl_ms)",
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
    # ── Sprint 3 · 3.1 events + amplop + idempotensi ─────────────────────
    Mutasi(
        "3.1",
        "event tanpa ON CONFLICT — event ganda menjadi galat, bukan ditelan",
        [
            Sunting(
                f"{MODUL}/events/repository.py",
                "    ON CONFLICT (user_id, idempotency_key) DO NOTHING" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_EVENT}::test_event_ganda_ditelan_sebagai_sukses"),
        harus_memuat="IntegrityError",
        kelompok="db",
    ),
    Mutasi(
        "E-3",
        "uji admisi tidak memeriksa sumber — `sensor` sampai ke basis data",
        [
            Sunting(
                f"{MODUL}/events/penerbit.py",
                "    if source not in SUMBER:",
                '    if source not in SUMBER | {"sensor"}:',
            )
        ],
        _pytest(f"{UJI_EVENT}::test_uji_admisi_menolak_sebelum_menyentuh_basis_data"),
        harus_memuat="IntegrityError",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        "kunci yang sama untuk kejadian lain ditelan diam-diam",
        [Sunting(f"{MODUL}/events/penerbit.py", "    if not sama:", "    if False:")],
        _pytest(f"{UJI_EVENT}::test_kunci_sama_untuk_kejadian_lain_ditolak_keras"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        "registry kode menambah jenis event yang tidak ada di spec/03",
        [
            Sunting(
                f"{MODUL}/events/kontrak.py",
                '    "checkin.logged": (1, CheckinDicatat),',
                '    "checkin.logged": (1, CheckinDicatat),'
                + NL
                + '    "habit.deleted": (1, HabitDilewati),',
            )
        ],
        _pytest("tests/unit/test_kontrak_event.py::test_registry_sama_dengan_baris_v0_spec03"),
        harus_memuat="hanya di kode: ['habit.deleted']",
    ),
    Mutasi(
        "3.1",
        "payload journal.created menerima medan lain — isi jurnal bisa masuk event",
        [
            Sunting(
                f"{MODUL}/events/kontrak.py",
                "class JurnalDibuat(_Payload):" + NL,
                "class JurnalDibuat(_Payload):"
                + NL
                + '    model_config = ConfigDict(extra="allow")'
                + NL,
            )
        ],
        _pytest("tests/unit/test_kontrak_event.py::test_isi_jurnal_tidak_pernah_masuk_event"),
        harus_memuat="DID NOT RAISE",
    ),
    # ── Sprint 3 · 3.2 penerbitan event dari goals · habits · checkins (aturan 6) ─
    Mutasi(
        "3.2",
        "POST /goals tanpa goal.created",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "            await events.terbitkan("
                + NL
                + "                conn,"
                + NL
                + "                user_id=user_id,"
                + NL
                + '                event_type="goal.created",',
                # Seluruh jangkar diganti — `.replace()` pada potongan terakhir saja
                # membuat mutasi ini tidak mengubah apa pun (tinjauan Sprint 3).
                "            await _tidak_menerbitkan("
                + NL
                + "                conn,"
                + NL
                + "                user_id=user_id,"
                + NL
                + '                event_type="goal.created",',
            ),
            _sisip(
                f"{MODUL}/goals/service.py",
                "async def _tidak_menerbitkan(*_a: object, **_k: object) -> None:"
                + NL
                + "    return None",
            ),
        ],
        _pytest(f"{UJI_TERBIT}::test_goal_dibuat_menerbitkan_goal_created_sekali"),
        harus_memuat="POST /goals tidak menerbitkan tepat satu goal.created",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "galat penerbitan ditelan — goal tersimpan tanpa event-nya",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                "            await events.terbitkan("
                + NL
                + "                conn,"
                + NL
                + "                user_id=user_id,"
                + NL
                + '                event_type="goal.created",',
                # Seluruh jangkar diganti — `.replace()` pada potongan terakhir saja
                # membuat mutasi ini tidak mengubah apa pun (tinjauan Sprint 3).
                "            await _terbit_diam("
                + NL
                + "                conn,"
                + NL
                + "                user_id=user_id,"
                + NL
                + '                event_type="goal.created",',
            ),
            _sisip(
                f"{MODUL}/goals/service.py",
                "async def _terbit_diam(conn: AsyncConnection, **isi: Any) -> None:"
                + NL
                + "    try:"
                + NL
                + "        await events.terbitkan(conn, **isi)"
                + NL
                + "    except events.EventTidakSah:"
                + NL
                + "        pass"
                + NL
                + "from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: E402",
            ),
        ],
        _pytest(f"{UJI_TERBIT}::test_event_yang_gagal_terbit_membatalkan_tulisannya"),
        harus_memuat="goal tersimpan tanpa event-nya",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "DELETE penyelesaian tanpa habit.completion_retracted",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                "        if dicabut is not None:" + NL + "            await events.terbitkan(",
                "        if dicabut is None:" + NL + "            await events.terbitkan(",
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_penyelesaian_kirim_ulang_batal_dan_koreksi"),
        harus_memuat="peta aturan 6 tidak ditepati",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "check-in diterbitkan juga saat isinya tidak berubah",
        [
            Sunting(
                f"{MODUL}/checkins/service.py",
                "        if lama != (c.energy, c.focus, c.sleep_hours):",
                "        if True:",
            )
        ],
        _pytest(
            f"{UJI_TERBIT}"
            "::test_check_in_diterbitkan_hanya_saat_isinya_berubah_dan_koreksi_tidak_ditelan"
        ),
        harus_memuat="event check-in tidak mengikuti perubahan isinya",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "kunci mood per menit (spec/03 lama) — mood kedua dalam satu menit ditolak",
        [
            Sunting(
                f"{MODUL}/checkins/service.py",
                '                idempotency_key=f"mood:{mood.id}",',
                '                idempotency_key=f"mood:{user_id}:{mood.occurred_at:%Y%m%d%H%M}",',
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_dua_mood_dalam_satu_menit_dua_event"),
        harus_memuat="mood kedua dalam menit yang sama gagal",
        kelompok="db",
    ),
    # ── Sprint 3 · 3.3 relay kotak keluar → Redis Streams + grup konsumen ──
    Mutasi(
        "3.3",
        "relay tanpa penanda per event — pindaian ulang jendela belakang menggandakan",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                "if redis.call('ZADD', KEYS[1], 'NX', ARGV[1], ARGV[2]) == 1 then",
                "if true then",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_relay_menyalin_rujukan_sekali_tanpa_payload"),
        harus_memuat="event terkirim 2 kali",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "relay hanya maju — event yang commit di belakang kursor hilang selamanya",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                "        if posisi is not None:"
                + NL
                + "            belakang = (posisi[0] - timedelta(seconds=LIHAT_BELAKANG_S), _NOL)",
                "        if False:"
                + NL
                + "            belakang = (posisi[0] - timedelta(seconds=LIHAT_BELAKANG_S), _NOL)",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_event_yang_commit_belakangan_tetap_terkirim"),
        harus_memuat="event yang commit di belakang kursor tidak pernah terkirim",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "konsumen tidak mengklaim pesan yang menggantung — milik konsumen mati hilang",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                "            for id_pesan, isi in pesan:"
                + NL
                + "                selesai += await self._proses(str(id_pesan), isi, diklaim=True)",
                "            for id_pesan, isi in pesan[:0]:"
                + NL
                + "                selesai += await self._proses(str(id_pesan), isi, diklaim=True)",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_konsumen_mati_event_tidak_hilang_saat_hidup_lagi"),
        harus_memuat="event milik konsumen yang mati hilang",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "tanpa stream mati — event yang selalu gagal dicoba tanpa akhir",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                "        if diklaim and await self._kali_diserahkan(id_pesan) > self._maks_kirim:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_penangan_yang_selalu_gagal_pindah_ke_stream_mati"),
        harus_memuat="dead letter: []",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "event jenis lain tidak di-ACK — menggantung di grup selamanya",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                '        if isi.get("event_type") not in self._jenis:'
                + NL
                + "            await self._r.xack(self.stream, self.grup, id_pesan)"
                + NL,
                '        if isi.get("event_type") not in self._jenis:' + NL,
            )
        ],
        _pytest(f"{UJI_RELAY}::test_penangan_menerima_isi_dari_postgresql_dan_jenis_lain_dilewati"),
        harus_memuat="goal.created tidak di-ACK",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pangkas mengabaikan pesan yang belum di-ACK — event yang sedang diproses dibuang",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                '            if int(ringkas["pending"]) > 0:'
                + NL
                + '                batas.append(str(ringkas["min"]))'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_pangkas_tidak_membuang_yang_masih_ditunggu"),
        harus_memuat="pesan yang belum di-ACK dibuang dari stream",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pekerja tidak menyalakan relay",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                '        tugas = [asyncio.create_task(_ulang("relay", relay_sekali, JEDA_RELAY_S, berhenti))]',
                "        tugas: list[asyncio.Task[None]] = []",
            )
        ],
        _pytest(f"{UJI_PEKERJA}::{_UJI_PEKERJA_PENUH}"),
        harus_memuat="pekerja tidak menyalurkan event dalam 15 detik",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "EXECUTE fungsi relay tidak dicabut dari PUBLIC (spec/01 DAN migrasi)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "REVOKE ALL ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) FROM PUBLIC;"
                + NL,
                "",
            ),
            Sunting(
                f"{MIGRASI}/0005_relay_event.up.sql",
                "REVOKE ALL ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) FROM PUBLIC;"
                + NL,
                "",
            ),
        ],
        _pytest(
            "tests/integration/test_kepemilikan_data.py"
            "::test_fungsi_security_definer_hanya_daftar_izin_terpatok_dan_bukan_untuk_public"
        ),
        harus_memuat="events_untuk_relay",
        kelompok="db",
    ),
    # ── Sprint 3 · 3.5 Qdrant — Qdrant tidak punya RLS; saringannya yang menjaga H-27 ──
    Mutasi(
        "3.5",
        "pencarian vektor tanpa saringan user_id — titik pengguna lain ikut",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                'wajib: list[dict[str, Any]] = [{"key": "user_id", "match": {"value": str(user_id)}}]',
                "wajib: list[dict[str, Any]] = []",
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_pencarian_hanya_titik_milik_pengguna_itu"),
        harus_memuat="titik pengguna lain ikut",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "saringan scope kosong dibaca sebagai 'semua scope'",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                '                return []  # saringan kosong = tidak ada yang boleh cocok, bukan "semua"',
                "                continue",
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_saringan_scope_dan_scope_kosong_tidak_berarti_semua"),
        harus_memuat="tanpa scope yang diizinkan, pencarian mengembalikan sesuatu",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "pencarian tanpa user_id tidak ditolak sebelum ke Qdrant",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                "        if not isinstance(user_id, UUID):"
                + NL
                + '            raise TypeError("pencarian vektor wajib dibatasi satu user_id (H-27)")'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_pencarian_tanpa_pengguna_ditolak_sebelum_ke_qdrant"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "hapus_milik tanpa saringan pengguna — titik semua pengguna terhapus",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                '            {"filter": {"must": [{"key": "user_id", "match": {"value": str(user_id)}}]}},',
                '            {"filter": {"must": []}},',
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_hapus_milik_menghapus_titik_satu_pengguna_saja"),
        harus_memuat="titik pengguna lain ikut terhapus",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "pesan GalatVektor memuat badan galat Qdrant (yang memantulkan masukan)",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                """raise GalatVektor(f"qdrant {metode} {jalur.split('?')[0]} → {r.status_code}")""",
                """raise GalatVektor(f"qdrant {metode} {jalur.split('?')[0]} → {r.status_code} {r.text}")""",
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_galat_qdrant_tidak_memantulkan_isi_permintaan"),
        harus_memuat="badan galat Qdrant ikut",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "koleksi berdimensi lain dipakai begitu saja",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                '                raise GalatVektor(f"koleksi {nama} bukan kosinus berdimensi {dimensi}")',
                "                pass",
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_koleksi_berdimensi_lain_ditolak_bukan_dipakai"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "penyemat memakai hash() Python — vektor berbeda tiap proses",
        [
            Sunting(
                f"{MODUL}/platform/sematan.py",
                "            cerna = hashlib.blake2b(fitur.encode(), digest_size=8, key=self._kunci).digest()",
                '            cerna = hash(fitur).to_bytes(8, "little", signed=True)',
            )
        ],
        _pytest(
            "tests/unit/test_sematan.py::test_sama_di_tiap_proses_bukan_hash_python_yang_diacak"
        ),
        harus_memuat="assert [",
    ),
    Mutasi(
        "3.5",
        "penyemat mengabaikan kuncinya — kata isi jurnal terbaca dari vektor dengan kamus",
        [
            Sunting(
                f"{MODUL}/platform/sematan.py",
                "            cerna = hashlib.blake2b(fitur.encode(), digest_size=8, key=self._kunci).digest()",
                "            cerna = hashlib.blake2b(fitur.encode(), digest_size=8).digest()",
            )
        ],
        _pytest(
            "tests/unit/test_sematan.py::test_tanpa_kunci_yang_sama_kata_tidak_bisa_ditebak_dari_vektor"
        ),
        harus_memuat="kata terbaca tanpa kunci",
    ),
    # ── Sprint 3 · 3.4 journal — daftar TANPA body; isi jurnal tidak pernah masuk event ──
    Mutasi(
        "3.4",
        "kontrak daftar jurnal memuat body (walau kosong)",
        [
            Sunting(
                f"{MODUL}/journal/schemas.py",
                "    word_count: int"
                + NL
                + "    created_at: datetime"
                + NL
                + "    updated_at: datetime"
                + NL
                + NL
                + NL
                + "class Jurnal(RingkasanJurnal):",
                "    word_count: int"
                + NL
                + "    created_at: datetime"
                + NL
                + "    updated_at: datetime"
                + NL
                + "    body: str | None = None"
                + NL
                + NL
                + NL
                + "class Jurnal(RingkasanJurnal):",
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_kontrak_daftar_jurnal_tidak_punya_medan_body"),
        harus_memuat="kontrak GET /journal memuat body",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "kueri daftar jurnal memilih body — isi tulisan ikut ke layar ringkasan",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "title, occurred_at, word_count, created_at, updated_at"
                + NL
                + "    FROM journal_entries",
                "title, body, occurred_at, word_count, created_at, updated_at"
                + NL
                + "    FROM journal_entries",
            ),
            Sunting(
                f"{MODUL}/journal/repository.py",
                "    return [RingkasanJurnal.model_validate(dict(b)) for b in hasil.mappings()]",
                "    return [Jurnal.model_validate(dict(b)) for b in hasil.mappings()]",
            ),
        ],
        _pytest(f"{UJI_JURNAL}::test_kueri_daftar_tidak_membaca_body_dari_basis_data"),
        harus_memuat="kueri daftar memilih body",
        kelompok="db",
    ),
    # ── Sprint 3 · 3.6 ekstraksi memori dari jurnal & mood ──
    Mutasi(
        "3.6",
        "memori ekstraksi tanpa event sumber",
        [
            Sunting(
                f"{MODUL}/memory/ekstraksi.py",
                "        source_event_id=ev.id,",
                "        source_event_id=None,  # type: ignore[arg-type]",
            )
        ],
        _pytest(
            f"{UJI_MEMORI}::test_tiap_memori_punya_kind_scope_confidence_bukti_dan_event_sumber"
        ),
        harus_memuat="memori tanpa event sumber",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "keyakinan memori dibiarkan bawaan kolom (0.500)",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "scope, content, confidence, evidence_count,"
                + NL
                + "                          model_version, source_event_id, valid_from)"
                + NL
                + "    VALUES (:id, :user_id, :kind, :scope, :content, :confidence, :evidence_count,",
                "scope, content, evidence_count,"
                + NL
                + "                          model_version, source_event_id, valid_from)"
                + NL
                + "    VALUES (:id, :user_id, :kind, :scope, :content, :evidence_count,",
            )
        ],
        _pytest(
            f"{UJI_MEMORI}::test_tiap_memori_punya_kind_scope_confidence_bukti_dan_event_sumber"
        ),
        harus_memuat="Decimal('0.500')",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "id memori tidak deterministik — event yang diserahkan lagi menggandakan memori",
        [
            Sunting(
                f"{MODUL}/memory/ekstraksi.py",
                'return uuid5(_RUANG_ID_MEMORI, f"{event_type}:{subjek_id}:{kind}")',
                'return uuid5(_RUANG_ID_MEMORI, f"{event_type}:{subjek_id}:{kind}:'
                "{__import__('os').urandom(8).hex()}\")",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_event_yang_diserahkan_lagi_tidak_menggandakan_memori"),
        harus_memuat="memori ganda untuk satu event",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "ekstraksi membaca jurnal yang sudah dihapus",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "    WHERE id = :id AND deleted_at IS NULL" + NL + "    FOR SHARE",
                "    WHERE id = :id" + NL + "    FOR SHARE",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_yang_dihapus_sebelum_diekstrak_tidak_diingat"),
        harus_memuat="jurnal terhapus tetap diingat",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "ekstraksi tanpa kunci BAGI — PATCH serentak kalah, memori memuat isi lama",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "    WHERE id = :id AND deleted_at IS NULL" + NL + "    FOR SHARE" + NL,
                "    WHERE id = :id AND deleted_at IS NULL" + NL,
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_sunting_jurnal_menunggu_ekstraksi_yang_sedang_membacanya"),
        harus_memuat="PATCH tidak menunggu ekstraksi yang sedang membaca jurnal",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "hapus jurnal tidak memanggil pendengarnya — isi hidup terus di memori",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "            raise _tidak_ditemukan()"
                + NL
                + "        for p in pendengar:"
                + NL
                + "            await p(conn, jurnal_id)"
                + NL,
                "            raise _tidak_ditemukan()" + NL,
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya"),
        harus_memuat="isi jurnal terhapus tetap di memori sampai penyelaras lewat",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "sunting jurnal tidak memanggil pendengarnya — memori memuat isi lama",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "            if jurnal is not None:"
                + NL
                + "                for p in pendengar:"
                + NL
                + "                    await p(conn, jurnal_id)"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_disunting_memori_dan_vektornya_mengikuti"),
        harus_memuat="assert 'bertengkar dengan atasan' == 'berdamai dengan atasan'",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "titik rakit tidak memasang pendengar jurnal",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "    app.state.pendengar_jurnal_berubah = (memory.selaraskan_jurnal,)",
                "    app.state.pendengar_jurnal_berubah = ()",
            )
        ],
        _pytest("tests/unit/test_main.py::test_titik_rakit_memasang_pembaca_lintas_modul"),
        harus_memuat="sunting & hapus jurnal tidak menyelaraskan memorinya",
    ),
    Mutasi(
        "3.6",
        "pekerja tidak merakit konsumen memori",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                "            tangani=memory.ekstrak," + NL + "        )," + NL + "    ]",
                "            tangani=memory.ekstrak," + NL + "        )," + NL + "    ][:0]",
            )
        ],
        _pytest(f"{UJI_PEKERJA}::{_UJI_PEKERJA_PENUH}"),
        harus_memuat="pekerja tidak mengekstrak memori dari mood",
        kelompok="db",
    ),
    # ── Sprint 3 · 3.5 penyelaras memories → Qdrant ──
    Mutasi(
        "3.5",
        "pekerja tidak menyalakan penyelaras vektor",
        [Sunting("apps/api/src/hvx/pekerja.py", "        if penyelaras:", "        if False:")],
        _pytest(f"{UJI_PEKERJA}::{_UJI_PEKERJA_PENUH}"),
        harus_memuat="pekerja tidak menyemat memori ke Qdrant",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "sunting isi tidak menandai vektornya basi",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "      embedding_model = CASE WHEN content IS DISTINCT FROM :content THEN NULL"
                + NL
                + "                             ELSE embedding_model END",
                "      embedding_model = embedding_model",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_disunting_memori_dan_vektornya_mengikuti"),
        harus_memuat="isi berubah, vektor lama dianggap masih cocok",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "penyelaras membuang baris tanpa membuang titiknya",
        [
            Sunting(
                f"{MODUL}/memory/penyelaras.py",
                "        await self._vektor.hapus(self._koleksi, buang)" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya"),
        harus_memuat="titik vektornya tertinggal",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "hapus jurnal tidak mengosongkan isi memorinya",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "    UPDATE memories SET content = '', summary = NULL, deleted_at = now()",
                "    UPDATE memories SET summary = NULL, deleted_at = now()",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya"),
        harus_memuat="isi jurnal terhapus tetap di memori sampai penyelaras lewat",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "payload titik Qdrant memuat isi memori",
        [
            Sunting(
                f"{MODUL}/memory/penyelaras.py",
                '"kind": b.kind, "model": nama},',
                '"kind": b.kind, "model": nama, "content": b.content},',
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_penyelaras_menyemat_tanpa_isi_di_payload"),
        harus_memuat="payload Qdrant memuat lebih dari rujukan",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "memori penyemat lain tidak disemat ulang (spec/01 DAN migrasi)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "    WHERE m.deleted_at IS NOT NULL OR m.embedding_model IS DISTINCT FROM p_model",
                "    WHERE m.deleted_at IS NOT NULL OR m.model_version IS NULL",
            ),
            Sunting(
                f"{MIGRASI}/0006_penyelaras_memori.up.sql",
                "    WHERE m.deleted_at IS NOT NULL OR m.embedding_model IS DISTINCT FROM p_model",
                "    WHERE m.deleted_at IS NOT NULL OR m.model_version IS NULL",
            ),
        ],
        _pytest(f"{UJI_MEMORI}::test_penyemat_lain_disemat_ulang_bukan_dicampur"),
        harus_memuat="memori penyemat lama tidak disemat ulang",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "EXECUTE penyelaras memori tidak dicabut dari PUBLIC (spec/01 DAN migrasi)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "REVOKE ALL ON FUNCTION memori_perlu_diselaraskan(text, integer) FROM PUBLIC;" + NL,
                "",
            ),
            Sunting(
                f"{MIGRASI}/0006_penyelaras_memori.up.sql",
                "REVOKE ALL ON FUNCTION memori_perlu_diselaraskan(text, integer) FROM PUBLIC;" + NL,
                "",
            ),
        ],
        _pytest(
            "tests/integration/test_kepemilikan_data.py"
            "::test_fungsi_security_definer_hanya_daftar_izin_terpatok_dan_bukan_untuk_public"
        ),
        harus_memuat="memori_perlu_diselaraskan",
        kelompok="db",
    ),
    # ── Sprint 3 · 3.7 pencarian memori — agent tanpa izin scope tidak menerima barisnya ──
    Mutasi(
        "3.7",
        "pencarian mengabaikan keputusan pengguna",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                '            keputusan = await self._izin.cek(user_id, subjek, scope, "read", bawaan=_BAWAAN_RISK_0)',
                '            keputusan = "allow"',
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_agent_tanpa_izin_scope_tidak_menerima_barisnya"),
        harus_memuat="journal_raw terbuka tanpa izin",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "manifest tidak membatasi — semua scope resmi dicari",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                "        for scope in sorted(diminta):",
                "        for scope in sorted(identity.SCOPE_RESMI):",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_agent_tanpa_izin_scope_tidak_menerima_barisnya"),
        harus_memuat="izin pengguna melebarkan manifest",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "scope tidak diperiksa ulang di baris PostgreSQL — payload Qdrant basi menang",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "      AND scope = ANY(CAST(:scope AS text[]))" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_payload_qdrant_basi_tidak_meloloskan_scope"),
        harus_memuat="scope di payload Qdrant menang atas scope di baris",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "memori terhapus diserahkan selama titiknya masih di Qdrant",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "    WHERE id = ANY(CAST(:ids AS uuid[])) AND deleted_at IS NULL"
                + NL
                + "      AND scope",
                "    WHERE id = ANY(CAST(:ids AS uuid[]))" + NL + "      AND scope",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya"),
        harus_memuat="memori terhapus diserahkan karena titiknya masih ada",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "kueri tanpa kata tetap menanyai Qdrant",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py", "        if not any(vektor):", "        if False:"
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_kueri_tanpa_kata_tidak_menanyai_qdrant"),
        harus_memuat="Qdrant ditanya padahal jawabannya sudah pasti kosong",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "kandidat berskor 0 diserahkan sebagai kecocokan",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                "            positif = [k for k in kandidat if k.skor > 0]  # kosinus ≤ 0 bukan kemiripan",
                "            positif = list(kandidat)  # kosinus ≤ 0 bukan kemiripan",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_kandidat_berskor_nol_bukan_kecocokan"),
        harus_memuat="kandidat berskor 0 diserahkan sebagai kecocokan",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "pencarian tidak menolak scope di luar daftar resmi sendiri",
        [Sunting(f"{MODUL}/memory/pencarian.py", "        if asing:", "        if False:")],
        _pytest(
            f"{UJI_MEMORI}::test_permintaan_yang_salah_bentuk_ditolak[manifest0-rapat-5-daftar resmi]"
        ),
        harus_memuat="Regex pattern did not match",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "batas hasil tidak dijaga",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                "not 1 <= batas <= MAKS_HASIL:",
                "not 0 <= batas <= MAKS_HASIL + 1_000:",
            )
        ],
        _pytest(
            f"{UJI_MEMORI}::test_permintaan_yang_salah_bentuk_ditolak[manifest2-rapat-0-batas]"
        ),
        harus_memuat="Qdrant ditanya padahal jawabannya sudah pasti kosong",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "scope sensitif terbuka karena bawaan risk 0",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                '        if bawaan == "allow" and SCOPE_RESMI[scope].sensitif:',
                "        if False:",
            )
        ],
        _pytest(
            "tests/integration/test_izin.py::test_scope_sensitif_tidak_pernah_allow_karena_bawaan"
        ),
        harus_memuat="journal_raw terbuka karena bawaan",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "mesin izin menerima scope di luar daftar resmi",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "    if scope not in SCOPE_RESMI:",
                "    if False:",
            )
        ],
        _pytest(
            "tests/unit/test_izin_masukan.py::test_scope_dan_aksi_tak_dikenal_ditolak[habit-read]"
        ),
        harus_memuat="disentuh sebelum masukan divalidasi",
    ),
    # ── Sprint 3 · 3.8 activities — `inferred` terpisah dari `manual` ──
    Mutasi(
        "3.8",
        "jalur sistem mencatat tebakannya sebagai manual",
        [
            Sunting(
                f"{MODUL}/activities/service.py",
                '        source="inferred",',
                '        source="manual",',
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_jalur_sistem_selalu_inferred_dan_bisa_dipisahkan"),
        harus_memuat="assert 'manual' == 'inferred'",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "saringan ?source= diabaikan — tebakan bercampur dengan catatan manusia",
        [
            Sunting(
                f"{MODUL}/activities/repository.py",
                "      AND (CAST(:source AS text) IS NULL OR source = CAST(:source AS text))" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_jalur_sistem_selalu_inferred_dan_bisa_dipisahkan"),
        harus_memuat="tebakan sistem bercampur dengan catatan manusia",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "klien bisa menyatakan sumber aktivitasnya",
        [
            Sunting(
                f"{MODUL}/activities/schemas.py",
                "    payload: Payload = Field(default_factory=dict)"
                + NL
                + NL
                + '    @model_validator(mode="after")',
                "    payload: Payload = Field(default_factory=dict)"
                + NL
                + '    source: Sumber = "manual"'
                + NL
                + NL
                + '    @model_validator(mode="after")',
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_klien_hanya_bisa_mencatat_manual"),
        harus_memuat="klien bisa menyatakan aktivitasnya disimpulkan",
        kelompok="db",
    ),
    # ── Sprint 3 · tinjauan adversarial: keamanan (S1–S5) · kontrak (K2–K8) ──
    Mutasi(
        "3.5",
        "S1: penyemat per pengguna memakai kunci proses — akun biasa bisa menyemat kamus",
        [
            Sunting(
                f"{MODUL}/platform/sematan.py",
                "        return _SematanHash(turunan, self._dimensi, self._nama)",
                "        return _SematanHash(self._kunci, self._dimensi, self._nama)",
            )
        ],
        _pytest("tests/unit/test_sematan.py::test_tiap_pengguna_ruang_vektornya_sendiri"),
        harus_memuat="vektor dua pengguna sebanding",
    ),
    Mutasi(
        "3.5",
        "S2: penyelaras menyemat di event loop pekerja",
        [
            Sunting(
                f"{MODUL}/memory/penyelaras.py",
                "        vektor = await asyncio.to_thread("
                + NL
                + "            lambda: [penyemat.semat(b.content[:MAKS_TEKS_SEMAT]) for b in semat]"
                + NL
                + "        )",
                "        vektor = [penyemat.semat(b.content) for b in semat]",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_penyelaras_tidak_menahan_event_loop_pekerja"),
        harus_memuat="penyelaras menahan event loop pekerja",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "S2: teks yang disemat tidak dibatasi — biaya satu memori tanpa batas",
        [
            Sunting(
                f"{MODUL}/memory/penyelaras.py",
                "penyemat.semat(b.content[:MAKS_TEKS_SEMAT])",
                "penyemat.semat(b.content)",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_penyelaras_hanya_menyemat_awal_teks_panjang"),
        harus_memuat="teks yang disemat tidak dibatasi",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "S3: penanda relay tidak dipangkas — satu penanda per event menumpuk di Redis",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                '        await self._r.zremrangebyscore(self._k_terkirim(), "-inf", f"({batas}")'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_penanda_relay_dipangkas_di_luar_jendela_belakang"),
        harus_memuat="penanda event di luar jendela belakang tidak dipangkas",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "stream mati tidak pernah dipangkas",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                '    return int(await redis.xtrim(kunci_mati(awalan), minid=f"{batas_ms}-0", approximate=False))',
                "    return 0",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_stream_mati_dipangkas_menurut_umur"),
        harus_memuat="stream mati tidak dipangkas menurut umur",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "S4: fungsi relay boleh dipanggil peran api (spec/01 DAN migrasi)",
        [
            Sunting(
                "spec/01-DATABASE-SCHEMA.md",
                "GRANT EXECUTE ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) TO hvx_pekerja;",
                "GRANT EXECUTE ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) TO hvx_app;",
            ),
            Sunting(
                f"{MIGRASI}/0005_relay_event.up.sql",
                "GRANT EXECUTE ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) TO hvx_pekerja;",
                "GRANT EXECUTE ON FUNCTION events_untuk_relay(timestamptz, uuid, integer) TO hvx_app;",
            ),
        ],
        _pytest(
            "tests/integration/test_kepemilikan_data.py"
            "::test_fungsi_security_definer_hanya_daftar_izin_terpatok_dan_bukan_untuk_public"
        ),
        harus_memuat="seharusnya ['hvx_pekerja']",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "S4: api mulai sebagai anggota hvx_pekerja",
        [
            Sunting(
                f"{MODUL}/platform/db.py",
                "    if not pekerja and peran.anggota_pekerja:",
                "    if False:",
            )
        ],
        _pytest(
            "tests/integration/test_aplikasi_hidup.py::test_api_menolak_mulai_sebagai_peran_pekerja"
        ),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "S4: pekerja mulai tanpa peran hvx_pekerja",
        [
            Sunting(
                f"{MODUL}/platform/db.py",
                "    if pekerja and not peran.anggota_pekerja:",
                "    if False:",
            )
        ],
        _pytest(
            "tests/integration/test_aplikasi_hidup.py::"
            "test_pekerja_menolak_mulai_dengan_peran_yang_salah[dsn_aplikasi-hvx_pekerja]"
        ),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "S5: jsonb dari klien tanpa batas kedalaman — tersimpan lalu 500 selamanya",
        [
            Sunting(
                f"{MODUL}/platform/teks.py",
                "        if _wadah >= KEDALAMAN_JSON_MAKS:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_payload_terlalu_dalam_ditolak_sebelum_tersimpan"),
        harus_memuat="payload terlalu dalam tidak ditolak 400",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "K2a: pencarian tidak memeriksa kesegaran vektor — kata yang dihapus masih cocok",
        [Sunting(f"{MODUL}/memory/repository.py", "      AND embedding_model = :model" + NL, "")],
        _pytest(
            f"{UJI_MEMORI}::test_kata_yang_dihapus_dari_jurnal_tidak_cocok_sebelum_penyelaras_lewat"
        ),
        harus_memuat="kata yang dihapus pemiliknya masih cocok",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "K2b: kandidat diambil sekali — titik memori terhapus menyingkirkan hasil sah",
        [Sunting(f"{MODUL}/memory/pencarian.py", "_MAKS_HALAMAN = 5", "_MAKS_HALAMAN = 1")],
        _pytest(f"{UJI_MEMORI}::test_titik_memori_terhapus_tidak_menyingkirkan_hasil_yang_sah"),
        harus_memuat="hasil sah tersingkir oleh titik memori terhapus",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "jangkar mutasi bergeser — mutasi diam-diam tidak mengubah apa pun",
        [Sunting(f"{MODUL}/memory/pencarian.py", "_MAKS_HALAMAN = 5", "_MAKS_HALAMAN = 6")],
        _pytest("tests/unit/test_jangkar_mutasi.py"),
        harus_memuat="jangkar cocok 0x",
    ),
    Mutasi(
        "3.5",
        "K3: penyelaras menandai tersemat tanpa mencocokkan isi — vektor lama menang",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "      AND encode(sha256(convert_to(m.content, 'UTF8')), 'hex') = s.cerna" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_sunting_jurnal_tidak_menunggu_qdrant_yang_lambat"),
        harus_memuat="vektor isi LAMA ditandai cocok dengan isi yang disunting",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "K4: penyelaras menimpa model_version (tempat ambang #34)",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "    SET embedding_id = CAST(m.id AS text), embedding_model = :model" + NL,
                "    SET embedding_id = CAST(m.id AS text), embedding_model = :model,"
                + " model_version = :model"
                + NL,
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_penyelaras_menyemat_tanpa_isi_di_payload"),
        harus_memuat="penyelaras menimpa model_version (K4)",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "K5: ended_at masa depan diterima",
        [
            Sunting(
                f"{MODUL}/activities/service.py",
                "            if badan.ended_at is not None and badan.ended_at > batas:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_ended_at_masa_depan_dan_durasi_yang_bertentangan_ditolak"),
        harus_memuat="ended_at masa depan diterima",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "K5: duration_seconds yang membantah ended_at diterima",
        [
            Sunting(
                f"{MODUL}/activities/schemas.py",
                "            if self.duration_seconds is not None and abs(self.duration_seconds - rentang) > 1:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_ended_at_masa_depan_dan_durasi_yang_bertentangan_ditolak"),
        harus_memuat="durasi yang membantah ended_at diterima",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        'K7: uji admisi event mengoersi tipe (True → 1, "3" → 3)',
        [
            Sunting(
                f"{MODUL}/events/kontrak.py",
                '    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)',
                '    model_config = ConfigDict(extra="forbid", frozen=True)',
            )
        ],
        _pytest("tests/unit/test_kontrak_event.py::test_payload_di_luar_kontrak_ditolak"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "3.2",
        "K8: penerbit jurnal menelan galatnya — jurnal tersimpan tanpa event",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "            await events.terbitkan(",
                "            await _telan(events.terbitkan)(",
            ),
            _sisip(
                f"{MODUL}/journal/service.py",
                "def _telan(f: Any) -> Any:"
                + NL
                + "    async def g(*a: Any, **k: Any) -> Any:"
                + NL
                + "        try:"
                + NL
                + "            return await f(*a, **k)"
                + NL
                + "        except Exception:"
                + NL
                + "            return None"
                + NL
                + NL
                + "    return g",
            ),
        ],
        _pytest(
            f"{UJI_TERBIT}::test_tiap_baris_peta_batal_bila_eventnya_gagal_terbit[POST /journal]"
        ),
        harus_memuat="galat penerbitan ditelan",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "K8: scope ditambahkan ke kode tanpa spec/05",
        [
            Sunting(
                f"{MODUL}/identity/scope.py",
                '        "journal_raw": Scope("isi jurnal apa adanya, dan memori episodiknya (3.6)", sensitif=True),',
                '        "journal_raw": Scope("isi jurnal apa adanya, dan memori episodiknya (3.6)", sensitif=True),'
                + NL
                + '        "health": Scope("kesehatan", sensitif=True),',
            )
        ],
        _pytest("tests/unit/test_scope_resmi.py::test_daftar_scope_resmi_spec05_sama_dengan_kode"),
        harus_memuat="spec/05 ≠ identity.SCOPE_RESMI",
    ),
    Mutasi(
        "3.3",
        "K8: `python -m hvx.pekerja` tidak menjalankan apa pun",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                "def main() -> None:" + NL + "    asyncio.run(_utama())",
                "def main() -> None:" + NL + "    return None",
            )
        ],
        _pytest(f"{UJI_PEKERJA}::test_python_m_hvx_pekerja_sebagai_proses_sungguhan"),
        harus_memuat="tidak menyalurkan event",
        kelompok="db",
    ),
    # ── Sprint 3 · tinjauan penegak buta: 68 mutasi dicoba, 49 lolos seluruh suite ──
    # Tiap mutasi di bawah LOLOS suite sebelum uji pembunuhnya ditulis. M07 · M08
    # (penanda ber-TTL) dan M19 (FOR UPDATE SKIP LOCKED) tidak berlaku lagi: desain
    # penanda dan penyelaras sudah diganti tinjauan keamanan/kontrak (S3 · K3).
    Mutasi(
        "3.1",
        "kunci yang sama untuk SUBJEK lain ditelan sebagai kiriman ulang",
        [
            Sunting(
                f"{MODUL}/events/penerbit.py", "        and lama.subject_id == subject_id" + NL, ""
            )
        ],
        _pytest(f"{UJI_EVENT}::test_kunci_sama_untuk_subjek_atau_jenis_lain_ditolak_keras"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        "kunci yang sama untuk JENIS lain (dilewati → dicabut) ditelan",
        [
            Sunting(
                f"{MODUL}/events/penerbit.py",
                "        lama.event_type == event_type"
                + NL
                + "        and lama.subject_type == subject_type"
                + NL,
                "        lama.subject_type == subject_type" + NL,
            )
        ],
        _pytest(f"{UJI_EVENT}::test_kunci_sama_untuk_subjek_atau_jenis_lain_ditolak_keras"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        "recorded_at = now() — membeku di awal transaksi, relay melompatinya",
        [
            Sunting(
                f"{MODUL}/events/repository.py",
                "    VALUES (:user_id, :event_type, :schema_version, :occurred_at, clock_timestamp(),",
                "    VALUES (:user_id, :event_type, :schema_version, :occurred_at, now(),",
            )
        ],
        _pytest(f"{UJI_EVENT}::test_recorded_at_saat_event_masuk_bukan_awal_transaksinya"),
        harus_memuat="recorded_at = awal transaksi",
        kelompok="db",
    ),
    Mutasi(
        "3.1",
        "kontrak V0 bernomor versi 2 — tidak dikenal satu konsumen pun",
        [
            Sunting(
                f"{MODUL}/events/kontrak.py",
                '    "mood.logged": (1, MoodDicatat),',
                '    "mood.logged": (2, MoodDicatat),',
            )
        ],
        _pytest("tests/unit/test_kontrak_event.py::test_tiap_kontrak_v0_schema_version_1"),
        harus_memuat="kontrak V0 bernomor versi lain",
    ),
    Mutasi(
        "3.1",
        "valence 0 lolos uji admisi (spec/01: 1–5)",
        [
            Sunting(
                f"{MODUL}/events/kontrak.py",
                "    valence: Annotated[int, Field(ge=1, le=5)]",
                "    valence: Annotated[int, Field(ge=0, le=5)]",
            )
        ],
        _pytest("tests/unit/test_kontrak_event.py::test_payload_di_luar_kontrak_ditolak"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "3.3",
        "relay tidak menyimpan kursornya — riwayat dikirim ulang tiap putaran",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                '            await self._r.set(self._k_posisi(), f"{maju[0].isoformat()}|{maju[1]}")'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_penanda_relay_dipangkas_di_luar_jendela_belakang"),
        harus_memuat="event lama terkirim",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "siapkan() melempar BUSYGROUP — pekerja yang dimulai ulang mati",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                '            if "BUSYGROUP" not in str(galat):',
                "            if galat:",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_konsumen_dimulai_ulang_grupnya_tidak_dibuat_ulang"),
        harus_memuat="BUSYGROUP",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "bawaan min_idle_ms 0 — pesan yang masih dikerjakan direbut, gagal diulang seketika",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                "        min_idle_ms: int = 30_000,",
                "        min_idle_ms: int = 0,",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_bawaan_konsumen_tidak_mencoba_ulang_sebelum_menganggur_30_dtk"),
        harus_memuat="tanpa menunggu 30 dtk",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "bawaan maks_kirim 50 — spec/03: stream mati sesudah 5",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                "        maks_kirim: int = 5,",
                "        maks_kirim: int = 50,",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_bawaan_konsumen_stream_mati_sesudah_5_kali"),
        harus_memuat="dicoba 8 kali",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pesan yang event-nya sudah tidak ada tidak di-ACK — rujukannya ke stream mati",
        [
            Sunting(
                f"{MODUL}/events/stream.py",
                "        await self._r.xack(self.stream, self.grup, id_pesan)"
                + NL
                + "        return 1 if baris is not None else 0",
                "        if baris is not None:"
                + NL
                + "            await self._r.xack(self.stream, self.grup, id_pesan)"
                + NL
                + "        return 1 if baris is not None else 0",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_event_akun_yang_dihapus_selesai_bukan_ke_stream_mati"),
        harus_memuat="akun yang dihapus menumpuk",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pangkas membandingkan id pesan sebagai teks — 5-10 < 5-9",
        [
            Sunting(
                f"{MODUL}/events/relay.py",
                "        paling_awal = min(batas, key=_urutan_id)",
                "        paling_awal = min(batas)",
            )
        ],
        _pytest(f"{UJI_RELAY}::test_pangkas_membandingkan_id_pesan_sebagai_angka"),
        harus_memuat="pesan yang belum di-ACK dibuang",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pekerja tidak memeriksa perannya — mulai sebagai superuser pemilik (B-40)",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                "        await platform.pastikan_peran_aplikasi(engine, pekerja=True)" + NL,
                "",
            )
        ],
        _pytest(
            "tests/integration/test_aplikasi_hidup.py::"
            "test_pekerja_menolak_mulai_dengan_peran_yang_salah[dsn_pemilik-superuser]"
        ),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "pekerja tidak pernah memangkas stream — Redis noeviction tumbuh selamanya",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                "            if putaran % PANGKAS_TIAP == 0:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_PEKERJA}::test_pekerja_memangkas_stream_yang_sudah_selesai"),
        harus_memuat="tidak pernah memangkas",
        kelompok="db",
    ),
    Mutasi(
        "3.3",
        "putaran yang gagal diulang tanpa jeda — CPU berputar, log banjir",
        [
            Sunting(
                "apps/api/src/hvx/pekerja.py",
                "            jeda = max(jeda_s, 1.0)  # galat berulang tidak memutar CPU",
                "            jeda = jeda_s",
            )
        ],
        _pytest("tests/unit/test_pekerja_ulang.py::test_putaran_yang_gagal_dijeda_sebelum_diulang"),
        harus_memuat="putaran gagal dalam 0,3 dtk",
    ),
    Mutasi(
        "3.6",
        "koreksi waktu jurnal tidak menggeser memorinya",
        [Sunting(f"{MODUL}/memory/repository.py", "      valid_from = :valid_from," + NL, "")],
        _pytest(f"{UJI_MEMORI}::test_waktu_jurnal_yang_dikoreksi_menggeser_memorinya"),
        harus_memuat="tidak mengikuti waktu yang dikoreksi",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "ekstraksi memakai waktu EVENT — koreksi sebelum diekstrak hilang",
        [
            Sunting(
                f"{MODUL}/memory/ekstraksi.py",
                '        isi, scope, sejak = teks_jurnal(jurnal), "journal_raw", jurnal.occurred_at',
                '        isi, scope, sejak = teks_jurnal(jurnal), "journal_raw", ev.occurred_at',
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_waktu_jurnal_yang_dikoreksi_menggeser_memorinya"),
        harus_memuat="tidak mengikuti waktu yang dikoreksi",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "ubah judul saja tidak menyelaraskan memori — judul lama tertinggal",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "            if jurnal is not None:" + NL + "                for p in pendengar:",
                '            if jurnal is not None and "body" in perubahan:'
                + NL
                + "                for p in pendengar:",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_ubah_judul_saja_memori_mengikuti"),
        harus_memuat="judul lama tetap di memori",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "hapus jurnal tidak mengosongkan ringkasan memorinya",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "    UPDATE memories SET content = '', summary = NULL, deleted_at = now()",
                "    UPDATE memories SET content = '', deleted_at = now()",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_hapus_jurnal_mengosongkan_ringkasan_memorinya"),
        harus_memuat="ringkasan isi jurnal yang dihapus",
        kelompok="db",
    ),
    Mutasi(
        "3.6",
        "event tanpa subjek dilewati diam-diam — tidak pernah ke stream mati",
        [
            Sunting(
                f"{MODUL}/memory/ekstraksi.py",
                '        raise ValueError(f"{ev.event_type} tanpa subject_id — tidak ada yang bisa diekstrak")',
                "        return",
            )
        ],
        _pytest(
            "tests/unit/test_ekstraksi_memori.py::test_event_tanpa_subjek_menjadi_galat_bukan_dilewati"
        ),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "3.7",
        "pencarian menyerahkan memori yang masa berlakunya lewat",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "      AND (valid_until IS NULL OR valid_until > now())" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_memori_yang_masa_berlakunya_lewat_tidak_diserahkan"),
        harus_memuat="valid_until-nya lewat",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "pencarian menyerahkan lebih dari `batas`",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                "        return HasilCariMemori(items[:batas], dipakai, perlu_izin)",
                "        return HasilCariMemori(items, dipakai, perlu_izin)",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_hasil_dibatasi_dan_terurut_dari_yang_paling_mirip"),
        harus_memuat="batas 1, diserahkan",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "hasil terurut dari yang paling TIDAK mirip",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                "for k in positif if k.id in baris]",
                "for k in reversed(positif) if k.id in baris]",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_hasil_dibatasi_dan_terurut_dari_yang_paling_mirip"),
        harus_memuat="tidak terurut dari yang paling mirip",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "Qdrant ditanya tanpa saringan model penyemat",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                '                saring={"scope": dipakai, "model": [self._penyemat.nama]},',
                '                saring={"scope": dipakai},',
            )
        ],
        _pytest(
            f"{UJI_MEMORI}::test_qdrant_hanya_ditanya_titik_penyemat_ini_di_scope_yang_diizinkan"
        ),
        harus_memuat="saringan Qdrant",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "scope yang DITOLAK pengguna dilaporkan perlu izin — pengguna ditanya lagi",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py",
                '            elif keputusan == "ask":',
                "            else:",
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_agent_tanpa_izin_scope_tidak_menerima_barisnya"),
        harus_memuat="dilaporkan perlu izin",
        kelompok="db",
    ),
    Mutasi(
        "3.7",
        "kandidat per hasil 1× — titik basi menghabiskan seluruh halaman",
        [
            Sunting(
                f"{MODUL}/memory/pencarian.py", "_KANDIDAT_PER_HASIL = 3", "_KANDIDAT_PER_HASIL = 1"
            )
        ],
        _pytest(f"{UJI_MEMORI}::test_titik_memori_terhapus_tidak_menyingkirkan_hasil_yang_sah"),
        harus_memuat="hasil sah tersingkir",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "PATCH /journal ke masa depan diterima",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "            await _periksa_waktu(conn, badan.occurred_at)"
                + NL
                + '            isi = perubahan.get("body")',
                '            isi = perubahan.get("body")',
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_jurnal_masa_depan_422"),
        harus_memuat="PATCH ke masa depan diterima",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "PATCH menyunting jurnal yang sudah dihapus — isinya hidup lagi di memori",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "                         ELSE occurred_at END"
                + NL
                + "    WHERE id = :id AND deleted_at IS NULL"
                + NL,
                "                         ELSE occurred_at END" + NL + "    WHERE id = :id" + NL,
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_jurnal_yang_dihapus_tidak_bisa_diubah_atau_dihapus_lagi"),
        harus_memuat="PATCH sesudah DELETE: 200",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "DELETE kedua 204 — pendengarnya berjalan lagi",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                # Tanpa kata kunci UPDATE di jangkar — S608 membaca potongan SQL sebagai kueri.
                "journal_entries SET deleted_at = now()"
                + NL
                + "    WHERE id = :id AND deleted_at IS NULL"
                + NL,
                "journal_entries SET deleted_at = now()" + NL + "    WHERE id = :id" + NL,
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_jurnal_yang_dihapus_tidak_bisa_diubah_atau_dihapus_lagi"),
        harus_memuat="DELETE kedua: 204",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "GET /journal mengabaikan ?from=",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "      AND (CAST(:dari AS timestamptz) IS NULL OR occurred_at >= CAST(:dari AS timestamptz))"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_daftar_terbaru_dulu_dan_rentang_waktu"),
        harus_memuat="rentang from–to",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "GET /journal from ≥ to tidak ditolak",
        [
            Sunting(
                f"{MODUL}/journal/service.py",
                "    if dari is not None and sampai is not None and dari >= sampai:"
                + NL
                + '        raise platform.GalatApi(400, "invalid_request", "`from` wajib sebelum `to`.")'
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_daftar_terbaru_dulu_dan_rentang_waktu"),
        harus_memuat="from sesudah to: 200",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "GET /journal terurut naik — kursor keyset menggandakan halaman",
        [
            Sunting(
                f"{MODUL}/journal/repository.py",
                "    ORDER BY occurred_at DESC, id DESC" + NL + "    LIMIT :batas",
                "    ORDER BY occurred_at, id" + NL + "    LIMIT :batas",
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_daftar_terbaru_dulu_dan_rentang_waktu"),
        harus_memuat="urutan halaman",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "PATCH {body: null} tidak ditolak di validasi",
        [
            Sunting(
                f"{MODUL}/journal/schemas.py",
                '            f for f in self.model_fields_set if f != "title" and getattr(self, f) is None',
                '            f for f in self.model_fields_set if f == "__tidak_ada__"',
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_ubah_jurnal_berbentuk_salah_400"),
        harus_memuat="{'body': None} →",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "PATCH /journal menerima medan yang tidak dikenal",
        [
            Sunting(
                f"{MODUL}/journal/schemas.py",
                '    """`PATCH /journal/{id}` — medan yang DIKIRIM saja; `title: null` = hapus judul."""'
                + NL
                + NL
                + '    model_config = ConfigDict(extra="forbid")'
                + NL,
                '    """`PATCH /journal/{id}` — medan yang DIKIRIM saja; `title: null` = hapus judul."""'
                + NL,
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_ubah_jurnal_berbentuk_salah_400"),
        harus_memuat="{'judul': 'x'} → 200",
        kelompok="db",
    ),
    Mutasi(
        "3.4",
        "jumlah kata hanya dipisah spasi tunggal — baris baru & tab tidak",
        [
            Sunting(
                f"{MODUL}/journal/schemas.py",
                "    return len(isi.split())",
                '    return len(isi.split(" "))',
            )
        ],
        _pytest(f"{UJI_JURNAL}::test_jumlah_kata_dipisah_spasi_apa_pun"),
        harus_memuat="bukan 4",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "mood.logged membawa waktu tercatat, bukan waktu kejadiannya",
        [
            Sunting(
                f"{MODUL}/checkins/service.py",
                "                occurred_at=mood.occurred_at,",
                "                occurred_at=mood.created_at,",
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_dua_mood_dalam_satu_menit_dua_event"),
        harus_memuat="occurred_at event mood",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "jam tidur dibandingkan sebagai Decimal — catatan saja menerbitkan event",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "    tidur = float(b.sleep_hours) if b.sleep_hours is not None else None",
                "    tidur = b.sleep_hours",
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_catatan_saja_tanpa_event_walau_jam_tidur_pecahan"),
        harus_memuat="catatan saja menerbitkan event",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "isi check-in sebelum PUT dibaca tanpa kunci — perubahan serentak hilang dari events",
        [
            Sunting(
                f"{MODUL}/checkins/repository.py",
                "    WHERE user_id = :user_id AND for_date = :for_date"
                + NL
                + "    FOR UPDATE"
                + NL,
                "    WHERE user_id = :user_id AND for_date = :for_date" + NL,
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_put_serentak_yang_mengubah_baris_selalu_menerbitkan"),
        harus_memuat="PUT 2 → 3 tidak menerbitkan event",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "checkin.logged tanpa focus",
        [Sunting(f"{MODUL}/checkins/service.py", '                    "focus": c.focus,' + NL, "")],
        _pytest(f"{UJI_TERBIT}::test_event_check_in_membawa_semua_medannya"),
        harus_memuat="payload check-in",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "habit.completed tanpa note (kontrak spec/03 hari ini — C-33)",
        [
            Sunting(
                f"{MODUL}/habits/service.py",
                '        payload = {"status": p.status, "tier_used": p.tier_used, "note": p.note}',
                '        payload = {"status": p.status, "tier_used": p.tier_used}',
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_event_penyelesaian_membawa_catatannya"),
        harus_memuat="catatan hilang dari event",
        kelompok="db",
    ),
    Mutasi(
        "3.2",
        "days_taken dari .seconds — goal yang berhari-hari tercatat 0 hari",
        [
            Sunting(
                f"{MODUL}/goals/service.py",
                '                payload={"days_taken": (goal.achieved_at - goal.created_at).days},',
                '                payload={"days_taken": (goal.achieved_at - goal.created_at).seconds // 86400},',
            )
        ],
        _pytest(f"{UJI_TERBIT}::test_days_taken_goal_yang_berhari_hari"),
        harus_memuat="days_taken",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "id aktivitas ganda 500, bukan 409",
        [
            Sunting(
                f"{MODUL}/activities/service.py",
                '        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "activities_pkey":',
                '        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "activity_pkey":',
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_id_buatan_klien_yang_sudah_ada_409"),
        harus_memuat="id ganda → 500",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "GET /activities mengabaikan ?to=",
        [
            Sunting(
                f"{MODUL}/activities/repository.py",
                "      AND (CAST(:sampai AS timestamptz) IS NULL OR occurred_at < CAST(:sampai AS timestamptz))"
                + NL,
                "",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_saring_rentang_waktu"),
        harus_memuat="rentang from–to aktivitas",
        kelompok="db",
    ),
    Mutasi(
        "3.8",
        "duration_seconds tanpa batas 7 hari",
        [
            Sunting(
                f"{MODUL}/activities/schemas.py",
                "    duration_seconds: platform.Bulat | None = Field(default=None, ge=0, le=_DURASI_MAKS_S)",
                "    duration_seconds: platform.Bulat | None = Field(default=None, ge=0)",
            )
        ],
        _pytest(f"{UJI_AKTIVITAS}::test_aktivitas_berbentuk_salah_400"),
        harus_memuat="691200",
        kelompok="db",
    ),
    Mutasi(
        "3.5",
        "kunci API Qdrant dikirim di kepala `api_key` — 401 di tiap panggilan produksi",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                '        kepala = {"api-key": kunci_api} if kunci_api else {}',
                '        kepala = {"api_key": kunci_api} if kunci_api else {}',
            )
        ],
        _pytest("tests/unit/test_klien_vektor.py::test_kunci_api_dikirim_di_kepala_api_key"),
        harus_memuat="kunci tidak di kepala api-key",
    ),
    Mutasi(
        "3.5",
        "penyemat peka huruf besar — `Rapat` tidak menemukan `rapat`",
        [
            Sunting(
                f"{MODUL}/platform/sematan.py",
                '        normal = unicodedata.normalize("NFKC", teks).casefold()',
                '        normal = unicodedata.normalize("NFKC", teks)',
            )
        ],
        _pytest("tests/unit/test_sematan.py::test_huruf_besar_dan_kecil_kata_yang_sama"),
        harus_memuat="Rapat ≠ rapat",
    ),
    Mutasi(
        "3.5",
        "jarak koleksi yang sudah ada tidak diperiksa — skor Euclid dibaca sebagai kosinus",
        [
            Sunting(
                f"{MODUL}/platform/vektor.py",
                '            if not isinstance(vektor, dict) or (vektor.get("size"), vektor.get("distance")) != (',
                '            if not isinstance(vektor, dict) or (vektor.get("size"), "Cosine") != (',
            )
        ],
        _pytest(f"{UJI_VEKTOR}::test_koleksi_berjarak_lain_ditolak_bukan_dipakai"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    # ── Sprint 1 · 1.5, ditemukan uji yang berkedip di gerbang penuh Sprint 3 ──
    Mutasi(
        "1.5",
        "umur cache izin sementara RELATIF dari saat dibaca — jeda tulis memperpanjangnya",
        [
            Sunting(
                f"{MODUL}/identity/izin.py",
                "        return cast(Keputusan, baris.decision), _UmurCache(pxat=habis)",
                "        return cast(Keputusan, baris.decision), _UmurCache(px=habis - baris.kini_ms)",
            )
        ],
        _pytest(f"{UJI_IZIN}::test_cache_yang_ditulis_terlambat_tidak_melewati_izin_sementaranya"),
        harus_memuat="cache yang ditulis terlambat melewati izin sementaranya",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.3 tool registry: di luar registry tak bisa dipanggil; agent lewat gerbang ──
    Mutasi(
        "4.3",
        "registry ≠ implementasi diterima — tool berimplementasi tanpa risk_level",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if tanpa_impl or tanpa_daftar:",
                "        if tanpa_impl:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_registry_dan_implementasi_satu_lawan_satu"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.3",
        "tool di luar registry tidak ditolak sebagai tidak_terdaftar",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py", "        if alat is None:", "        if False:"
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_tool_di_luar_registry_tidak_bisa_dipanggil"),
        harus_memuat="tool di luar registry dijalankan",
    ),
    Mutasi(
        "4.3",
        "agent memanggil tool yang tidak dinyatakan manifest-nya",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if nama not in jalannya.agent.tools:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_agent_hanya_memanggil_tool_manifestnya"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.3",
        "medan masukan tak dikenal diterima",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                '        raise _salah(alat.name, f"medan tak dikenal: {asing}")',
                "        pass",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="'lain': 1} diterima",
    ),
    Mutasi(
        "4.3",
        "medan masukan wajib boleh hilang",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "            if medan.required:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="habit.streak {} diterima",
    ),
    Mutasi(
        "4.3",
        "tanggal bentuk dasar ISO (20260901) diterima — hanya fromisoformat",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if not isinstance(nilai, str) or not _TANGGAL.fullmatch(nilai):",
                "        if not isinstance(nilai, str):",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="'20260901'} diterima",
    ),
    Mutasi(
        "4.3",
        "boolean diterima sebagai bilangan bulat (E-170 di sisi agent)",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if isinstance(nilai, bool) or not isinstance(nilai, int):",
                "        if not isinstance(nilai, int):",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="{'hari': True} diterima",
    ),
    Mutasi(
        "4.3",
        "pemanggilan tool tidak menanyai gerbang — agent memanggil agent tanpa gerbang",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        await self._gerbang.periksa(jalannya, alat, bersih)\n",
                "",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_pemanggilan_agent_ikut_melewati_gerbang"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.3",
        "keluaran tool tidak diperiksa skemanya — medan tak dinyatakan lolos",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        periksa_keluaran(alat, keluaran)\n",
                "",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_keluaran_di_luar_skema_adalah_cacat"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.3",
        "batas laju tool tidak ditegakkan",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        await self._batasi(jalannya, alat)\n",
                "",
            )
        ],
        _pytest(f"{UJI_ALAT}::test_batas_laju_tool_per_pengguna"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "checkin.get membocorkan catatan bebas pengguna (C-32)",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                '            "sleep_hours": c.sleep_hours,\n',
                '            "sleep_hours": c.sleep_hours,\n            "note": c.note,\n',
            )
        ],
        _pytest(f"{UJI_ALAT}::test_alat_baca_coach_tanpa_catatan_bebas_pengguna"),
        harus_memuat="catatan bebas pengguna keluar",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "mood.recent membocorkan catatan bebas pengguna (C-32)",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                '{"valence": x.valence, "label": x.label, "occurred_at": x.occurred_at.isoformat()}',
                '{"valence": x.valence, "label": x.label, "note": x.note, "occurred_at": x.occurred_at.isoformat()}',
            )
        ],
        _pytest(f"{UJI_ALAT}::test_alat_baca_coach_tanpa_catatan_bebas_pengguna"),
        harus_memuat="catatan bebas pengguna keluar",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "pagu scope tidak diperiksa — memory.write ke journal_raw sampai ke gerbang",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        _periksa_pagu_scope(jalannya, alat, bersih)\n",
                "",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_scope_memory_write_di_luar_pagu_ditolak_sebelum_gerbang"),
        harus_memuat="memory.write ke journal_raw diterima — DENY naskah 5 §15",
    ),
    Mutasi(
        "4.3",
        "pagu manifest tidak membatasi scope memory.write — hanya scopes tool",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if scope not in alat.scopes or scope not in pagu:",
                "        if scope not in alat.scopes:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_scope_memory_write_di_luar_pagu_ditolak_sebelum_gerbang"),
        harus_memuat="memory.write ke habits diterima — pagu manifest sempit",
    ),
    Mutasi(
        "4.3",
        "scopes tool tidak membatasi scope memory.write — manifest melebar menang",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if scope not in alat.scopes or scope not in pagu:",
                "        if scope not in pagu:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_scope_memory_write_di_luar_pagu_ditolak_sebelum_gerbang"),
        harus_memuat="memory.write ke journal_raw diterima — manifest melebar",
    ),
    Mutasi(
        "4.3",
        "enum skema tool tidak ditegakkan — status habit sembarang sampai ke gerbang R2",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if medan.enum is not None and nilai not in medan.enum:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="'status': 'x'} diterima",
    ),
    Mutasi(
        "4.3",
        "min/max skema tool tidak ditegakkan",
        [
            Sunting(
                f"{MODUL}/agents/pelaksana_alat.py",
                "        if (medan.min is not None and nilai < medan.min) or (",
                "        if False and (",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_masukan_yang_salah_ditolak_sebelum_gerbang"),
        harus_memuat="'tier_used': -1} diterima",
    ),
    Mutasi(
        "4.3",
        "enum pada medan bilangan diterima registry",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '        if self.enum is not None and (self.type != "string" or not self.enum):',
                "        if False:",
            )
        ],
        _pytest(f"{UJI_REGISTRI}"),
        harus_memuat="aturan bentuk tidak ditegakkan — enum pada medan bilangan",
    ),
    Mutasi(
        "4.3",
        "min/max pada medan teks diterima registry",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '        if berbatas and self.type not in ("integer", "number"):',
                "        if False:",
            )
        ],
        _pytest(f"{UJI_REGISTRI}"),
        harus_memuat="aturan bentuk tidak ditegakkan — min pada medan teks",
    ),
    Mutasi(
        "4.3",
        "min > max diterima registry — medan yang tak pernah sah",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "        if self.min is not None and self.max is not None and self.min > self.max:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_REGISTRI}"),
        harus_memuat="aturan bentuk tidak ditegakkan — min lebih besar daripada max",
    ),
    Mutasi(
        "4.3",
        "skema tool menyimpang dari modul pemiliknya (status habit)",
        [
            Sunting(
                f"{MODUL}/agents/alat/habit.complete.yaml",
                "enum: [done, skipped, partial]",
                "enum: [done, skipped]",
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_batas_nilai_tool_sama_dengan_modul_pemiliknya"),
        harus_memuat="habit.complete.status",
    ),
    Mutasi(
        "4.3",
        "mood.recent memotong diam-diam",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                '    return {  # tanpa `note` (C-32)\n        "terpotong": halaman.next_cursor is not None,',
                '    return {  # tanpa `note` (C-32)\n        "terpotong": False,',
            )
        ],
        _pytest(f"{UJI_ALAT}::test_daftar_yang_terpotong_mengatakannya"),
        harus_memuat="mood terpotong diam-diam",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "goal.list memotong diam-diam",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                '(K-24)\n        "terpotong": halaman.next_cursor is not None,',
                '(K-24)\n        "terpotong": False,',
            )
        ],
        _pytest(f"{UJI_ALAT}::test_daftar_yang_terpotong_mengatakannya"),
        harus_memuat="goal terpotong diam-diam",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "memory.search mencatat scope yang DIMINTA, bukan yang diizinkan",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                "    k.jalannya.catat_scope(*hasil.scope_dipakai)",
                "    k.jalannya.catat_scope(*k.jalannya.agent.memory.read)",
            )
        ],
        _pytest(f"{UJI_ALAT}::test_memory_search_hanya_scope_manifest_yang_diizinkan"),
        harus_memuat="scope yang dicatat run",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "agent.coach memanggil agent yang salah",
        [
            Sunting(
                f"{MODUL}/agents/alat_v0.py",
                '    "agent.coach": _agent("coach-agent"),',
                '    "agent.coach": _agent("habit-agent"),',
            )
        ],
        _pytest(f"{UJI_PELAKSANA}::test_pemanggilan_agent_ikut_melewati_gerbang"),
        harus_memuat="agent yang ditolak tetap dipanggil",
    ),
    Mutasi(
        "4.3",
        "memory.write mengingat hal yang sama dua kali",
        [
            Sunting(
                f"{MODUL}/memory/repository.py",
                "    if ada is not None:\n        return ada.id, False\n",
                "",
            )
        ],
        _pytest(f"{UJI_ALAT}::test_memory_write_hanya_bila_belum_diingat_dan_di_scope_manifestnya"),
        harus_memuat="diingat dua kali",
        kelompok="db",
    ),
    Mutasi(
        "4.3",
        "rekomendasi tanpa alasan disimpan",
        [
            Sunting(
                f"{MODUL}/intelligence/rekomendasi.py",
                "        not rationale\n        or len(rationale) > ALASAN_MAKS",
                "        len(rationale) > ALASAN_MAKS",
            )
        ],
        _pytest(f"{UJI_ALAT}::test_recommendation_create_menyimpan_keyakinan_dan_alasan"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.4 agent runtime: tiap run mencatat tools, scope, decision, confidence, cost ──
    Mutasi(
        "4.4",
        "balasan tanpa alasan diterima (Konstitusi Pasal 3)",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "    if not 1 <= len(k.rationale) <= ALASAN_MAKS or not all(",
                "    if len(k.rationale) > ALASAN_MAKS or not all(",
            )
        ],
        _pytest(f"{UJI_KEPUTUSAN}"),
        harus_memuat="keputusan rusak diterima — tanpa alasan",
    ),
    Mutasi(
        "4.4",
        "keyakinan di luar 0–1 diterima",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "    if not isinstance(k.confidence, Decimal) or not Decimal(0) <= k.confidence <= Decimal(1):",
                "    if not isinstance(k.confidence, Decimal):",
            )
        ],
        _pytest(f"{UJI_KEPUTUSAN}"),
        harus_memuat="keputusan rusak diterima — keyakinan di atas 1",
    ),
    Mutasi(
        "4.4",
        "decision bersarang diterima — penalaran masuk jejak audit",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "        if nilai is not None and not isinstance(nilai, str | int | bool):",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_KEPUTUSAN}"),
        harus_memuat="keputusan rusak diterima — aksi bersarang — penalaran",
    ),
    Mutasi(
        "4.4",
        "decision berisi tulisan panjang diterima",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "        if isinstance(nilai, str) and len(nilai) > AKSI_NILAI_MAKS:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_KEPUTUSAN}"),
        harus_memuat="keputusan rusak diterima — aksi berisi tulisan panjang",
    ),
    Mutasi(
        "4.4",
        "keputusan program tidak diperiksa runtime",
        [Sunting(f"{MODUL}/agents/runtime.py", "            periksa_keputusan(keputusan)\n", "")],
        _pytest(f"{UJI_RUNTIME}::test_keputusan_tanpa_alasan_menggagalkan_run"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "tools_used tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "                tools_used=j.alat_dipakai,",
                "                tools_used=[],",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="tool yang dipakai tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "memory_scopes tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "                memory_scopes=sorted(j.scope_dipakai),",
                "                memory_scopes=[],",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="scope yang disentuh tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "decision tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            dict(keputusan.aksi) if keputusan is not None else dict(aksi or {"action": status})',
                '            dict(aksi or {"action": status})',
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="keputusan tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "confidence tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "                confidence=None if keputusan is None else keputusan.confidence,",
                "                confidence=None,",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="keyakinan tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "biaya tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "                cost_usd=j.biaya_usd,",
                "                cost_usd=Decimal(0),",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="biaya tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "model tidak dicatat",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '                model_used=",".join(j.model_dipakai) or None,',
                "                model_used=None,",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="model tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "peristiwa tool_call tidak mengalir ke klien",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '        await self._kabari("tool_call", {"tool": nama, "agent": self.jalannya.agent.name})\n',
                "",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="peristiwa tool_call tidak mengalir",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "token model tidak mengalir ke klien",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '                await self._kabari("token", {"text": p})',
                "                pass",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_mencatat_tools_scope_decision_confidence_cost"),
        harus_memuat="token tidak mengalir",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "run yang gagal dibiarkan running",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            await self._tutup(\n                j,\n                status,\n                None,\n                {"code": _kode_galat(galat), "type": type(galat).__name__},\n                mulai,\n                aksi=_aksi_tertahan(galat) if status == "blocked" else None,\n            )\n',
                "",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_yang_gagal_tetap_ditutup_tanpa_isi_galat"),
        harus_memuat="run yang gagal dibiarkan `running`",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "isi galat (dan pesan pengguna) masuk jejak audit",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '{"code": _kode_galat(galat), "type": type(galat).__name__}',
                '{"code": _kode_galat(galat), "type": type(galat).__name__, "pesan": str(galat)}',
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_yang_gagal_tetap_ditutup_tanpa_isi_galat"),
        harus_memuat="isi galat — dan pesan pengguna — masuk jejak audit",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "run yang ditahan gerbang tercatat gagal",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            status: StatusRun = (\n                "blocked"\n                if isinstance(galat, AlatDitolak) and galat.kode in KODE_GERBANG\n                else "failed"\n            )',
                '            status: StatusRun = "failed"',
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_yang_ditahan_gerbang_blocked_bukan_failed"),
        harus_memuat="run yang menunggu manusia tercatat sebagai kegagalan",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "run yang dibatalkan tidak ditutup",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            await asyncio.shield(self._tutup(j, "cancelled", None, {"code": "cancelled"}, mulai))\n',
                "",
            )
        ],
        _pytest(
            f"{UJI_RUNTIME}::test_run_yang_dibatalkan_di_tengah_aliran_tetap_ditutup_dan_dibayar"
        ),
        harus_memuat="run yang dibatalkan tidak ditutup",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "aliran yang ditinggal klien tidak ditutup — tokennya tidak tercatat",
        [Sunting(f"{MODUL}/agents/runtime.py", "            await potongan.aclose()\n", "")],
        _pytest(f"{UJI_RUNTIME}::test_klien_lambat_yang_dibatalkan_tokennya_tetap_tercatat"),
        harus_memuat="token aliran yang ditinggal klien tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "aliran model yang terputus tidak menghitung token yang sudah keluar",
        [
            Sunting(
                f"{MODUL}/platform/model.py",
                '        try:\n            async for p in self._potongan:\n                bagian.append(p)\n                yield p\n        finally:\n            self.jawaban = self._selesai("".join(bagian))\n',
                '        async for p in self._potongan:\n            bagian.append(p)\n            yield p\n        self.jawaban = self._selesai("".join(bagian))\n',
            )
        ],
        _pytest(
            f"{UJI_RUNTIME}::test_run_yang_dibatalkan_di_tengah_aliran_tetap_ditutup_dan_dibayar"
        ),
        harus_memuat="token aliran yang terputus tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "run yang sudah selesai bisa ditutup lagi — jejak ditimpa",
        [
            Sunting(
                f"{MODUL}/agents/repository.py",
                "    WHERE id = :id AND status = 'running'",
                "    WHERE id = :id",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_tidak_bisa_ditutup_dua_kali"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.4",
        "run anak menunjuk run induk milik pengguna lain",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "        if induk is not None and (induk.user_id != user_id or not induk.tersimpan):",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_RUNTIME}::test_run_anak_tidak_bisa_menunjuk_run_pengguna_lain"),
        harus_memuat="IntegrityError",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.5 gerbang risiko: risk 2 minta izin sekali; risk 3 minta setiap kali ──
    Mutasi(
        "4.5",
        "R2 dijalankan tanpa bertanya — bawaan allow untuk semua risiko",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                '            "allow" if delegasi or alat.risk_level <= RISIKO_BAWAAN_IZINKAN else "ask"',
                '            "allow"',
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_2_minta_izin_sekali"),
        harus_memuat="gerbang tidak menahan — dijalankan tanpa bertanya",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "delegasi ditanya sendiri — satu permintaan ditanya dua kali",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                '            "allow" if delegasi or alat.risk_level <= RISIKO_BAWAAN_IZINKAN else "ask"',
                '            "allow" if alat.risk_level <= RISIKO_BAWAAN_IZINKAN else "ask"',
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_delegasi_tidak_ditanya_dua_kali"),
        harus_memuat="delegasi ditanyakan sendiri",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "izin R2 yang disetujui tidak diingat — ditanya lagi tiap giliran",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                '            await mesin_izin.tetapkan(user_id, subjek, scope, p.aksi, "allow")',
                "            pass",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_2_minta_izin_sekali"),
        harus_memuat="menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "R3 lolos tanpa konfirmasi bila izinnya allow",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                "        konfirmasi = not delegasi and alat.risk_level >= RISIKO_KONFIRMASI",
                "        konfirmasi = False",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_3_minta_setiap_kali"),
        harus_memuat="gerbang tidak menahan — dijalankan tanpa bertanya",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "konfirmasi R3 bisa diingat — tidak lagi ditanya tiap kali",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                '    if jawaban == "izinkan_selalu" and p.jenis != "izin":',
                "    if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_3_minta_setiap_kali"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "konfirmasi pengguna tidak tercatat di run",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                "        if disetujui:\n            jalannya.dikonfirmasi = True\n",
                "",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_3_minta_setiap_kali"),
        harus_memuat="konfirmasi pengguna tidak tercatat di run",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "deny pengguna tidak menolak",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py", '        if "deny" in keputusan:', "        if False:"
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_deny_ditolak_dan_dicatat"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "penolakan gerbang tidak tercatat di audit",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                '                aksi="agent.tool_denied",',
                '                aksi="agent.tool_skipped",',
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_deny_ditolak_dan_dicatat"),
        harus_memuat="penolakan tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "R4 bisa dikonfirmasi — tidak DENY",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                "        if alat.risk_level >= RISIKO_TERLARANG:",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_4_ditolak_tanpa_bertanya"),
        harus_memuat="R4 bisa dikonfirmasi",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "persetujuan berpindah ke pemanggilan lain — sidik masukan tidak dibandingkan",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                "            p.agent == jalannya.agent.name and p.alat == alat.name and p.sidik == sidik",
                "            p.agent == jalannya.agent.name and p.alat == alat.name",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_persetujuan_tidak_berpindah_ke_pemanggilan_lain"),
        harus_memuat="gerbang tidak menahan — dijalankan tanpa bertanya",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "persetujuan giliran tidak diwarisi run anak",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "            persetujuan=persetujuan if induk is None else induk.persetujuan,",
                "            persetujuan=persetujuan,",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_delegasi_tidak_ditanya_dua_kali"),
        harus_memuat="menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "jawaban konfirmasi bisa dipakai dua kali",
        [
            Sunting(
                f"{MODUL}/agents/repository.py",
                "    WHERE id = :id AND status = 'blocked' AND confirmed_by_user IS NULL",
                "    WHERE id = :id AND status = 'blocked'",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_jawaban_sekali_pakai"),
        harus_memuat="KonfirmasiTerjawab",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "jawaban pengguna tidak tercatat di audit",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                '            aksi="agent.action_approved" if setuju else "agent.action_rejected",',
                '            aksi="agent.action_noted",',
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_risk_2_minta_izin_sekali"),
        harus_memuat="jawaban pengguna tidak tercatat",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "token milik pengguna lain diterima",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                '        if d["u"] != str(user_id):',
                "        if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_token_milik_pengguna_lain_ditolak"),
        harus_memuat="KonfirmasiTerjawab",  # lapis kedua (RLS) menahan, dengan galat yang salah
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "tanda tangan token tidak diperiksa",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                "        if not hmac.compare_digest(self._penanda(isi), tanda):",
                "        if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_token_yang_diubah_ditolak"),
        harus_memuat="token yang tanda tangannya diubah diterima",
        kelompok="db",
    ),
    Mutasi(
        "4.5",
        "token kedaluwarsa diterima",
        [
            Sunting(
                f"{MODUL}/agents/konfirmasi.py",
                '        if d["e"] < time.time():',
                "        if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG}::test_token_kedaluwarsa_ditolak"),
        harus_memuat="token kedaluwarsa diterima",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.6 orchestrator: parent_run_id membentuk pohon eksekusi ──
    Mutasi(
        "4.6",
        "run anak tidak menunjuk induknya — pohon putus",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "                parent_run_id=None if induk is None else induk.id,",
                "                parent_run_id=None,",
            )
        ],
        _pytest(f"{UJI_ORKESTRATOR}::test_parent_run_id_membentuk_pohon_eksekusi"),
        harus_memuat="pohon eksekusi:",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "run anak tercatat dipicu pengguna, bukan agent",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            pemicu="agent",',
                '            pemicu="user",',
            )
        ],
        _pytest(f"{UJI_ORKESTRATOR}::test_parent_run_id_membentuk_pohon_eksekusi"),
        harus_memuat="pohon eksekusi:",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "biaya run anak tidak ikut dibayar permintaannya",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "        induk.biaya_turunan_usd += hasil.biaya_usd\n",
                "",
            )
        ],
        _pytest(
            f"{UJI_ORKESTRATOR}::test_balasan_anak_sampai_tanpa_dikarang_ulang_dan_biayanya_ikut"
        ),
        harus_memuat="biaya run anak tidak ikut dibayar permintaannya",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "orchestrator mengarang ulang keyakinan agent yang menjawab",
        [
            Sunting(
                f"{MODUL}/agents/orkestrator.py",
                '        Decimal(str(balasan["confidence"])),',
                '        Decimal("1"),',
            )
        ],
        _pytest(
            f"{UJI_ORKESTRATOR}::test_balasan_anak_sampai_tanpa_dikarang_ulang_dan_biayanya_ikut"
        ),
        harus_memuat="orchestrator mengubah balasan agent yang menjawab",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "perintah habit diserahkan ke coach",
        [
            Sunting(
                f"{MODUL}/agents/orkestrator.py",
                '    "tandai_habit": "agent.habit",',
                '    "tandai_habit": "agent.coach",',
            )
        ],
        _pytest(f"{UJI_ORKESTRATOR}::test_niat_menentukan_agent_yang_dipanggil"),
        harus_memuat="diserahkan ke agent yang salah",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "permintaan mengingat diserahkan ke coach",
        [
            Sunting(
                f"{MODUL}/agents/orkestrator.py",
                '    "ingat": "agent.memory",',
                '    "ingat": "agent.coach",',
            )
        ],
        _pytest(f"{UJI_ORKESTRATOR}::test_niat_menentukan_agent_yang_dipanggil"),
        harus_memuat="diserahkan ke agent yang salah",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "perintah deterministik dijalankan agent (coach)",
        [
            Sunting(
                f"{MODUL}/agents/orkestrator.py",
                "    alat = AGENT_UNTUK.get(niat.jenis)",
                '    alat = AGENT_UNTUK.get(niat.jenis, "agent.coach")',
            )
        ],
        _pytest(f"{UJI_ORKESTRATOR}::test_perintah_deterministik_tidak_dijalankan_agent"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.6",
        "“ingatkan” (pengingat) dibaca sebagai permintaan mengingat",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                '    r"^\\s*(?:tolong\\s+)?ingat(?:lah)?',
                '    r"^\\s*(?:tolong\\s+)?ingat(?:lah|kan)?',
            )
        ],
        _pytest("tests/unit/test_niat.py::test_yang_bukan_perintah_agent_ke_coach"),
        harus_memuat="dijalankan sebagai perintah agent",
    ),
    Mutasi(
        "4.6",
        "kata perintah habit tidak wajib di awal pesan",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                '    r"^\\s*(?:tolong\\s+)?(?P<kata>tandai|',
                '    r".*?(?P<kata>tandai|',
            )
        ],
        _pytest("tests/unit/test_niat.py::test_yang_bukan_perintah_agent_ke_coach"),
        harus_memuat="dijalankan sebagai perintah agent",
    ),
    Mutasi(
        "4.6",
        "“lewati” dicatat sebagai selesai",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                '        lewati = tandai["kata"].lower() in _LEWATI or (tandai["akhir"] or "").lower() in _LEWATI',
                "        lewati = False",
            )
        ],
        _pytest("tests/unit/test_niat.py::test_niat_memilih_agent"),
        harus_memuat="“lewati lari hari ini” dibaca",
    ),
    # ── Sprint 4 · 4.7 agent V0: tiap balasan membawa confidence + rationale ──
    Mutasi(
        "4.7",
        "gerbang ikut menanyakan scope memory.search — tiap jawaban coach tertahan (E-193)",
        [
            Sunting(
                f"{MODUL}/agents/gerbang.py",
                "            if alat.menyaring_izin",
                "            if False",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_tidak_tertahan_scope_ingatan_yang_belum_diputuskan"),
        harus_memuat="memory.search menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "memory.search tidak menyatakan menyaring izinnya sendiri",
        [Sunting(f"{MODUL}/agents/alat/memory.search.yaml", "menyaring_izin: true\n", "")],
        _pytest(f"{UJI_AGENT_V0}::test_coach_tanpa_data_mengatakannya"),
        harus_memuat="memory.search menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "tulisan boleh menyaring izinnya sendiri — lolos dari gerbang",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '    if alat.menyaring_izin and (alat.kind != "read" or alat.side_effects != "none"):',
                "    if False:",
            )
        ],
        _pytest(f"{UJI_REGISTRI}"),
        harus_memuat="aturan bentuk tidak ditegakkan — tulisan yang menyaring izinnya sendiri",
    ),
    Mutasi(
        "4.7",
        "coach berhenti saat satu sumber ditolak pengguna",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "        if _baca_ditolak(galat):\n            return None\n",
                "",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_melewati_sumber_yang_ditolak_dan_mengatakannya"),
        harus_memuat="ditolak_pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "coach melewati “tanya aku” pengguna seperti deny",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                '    return galat.kode == "ditolak_pengguna"',
                "    return True",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_bertanya_bila_pengguna_minta_ditanya"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "coach tidak menyatakan sumber yang dilewati",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "    if dilewati:\n        alasan.append(",
                "    if False:\n        alasan.append(",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_melewati_sumber_yang_ditolak_dan_mengatakannya"),
        harus_memuat="sumber yang dilewati tidak dinyatakan",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "keyakinan coach tidak mengikuti datanya",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "        KEYAKINAN_SUMBER[sumber],",
                "        KEYAKINAN_SUMBER[5],",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_menjawab_dari_data_pengguna_tanpa_catatan_bebasnya"),
        harus_memuat="keyakinan tidak mengikuti datanya",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "alasan coach bukan fakta yang dipakai",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "    alasan = [f[:300] for f in fakta][:9] or [",
                "    alasan = [",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_menjawab_dari_data_pengguna_tanpa_catatan_bebasnya"),
        harus_memuat="alasan bukan fakta yang dipakai",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "coach mengarang bahan saat tidak ada data (Pasal 8)",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "        bahan=fakta,\n",
                '        bahan=fakta or ["Kamu baik-baik saja."],\n',
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_coach_tanpa_data_mengatakannya"),
        harus_memuat="coach mengarang jawaban tanpa data (Pasal 8)",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "habit agent menebak di antara beberapa yang cocok",
        [Sunting(f"{MODUL}/agents/program_v0.py", "    if len(cocok) > 1:", "    if False:")],
        _pytest(f"{UJI_AGENT_V0}::test_habit_agent_tidak_menebak"),
        harus_memuat="menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "habit agent tidak membedakan judul persis",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                "        KEYAKINAN_JUDUL_PERSIS if persis else KEYAKINAN_JUDUL_SEBAGIAN,",
                "        KEYAKINAN_JUDUL_SEBAGIAN,",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_habit_agent_menandai_setelah_izin_sekali"),
        harus_memuat="keyakinan tidak membedakan judul yang cocok persis",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "habit agent menandai “lewati” sebagai selesai",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                '            "habit.complete", {"habit_id": h["id"], "for_date": hari, "status": niat.status}',
                '            "habit.complete", {"habit_id": h["id"], "for_date": hari, "status": "done"}',
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_habit_agent_menandai_setelah_izin_sekali"),
        harus_memuat="“lewati” tidak dicatat sebagai dilewati",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "habit agent tidak memeriksa catatan yang sudah ada — minta izin menulis yang tak berubah",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                '    tercatat = (h.get("day") or {}).get("status")',
                "    tercatat = None",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_habit_agent_tidak_mengaku_mengubah_yang_sudah_tercatat"),
        harus_memuat="menunggu izin pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "habit agent mengaku mengubah catatan yang tercatat bersamaan",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                '        tercatat = hasil["status"] if hasil["status"] != niat.status else None',
                "        tercatat = None",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_habit_agent_jujur_bila_tanggalnya_tercatat_bersamaan"),
        harus_memuat="habit agent mengaku melewati habit yang tercatat selesai",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "memory agent mengaku mengingat lagi",
        [
            Sunting(
                f"{MODUL}/agents/program_v0.py",
                '        if not tulis["baru"]:',
                "        if False:",
            )
        ],
        _pytest(f"{UJI_AGENT_V0}::test_memory_agent_mengingat_hanya_bila_belum_diingat"),
        harus_memuat="memory-agent mengaku mengingat lagi",
        kelompok="db",
    ),
    Mutasi(
        "4.7",
        "agent aktif tanpa program",
        [Sunting(f"{MODUL}/agents/program_v0.py", '    "memory-agent": memori,\n', "")],
        _pytest(f"{UJI_AGENT_V0}::test_tiap_agent_aktif_punya_program"),
        harus_memuat="agent aktif tanpa program",
    ),
    # ── Sprint 4 · 4.8 percakapan + SSE: token mengalir; done memuat cost_usd ──
    Mutasi(
        "4.8",
        "done tanpa biaya permintaannya",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                '        "cost_usd": float(pesan.cost_usd or 0),',
                '        "cost_usd": 0.0,',
            )
        ],
        _pytest(
            f"{UJI_PERCAKAPAN}::test_token_mengalir_lalu_done_membawa_biaya_keyakinan_dan_alasan"
        ),
        harus_memuat="done tanpa biaya permintaannya",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "biaya giliran hanya run akar — run anak tidak dihitung",
        [
            Sunting(
                f"{MODUL}/agents/repository.py",
                "      FROM agent_runs a JOIN pohon p ON a.parent_run_id = p.id",
                "      FROM agent_runs a JOIN pohon p ON false",
            )
        ],
        _pytest(
            f"{UJI_PERCAKAPAN}::test_token_mengalir_lalu_done_membawa_biaya_keyakinan_dan_alasan"
        ),
        harus_memuat="done tanpa biaya permintaannya",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "peristiwa runtime tidak mengalir ke klien",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                "        async def pendengar(jenis: str, data: Mapping[str, Any]) -> None:\n            await self.aliran.kirim(percakapan_id, jenis, data)\n",
                "        async def pendengar(jenis: str, data: Mapping[str, Any]) -> None:\n            return None\n",
            )
        ],
        _pytest(
            f"{UJI_PERCAKAPAN}::test_token_mengalir_lalu_done_membawa_biaya_keyakinan_dan_alasan"
        ),
        harus_memuat="tool_call tidak mengalir",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "balasan tersimpan tanpa alasannya (E-194)",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                "                rationale=alasan,",
                "                rationale=(),",
            )
        ],
        _pytest(
            f"{UJI_PERCAKAPAN}::test_token_mengalir_lalu_done_membawa_biaya_keyakinan_dan_alasan"
        ),
        harus_memuat="done tanpa alasan",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "klien yang tersambung sesudah POST kehilangan awal aliran",
        [
            Sunting(
                f"{MODUL}/agents/aliran.py",
                "        i = 0\n        while True:",
                "        i = len(g.peristiwa)\n        while True:",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_klien_yang_tersambung_belakangan_menerima_seluruh_aliran"),
        harus_memuat="klien yang terlambat kehilangan awal aliran",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "“catat mood” lewat percakapan dijalankan agent",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                '            if niat.rute == "deterministic":',
                "            if False:",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_catat_mood_lewat_percakapan_tanpa_model_sama_sekali"),
        harus_memuat="“catat mood” dijalankan agent",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "dua giliran serentak dalam satu percakapan",
        [
            Sunting(
                f"{MODUL}/agents/aliran.py",
                "        if self.sibuk(percakapan_id):\n            raise GiliranBerjalan(",
                "        if False:\n            raise GiliranBerjalan(",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_satu_giliran_per_percakapan"),
        harus_memuat="dua giliran serentak dalam satu percakapan",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "giliran yang ditahan tidak mengalirkan pertanyaannya",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                '                await self.aliran.kirim(\n                    percakapan_id, "confirmation_required", _permintaan(galat.konfirmasi)\n                )\n',
                "                pass\n",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_konfirmasi_lewat_percakapan_lalu_giliran_diulang"),
        harus_memuat="confirmation_required tidak mengalir",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "token konfirmasi percakapan lain diterima",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                "                if akar is None or akar[1] != percakapan_id",
                "                if akar is None",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_token_konfirmasi_percakapan_lain_ditolak"),
        harus_memuat="token konfirmasi percakapan lain diterima",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "penolakan tetap menjalankan giliran",
        [
            Sunting(
                f"{MODUL}/agents/percakapan.py",
                "            if setuju is None:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_konfirmasi_ditolak_tidak_menjalankan_apa_pun"),
        harus_memuat="penolakan tetap menjalankan giliran",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "aliran percakapan orang lain terjangkau",
        [
            Sunting(
                f"{MODUL}/agents/routes.py",
                '    if await layanan.baca(pengguna.user_id, percakapan_id) is None:\n        raise platform.GalatApi(404, "not_found", "Percakapan tidak ditemukan.")\n',
                "",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_percakapan_orang_lain_tidak_terjangkau"),
        harus_memuat="percakapan orang lain terjangkau",
        kelompok="db",
    ),
    Mutasi(
        "4.8",
        "aliran tanpa giliran bukan 204 — klien menyambung ulang tanpa akhir",
        [
            Sunting(
                f"{MODUL}/agents/routes.py",
                "    if not layanan.aliran.ada(percakapan_id):\n        return Response(status_code=204)\n",
                "",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_aliran_tanpa_giliran_204"),
        harus_memuat="204 berarti jangan menyambung ulang",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.9 anggaran harian: melewati batas → turun ke model kecil, bukan gagal ──
    Mutasi(
        "4.9",
        "anggaran tidak diperiksa sebelum memanggil model",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "        pilihan = self._runtime.gerbang_model.pilih_kelas(diminta, anggaran_habis=habis)",
                "        pilihan = self._runtime.gerbang_model.pilih_kelas(diminta, anggaran_habis=False)",
            )
        ],
        _pytest(f"{UJI_ANGGARAN}::test_anggaran_habis_turun_ke_model_kecil_bukan_gagal"),
        harus_memuat="anggaran habis tidak menurunkan kelas model",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "turun kelas tidak tercatat di jejak run",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '            keputusan_run["model_downgraded"] = True  # anggaran harian habis (4.9)',
                "            pass",
            )
        ],
        _pytest(f"{UJI_ANGGARAN}::test_anggaran_habis_turun_ke_model_kecil_bukan_gagal"),
        harus_memuat="turun kelas tidak tercatat di jejaknya",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "biaya sebelum hari ini ikut dihitung",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "            hour=0, minute=0, second=0, microsecond=0",
                "            year=2000, hour=0, minute=0, second=0, microsecond=0",
            )
        ],
        _pytest(f"{UJI_ANGGARAN}::test_biaya_kemarin_waktu_lokal_tidak_dihitung"),
        harus_memuat="biaya hari kemarin (waktu lokal) ikut dihitung",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "hari anggaran = hari UTC, bukan hari lokal pengguna",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                '        return self._jam().astimezone(ZoneInfo(zona or "UTC"))',
                '        return self._jam().astimezone(ZoneInfo("UTC"))',
            )
        ],
        _pytest(f"{UJI_ANGGARAN}::test_hari_anggaran_adalah_hari_lokal_bukan_hari_utc"),
        harus_memuat="anggaran dihitung per hari UTC, bukan hari pengguna",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "biaya run yang sedang berjalan tidak dihitung",
        [
            Sunting(
                f"{MODUL}/agents/runtime.py",
                "            berjalan += run.biaya_usd",
                "            berjalan += 0",
            )
        ],
        _pytest(f"{UJI_ANGGARAN}::test_panggilan_kedua_satu_run_melihat_biaya_yang_pertama"),
        harus_memuat="biaya run yang sedang berjalan tidak dihitung",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "anggaran harian tidak dirakit — api tanpa batas biaya",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "            anggaran_harian_usd=settings.ai_anggaran_harian_usd,\n",
                "",
            )
        ],
        _pytest(f"{UJI_PERCAKAPAN}::test_anggaran_harian_dirakit_dari_setelan"),
        harus_memuat="anggaran harian tidak dirakit",
        kelompok="db",
    ),
    Mutasi(
        "4.9",
        "anggaran harian negatif diterima",
        [
            Sunting(
                f"{MODUL}/platform/config.py",
                '    ai_anggaran_harian_usd: Decimal = Field(default=Decimal("0.50"), ge=0, le=1_000)',
                '    ai_anggaran_harian_usd: Decimal = Field(default=Decimal("0.50"), le=1_000)',
            )
        ],
        _pytest("tests/unit/test_config.py::test_anggaran_harian_negatif_ditolak"),
        harus_memuat="anggaran harian negatif diterima",
    ),
    # ── alat ini sendiri: bytecode mutan tidak tertinggal sesudah dipulihkan ──
    Mutasi(
        "alat",
        "mutasi menulis bytecode — .pyc mutan ukuran-sama dipakai sesudah dipulihkan",
        [
            Sunting(
                "tools/uji_mutasi_kode.py",
                # Dipotong dua: jangkar yang utuh di sini membuat jangkarnya tidak unik.
                '"utf-8", "PYTHONDONTWRITEBYTECODE"' + ': "1"}',
                '"utf-8"}',
            )
        ],
        _pytest(
            "tests/unit/test_alat_mutasi_bytecode.py::"
            "test_mutasi_ukuran_sama_tidak_meninggalkan_bytecode_basi"
        ),
        harus_memuat="bytecode mutan dipakai sesudah berkasnya dipulihkan",
    ),
    Mutasi(
        "alat",
        "pemulihan tidak membuang bytecode berkas yang dimutasi",
        [
            Sunting(
                "tools/uji_mutasi_kode.py",
                '            for pyc in (p.parent / "__pycache__").glob(f"{p.stem}.*.pyc"):' + NL,
                '            for pyc in (p.parent / "__pycache__").glob(f"{p.stem}.*.tidak-ada"):'
                + NL,
            )
        ],
        _pytest(
            "tests/unit/test_alat_mutasi_bytecode.py::"
            "test_pemulihan_membuang_bytecode_berkas_yang_dimutasi"
        ),
        harus_memuat="bytecode berkas yang dimutasi tertinggal",
    ),
    # ── Sprint 4 · 4.1 AI Gateway + Model Router — "catat mood" tanpa model ──
    Mutasi(
        "4.1",
        "catat mood dirutekan ke model — INSERT lewat inferensi",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                '            return Niat("deterministic", "catat_mood", mood)',
                '            return Niat("simple", "catat_mood", mood)',
            )
        ],
        _pytest(f"{UJI_NIAT}::test_perintah_mood_dirutekan_deterministik_tanpa_model"),
        harus_memuat="dirutekan ke model simple",
    ),
    Mutasi(
        "4.1",
        "perintah di tengah kalimat dijalankan — teks yang tidak dimaksudkan bertindak",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                '    r"^\\s*(?:(?:catat|log|simpan|isi)\\s+)?mood',
                '    r"\\s*(?:(?:catat|log|simpan|isi)\\s+)?mood',
            ),
            Sunting(
                f"{MODUL}/agents/niat.py",
                "    awalan = _AWALAN_MOOD.match(teks)",
                "    awalan = _AWALAN_MOOD.search(teks)",
            ),
        ],
        _pytest(f"{UJI_NIAT}::test_yang_bukan_perintah_tidak_dijalankan"),
        harus_memuat="dijalankan sebagai perintah",
    ),
    Mutasi(
        "4.1",
        "valensi yang tidak utuh ditebak — “catat mood 34” menjadi 3",
        [
            Sunting(
                f"{MODUL}/agents/niat.py",
                'rf"^(?P<v>[1-5])(?:\\s*/\\s*5)?(?=\\s|{_PEMISAH}|$)"',
                'rf"^(?P<v>[1-5])(?:\\s*/\\s*5)?"',
            )
        ],
        _pytest(f"{UJI_NIAT}::test_perintah_mood_tanpa_valensi_utuh_dijawab_bukan_ditebak"),
        harus_memuat="ditebak",
    ),
    Mutasi(
        "4.1",
        "Model Router tetap memakai model besar sesudah anggaran habis",
        [
            Sunting(
                f"{MODUL}/platform/model.py",
                '        return "simple" if anggaran_habis else kelas',
                "        return kelas",
            )
        ],
        _pytest(f"{UJI_GERBANG_MODEL}::test_model_router_turun_ke_model_kecil_saat_anggaran_habis"),
        harus_memuat="anggaran habis, tetap model besar",
    ),
    Mutasi(
        "4.1",
        "penyedia lokal mengarang jawaban tanpa bahan (Pasal 8)",
        [
            Sunting(
                f"{MODUL}/platform/model.py",
                "            teks = TANPA_DATA",
                '            teks = "Kamu baik-baik saja minggu ini."',
            )
        ],
        _pytest(f"{UJI_GERBANG_MODEL}::test_tanpa_bahan_tidak_mengarang"),
        harus_memuat="jawaban tanpa bahan",
    ),
    Mutasi(
        "4.1",
        "model berbayar tanpa harga diterima — biayanya tidak bisa dibatasi",
        [
            Sunting(
                f"{MODUL}/platform/model.py",
                "            if model not in self._harga and nama_penyedia != PenyediaLokal.nama:",
                "            if False:",
            )
        ],
        _pytest(f"{UJI_GERBANG_MODEL}::test_model_berbayar_tanpa_harga_ditolak_saat_dirakit"),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.1",
        "biaya tanpa token keluar — anggaran meremehkan jawaban panjang",
        [
            Sunting(
                f"{MODUL}/platform/model.py",
                "        mentah = (Decimal(token_masuk) * self.masuk + Decimal(token_keluar) * self.keluar) / (",
                "        mentah = (Decimal(token_masuk) * self.masuk) / (",
            )
        ],
        _pytest(f"{UJI_GERBANG_MODEL}::test_kelas_menentukan_model_dan_jejaknya_lengkap"),
        harus_memuat="tarif × token masuk & keluar",
    ),
    Mutasi(
        "4.1",
        "harga model negatif diterima",
        [
            Sunting(
                f"{MODUL}/platform/config.py",
                "            if masuk < 0 or keluar < 0 or not (masuk.is_finite() and keluar.is_finite()):",
                "            if not (masuk.is_finite() and keluar.is_finite()):",
            )
        ],
        _pytest(
            "tests/unit/test_config.py::test_harga_model_dibaca_dari_json_dan_yang_salah_ditolak"
        ),
        harus_memuat="DID NOT RAISE",
    ),
    Mutasi(
        "4.1",
        "pesan yang dikirim ulang mencatat mood kedua",
        [
            Sunting(
                f"{MODUL}/agents/deterministik.py",
                "            id=mood_id, valence=niat.mood.valensi,",
                "            id=None, valence=niat.mood.valensi,",
            )
        ],
        _pytest(f"{UJI_RUTE}::test_pesan_yang_dikirim_ulang_tidak_mencatat_mood_dua_kali"),
        harus_memuat="kiriman ulang mencatat mood dua kali",
        kelompok="db",
    ),
    # ── Sprint 4 · 4.2 registry agent: 9 aturan spec/05 + A-1 + K-14, katalog dikelola migrasi ──
    Mutasi(
        "4.2",
        "aturan 1 — tool di luar registry diterima",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '            salah.append(Pelanggaran(m.name, "1", f"tool {t} tidak ada di tool registry"))',
                "            pass",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 1 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 2 — scope manifest di luar daftar resmi diterima",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "    asing = sorted(scope - identity.SCOPE_RESMI.keys())  # aturan 2",
                "    asing: list[str] = []  # aturan 2",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 2 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 3 — tool lebih berisiko dari pagu max_risk diterima",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "        if alat[t].risk_level > m.pagu_risiko:",
                "        if False:",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 3 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 4 — gerbang keselamatan tidak diperiksa",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "    if keselamatan is None or keselamatan < AMBANG_KESELAMATAN:",
                "    if False:",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 4 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 5 — dua versi aktif untuk satu nama",
        [
            Sunting(
                f"{MODUL}/agents/registri.py", "        if m.name in aktif:", "        if False:"
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 5 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 6 — pihak ketiga boleh meminta journal_raw",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '            ("6", SCOPE_TERLARANG_PIHAK_KETIGA_6),\n',
                "",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 6 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 7 — tool yang menyentuh orang lain di bawah R3",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "    if alat.reaches_third_party and alat.risk_level < 3:",
                "    if False:",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 7 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 8 — tool tanpa risk_level tidak ditolak sebagai aturan 8",
        [
            Sunting(
                f"{MODUL}/agents/registri.py", '    if "risk_level" not in mentah:', "    if False:"
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 8 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "aturan 9 — pihak ketiga boleh meminta lokasi",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '            ("9", SCOPE_TERLARANG_PIHAK_KETIGA_9),\n',
                "",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan 9 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "A-1 — risk_level sebagai properti agent diterima",
        [
            Sunting(
                f"{MODUL}/agents/registri.py", "        if terlarang in mentah", "        if False"
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan A-1 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "K-14 — entri agent lebih murah dari agent yang dipanggil",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "        elif a.risk_level != dipanggil.pagu_risiko:",
                "        elif False:",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan K-14 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "K-14 — entri agent tanpa agent aktif",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                '            salah.append(Pelanggaran(a.name, "K-14", "tidak menunjuk agent aktif mana pun"))',
                "            continue",
            )
        ],
        _pytest(UJI_REGISTRI),
        harus_memuat="aturan K-14 tidak ditegakkan",
    ),
    Mutasi(
        "4.2",
        "katalog: isi manifest jsonb tidak dibandingkan — manifest yang disunting berjalan diam-diam",
        [
            Sunting(
                f"{MODUL}/agents/registri.py",
                "        if harapan != ada or json.loads(manifest_json(registri.mentah[nama])) != b.manifest:",
                "        if harapan != ada:",
            )
        ],
        _pytest(f"{UJI_KATALOG}::test_api_menolak_mulai_bila_katalog_berbeda_dari_manifest"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    Mutasi(
        "4.2",
        "api mulai tanpa membandingkan katalog dengan manifest",
        [
            Sunting(
                "apps/api/src/hvx/main.py",
                "            await agents.pastikan_katalog(engine, registri)" + NL,
                "",
            )
        ],
        _pytest(f"{UJI_KATALOG}::test_api_menolak_mulai_bila_katalog_berbeda_dari_manifest"),
        harus_memuat="DID NOT RAISE",
        kelompok="db",
    ),
    # ── alat ini sendiri: mutasi yang menggantung dihentikan beserta turunannya ──
    Mutasi(
        "alat",
        "mutasi yang menggantung: hanya proses langsungnya yang dihentikan",
        [
            Sunting(
                "tools/uji_mutasi_kode.py",
                '        if os.name == "nt":'
                + NL
                + "            subprocess.run("
                + NL
                + '                ["taskkill", "/F", "/T", "/PID", str(proses.pid)], capture_output=True, check=False'
                + NL
                + "            )"
                + NL
                + "        else:"
                + NL
                + "            os.killpg(proses.pid, signal.SIGKILL)"
                + NL,
                "        proses.kill()" + NL,
            )
        ],
        _pytest(
            "tests/unit/test_alat_mutasi_terbatas_waktu.py::"
            "test_proses_turunan_yang_menggantung_ikut_dihentikan"
        ),
        harus_memuat="pohon prosesnya tidak dihentikan",
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
        if p.suffix == ".py":
            # Bytecode yang dikompilasi dari MUTAN — lapis kedua sesudah
            # PYTHONDONTWRITEBYTECODE: perintah yang tidak mewarisi lingkungannya
            # (subproses yang menyetel ulang env) tetap tidak meninggalkan .pyc basi.
            for pyc in (p.parent / "__pycache__").glob(f"{p.stem}.*.pyc"):
                pyc.unlink(missing_ok=True)
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

    kosong = [v for v in ("HVX_TEST_DATABASE_URL", "HVX_TEST_QDRANT_URL") if not os.environ.get(v)]
    if "db" in jalan and kosong:
        print(f"🛑 {' · '.join(kosong)} tidak diisi — mutasi kelompok db tidak bisa dibuktikan.")
        print(
            "   Isi variabelnya, atau jalankan dengan --tanpa-db untuk MENYATAKAN bagian itu dilewati."
        )
        return 1

    lemah: list[str] = []
    dilewati: dict[str, int] = {}
    lingkungan = lingkungan_mutasi()
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
            kode, keluaran = jalankan_terbatas(
                m.perintah,
                AKAR / m.cwd if m.cwd else AKAR,
                {**lingkungan, "TZ": _tz_flutter()} if m.cwd == APLIKASI else lingkungan,
            )
        finally:
            _pulihkan(cadangan, dir_baru)
        tertangkap = kode in m.kode_tertangkap and alasan_terbaca(m, keluaran)
        print(
            f"  {'✅' if tertangkap else '🛑'} {label} → "
            f"{'BERBUNYI' if tertangkap else f'DIAM/SALAH ALASAN (keluar {kode})'}"
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
