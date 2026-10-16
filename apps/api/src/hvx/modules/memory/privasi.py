"""Bagian `memory` di Privacy Center — spec/07 6.4 (K-41 · K-42), naskah 11 §7.25.

Memori adalah **turunan**: diekstrak dari jurnal & mood (3.6), dihitung dari pola perilaku
(5.2), atau diminta diingat (4.3). Dua jalan menghapusnya:

* kategori **`memories`** — *“lupakan semua yang kamu ingat tentangku”*, sumbernya tetap;
* kategori SUMBER yang dihapus membawa memori turunannya — menurut scope (jurnal →
  `journal_raw`, mood → `mood`, …) dan, untuk riwayat kejadian, pola perilaku
  (`kind='behavioral'`) yang dihitung dari event.

Melupakan = isi dikosongkan SEKARANG (`deleted_at`), di transaksi penghapusnya; titik Qdrant
dan barisnya dibuang penyelaras sesudah commit (spec/01 §12) — Qdrant tidak ikut transaksi.
Karena itu yang dihitung dan diekspor hanya memori yang HIDUP: baris yang menunggu dibuang
sudah tanpa isi.
"""

from __future__ import annotations

from types import MappingProxyType

from hvx.modules import identity

# Kategori sumber → scope memori yang diturunkan darinya.
SCOPE_SUMBER = MappingProxyType(
    {
        "journal": "journal_raw",
        "moods": "mood",
        "habits": "habits",
        "goals": "goals",
        "checkins": "checkins",
    }
)

_LUPAKAN_SEMUA = (
    "UPDATE memories SET content = '', summary = NULL, deleted_at = now() "
    "WHERE user_id = :u AND deleted_at IS NULL"
)
_LUPAKAN_SCOPE = (
    "UPDATE memories SET content = '', summary = NULL, deleted_at = now() "
    "WHERE user_id = :u AND deleted_at IS NULL AND scope = :scope"
)
_LUPAKAN_POLA = (
    "UPDATE memories SET content = '', summary = NULL, deleted_at = now() "
    "WHERE user_id = :u AND deleted_at IS NULL AND kind = 'behavioral'"
)

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "memories",
        "memories",
        "SELECT count(*) FROM memories WHERE user_id = :u AND deleted_at IS NULL",
        "SELECT id, kind, scope, content, summary, confidence, evidence_count, model_version, "
        "source_event_id, valid_from, valid_until, last_reinforced_at, created_at, updated_at "
        "FROM memories WHERE user_id = :u AND deleted_at IS NULL ORDER BY created_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.penghapus_sql("memories", "memories", _LUPAKAN_SEMUA),
    *(
        identity.penghapus_sql(
            kategori, "memories", _LUPAKAN_SCOPE, turunan=True, parameter={"scope": scope}
        )
        for kategori, scope in SCOPE_SUMBER.items()
    ),
    identity.penghapus_sql("history", "memories", _LUPAKAN_POLA, turunan=True),
)
