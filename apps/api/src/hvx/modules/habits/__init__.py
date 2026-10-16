"""`habits` — apa yang dilakukan berulang.

Memiliki tabel: habits · habit_completions (spec/06).
Dikerjakan: Sprint 2 (2.2–2.4) — spec/07.

Modul domain: tidak boleh mengimpor modul domain lain — komunikasinya lewat
event (spec/06 aturan 3), atau lewat pembaca/pendengar yang disambung titik
rakit `hvx.main` di transaksi yang sama (K-23): zona waktu profil, energi
check-in, goal yang hidup — dan `lepas_goal` saat goal dihapus.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .rentetan import Rentetan, hitung_rentetan
from .routes import router
from .schemas import CatatPenyelesaian, Habit
from .service import (
    PembacaEnergi,
    PembacaGoalHidup,
    PembacaZonaWaktu,
    habit_pada,
    lepas_goal,
    rentetan_pada,
)

# Jalur tool agent (spec/05 habit.list · habit.streak · habit.complete, spec/07 4.3).
from .service import catat as catat_penyelesaian
from .service import daftar as daftar_habit
from .service import rentetan as rentetan_habit
from .tier import tier_untuk_energi

__all__ = [
    "CatatPenyelesaian",
    "Habit",
    "PembacaEnergi",
    "PembacaGoalHidup",
    "PembacaZonaWaktu",
    "Rentetan",
    "catat_penyelesaian",
    "daftar_habit",
    "habit_pada",
    "hitung_rentetan",
    "lepas_goal",
    "rentetan_habit",
    "rentetan_pada",
    "router",
    "tier_untuk_energi",
]
