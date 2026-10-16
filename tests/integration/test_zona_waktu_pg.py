"""Tiap nama zona yang api terima, dikenal PostgreSQL — spec/07 1.3 · 2.4.

`platform.ZonaWaktuIANA` memeriksa nama terhadap `tzdata` Python, tetapi
"hari ini" pengguna dihitung PostgreSQL (`now() AT TIME ZONE :zona`, jam basis
data — spec/07 1.5). Nama yang Python kenal tetapi PostgreSQL tidak — `tzdata`
Python lebih baru dari basis data zona citra `postgres` — lolos validasi lalu
menjadi 500 di tiap permintaan pengguna itu. Uji ini yang memberi tahu saat
kedua daftar berselisih.
"""

from __future__ import annotations

import psycopg
import pytest

from hvx.modules.platform import nama_zona_sah

pytestmark = pytest.mark.integration


def test_tiap_zona_yang_diterima_dikenal_postgresql(dsn_admin_uji: str) -> None:
    with psycopg.connect(dsn_admin_uji) as k:
        pg = {nama for (nama,) in k.execute("SELECT name FROM pg_timezone_names")}

    hilang = sorted(nama_zona_sah() - pg)

    assert len(pg) > 500
    assert not hilang, f"zona diterima api tetapi tidak dikenal PostgreSQL: {hilang}"
