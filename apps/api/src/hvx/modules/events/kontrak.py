"""Kontrak event V0 — spec/03: amplop, dan payload tiap `event_type` yang dipakai V0.

Registry di bawah adalah UJI ADMISI saat terbit (arch/11 E-3, tugas 3.1): event
yang jenisnya tidak terdaftar, payload-nya tidak berbentuk kontraknya, atau
sumbernya bukan salah satu dari empat sumber spec/03 — DITOLAK sebelum menyentuh
basis data. `tests/unit/test_kontrak_event.py` menuntut registry ini SAMA
dengan baris ✅ tabel spec/03, jadi nama dan bentuknya tidak bisa menyimpang
diam-diam dari dokumennya.

* **Produsen ketat, konsumen longgar** (spec/03 aturan 3): payload yang
  diterbitkan ditolak kalau membawa medan yang tidak dikenal (`extra="forbid"`)
  **atau bertipe lain** (`strict=True`) — `True` bukan valensi, `"3"` bukan
  angka, `"2026-09-24"` bukan tanggal: kelas galat E-170 di sisi penerbit, yang
  versi pertama loloskan (tinjauan kontrak Sprint 3, K7). Konsumen wajib
  mengabaikan medan yang tidak dikenalnya.
* **Isi jurnal tidak pernah masuk event** — `journal.created` hanya membawa
  `word_count` (spec/03). Model payload-nya menolak medan lain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Sumber = Literal["app", "agent", "integration", "backfill"]
# spec/01 `events.source` CHECK — `sensor` tidak pernah (arch/11 E-3): aliran
# sensor diringkas dulu, dan ringkasannya diterbitkan sumber yang meringkasnya.
SUMBER: frozenset[str] = frozenset({"app", "agent", "integration", "backfill"})


class _Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class HabitDibuat(_Payload):
    title: str
    period: Literal["day", "week", "month"]
    target_count: int


class HabitSelesai(_Payload):
    status: Literal["done", "partial"]
    tier_used: int | None = None
    note: str | None = None
    # spec/03 🔧 3.2 — tanpa keduanya proyeksi `habit_completions` (spec/02
    # aturan D) tidak bisa dibangun ulang: tanggal LOKAL, dan baris yang dicatat.
    for_date: date
    completion_id: UUID


class HabitDilewati(_Payload):
    reason: str | None = None
    for_date: date
    completion_id: UUID


class PenyelesaianDicabut(_Payload):
    """`habit.completion_retracted` 🔧 (E-178) — penyelesaian yang DIBATALKAN pengguna."""

    for_date: date
    completion_id: UUID


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
    sleep_hours: float | None = None  # angka JSON, seperti spec/04 (E-170) — bukan "7.5"
    for_date: date  # spec/03 🔧 3.2 — tanggal lokal check-in itu


# event_type → (schema_version, model payload). Hanya jenis ✅ V0 spec/03.
REGISTRY: dict[str, tuple[int, type[_Payload]]] = {
    "habit.created": (1, HabitDibuat),
    "habit.completed": (1, HabitSelesai),
    "habit.skipped": (1, HabitDilewati),
    "habit.completion_retracted": (1, PenyelesaianDicabut),
    "mood.logged": (1, MoodDicatat),
    "journal.created": (1, JurnalDibuat),
    "goal.created": (1, GoalDibuat),
    "goal.completed": (1, GoalTercapai),
    "checkin.logged": (1, CheckinDicatat),
}


@dataclass(frozen=True)
class Admisi:
    """Uji admisi `events` (arch/06 §3) untuk SATU jenis — bagian yang bisa dibaca mesin.

    Syarat 1 (*pengguna bisa mengenalinya*) ditulis sebagai kalimat di tabel *Uji admisi
    per event* spec/03; syarat 2 dan 3 di sini, supaya penerbit menegakkannya saat terbit:

    * `kunci` — templat `idempotency_key` aturan 1 spec/03 (`<…>` = identitas). Kunci yang
      berbentuk lain bukan *“pengiriman ulang berarti hal yang sama”*: `goal:<id>:created`
      untuk `mood.logged` lolos `jenis:identitas`, tetapi menelan mood berikutnya.
    * `sumber` — himpunan `source` yang sah untuk jenis ini, bagian dari `SUMBER`.

    🔴 Sebelum V1 7.1 hanya syarat 3 yang dijaga (E-3), dan hanya terhadap empat sumber
    sekaligus — `mood.logged` bersumber `agent` lolos padahal tak satu agent pun mencatat
    mood. Jenis baru yang ditambahkan ke `REGISTRY` tanpa baris di sini ditolak saat
    terbit, dan `tests/unit/test_admisi_event.py` menuntut tabel ini sama dengan spec/03.
    """

    kunci: str
    sumber: frozenset[str]

    def __post_init__(self) -> None:
        if not self.sumber or not self.sumber <= SUMBER:
            raise ValueError(f"sumber admisi di luar spec/03: {sorted(self.sumber)}")

    @property
    def pola(self) -> re.Pattern[str]:
        """Templat → regex: bagian harfiah wajib sama, tiap `<…>` satu identitas."""
        bagian = re.split(r"<[a-z_]+>", self.kunci)
        return re.compile(_IDENTITAS.join(re.escape(b) for b in bagian))


_IDENTITAS = "[A-Za-z0-9:._+-]+"
_APP = frozenset({"app"})

# event_type → uji admisi. Sama dengan aturan 1 + tabel *Uji admisi per event* spec/03.
ADMISI: dict[str, Admisi] = {
    "habit.created": Admisi("habit:<habit_id>:created", _APP),
    # habit-agent menandai selesai lewat tool `habit.complete` (E-205: event bersumber agent)
    "habit.completed": Admisi("habit-completion:<completion_id>", frozenset({"app", "agent"})),
    "habit.skipped": Admisi("habit-completion:<completion_id>", frozenset({"app", "agent"})),
    "habit.completion_retracted": Admisi("habit-completion:<completion_id>:retracted", _APP),
    "mood.logged": Admisi("mood:<mood_id>", _APP),
    "journal.created": Admisi("journal:<journal_id>", _APP),
    "goal.created": Admisi("goal:<goal_id>:created", _APP),
    "goal.completed": Admisi("goal:<goal_id>:completed:<achieved_at>", _APP),
    "checkin.logged": Admisi("checkin:<for_date>:<updated_at>", _APP),
}


class EventTidakSah(ValueError):
    """Event yang tidak lulus uji admisi — ditolak sebelum menyentuh basis data."""


def admisi_sah(event_type: str, idempotency_key: str, source: str) -> None:
    """Syarat 2 dan 3 uji admisi untuk jenis ini — atau `EventTidakSah`.

    Pesan galat tidak mengutip kuncinya: kunci memuat id dan tanggal milik pengguna."""
    admisi = ADMISI.get(event_type)
    if admisi is None:
        raise EventTidakSah(f"event_type tanpa uji admisi spec/03: {event_type!r}")
    if source not in admisi.sumber:
        raise EventTidakSah(f"source {source!r} tidak sah untuk {event_type} (spec/03)")
    if not admisi.pola.fullmatch(idempotency_key):
        raise EventTidakSah(f"idempotency_key {event_type} wajib `{admisi.kunci}` (spec/03)")


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
