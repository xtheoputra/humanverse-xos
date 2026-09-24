"""`checkins` — bagaimana hari ini terasa.

Memiliki tabel: daily_checkins · mood_entries (spec/06).
Dikerjakan: Sprint 2 (2.5–2.6) — spec/07.

Modul domain: tidak boleh mengimpor modul domain lain — komunikasinya lewat
event (spec/06 aturan 3). `energi_pada` diserahkan ke modul lain lewat titik
rakit `hvx.main` (K-23), bukan lewat impor.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .repository import energi_pada
from .routes import router
from .schemas import Checkin, Mood
from .service import mood_untuk_ekstraksi

__all__ = ["Checkin", "Mood", "energi_pada", "mood_untuk_ekstraksi", "router"]
