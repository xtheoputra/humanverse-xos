"""Privacy Center — spec/07 6.4, naskah 5 §26: *apa yang diketahui sistem*, izin per agent,
ekspor, hapus. Keputusan bentuknya: **K-41 · K-42 · K-43** (docs/KEPUTUSAN-DIDELEGASIKAN.md).

`identity` menjadi rumahnya karena izin, persetujuan, dan jejak audit miliknya — tetapi data
yang diringkas, diekspor, dan dihapus milik SEMUA modul, dan modul domain tidak saling impor
(spec/06 aturan 3). Jadi tiap modul menyatakan bagiannya sendiri:

* **`BagianData`** — satu tabel milik pengguna: dihitung (ringkasan) dan diekspor, dengan SQL
  modul pemiliknya (spec/06 aturan 5). Tiap tabel ber-`user_id` di spec/01 muncul **tepat
  sekali** (`tests/unit/test_cakupan_privasi.py`): tabel baru yang lupa dinyatakan tidak
  terlihat di layar ini — dan uji itu merah.
* **`Penghapus`** — satu langkah hapus untuk satu kategori. Kategori yang dihapus membawa
  **turunannya** (naskah 11 §7.25 *Deletion Engine*: event, memori → vektor Qdrant, human
  state, rekomendasi): modul yang MENURUNKAN sesuatu menyatakan penghapus turunan untuk
  kategori sumbernya. Turunan dijalankan SESUDAH sumbernya — menghapus baris sumber
  menunggu kunci yang dipegang ekstraksi yang sedang berjalan (K-27), jadi memori yang
  baru diekstraknya ikut terlihat dan ikut dilupakan.

`hvx.main` merakit keduanya di `app.state` (K-23) — `identity` tidak mengimpor satu modul
domain pun.

🔒 Tiga hal yang tidak boleh terjadi, dan penjaganya:

* **Ekspor dan hapus tanpa sandi ulang** (OWASP ASVS 4.0.3 V3.7.1) — token yang dicuri
  tidak boleh cukup untuk menyalin atau memusnahkan seluruh hidup seseorang. Tebakan sandi
  lewat pintu ini dihitung bersama tebakan login (`PenjagaGagalMasuk`).
* **Rahasia di URL** (ASVS V8.3.1) — tautan unduh tidak membawa token; unduhan butuh sesi
  pemiliknya DAN catatan ekspor yang belum dipakai, sekali pakai (satu skrip Lua).
* **Salinan data yang menginap** — ekspor DIBANGUN saat diunduh dari PostgreSQL, di bawah
  RLS, dalam satu potret (`REPEATABLE READ`). Redis hanya menyimpan status, tidak pernah isi
  (prinsip E-171).
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from types import MappingProxyType
from typing import Any, cast
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from hvx.modules import platform

from .audit import audit
from .izin import Aksi, Keputusan, MesinIzin, Subjek
from .scope import SCOPE_RESMI

Hitung = Callable[[AsyncConnection, UUID], Awaitable[int]]
Ekspor = Callable[[AsyncConnection, UUID], Awaitable[list[dict[str, Any]]]]
Hapus = Callable[[AsyncConnection, UUID], Awaitable[int]]


@dataclass(frozen=True)
class Kategori:
    """Satu baris layar Privacy Center (naskah 5 §26: *Profile ✓ · Goals ✓ · Journal ✓ …*)."""

    label: str
    retensi: str  # berapa lama disimpan, dalam kalimat untuk pengguna (GDPR Art. 13(2)(a))
    # None = bisa dihapus di sini; teks = kenapa tidak, dan jalannya (mis. hapus akun)
    tidak_bisa_dihapus: str | None = None


_SAMPAI_DIHAPUS = "Sampai kamu menghapusnya di sini, atau menghapus akun."

KATEGORI: Mapping[str, Kategori] = MappingProxyType(
    {
        "account": Kategori(
            "Akun, persetujuan & izin",
            "Sampai akun dihapus. Riwayat persetujuan disimpan utuh sebagai bukti apa yang "
            "kamu setujui dan kapan.",
            "Dihapus bersama akun (Hapus akun). Izin agent bisa diubah di bagian Izin.",
        ),
        "profile": Kategori(
            "Profil",
            "Sampai akun dihapus.",
            "Ubah lewat Profil; dihapus bersama akun.",
        ),
        "goals": Kategori("Goal", _SAMPAI_DIHAPUS),
        "habits": Kategori("Habit", _SAMPAI_DIHAPUS),
        "checkins": Kategori("Check-in harian (energi, fokus, tidur)", _SAMPAI_DIHAPUS),
        "moods": Kategori("Mood", _SAMPAI_DIHAPUS),
        "journal": Kategori("Jurnal", _SAMPAI_DIHAPUS),
        "activities": Kategori("Aktivitas", _SAMPAI_DIHAPUS),
        "memories": Kategori(
            "Ingatan asisten",
            "Sampai kamu menghapusnya, sumbernya dihapus, atau akun dihapus.",
        ),
        "conversations": Kategori("Percakapan dengan asisten", _SAMPAI_DIHAPUS),
        "recommendations": Kategori("Rekomendasi", _SAMPAI_DIHAPUS),
        "history": Kategori(
            "Riwayat kejadian",
            "Sampai kamu menghapusnya, sumbernya dihapus, atau akun dihapus.",
        ),
        "audit": Kategori(
            "Jejak audit & jejak kerja asisten",
            "Selama layanan berjalan. Saat akun dihapus, jejak ini dianonimkan (id semu, "
            "tanpa jejak jaringan).",
            "Jejak bahwa sesuatu terjadi — tanpa isinya — adalah bukti bagimu dan bagi kami "
            "(termasuk bukti bahwa penghapusan dijalankan).",
        ),
    }
)

# Yang naskah 5 §26 tampilkan dengan ○ — V0 tidak mengumpulkannya sama sekali. Ditampilkan
# supaya *“apa yang kamu tahu tentang saya”* juga menjawab apa yang TIDAK diketahui.
TIDAK_DIKUMPULKAN: Mapping[str, str] = MappingProxyType(
    {
        "location": "Lokasi",
        "calendar": "Kalender",
        "finance": "Data keuangan",
        "wearable": "Data perangkat kesehatan (wearable)",
    }
)


@dataclass(frozen=True)
class BagianData:
    """Satu tabel milik pengguna — dihitung dan diekspor oleh modul pemiliknya."""

    kategori: str
    tabel: str
    hitung: Hitung
    ekspor: Ekspor
    # Disimpulkan/dihitung sistem, bukan dicatat pengguna — dihitung terpisah di ringkasan.
    turunan: bool = False


@dataclass(frozen=True)
class Penghapus:
    """Satu langkah hapus kategori `kategori` atas `tabel` — mengembalikan banyak baris."""

    kategori: str
    tabel: str
    hapus: Hapus
    # Turunan dijalankan SESUDAH semua langkah sumber kategori itu (docstring modul).
    turunan: bool = False


@dataclass(frozen=True)
class IzinDiminta:
    """Satu (scope, aksi) yang diminta agent lewat tool-nya — dari registry `agents` (K-23)."""

    agent: str
    tujuan: tuple[str, ...]
    scope: str
    aksi: Aksi
    bawaan: Keputusan  # keputusan bila pengguna belum pernah memutuskan
    konfirmasi_tiap_kali: bool  # R3: tetap ditanya walau `allow` (H-15)


# ── bagian milik `identity` sendiri ──────────────────────────────────────────


def _baris(hasil: Iterable[Any]) -> list[dict[str, Any]]:
    return [dict(b) for b in hasil]


_HITUNG_USERS = text("SELECT count(*) FROM users WHERE id = :u")
# Tanpa `password_hash` — selamanya (bentuk `PenggunaRingkas`).
_EKSPOR_USERS = text(
    """
    SELECT id, email, status, email_verified_at, last_login_at, created_at, updated_at,
           deleted_at, deletion_scheduled_at
    FROM users WHERE id = :u
    """
)
_HITUNG_CONSENTS = text("SELECT count(*) FROM consents WHERE user_id = :u")
_EKSPOR_CONSENTS = text("SELECT * FROM consents WHERE user_id = :u ORDER BY created_at, id")
_HITUNG_PERMISSIONS = text("SELECT count(*) FROM permissions WHERE user_id = :u")
_EKSPOR_PERMISSIONS = text(
    "SELECT * FROM permissions WHERE user_id = :u ORDER BY subject_id, scope, action"
)
_HITUNG_AUDIT = text("SELECT count(*) FROM audit_logs WHERE user_id = :u")
_EKSPOR_AUDIT = text("SELECT * FROM audit_logs WHERE user_id = :u ORDER BY occurred_at, id")


def _penghitung(kueri: Any) -> Hitung:
    async def hitung(conn: AsyncConnection, user_id: UUID) -> int:
        return int((await conn.execute(kueri, {"u": user_id})).scalar_one())

    return hitung


def _pengekspor(kueri: Any) -> Ekspor:
    async def ekspor(conn: AsyncConnection, user_id: UUID) -> list[dict[str, Any]]:
        return _baris((await conn.execute(kueri, {"u": user_id})).mappings())

    return ekspor


def bagian_sql(
    kategori: str, tabel: str, hitung: str, ekspor: str, *, turunan: bool = False
) -> BagianData:
    """`BagianData` dari dua kueri ber-parameter `:u` (id pengguna) — SQL-nya ditulis di
    modul PEMILIK tabel, jadi aturan 5 spec/06 (`test_batas_tabel`) tetap membacanya di sana."""
    return BagianData(
        kategori, tabel, _penghitung(text(hitung)), _pengekspor(text(ekspor)), turunan
    )


def penghapus_sql(
    kategori: str,
    tabel: str,
    hapus: str,
    *,
    turunan: bool = False,
    parameter: Mapping[str, Any] | None = None,
) -> Penghapus:
    """`Penghapus` dari satu pernyataan ber-parameter `:u` (+ `parameter` tetap); jumlahnya =
    baris yang terkena.

    Pernyataan yang MENGEMBALIKAN jumlah (`SELECT fungsi(...)`) dibaca nilainya — fungsi
    `SECURITY DEFINER` tidak punya `rowcount`."""
    kueri = text(hapus)
    mengembalikan = hapus.lstrip().upper().startswith("SELECT")
    tetap = dict(parameter or {})

    async def jalankan(conn: AsyncConnection, user_id: UUID) -> int:
        hasil = await conn.execute(kueri, {**tetap, "u": user_id})
        return int(hasil.scalar_one()) if mengembalikan else int(hasil.rowcount)

    return Penghapus(kategori, tabel, jalankan, turunan)


BAGIAN_PRIVASI: tuple[BagianData, ...] = (
    BagianData("account", "users", _penghitung(_HITUNG_USERS), _pengekspor(_EKSPOR_USERS)),
    BagianData("account", "consents", _penghitung(_HITUNG_CONSENTS), _pengekspor(_EKSPOR_CONSENTS)),
    BagianData(
        "account",
        "permissions",
        _penghitung(_HITUNG_PERMISSIONS),
        _pengekspor(_EKSPOR_PERMISSIONS),
    ),
    BagianData("audit", "audit_logs", _penghitung(_HITUNG_AUDIT), _pengekspor(_EKSPOR_AUDIT)),
)


# ── ringkasan ────────────────────────────────────────────────────────────────


async def ringkasan(
    engine: AsyncEngine, user_id: UUID, bagian: Sequence[BagianData], penghapus: Sequence[Penghapus]
) -> dict[str, Any]:
    """Per kategori: berapa baris yang kamu catat, berapa yang sistem turunkan, per tabel.

    Jumlah, BUKAN isi (spec/04): layar ini menjawab *“apa yang kamu tahu tentang saya”*
    tanpa menumpahkan seluruh data ke layar. Baris yang diarsipkan (`deleted_at`) ikut
    dihitung — masih tersimpan, jadi masih diketahui.
    """
    bisa_dihapus = {p.kategori for p in penghapus if not p.turunan}
    hasil: dict[str, dict[str, Any]] = {}
    async with platform.transaksi_pengguna(engine, user_id, satu_potret=True) as conn:
        for b in bagian:
            n = await b.hitung(conn, user_id)
            k = hasil.setdefault(b.kategori, {"count": 0, "derived_count": 0, "tables": {}})
            k["tables"][b.tabel] = k["tables"].get(b.tabel, 0) + n
            k["derived_count" if b.turunan else "count"] += n
    return {
        "categories": [
            {
                "key": kunci,
                "label": kat.label,
                **hasil.get(kunci, {"count": 0, "derived_count": 0, "tables": {}}),
                "deletable": kunci in bisa_dihapus and kat.tidak_bisa_dihapus is None,
                "retention": kat.retensi,
                "why_not_deletable": kat.tidak_bisa_dihapus,
            }
            for kunci, kat in KATEGORI.items()
        ],
        "not_collected": [{"key": k, "label": v} for k, v in TIDAK_DIKUMPULKAN.items()],
    }


# ── izin per agent ───────────────────────────────────────────────────────────

_IZIN_AGENT = text(
    """
    SELECT subject_id, scope, action, decision, expires_at,
           (expires_at IS NOT NULL AND expires_at <= clock_timestamp()) AS habis
    FROM permissions
    WHERE user_id = :u AND subject_type = 'agent'
    """
)


def _bawaan(diminta: IzinDiminta) -> Keputusan:
    # Scope sensitif tidak pernah `allow` karena bawaan — aturan `MesinIzin.cek` (E-180).
    return (
        "ask"
        if diminta.bawaan == "allow" and SCOPE_RESMI[diminta.scope].sensitif
        else (diminta.bawaan)
    )


async def izin_per_agent(
    engine: AsyncEngine, user_id: UUID, katalog: Sequence[IzinDiminta]
) -> dict[str, Any]:
    """Tiap agent aktif dan tiap (scope, aksi) yang dimintanya: keputusan yang BERLAKU.

    `source: "user"` = keputusan yang kamu simpan (belum kedaluwarsa); `"default"` = bawaan
    gerbang risiko (R0·R1 `allow`, R2 ke atas `ask`, scope sensitif selalu `ask`).
    """
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        tersimpan = {
            (b.subject_id, b.scope, b.action): b
            for b in (await conn.execute(_IZIN_AGENT, {"u": user_id})).all()
            if not b.habis
        }
    agen: dict[str, dict[str, Any]] = {}
    for d in katalog:
        a = agen.setdefault(
            d.agent,
            {"subject_type": "agent", "subject_id": d.agent, "purpose": list(d.tujuan),
             "permissions": []},
        )  # fmt: skip
        b = tersimpan.get((d.agent, d.scope, d.aksi))
        a["permissions"].append(
            {
                "scope": d.scope,
                "action": d.aksi,
                "decision": b.decision if b else _bawaan(d),
                "source": "user" if b else "default",
                "expires_at": b.expires_at if b else None,
                "sensitive": SCOPE_RESMI[d.scope].sensitif,
                "confirm_each_time": d.konfirmasi_tiap_kali,
            }
        )
    return {"agents": list(agen.values())}


async def tetapkan_izin(
    mesin: MesinIzin,
    user_id: UUID,
    katalog: Sequence[IzinDiminta],
    *,
    subjek_tipe: str,
    subjek_id: str,
    scope: str,
    aksi: str,
    keputusan: Keputusan,
    expires_at: datetime | None,
    ip_hash: str | None,
) -> None:
    """Simpan keputusan atas (agent, scope, aksi) yang SUNGGUH diminta agent itu.

    Yang tidak diminta siapa pun ditolak (`404`), bukan disimpan sebagai baris yang tak
    pernah ditanyakan — prinsip yang sama dengan scope di luar daftar resmi (`izin.py`).
    """
    diminta = any(
        subjek_tipe == "agent" and d.agent == subjek_id and d.scope == scope and d.aksi == aksi
        for d in katalog
    )
    if not diminta:
        raise platform.GalatApi(
            404, "permission_not_requested", "Izin itu tidak diminta agent mana pun."
        )
    await mesin.tetapkan(
        user_id,
        Subjek("agent", subjek_id),
        scope,
        cast(Aksi, aksi),  # sudah dicocokkan dengan katalog — aksi agent yang sah
        keputusan,
        expires_at=expires_at,
        ip_hash=ip_hash,
    )


# ── ekspor (K-43) ────────────────────────────────────────────────────────────

FORMAT_EKSPOR = "humanverse-export"
VERSI_EKSPOR = 1
UMUR_EKSPOR_S = 3_600  # tautan berlaku satu jam — cukup untuk mengunduh, tidak untuk menginap
BATAS_EKSPOR = platform.BatasLaju("ekspor-privasi", 5, 3_600)  # per pengguna per jam

_SIAP = "ready"
_DIUNDUH = "downloaded"

# Sekali pakai, atomik: hanya catatan yang masih `ready` berpindah ke `downloaded` (umurnya
# tetap). 1 = boleh diunduh · 2 = sudah diunduh · 0 = tidak ada / kedaluwarsa.
_AMBIL_SEKALI = """
local s = redis.call('GET', KEYS[1])
if not s then
  return 0
end
if s ~= ARGV[1] then
  return 2
end
redis.call('SET', KEYS[1], ARGV[2], 'KEEPTTL')
return 1
"""
# Pembangunan ekspor gagal sesudah catatannya diambil: kembalikan — tanpa ini galat sesaat
# membakar tautan sekali pakai pemiliknya.
_KEMBALIKAN = """
if redis.call('GET', KEYS[1]) == ARGV[2] then
  redis.call('SET', KEYS[1], ARGV[1], 'KEEPTTL')
  return 1
end
return 0
"""


def _k_ekspor(awalan: str, user_id: UUID, ekspor_id: UUID) -> str:
    # `user_id` di nama kunci: id ekspor milik A tidak pernah terbaca untuk B (H-27).
    return f"{awalan}:ekspor:{user_id}:{ekspor_id}"


def _galat_ekspor_tidak_ada() -> platform.GalatApi:
    return platform.GalatApi(404, "export_not_found", "Ekspor tidak ditemukan atau kedaluwarsa.")


async def minta_ekspor(
    engine: AsyncEngine,
    redis: Redis,
    awalan: str,
    user_id: UUID,
    *,
    ip_hash: str | None,
) -> dict[str, Any]:
    """Catat permintaan ekspor (status `ready`) — sandi sudah diverifikasi pemanggil."""
    ekspor_id = uuid.uuid4()
    await redis.set(_k_ekspor(awalan, user_id, ekspor_id), _SIAP, ex=UMUR_EKSPOR_S)
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        await audit(
            conn,
            aksi="data.export_requested",
            aktor_tipe="user",
            aktor_id=str(user_id),
            user_id=user_id,
            subjek_tipe="export",
            subjek_id=str(ekspor_id),
            ip_hash=ip_hash,
        )
    # `ready` tanpa `download_url` (versi pertama) memaksa klien menyusun jalurnya sendiri —
    # bentuknya kini sama dengan `status_ekspor` untuk status yang sama.
    return {
        "export_id": ekspor_id,
        "status": _SIAP,
        "expires_at": datetime.now(UTC) + timedelta(seconds=UMUR_EKSPOR_S),
        "download_url": _jalur_unduh(ekspor_id),
    }


async def status_ekspor(
    redis: Redis, awalan: str, user_id: UUID, ekspor_id: UUID
) -> dict[str, Any]:
    kunci = _k_ekspor(awalan, user_id, ekspor_id)
    async with redis.pipeline(transaction=True) as p:
        p.get(kunci)
        p.pttl(kunci)
        status, sisa_ms = await p.execute()
    if status is None or sisa_ms is None or sisa_ms < 0:
        raise _galat_ekspor_tidak_ada()
    hasil: dict[str, Any] = {
        "export_id": ekspor_id,
        "status": status,
        "expires_at": datetime.now(UTC) + timedelta(milliseconds=int(sisa_ms)),
        "download_url": None,
    }
    if status == _SIAP:
        hasil["download_url"] = _jalur_unduh(ekspor_id)
    return hasil


def _jalur_unduh(ekspor_id: UUID) -> str:
    """Jalur tanpa rahasia (ASVS V8.3.1) — pengunduhnya tetap butuh token akses."""
    return f"/v1/privacy/export/{ekspor_id}/download"


async def unduh_ekspor(
    engine: AsyncEngine,
    redis: Redis,
    awalan: str,
    user_id: UUID,
    ekspor_id: UUID,
    bagian: Sequence[BagianData],
    *,
    ip_hash: str | None,
) -> dict[str, Any]:
    """Salinan data pengguna, mesin-terbaca (GDPR Art. 15 · 20; UU PDP Pasal 7 · 13).

    Sekali pakai: yang kedua `410`. Dibangun dari satu potret basis data, dan jejak
    `data.exported` ditulis di transaksi yang sama dengan bacaannya.
    """
    kunci = _k_ekspor(awalan, user_id, ekspor_id)
    hasil = await redis.register_script(_AMBIL_SEKALI)(keys=[kunci], args=[_SIAP, _DIUNDUH])
    if int(hasil) == 0:
        raise _galat_ekspor_tidak_ada()
    if int(hasil) == 2:
        raise platform.GalatApi(
            410, "export_already_downloaded", "Ekspor ini sudah diunduh. Minta ekspor baru."
        )
    try:
        kategori: dict[str, dict[str, list[dict[str, Any]]]] = {}
        async with platform.transaksi_pengguna(engine, user_id, satu_potret=True) as conn:
            waktu = (await conn.execute(text("SELECT now()"))).scalar_one()
            jumlah = 0
            for b in bagian:
                baris = await b.ekspor(conn, user_id)
                kategori.setdefault(b.kategori, {}).setdefault(b.tabel, []).extend(baris)
                jumlah += len(baris)
            await audit(
                conn,
                aksi="data.exported",
                aktor_tipe="user",
                aktor_id=str(user_id),
                user_id=user_id,
                subjek_tipe="export",
                subjek_id=str(ekspor_id),
                ip_hash=ip_hash,
                metadata={"rows": jumlah},
            )
    except BaseException:
        await redis.register_script(_KEMBALIKAN)(keys=[kunci], args=[_SIAP, _DIUNDUH])
        raise
    dokumen: dict[str, Any] = jsonable_encoder(
        {
            "format": FORMAT_EKSPOR,
            "format_version": VERSI_EKSPOR,
            "exported_at": waktu,
            "user_id": user_id,
            "categories": kategori,
        }
    )
    return dokumen


# ── hapus per kategori (K-42) ────────────────────────────────────────────────


def periksa_kategori_bisa_dihapus(kategori: str, penghapus: Sequence[Penghapus]) -> None:
    kat = KATEGORI.get(kategori)
    if kat is None:
        raise platform.GalatApi(404, "unknown_category", "Kategori data tidak dikenal.")
    if kat.tidak_bisa_dihapus is not None or not any(
        p.kategori == kategori and not p.turunan for p in penghapus
    ):
        raise platform.GalatApi(
            409, "category_not_deletable", "Kategori ini tidak bisa dihapus di sini."
        )


async def hapus_kategori(
    engine: AsyncEngine,
    user_id: UUID,
    kategori: str,
    penghapus: Sequence[Penghapus],
    *,
    ip_hash: str | None,
) -> dict[str, int]:
    """Hapus satu kategori dan turunannya, SATU transaksi; jejaknya di transaksi yang sama.

    Hapus KERAS — bukan arsip. Titik vektor memori yang dilupakan dibuang penyelaras
    sesudah commit (Qdrant tidak ikut transaksi; spec/01 §12) — itulah kenapa `202`.
    """
    periksa_kategori_bisa_dihapus(kategori, penghapus)
    langkah = [p for p in penghapus if p.kategori == kategori]
    urut = [p for p in langkah if not p.turunan] + [p for p in langkah if p.turunan]
    terhapus: dict[str, int] = {}
    async with platform.transaksi_pengguna(engine, user_id) as conn:
        # Pertama: tunggu konsumen pekerja yang sedang menurunkan data pengguna ini, dan
        # tahan yang berikutnya sampai commit — turunan yang disisipkan di tengah tidak
        # lolos dari penghapus turunan di bawah (tinjauan keamanan S5–6, S3).
        await platform.kunci_turunan(conn, user_id, eksklusif=True)
        for p in urut:
            terhapus[p.tabel] = terhapus.get(p.tabel, 0) + await p.hapus(conn, user_id)
        await audit(
            conn,
            aksi="data.deleted",
            aktor_tipe="user",
            aktor_id=str(user_id),
            user_id=user_id,
            subjek_tipe="category",
            subjek_id=kategori,
            ip_hash=ip_hash,
            metadata={"rows": sum(terhapus.values())},
        )
    return terhapus
