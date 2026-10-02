"""Behavior projector — spec/07 5.1: *“proyeksi bisa dibangun ulang dari nol dan
hasilnya sama”*.

Behavior Engine (naskah 4 §5): AI tidak hanya melihat apa yang user **katakan**,
tetapi **apa yang benar-benar dilakukan**. Projector ini mengubah aliran `events`
— sumber kebenaran perilaku (spec/02 aturan D) — menjadi satu lajur aktivitas
`source='inferred'` (modul `activities`), bahan untuk deteksi pola (5.2) dan
`human_states` (5.3).

Dua sifat yang mengikat (K-33):

* **Idempoten & bisa dibangun ulang.** `id` tiap baris proyeksi DETERMINISTIK
  dari penyelesaian sumbernya (`uuid5`), jadi event yang sama — disalurkan ulang
  stream, atau diputar ulang `bangun_ulang_proyeksi` — tidak pernah melahirkan
  baris kedua.
* **Konvergen, bukan bergantung urutan tiba.** Alih-alih "sisip saat selesai,
  hapus saat dicabut" — yang bisa menghidupkan kembali baris dicabut kalau event
  `completed` disalurkan ulang SESUDAH `retracted` (celah ACK stream) — projector
  menghitung keadaan AKHIR tiap penyelesaian dari `events`: ada `habit.completed`
  dan tidak ada `habit.completion_retracted` → baris ada; selain itu → tidak ada.
  Urutan tiba, pengiriman ganda, dua replika pekerja: hasilnya satu.

Projector mendengarkan **semua** jenis event (spec/03 *Consumer V0* — wajib); V0
baru memproyeksikan siklus penyelesaian habit. Jenis lain ditelan tanpa efek,
jadi menambah proyeksi baru kelak tidak mengubah perkabelan pekerja.

Modul `intelligence` ada di lapisan di atas `events` dan `activities`
(`pyproject.toml` M-1), jadi memanggil pintu keluarnya langsung — bukan lewat
event — adalah jalur yang sah.
"""

from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import activities, events, platform

# Namespace tetap untuk id proyeksi — bukan rahasia, hanya pembeda ruang nama.
_NS = uuid.UUID("7c0a1b2c-3d4e-5f60-8a1b-2c3d4e5f6071")
KIND_HABIT = "habit"

# Konsumen "semua" (spec/03): mendengarkan tiap jenis V0, memproyeksikan yang dikenal.
JENIS_EVENT: frozenset[str] = frozenset(events.REGISTRY)

# Payload proyeksi = kerangka perilaku, BUKAN teks bebas pengguna: `note`/`reason`
# habit sengaja tidak ikut (C-33 — teks bebas tidak disebar ke proyeksi).
_MEDAN_HABIT = ("completion_id", "for_date", "status", "tier_used")


def _id_proyeksi(completion_id: UUID) -> UUID:
    """id baris proyeksi — deterministik dari penyelesaian, stabil lintas pemutaran."""
    return uuid.uuid5(_NS, f"habit-completion:{completion_id}")


async def _proyeksikan_habit(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Konvergenkan satu penyelesaian habit dari `events` ke lajur aktivitas."""
    mentah = event.payload.get("completion_id")
    if mentah is None:
        return
    try:
        completion_id = UUID(str(mentah))
    except ValueError:
        return

    selesai = await events.cari_penyelesaian(
        conn, event.user_id, event_type="habit.completed", completion_id=completion_id
    )
    dicabut = await events.cari_penyelesaian(
        conn, event.user_id, event_type="habit.completion_retracted", completion_id=completion_id
    )
    aid = _id_proyeksi(completion_id)
    if selesai is not None and dicabut is None:
        muatan = {m: selesai.payload[m] for m in _MEDAN_HABIT if m in selesai.payload}
        await activities.catat_proyeksi(
            conn,
            event.user_id,
            id_=aid,
            kind=KIND_HABIT,
            occurred_at=selesai.occurred_at,
            payload=muatan,
        )
    else:
        await activities.hapus_proyeksi(conn, event.user_id, aid)


# event_type → proyektornya. Siklus penyelesaian habit memakai proyektor konvergen
# yang sama: `completed` DAN `retracted` memicu perhitungan ulang keadaan akhir.
_PROYEKSI = {
    "habit.completed": _proyeksikan_habit,
    "habit.completion_retracted": _proyeksikan_habit,
}


async def proyeksikan_perilaku(conn: AsyncConnection, event: events.EventMasuk) -> None:
    """Penangan konsumen (spec/03 Behavior projector) — satu event → proyeksinya.

    Berjalan di transaksi pemilik event yang dibuka `KonsumenStream`: bacaan `events`
    dan tulisan `activities` commit bersama atau batal bersama. Jenis yang belum
    diproyeksikan V0 ditelan tanpa efek (konsumen tetap meng-ACK-nya).
    """
    proyektor = _PROYEKSI.get(event.event_type)
    if proyektor is not None:
        await proyektor(conn, event)


async def bangun_ulang_proyeksi(engine: AsyncEngine, user_id: UUID) -> int:
    """Bangun proyeksi perilaku seorang pengguna DARI NOL dari `events` (spec/02 aturan D).

    Mengosongkan seluruh baris `inferred`, lalu memutar ulang setiap event urut
    tiba — satu transaksi, jadi tidak ada jendela saat proyeksi kosong. Karena
    proyektornya konvergen & idempoten, hasilnya sama dengan aliran langsung.
    Mengembalikan jumlah event yang diputar ulang.
    """
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        await activities.kosongkan_proyeksi(conn, user_id)
        riwayat = await events.untuk_proyeksi(conn, user_id)
        for event in riwayat:
            await proyeksikan_perilaku(conn, event)
    return len(riwayat)
