"""spec/07 4.2 · K-29 — katalog `agents` DIKELOLA MIGRASI; api menolak mulai bila berbeda.

spec/01 §10: `hvx_app` hanya `SELECT` atas `agents`/`agent_tools` — api tidak bisa
mendaftarkan agent. Manifest yang disunting tanpa migrasinya tidak boleh berjalan
diam-diam dengan pagu risiko dan tool yang lama, jadi api membandingkan katalog
basis data dengan manifest yang divalidasinya saat mulai.
"""

from __future__ import annotations

from collections.abc import Callable

import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from asgi_lifespan import LifespanManager
from psycopg import errors

from hvx.main import create_app
from hvx.modules import agents
from hvx.modules.platform import Settings, buat_engine

pytestmark = pytest.mark.integration


async def test_katalog_migrasi_sama_dengan_manifest(v0_bersama: BasisDataV0) -> None:
    registri = agents.muat_registri()
    engine = buat_engine(v0_bersama.dsn_aplikasi)
    try:
        await agents.pastikan_katalog(engine, registri)  # tidak melempar
    finally:
        await engine.dispose()

    with psycopg.connect(psycopg_dsn(v0_bersama.dsn_pemilik)) as k:
        baris = k.execute(
            """
            SELECT a.name, a.max_risk, array_agg(t.tool_name ORDER BY t.tool_name)
            FROM agents a JOIN agent_tools t ON t.agent_id = a.id
            WHERE a.status = 'active' GROUP BY a.name, a.max_risk ORDER BY a.name
            """
        ).fetchall()
    assert baris == [
        (m.name, m.pagu_risiko, sorted(m.tools)) for _n, m in sorted(registri.agent.items())
    ]


@pytest.mark.parametrize(
    "rusak",
    [
        "UPDATE agents SET max_risk = 4 WHERE name = 'coach-agent'",
        "DELETE FROM agent_tools WHERE tool_name = 'habit.complete'",
        "UPDATE agents SET manifest = jsonb_set(manifest, '{max_risk}', '\"R4\"') "
        "WHERE name = 'habit-agent'",
        "UPDATE agents SET status = 'disabled' WHERE name = 'memory-agent'",
    ],
)
async def test_api_menolak_mulai_bila_katalog_berbeda_dari_manifest(
    basis_data_termigrasi: Callable[[str], BasisDataV0], url_redis_uji: str, rusak: str
) -> None:
    db = basis_data_termigrasi("katalog")
    with psycopg.connect(psycopg_dsn(db.dsn_pemilik), autocommit=True) as k:
        k.execute(rusak)
    app = create_app(Settings(database_url=db.dsn_aplikasi, redis_url=url_redis_uji, env="test"))

    with pytest.raises(agents.KatalogBerbeda, match="K-29"):
        async with LifespanManager(app):
            pass


def test_peran_aplikasi_tidak_bisa_mengubah_katalog(v0_bersama: BasisDataV0) -> None:
    """Katalog sistem hanya-baca bagi api (spec/01 §10) — agent tidak mendaftarkan dirinya."""
    with (
        psycopg.connect(psycopg_dsn(v0_bersama.dsn_aplikasi), autocommit=True) as k,
        pytest.raises(errors.InsufficientPrivilege),
    ):
        k.execute("UPDATE agents SET max_risk = 4")
