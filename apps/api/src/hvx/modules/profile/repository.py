"""SQL modul `profile` — hanya tabel miliknya: profiles · human_states (spec/06 aturan 5)."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import date
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
      preferences  = CASE WHEN :ubah_preferences
                          THEN CAST(:preferences AS jsonb)
                               || jsonb_strip_nulls(jsonb_build_object(
                                    'notifications', preferences -> 'notifications'))
                          ELSE preferences END
    WHERE user_id = :user_id
    RETURNING display_name, timezone, locale, birth_year, avatar_url, preferences, updated_at
    """
)
_BISA_DIUBAH = ("display_name", "timezone", "locale", "preferences")

_ZONA_WAKTU = text("SELECT timezone FROM profiles WHERE user_id = :user_id")

# 6.3 (K-44): `preferences.notifications` dibaca lalu ditulis di bawah kunci baris — dua
# `PATCH /me/notifications` serentak untuk jenis berbeda tidak saling menimpa.
_NOTIFIKASI_UNTUK_UBAH = text(
    "SELECT preferences -> 'notifications' AS n FROM profiles WHERE user_id = :user_id "
    "FOR NO KEY UPDATE"
)
_NOTIFIKASI = text(
    "SELECT preferences -> 'notifications' AS n FROM profiles WHERE user_id = :user_id"
)
_SIMPAN_NOTIFIKASI = text(
    """
    UPDATE profiles
    SET preferences = jsonb_set(preferences, '{notifications}', CAST(:n AS jsonb), true)
    WHERE user_id = :user_id
    """
)

# human_states (§6): satu baris per (pengguna, tanggal lokal, versi model). Behavior
# Engine (5.3) menghitung ulang → upsert pada kunci unik itu, bukan baris kedua.
# `model_version` di kunci membiarkan dua versi hidup berdampingan (prasyarat
# evaluasi/rollback §23).
_SIMPAN_HUMAN_STATE = text(
    """
    INSERT INTO human_states (user_id, for_date, metrics, model_version)
    VALUES (:user_id, :for_date, CAST(:metrics AS jsonb), :model_version)
    ON CONFLICT (user_id, for_date, model_version) DO UPDATE SET
      metrics = EXCLUDED.metrics,
      computed_at = now()
    """
)
_MEDAN_METRIK = frozenset({"value", "confidence", "evidence_count"})

# Human state terkini (Dashboard 6.1): baris paling baru per pengguna. `for_date`
# lebih dulu (keadaan HARI mana), lalu `computed_at` sebagai pemecah seri.
_HUMAN_STATE_TERKINI = text(
    """
    SELECT for_date, metrics, model_version
    FROM human_states WHERE user_id = :user_id
    ORDER BY for_date DESC, computed_at DESC
    LIMIT 1
    """
)


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


async def simpan_human_state(
    conn: AsyncConnection,
    user_id: UUID,
    *,
    for_date: date,
    metrics: Mapping[str, Mapping[str, Any]],
    model_version: str,
) -> None:
    """Simpan/ganti satu `human_state` harian (spec/07 5.3), di transaksi pemanggil.

    Tiap metrik WAJIB `{value, confidence, evidence_count}` (Confidence Layer §19) —
    dijaga di sini supaya tak ada metrik tanpa keyakinan & bukti yang lolos ke tabel.
    """
    if not metrics:
        raise ValueError("human_state tanpa metrik tidak ditulis")
    for nama, m in metrics.items():
        if set(m) != _MEDAN_METRIK:
            raise ValueError(f"metrik {nama!r} wajib tepat {sorted(_MEDAN_METRIK)}")
    await conn.execute(
        _SIMPAN_HUMAN_STATE,
        {
            "user_id": user_id,
            "for_date": for_date,
            "metrics": json.dumps(dict(metrics), sort_keys=True),
            "model_version": model_version,
        },
    )


async def human_state_terkini(conn: AsyncConnection, user_id: UUID) -> Mapping[str, Any] | None:
    """Human state paling baru pengguna — `{for_date, metrics, model_version}` atau `None`.

    Dibaca Dashboard (6.1) lewat pintu keluar `profile` karena `human_states` milik
    `profile` (spec/06 aturan 5). Berjalan di koneksi & RLS pemanggil."""
    baris = (await conn.execute(_HUMAN_STATE_TERKINI, {"user_id": user_id})).mappings().first()
    return dict(baris) if baris else None


async def zona_waktu(conn: AsyncConnection, user_id: UUID) -> str | None:
    """Zona waktu IANA pengguna — dipasang `hvx.main` sebagai `pembaca_zona_waktu` (K-23).

    Modul domain lain (habits: "hari ini" untuk rentetan, spec/07 2.4) tidak
    boleh mengimpor `profile` (spec/06 aturan 3) dan tidak boleh membaca
    `profiles` (aturan 5); titik rakit menyerahkan fungsi ini kepada mereka.
    Berjalan di koneksi PEMANGGIL — transaksi dan RLS-nya sama.
    """
    nilai = (await conn.execute(_ZONA_WAKTU, {"user_id": user_id})).scalar_one_or_none()
    return str(nilai) if nilai is not None else None


# ── spec/07 6.3 — preferensi notifikasi (K-44) ───────────────────────────────


async def notifikasi(conn: AsyncConnection, user_id: UUID) -> dict[str, Any] | None:
    """`preferences.notifications` yang tersimpan — `None` bila belum pernah dipilih."""
    nilai = (await conn.execute(_NOTIFIKASI, {"user_id": user_id})).scalar_one_or_none()
    return dict(nilai) if isinstance(nilai, dict) else None


async def notifikasi_untuk_ubah(conn: AsyncConnection, user_id: UUID) -> dict[str, Any] | None:
    nilai = (await conn.execute(_NOTIFIKASI_UNTUK_UBAH, {"user_id": user_id})).scalar_one_or_none()
    return dict(nilai) if isinstance(nilai, dict) else None


async def simpan_notifikasi(conn: AsyncConnection, user_id: UUID, isi: dict[str, Any]) -> None:
    await conn.execute(_SIMPAN_NOTIFIKASI, {"user_id": user_id, "n": json.dumps(isi)})
