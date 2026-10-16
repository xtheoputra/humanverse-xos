"""spec/07 3.8 — `activities`: *“`source='inferred'` terpisah dari `manual`”*.

Terpisah di tiga arah: klien TIDAK BISA mencatat `inferred` (atau sumber apa
pun) lewat HTTP; jalur sistem (`catat_disimpulkan`) SELALU mencatat `inferred`;
dan pembacanya bisa memisahkan keduanya (`?source=`) — supaya Behavior Engine
(Sprint 5) tidak belajar dari tebakannya sendiri (spec/01).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn

from hvx.modules import activities
from hvx.modules.platform import KEDALAMAN_JSON_MAKS, transaksi_pengguna

pytestmark = pytest.mark.integration

LALU = (datetime.now(UTC) - timedelta(hours=3)).replace(microsecond=0)


async def _catat(api: ApiUji, token: str, **isi: Any) -> Any:
    isi.setdefault("kind", "workout")
    isi.setdefault("occurred_at", LALU.isoformat())
    return await api.klien.post("/v1/activities", json=isi, headers=auth(token))


async def _simpulkan(api: ApiUji, user_id: UUID, **isi: Any) -> activities.Aktivitas:
    async with transaksi_pengguna(api.app.state.engine, user_id) as conn:
        return await activities.catat_disimpulkan(
            conn, user_id, kind=isi.pop("kind", "workout"), occurred_at=LALU, **isi
        )


async def test_klien_hanya_bisa_mencatat_manual(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await _catat(api_bersama, token, duration_seconds=1800, payload={"jenis": "lari"})
    menyamar = await _catat(api_bersama, token, source="inferred")

    assert r.status_code == 201, r.text
    assert r.json()["source"] == "manual"
    assert menyamar.status_code == 400, "klien bisa menyatakan aktivitasnya disimpulkan"


async def test_jalur_sistem_selalu_inferred_dan_bisa_dipisahkan(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    manual = (await _catat(api_bersama, token, kind="meal")).json()
    tebakan = await _simpulkan(api_bersama, uid, kind="meal")
    k = api_bersama.klien

    hanya_manual = await k.get("/v1/activities", params={"source": "manual"}, headers=auth(token))
    hanya_tebakan = await k.get(
        "/v1/activities", params={"source": "inferred"}, headers=auth(token)
    )
    semua = await k.get("/v1/activities", headers=auth(token))

    assert tebakan.source == "inferred"
    assert [a["id"] for a in hanya_manual.json()["items"]] == [manual["id"]], (
        "tebakan sistem bercampur dengan catatan manusia"
    )
    assert [a["id"] for a in hanya_tebakan.json()["items"]] == [str(tebakan.id)]
    assert {a["source"] for a in semua.json()["items"]} == {"manual", "inferred"}


@pytest.mark.parametrize(
    "isi",
    [
        {"ended_at": (LALU - timedelta(minutes=1)).isoformat()},
        {"occurred_at": "2026-09-01T08:00:00"},  # tanpa zona
        {"kind": "Workout"},
        {"kind": "lari pagi"},
        {"duration_seconds": -1},
        {"duration_seconds": 8 * 86_400},  # > 7 hari
        {"payload": {"catatan": "a\u0000b"}},
        {"payload": {"x": "y" * 17_000}},
        {"source": "manual"},  # medan sumber tidak diterima sama sekali
    ],
)
async def test_aktivitas_berbentuk_salah_400(api_bersama: ApiUji, isi: dict[str, Any]) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await _catat(api_bersama, token, **isi)

    assert r.status_code == 400, r.text


def _bersarang(dalam: int) -> Any:
    isi: Any = "x"
    for _ in range(dalam):
        isi = {"a": isi}
    return isi


async def test_payload_terlalu_dalam_ditolak_sebelum_tersimpan(api_bersama: ApiUji) -> None:
    """Tinjauan keamanan Sprint 3 (S5): payload bersarang 100 tingkat lolos validasi,
    TERSIMPAN, lalu jawabannya gagal diserialisasi (500) — dan sejak itu `GET
    /v1/activities` pengguna itu 500, tanpa rute untuk menghapus barisnya."""
    _uid, token = await api_bersama.pengguna_baru()

    pas = await _catat(api_bersama, token, payload=_bersarang(KEDALAMAN_JSON_MAKS))
    lewat = await _catat(api_bersama, token, payload=_bersarang(KEDALAMAN_JSON_MAKS + 1))
    jauh = await _catat(api_bersama, token, payload=_bersarang(400))
    daftar = await api_bersama.klien.get("/v1/activities", headers=auth(token))

    assert pas.status_code == 201, pas.text
    assert (lewat.status_code, jauh.status_code) == (400, 400), (
        f"payload terlalu dalam tidak ditolak 400: {lewat.status_code} · {jauh.status_code}"
    )
    assert daftar.status_code == 200, daftar.text
    assert len(daftar.json()["items"]) == 1, "payload yang ditolak ikut tersimpan"


async def test_badan_json_sangat_dalam_400_bukan_500(api_bersama: ApiUji) -> None:
    """Lebih dalam dari batas rekursi pengurai JSON — di bawah batas ukuran badan 1 MiB."""
    _uid, token = await api_bersama.pengguna_baru()

    r = await api_bersama.klien.post(
        "/v1/activities",
        content="[" * 50_000 + "]" * 50_000,
        headers={**auth(token), "content-type": "application/json"},
    )

    assert r.status_code == 400, r.text[:200]


async def test_ended_at_masa_depan_dan_durasi_yang_bertentangan_ditolak(
    api_bersama: ApiUji,
) -> None:
    """Tinjauan kontrak Sprint 3 (K5): `ended_at` 2999 dengan `duration_seconds` 60 semula
    tersimpan — dua fakta tentang satu aktivitas yang saling membantah, dibaca apa adanya
    oleh Behavior Engine (Sprint 5)."""
    _uid, token = await api_bersama.pengguna_baru()
    selesai = (LALU + timedelta(minutes=30)).isoformat()

    sejam_lagi = (datetime.now(UTC) + timedelta(hours=1)).isoformat()

    nanti = await _catat(api_bersama, token, ended_at=sejam_lagi)
    jauh = await _catat(api_bersama, token, ended_at="2999-01-01T00:00:00Z")
    bertentangan = await _catat(api_bersama, token, ended_at=selesai, duration_seconds=60)
    cocok = await _catat(api_bersama, token, ended_at=selesai, duration_seconds=1800)

    assert nanti.status_code == 422, f"ended_at masa depan diterima: {nanti.status_code}"
    assert nanti.json()["error"]["code"] == "ended_at_in_future"
    assert jauh.status_code == 400, jauh.text  # rentang > 7 hari, batas duration_seconds
    assert bertentangan.status_code == 400, (
        f"durasi yang membantah ended_at diterima: {bertentangan.status_code}"
    )
    assert cocok.status_code == 201, cocok.text


async def test_id_buatan_klien_yang_sudah_ada_409(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    isi = {"id": str(uuid4()), "kind": "workout", "occurred_at": LALU.isoformat()}

    a = await api_bersama.klien.post("/v1/activities", json=isi, headers=auth(token))
    b = await api_bersama.klien.post("/v1/activities", json=isi, headers=auth(token))

    assert a.status_code == 201, a.text
    assert b.status_code == 409, f"id ganda → {b.status_code}"
    assert b.json()["error"]["code"] == "already_exists"


async def test_aktivitas_masa_depan_422(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()

    r = await _catat(api_bersama, token, occurred_at="2999-01-01T00:00:00Z")

    assert r.status_code == 422, r.text


async def test_saring_jenis_rentang_dan_halaman(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for jam in range(4):
        waktu = (LALU - timedelta(hours=jam)).isoformat()
        await _catat(api_bersama, token, kind="workout" if jam % 2 else "meal", occurred_at=waktu)
    k = api_bersama.klien

    workout = await k.get("/v1/activities", params={"kind": "workout"}, headers=auth(token))
    halaman1 = await k.get("/v1/activities", params={"limit": 3}, headers=auth(token))
    halaman2 = await k.get(
        "/v1/activities",
        params={"limit": 3, "cursor": halaman1.json()["next_cursor"]},
        headers=auth(token),
    )

    assert {a["kind"] for a in workout.json()["items"]} == {"workout"}
    assert len(workout.json()["items"]) == 2
    semua = [a["id"] for a in halaman1.json()["items"] + halaman2.json()["items"]]
    assert len(semua) == len(set(semua)) == 4
    assert halaman2.json()["next_cursor"] is None


async def test_saring_rentang_waktu(api_bersama: ApiUji) -> None:
    _uid, token = await api_bersama.pengguna_baru()
    for jam in (1, 2, 3):
        await _catat(api_bersama, token, occurred_at=(LALU - timedelta(hours=jam)).isoformat())
    dari = (LALU - timedelta(hours=2, minutes=30)).isoformat()
    sampai = (LALU - timedelta(hours=1, minutes=30)).isoformat()

    r = await api_bersama.klien.get(
        "/v1/activities", params={"from": dari, "to": sampai}, headers=auth(token)
    )

    assert r.status_code == 200, r.text
    waktu = [datetime.fromisoformat(a["occurred_at"]) for a in r.json()["items"]]
    assert waktu == [LALU - timedelta(hours=2)], f"rentang from–to aktivitas: {waktu}"


async def test_aktivitas_tanpa_event_v0_dan_milik_pemiliknya(api_bersama: ApiUji) -> None:
    """Peta aturan 6 (spec/06): belum ada jenis event V0 untuk aktivitas umum."""
    uid, token = await api_bersama.pengguna_baru()
    _lain, token_lain = await api_bersama.pengguna_baru()

    await _catat(api_bersama, token)
    lain = await api_bersama.klien.get("/v1/activities", headers=auth(token_lain))

    assert lain.json()["items"] == []
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik)) as k:
        (n,) = k.execute("SELECT count(*) FROM events WHERE user_id = %s", (uid,)).fetchone() or (
            0,
        )
    assert n == 0
