"""Zona waktu IANA — spec/07 tugas 1.3: *“timezone IANA divalidasi”*.

Kenapa di `platform`: ini bentuk data, bukan aturan domain — `identity`
(pendaftaran) dan `profile` sama-sama menerimanya, dan `identity` tidak boleh
mengimpor `profile` (K-17).

Daftar nama diambil dari paket `tzdata`, bukan dari sistem operasi: di Windows
`zoneinfo` tidak punya basis data sendiri, dan di citra Linux isinya bergantung
pada paket Debian hari itu. Satu sumber membuat uji di kedua tempat menjawab
hal yang sama. Peka huruf besar-kecil, seperti IANA: `asia/jakarta` DITOLAK —
tanggal lokal pengguna (`habit_completions.for_date`) dihitung dari nama ini,
dan nama yang "hampir benar" tidak pernah diterima diam-diam.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from typing import Annotated
from zoneinfo import available_timezones

from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

# UTC+14 sepanjang tahun — offset terbesar di basis data IANA. Tanggal lokal
# yang MELEWATI tanggal di sini belum terjadi di tempat mana pun di Bumi.
ZONA_PALING_MAJU = "Pacific/Kiritimati"

_HARI_INI_DI = text("SELECT (now() AT TIME ZONE :zona)::date")


@cache
def _nama_sah() -> frozenset[str]:
    return frozenset(available_timezones())


async def hari_ini_di(conn: AsyncConnection, zona: str) -> date:
    """Tanggal lokal SEKARANG di `zona`, menurut jam BASIS DATA.

    Jam basis data, bukan jam proses api — satu sumber waktu untuk semua
    instans, sama dengan kedaluwarsa izin (spec/07 1.5). Zona tak dikenal
    ditolak sebelum menyentuh basis data.
    """
    if not zona_waktu_sah(zona):
        raise ValueError("bukan nama zona waktu IANA")
    hasil = (await conn.execute(_HARI_INI_DI, {"zona": zona})).scalar_one()
    if not isinstance(hasil, date):  # pragma: no cover - bentuk dari PostgreSQL
        raise TypeError(type(hasil).__name__)
    return hasil


async def tanggal_paling_maju(conn: AsyncConnection) -> date:
    """Tanggal lokal paling maju di Bumi saat ini — batas atas `for_date` dari klien.

    Klien menyebut tanggal LOKAL perangkatnya (spec/01 `for_date`), dan perangkat
    yang sedang bepergian bisa berada di zona lain dari `profiles.timezone`.
    Batas yang tidak bergantung zona siapa pun: tanggal yang belum terjadi di
    tempat mana pun di Bumi pasti tanggal masa depan.
    """
    return await hari_ini_di(conn, ZONA_PALING_MAJU)


def zona_waktu_sah(nama: str) -> bool:
    return nama in _nama_sah()


def _periksa(nama: str) -> str:
    if not zona_waktu_sah(nama):
        # Nilainya sengaja tidak dikutip balik — jawaban galat tidak memantulkan masukan.
        raise ValueError("bukan nama zona waktu IANA (contoh: 'Asia/Jakarta')")
    return nama


ZonaWaktuIANA = Annotated[str, AfterValidator(_periksa)]
