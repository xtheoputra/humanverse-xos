"""Bagian `events` di Privacy Center — spec/07 6.4 (K-42), naskah 11 §7.25.

*“Tidak boleh hanya menghapus row di PostgreSQL”* — dan `events` adalah tempat pertama
fakta yang dihapus tetap hidup: payload membawa teks bebas (C-33: `note`, `reason`, judul,
label mood) yang tabel sumbernya sudah tidak punya. Maka:

* kategori **`history`** — seluruh riwayat kejadian: dihitung, diekspor, dan bisa dihapus
  sendiri (membersihkan sisa teks yang sudah dicabut di tabel sumbernya);
* tiap kategori SUMBER (habit, goal, check-in, mood, jurnal) membawa event jenisnya ikut
  terhapus sebagai **turunan**, di transaksi yang sama.

Penghapusannya lewat satu fungsi `SECURITY DEFINER` sempit (`hapus_event_pengguna`, spec/01
§12, migrasi 0013): `hvx_app` tetap tanpa `DELETE`/`UPDATE` atas `events` (§10), dan fungsi
itu hanya menyentuh event milik pengguna yang sedang dilayani transaksi.
"""

from __future__ import annotations

from collections.abc import Collection
from types import MappingProxyType
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import identity

from .kontrak import REGISTRY

# Domain event (`domain.kata_kerja_lampau`, spec/03) → kategori Privacy Center sumbernya.
# Jenis baru di REGISTRY tanpa domain di sini membuat `test_cakupan_privasi` merah.
KATEGORI_EVENT = MappingProxyType(
    {
        "habit": "habits",
        "goal": "goals",
        "checkin": "checkins",
        "mood": "moods",
        "journal": "journal",
    }
)

_HAPUS = text("SELECT hapus_event_pengguna(CAST(:jenis AS text[]), NULL, NULL)")
_HAPUS_SUBJEK = text(
    "SELECT hapus_event_pengguna(CAST(:jenis AS text[]), :subjek_tipe, CAST(:subjek_id AS uuid))"
)
_SEMUA_JENIS = text("SELECT DISTINCT event_type FROM events WHERE user_id = :u")


def jenis_untuk(kategori: str) -> list[str]:
    """Jenis event REGISTRY yang sumbernya kategori `kategori`."""
    return sorted(t for t in REGISTRY if KATEGORI_EVENT.get(t.split(".", 1)[0]) == kategori)


async def hapus_riwayat(conn: AsyncConnection, jenis: Collection[str]) -> int:
    """Hapus event milik pengguna yang dilayani `conn`, sejenis `jenis`; jumlahnya."""
    return int((await conn.execute(_HAPUS, {"jenis": sorted(jenis)})).scalar_one())


async def hapus_riwayat_subjek(
    conn: AsyncConnection, jenis: Collection[str], subjek_tipe: str, subjek_id: UUID
) -> int:
    """Hapus event satu subjek (mis. satu jurnal) milik pengguna yang dilayani `conn`."""
    hasil = await conn.execute(
        _HAPUS_SUBJEK,
        {"jenis": sorted(jenis), "subjek_tipe": subjek_tipe, "subjek_id": subjek_id},
    )
    return int(hasil.scalar_one())


def _turunan(kategori: str) -> identity.Penghapus:
    jenis = jenis_untuk(kategori)

    async def hapus(conn: AsyncConnection, user_id: UUID) -> int:
        return await hapus_riwayat(conn, jenis)

    return identity.Penghapus(kategori, "events", hapus, turunan=True)


async def _hapus_semua(conn: AsyncConnection, user_id: UUID) -> int:
    # Seluruh riwayat — juga jenis di luar REGISTRY hari ini (backfill lama, jenis yang pensiun).
    jenis = [b[0] for b in (await conn.execute(_SEMUA_JENIS, {"u": user_id})).all()]
    return await hapus_riwayat(conn, jenis) if jenis else 0


BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "history",
        "events",
        "SELECT count(*) FROM events WHERE user_id = :u",
        "SELECT * FROM events WHERE user_id = :u ORDER BY occurred_at, recorded_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.Penghapus("history", "events", _hapus_semua),
    *(_turunan(k) for k in sorted(set(KATEGORI_EVENT.values()))),
)
