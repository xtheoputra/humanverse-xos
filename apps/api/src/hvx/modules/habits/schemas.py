"""Bentuk data `habits` — spec/04 *Goals & habits* (spec/07 2.2–2.4)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from hvx.modules import platform

# Sama dengan CHECK spec/01 — salah ketik menjadi 400, bukan 500.
Periode = Literal["day", "week", "month"]
StatusHabit = Literal["active", "paused", "archived"]
StatusSelesai = Literal["done", "skipped", "partial"]

Judul = Annotated[platform.TeksBerisi, Field(min_length=1, max_length=200)]
Catatan = Annotated[platform.TeksTanpaNul, Field(max_length=1000)]

# Berapa kali sebuah periode BISA dipenuhi: satu baris penyelesaian per tanggal
# (`UNIQUE (habit_id, for_date)`), jadi "3× sehari" tidak bisa dicatat, dan
# "8× seminggu" tidak pernah terpenuhi.
TARGET_MAKS: dict[str, int] = {"day": 1, "week": 7, "month": 31}
TIER_MAKS = 5


def periksa_target(period: str, target_count: int) -> None:
    maks = TARGET_MAKS[period]
    if not 1 <= target_count <= maks:
        raise ValueError(
            f"target_count untuk period '{period}' wajib 1–{maks}: satu tanggal satu "
            "penyelesaian (spec/01 UNIQUE (habit_id, for_date))"
        )


def periksa_jadwal(period: str, schedule: dict[str, Any]) -> None:
    if schedule.get("weekdays") and period != "day":
        raise ValueError(
            "schedule.weekdays hanya untuk period 'day' — habit mingguan/bulanan "
            "dihitung per periode, bukan per hari yang dijadwalkan"
        )


class Jadwal(BaseModel):
    """`schedule` spec/01: `{"weekdays":[1,3,5],"time":"18:00"}` — ISO: 1 = Senin, 7 = Minggu."""

    model_config = ConfigDict(extra="forbid")

    weekdays: list[Annotated[int, Field(ge=1, le=7)]] | None = Field(
        default=None, min_length=1, max_length=7
    )
    time: str | None = Field(default=None, pattern=r"^([01][0-9]|2[0-3]):[0-5][0-9]$")

    @field_validator("weekdays")
    @classmethod
    def _unik_terurut(cls, nilai: list[int] | None) -> list[int] | None:
        if nilai is not None and nilai != sorted(set(nilai)):
            raise ValueError("weekdays wajib unik dan terurut naik")
        return nilai


class Tier(BaseModel):
    """Satu tingkat Adaptive Habit Engine naskah 4 §34 — indeks 0 versi penuh."""

    model_config = ConfigDict(extra="forbid")

    label: Annotated[platform.TeksBerisi, Field(min_length=1, max_length=100)]
    minutes: int | None = Field(default=None, ge=1, le=1440)


class Habit(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    goal_id: UUID | None
    title: str
    period: Periode
    target_count: int
    schedule: dict[str, Any]
    adaptive_tiers: list[dict[str, Any]]
    status: StatusHabit
    created_at: datetime
    updated_at: datetime


class BuatHabit(BaseModel):
    """`POST /habits` — spec/04: `period` dan `target_count` WAJIB (bukan bawaan spec/01)."""

    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    title: Judul
    period: Periode
    target_count: int
    schedule: Jadwal = Field(default_factory=Jadwal)
    goal_id: UUID | None = None
    adaptive_tiers: list[Tier] = Field(default_factory=list, max_length=TIER_MAKS)

    @model_validator(mode="after")
    def _target_dan_jadwal_sesuai_periode(self) -> BuatHabit:
        periksa_target(self.period, self.target_count)
        periksa_jadwal(self.period, self.schedule.model_dump(exclude_none=True))
        return self


class UbahHabit(BaseModel):
    """`PATCH /habits/{id}` — medan yang DIKIRIM saja; kecocokan periode diperiksa
    terhadap baris yang tersimpan (service), bukan hanya terhadap badan ini."""

    model_config = ConfigDict(extra="forbid")

    title: Judul | None = None
    period: Periode | None = None
    target_count: int | None = None
    schedule: Jadwal | None = None
    goal_id: UUID | None = None  # null = lepas dari goal
    adaptive_tiers: list[Tier] | None = Field(default=None, max_length=TIER_MAKS)
    status: StatusHabit | None = None

    @model_validator(mode="after")
    def _yang_dikirim_tidak_null(self) -> UbahHabit:
        kosong = sorted(
            f for f in self.model_fields_set if f != "goal_id" and getattr(self, f) is None
        )
        if kosong:
            raise ValueError(f"tidak boleh null: {', '.join(kosong)}")
        return self


# ── spec/07 2.3 — penyelesaian ────────────────────────────────────────────────


class Penyelesaian(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    habit_id: UUID
    for_date: date
    status: StatusSelesai
    tier_used: int | None
    note: str | None
    source: str
    completed_at: datetime
    created_at: datetime


class CatatPenyelesaian(BaseModel):
    """`POST /habits/{id}/completions` — `for_date` tanggal LOKAL perangkat (spec/01)."""

    model_config = ConfigDict(extra="forbid")

    for_date: date
    status: StatusSelesai
    tier_used: int | None = Field(default=None, ge=0, le=TIER_MAKS - 1)
    note: Catatan | None = None

    @model_validator(mode="after")
    def _tier_hanya_untuk_yang_dijalankan(self) -> CatatPenyelesaian:
        if self.status == "skipped" and self.tier_used is not None:
            raise ValueError("tier_used tidak berarti untuk status 'skipped'")
        return self


# ── spec/07 2.2 · 2.5 — habit pada satu tanggal ──────────────────────────────


class HariHabit(BaseModel):
    """`GET /habits?for_date=` — keadaan habit pada tanggal LOKAL itu.

    `energy` ikut dikirim sebagai ALASAN `suggested_tier` (Explainable AI naskah 4
    §29): tier yang turun tanpa menyebut kenapa terbaca seperti hukuman.
    """

    for_date: date
    completion: Penyelesaian | None
    energy: int | None
    suggested_tier: int | None


class HabitHari(Habit):
    day: HariHabit | None = None


class DaftarHabit(BaseModel):
    items: list[HabitHari]


# ── spec/07 2.4 — rentetan ────────────────────────────────────────────────────


class JawabanRentetan(BaseModel):
    """spec/04 `GET /habits/{id}/streak` → `{ current, longest, completion_rate_30d }`."""

    current: int
    longest: int
    completion_rate_30d: float | None
