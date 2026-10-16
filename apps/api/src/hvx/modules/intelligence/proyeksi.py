"""Proyeksi terdaftar — spec/08 7.2: *“proyeksi yang didaftarkan dibangun ulang dari nol dan
hasilnya sama; proyeksi baru yang tidak didaftarkan → CI merah”*.

Proyeksi = keadaan yang diturunkan dari `events`, sumber kebenaran perilaku (spec/02
aturan D). Janjinya satu: **dibuang lalu diputar ulang dari `events`, hasilnya sama**
dengan yang dibangun aliran langsung — termasuk aliran yang mengirim ganda dan tidak
berurutan (spec/03 aturan 2). V0 membuktikannya untuk satu proyeksi (5.1) dengan uji
miliknya sendiri; V1 menambah agregat, pola, dan prediksi (spec/08 Sprint 8–10), dan
tiap proyeksi baru yang tak dibuktikan adalah proyeksi yang diam-diam tak bisa
dibangun ulang.

Karena itu pendaftarannya dipaksa dari sisi PERKABELAN, bukan dari ingatan penulisnya:
tiap grup konsumen di `hvx.pekerja.rakit_konsumen` wajib ada di **tepat satu** dari
`PROYEKSI` (lalu diuji generik oleh `tests/integration/test_proyeksi_terdaftar.py`) atau
`BUKAN_PROYEKSI` (dengan alasannya). Konsumen baru di luar keduanya → `test_proyeksi_daftar.py`
merah.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import activities, events, platform, profile

from .keadaan import JENIS_KEADAAN, MODEL, hitung_human_state
from .proyektor import JENIS_EVENT, proyeksikan_perilaku


@dataclass(frozen=True)
class Proyeksi:
    """Satu proyeksi: penangan konsumennya + dua langkah yang membuatnya bisa dibangun ulang."""

    jenis: frozenset[str]  # event yang didengarnya — sama dengan konsumennya di pekerja
    tangani: events.Penangan  # penangan konsumen — sama dengan konsumennya di pekerja
    kosongkan: Callable[[AsyncConnection, UUID], Awaitable[object]]  # "dari nol"
    potret: Callable[[AsyncConnection, UUID], Awaitable[Any]]  # keadaan, untuk dibandingkan


async def _kosongkan_human_state(conn: AsyncConnection, user_id: UUID) -> int:
    return await profile.kosongkan_human_state(conn, user_id, model_version=MODEL)


async def _potret_human_state(conn: AsyncConnection, user_id: UUID) -> list[dict[str, Any]]:
    return await profile.potret_human_state(conn, user_id, model_version=MODEL)


# grup konsumen (`hvx.pekerja`) → proyeksinya.
PROYEKSI: dict[str, Proyeksi] = {
    # Behavior projector (5.1): lajur `activities` `inferred`.
    "proyektor": Proyeksi(
        jenis=JENIS_EVENT,
        tangani=proyeksikan_perilaku,
        kosongkan=activities.kosongkan_proyeksi,
        potret=activities.potret_proyeksi,
    ),
    # Human State (5.3): `human_states` versi `MODEL`, dari check-in OTORITATIF (K-35 (a)).
    "human-state": Proyeksi(
        jenis=JENIS_KEADAAN,
        tangani=hitung_human_state,
        kosongkan=_kosongkan_human_state,
        potret=_potret_human_state,
    ),
}

# grup konsumen → kenapa ia BUKAN proyeksi yang dibangun ulang dari `events`.
BUKAN_PROYEKSI: dict[str, str] = {
    "pola": (
        "proyeksi, tetapi ditulis ke `memories(kind='behavioral')` (K-34) yang juga memuat "
        "memori bukan-proyeksi; spec/08 9.1 memindahkannya ke tabel `patterns` — dan 9.1 "
        "WAJIB mendaftarkannya di `PROYEKSI`"
    ),
    "rekomendasi": (
        "memuat keadaan milik PENGGUNA (`shown`, `accepted`, umpan balik 5.6) yang tidak ada "
        "di `events`; membuangnya berarti membuang jawaban pengguna"
    ),
    "memori": (
        "menyemat ke Qdrant di luar transaksi; dipulihkan penyelaras vektor (3.6) dari "
        "`memories`, bukan diputar dari `events`"
    ),
}


async def bangun_ulang(engine: AsyncEngine, user_id: UUID, nama: str) -> int:
    """Bangun proyeksi `nama` seorang pengguna DARI NOL dari `events` (spec/02 aturan D).

    Mengosongkan, lalu memutar ulang tiap event yang didengar proyeksinya urut tiba — satu
    transaksi, jadi tidak ada jendela saat proyeksinya kosong. Mengembalikan jumlah event
    yang diputar ulang.
    """
    proyeksi = PROYEKSI[nama]
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        await proyeksi.kosongkan(conn, user_id)
        riwayat = [
            e for e in await events.untuk_proyeksi(conn, user_id) if e.event_type in proyeksi.jenis
        ]
        for event in riwayat:
            await proyeksi.tangani(conn, event)
    return len(riwayat)


async def bangun_ulang_proyeksi(engine: AsyncEngine, user_id: UUID) -> int:
    """Behavior projector (5.1) dari nol — nama lama, dipakai uji & alat sejak V0."""
    return await bangun_ulang(engine, user_id, "proyektor")
