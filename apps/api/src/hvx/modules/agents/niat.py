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

Dua salah rute tidak sama mahalnya. Pertanyaan analisis yang jatuh ke `simple`
hanya dijawab lebih dangkal; teks yang BUKAN perintah tetapi dijalankan
`deterministic` bertindak atas sesuatu yang tidak dimaksudkan pengguna. Karena
itu `deterministic` hanya untuk perintah yang **diawali** kata perintahnya dan
**valensinya utuh** terbaca — *“aku mau catat mood nanti”* bukan perintah, dan
*“catat mood 3.5”* dijawab dengan cara mengisinya, bukan ditebak. Kata sesudah
valensi tidak ditebak artinya: satu kata menjadi label, sisanya disimpan apa
adanya sebagai catatan pengguna sendiri.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from hvx.modules import platform

JenisNiat = Literal["catat_mood", "catat_mood_salah", "tanya"]

# Pesan sepanjang ini (kata) diperlakukan sebagai permintaan analisis.
KATA_PANJANG = 40
# Batas `mood_entries.label` (spec/04 `POST /moods`). Catatan TIDAK dipotong di
# sini: yang terlalu panjang ditolak skema `POST /moods` yang sama, lalu dijawab.
LABEL_MAKS = 50

_PEMISAH = r"[,;:\-–—]"
# "catat mood 3" · "catat mood saya: 2 cemas" · "log mood 4/5 lega, habis lari" · "mood 5"
_AWALAN_MOOD = re.compile(
    r"^\s*(?:(?:catat|log|simpan|isi)\s+)?mood(?:\s+(?:saya|aku|ku|hari\s+ini))?"
    rf"\s*{_PEMISAH}?\s*",
    re.IGNORECASE,
)
_PERINTAH_MOOD = re.compile(r"^\s*(?:catat|log|simpan|isi)\s+mood\b", re.IGNORECASE)
# Valensi 1–5 yang UTUH: "3" · "3/5" — bukan "34", "3.5", atau "3x".
_VALENSI = re.compile(rf"^(?P<v>[1-5])(?:\s*/\s*5)?(?=\s|{_PEMISAH}|$)")
_LABEL = re.compile(
    rf"^(?P<label>[^\W\d_]{{1,{LABEL_MAKS}}})(?:\s*{_PEMISAH}\s*(?P<sisa>.*))?$", re.DOTALL
)
_SESUDAH_PEMISAH = re.compile(rf"^{_PEMISAH}\s*(?P<sisa>.*)$", re.DOTALL)

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


def kenali(teks: str) -> Niat:
    """Niat satu pesan pengguna — murni, tanpa basis data dan tanpa model."""
    awalan = _AWALAN_MOOD.match(teks)
    if awalan:
        mood = _urai_mood(teks[awalan.end() :])
        if mood is not None:
            return Niat("deterministic", "catat_mood", mood)
        if _PERINTAH_MOOD.match(teks):
            # Perintah yang jelas, angkanya tidak: dijawab dengan cara mengisinya —
            # bukan ditebak, dan bukan dilempar ke model.
            return Niat("deterministic", "catat_mood_salah")
    if _ANALISIS.search(teks) or len(teks.split()) >= KATA_PANJANG:
        return Niat("reasoning", "tanya")
    return Niat("simple", "tanya")
