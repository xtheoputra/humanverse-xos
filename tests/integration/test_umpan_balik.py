"""spec/07 5.6 — umpan balik rekomendasi: *modified & snoozed bukan penolakan*.

`POST /recommendations/{id}/feedback` menambah baris `recommendation_feedback`
(append-only) dan menyesuaikan `recommendations.status` dalam SATU transaksi.
Status diperiksa di basis data (pemilik skema, di luar RLS), bukan hanya kode
status — perubahan status yang diam-diam salah tetap merah.
"""

from __future__ import annotations

import uuid
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg import sql

pytestmark = pytest.mark.integration


def _buat_rekomendasi(api: ApiUji, uid: Any, *, status: str = "shown") -> str:
    rid = uuid.uuid4()
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        k.execute(
            "INSERT INTO recommendations (id, user_id, domain, title, status) "
            "VALUES (%s, %s, 'habit', 'Lari pagi', %s)",
            (rid, uid, status),
        )
        k.commit()
    return str(rid)


def _status(api: ApiUji, rid: str) -> str:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        (s,) = k.execute("SELECT status FROM recommendations WHERE id = %s", (rid,)).fetchone()
    return s


def _umpan_balik(api: ApiUji, rid: str) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT action, reason FROM recommendation_feedback "
            "WHERE recommendation_id = %s ORDER BY created_at",
            (rid,),
        ).fetchall()


def _kunci(token: str) -> dict[str, str]:
    return {**auth(token), "Idempotency-Key": f"k-{uuid.uuid4().hex}"}


async def test_accepted_dan_rejected_mengubah_status(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    for action, harap in (("accepted", "accepted"), ("rejected", "rejected")):
        rid = _buat_rekomendasi(api_bersama, uid)
        r = await api_bersama.klien.post(
            f"/v1/recommendations/{rid}/feedback", json={"action": action}, headers=_kunci(token)
        )
        assert r.status_code == 201, r.text
        assert r.json()["action"] == action
        assert _status(api_bersama, rid) == harap
        assert _umpan_balik(api_bersama, rid) == [(action, None)]


@pytest.mark.parametrize("action", ["modified", "snoozed", "ignored"])
async def test_modified_snoozed_ignored_bukan_penolakan(api_bersama: ApiUji, action: str) -> None:
    """Statusnya TIDAK berubah jadi rejected — tercatat sebagai bukti, tetap bisa diterima nanti."""
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid, status="shown")

    r = await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback",
        json={"action": action, "reason": "pilih yang lain"},
        headers=_kunci(token),
    )

    assert r.status_code == 201, r.text
    assert _status(api_bersama, rid) == "shown", f"“{action}” mengubah status rekomendasi"
    assert _umpan_balik(api_bersama, rid) == [(action, "pilih yang lain")]


async def test_idempotency_key_tidak_melahirkan_umpan_balik_kedua(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid)
    h = _kunci(token)

    pertama = await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback", json={"action": "snoozed"}, headers=h
    )
    kedua = await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback", json={"action": "snoozed"}, headers=h
    )

    assert pertama.status_code == 201, pertama.text
    assert kedua.status_code == 201, kedua.text
    assert kedua.headers.get("Idempotent-Replayed") == "true"
    assert kedua.json()["id"] == pertama.json()["id"]
    assert len(_umpan_balik(api_bersama, rid)) == 1, "Idempotency-Key diabaikan: umpan balik ganda"


async def test_umpan_balik_append_only_banyak_baris(api_bersama: ApiUji) -> None:
    """Kunci berbeda → baris berbeda: snooze lalu terima adalah dua bukti, bukan satu ditimpa."""
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid)

    await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback", json={"action": "snoozed"}, headers=_kunci(token)
    )
    await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback", json={"action": "accepted"}, headers=_kunci(token)
    )

    assert [a for a, _ in _umpan_balik(api_bersama, rid)] == ["snoozed", "accepted"]
    assert _status(api_bersama, rid) == "accepted", "status akhir mengikuti umpan balik terakhir"


async def test_rekomendasi_tak_dikenal_404_tanpa_menulis(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    asing = uuid.uuid4()

    r = await api_bersama.klien.post(
        f"/v1/recommendations/{asing}/feedback", json={"action": "accepted"}, headers=_kunci(token)
    )

    assert r.status_code == 404, r.text
    assert r.json()["error"]["code"] == "recommendation_not_found"


async def test_tak_bisa_umpan_balik_rekomendasi_pengguna_lain(api_bersama: ApiUji) -> None:
    """RLS: rekomendasi milik orang lain tak terlihat → 404, bukan jalan masuk menulis."""
    uid_a, _ = await api_bersama.pengguna_baru()
    _uid_b, token_b = await api_bersama.pengguna_baru()
    rid_a = _buat_rekomendasi(api_bersama, uid_a)

    r = await api_bersama.klien.post(
        f"/v1/recommendations/{rid_a}/feedback",
        json={"action": "accepted"},
        headers=_kunci(token_b),
    )

    assert r.status_code == 404, r.text
    assert _umpan_balik(api_bersama, rid_a) == []
    assert _status(api_bersama, rid_a) == "shown"


# ── Tinjauan penegak buta S5–6 ──────────────────────────────────────────────────


async def test_outcome_umpan_balik_tersimpan(api_bersama: ApiUji) -> None:
    """`modified` membawa APA yang dipilih sebagai gantinya — bukti itu yang membuat
    'memilih B setelah disarankan A' bukan penolakan; ia wajib tersimpan."""
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid)
    hasil = {"dipilih": "jalan kaki 10 menit"}

    r = await api_bersama.klien.post(
        f"/v1/recommendations/{rid}/feedback",
        json={"action": "modified", "outcome": hasil},
        headers=_kunci(token),
    )

    assert r.status_code == 201, r.text
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (tersimpan,) = k.execute(
            "SELECT outcome FROM recommendation_feedback WHERE recommendation_id = %s", (rid,)
        ).fetchone() or (None,)
    assert tersimpan == hasil, f"outcome umpan balik tidak disimpan: {tersimpan}"
    assert r.json()["outcome"] == hasil


async def test_umpan_balik_dan_status_satu_transaksi(api_bersama: ApiUji) -> None:
    """K-37: baris umpan balik dan perubahan status commit BERSAMA atau batal bersama.
    Perubahan status yang gagal (pemicu uji menolaknya) tidak meninggalkan umpan balik."""
    uid, token = await api_bersama.pengguna_baru()
    rid = _buat_rekomendasi(api_bersama, uid)
    nama = f"uji_tolak_status_{uuid.uuid4().hex[:10]}"
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        k.execute(
            sql.SQL(
                "CREATE FUNCTION {}() RETURNS trigger LANGUAGE plpgsql AS "
                "$$ BEGIN RAISE EXCEPTION 'status ditolak pemicu uji'; END $$"
            ).format(sql.Identifier(nama))
        )
        k.execute(
            sql.SQL(
                "CREATE TRIGGER {} BEFORE UPDATE OF status ON recommendations FOR EACH ROW "
                "WHEN (OLD.id = {}) EXECUTE FUNCTION {}()"
            ).format(sql.Identifier(nama), sql.Literal(rid), sql.Identifier(nama))
        )
        k.commit()
    try:
        r = await api_bersama.klien.post(
            f"/v1/recommendations/{rid}/feedback",
            json={"action": "accepted"},
            headers=_kunci(token),
        )
    finally:
        with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
            k.execute(sql.SQL("DROP TRIGGER {} ON recommendations").format(sql.Identifier(nama)))
            k.execute(sql.SQL("DROP FUNCTION {}()").format(sql.Identifier(nama)))
            k.commit()

    assert r.status_code == 500, r.text
    assert _umpan_balik(api_bersama, rid) == [], (
        "umpan balik tercatat walau status gagal diubah — bukan satu transaksi (K-37)"
    )
    assert _status(api_bersama, rid) == "shown"
