"""Teks bebas dari klien yang akan disimpan PostgreSQL — tanpa karakter NUL.

PostgreSQL menolak `\\x00` di `text` dan `\\u0000` di `jsonb`. Tanpa penjaga ini
nilai itu lolos validasi, lalu gagal di basis data sebagai **500** — jawaban
galat server untuk masukan klien yang salah bentuk, dan satu baris
`request.failed` di log untuk tiap percobaan (tinjauan Sprint 1: `PATCH
/v1/me/profile` dengan NUL di `display_name`).

Kenapa di `platform`: bentuk data, bukan aturan domain — `identity` (daftar) dan
`profile` sama-sama menerimanya, dan keduanya tidak boleh saling mengimpor (K-17).
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import AfterValidator

_NUL = "\x00"
_PESAN = "tidak boleh memuat karakter NUL"


def _tanpa_nul(nilai: str) -> str:
    if _NUL in nilai:
        raise ValueError(_PESAN)  # nilainya tidak dikutip — galat tidak memantulkan masukan
    return nilai


def tanpa_nul_bersarang(nilai: Any) -> Any:
    """Kunci dan nilai teks di dalam struktur yang disimpan sebagai `jsonb`."""
    if isinstance(nilai, str):
        _tanpa_nul(nilai)
    elif isinstance(nilai, dict):
        for kunci, isi in nilai.items():
            _tanpa_nul(str(kunci))
            tanpa_nul_bersarang(isi)
    elif isinstance(nilai, list):
        for isi in nilai:
            tanpa_nul_bersarang(isi)
    return nilai


TeksTanpaNul = Annotated[str, AfterValidator(_tanpa_nul)]
