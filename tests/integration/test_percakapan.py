"""spec/07 4.8 — percakapan + SSE: *token mengalir; `done` memuat `cost_usd`*.

Aplikasi utuh (`create_app` + lifespan): runtime, gerbang risiko, dan AI Gateway yang
dirakit `hvx.main` — bukan rakitan uji. Model lokal V0 diberi HARGA lewat
`HVX_MODEL_HARGA`, supaya biaya nol tidak bisa lolos sebagai "tercatat".

Juga bukti ujung-ke-ujung 4.1: *“catat mood 3”* lewat percakapan tidak menyentuh
penyedia model sama sekali.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

import httpx
import pytest
from _bantuan_agent import REGISTRI, sql
from _bantuan_db import ApiUji, BasisDataV0, auth
from asgi_lifespan import LifespanManager
from test_habits import buat_habit

from hvx.main import create_app
from hvx.modules import identity, platform
from hvx.modules.platform import Settings, buat_engine

pytestmark = pytest.mark.integration

HARGA = {
    "lokal/hvx-ringkas-v1": (Decimal(1), Decimal(2)),
    "lokal/hvx-nalar-v1": (Decimal(10), Decimal(30)),
}


@pytest.fixture(scope="module")
async def api(v0_bersama: BasisDataV0, url_redis_uji: str) -> AsyncIterator[ApiUji]:
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    app = create_app(
        Settings(
            env="test",
            database_url=v0_bersama.dsn_aplikasi,
            redis_url=url_redis_uji,
            redis_prefix=awalan,
            rate_limit_ip="100000/60",
            rate_limit_user="100000/60",
            model_harga=HARGA,
        )
    )
    async with (
        LifespanManager(app),
        httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://uji") as klien,
    ):
        engine_pekerja = buat_engine(v0_bersama.dsn_pekerja)
        try:
            yield ApiUji(
                app=app,
                klien=klien,
                db=v0_bersama,
                awalan_redis=awalan,
                engine_pekerja=engine_pekerja,
            )
        finally:
            await engine_pekerja.dispose()


def _sse(teks: str) -> list[tuple[str, dict[str, Any]]]:
    peristiwa = []
    for blok in filter(None, teks.strip().split("\n\n")):
        baris = dict(b.split(": ", 1) for b in blok.split("\n") if ": " in b)
        peristiwa.append((baris["event"], json.loads(baris["data"])))
    return peristiwa


async def _percakapan(api: ApiUji, token: str) -> str:
    r = await api.klien.post("/v1/conversations", json={"title": "Uji"}, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: str = r.json()["id"]
    return hasil


async def _kirim(api: ApiUji, token: str, cid: str, isi: str, **kepala: str) -> dict[str, Any]:
    r = await api.klien.post(
        f"/v1/conversations/{cid}/messages",
        json={"content": isi},
        headers={**auth(token), **kepala},
    )
    assert r.status_code == 202, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def _aliran(api: ApiUji, token: str, cid: str) -> list[tuple[str, dict[str, Any]]]:
    r = await api.klien.get(f"/v1/conversations/{cid}/stream", headers=auth(token))
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].startswith("text/event-stream")
    return _sse(r.text)


def test_anggaran_harian_dirakit_dari_setelan(api: ApiUji) -> None:
    assert api.app.state.percakapan.runtime.anggaran_harian_usd == Decimal("0.50"), (
        "anggaran harian tidak dirakit"
    )


async def test_percakapan_dibuat_dan_didaftar(api: ApiUji) -> None:
    _uid, token = await api.pengguna_baru()
    kunci = {"Idempotency-Key": f"k-{uuid.uuid4().hex}"}

    a = await api.klien.post(
        "/v1/conversations", json={"title": "Pagi"}, headers={**auth(token), **kunci}
    )
    b = await api.klien.post(
        "/v1/conversations", json={"title": "Pagi"}, headers={**auth(token), **kunci}
    )
    daftar = await api.klien.get("/v1/conversations", headers=auth(token))

    assert (a.status_code, b.status_code) == (201, 201)
    assert a.json() == b.json()
    assert b.headers["Idempotent-Replayed"] == "true"
    assert [p["id"] for p in daftar.json()["items"]] == [a.json()["id"]]
    assert daftar.json()["items"][0]["message_count"] == 0


async def test_token_mengalir_lalu_done_membawa_biaya_keyakinan_dan_alasan(api: ApiUji) -> None:
    uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)

    terima = await _kirim(api, token, cid, "bagaimana hariku?")
    peristiwa = await _aliran(api, token, cid)
    riwayat = (await api.klien.get(f"/v1/conversations/{cid}/messages", headers=auth(token))).json()

    jenis = [j for j, _ in peristiwa]
    token_ = [d["text"] for j, d in peristiwa if j == "token"]
    (done,) = [d for j, d in peristiwa if j == "done"]
    biaya_pohon = sql(
        api,
        "SELECT sum(cost_usd) FROM agent_runs WHERE id = %s OR parent_run_id = %s",
        terima["agent_run_id"],
        terima["agent_run_id"],
    )[0][0]
    assert terima["status"] == "processing"
    assert "tool_call" in jenis, f"tool_call tidak mengalir: {jenis}"
    assert len(token_) > 1, f"token tidak mengalir: {jenis}"
    assert jenis[-1:] == ["done"], "aliran tidak berakhir dengan done"
    assert done["content"] == "".join(token_)
    assert done["cost_usd"] == float(biaya_pohon) > 0, "done tanpa biaya permintaannya"
    assert done["agent_run_id"] == terima["agent_run_id"]
    assert done["rationale"], "done tanpa alasan"
    assert 0 <= done["confidence"] <= 1
    balasan, pesan = riwayat["items"]  # terbaru dulu
    assert (pesan["role"], pesan["content"], pesan["agent_run_id"]) == (
        "user",
        "bagaimana hariku?",
        terima["agent_run_id"],
    )
    assert (balasan["role"], balasan["content"], balasan["rationale"]) == (
        "assistant",
        done["content"],
        done["rationale"],
    ), "riwayat kehilangan alasan balasannya (E-194)"
    assert balasan["cost_usd"] == done["cost_usd"]
    assert uid


async def test_klien_yang_tersambung_belakangan_menerima_seluruh_aliran(api: ApiUji) -> None:
    """Jaringan seluler: SSE tersambung SESUDAH gilirannya selesai — tetap dari token pertama."""
    _uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)

    await _kirim(api, token, cid, "bagaimana hariku?")
    for _ in range(200):  # tunggu balasannya tersimpan — gilirannya sudah selesai
        riwayat = await api.klien.get(f"/v1/conversations/{cid}/messages", headers=auth(token))
        if len(riwayat.json()["items"]) == 2:
            break
        await asyncio.sleep(0.05)
    peristiwa = await _aliran(api, token, cid)

    jenis = [j for j, _ in peristiwa]
    assert jenis.count("token") > 1, f"klien yang terlambat kehilangan awal aliran: {jenis}"
    assert jenis[-1:] == ["done"]


async def test_catat_mood_lewat_percakapan_tanpa_model_sama_sekali(
    api: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """4.1 ujung-ke-ujung: perintah berbentuk tetap = `INSERT`, bukan inferensi."""
    uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)
    dipanggil: list[str] = []
    asli = platform.PenyediaLokal.alirkan

    def mencatat(self: Any, model: str, p: Any) -> Any:
        dipanggil.append(model)
        return asli(self, model, p)

    monkeypatch.setattr(platform.PenyediaLokal, "alirkan", mencatat)

    terima = await _kirim(api, token, cid, "catat mood 3 cemas")
    peristiwa = await _aliran(api, token, cid)

    assert dipanggil == [], f"“catat mood” memanggil model: {dipanggil}"
    assert (terima["agent_run_id"], terima["status"]) == (None, "completed"), (
        "“catat mood” dijalankan agent"
    )
    (done,) = [d for j, d in peristiwa if j == "done"]
    assert (done["content"], done["cost_usd"], done["confidence"]) == (
        "Mood 3/5 (cemas) dicatat.",
        0,
        1,
    )
    assert sql(api, "SELECT valence, label FROM mood_entries WHERE user_id = %s", uid) == [
        (3, "cemas")
    ]
    assert sql(api, "SELECT count(*) FROM agent_runs WHERE user_id = %s", uid) == [(0,)]


async def _tahan(api: ApiUji, token: str, cid: str, isi: str) -> dict[str, Any]:
    await _kirim(api, token, cid, isi)
    peristiwa = await _aliran(api, token, cid)
    tanya = [d for j, d in peristiwa if j == "confirmation_required"]
    assert len(tanya) == 1, f"confirmation_required tidak mengalir: {[j for j, _ in peristiwa]}"
    assert [j for j, _ in peristiwa][-1:] == ["done"]
    return tanya[0]


async def test_konfirmasi_lewat_percakapan_lalu_giliran_diulang(api: ApiUji) -> None:
    uid, token = await api.pengguna_baru()
    habit = await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)

    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")
    r = await api.klien.post(
        f"/v1/conversations/{cid}/confirmations",
        json={"token": tanya["token"], "decision": "allow_always"},
        headers=auth(token),
    )
    peristiwa = await _aliran(api, token, cid)
    lagi = await api.klien.post(
        f"/v1/conversations/{cid}/confirmations",
        json={"token": tanya["token"], "decision": "allow_once"},
        headers=auth(token),
    )

    assert {
        k: tanya[k] for k in ("kind", "agent", "tool", "risk_level", "scopes", "remember_allowed")
    } == {
        "kind": "permission",
        "agent": "habit-agent",
        "tool": "habit.complete",
        "risk_level": 2,
        "scopes": ["habits"],
        "remember_allowed": True,
    }
    assert (r.status_code, r.json()["status"]) == (202, "processing"), r.text
    (done,) = [d for j, d in peristiwa if j == "done"]
    assert done["content"].startswith("“Lari pagi” ditandai selesai untuk ")
    assert sql(api, "SELECT count(*) FROM habit_completions WHERE habit_id = %s", habit["id"]) == [
        (1,)
    ]
    assert (lagi.status_code, lagi.json()["error"]["code"]) == (409, "confirmation_answered")
    assert uid


async def test_konfirmasi_ditolak_tidak_menjalankan_apa_pun(api: ApiUji) -> None:
    uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)

    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")
    r = await api.klien.post(
        f"/v1/conversations/{cid}/confirmations",
        json={"token": tanya["token"], "decision": "reject"},
        headers=auth(token),
    )
    peristiwa = await _aliran(api, token, cid)

    assert (r.status_code, r.json()["status"]) == (202, "completed"), (
        "penolakan tetap menjalankan giliran"
    )
    (done,) = [d for j, d in peristiwa if j == "done"]
    assert done["content"] == "Baik, habit.complete tidak dijalankan."
    assert sql(api, "SELECT count(*) FROM habit_completions WHERE user_id = %s", uid) == [(0,)]


async def test_token_konfirmasi_percakapan_lain_ditolak(api: ApiUji) -> None:
    _uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid, lain = await _percakapan(api, token), await _percakapan(api, token)
    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")

    r = await api.klien.post(
        f"/v1/conversations/{lain}/confirmations",
        json={"token": tanya["token"], "decision": "allow_once"},
        headers=auth(token),
    )

    assert (r.status_code, r.json().get("error", {}).get("code")) == (
        422,
        "invalid_confirmation",
    ), "token konfirmasi percakapan lain diterima"


async def test_satu_giliran_per_percakapan(api: ApiUji, monkeypatch: pytest.MonkeyPatch) -> None:
    _uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)
    lepas = asyncio.Event()
    asli = platform.PenyediaLokal.alirkan

    async def tertahan(self: Any, model: str, p: Any) -> AsyncIterator[str]:
        await lepas.wait()
        async for x in asli(self, model, p):
            yield x

    monkeypatch.setattr(platform.PenyediaLokal, "alirkan", tertahan)

    await _kirim(api, token, cid, "halo")
    kedua = await api.klien.post(
        f"/v1/conversations/{cid}/messages", json={"content": "halo lagi"}, headers=auth(token)
    )
    lepas.set()
    peristiwa = await _aliran(api, token, cid)

    assert (kedua.status_code, kedua.json().get("error", {}).get("code")) == (
        409,
        "turn_in_progress",
    ), "dua giliran serentak dalam satu percakapan"
    assert [j for j, _ in peristiwa][-1] == "done"


async def test_percakapan_orang_lain_tidak_terjangkau(api: ApiUji) -> None:
    _a, token_a = await api.pengguna_baru()
    _b, token_b = await api.pengguna_baru()
    cid = await _percakapan(api, token_a)
    h = auth(token_b)

    pesan = await api.klien.get(f"/v1/conversations/{cid}/messages", headers=h)
    aliran = await api.klien.get(f"/v1/conversations/{cid}/stream", headers=h)
    kirim = await api.klien.post(
        f"/v1/conversations/{cid}/messages", json={"content": "x"}, headers=h
    )

    assert (pesan.status_code, aliran.status_code, kirim.status_code) == (404, 404, 404), (
        "percakapan orang lain terjangkau"
    )


async def test_aliran_tanpa_giliran_204(api: ApiUji) -> None:
    _uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)

    r = await api.klien.get(f"/v1/conversations/{cid}/stream", headers=auth(token))

    assert r.status_code == 204, "SSE tanpa giliran — 204 berarti jangan menyambung ulang"


async def test_pesan_yang_dikirim_ulang_tidak_melahirkan_giliran_kedua(api: ApiUji) -> None:
    uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)
    kunci = {"Idempotency-Key": f"k-{uuid.uuid4().hex}"}

    a = await _kirim(api, token, cid, "halo", **kunci)
    await _aliran(api, token, cid)
    r = await api.klien.post(
        f"/v1/conversations/{cid}/messages",
        json={"content": "halo"},
        headers={**auth(token), **kunci},
    )

    assert (r.status_code, r.headers["Idempotent-Replayed"]) == (202, "true")
    assert r.json() == {**a, "status": "completed"}
    assert sql(
        api, "SELECT count(*) FROM agent_runs WHERE user_id = %s AND parent_run_id IS NULL", uid
    ) == [(1,)]


# ── Tinjauan Sprint 4 (E-199 · E-200 · E-202 · E-203) ──────────────────────────────


def _kode(r: httpx.Response) -> str | None:
    kode: str | None = r.json().get("error", {}).get("code")
    return kode


async def _jawab(api: ApiUji, token: str, cid: str, tok: str, keputusan: str) -> httpx.Response:
    return await api.klien.post(
        f"/v1/conversations/{cid}/confirmations",
        json={"token": tok, "decision": keputusan},
        headers=auth(token),
    )


async def test_id_percakapan_buatan_klien_yang_sudah_ada_409(api: ApiUji) -> None:
    """spec/04 *klien boleh membuat id sendiri* — id kembar `409 already_exists` seperti
    modul lain, bukan 500 (tinjauan kontrak Sprint 4) — juga id milik pengguna lain."""
    _a, token_a = await api.pengguna_baru()
    _b, token_b = await api.pengguna_baru()
    cid = str(uuid.uuid4())

    awal = await api.klien.post("/v1/conversations", json={"id": cid}, headers=auth(token_a))
    ulang = await api.klien.post("/v1/conversations", json={"id": cid}, headers=auth(token_a))
    lain = await api.klien.post("/v1/conversations", json={"id": cid}, headers=auth(token_b))

    assert awal.status_code == 201, awal.text
    assert [(r.status_code, _kode(r)) for r in (ulang, lain)] == [(409, "already_exists")] * 2


async def test_id_pesan_kembar_409_dan_aliran_giliran_terakhir_utuh(api: ApiUji) -> None:
    """E-200: kiriman ulang klien luring (id buatannya, tanpa Idempotency-Key yang sama) —
    dulu 500, run akarnya ditinggal `running` selamanya, dan `error` menimpa aliran."""
    uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)
    kirim = {"id": str(uuid.uuid4()), "content": "halo"}

    a = await api.klien.post(f"/v1/conversations/{cid}/messages", json=kirim, headers=auth(token))
    assert a.status_code == 202, a.text
    giliran = await _aliran(api, token, cid)
    b = await api.klien.post(f"/v1/conversations/{cid}/messages", json=kirim, headers=auth(token))
    sesudah = await _aliran(api, token, cid)

    assert (b.status_code, _kode(b)) == (409, "already_exists"), b.text
    assert sql(
        api, "SELECT count(*) FROM agent_runs WHERE user_id = %s AND status = 'running'", uid
    ) == [(0,)], "run ditinggal running"
    assert sql(
        api, "SELECT count(*) FROM agent_runs WHERE user_id = %s AND status = 'failed'", uid
    ) == [(0,)], "id kembar menulis run lalu menggagalkannya — diperiksa sesudah, bukan sebelum"
    assert sesudah == giliran, "permintaan yang ditolak menimpa aliran giliran terakhir"


async def test_id_pesan_milik_pengguna_lain_run_yang_terlanjur_ditulis_ditutup(api: ApiUji) -> None:
    """Id pesan pengguna LAIN tidak terlihat sebelum run ditulis (RLS) — tabrakannya baru
    ketahuan saat pesan disisipkan. Run yang terlanjur ditulis ditutup `failed` (E-200)."""
    _a, token_a = await api.pengguna_baru()
    uid_b, token_b = await api.pengguna_baru()
    cid_a, cid_b = await _percakapan(api, token_a), await _percakapan(api, token_b)
    kirim = {"id": str(uuid.uuid4()), "content": "halo"}
    r = await api.klien.post(
        f"/v1/conversations/{cid_a}/messages", json=kirim, headers=auth(token_a)
    )
    assert r.status_code == 202, r.text
    await _aliran(api, token_a, cid_a)

    b = await api.klien.post(
        f"/v1/conversations/{cid_b}/messages", json=kirim, headers=auth(token_b)
    )
    runs = sql(api, "SELECT status, error FROM agent_runs WHERE user_id = %s", uid_b)
    aliran_b = await api.klien.get(f"/v1/conversations/{cid_b}/stream", headers=auth(token_b))

    assert (b.status_code, _kode(b)) == (409, "already_exists"), b.text
    assert runs == [("failed", {"code": "already_exists", "type": "GalatApi"})], (
        f"run yang ditulis sebelum pesannya ditolak tidak ditutup: {runs}"
    )
    assert aliran_b.status_code == 204, "permintaan yang ditolak meninggalkan giliran di aliran"


async def test_dua_izin_dalam_satu_giliran_bisa_dijawab_dan_keduanya_berlaku(
    api: ApiUji,
) -> None:
    """E-199: pengguna memilih *“tanya aku”* untuk habit-agent MEMBACA habits, lalu
    `habit.complete` (R2) meminta izin kedua — dulu token kedua ditolak `422` (pesannya
    dicari di run akar ulangan), dan persetujuan pertama hilang di ulangan berikutnya."""
    uid, token = await api.pengguna_baru()
    habit = await buat_habit(api, token, title="Lari pagi")
    izin = api.app.state.percakapan._izin
    await izin.tetapkan(uid, identity.Subjek("agent", "habit-agent"), "habits", "read", "ask")
    cid = await _percakapan(api, token)

    pertama = await _tahan(api, token, cid, "tandai lari pagi selesai")
    r1 = await _jawab(api, token, cid, pertama["token"], "allow_once")
    assert r1.status_code == 202, f"izin pertama ditolak: {r1.text}"
    ulang = await _aliran(api, token, cid)
    (kedua,) = [d for j, d in ulang if j == "confirmation_required"]
    r2 = await _jawab(api, token, cid, kedua["token"], "allow_once")
    assert r2.status_code == 202, f"izin kedua ditolak: {r2.text}"
    akhir = await _aliran(api, token, cid)

    assert (pertama["tool"], kedua["tool"]) == ("habit.list", "habit.complete")
    assert [j for j, _ in akhir if j == "confirmation_required"] == [], (
        "persetujuan pertama hilang di ulangan kedua — ditanya lagi"
    )
    (done,) = [d for j, d in akhir if j == "done"]
    assert done["content"].startswith("“Lari pagi” ditandai selesai untuk ")
    assert sql(api, "SELECT count(*) FROM habit_completions WHERE habit_id = %s", habit["id"]) == [
        (1,)
    ]


async def test_jawaban_konfirmasi_yang_ditolak_tidak_menimpa_aliran(api: ApiUji) -> None:
    """E-202: `GET …/stream` = seluruh peristiwa giliran TERAKHIR. Jawaban kedua (409) bukan
    giliran — dulu `jawab` memulai giliran baru SEBELUM memeriksanya, lalu mengirim
    `error`: klien yang menyambung ulang kehilangan `done` yang sungguh terjadi."""
    _uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)
    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")
    r = await _jawab(api, token, cid, tanya["token"], "allow_once")
    assert r.status_code == 202, r.text
    giliran = await _aliran(api, token, cid)

    lagi = await _jawab(api, token, cid, tanya["token"], "allow_once")
    rusak = await _jawab(api, token, cid, tanya["token"] + "x", "allow_once")
    sesudah = await _aliran(api, token, cid)

    assert (lagi.status_code, _kode(lagi)) == (409, "confirmation_answered")
    assert (rusak.status_code, _kode(rusak)) == (422, "invalid_confirmation")
    assert sesudah == giliran, "jawaban yang ditolak menimpa aliran giliran terakhir"


async def test_ketukan_ganda_saat_giliran_ulangan_berjalan_dijawab_sudah_dijawab(
    api: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """spec/04: jawaban kedua → `409 confirmation_answered` — juga saat giliran ulangannya
    masih berjalan (dulu `turn_in_progress`: giliran diperiksa sebelum tokennya)."""
    _uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)
    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")
    lepas = asyncio.Event()
    pelaksana = api.app.state.percakapan.runtime.pelaksana
    asli = pelaksana._impl["habit.complete"]

    async def tertahan(k: Any, m: dict[str, Any]) -> dict[str, Any]:
        await lepas.wait()
        hasil: dict[str, Any] = await asli(k, m)
        return hasil

    monkeypatch.setitem(pelaksana._impl, "habit.complete", tertahan)

    r1 = await _jawab(api, token, cid, tanya["token"], "allow_once")
    r2 = await _jawab(api, token, cid, tanya["token"], "allow_once")
    lepas.set()
    await _aliran(api, token, cid)

    assert r1.status_code == 202, r1.text
    assert (r2.status_code, _kode(r2)) == (409, "confirmation_answered")


async def test_galat_sse_berkode_api_bukan_kode_internal(api: ApiUji) -> None:
    """E-203 (AGENTS.md §7): `error.code` di SSE = kode API berbahasa Inggris — batas laju
    tool menjadi `rate_limited` (spec/04), bukan `terlalu_sering` pelaksana."""
    uid, token = await api.pengguna_baru()
    cid = await _percakapan(api, token)
    pembatas: platform.PembatasLaju = api.app.state.percakapan.runtime.pelaksana._pembatas
    jumlah = int(REGISTRI.alat["agent.coach"].rate_limit.split("/")[0])
    batas = platform.BatasLaju("alat-agent-coach", jumlah, 60)
    for _ in range(jumlah):
        await pembatas.ambil(batas, str(uid))

    await _kirim(api, token, cid, "halo")
    peristiwa = await _aliran(api, token, cid)

    assert peristiwa[-1] == ("error", {"code": "rate_limited"}), f"SSE: {peristiwa}"


async def test_jawaban_yang_kalah_balapan_tidak_menimpa_aliran(
    api: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dua jawaban serentak: keduanya lolos pemeriksaan awal, satu kalah saat dicatat
    (`UPDATE … WHERE confirmed_by_user IS NULL`). Yang kalah bukan giliran — giliran yang
    sudah dimulainya di-`urungkan`, aliran tetap giliran terakhir (E-202)."""
    from hvx.modules.agents import repository

    _uid, token = await api.pengguna_baru()
    await buat_habit(api, token, title="Lari pagi")
    cid = await _percakapan(api, token)
    tanya = await _tahan(api, token, cid, "tandai lari pagi selesai")
    sebelum = await _aliran(api, token, cid)

    async def kalah(*_a: Any, **_k: Any) -> bool:
        return False

    monkeypatch.setattr(repository, "jawab_run", kalah)
    r = await _jawab(api, token, cid, tanya["token"], "allow_once")
    sesudah = await _aliran(api, token, cid)

    assert (r.status_code, _kode(r)) == (409, "confirmation_answered")
    assert sesudah == sebelum, "jawaban yang kalah balapan menimpa aliran giliran terakhir"
