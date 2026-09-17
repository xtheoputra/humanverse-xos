"""Aturan identity — spec/07 tugas 1.1: daftar · masuk · segarkan · keluar.

Selesai bila: argon2id; refresh token berotasi; uji integrasi hijau.

🔑 **Pendaftaran menulis beberapa modul dalam SATU transaksi**: `users` dan
`consents` (milik identity), `profiles` (milik profile), dan `audit_logs`.
`identity` tidak boleh mengimpor `profile` (K-17), jadi profil dibuat oleh
**pendengar pendaftaran** yang dipasang titik rakit `hvx.main` — identity
hanya tahu ada yang mendengar, bukan siapa. Pendengar yang gagal menggagalkan
seluruh pendaftaran: akun tanpa profil tidak pernah tercipta.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from . import repository, sandi
from .audit import audit
from .dependensi import PenggunaMasuk
from .laju import PenjagaGagalMasuk
from .persetujuan import TUJUAN_LAYANAN, TUJUAN_PELATIHAN_MODEL, Persetujuan, catat_persetujuan
from .schemas import PenggunaRingkas, PermintaanDaftar
from .sesi import PenyimpanSesi, SesiAktif, Token


@dataclass(frozen=True)
class PenggunaBaru:
    """Yang diterima pendengar pendaftaran — di dalam transaksi pendaftaran."""

    user_id: UUID
    display_name: str
    timezone: str


PendengarPendaftaran = Callable[[AsyncConnection, PenggunaBaru], Awaitable[None]]


def _galat(status: int, kode: str, pesan: str) -> platform.GalatApi:
    return platform.GalatApi(status, kode, pesan)


async def daftar(
    engine: AsyncEngine,
    sesi: PenyimpanSesi,
    permintaan: PermintaanDaftar,
    *,
    pendengar: Sequence[PendengarPendaftaran],
    ip_hash: str | None,
) -> tuple[PenggunaRingkas, Token]:
    persetujuan = permintaan.consents
    if not (persetujuan.terms and persetujuan.privacy):
        raise _galat(
            422, "consent_required", "Syarat layanan dan kebijakan privasi wajib disetujui."
        )
    kata_sandi = permintaan.password.get_secret_value()
    alasan = sandi.alasan_ditolak(kata_sandi, email=permintaan.email, nama=permintaan.display_name)
    if alasan is not None:  # NIST SP 800-63B-4 §3.1.1.2 — daftar tolak
        raise platform.GalatApi(
            422,
            "password_rejected",
            "Sandi terlalu mudah ditebak. Pilih sandi lain.",
            rincian={"reason": alasan},
        )
    user_id = uuid4()
    hash_ = await sandi.hash_sandi_async(kata_sandi)
    versi = persetujuan.policy_version
    try:
        async with platform.transaksi_pengguna(engine, user_id) as conn:
            await repository.tambah_pengguna(conn, user_id, permintaan.email, hash_)
            for kind in ("terms", "privacy"):
                await catat_persetujuan(
                    conn,
                    user_id,
                    Persetujuan(
                        kind=kind, purpose=TUJUAN_LAYANAN, granted=True, policy_version=versi
                    ),
                    ip_hash=ip_hash,
                )
            latih = persetujuan.model_training
            await catat_persetujuan(
                conn,
                user_id,
                Persetujuan(
                    kind="model_training",
                    purpose=TUJUAN_PELATIHAN_MODEL,
                    granted=latih.granted,
                    policy_version=versi,
                    data_scopes=frozenset(latih.data_scopes),
                ),
                ip_hash=ip_hash,
            )
            baru = PenggunaBaru(user_id, permintaan.display_name, permintaan.timezone)
            for p in pendengar:
                await p(conn, baru)
            await audit(
                conn,
                aksi="account.registered",
                aktor_tipe="user",
                aktor_id=str(user_id),
                user_id=user_id,
                ip_hash=ip_hash,
            )
            akun = await repository.ambil_pengguna(conn, user_id)
    except IntegrityError as galat:
        if "users_email_key" in str(galat.orig):
            raise _galat(409, "email_taken", "Email sudah terdaftar.") from None
        raise
    if akun is None:  # pragma: no cover - baris yang baru ditulis di transaksi yang sama
        raise RuntimeError("akun yang baru didaftarkan tidak terbaca kembali")
    return akun, await sesi.buat(user_id)


async def masuk(
    engine: AsyncEngine,
    sesi: PenyimpanSesi,
    email: str,
    kata_sandi: str,
    *,
    ip_hash: str | None,
    penjaga: PenjagaGagalMasuk,
) -> tuple[PenggunaRingkas, Token]:
    async with platform.transaksi_sistem(engine) as conn:  # pengguna belum dikenali
        dicari = await repository.cari_untuk_masuk(conn, email)
    akun, kunci = dicari.akun, dicari.kunci  # kunci: email sebagaimana citext mengenalinya
    await penjaga.pakai(kunci)  # SEBELUM argon2 — tebakan serentak tidak lolos bersama-sama
    # Satu verifikasi argon2 SELALU dijalankan — juga untuk email tak dikenal.
    cocok = await sandi.cocokkan_async(akun.password_hash if akun else None, kata_sandi)

    if akun is None or not cocok:
        await _catat_gagal(engine, akun.id if akun else None, "kredensial", ip_hash)
        raise _galat(401, "invalid_credentials", "Email atau sandi salah.")
    if akun.status != "active":
        await _catat_gagal(engine, akun.id, akun.status, ip_hash)
        raise _galat(403, "account_not_active", "Akun tidak aktif.")

    async with platform.transaksi_pengguna(engine, akun.id) as conn:
        if sandi.perlu_hash_ulang(akun.password_hash):
            await repository.ganti_hash_sandi(
                conn, akun.id, await sandi.hash_sandi_async(kata_sandi)
            )
        await repository.catat_masuk(conn, akun.id)
        await audit(
            conn,
            aksi="session.login_succeeded",
            aktor_tipe="user",
            aktor_id=str(akun.id),
            user_id=akun.id,
            ip_hash=ip_hash,
        )
        ringkas = await repository.ambil_pengguna(conn, akun.id)
    if ringkas is None:  # pragma: no cover - akun yang baru saja lolos verifikasi
        raise RuntimeError("akun yang baru masuk tidak terbaca kembali")
    await penjaga.berhasil(kunci)  # masuk yang berhasil mengosongkan hitungan gagal akun ini
    return ringkas, await sesi.buat(akun.id)


async def _catat_gagal(
    engine: AsyncEngine, user_id: UUID | None, alasan: str, ip_hash: str | None
) -> None:
    """Akun dikenal → baris milik akun itu; tak dikenal → baris sistem TANPA email.

    Kedua cabang menjalankan kueri yang sama banyak (`transaksi_sistem` berbentuk
    sama dengan `transaksi_pengguna`): waktu jawaban 401 tidak membedakan email
    yang terdaftar dari yang tidak.
    """
    if user_id is None:
        async with platform.transaksi_sistem(engine) as conn:
            await audit(
                conn,
                aksi="session.login_failed",
                aktor_tipe="system",
                aktor_id="auth",
                user_id=None,
                ip_hash=ip_hash,
                metadata={"alasan": "akun_tidak_dikenal"},
            )
        return
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        await audit(
            conn,
            aksi="session.login_failed",
            aktor_tipe="user",
            aktor_id=str(user_id),
            user_id=user_id,
            ip_hash=ip_hash,
            metadata={"alasan": alasan},
        )


async def segarkan(
    engine: AsyncEngine, sesi: PenyimpanSesi, token_segar: str, *, ip_hash: str | None
) -> Token:
    # Status akun dibaca di TIAP penyegaran, SEBELUM token diputar. 🔴 Dua versi
    # yang salah (tinjauan Sprint 1): status hanya dibaca saat login — akun yang
    # ditangguhkan memperpanjang sesinya sendiri tanpa batas; lalu status dibaca
    # SESUDAH rotasi — galat basis data membakar token klien, dan ulangan klien
    # dicatat sebagai pencurian.
    pemilik = await sesi.pemilik_token_segar(token_segar)
    if pemilik is not None and not await _masih_aktif(engine, pemilik, ip_hash=ip_hash):
        # Semua sesi akun itu, bukan hanya yang sedang disegarkan — sesi lain
        # tidak menunggu penyegarannya sendiri untuk berhenti.
        await sesi.cabut_semua(pemilik.user_id)
        raise _galat(401, "invalid_refresh_token", "Token segar tidak sah atau sudah dipakai.")

    hasil = await sesi.segarkan(token_segar)
    if hasil.dipakai_ulang is not None:
        curian = hasil.dipakai_ulang
        async with platform.transaksi_pengguna(engine, curian.user_id) as conn:
            await audit(
                conn,
                aksi="session.refresh_reused",
                aktor_tipe="system",
                aktor_id="auth",
                user_id=curian.user_id,
                subjek_tipe="session",
                subjek_id=str(curian.sesi_id),
                ip_hash=ip_hash,
            )
    if hasil.token is None:
        raise _galat(401, "invalid_refresh_token", "Token segar tidak sah atau sudah dipakai.")
    return hasil.token


async def _masih_aktif(engine: AsyncEngine, pemilik: SesiAktif, *, ip_hash: str | None) -> bool:
    """Akun pemilik sesi masih `active` — kalau tidak, pencabutan sesinya dicatat di sini."""
    async with platform.transaksi_pengguna(engine, pemilik.user_id) as conn:
        akun = await repository.ambil_pengguna(conn, pemilik.user_id)
        aktif = akun is not None and akun.status == "active"
        if not aktif:
            await audit(
                conn,
                aksi="session.revoked",
                aktor_tipe="system",
                aktor_id="auth",
                user_id=pemilik.user_id,
                subjek_tipe="session",
                subjek_id=str(pemilik.sesi_id),
                ip_hash=ip_hash,
                metadata={"alasan": akun.status if akun else "akun_tidak_ada", "semua_sesi": True},
            )
    return aktif


async def keluar(
    engine: AsyncEngine, sesi: PenyimpanSesi, pengguna: PenggunaMasuk, *, ip_hash: str | None
) -> None:
    await sesi.cabut(pengguna.sesi_id)
    async with platform.transaksi_pengguna(engine, pengguna.user_id) as conn:
        await audit(
            conn,
            aksi="session.logged_out",
            aktor_tipe="user",
            aktor_id=str(pengguna.user_id),
            user_id=pengguna.user_id,
            subjek_tipe="session",
            subjek_id=str(pengguna.sesi_id),
            ip_hash=ip_hash,
        )
