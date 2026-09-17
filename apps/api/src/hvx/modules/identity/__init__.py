"""`identity` — siapa pengguna ini, dan apa yang ia izinkan.

Memiliki tabel: users · consents · permissions · audit_logs (spec/06).
Dikerjakan: Sprint 1 (1.1–1.7) — spec/07.

Semua modul boleh mengimpornya untuk cek izin (spec/06). Pengguna MANUSIA —
identitas agent tinggal di `agents` (arch/03 §5).

Berkas ini satu-satunya pintu keluar modul (spec/06 aturan 1).
"""

from .audit import AktorTipe, AuditTidakSah, audit

__all__ = ["AktorTipe", "AuditTidakSah", "audit"]
