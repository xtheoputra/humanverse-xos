"""spec/07 3.1 — modul `events` + amplop + idempotensi: *“event ganda ditelan sebagai sukses”*.

Diterbitkan sebagai peran APLIKASI di dalam `platform.transaksi_pengguna` (RLS),
dan BARIS-nya dihitung di basis data sebagai pemilik skema.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from psycopg import errors
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import events
from hvx.modules.platform import buat_engine, transaksi_pengguna

pytestmark = pytest.mark.integration

# Sudah lewat menurut jam basis data juga — jam VM Docker bisa tertinggal dari jam hos.
SEKARANG = datetime.now(UTC) - timedelta(minutes=10)


@pytest.fixture(scope="module")
async def engine(v0_bersama: BasisDataV0) -> AsyncIterator[AsyncEngine]:
    e = buat_engine(v0_bersama.dsn_aplikasi)
    yield e
    await e.dispose()


def _pengguna(db: BasisDataV0) -> UUID:
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
        baris = k.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
            (f"{uuid4().hex}@uji.id",),
        ).fetchone()
    assert baris is not None
    uid: UUID = baris[0]
    return uid


def _baris(db: BasisDataV0, user_id: UUID) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT event_type, idempotency_key, source, payload, recorded_at >= occurred_at "
            "FROM events WHERE user_id = %s ORDER BY recorded_at",
            (user_id,),
        ).fetchall()


async def _terbit(engine: AsyncEngine, user_id: UUID, **isi: Any) -> events.HasilTerbit:
    isi.setdefault("event_type", "mood.logged")
    isi.setdefault("occurred_at", SEKARANG)
    isi.setdefault("idempotency_key", f"mood:{uuid4()}")
    isi.setdefault("payload", {"valence": 3})
    async with transaksi_pengguna(engine, user_id) as conn:
        return await events.terbitkan(conn, user_id=user_id, **isi)


async def test_event_terbit_dengan_amplop_spec03(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    uid = _pengguna(v0_bersama)

    hasil = await _terbit(
        engine, uid, idempotency_key="mood:satu", payload={"valence": 2, "label": "cemas"}
    )

    assert hasil.baru is True
    assert _baris(v0_bersama, uid) == [
        ("mood.logged", "mood:satu", "app", {"valence": 2, "label": "cemas"}, True)
    ]


async def test_event_ganda_ditelan_sebagai_sukses(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    uid = _pengguna(v0_bersama)

    pertama = await _terbit(engine, uid, idempotency_key="mood:ganda")
    kedua = await _terbit(engine, uid, idempotency_key="mood:ganda")

    assert (pertama.baru, kedua.baru) == (True, False)
    assert kedua.id == pertama.id
    assert len(_baris(v0_bersama, uid)) == 1, "event ganda menulis baris kedua"


async def test_event_ganda_serentak_satu_baris_tanpa_galat(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    uid = _pengguna(v0_bersama)

    hasil = await asyncio.gather(
        *(_terbit(engine, uid, idempotency_key="mood:serentak") for _ in range(6))
    )

    assert sorted(h.baru for h in hasil) == [False] * 5 + [True]
    assert len({h.id for h in hasil}) == 1
    assert len(_baris(v0_bersama, uid)) == 1


async def test_kunci_sama_milik_dua_pengguna_dua_event(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    a, b = _pengguna(v0_bersama), _pengguna(v0_bersama)

    ha = await _terbit(engine, a, idempotency_key="mood:bersama")
    hb = await _terbit(engine, b, idempotency_key="mood:bersama")

    assert ha.baru is hb.baru is True
    assert ha.id != hb.id


async def test_kunci_sama_untuk_kejadian_lain_ditolak_keras(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    uid = _pengguna(v0_bersama)
    await _terbit(engine, uid, idempotency_key="mood:tabrak", payload={"valence": 3})

    with pytest.raises(events.EventTidakSah, match="kejadian yang berbeda"):
        await _terbit(engine, uid, idempotency_key="mood:tabrak", payload={"valence": 1})

    assert len(_baris(v0_bersama, uid)) == 1


@pytest.mark.parametrize(
    "lain",
    [
        {"subject_id": UUID("00000000-0000-4000-8000-000000000002")},
        {"event_type": "habit.completion_retracted"},  # payload yang SAMA sah bagi keduanya
    ],
)
async def test_kunci_sama_untuk_subjek_atau_jenis_lain_ditolak_keras(
    engine: AsyncEngine, v0_bersama: BasisDataV0, lain: dict[str, Any]
) -> None:
    """Payload yang sama tidak cukup untuk menelan: subjek lain, atau jenis lain (dilewati
    lalu DICABUT), adalah kejadian lain — tinjauan penegak buta Sprint 3."""
    uid = _pengguna(v0_bersama)
    cid = uuid4()
    isi: dict[str, Any] = {
        "event_type": "habit.skipped",
        "idempotency_key": f"habit-completion:{cid}",
        "payload": {"for_date": date(2026, 9, 10), "completion_id": cid},
        "subject_type": "habit",
        "subject_id": UUID("00000000-0000-4000-8000-000000000001"),
    }
    await _terbit(engine, uid, **isi)

    with pytest.raises(events.EventTidakSah, match="kejadian yang berbeda"):
        await _terbit(engine, uid, **{**isi, **lain})

    assert len(_baris(v0_bersama, uid)) == 1


async def test_recorded_at_saat_event_masuk_bukan_awal_transaksinya(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    """`now()` membeku di awal transaksi: event yang disisip di ujung transaksi panjang
    tercatat LEBIH AWAL dari event transaksi lain yang sudah commit — dan relay yang
    membaca menurut `recorded_at` melompatinya (events/repository.py)."""
    uid = _pengguna(v0_bersama)

    async with transaksi_pengguna(engine, uid) as conn:
        awal = (await conn.execute(text("SELECT now()"))).scalar_one()
        await asyncio.sleep(0.5)  # transaksi yang sibuk sebelum menerbitkan
        await events.terbitkan(
            conn,
            user_id=uid,
            event_type="mood.logged",
            occurred_at=SEKARANG,
            idempotency_key="mood:ujung-transaksi",
            payload={"valence": 3},
        )

    with psycopg.connect(psycopg_dsn(v0_bersama.dsn_pemilik)) as k:
        (masuk,) = k.execute(
            "SELECT recorded_at FROM events WHERE user_id = %s", (uid,)
        ).fetchone() or (None,)
    assert masuk is not None
    assert masuk - awal >= timedelta(seconds=0.4), (
        f"recorded_at = awal transaksi, bukan saat event masuk ({masuk - awal})"
    )


@pytest.mark.parametrize(
    "isi",
    [
        {"event_type": "habit.deleted", "payload": {}},
        {"payload": {"valence": 3, "catatan": "x"}},
        {"source": "sensor"},  # arch/11 E-3 — uji admisi saat terbit
        {"occurred_at": datetime(2026, 9, 24, 6, 30)},
        {"idempotency_key": "tanpa-jenis"},
        {"subject_type": "Habit"},
    ],
)
async def test_uji_admisi_menolak_sebelum_menyentuh_basis_data(
    engine: AsyncEngine, v0_bersama: BasisDataV0, isi: dict[str, Any]
) -> None:
    uid = _pengguna(v0_bersama)

    with pytest.raises(events.EventTidakSah):
        await _terbit(engine, uid, **isi)

    assert _baris(v0_bersama, uid) == []


def test_basis_data_sendiri_menolak_sumber_sensor(v0_bersama: BasisDataV0) -> None:
    """E-3 separuh DDL — CHECK `events.source` menolak `sensor` juga bagi pemilik skema."""
    uid = _pengguna(v0_bersama)
    with (
        psycopg.connect(psycopg_dsn(v0_bersama.dsn_pemilik), autocommit=True) as k,
        pytest.raises(errors.CheckViolation),
    ):
        k.execute(
            "INSERT INTO events (user_id, event_type, occurred_at, source, idempotency_key) "
            "VALUES (%s, 'mood.logged', now(), 'sensor', 'mood:x')",
            (uid,),
        )


async def test_pengguna_yang_dilayani_tidak_bisa_menerbitkan_atas_nama_orang_lain(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    """RLS WITH CHECK — transaksi A tidak bisa menulis event milik B."""
    a, b = _pengguna(v0_bersama), _pengguna(v0_bersama)

    with pytest.raises(DBAPIError):
        async with transaksi_pengguna(engine, a) as conn:
            await events.terbitkan(
                conn,
                user_id=b,
                event_type="mood.logged",
                occurred_at=SEKARANG,
                idempotency_key="mood:menyamar",
                payload={"valence": 3},
            )

    assert _baris(v0_bersama, b) == []


async def test_event_ikut_batal_bersama_tulisan_yang_batal(
    engine: AsyncEngine, v0_bersama: BasisDataV0
) -> None:
    """Kotak keluar di transaksi pemanggil: tulisan yang batal tidak meninggalkan event."""
    uid = _pengguna(v0_bersama)

    async def tulisan_yang_gagal() -> None:
        async with transaksi_pengguna(engine, uid) as conn:
            await events.terbitkan(
                conn,
                user_id=uid,
                event_type="mood.logged",
                occurred_at=SEKARANG - timedelta(minutes=1),
                idempotency_key="mood:batal",
                payload={"valence": 3},
            )
            raise RuntimeError("tulisan domain gagal")

    with pytest.raises(RuntimeError, match="tulisan domain gagal"):
        await tulisan_yang_gagal()

    assert _baris(v0_bersama, uid) == [], "event terbit untuk tulisan yang batal"
