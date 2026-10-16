"""Human State harian — spec/07 5.3: *“tiap metrik punya value, confidence, evidence_count”*.

Dari check-in harian (energi, fokus), `intelligence` menghitung metrik keadaan
pengguna dan menuliskannya ke `human_states` (tabel milik `profile`) lewat pintu
keluar `profile.simpan_human_state`. `intelligence` ada di atas `profile`/`checkins`
(M-1), jadi memanggilnya langsung.

Bentuk metrik (spec/01 §6): `{value, confidence, evidence_count}`. V0:

* **value** — skala laporan 1–5 dinormalkan ke 0–1 (`(x-1)/4`), seragam dengan
  skor 0–1 di lapisan rekomendasi (5.5) dan issue #2 (`metrics jsonb` menampung
  model mana pun; yang menetap dipromosikan jadi kolom tanpa membuang data lama).
* **confidence** — keadaan ini LAPORAN pengguna sendiri, bukan tebakan: 1,0,
  sejalan `memory.KEYAKINAN_LAPORAN_SENDIRI`. Yang menjadi hati-hati justru
  `evidence_count`.
* **evidence_count** — satu check-in = satu bukti untuk HARI itu. Human State
  V0 adalah keadaan per-hari (for_date lokal perangkat, bukan zona profil —
  K-35), bukan tren berjendela; menyatukan beberapa hari jadi tren, dan keyakinan
  yang tumbuh dengan bukti, adalah pekerjaan sesudah V0.

Ambang kapan evidence cukup untuk MENYATAKAN vs BERTANYA adalah milik pemilik
(#34, tugas 5.4) — di sini hanya aturan keras: tanpa metrik (check-in tanpa
energi/fokus) tidak ada baris yang dinyatakan.

Konvergen seperti 5.1/5.2: dihitung ulang dari check-in OTORITATIF (bukan payload
event yang bisa basi), dan upsert per (pengguna, for_date, versi) — penyaluran
ulang menyatukan ke keadaan yang sama.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import checkins, events, profile

MODEL = "human-state@v1"
SKALA_MIN, SKALA_MAKS = 1, 5
# Laporan pengguna sendiri — bukan tebakan (sejalan memory.KEYAKINAN_LAPORAN_SENDIRI).
_KEYAKINAN_LAPORAN = 1.0

JENIS_KEADAAN: frozenset[str] = frozenset({"checkin.logged"})

type Metrik = dict[str, float | int]


def _normalisasi_skala(nilai: int) -> float:
    """Skala laporan 1–5 → 0–1."""
    return round((nilai - SKALA_MIN) / (SKALA_MAKS - SKALA_MIN), 3)


def _metrik(value: float, *, evidence_count: int) -> Metrik:
    return {"value": value, "confidence": _KEYAKINAN_LAPORAN, "evidence_count": evidence_count}


def metrik_harian(*, energy: int | None, focus: int | None) -> dict[str, Metrik]:
    """Metrik dari satu check-in — hanya medan yang dilaporkan (yang `None` dilewati)."""
    metrik: dict[str, Metrik] = {}
    if energy is not None:
        metrik["energy"] = _metrik(_normalisasi_skala(energy), evidence_count=1)
    if focus is not None:
        metrik["focus"] = _metrik(_normalisasi_skala(focus), evidence_count=1)
    return metrik


async def hitung_human_state(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Penangan konsumen `checkin.logged` — hitung `human_states` tanggal check-in itu."""
    mentah = event.payload.get("for_date")
    if mentah is None:
        return
    for_date = date.fromisoformat(str(mentah))
    checkin = await checkins.checkin_pada(conn, event.user_id, for_date)
    metrik = metrik_harian(energy=checkin.energy, focus=checkin.focus) if checkin else {}
    if not metrik:
        # Check-in hanya tidur/kosong — tidak ada yang dinyatakan, JUGA bila hari itu pernah
        # berbaris: `PUT /checkins` MENGGANTI (spec/04). 🔴 Versi pertama hanya `return`,
        # dan energi yang sudah diganti pemiliknya tetap dinyatakan di `human_states` dan
        # dashboard (tinjauan kontrak S5–6, K1).
        await profile.hapus_human_state(conn, event.user_id, for_date=for_date, model_version=MODEL)
        return
    await profile.simpan_human_state(
        conn, event.user_id, for_date=for_date, metrics=metrik, model_version=MODEL
    )
