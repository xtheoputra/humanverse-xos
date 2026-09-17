"""Konfigurasi proses — seluruhnya dari lingkungan, awalan `HVX_`.

Tidak ada nilai bawaan untuk hal yang salahnya diam-diam: DSN (arch/09 §5
aturan 3 — rahasia tidak pernah di repo) **dan lingkungan**. Proses yang lupa
diberi `HVX_DATABASE_URL` atau `HVX_ENV` GAGAL saat mulai.

🔴 `env` semula berbawaan `"local"`. Citra api adalah satu artefak untuk semua
lingkungan dan tidak menyetel `HVX_ENV`, jadi deployment yang lupa mengisinya
menyajikan `/docs` dan `/openapi.json` sambil melaporkan dirinya sebagai
`local`. Bawaan yang gagal-terbuka bertentangan dengan alasan DSN di atas
dibuat wajib — jadi keduanya kini diperlakukan sama.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .db import url_async

Lingkungan = Literal["local", "test", "ci", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HVX_", extra="ignore", frozen=True)

    env: Lingkungan
    database_url: str = Field(min_length=1)
    redis_url: str = Field(min_length=1)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = True

    # Batas waktu tiap pemeriksaan ketergantungan di /health. Tanpa batas,
    # basis data yang menggantung membuat /health ikut menggantung — dan
    # pemeriksa kesehatan yang tidak pernah menjawab tidak bisa membedakan
    # "sakit" dari "lambat". HANYA untuk /health.
    health_timeout_s: float = Field(default=1.0, gt=0, le=10)

    # Batas soket klien Redis bersama (sesi, cache). Terpisah dari
    # health_timeout_s — lihat redis_store.py.
    redis_socket_timeout_s: float = Field(default=5.0, gt=0, le=60)
    redis_connect_timeout_s: float = Field(default=2.0, gt=0, le=30)

    @field_validator("database_url")
    @classmethod
    def _dsn_bisa_dipakai_kedua_driver(cls, nilai: str) -> str:
        url_async(nilai)  # melempar ValueError untuk skema asing atau parameter kueri
        return nilai
