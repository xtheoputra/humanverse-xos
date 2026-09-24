"""spec/07 3.6 — ekstraksi memori dari jurnal & mood, dan penyelarasnya ke Qdrant.

3.6 Selesai bila: *tiap memori punya `kind`, `scope`, `confidence`,
`evidence_count`, `source_event_id`.*

Jalannya sungguhan dari ujung ke ujung: tulisan lewat HTTP → event (3.2) →
relay → stream → konsumen `memori` (3.3) → baris `memories` → penyelaras →
Qdrant (3.5). Tiap uji memakai koleksi Qdrant sekali pakai.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from psycopg.rows import dict_row

from hvx.modules import events, memory, platform

pytestmark = pytest.mark.integration

PENYEMAT = platform.PenyematHash(b"k" * 32)


@pytest.fixture
async def koleksi(url_qdrant_uji: str) -> AsyncIterator[tuple[platform.KlienVektor, str]]:
    klien = platform.KlienVektor(url_qdrant_uji)
    nama = f"uji-memori-{uuid.uuid4().hex[:12]}"
    try:
        yield klien, nama
    finally:
        async with httpx.AsyncClient(base_url=url_qdrant_uji) as h:
            await h.delete(f"/collections/{nama}")
        await klien.tutup()


def _awalan() -> str:
    return f"uji-memori-{uuid.uuid4().hex[:10]}"


async def _ekstrak_semua(api: ApiUji, awalan: str) -> None:
    """Relay → stream → konsumen `memori`, sampai stream habis."""
    await events.Relay(api.app.state.engine, api.app.state.redis, awalan).putaran()
    k = events.KonsumenStream(
        engine=api.app.state.engine,
        redis=api.app.state.redis,
        awalan=awalan,
        grup="memori",
        nama="uji",
        jenis=memory.JENIS_EVENT,
        tangani=memory.ekstrak,
        blok_ms=50,
        jumlah=1000,
    )
    await k.siapkan()
    for _ in range(3):
        await k.putaran()


def _penyelaras(api: ApiUji, koleksi: tuple[platform.KlienVektor, str]) -> memory.PenyelarasVektor:
    return memory.PenyelarasVektor(api.app.state.engine, koleksi[0], PENYEMAT, koleksi[1])


def _memori_milik(api: ApiUji, uid: UUID) -> list[dict[str, Any]]:
    """Dibaca PEMILIK skema — bukan lewat kode yang diuji."""
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        return k.execute(
            """
            SELECT m.*, e.event_type AS jenis_sumber, e.subject_id AS subjek_sumber
            FROM memories m LEFT JOIN events e ON e.id = m.source_event_id
            WHERE m.user_id = %s ORDER BY m.valid_from
            """,
            (uid,),
        ).fetchall()


def _event(api: ApiUji, kunci: str) -> events.EventMasuk:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), row_factory=dict_row) as k:
        baris = k.execute(
            """
            SELECT id, user_id, event_type, schema_version, occurred_at, recorded_at, source,
                   subject_type, subject_id, payload
            FROM events WHERE idempotency_key = %s
            """,
            (kunci,),
        ).fetchone()
    assert baris is not None, f"event {kunci} tidak diterbitkan"
    return events.EventMasuk(**baris)


async def _post(api: ApiUji, token: str, jalur: str, isi: dict[str, Any]) -> dict[str, Any]:
    r = await api.klien.post(jalur, json=isi, headers=auth(token))
    assert r.status_code == 201, r.text
    hasil: dict[str, Any] = r.json()
    return hasil


async def _titik(url_qdrant: str, nama: str, id_: UUID) -> dict[str, Any] | None:
    """Titik Qdrant apa adanya — payload DAN vektornya."""
    async with httpx.AsyncClient(base_url=url_qdrant) as h:
        r = await h.post(
            f"/collections/{nama}/points",
            json={"ids": [str(id_)], "with_payload": True, "with_vector": True},
        )
    assert r.status_code == 200, r.text
    titik: list[dict[str, Any]] = r.json()["result"]
    return titik[0] if titik else None


def _kosinus(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


# ────────────────────────────────────────────────────────────── 3.6 ──


async def test_tiap_memori_punya_kind_scope_confidence_bukti_dan_event_sumber(
    api_bersama: ApiUji,
) -> None:
    """spec/07 3.6 Selesai bila — dua mood dan satu jurnal, tiga memori, lima medan."""
    uid, token = await api_bersama.pengguna_baru()
    m1 = await _post(api_bersama, token, "/v1/moods", {"valence": 2, "label": "cemas"})
    m2 = await _post(api_bersama, token, "/v1/moods", {"valence": 4, "note": "lega"})
    j = await _post(api_bersama, token, "/v1/journal", {"title": "Senin", "body": "Rapat lagi."})

    await _ekstrak_semua(api_bersama, _awalan())

    memori = _memori_milik(api_bersama, uid)
    assert len(memori) == 3, f"memori: {memori}"
    for m in memori:
        assert m["kind"] == "episodic"
        assert m["scope"] in {"mood", "journal_raw"}
        assert m["confidence"] == Decimal("1.000")
        assert m["evidence_count"] == 1
        assert m["source_event_id"] is not None, "memori tanpa event sumber"
    sumber = {(m["jenis_sumber"], m["subjek_sumber"], m["scope"]) for m in memori}
    assert sumber == {
        ("mood.logged", UUID(m1["id"]), "mood"),
        ("mood.logged", UUID(m2["id"]), "mood"),
        ("journal.created", UUID(j["id"]), "journal_raw"),
    }


async def test_isi_memori_dari_sumbernya_bukan_dari_event(api_bersama: ApiUji) -> None:
    """`note` mood dan isi jurnal tidak pernah masuk event (spec/03) — dibaca dari barisnya."""
    uid, token = await api_bersama.pengguna_baru()
    mood = await _post(
        api_bersama,
        token,
        "/v1/moods",
        {"valence": 2, "label": "cemas", "note": "capek sesudah rapat"},
    )
    await _post(api_bersama, token, "/v1/journal", {"title": "Selasa", "body": "Isi pribadi."})

    await _ekstrak_semua(api_bersama, _awalan())

    isi = {m["scope"]: m for m in _memori_milik(api_bersama, uid)}
    assert isi["mood"]["content"] == "Mood dilaporkan 2/5 (cemas): capek sesudah rapat"
    assert isi["mood"]["valid_from"].isoformat() == mood["occurred_at"].replace("Z", "+00:00")
    assert isi["journal_raw"]["content"] == "Selasa\n\nIsi pribadi."
    assert isi["mood"]["model_version"] is None, "ekstraksi menyemat sendiri — Qdrant di jalurnya"


async def test_event_yang_diserahkan_lagi_tidak_menggandakan_memori(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    mood = await _post(api_bersama, token, "/v1/moods", {"valence": 3})
    ev = _event(api_bersama, f"mood:{mood['id']}")

    for _ in range(2):
        async with platform.transaksi_pengguna(api_bersama.app.state.engine, uid) as conn:
            await memory.ekstrak(conn, ev)

    assert len(_memori_milik(api_bersama, uid)) == 1, "memori ganda untuk satu event"


async def test_jurnal_yang_dihapus_sebelum_diekstrak_tidak_diingat(api_bersama: ApiUji) -> None:
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "Tulisan yang disesali."})
    r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    assert r.status_code == 204

    await _ekstrak_semua(api_bersama, _awalan())

    assert _memori_milik(api_bersama, uid) == [], "jurnal terhapus tetap diingat"


async def test_sunting_jurnal_menunggu_ekstraksi_yang_sedang_membacanya(
    api_bersama: ApiUji,
) -> None:
    """Ekstraksi membaca isi lama; `PATCH` serentak mengganti isinya. Tanpa kunci BAGI,
    pendengar `PATCH` tidak melihat memori yang belum commit — lalu ekstraksi commit
    isi LAMA, dan kalimat yang sudah dihapus pemiliknya hidup terus di memori."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "kalimat yang akan dihapus"})
    ev = _event(api_bersama, f"journal:{j['id']}")

    async with platform.transaksi_pengguna(api_bersama.app.state.engine, uid) as conn:
        await memory.ekstrak(conn, ev)
        sunting = asyncio.create_task(
            api_bersama.klien.patch(
                f"/v1/journal/{j['id']}", json={"body": "isi baru"}, headers=auth(token)
            )
        )
        await asyncio.sleep(0.5)
        assert not sunting.done(), "PATCH tidak menunggu ekstraksi yang sedang membaca jurnal"
    assert (await sunting).status_code == 200

    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "isi baru", f"memori memuat isi lama: {m['content']!r}"


# ─────────────────────────────────────── 3.5 penyelaras memories → Qdrant ──


async def test_penyelaras_menyemat_tanpa_isi_di_payload(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await _post(api_bersama, token, "/v1/moods", {"valence": 2, "note": "rahasia-kecil-xyz"})
    await _ekstrak_semua(api_bersama, _awalan())

    assert await _penyelaras(api_bersama, koleksi).putaran() >= 1

    (m,) = _memori_milik(api_bersama, uid)
    assert m["model_version"] == PENYEMAT.nama
    assert m["embedding_id"] == str(m["id"])
    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    assert titik is not None, "memori tersemat tanpa titik"
    assert titik["payload"] == {
        "user_id": str(uid),
        "scope": "mood",
        "kind": "episodic",
        "model": PENYEMAT.nama,
    }, "payload Qdrant memuat lebih dari rujukan"


async def test_jurnal_disunting_memori_dan_vektornya_mengikuti(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "bertengkar dengan atasan"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()

    r = await api_bersama.klien.patch(
        f"/v1/journal/{j['id']}", json={"body": "berdamai dengan atasan"}, headers=auth(token)
    )
    assert r.status_code == 200
    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "berdamai dengan atasan"
    assert m["model_version"] is None, "isi berubah, vektor lama dianggap masih cocok"
    await _penyelaras(api_bersama, koleksi).putaran()

    titik = await _titik(url_qdrant_uji, koleksi[1], m["id"])
    assert titik is not None
    assert _kosinus(titik["vector"], PENYEMAT.semat("berdamai dengan atasan")) > 0.999, (
        "vektor isi lama tertinggal di Qdrant"
    )


async def test_jurnal_dihapus_isi_memori_hilang_seketika_lalu_titiknya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str], url_qdrant_uji: str
) -> None:
    """Naskah (docs/139): *“tidak boleh hanya menghapus row di PostgreSQL”*."""
    uid, token = await api_bersama.pengguna_baru()
    j = await _post(api_bersama, token, "/v1/journal", {"body": "rahasia yang dicabut"})
    await _ekstrak_semua(api_bersama, _awalan())
    await _penyelaras(api_bersama, koleksi).putaran()
    (m,) = _memori_milik(api_bersama, uid)
    assert await _titik(url_qdrant_uji, koleksi[1], m["id"]) is not None

    r = await api_bersama.klien.delete(f"/v1/journal/{j['id']}", headers=auth(token))
    assert r.status_code == 204

    (m,) = _memori_milik(api_bersama, uid)
    assert m["content"] == "", "isi jurnal terhapus tetap di memori sampai penyelaras lewat"
    assert m["deleted_at"] is not None

    await _penyelaras(api_bersama, koleksi).putaran()
    assert _memori_milik(api_bersama, uid) == []
    assert await _titik(url_qdrant_uji, koleksi[1], m["id"]) is None, "titik vektornya tertinggal"


async def test_penyemat_lain_disemat_ulang_bukan_dicampur(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Kunci penyemat diganti (K-26): vektor lama tidak sebanding dengan kueri baru."""
    uid, token = await api_bersama.pengguna_baru()
    await _post(api_bersama, token, "/v1/moods", {"valence": 3, "note": "jalan sore"})
    await _ekstrak_semua(api_bersama, _awalan())
    lain = platform.PenyematHash(b"z" * 32)
    await memory.PenyelarasVektor(
        api_bersama.app.state.engine, koleksi[0], lain, koleksi[1]
    ).putaran()

    await _penyelaras(api_bersama, koleksi).putaran()

    (m,) = _memori_milik(api_bersama, uid)
    assert m["model_version"] == PENYEMAT.nama, "memori penyemat lama tidak disemat ulang"
