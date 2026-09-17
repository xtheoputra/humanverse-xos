"""SQL modul `profile` — hanya tabel miliknya: profiles · human_states (spec/06 aturan 5)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Profil

_KOLOM_PROFIL = "display_name, timezone, locale, birth_year, avatar_url, preferences, updated_at"

# Satu-satunya kolom yang boleh diubah lewat PATCH — nama kolom SQL berasal
# dari daftar ini, tidak pernah dari masukan klien.
_BISA_DIUBAH: dict[str, str] = {
    "display_name": ":display_name",
    "timezone": ":timezone",
    "locale": ":locale",
    "preferences": "CAST(:preferences AS jsonb)",
}


async def ambil_profil(conn: AsyncConnection, user_id: UUID) -> Profil | None:
    baris = (
        (
            await conn.execute(
                text(f"SELECT {_KOLOM_PROFIL} FROM profiles WHERE user_id = :user_id"),  # noqa: S608
                {"user_id": user_id},
            )
        )
        .mappings()
        .first()
    )
    return Profil.model_validate(dict(baris)) if baris else None


async def buat_profil(
    conn: AsyncConnection, user_id: UUID, display_name: str, timezone: str
) -> None:
    await conn.execute(
        text(
            "INSERT INTO profiles (user_id, display_name, timezone) "
            "VALUES (:user_id, :display_name, :timezone)"
        ),
        {"user_id": user_id, "display_name": display_name, "timezone": timezone},
    )


async def ubah_profil(
    conn: AsyncConnection, user_id: UUID, perubahan: Mapping[str, Any]
) -> Profil | None:
    kolom = [k for k in perubahan if k in _BISA_DIUBAH]
    if len(kolom) != len(perubahan):
        raise ValueError(
            f"kolom profil yang tidak bisa diubah: {sorted(set(perubahan) - set(kolom))}"
        )
    if not kolom:
        return await ambil_profil(conn, user_id)
    nilai: dict[str, Any] = {"user_id": user_id}
    for k in kolom:
        nilai[k] = json.dumps(perubahan[k]) if k == "preferences" else perubahan[k]
    set_ = ", ".join(f"{k} = {_BISA_DIUBAH[k]}" for k in kolom)
    # Nama kolom berasal dari _BISA_DIUBAH, nilainya parameter — bukan masukan klien.
    kueri = text(
        f"UPDATE profiles SET {set_} "  # noqa: S608
        f"WHERE user_id = :user_id RETURNING {_KOLOM_PROFIL}"
    )
    baris = (await conn.execute(kueri, nilai)).mappings().first()
    return Profil.model_validate(dict(baris)) if baris else None
