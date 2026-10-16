"""Jalur deterministik — spec/07 4.1: perintah berbentuk tetap dijalankan layanan, TANPA model.

Naskah 5 §22: *“Catat mood saya” → deterministic* — mencatat mood adalah
`INSERT`, bukan inferensi. Ini **service**, bukan agent (K-5): satu langkah tetap,
tidak memilih tool, dan tidak butuh gerbang risiko — yang bertindak adalah
pengguna sendiri lewat kalimatnya, persis seperti `POST /moods`. Mood yang
dicatat menerbitkan `mood.logged` di transaksinya (3.2), sama dengan jalur HTTP.

Tidak ada `GerbangModel` di tanda tangan fungsi ini — jalur yang tidak bisa
memanggil model tidak bisa memanggil model besar.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import checkins, platform

from .niat import Niat

CARA_MENGISI_MOOD = (
    "Mood diisi angka 1 (terburuk) sampai 5 (terbaik), boleh dengan satu kata dan catatan — "
    "mis. “catat mood 3 cemas, rapat seharian”."
)


@dataclass(frozen=True)
class HasilDeterministik:
    teks: str
    mood_id: UUID | None = None


async def jalankan_deterministik(
    engine: AsyncEngine, user_id: UUID, niat: Niat, *, mood_id: UUID | None = None
) -> HasilDeterministik:
    """Jalankan niat `deterministic`. `mood_id` tetap untuk pesan yang dikirim ulang:
    mood yang sama tidak tercatat dua kali (`POST /moods` menolak id kembar)."""
    if niat.jenis != "catat_mood" or niat.mood is None:
        return HasilDeterministik(CARA_MENGISI_MOOD)
    try:
        badan = checkins.CatatMood(
            id=mood_id, valence=niat.mood.valensi, label=niat.mood.label, note=niat.mood.catatan
        )
    except ValidationError:
        return HasilDeterministik(CARA_MENGISI_MOOD)  # mis. catatan > 4.000 karakter
    teks = f"Mood {niat.mood.valensi}/5" + (f" ({niat.mood.label})" if niat.mood.label else "")
    try:
        mood = await checkins.catat_mood(engine, user_id, badan)
    except platform.GalatApi as galat:
        if galat.kode != "already_exists" or mood_id is None:
            raise
        return HasilDeterministik(f"{teks} sudah dicatat.", mood_id)  # kiriman ulang
    return HasilDeterministik(f"{teks} dicatat.", mood.id)
