"""Bagian `journal` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Tulisan paling pribadi pengguna (Level 3 *Sensitive*, naskah 133): yang dihitung jumlahnya,
yang diekspor isinya — ekspor adalah salinan MILIK pemiliknya (GDPR Art. 15 · 20).
Hapus kategori = hapus KERAS; memori turunannya dilupakan modul `memory` dan event
`journal.created`-nya dibuang modul `events`, di transaksi yang sama.
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "journal",
        "journal_entries",
        "SELECT count(*) FROM journal_entries WHERE user_id = :u",
        "SELECT * FROM journal_entries WHERE user_id = :u ORDER BY occurred_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.penghapus_sql(
        "journal", "journal_entries", "DELETE FROM journal_entries WHERE user_id = :u"
    ),
)
