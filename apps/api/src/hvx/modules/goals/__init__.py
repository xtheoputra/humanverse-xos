"""`goals` — apa yang ingin dicapai.

Memiliki tabel: goals · goal_milestones (spec/06).
Dikerjakan: Sprint 2 (2.1) — spec/07.

Modul domain: tidak boleh mengimpor modul domain lain — komunikasinya lewat
event (spec/06 aturan 3).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .routes import router
from .schemas import Goal, GoalRinci, Milestone, SimpulPohon

__all__ = ["Goal", "GoalRinci", "Milestone", "SimpulPohon", "router"]
