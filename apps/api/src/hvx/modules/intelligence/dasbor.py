"""Dashboard — spec/07 6.1: *“beberapa dimensi, tiap skor punya Why”* (naskah 4 §28).

Pemilik menolak **satu angka Life Score** (§28: *“terlalu menyederhanakan manusia”*);
dashboard menyajikan beberapa dimensi, dan **setiap skor membawa Why** (§29 Explainable
AI). V0 menampilkan dimensi yang benar-benar DIUKUR — metrik `human_states` (energi,
fokus) yang dilaporkan pengguna sendiri. Sumbu lain di §28 (Finance/Social/Career/…)
belum punya ukuran yang disepakati (A-19/B-38, docs/99); menampilkannya sebagai angka
berarti mengambil posisi dalam model yang belum diputuskan pemilik — jadi tidak
ditampilkan sampai keputusan itu diambil dan datanya ada.

`intelligence` ada di atas `profile` (M-1) dan `human_states` miliknya; dibaca lewat
pintu keluar `profile.human_state_terkini`.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform, profile

from .schemas import Dasbor, Dimensi

# Label manusiawi tiap metrik V0. Metrik baru tanpa label tampil apa adanya (key-nya).
_LABEL: dict[str, str] = {"energy": "Energi", "focus": "Fokus"}


def _why(key: str, for_date: date) -> str:
    """Why untuk metrik LAPORAN-SENDIRI V0: keduanya dari check-in, bukan taksiran sistem."""
    label = _LABEL.get(key, key)
    return f"{label} yang kamu laporkan sendiri di check-in {for_date.isoformat()}."


def dimensi_dari_metrik(metrics: Mapping[str, Mapping[str, Any]], for_date: date) -> list[Dimensi]:
    """Metrik `human_states` → dimensi dashboard, tiap satu membawa Why. Urut key (stabil)."""
    dimensi: list[Dimensi] = []
    for key in sorted(metrics):
        m = metrics[key]
        dimensi.append(
            Dimensi(
                key=key,
                value=float(m["value"]),
                confidence=float(m["confidence"]),
                evidence_count=int(m["evidence_count"]),
                why=_why(key, for_date),
            )
        )
    return dimensi


async def dasbor(engine: AsyncEngine, user_id: UUID) -> Dasbor:
    """Dashboard pengguna: dimensi dari human_state terbarunya, tiap skor ber-Why."""
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        terkini = await profile.human_state_terkini(conn, user_id)
    if terkini is None:  # belum ada check-in — cold start, bukan "satu angka 0"
        return Dasbor(as_of=None, dimensions=[])
    for_date = terkini["for_date"]
    return Dasbor(as_of=for_date, dimensions=dimensi_dari_metrik(terkini["metrics"], for_date))
