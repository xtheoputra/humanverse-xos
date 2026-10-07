"""Bagian `habits` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Habit yang diarsipkan (`deleted_at`) ikut dihitung dan diekspor: masih tersimpan, jadi masih
diketahui. Hapus kategori = hapus KERAS habit DAN penyelesaiannya.
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "habits",
        "habits",
        "SELECT count(*) FROM habits WHERE user_id = :u",
        "SELECT * FROM habits WHERE user_id = :u ORDER BY created_at, id",
    ),
    identity.bagian_sql(
        "habits",
        "habit_completions",
        "SELECT count(*) FROM habit_completions WHERE user_id = :u",
        "SELECT * FROM habit_completions WHERE user_id = :u ORDER BY for_date, habit_id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    # Penyelesaian dulu supaya jumlahnya terhitung sendiri (cascade tidak melaporkan baris).
    identity.penghapus_sql(
        "habits", "habit_completions", "DELETE FROM habit_completions WHERE user_id = :u"
    ),
    identity.penghapus_sql("habits", "habits", "DELETE FROM habits WHERE user_id = :u"),
)
