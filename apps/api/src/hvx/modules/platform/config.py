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

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .db import url_async

Lingkungan = Literal["local", "test", "ci", "production"]

# "jumlah/detik" — lihat batas_laju.py
POLA_BATAS = r"^[1-9][0-9]{0,5}/[1-9][0-9]{0,5}$"


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

    # Awalan semua kunci Redis milik proses ini — uji memakai awalan acak supaya
    # sesi dan penghitung batas laju tidak bertabrakan antaruji.
    redis_prefix: str = Field(default="hvx", pattern=r"^[a-z0-9][a-z0-9-]{0,39}$")

    # Sesi (spec/07 1.2). Token akses berumur pendek karena ia yang dibawa tiap
    # permintaan; token segar berumur panjang dan BEROTASI tiap dipakai.
    access_token_ttl_s: int = Field(default=900, ge=60, le=86_400)
    refresh_token_ttl_s: int = Field(default=2_592_000, ge=3_600, le=7_776_000)

    # Umur MAKSIMAL cache keputusan izin (spec/07 1.5). Pencabutan tidak
    # menunggu angka ini — generasi cache diganti saat izin berubah; angka ini
    # hanya membatasi berapa lama perubahan di LUAR mesin izin tak terlihat.
    permission_cache_ttl_s: int = Field(default=300, ge=1, le=3_600)

    # Batas laju (spec/07 1.7), "jumlah/detik": boleh meledak sampai `jumlah`,
    # lalu terisi satu tiap `detik/jumlah`. Satuan kuncinya di sebelah kanan.
    rate_limit_ip: str = Field(default="600/60", pattern=POLA_BATAS)  # seluruh /v1/*, per IP (/64)
    rate_limit_user: str = Field(default="300/60", pattern=POLA_BATAS)  # rute bersesi, per pengguna
    rate_limit_auth_ip: str = Field(default="30/600", pattern=POLA_BATAS)  # daftar & masuk, per IP
    # Login GAGAL beruntun per akun — NIST SP 800-63B-4: tidak lebih dari 100.
    # Berhasil masuk menghapus hitungannya.
    rate_limit_login_failures: str = Field(default="100/86400", pattern=POLA_BATAS)

    # Kunci HMAC untuk `audit_logs.ip_hash` (spec/01: "hash, bukan IP mentah")
    # dan kunci batas laju per IP. WAJIB, tanpa bawaan: sha256 polos atas IPv4
    # bisa dibalik dengan mencoba keempat miliar alamat, dan kunci acak per
    # proses membuat jejak satu IP tidak bisa dipertemukan antarinstans.
    ip_hash_key: SecretStr = Field(min_length=32)

    @field_validator("database_url")
    @classmethod
    def _dsn_bisa_dipakai_kedua_driver(cls, nilai: str) -> str:
        url_async(nilai)  # melempar ValueError untuk skema asing atau parameter kueri
        return nilai
