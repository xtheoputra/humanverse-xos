"""Persetujuan & pembatasan tujuan — spec/07 tugas 1.4, B-22 (#59), naskah 12 §8.9–§8.10.

Selesai bila: riwayat append-only; pencabutan = baris baru; uji:
`data.purpose ⊆ consent.purpose` ditegakkan.

* **Hanya-tambah** ditegakkan basis data: peran aplikasi tidak punya
  `UPDATE`/`DELETE` atas `consents` (spec/01 §10). Fungsi di sini hanya bisa
  MENAMBAH baris; mencabut = menambah baris `granted = false`.
* **Pembatasan tujuan** (§8.10 — *“data boleh digunakan untuk tujuan yang
  diizinkan, bukan semua tujuan yang secara teknis memungkinkan”*) menjadi
  `boleh_dipakai_untuk()`: tiap tujuan butuh persetujuan TERAKHIR untuk tujuan
  itu yang diberikan, belum kedaluwarsa, dan mencakup data yang dipakai.
  Tujuan tanpa riwayat sama sekali = DITOLAK, bukan "belum ditanya maka boleh".
* **Kosakata tujuan tidak diputuskan di sini** (#59 butir 2 — milik pemilik):
  bentuknya `snake_case` (`CHECK` spec/01), isinya bebas.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from . import repository
from .audit import audit

_POLA_TUJUAN = re.compile(r"^[a-z][a-z0-9_]{0,62}$")

# Tujuan yang dicatat saat pendaftaran (tugas 1.1). `service` = menyediakan
# layanan itu sendiri; `model_training` = melatih model (B-22) — persetujuan
# TERSENDIRI yang boleh ditolak tanpa mengurangi layanan.
TUJUAN_LAYANAN = "service"
TUJUAN_PELATIHAN_MODEL = "model_training"


class PersetujuanTidakSah(ValueError):
    """Bentuk persetujuan yang tidak boleh dicatat."""


@dataclass(frozen=True)
class Persetujuan:
    kind: str
    purpose: str
    granted: bool
    policy_version: str
    data_scopes: frozenset[str] = field(default_factory=frozenset)
    expires_at: datetime | None = None
    source: Literal["app", "import", "admin"] = "app"

    def __post_init__(self) -> None:
        if not _POLA_TUJUAN.fullmatch(self.purpose):
            raise PersetujuanTidakSah(f"purpose wajib snake_case: {self.purpose!r}")
        if not self.kind or not self.policy_version:
            raise PersetujuanTidakSah("kind dan policy_version wajib diisi")
        if len(self.kind) > 64 or len(self.policy_version) > 64:
            raise PersetujuanTidakSah("kind dan policy_version maksimal 64 karakter")
        tak_sah = sorted(c for c in self.data_scopes if not _POLA_TUJUAN.fullmatch(c))
        if tak_sah:
            raise PersetujuanTidakSah(f"data_scopes wajib snake_case: {tak_sah}")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise PersetujuanTidakSah("expires_at wajib berzona waktu (timestamptz, UTC)")


async def catat_persetujuan(
    conn: AsyncConnection,
    user_id: UUID,
    persetujuan: Persetujuan,
    *,
    ip_hash: str | None = None,
) -> None:
    """Tambah SATU baris riwayat + jejak audit, di transaksi yang sama."""
    await _tambah(conn, user_id, persetujuan, dicabut=False)
    await audit(
        conn,
        aksi="consent.granted" if persetujuan.granted else "consent.declined",
        aktor_tipe="user",
        aktor_id=str(user_id),
        user_id=user_id,
        subjek_tipe="consent",
        subjek_id=persetujuan.purpose,
        ip_hash=ip_hash,
        metadata={"kind": persetujuan.kind, "policy_version": persetujuan.policy_version},
    )


async def cabut_persetujuan(
    conn: AsyncConnection,
    user_id: UUID,
    *,
    kind: str,
    purpose: str,
    policy_version: str,
    ip_hash: str | None = None,
) -> None:
    """Pencabutan = baris BARU `granted = false` — riwayat lama tidak disentuh."""
    await _tambah(
        conn,
        user_id,
        Persetujuan(kind=kind, purpose=purpose, granted=False, policy_version=policy_version),
        dicabut=True,
    )
    await audit(
        conn,
        aksi="consent.revoked",
        aktor_tipe="user",
        aktor_id=str(user_id),
        user_id=user_id,
        subjek_tipe="consent",
        subjek_id=purpose,
        ip_hash=ip_hash,
        metadata={"kind": kind, "policy_version": policy_version},
    )


async def _tambah(conn: AsyncConnection, user_id: UUID, p: Persetujuan, *, dicabut: bool) -> None:
    await repository.tambah_persetujuan(
        conn,
        user_id=user_id,
        kind=p.kind,
        purpose=p.purpose,
        data_scopes=sorted(p.data_scopes),
        granted=p.granted,
        dicabut=dicabut,
        policy_version=p.policy_version,
        source=p.source,
        expires_at=p.expires_at,
    )


async def boleh_dipakai_untuk(
    conn: AsyncConnection,
    user_id: UUID,
    tujuan: Iterable[str],
    cakupan_data: Iterable[str] = (),
) -> bool:
    """`data.purpose ⊆ consent.purpose` — semua tujuan harus lolos, satu gagal = tolak.

    `tujuan` kosong DITOLAK: "memakai data untuk tidak ada tujuan" bukan
    pertanyaan yang boleh dijawab ya.
    """
    diminta = frozenset(tujuan)
    cakupan = frozenset(cakupan_data)
    if not diminta:
        return False
    terakhir = await repository.persetujuan_terakhir(conn, user_id, sorted(diminta))
    for t in diminta:
        if t not in terakhir:
            return False
        diberikan, cakupan_disetujui, masih_berlaku = terakhir[t]
        if not (diberikan and masih_berlaku and cakupan <= cakupan_disetujui):
            return False
    return True
