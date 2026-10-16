"""Bagian `goals` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Goal yang diarsipkan (`deleted_at`) ikut dihitung dan diekspor: masih tersimpan, jadi masih
diketahui. Hapus kategori = hapus KERAS; milestone ikut lewat `ON DELETE CASCADE`, dan habit
yang menaut goal dilepas basis data sendiri (`ON DELETE SET NULL (goal_id)`, spec/01).
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "goals",
        "goals",
        "SELECT count(*) FROM goals WHERE user_id = :u",
        "SELECT * FROM goals WHERE user_id = :u ORDER BY created_at, id",
    ),
    identity.bagian_sql(
        "goals",
        "goal_milestones",
        "SELECT count(*) FROM goal_milestones WHERE user_id = :u",
        "SELECT * FROM goal_milestones WHERE user_id = :u ORDER BY goal_id, position, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    # Milestone dulu supaya jumlahnya terhitung sendiri (cascade tidak melaporkan baris).
    identity.penghapus_sql(
        "goals", "goal_milestones", "DELETE FROM goal_milestones WHERE user_id = :u"
    ),
    identity.penghapus_sql("goals", "goals", "DELETE FROM goals WHERE user_id = :u"),
)
