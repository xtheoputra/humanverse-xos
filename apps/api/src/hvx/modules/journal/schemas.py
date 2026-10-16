"""Bentuk data `journal` — spec/04 *Catatan harian* (spec/07 3.4).

🔒 **`RingkasanJurnal` sengaja TIDAK punya medan `body`** — bukan disaring saat
dikirim. spec/04: *“`GET /journal` tidak mengembalikan `body`: mengirim seluruh
isi tulisan pribadi ke layar ringkasan adalah kebocoran yang tidak perlu.”*
Model yang tidak punya medannya tidak bisa membocorkannya karena lupa
`exclude`; kueri daftar pun tidak memilih kolomnya.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hvx.modules import platform

Judul = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=200)]
# Tulisan pribadi boleh panjang, tetapi tidak tanpa batas: satu permintaan
# tidak boleh menjadi cara menyimpan berkas besar di kolom teks.
Isi = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=100_000)]


class RingkasanJurnal(BaseModel):
    """Satu baris `GET /journal` — TANPA isi tulisan."""

    model_config = ConfigDict(frozen=True)

    id: UUID
    title: str | None
    occurred_at: datetime
    word_count: int
    created_at: datetime
    updated_at: datetime


class Jurnal(RingkasanJurnal):
    """`GET /journal/{id}` — dengan isi (spec/04)."""

    body: str


class HalamanJurnal(BaseModel):
    items: list[RingkasanJurnal]
    next_cursor: str | None


class BuatJurnal(BaseModel):
    """`POST /journal` — `id` boleh dibuat klien (spec/04: dukungan luring)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    title: Judul | None = None
    body: Isi
    occurred_at: platform.WaktuBerzona | None = None


class UbahJurnal(BaseModel):
    """`PATCH /journal/{id}` — medan yang DIKIRIM saja; `title: null` = hapus judul."""

    model_config = ConfigDict(extra="forbid")

    title: Judul | None = None
    body: Isi | None = None
    occurred_at: platform.WaktuBerzona | None = None

    @model_validator(mode="after")
    def _yang_dikirim_tidak_null(self) -> UbahJurnal:
        kosong = sorted(
            f for f in self.model_fields_set if f != "title" and getattr(self, f) is None
        )
        if kosong:
            raise ValueError(f"tidak boleh null: {', '.join(kosong)}")
        return self


def hitung_kata(isi: str) -> int:
    """Jumlah kata — dipisah spasi. ⚠️ Untuk aksara tanpa spasi (CJK) ini menghitung
    kalimat, bukan kata; `word_count` adalah satu-satunya yang event bawa (spec/03)."""
    return len(isi.split())
