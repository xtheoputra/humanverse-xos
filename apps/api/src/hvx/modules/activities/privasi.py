"""Bagian `activities` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Yang dicatat pengguna (`manual`) dan yang disimpulkan sistem (`inferred`, 3.8) satu tabel,
satu kategori: menghapus aktivitas menghapus keduanya.
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "activities",
        "activities",
        "SELECT count(*) FROM activities WHERE user_id = :u",
        "SELECT * FROM activities WHERE user_id = :u ORDER BY occurred_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.penghapus_sql("activities", "activities", "DELETE FROM activities WHERE user_id = :u"),
)
