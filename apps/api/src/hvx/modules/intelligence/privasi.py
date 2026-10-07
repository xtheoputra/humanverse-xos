"""Bagian `intelligence` di Privacy Center — spec/07 6.4 (K-41 · K-42), naskah 11 §7.25.

Rekomendasi adalah **turunan**: judul dan alasannya mengutip habit (*“Kembali ke ‘Lari
pagi’”*), energi check-in (`context_snapshot.context`, *“Energi 2/5 pada …”*), atau — untuk
yang ditulis agent lewat `recommendation.create` — apa pun yang dibaca agent itu (habit,
goal, check-in, mood; spec/05 coach-agent). Menghapus sumbernya menghapus rekomendasi yang
bisa membawanya. Untuk rekomendasi agent, sumber pastinya tidak tercatat per baris, jadi
yang dipilih sisi yang melindungi: ikut terhapus bersama SALAH SATU sumber yang mungkin.
Rekomendasi bisa dihitung ulang; teks yang terlanjur menginap tidak bisa ditarik kembali.
"""

from __future__ import annotations

from hvx.modules import identity

_REKOMENDASI = "recommendations"

BAGIAN_PRIVASI: tuple[identity.BagianData, ...] = (
    identity.bagian_sql(
        _REKOMENDASI,
        "recommendations",
        "SELECT count(*) FROM recommendations WHERE user_id = :u",
        "SELECT * FROM recommendations WHERE user_id = :u ORDER BY created_at, id",
        turunan=True,
    ),
    identity.bagian_sql(
        _REKOMENDASI,
        "recommendation_feedback",
        "SELECT count(*) FROM recommendation_feedback WHERE user_id = :u",
        "SELECT * FROM recommendation_feedback WHERE user_id = :u ORDER BY created_at, id",
    ),
)

PENGHAPUS_PRIVASI: tuple[identity.Penghapus, ...] = (
    # Umpan balik hanya-tambah bagi `hvx_app` (spec/01 §10 — tanpa DELETE): terhapus lewat
    # `ON DELETE CASCADE` rekomendasinya. Langkah ini HANYA menghitungnya lebih dulu.
    identity.penghapus_sql(
        _REKOMENDASI,
        "recommendation_feedback",
        "SELECT count(*) FROM recommendation_feedback WHERE user_id = :u",
    ),
    identity.penghapus_sql(
        _REKOMENDASI, "recommendations", "DELETE FROM recommendations WHERE user_id = :u"
    ),
    identity.penghapus_sql(
        "habits",
        "recommendations",
        "DELETE FROM recommendations WHERE user_id = :u "
        "AND (domain = 'habit' OR subject_type = 'habit' OR agent_id IS NOT NULL)",
        turunan=True,
    ),
    identity.penghapus_sql(
        "goals",
        "recommendations",
        "DELETE FROM recommendations WHERE user_id = :u "
        "AND (domain = 'goal' OR subject_type = 'goal' OR agent_id IS NOT NULL)",
        turunan=True,
    ),
    identity.penghapus_sql(
        "checkins",
        "recommendations",
        "DELETE FROM recommendations WHERE user_id = :u "
        "AND (context_snapshot -> 'context' IS NOT NULL OR agent_id IS NOT NULL)",
        turunan=True,
    ),
    identity.penghapus_sql(
        "moods",
        "recommendations",
        "DELETE FROM recommendations WHERE user_id = :u AND agent_id IS NOT NULL",
        turunan=True,
    ),
)
