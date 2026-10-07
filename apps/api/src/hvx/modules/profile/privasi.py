"""Bagian `profile` di Privacy Center — spec/07 6.4 (K-41 · K-42).

* `profiles` — kategori `profile`, tidak dihapus di sini: profil dihapus bersama akun.
* `human_states` — **turunan** check-in (5.3 menghitungnya dari `checkin.logged`); di V0
  tidak ada sumber lain, jadi menghapus check-in menghapus seluruh human state (naskah 11
  §7.25: nilai turunan tetap membawa jejak perilaku meski sumbernya hilang).
"""

from __future__ import annotations

from hvx.modules import identity

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        "profile",
        "profiles",
        "SELECT count(*) FROM profiles WHERE user_id = :u",
        "SELECT * FROM profiles WHERE user_id = :u",
    ),
    identity.bagian_sql(
        "checkins",
        "human_states",
        "SELECT count(*) FROM human_states WHERE user_id = :u",
        "SELECT * FROM human_states WHERE user_id = :u ORDER BY for_date, model_version",
        turunan=True,
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    identity.penghapus_sql(
        "checkins", "human_states", "DELETE FROM human_states WHERE user_id = :u", turunan=True
    ),
)
