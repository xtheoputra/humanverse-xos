"""Aturan `profile` — pendengar pendaftaran (spec/07 1.1 · 1.3)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import identity

from . import repository


async def buat_profil_awal(conn: AsyncConnection, baru: identity.PenggunaBaru) -> None:
    """Dipasang `hvx.main` sebagai pendengar pendaftaran identity.

    Berjalan di transaksi pendaftaran yang SAMA: kalau profil gagal dibuat,
    akunnya pun tidak pernah ada (K-17 — identity tidak mengimpor profile).
    """
    await repository.buat_profil(conn, baru.user_id, baru.display_name, baru.timezone)
