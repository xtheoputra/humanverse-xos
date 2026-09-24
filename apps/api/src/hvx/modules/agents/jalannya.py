"""Satu run agent — konteks tiap pemanggilan tool dan model, dan bahan jejak auditnya.

Yang dikumpulkan di sini menjadi satu baris `agent_runs` (spec/01 §8, spec/07 4.4):
tool yang dipakai, scope memori yang disentuh, risiko tertinggi, model, token, biaya.
Naskah 5 §24: *metadata audit — bukan hidden chain-of-thought mentah*; tidak ada
medan di sini untuk menyimpan penalaran, dan itu disengaja.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal
from uuid import UUID

from hvx.modules import platform

from .registri import Manifest

Pemicu = Literal["user", "schedule", "event", "agent"]


@dataclass
class Jalannya:
    id: UUID
    user_id: UUID
    agent: Manifest
    pemicu: Pemicu
    induk: Jalannya | None = None
    percakapan_id: UUID | None = None
    # Baris `agent_runs`-nya sudah ada (4.4) — rujukan (FK) ke run ini baru sah sesudahnya.
    tersimpan: bool = False
    alat_dipakai: list[str] = field(default_factory=list)
    scope_dipakai: set[str] = field(default_factory=set)
    risiko_tertinggi: int | None = None
    dikonfirmasi: bool | None = None
    model_dipakai: list[str] = field(default_factory=list)
    token_masuk: int = 0
    token_keluar: int = 0
    biaya_usd: Decimal = field(default_factory=lambda: Decimal("0"))

    def catat_alat(self, nama: str, risiko: int) -> None:
        if nama not in self.alat_dipakai:
            self.alat_dipakai.append(nama)
        self.risiko_tertinggi = max(risiko, self.risiko_tertinggi or 0)

    def catat_scope(self, *scope: str) -> None:
        self.scope_dipakai.update(scope)

    def catat_model(self, jawaban: platform.JawabanModel) -> None:
        if jawaban.model not in self.model_dipakai:
            self.model_dipakai.append(jawaban.model)
        self.token_masuk += jawaban.token_masuk
        self.token_keluar += jawaban.token_keluar
        self.biaya_usd += jawaban.biaya_usd
