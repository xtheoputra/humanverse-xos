"""spec/07 4.1 — *“catat mood” tidak memanggil model besar*: jalurnya sampai ke basis data.

`kenali` memutuskan rutenya (`tests/unit/test_niat.py`); di sini jalur
`deterministic` dijalankan terhadap PostgreSQL sungguhan. Mood tercatat lewat
layanan `checkins` yang sama dengan `POST /moods` — beserta event-nya — dan
jalurnya tidak memegang gerbang model sama sekali. Buktinya lewat percakapan,
dengan gerbang model yang dihitung panggilannya: 4.8.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import psycopg
import pytest
from _bantuan_db import ApiUji, psycopg_dsn

from hvx.modules import agents

pytestmark = pytest.mark.integration


def _milik(api: ApiUji, uid: UUID) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]]]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        mood = k.execute(
            "SELECT valence, label, note FROM mood_entries WHERE user_id = %s", (uid,)
        ).fetchall()
        ev = k.execute("SELECT event_type FROM events WHERE user_id = %s", (uid,)).fetchall()
    return mood, ev


async def test_catat_mood_lewat_kalimat_menulis_mood_dan_eventnya(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    niat = agents.kenali("catat mood 2 cemas, rapat seharian")
    assert niat.rute == "deterministic"

    hasil = await agents.jalankan_deterministik(api_bersama.app.state.engine, uid, niat)

    assert hasil.teks == "Mood 2/5 (cemas) dicatat."
    assert _milik(api_bersama, uid) == ([(2, "cemas", "rapat seharian")], [("mood.logged",)])


async def test_pesan_yang_dikirim_ulang_tidak_mencatat_mood_dua_kali(api_bersama: ApiUji) -> None:
    uid, _token = await api_bersama.pengguna_baru()
    niat = agents.kenali("catat mood 4")
    mood_id = uuid4()
    engine = api_bersama.app.state.engine

    pertama = await agents.jalankan_deterministik(engine, uid, niat, mood_id=mood_id)
    kedua = await agents.jalankan_deterministik(engine, uid, niat, mood_id=mood_id)

    assert (pertama.teks, kedua.teks) == ("Mood 4/5 dicatat.", "Mood 4/5 sudah dicatat."), (
        "kiriman ulang mencatat mood dua kali"
    )
    assert pertama.mood_id == kedua.mood_id == mood_id
    assert _milik(api_bersama, uid) == ([(4, None, None)], [("mood.logged",)])


@pytest.mark.parametrize("teks", ["catat mood 7", "catat mood 3 " + "x" * 4_001])
async def test_perintah_yang_tidak_utuh_dijawab_tanpa_menulis_apa_pun(
    api_bersama: ApiUji, teks: str
) -> None:
    uid, _token = await api_bersama.pengguna_baru()

    hasil = await agents.jalankan_deterministik(
        api_bersama.app.state.engine, uid, agents.kenali(teks)
    )

    assert hasil.teks == agents.CARA_MENGISI_MOOD
    assert _milik(api_bersama, uid) == ([], [])
