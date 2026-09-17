"""SQL modul `profile` — hanya tabel miliknya: profiles · human_states (spec/06 aturan 5)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Profil

# SQL STATIS seluruhnya — tidak ada nama kolom yang dirakit dari string. Versi
# pertama merakit `SET` dari daftar izin dengan f-string: aman, tetapi `bandit`
# (tahap scan) tidak bisa membedakannya dari injeksi, dan pembungkaman yang
# dibiarkan menjadi kebiasaan adalah pembungkaman yang suatu hari salah.
_AMBIL = text(
    "SELECT display_name, timezone, locale, birth_year, avatar_url, preferences, updated_at "
    "FROM profiles WHERE user_id = :user_id"
)

# Tiap kolom yang boleh diubah PATCH punya bendera `ubah_*`; yang tidak dikirim
# tetap nilainya sendiri. Kolom di luar daftar ini tidak bisa disentuh.
_UBAH = text(
    """
    UPDATE profiles SET
      display_name = CASE WHEN :ubah_display_name THEN :display_name ELSE display_name END,
      timezone     = CASE WHEN :ubah_timezone THEN :timezone ELSE timezone END,
      locale       = CASE WHEN :ubah_locale THEN :locale ELSE locale END,
      preferences  = CASE WHEN :ubah_preferences THEN CAST(:preferences AS jsonb)
                          ELSE preferences END
    WHERE user_id = :user_id
    RETURNING display_name, timezone, locale, birth_year, avatar_url, preferences, updated_at
    """
)
_BISA_DIUBAH = ("display_name", "timezone", "locale", "preferences")


async def ambil_profil(conn: AsyncConnection, user_id: UUID) -> Profil | None:
    baris = (await conn.execute(_AMBIL, {"user_id": user_id})).mappings().first()
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
    for k in _BISA_DIUBAH:
        nilai[f"ubah_{k}"] = k in perubahan
        v = perubahan.get(k)
        nilai[k] = json.dumps(v) if k == "preferences" and k in perubahan else v
    baris = (await conn.execute(_UBAH, nilai)).mappings().first()
    return Profil.model_validate(dict(baris)) if baris else None
