"""Aturan `checkins` — spec/07 2.5 (`daily_checkins`, upsert per tanggal) · 2.6 (`mood_entries`).

* **2.5** `PUT /checkins/{for_date}` dua kali → SATU baris: `UNIQUE (user_id,
  for_date)` + `ON CONFLICT DO UPDATE`, satu pernyataan — dua PUT serentak
  tidak bisa keduanya menyisipkan. PUT = ganti (lihat `IsiCheckin`).
* `for_date` tanggal lokal perangkat — batasnya tanggal paling maju di Bumi
  (`platform.tanggal_paling_maju`), sama dengan penyelesaian habit (2.3).
* **Event (spec/07 3.2)** — `checkin.logged` hanya bila PUT MENGUBAH isi
  check-in (atau membuatnya): kuncinya `updated_at` baris itu, jadi koreksi
  A → B → A menjadi tiga event dan proyeksinya berakhir di A — sama dengan
  tabelnya. PUT yang sama persis tidak menerbitkan apa pun. `mood.logged` untuk
  tiap mood baru, kuncinya id mood (spec/03 aturan 1, E-177).
* **2.6** mood DILAPORKAN pengguna (spec/01: bukan ditaksir sistem — E-34).
  `occurred_at` wajib berzona waktu, boleh lampau (dicatat belakangan), dan
  tidak boleh lebih dari `LONGGAR_JAM_S` di depan jam basis data.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import events, platform

from . import repository
from .repository import HasilSimpan
from .schemas import CatatMood, DaftarCheckin, HalamanMood, IsiCheckin, Mood

# `GET /checkins` tanpa rentang: satu bulan terakhir yang tercatat.
TERAKHIR_BAWAAN = 31
# Rentang paling lebar yang dijawab sekaligus — satu tahun kabisat.
RENTANG_MAKS_HARI = 366
# Jam perangkat yang sedikit maju tidak membuat mood "sekarang" ditolak.
LONGGAR_JAM_S = 300


async def simpan(
    engine: AsyncEngine, user_id: UUID, for_date: date, isi: IsiCheckin
) -> HasilSimpan:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if for_date > await platform.tanggal_paling_maju(conn):
            raise platform.GalatApi(
                422, "for_date_in_future", "Tanggal itu belum terjadi di mana pun."
            )
        lama = await repository.sebelum(conn, user_id, for_date)
        hasil = await repository.simpan(
            conn,
            user_id=user_id,
            for_date=for_date,
            energy=isi.energy,
            focus=isi.focus,
            sleep_hours=isi.sleep_hours,
            note=isi.note,
        )
        c = hasil.checkin
        if lama != (c.energy, c.focus, c.sleep_hours):
            await events.terbitkan(
                conn,
                user_id=user_id,
                event_type="checkin.logged",
                occurred_at=c.updated_at,
                idempotency_key=f"checkin:{for_date.isoformat()}:{c.updated_at.isoformat()}",
                subject_type="checkin",
                subject_id=c.id,
                payload={
                    "energy": c.energy,
                    "focus": c.focus,
                    "sleep_hours": c.sleep_hours,
                    "for_date": for_date,
                },
            )
        return hasil


async def daftar(
    engine: AsyncEngine, user_id: UUID, *, dari: date | None, sampai: date | None
) -> DaftarCheckin:
    if (dari is None) != (sampai is None):
        # Setengah rentang ditolak, bukan ditebak ujung satunya.
        raise platform.GalatApi(400, "invalid_request", "`from` dan `to` dikirim bersama.")
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if dari is None or sampai is None:
            checkin = await repository.terakhir(conn, user_id=user_id, batas=TERAKHIR_BAWAAN)
        else:
            if dari > sampai or sampai - dari >= timedelta(days=RENTANG_MAKS_HARI):
                raise platform.GalatApi(
                    400,
                    "invalid_request",
                    f"Rentang tanggal wajib `from` ≤ `to`, paling lebar {RENTANG_MAKS_HARI} hari.",
                )
            checkin = await repository.rentang(conn, user_id=user_id, dari=dari, sampai=sampai)
    return DaftarCheckin(items=checkin)


# ── spec/07 2.6 — mood_entries ────────────────────────────────────────────────


async def catat_mood(engine: AsyncEngine, user_id: UUID, badan: CatatMood) -> Mood:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            if badan.occurred_at is not None and badan.occurred_at > (
                await repository.batas_waktu_mood(conn, LONGGAR_JAM_S)
            ):
                raise platform.GalatApi(
                    422, "occurred_at_in_future", "Waktu mood itu belum terjadi."
                )
            mood = await repository.sisip_mood(
                conn,
                user_id=user_id,
                id_=badan.id,
                occurred_at=badan.occurred_at,
                valence=badan.valence,
                label=badan.label,
                note=badan.note,
            )
            await events.terbitkan(
                conn,
                user_id=user_id,
                event_type="mood.logged",
                occurred_at=mood.occurred_at,
                idempotency_key=f"mood:{mood.id}",
                subject_type="mood",
                subject_id=mood.id,
                payload={"valence": mood.valence, "label": mood.label},
            )
            return mood
    except IntegrityError as galat:
        p = platform.rincian_pelanggaran(galat)
        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "mood_entries_pkey":
            raise platform.GalatApi(
                409, "already_exists", "Mood dengan id ini sudah ada."
            ) from None
        raise


async def baca_mood(engine: AsyncEngine, user_id: UUID, mood_id: UUID) -> Mood | None:
    """Mood itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi, E-171)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.mood_id(conn, mood_id)


async def daftar_mood(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    dari: datetime | None,
    sampai: datetime | None,
    batas: int,
    kursor: str | None,
) -> HalamanMood:
    if dari is not None and sampai is not None and dari >= sampai:
        raise platform.GalatApi(400, "invalid_request", "`from` wajib sebelum `to`.")
    sesudah = platform.baca_kursor_waktu("moods", kursor)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        mood = await repository.daftar_mood(
            conn, user_id=user_id, dari=dari, sampai=sampai, sesudah=sesudah, batas=batas + 1
        )
    lanjut = None
    if len(mood) > batas:
        mood = mood[:batas]
        lanjut = platform.kursor_waktu("moods", mood[-1].occurred_at, mood[-1].id)
    return HalamanMood(items=mood, next_cursor=lanjut)
