from __future__ import annotations

import pytest
from pydantic import ValidationError

from hvx.modules.platform import Settings, url_async, url_sync

LENGKAP = {
    "HVX_DATABASE_URL": "postgresql://u:p@db:5432/hvx",
    "HVX_REDIS_URL": "redis://r:6379/0",
    "HVX_ENV": "ci",
    "HVX_IP_HASH_KEY": "k" * 32,
}


def _isi(monkeypatch: pytest.MonkeyPatch, **kecuali: None) -> None:
    for nama, nilai in LENGKAP.items():
        if nama in kecuali:
            monkeypatch.delenv(nama, raising=False)
        else:
            monkeypatch.setenv(nama, nilai)


def test_settings_dibaca_dari_lingkungan_berawalan_hvx(monkeypatch: pytest.MonkeyPatch) -> None:
    _isi(monkeypatch)

    s = Settings()

    assert s.database_url == "postgresql://u:p@db:5432/hvx"
    assert s.redis_url == "redis://r:6379/0"
    assert s.env == "ci"
    assert s.health_timeout_s == 1.0


@pytest.mark.parametrize(
    "hilang", ["HVX_DATABASE_URL", "HVX_REDIS_URL", "HVX_ENV", "HVX_IP_HASH_KEY"]
)
def test_tanpa_nilai_wajib_proses_gagal_mulai(monkeypatch: pytest.MonkeyPatch, hilang: str) -> None:
    """Tidak ada DSN bawaan dan tidak ada lingkungan bawaan — lupa mengisinya gagal keras.

    `HVX_ENV` semula berbawaan `local`: deployment yang lupa mengisinya
    menyajikan /docs sambil mengaku lingkungan lokal.
    """
    _isi(monkeypatch, **{hilang: None})

    with pytest.raises(ValidationError, match=hilang.removeprefix("HVX_").lower()):
        Settings()


def test_kunci_sidik_ip_pendek_ditolak(monkeypatch: pytest.MonkeyPatch) -> None:
    """Kunci HMAC pendek bisa ditebak — dan sidik IP-nya kembali bisa dibalik."""
    _isi(monkeypatch)
    monkeypatch.setenv("HVX_IP_HASH_KEY", "k" * 31)

    with pytest.raises(ValidationError, match="ip_hash_key"):
        Settings()


def test_token_akses_tidak_boleh_hidup_lebih_lama_dari_sesinya(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """🔴 Tinjauan Sprint 1: akses 86400 dtk + segar 3600 dtk diterima — catatan sesi
    kedaluwarsa lebih dulu, dan tanpa catatan itu `cabut` tidak menemukan token
    akses yang masih hidup: "dicabut → 401 seketika" patah."""
    _isi(monkeypatch)

    with pytest.raises(ValidationError, match="access_token_ttl_s"):
        Settings(access_token_ttl_s=7_200, refresh_token_ttl_s=3_600)

    s = Settings(access_token_ttl_s=3_600, refresh_token_ttl_s=3_600)
    assert s.access_token_ttl_s == s.refresh_token_ttl_s


def test_bawaan_gagal_masuk_per_akun_tidak_meledak_lebih_dari_100(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NIST SP 800-63B-4 §3.2.2 — ≤ 100 kegagalan. Bawaannya lapis pertama; lihat K-22."""
    _isi(monkeypatch)
    jumlah, _jendela = Settings().rate_limit_login_failures.split("/")

    assert int(jumlah) <= 100, f"bawaan batas gagal masuk per akun: {jumlah} tebakan sekaligus"


def test_lingkungan_tak_dikenal_ditolak() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql://x", redis_url="redis://x", env="staging")  # type: ignore[arg-type]


def test_batas_waktu_redis_terpisah_dari_batas_waktu_health() -> None:
    s = Settings(
        database_url="postgresql://x", redis_url="redis://x", env="test", health_timeout_s=0.5
    )

    assert s.redis_socket_timeout_s > s.health_timeout_s


@pytest.mark.parametrize(
    ("dsn", "async_", "sync_"),
    [
        (
            "postgresql://u:p@h:5432/d",
            "postgresql+asyncpg://u:p@h:5432/d",
            "postgresql+psycopg://u:p@h:5432/d",
        ),
        ("postgres://u@h/d", "postgresql+asyncpg://u@h/d", "postgresql+psycopg://u@h/d"),
        ("postgresql+psycopg2://u@h/d", "postgresql+asyncpg://u@h/d", "postgresql+psycopg://u@h/d"),
    ],
)
def test_driver_diturunkan_dari_satu_dsn(dsn: str, async_: str, sync_: str) -> None:
    assert url_async(dsn) == async_
    assert url_sync(dsn) == sync_


def test_skema_bukan_postgres_ditolak() -> None:
    with pytest.raises(ValueError, match="postgresql"):
        url_async("mysql://u@h/d")


@pytest.mark.parametrize(
    "dsn",
    [
        "postgresql://u@h/d?sslmode=require",
        "postgresql://u@h/d?ssl=true",
        "postgresql://u@h/d?connect_timeout=5",
        "postgresql://u@h/d?application_name=hvx",
    ],
)
def test_dsn_berparameter_kueri_ditolak_saat_mulai(dsn: str) -> None:
    """asyncpg menolak `sslmode`, psycopg menolak `ssl` — tidak ada DSN
    berparameter yang bekerja untuk keduanya. Ditolak di Settings, bukan di
    kueri pertama."""
    with pytest.raises(ValidationError, match="PGSSLMODE"):
        Settings(database_url=dsn, redis_url="redis://x", env="test")


def test_qdrant_tanpa_kunci_penyemat_ditolak_saat_mulai(monkeypatch: pytest.MonkeyPatch) -> None:
    """K-26 — penyemat tanpa kunci bisa dibalik dengan kamus: vektor di Qdrant
    membocorkan kata isi jurnal. Qdrant yang diisi tanpa kunci gagal keras."""
    _isi(monkeypatch)
    monkeypatch.setenv("HVX_QDRANT_URL", "http://qdrant:6333")

    with pytest.raises(ValidationError, match="HVX_SEMATAN_KEY"):
        Settings()

    monkeypatch.setenv("HVX_SEMATAN_KEY", "s" * 31)
    with pytest.raises(ValidationError, match="sematan_key"):
        Settings()

    monkeypatch.setenv("HVX_SEMATAN_KEY", "s" * 32)
    assert Settings().qdrant_url == "http://qdrant:6333"
