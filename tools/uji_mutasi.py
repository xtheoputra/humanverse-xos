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
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AKAR = pathlib.Path(__file__).resolve().parent.parent

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
        "R-1", "arch/10-URUTAN-IMPLEMENTASI.md",
        "C20.7  -> C20.6",
        "C20.1  -> C20.6",
        "pasangan gerbang yang urutannya dibalik",
    ),
]


def main() -> int:
    lemah: list[str] = []
    lewat: list[str] = []
    for kode, berkas, lama, baru, maksud in MUTASI:
        p = AKAR / berkas
        asli = p.read_text(encoding="utf-8")
        if asli.count(lama) != 1:
            print(f"  ⚠️  {kode:4s} pola mutasi tidak unik "
                  f"({asli.count(lama)}) — dilewati")
            lewat.append(kode)
            continue
        try:
            p.write_text(asli.replace(lama, baru), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(AKAR / "tools" / "periksa_dokumen.py"), kode],
                capture_output=True, text=True, encoding="utf-8", cwd=AKAR,
            )
        finally:
            p.write_text(asli, encoding="utf-8")
        berbunyi = r.returncode == 1
        print(f"  {'✅' if berbunyi else '🛑'} {kode:4s} {maksud:44s} → "
              f"{'BERBUNYI' if berbunyi else 'DIAM'}")
        if not berbunyi:
            lemah.append(kode)

    print()
    print(f"mutasi dijalankan : {len(MUTASI) - len(lewat)} dari {len(MUTASI)}")
    print(f"terbukti berbunyi : {len(MUTASI) - len(lewat) - len(lemah)}")
    if lewat:
        print(f"🛑 pola mutasinya basi (berkasnya berubah): {' '.join(lewat)}")
    if lemah:
        print(f"🛑 DIAM saat dirusak: {' '.join(lemah)}")
    return 1 if (lemah or lewat) else 0


if __name__ == "__main__":
    sys.exit(main())
