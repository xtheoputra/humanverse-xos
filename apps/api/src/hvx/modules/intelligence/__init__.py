"""`intelligence` — apa yang disimpulkan dan disarankan.

Memiliki tabel: recommendations · recommendation_feedback (spec/06).
Dikerjakan: Sprint 5 (5.1–5.6) — spec/07.

Sejak spec/07 4.3: `buat_rekomendasi` — jalur tool `recommendation.create`.

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .rekomendasi import DOMAIN, buat_rekomendasi, periksa_rekomendasi

__all__ = ["DOMAIN", "buat_rekomendasi", "periksa_rekomendasi"]
