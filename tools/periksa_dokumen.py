#!/usr/bin/env python3
"""Pemeriksa dokumen HumanVerse XOS — pemeriksaan `arch/11` yang membaca
DOKUMEN, DDL, dan POHON DIREKTORI (bukan impor kode — itu `import-linter`).

Semula ditulis untuk empat pemeriksaan tanpa satu baris kode produksi. Sejak
Sprint 0 ia juga membaca artefak yang sampai ke basis data (berkas migrasi)
dan pohon repo yang sungguhan — tetapi tetap nol dependensi.

    E-1  segmen pertama `event_type` wajib ada di registry domain (arch/07 §2)
    E-2  `event_type` wajib dua segmen, huruf kecil, kata kerja lampau
    E-3  tidak ada `source='sensor'` di `events` (spec/01 + migrasi)
    E-4  kata kerja pengubah keadaan punya kembaran kegagalan (arch/07 §6)
    E-5  tiap nama event di naskah punya baris di tabel padanan spec/03
    P-1  tiap CREATE TABLE menyatakan retensi/who-can-set/on-delete (spec/01 + migrasi)
    P-2  tiap tabel punya kolom `data_subject` (spec/01 + migrasi)
    P-3  tidak ada `user_id` nullable tanpa penjaga (spec/01 + migrasi)
    A-1  satu angka tidak dipakai untuk R DAN L (manifest spec/05 + DDL `agents`)
    A-2  tiap tool di `tools:` punya `risk_level <= max_risk` (spec/05)
    A-3  agent yang dipanggil agent lain punya entri `kind: agent`
    B-6  tepat satu pohon `security/` (arch/03) · tak ada pohon kedua (repo nyata)
    M-4  tak ada direktori bernama kata kamus tabrakan di luar pemiliknya (repo nyata)
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
import os
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
SPEC01 = AKAR / "spec" / "01-DATABASE-SCHEMA.md"
SPEC03 = AKAR / "spec" / "03-EVENT-CONTRACTS.md"
SPEC05 = AKAR / "spec" / "05-AGENT-CONTRACTS.md"
ARCH03 = AKAR / "arch" / "03-MONOREPO-FINAL.md"
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
    "sung", "sunk", "swum", "torn", "bound", "sworn",
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


# ═══════════════════════════════════════════════ P · penyimpanan ══
#
# 🔑 `arch/11` §2 menggolongkan kelompok P sebagai "butuh kode: ya",
#    dan itu dijawab untuk artefak YANG BERJALAN. Tetapi yang diperiksa
#    P-1/P-2/P-3 adalah **DDL**, dan DDL-nya sudah ada — sebagai dokumen,
#    di `spec/01`. Pertanyaan yang terlewat bukan "apakah aturannya
#    benar" melainkan "**apakah yang diperiksanya sudah ada dalam
#    bentuk lain?**"

# 🔴 Versi pertama: `CREATE TABLE (\w+) \((.*?)\n\);` — SATU ejaan persis.
#    `IF NOT EXISTS`, nama berskema (`public.x`), `UNLOGGED`, atau akhiran
#    `) WITH (...);` membuat tabel TIDAK TERLIHAT, dan akhiran yang bukan
#    `\n);` membuat pola malas MENELAN tabel berikutnya — anotasi, kolom
#    `data_subject`, dan `user_id` tabel yang tertelan tidak pernah diperiksa.
#    Kini kepala dicari longgar, badan diambil dengan MENYEIMBANGKAN tanda
#    kurung, dan jumlah token `CREATE … TABLE` wajib sama dengan jumlah tabel
#    yang terbaca — tabel yang tidak terbaca parser adalah KEGAGALAN.
POLA_KEPALA_TABEL = re.compile(
    r"\bCREATE\s+(?:(?:GLOBAL|LOCAL)\s+)?(?:(?:TEMPORARY|TEMP|UNLOGGED)\s+)?TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?(?:\"?\w+\"?\.)?\"?(\w+)\"?\s*\(",
    re.I,
)
POLA_TOKEN_TABEL = re.compile(r"\bCREATE\b[\w\s]*?\bTABLE\b", re.I)
ANOTASI = ("@retention", "@who-can-set", "@on-delete")
MIGRASI = AKAR / "data" / "migrations" / "versions"


def buang_komentar_sql(teks: str) -> str:
    """Buang `-- …` sampai akhir baris, KECUALI di dalam literal '…'."""
    keluar, di_string, i = [], False, 0
    while i < len(teks):
        c = teks[i]
        if c == "'":
            di_string = not di_string
        elif not di_string and teks.startswith("--", i):
            j = teks.find("\n", i)
            i = len(teks) if j == -1 else j
            continue
        keluar.append(c)
        i += 1
    return "".join(keluar)


def _badan_seimbang(teks: str, buka: int) -> str | None:
    """Isi di antara `(` pada posisi `buka` dan pasangannya."""
    kedalaman, di_string, i = 0, False, buka
    while i < len(teks):
        c = teks[i]
        if c == "'":
            di_string = not di_string
        elif not di_string and teks.startswith("--", i):
            j = teks.find("\n", i)
            i = len(teks) if j == -1 else j
            continue
        elif not di_string and c == "(":
            kedalaman += 1
        elif not di_string and c == ")":
            kedalaman -= 1
            if kedalaman == 0:
                return teks[buka + 1:i]
        i += 1
    return None


def _sumber_ddl() -> list[tuple[str, str]]:
    """[(label, SQL)] — blok ```sql `spec/01` DAN tiap berkas migrasi naik.

    🔑 Sejak Sprint 0 tugas 0.4 DDL hidup di DUA tempat: sebagai dokumen
    (`spec/01`) dan sebagai artefak yang benar-benar dijalankan ke basis data
    (`data/migrations/versions/*.up.sql`). Memeriksa dokumennya saja akan
    meloloskan migrasi yang lupa anotasinya — dan migrasilah yang sampai ke
    basis data. Dari `spec/01` hanya blok ```sql yang dibaca: prosa yang
    menyebut "CREATE TABLE" bukan DDL.
    """
    blok = re.findall(r"```sql\n(.*?)```", baca(SPEC01), re.S)
    if not blok:
        raise SystemExit("🛑 spec/01 tanpa satu blok ```sql pun — P-1..P-3 tidak melihat apa pun")
    sumber = [("spec/01", "\n".join(blok))]
    if MIGRASI.exists():
        berkas = sorted(MIGRASI.glob("*.up.sql"))
        if not berkas:
            raise SystemExit(
                "🛑 data/migrations/versions ada tetapi tanpa satu pun *.up.sql — "
                "populasi migrasi kosong, P-1..P-3 tidak akan melihat apa pun"
            )
        sumber += [(p.relative_to(AKAR).as_posix(), baca(p)) for p in berkas]
    return sumber


def _tabel_ddl() -> list[tuple[str, str, str, str]]:
    """[(sumber, nama, badan, anotasi di atasnya)] dari spec/01 + migrasi.

    Badan yang dikembalikan masih memuat komentar SQL; pemeriksa yang
    menilai KODE wajib membuangnya sendiri (`buang_komentar_sql`).
    """
    hasil = []
    for label, teks in _sumber_ddl():
        for m in POLA_KEPALA_TABEL.finditer(teks):
            if "--" in teks[teks.rfind("\n", 0, m.start()) + 1:m.start()]:
                continue  # kepala di dalam komentar
            badan = _badan_seimbang(teks, m.end() - 1)
            if badan is None:
                raise SystemExit(f"🛑 {label}: tanda kurung CREATE TABLE {m.group(1)} tidak seimbang")
            kepala = teks[max(0, m.start() - 400):m.start()]
            # hanya baris komentar yang menempel tepat di atas CREATE TABLE
            atas = []
            for baris in reversed(kepala.splitlines()):
                if baris.strip().startswith("--"):
                    atas.append(baris)
                elif baris.strip() == "":
                    continue
                else:
                    break
            hasil.append((label, m.group(1), badan, "\n".join(atas)))
    return hasil


def _populasi_tak_terbaca() -> list[tuple[str, int, int]]:
    """[(sumber, token CREATE…TABLE, tabel terbaca)] yang jumlahnya tidak sama."""
    terbaca: dict[str, int] = {}
    for label, *_ in _tabel_ddl():
        terbaca[label] = terbaca.get(label, 0) + 1
    selisih = []
    for label, teks in _sumber_ddl():
        token = len(POLA_TOKEN_TABEL.findall(buang_komentar_sql(teks)))
        if token != terbaca.get(label, 0):
            selisih.append((label, token, terbaca.get(label, 0)))
    return selisih


def periksa_p1() -> Hasil:
    h = Hasil("P-1", "tiap CREATE TABLE menyatakan retensi, who-can-set, on-delete")
    tabel = _tabel_ddl()
    per_sumber: dict[str, int] = {}
    for label, *_ in tabel:
        per_sumber[label] = per_sumber.get(label, 0) + 1
    h.catatan.append(
        "tabel per sumber: " + " · ".join(f"`{s}` **{n}**" for s, n in per_sumber.items())
    )
    if MIGRASI.exists() and not any(s != "spec/01" for s in per_sumber):
        h.gagal(
            "data/migrations",
            "berkas migrasi ada tetapi tidak satu pun CREATE TABLE terbaca — "
            "pemeriksa tidak melihat artefak yang sampai ke basis data",
            "data/migrations/versions",
        )
    for label, token, terbaca in _populasi_tak_terbaca():
        h.gagal(
            label,
            f"{token} pernyataan CREATE … TABLE tetapi hanya {terbaca} yang terbaca parser — "
            "tabel yang tidak terbaca tidak pernah diperiksa",
            label,
        )
    for label, nama, _badan, atas in tabel:
        h.diperiksa += 1
        hilang = [a for a in ANOTASI if a not in atas]
        h.senarai.append(
            f"{label:40s} {nama:26s} {'lengkap' if not hilang else 'HILANG ' + ' '.join(hilang)}"
        )
        if hilang:
            h.gagal(nama, f"tanpa {' · '.join(hilang)}", label)
    return h


def periksa_p2() -> Hasil:
    h = Hasil("P-2", "tiap tabel punya kolom `data_subject`")
    for label, nama, badan, _atas in _tabel_ddl():
        h.diperiksa += 1
        ada = re.search(r"^\s*data_subject\s", buang_komentar_sql(badan), re.M) is not None
        h.senarai.append(f"{label:40s} {nama:26s} {'ada' if ada else 'TIDAK ADA'}")
        if not ada:
            h.gagal(
                nama,
                "tanpa kolom `data_subject` — baris pengguna tidak bisa "
                "dibedakan dari baris orang yang tak punya akun",
                label,
            )
    return h


def periksa_p3() -> Hasil:
    """`user_id` nullable = RLS `user_id = current_user` meloloskan NULL.

    ⚠️ `PRIMARY KEY` sudah berarti `NOT NULL`; menghitungnya sebagai
    pelanggaran adalah positif palsu, dan versi pertama pemeriksa ini
    melakukannya (`profiles.user_id uuid PRIMARY KEY`).
    """
    h = Hasil("P-3", "tidak ada `user_id` yang nullable tanpa penjaga")
    for label, nama, badan, _atas in _tabel_ddl():
        m = re.search(r"^\s*user_id\s+(\S+)([^\n]*)$", buang_komentar_sql(badan), re.M)
        if not m:
            h.senarai.append(f"{label:40s} {nama:26s} tanpa user_id")
            continue
        h.diperiksa += 1
        sisa = m.group(2)
        aman = "NOT NULL" in sisa or "PRIMARY KEY" in sisa
        # CHECK yang mengikat user_id kepada data_subject juga sah
        # `[^)]*` tidak cukup: CHECK yang sah punya tanda kurung BERSARANG
        # — `CHECK ((data_subject = 'user') = (user_id IS NOT NULL))` —
        # dan versi pertama pemeriksa ini menolaknya sebagai tak-terjaga.
        # 🔴 Komentar SQL dibuang dulu: sebuah komentar yang kebetulan
        # menyebut "CHECK … data_subject … user_id" bukan penjaga, dan
        # migrasi 0001 memang punya komentar semacam itu di atas CHECK-nya.
        dijaga = any(
            "CHECK" in kode and "data_subject" in kode and "user_id" in kode
            for kode in buang_komentar_sql(badan).splitlines()
        )
        h.senarai.append(
            f"{label:40s} {nama:26s} "
            f"{'NOT NULL/PK' if aman else ('dijaga CHECK' if dijaga else 'NULLABLE')}"
        )
        if not aman and not dijaga:
            h.gagal(
                nama,
                "`user_id` nullable tanpa CHECK yang mengikatnya ke "
                "`data_subject` — RLS `user_id = current_user` meloloskan NULL",
                label,
            )
    return h


# ═════════════════════════════════════════ E-3 · bukan aliran sensor ══


def periksa_e3() -> Hasil:
    """arch/06 §3 — `events` hanya menerima kejadian bermakna bagi manusia.

    Separuh E-3 yang membaca DDL bisa jalan sekarang; separuh lainnya (uji
    admisi saat event diterbitkan) menunggu Sprint 3 tugas 3.1.
    """
    h = Hasil("E-3", "tidak ada `source='sensor'` di tabel `events`")
    for label, nama, badan, _atas in _tabel_ddl():
        if nama != "events":
            continue
        h.diperiksa += 1
        # Komentar dibuang dulu — pelajaran P-3 berlaku di sini juga — dan
        # CHECK `source` wajib TEPAT satu.
        pola_check = r"CHECK\s*\(\s*source\s+IN\s*\(([^)]*)\)\s*\)"
        cocok = re.findall(pola_check, buang_komentar_sql(badan))
        if len(cocok) > 1:
            h.gagal(f"{label} · events.source", f"{len(cocok)} CHECK source — wajib tepat satu", label)
            continue
        m = re.search(pola_check, buang_komentar_sql(badan))
        if not m:
            h.gagal(
                f"{label} · events.source",
                "tanpa CHECK — nilai apa pun lolos, termasuk `sensor`",
                label,
            )
            continue
        nilai = re.findall(r"'([^']*)'", m.group(1))
        h.senarai.append(f"{label:40s} events.source ∈ {{{', '.join(nilai)}}}")
        if "sensor" in nilai:
            h.gagal(
                f"{label} · events.source",
                "`sensor` diizinkan — uji admisi arch/06 §3 bisa dilewati dengan satu nilai enum",
                label,
            )
    if h.diperiksa == 0:
        h.gagal("events", "tabel `events` tidak ditemukan di DDL mana pun — pemeriksa buta", "spec/01")
    return h


# ═══════════════════════════════════════════════════ A · agent ══


def _registry_tool() -> dict[str, tuple[str, int]]:
    teks = baca(SPEC05)
    reg: dict[str, tuple[str, int]] = {}
    for m in re.finditer(
        r"^\| `([a-z][a-z0-9_.]*)` \| \*{0,2}(read|write|agent)\*{0,2} \| (\d) \|",
        teks,
        re.M,
    ):
        reg[m.group(1)] = (m.group(2), int(m.group(3)))
    return reg


def _agent_v0() -> dict[str, tuple[int, list[str]]]:
    teks = baca(SPEC05)
    ag: dict[str, tuple[int, list[str]]] = {}
    for m in re.finditer(
        r"^\| `([a-z-]+-agent)` \| \*{0,2}(R\d)\*{0,2}[^|]*\| ([^|]+)\|", teks, re.M
    ):
        tools = re.findall(r"`?([a-z][a-z0-9_.]*\.[a-z][a-z0-9_]*)`?", m.group(3))
        ag[m.group(1)] = (int(m.group(2)[1]), tools)
    return ag


def periksa_a2() -> Hasil:
    h = Hasil("A-2", "tiap tool di `tools:` punya `risk_level <= max_risk`")
    reg, ag = _registry_tool(), _agent_v0()
    h.catatan.append(f"registry tool: **{len(reg)}** · agent: **{len(ag)}**")
    if not reg or not ag:
        h.gagal("spec/05", "tabel registry tool atau tabel agent tidak terbaca")
        return h
    for nama, (pagu, tools) in sorted(ag.items()):
        for t in tools:
            h.diperiksa += 1
            if t not in reg:
                h.gagal(
                    f"{nama} → {t}",
                    "tool dipakai agent tetapi TIDAK ADA di registry tool — "
                    "`risk_level`-nya tidak bisa dibandingkan dengan `max_risk`",
                    "spec/05",
                )
                continue
            _kind, risk = reg[t]
            h.senarai.append(f"{nama:22s} {t:24s} risk={risk} <= pagu={pagu}")
            if risk > pagu:
                h.gagal(
                    f"{nama} → {t}",
                    f"risk_level {risk} > max_risk R{pagu}",
                    "spec/05",
                )
    return h


def periksa_a3() -> Hasil:
    h = Hasil("A-3", "agent yang dipanggil agent lain punya entri `kind: agent`")
    reg, ag = _registry_tool(), _agent_v0()
    dipanggil = {
        t for _n, (_p, tools) in ag.items() for t in tools if t.startswith("agent.")
    }
    h.catatan.append(f"agent yang dipanggil sebagai tool: **{len(dipanggil)}**")
    for t in sorted(dipanggil):
        h.diperiksa += 1
        if t not in reg:
            h.gagal(
                t,
                "dipanggil sebagai tool tetapi tidak punya baris di registry "
                "tool — K-14 menuntut entri `kind: agent`; tanpa barisnya "
                "pemanggilannya tidak melewati gerbang",
                "spec/05",
            )
            continue
        kind, _risk = reg[t]
        h.senarai.append(f"{t:24s} kind={kind}")
        if kind != "agent":
            h.gagal(t, f"terdaftar `kind: {kind}`, wajib `agent`", "spec/05")
    return h


def periksa_a1() -> Hasil:
    """H-21 — `R` (risiko AKSI) dan `L` (otonomi AGENT) adalah dua tangga.

    Yang diperiksanya sudah ada sebagai dokumen: skema manifest `spec/05` dan
    DDL tabel `agents` (spec/01 + migrasi). Validator manifest (Sprint 4
    tugas 4.2) kelak memeriksa MANIFEST SUNGGUHAN dengan aturan yang sama.
    """
    h = Hasil("A-1", "satu angka tidak dipakai untuk `R` DAN `L`")
    teks = baca(SPEC05)
    m = re.search(r"## Skema manifest\s+```yaml\n(.*?)```", teks, re.S)
    if not m:
        h.gagal("spec/05", "blok ```yaml skema manifest tidak ditemukan", "spec/05")
        return h
    yaml = m.group(1)
    atas = dict(re.findall(r"^([a-z_]+):[ \t]*([^#\n]*)", yaml, re.M))
    h.diperiksa += 1
    for terlarang in ("risk_level", "risk"):
        if terlarang in atas:
            h.gagal(
                f"manifest · {terlarang}",
                f"`{terlarang}` sebagai properti AGENT membalik H-21 — agent memakai "
                "`max_risk` (pagu), bukan satu tingkat risiko",
                "spec/05",
            )
    pagu = atas.get("max_risk", "").strip()
    otonomi = re.search(r"^autonomy:[ \t]*\n((?:[ \t]+[^\n]*\n)+)", yaml, re.M)
    level = re.search(r"^\s+max_level:[ \t]*(\S+)", otonomi.group(1), re.M) if otonomi else None
    h.senarai.append(f"manifest max_risk={pagu or '—'} · autonomy.max_level="
                     f"{level.group(1) if level else '—'}")
    if not re.fullmatch(r"R[0-4]", pagu):
        h.gagal("manifest · max_risk", f"wajib bernilai R0–R4, tertulis `{pagu or 'kosong'}`", "spec/05")
    if not level:
        h.gagal("manifest · autonomy.max_level", "tidak ada — tangga L tidak punya tempat", "spec/05")
    elif not re.fullmatch(r"L[0-5]", level.group(1)):
        h.gagal(
            "manifest · autonomy.max_level",
            f"wajib bernilai L0–L5, tertulis `{level.group(1)}` — "
            "angka dari tangga lain dipakai untuk otonomi",
            "spec/05",
        )
    for label, nama, badan, _atas in _tabel_ddl():
        if nama != "agents":
            continue
        h.diperiksa += 1
        kolom = re.findall(r"^\s*([a-z_]+)\s+[a-z]", badan, re.M)
        h.senarai.append(f"{label:40s} agents: max_risk={'max_risk' in kolom} "
                         f"risk_level={'risk_level' in kolom}")
        if "risk_level" in kolom:
            h.gagal(f"{label} · agents.risk_level",
                    "kolom satu-angka pada baris agent — E-119/#97", label)
        if "max_risk" not in kolom:
            h.gagal(f"{label} · agents.max_risk", "pagu risiko agent tidak ada", label)
    return h


# ══════════════════════════════════════════════ B-6 · satu pohon ══

KELUARGA_KEAMANAN = {
    "security", "safety", "privacy", "consent", "audit",
    "permissions", "policies", "trust", "compliance", "ethics",
}


def periksa_b6() -> Hasil:
    h = Hasil("B-6", "tepat satu pohon `security/` di tingkat atas")
    teks = baca(ARCH03)
    potong = teks.split("```")
    if len(potong) < 2:
        h.gagal("arch/03", "blok pohon monorepo tidak ditemukan")
        return h
    blok = potong[1]
    atas = re.findall(r"^[├└]── ([a-z][a-z0-9-]*)/", blok, re.M)
    h.diperiksa = len(atas)
    h.catatan.append(f"direktori tingkat atas: **{len(atas)}**")
    ketemu = [d for d in atas if d in KELUARGA_KEAMANAN]
    h.senarai.append("keluarga keamanan: " + (" ".join(ketemu) or "NIHIL"))
    if len(ketemu) != 1:
        h.gagal(
            "arch/03",
            f"{len(ketemu)} pohon keluarga keamanan ({' '.join(ketemu)}), "
            f"wajib tepat 1 — tanpa itu aturan impor §8.42 tidak bisa DINYATAKAN",
            "arch/03",
        )

    # ── Pohon NYATA (sejak Sprint 0). V0 belum punya `security/` sebagai
    # kode (arch/03 §8), jadi "tepat satu" belum bisa dituntut di sini. Yang
    # BISA dituntut hari ini adalah bentuk yang membuat B-1 mustahil
    # dinyatakan: pohon keamanan KEDUA. Diperiksa di tingkat atas repo, di
    # akar tiap paket aplikasi, dan di antara modulnya.
    nyata = _direktori_tingkat_atas_nyata()
    keluarga = [p for p in nyata if p.rsplit("/", 1)[-1] in KELUARGA_KEAMANAN]
    h.diperiksa += len(nyata)
    h.catatan.append(
        f"repo nyata: **{len(nyata)}** direktori tingkat atas/paket/modul · "
        f"keluarga keamanan: {' '.join(keluarga) or 'NIHIL'}"
    )
    bukan_security = [p for p in keluarga if not p.endswith("security")]
    if bukan_security or len(keluarga) > 1:
        h.gagal(
            "repo nyata",
            f"pohon keluarga keamanan di luar satu `security/`: {' '.join(keluarga)} — "
            "pohon kedua membuat §8.42 (B-1) tidak bisa DINYATAKAN",
            "arch/03 §3 · §8",
        )
    return h


_ABAIKAN_DIREKTORI = {
    ".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".ruff_cache",
    ".pytest_cache", ".import_linter_cache", "htmlcov", ".idea", ".vscode",
    # keluaran `flutter pub get` / `flutter build` (apps/mobile) — dibuat ulang
    # tiap pembangunan dan diabaikan git; bukan pohon yang ditulis orang
    ".dart_tool", "build",
}


def _direktori_tingkat_atas_nyata() -> list[str]:
    """Tingkat atas repo · akar tiap paket aplikasi dan modulnya · isi
    `services/` dan `packages/` (wadah kode di pohon final arch/03).

    ⚠️ Yang SENGAJA tidak ditelusuri: subdirektori di DALAM sebuah modul.
    `identity/consent/` sah — spec/06 memberi `consents` kepada `identity` —
    dan `tests/security/`, `docs/security/` sah di pohon arch/03 sendiri.
    Menelusuri semuanya akan menuduh yang benar.
    """
    calon = [p for p in AKAR.iterdir() if p.is_dir() and p.name not in _ABAIKAN_DIREKTORI]
    for wadah in ("services", "packages"):
        if (AKAR / wadah).is_dir():
            calon += [
                p for p in (AKAR / wadah).iterdir()
                if p.is_dir() and p.name not in _ABAIKAN_DIREKTORI
            ]
    for paket in sorted(AKAR.glob("apps/*/src/*")):
        if paket.is_dir() and paket.name not in _ABAIKAN_DIREKTORI:
            calon += [p for p in paket.iterdir() if p.is_dir() and p.name not in _ABAIKAN_DIREKTORI]
            modul = paket / "modules"
            if modul.is_dir():
                calon += [p for p in modul.iterdir() if p.is_dir() and p.name not in _ABAIKAN_DIREKTORI]
    return sorted(p.relative_to(AKAR).as_posix() for p in calon)


# ═══════════════════════════════════ M-4 · kata dari kamus tabrakan ══

ARCH02 = AKAR / "arch" / "02-BOUNDED-CONTEXT.md"

# arch/03 §8 — letak modul V0 di dalam monolit lawan letaknya di pohon final.
# Modul human-core naik ke `services/`; sisanya naik satu tingkat, nama sama.
AKAR_KODE_V0 = "apps/api/src/hvx/modules/"
MODUL_SERVICES_V0 = {"identity", "profile", "goals", "habits", "checkins", "journal", "activities"}


def _muat_kamus_tabrakan() -> dict[str, set[str]]:
    """arch/02 §4 → {kata: himpunan path SAH untuk direktori bernama kata itu}.

    Satu baris sah hanya kalau kolom "Nama direktori final" memakai kata itu
    TELANJANG (`agents/registry/`, `planning/`). Baris yang mengganti nama
    (`sim-behavior/`) tidak memberi izin apa pun, dan baris ber-🛑
    (*“tidak punya `research/`”*) adalah LARANGAN, bukan izin.
    """
    sek = bagian(baca(ARCH02), r"^## §4 Kamus")
    kamus: dict[str, set[str]] = {}
    kata = None
    for b in sek.splitlines():
        m = re.match(r"^\|\s*(?:\*\*([a-z]+)\*\*)?\s*\|(.*)\|\s*$", b)
        if not m:
            continue
        kata = m.group(1) or kata
        kolom = [k.strip() for k in m.group(2).split("|")]
        if kata is None or len(kolom) < 3:
            continue
        kamus.setdefault(kata, set())
        konteks, final = kolom[0], kolom[-1]
        if "🛑" in final:
            continue
        for path in re.findall(r"`([a-z][a-z0-9/-]*)/`", final):
            if path.rsplit("/", 1)[-1] != kata:
                continue
            if "/" in path:
                kamus[kata].add(path)
            else:
                for k in re.findall(r"[`*]([a-z][a-z0-9-]*)[`*]", konteks):
                    kamus[kata].add(kata if k == kata else f"{k}/{kata}")
    return kamus


def _normalkan_v0(rel: str) -> str:
    if not rel.startswith(AKAR_KODE_V0):
        return rel
    sisa = rel[len(AKAR_KODE_V0):]
    return f"services/{sisa}" if sisa.split("/", 1)[0] in MODUL_SERVICES_V0 else sisa


def periksa_m4() -> Hasil:
    h = Hasil("M-4", "tidak ada direktori bernama kata kamus tabrakan di luar pemilik sahnya")
    kamus = _muat_kamus_tabrakan()
    if not kamus:
        h.gagal("arch/02 §4", "kamus tabrakan tidak terbaca — pemeriksa buta", "arch/02")
        return h
    # Direktori tingkat atas arch/03 adalah pemilik sah namanya sendiri
    # (`simulation/` mesin bersama, `memory/`, `research/`).
    pohon = baca(ARCH03).split("```")[1]
    for d in re.findall(r"^[├└]── ([a-z][a-z0-9-]*)/", pohon, re.M):
        if d in kamus:
            kamus[d].add(d)
    h.catatan.append(
        "kamus: " + " · ".join(f"`{k}`→{sorted(v) or '∅'}" for k, v in sorted(kamus.items()))
    )
    for akar, dirs, _berkas in os.walk(AKAR):
        dirs[:] = [d for d in dirs if d not in _ABAIKAN_DIREKTORI]
        for d in dirs:
            rel = (Path(akar) / d).relative_to(AKAR).as_posix()
            h.diperiksa += 1
            if d not in kamus:
                continue
            norm = _normalkan_v0(rel)
            h.senarai.append(f"{rel} → {norm}")
            if norm not in kamus[d]:
                h.gagal(
                    rel,
                    f"`{d}/` di luar pemilik sahnya — yang sah: "
                    f"{', '.join(sorted(kamus[d])) or 'TIDAK ADA (nama wajib dikualifikasi)'}",
                    "arch/02 §4",
                )
    return h


# ════════════════════════════════════════════ E-4 · kembaran ══


def periksa_e4() -> Hasil:
    h = Hasil("E-4", "kata kerja pengubah keadaan punya kembaran kegagalan")
    # 🔴 Nama HANYA dicari di `spec/03`. Versi pertama memakai
    # `panen_event()`, yang ikut memanen `arch/07` — dan daftar wajibnya
    # sendiri ada di `arch/07` §6. Hasilnya LULUS untuk semua, sebab
    # pemeriksa mencari namanya di berkas yang menuliskannya. Melingkar.
    teks03 = baca(SPEC03)
    nama = set(POLA_EVENT.findall(teks03)) | set(POLA_TELANJANG.findall(teks03))
    nama -= set(BUKAN_EVENT)
    teks = baca(ARCH07)
    if "## §6" not in teks:
        h.gagal("arch/07", "§6 (tabel kembaran wajib) tidak ditemukan")
        return h
    sek = teks.split("## §6")[1].split("## §7")[0]
    pasangan = re.findall(r"^\| `([a-z][a-z0-9_.]*)` \| ([^|]+)\|", sek, re.M)
    h.catatan.append(f"pasangan wajib arch/07 §6: **{len(pasangan)}**")
    for aksi, kolom in pasangan:
        kembar = re.findall(r"`([a-z][a-z0-9_.]*)`", kolom)
        ada_aksi = aksi in nama
        hilang = [k for k in kembar if k not in nama]
        h.senarai.append(
            f"{aksi:26s} {'ADA ' if ada_aksi else 'belum'} → "
            + " ".join(f"{k}={'ADA' if k in nama else 'HILANG'}" for k in kembar)
        )
        h.diperiksa += 1
        # Aturannya SIMETRIS di sini: satu sisi ada, sisi lain wajib ada.
        # Pasangan yang KEDUANYA belum ada adalah pekerjaan fase nanti,
        # bukan pelanggaran hari ini — dan itu dinyatakan, bukan didiamkan.
        if ada_aksi and hilang:
            h.gagal(
                aksi,
                f"ada di `spec/03` tetapi kembarannya tidak: {' '.join(hilang)}",
                "arch/07 §6",
            )
        elif not ada_aksi and len(hilang) < len(kembar):
            punya = [k for k in kembar if k in nama]
            h.gagal(
                aksi,
                f"kembarannya ada ({' '.join(punya)}) tetapi kata kerja "
                f"aksinya sendiri tidak pernah didefinisikan",
                "arch/07 §6",
            )
    belum = [a for a, k in pasangan if a not in nama
             and all(x not in nama for x in re.findall(r"`([a-z][a-z0-9_.]*)`", k))]
    if belum:
        h.catatan.append(
            f"pasangan yang KEDUA sisinya belum ada (pekerjaan fase nanti, "
            f"bukan pelanggaran): {' '.join(belum)}"
        )
    return h


# ───────────────────────────────────────────────────── penyaji ──

PEMERIKSAAN = {
    "B-6": periksa_b6,
    "M-4": periksa_m4,
    "P-1": periksa_p1,
    "P-2": periksa_p2,
    "P-3": periksa_p3,
    "E-1": periksa_e1,
    "E-2": periksa_e2,
    "E-3": periksa_e3,
    "E-4": periksa_e4,
    "E-5": periksa_e5,
    "A-1": periksa_a1,
    "A-2": periksa_a2,
    "A-3": periksa_a3,
    "G-1": periksa_g1,
    "R-1": periksa_r1,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "kode", nargs="*",
        help=" ".join(PEMERIKSAAN) + " (kosong = semua)"
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
