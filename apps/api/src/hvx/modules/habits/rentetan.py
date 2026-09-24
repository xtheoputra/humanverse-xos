"""Rentetan & tingkat penyelesaian — spec/07 2.4.

Selesai bila: benar melintasi zona waktu; uji pengguna yang pindah negara.

Tiga hal yang membuatnya "benar melintasi zona waktu", dan masing-masing
menutup satu cara salah yang nyata:

1. **Dihitung dari `for_date`, tidak pernah dari `completed_at`.** `for_date`
   tanggal LOKAL saat habit dijalankan (spec/01): workout Senin pagi di
   Jakarta (06:30 WIB = 23:30 UTC hari Minggu) adalah Senin. Menurunkan tanggal
   dari cap waktu UTC memindahkannya ke Minggu; menurunkannya dengan zona
   profil SEKARANG menggeser seluruh riwayat setiap kali pengguna pindah negara.
2. **"Hari ini" menurut zona profil SAAT INI, dari jam basis data** — satu
   sumber waktu untuk semua instans (spec/07 1.5). Hari ini yang belum
   dijalankan tidak memutus rentetan: harinya belum berakhir.
3. **Tanggal sesudah "hari ini" tetap dihitung.** Perangkat yang sedang di
   zona lebih timur dari profilnya mencatat tanggal yang, menurut profil,
   baru besok — itu hari yang sudah terjadi bagi pemiliknya.

Satuan rentetan adalah **periode** habit (spec/01 `period`): hari, minggu ISO
(Senin–Minggu), atau bulan kalender. Sebuah periode **terpenuhi** bila jumlah
tanggal `done`/`partial` di dalamnya ≥ `target_count`.

* `partial` dan tier yang lebih ringan **memenuhi** — *Consistency >
  Perfection* (naskah 4 §34).
* `skipped` **netral**: tidak menambah, tidak memutus (*“Bukan menyalahkan
  user”*, naskah 4 §33), dan tidak masuk penyebut tingkat penyelesaian. Netral
  PER KEJADIAN: tiap `skipped` memaafkan satu kali dari target periodenya —
  minggu bertarget 2 dengan satu `done` dan satu `skipped` dimaafkan, bukan
  gagal. 🔴 Versi pertama hanya menetralkan `skipped` pada habit harian; pada
  habit mingguan/bulanan ia diabaikan, dan minggu itu memutus rentetan
  (tinjauan kontrak Sprint 2, F7).
* Hari di luar `schedule.weekdays` bukan hari habit itu — dilewati.
* **Periode yang dimulai sebelum habit dibuat hanya dihitung bila terpenuhi**
  (spec/04: tingkat penyelesaian *“tidak lebih awal dari awal habit”*).
  Catatan mundur tetap dihargai; hari-hari sebelum habit ada tidak menjadi
  "gagal" di penyebut. 🔴 Versi pertama menghitungnya: habit yang dibuat hari
  ini dengan satu catatan sepuluh hari lalu bertingkat 0,1 (F8).

⚠️ Batas yang diakui: penyeberangan garis tanggal ke TIMUR melompati satu
tanggal kalender; rentetan harian putus di sana kecuali tanggal itu dicatat
(`for_date` boleh tanggal lampau — perangkat bisa mencatatnya). Riwayat
`paused` tidak disimpan (spec/01 tidak punya kolomnya), jadi masa jeda dihitung
seperti hari biasa.
"""

from __future__ import annotations

import calendar
from collections import Counter
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

MEMENUHI = frozenset({"done", "partial"})
JENDELA_HARI = 30
# Riwayat yang ditelusuri paling jauh ~10 tahun ke belakang: `for_date` boleh
# tanggal lampau berapa pun, dan satu tanggal tahun 0001 tidak boleh membuat
# satu permintaan menelusuri 740 ribu hari.
RIWAYAT_MAKS_HARI = 3660

Keadaan = Literal["penuh", "dimaafkan", "kosong", "belum", "luar"]


@dataclass(frozen=True)
class Rentetan:
    current: int
    longest: int
    completion_rate_30d: float | None


def awal_riwayat(hari_ini: date) -> date:
    """Tanggal paling awal yang bisa memengaruhi hasil — batas bawah kueri riwayat.

    Periode terpanjang sebulan: awal bulan dari `RIWAYAT_MAKS_HARI` lalu.
    """
    return awal_periode("month", hari_ini - timedelta(days=RIWAYAT_MAKS_HARI))


def awal_periode(period: str, d: date) -> date:
    if period == "day":
        return d
    if period == "week":
        return d - timedelta(days=d.weekday())  # Senin — minggu ISO
    if period == "month":
        return d.replace(day=1)
    raise ValueError(f"period tak dikenal: {period!r}")


def _berikut(period: str, awal: date) -> date:
    if period == "day":
        return awal + timedelta(days=1)
    if period == "week":
        return awal + timedelta(days=7)
    hari_terakhir = calendar.monthrange(awal.year, awal.month)[1]
    return awal.replace(day=hari_terakhir) + timedelta(days=1)


def hitung_rentetan(
    *,
    period: str,
    target_count: int,
    weekdays: Collection[int] | None,
    mulai: date,
    hari_ini: date,
    penyelesaian: Mapping[date, str],
) -> Rentetan:
    """`mulai` = tanggal lokal habit dibuat; `penyelesaian` = {for_date: status}."""
    if target_count < 1:
        raise ValueError("target_count wajib ≥ 1")
    terjadwal = frozenset(weekdays) if period == "day" and weekdays else None
    periode_kini = awal_periode(period, hari_ini)
    penuh_per_periode = Counter(
        awal_periode(period, d) for d, status in penyelesaian.items() if status in MEMENUHI
    )
    maaf_per_periode = Counter(
        awal_periode(period, d) for d, status in penyelesaian.items() if status == "skipped"
    )

    def keadaan(p: date) -> Keadaan:
        if period == "day":
            if terjadwal is not None and p.isoweekday() not in terjadwal:
                return "luar"
            status = penyelesaian.get(p)
            if status in MEMENUHI:
                return "penuh"
            if status == "skipped":
                return "dimaafkan"
        else:
            penuh = penuh_per_periode[p]
            if penuh >= target_count:
                return "penuh"
            if maaf_per_periode[p] and penuh + maaf_per_periode[p] >= target_count:
                return "dimaafkan"
        # Periode yang belum berakhir — hari ini, minggu ini, atau sesudahnya —
        # belum gagal; ia hanya belum terpenuhi.
        return "belum" if p >= periode_kini else "kosong"

    awal = max(min([mulai, *penyelesaian]), hari_ini - timedelta(days=RIWAYAT_MAKS_HARI))
    akhir = max([hari_ini, *penyelesaian])

    beruntun = terpanjang = 0
    p = awal_periode(period, awal)
    while p <= akhir:
        k = keadaan(p)
        if k == "penuh":
            beruntun += 1
            terpanjang = max(terpanjang, beruntun)
        elif k == "kosong":
            beruntun = 0
        p = _berikut(period, p)

    # Tingkat penyelesaian 30 hari: periode yang BERSINGGUNGAN dengan jendela.
    # Penyebutnya hanya periode yang sudah jatuh tempo (berakhir, atau sudah
    # terpenuhi) — `dimaafkan`, `luar`, dan yang `belum` tidak dihitung — dan
    # periode `kosong` hanya bila habit sudah ada sepanjang periode itu.
    dari = max(hari_ini - timedelta(days=JENDELA_HARI - 1), awal)
    terpenuhi = jatuh_tempo = 0
    p = awal_periode(period, dari)
    while p <= periode_kini:
        k = keadaan(p)
        if k == "penuh":
            terpenuhi += 1
            jatuh_tempo += 1
        elif k == "kosong" and p >= mulai:
            jatuh_tempo += 1
        p = _berikut(period, p)
    tingkat = round(terpenuhi / jatuh_tempo, 3) if jatuh_tempo else None

    return Rentetan(current=beruntun, longest=terpanjang, completion_rate_30d=tingkat)
