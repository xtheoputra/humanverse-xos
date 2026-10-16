"""Recommendation engine — spec/07 5.5: *“skor 0–1, scoring_version, rationale terisi”*.

§11 Recommendation Engine (naskah, docs/87): *“semua recommendation harus melewati
scoring”*. Skornya **rata-rata komponen dengan bobot sama** (docs/87: lima komponen
contoh dirata-rata) — `score_breakdown` menyimpan tiap komponen apa adanya plus
`"weights":"equal"`, sehingga rumusnya bisa dibaca dan diuji. `scoring_version`
membuat rumus boleh berganti tanpa migrasi (spec/01 §7).

🔑 **Skor dari DATA, bukan karangan agent** (K-36): `recommendation.create` tetap
jalur coach yang memasok `confidence`+`rationale`-nya sendiri (`rekomendasi.py`);
mesin ini sistem — `score` dihitung dari sinyal V0, `confidence` dibiarkan kosong.

🔑 **Confidence Layer (5.4):** tanpa satu pun komponen (habit baru tanpa riwayat DAN
tanpa check-in) tidak ada skor — tidak ada rekomendasi. Nol bukti → sistem diam di
sini, dan bertanya di tempat yang memang bertanya (coach). Lihat [`keyakinan`].

Dipicu dua event (spec/03 *Recommendation trigger*, boleh gagal lalu diulang):

* **`habit.skipped`** → satu rekomendasi *kembali ke habit itu, versi lebih ringan*
  untuk habit yang dilewati. Idempoten per (habit, tanggal): id deterministik +
  `ON CONFLICT DO NOTHING`, jadi event yang disalurkan ulang tidak menumpuk baris,
  dan status yang sudah diubah pengguna tidak pernah tertimpa.
* **`checkin.logged`** → **menyegarkan** komponen `context` (energi) rekomendasi
  pending hari itu dengan energi yang baru dilaporkan, lalu menghitung ulang skornya.
  Konvergen seperti 5.1–5.3: energi terakhir yang menang, bukan urutan tibanya.

`intelligence` ada di atas `habits`/`checkins`/`profile`/`events` (M-1), jadi membaca
sinyalnya lewat pintu keluar masing-masing — di transaksi event yang sama.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import checkins, events, habits, profile

from . import repository
from .keyakinan import cukup_untuk_menyatakan

_NS = uuid.UUID("5e1c0a2b-4d6f-5a80-9c1b-2d3e4f5a6b70")
SKOR_VERSI = "v1"
DOMAIN_HABIT = "habit"
SUBJEK_HABIT = "habit"
ZONA_BAWAAN = "UTC"
SKALA_MIN, SKALA_MAKS = 1, 5

# spec/03 *Recommendation trigger* — dua event ini memicu mesin (boleh gagal).
JENIS_REKOMENDASI: frozenset[str] = frozenset({"habit.skipped", "checkin.logged"})

type Komponen = dict[str, float]


@dataclass(frozen=True)
class Skor:
    score: Decimal
    breakdown: dict[str, float | str]


def _norm(nilai: int) -> float:
    """Skala laporan 1–5 → 0–1 (sejalan `keadaan._normalisasi_skala`, 5.3)."""
    return round((nilai - SKALA_MIN) / (SKALA_MAKS - SKALA_MIN), 3)


def nilai_rekomendasi(komponen: Komponen) -> Skor | None:
    """Skor = rata-rata komponen, bobot sama (docs/87). `breakdown` membawa tiap
    komponen + `"weights":"equal"` supaya rumusnya bisa dibaca.

    Tanpa komponen (nol bukti) → `None`: Confidence Layer (5.4) — sistem tidak
    menyekor sesuatu yang tak punya satu pun dasar."""
    if not cukup_untuk_menyatakan(len(komponen)):
        return None
    rata = sum(komponen.values()) / len(komponen)
    breakdown: dict[str, float | str] = {k: round(v, 3) for k, v in komponen.items()}
    breakdown["weights"] = "equal"
    return Skor(Decimal(str(round(rata, 3))), breakdown)


def _tier_ringan(habit: habits.Habit, energi: int | None) -> str | None:
    """Label tier yang disarankan untuk energi itu (K-23) — `None` bila habit tanpa tier."""
    idx = habits.tier_untuk_energi(len(habit.adaptive_tiers), energi)
    if idx is None:
        return None
    label = habit.adaptive_tiers[idx].get("label")
    return str(label) if isinstance(label, str) and label.strip() else None


async def _rekomendasi_habit(
    conn: AsyncConnection, user_id: UUID, habit_id: UUID, for_date: date
) -> None:
    """Rekomendasi *kembali ke habit ini* untuk satu habit yang dilewati pada `for_date`."""
    habit = await habits.habit_pada(conn, habit_id)
    if habit is None:  # habit dihapus — tak ada yang disarankan
        return
    zona = await profile.zona_waktu(conn, user_id) or ZONA_BAWAAN
    rentetan = await habits.rentetan_pada(conn, user_id, habit_id, zona)
    checkin = await checkins.checkin_pada(conn, user_id, for_date)
    energi = checkin.energy if checkin else None

    komponen: Komponen = {}
    if rentetan is not None and rentetan.completion_rate_30d is not None:
        komponen["history"] = round(rentetan.completion_rate_30d, 3)
    if energi is not None:
        komponen["context"] = _norm(energi)

    skor = nilai_rekomendasi(komponen)
    if skor is None:  # nol bukti → tidak menyarankan (Confidence Layer 5.4)
        return

    tier = _tier_ringan(habit, energi)
    dasar = "Melewatkan sesekali tidak mematahkan kebiasaan."
    body = (
        f'{dasar} Besok coba versi lebih ringan: "{tier}".'
        if tier
        else f"{dasar} Coba lagi besok dengan target yang pas."
    )
    rationale: list[str] = []
    if "history" in komponen:
        rationale.append(f"Penyelesaian 30 hari terakhir: {round(komponen['history'] * 100)}%.")
    if energi is not None:
        rationale.append(f"Energi {energi}/5 pada {for_date.isoformat()}.")
    rationale.append(f'"{habit.title}" dilewati hari itu.')

    await repository.sisip_mesin(
        conn,
        id_=uuid.uuid5(_NS, f"habit-reengage:{habit_id}:{for_date.isoformat()}"),
        user_id=user_id,
        domain=DOMAIN_HABIT,
        subject_type=SUBJEK_HABIT,
        subject_id=habit_id,
        title=f"Kembali ke “{habit.title}”",
        body=body,
        score=skor.score,
        scoring_version=SKOR_VERSI,
        score_breakdown=skor.breakdown,
        rationale=rationale,
        context_snapshot={"for_date": for_date.isoformat(), **komponen},
    )


async def _dari_habit_dilewati(conn: AsyncConnection, event: events.EventMasuk) -> None:
    habit_id = event.subject_id
    mentah = event.payload.get("for_date")
    if habit_id is None or mentah is None:
        return
    await _rekomendasi_habit(conn, event.user_id, habit_id, date.fromisoformat(str(mentah)))


async def _dari_checkin(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Energi baru dilaporkan → segarkan komponen `context` rekomendasi pending hari itu.

    Hanya menyentuh rekomendasi mesin yang MASIH `pending` (status yang sudah diubah
    pengguna tidak diganggu), dan hanya menghitung ulang — `history` yang tersimpan di
    `context_snapshot` dipertahankan, `context` diganti energi terbaru."""
    mentah = event.payload.get("for_date")
    if mentah is None:
        return
    for_date = date.fromisoformat(str(mentah))
    energi = event.payload.get("energy")
    for baris in await repository.pending_mesin(
        conn, event.user_id, SKOR_VERSI, for_date.isoformat()
    ):
        snap = dict(baris.context_snapshot)
        komponen: Komponen = {}
        if "history" in snap:
            komponen["history"] = float(snap["history"])
        if isinstance(energi, int):
            komponen["context"] = _norm(energi)
        skor = nilai_rekomendasi(komponen)
        if skor is None:  # tak mungkin bila history ada; jaga-jaga, biarkan apa adanya
            continue
        await repository.perbarui_skor(
            conn,
            baris.id,
            event.user_id,
            score=skor.score,
            score_breakdown=skor.breakdown,
            context_snapshot={"for_date": for_date.isoformat(), **komponen},
        )


_PEMICU = {
    "habit.skipped": _dari_habit_dilewati,
    "checkin.logged": _dari_checkin,
}


async def sarankan(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Penangan konsumen (spec/03 *Recommendation trigger*) — satu event → rekomendasinya.

    Berjalan di transaksi pemilik event (`KonsumenStream`): bacaan sinyal dan tulisan
    `recommendations` commit atau batal bersama."""
    pemicu = _PEMICU.get(event.event_type)
    if pemicu is not None:
        await pemicu(conn, event)
