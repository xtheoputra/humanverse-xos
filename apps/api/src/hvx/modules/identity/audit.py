"""`audit()` — spec/07 tugas 1.6: jejak bahwa sesuatu TERJADI, bukan isinya.

Aturan yang dipegang, dan dari mana:

* **Tidak menyimpan isi** (spec/02 aturan F): `metadata` hanya menerima nilai
  skalar pendek — id, nama aksi, angka. Isi jurnal, pesan, atau memori tidak
  punya tempat di sini, dan panjang nilai dibatasi supaya ia tidak bisa
  diselundupkan sebagai string.
* **Hanya-tambah** (B-40): peran aplikasi tidak punya `UPDATE`/`DELETE` atas
  `audit_logs` — ditegakkan basis data, bukan fungsi ini (spec/01 §10).
* **`data_subject` sifat baris**: baris dengan `user_id` milik pengguna itu,
  tanpa `user_id` milik sistem. RLS (spec/01 §11) hanya meloloskan baris
  sistem atau baris pengguna yang sedang dilayani transaksi.
* **`request_id` dari konteks log** (tugas 0.5), supaya baris audit dan baris
  log satu permintaan bisa dipertemukan tanpa diteruskan tangan.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Literal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncConnection

from . import repository

AktorTipe = Literal["user", "agent", "system", "admin"]
NilaiMetadata = str | int | bool | None

_POLA_AKSI = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
_PANJANG_NILAI_MAKS = 120
_KUNCI_MAKS = 20


class AuditTidakSah(ValueError):
    """Baris audit yang melanggar bentuknya — ditolak sebelum menyentuh basis data."""


def _periksa(aksi: str, metadata: Mapping[str, NilaiMetadata]) -> None:
    if not _POLA_AKSI.fullmatch(aksi):
        raise AuditTidakSah(f"aksi audit wajib `domain.kata_kerja`, bukan {aksi!r}")
    if len(metadata) > _KUNCI_MAKS:
        raise AuditTidakSah(f"metadata audit maksimal {_KUNCI_MAKS} kunci")
    for kunci, nilai in metadata.items():
        if not isinstance(nilai, str | int | bool) and nilai is not None:
            raise AuditTidakSah(
                f"metadata `{kunci}`: hanya nilai skalar, bukan {type(nilai).__name__}"
            )
        if isinstance(nilai, str) and len(nilai) > _PANJANG_NILAI_MAKS:
            raise AuditTidakSah(
                f"metadata `{kunci}`: {len(nilai)} karakter — audit menyimpan bahwa sesuatu "
                "terjadi, bukan isinya (spec/02 aturan F)"
            )


async def audit(
    conn: AsyncConnection,
    *,
    aksi: str,
    aktor_tipe: AktorTipe,
    aktor_id: str,
    user_id: UUID | None,
    subjek_tipe: str | None = None,
    subjek_id: str | None = None,
    ip_hash: str | None = None,
    metadata: Mapping[str, NilaiMetadata] | None = None,
) -> None:
    """Tambahkan satu baris `audit_logs` di transaksi `conn` — gagal kalau transaksinya gagal.

    Ditulis di transaksi yang SAMA dengan perubahan yang dicatatnya: perubahan
    tanpa jejak, atau jejak tanpa perubahan, sama-sama tidak boleh terjadi.
    """
    isi = dict(metadata or {})
    _periksa(aksi, isi)
    await repository.tambah_audit(
        conn,
        data_subject="user" if user_id is not None else "system",
        aktor_tipe=aktor_tipe,
        aktor_id=aktor_id,
        user_id=user_id,
        aksi=aksi,
        subjek_tipe=subjek_tipe,
        subjek_id=subjek_id,
        request_id=structlog.contextvars.get_contextvars().get("request_id"),
        ip_hash=ip_hash,
        metadata=isi,
    )
