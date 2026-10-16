"""spec/08 7.3 — tugas terjadwal per jam LOKAL pengguna, tepat sekali per hari lokal.

*Selesai bila*: tugas malam berjalan **tepat sekali** per pengguna per hari lokal; dua
pekerja serentak tidak menggandakan; pengguna di dua zona waktu diproses pada jam lokal
masing-masing; ganti zona waktu tidak melewatkan atau menggandakan hari.

Basis data uji `api_bersama` dibuat per berkas, dan tiap uji memakai NAMA TUGAS sendiri
— pengguna dari uji lain di berkas ini ikut jatuh tempo, maka asersi selalu disaring
per pengguna.
"""

from __future__ import annotations

import asyncio
from collections import Counter
from datetime import date, timedelta
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, psycopg_dsn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from hvx.modules import intelligence
from hvx.modules.platform import transaksi_pengguna

pytestmark = pytest.mark.integration

TIMUR, BARAT = "Pacific/Kiritimati", "Pacific/Pago_Pago"  # UTC+14 · UTC−11: selisih 25 jam


def _nama() -> str:
    return f"uji-{uuid4().hex[:8]}"


def _pemilik(api: ApiUji, sql: str, *param: object) -> list[tuple[object, ...]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        kursor = k.execute(sql, param)
        return kursor.fetchall() if kursor.description else []


def _lokal(api: ApiUji, zona: str) -> tuple[date, int]:
    """(tanggal lokal, menit sejak tengah malam lokal) menurut jam BASIS DATA — jam yang sama
    dengan yang dibaca `tugas_jatuh_tempo` (jam VM Docker bisa berbeda dari hos)."""
    ((tanggal, menit),) = _pemilik(
        api,
        "SELECT (now() AT TIME ZONE %s)::date, "
        "extract(hour FROM now() AT TIME ZONE %s)::int * 60 "
        "+ extract(minute FROM now() AT TIME ZONE %s)::int",
        zona,
        zona,
        zona,
    )
    assert isinstance(tanggal, date)
    assert isinstance(menit, int)
    return tanggal, menit


async def _pengguna(api: ApiUji, zona: str, *, umur_hari: int = 0) -> UUID:
    uid, _token = await api.pengguna_baru(timezone=zona)
    if umur_hari:
        _pemilik(
            api,
            "UPDATE users SET created_at = now() - make_interval(days => %s) WHERE id = %s",
            umur_hari,
            uid,
        )
    return uid


class _Pencatat:
    """Kerja tugas uji: mencatat (pengguna, hari lokal) yang dikerjakan, dari transaksinya."""

    def __init__(self, jeda_s: float = 0.0) -> None:
        self.dikerjakan: list[tuple[UUID, date]] = []
        self._jeda_s = jeda_s

    async def __call__(self, _conn: AsyncConnection, user_id: UUID, for_date: date) -> None:
        if self._jeda_s:
            await asyncio.sleep(self._jeda_s)  # menahan klaim selagi pekerja lain mencoba
        self.dikerjakan.append((user_id, for_date))

    def milik(self, uid: UUID) -> list[date]:
        return sorted(d for u, d in self.dikerjakan if u == uid)


async def _habiskan(api: ApiUji, tugas: intelligence.TugasTerjadwal) -> None:
    while await intelligence.jalankan_jatuh_tempo(api.engine_pekerja, tugas):
        pass


async def test_tepat_sekali_per_hari_lokal_dan_tidak_sebelum_akun_dibuat(
    api_bersama: ApiUji,
) -> None:
    lama = await _pengguna(api_bersama, "Asia/Jakarta", umur_hari=5)
    baru = await _pengguna(api_bersama, "Asia/Jakarta")
    kerja = _Pencatat()
    tugas = intelligence.TugasTerjadwal(_nama(), 0, kerja)  # 00:00 — selalu jatuh tempo

    await _habiskan(api_bersama, tugas)
    await _habiskan(api_bersama, tugas)  # putaran kedua: tidak ada yang tersisa

    hari_ini, _ = _lokal(api_bersama, "Asia/Jakarta")
    assert kerja.milik(lama) == [hari_ini - timedelta(days=1), hari_ini], "bukan tepat sekali"
    assert kerja.milik(baru) == [hari_ini], "hari sebelum akunnya dibuat ikut dikerjakan"
    assert _pemilik(
        api_bersama,
        "SELECT count(*) FROM scheduled_runs WHERE user_id = %s AND task = %s",
        lama,
        tugas.nama,
    ) == [(2,)]


async def test_dua_pekerja_serentak_tidak_menggandakan(api_bersama: ApiUji) -> None:
    uid = await _pengguna(api_bersama, "Asia/Jakarta", umur_hari=3)
    kerja = _Pencatat(jeda_s=0.3)
    tugas = intelligence.TugasTerjadwal(_nama(), 0, kerja)

    await asyncio.gather(
        *(intelligence.jalankan_jatuh_tempo(api_bersama.engine_pekerja, tugas) for _ in range(3))
    )
    await _habiskan(api_bersama, tugas)

    ganda = {k: n for k, n in Counter(kerja.dikerjakan).items() if n > 1}
    assert not ganda, f"dikerjakan lebih dari sekali: {ganda}"
    assert len(kerja.milik(uid)) == 2


async def test_kerja_yang_gagal_membatalkan_klaimnya_dan_dicoba_lagi(api_bersama: ApiUji) -> None:
    uid = await _pengguna(api_bersama, "Asia/Jakarta")
    gagal = {"sekali": True}
    berhasil: list[date] = []

    async def kerjakan(_conn: AsyncConnection, user_id: UUID, for_date: date) -> None:
        if user_id == uid and gagal.pop("sekali", False):
            raise RuntimeError("kerja gagal")
        if user_id == uid:
            berhasil.append(for_date)

    tugas = intelligence.TugasTerjadwal(_nama(), 0, kerjakan)
    await intelligence.jalankan_jatuh_tempo(api_bersama.engine_pekerja, tugas)
    assert not berhasil
    assert _pemilik(
        api_bersama,
        "SELECT count(*) FROM scheduled_runs WHERE user_id = %s AND task = %s",
        uid,
        tugas.nama,
    ) == [(0,)], "klaim kerja yang gagal tertinggal — hari itu tak akan pernah dikerjakan"

    await _habiskan(api_bersama, tugas)
    assert berhasil == [_lokal(api_bersama, "Asia/Jakarta")[0]]


async def test_dua_zona_diproses_pada_jam_lokal_masing_masing(api_bersama: ApiUji) -> None:
    """Jam lokal TIMUR selalu 1 jam di depan BARAT (selisih 25 jam). Ambang ditaruh 30 menit
    sesudah jam lokal salah satunya: yang jamnya sudah lewat dikerjakan, yang belum tidak."""
    timur = await _pengguna(api_bersama, TIMUR)
    barat = await _pengguna(api_bersama, BARAT)
    (hari_t, menit_t), (hari_b, menit_b) = _lokal(api_bersama, TIMUR), _lokal(api_bersama, BARAT)
    if menit_b + 30 < 24 * 60 and menit_t >= menit_b + 30:
        ambang, sudah, belum, hari = menit_b + 30, timur, barat, hari_t
    else:  # jam barat dekat tengah malam: timur sudah melewati tengah malam — dibalik
        ambang, sudah, belum, hari = menit_t + 30, barat, timur, hari_b
    kerja = _Pencatat()
    tugas = intelligence.TugasTerjadwal(_nama(), ambang, kerja)

    await _habiskan(api_bersama, tugas)

    assert kerja.milik(sudah) == [hari], "pengguna yang jam lokalnya sudah lewat tidak dikerjakan"
    assert kerja.milik(belum) == [], "pengguna yang jam lokalnya BELUM sampai ikut dikerjakan"


async def test_ganti_zona_tidak_melewatkan_atau_menggandakan_hari(api_bersama: ApiUji) -> None:
    uid = await _pengguna(api_bersama, BARAT, umur_hari=4)
    kerja = _Pencatat()
    tugas = intelligence.TugasTerjadwal(_nama(), 0, kerja)

    await _habiskan(api_bersama, tugas)
    for zona in (TIMUR, BARAT, TIMUR):  # timur: hari lokal melompat · barat: mundur
        _pemilik(api_bersama, "UPDATE profiles SET timezone = %s WHERE user_id = %s", zona, uid)
        await _habiskan(api_bersama, tugas)

    hari = kerja.milik(uid)
    assert len(hari) == len(set(hari)), f"hari dikerjakan dua kali: {hari}"
    rentang = (hari[-1] - hari[0]).days + 1
    assert len(hari) == rentang, f"hari terlewat di antara {hari[0]} dan {hari[-1]}: {hari}"
    assert hari[-1] == _lokal(api_bersama, TIMUR)[0]


async def test_akun_menunggu_dihapus_dan_zona_tak_dikenal_dilewati(api_bersama: ApiUji) -> None:
    pergi = await _pengguna(api_bersama, "Asia/Jakarta", umur_hari=2)
    _pemilik(
        api_bersama,
        "UPDATE users SET status = 'pending_deletion', "
        "deletion_scheduled_at = now() + interval '30 days' WHERE id = %s",
        pergi,
    )
    asing = await _pengguna(api_bersama, "Asia/Jakarta")
    _pemilik(api_bersama, "UPDATE profiles SET timezone = 'Bukan/Zona' WHERE user_id = %s", asing)
    sah = await _pengguna(api_bersama, "Asia/Jakarta")
    kerja = _Pencatat()
    tugas = intelligence.TugasTerjadwal(_nama(), 0, kerja)

    await _habiskan(api_bersama, tugas)

    assert kerja.milik(pergi) == [], "akun yang menunggu dihapus ikut dikerjakan"
    assert kerja.milik(asing) == []
    assert kerja.milik(sah), "zona asing satu pengguna menggagalkan semua pengguna"


async def test_klaim_hanya_terlihat_pemiliknya(api_bersama: ApiUji) -> None:
    a = await _pengguna(api_bersama, "Asia/Jakarta")
    b = await _pengguna(api_bersama, "Asia/Jakarta")
    tugas = intelligence.TugasTerjadwal(_nama(), 0, _Pencatat())
    await _habiskan(api_bersama, tugas)

    async with transaksi_pengguna(api_bersama.app.state.engine, a) as conn:
        terlihat = (
            (await conn.execute(text("SELECT DISTINCT user_id FROM scheduled_runs")))
            .scalars()
            .all()
        )
    assert set(terlihat) == {a}, "RLS scheduled_runs meloloskan klaim pengguna lain"
    assert b not in terlihat


def test_nama_dan_menit_tugas_divalidasi() -> None:
    async def _kosong(_c: AsyncConnection, _u: UUID, _d: date) -> None:
        return None

    with pytest.raises(ValueError, match="kebab-case"):
        intelligence.TugasTerjadwal("Weekly Review", 0, _kosong)
    with pytest.raises(ValueError, match="satu hari"):
        intelligence.TugasTerjadwal("tinjauan", 24 * 60, _kosong)
