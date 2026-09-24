"""Bantuan uji integrasi basis data — satu tempat, dipakai conftest.py dan berkas uji.

Diawali garis bawah supaya pytest tidak mengumpulkannya sebagai berkas uji.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from alembic.config import Config
from sqlalchemy.engine import make_url

from hvx.modules.platform import url_sync

AKAR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = AKAR / "data" / "migrations" / "alembic.ini"

# Peran LOGIN anggota `hvx_app` khusus uji — kembaran `hvx_api` di compose
# (B-40). Uji yang tersambung sebagai admin (superuser, pemilik tabel) tidak
# menguji apa pun tentang hak akses dan RLS: superuser melewati keduanya.
PERAN_APLIKASI_UJI = "hvx_api_uji"

# Sama dengan blok di spec/01 §Awalan — di sini karena peran login uji harus
# bisa dijadikan anggota `hvx_app` sebelum basis data mana pun dimigrasikan.
BUAT_HVX_APP = """
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hvx_app') THEN
    CREATE ROLE hvx_app NOLOGIN;
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$
"""


@dataclass(frozen=True)
class BasisDataV0:
    """Satu basis data termigrasi, dengan dua pintu masuk yang tidak boleh tertukar."""

    dsn_pemilik: str  # peran migrasi — superuser & pemilik tabel; RLS TIDAK berlaku
    dsn_aplikasi: str  # `hvx_api_uji` — anggota hvx_app; RLS dan GRANT spec/01 berlaku


def psycopg_dsn(dsn: str) -> str:
    return url_sync(dsn).replace("postgresql+psycopg://", "postgresql://", 1)


def dsn_ke(
    dsn_admin: str, nama_db: str, pengguna: str | None = None, sandi: str | None = None
) -> str:
    url = make_url(dsn_admin).set(database=nama_db)
    if pengguna is not None:
        url = url.set(username=pengguna, password=sandi)
    return url.render_as_string(hide_password=False)


def nama_db(dsn: str) -> str:
    nama = make_url(dsn).database
    assert nama, f"DSN tanpa nama basis data: {dsn}"
    return nama


def alembic(dsn: str) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", dsn)
    cfg.attributes["konfigurasi_log"] = False
    return cfg


@dataclass
class ApiUji:
    """Aplikasi utuh (create_app + lifespan) sebagai peran APLIKASI, dengan klien HTTP."""

    app: Any
    klien: Any  # httpx.AsyncClient
    db: BasisDataV0
    awalan_redis: str

    def penyimpan_sesi(self) -> Any:
        from hvx.modules.identity import PenyimpanSesi

        s = self.app.state.settings
        return PenyimpanSesi(
            self.app.state.redis, s.redis_prefix, s.access_token_ttl_s, s.refresh_token_ttl_s
        )

    async def pengguna_baru(
        self, *, display_name: str = "Pengguna Uji", timezone: str = "Asia/Jakarta"
    ) -> tuple[UUID, str]:
        """Pengguna + profil ditulis PEMILIK skema (bukan lewat /auth), plus token akses sah."""
        import psycopg

        with psycopg.connect(psycopg_dsn(self.db.dsn_pemilik), autocommit=True) as k:
            (uid,) = k.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
                (f"{uuid4().hex}@uji.id",),
            ).fetchone() or (None,)
            k.execute(
                "INSERT INTO profiles (user_id, display_name, timezone) VALUES (%s, %s, %s)",
                (uid, display_name, timezone),
            )
        assert isinstance(uid, UUID)
        token = await self.penyimpan_sesi().buat(uid)
        return uid, token.access_token


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class PenghitungKueri:
    """Menghitung pernyataan SQL yang dikirim engine aplikasi — tanpa `set_config` RLS.

    Dipakai untuk bukti *"terbaca dalam satu query"* (spec/07 2.1): jumlah
    kueri DATA yang benar-benar sampai ke PostgreSQL, bukan jumlah panggilan
    fungsi di kode.
    """

    def __init__(self, app: Any) -> None:
        from sqlalchemy import event

        self._event = event
        self._engine = app.state.engine.sync_engine
        self.pernyataan: list[str] = []

    def _catat(self, _conn: Any, _cursor: Any, sql: str, *_: Any) -> None:
        if "set_config('hvx.user_id'" not in sql:
            self.pernyataan.append(" ".join(sql.split()))

    def __enter__(self) -> PenghitungKueri:
        self._event.listen(self._engine, "before_cursor_execute", self._catat)
        return self

    def __exit__(self, *_: object) -> None:
        self._event.remove(self._engine, "before_cursor_execute", self._catat)
