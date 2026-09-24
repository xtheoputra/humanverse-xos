"""Tipe masukan KETAT — spec/04 *Aturan lintas endpoint*: bentuk yang salah → `400`.

FastAPI memvalidasi badan permintaan dalam mode PYTHON pydantic
(`TypeAdapter.validate_python`), dan mode itu LONGGAR. Tinjauan kontrak
Sprint 2 (E-170) membuktikannya di tiap rute tulis, semuanya dijawab `201`:

* `true` diterima sebagai angka 1 (`valence`, `energy`), `false` sebagai tier 0;
* `"3"` diterima sebagai `target_count` 3;
* `1758672000` diterima sebagai `for_date` — detik Unix diubah menjadi tanggal
  **UTC**, tepat yang spec/01 larang (`for_date` tanggal LOKAL, tidak pernah
  diturunkan dari UTC);
* `"2026-09-24T00:00:00Z"` diterima sebagai tanggal;
* persetujuan pelatihan model tercatat `granted = true` dari string `"on"`.

Tipe di sini yang dipakai badan, kueri, dan jalur permintaan:

* `Bulat` — bilangan bulat JSON saja: bukan `true`, bukan `"3"`, bukan `3.0`.
* `Benar` — `true`/`false` saja.
* `Tanggal` — string `YYYY-MM-DD` saja, `1900-01-01` … `2999-12-31`.
* `WaktuBerzona` — string ISO-8601 BERZONA saja, rentang yang sama (UTC).
* `AngkaJson` — angka JSON (bukan string), untuk kolom `numeric`.

Rentang tanggal bukan hiasan (tinjauan keamanan Sprint 2): asyncpg menyimpan
`date.min`/`datetime.min` sebagai `-infinity`, dan `0001-01-01T00:00+14:00`
meluap saat diubah ke UTC — keduanya menjadi 500 di pembacaan berikutnya.

`tests/unit/test_masukan_ketat_semua_rute.py` menelusuri skema inti TIAP rute yang
dirakit `hvx.main`: medan angka, boolean, tanggal, atau waktu yang tidak
memakai tipe di sini membuatnya merah.
"""

from __future__ import annotations

import math
import re
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, BeforeValidator, Strict

TANGGAL_MIN = date(1900, 1, 1)
TANGGAL_MAKS = date(2999, 12, 31)
WAKTU_MIN = datetime(1900, 1, 1, tzinfo=UTC)
WAKTU_MAKS = datetime(2999, 12, 31, 23, 59, 59, 999_999, tzinfo=UTC)

_POLA_TANGGAL = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
# Awal ISO-8601 — sisanya (detik, pecahan, zona) diurai pydantic. Yang ditolak
# di sini: angka (detik Unix) dan teks lain yang pydantic longgar terima.
_POLA_WAKTU = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt ][0-9]{2}:[0-9]{2}")

_PESAN_TANGGAL = "tanggal wajib string YYYY-MM-DD"
_PESAN_WAKTU = "waktu wajib string ISO-8601 berzona, mis. 2026-09-24T06:30:00+07:00"


def _tanggal_iso(nilai: object) -> object:
    if isinstance(nilai, datetime):  # `datetime` turunan `date` — bukan tanggal
        raise ValueError(_PESAN_TANGGAL)
    if isinstance(nilai, date):
        return nilai
    if isinstance(nilai, str) and _POLA_TANGGAL.fullmatch(nilai):
        return nilai
    raise ValueError(_PESAN_TANGGAL)


def _tanggal_dalam_rentang(nilai: date) -> date:
    if not TANGGAL_MIN <= nilai <= TANGGAL_MAKS:
        raise ValueError("tanggal di luar rentang 1900-01-01 … 2999-12-31")
    return nilai


def _waktu_iso(nilai: object) -> object:
    if isinstance(nilai, datetime):
        return nilai
    if isinstance(nilai, str) and _POLA_WAKTU.match(nilai):
        return nilai
    raise ValueError(_PESAN_WAKTU)


def _waktu_dalam_rentang(nilai: datetime) -> datetime:
    try:
        utc = nilai.astimezone(UTC)
    except (OverflowError, ValueError):
        raise ValueError("waktu di luar rentang 1900 … 2999 (UTC)") from None
    if not WAKTU_MIN <= utc <= WAKTU_MAKS:
        raise ValueError("waktu di luar rentang 1900 … 2999 (UTC)")
    return nilai


def _angka_json(nilai: object) -> object:
    # `bool` turunan `int` di Python — `true` bukan angka di JSON.
    if isinstance(nilai, bool) or not isinstance(nilai, int | float | Decimal):
        raise ValueError("wajib angka JSON, bukan string atau boolean")
    if isinstance(nilai, float):
        if not math.isfinite(nilai):
            raise ValueError("wajib angka JSON yang terhingga")
        # `repr` = representasi terpendek yang kembali ke float yang sama: 7.5 → '7.5',
        # bukan 7.5000000000000000001 — `decimal_places` memeriksa yang DIKIRIM klien.
        return Decimal(repr(nilai))
    return nilai


Bulat = Annotated[int, Strict()]
Benar = Annotated[bool, Strict()]
Tanggal = Annotated[date, BeforeValidator(_tanggal_iso), AfterValidator(_tanggal_dalam_rentang)]
WaktuBerzona = Annotated[
    AwareDatetime, BeforeValidator(_waktu_iso), AfterValidator(_waktu_dalam_rentang)
]
AngkaJson = Annotated[Decimal, BeforeValidator(_angka_json)]

# Dibaca `tests/unit/test_masukan_ketat_semua_rute.py`: validator yang MEMBUAT tanggal,
# waktu, dan desimal ketat — node skema inti yang dibungkusnya dianggap ketat.
PENJAGA_KETAT = frozenset({_tanggal_iso, _waktu_iso, _angka_json})
