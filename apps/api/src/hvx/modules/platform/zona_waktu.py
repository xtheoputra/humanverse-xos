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

from functools import cache
from typing import Annotated
from zoneinfo import available_timezones

from pydantic import AfterValidator


@cache
def _nama_sah() -> frozenset[str]:
    return frozenset(available_timezones())


def zona_waktu_sah(nama: str) -> bool:
    return nama in _nama_sah()


def _periksa(nama: str) -> str:
    if not zona_waktu_sah(nama):
        # Nilainya sengaja tidak dikutip balik — jawaban galat tidak memantulkan masukan.
        raise ValueError("bukan nama zona waktu IANA (contoh: 'Asia/Jakarta')")
    return nama


ZonaWaktuIANA = Annotated[str, AfterValidator(_periksa)]
