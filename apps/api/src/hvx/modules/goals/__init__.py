"""`goals` — apa yang ingin dicapai.

Memiliki tabel: goals · goal_milestones (spec/06).
Dikerjakan: Sprint 2 (2.1) — spec/07.

Modul domain: tidak boleh mengimpor modul domain lain — komunikasinya lewat
event (spec/06 aturan 3), atau lewat pembaca/pendengar yang disambung titik
rakit `hvx.main` di transaksi yang sama (K-17, K-23): `kunci_goal_hidup` untuk
modul yang menaut goal, `PendengarGoalDihapus` untuk yang harus melepasnya.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .privasi import BAGIAN_PRIVASI, PENGHAPUS_PRIVASI
from .routes import router
from .schemas import Goal, GoalRinci, Milestone, SimpulPohon, StatusGoal
from .service import MAKS_GOAL, MAKS_MILESTONE, PendengarGoalDihapus, kunci_goal_hidup
from .service import daftar as daftar_goal  # tool goal.list (spec/07 4.3)

__all__ = [
    "BAGIAN_PRIVASI",
    "MAKS_GOAL",
    "MAKS_MILESTONE",
    "PENGHAPUS_PRIVASI",
    "Goal",
    "GoalRinci",
    "Milestone",
    "PendengarGoalDihapus",
    "SimpulPohon",
    "StatusGoal",
    "daftar_goal",
    "kunci_goal_hidup",
    "router",
]
