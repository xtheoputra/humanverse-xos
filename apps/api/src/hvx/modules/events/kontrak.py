"""Kontrak event V0 — spec/03: amplop, dan payload tiap `event_type` yang dipakai V0.

Registry di bawah adalah UJI ADMISI saat terbit (arch/11 E-3, tugas 3.1): event
yang jenisnya tidak terdaftar, payload-nya tidak berbentuk kontraknya, atau
sumbernya bukan salah satu dari empat sumber spec/03 — DITOLAK sebelum menyentuh
basis data. `tests/unit/test_kontrak_event.py` menuntut registry ini SAMA
dengan baris ✅ tabel spec/03, jadi nama dan bentuknya tidak bisa menyimpang
diam-diam dari dokumennya.

* **Produsen ketat, konsumen longgar** (spec/03 aturan 3): payload yang
  diterbitkan ditolak kalau membawa medan yang tidak dikenal (`extra="forbid"`);
  konsumen wajib mengabaikan medan yang tidak dikenalnya.
* **Isi jurnal tidak pernah masuk event** — `journal.created` hanya membawa
  `word_count` (spec/03). Model payload-nya menolak medan lain.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Sumber = Literal["app", "agent", "integration", "backfill"]
# spec/01 `events.source` CHECK — `sensor` tidak pernah (arch/11 E-3): aliran
# sensor diringkas dulu, dan ringkasannya diterbitkan sumber yang meringkasnya.
SUMBER: frozenset[str] = frozenset({"app", "agent", "integration", "backfill"})


class _Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class HabitDibuat(_Payload):
    title: str
    period: Literal["day", "week", "month"]
    target_count: int


class HabitSelesai(_Payload):
    status: Literal["done", "partial"]
    tier_used: int | None = None
    note: str | None = None


class HabitDilewati(_Payload):
    reason: str | None = None


class MoodDicatat(_Payload):
    valence: Annotated[int, Field(ge=1, le=5)]
    label: str | None = None


class JurnalDibuat(_Payload):
    word_count: Annotated[int, Field(ge=0)]


class GoalDibuat(_Payload):
    title: str
    domain: str | None = None
    target_date: date | None = None


class GoalTercapai(_Payload):
    days_taken: Annotated[int, Field(ge=0)]


class CheckinDicatat(_Payload):
    energy: int | None = None
    focus: int | None = None
    sleep_hours: Decimal | None = None


# event_type → (schema_version, model payload). Hanya jenis ✅ V0 spec/03.
REGISTRY: dict[str, tuple[int, type[_Payload]]] = {
    "habit.created": (1, HabitDibuat),
    "habit.completed": (1, HabitSelesai),
    "habit.skipped": (1, HabitDilewati),
    "mood.logged": (1, MoodDicatat),
    "journal.created": (1, JurnalDibuat),
    "goal.created": (1, GoalDibuat),
    "goal.completed": (1, GoalTercapai),
    "checkin.logged": (1, CheckinDicatat),
}


class EventTidakSah(ValueError):
    """Event yang tidak lulus uji admisi — ditolak sebelum menyentuh basis data."""


def payload_sah(event_type: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """(schema_version, payload dalam bentuk JSON) — atau `EventTidakSah`."""
    if event_type not in REGISTRY:
        raise EventTidakSah(f"event_type tidak terdaftar di spec/03 V0: {event_type!r}")
    versi, model = REGISTRY[event_type]
    try:
        isi = model.model_validate(payload)
    except ValueError as galat:
        raise EventTidakSah(f"payload {event_type} tidak sesuai kontrak spec/03") from galat
    return versi, isi.model_dump(mode="json", exclude_none=True)
