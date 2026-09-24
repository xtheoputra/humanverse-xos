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

import re
from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .db import url_async

Lingkungan = Literal["local", "test", "ci", "production"]

# "jumlah/detik" — lihat batas_laju.py
POLA_BATAS = r"^[1-9][0-9]{0,5}/[1-9][0-9]{0,5}$"

# Id model "penyedia/nama" — `lokal/hvx-nalar-v1` (platform/model.py, K-28).
POLA_MODEL = r"^[a-z][a-z0-9-]{0,19}/[a-z0-9][a-z0-9._-]{0,79}$"

# Satu asal peramban: skema + host + port opsional — persis yang dikirim `Origin`.
_POLA_ASAL = r"https?://[a-z0-9]([a-z0-9.-]*[a-z0-9])?(:[0-9]{1,5})?"


def _pisah_asal(nilai: str) -> tuple[str, ...]:
    return tuple(a.strip() for a in nilai.split(",") if a.strip())


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
    # Login GAGAL per akun: `jumlah` tebakan sekaligus (NIST SP 800-63B-4 §3.2.2:
    # ≤ 100), lalu satu tiap `detik/jumlah`. Ini batas LAJU, bukan penguncian
    # sesudah 100 kegagalan beruntun — penguncian butuh jalur pemulihan akun yang
    # V0 belum punya (K-22, tinjauan Sprint 1). Berhasil masuk menghapus hitungannya.
    rate_limit_login_failures: str = Field(default="100/86400", pattern=POLA_BATAS)

    # Kunci HMAC untuk `audit_logs.ip_hash` (spec/01: "hash, bukan IP mentah")
    # dan kunci batas laju per IP. WAJIB, tanpa bawaan: sha256 polos atas IPv4
    # bisa dibalik dengan mencoba keempat miliar alamat, dan kunci acak per
    # proses membuat jejak satu IP tidak bisa dipertemukan antarinstans.
    ip_hash_key: SecretStr = Field(min_length=32)

    # Asal peramban yang boleh memanggil api (CORS) — dipisah koma, mis.
    # `http://localhost:5000` untuk aplikasi Flutter web lokal (spec/07 2.7).
    # Kosong = tidak ada CORS sama sekali: aplikasi seluler tidak butuh, dan
    # asal yang tidak disebut tidak pernah diloloskan. `*` DITOLAK — token
    # bearer di tangan skrip asal mana pun bukan pilihan yang bisa diambil diam-diam.
    cors_origins: str = ""

    # Basis data vektor memori (spec/07 3.5, ADR-003). Kosong = memori tanpa
    # pencarian semantik: ekstraksi tetap menulis memori ke PostgreSQL, pekerja
    # tidak menyemat, dan pencarian memori tidak tersedia — fitur lain tetap
    # berjalan (Qdrant bukan ketergantungan autentikasi). Memori yang tertunda
    # disemat penyelaras begitu Qdrant diisi.
    qdrant_url: str | None = None
    qdrant_api_key: SecretStr | None = None
    qdrant_koleksi: str = Field(default="memories", pattern=r"^[a-z0-9][a-z0-9_-]{0,59}$")
    # Kunci penyemat lokal (K-26) — WAJIB bila `qdrant_url` diisi: feature hashing
    # tanpa kunci bisa dibalik dengan kamus, jadi vektor di Qdrant membocorkan kata
    # isi jurnal. Mengganti kunci = seluruh memori disemat ulang (sidiknya ikut di
    # nama penyemat, `memories.embedding_model`).
    sematan_key: SecretStr | None = Field(default=None, min_length=32)

    # AI Gateway (spec/07 4.1, K-28): model tiap kelas, "penyedia/nama". V0 hanya
    # penyedia `lokal` — tanpa jaringan dan tanpa biaya; penyedia berbayar, dan ke
    # mana data pengguna boleh dikirim, keputusan pemilik (A-6/#18, arch/05 §6).
    model_simple: str = Field(default="lokal/hvx-ringkas-v1", pattern=POLA_MODEL)
    model_reasoning: str = Field(default="lokal/hvx-nalar-v1", pattern=POLA_MODEL)
    # Harga USD per SEJUTA token (masuk, keluar) per model — JSON,
    # `{"lokal/hvx-nalar-v1": [3, 15]}`. Model di luar penyedia `lokal` tanpa harga
    # DITOLAK gerbang: biaya yang tak terhitung tak bisa dibatasi (4.9).
    model_harga: dict[str, tuple[Decimal, Decimal]] = Field(default_factory=dict)

    @field_validator("model_harga")
    @classmethod
    def _harga_model_sah(
        cls, nilai: dict[str, tuple[Decimal, Decimal]]
    ) -> dict[str, tuple[Decimal, Decimal]]:
        for model, (masuk, keluar) in nilai.items():
            if not re.fullmatch(POLA_MODEL, model):
                raise ValueError("HVX_MODEL_HARGA: id model wajib `penyedia/nama`")
            if masuk < 0 or keluar < 0 or not (masuk.is_finite() and keluar.is_finite()):
                raise ValueError("HVX_MODEL_HARGA: harga wajib angka ≥ 0")
        return nilai

    @model_validator(mode="after")
    def _vektor_berkunci(self) -> Self:
        if self.qdrant_url and self.sematan_key is None:
            raise ValueError("HVX_SEMATAN_KEY wajib bila HVX_QDRANT_URL diisi (K-26)")
        return self

    @field_validator("cors_origins")
    @classmethod
    def _asal_cors_persis(cls, nilai: str) -> str:
        for asal in _pisah_asal(nilai):
            if not re.fullmatch(_POLA_ASAL, asal):
                raise ValueError(
                    "HVX_CORS_ORIGINS: tiap asal wajib `http(s)://host[:port]` huruf kecil, "
                    "tanpa jalur, tanpa `*`"
                )
        return nilai

    @property
    def asal_cors(self) -> tuple[str, ...]:
        return _pisah_asal(self.cors_origins)

    @field_validator("database_url")
    @classmethod
    def _dsn_bisa_dipakai_kedua_driver(cls, nilai: str) -> str:
        url_async(nilai)  # melempar ValueError untuk skema asing atau parameter kueri
        return nilai

    @model_validator(mode="after")
    def _token_akses_tidak_hidup_lebih_lama_dari_sesinya(self) -> Self:
        # Catatan sesi di Redis berumur token SEGAR; pencabutan membaca sidik token
        # akses dari catatan itu. Token akses yang hidup lebih lama dari catatannya
        # tidak bisa dicabut lagi — "dicabut → 401 seketika" patah (tinjauan Sprint 1).
        if self.access_token_ttl_s > self.refresh_token_ttl_s:
            raise ValueError(
                "access_token_ttl_s tidak boleh melebihi refresh_token_ttl_s: token akses "
                "yang hidup lebih lama dari catatan sesinya tidak bisa dicabut"
            )
        return self
