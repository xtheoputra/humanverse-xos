"""SQL modul `identity` — hanya tabel miliknya: users · consents · permissions · audit_logs.

spec/06 aturan 5, dijaga `tests/unit/test_batas_tabel.py`: berkas di modul ini
tidak boleh menyebut tabel milik modul lain.

Tiap fungsi menerima `AsyncConnection` dari pemanggil — transaksinya milik
lapisan layanan (`platform.transaksi_pengguna`), bukan milik repository, supaya
satu tindakan pengguna bisa menulis beberapa tabel secara atomik.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from .schemas import PenggunaRingkas

_SISIP_AUDIT = text(
    """
    INSERT INTO audit_logs
      (data_subject, actor_type, actor_id, user_id, action,
       subject_type, subject_id, request_id, ip_hash, metadata)
    VALUES
      (:data_subject, :actor_type, :actor_id, :user_id, :action,
       :subject_type, :subject_id, :request_id, :ip_hash, CAST(:metadata AS jsonb))
    """
)


async def tambah_audit(
    conn: AsyncConnection,
    *,
    data_subject: str,
    aktor_tipe: str,
    aktor_id: str,
    user_id: UUID | None,
    aksi: str,
    subjek_tipe: str | None,
    subjek_id: str | None,
    request_id: str | None,
    ip_hash: str | None,
    metadata: Mapping[str, object],
) -> None:
    await conn.execute(
        _SISIP_AUDIT,
        {
            "data_subject": data_subject,
            "actor_type": aktor_tipe,
            "actor_id": aktor_id,
            "user_id": user_id,
            "action": aksi,
            "subject_type": subjek_tipe,
            "subject_id": subjek_id,
            "request_id": request_id,
            "ip_hash": ip_hash,
            "metadata": json.dumps(dict(metadata)),
        },
    )


_PENGGUNA = text(
    """
    SELECT id, email::text AS email, status, email_verified_at, created_at
    FROM users
    WHERE id = :user_id AND deleted_at IS NULL
    """
)


# Baris akun masih ADA — dan tetap ada sampai transaksi pemanggil selesai: `FOR KEY SHARE`
# menahan `DELETE` sapuan hapus akun (tahap 3, `FOR UPDATE`), jadi jejak yang ditulis di
# transaksi ini masih ikut dianonimkan sapuan; sapuan yang menang lebih dulu → `False`.
_KUNCI_AKUN_ADA = text("SELECT 1 FROM users WHERE id = :id FOR KEY SHARE")


async def kunci_akun_ada(conn: AsyncConnection, user_id: UUID) -> bool:
    return (await conn.execute(_KUNCI_AKUN_ADA, {"id": user_id})).first() is not None


async def ambil_pengguna(conn: AsyncConnection, user_id: UUID) -> PenggunaRingkas | None:
    baris = (await conn.execute(_PENGGUNA, {"user_id": user_id})).mappings().first()
    return PenggunaRingkas.model_validate(dict(baris)) if baris else None


# ── consents (spec/07 1.4) ──────────────────────────────────────────────────
# `created_at = clock_timestamp()`, bukan bawaan `now()`: now() membeku di awal
# transaksi, sehingga "cabut lalu setujui lagi" dalam satu transaksi akan punya
# waktu yang SAMA — dan urutan riwayat yang hanya-tambah jadi tak tentu.
_SISIP_PERSETUJUAN = text(
    """
    INSERT INTO consents
      (user_id, kind, purpose, data_scopes, granted, policy_version, source,
       granted_at, revoked_at, expires_at, created_at)
    VALUES
      (:user_id, :kind, :purpose, :data_scopes, :granted, :policy_version, :source,
       CASE WHEN :granted THEN clock_timestamp() END,
       CASE WHEN :dicabut THEN clock_timestamp() END,
       :expires_at, clock_timestamp())
    """
)

# Satu baris TERAKHIR per (tujuan, jenis) — riwayat hanya-tambah dibaca dari
# ujungnya. 🔴 Versi pertama per tujuan saja: `terms` dan `privacy` sama-sama
# bertujuan `service`, jadi menyetujui syarat baru sesudah mencabut privasi
# menutupi pencabutannya (tinjauan Sprint 1).
_PERSETUJUAN_TERAKHIR = text(
    """
    SELECT DISTINCT ON (purpose, kind) purpose, kind, granted, data_scopes,
           (expires_at IS NULL OR expires_at > now()) AS masih_berlaku
    FROM consents
    WHERE user_id = :user_id AND purpose = ANY(:tujuan)
    ORDER BY purpose, kind, created_at DESC
    """
)


@dataclass(frozen=True)
class PersetujuanTerakhir:
    kind: str
    granted: bool
    data_scopes: frozenset[str]
    masih_berlaku: bool


async def tambah_persetujuan(
    conn: AsyncConnection,
    *,
    user_id: UUID,
    kind: str,
    purpose: str,
    data_scopes: list[str],
    granted: bool,
    dicabut: bool,
    policy_version: str,
    source: str,
    expires_at: object | None,
) -> None:
    await conn.execute(
        _SISIP_PERSETUJUAN,
        {
            "user_id": user_id,
            "kind": kind,
            "purpose": purpose,
            "data_scopes": data_scopes,
            "granted": granted,
            "dicabut": dicabut,
            "policy_version": policy_version,
            "source": source,
            "expires_at": expires_at,
        },
    )


async def persetujuan_terakhir(
    conn: AsyncConnection, user_id: UUID, tujuan: list[str]
) -> dict[str, list[PersetujuanTerakhir]]:
    """{purpose: baris terakhir tiap jenisnya}; tujuan tanpa riwayat tidak muncul."""
    hasil = await conn.execute(_PERSETUJUAN_TERAKHIR, {"user_id": user_id, "tujuan": tujuan})
    terakhir: dict[str, list[PersetujuanTerakhir]] = {}
    for b in hasil:
        terakhir.setdefault(b.purpose, []).append(
            PersetujuanTerakhir(
                kind=b.kind,
                granted=bool(b.granted),
                data_scopes=frozenset(b.data_scopes or ()),
                masih_berlaku=bool(b.masih_berlaku),
            )
        )
    return terakhir


# ── users (spec/07 1.1) ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class AkunUntukMasuk:
    id: UUID
    password_hash: str
    status: str


@dataclass(frozen=True)
class PencarianMasuk:
    """`kunci` = email sebagaimana `citext` membandingkannya — terisi juga bila akun tak ada."""

    kunci: str
    akun: AkunUntukMasuk | None


async def tambah_pengguna(
    conn: AsyncConnection, user_id: UUID, email: str, password_hash: str
) -> None:
    # `id` dari aplikasi, bukan bawaan basis data: RLS (spec/01 §11) hanya
    # meloloskan baris `users` yang id-nya sama dengan pengguna transaksi ini.
    await conn.execute(
        text("INSERT INTO users (id, email, password_hash) VALUES (:id, :email, :hash)"),
        {"id": user_id, "email": email, "hash": password_hash},
    )


# `lower(text)` dan pembanding `citext` sama-sama memakai collation bawaan basis
# data — kunci batas laju per akun yang dibentuk DI SINI mengenali akun persis
# seperti `auth_lookup_for_login` mengenalinya. Satu perjalanan untuk keduanya,
# dan selalu satu baris: akun yang tidak ada tetap punya kunci.
_CARI_UNTUK_MASUK = text(
    """
    SELECT k.kunci, a.id, a.password_hash, a.status
    FROM (SELECT lower(CAST(:email AS text)) AS kunci) AS k
    LEFT JOIN LATERAL auth_lookup_for_login(CAST(:email AS citext)) AS a ON true
    """
)


async def cari_untuk_masuk(conn: AsyncConnection, email: str) -> PencarianMasuk:
    """Satu-satunya pencarian akun sebelum pengguna dikenali — lewat fungsi spec/01 §12."""
    b = (await conn.execute(_CARI_UNTUK_MASUK, {"email": email})).one()
    akun = AkunUntukMasuk(b.id, b.password_hash, b.status) if b.id is not None else None
    return PencarianMasuk(kunci=b.kunci, akun=akun)


async def ganti_hash_sandi(conn: AsyncConnection, user_id: UUID, password_hash: str) -> None:
    await conn.execute(
        text("UPDATE users SET password_hash = :hash WHERE id = :id"),
        {"hash": password_hash, "id": user_id},
    )


async def catat_masuk(conn: AsyncConnection, user_id: UUID) -> None:
    await conn.execute(
        text("UPDATE users SET last_login_at = now() WHERE id = :id"), {"id": user_id}
    )


# ── Alur hapus akun (6.5) — tahap 1 & pembatalan, di RLS pemiliknya ──


@dataclass(frozen=True)
class AkunUntukHapus:
    password_hash: str
    status: str
    deletion_scheduled_at: datetime | None
    # Kunci jatah login gagal akun ini — email sebagaimana `citext` mengenalinya, sama
    # dengan `_CARI_UNTUK_MASUK` (`lower()` PostgreSQL, bukan Python; laju.py).
    kunci: str


_AKUN_HAPUS = text(
    "SELECT password_hash, status, deletion_scheduled_at, lower(CAST(email AS text)) AS kunci "
    "FROM users WHERE id = :id"
)
# Tahap 1: hanya dari `active` (RETURNING kosong kalau sudah pending/suspended).
_JADWALKAN_HAPUS = text(
    """
    UPDATE users
    SET status = 'pending_deletion',
        deletion_scheduled_at = now() + make_interval(days => :hari)
    WHERE id = :id AND status = 'active'
    RETURNING deletion_scheduled_at
    """
)
# Tenggang BERAKHIR di `deletion_scheduled_at`: sesudahnya tidak ada jalan pulang — sapuan
# sudah boleh membuang titik Qdrant-nya, dan akun yang dipulihkan sesudah itu hidup
# tanpa vektor memorinya (K-39).
_BATALKAN_HAPUS = text(
    """
    UPDATE users SET status = 'active', deletion_scheduled_at = NULL
    WHERE id = :id AND status = 'pending_deletion' AND deletion_scheduled_at > now()
    RETURNING id
    """
)
_STATUS_AKUN = text("SELECT status FROM users WHERE id = :id")


async def akun_untuk_hapus(conn: AsyncConnection, user_id: UUID) -> AkunUntukHapus | None:
    """Sandi + status + jadwal + kunci jatah akun sendiri — untuk sandi ulang (RLS own-row)."""
    b = (await conn.execute(_AKUN_HAPUS, {"id": user_id})).mappings().first()
    if b is None:
        return None
    return AkunUntukHapus(b["password_hash"], b["status"], b["deletion_scheduled_at"], b["kunci"])


async def jadwalkan_hapus(conn: AsyncConnection, user_id: UUID, hari: int) -> datetime | None:
    """Tandai `pending_deletion` + jadwal; `None` bila bukan dari `active` (idempoten)."""
    b = (await conn.execute(_JADWALKAN_HAPUS, {"id": user_id, "hari": hari})).first()
    hasil: datetime | None = b.deletion_scheduled_at if b else None
    return hasil


async def batalkan_hapus(conn: AsyncConnection, user_id: UUID) -> bool:
    """`True` bila akun yang `pending_deletion` DAN masih dalam tenggang dikembalikan `active`."""
    b = (await conn.execute(_BATALKAN_HAPUS, {"id": user_id})).first()
    return b is not None


async def status_akun(conn: AsyncConnection, user_id: UUID) -> str | None:
    """Status akun sendiri (RLS own-row); `None` bila barisnya tidak terlihat."""
    b = (await conn.execute(_STATUS_AKUN, {"id": user_id})).first()
    status: str | None = b.status if b else None
    return status


# ── Sapuan hapus akun, tahap 3–6 (6.5 Stage B) ──
# Tiga fungsi `SECURITY DEFINER` spec/01 §12, hanya untuk `hvx_pekerja` — dipanggil dari
# transaksi sistem proses pekerja. Tahap 4 (Qdrant) berjalan DI ANTARA kunci dan hapus.


@dataclass(frozen=True)
class AkunJatuhTempo:
    user_id: UUID
    punya_titik: bool  # ada memori yang pernah disemat ke Qdrant


_AKUN_JATUH_TEMPO = text("SELECT user_id, punya_titik FROM akun_jatuh_tempo(:batas)")
_KUNCI_JATUH_TEMPO = text("SELECT kunci_akun_jatuh_tempo(:id) AS terkunci")
_HAPUS_JATUH_TEMPO = text("SELECT hapus_akun_jatuh_tempo(:id, :semu) AS terhapus")


async def akun_jatuh_tempo(conn: AsyncConnection, batas: int) -> list[AkunJatuhTempo]:
    baris = (await conn.execute(_AKUN_JATUH_TEMPO, {"batas": batas})).all()
    return [AkunJatuhTempo(b.user_id, b.punya_titik) for b in baris]


async def kunci_akun_jatuh_tempo(conn: AsyncConnection, user_id: UUID) -> bool:
    """Kunci baris akun sampai transaksi selesai; `False` bila sudah bukan jatuh tempo."""
    b = (await conn.execute(_KUNCI_JATUH_TEMPO, {"id": user_id})).one()
    return bool(b.terkunci)


async def hapus_akun_jatuh_tempo(conn: AsyncConnection, user_id: UUID, semu: UUID) -> bool:
    """Tahap 5 · 3 · 6; `False` bila akunnya sudah bukan jatuh tempo (tidak ada yang berubah)."""
    b = (await conn.execute(_HAPUS_JATUH_TEMPO, {"id": user_id, "semu": semu})).one()
    return bool(b.terhapus)
