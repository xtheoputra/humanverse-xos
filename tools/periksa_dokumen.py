#!/usr/bin/env python3
"""Pemeriksa dokumen HumanVerse XOS — E-1, E-2, G-1, R-1.

Empat dari dua puluh lima pemeriksaan `arch/11` yang bisa dijalankan
TANPA satu baris kode produksi, sebab keempatnya membaca DOKUMEN.

    E-1  segmen pertama `event_type` wajib ada di registry domain (arch/07 §2)
    E-2  `event_type` wajib dua segmen, huruf kecil, kata kerja lampau
    E-4  kata kerja pengubah keadaan punya kembaran kegagalan (arch/07 §6)
    E-5  tiap nama event di naskah punya baris di tabel padanan spec/03
    P-1  tiap CREATE TABLE menyatakan retensi/who-can-set/on-delete (spec/01)
    P-2  tiap tabel punya kolom `data_subject`
    P-3  tidak ada `user_id` nullable tanpa penjaga
    A-2  tiap tool di `tools:` punya `risk_level <= max_risk` (spec/05)
    A-3  agent yang dipanggil agent lain punya entri `kind: agent`
    B-6  tepat satu pohon `security/` (arch/03)
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


# ═══════════════════════════════════════════════ P · penyimpanan ══
#
# 🔑 `arch/11` §2 menggolongkan kelompok P sebagai "butuh kode: ya",
#    dan itu dijawab untuk artefak YANG BERJALAN. Tetapi yang diperiksa
#    P-1/P-2/P-3 adalah **DDL**, dan DDL-nya sudah ada — sebagai dokumen,
#    di `spec/01`. Pertanyaan yang terlewat bukan "apakah aturannya
#    benar" melainkan "**apakah yang diperiksanya sudah ada dalam
#    bentuk lain?**"

POLA_TABEL = re.compile(r"CREATE TABLE (\w+) \((.*?)\n\);", re.S)
ANOTASI = ("@retention", "@who-can-set", "@on-delete")


def _tabel_ddl() -> list[tuple[str, str, str]]:
    """[(nama, badan, anotasi di atasnya)] dari spec/01."""
    teks = baca(SPEC01)
    hasil = []
    for m in POLA_TABEL.finditer(teks):
        awal = teks.rfind("\n\n", 0, m.start())
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
        hasil.append((m.group(1), m.group(2), "\n".join(atas)))
    return hasil


def periksa_p1() -> Hasil:
    h = Hasil("P-1", "tiap CREATE TABLE menyatakan retensi, who-can-set, on-delete")
    tabel = _tabel_ddl()
    h.catatan.append(f"tabel di `spec/01`: **{len(tabel)}**")
    for nama, _badan, atas in tabel:
        h.diperiksa += 1
        hilang = [a for a in ANOTASI if a not in atas]
        h.senarai.append(f"{nama:26s} {'lengkap' if not hilang else 'HILANG ' + ' '.join(hilang)}")
        if hilang:
            h.gagal(nama, f"tanpa {' · '.join(hilang)}", "spec/01")
    return h


def periksa_p2() -> Hasil:
    h = Hasil("P-2", "tiap tabel punya kolom `data_subject`")
    for nama, badan, _atas in _tabel_ddl():
        h.diperiksa += 1
        ada = re.search(r"^\s*data_subject\s", badan, re.M) is not None
        h.senarai.append(f"{nama:26s} {'ada' if ada else 'TIDAK ADA'}")
        if not ada:
            h.gagal(
                nama,
                "tanpa kolom `data_subject` — baris pengguna tidak bisa "
                "dibedakan dari baris orang yang tak punya akun",
                "spec/01",
            )
    return h


def periksa_p3() -> Hasil:
    """`user_id` nullable = RLS `user_id = current_user` meloloskan NULL.

    ⚠️ `PRIMARY KEY` sudah berarti `NOT NULL`; menghitungnya sebagai
    pelanggaran adalah positif palsu, dan versi pertama pemeriksa ini
    melakukannya (`profiles.user_id uuid PRIMARY KEY`).
    """
    h = Hasil("P-3", "tidak ada `user_id` yang nullable tanpa penjaga")
    for nama, badan, _atas in _tabel_ddl():
        m = re.search(r"^\s*user_id\s+(\S+)([^\n]*)$", badan, re.M)
        if not m:
            h.senarai.append(f"{nama:26s} tanpa user_id")
            continue
        h.diperiksa += 1
        sisa = m.group(2)
        aman = "NOT NULL" in sisa or "PRIMARY KEY" in sisa
        # CHECK yang mengikat user_id kepada data_subject juga sah
        # `[^)]*` tidak cukup: CHECK yang sah punya tanda kurung BERSARANG
        # — `CHECK ((data_subject = 'user') = (user_id IS NOT NULL))` —
        # dan versi pertama pemeriksa ini menolaknya sebagai tak-terjaga.
        dijaga = any(
            "CHECK" in b_ and "data_subject" in b_ and "user_id" in b_
            for b_ in badan.splitlines()
        )
        h.senarai.append(
            f"{nama:26s} {'NOT NULL/PK' if aman else ('dijaga CHECK' if dijaga else 'NULLABLE')}"
        )
        if not aman and not dijaga:
            h.gagal(
                nama,
                "`user_id` nullable tanpa CHECK yang mengikatnya ke "
                "`data_subject` — RLS `user_id = current_user` meloloskan NULL",
                "spec/01",
            )
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
            kind, risk = reg[t]
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
    "P-1": periksa_p1,
    "P-2": periksa_p2,
    "P-3": periksa_p3,
    "E-1": periksa_e1,
    "E-2": periksa_e2,
    "E-4": periksa_e4,
    "E-5": periksa_e5,
    "A-2": periksa_a2,
    "A-3": periksa_a3,
    "G-1": periksa_g1,
    "R-1": periksa_r1,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "kode", nargs="*",
        help="B-6 P-1 P-2 P-3 E-1 E-2 E-4 E-5 A-2 A-3 G-1 R-1 (kosong = semua)"
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
