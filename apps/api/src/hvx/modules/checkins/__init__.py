"""`checkins` — bagaimana hari ini terasa.

Memiliki tabel: daily_checkins · mood_entries (spec/06).
Dikerjakan: Sprint 2 (2.5–2.6) — spec/07.

Modul domain: tidak boleh mengimpor modul domain lain — komunikasinya lewat
event (spec/06 aturan 3). `energi_pada` diserahkan ke modul lain lewat titik
rakit `hvx.main` (K-23), bukan lewat impor. `catat_mood` dipakai jalur
deterministik percakapan (`agents`, spec/07 4.1) — `agents` di atas modul domain.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .repository import energi_pada
from .routes import router
from .schemas import CatatMood, Checkin, Mood
from .service import catat_mood, daftar_mood, mood_untuk_ekstraksi
from .service import daftar as daftar_checkin  # tool checkin.get (spec/07 4.3)

__all__ = [
    "CatatMood",
    "Checkin",
    "Mood",
    "catat_mood",
    "daftar_checkin",
    "daftar_mood",
    "energi_pada",
    "mood_untuk_ekstraksi",
    "router",
]
