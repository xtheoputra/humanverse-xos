"""Bacaan `events` untuk membangun ulang proyeksi perilaku (spec/07 5.1, spec/02 aturan D).

`events` adalah sumber kebenaran: tabel domain — dan proyeksi `activities`
(`source='inferred'`) yang dibangun Behavior projector — boleh dibangun ulang
dari sini, dan kalau berbeda, **event yang benar** (spec/02 aturan D). Behavior
projector (modul `intelligence`, lapisan di atas `events`) memanggil dua bacaan
ini di dalam `transaksi_pengguna` pemiliknya, jadi RLS sendiri yang membatasinya
ke satu pengguna — tanpa fungsi `SECURITY DEFINER`, tidak seperti relay yang
memang perlu melihat lintas pengguna (`events_untuk_relay`, spec/01 §12).

SQL di sini hanya menyebut tabel `events` — milik modul ini (spec/06 aturan 5).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .stream import EventMasuk

_KOLOM = (
    "id, user_id, event_type, schema_version, occurred_at, recorded_at, source, "
    "subject_type, subject_id, payload"
)

# Urutan `recorded_at` (jam saat event MASUK sistem) — sama dengan urutan relay
# menyalurkannya ke konsumen (`relay.py`), jadi membangun ulang menapaki jalur
# yang sama dengan aliran langsung. `id` sebagai pemecah seri yang tentu.
_SEMUA = text(
    f"""
    SELECT {_KOLOM}
    FROM events
    WHERE user_id = :user_id
    ORDER BY recorded_at, id
    """  # noqa: S608 — _KOLOM konstanta modul, bukan masukan
)

# Satu event menurut (jenis, completion_id di payload). Behavior projector
# memakainya untuk menghitung keadaan AKHIR sebuah penyelesaian dari event —
# "pernah selesai?" dan "pernah dicabut?" — alih-alih menebak dari urutan tiba,
# yang bisa terbalik oleh pengiriman ulang stream.
_MENURUT_PENYELESAIAN = text(
    f"""
    SELECT {_KOLOM}
    FROM events
    WHERE user_id = :user_id
      AND event_type = :event_type
      AND payload ->> 'completion_id' = :completion_id
    ORDER BY recorded_at, id
    LIMIT 1
    """  # noqa: S608 — _KOLOM konstanta modul, bukan masukan
)


async def untuk_proyeksi(conn: AsyncConnection, user_id: UUID) -> list[EventMasuk]:
    """SEMUA event satu pengguna, urut tiba — bahan membangun ulang proyeksi dari nol."""
    hasil = await conn.execute(_SEMUA, {"user_id": user_id})
    return [EventMasuk(**baris._asdict()) for baris in hasil]


async def cari_penyelesaian(
    conn: AsyncConnection, user_id: UUID, *, event_type: str, completion_id: UUID
) -> EventMasuk | None:
    """Event `event_type` paling awal untuk sebuah `completion_id`, atau `None`.

    `event_type` dan `completion_id` adalah medan kontrak spec/03, bukan format
    kunci idempotensi internal `habits` — projector tidak terikat pada bentuk kunci itu.
    """
    baris = (
        await conn.execute(
            _MENURUT_PENYELESAIAN,
            {
                "user_id": user_id,
                "event_type": event_type,
                "completion_id": str(completion_id),
            },
        )
    ).first()
    return EventMasuk(**baris._asdict()) if baris is not None else None
