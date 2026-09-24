"""spec/07 2.6 — `mood_entries`: mood DILAPORKAN pengguna (spec/01, E-34).

`spec/07` tidak memberi 2.6 kalimat *“Selesai bila”*. Yang dibuktikan di sini
adalah kontrak `spec/04` (`POST /moods`, `GET /moods ?from=&to=&cursor=`) dan
aturan lintas endpoint: id buatan klien, halaman berkursor, waktu berzona,
Idempotency-Key, dan baris yang hanya terlihat oleh pemiliknya.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

pytestmark = pytest.mark.integration


async def _mood(api: ApiUji, token: str, **isi: Any) -> Any:
    isi.setdefault("valence", 3)
    return await api.klien.post("/v1/moods", json=isi, headers=auth(token))


def _jumlah(api: ApiUji, user_id: Any) -> int:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute(
            "SELECT count(*) FROM mood_entries WHERE user_id = %s", (user_id,)
        ).fetchone()
    assert baris is not None
    return int(baris[0])


async def test_mood_dicatat_dan_terbaca_terbaru_dulu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    lama = await _mood(api_bersama, token, valence=2, label="cemas",
                       occurred_at="2026-09-01T08:00:00Z")  # fmt: skip
    baru = await _mood(api_bersama, token, valence=4, label="lega", note="sesudah lari")
    daftar = (await api_bersama.klien.get("/v1/moods", headers=auth(token))).json()

    assert lama.status_code == baru.status_code == 201, baru.text
    assert lama.json()["occurred_at"] == "2026-09-01T08:00:00Z"
    assert [m["label"] for m in daftar["items"]] == ["lega", "cemas"]
    assert daftar["next_cursor"] is None


async def test_occurred_at_tanpa_zona_waktu_ditolak_400(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()

    r = await _mood(api_bersama, token, occurred_at="2026-09-01T08:00:00")

    assert r.status_code == 400, r.text
    assert _jumlah(api_bersama, uid) == 0


async def test_mood_di_masa_depan_ditolak_tetapi_jam_perangkat_sedikit_maju_diterima(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    sekarang = datetime.now(UTC)

    sedikit_maju = await _mood(
        api_bersama, token, occurred_at=(sekarang + timedelta(seconds=60)).isoformat()
    )
    besok = await _mood(api_bersama, token, occurred_at=(sekarang + timedelta(days=1)).isoformat())

    assert sedikit_maju.status_code == 201, sedikit_maju.text
    assert besok.status_code == 422, "mood masa depan tersimpan: " + besok.text
    assert besok.json()["error"]["code"] == "occurred_at_in_future"
    assert _jumlah(api_bersama, uid) == 1


@pytest.mark.parametrize(
    "isi",
    [
        {"valence": 0},
        {"valence": 6},
        {"valence": None},
        {"valence": 3, "label": "   "},
        {"valence": 3, "label": "x" * 51},
        {"valence": 3, "note": "a\u0000b"},
        {"valence": 3, "suasana": "baik"},
    ],
)
async def test_mood_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post("/v1/moods", json=isi, headers=auth(token))

    assert r.status_code == 400, r.text
    assert _jumlah(api_bersama, uid) == 0


async def test_id_buatan_klien_dan_id_sama_409(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mid = "7b1d4f8e-2a55-4c86-9d3f-3f5c1b7e9a01"

    pertama = await _mood(api_bersama, token, id=mid)
    kedua = await _mood(api_bersama, token, id=mid)

    assert pertama.json()["id"] == mid
    assert kedua.status_code == 409
    assert _jumlah(api_bersama, uid) == 1


async def test_idempotency_key_memutar_ulang_mood_yang_sama(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = {**auth(token), "Idempotency-Key": "mood-pagi"}

    a = await api_bersama.klien.post("/v1/moods", json={"valence": 3}, headers=h)
    b = await api_bersama.klien.post("/v1/moods", json={"valence": 3}, headers=h)

    assert a.json() == b.json()
    assert b.headers.get("Idempotent-Replayed") == "true"
    assert _jumlah(api_bersama, uid) == 1


async def test_halaman_berkursor_tanpa_ganda_dan_rentang_waktu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for jam in range(5):
        await _mood(api_bersama, token, valence=1 + jam, occurred_at=f"2026-09-02T0{jam}:00:00Z")

    terbaca: list[int] = []
    kursor = None
    while True:
        param: dict[str, Any] = {"limit": 2}
        if kursor:
            param["cursor"] = kursor
        r = (await api_bersama.klien.get("/v1/moods", params=param, headers=auth(token))).json()
        terbaca += [m["valence"] for m in r["items"]]
        kursor = r["next_cursor"]
        if kursor is None:
            break
    rentang = await api_bersama.klien.get(
        "/v1/moods",
        params={"from": "2026-09-02T01:00:00Z", "to": "2026-09-02T03:00:00Z"},
        headers=auth(token),
    )

    assert terbaca == [5, 4, 3, 2, 1], f"halaman mood mengulang atau melompati baris: {terbaca}"
    assert [m["valence"] for m in rentang.json()["items"]] == [3, 2], "`to` tidak eksklusif"


@pytest.mark.parametrize(
    "param",
    [
        {"from": "2026-09-02T03:00:00Z", "to": "2026-09-02T01:00:00Z"},
        {"from": "2026-09-02T01:00:00"},
        {"cursor": "rusak"},
    ],
)
async def test_parameter_daftar_tidak_sah_400(api_bersama: ApiUji, param: dict[str, str]) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.get("/v1/moods", params=param, headers=auth(token))

    assert r.status_code == 400, r.text


async def test_mood_pengguna_lain_tidak_terlihat(api_bersama: ApiUji) -> None:
    _a, token_a = await api_bersama.pengguna_baru()
    _b, token_b = await api_bersama.pengguna_baru()
    await _mood(api_bersama, token_a, valence=1, note="rahasia A")

    r = await api_bersama.klien.get("/v1/moods", headers=auth(token_b))

    assert r.json()["items"] == []
