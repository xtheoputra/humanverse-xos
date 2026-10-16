"""spec/07 3.4 — modul `journal`: *“`GET /journal` tidak pernah mengembalikan `body`”*.

"Tidak pernah" diuji di tiga lapis: jawaban HTTP daftar (tiap item, tiap
halaman), skema OpenAPI yang diterbitkan (kontraknya sendiri tidak punya
medannya), dan event `journal.created` (isi jurnal tidak masuk event — spec/03).
"""

from __future__ import annotations

import re
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, PenghitungKueri, auth, psycopg_dsn

pytestmark = pytest.mark.integration

RAHASIA = "Hari ini aku menangis di kereta dan tidak tahu kenapa"


async def _tulis(api: ApiUji, token: str, **isi: Any) -> dict[str, Any]:
    isi.setdefault("body", RAHASIA)
    r = await api.klien.post("/v1/journal", json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def test_daftar_jurnal_tidak_pernah_membawa_body(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for i in range(3):
        await _tulis(api_bersama, token, title=f"J{i}")

    halaman: list[dict[str, Any]] = []
    kursor = None
    while True:
        param: dict[str, Any] = {"limit": 2, **({"cursor": kursor} if kursor else {})}
        r = await api_bersama.klien.get("/v1/journal", params=param, headers=auth(token))
        assert r.status_code == 200, r.text
        halaman += r.json()["items"]
        assert RAHASIA not in r.text, "GET /journal mengembalikan body"
        kursor = r.json()["next_cursor"]
        if not kursor:
            break

    assert len(halaman) == 3
    assert all("body" not in j for j in halaman), "GET /journal mengembalikan body"
    assert {j["word_count"] for j in halaman} == {len(RAHASIA.split())}


async def test_kueri_daftar_tidak_membaca_body_dari_basis_data(api_bersama: ApiUji) -> None:
    """Lapis di bawah skema jawaban (repository docstring): `RingkasanJurnal` menyaring
    JAWABAN, tetapi kueri yang memilih `body` tetap memuat isi tulisan pribadi ke proses
    api untuk permintaan yang tidak membutuhkannya — tinjauan penegak Sprint 3."""
    _uid, token = await api_bersama.pengguna_baru()
    await _tulis(api_bersama, token)

    with PenghitungKueri(api_bersama.app) as hitung:
        r = await api_bersama.klien.get("/v1/journal", headers=auth(token))

    assert r.status_code == 200, r.text
    daftar = [s for s in hitung.pernyataan if "FROM journal_entries" in s]
    assert daftar, "kueri daftar jurnal tidak terbaca — pemindai buta?"
    assert not [s for s in daftar if re.search(r"\bbody\b", s)], (
        f"kueri daftar memilih body: {daftar}"
    )


async def test_satu_jurnal_dengan_body(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token, title="Kereta")

    r = await api_bersama.klien.get(f"/v1/journal/{j['id']}", headers=auth(token))

    assert r.status_code == 200
    assert (r.json()["body"], r.json()["title"]) == (RAHASIA, "Kereta")


async def test_kontrak_daftar_jurnal_tidak_punya_medan_body(api_bersama: ApiUji) -> None:
    """Skema OpenAPI yang DITERBITKAN — bukan hanya jawaban hari ini."""
    skema = api_bersama.app.openapi()
    ringkasan = skema["components"]["schemas"]["RingkasanJurnal"]

    assert "body" not in ringkasan["properties"], "kontrak GET /journal memuat body"
    assert "body" in skema["components"]["schemas"]["Jurnal"]["properties"]


async def test_event_jurnal_hanya_word_count(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token, title="Rahasia")

    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        ev = k.execute(
            "SELECT event_type, idempotency_key, payload FROM events WHERE user_id = %s", (uid,)
        ).fetchall()

    assert ev == [("journal.created", f"journal:{j['id']}", {"word_count": 10})], (
        f"isi jurnal masuk event: {ev}"
    )


async def test_ubah_isi_menghitung_ulang_kata_dan_judul_bisa_dihapus(
    api_bersama: ApiUji,
) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token, title="Awal")

    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"body": "dua kata", "title": None}, headers=auth(token)
    )
    kosong = await api_bersama.klien.patch(f"/v1/journal/{j['id']}", json={}, headers=auth(token))

    assert r.status_code == 200, r.text
    assert (r.json()["word_count"], r.json()["title"]) == (2, None)
    assert kosong.json()["updated_at"] == r.json()["updated_at"]


async def test_jumlah_kata_dipisah_spasi_apa_pun(api_bersama: ApiUji) -> None:
    """Baris baru, tab, spasi ganda — `word_count` satu-satunya yang event bawa (spec/03)."""
    _uid, token = await api_bersama.pengguna_baru()

    j = await _tulis(api_bersama, token, body="satu\ndua\ttiga  empat\n")

    assert j["word_count"] == 4, f"kata dihitung {j['word_count']}, bukan 4"


@pytest.mark.parametrize(
    "isi",
    [
        {"body": ""},
        {"body": "   "},
        {"body": "a\u0000b"},
        {"body": "x" * 100_001},
        {"body": "ada", "occurred_at": "2026-09-01T08:00:00"},  # tanpa zona
        {"body": "ada", "mood": "sedih"},
        {"title": "tanpa isi"},
    ],
)
async def test_jurnal_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post("/v1/journal", json=isi, headers=auth(token))

    assert r.status_code == 400, r.text


async def test_jurnal_masa_depan_422(api_bersama: ApiUji) -> None:
    """Ditulis ATAU dikoreksi ke masa depan — `PATCH` bukan jalan memutar."""
    _uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token)
    nanti = "2999-01-01T00:00:00Z"

    buat = await api_bersama.klien.post(
        "/v1/journal", json={"body": "nanti", "occurred_at": nanti}, headers=auth(token)
    )
    ubah = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"occurred_at": nanti}, headers=auth(token)
    )

    assert buat.status_code == 422, buat.text
    assert ubah.status_code == 422, f"PATCH ke masa depan diterima: {ubah.status_code}"
    assert buat.json()["error"]["code"] == "occurred_at_in_future"
    assert ubah.json()["error"]["code"] == "occurred_at_in_future"


async def test_hapus_keras_dan_jurnal_orang_lain_tidak_terlihat(api_bersama: ApiUji) -> None:
    """C-31 (K-46): hapus = hapus KERAS — barisnya DAN event `journal.created`-nya, bukan arsip
    yang menyimpan tulisan paling pribadi sampai akun dihapus."""
    a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token_a)
    k = api_bersama.klien

    orang_lain = await k.get(f"/v1/journal/{j['id']}", headers=auth(token_b))
    ubah_lain = await k.patch(f"/v1/journal/{j['id']}", json={"body": "x"}, headers=auth(token_b))
    daftar_lain = (await k.get("/v1/journal", headers=auth(token_b))).json()["items"]
    hapus = await k.delete(f"/v1/journal/{j['id']}", headers=auth(token_a))
    sesudah = await k.get(f"/v1/journal/{j['id']}", headers=auth(token_a))

    assert (orang_lain.status_code, ubah_lain.status_code, daftar_lain) == (404, 404, [])
    assert (hapus.status_code, sesudah.status_code) == (204, 404)
    assert (await k.get("/v1/journal", headers=auth(token_a))).json()["items"] == []
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as p:
        sisa = p.execute("SELECT count(*) FROM journal_entries WHERE id = %s", (j["id"],))
        assert sisa.fetchone() == (0,), "jurnal yang dihapus menginap sebagai arsip (C-31)"
        ev = p.execute(
            "SELECT count(*) FROM events WHERE user_id = %s AND subject_id = %s", (a, j["id"])
        )
        assert ev.fetchone() == (0,), "event jurnal yang dihapus tetap di riwayat (C-31)"


async def test_id_buatan_klien_409_dan_kunci_idempotensi(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    jid = "0b8f9a4e-4f6a-4a41-9b2c-0d7e5f1a2b3c"
    h = {**auth(token), "Idempotency-Key": "jurnal-pagi"}

    a = await api_bersama.klien.post("/v1/journal", json={"id": jid, "body": "x"}, headers=h)
    b = await api_bersama.klien.post("/v1/journal", json={"id": jid, "body": "x"}, headers=h)
    c = await api_bersama.klien.post(
        "/v1/journal", json={"id": jid, "body": "x"}, headers=auth(token)
    )

    assert (a.status_code, b.status_code, c.status_code) == (201, 201, 409)
    assert b.headers.get("Idempotent-Replayed") == "true"
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (n,) = k.execute("SELECT count(*) FROM events WHERE user_id = %s", (uid,)).fetchone() or (
            0,
        )
    assert n == 1


@pytest.mark.parametrize(
    "isi",
    [
        {"body": None},
        {"occurred_at": None},
        {"judul": "x"},  # medan yang tidak dikenal
    ],
)
async def test_ubah_jurnal_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    """`title: null` menghapus judul; `body`/`occurred_at` null tidak punya arti — 400, bukan
    500 dari NOT NULL (tinjauan penegak buta Sprint 3)."""
    _uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token)

    r = await api_bersama.klien.patch(f"/v1/journal/{j['id']}", json=isi, headers=auth(token))

    assert r.status_code == 400, f"{isi} → {r.status_code} {r.text}"


async def test_jurnal_yang_dihapus_tidak_bisa_diubah_atau_dihapus_lagi(
    api_bersama: ApiUji,
) -> None:
    """Hapus-lunak bukan arsip yang bisa disunting: `PATCH` sesudah `DELETE` menghidupkan
    isi yang dicabut pemiliknya ke memori, dan `DELETE` kedua menjalankan pendengarnya
    lagi."""
    _uid, token = await api_bersama.pengguna_baru()
    j = await _tulis(api_bersama, token)
    k = api_bersama.klien

    pertama = await k.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    kedua = await k.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    ubah = await k.patch(f"/v1/journal/{j['id']}", json={"body": "hidup lagi"}, headers=auth(token))

    assert pertama.status_code == 204, pertama.text
    assert kedua.status_code == 404, f"DELETE kedua: {kedua.status_code}"
    assert ubah.status_code == 404, f"PATCH sesudah DELETE: {ubah.status_code}"


async def test_daftar_terbaru_dulu_dan_rentang_waktu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for hari in ("01", "02", "03"):
        await _tulis(api_bersama, token, occurred_at=f"2026-09-{hari}T08:00:00Z")
    k = api_bersama.klien

    tanggal: list[str] = []
    kursor = None
    while True:
        param: dict[str, Any] = {"limit": 2, **({"cursor": kursor} if kursor else {})}
        r = await k.get("/v1/journal", params=param, headers=auth(token))
        assert r.status_code == 200, r.text
        tanggal += [j["occurred_at"][:10] for j in r.json()["items"]]
        kursor = r.json()["next_cursor"]
        if not kursor:
            break
    rentang = await k.get(
        "/v1/journal",
        params={"from": "2026-09-02T00:00:00Z", "to": "2026-09-03T00:00:00Z"},
        headers=auth(token),
    )
    terbalik = await k.get(
        "/v1/journal",
        params={"from": "2026-09-03T00:00:00Z", "to": "2026-09-02T00:00:00Z"},
        headers=auth(token),
    )

    assert tanggal == ["2026-09-03", "2026-09-02", "2026-09-01"], f"urutan halaman: {tanggal}"
    dalam = [j["occurred_at"][:10] for j in rentang.json()["items"]]
    assert dalam == ["2026-09-02"], f"rentang from–to: {dalam}"
    assert terbalik.status_code == 400, f"from sesudah to: {terbalik.status_code}"
