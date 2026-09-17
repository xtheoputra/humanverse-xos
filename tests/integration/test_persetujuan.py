"""spec/07 1.4 — riwayat persetujuan append-only; pencabutan = baris baru;
`data.purpose ⊆ consent.purpose` ditegakkan (B-22, naskah 12 §8.9–§8.10).

Semuanya dijalankan sebagai PERAN APLIKASI di dalam transaksi pengguna — jalur
yang sama dengan kode produksi, termasuk RLS dan GRANT hanya-tambah.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta

import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules.identity import (
    Persetujuan,
    PersetujuanTidakSah,
    boleh_dipakai_untuk,
    cabut_persetujuan,
    catat_persetujuan,
)
from hvx.modules.platform import buat_engine, transaksi_pengguna

pytestmark = pytest.mark.integration

V = "2026-09-17"


def _latih(granted: bool, *cakupan: str, kedaluwarsa: datetime | None = None) -> Persetujuan:
    return Persetujuan(
        kind="model_training",
        purpose="model_training",
        granted=granted,
        policy_version=V,
        data_scopes=frozenset(cakupan),
        expires_at=kedaluwarsa,
    )


@pytest.fixture
async def v0(
    basis_data_termigrasi: Callable[[str], BasisDataV0],
) -> AsyncIterator[tuple[BasisDataV0, AsyncEngine, uuid.UUID]]:
    db = basis_data_termigrasi("persetujuan")
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
        (uid,) = k.execute(
            "INSERT INTO users (email, password_hash) VALUES ('p@uji.id', 'x') RETURNING id"
        ).fetchone() or (None,)
    assert isinstance(uid, uuid.UUID)
    engine = buat_engine(db.dsn_aplikasi)
    try:
        yield db, engine, uid
    finally:
        await engine.dispose()


async def _boleh(engine: AsyncEngine, uid: uuid.UUID, tujuan: set[str], cakupan: set[str]) -> bool:
    async with transaksi_pengguna(engine, uid) as conn:
        return await boleh_dipakai_untuk(conn, uid, tujuan, cakupan)


async def test_tujuan_dan_cakupan_harus_tercakup_persetujuan_terakhir(
    v0: tuple[BasisDataV0, AsyncEngine, uuid.UUID],
) -> None:
    _db, engine, uid = v0
    async with transaksi_pengguna(engine, uid) as conn:
        await catat_persetujuan(conn, uid, _latih(True, "habits", "checkins"))

    assert await _boleh(engine, uid, {"model_training"}, {"habits"})
    assert await _boleh(engine, uid, {"model_training"}, {"habits", "checkins"})
    # data di luar cakupan: data.purpose ⊆ consent.purpose tidak cukup, data juga harus tercakup
    assert not await _boleh(engine, uid, {"model_training"}, {"habits", "journal"})
    # tujuan tanpa riwayat sama sekali = ditolak, bukan "belum ditanya maka boleh"
    assert not await _boleh(engine, uid, {"model_training", "research"}, {"habits"})
    assert not await _boleh(engine, uid, set(), {"habits"})


async def test_pencabutan_adalah_baris_baru_dan_riwayat_lama_utuh(
    v0: tuple[BasisDataV0, AsyncEngine, uuid.UUID],
) -> None:
    db, engine, uid = v0
    async with transaksi_pengguna(engine, uid) as conn:
        await catat_persetujuan(conn, uid, _latih(True, "habits"))
    assert await _boleh(engine, uid, {"model_training"}, {"habits"})

    async with transaksi_pengguna(engine, uid) as conn:
        await cabut_persetujuan(
            conn, uid, kind="model_training", purpose="model_training", policy_version=V
        )

    assert not await _boleh(engine, uid, {"model_training"}, {"habits"})
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik)) as k:
        riwayat = k.execute(
            "SELECT granted, granted_at IS NOT NULL, revoked_at IS NOT NULL, data_scopes "
            "FROM consents WHERE user_id = %s ORDER BY created_at",
            (uid,),
        ).fetchall()
        aksi = [
            r[0]
            for r in k.execute(
                "SELECT action FROM audit_logs WHERE user_id = %s ORDER BY id", (uid,)
            )
        ]
    assert riwayat == [(True, True, False, ["habits"]), (False, False, True, [])]
    assert aksi == ["consent.granted", "consent.revoked"]


async def test_cabut_lalu_setujui_lagi_dalam_satu_transaksi_berurutan_benar(
    v0: tuple[BasisDataV0, AsyncEngine, uuid.UUID],
) -> None:
    """now() membeku per transaksi; clock_timestamp() tidak — urutan riwayat tetap tentu."""
    _db, engine, uid = v0
    async with transaksi_pengguna(engine, uid) as conn:
        await catat_persetujuan(conn, uid, _latih(True, "habits"))
        await cabut_persetujuan(
            conn, uid, kind="model_training", purpose="model_training", policy_version=V
        )
        await catat_persetujuan(conn, uid, _latih(True, "habits"))

    assert await _boleh(engine, uid, {"model_training"}, {"habits"})


async def test_persetujuan_kedaluwarsa_atau_ditolak_tidak_meloloskan(
    v0: tuple[BasisDataV0, AsyncEngine, uuid.UUID],
) -> None:
    _db, engine, uid = v0
    lalu = datetime.now(UTC) - timedelta(days=1)
    async with transaksi_pengguna(engine, uid) as conn:
        await catat_persetujuan(conn, uid, _latih(True, "habits", kedaluwarsa=lalu))
        await catat_persetujuan(
            conn,
            uid,
            Persetujuan(kind="research", purpose="research", granted=False, policy_version=V),
        )

    assert not await _boleh(engine, uid, {"model_training"}, {"habits"})
    assert not await _boleh(engine, uid, {"research"}, set())


async def test_riwayat_persetujuan_tidak_bisa_diubah_atau_dihapus_aplikasi(
    v0: tuple[BasisDataV0, AsyncEngine, uuid.UUID],
) -> None:
    _db, engine, uid = v0
    async with transaksi_pengguna(engine, uid) as conn:
        await catat_persetujuan(conn, uid, _latih(True, "habits"))

    for perintah in ("UPDATE consents SET granted = false", "DELETE FROM consents"):
        with pytest.raises(DBAPIError) as galat:
            async with transaksi_pengguna(engine, uid) as conn:
                await conn.execute(text(perintah))
        assert getattr(galat.value.orig, "pgcode", None) == "42501", galat.value


@pytest.mark.parametrize(
    ("isian", "pesan"),
    [
        ({"purpose": "Model Training"}, "snake_case"),
        ({"purpose": "latih", "data_scopes": frozenset({"Semua Data"})}, "data_scopes"),
        ({"purpose": "latih", "expires_at": datetime(2027, 1, 1)}, "zona waktu"),
        ({"purpose": "latih", "policy_version": ""}, "wajib diisi"),
    ],
)
def test_bentuk_persetujuan_yang_tidak_sah_ditolak(isian: dict[str, object], pesan: str) -> None:
    dasar: dict[str, object] = {"kind": "k", "granted": True, "policy_version": V}
    with pytest.raises(PersetujuanTidakSah, match=pesan):
        Persetujuan(**(dasar | isian))  # type: ignore[arg-type]
