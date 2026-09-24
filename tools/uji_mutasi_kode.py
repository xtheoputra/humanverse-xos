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
                "redis.call('SET', KEYS[1], tat_baru, 'PX', tat_baru - sekarang)" + NL,
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
                "    if saat.utcoffset() is None:" + NL + "        raise _kursor_rusak()" + NL,
                "",
            )
        ],
        _pytest("tests/unit/test_halaman.py::test_kursor_rusak_menjadi_galat_400"),
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
                '        return f"{self._awalan}:idem:{user_id}:{sidik}"',
                '        return f"{self._awalan}:idem:{sidik}"',
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
                '        if tersimpan.get("sidik") != self._sidik:'
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
        "penanda 'sedang berjalan' tanpa NX — permintaan serentak semuanya menulis",
        [
            Sunting(
                f"{MODUL}/platform/idempotensi.py",
                "        if not await self._r.set(k, penanda, nx=True, ex=_UMUR_PROSES_S):",
                "        if not await self._r.set(k, penanda, ex=_UMUR_PROSES_S):",
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
                + '            await self._r.set(k, json.dumps({"sidik": self._sidik, "status": g.status, "badan": {}}))'
                + NL
                + "            raise"
                + NL,
            )
        ],
        _pytest(f"{UJI_IDEM}::test_galat_tidak_disimpan_sebagai_jawaban"),
        harus_memuat="galat disimpan sebagai jawaban",
        kelompok="db",
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
