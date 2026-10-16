"""Zona waktu IANA — spec/07 tugas 1.3: *“timezone IANA divalidasi”*.

Kenapa di `platform`: ini bentuk data, bukan aturan domain — `identity`
(pendaftaran) dan `profile` sama-sama menerimanya, dan `identity` tidak boleh
mengimpor `profile` (K-17).

Daftar nama diambil dari paket `tzdata` — daftar `zones`-nya, bukan dari sistem
operasi: di Windows `zoneinfo` tidak punya basis data sendiri, dan di citra
Linux isinya bergantung pada paket Debian hari itu. Satu sumber membuat uji di
kedua tempat menjawab hal yang sama. 🔴 Versi pertama memakai
`zoneinfo.available_timezones()`, yang JUGA menelusuri `/usr/share/zoneinfo`
sistem: di kontainer Debian `localtime` ikut diterima (tinjauan keamanan
Sprint 2) — nama yang artinya "zona server". `Factory` (zona semu IANA,
singkatan `-00`) juga bukan zona tempat orang tinggal. Tiap nama yang diterima
di sini dikenal PostgreSQL (`tests/integration/test_zona_waktu_pg.py`).

Peka huruf besar-kecil, seperti IANA: `asia/jakarta` DITOLAK — tanggal lokal
pengguna (`habit_completions.for_date`) dihitung dari nama ini,
dan nama yang "hampir benar" tidak pernah diterima diam-diam.
"""

from __future__ import annotations

from datetime import date
from functools import cache
from importlib.resources import files
from typing import Annotated

from pydantic import AfterValidator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

# UTC+14 sepanjang tahun — offset terbesar di basis data IANA. Tanggal lokal
# yang MELEWATI tanggal di sini belum terjadi di tempat mana pun di Bumi.
ZONA_PALING_MAJU = "Pacific/Kiritimati"

_HARI_INI_DI = text("SELECT (now() AT TIME ZONE :zona)::date")


# Nama di daftar IANA yang bukan zona tempat orang tinggal.
_BUKAN_ZONA_PENGGUNA = frozenset({"Factory"})


@cache
def nama_zona_sah() -> frozenset[str]:
    daftar = files("tzdata").joinpath("zones").read_text(encoding="utf-8")
    return frozenset(daftar.split()) - _BUKAN_ZONA_PENGGUNA


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
    return nama in nama_zona_sah()


def _periksa(nama: str) -> str:
    if not zona_waktu_sah(nama):
        # Nilainya sengaja tidak dikutip balik — jawaban galat tidak memantulkan masukan.
        raise ValueError("bukan nama zona waktu IANA (contoh: 'Asia/Jakarta')")
    return nama


ZonaWaktuIANA = Annotated[str, AfterValidator(_periksa)]
