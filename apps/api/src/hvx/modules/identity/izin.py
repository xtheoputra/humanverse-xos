"""Mesin izin — spec/07 tugas 1.5: `check(user, subject, scope, action)`.

Selesai bila: default `ask`; hasil di-cache di Redis; uji untuk
allow/deny/ask/expired. Dipakai gerbang risiko spec/05 (`deny` → tolak & catat,
`ask` → minta izin, `allow` → lanjut).

* **Tanpa baris = `ask`**, bukan `deny` dan bukan `allow` (spec/01
  `permissions.decision DEFAULT 'ask'`; naskah 4 *“Act selalu di bawah kontrol
  pengguna”*). Izin yang **kedaluwarsa juga kembali ke `ask`**: "izinkan sekali"
  yang habis tidak diam-diam berubah menjadi izin permanen, dan larangan
  sementara yang habis tidak berubah menjadi larangan permanen.
* **`bawaan` pemanggil** menggantikan `ask` itu — HANYA untuk yang tanpa
  keputusan tersimpan atau kedaluwarsa. Gerbang risiko spec/05 butuh risk 0·1 →
  `allow` tanpa menimpa *“tanya aku”* yang disetel pengguna; versi pertama
  menjawab `ask` untuk keduanya, jadi keduanya tak bisa dibedakan (E-167). Cache
  menyimpan *“tanpa keputusan”*, bukan bawaan satu pemanggil.
* **Scope sensitif tidak pernah `allow` karena bawaan** (`scope.SCOPE_RESMI`,
  E-180): `bawaan="allow"` untuk `journal_raw` menjadi `ask`. Aturannya di SATU
  tempat — gerbang risiko 4.5 dan pencarian memori 3.7 tidak perlu ingat.
* **Scope di luar daftar resmi ditolak** (spec/05 aturan 2) — keputusan atas
  scope salah ketik tidak tersimpan sebagai baris yang tidak pernah ditanyakan.
* **Kedaluwarsa diukur jam basis data**, bukan jam proses api — satu sumber
  waktu untuk semua instans.
* **Cache tidak hidup lebih lama dari izinnya**: cache izin sementara berakhir
  pada waktu MUTLAK — `min(dibaca + HVX_PERMISSION_CACHE_TTL_S, expires_at − 1
  dtk)` menurut jam basis data, lewat `SET … PXAT` — jadi jeda antara membaca
  basis data dan menulis Redis tidak memperpanjangnya. 🔴 Versi pertama tanpa
  margin (tinjauan Sprint 1); versi kedua memakai umur RELATIF yang dihitung
  saat dibaca, dan cache yang ditulis > 1 dtk sesudahnya — sistem yang sibuk —
  tetap menjawab `allow` sesudah izinnya habis (ditemukan uji yang berkedip di
  gerbang penuh Sprint 3). Margin kini hanya menyerap selisih jam PostgreSQL dan
  Redis (satu mesin di V0). Izin yang tinggal kurang dari sedetik tidak di-cache.
* **Pencabutan berlaku seketika, bukan setelah cache habis** — sama dengan
  sesi (tugas 1.2). Menghapus kunci cache saja TIDAK cukup: pembaca yang
  membaca basis data sebelum commit lalu menulis cache sesudahnya menghidupkan
  kembali izin yang baru dicabut, selama umur cache. Karena itu tiap kunci
  memuat **generasi** milik pengguna, dan `tetapkan()` mengganti generasinya
  sebelum dan sesudah commit: tulisan pembaca lambat mendarat di generasi yang
  sudah tidak dibaca siapa pun. Generasi yang hilang dari Redis (kedaluwarsa,
  diusir) diganti generasi acak baru — hasilnya cache kosong, tidak pernah
  cache lama.
* Tiap perubahan dicatat `audit()` di transaksi yang sama (tugas 1.6:
  *“izin … tercatat”*).

Yang TIDAK diputuskan di sini: `condition.consent` naskah 12 §8.7 dan
"persetujuan sebagai atap izin" (#59 butir 3) — keduanya milik pemilik.
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import platform

from .audit import audit
from .scope import SCOPE_RESMI

Keputusan = Literal["allow", "deny", "ask"]
SubjekTipe = Literal["agent", "tool", "integration"]
Aksi = Literal["read", "write", "execute", "share", "delete"]

# Sama dengan CHECK spec/01 `permissions` — ditolak di sini supaya salah ketik
# tidak sampai ke basis data sebagai galat 500.
_KEPUTUSAN: frozenset[str] = frozenset({"allow", "deny", "ask"})
_SUBJEK_TIPE: frozenset[str] = frozenset({"agent", "tool", "integration"})
_AKSI: frozenset[str] = frozenset({"read", "write", "execute", "share", "delete"})
# 'coach-agent' (spec/05 manifest) · 'habit.streak' (tool registry)
_POLA_SUBJEK = re.compile(r"^[a-z0-9][a-z0-9._-]{0,99}$")
# 'habits' · 'journal_raw' · 'coaching_notes' (spec/05 scope)
_POLA_SCOPE = re.compile(r"^[a-z][a-z0-9_]{0,62}$")

# Umur kunci generasi. Bila habis, generasi baru dibuat — cache pengguna itu
# kosong sekali, tidak pernah basi.
_UMUR_GENERASI_S = 86_400

# Umur cache izin sementara = sisa umurnya saat dibaca − margin ini (lihat docstring).
_MARGIN_KEDALUWARSA_MS = 1_000

# Nilai cache untuk "tidak ada keputusan tersimpan" — jawabannya bawaan pemanggil.
_TANPA_KEPUTUSAN = "-"

_AKSI_AUDIT: dict[str, str] = {
    "allow": "permission.granted",
    "deny": "permission.denied",
    "ask": "permission.reset",
}


@dataclass(frozen=True)
class _UmurCache:
    """Kapan jawaban cache habis: relatif (`px`) — atau MUTLAK (`pxat`, jam basis data)
    untuk izin sementara, supaya jeda sebelum ditulis tidak memperpanjangnya."""

    px: int | None = None
    pxat: int | None = None


class IzinTidakSah(ValueError):
    """Subjek, scope, aksi, atau keputusan berbentuk salah — ditolak sebelum Redis & basis data."""


@dataclass(frozen=True)
class Subjek:
    """Siapa yang meminta: agent (`coach-agent`), tool (`habit.streak`), atau integrasi."""

    tipe: SubjekTipe
    id: str

    def __post_init__(self) -> None:
        if self.tipe not in _SUBJEK_TIPE:
            raise IzinTidakSah(f"tipe subjek tak dikenal: {self.tipe!r}")
        if not isinstance(self.id, str) or not _POLA_SUBJEK.fullmatch(self.id):
            raise IzinTidakSah("id subjek wajib huruf kecil, angka, `.`, `_`, `-` (≤100)")


# Milidetik epoch menurut jam BASIS DATA — kedaluwarsa cache dihitung dari
# keduanya, bukan dari jam proses api.
_BACA = text(
    """
    SELECT decision,
           floor(extract(epoch FROM expires_at) * 1000)::bigint AS habis_ms,
           floor(extract(epoch FROM clock_timestamp()) * 1000)::bigint AS kini_ms
    FROM permissions
    WHERE user_id = :user_id AND subject_type = :tipe AND subject_id = :subjek
      AND scope = :scope AND action = :aksi
    """
)

_TETAPKAN = text(
    """
    INSERT INTO permissions (user_id, subject_type, subject_id, scope, action, decision, expires_at)
    VALUES (:user_id, :tipe, :subjek, :scope, :aksi, :keputusan, :expires_at)
    ON CONFLICT (user_id, subject_type, subject_id, scope, action)
    DO UPDATE SET decision = EXCLUDED.decision, expires_at = EXCLUDED.expires_at
    """
)


def _periksa(user_id: UUID, scope: str, aksi: str) -> None:
    if not isinstance(user_id, UUID):
        raise TypeError(f"user_id wajib UUID, bukan {type(user_id).__name__}")
    if not isinstance(scope, str) or not _POLA_SCOPE.fullmatch(scope):
        raise IzinTidakSah("scope wajib snake_case huruf kecil (≤63)")
    if scope not in SCOPE_RESMI:
        raise IzinTidakSah("scope tidak ada di daftar scope resmi (spec/05 aturan 2)")
    if aksi not in _AKSI:
        raise IzinTidakSah(f"aksi tak dikenal: {aksi!r}")


class MesinIzin:
    def __init__(self, engine: AsyncEngine, redis: Redis, awalan: str, ttl_cache_s: int) -> None:
        self._engine = engine
        self._r = redis
        self._awalan = awalan
        self._ttl_ms = ttl_cache_s * 1000

    def _k_generasi(self, user_id: UUID) -> str:
        return f"{self._awalan}:izin:{user_id}:generasi"

    def _k_keputusan(
        self, user_id: UUID, generasi: str, subjek: Subjek, scope: str, aksi: str
    ) -> str:
        # Semua bagian sudah lolos pola tanpa `:` — kunci tidak bisa ditabrakkan.
        return f"{self._awalan}:izin:{user_id}:{generasi}:{subjek.tipe}:{subjek.id}:{scope}:{aksi}"

    async def _generasi(self, user_id: UUID) -> str:
        """Generasi cache pengguna — dibuat acak bila belum ada, dalam SATU perintah."""
        calon = secrets.token_hex(8)
        lama = await self._r.set(
            self._k_generasi(user_id), calon, nx=True, get=True, ex=_UMUR_GENERASI_S
        )
        return calon if lama is None else str(lama)

    async def _ganti_generasi(self, user_id: UUID) -> None:
        await self._r.set(self._k_generasi(user_id), secrets.token_hex(8), ex=_UMUR_GENERASI_S)

    async def _baca_basis_data(
        self, user_id: UUID, subjek: Subjek, scope: str, aksi: str
    ) -> tuple[Keputusan | None, _UmurCache | None]:
        """(keputusan tersimpan atau None, umur cache-nya) — umur None: jangan di-cache."""
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            baris = (
                await conn.execute(
                    _BACA,
                    {
                        "user_id": user_id,
                        "tipe": subjek.tipe,
                        "subjek": subjek.id,
                        "scope": scope,
                        "aksi": aksi,
                    },
                )
            ).first()
        if baris is None:
            return None, _UmurCache(px=self._ttl_ms)
        if baris.habis_ms is None:
            return cast(Keputusan, baris.decision), _UmurCache(px=self._ttl_ms)
        if baris.habis_ms <= baris.kini_ms:
            return None, _UmurCache(px=self._ttl_ms)  # kedaluwarsa → kembali ke bawaan
        habis = min(baris.kini_ms + self._ttl_ms, baris.habis_ms - _MARGIN_KEDALUWARSA_MS)
        if habis <= baris.kini_ms:
            return cast(Keputusan, baris.decision), None
        return cast(Keputusan, baris.decision), _UmurCache(pxat=habis)

    async def cek(
        self,
        user_id: UUID,
        subjek: Subjek,
        scope: str,
        aksi: Aksi,
        *,
        bawaan: Keputusan = "ask",
    ) -> Keputusan:
        """`allow` · `deny` · `ask` untuk `subjek` yang ingin `aksi` atas `scope` milik pengguna.

        `bawaan` hanya untuk yang tanpa keputusan tersimpan (atau kedaluwarsa) —
        keputusan pengguna, termasuk `ask` eksplisit, selalu menang.
        """
        _periksa(user_id, scope, aksi)
        if bawaan not in _KEPUTUSAN:
            raise IzinTidakSah(f"bawaan tak dikenal: {bawaan!r}")
        if bawaan == "allow" and SCOPE_RESMI[scope].sensitif:
            bawaan = "ask"  # hanya `allow` yang DISIMPAN pengguna membuka scope sensitif
        generasi = await self._generasi(user_id)
        kunci = self._k_keputusan(user_id, generasi, subjek, scope, aksi)
        tersimpan = await self._r.get(kunci)
        if tersimpan in _KEPUTUSAN:
            return cast(Keputusan, tersimpan)
        if tersimpan == _TANPA_KEPUTUSAN:
            return bawaan

        keputusan, umur = await self._baca_basis_data(user_id, subjek, scope, aksi)
        if umur is not None:
            await self._r.set(kunci, keputusan or _TANPA_KEPUTUSAN, px=umur.px, pxat=umur.pxat)
        return keputusan or bawaan

    async def tetapkan(
        self,
        user_id: UUID,
        subjek: Subjek,
        scope: str,
        aksi: Aksi,
        keputusan: Keputusan,
        *,
        expires_at: datetime | None = None,
        ip_hash: str | None = None,
    ) -> None:
        """Simpan keputusan pengguna. `expires_at=None` = sampai diubah; `ask` = tanya lagi."""
        _periksa(user_id, scope, aksi)
        if keputusan not in _KEPUTUSAN:
            raise IzinTidakSah(f"keputusan tak dikenal: {keputusan!r}")
        if expires_at is not None and expires_at.utcoffset() is None:
            raise IzinTidakSah("expires_at wajib berzona waktu")

        await self._ganti_generasi(user_id)
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            await conn.execute(
                _TETAPKAN,
                {
                    "user_id": user_id,
                    "tipe": subjek.tipe,
                    "subjek": subjek.id,
                    "scope": scope,
                    "aksi": aksi,
                    "keputusan": keputusan,
                    "expires_at": expires_at,
                },
            )
            await audit(
                conn,
                aksi=_AKSI_AUDIT[keputusan],
                aktor_tipe="user",
                aktor_id=str(user_id),
                user_id=user_id,
                subjek_tipe=subjek.tipe,
                subjek_id=subjek.id,
                ip_hash=ip_hash,
                metadata={"scope": scope, "action": aksi, "sementara": expires_at is not None},
            )
        # Sesudah commit: pembaca yang membaca nilai lama di tengah transaksi di
        # atas menulis ke generasi yang kini ditinggalkan.
        await self._ganti_generasi(user_id)


def mesin_izin(request: Request) -> MesinIzin:
    """Dependensi FastAPI — mesin izin di atas engine & Redis bersama proses."""
    settings = platform.settings_dari(request)
    return MesinIzin(
        platform.engine_dari(request),
        platform.redis_dari(request),
        settings.redis_prefix,
        settings.permission_cache_ttl_s,
    )
