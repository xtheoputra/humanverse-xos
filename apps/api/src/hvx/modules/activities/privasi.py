"""Bagian `activities` di Privacy Center — spec/07 6.4 (K-41 · K-42).

Yang dicatat pengguna (`manual`) dan yang disimpulkan sistem (`inferred`, 3.8) satu tabel,
satu kategori: menghapus aktivitas menghapus keduanya.

Lajur `inferred` juga **turunan** kategori lain: Behavior projector (5.1) memproyeksikan tiap
penyelesaian habit dari event `habit.*` menjadi satu aktivitas `kind='habit'` — `completion_id`,
tanggal, status, tier. 🔴 Versi pertama hanya menyatakan kategori `activities`: hapus `habits`
atau seluruh `history` (sumber proyeksinya) meninggalkan riwayat penyelesaian habit itu utuh
di sini — terekspor dan tampil di `GET /activities` (tinjauan keamanan S5–6, S1; K-42
menolak *“hapus sumbernya saja”*). Kini keduanya membawa proyeksinya; aktivitas yang
DICATAT pengguna tidak pernah tersentuh.
"""

from __future__ import annotations

from hvx.modules import identity

# `kind` proyeksi penyelesaian habit = `intelligence.proyektor.KIND_HABIT` — lapisan di atas
# modul ini (M-1), jadi nilainya disebut di sini; uji HTTP-nya memproyeksikan sungguhan.
_KIND_PROYEKSI_HABIT = "habit"

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
    identity.penghapus_sql(
        "habits",
        "activities",
        "DELETE FROM activities WHERE user_id = :u AND source = 'inferred' AND kind = :kind",
        turunan=True,
        parameter={"kind": _KIND_PROYEKSI_HABIT},
    ),
    # Proyeksi = turunan `events` (spec/02 aturan D): tanpa riwayatnya, membangun ulang dari
    # nol pun tidak melahirkannya lagi — jadi ia ikut riwayat yang dihapus.
    identity.penghapus_sql(
        "history",
        "activities",
        "DELETE FROM activities WHERE user_id = :u AND source = 'inferred'",
        turunan=True,
    ),
)
