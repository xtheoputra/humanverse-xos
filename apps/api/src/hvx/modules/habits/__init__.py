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
from .schemas import Habit
from .service import PembacaEnergi, PembacaGoalHidup, PembacaZonaWaktu, lepas_goal
from .tier import tier_untuk_energi

__all__ = [
    "Habit",
    "PembacaEnergi",
    "PembacaGoalHidup",
    "PembacaZonaWaktu",
    "Rentetan",
    "hitung_rentetan",
    "lepas_goal",
    "router",
    "tier_untuk_energi",
]
