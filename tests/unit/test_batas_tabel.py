"""spec/06 aturan 5 — SQL sebuah modul hanya menyebut tabel milik modul itu.

Aturan ini menunggu `repository.py` pertama (Sprint 1). Tabel kepemilikan
dibaca DARI spec/06, bukan disalin ke sini: kalau spec/06 memindahkan tabel,
uji ini ikut pindah; kalau tabelnya hilang dari dokumen, uji ini GAGAL.

Yang dipindai: tiap berkas `.py` di modul — bukan hanya `repository.py` —
sebab SQL yang pindah ke `service.py` tetap SQL.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import pytest

AKAR = Path(__file__).resolve().parents[2]
MODUL = AKAR / "apps/api/src/hvx/modules"
SPEC06 = AKAR / "spec" / "06-MODULE-BOUNDARIES.md"

# Kata SQL yang diikuti nama tabel. `ON` sengaja tidak dihitung: ia juga dipakai
# `ON CONFLICT (kolom)` dan `ON DELETE`, yang bukan nama tabel. `USING` dihitung:
# `DELETE … USING tabel` — `USING (ungkapan)` tidak diawali nama, jadi tidak cocok.
#
# 🔴 Tinjauan Sprint 1: versi pertama hanya membaca SATU tabel sesudah kata kunci —
# `FROM users u, goals g` dan `DELETE … USING goals` lolos tanpa terbaca.
_NAMA = r"(?:ONLY\s+)?(?:public\.)?\"?([a-z_]+)\"?(?:\s+(?:AS\s+)?[a-z_]+)?"
_RUJUKAN = re.compile(
    rf"\b(?:FROM|JOIN|INTO|UPDATE|TABLE|REFERENCES|USING)\s+{_NAMA}((?:\s*,\s*{_NAMA})*)",
    re.IGNORECASE,
)
_SESUDAH_KOMA = re.compile(rf"\s*,\s*{_NAMA}", re.IGNORECASE)


def tabel_disebut(teks: str) -> Iterator[tuple[int, str]]:
    """(posisi, nama) tiap calon nama tabel di teks — kata SQL biasa ikut, disaring pemanggil."""
    for cocok in _RUJUKAN.finditer(teks):
        yield cocok.start(), cocok.group(1).lower()
        for lanjutan in _SESUDAH_KOMA.finditer(cocok.group(2)):
            yield cocok.start(), lanjutan.group(1).lower()


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT g.id FROM goals g",
        "SELECT 1 FROM users u, goals g WHERE g.user_id = u.id",
        "SELECT 1 FROM users AS u, public.goals AS g",
        "DELETE FROM consents c USING goals g WHERE c.user_id = g.user_id",
        "SELECT 1 FROM users u JOIN goals g ON g.user_id = u.id",
    ],
)
def test_pemindai_membaca_tiap_tabel_di_klausa(sql: str) -> None:
    assert "goals" in {nama for _, nama in tabel_disebut(sql)}, f"`goals` tidak terbaca di: {sql}"


def _kepemilikan() -> dict[str, set[str]]:
    teks = SPEC06.read_text(encoding="utf-8")
    bagian = teks.split("## Kepemilikan tabel", 1)[1].split("\n## ", 1)[0]
    milik: dict[str, set[str]] = {}
    for modul, tabel in re.findall(r"^\| `([a-z]+)` \| (.+?) \|$", bagian, re.M):
        milik[modul] = set(re.findall(r"`([a-z_]+)`", tabel))
    return milik


def test_tabel_kepemilikan_spec06_terbaca_utuh() -> None:
    milik = _kepemilikan()
    semua = [t for tabel in milik.values() for t in tabel]

    assert len(milik) == 11, f"modul pemilik tabel di spec/06: {sorted(milik)}"
    assert len(semua) == 23, f"tabel V0 di tabel kepemilikan spec/06: {len(semua)}"
    assert len(set(semua)) == 23, "satu tabel dimiliki lebih dari satu modul"


def test_sql_tiap_modul_hanya_menyebut_tabel_miliknya() -> None:
    milik = _kepemilikan()
    semua_tabel = set().union(*milik.values())
    pelanggaran: list[str] = []
    rujukan_terbaca = 0

    for berkas in sorted(MODUL.glob("*/**/*.py")):
        modul = berkas.relative_to(MODUL).parts[0]
        teks = berkas.read_text(encoding="utf-8")
        for posisi, tabel in tabel_disebut(teks):
            if tabel not in semua_tabel:
                continue  # kata SQL biasa, alias, atau fungsi — bukan tabel V0
            rujukan_terbaca += 1
            if tabel not in milik.get(modul, set()):
                baris = teks[:posisi].count("\n") + 1
                pelanggaran.append(
                    f"{berkas.relative_to(AKAR)}:{baris} — `{modul}` menyebut `{tabel}`"
                )

    assert rujukan_terbaca > 0, "tidak satu pun rujukan tabel terbaca — pemindai buta?"
    assert not pelanggaran, (
        "SQL menyentuh tabel milik modul lain (spec/06 aturan 5) — lewat __init__.py "
        "pemiliknya:\n" + "\n".join(pelanggaran)
    )
