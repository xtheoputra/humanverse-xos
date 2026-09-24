"""Halaman berkursor — spec/04: `?limit=` (maks 100) + `?cursor=`; balasan memuat `next_cursor`.

Kursor **keyset** `(waktu, id)`, bukan `OFFSET`: baris yang ditambahkan di
antara dua halaman tidak menggeser halaman berikutnya — bagi klien luring yang
menyinkron sambil pengguna terus menulis, `OFFSET` mengulang atau melompati
baris. `id` ikut di kursor karena dua baris bisa punya waktu yang sama persis.

Kursornya opak bagi klien (base64url JSON) tetapi TIDAK ditandatangani: yang
bisa dirusak klien hanya halaman miliknya sendiri — RLS (spec/01 §11) tetap
membatasi baris pada pengguna yang dilayani. Kursor yang rusak → `400
invalid_cursor`, bukan 500.
"""

from __future__ import annotations

import base64
import binascii
import json
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Query

from .galat import GalatApi

BATAS_MAKS = 100
BATAS_BAWAAN = 50

Batas = Annotated[int, Query(ge=1, le=BATAS_MAKS, description="Jumlah baris per halaman.")]
Kursor = Annotated[
    str | None, Query(max_length=200, description="`next_cursor` dari halaman sebelumnya.")
]


def kursor_waktu(saat: datetime, id_: UUID) -> str:
    if saat.utcoffset() is None:
        raise ValueError("waktu kursor wajib berzona waktu")
    mentah = json.dumps([saat.isoformat(), str(id_)], separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(mentah).decode().rstrip("=")


def _kursor_rusak() -> GalatApi:
    return GalatApi(400, "invalid_cursor", "Kursor halaman tidak sah.")


def baca_kursor_waktu(teks: str | None) -> tuple[datetime, UUID] | None:
    """`(waktu, id)` dari `?cursor=` — `None` untuk halaman pertama."""
    if teks is None:
        return None
    try:
        mentah = base64.urlsafe_b64decode(teks + "=" * (-len(teks) % 4))
        saat_teks, id_teks = json.loads(mentah)
        saat = datetime.fromisoformat(saat_teks)
        id_ = UUID(id_teks)
    except (binascii.Error, ValueError, TypeError, UnicodeDecodeError):
        raise _kursor_rusak() from None
    if saat.utcoffset() is None:
        raise _kursor_rusak()
    return saat, id_
