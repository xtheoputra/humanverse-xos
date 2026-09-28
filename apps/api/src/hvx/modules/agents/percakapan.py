"""Percakapan — spec/07 4.8: *token mengalir; `done` memuat `cost_usd`*.

Satu giliran = satu pesan pengguna → satu balasan, di satu dari dua jalan:

* **deterministik** (*“catat mood 3”*, 4.1) — dijalankan saat itu juga, tanpa agent,
  tanpa run, dan TANPA model: jalur ini tidak memegang `GerbangModel` sama sekali;
* **agent** — `orchestrator-agent` (4.6) di tugas latar; run akarnya ditulis SEBELUM
  `202` dijawab, jadi `agent_run_id` di jawaban itu sudah sah dirujuk.

Pesan pengguna dan balasannya berbagi run AKAR giliran itu (`ai_messages.agent_run_id`).
Giliran yang ditahan gerbang (4.5) berakhir dengan `confirmation_required` + `done`
berisi pertanyaannya; jawabannya (`POST …/confirmations`) mengulang giliran yang sama
dari pesan penggunanya, dengan persetujuan itu. Tiap giliran berakhir dengan `done`
atau `error` — klien tidak pernah menunggu aliran yang tidak akan selesai.

Permintaan yang DITOLAK sebelum apa pun tercatat — id kembar, token yang sudah dijawab
— bukan giliran: alirannya di-`urungkan` (E-202), dan run yang terlanjur ditulis
ditutup (E-200). `error.code` di SSE adalah kode API berbahasa Inggris (AGENTS.md §7,
E-203), bukan kode internal pelaksana tool.
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4, uuid5

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import identity, platform

from . import repository
from .aliran import AliranPercakapan, Giliran, GiliranBerjalan
from .deterministik import jalankan_deterministik
from .jalannya import Jalannya
from .konfirmasi import (
    JawabanKonfirmasi,
    KonfirmasiTerjawab,
    KonfirmasiTidakSah,
    PermintaanKonfirmasi,
    PersetujuanAksi,
    TokenKonfirmasi,
    jawab_konfirmasi,
)
from .niat import kenali
from .pelaksana_alat import AlatDitolak, AlatGagal
from .runtime import KODE_GERBANG, KeputusanTidakSah, RuntimeAgent
from .schemas import (
    BuatPercakapan,
    HalamanPercakapan,
    HalamanPesan,
    JawabKonfirmasi,
    KirimPesan,
    Percakapan,
    Pesan,
    StatusGiliran,
    TerimaKonfirmasi,
    TerimaPesan,
)

log = structlog.get_logger(__name__)

AGENT_AKAR = "orchestrator-agent"
KEYAKINAN_PASTI = Decimal("1")
# uuid5 mood dari pesan yang memerintahkannya: giliran yang sama tidak mencatatnya dua kali.
RUANG_MOOD_PESAN = UUID("3b1c1f9e-8a4d-4e61-9b7c-2f5d0e6a9c14")
_JAWABAN: Mapping[str, JawabanKonfirmasi] = {
    "allow_always": "izinkan_selalu",
    "allow_once": "izinkan_sekali",
    "reject": "tolak",
}
_ALASAN_DETERMINISTIK = {
    "catat_mood": "Dicatat apa adanya dari perintahmu — tanpa model.",
    "catat_mood_salah": "Angka mood tidak terbaca utuh — tidak ditebak.",
}


def _tidak_ditemukan() -> platform.GalatApi:
    return platform.GalatApi(404, "not_found", "Percakapan tidak ditemukan.")


def _id_kembar(galat: IntegrityError, constraint: str, pesan: str) -> platform.GalatApi | None:
    """Id buatan klien yang sudah ada (spec/04 *klien boleh membuat id sendiri*) → 409,
    sama dengan modul lain — bukan 500 (tinjauan kontrak Sprint 4)."""
    p = platform.rincian_pelanggaran(galat)
    if p.sqlstate == platform.UNIQUE_VIOLATION and p.constraint == constraint:
        return platform.GalatApi(409, "already_exists", pesan)
    return None


def _pesan_kembar() -> platform.GalatApi:
    return platform.GalatApi(409, "already_exists", "Pesan dengan id ini sudah ada.")


def _percakapan(b: repository.BarisPercakapan) -> Percakapan:
    return Percakapan(
        id=b.id,
        title=b.title,
        started_at=b.started_at,
        last_message_at=b.last_message_at,
        message_count=b.message_count,
    )


def _pesan(b: repository.BarisPesan) -> Pesan:
    return Pesan(
        id=b.id,
        role=b.role,  # CHECK spec/01 — hanya empat nilai
        content=b.content,
        agent_run_id=b.agent_run_id,
        confidence=None if b.confidence is None else float(b.confidence),
        rationale=list(b.rationale),
        cost_usd=None if b.cost_usd is None else float(b.cost_usd),
        created_at=b.created_at,
    )


def _done(pesan: repository.BarisPesan) -> dict[str, Any]:
    """SSE `done` (spec/04) — isi yang sama dengan balasan yang TERSIMPAN."""
    return {
        "message_id": str(pesan.id),
        "content": pesan.content,
        "confidence": None if pesan.confidence is None else float(pesan.confidence),
        "rationale": list(pesan.rationale),
        "agent_run_id": None if pesan.agent_run_id is None else str(pesan.agent_run_id),
        "cost_usd": float(pesan.cost_usd or 0),
    }


class LayananPercakapan:
    """Dirakit `hvx.main` (K-23): runtime, aliran, mesin izin, tanda konfirmasi."""

    def __init__(
        self,
        engine: AsyncEngine,
        runtime: RuntimeAgent,
        aliran: AliranPercakapan,
        mesin_izin: identity.MesinIzin,
        tanda: TokenKonfirmasi,
    ) -> None:
        self._engine = engine
        self.runtime = runtime
        self.aliran = aliran
        self._izin = mesin_izin
        self._tanda = tanda
        self._tugas: set[asyncio.Task[None]] = set()

    # ── baca ────────────────────────────────────────────────────────────────
    async def buat(self, user_id: UUID, badan: BuatPercakapan) -> Percakapan:
        try:
            async with platform.transaksi_pengguna(self._engine, user_id) as conn:
                b = await repository.buat_percakapan(
                    conn, id=badan.id or uuid4(), user_id=user_id, title=badan.title
                )
        except IntegrityError as galat:
            kembar = _id_kembar(
                galat, "ai_conversations_pkey", "Percakapan dengan id ini sudah ada."
            )
            if kembar is None:
                raise
            raise kembar from None
        return _percakapan(b)

    async def baca(self, user_id: UUID, percakapan_id: UUID) -> Percakapan | None:
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            b = await repository.baca_percakapan(conn, user_id, percakapan_id)
        return None if b is None else _percakapan(b)

    async def daftar(self, user_id: UUID, *, batas: int, kursor: str | None) -> HalamanPercakapan:
        sesudah = platform.baca_kursor_waktu("conversations", kursor)
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            baris = await repository.daftar_percakapan(
                conn, user_id, batas=batas + 1, sesudah=sesudah
            )
        lanjut = None
        if len(baris) > batas:
            baris = baris[:batas]
            lanjut = platform.kursor_waktu("conversations", baris[-1].created_at, baris[-1].id)
        return HalamanPercakapan(items=[_percakapan(b) for b in baris], next_cursor=lanjut)

    async def pesan(
        self, user_id: UUID, percakapan_id: UUID, *, batas: int, kursor: str | None
    ) -> HalamanPesan:
        sesudah = platform.baca_kursor_waktu(f"messages:{percakapan_id}", kursor)
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            if await repository.baca_percakapan(conn, user_id, percakapan_id) is None:
                raise _tidak_ditemukan()
            baris = await repository.daftar_pesan(
                conn, user_id, percakapan_id, batas=batas + 1, sesudah=sesudah
            )
        lanjut = None
        if len(baris) > batas:
            baris = baris[:batas]
            lanjut = platform.kursor_waktu(
                f"messages:{percakapan_id}", baris[-1].created_at, baris[-1].id
            )
        return HalamanPesan(items=[_pesan(b) for b in baris], next_cursor=lanjut)

    async def baca_terima(self, user_id: UUID, pesan_id: UUID) -> TerimaPesan | None:
        """Jawaban `POST …/messages` dibaca ulang (Idempotency-Key) — keadaannya SAAT INI."""
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            p = await repository.baca_pesan(conn, user_id, pesan_id)
            if p is None or p.role != "user":
                return None
            if p.agent_run_id is None:  # perintah deterministik — dijawab saat itu juga
                return TerimaPesan(message_id=p.id, agent_run_id=None, status="completed")
            run = await repository.baca_run(conn, p.agent_run_id)
            balasan = await repository.pesan_run(conn, user_id, p.agent_run_id, "assistant")
        return TerimaPesan(
            message_id=p.id,
            agent_run_id=p.agent_run_id,
            status=_status_giliran(balasan is not None, run),
        )

    async def baca_terima_konfirmasi(self, user_id: UUID, run_id: UUID) -> TerimaKonfirmasi | None:
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            run = await repository.baca_run(conn, run_id)
            if run is None:
                return None
            balasan = await repository.pesan_run(conn, user_id, run_id, "assistant")
        status = _status_giliran(balasan is not None, run)
        return TerimaKonfirmasi(agent_run_id=run_id, status=status)

    # ── giliran ─────────────────────────────────────────────────────────────
    async def _pastikan_ada(self, user_id: UUID, percakapan_id: UUID) -> None:
        if await self.baca(user_id, percakapan_id) is None:
            raise _tidak_ditemukan()

    def _mulai_giliran(self, percakapan_id: UUID) -> Giliran | None:
        try:
            return self.aliran.mulai(percakapan_id)
        except GiliranBerjalan:
            raise platform.GalatApi(
                409, "turn_in_progress", "Percakapan ini masih menjawab pesan sebelumnya."
            ) from None

    async def kirim(self, user_id: UUID, percakapan_id: UUID, badan: KirimPesan) -> TerimaPesan:
        await self._pastikan_ada(user_id, percakapan_id)
        pesan_id = badan.id or uuid4()
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            if await repository.baca_pesan(conn, user_id, pesan_id) is not None:
                raise _pesan_kembar()  # kiriman ulang klien luring — sebelum run ditulis
        lama = self._mulai_giliran(percakapan_id)
        niat = kenali(badan.content)
        j: Jalannya | None = None
        try:
            if niat.rute == "deterministic":
                await self._simpan(user_id, percakapan_id, pesan_id, "user", badan.content)
            else:
                j = await self.runtime.mulai(
                    user_id,
                    AGENT_AKAR,
                    pemicu="user",
                    percakapan_id=percakapan_id,
                    pesan_id=pesan_id,
                )
                await self._simpan(
                    user_id, percakapan_id, pesan_id, "user", badan.content, agent_run_id=j.id
                )
        except BaseException as galat:
            # Pesannya tidak tercatat: permintaan ini gagal, bukan giliran. Run yang
            # terlanjur ditulis ditutup — tanpa itu ia `running` selamanya (E-200).
            if j is not None:
                await asyncio.shield(self.runtime.gagalkan(j, galat))
            await self.aliran.urungkan(percakapan_id, lama)
            raise
        if j is None:
            try:
                return await self._deterministik(user_id, percakapan_id, pesan_id, badan.content)
            except BaseException as galat:
                await self.aliran.kirim(percakapan_id, "error", {"code": _kode(galat)})
                raise
        self._latar(self._giliran(user_id, percakapan_id, j, badan.content))
        return TerimaPesan(message_id=pesan_id, agent_run_id=j.id, status="processing")

    async def _deterministik(
        self, user_id: UUID, percakapan_id: UUID, pesan_id: UUID, isi: str
    ) -> TerimaPesan:
        """4.1 — `INSERT`, bukan inferensi: tanpa agent, tanpa run, tanpa model."""
        niat = kenali(isi)
        hasil = await jalankan_deterministik(
            self._engine, user_id, niat, mood_id=uuid5(RUANG_MOOD_PESAN, str(pesan_id))
        )
        balasan = await self._simpan(
            user_id,
            percakapan_id,
            uuid4(),
            "assistant",
            hasil.teks,
            cost_usd=Decimal(0),
            confidence=KEYAKINAN_PASTI,
            rationale=(_ALASAN_DETERMINISTIK[niat.jenis],),
        )
        await self.aliran.kirim(percakapan_id, "token", {"text": hasil.teks})
        await self.aliran.kirim(percakapan_id, "done", _done(balasan))
        return TerimaPesan(message_id=pesan_id, agent_run_id=None, status="completed")

    async def _simpan(
        self,
        user_id: UUID,
        percakapan_id: UUID,
        pesan_id: UUID,
        role: str,
        isi: str,
        **kolom: Any,
    ) -> repository.BarisPesan:
        try:
            async with platform.transaksi_pengguna(self._engine, user_id) as conn:
                if not await repository.kunci_percakapan(conn, user_id, percakapan_id):
                    raise _tidak_ditemukan()
                return await repository.sisip_pesan(
                    conn,
                    id=pesan_id,
                    conversation_id=percakapan_id,
                    user_id=user_id,
                    role=role,
                    content=isi,
                    **kolom,
                )
        except IntegrityError as galat:
            kembar = _id_kembar(galat, "ai_messages_pkey", "Pesan dengan id ini sudah ada.")
            if kembar is None:
                raise
            raise kembar from None

    def _latar(self, kerja: Any) -> None:
        tugas: asyncio.Task[None] = asyncio.create_task(kerja)
        self._tugas.add(tugas)
        tugas.add_done_callback(self._tugas.discard)

    async def _giliran(self, user_id: UUID, percakapan_id: UUID, j: Jalannya, isi: str) -> None:
        async def pendengar(jenis: str, data: Mapping[str, Any]) -> None:
            await self.aliran.kirim(percakapan_id, jenis, data)

        try:
            hasil = await self.runtime.lanjutkan(j, isi, pendengar=pendengar)
            k = hasil.keputusan
            teks, keyakinan, alasan = k.teks, k.confidence, k.rationale
        except AlatDitolak as galat:
            if galat.kode not in KODE_GERBANG:
                await self._gagal(percakapan_id, galat)
                return
            teks, keyakinan, alasan = self._tertahan(galat)
            if galat.konfirmasi is not None:
                await self.aliran.kirim(
                    percakapan_id, "confirmation_required", _permintaan(galat.konfirmasi)
                )
        except asyncio.CancelledError:
            await self.aliran.kirim(percakapan_id, "error", {"code": "cancelled"})
            raise
        except Exception as galat:
            await self._gagal(percakapan_id, galat)
            return
        try:
            async with platform.transaksi_pengguna(self._engine, user_id) as conn:
                pohon = await repository.ringkas_pohon(conn, user_id, j.id)
            balasan = await self._simpan(
                user_id,
                percakapan_id,
                uuid4(),
                "assistant",
                teks,
                agent_run_id=j.id,
                model=pohon.model,
                tokens_in=pohon.masuk,
                tokens_out=pohon.keluar,
                cost_usd=pohon.biaya,
                confidence=keyakinan,
                rationale=alasan,
            )
        except Exception as galat:
            await self._gagal(percakapan_id, galat)
            return
        await self.aliran.kirim(percakapan_id, "done", _done(balasan))

    async def _gagal(self, percakapan_id: UUID, galat: BaseException) -> None:
        log.error("percakapan.giliran_gagal", kode=_kode(galat), jenis=type(galat).__name__)
        await self.aliran.kirim(percakapan_id, "error", {"code": _kode(galat)})

    @staticmethod
    def _tertahan(galat: AlatDitolak) -> tuple[str, Decimal, tuple[str, ...]]:
        k = galat.konfirmasi
        if k is None:
            return (
                f"Tidak dijalankan: {galat.alat} ditolak ({galat.kode}).",
                KEYAKINAN_PASTI,
                ("Kamu menolak izin ini, atau risikonya tidak diizinkan sama sekali.",),
            )
        tanya = "konfirmasimu" if k.jenis == "konfirmasi" else "izinmu"
        return (
            f"Perlu {tanya}: {k.agent} ingin menjalankan {k.alat} (risiko R{k.risk_level}).",
            KEYAKINAN_PASTI,
            (
                f"{k.alat} berisiko R{k.risk_level} dan menyentuh: {', '.join(k.scopes)}.",
                "Aksi agent di bawah kendalimu — tidak dijalankan sebelum kamu menjawab.",
            ),
        )

    async def jawab(
        self, user_id: UUID, percakapan_id: UUID, badan: JawabKonfirmasi
    ) -> TerimaKonfirmasi:
        """Jawaban atas `confirmation_required` — lalu giliran yang sama diulang (4.5).

        Yang bisa MENOLAK jawaban ini diperiksa sebelum giliran baru dimulai (E-202):
        token, percakapannya, dan apakah permintaannya sudah dijawab — ketukan ganda
        saat giliran ulangan masih berjalan menerima `409 confirmation_answered`, bukan
        `turn_in_progress`. Yang baru ketahuan saat jawabannya dicatat (`allow_always`
        untuk R3, balapan dua jawaban) meng-`urungkan` giliran yang belum terjadi.
        """
        await self._pastikan_ada(user_id, percakapan_id)
        try:
            permintaan = self._tanda.baca(badan.token, user_id)
        except KonfirmasiTidakSah:
            raise _konfirmasi_tidak_sah() from None
        async with platform.transaksi_pengguna(self._engine, user_id) as conn:
            akar = await repository.akar_run(conn, user_id, permintaan.run_id)
            ditahan = await repository.baca_run(conn, permintaan.run_id)
            pesan_awal = (
                None
                if permintaan.pesan_id is None
                else await repository.baca_pesan(conn, user_id, permintaan.pesan_id)
            )
        if (
            akar is None
            or akar[1] != percakapan_id
            or ditahan is None
            or pesan_awal is None
            or pesan_awal.role != "user"
            or pesan_awal.conversation_id != percakapan_id
        ):
            raise _konfirmasi_tidak_sah()  # bukan milik percakapan ini
        if ditahan.status != "blocked" or ditahan.confirmed_by_user is not None:
            raise _sudah_dijawab()
        lama = self._mulai_giliran(percakapan_id)
        try:
            setuju = await self._jawab(user_id, badan)
        except BaseException:
            await self.aliran.urungkan(percakapan_id, lama)  # tidak ada yang tercatat
            raise
        try:
            if setuju is None:
                balasan = await self._simpan(
                    user_id,
                    percakapan_id,
                    uuid4(),
                    "assistant",
                    f"Baik, {permintaan.alat} tidak dijalankan.",
                    agent_run_id=akar[0],
                    cost_usd=Decimal(0),
                    confidence=KEYAKINAN_PASTI,
                    rationale=("Kamu menolaknya.",),
                )
                await self.aliran.kirim(percakapan_id, "done", _done(balasan))
                return TerimaKonfirmasi(agent_run_id=akar[0], status="completed")
            # Persetujuan yang sudah dipegang giliran ini ikut diulang (E-199).
            j = await self.runtime.mulai(
                user_id,
                AGENT_AKAR,
                pemicu="user",
                percakapan_id=percakapan_id,
                persetujuan=frozenset(permintaan.persetujuan_lalu) | {setuju},
                pesan_id=pesan_awal.id,
            )
        except BaseException as galat:
            await self.aliran.kirim(percakapan_id, "error", {"code": _kode(galat)})
            raise
        self._latar(self._giliran(user_id, percakapan_id, j, pesan_awal.content))
        return TerimaKonfirmasi(agent_run_id=j.id, status="processing")

    async def _jawab(self, user_id: UUID, badan: JawabKonfirmasi) -> PersetujuanAksi | None:
        try:
            return await jawab_konfirmasi(
                self._izin,
                self._tanda,
                user_id,
                badan.token,
                _JAWABAN[badan.decision],
            )
        except KonfirmasiTerjawab:
            raise _sudah_dijawab() from None
        except KonfirmasiTidakSah:
            raise _konfirmasi_tidak_sah() from None

    async def tutup(self) -> None:
        """Api berhenti: giliran yang masih berjalan dibatalkan — run-nya ditutup `cancelled`."""
        for tugas in list(self._tugas):
            tugas.cancel()
        if self._tugas:
            await asyncio.gather(*self._tugas, return_exceptions=True)


def _status_giliran(ada_balasan: bool, run: repository.BarisRun | None) -> StatusGiliran:
    """Keadaan giliran yang diputar ulang (Idempotency-Key) — dari balasannya DAN run
    akarnya. Giliran yang gagal tidak menyimpan balasan: dulu terbaca `processing` selamanya,
    dan klien yang menunggu tidak pernah berhenti menunggu (E-212, tinjauan Sprint 4). Run
    `blocked` = selesai: pertanyaannya ADALAH balasannya."""
    if ada_balasan or run is None or run.status == "blocked":
        return "completed"
    return "processing" if run.status == "running" else "failed"


def _konfirmasi_tidak_sah() -> platform.GalatApi:
    # Tanpa membedakan rusak · kedaluwarsa · milik orang lain: pesan tidak mengutip masukan.
    return platform.GalatApi(422, "invalid_confirmation", "Token konfirmasi tidak sah.")


def _sudah_dijawab() -> platform.GalatApi:
    return platform.GalatApi(409, "confirmation_answered", "Permintaan ini sudah dijawab.")


def _permintaan(k: PermintaanKonfirmasi) -> dict[str, Any]:
    """SSE `confirmation_required` — yang dilihat pengguna sebelum menjawab (tanpa masukan)."""
    return {
        "token": k.token,
        "kind": "confirmation" if k.jenis == "konfirmasi" else "permission",
        "agent": k.agent,
        "tool": k.alat,
        "risk_level": k.risk_level,
        "scopes": list(k.scopes),
        "remember_allowed": k.jenis == "izin",
        "expires_at": datetime.fromtimestamp(k.kedaluwarsa, UTC).isoformat(),
    }


# SSE `error.code` (spec/04) — kode API berbahasa Inggris (AGENTS.md §7), bukan kode
# internal pelaksana tool (E-203): klien tidak bisa berbuat apa pun atas `masukan_salah`.
_KODE_API_ALAT = {"terlalu_sering": "rate_limited"}
KODE_GALAT_AGENT = "agent_error"  # program agent memanggil tool/keputusan secara salah


def _kode(galat: BaseException) -> str:
    if isinstance(galat, platform.GalatApi):
        return galat.kode
    if isinstance(galat, asyncio.CancelledError):
        return "cancelled"
    if isinstance(galat, AlatDitolak):
        return _KODE_API_ALAT.get(galat.kode, KODE_GALAT_AGENT)
    if isinstance(galat, AlatGagal):
        return galat.kode  # kode API layanan pemilik datanya: `not_found`, `invalid_tier`, …
    if isinstance(galat, KeputusanTidakSah):
        return KODE_GALAT_AGENT
    if isinstance(galat, platform.GalatModel):
        return "model_unavailable"
    return "internal_error"
