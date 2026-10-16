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

    # Dulu jawaban A yang diputar ulang (isinya tersimpan); kini rujukannya dibaca ulang
    # di bawah RLS B — tetap salah (404 untuk tulisan yang tidak pernah B buat).
    assert "Idempotent-Replayed" not in rb.headers, "jawaban pengguna A diputar ulang untuk B"
    assert ra.status_code == rb.status_code == 201
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

    assert "Idempotent-Replayed" not in kedua.headers, "galat disimpan sebagai jawaban"
    assert pertama.status_code == kedua.status_code == 422


@pytest.mark.parametrize("kunci", ["", "a b", "x" * 129, "k/garis-miring"])
async def test_kunci_berbentuk_salah_400(api_bersama: ApiUji, kunci: str) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post(
        "/v1/goals",
        json={"title": "X"},
        headers={**auth(token), "Idempotency-Key": kunci},
    )

    assert r.status_code == 400, r.text


# ── Tinjauan keamanan Sprint 2 (E-171): rujukan, bukan isi — dan berkuota ─────


async def _nilai_redis(api: ApiUji, user_id: Any) -> list[str]:
    r = api.app.state.redis
    kunci = [k async for k in r.scan_iter(match=f"{api.awalan_redis}:idem:{user_id}:*")]
    return [await r.get(k) for k in kunci]


async def test_redis_hanya_menyimpan_rujukan_tanpa_isi_tulisan(api_bersama: ApiUji) -> None:
    """Dulu badan jawaban utuh disimpan 24 jam — ~5 KiB per permintaan 19 byte, dan
    catatan pengguna yang tinggal di Redis sesudah hapus-keras."""
    uid, token = await api_bersama.pengguna_baru()
    rahasia = "catatan-pribadi-" + "x" * 3000

    r = await api_bersama.klien.post(
        "/v1/goals",
        json={"title": "Rahasia", "description": rahasia},
        headers=_kunci(api_bersama, token, "rujukan-saja"),
    )
    nilai = await _nilai_redis(api_bersama, uid)

    assert r.status_code == 201, r.text
    assert len(nilai) == 1
    assert "Rahasia" not in nilai[0]
    assert "catatan-pribadi" not in nilai[0]
    assert len(nilai[0]) < 200, f"yang disimpan {len(nilai[0])} byte — bukan rujukan"


async def test_ulangan_membaca_ulang_keadaan_sekarang(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "baca-ulang")
    k = api_bersama.klien

    pertama = await k.post("/v1/goals", json={"title": "Awal"}, headers=h)
    goal_id = pertama.json()["id"]
    await k.patch(f"/v1/goals/{goal_id}", json={"title": "Sesudah"}, headers=auth(token))
    ulang = await k.post("/v1/goals", json={"title": "Awal"}, headers=h)

    assert ulang.status_code == 201
    assert ulang.headers.get("Idempotent-Replayed") == "true"
    assert ulang.json()["id"] == goal_id
    assert ulang.json()["title"] == "Sesudah", "ulangan memutar isi lama yang tersimpan"


async def test_ulangan_sesudah_sumber_dayanya_dihapus_404(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "sudah-dihapus")
    k = api_bersama.klien

    pertama = await k.post("/v1/goals", json={"title": "Hilang"}, headers=h)
    await k.delete(f"/v1/goals/{pertama.json()['id']}", headers=auth(token))
    ulang = await k.post("/v1/goals", json={"title": "Hilang"}, headers=h)

    assert ulang.status_code == 404, ulang.text
    assert ulang.headers.get("Idempotent-Replayed") == "true"


async def test_kuota_kunci_per_pengguna_429_dan_ulangan_tetap_jalan(api_bersama: ApiUji) -> None:
    """Batas laju per pengguna 300/60 = 432 ribu tulisan sehari; tanpa kuota, tiap
    tulisan berkunci satu entri Redis 24 jam (Redis `noeviction`, bersama sesi)."""
    from hvx.modules.platform import KUOTA_KUNCI

    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    lama = await k.post("/v1/goals", json={"title": "L"}, headers=_kunci(api_bersama, token, "l"))
    r = api_bersama.app.state.redis
    await r.set(f"{api_bersama.awalan_redis}:idem-kuota:{uid}", KUOTA_KUNCI, ex=3600)

    baru = await k.post("/v1/goals", json={"title": "B"}, headers=_kunci(api_bersama, token, "b"))
    ulang = await k.post("/v1/goals", json={"title": "L"}, headers=_kunci(api_bersama, token, "l"))
    tanpa_kunci = await k.post("/v1/goals", json={"title": "T"}, headers=auth(token))

    assert lama.status_code == 201
    assert baru.status_code == 429, f"kuota kunci tidak ditegakkan: {baru.status_code}"
    assert baru.json()["error"]["code"] == "rate_limited"
    assert 3000 < int(baru.headers["Retry-After"]) <= 3600
    assert ulang.status_code == 201, "ulangan kunci LAMA ikut terhitung kuota"
    assert ulang.headers.get("Idempotent-Replayed") == "true"
    assert tanpa_kunci.status_code == 201
    assert _jumlah_goal(api_bersama, uid) == 2


async def test_kunci_sf_string_bertanda_kutip_sama_dengan_telanjang(api_bersama: ApiUji) -> None:
    """Draf IETF: `Idempotency-Key: "8e03978e-…"` (sf-string) — dulu 400."""
    uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien

    kutip = await k.post(
        "/v1/goals", json={"title": "Q"}, headers=_kunci(api_bersama, token, '"8e03978e-40d5"')
    )
    telanjang = await k.post(
        "/v1/goals", json={"title": "Q"}, headers=_kunci(api_bersama, token, "8e03978e-40d5")
    )

    assert kutip.status_code == telanjang.status_code == 201, kutip.text
    assert telanjang.headers.get("Idempotent-Replayed") == "true", (
        "kunci bertanda kutip dan telanjang dianggap kunci berbeda"
    )
    assert _jumlah_goal(api_bersama, uid) == 1


@pytest.mark.parametrize("kunci", ['"', '""', '"a', 'a"', '"a"b"'])
async def test_kutip_yang_tidak_seimbang_400(api_bersama: ApiUji, kunci: str) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post(
        "/v1/goals", json={"title": "X"}, headers=_kunci(api_bersama, token, kunci)
    )

    assert r.status_code == 400, r.text


async def test_badan_bersarang_dalam_bukan_json_tidak_500(api_bersama: ApiUji) -> None:
    """`json.loads` melempar RecursionError, bukan ValueError — dulu 500 (tinjauan keamanan)."""
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post(
        "/v1/goals",
        content=b"[" * 100_000,
        headers={**_kunci(api_bersama, token, "dalam"), "Content-Type": "text/plain"},
    )

    assert r.status_code == 400, f"badan bersarang dalam dijawab {r.status_code}"


# ── tinjauan penegak buta Sprint 2 ───────────────────────────────────────────


async def test_kunci_dan_badan_sama_di_rute_lain_bukan_ulangan(api_bersama: ApiUji) -> None:
    """Sidik memuat JALUR: `PATCH /goals/A` dan `/goals/B` berbadan sama adalah dua permintaan."""
    _uid, token = await api_bersama.pengguna_baru()
    k = api_bersama.klien
    a = (await k.post("/v1/goals", json={"title": "A"}, headers=auth(token))).json()
    b = (await k.post("/v1/goals", json={"title": "B"}, headers=auth(token))).json()
    h = _kunci(api_bersama, token, "capai")

    ra = await k.patch(f"/v1/goals/{a['id']}", json={"status": "achieved"}, headers=h)
    rb = await k.patch(f"/v1/goals/{b['id']}", json={"status": "achieved"}, headers=h)
    b_kini = (await k.get(f"/v1/goals/{b['id']}", headers=auth(token))).json()

    assert ra.status_code == 200
    assert rb.status_code == 422, f"rute lain diputar ulang: {rb.status_code}"
    assert b_kini["status"] == "active"


async def test_kunci_sama_di_post_habits_satu_baris(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    h = _kunci(api_bersama, token, "habit-1")
    badan = {"title": "Air", "period": "day", "target_count": 1}

    x = await api_bersama.klien.post("/v1/habits", json=badan, headers=h)
    y = await api_bersama.klien.post("/v1/habits", json=badan, headers=h)
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (n,) = k.execute("SELECT count(*) FROM habits WHERE user_id = %s", (uid,)).fetchone() or (
            0,
        )

    assert n == 1, "Idempotency-Key diabaikan: habit ganda"
    assert y.headers.get("Idempotent-Replayed") == "true"
    assert x.json() == y.json()


async def test_rujukan_diingat_dua_puluh_empat_jam(api_bersama: ApiUji) -> None:
    import hashlib

    uid, token = await api_bersama.pengguna_baru()
    await api_bersama.klien.post(
        "/v1/goals", json={"title": "X"}, headers=_kunci(api_bersama, token, "ttl-uji")
    )
    kunci = f"{api_bersama.awalan_redis}:idem:{uid}:{hashlib.sha256(b'ttl-uji').hexdigest()}"

    ttl = await api_bersama.app.state.redis.ttl(kunci)

    assert ttl > 23 * 3600, f"rujukan idempoten hanya diingat {ttl} detik"
