"""Aturan `journal` — spec/07 3.4: *“`GET /journal` tidak pernah mengembalikan `body`”*.

* Tulisan PALING pribadi pengguna: RLS (spec/01 §11) membatasinya pada
  pemiliknya, daftar tidak memuat isinya (`schemas.RingkasanJurnal`), dan
  event-nya hanya `word_count` (spec/03 — isi jurnal tidak pernah masuk event).
* `journal.created` terbit di transaksi yang sama dengan barisnya (spec/06
  aturan 6); kuncinya id jurnal — id buatan klien, jadi kirim ulang tetap satu
  kunci. Menyunting jurnal bukan fakta perilaku baru (peta aturan 6 spec/06).
* `safety_flag` tetap NULL: jalur eskalasi keselamatan (issue #21) milik
  pemilik — kolomnya hanya memastikan tempatnya sudah ada (spec/01).
* **Menyunting atau menghapus jurnal menyelaraskan TURUNANNYA di transaksi yang
  sama** — pendengar yang dipasang titik rakit `hvx.main` (K-23): memori
  episodik jurnal (3.6) mengikuti isi barunya, atau dikosongkan saat jurnalnya
  dihapus. Tanpa itu kalimat yang dihapus pemiliknya dari jurnal tetap hidup di
  memori — dan di vektornya.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import events, platform

from . import repository
from .schemas import BuatJurnal, HalamanJurnal, Jurnal, UbahJurnal, hitung_kata

# (koneksi transaksi penyunting, id jurnal) — dipanggil SESUDAH jurnal diubah atau
# dihapus, sebelum commit. Pendengar membaca keadaan barunya lewat
# `isi_untuk_ekstraksi` (`None` = sudah dihapus).
PendengarJurnalBerubah = Callable[[AsyncConnection, UUID], Awaitable[None]]

# Jam perangkat yang sedikit maju tidak membuat tulisan "sekarang" ditolak.
LONGGAR_JAM_S = 300
_BATAS_WAKTU = text("SELECT now() + make_interval(secs => :longgar)")


def _tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Jurnal tidak ditemukan.")


async def _periksa_waktu(conn: AsyncConnection, occurred_at: datetime | None) -> None:
    if occurred_at is None:
        return
    batas = (await conn.execute(_BATAS_WAKTU, {"longgar": LONGGAR_JAM_S})).scalar_one()
    if occurred_at > batas:
        raise platform.GalatApi(422, "occurred_at_in_future", "Waktu tulisan itu belum terjadi.")


async def buat(engine: AsyncEngine, user_id: UUID, badan: BuatJurnal) -> Jurnal:
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            await _periksa_waktu(conn, badan.occurred_at)
            jurnal = await repository.sisip(
                conn,
                user_id=user_id,
                id_=badan.id,
                title=badan.title,
                body=badan.body,
                word_count=hitung_kata(badan.body),
                occurred_at=badan.occurred_at,
            )
            await events.terbitkan(
                conn,
                user_id=user_id,
                event_type="journal.created",
                occurred_at=jurnal.occurred_at,
                idempotency_key=f"journal:{jurnal.id}",
                subject_type="journal",
                subject_id=jurnal.id,
                payload={"word_count": jurnal.word_count},
            )
            return jurnal
    except IntegrityError as galat:
        p = platform.rincian_pelanggaran(galat)
        if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == "journal_entries_pkey":
            raise platform.GalatApi(
                409, "already_exists", "Jurnal dengan id ini sudah ada."
            ) from None
        raise


async def baca_jurnal(engine: AsyncEngine, user_id: UUID, jurnal_id: UUID) -> Jurnal | None:
    """Jurnal itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi, E-171).

    Isinya dibaca dari PostgreSQL di bawah RLS pemiliknya: Redis tidak pernah
    menyimpan tulisan pribadi (E-171) — juga tidak untuk 24 jam ulangan.
    """
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.ambil(conn, jurnal_id)


async def ambil(engine: AsyncEngine, user_id: UUID, jurnal_id: UUID) -> Jurnal:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        jurnal = await repository.ambil(conn, jurnal_id)
    if jurnal is None:
        raise _tidak_ditemukan()
    return jurnal


async def daftar(
    engine: AsyncEngine,
    user_id: UUID,
    *,
    dari: datetime | None,
    sampai: datetime | None,
    batas: int,
    kursor: str | None,
) -> HalamanJurnal:
    if dari is not None and sampai is not None and dari >= sampai:
        raise platform.GalatApi(400, "invalid_request", "`from` wajib sebelum `to`.")
    sesudah = platform.baca_kursor_waktu("journal", kursor)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        jurnal = await repository.daftar(
            conn, user_id=user_id, dari=dari, sampai=sampai, sesudah=sesudah, batas=batas + 1
        )
    lanjut = None
    if len(jurnal) > batas:
        jurnal = jurnal[:batas]
        lanjut = platform.kursor_waktu("journal", jurnal[-1].occurred_at, jurnal[-1].id)
    return HalamanJurnal(items=jurnal, next_cursor=lanjut)


async def ubah(
    engine: AsyncEngine,
    user_id: UUID,
    jurnal_id: UUID,
    badan: UbahJurnal,
    pendengar: Sequence[PendengarJurnalBerubah],
) -> Jurnal:
    perubahan: dict[str, Any] = badan.model_dump(include=badan.model_fields_set)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if not perubahan:  # `PATCH {}` tidak menyentuh baris — updated_at tetap
            jurnal = await repository.ambil(conn, jurnal_id)
        else:
            await _periksa_waktu(conn, badan.occurred_at)
            isi = perubahan.get("body")
            jurnal = await repository.ubah(
                conn, jurnal_id, perubahan, hitung_kata(isi) if isi is not None else None
            )
            if jurnal is not None:
                for p in pendengar:
                    await p(conn, jurnal_id)
    if jurnal is None:
        raise _tidak_ditemukan()
    return jurnal


async def hapus(
    engine: AsyncEngine,
    user_id: UUID,
    jurnal_id: UUID,
    pendengar: Sequence[PendengarJurnalBerubah],
) -> None:
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        if not await repository.hapus(conn, jurnal_id):
            raise _tidak_ditemukan()
        for p in pendengar:
            await p(conn, jurnal_id)


async def isi_untuk_ekstraksi(conn: AsyncConnection, jurnal_id: UUID) -> Jurnal | None:
    """Satu jurnal hidup — HANYA untuk memori (spec/07 3.6), di transaksi pemiliknya.

    Isi jurnal sengaja tidak pernah masuk event (spec/03), jadi ekstraktor dan
    pendengar memori membacanya di sini — `memory` boleh mengimpor `journal`
    (K-17). `None` = sudah dihapus. Dibaca di bawah kunci BAGI (lihat
    `repository._AMBIL_UNTUK_EKSTRAKSI`).
    """
    return await repository.ambil_untuk_ekstraksi(conn, jurnal_id)
