"""spec/07 3.6 · 3.7 — ekstraksi memori dari jurnal & mood, dan pencarian bersaring scope.

3.6 Selesai bila: *tiap memori punya `kind`, `scope`, `confidence`,
`evidence_count`, `source_event_id`.*
3.7 Selesai bila: *agent tanpa izin scope **tidak** menerima barisnya.*

Jalannya sungguhan dari ujung ke ujung: tulisan lewat HTTP → event (3.2) →
relay → stream → konsumen `memori` (3.3) → baris `memories` → penyelaras →
Qdrant (3.5) → `PencariMemori`. Tiap uji memakai koleksi Qdrant sekali pakai.
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

from hvx.modules import events, identity, memory, platform

pytestmark = pytest.mark.integration

PENYEMAT = platform.PenyematHash(b"k" * 32)
# spec/05 — `memory.read` coach-agent.
SCOPE_COACH = ["habits", "goals", "checkins", "mood", "coaching_notes"]
COACH = identity.Subjek("agent", "coach-agent")


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


def _izin(api: ApiUji) -> identity.MesinIzin:
    s = api.app.state.settings
    return identity.MesinIzin(
        api.app.state.engine, api.app.state.redis, s.redis_prefix, s.permission_cache_ttl_s
    )


def _pencari(api: ApiUji, koleksi: tuple[platform.KlienVektor, str]) -> memory.PencariMemori:
    return memory.PencariMemori(api.app.state.engine, _izin(api), koleksi[0], PENYEMAT, koleksi[1])


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


def _sql_pemilik(api: ApiUji, sql: str, *param: object) -> None:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True) as k:
        k.execute(sql, param)


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
    await _izin(api_bersama).tetapkan(uid, COACH, "journal_raw", "read", "allow")
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
    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rahasia"
    )
    assert hasil.items == [], "memori terhapus diserahkan karena titiknya masih ada"

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


# ────────────────────────────────────────────────────────────── 3.7 ──


async def _siapkan_pengguna(
    api: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> tuple[UUID, dict[str, UUID]]:
    """Satu mood dan satu jurnal yang sama-sama menyebut "rapat", sudah tersemat."""
    uid, token = await api.pengguna_baru()
    await _post(api, token, "/v1/moods", {"valence": 2, "note": "capek sesudah rapat"})
    await _post(api, token, "/v1/journal", {"body": "rapat itu membuatku ingin berhenti"})
    await _ekstrak_semua(api, _awalan())
    await _penyelaras(api, koleksi).putaran()
    return uid, {m["scope"]: m["id"] for m in _memori_milik(api, uid)}


async def test_agent_berizin_menemukan_memorinya_secara_semantik(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert [h.memori.id for h in hasil.items] == [ids["mood"]]
    assert hasil.items[0].skor > 0
    assert hasil.scope_dipakai == sorted(SCOPE_COACH)
    assert hasil.perlu_izin == []


async def test_agent_tanpa_izin_scope_tidak_menerima_barisnya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """spec/07 3.7 Selesai bila — tiga jalan "tanpa izin", satu bukti bahwa izinlah pembedanya."""
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    cari = _pencari(api_bersama, koleksi)
    izin = _izin(api_bersama)

    # 1 · scope sensitif di manifest, tanpa `allow` yang disimpan pengguna
    tanpa = await cari.cari(
        user_id=uid, agent="uji-agent", scope_manifest=["mood", "journal_raw"], kueri="rapat"
    )
    assert ids["journal_raw"] not in [h.memori.id for h in tanpa.items], (
        "journal_raw terbuka tanpa izin"
    )
    assert tanpa.perlu_izin == ["journal_raw"]

    # 2 · pengguna MENOLAK scope yang ada di manifest coach
    await izin.tetapkan(uid, COACH, "mood", "read", "deny")
    ditolak = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )
    assert ditolak.items == [], "scope yang ditolak pengguna tetap diserahkan"
    assert "mood" not in ditolak.scope_dipakai

    # 3 · scope yang tidak diminta manifest — izin pengguna tidak melebarkan manifest
    await izin.tetapkan(uid, COACH, "journal_raw", "read", "allow")
    di_luar = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )
    assert di_luar.items == [], "izin pengguna melebarkan manifest"

    # bukti: dengan manifest DAN izin, baris yang sama diserahkan
    diizinkan = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["journal_raw"], kueri="rapat"
    )
    assert [h.memori.id for h in diizinkan.items] == [ids["journal_raw"]]


async def test_payload_qdrant_basi_tidak_meloloskan_scope(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    """Qdrant tidak punya RLS dan payload-nya bisa basi — barisnya yang memutuskan."""
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    _sql_pemilik(
        api_bersama, "UPDATE memories SET scope = 'journal_raw' WHERE id = %s", ids["mood"]
    )

    hasil = await _pencari(api_bersama, koleksi).cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert hasil.items == [], "scope di payload Qdrant menang atas scope di baris"


async def test_pencarian_hanya_memori_pemiliknya(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    a, ids_a = await _siapkan_pengguna(api_bersama, koleksi)
    b, ids_b = await _siapkan_pengguna(api_bersama, koleksi)

    hasil_b = await _pencari(api_bersama, koleksi).cari(
        user_id=b, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="capek rapat"
    )

    assert [h.memori.id for h in hasil_b.items] == [ids_b["mood"]], "memori pengguna lain ikut"
    assert ids_a["mood"] not in [h.memori.id for h in hasil_b.items]
    assert a != b


class _QdrantTakBolehDitanya:
    async def cari(self, *_a: object, **_k: object) -> list[platform.HasilCari]:
        raise AssertionError("Qdrant ditanya padahal jawabannya sudah pasti kosong")


class _QdrantSkorNol:
    """Kandidat yang tidak mirip sama sekali — kosinus 0."""

    def __init__(self, ids: list[UUID]) -> None:
        self._ids = ids

    async def cari(self, *_a: object, **_k: object) -> list[platform.HasilCari]:
        return [platform.HasilCari(i, 0.0, {}) for i in self._ids]


async def test_kueri_tanpa_kata_tidak_menanyai_qdrant(api_bersama: ApiUji) -> None:
    """Vektor nol "berjarak" 0 ke SEMUA titik, dan Qdrant mengembalikan semuanya."""
    uid, _token = await api_bersama.pengguna_baru()
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=["mood"], kueri="... ?!"
    )

    assert hasil.items == []
    assert hasil.scope_dipakai == ["mood"]


async def test_kandidat_berskor_nol_bukan_kecocokan(
    api_bersama: ApiUji, koleksi: tuple[platform.KlienVektor, str]
) -> None:
    uid, ids = await _siapkan_pengguna(api_bersama, koleksi)
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantSkorNol([ids["mood"]]),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="coach-agent", scope_manifest=SCOPE_COACH, kueri="rapat"
    )

    assert hasil.items == [], "kandidat berskor 0 diserahkan sebagai kecocokan"


async def test_tanpa_scope_diizinkan_qdrant_tidak_ditanya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    hasil = await cari.cari(
        user_id=uid, agent="uji-agent", scope_manifest=["journal_raw"], kueri="apa saja"
    )

    assert hasil.items == []
    assert hasil.perlu_izin == ["journal_raw"]


@pytest.mark.parametrize(
    ("manifest", "kueri", "batas", "pesan"),
    [
        (["habit"], "rapat", 5, "daftar resmi"),  # salah ketik — bukan scope resmi
        (["mood"], "   ", 5, "kosong"),
        (["mood"], "rapat", 0, "batas"),
        (["mood"], "rapat", memory.MAKS_HASIL + 1, "batas"),
    ],
)
async def test_permintaan_yang_salah_bentuk_ditolak(
    api_bersama: ApiUji, manifest: list[str], kueri: str, batas: int, pesan: str
) -> None:
    cari = memory.PencariMemori(
        api_bersama.app.state.engine,
        _izin(api_bersama),
        _QdrantTakBolehDitanya(),  # type: ignore[arg-type]
        PENYEMAT,
        "tidak-dipakai",
    )

    with pytest.raises(ValueError, match=pesan):
        await cari.cari(
            user_id=uuid.uuid4(),
            agent="coach-agent",
            scope_manifest=manifest,
            kueri=kueri,
            batas=batas,
        )
