"""Menerbitkan event — spec/07 3.1: amplop + idempotensi; *“event ganda ditelan sebagai sukses”*.

* **Di transaksi PEMANGGIL** (`conn` dari `platform.transaksi_pengguna`): tulisan
  domain dan event-nya commit bersama atau tidak sama sekali. Tabel `events`
  adalah kotak keluar (*outbox*) — relay ke Redis Streams (3.3) membacanya
  sesudah commit, jadi tidak ada event yang terbit untuk tulisan yang batal,
  dan tidak ada tulisan yang lolos tanpa event-nya (spec/06 aturan 6).
* **Uji admisi** (arch/11 E-3): jenis dari registry V0, payload berbentuk
  kontraknya, sumber salah satu dari empat — `kontrak.py`.
* **Idempoten** (spec/03 aturan 1): kunci yang sama → event yang SAMA dipulangkan
  (`baru=False`), bukan galat. Tetapi kunci yang sama untuk kejadian yang BERBEDA
  (jenis, subjek, atau payload lain) adalah cacat produsen — kuncinya tidak
  mengidentifikasi kejadian — dan ditolak keras, bukan ditelan diam-diam.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection

from . import repository
from .kontrak import SUMBER, EventTidakSah, Sumber, payload_sah

# `habit-completion:<uuid>` · `goal:<uuid>:created` · `checkin:2026-09-24:<sidik>`
_POLA_KUNCI = re.compile(r"^[a-z][a-z0-9-]{0,39}:[A-Za-z0-9:._+-]{1,200}$")
_POLA_SUBJEK = re.compile(r"^[a-z][a-z_]{0,39}$")


@dataclass(frozen=True)
class HasilTerbit:
    id: UUID
    baru: bool  # False = kunci itu sudah terbit; event lama yang dipulangkan


async def terbitkan(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    event_type: str,
    occurred_at: datetime,
    idempotency_key: str,
    payload: dict[str, Any],
    subject_type: str | None = None,
    subject_id: UUID | None = None,
    source: Sumber = "app",
) -> HasilTerbit:
    if not isinstance(user_id, UUID):
        raise TypeError(f"user_id wajib uuid.UUID, bukan {type(user_id).__name__}")
    if occurred_at.utcoffset() is None:
        raise EventTidakSah("occurred_at wajib berzona waktu (spec/03: UTC)")
    if source not in SUMBER:
        raise EventTidakSah(f"source di luar spec/03: {source!r}")
    if not _POLA_KUNCI.fullmatch(idempotency_key):
        raise EventTidakSah("idempotency_key wajib `jenis:identitas` (spec/03 aturan 1)")
    if subject_type is not None and not _POLA_SUBJEK.fullmatch(subject_type):
        raise EventTidakSah("subject_type wajib snake_case")
    versi, isi = payload_sah(event_type, payload)

    baru = await repository.sisip(
        conn,
        user_id=user_id,
        event_type=event_type,
        schema_version=versi,
        occurred_at=occurred_at,
        source=source,
        kunci=idempotency_key,
        subject_type=subject_type,
        subject_id=subject_id,
        payload=isi,
    )
    if baru is not None:
        return HasilTerbit(baru, baru=True)

    lama = await repository.menurut_kunci(conn, user_id, idempotency_key)
    if lama is None:  # pragma: no cover - DO NOTHING berarti barisnya ada (dan terlihat RLS)
        raise RuntimeError("event dengan kunci itu tidak terbaca kembali")
    sama = (
        lama.event_type == event_type
        and lama.subject_type == subject_type
        and lama.subject_id == subject_id
        and json.dumps(lama.payload, sort_keys=True) == json.dumps(isi, sort_keys=True)
    )
    if not sama:
        raise EventTidakSah(
            "idempotency_key yang sama untuk kejadian yang berbeda — kuncinya tidak "
            "mengidentifikasi kejadian (spec/03 aturan 1)"
        )
    return HasilTerbit(lama.id, baru=False)
