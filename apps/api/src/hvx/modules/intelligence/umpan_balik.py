"""Umpan balik rekomendasi — spec/07 5.6: *“`modified` dan `snoozed` tidak dihitung
sebagai penolakan”*.

Satu rute tulis (`POST /recommendations/{id}/feedback`) melakukan DUA hal dalam SATU
transaksi (K-37): menambah baris `recommendation_feedback` (append-only) dan
memperbarui `recommendations.status`. Peta statusnya menegakkan butir intinya:

| action | status rekomendasi |
|---|---|
| `accepted` | → `accepted` |
| `rejected` | → `rejected` |
| `modified` · `snoozed` · `ignored` | **tidak disentuh** — bukan penolakan |

Memilih B setelah disarankan A bukan penolakan; menunda bukan mengabaikan (naskah 4
§24, spec/01 §7). Jadi `modified`/`snoozed`/`ignored` tercatat sebagai bukti umpan
balik, tetapi rekomendasinya tetap pada statusnya — pengguna masih bisa menerimanya
nanti.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from . import repository
from .schemas import CatatUmpanBalik, UmpanBalik

# Hanya accepted/rejected MENGUBAH status; sisanya membiarkannya (K-37).
_STATUS_BARU: dict[str, str] = {"accepted": "accepted", "rejected": "rejected"}


def status_sesudah(status_kini: str, action: str) -> str:
    """Status rekomendasi SESUDAH satu umpan balik — modified/snoozed/ignored ≠ rejected."""
    return _STATUS_BARU.get(action, status_kini)


async def catat_umpan_balik(
    engine: AsyncEngine, user_id: UUID, rekomendasi_id: UUID, badan: CatatUmpanBalik
) -> UmpanBalik:
    """Catat umpan balik dan sesuaikan status rekomendasi — satu transaksi (K-37)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        status_kini = await repository.status_rekomendasi(conn, rekomendasi_id)
        if status_kini is None:
            raise platform.GalatApi(404, "recommendation_not_found", "rekomendasi tidak ditemukan")
        hasil = await repository.sisip_umpan_balik(
            conn,
            rekomendasi_id=rekomendasi_id,
            user_id=user_id,
            action=badan.action,
            reason=badan.reason,
            outcome=badan.outcome,
        )
        baru = status_sesudah(status_kini, badan.action)
        if baru != status_kini:
            await repository.set_status_rekomendasi(conn, rekomendasi_id, user_id, baru)
        return hasil


async def baca_umpan_balik(
    engine: AsyncEngine, user_id: UUID, feedback_id: UUID
) -> UmpanBalik | None:
    """Umpan balik itu SEKARANG — pemutaran ulang Idempotency-Key (platform.idempotensi)."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        return await repository.umpan_balik_id(conn, feedback_id)
