"""spec/07 1.5 — mesin izin: default `ask`; di-cache di Redis; allow/deny/ask/expired.

PostgreSQL dan Redis sungguhan, sebagai PERAN APLIKASI di dalam transaksi
pengguna — RLS berlaku. Tiap uji memakai pengguna baru dan awalan Redis acak.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules.identity import Keputusan, MesinIzin, Subjek
from hvx.modules.identity import izin as identity_izin
from hvx.modules.platform import buat_engine, buat_redis

pytestmark = pytest.mark.integration

COACH = Subjek("agent", "coach-agent")


@dataclass
class Izin:
    db: BasisDataV0
    engine: AsyncEngine
    redis: Redis
    awalan: str
    mesin: MesinIzin

    def pemilik(self) -> psycopg.Connection[Any]:
        return psycopg.connect(psycopg_dsn(self.db.dsn_pemilik), autocommit=True)

    def pengguna_baru(self) -> uuid.UUID:
        with self.pemilik() as k:
            (uid,) = k.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
                (f"{uuid.uuid4().hex}@uji.id",),
            ).fetchone() or (None,)
        assert isinstance(uid, uuid.UUID)
        return uid

    def jam_basis_data(self) -> datetime:
        """Kedaluwarsa diukur jam basis data — jam Docker Desktop bisa bergeser dari hos."""
        with self.pemilik() as k:
            (sekarang,) = k.execute("SELECT clock_timestamp()").fetchone() or (None,)
        assert isinstance(sekarang, datetime)
        return sekarang


@pytest.fixture
async def izin(v0_bersama: BasisDataV0, url_redis_uji: str) -> AsyncIterator[Izin]:
    engine = buat_engine(v0_bersama.dsn_aplikasi)
    redis = buat_redis(url_redis_uji, socket_timeout_s=5, connect_timeout_s=2)
    awalan = f"uji-{uuid.uuid4().hex[:12]}"
    try:
        yield Izin(v0_bersama, engine, redis, awalan, MesinIzin(engine, redis, awalan, 300))
    finally:
        async for kunci in redis.scan_iter(match=f"{awalan}:*"):
            await redis.delete(kunci)
        await redis.aclose()
        await engine.dispose()


async def test_tanpa_keputusan_tersimpan_jawabannya_ask(izin: Izin) -> None:
    uid = izin.pengguna_baru()

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "ask"


async def test_bawaan_pemanggil_hanya_untuk_yang_tanpa_keputusan_tersimpan(izin: Izin) -> None:
    """E-167: gerbang risiko spec/05 — risk 0·1 bawaannya `allow`, 2·3 `ask`.

    Mesin izin versi pertama menjawab `ask` untuk tanpa baris DAN untuk `ask` yang
    disetel pengguna: gerbang tidak bisa menerapkan bawaan risiko tanpa menimpa
    pilihan *“tanya aku”* (tinjauan Sprint 1).
    """
    uid = izin.pengguna_baru()

    assert await izin.mesin.cek(uid, COACH, "habits", "read", bawaan="allow") == "allow"
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "ask", (
        "bawaan satu pemanggil tercache untuk pemanggil lain"
    )

    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "ask")
    assert await izin.mesin.cek(uid, COACH, "habits", "read", bawaan="allow") == "ask", (
        "bawaan pemanggil menimpa pilihan eksplisit pengguna"
    )

    lewat = izin.jam_basis_data() - timedelta(seconds=1)
    await izin.mesin.tetapkan(uid, COACH, "mood", "read", "deny", expires_at=lewat)
    assert await izin.mesin.cek(uid, COACH, "mood", "read", bawaan="allow") == "allow"


async def test_perubahan_izin_tidak_tersimpan_tanpa_jejak_audit(
    izin: Izin, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tugas 1.6: jejak di transaksi yang SAMA — perubahan tanpa jejak tidak boleh ada.

    🔴 Tinjauan Sprint 1: tidak ada uji yang menggagalkan audit. Izin yang
    di-commit lebih dulu lalu dicatat di transaksi kedua lulus semua uji.
    """
    uid = izin.pengguna_baru()

    async def audit_gagal(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("audit gagal ditulis")

    monkeypatch.setattr(identity_izin, "audit", audit_gagal)
    with pytest.raises(RuntimeError, match="audit gagal ditulis"):
        await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")

    with izin.pemilik() as k:
        (jumlah,) = k.execute(
            "SELECT count(*) FROM permissions WHERE user_id = %s", (uid,)
        ).fetchone() or (0,)
    assert jumlah == 0, "izin tersimpan tanpa jejak audit"


async def test_allow_dan_deny_berlaku_tepat_untuk_subjek_scope_dan_aksinya(izin: Izin) -> None:
    uid = izin.pengguna_baru()
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")
    await izin.mesin.tetapkan(uid, COACH, "journal_raw", "read", "deny")

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"
    assert await izin.mesin.cek(uid, COACH, "journal_raw", "read") == "deny"
    # tidak merembes ke aksi, scope, atau subjek lain
    assert await izin.mesin.cek(uid, COACH, "habits", "write") == "ask"
    assert await izin.mesin.cek(uid, COACH, "goals", "read") == "ask"
    assert await izin.mesin.cek(uid, Subjek("tool", "habit.streak"), "habits", "read") == "ask"


async def test_izin_kedaluwarsa_kembali_ke_ask(izin: Izin) -> None:
    uid = izin.pengguna_baru()
    lewat = izin.jam_basis_data() - timedelta(seconds=1)
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow", expires_at=lewat)
    await izin.mesin.tetapkan(uid, COACH, "mood", "read", "deny", expires_at=lewat)

    # "izinkan sekali" yang habis bukan izin permanen; larangan sementara pun begitu
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "ask"
    assert await izin.mesin.cek(uid, COACH, "mood", "read") == "ask"


async def test_cache_izin_sementara_tidak_hidup_lebih_lama_dari_izinnya(izin: Izin) -> None:
    """Umur cache = sisa umur izin saat dibaca − 1 dtk.

    🔴 Versi pertama memberi cache tepat sisa umur izin saat basis data dibaca —
    lalu menulisnya ke Redis sesudah commit dan satu perjalanan pulang-pergi,
    jadi cache hidup beberapa milidetik MELEWATI izinnya (tinjauan Sprint 1).
    """
    uid = izin.pengguna_baru()
    sampai = izin.jam_basis_data() + timedelta(seconds=3)
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow", expires_at=sampai)

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"
    pola = f"{izin.awalan}:izin:{uid}:*:agent:coach-agent:habits:read"
    umur = [await izin.redis.pttl(k) async for k in izin.redis.scan_iter(match=pola)]
    assert umur, "keputusan tidak di-cache"
    assert all(0 < u <= 2_000 for u in umur), f"cache hidup lebih lama dari izinnya: {umur} ms"

    # Menunggu menurut jam BASIS DATA, bukan tidur 3,3 dtk jam hos: di bawah beban,
    # jam VM Docker Desktop tertinggal dan izinnya belum kedaluwarsa di sana — uji
    # ini sempat merah sekali di gerbang penuh karena itu.
    batas_tunggu = asyncio.get_running_loop().time() + 30
    while izin.jam_basis_data() <= sampai:
        assert asyncio.get_running_loop().time() < batas_tunggu, "jam basis data tidak bergerak"
        await asyncio.sleep(0.1)
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "ask"


async def test_hasil_di_cache_di_redis(izin: Izin) -> None:
    uid = izin.pengguna_baru()
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"

    # Diubah di LUAR mesin izin — bukan jalur aplikasi. Yang menjawab cache.
    with izin.pemilik() as k:
        k.execute("UPDATE permissions SET decision = 'deny' WHERE user_id = %s", (uid,))

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"


async def test_pencabutan_berlaku_seketika_bukan_setelah_cache_habis(izin: Izin) -> None:
    uid = izin.pengguna_baru()
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"

    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "deny")
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "deny"

    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "ask")
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "ask"


async def test_pembaca_di_tengah_pencabutan_tidak_menghidupkan_kembali_izin(
    izin: Izin, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Permintaan lain membaca basis data SEBELUM commit dan menulis cache SESUDAHNYA."""
    uid = izin.pengguna_baru()
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")

    ganti_asli = MesinIzin._ganti_generasi
    baca_asli = MesinIzin._baca_basis_data
    sudah_membaca = asyncio.Event()
    lanjutkan = asyncio.Event()
    pembaca: list[asyncio.Task[Keputusan]] = []

    async def baca_lalu_tertahan(self: MesinIzin, *args: Any) -> Any:
        hasil = await baca_asli(self, *args)
        sudah_membaca.set()
        await lanjutkan.wait()  # nilai LAMA sudah di tangan, cache belum ditulis
        return hasil

    async def ganti_lalu_ada_pembaca(self: MesinIzin, user_id: uuid.UUID) -> None:
        await ganti_asli(self, user_id)
        if not pembaca:
            monkeypatch.setattr(MesinIzin, "_baca_basis_data", baca_lalu_tertahan)
            pembaca.append(asyncio.create_task(self.cek(user_id, COACH, "habits", "read")))
            await sudah_membaca.wait()
            monkeypatch.setattr(MesinIzin, "_baca_basis_data", baca_asli)

    monkeypatch.setattr(MesinIzin, "_ganti_generasi", ganti_lalu_ada_pembaca)
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "deny")
    lanjutkan.set()
    # dimulai sebelum commit — jawaban lama untuk permintaan itu wajar
    assert await pembaca[0] == "allow"
    monkeypatch.setattr(MesinIzin, "_ganti_generasi", ganti_asli)

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "deny", (
        "pembaca lambat menghidupkan kembali izin yang dicabut"
    )


async def test_redis_putus_sesudah_commit_tidak_meninggalkan_izin_lama(
    izin: Izin, monkeypatch: pytest.MonkeyPatch
) -> None:
    uid = izin.pengguna_baru()
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow")
    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "allow"
    ganti_asli = MesinIzin._ganti_generasi

    async def putus_sesudah_commit(self: MesinIzin, user_id: uuid.UUID) -> None:
        with izin.pemilik() as k:
            (keputusan,) = k.execute(
                "SELECT decision FROM permissions WHERE user_id = %s", (user_id,)
            ).fetchone() or (None,)
        if keputusan == "deny":
            raise ConnectionError("Redis putus sesudah commit")
        await ganti_asli(self, user_id)

    monkeypatch.setattr(MesinIzin, "_ganti_generasi", putus_sesudah_commit)
    with pytest.raises(ConnectionError):
        await izin.mesin.tetapkan(uid, COACH, "habits", "read", "deny")
    monkeypatch.setattr(MesinIzin, "_ganti_generasi", ganti_asli)

    assert await izin.mesin.cek(uid, COACH, "habits", "read") == "deny", (
        "izin yang dicabut masih dijawab cache lama"
    )


async def test_izin_satu_pengguna_tidak_berlaku_bagi_pengguna_lain(izin: Izin) -> None:
    a, b = izin.pengguna_baru(), izin.pengguna_baru()
    await izin.mesin.tetapkan(a, COACH, "habits", "read", "allow")
    assert await izin.mesin.cek(a, COACH, "habits", "read") == "allow"

    assert await izin.mesin.cek(b, COACH, "habits", "read") == "ask"
    await izin.mesin.tetapkan(b, COACH, "habits", "read", "deny")

    assert await izin.mesin.cek(a, COACH, "habits", "read") == "allow"
    assert await izin.mesin.cek(b, COACH, "habits", "read") == "deny"
    with izin.pemilik() as k:
        baris = k.execute(
            "SELECT user_id, decision FROM permissions WHERE user_id = ANY(%s)", ([a, b],)
        ).fetchall()
    assert sorted(baris) == sorted([(a, "allow"), (b, "deny")])


async def test_tiap_perubahan_izin_tercatat_di_audit(izin: Izin) -> None:
    uid = izin.pengguna_baru()
    sejam = izin.jam_basis_data() + timedelta(hours=1)

    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "allow", expires_at=sejam)
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "deny")
    await izin.mesin.tetapkan(uid, COACH, "habits", "read", "ask")

    with izin.pemilik() as k:
        baris = k.execute(
            "SELECT action, actor_type, actor_id, subject_type, subject_id, metadata "
            "FROM audit_logs WHERE user_id = %s ORDER BY id",
            (uid,),
        ).fetchall()
    sifat = ("user", str(uid), "agent", "coach-agent")
    assert baris == [
        ("permission.granted", *sifat, {"scope": "habits", "action": "read", "sementara": True}),
        ("permission.denied", *sifat, {"scope": "habits", "action": "read", "sementara": False}),
        ("permission.reset", *sifat, {"scope": "habits", "action": "read", "sementara": False}),
    ]
