"""Bagian `checkins` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Dua kategori, sebab dua hal yang berbeda bagi pemiliknya: check-in harian (energi, fokus,
tidur) dan mood — yang kini **sensitif** (C-32, K-46: dekat dengan data kesehatan jiwa;
GDPR Art. 9, UU PDP Pasal 4(2)). Menghapus salah satunya tidak menyentuh yang lain.
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "checkins",
        "daily_checkins",
        "SELECT count(*) FROM daily_checkins WHERE user_id = :u",
        "SELECT * FROM daily_checkins WHERE user_id = :u ORDER BY for_date",
    ),
    identity.bagian_sql(
        "moods",
        "mood_entries",
        "SELECT count(*) FROM mood_entries WHERE user_id = :u",
        "SELECT * FROM mood_entries WHERE user_id = :u ORDER BY occurred_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.penghapus_sql(
        "checkins", "daily_checkins", "DELETE FROM daily_checkins WHERE user_id = :u"
    ),
    identity.penghapus_sql("moods", "mood_entries", "DELETE FROM mood_entries WHERE user_id = :u"),
)
