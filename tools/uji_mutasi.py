#!/usr/bin/env python3
"""Uji mutasi untuk `periksa_dokumen.py` — membuktikan MERAHnya bisa terjadi.

Kenapa berkas ini ada, dan kenapa ia bukan kemewahan:

    “Dua belas LULUS” tidak berarti apa pun sampai bisa ditunjukkan bahwa
    kedua belasnya SANGGUP GAGAL. Pemeriksaan yang salah tulis — regex yang
    tidak pernah cocok, tabel yang tidak pernah terbaca — memulangkan LULUS
    dengan tenang, dan itu persis bentuk kegagalan yang seluruh `arch/11`
    dibangun untuk menutupnya.

Cara kerjanya: rusak **satu** hal yang sebuah pemeriksaan KLAIM deteksi,
jalankan pemeriksaan itu saja, pastikan ia keluar dengan kode 1, lalu
kembalikan berkasnya. Selalu dikembalikan, termasuk kalau prosesnya gagal
di tengah (`try/finally`).

    python tools/uji_mutasi.py        # keluar 1 kalau ada yang DIAM

🔴 **Pelajaran dari putaran pertama, dan ia layak disimpan:** mutasi pertama
untuk G-1 mengubah NAMA pasal (`Reversibility` → `Reversibility X`) dan
G-1 diam — yang terbaca seperti pemeriksaan buta. Ia tidak buta; G-1 memang
tidak memeriksa nama pasal, ia memeriksa **adanya penegak**. Yang cacat
mutasinya. ⇒ **sebuah uji yang tidak menguji apa yang dikiranya diuji akan
menuduh yang benar.** Mutasi harus menyasar KLAIM pemeriksaannya, bukan
teks di dekatnya.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AKAR = pathlib.Path(__file__).resolve().parent.parent
MIGRASI_0001 = "data/migrations/versions/0001_v0_skema.up.sql"

# (kode, berkas, yang dicari, penggantinya, apa yang dirusak)
MUTASI: list[tuple[str, str, str, str, str]] = [
    (
        "B-6", "arch/03-MONOREPO-FINAL.md",
        "├── governance/          constitution/",
        "├── privacy/             constitution/",
        "pohon keluarga keamanan jadi dua",
    ),
    (
        "P-1", "spec/01-DATABASE-SCHEMA.md",
        "-- @retention   : until-account-deleted\n"
        "-- @who-can-set : user\n"
        "-- @on-delete   : hard\n"
        "CREATE TABLE habits (",
        "CREATE TABLE habits (",
        "tabel tanpa anotasi retensi",
    ),
    (
        "P-2", "spec/01-DATABASE-SCHEMA.md",
        "  data_subject text NOT NULL DEFAULT 'user'\n"
        "                 CHECK (data_subject IN "
        "('user','bystander','world','system')),\n"
        "  goal_id          uuid REFERENCES goals(id) ON DELETE SET NULL,",
        "  goal_id          uuid REFERENCES goals(id) ON DELETE SET NULL,",
        "tabel tanpa kolom data_subject",
    ),
    (
        "P-3", "spec/01-DATABASE-SCHEMA.md",
        "  CHECK ((data_subject = 'user') = (user_id IS NOT NULL))",
        "  -- dihapus oleh uji mutasi",
        "user_id nullable tanpa penjaga",
    ),
    (
        "E-1", "arch/07-EVENT-CONTRACTS.md",
        "· `purchase` · `health`⁽¹⁾ |",
        "· `purchase` |",
        "domain dipakai tetapi dicabut dari registry",
    ),
    (
        "E-2", "spec/03-EVENT-CONTRACTS.md",
        "| `MissionFailed` | **`mission.failed`** | `235` |",
        "| `MissionFailed` | **`mission.failure`** | `235` |",
        "verb bukan kata kerja lampau",
    ),
    (
        "E-4", "spec/03-EVENT-CONTRACTS.md",
        "| `emergency.recovery_completed` | melengkapi "
        "`emergency.recovery_started` | 16 |",
        "",
        "kembaran pemulihan hilang",
    ),
    (
        "E-5", "spec/03-EVENT-CONTRACTS.md",
        "| `MeetingCreated` | **`meeting.created`** 🆕 | `167` |",
        "",
        "nama event naskah tanpa baris padanan",
    ),
    (
        "A-2", "spec/05-AGENT-CONTRACTS.md",
        "| `agent.habit` | **agent** | 2 | Orchestrator |",
        "| `agent.habit` | **agent** | 4 | Orchestrator |",
        "tool risk_level melebihi max_risk",
    ),
    (
        "A-3", "spec/05-AGENT-CONTRACTS.md",
        "| `agent.memory` | **agent** | 2 | Orchestrator |",
        "| `agent.memory` | **write** | 2 | Orchestrator |",
        "entri agent terdaftar bukan `kind: agent`",
    ),
    (
        "G-1", "arch/08-AGENT-CONTRACTS.md",
        "| **5** Reversibility | R4 = `DENY` (*irreversible*) + `Rollback` "
        "di enam kata kerja override | ✅ |",
        "| **5** Reversibility |  | ✅ |",
        "pasal Konstitusi tanpa penegak",
    ),
    (
        # 🔴 Versi pertama mengubah `C20.7 -> C20.6` menjadi `C20.1 -> C20.6` —
        # itu MENGHAPUS satu temuan (pasangan jadi benar), dan R-1 tetap keluar
        # 1 karena enam temuan lain. Dihitung BERBUNYI padahal tidak menguji
        # apa pun. Sekarang mutasinya MEMBALIK pasangan yang hari ini lulus,
        # dan yang dihitung adalah temuan BARU, bukan kode keluar.
        "R-1", "arch/10-URUTAN-IMPLEMENTASI.md",
        "4.5 -> 4.6 4.7",
        "4.8 -> 4.6 4.7",
        "gerbang dijadwalkan sesudah yang dijaganya",
    ),
    # ── Sejak Sprint 0: DDL yang sampai ke basis data, dan pohon yang nyata ──
    (
        "P-1", MIGRASI_0001,
        "-- @retention   : until-account-deleted\n"
        "-- @who-can-set : user\n"
        "-- @on-delete   : hard\n"
        "CREATE TABLE habits (",
        "CREATE TABLE habits (",
        "tabel di MIGRASI tanpa anotasi retensi",
    ),
    (
        "P-2", MIGRASI_0001,
        "  data_subject text NOT NULL DEFAULT 'user'\n"
        "                 CHECK (data_subject IN "
        "('user','bystander','world','system')),\n"
        "  goal_id          uuid REFERENCES goals(id) ON DELETE SET NULL,",
        "  goal_id          uuid REFERENCES goals(id) ON DELETE SET NULL,",
        "tabel di MIGRASI tanpa kolom data_subject",
    ),
    (
        "P-3", MIGRASI_0001,
        "  CHECK ((data_subject = 'user') = (user_id IS NOT NULL))",
        "  -- CHECK ((data_subject = 'user') = (user_id IS NOT NULL))",
        "penjaga user_id tinggal KOMENTAR (migrasi)",
    ),
    (
        "E-3", "spec/01-DATABASE-SCHEMA.md",
        "CHECK (source IN ('app','agent','integration','backfill')),",
        "CHECK (source IN ('app','agent','integration','backfill','sensor')),",
        "events menerima source='sensor' (spec/01)",
    ),
    (
        "E-3", MIGRASI_0001,
        "CHECK (source IN ('app','agent','integration','backfill')),",
        "CHECK (source IN ('app','agent','integration','backfill','sensor')),",
        "events menerima source='sensor' (migrasi)",
    ),
    (
        "A-1", "spec/05-AGENT-CONTRACTS.md",
        "  max_level: L2   ",
        "  max_level: R2   ",
        "angka tangga R dipakai untuk otonomi L",
    ),
    (
        "A-1", MIGRASI_0001,
        "  max_risk              smallint",
        "  risk_level            smallint",
        "kolom satu-angka agents.risk_level (migrasi)",
    ),
    # ── Ejaan DDL yang parser pertama tidak lihat ──
    (
        "P-1", MIGRASI_0001,
        "-- dipakai semua tabel yang punya updated_at\n",
        "CREATE TABLE IF NOT EXISTS public.catatan_liar (\n"
        "  id uuid PRIMARY KEY\n"
        ") WITH (fillfactor = 90);\n\n"
        "-- dipakai semua tabel yang punya updated_at\n",
        "tabel IF NOT EXISTS + skema + WITH, tanpa anotasi",
    ),
    (
        "P-2", MIGRASI_0001,
        "  deleted_at       timestamptz\n"
        ");\n"
        "CREATE INDEX habits_user_status_idx ON habits (user_id, status) WHERE deleted_at IS NULL;\n"
        "\n"
        "-- @retention   : until-account-deleted\n"
        "-- @who-can-set : user\n"
        "-- @on-delete   : hard\n"
        "CREATE TABLE habit_completions (\n"
        "  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),\n"
        "  data_subject text NOT NULL DEFAULT 'user'\n"
        "                 CHECK (data_subject IN ('user','bystander','world','system')),\n",
        "  deleted_at       timestamptz\n"
        ") WITH (fillfactor = 90);\n"
        "CREATE INDEX habits_user_status_idx ON habits (user_id, status) WHERE deleted_at IS NULL;\n"
        "\n"
        "-- @retention   : until-account-deleted\n"
        "-- @who-can-set : user\n"
        "-- @on-delete   : hard\n"
        "CREATE TABLE habit_completions (\n"
        "  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),\n",
        "akhiran WITH menelan tabel berikut tanpa data_subject",
    ),
    (
        "E-3", MIGRASI_0001,
        "  source          text NOT NULL DEFAULT 'app'\n"
        "                    CHECK (source IN ('app','agent','integration','backfill')),",
        "  source          text NOT NULL DEFAULT 'app' -- lama: CHECK (source IN ('app','agent'))\n"
        "                    CHECK (source IN ('app','agent','integration','backfill','sensor')),",
        "CHECK lama di KOMENTAR menutupi CHECK yang asli",
    ),
]

# (kode, direktori yang dibuat sementara, apa yang dirusak)
MUTASI_DIREKTORI: list[tuple[str, str, str]] = [
    ("B-6", "apps/api/src/hvx/modules/audit", "pohon keamanan KEDUA di antara modul V0"),
    ("B-6", "services/audit", "pohon keamanan KEDUA di wadah services/"),
    ("M-4", "apps/api/src/hvx/modules/habits/registry", "`registry/` di luar agents & tools"),
]

_TEMUAN_AWAL: dict[str, set[str]] = {}


def _temuan(kode: str) -> tuple[int, set[str]]:
    r = subprocess.run(
        [sys.executable, str(AKAR / "tools" / "periksa_dokumen.py"), kode],
        capture_output=True, text=True, encoding="utf-8", cwd=AKAR,
    )
    return r.returncode, {b.strip() for b in r.stdout.splitlines() if b.startswith("  🛑 ")}


def _periksa(kode: str) -> tuple[int, set[str]]:
    """Kode keluar + temuan yang BARU dibanding repo tanpa mutasi.

    🔴 Kode keluar 1 saja tidak membuktikan apa pun untuk pemeriksaan yang
    sudah merah sebelum dirusak (R-1: tujuh temuan keputusan cakupan). Yang
    dituntut: mutasi melahirkan temuan yang tadinya tidak ada.
    """
    if kode not in _TEMUAN_AWAL:
        raise RuntimeError(f"temuan awal {kode} belum direkam")
    kembali, temuan = _temuan(kode)
    return kembali, temuan - _TEMUAN_AWAL[kode]


def _lapor(kode: str, maksud: str, hasil: tuple[int, set[str]], lemah: list[str]) -> None:
    kembali, baru = hasil
    berbunyi = kembali == 1 and bool(baru)
    print(f"  {'✅' if berbunyi else '🛑'} {kode:4s} {maksud:48s} → "
          f"{'BERBUNYI' if berbunyi else 'DIAM'}"
          + (f"  ({sorted(baru)[0]})" if berbunyi else ""))
    if not berbunyi:
        lemah.append(kode)


def main() -> int:
    lemah: list[str] = []
    lewat: list[str] = []
    # Temuan repo TANPA mutasi, sekali per kode, sebelum apa pun dirusak.
    for kode in sorted({m[0] for m in MUTASI} | {m[0] for m in MUTASI_DIREKTORI}):
        _TEMUAN_AWAL[kode] = _temuan(kode)[1]
    for kode, berkas, lama, baru, maksud in MUTASI:
        p = AKAR / berkas
        # Dibaca & dikembalikan sebagai BYTE: `read_text`/`write_text` di
        # Windows menerjemahkan akhir baris, dan versi pertama berkas ini
        # diam-diam mengubah berkas ber-LF menjadi CRLF saat mengembalikannya.
        asli = p.read_bytes()
        teks = asli.decode("utf-8")
        crlf = "\r\n" in teks
        teks = teks.replace("\r\n", "\n")
        if teks.count(lama) != 1:
            print(f"  ⚠️  {kode:4s} pola mutasi tidak unik "
                  f"({teks.count(lama)}) — dilewati")
            lewat.append(kode)
            continue
        rusak = teks.replace(lama, baru)
        try:
            p.write_bytes((rusak.replace("\n", "\r\n") if crlf else rusak).encode("utf-8"))
            kembali = _periksa(kode)
        finally:
            p.write_bytes(asli)
        _lapor(kode, maksud, kembali, lemah)

    for kode, rel, maksud in MUTASI_DIREKTORI:
        d = AKAR / rel
        if d.exists():
            print(f"  ⚠️  {kode:4s} {rel} sudah ada — mutasi direktori dilewati")
            lewat.append(kode)
            continue
        try:
            d.mkdir()
            kembali = _periksa(kode)
        finally:
            shutil.rmtree(d, ignore_errors=True)
        _lapor(kode, maksud, kembali, lemah)

    total = len(MUTASI) + len(MUTASI_DIREKTORI)
    print()
    print(f"mutasi dijalankan : {total - len(lewat)} dari {total}")
    print(f"terbukti berbunyi : {total - len(lewat) - len(lemah)}")
    if lewat:
        print(f"🛑 pola mutasinya basi (berkasnya berubah): {' '.join(lewat)}")
    if lemah:
        print(f"🛑 DIAM saat dirusak: {' '.join(lemah)}")
    return 1 if (lemah or lewat) else 0


if __name__ == "__main__":
    sys.exit(main())
