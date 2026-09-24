"""spec/04 *Aturan lintas endpoint* — `Idempotency-Key` di tulisan domain (E-165).

*“`POST`/`PATCH` domain menerima header `Idempotency-Key`; kunci yang sama
mengembalikan hasil yang sama.”* Diuji lewat HTTP, sebagai peran aplikasi,
terhadap Redis dan PostgreSQL sungguhan: jumlah BARIS yang dibuat dihitung,
bukan hanya kode status.
"""

from __future__ import annotations

import asyncio
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

pytestmark = pytest.mark.integration


def _jumlah_goal(api: ApiUji, user_id: Any) -> int:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        baris = k.execute("SELECT count(*) FROM goals WHERE user_id = %s", (user_id,)).fetchone()
    assert baris is not None
    (n,) = baris
    return int(n)


def _kunci(api: ApiUji, token: str, kunci: str) -> dict[str, str]:
    return {**auth(token), "Idempotency-Key": kunci}


async def test_kunci_sama_memutar_ulang_jawaban_pertama_tanpa_baris_kedua(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "buat-goal-1")

    pertama = await api_bersama.klien.post("/v1/goals", json={"title": "Sekali"}, headers=h)
    kedua = await api_bersama.klien.post("/v1/goals", json={"title": "Sekali"}, headers=h)

    assert pertama.status_code == kedua.status_code == 201, kedua.text
    assert kedua.json() == pertama.json()
    assert kedua.headers.get("Idempotent-Replayed") == "true"
    assert "Idempotent-Replayed" not in pertama.headers
    assert _jumlah_goal(api_bersama, uid) == 1, "kunci yang sama membuat baris kedua"


async def test_tanpa_kunci_tiap_permintaan_berjalan(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()

    for _ in range(2):
        r = await api_bersama.klien.post("/v1/goals", json={"title": "Dua"}, headers=auth(token))
        assert r.status_code == 201

    assert _jumlah_goal(api_bersama, uid) == 2


async def test_kunci_sama_dengan_badan_lain_422_bukan_diputar_ulang(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "kunci-dipakai-lagi")

    await api_bersama.klien.post("/v1/goals", json={"title": "Pertama"}, headers=h)
    r = await api_bersama.klien.post("/v1/goals", json={"title": "Lain"}, headers=h)

    assert r.status_code == 422, "kunci yang sama dengan badan lain diputar ulang: " + r.text
    assert r.json()["error"]["code"] == "idempotency_key_reused"
    assert _jumlah_goal(api_bersama, uid) == 1


async def test_spasi_json_tidak_mengubah_sidik_permintaan(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = {**_kunci(api_bersama, token, "spasi"), "Content-Type": "application/json"}

    a = await api_bersama.klien.post("/v1/goals", content=b'{"title":"Sama"}', headers=h)
    b = await api_bersama.klien.post("/v1/goals", content=b'{ "title" : "Sama" }', headers=h)

    assert a.status_code == b.status_code == 201, b.text
    assert _jumlah_goal(api_bersama, uid) == 1


async def test_kunci_yang_sama_milik_dua_pengguna_tidak_saling_memutar_ulang(
    api_bersama: ApiUji,
) -> None:
    """H-27 — jawaban pengguna A tidak pernah diputar ulang untuk pengguna B."""
    a, token_a = await api_bersama.pengguna_baru()
    b, token_b = await api_bersama.pengguna_baru()

    ra = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Sama"}, headers=_kunci(api_bersama, token_a, "bersama")
    )
    rb = await api_bersama.klien.post(
        "/v1/goals", json={"title": "Sama"}, headers=_kunci(api_bersama, token_b, "bersama")
    )

    assert ra.status_code == rb.status_code == 201
    assert "Idempotent-Replayed" not in rb.headers, "jawaban pengguna A diputar ulang untuk B"
    assert ra.json()["id"] != rb.json()["id"]
    assert _jumlah_goal(api_bersama, a) == _jumlah_goal(api_bersama, b) == 1


async def test_permintaan_serentak_dengan_kunci_sama_hanya_satu_yang_jalan(
    api_bersama: ApiUji,
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "serentak")

    hasil = await asyncio.gather(
        *(api_bersama.klien.post("/v1/goals", json={"title": "S"}, headers=h) for _ in range(6))
    )

    kode = sorted(r.status_code for r in hasil)
    assert set(kode) <= {201, 409}, kode
    assert _jumlah_goal(api_bersama, uid) == 1, f"serentak: {kode}"
    for r in hasil:
        if r.status_code == 409:
            assert r.json()["error"]["code"] == "idempotency_in_progress"
            assert r.headers.get("Retry-After") == "1"


async def test_galat_tidak_disimpan_sebagai_jawaban(api_bersama: ApiUji) -> None:
    """Jawaban 4xx tidak dikunci: ulangan menjalankan permintaannya lagi."""
    _uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "galat-dulu")
    induk_hilang = "00000000-0000-4000-8000-000000000000"

    pertama = await api_bersama.klien.post(
        "/v1/goals", json={"title": "X", "parent_id": induk_hilang}, headers=h
    )
    kedua = await api_bersama.klien.post(
        "/v1/goals", json={"title": "X", "parent_id": induk_hilang}, headers=h
    )

    assert pertama.status_code == kedua.status_code == 422
    assert "Idempotent-Replayed" not in kedua.headers, "galat disimpan sebagai jawaban"


@pytest.mark.parametrize("kunci", ["", "a b", "x" * 129, "k/garis-miring"])
async def test_kunci_berbentuk_salah_400(api_bersama: ApiUji, kunci: str) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post(
        "/v1/goals",
        json={"title": "X"},
        headers={**auth(token), "Idempotency-Key": kunci},
    )

    assert r.status_code == 400, r.text
