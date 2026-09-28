"""Alur konfirmasi — spec/07 4.5: *risk 2 minta izin sekali; risk 3 minta setiap kali*.

Pemanggilan yang ditahan gerbang tidak disimpan di mana pun: yang disimpan hanya
bahwa sebuah run MENUNGGU (`agent_runs.status = 'blocked'`). Yang dikirim ke
pengguna adalah `PermintaanKonfirmasi` bertanda tangan (HMAC berlabel, kunci
`HVX_IP_HASH_KEY` — `platform.sidik`): siapa, agent mana, tool apa, risiko, scope,
dan SIDIK masukannya — bukan masukannya. Tulisan pengguna (isi memori, pesan untuk
agent lain) tidak masuk token, tidak masuk jejak audit, dan tidak masuk Redis.

Menjawab satu permintaan:

* **sekali pakai** — jawabannya menandai run yang ditahan (`confirmed_by_user`,
  hanya bila masih `NULL`); jawaban kedua `409`;
* **`izinkan_selalu`** — hanya untuk permintaan **izin** (R ≤ 2): keputusan
  `allow` disimpan mesin izin per scope, jadi pemanggilan berikutnya tidak
  ditanyakan lagi — *minta izin sekali*;
* **`izinkan_sekali`** — persetujuan untuk pemanggilan yang SAMA (agent, tool,
  sidik masukan) pada giliran yang diulang; satu-satunya jawaban untuk
  **konfirmasi** R3 — *minta setiap kali*;
* **`tolak`** — tercatat, tidak ada yang dijalankan.

Giliran yang disetujui dijalankan ULANG dari awal dengan persetujuan itu: gerbang
meloloskan pemanggilan yang sidiknya sama, dan hanya itu. Program yang pada
ulangannya memanggil sesuatu yang lain ditanyakan lagi — persetujuan tidak bisa
dipindahkan ke aksi yang tidak dilihat pengguna.

🔧 **Satu giliran bisa ditanya lebih dari sekali** (E-199, tinjauan kontrak Sprint 4):
*“tanya aku”* untuk bacaan habit-agent, lalu `habit.complete` R2. Token karena itu
membawa **pesan pengguna yang memulai giliran** (`pesan_id` — run ulangan tidak punya
pesannya sendiri) dan **persetujuan yang sudah dipegang giliran itu**: jawaban kedua
mengulang giliran dengan KEDUANYA. Dulu token kedua ditolak `422` (pesannya dicari di
run akar ulangan, yang tidak punya pesan), dan persetujuan pertama hilang di ulangan
berikutnya — `izinkan_sekali` menanyakan hal yang sama tanpa akhir.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast
from uuid import UUID

from hvx.modules import identity

from . import repository

JenisKonfirmasi = Literal["izin", "konfirmasi"]
JawabanKonfirmasi = Literal["izinkan_selalu", "izinkan_sekali", "tolak"]
UMUR_TOKEN_S = 900  # 15 menit — lebih lama dari itu, pengguna menjawab keadaan yang sudah lewat


class KonfirmasiTidakSah(ValueError):
    """Token rusak, kedaluwarsa, milik pengguna lain, atau jawabannya tidak boleh."""


class KonfirmasiTerjawab(RuntimeError):
    """Permintaan ini sudah dijawab — sekali pakai."""


def sidik_masukan(alat: str, masukan: Mapping[str, Any]) -> str:
    """Sidik satu pemanggilan — masukan bersih (uuid, tanggal) dalam bentuk kanonik."""
    kanonik = json.dumps(
        {"alat": alat, "masukan": masukan}, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(kanonik.encode()).hexdigest()


@dataclass(frozen=True)
class PersetujuanAksi:
    """Pengguna menyetujui pemanggilan INI — hanya berlaku untuk sidik yang sama."""

    agent: str
    alat: str
    sidik: str


@dataclass(frozen=True)
class PermintaanKonfirmasi:
    """Pemanggilan yang menunggu manusia. `token` dikirim balik bersama jawabannya."""

    jenis: JenisKonfirmasi
    user_id: UUID
    run_id: UUID  # run yang ditahan gerbang — satu-satunya yang menyimpan jawabannya
    agent: str
    alat: str
    risk_level: int
    scopes: tuple[str, ...]
    aksi: identity.Aksi
    sidik: str
    kedaluwarsa: int  # detik epoch
    # Pesan pengguna yang memulai giliran ini — yang diulang bila disetujui (E-199).
    pesan_id: UUID | None = None
    # Persetujuan yang sudah dipegang giliran ini; diulang bersama jawaban ini (E-199).
    persetujuan_lalu: tuple[PersetujuanAksi, ...] = ()
    token: str = ""

    def persetujuan(self) -> PersetujuanAksi:
        return PersetujuanAksi(self.agent, self.alat, self.sidik)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(teks: str) -> bytes:
    return base64.urlsafe_b64decode(teks + "=" * (-len(teks) % 4))


class TokenKonfirmasi:
    """Tanda tangan permintaan konfirmasi — `penanda(isi) -> hex` = HMAC berlabel."""

    def __init__(self, penanda: Callable[[str], str], umur_s: int = UMUR_TOKEN_S) -> None:
        self._penanda = penanda
        self._umur_s = umur_s

    def buat(
        self,
        *,
        jenis: JenisKonfirmasi,
        user_id: UUID,
        run_id: UUID,
        agent: str,
        alat: str,
        risk_level: int,
        scopes: tuple[str, ...],
        aksi: identity.Aksi,
        sidik: str,
        pesan_id: UUID | None = None,
        persetujuan_lalu: frozenset[PersetujuanAksi] = frozenset(),
    ) -> PermintaanKonfirmasi:
        lalu = tuple(sorted(persetujuan_lalu, key=lambda x: (x.agent, x.alat, x.sidik)))
        p = PermintaanKonfirmasi(
            jenis, user_id, run_id, agent, alat, risk_level, scopes, aksi, sidik,
            int(time.time()) + self._umur_s, pesan_id, lalu,
        )  # fmt: skip
        isi = json.dumps(
            {
                "j": p.jenis,
                "u": str(p.user_id),
                "r": str(p.run_id),
                "a": p.agent,
                "t": p.alat,
                "k": p.risk_level,
                "s": list(p.scopes),
                "x": p.aksi,
                "h": p.sidik,
                "e": p.kedaluwarsa,
                "m": None if p.pesan_id is None else str(p.pesan_id),
                "p": [[x.agent, x.alat, x.sidik] for x in p.persetujuan_lalu],
            },
            separators=(",", ":"),
        )
        token = f"{_b64(isi.encode())}.{self._penanda(isi)}"
        return PermintaanKonfirmasi(**{**p.__dict__, "token": token})

    def baca(self, token: str, user_id: UUID) -> PermintaanKonfirmasi:
        try:
            bagian_isi, tanda = token.split(".", 1)
            isi = _unb64(bagian_isi).decode()
        except (ValueError, UnicodeDecodeError):
            raise KonfirmasiTidakSah("token konfirmasi rusak") from None
        # Dibandingkan sebagai BYTE: `compare_digest` atas `str` ber-non-ASCII melempar
        # TypeError — token rusak menjadi 500, bukan 422 (tinjauan keamanan Sprint 4).
        if not hmac.compare_digest(self._penanda(isi).encode(), tanda.encode()):
            raise KonfirmasiTidakSah("token konfirmasi rusak")
        d = json.loads(isi)
        if d["u"] != str(user_id):
            raise KonfirmasiTidakSah("token konfirmasi milik pengguna lain")
        if d["e"] < time.time():
            raise KonfirmasiTidakSah("token konfirmasi kedaluwarsa")
        return PermintaanKonfirmasi(
            d["j"], user_id, UUID(d["r"]), d["a"], d["t"], d["k"], tuple(d["s"]),
            cast(identity.Aksi, d["x"]),
            d["h"], d["e"],
            None if d["m"] is None else UUID(d["m"]),
            tuple(PersetujuanAksi(*x) for x in d["p"]),
            token,
        )  # fmt: skip


async def jawab_konfirmasi(
    mesin_izin: identity.MesinIzin,
    tanda: TokenKonfirmasi,
    user_id: UUID,
    token: str,
    jawaban: JawabanKonfirmasi,
) -> PersetujuanAksi | None:
    """Catat jawaban pengguna — sekali. Persetujuan untuk giliran yang diulang, atau None.

    `izinkan_selalu` menyimpan izinnya di transaksi YANG SAMA dengan jawabannya: token
    yang terpakai tanpa izin tersimpan — atau izin tersimpan dari jawaban yang ditolak
    karena sudah dijawab — tidak bisa terjadi.
    """
    p = tanda.baca(token, user_id)
    periksa_jawaban(p, jawaban)
    setuju = jawaban != "tolak"
    async with mesin_izin.ubah(user_id) as u:
        if not await repository.jawab_run(u.conn, p.run_id, setuju):
            raise KonfirmasiTerjawab("permintaan ini sudah dijawab")
        await identity.audit(
            u.conn,
            aksi="agent.action_approved" if setuju else "agent.action_rejected",
            aktor_tipe="user",
            aktor_id=str(user_id),
            user_id=user_id,
            subjek_tipe="tool",
            subjek_id=p.alat,
            metadata={
                "agent": p.agent,
                "risk": p.risk_level,
                "jenis": p.jenis,
                "jawaban": jawaban,
                "run": str(p.run_id),
            },
        )
        if jawaban == "izinkan_selalu":
            subjek = identity.Subjek("agent", p.agent)
            for scope in p.scopes:
                await u.tetapkan(subjek, scope, p.aksi, "allow")
    return p.persetujuan() if setuju else None


def periksa_jawaban(p: PermintaanKonfirmasi, jawaban: JawabanKonfirmasi) -> None:
    """Jawaban yang tidak boleh untuk permintaan ini — diperiksa SEBELUM apa pun dicatat."""
    if jawaban == "izinkan_selalu" and p.jenis != "izin":
        # R3: *minta setiap kali* — persetujuan tidak bisa menjadi izin yang diingat.
        raise KonfirmasiTidakSah("konfirmasi risiko 3 tidak bisa diingat")
