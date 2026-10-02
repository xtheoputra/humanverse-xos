"""SQL modul `checkins` — hanya tabel miliknya: daily_checkins · mood_entries (spec/06 aturan 5).

SQL statis seluruhnya (lihat `profile/repository.py`). Tiap fungsi menerima
koneksi dari lapisan layanan, di dalam `platform.transaksi_pengguna`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import RowMapping, text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import Checkin, Mood

# spec/07 2.5 — upsert per tanggal: `UNIQUE (user_id, for_date)` + `DO UPDATE`.
# PUT = GANTI: tiap kolom diambil dari badan (EXCLUDED), termasuk yang kosong.
# `xmax = 0` membedakan baris yang baru disisipkan dari yang diperbarui — tanpa
# kueri kedua, dan tanpa membaca-lalu-menulis yang kalah balapan.
#
# `WHERE … IS DISTINCT FROM`: PUT yang IDENTIK tidak menulis apa pun — spec/04
# *“dua PUT yang sama selalu menghasilkan baris yang sama”*, termasuk
# `updated_at` (tinjauan kontrak Sprint 2, F11: dulu bergeser tiap PUT). Tanpa
# pembaruan `RETURNING` kosong; barisnya dibaca `_PADA` — sudah terkunci oleh
# `ON CONFLICT` di transaksi yang sama.
_SIMPAN = text(
    """
    INSERT INTO daily_checkins (user_id, for_date, energy, focus, sleep_hours, note)
    VALUES (:user_id, :for_date, CAST(:energy AS smallint), CAST(:focus AS smallint),
            CAST(:sleep_hours AS numeric), CAST(:note AS text))
    ON CONFLICT (user_id, for_date) DO UPDATE SET
      energy = EXCLUDED.energy,
      focus = EXCLUDED.focus,
      sleep_hours = EXCLUDED.sleep_hours,
      note = EXCLUDED.note
    WHERE (daily_checkins.energy, daily_checkins.focus, daily_checkins.sleep_hours,
           daily_checkins.note)
          IS DISTINCT FROM (EXCLUDED.energy, EXCLUDED.focus, EXCLUDED.sleep_hours,
                            EXCLUDED.note)
    RETURNING id, for_date, energy, focus, sleep_hours, note, created_at, updated_at,
              (xmax = 0) AS baru
    """
)

_PADA = text(
    """
    SELECT id, for_date, energy, focus, sleep_hours, note, created_at, updated_at
    FROM daily_checkins
    WHERE user_id = :user_id AND for_date = :for_date
    """
)

# Isi check-in SEBELUM PUT — dikunci sampai transaksi selesai, supaya "berubah
# atau tidak" diputuskan terhadap baris yang tidak bisa berubah di tengahnya.
_SEBELUM = text(
    """
    SELECT energy, focus, sleep_hours
    FROM daily_checkins
    WHERE user_id = :user_id AND for_date = :for_date
    FOR UPDATE
    """
)

_RENTANG = text(
    """
    SELECT id, for_date, energy, focus, sleep_hours, note, created_at, updated_at
    FROM daily_checkins
    WHERE user_id = :user_id AND for_date BETWEEN :dari AND :sampai
    ORDER BY for_date DESC
    """
)

_TERAKHIR = text(
    """
    SELECT id, for_date, energy, focus, sleep_hours, note, created_at, updated_at
    FROM daily_checkins
    WHERE user_id = :user_id
    ORDER BY for_date DESC
    LIMIT :batas
    """
)

_ENERGI_PADA = text(
    "SELECT energy FROM daily_checkins WHERE user_id = :user_id AND for_date = :for_date"
)


@dataclass(frozen=True)
class HasilSimpan:
    checkin: Checkin
    baru: bool


def _checkin(baris: RowMapping) -> Checkin:
    return Checkin.model_validate({k: v for k, v in baris.items() if k != "baru"})


async def simpan(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    for_date: date,
    energy: int | None,
    focus: int | None,
    sleep_hours: Decimal | None,
    note: str | None,
) -> HasilSimpan:
    baris = (
        (
            await conn.execute(
                _SIMPAN,
                {
                    "user_id": user_id,
                    "for_date": for_date,
                    "energy": energy,
                    "focus": focus,
                    "sleep_hours": sleep_hours,
                    "note": note,
                },
            )
        )
        .mappings()
        .first()
    )
    if baris is not None:
        return HasilSimpan(_checkin(baris), baru=bool(baris["baru"]))
    # Isi sama persis dengan yang tersimpan — baris lama, tidak ditulis ulang.
    lama = (await conn.execute(_PADA, {"user_id": user_id, "for_date": for_date})).mappings().one()
    return HasilSimpan(_checkin(lama), baru=False)


async def sebelum(
    conn: AsyncConnection, user_id: UUID, for_date: date
) -> tuple[int | None, int | None, float | None] | None:
    """(energy, focus, sleep_hours) tanggal itu — `None` bila belum pernah check-in.

    `sleep_hours` sebagai float, SAMA dengan `Checkin.sleep_hours` (E-170): yang
    dibandingkan `service.simpan` harus bertipe sama — `Decimal("7.1") != 7.1`,
    dan check-in yang identik akan terbaca "berubah" lalu menerbitkan event palsu.
    """
    b = (await conn.execute(_SEBELUM, {"user_id": user_id, "for_date": for_date})).first()
    if b is None:
        return None
    tidur = float(b.sleep_hours) if b.sleep_hours is not None else None
    return (b.energy, b.focus, tidur)


async def rentang(
    conn: AsyncConnection, *, user_id: UUID, dari: date, sampai: date
) -> list[Checkin]:
    hasil = await conn.execute(_RENTANG, {"user_id": user_id, "dari": dari, "sampai": sampai})
    return [_checkin(b) for b in hasil.mappings()]


async def terakhir(conn: AsyncConnection, *, user_id: UUID, batas: int) -> list[Checkin]:
    hasil = await conn.execute(_TERAKHIR, {"user_id": user_id, "batas": batas})
    return [_checkin(b) for b in hasil.mappings()]


async def checkin_pada(conn: AsyncConnection, user_id: UUID, for_date: date) -> Checkin | None:
    """Check-in pengguna pada tanggal LOKAL itu — `None` bila belum ada.

    Pembaca lapisan atas (Behavior Engine 5.3) yang menghitung `human_states` dari
    keadaan OTORITATIF check-in, bukan dari payload event yang bisa basi saat
    disalurkan ulang. Berjalan di koneksi & RLS pemanggil.
    """
    baris = (
        (await conn.execute(_PADA, {"user_id": user_id, "for_date": for_date})).mappings().first()
    )
    return _checkin(baris) if baris else None


async def energi_pada(conn: AsyncConnection, user_id: UUID, for_date: date) -> int | None:
    """Energi check-in pengguna pada tanggal LOKAL itu — dipasang `hvx.main` sebagai
    `pembaca_energi` (K-23): tier habit yang disarankan (spec/07 2.2, naskah 4 §34).

    Berjalan di koneksi PEMANGGIL — transaksi dan RLS-nya sama.
    """
    nilai = (
        await conn.execute(_ENERGI_PADA, {"user_id": user_id, "for_date": for_date})
    ).scalar_one_or_none()
    return int(nilai) if nilai is not None else None


# ── spec/07 2.6 — mood_entries ────────────────────────────────────────────────

_SISIP_MOOD = text(
    """
    INSERT INTO mood_entries (id, user_id, occurred_at, valence, label, note)
    VALUES (COALESCE(CAST(:id AS uuid), gen_random_uuid()), :user_id,
            COALESCE(CAST(:occurred_at AS timestamptz), now()), :valence,
            CAST(:label AS text), CAST(:note AS text))
    RETURNING id, occurred_at, valence, label, note, created_at
    """
)

_MOOD_ID = text(
    """
    SELECT id, occurred_at, valence, label, note, created_at
    FROM mood_entries
    WHERE id = :id AND deleted_at IS NULL
    """
)

# Kursor keyset (occurred_at, id) turun — mood yang dicatat mundur (occurred_at
# lampau) tetap masuk di tempatnya, dan halaman berikutnya tidak bergeser.
_DAFTAR_MOOD = text(
    """
    SELECT id, occurred_at, valence, label, note, created_at
    FROM mood_entries
    WHERE user_id = :user_id AND deleted_at IS NULL
      AND (CAST(:dari AS timestamptz) IS NULL OR occurred_at >= CAST(:dari AS timestamptz))
      AND (CAST(:sampai AS timestamptz) IS NULL OR occurred_at < CAST(:sampai AS timestamptz))
      AND (CAST(:k_waktu AS timestamptz) IS NULL
           OR (occurred_at, id) < (CAST(:k_waktu AS timestamptz), CAST(:k_id AS uuid)))
    ORDER BY occurred_at DESC, id DESC
    LIMIT :batas
    """
)

# Batas atas `occurred_at` menurut jam BASIS DATA, dengan kelonggaran untuk jam
# perangkat yang sedikit maju.
_BATAS_WAKTU_MOOD = text("SELECT now() + make_interval(secs => :longgar)")


async def sisip_mood(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    id_: UUID | None,
    occurred_at: datetime | None,
    valence: int,
    label: str | None,
    note: str | None,
) -> Mood:
    baris = (
        (
            await conn.execute(
                _SISIP_MOOD,
                {
                    "id": id_,
                    "user_id": user_id,
                    "occurred_at": occurred_at,
                    "valence": valence,
                    "label": label,
                    "note": note,
                },
            )
        )
        .mappings()
        .one()
    )
    return Mood.model_validate(dict(baris))


async def mood_id(conn: AsyncConnection, mood_id_: UUID) -> Mood | None:
    baris = (await conn.execute(_MOOD_ID, {"id": mood_id_})).mappings().first()
    return Mood.model_validate(dict(baris)) if baris else None


async def daftar_mood(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    dari: datetime | None,
    sampai: datetime | None,
    sesudah: tuple[datetime, UUID] | None,
    batas: int,
) -> list[Mood]:
    hasil = await conn.execute(
        _DAFTAR_MOOD,
        {
            "user_id": user_id,
            "dari": dari,
            "sampai": sampai,
            "k_waktu": sesudah[0] if sesudah else None,
            "k_id": sesudah[1] if sesudah else None,
            "batas": batas,
        },
    )
    return [Mood.model_validate(dict(b)) for b in hasil.mappings()]


async def batas_waktu_mood(conn: AsyncConnection, longgar_s: int) -> datetime:
    nilai = (await conn.execute(_BATAS_WAKTU_MOOD, {"longgar": longgar_s})).scalar_one()
    if not isinstance(nilai, datetime):  # pragma: no cover - bentuk dari PostgreSQL
        raise TypeError(type(nilai).__name__)
    return nilai
