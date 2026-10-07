"""Tinjauan mingguan — spec/07 6.2: *menjawab 5 pertanyaan naskah 4 §31* (K-45).

*What went well? · What changed? · What failed? · Why? · What should change next week?*

Tiga hal yang sengaja TIDAK dilakukan, dan kenapa:

* **Tidak menjawab "Kenapa?" atas nama pengguna.** Data observasional tidak membuktikan
  sebab (naskah 4 §7; `pola.tanpa_klaim_kausal`) — yang bisa diberikan sistem hanya hal yang
  terjadi BERSAMAAN (energi di hari terpenuhi vs terlewat) dan alasan yang pengguna catat
  sendiri saat melewatkan habit. Pertanyaannya tetap pertanyaan: sikapnya selalu `ask`.
  Refleksi sendiri — inti siklus Gibbs (1988) dan *retrospective* tim (Derby & Larsen,
  2006) — adalah yang membuat tinjauan berguna; sistem menyiapkan bahannya.
* **Tidak mengarang sumbu yang tidak diukur.** §31 menyebut tujuh sumbu (Habits · Health ·
  Learning · Finance · Social · Career · Lifestyle); V0 mengukur habit dan sebagian
  kesehatan yang DILAPORKAN sendiri (energi, fokus, tidur, mood). Sisanya disebut
  `not_measured` — sama dengan dashboard 6.1 (A-19/B-38).
* **Tidak menyimpan apa pun.** Tinjauan dihitung saat dibaca dari data yang sudah ada:
  tak ada salinan baru tentang pengguna (minimisasi data, GDPR Art. 5(1)(c)), dan menghapus
  sumbernya di Privacy Center juga menghapus tinjauannya. Refleksi pengguna sendiri
  ditulis di jurnal — tempat yang sudah sensitif, privat, dan bisa dihapus.

Confidence Layer (5.4): butir hanya dinyatakan dengan bukti (`evidence_count` ≥ 1); tanpa
butir, pertanyaannya `ask` — sistem bertanya, tidak menebak. Saran minggu depan memakai
dua temuan riset perubahan perilaku yang paling kokoh: versi minimum di hari sulit (*Tiny
Habits*, Fogg 2019 — tier adaptif naskah 4 §34) dan rencana *jika–maka* (*implementation
intentions*, meta-analisis Gollwitzer & Sheeran 2006, d≈0,65).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from statistics import fmean
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import checkins, habits, platform, profile

VERSI = "tinjauan-mingguan@v1"
ZONA_BAWAAN = "UTC"
POLA_MINGGU = r"^[0-9]{4}-W(0[1-9]|[1-4][0-9]|5[0-3])$"

AMBANG_BAIK = 0.8  # bagian periode terpenuhi → "berjalan baik"
AMBANG_BELUM = 0.5  # di bawah ini → "belum berhasil"
AMBANG_BERUBAH_TINGKAT = 0.2  # perubahan tingkat penyelesaian antar-minggu
AMBANG_BERUBAH_SKALA = 0.5  # perubahan rata-rata skala 1–5 (atau jam tidur)
AMBANG_SELISIH_ENERGI = 1.0  # beda energi hari terpenuhi vs terlewat yang disebut
PERIODE_MIN_BANDING = 2  # periode terhitung minimal di KEDUA minggu sebelum dibandingkan
ALASAN_MAKS = 3
ALASAN_PANJANG = 80

_MEMENUHI = frozenset({"done", "partial"})
_SATUAN = {"day": "hari", "week": "minggu"}

TAK_DIUKUR: tuple[tuple[str, str], ...] = (
    ("learning", "Belajar"),
    ("finance", "Keuangan"),
    ("social", "Sosial"),
    ("career", "Karier"),
    ("lifestyle", "Gaya hidup"),
)

PERTANYAAN: tuple[tuple[str, str], ...] = (
    ("went_well", "Apa yang berjalan baik?"),
    ("changed", "Apa yang berubah?"),
    ("failed", "Apa yang belum berhasil?"),
    ("why", "Kenapa?"),
    ("change_next_week", "Apa yang perlu diubah minggu depan?"),
)

_AJAKAN = {
    "went_well": "Apa satu hal yang berjalan baik minggu ini, menurutmu?",
    "changed": "Apa yang terasa berbeda dibanding minggu lalu?",
    "failed": "Adakah yang belum berjalan seperti yang kamu mau? Bukan untuk menyalahkan diri.",
    "why": "Menurutmu, apa yang ada di baliknya? Yang di atas hanya hal yang terjadi bersamaan.",
    "change_next_week": "Tulis satu rencana jika–maka: “Jika …, maka aku …”.",
}


def awal_minggu(teks: str) -> date:
    """`2026-W40` → Senin minggu ISO itu. `ValueError` bila minggu itu tidak ada (W53)."""
    if not re.fullmatch(POLA_MINGGU, teks):
        raise ValueError("minggu wajib YYYY-Www")
    return date.fromisocalendar(int(teks[:4]), int(teks[6:]), 1)


def label_minggu(senin: date) -> str:
    tahun, minggu, _ = senin.isocalendar()
    return f"{tahun}-W{minggu:02d}"


def _angka(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


@dataclass(frozen=True)
class NilaiHabit:
    """Satu habit dalam satu minggu: periode terpenuhi, terlewat, dilewati sengaja."""

    habit: habits.HabitDalamRentang
    terpenuhi: int = 0
    terlewat: int = 0
    dimaafkan: int = 0
    berjalan: int = 0
    hari_terpenuhi: tuple[date, ...] = ()
    hari_terlewat: tuple[date, ...] = ()
    alasan: tuple[str, ...] = field(default=())

    @property
    def dihitung(self) -> int:
        return self.terpenuhi + self.terlewat

    @property
    def tingkat(self) -> float | None:
        return self.terpenuhi / self.dihitung if self.dihitung else None


def nilai_habit(h: habits.HabitDalamRentang, senin: date, hari_ini: date) -> NilaiHabit | None:
    """Nilai mingguan satu habit — aturan rentetan 2.4: `partial` memenuhi, `skipped`
    netral (dimaafkan, bukan gagal), hari di luar jadwal dan sebelum habit ada tidak
    dihitung, periode yang belum berakhir belum gagal. Habit bulanan tidak dinilai per
    minggu (`None`): sebulan tidak bisa dihakimi dari seminggunya."""
    minggu = [senin + timedelta(days=i) for i in range(7)]
    alasan = tuple(
        (catatan or "").strip()[:ALASAN_PANJANG]
        for d, (status, catatan) in sorted(h.catatan.items())
        if senin <= d <= minggu[-1] and status == "skipped" and (catatan or "").strip()
    )
    if h.period == "day":
        penuh: list[date] = []
        lewat: list[date] = []
        maaf = jalan = 0
        for d in minggu:
            if d < h.mulai or (h.weekdays and d.isoweekday() not in h.weekdays):
                continue
            status = h.catatan.get(d, ("", None))[0]
            if status in _MEMENUHI:
                penuh.append(d)
            elif status == "skipped":
                maaf += 1
            elif d < hari_ini:
                lewat.append(d)
            else:
                jalan += 1
        return NilaiHabit(
            h, len(penuh), len(lewat), maaf, jalan, tuple(penuh), tuple(lewat), alasan
        )
    if h.period == "week":
        if h.mulai > minggu[-1]:
            return NilaiHabit(h)
        tanggal = [d for d in minggu if d in h.catatan]
        penuh = [d for d in tanggal if h.catatan[d][0] in _MEMENUHI]
        maaf_n = sum(1 for d in tanggal if h.catatan[d][0] == "skipped")
        if len(penuh) >= h.target_count:
            return NilaiHabit(h, terpenuhi=1, hari_terpenuhi=tuple(penuh), alasan=alasan)
        if maaf_n and len(penuh) + maaf_n >= h.target_count:
            return NilaiHabit(h, dimaafkan=1, hari_terpenuhi=tuple(penuh), alasan=alasan)
        if minggu[-1] < hari_ini:
            return NilaiHabit(h, terlewat=1, hari_terpenuhi=tuple(penuh), alasan=alasan)
        return NilaiHabit(h, berjalan=1, hari_terpenuhi=tuple(penuh), alasan=alasan)
    return None


@dataclass(frozen=True)
class Kesehatan:
    """Rata-rata yang dilaporkan sendiri dalam seminggu — `None` bila tak ada laporan."""

    energi: tuple[float | None, int]
    fokus: tuple[float | None, int]
    tidur: tuple[float | None, int]
    mood: tuple[float | None, int]


def _rata(nilai: Sequence[float]) -> tuple[float | None, int]:
    return (round(fmean(nilai), 2), len(nilai)) if nilai else (None, 0)


def kesehatan(
    catatan: Sequence[checkins.Checkin], mood: Sequence[tuple[date, int]], senin: date
) -> Kesehatan:
    akhir = senin + timedelta(days=6)
    di = [c for c in catatan if senin <= c.for_date <= akhir]
    return Kesehatan(
        energi=_rata([c.energy for c in di if c.energy is not None]),
        fokus=_rata([c.focus for c in di if c.focus is not None]),
        tidur=_rata([float(c.sleep_hours) for c in di if c.sleep_hours is not None]),
        mood=_rata([float(v) for d, v in mood if senin <= d <= akhir]),
    )


_SUMBU_KESEHATAN = (
    ("energy", "Energi", "energi", "1-5"),
    ("focus", "Fokus", "fokus", "1-5"),
    ("sleep", "Tidur", "tidur", "jam"),
    ("mood", "Mood", "mood", "1-5"),
)


def _butir(teks: str, bukti: int) -> dict[str, Any]:
    return {"text": teks, "evidence_count": bukti}


def susun_tinjauan(
    senin: date,
    hari_ini: date,
    habit_rentang: Sequence[habits.HabitDalamRentang],
    catatan: Sequence[checkins.Checkin],
    mood: Sequence[tuple[date, int]],
) -> dict[str, Any]:
    """Tinjauan minggu `senin` dari data dua minggu (minggu itu dan sebelumnya). Murni."""
    lalu = senin - timedelta(days=7)
    kini = {h.id: n for h in habit_rentang if (n := nilai_habit(h, senin, hari_ini))}
    dulu = {h.id: n for h in habit_rentang if (n := nilai_habit(h, lalu, hari_ini))}
    sehat, sehat_lalu = kesehatan(catatan, mood, senin), kesehatan(catatan, mood, lalu)
    energi_hari = {c.for_date: c.energy for c in catatan if c.energy is not None}

    # ── sumbu ──
    def _tingkat(nilai: dict[UUID, NilaiHabit]) -> tuple[float | None, int, int, int]:
        t = sum(n.terpenuhi for n in nilai.values())
        lw = sum(n.terlewat for n in nilai.values())
        m = sum(n.dimaafkan for n in nilai.values())
        return ((round(t / (t + lw), 3) if t + lw else None), t, lw, m)

    tk, t, lw, m = _tingkat(kini)
    tk_lalu = _tingkat(dulu)[0]
    sumbu: list[dict[str, Any]] = []
    if tk is not None:
        sumbu.append(
            {
                "key": "habits",
                "label": "Habit",
                "value": tk,
                "previous": tk_lalu,
                "unit": "0-1",
                "evidence_count": t + lw + m,
                "why": f"{t} dari {t + lw} periode terjadwal terpenuhi; {m} dilewati dengan "
                "sengaja dan tidak dihitung gagal.",
            }
        )
    for kunci, label, kata, satuan in _SUMBU_KESEHATAN:
        (nilai, n), (lama, _) = getattr(sehat, kata), getattr(sehat_lalu, kata)
        if nilai is None:
            continue
        sumbu.append(
            {
                "key": kunci,
                "label": label,
                "value": nilai,
                "previous": lama,
                "unit": satuan,
                "evidence_count": n,
                "why": f"Rata-rata {n} laporan {kata} yang kamu isi sendiri minggu ini.",
            }
        )

    # ── lima pertanyaan ──
    baik: list[dict[str, Any]] = []
    berubah: list[dict[str, Any]] = []
    belum: list[dict[str, Any]] = []
    kenapa: list[dict[str, Any]] = []
    ubah: list[dict[str, Any]] = []
    for hid, n in kini.items():
        judul, satuan = n.habit.title, _SATUAN.get(n.habit.period, "periode")
        if n.tingkat is not None and n.tingkat >= AMBANG_BAIK and n.terpenuhi:
            baik.append(
                _butir(f"“{judul}” terpenuhi {n.terpenuhi} dari {n.dihitung} {satuan}.", n.dihitung)
            )
        if n.tingkat is not None and n.tingkat < AMBANG_BELUM and n.terlewat:
            belum.append(
                _butir(
                    f"“{judul}” belum terpenuhi di {n.terlewat} dari {n.dihitung} {satuan}.",
                    n.dihitung,
                )
            )
        lama = dulu.get(hid)
        if (
            lama is not None
            and lama.tingkat is not None
            and n.tingkat is not None
            and min(lama.dihitung, n.dihitung) >= PERIODE_MIN_BANDING
            and abs(n.tingkat - lama.tingkat) >= AMBANG_BERUBAH_TINGKAT
        ):
            berubah.append(
                _butir(
                    f"“{judul}”: {round(lama.tingkat * 100)}% → {round(n.tingkat * 100)}% "
                    "periode terpenuhi.",
                    lama.dihitung + n.dihitung,
                )
            )
        if senin <= n.habit.mulai <= senin + timedelta(days=6):
            berubah.append(_butir(f"Habit baru dimulai: “{judul}”.", 1))
        if n.alasan:
            kutip = ", ".join(f"“{a}”" for a in n.alasan[:ALASAN_MAKS])
            kenapa.append(
                _butir(f"Alasan yang kamu catat saat melewatkan “{judul}”: {kutip}.", len(n.alasan))
            )
        e_penuh = [energi_hari[d] for d in n.hari_terpenuhi if d in energi_hari]
        e_lewat = [energi_hari[d] for d in n.hari_terlewat if d in energi_hari]
        rendah: float | None = None
        if min(len(e_penuh), len(e_lewat)) >= PERIODE_MIN_BANDING:
            a, b = fmean(e_penuh), fmean(e_lewat)
            if abs(a - b) >= AMBANG_SELISIH_ENERGI:
                kenapa.append(
                    _butir(
                        f"Di hari “{judul}” terpenuhi, energimu rata-rata {_angka(a)}; di hari "
                        f"terlewat, {_angka(b)}.",
                        len(e_penuh) + len(e_lewat),
                    )
                )
                rendah = b if b < a else None
        if n.tingkat is not None and n.tingkat < AMBANG_BELUM and n.terlewat:
            if rendah is not None and n.habit.adaptive_tiers:
                ubah.append(
                    _butir(
                        f"Untuk “{judul}”, siapkan versi ringan “{n.habit.adaptive_tiers[-1]}” "
                        "di hari energimu rendah.",
                        n.dihitung,
                    )
                )
            elif n.terpenuhi == 0 and n.terlewat >= 3:
                ubah.append(
                    _butir(
                        f"“{judul}” belum sekali pun terpenuhi minggu ini — coba target yang "
                        "lebih kecil, atau jadwal yang lain.",
                        n.dihitung,
                    )
                )
    for kunci, _label, kata, _satuan in _SUMBU_KESEHATAN:
        (nilai, n), (lama, n_lama) = getattr(sehat, kata), getattr(sehat_lalu, kata)
        if nilai is None or lama is None or abs(nilai - lama) < AMBANG_BERUBAH_SKALA:
            continue
        arah = "naik" if nilai > lama else "turun"
        teks = f"Rata-rata {kata} {arah} dari {_angka(lama)} ke {_angka(nilai)}."
        berubah.append(_butir(teks, n + n_lama))
        if nilai > lama and kunci != "sleep":
            baik.append(_butir(teks, n + n_lama))

    butir = {"went_well": baik, "changed": berubah, "failed": belum, "why": kenapa}
    butir["change_next_week"] = ubah
    akhir = senin + timedelta(days=6)
    return {
        "week": label_minggu(senin),
        "start": senin,
        "end": akhir,
        "complete": akhir < hari_ini,
        "axes": sumbu,
        "not_measured": [{"key": k, "label": v} for k, v in TAK_DIUKUR],
        "questions": [
            {
                "key": kunci,
                "question": tanya,
                # "Kenapa?" tidak pernah dijawab sistem — hanya bahan untuk pemiliknya.
                "stance": "state" if butir[kunci] and kunci != "why" else "ask",
                "items": butir[kunci],
                "prompt": _AJAKAN[kunci],
            }
            for kunci, tanya in PERTANYAAN
        ],
        "review_version": VERSI,
    }


async def tinjauan_mingguan(
    engine: AsyncEngine, user_id: UUID, minggu: str | None
) -> dict[str, Any]:
    """`GET /reviews/weekly` — minggu ISO di zona profil; bawaan: minggu yang sedang berjalan."""
    async with platform.transaksi_pengguna(engine, user_id, satu_potret=True) as conn:
        zona = await profile.zona_waktu(conn, user_id) or ZONA_BAWAAN
        hari_ini = await platform.hari_ini_di(conn, zona)
        if minggu is None:
            senin = hari_ini - timedelta(days=hari_ini.weekday())
        else:
            try:
                senin = awal_minggu(minggu)
            except ValueError:
                raise platform.GalatApi(
                    400, "invalid_week", "Minggu wajib berbentuk YYYY-Www yang ada."
                ) from None
            if senin > hari_ini:
                raise platform.GalatApi(422, "week_in_future", "Minggu itu belum dimulai.")
        lalu, akhir = senin - timedelta(days=7), senin + timedelta(days=6)
        daftar_habit = await habits.habit_rentang(conn, user_id, lalu, akhir, zona)
        catatan = await checkins.checkin_rentang(conn, user_id, lalu, akhir)
        mood = await checkins.mood_rentang(conn, user_id, lalu, akhir, zona)
    tinjauan = susun_tinjauan(senin, hari_ini, daftar_habit, catatan, mood)
    tinjauan["timezone"] = zona
    return tinjauan
