"""spec/08 7.2 — *“proyeksi yang didaftarkan dibangun ulang dari nol dan hasilnya sama”*.

Satu uji untuk SEMUA proyeksi di `intelligence.PROYEKSI` — proyeksi yang didaftarkan kelak
(spec/08 Sprint 8–10) ikut teruji tanpa menulis uji baru. Tiga tuntutan per proyeksi:

1. **aliran = bangun ulang** — penangannya dijalankan atas event pengguna seperti stream
   mengirimnya paling buruk (urutan terbalik, tiap event DUA kali — spec/03 aturan 2), lalu
   `bangun_ulang` dari nol: potret keduanya identik;
2. **tidak buta** — skenario menghasilkan keadaan yang tidak kosong untuk proyeksi itu
   (proyeksi baru yang tidak tersentuh skenario → merah: lengkapi skenarionya);
3. **benar-benar dari nol** — sesudah `events` pengguna dibuang, bangun ulang meninggalkan
   proyeksi KOSONG: tidak ada baris basi yang selamat dari pengosongan.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_habits import buat_habit
from test_penyelesaian import _catat

from hvx.modules import events, intelligence
from hvx.modules.platform import transaksi_pengguna

pytestmark = pytest.mark.integration


async def _skenario(api: ApiUji, token: str) -> None:
    """Perilaku seorang pengguna lewat API — tiap jenis event V0 yang diproyeksikan, plus
    kasus yang pernah salah: penyelesaian dicabut, check-in yang diganti tanpa metrik (K1)."""
    h = await buat_habit(api, token, title="Lari pagi")
    for tanggal, status in (("2026-09-01", "done"), ("2026-09-02", "partial")):
        r = await _catat(api, token, h["id"], for_date=tanggal, status=status)
        assert r.status_code == 201, r.text
    r = await _catat(api, token, h["id"], for_date="2026-09-03", status="skipped")
    assert r.status_code == 201, r.text
    r = await _catat(api, token, h["id"], for_date="2026-09-04")
    assert r.status_code == 201, r.text
    r = await api.klien.delete(f"/v1/habits/{h['id']}/completions/2026-09-04", headers=auth(token))
    assert r.status_code == 204, r.text

    for tanggal, isi in (
        ("2026-09-01", {"energy": 2, "focus": 3}),
        ("2026-09-01", {"energy": 4, "focus": 3}),  # diganti — energi terakhir yang benar
        ("2026-09-02", {"energy": 5}),
        ("2026-09-02", {"sleep_hours": 7.5}),  # diganti TANPA metrik → tanpa human state
        ("2026-09-03", {"focus": 1}),
    ):
        r = await api.klien.put(f"/v1/checkins/{tanggal}", json=isi, headers=auth(token))
        assert r.status_code in (200, 201), r.text


async def _potret(api: ApiUji, uid: UUID, nama: str) -> Any:
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        return await intelligence.PROYEKSI[nama].potret(conn, uid)


async def _alirkan_terburuk(api: ApiUji, uid: UUID, nama: str) -> None:
    """Penangan konsumen atas event pengguna: urutan terbalik, tiap event dua kali."""
    proyeksi = intelligence.PROYEKSI[nama]
    async with transaksi_pengguna(api.app.state.engine, uid) as conn:
        riwayat = [
            e for e in await events.untuk_proyeksi(conn, uid) if e.event_type in proyeksi.jenis
        ]
    for event in reversed(riwayat * 2):
        async with transaksi_pengguna(api.app.state.engine, uid) as conn:
            await proyeksi.tangani(conn, event)


def test_ada_proyeksi_terdaftar() -> None:
    assert intelligence.PROYEKSI, "tak satu proyeksi pun terdaftar — uji di bawah buta"


@pytest.mark.parametrize("nama", sorted(intelligence.PROYEKSI))
async def test_proyeksi_terdaftar_dibangun_ulang_dari_nol_dan_hasilnya_sama(
    api_bersama: ApiUji, nama: str
) -> None:
    uid, token = await api_bersama.pengguna_baru()
    await _skenario(api_bersama, token)
    engine = api_bersama.app.state.engine

    await _alirkan_terburuk(api_bersama, uid, nama)
    dialirkan = await _potret(api_bersama, uid, nama)
    assert dialirkan, f"skenario tidak menghasilkan apa pun untuk proyeksi {nama!r} — lengkapi"

    diputar = await intelligence.bangun_ulang(engine, uid, nama)
    assert diputar > 0
    assert await _potret(api_bersama, uid, nama) == dialirkan, (
        f"proyeksi {nama!r}: bangun ulang dari nol ≠ aliran"
    )

    # Tanpa events, "dari nol" berarti KOSONG — pengosongannya tidak menyisakan baris basi.
    with psycopg.connect(psycopg_dsn(api_bersama.db.dsn_pemilik), autocommit=True) as k:
        k.execute("DELETE FROM events WHERE user_id = %s", (uid,))
    assert await intelligence.bangun_ulang(engine, uid, nama) == 0
    sisa = await _potret(api_bersama, uid, nama)
    assert not sisa, f"proyeksi {nama!r}: baris basi selamat dari pengosongan: {sisa}"
