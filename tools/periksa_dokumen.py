#!/usr/bin/env python3
"""Pemeriksa dokumen HumanVerse XOS — E-1, E-2, G-1, R-1.

Empat dari dua puluh lima pemeriksaan `arch/11` yang bisa dijalankan
TANPA satu baris kode produksi, sebab keempatnya membaca DOKUMEN.

    E-1  segmen pertama `event_type` wajib ada di registry domain (arch/07 §2)
    E-2  `event_type` wajib dua segmen, huruf kecil, kata kerja lampau
    E-5  tiap nama event di naskah punya baris di tabel padanan spec/03
    G-1  tiap pasal Konstitusi §20.16 wajib punya >= 1 penegak (arch/08 §4)
    R-1  tiap pasangan (gerbang G, yang dijaga T): index(G) < index(T)

Aturan rancangan yang dipegang berkas ini:

1.  **Registry dibaca dari dokumennya, tidak ditulis ulang di sini.**
    Kalau `arch/07` §2 menambah domain, pemeriksa ikut tanpa disunting.
    Kalau daftarnya hilang, pemeriksa GAGAL — bukan lulus diam-diam.

2.  **Populasi yang diperiksa dinyatakan, bukan ditebak.** `--senarai`
    mencetak tiap nama yang dipanen beserta asalnya, supaya positif palsu
    bisa dilihat, bukan diperdebatkan.

3.  **Yang tidak bisa diperiksa mesin dikatakan**, tidak disembunyikan di
    balik "LULUS".

Pemakaian:
    python tools/periksa_dokumen.py                 # semua, ringkas
    python tools/periksa_dokumen.py --senarai       # + daftar lengkap
    python tools/periksa_dokumen.py E-1 E-2         # sebagian
    python tools/periksa_dokumen.py --json          # untuk CI

Keluar dengan kode 1 kalau ada pemeriksaan yang GAGAL.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

# Konsol Windows bawaan cp1252; laporan ini memakai ✅/🛑.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AKAR = Path(__file__).resolve().parent.parent

ARCH07 = AKAR / "arch" / "07-EVENT-CONTRACTS.md"
ARCH08 = AKAR / "arch" / "08-AGENT-CONTRACTS.md"
ARCH10 = AKAR / "arch" / "10-URUTAN-IMPLEMENTASI.md"
SPEC03 = AKAR / "spec" / "03-EVENT-CONTRACTS.md"
SPEC07 = AKAR / "spec" / "07-BACKLOG-V0.md"
DOCS = AKAR / "docs"


# ───────────────────────────────────────────────────────── hasil ──


@dataclass
class Temuan:
    """Satu pelanggaran. `sumber` selalu diisi supaya bisa dibuka."""

    subjek: str
    alasan: str
    sumber: str = ""


@dataclass
class Hasil:
    kode: str
    judul: str
    lulus: bool = True
    diperiksa: int = 0
    temuan: list[Temuan] = field(default_factory=list)
    catatan: list[str] = field(default_factory=list)
    senarai: list[str] = field(default_factory=list)

    def gagal(self, subjek: str, alasan: str, sumber: str = "") -> None:
        self.lulus = False
        self.temuan.append(Temuan(subjek, alasan, sumber))


# ─────────────────────────────────────────────── alat baca berkas ──


def baca(p: Path) -> str:
    if not p.exists():
        raise SystemExit(f"🛑 berkas wajib tidak ada: {p.relative_to(AKAR)}")
    return p.read_text(encoding="utf-8")


def bagian(teks: str, judul_awal: str, judul_berikut: str = r"^## ") -> str:
    """Potong satu bagian `## …` dari sebuah berkas markdown."""
    baris = teks.splitlines()
    mulai = None
    for i, b in enumerate(baris):
        if re.match(judul_awal, b):
            mulai = i
            break
    if mulai is None:
        return ""
    for j in range(mulai + 1, len(baris)):
        if re.match(judul_berikut, baris[j]):
            return "\n".join(baris[mulai:j])
    return "\n".join(baris[mulai:])


# ───────────────────────────────────────── registry domain (E-1) ──


def muat_registry_domain() -> tuple[dict[str, str], str]:
    """arch/07 §2 — tabel `| konteks | domain · domain · … |`.

    Memulangkan {domain: konteks pemilik} dan teks bagiannya.
    """
    teks = baca(ARCH07)
    sek = bagian(teks, r"^## §2 ")
    if not sek:
        raise SystemExit("🛑 arch/07 §2 (registry domain) tidak ditemukan")

    registry: dict[str, str] = OrderedDict()
    for baris in sek.splitlines():
        m = re.match(r"^\|\s*`([a-z][a-z0-9-]*)`\s*\|(.+?)\|\s*$", baris)
        if not m:
            continue
        konteks, isi = m.group(1), m.group(2)
        for d in re.findall(r"`([a-z][a-z0-9_]*)`", isi):
            if d in registry:
                raise SystemExit(
                    f"🛑 domain `{d}` dimiliki dua konteks: "
                    f"{registry[d]} dan {konteks} — arch/07 §2 aturan "
                    f"'tiap domain dimiliki tepat satu konteks' dilanggar"
                )
            registry[d] = konteks
    if not registry:
        raise SystemExit("🛑 arch/07 §2 ada tapi nol domain terbaca")
    return registry, sek


def jumlah_yang_diklaim(sek: str) -> int | None:
    m = re.search(r"\*\*(\d+)\s+domain", sek)
    return int(m.group(1)) if m else None


# ─────────────────────────────────── panen nama event (E-1, E-2) ──

# Token berbentuk `a.b` huruf kecil di dalam backtick. Bentuk ini
# sengaja sempit: PascalCase, jalur berkas (punya `/`), dan nomor versi
# (punya angka di kedua sisi titik) tidak pernah cocok.
POLA_EVENT = re.compile(r"`([a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_.]*)+)`")

# Bentuk `a.b` huruf kecil yang BUKAN nama event. Tiap baris disertai
# alasan, supaya daftar ini tidak menjadi tempat menyembunyikan temuan.
BUKAN_EVENT = {
    "agents.max_risk": "kolom manifest",
    "agents.risk_level": "kolom manifest",
    "consent.purpose": "kolom tabel",
    "consents.purpose": "kolom tabel",
    "data.purpose": "kolom tabel",
    "autonomy.max_level": "medan manifest",
    "evaluation.gates.safety": "kunci konfigurasi",
    "docker-compose.yml": "nama berkas",
    "__init__.py": "nama berkas",
    "domain.verb": "cetakan format, bukan nama",
    "stuff.happened": "contoh tandingan arch/07 §2 (justru harus ditolak)",
    "fashion.outfit.selected": "contoh tiga segmen yang arch/07 §2 nyatakan TIDAK dipakai",
    "workout.completed.v2": "contoh penamaan versi di spec/03 aturan 3",
}

# Bentuk `a.b` huruf kecil TANPA backtick — dipakai di blok kode.
# Tepi kiri/kanan menolak jalur berkas (`a/b.c`) dan nama bertitik ganda.
POLA_TELANJANG = re.compile(
    r"(?<![`\w/.-])([a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)(?![`\w/.-])"
)

# Segmen kedua yang sengaja glob (`security.*`) tidak diperiksa E-2.
POLA_GLOB = re.compile(r"\.\*$")

SUMBER_EVENT = [
    (SPEC03, "spec/03"),
    (ARCH07, "arch/07"),
]

# Kata kerja lampau tak beraturan yang dipakai / mungkin dipakai.
LAMPAU_TAK_BERATURAN = {
    "worn", "lost", "built", "sent", "written", "read", "made", "found",
    "left", "begun", "done", "gone", "given", "taken", "shown", "known",
    "drawn", "grown", "thrown", "won", "kept", "held", "met", "paid",
    "set", "put", "cut", "hit", "let", "split", "spent", "told", "sold",
    "bought", "brought", "caught", "taught", "thought", "felt", "fallen",
    "risen", "broken", "chosen", "frozen", "spoken", "stolen", "woken",
    "forgotten", "hidden", "ridden", "beaten", "eaten", "driven", "run",
    "sung", "sunk", "swum", "torn", "worn", "bound", "sworn",
}


def panen_event() -> list[tuple[str, str]]:
    """Memulangkan [(nama, sumber)] tanpa duplikat, urut.

    🔴 Panen backtick saja TIDAK cukup, dan itu diukur bukan ditebak:
    kedelapan nama `security.*` (K-10) hidup di dalam blok kode **tanpa
    backtick**, jadi versi pertama pemeriksa ini buta terhadap seluruh
    keluarga event keamanan — tepat keluarga yang paling mungkin diaudit.
    Karena itu token telanjang ikut dipanen.
    """
    hasil: dict[str, str] = OrderedDict()
    for path, label in SUMBER_EVENT:
        teks = baca(path)
        for i, baris in enumerate(teks.splitlines(), start=1):
            ketemu = POLA_EVENT.findall(baris) + POLA_TELANJANG.findall(baris)
            for nama in ketemu:
                if nama in BUKAN_EVENT:
                    continue
                if nama not in hasil:
                    hasil[nama] = f"{label}:{i}"
    return sorted(hasil.items())


def lampau(kata: str) -> bool:
    return kata.endswith("ed") or kata in LAMPAU_TAK_BERATURAN


# ───────────────────────────────────────────────────── E-1 · E-2 ──


def periksa_e1() -> Hasil:
    h = Hasil("E-1", "segmen pertama `event_type` ada di registry domain")
    registry, sek = muat_registry_domain()
    diklaim = jumlah_yang_diklaim(sek)

    h.catatan.append(f"registry arch/07 §2 memuat **{len(registry)} domain**")
    if diklaim is not None and diklaim != len(registry):
        h.gagal(
            f"arch/07 §2 (\"{diklaim} domain\")",
            f"tabelnya memuat {len(registry)} domain, bukan {diklaim} — "
            f"hitungan di prosa dan tabel di atasnya berbeda",
            "arch/07 §2",
        )

    for nama, sumber in panen_event():
        h.diperiksa += 1
        domain = nama.split(".", 1)[0]
        h.senarai.append(f"{nama:46s} {domain:16s} {sumber}")
        if domain not in registry:
            h.gagal(nama, f"domain `{domain}` tidak ada di registry", sumber)
    return h


def periksa_e2() -> Hasil:
    h = Hasil("E-2", "`event_type` dua segmen, huruf kecil, kata kerja lampau")
    for nama, sumber in panen_event():
        h.diperiksa += 1
        if POLA_GLOB.search(nama):
            h.senarai.append(f"{nama:46s} (glob — dilewati)")
            h.diperiksa -= 1
            continue
        segmen = nama.split(".")
        if len(segmen) != 2:
            h.gagal(nama, f"{len(segmen)} segmen, wajib 2", sumber)
            continue
        verb = segmen[1]
        kata_akhir = verb.rsplit("_", 1)[-1]
        h.senarai.append(f"{nama:46s} kata akhir: {kata_akhir}")
        if not lampau(kata_akhir):
            h.gagal(
                nama,
                f"`{kata_akhir}` bukan kata kerja lampau",
                sumber,
            )
    return h


# ───────────────────────────────────────────────────────── E-5 ──

# Nama event ditulis TELANJANG di naskah (`MissionCompleted`, bukan di
# dalam backtick), jadi panennya tidak boleh menuntut backtick.
POLA_PASCAL = re.compile(r"\b((?:[A-Z][a-z]+|WiFi){2,})\b")

# Nama dari naskah 1-2 (`16`), ditulis SEBELUM #38 memilih formatnya.
# `docs/SENSUS-EVENT.md` sudah mengeluarkannya dari hitungan pelanggaran
# dengan alasan yang sama: itu asal-usulnya, bukan pelanggarannya.
PRA_KEPUTUSAN = {
    "MeetingFinished": "naskah 1-2; kata kerjanya diselesaikan MeetingEnded",
    "MoodLogged": "naskah 1-2; justru nama yang akhirnya dipilih",
}

# Ditangani K-10, bukan lewat tabel padanan: ia jadi delapan `security.*`.
DILUAR_TABEL = {"SecurityEvent": "K-10 — amplop sama, domain `security.*`"}


def _ekor(nama: str) -> str:
    potong = re.findall(r"[A-Z][a-z]+|[A-Z]+(?![a-z])", nama)
    return potong[-1] if potong else ""


def periksa_e5() -> Hasil:
    """Tiap nama event di naskah punya baris di tabel padanan spec/03.

    Lubang yang ditutupnya nyata: E-1 dan E-2 hanya melihat nama yang
    SUDAH masuk tabel. Nama yang tidak pernah masuk tidak punya
    `event_type` sama sekali — jadi keduanya buta terhadapnya, dan
    justru itu bentuk kegagalan yang paling mungkin terjadi pada naskah
    berikutnya.
    """
    h = Hasil("E-5", "tiap nama event di naskah punya baris di tabel padanan")
    spec = baca(SPEC03)
    tabel = set(re.findall(r"^\| `([A-Za-z]+)` \| \*\*`", spec, re.M))
    if not tabel:
        h.gagal("spec/03", "tabel padanan tidak terbaca")
        return h
    # Kata kerja penutup yang tabel sendiri pakai = pembeda "ini nama
    # event", bukan daftar yang saya karang.
    verba = {_ekor(n) for n in tabel}
    h.catatan.append(
        f"tabel padanan: **{len(tabel)} baris**, "
        f"{len(verba)} kata kerja penutup dikenal"
    )

    kandidat: dict[str, set[str]] = {}
    for p in sorted(DOCS.glob("*.md")):
        if p.name in {"99-CATATAN-AUDIT.md", "SESSION-LOG.md"}:
            continue
        teks = buang_catatan_audit(p.read_text(encoding="utf-8"))
        for nama in POLA_PASCAL.findall(teks):
            if _ekor(nama) in verba:
                kandidat.setdefault(nama, set()).add(p.name.split("-")[0])

    h.catatan.append(f"kandidat di docs/: **{len(kandidat)}**")
    for nama in sorted(kandidat):
        h.diperiksa += 1
        asal = "·".join(sorted(kandidat[nama]))
        if nama in tabel:
            continue
        if nama in PRA_KEPUTUSAN:
            h.catatan.append(f"{nama} dikecualikan — {PRA_KEPUTUSAN[nama]}")
            continue
        if nama in DILUAR_TABEL:
            h.catatan.append(f"{nama} dikecualikan — {DILUAR_TABEL[nama]}")
            continue
        h.gagal(
            nama,
            "ditulis di naskah tetapi tidak punya baris di tabel padanan "
            "spec/03 — ia tidak punya `event_type`, jadi E-1 dan E-2 "
            "tidak bisa melihatnya",
            f"docs/{asal}",
        )
    return h


# ───────────────────────────────────────────────────────── G-1 ──


def periksa_g1() -> Hasil:
    h = Hasil("G-1", "tiap pasal Konstitusi §20.16 punya >= 1 penegak")
    teks = baca(ARCH08)
    sek = bagian(teks, r"^## §4 ")
    if not sek:
        h.gagal("arch/08 §4", "tabel penegak Konstitusi tidak ditemukan")
        return h

    pasal: dict[int, tuple[str, str, str]] = {}
    for baris in sek.splitlines():
        m = re.match(
            r"^\|\s*\*\*(\d+)\*\*\s*([^|]*?)\s*\|([^|]*)\|([^|]*)\|\s*$", baris
        )
        if not m:
            continue
        pasal[int(m.group(1))] = (
            m.group(2).strip(),
            m.group(3).strip(),
            m.group(4).strip(),
        )

    m = re.search(r"§4 Konstitusi §20\.16 — (\w+) pasal", sek)
    diharap = {"sepuluh": 10, "sembilan": 9, "sebelas": 11}.get(
        m.group(1) if m else "", 10
    )

    h.catatan.append(f"pasal terbaca: **{len(pasal)}** (diharapkan {diharap})")
    if len(pasal) != diharap:
        h.gagal(
            "arch/08 §4",
            f"{len(pasal)} pasal terbaca, judulnya menyebut {diharap}",
            "arch/08 §4",
        )

    for nomor in sorted(pasal):
        nama, penegak, mesin = pasal[nomor]
        h.diperiksa += 1
        bersih = re.sub(r"[⚠️✅🛑\s—-]+", "", penegak)
        h.senarai.append(f"Pasal {nomor:2d} {nama:28s} mesin={mesin}")
        if not bersih:
            h.gagal(f"Pasal {nomor} {nama}", "nol penegak", "arch/08 §4")
            continue
        if "⚠️" in mesin or "sebagian" in penegak.lower():
            # Pasal sebagian WAJIB menyebut bagian yang tak bisa diperiksa.
            if "tidak bisa diperiksa mesin" not in sek:
                h.gagal(
                    f"Pasal {nomor} {nama}",
                    "ditandai sebagian tetapi bagian yang tak terjaga "
                    "tidak dinyatakan",
                    "arch/08 §4",
                )
            else:
                h.catatan.append(
                    f"Pasal {nomor} **sebagian** — batasnya dinyatakan ✅"
                )
    return h


# ───────────────────────────────────────────────────────── R-1 ──

POLA_PASANGAN = re.compile(
    r"^\s*(?P<gerbang>[A-Za-z0-9_.]+|TIDAK-ADA)\s*->\s*(?P<dijaga>.+?)\s*$"
)


def muat_pasangan() -> tuple[dict[str, list[tuple[str, list[str]]]], str]:
    """Baca blok ```r1 dari arch/10 — dokumennya tetap sumber kebenaran."""
    teks = baca(ARCH10)
    m = re.search(r"```r1\n(.*?)```", teks, re.S)
    if not m:
        raise SystemExit(
            "🛑 arch/10 tidak memuat blok ```r1``` berisi pasangan gerbang. "
            "R-1 menolak menebak pasangannya sendiri."
        )
    blok = m.group(1)
    peta: dict[str, list[tuple[str, list[str]]]] = OrderedDict()
    peta_roadmap = None
    for baris in blok.splitlines():
        baris = baris.split("#", 1)[0].rstrip()
        if not baris.strip():
            continue
        if baris.startswith("[") and baris.rstrip().endswith("]"):
            peta_roadmap = baris.strip()[1:-1]
            peta.setdefault(peta_roadmap, [])
            continue
        mm = POLA_PASANGAN.match(baris)
        if mm and peta_roadmap:
            peta[peta_roadmap].append(
                (mm.group("gerbang"), mm.group("dijaga").split())
            )
    return peta, blok


POLA_BUTIR_FASE = re.compile(
    r"(?:\*\*)?`?([A-Z]{1,2}\d{2}\.\d{1,2})`?(?:\*\*)?"
)

# Penanda yang membuka catatan audit saya sendiri di dalam blok `>`.
# Pembedanya bukan tebakan: `docs/SENSUS-EVENT.md` sudah mengujinya —
# percobaan "semua baris `>` = catatan saya" SALAH (naskah juga mengutip
# pemilik dengan `>`), dan yang lulus validasi silang adalah menilai blok
# dari BARIS PERTAMANYA.
PENANDA_VONIS = ("⭐", "🛑", "⚠️", "💡", "🔴", "🔑", "🆕", "✅", "Butir", "**Butir")


def buang_catatan_audit(teks: str) -> str:
    """Buang blok `>` yang dibuka penanda vonis — usul, bukan naskah.

    Tanpa ini, milestone yang hanya SAYA usulkan (`G18.11 Safety, Privacy
    & Governance`) ikut terhitung sebagai butir roadmap yang ada — dan
    justru menutupi kegagalan yang R-1 cari.
    """
    keluar: list[str] = []
    dalam_blok = False
    blok_dibuang = False
    for baris in teks.splitlines():
        if baris.lstrip().startswith(">"):
            isi = baris.lstrip()[1:].strip()
            if not dalam_blok:
                dalam_blok = True
                blok_dibuang = isi.startswith(PENANDA_VONIS)
            if blok_dibuang:
                continue
            keluar.append(baris)
            continue
        if dalam_blok and not baris.strip():
            # baris kosong tidak memutus blok kutipan multi-paragraf
            if blok_dibuang:
                continue
            keluar.append(baris)
            continue
        dalam_blok = False
        blok_dibuang = False
        keluar.append(baris)
    return "\n".join(keluar)


_KODE_FASE: list[str] | None = None


def _semua_kode_fase() -> list[str]:
    """Panen sekali, pakai untuk semua prefiks — 272 berkas, bukan 272x6."""
    global _KODE_FASE
    if _KODE_FASE is None:
        kumpul: list[str] = []
        for p in sorted(DOCS.glob("*.md")):
            if p.name in {"99-CATATAN-AUDIT.md", "SESSION-LOG.md"}:
                continue
            teks = buang_catatan_audit(p.read_text(encoding="utf-8"))
            kumpul.extend(POLA_BUTIR_FASE.findall(teks))
        _KODE_FASE = kumpul
    return _KODE_FASE


def panen_butir_roadmap(prefiks: str) -> dict[str, int]:
    """Cari indeks tiap butir roadmap berprefiks `A14`/`R16`/… di docs/.

    Indeksnya angka sesudah titik; keberadaannya yang dicari, bukan
    urutan tulisnya.
    """
    butir: dict[str, int] = {}
    for kode in _semua_kode_fase():
        if kode.startswith(prefiks + "."):
            butir[kode] = int(kode.split(".", 1)[1])
    return butir


def panen_butir_spec07() -> dict[str, int]:
    teks = baca(SPEC07)
    butir: dict[str, int] = {}
    for m in re.finditer(r"^\|\s*(\d)\.(\d)\s*\|", teks, re.M):
        kode = f"{m.group(1)}.{m.group(2)}"
        butir[kode] = int(m.group(1)) * 100 + int(m.group(2))
    return butir


def panen_butir_arch10() -> dict[str, int]:
    teks = baca(ARCH10)
    butir: dict[str, int] = {}
    for m in re.finditer(r"^\|\s*\*\*T(\d{1,2})\*\*\s*\|", teks, re.M):
        butir[f"T{m.group(1)}"] = int(m.group(1))
    return butir


def indeks_roadmap(nama: str) -> dict[str, int]:
    if nama == "spec/07":
        return panen_butir_spec07()
    if nama == "arch/10":
        return panen_butir_arch10()
    return panen_butir_roadmap(nama)


def periksa_r1() -> Hasil:
    h = Hasil("R-1", "gerbang dijadwalkan sebelum hal yang dijaganya")
    peta, _ = muat_pasangan()

    for roadmap, pasangan in peta.items():
        butir = indeks_roadmap(roadmap)
        if not butir:
            h.gagal(roadmap, "nol butir roadmap terbaca dari dokumen")
            continue
        h.catatan.append(f"{roadmap}: {len(butir)} butir terbaca")
        for gerbang, dijaga in pasangan:
            h.diperiksa += 1
            if gerbang == "TIDAK-ADA":
                h.gagal(
                    roadmap,
                    f"gerbang untuk {' '.join(dijaga)} tidak punya butir "
                    f"roadmap sama sekali",
                    roadmap,
                )
                continue
            if gerbang not in butir:
                h.gagal(
                    roadmap,
                    f"gerbang `{gerbang}` tidak ditemukan di dokumen",
                    roadmap,
                )
                continue
            ig = butir[gerbang]
            telat = [t for t in dijaga if t in butir and butir[t] < ig]
            h.senarai.append(
                f"{roadmap:8s} {gerbang:8s} idx={ig:4d} "
                f"menjaga {len(dijaga):2d} butir · "
                f"{'GAGAL' if telat else 'lulus'}"
            )
            if telat:
                h.gagal(
                    f"{roadmap} · {gerbang}",
                    f"dijadwalkan SESUDAH {len(telat)} butir yang "
                    f"dijaganya: {' '.join(telat)}",
                    roadmap,
                )
    return h


# ───────────────────────────────────────────────────── penyaji ──

PEMERIKSAAN = {
    "E-1": periksa_e1,
    "E-2": periksa_e2,
    "E-5": periksa_e5,
    "G-1": periksa_g1,
    "R-1": periksa_r1,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "kode", nargs="*", help="E-1 E-2 E-5 G-1 R-1 (kosong = semua)"
    )
    p.add_argument("--senarai", action="store_true", help="cetak daftar panen")
    p.add_argument("--json", action="store_true", help="keluaran mesin")
    a = p.parse_args()

    pilih = [k.upper() for k in a.kode] or list(PEMERIKSAAN)
    tak_dikenal = [k for k in pilih if k not in PEMERIKSAAN]
    if tak_dikenal:
        raise SystemExit(f"🛑 pemeriksaan tak dikenal: {tak_dikenal}")

    hasil = [PEMERIKSAAN[k]() for k in pilih]

    if a.json:
        print(
            json.dumps(
                [
                    {
                        "kode": h.kode,
                        "judul": h.judul,
                        "lulus": h.lulus,
                        "diperiksa": h.diperiksa,
                        "temuan": [vars(t) for t in h.temuan],
                        "catatan": h.catatan,
                    }
                    for h in hasil
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if all(h.lulus for h in hasil) else 1

    for h in hasil:
        tanda = "✅ LULUS" if h.lulus else "🛑 GAGAL"
        print(f"\n{'=' * 72}")
        print(f"{h.kode}  {h.judul}")
        print(f"{'=' * 72}")
        print(f"diperiksa : {h.diperiksa}")
        for c in h.catatan:
            print(f"catatan   : {c}")
        print(f"hasil     : {tanda}  ({len(h.temuan)} temuan)")
        if h.temuan:
            print()
            for t in h.temuan:
                print(f"  🛑 {t.subjek}")
                print(f"     {t.alasan}")
                if t.sumber:
                    print(f"     → {t.sumber}")
        if a.senarai and h.senarai:
            print("\n  — yang dipanen —")
            for s in h.senarai:
                print(f"  · {s}")

    gagal = [h for h in hasil if not h.lulus]
    print(f"\n{'=' * 72}")
    print(
        f"RINGKASAN  {len(hasil) - len(gagal)} lulus · {len(gagal)} gagal  "
        f"({', '.join(h.kode for h in gagal) if gagal else 'nihil'})"
    )
    print(f"{'=' * 72}")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main())
