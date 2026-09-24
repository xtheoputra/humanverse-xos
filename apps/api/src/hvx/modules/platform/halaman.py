"""Halaman berkursor — spec/04: `?limit=` (maks 100) + `?cursor=`; balasan memuat `next_cursor`.

Kursor **keyset** `(waktu, id)`, bukan `OFFSET`: baris yang ditambahkan di
antara dua halaman tidak menggeser halaman berikutnya — bagi klien luring yang
menyinkron sambil pengguna terus menulis, `OFFSET` mengulang atau melompati
baris. `id` ikut di kursor karena dua baris bisa punya waktu yang sama persis.

Kursornya opak bagi klien (base64url JSON) tetapi TIDAK ditandatangani: yang
bisa dirusak klien hanya halaman miliknya sendiri — RLS (spec/01 §11) tetap
membatasi baris pada pengguna yang dilayani. Kursor yang rusak → `400
invalid_cursor`, bukan 500 — termasuk bentuk yang dirakit tangan: id berupa
angka, waktu tahun 0001 yang meluap saat diubah ke UTC (tinjauan keamanan
Sprint 2). Kursor juga menyebut DAFTAR asalnya (`jenis`): kursor `/goals` yang
dikirim ke `/moods` ditolak, bukan diam-diam memotong halaman di waktu goal.
"""

from __future__ import annotations

import base64
import binascii
import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Query

from .galat import GalatApi
from .masukan import WAKTU_MAKS, WAKTU_MIN

BATAS_MAKS = 100
BATAS_BAWAAN = 50

Batas = Annotated[int, Query(ge=1, le=BATAS_MAKS, description="Jumlah baris per halaman.")]
Kursor = Annotated[
    str | None, Query(max_length=200, description="`next_cursor` dari halaman sebelumnya.")
]


def kursor_waktu(jenis: str, saat: datetime, id_: UUID) -> str:
    """Kursor sesudah baris `(saat, id_)` di daftar `jenis` (mis. `"goals"`)."""
    if saat.utcoffset() is None:
        raise ValueError("waktu kursor wajib berzona waktu")
    mentah = json.dumps([jenis, saat.isoformat(), str(id_)], separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(mentah).decode().rstrip("=")


def _kursor_rusak() -> GalatApi:
    return GalatApi(400, "invalid_cursor", "Kursor halaman tidak sah.")


def baca_kursor_waktu(jenis: str, teks: str | None) -> tuple[datetime, UUID] | None:
    """`(waktu, id)` dari `?cursor=` daftar `jenis` — `None` untuk halaman pertama."""
    if teks is None:
        return None
    try:
        isi = json.loads(base64.urlsafe_b64decode(teks + "=" * (-len(teks) % 4)))
    except (binascii.Error, ValueError, UnicodeDecodeError, RecursionError):
        raise _kursor_rusak() from None
    # Bentuk diperiksa SEBELUM dipakai: `UUID(5)` bukan ValueError melainkan
    # AttributeError — lolos dari `except` di atas dan menjadi 500.
    if not (isinstance(isi, list) and len(isi) == 3 and all(isinstance(x, str) for x in isi)):
        raise _kursor_rusak()
    jenis_kursor, saat_teks, id_teks = isi
    if jenis_kursor != jenis:
        raise _kursor_rusak()
    try:
        saat = datetime.fromisoformat(saat_teks)
        id_ = UUID(id_teks)
        if saat.utcoffset() is None or not WAKTU_MIN <= saat.astimezone(UTC) <= WAKTU_MAKS:
            raise _kursor_rusak()
    except (ValueError, OverflowError):
        raise _kursor_rusak() from None
    return saat, id_
