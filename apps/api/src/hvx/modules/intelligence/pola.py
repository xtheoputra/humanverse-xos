"""Deteksi pola perilaku — spec/07 5.2: *“keluarannya asosiatif, bukan kausal”*.

Behavioral Pattern Mining (naskah 4 §6): dari penyelesaian habit, tiga pola V0 —
**hari-dalam-minggu**, **waktu-hari**, dan **konsistensi/rentetan** — ditulis
sebagai `memories(kind='behavioral')` lewat pintu keluar `memory`.

🔑 **Asosiatif, bukan kausal** (naskah 4 §7, docs/54): keluarannya menyebut
*“paling sering … pada …”*, tidak pernah *“menyebabkan”*. Causality Engine ada
di luar V0; menyatakan sebab dari data observasional adalah justru yang §7
larang. `tanpa_klaim_kausal` menjaganya, diuji.

🔑 **Confidence Layer** (§19): tiap memori membawa `confidence` (seberapa
terpusat polanya) dan `evidence_count` (berapa penyelesaian jadi dasarnya).
Keduanya disimpan apa adanya — AMBANG kapan sistem menyatakan vs bertanya milik
pemilik (#34, tugas 5.4). Di sini hanya aturan keras: tanpa data (0 penyelesaian)
tidak ada yang dinyatakan — polanya diluruhkan.

Pemicu: konsumen atas `habit.*` di `hvx.pekerja`. Idempoten & menguatkan: id
memori deterministik per (pengguna, habit, jenis pola), jadi menghitung ulang
menimpa, bukan menumpuk. `intelligence` ada di atas `events`/`habits`/`memory`/
`profile` (M-1), jadi memanggil pintu keluarnya langsung.
"""

from __future__ import annotations

import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import events, habits, memory, profile

from .keyakinan import cukup_untuk_menyatakan

_NS = uuid.UUID("3f6b9d14-2a7c-5e80-9b1a-6c5d4e3f2a10")
MODEL = "pola-perilaku@v1"
SCOPE = "habits"  # pola tentang habit & penyelesaiannya (identity.SCOPE_RESMI)
ZONA_BAWAAN = "UTC"

# Konsumen "Habit streak" spec/03 (habit.*): tiap perubahan penyelesaian memicu
# hitung ulang. `created`/jenis lain tidak mengubah riwayat penyelesaian.
JENIS_POLA: frozenset[str] = frozenset(
    {"habit.completed", "habit.skipped", "habit.completion_retracted"}
)

_HARI = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")  # weekday() 0=Senin
_PERIODE = {"day": "hari", "week": "minggu", "month": "bulan"}

# Kata yang mengklaim SEBAB — tak boleh muncul di keluaran pola (naskah 4 §7).
_KATA_KAUSAL = (
    "menyebabkan",
    "penyebab",
    "sebab",
    "karena",
    "akibat",
    "mengakibatkan",
    "memicu",
    "membuat",
)


def tanpa_klaim_kausal(teks: str) -> bool:
    """`True` bila teks tidak mengandung klaim sebab — penjaga aturan §7, diuji."""
    rendah = teks.lower()
    return not any(k in rendah for k in _KATA_KAUSAL)


def _bagian_hari(jam: int) -> str:
    if 5 <= jam < 11:
        return "pagi"
    if 11 <= jam < 15:
        return "siang"
    if 15 <= jam < 19:
        return "sore"
    return "malam"


@dataclass(frozen=True)
class Pola:
    content: str
    confidence: Decimal
    evidence_count: int


def _terpusat(nilai: list[str]) -> tuple[str, int]:
    """(nilai paling sering, jumlahnya) — pemecah seri: yang lebih dulu muncul."""
    return Counter(nilai).most_common(1)[0]


def pola_hari(title: str, hari: list[int]) -> Pola | None:
    """Hari-dalam-minggu penyelesaian paling sering — asosiatif, dari `for_date` lokal."""
    if not hari:
        return None
    dom, n = _terpusat([_HARI[h] for h in hari])
    total = len(hari)
    isi = (
        f'Dalam {total} penyelesaian tercatat, "{title}" '
        f"paling sering diselesaikan pada hari {dom} ({n}/{total})."
    )
    return Pola(isi, Decimal(n) / Decimal(total), total)


def pola_waktu(title: str, jam_lokal: list[int]) -> Pola | None:
    """Bagian hari penyelesaian paling sering DICATAT (waktu catat, bukan waktu laku)."""
    if not jam_lokal:
        return None
    dom, n = _terpusat([_bagian_hari(j) for j in jam_lokal])
    total = len(jam_lokal)
    isi = (
        f'Dalam {total} penyelesaian tercatat, "{title}" '
        f"paling sering dicatat pada {dom} hari ({n}/{total})."
    )
    return Pola(isi, Decimal(n) / Decimal(total), total)


def pola_konsistensi(
    title: str, period: str, rentetan: habits.Rentetan | None, total: int
) -> Pola | None:
    """Konsistensi 30 hari + rentetan berjalan — ringkasan, bukan klaim sebab.

    🔴 Tinjauan buta S5–6 (B1): periode yang jatuh tempo KOSONG memberi tingkat 0,0, bukan
    `None` — tanpa penjaga bukti, habit yang belum (atau tak lagi) punya satu pun
    penyelesaian menulis pola "dipenuhi 0%" ber-`evidence_count` 0, justru yang
    Confidence Layer (5.4) larang di sisi tulis. Nol penyelesaian → diluruhkan."""
    if rentetan is None or rentetan.completion_rate_30d is None:
        return None
    if not cukup_untuk_menyatakan(total):
        return None
    pct = round(rentetan.completion_rate_30d * 100)
    periode = _PERIODE.get(period, "periode")
    isi = (
        f'Dalam 30 hari terakhir, "{title}" dipenuhi {pct}% {periode} '
        f"(rentetan berjalan {rentetan.current}, terpanjang {rentetan.longest})."
    )
    return Pola(isi, Decimal(str(rentetan.completion_rate_30d)), total)


def _zona(zona: str) -> ZoneInfo:
    try:
        return ZoneInfo(zona)
    except (ZoneInfoNotFoundError, ValueError):  # pragma: no cover - profil memvalidasi IANA
        return ZoneInfo(ZONA_BAWAAN)


def _id(user_id: UUID, habit_id: UUID, jenis: str) -> UUID:
    return uuid.uuid5(_NS, f"{user_id}:{habit_id}:{jenis}")


async def _simpan(conn: AsyncConnection, user_id: UUID, id_: UUID, pola: Pola | None) -> None:
    if pola is None:
        await memory.luruhkan_pola(conn, user_id, id_)
    else:
        await memory.catat_pola(
            conn,
            user_id,
            id_=id_,
            scope=SCOPE,
            content=pola.content,
            confidence=pola.confidence,
            evidence_count=pola.evidence_count,
            model_version=MODEL,
        )


async def deteksi_pola_habit(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Penangan konsumen habit.* — hitung ulang ketiga pola habit itu, di transaksi event.

    Konvergen: membaca riwayat HIDUP (tak dicabut) dari `events` tiap kali, jadi
    pencabutan/penyaluran ulang menyatukan ke keadaan yang sama (seperti 5.1).
    """
    habit_id = event.subject_id
    if habit_id is None:
        return
    uid = event.user_id
    id_hari = _id(uid, habit_id, "weekday")
    id_waktu = _id(uid, habit_id, "timeofday")
    id_konsisten = _id(uid, habit_id, "consistency")

    habit = await habits.habit_pada(conn, habit_id)
    if habit is None:  # habit dihapus — tak ada pola yang berlaku lagi
        for mid in (id_hari, id_waktu, id_konsisten):
            await memory.luruhkan_pola(conn, uid, mid)
        return

    riwayat = await events.riwayat_habit(conn, uid, habit_id)
    zona = await profile.zona_waktu(conn, uid) or ZONA_BAWAAN
    zi = _zona(zona)
    hari = [date.fromisoformat(str(e.payload["for_date"])).weekday() for e in riwayat]
    jam = [e.occurred_at.astimezone(zi).hour for e in riwayat]

    await _simpan(conn, uid, id_hari, pola_hari(habit.title, hari))
    await _simpan(conn, uid, id_waktu, pola_waktu(habit.title, jam))
    rentetan = await habits.rentetan_pada(conn, uid, habit_id, zona)
    await _simpan(
        conn, uid, id_konsisten, pola_konsistensi(habit.title, habit.period, rentetan, len(riwayat))
    )
