"""Pengenal niat — spec/07 4.1: rute sebuah pesan SEBELUM model mana pun dipanggil.

Naskah 5 §22: *Request → **Classifier** → Simple · Reasoning*. Pengenal V0
berbentuk aturan, bukan model — memanggil model untuk memutuskan apakah perlu
model menggagalkan tujuannya (biaya & latensi, naskah 4 §48).

* **`deterministic`** — perintah berbentuk tetap yang cukup dijalankan layanan
  biasa: *“catat mood 3 cemas”* adalah `INSERT` (naskah 5 §22), dan gerbang model
  tidak pernah disentuh.
* **`reasoning`** — permintaan analisis: pola, kenapa, evaluasi, rencana, atau
  pesan panjang.
* **`simple`** — selainnya.

🔧 **Sejak 4.6 niat juga memilih AGENT** yang dipanggil `orchestrator-agent`, dengan
aturan yang sama ketatnya — perintah yang BERTINDAK hanya bila diawali kata
perintahnya:

* **`tandai_habit`** — *“tandai lari pagi selesai”* · *“centang meditasi”* ·
  *“lewati lari hari ini”* → `habit-agent` (tulisan R2, ditanya gerbang);
* **`ingat`** — *“ingat bahwa aku alergi kacang”* → `memory-agent`. *“Ingatkan …”*
  (minta diingatkan, pengingat) BUKAN permintaan mengingat;
* **`cari_ingatan`** — *“apa yang kamu ingat tentang tidurku?”* → `memory-agent`;
* **`tanya`** — selainnya → `coach-agent`.

Dua salah rute tidak sama mahalnya. Pertanyaan analisis yang jatuh ke `simple`
hanya dijawab lebih dangkal; teks yang BUKAN perintah tetapi dijalankan
`deterministic` bertindak atas sesuatu yang tidak dimaksudkan pengguna. Karena
itu `deterministic` hanya untuk perintah yang **diawali** kata perintahnya dan
**valensinya utuh** terbaca — *“aku mau catat mood nanti”* bukan perintah, dan
*“catat mood 3.5”* dijawab dengan cara mengisinya, bukan ditebak. Kata sesudah
valensi tidak ditebak artinya: satu kata menjadi label, sisanya disimpan apa
adanya sebagai catatan pengguna sendiri. 🔧 Kata perintahnya WAJIB (E-198): *“mood 3
hari lalu buruk sekali”* MENCERITAKAN mood lampau — dulu kata perintahnya opsional,
dan kalimat itu tercatat sebagai mood baru saat ini.

🔧 **Pola perintah dibaca per KATA** (E-197): spasi dirapatkan dan tanda baca penutup
dibuang sebelum pola mana pun melihat teksnya, dan ekor pola hanya kata utuh. Satu
pesan sah 4.000 karakter (*“tandai x”*, 3.991 spasi, *“y”*) dulu menelusur mundur
O(n³) — 75 detik per panggilan, di event loop, tiga kali per pesan: seluruh proses api
membeku untuk semua pengguna. Catatan mood tetap dibaca dari teks ASLINYA — itu
tulisan pengguna, bukan perintah.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from hvx.modules import platform

JenisNiat = Literal[
    "catat_mood", "catat_mood_salah", "tandai_habit", "ingat", "cari_ingatan", "tanya"
]
StatusHabit = Literal["done", "skipped"]

# Pesan sepanjang ini (kata) diperlakukan sebagai permintaan analisis.
KATA_PANJANG = 40
# Batas `mood_entries.label` (spec/04 `POST /moods`). Catatan TIDAK dipotong di
# sini: yang terlalu panjang ditolak skema `POST /moods` yang sama, lalu dijawab.
LABEL_MAKS = 50

_PEMISAH = r"[,;:\-–—]"
# "catat mood 3" · "catat mood saya: 2 cemas" · "log mood 4/5 lega, habis lari" — kata
# perintah WAJIB: "mood 3 hari lalu buruk" bercerita, bukan memerintah (E-198).
_AWALAN_MOOD = re.compile(
    r"^\s*(?:catat|log|simpan|isi)\s+mood\b(?:\s+(?:saya|aku|ku|hari\s+ini))?"
    rf"\s*{_PEMISAH}?\s*",
    re.IGNORECASE,
)
# Valensi 1–5 yang UTUH: "3" · "3/5" — bukan "34", "3.5", atau "3x".
_VALENSI = re.compile(rf"^(?P<v>[1-5])(?:\s*/\s*5)?(?=\s|{_PEMISAH}|$)")
_LABEL = re.compile(
    rf"^(?P<label>[^\W\d_]{{1,{LABEL_MAKS}}})(?:\s*{_PEMISAH}\s*(?P<sisa>.*))?$", re.DOTALL
)
_SESUDAH_PEMISAH = re.compile(rf"^{_PEMISAH}\s*(?P<sisa>.*)$", re.DOTALL)

# "tandai lari pagi selesai" · "centang meditasi" · "lewati lari hari ini" · "tolong tandai …"
# Dicocokkan pada `_perintah(teks)`: satu spasi antarkata, tanpa tanda baca penutup — ekor
# pola hanya kata utuh, jadi `.+?` malas tidak punya deretan untuk ditelusur mundur (E-197).
_TANDAI = re.compile(
    r"^(?:tolong )?(?P<kata>tandai|centang|selesaikan|lewati|lewatkan|skip) "
    r"(?:habit )?(?P<judul>.+?)"
    r"(?: (?P<akhir>selesai|sudah selesai|sudah|dilewati|terlewat))?"
    r"(?: hari ini)?$",
    re.IGNORECASE,
)
_LEWATI = frozenset({"lewati", "lewatkan", "skip", "dilewati", "terlewat"})
# "ingat bahwa …" · "tolong ingat, …" · "ingatlah: …" — BUKAN "ingatkan" (pengingat).
_INGAT = re.compile(
    r"^(?:tolong )?ingat(?:lah)?(?: (?:ya|bahwa|kalau))? ?[,:]? (?P<isi>\S.*)$",
    re.IGNORECASE,
)
_CARI_INGATAN = re.compile(
    r"^apa (?:saja )?yang (?:kamu|kau|anda) (?:ingat|tahu)(?: tentang (?P<kueri>.+))?$",
    re.IGNORECASE,
)
_PENUTUP = " .!?"

_ANALISIS = re.compile(
    r"\b(?:analisis|analisa|menganalisis|pola|tren|kenapa|mengapa|evaluasi|refleksi|"
    r"rencana|strategi|bandingkan|rangkum|ringkas(?:kan)?\s+minggu|minggu\s+ini|bulan\s+ini|"
    r"bagaimana\s+(?:cara|supaya|agar)|why|analy[sz]e|analysis|pattern|trend|plan|"
    r"reflect|compare|summari[sz]e)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class MoodDiminta:
    valensi: int
    label: str | None
    catatan: str | None


@dataclass(frozen=True)
class Niat:
    rute: platform.Rute
    jenis: JenisNiat
    mood: MoodDiminta | None = None
    # tandai_habit: judul yang disebut · ingat: isi yang diminta diingat · cari_ingatan: kuerinya
    sasaran: str | None = None
    status: StatusHabit | None = None  # tandai_habit


def _urai_mood(sisa: str) -> MoodDiminta | None:
    valensi = _VALENSI.match(sisa)
    if not valensi:
        return None
    lanjut = sisa[valensi.end() :].strip()
    label: str | None = None
    catatan: str | None = lanjut or None
    satu_kata = _LABEL.match(lanjut)
    if satu_kata and (satu_kata["sisa"] is not None or not re.search(r"\s", lanjut)):
        label, catatan = satu_kata["label"], (satu_kata["sisa"] or "").strip() or None
    elif (pemisah := _SESUDAH_PEMISAH.match(lanjut)) is not None:
        catatan = pemisah["sisa"].strip() or None
    return MoodDiminta(int(valensi["v"]), label, catatan)


def _perintah(teks: str) -> str:
    """Teks yang dilihat pola PERINTAH: satu spasi antarkata, tanpa tanda baca penutup.

    Dirapatkan dengan `split`/`rstrip` — linear, tanpa regex — sebelum pola mana pun
    melihatnya: deretan spasi dan titik yang dulu membuat `_TANDAI` menelusur mundur
    kubik (E-197) tidak pernah sampai ke sana.
    """
    return " ".join(teks.split()).rstrip(_PENUTUP)


def kenali(teks: str) -> Niat:
    """Niat satu pesan pengguna — murni, tanpa basis data dan tanpa model."""
    awalan = _AWALAN_MOOD.match(teks)
    if awalan:
        mood = _urai_mood(teks[awalan.end() :])
        if mood is not None:
            return Niat("deterministic", "catat_mood", mood)
        # Perintah yang jelas, angkanya tidak: dijawab dengan cara mengisinya — bukan
        # ditebak, dan bukan dilempar ke model.
        return Niat("deterministic", "catat_mood_salah")
    perintah = _perintah(teks)
    if tandai := _TANDAI.match(perintah):
        lewati = tandai["kata"].lower() in _LEWATI or (tandai["akhir"] or "").lower() in _LEWATI
        status: StatusHabit = "skipped" if lewati else "done"
        return Niat("simple", "tandai_habit", sasaran=tandai["judul"], status=status)
    if ingat := _INGAT.match(perintah):
        return Niat("simple", "ingat", sasaran=ingat["isi"])
    if cari := _CARI_INGATAN.match(perintah):
        return Niat("simple", "cari_ingatan", sasaran=cari["kueri"] or None)
    if _ANALISIS.search(perintah) or len(perintah.split()) >= KATA_PANJANG:
        return Niat("reasoning", "tanya")
    return Niat("simple", "tanya")
