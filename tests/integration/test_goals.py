"""spec/07 2.1 — modul `goals` + milestone + `parent_id`.

Selesai bila: pohon goal 3 tingkat terbaca dalam SATU query — dihitung dari
pernyataan SQL yang benar-benar sampai ke PostgreSQL (`PenghitungKueri`),
bukan dari jumlah panggilan fungsi.
"""

from __future__ import annotations

import uuid
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, BasisDataV0, PenghitungKueri, auth, psycopg_dsn
from psycopg import errors

pytestmark = pytest.mark.integration


async def _goal(api: ApiUji, token: str, **isi: Any) -> dict[str, Any]:
    isi.setdefault("title", "Goal uji")
    r = await api.klien.post("/v1/goals", json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


# ───────────────────────────────────────────────────────── pohon (2.1) ──


async def test_pohon_goal_tiga_tingkat_terbaca_dalam_satu_kueri(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    akar = await _goal(api_bersama, token, title="Hidup sehat", domain="health")
    karier = await _goal(api_bersama, token, title="Lari 10K", parent_id=akar["id"])
    await _goal(api_bersama, token, title="Tidur cukup", parent_id=akar["id"])
    cucu = await _goal(api_bersama, token, title="Interval mingguan", parent_id=karier["id"])

    with PenghitungKueri(api_bersama.app) as hitung:
        r = await api_bersama.klien.get(f"/v1/goals/{akar['id']}/tree", headers=auth(token))

    assert r.status_code == 200, r.text
    assert len(hitung.pernyataan) == 1, "pohon goal tidak terbaca dalam satu kueri:\n" + "\n".join(
        hitung.pernyataan
    )
    pohon = r.json()
    assert pohon["id"] == akar["id"]
    assert [a["title"] for a in pohon["children"]] == ["Lari 10K", "Tidur cukup"]
    lari = pohon["children"][0]
    assert [c["id"] for c in lari["children"]] == [cucu["id"]]
    assert lari["children"][0]["children"] == []


async def test_pohon_hanya_memuat_keturunan_bukan_leluhur(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    akar = await _goal(api_bersama, token, title="Akar")
    tengah = await _goal(api_bersama, token, title="Tengah", parent_id=akar["id"])
    await _goal(api_bersama, token, title="Daun", parent_id=tengah["id"])

    r = await api_bersama.klien.get(f"/v1/goals/{tengah['id']}/tree", headers=auth(token))

    assert r.status_code == 200
    assert r.json()["title"] == "Tengah"
    assert [c["title"] for c in r.json()["children"]] == ["Daun"]


async def test_pohon_goal_pengguna_lain_404(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    milik_a = await _goal(api_bersama, token_a)

    r = await api_bersama.klien.get(f"/v1/goals/{milik_a['id']}/tree", headers=auth(token_b))

    assert r.status_code == 404


# ──────────────────────────────────────────────────────── induk goal ──


async def test_induk_milik_pengguna_lain_ditolak(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    milik_a = await _goal(api_bersama, token_a)

    r = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Menumpang", "parent_id": milik_a["id"]}, headers=auth(token_b)
    )

    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "parent_not_found"


async def test_goal_tidak_bisa_menjadi_induk_dirinya_sendiri(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    gid = str(uuid.uuid4())

    r = await api_bersama.klien.post(
        "/v1/goals", json={"id": gid, "title": "Lingkaran", "parent_id": gid}, headers=auth(token)
    )

    assert r.status_code == 400, r.text


def test_basis_data_menolak_goal_yang_menjadi_induk_dirinya(v0_bersama: BasisDataV0) -> None:
    """CHECK `goals_parent_not_self` (migrasi 0004) — penjaga di bawah skema API.

    FK komposit diperiksa SESUDAH barisnya ada, jadi tanpa CHECK baris yang
    menunjuk dirinya sendiri LOLOS, dan pohonnya menjadi lingkaran.
    """
    with psycopg.connect(psycopg_dsn(v0_bersama.dsn_pemilik), autocommit=True) as k:
        (uid,) = k.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
            (f"{uuid.uuid4().hex}@uji.id",),
        ).fetchone() or (None,)
        gid = uuid.uuid4()
        with pytest.raises(errors.CheckViolation, match="goals_parent_not_self"):
            k.execute(
                "INSERT INTO goals (id, user_id, parent_id, title) VALUES (%s, %s, %s, 'x')",
                (gid, uid, gid),
            )


async def test_pohon_lebih_dari_sepuluh_tingkat_ditolak_saat_menulis(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    induk = None
    for tingkat in range(10):
        isi: dict[str, Any] = {"title": f"Tingkat {tingkat}"}
        if induk:
            isi["parent_id"] = induk
        induk = (await _goal(api_bersama, token, **isi))["id"]

    r = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Tingkat 10", "parent_id": induk}, headers=auth(token)
    )

    assert r.status_code == 422, "goal tingkat ke-11 diterima: " + r.text
    assert r.json()["error"]["code"] == "goal_tree_too_deep"


async def test_hapus_lunak_menaikkan_anak_menjadi_akar(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    induk = await _goal(api_bersama, token, title="Induk")
    anak = await _goal(api_bersama, token, title="Anak", parent_id=induk["id"])

    r = await api_bersama.klien.delete(f"/v1/goals/{induk['id']}", headers=auth(token))

    assert r.status_code == 204
    assert (
        await api_bersama.klien.get(f"/v1/goals/{induk['id']}", headers=auth(token))
    ).status_code == 404
    sisa = (await api_bersama.klien.get(f"/v1/goals/{anak['id']}", headers=auth(token))).json()
    assert sisa["parent_id"] is None, "anak goal yang dihapus tidak naik menjadi akar"
    semua = (await api_bersama.klien.get("/v1/goals", headers=auth(token))).json()["items"]
    assert [g["id"] for g in semua] == [anak["id"]]
    assert (
        await api_bersama.klien.delete(f"/v1/goals/{induk['id']}", headers=auth(token))
    ).status_code == 404


# ──────────────────────────────────────────────────── tulis & ubah ──


async def test_id_buatan_klien_dipakai_dan_id_yang_sama_409(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    gid = str(uuid.uuid4())

    pertama = await api_bersama.klien.post(
        "/v1/goals", json={"id": gid, "title": "Luring"}, headers=auth(token)
    )
    kedua = await api_bersama.klien.post(
        "/v1/goals", json={"id": gid, "title": "Luring"}, headers=auth(token)
    )

    assert pertama.status_code == 201
    assert pertama.json()["id"] == gid
    assert kedua.status_code == 409
    assert kedua.json()["error"]["code"] == "already_exists"


async def test_status_achieved_mengisi_achieved_at_dan_kembali_mengosongkannya(
    api_bersama: ApiUji,
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token, target_date="2026-12-31")

    tercapai = await api_bersama.klien.patch(
        f"/v1/goals/{g['id']}", json={"status": "achieved"}, headers=auth(token)
    )
    dibuka = await api_bersama.klien.patch(
        f"/v1/goals/{g['id']}", json={"status": "active", "target_date": None}, headers=auth(token)
    )

    assert tercapai.status_code == 200, tercapai.text
    assert tercapai.json()["achieved_at"] is not None
    assert dibuka.json()["achieved_at"] is None
    assert dibuka.json()["target_date"] is None


@pytest.mark.parametrize(
    "badan",
    [
        {"parent_id": "00000000-0000-0000-0000-000000000000"},  # spec/04: tidak bisa diubah
        {"title": None},
        {"title": "   "},
        {"status": "selesai"},
        {"title": "A\u0000B"},
    ],
)
async def test_patch_goal_yang_tidak_sah_ditolak_400(
    api_bersama: ApiUji, badan: dict[str, object]
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token, title="Tetap")

    r = await api_bersama.klien.patch(f"/v1/goals/{g['id']}", json=badan, headers=auth(token))

    assert r.status_code == 400, r.text
    tetap = (await api_bersama.klien.get(f"/v1/goals/{g['id']}", headers=auth(token))).json()
    assert tetap["title"] == "Tetap"


async def test_patch_kosong_tidak_menyentuh_baris(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token)

    r = await api_bersama.klien.patch(f"/v1/goals/{g['id']}", json={}, headers=auth(token))

    assert r.status_code == 200
    assert r.json()["updated_at"] == g["updated_at"]


async def test_goal_pengguna_lain_tidak_bisa_dibaca_diubah_atau_dihapus(
    api_bersama: ApiUji,
) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token_a, title="Milik A")
    k = api_bersama.klien

    assert (await k.get(f"/v1/goals/{g['id']}", headers=auth(token_b))).status_code == 404
    ubah = await k.patch(f"/v1/goals/{g['id']}", json={"title": "B"}, headers=auth(token_b))
    assert ubah.status_code == 404
    assert (await k.delete(f"/v1/goals/{g['id']}", headers=auth(token_b))).status_code == 404
    assert (await k.get("/v1/goals", headers=auth(token_b))).json()["items"] == []
    assert (await k.get(f"/v1/goals/{g['id']}", headers=auth(token_a))).json()["title"] == "Milik A"


# ───────────────────────────────────────────────────────── daftar ──


async def test_daftar_berhalaman_tanpa_ganda_dan_tanpa_lompat(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    dibuat = [(await _goal(api_bersama, token, title=f"G{i}"))["id"] for i in range(5)]

    terbaca: list[str] = []
    kursor = None
    for _ in range(5):
        param: dict[str, Any] = {"limit": 2}
        if kursor:
            param["cursor"] = kursor
        r = await api_bersama.klien.get("/v1/goals", params=param, headers=auth(token))
        assert r.status_code == 200, r.text
        terbaca += [g["id"] for g in r.json()["items"]]
        kursor = r.json()["next_cursor"]
        if kursor is None:
            break

    assert terbaca == list(reversed(dibuat))


async def test_daftar_menyaring_status(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    aktif = await _goal(api_bersama, token, title="Aktif")
    jeda = await _goal(api_bersama, token, title="Jeda")
    await api_bersama.klien.patch(
        f"/v1/goals/{jeda['id']}", json={"status": "paused"}, headers=auth(token)
    )

    r = await api_bersama.klien.get("/v1/goals", params={"status": "active"}, headers=auth(token))

    assert [g["id"] for g in r.json()["items"]] == [aktif["id"]]


@pytest.mark.parametrize("kursor", ["bukan-kursor", "e30", "WyIyMDI2IiwieCJd"])
async def test_kursor_rusak_400_bukan_500(api_bersama: ApiUji, kursor: str) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.get("/v1/goals", params={"cursor": kursor}, headers=auth(token))

    assert r.status_code == 400, r.text
    assert r.json()["error"]["code"] == "invalid_cursor"


# ──────────────────────────────────────────────────────── milestone ──


async def test_milestone_berurutan_dan_status_done_mengisi_completed_at(
    api_bersama: ApiUji,
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token)
    k = api_bersama.klien

    satu = await k.post(
        f"/v1/goals/{g['id']}/milestones", json={"title": "Satu"}, headers=auth(token)
    )
    dua = await k.post(
        f"/v1/goals/{g['id']}/milestones", json={"title": "Dua"}, headers=auth(token)
    )
    selesai = await k.patch(
        f"/v1/milestones/{satu.json()['id']}", json={"status": "done"}, headers=auth(token)
    )
    batal = await k.patch(
        f"/v1/milestones/{satu.json()['id']}", json={"status": "pending"}, headers=auth(token)
    )

    assert satu.status_code == 201, satu.text
    assert [satu.json()["position"], dua.json()["position"]] == [0, 1]
    assert selesai.json()["completed_at"] is not None
    assert batal.json()["completed_at"] is None
    rinci = (await k.get(f"/v1/goals/{g['id']}", headers=auth(token))).json()
    assert [m["title"] for m in rinci["milestones"]] == ["Satu", "Dua"]


async def test_milestone_goal_terhapus_atau_milik_orang_lain_404(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    g = await _goal(api_bersama, token_a)
    k = api_bersama.klien
    m = (
        await k.post(f"/v1/goals/{g['id']}/milestones", json={"title": "M"}, headers=auth(token_a))
    ).json()

    orang_lain = await k.post(
        f"/v1/goals/{g['id']}/milestones", json={"title": "X"}, headers=auth(token_b)
    )
    ubah_lain = await k.patch(
        f"/v1/milestones/{m['id']}", json={"status": "done"}, headers=auth(token_b)
    )
    await k.delete(f"/v1/goals/{g['id']}", headers=auth(token_a))
    sesudah_hapus = await k.patch(
        f"/v1/milestones/{m['id']}", json={"status": "done"}, headers=auth(token_a)
    )

    assert orang_lain.status_code == 404
    assert ubah_lain.status_code == 404
    assert sesudah_hapus.status_code == 404
