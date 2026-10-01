"""Runtime agent — spec/07 4.4: *tiap run mencatat tools, scope, decision, confidence, cost*.

Satu run = satu baris `agent_runs` (spec/01 §8) — **AI Audit Trail** naskah 5 §24:
*Request → Agent → Tools → Memory accessed → Decision → Action → Outcome*, disimpan
sebagai **metadata audit, bukan hidden chain-of-thought mentah**. Barisnya ditulis
SEBELUM program agent berjalan (status `running`), jadi tulisan yang merujuknya —
rekomendasi, run anak (`parent_run_id`) — sah sejak langkah pertama; dan ditutup
sekali, apa pun akhirnya: `succeeded` · `blocked` (gerbang menahan) · `failed` ·
`cancelled`. Run yang dibatalkan di tengah jalan tetap ditutup — penutupnya
dilindungi dari pembatalan yang sama.

Program agent tidak menyentuh basis data maupun model secara langsung: ia hanya
punya `KonteksAgent` — `alat()` lewat pelaksana tool (registry, manifest, masukan,
batas laju, gerbang; 4.3) dan `model()` lewat AI Gateway (4.1). Keduanya yang
mencatat apa yang dipakai, jadi yang tercatat adalah yang TERJADI, bukan yang
dilaporkan program.

Keputusan tiap program wajib membawa `confidence` + `rationale` (Konstitusi Pasal 3,
arch/08 §4; spec/04 SSE `done`), dan `aksi`-nya — isi kolom `decision` — hanya
skalar pendek: `decision` adalah APA yang diputuskan (`reply`, `delegate`, id yang
disentuh), bukan penalarannya, dan bukan tulisan pengguna.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal, Protocol
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import memory, platform, profile

from . import repository
from .jalannya import Jalannya, Pemicu
from .konfirmasi import PersetujuanAksi
from .pelaksana_alat import AlatDitolak, AlatGagal, LayananAlat, PelaksanaAlat
from .registri import RegistriAgent

StatusRun = Literal["succeeded", "blocked", "failed", "cancelled"]
NilaiAksi = str | int | bool | None

# Penolakan GERBANG (spec/05 *Risk gate*, 4.5) — run menunggu manusia, bukan gagal.
KODE_GERBANG = frozenset({"perlu_izin", "perlu_konfirmasi", "ditolak_pengguna", "risiko_terlarang"})
ALASAN_MAKS = 10
ALASAN_PANJANG_MAKS = 300
TEKS_MAKS = 8_000
AKSI_KUNCI_MAKS = 10
AKSI_NILAI_MAKS = 120
_KUNCI_AKSI = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
# Anggaran biaya model (4.9, K-32): jendela yang BERGULIR, bukan hari kalender — hari lokal
# bisa digeser pengguna lewat zona waktu profilnya (E-201).
JENDELA_ANGGARAN = timedelta(hours=24)


class KeputusanTidakSah(ValueError):
    """Program agent mengembalikan keputusan tanpa keyakinan/alasan, atau `aksi` berisi isi."""


@dataclass(frozen=True)
class Keputusan:
    """Yang diputuskan satu run: balasan + keyakinan + alasan + APA yang dilakukan."""

    teks: str
    confidence: Decimal
    rationale: tuple[str, ...]
    aksi: Mapping[str, NilaiAksi]


def periksa_keputusan(k: Keputusan) -> None:
    if not isinstance(k.teks, str) or not k.teks.strip() or len(k.teks) > TEKS_MAKS:
        raise KeputusanTidakSah(f"teks balasan wajib 1–{TEKS_MAKS} karakter")
    if not isinstance(k.confidence, Decimal) or not Decimal(0) <= k.confidence <= Decimal(1):
        raise KeputusanTidakSah("confidence wajib Decimal 0–1")
    if not 1 <= len(k.rationale) <= ALASAN_MAKS or not all(
        isinstance(a, str) and a.strip() and len(a) <= ALASAN_PANJANG_MAKS for a in k.rationale
    ):
        raise KeputusanTidakSah(
            f"rationale wajib 1–{ALASAN_MAKS} alasan berisi, ≤{ALASAN_PANJANG_MAKS} karakter"
        )
    if "action" not in k.aksi or len(k.aksi) > AKSI_KUNCI_MAKS:
        raise KeputusanTidakSah(f"aksi wajib memuat `action`, ≤{AKSI_KUNCI_MAKS} kunci")
    for kunci, nilai in k.aksi.items():
        if not isinstance(kunci, str) or not _KUNCI_AKSI.fullmatch(kunci):
            raise KeputusanTidakSah("kunci aksi wajib snake_case pendek")
        if nilai is not None and not isinstance(nilai, str | int | bool):
            raise KeputusanTidakSah(f"aksi `{kunci}`: hanya skalar — decision bukan penalaran")
        if isinstance(nilai, str) and len(nilai) > AKSI_NILAI_MAKS:
            raise KeputusanTidakSah(f"aksi `{kunci}`: ≤{AKSI_NILAI_MAKS} karakter — bukan isi")


@dataclass(frozen=True)
class HasilRun:
    run_id: UUID
    keputusan: Keputusan
    # Biaya run ini DAN seluruh run anaknya — yang dibayar satu permintaan (SSE `done`).
    biaya_usd: Decimal


# Peristiwa yang mengalir ke klien (4.8): ("token", {"text"}) · ("tool_call", {"tool", "agent"}).
Pendengar = Callable[[str, Mapping[str, Any]], Awaitable[None]]


class ProgramAgent(Protocol):
    async def __call__(self, k: KonteksAgent, pesan: str) -> Keputusan: ...


def _aksi_tertahan(galat: BaseException) -> dict[str, NilaiAksi]:
    """`decision` run yang ditahan gerbang — tool apa, menunggu apa; tanpa masukannya."""
    if not isinstance(galat, AlatDitolak):  # pragma: no cover - `blocked` hanya dari AlatDitolak
        return {"action": "blocked"}
    if galat.konfirmasi is None:
        return {"action": "denied", "tool": galat.alat, "code": galat.kode}
    k = galat.konfirmasi
    return {
        "action": "awaiting_confirmation",
        "tool": k.alat,
        "agent": k.agent,
        "risk_level": k.risk_level,
        "kind": "confirmation" if k.jenis == "konfirmasi" else "permission",  # = SSE spec/04
    }


def _galat_run(galat: BaseException) -> dict[str, str]:
    """Kolom `error` run (spec/01 §8): `{code, type}` — tanpa pesan, apa pun akhirnya."""
    return {"code": _kode_galat(galat), "type": type(galat).__name__}


def _kode_galat(galat: BaseException) -> str:
    if isinstance(galat, asyncio.CancelledError):
        return "cancelled"
    if isinstance(galat, AlatDitolak | AlatGagal | platform.GalatApi):
        return galat.kode
    if isinstance(galat, KeputusanTidakSah):
        return "keputusan_tidak_sah"
    if isinstance(galat, platform.GalatModel):
        return "model_gagal"
    return "internal"


class KonteksAgent:
    """Satu-satunya yang dimiliki program agent: tool dan model, keduanya tercatat."""

    def __init__(
        self, runtime: RuntimeAgent, jalannya: Jalannya, pendengar: Pendengar | None
    ) -> None:
        self._runtime = runtime
        self.jalannya = jalannya
        self._pendengar = pendengar

    async def tanggal_lokal(self) -> date:
        """*Hari ini* pengguna — zona waktu profilnya (spec/01 `profiles.timezone`), bukan
        jam server: *“tandai lari selesai”* pukul 01.00 WIB adalah hari itu di Jakarta."""
        return (await self._runtime.kini_lokal(self.jalannya.user_id)).date()

    async def _kabari(self, jenis: str, data: Mapping[str, Any]) -> None:
        if self._pendengar is not None:
            await self._pendengar(jenis, data)

    async def alat(self, nama: str, masukan: Mapping[str, Any]) -> dict[str, Any]:
        await self._kabari("tool_call", {"tool": nama, "agent": self.jalannya.agent.name})
        return await self._runtime.pelaksana.panggil(
            self._runtime.engine,
            self.jalannya,
            nama,
            masukan,
            LayananAlat(
                pencari_memori=self._runtime.pencari_memori, pelaksana_agent=self._agent_anak
            ),
        )

    async def _agent_anak(self, nama: str, pesan: str, induk: Jalannya) -> dict[str, Any]:
        """Tool `kind: agent` (K-14) — run anak dengan `parent_run_id` = run ini (4.6)."""
        hasil = await self._runtime.jalankan(
            induk.user_id,
            nama,
            pesan,
            pemicu="agent",
            induk=induk,
            percakapan_id=induk.percakapan_id,
            pendengar=self._pendengar,
        )
        induk.biaya_turunan_usd += hasil.biaya_usd
        k = hasil.keputusan
        return {"teks": k.teks, "confidence": float(k.confidence), "rationale": list(k.rationale)}

    async def model(
        self,
        *,
        tugas: str,
        pertanyaan: str,
        bahan: Sequence[str] = (),
        kelas: platform.KelasModel | None = None,
        maks_token: int = 400,
    ) -> platform.JawabanModel:
        """Satu panggilan AI Gateway — tokennya mengalir ke pendengar, biayanya ke run ini.

        `kelas` bawaan = `model.class` manifest. Kelas yang dipakai dipilih — dan jatah
        anggarannya DIPESAN — sebelum panggilan (`RuntimeAgent.pesan_model`, 4.9). Aliran
        yang terputus (dibatalkan) tetap tercatat sebatas yang sudah keluar: token yang
        sudah dibayar tidak hilang dari jejak dan dari anggaran.
        """
        diminta = kelas or self._runtime.kelas_bawaan(self.jalannya)
        permintaan = await self._runtime.pesan_model(
            self.jalannya,
            platform.PermintaanModel(diminta, tugas, pertanyaan, tuple(bahan), maks_token),
        )
        if permintaan.kelas != diminta:
            self.jalannya.turun_kelas = True
        aliran = self._runtime.gerbang_model.alirkan(permintaan)
        potongan = aliran.__aiter__()
        try:
            async for p in potongan:
                await self._kabari("token", {"text": p})
        finally:
            await potongan.aclose()
            if aliran.jawaban is not None:
                self.jalannya.catat_model(aliran.jawaban)
        if aliran.jawaban is None:  # pragma: no cover - aliran yang habis selalu mengisinya
            raise platform.GalatModel("aliran model berhenti tanpa jawaban")
        # Jatah diganti biaya sebenarnya. Jalur galat & pembatalan tidak perlu: penutup
        # run (`_tutup`) menulis biaya akhirnya apa pun yang terjadi.
        await self._runtime.lunasi_model(self.jalannya)
        return aliran.jawaban


class RuntimeAgent:
    """Menjalankan program agent terdaftar dan menutup jejaknya — sekali, apa pun akhirnya."""

    def __init__(
        self,
        engine: AsyncEngine,
        registri: RegistriAgent,
        program: Mapping[str, ProgramAgent],
        pelaksana: PelaksanaAlat,
        gerbang_model: platform.GerbangModel,
        pencari_memori: memory.PencariMemori | None = None,
        anggaran_harian_usd: Decimal | None = None,
        jam: Callable[[], datetime] | None = None,
    ) -> None:
        asing = sorted(set(program) - set(registri.agent))
        if asing:
            raise ValueError(f"program untuk agent yang tidak terdaftar/aktif: {asing}")
        self.engine = engine
        self.registri = registri
        self._program = dict(program)
        self.pelaksana = pelaksana
        self.gerbang_model = gerbang_model
        self.pencari_memori = pencari_memori
        self.anggaran_harian_usd = anggaran_harian_usd
        # Jam yang bisa diganti uji: batas "hari lokal" diuji di SATU saat yang dipilih,
        # bukan bergantung pada pukul berapa uji itu kebetulan dijalankan.
        self._jam = jam or (lambda: datetime.now(UTC))

    async def kini_lokal(self, user_id: UUID) -> datetime:
        async with platform.transaksi_pengguna(self.engine, user_id) as conn:
            zona = await profile.zona_waktu(conn, user_id)
        return self._jam().astimezone(ZoneInfo(zona or "UTC"))

    async def pesan_model(
        self, j: Jalannya, permintaan: platform.PermintaanModel
    ) -> platform.PermintaanModel:
        """Model Router berjatah (4.9, K-32): kelas yang dipakai panggilan ini, dan jatahnya.

        Di bawah kunci anggaran PER PENGGUNA: biaya 24 jam terakhir — run yang sudah
        ditutup DAN jatah run yang masih berjalan, di pohon mana pun — ditambah perkiraan
        TERBURUK panggilan ini (token masuk + `maks_token` keluar). Anggaran sudah habis,
        atau panggilan ini akan melewatinya → turun ke `simple`, bukan gagal. Jatahnya
        ditulis ke `cost_usd` run ini SEBELUM kunci dilepas, jadi giliran serentak —
        percakapan lain, perangkat lain — melihatnya (E-201: dulu tiap giliran hanya
        melihat pohonnya sendiri, dan empat giliran serentak memakai model besar dengan
        anggaran untuk satu).
        """
        anggaran = self.anggaran_harian_usd
        if anggaran is None:
            return permintaan
        gm = self.gerbang_model
        async with platform.transaksi_pengguna(self.engine, j.user_id) as conn:
            await repository.kunci_anggaran(conn, j.user_id)
            terpakai = await repository.biaya_sejak(conn, j.user_id, self._jam() - JENDELA_ANGGARAN)
            habis = terpakai >= anggaran or terpakai + gm.perkiraan_biaya(permintaan) > anggaran
            kelas = gm.pilih_kelas(permintaan.kelas, anggaran_habis=habis)
            dipilih = replace(permintaan, kelas=kelas)
            await repository.catat_biaya_berjalan(
                conn, j.id, j.biaya_usd + gm.perkiraan_biaya(dipilih)
            )
        return dipilih

    async def lunasi_model(self, j: Jalannya) -> None:
        """Jatah panggilan yang selesai diganti biaya sebenarnya (`cost_usd` run berjalan)."""
        if self.anggaran_harian_usd is None:
            return
        async with platform.transaksi_pengguna(self.engine, j.user_id) as conn:
            await repository.catat_biaya_berjalan(conn, j.id, j.biaya_usd)

    def kelas_bawaan(self, jalannya: Jalannya) -> platform.KelasModel:
        kelas = jalannya.agent.model.kelas
        if kelas not in platform.KELAS_MODEL:  # vision · embedding — tidak ada di V0 (K-28)
            raise platform.GalatModel(f"kelas model {kelas} tidak tersedia di V0")
        return kelas

    async def mulai(
        self,
        user_id: UUID,
        agent: str,
        *,
        pemicu: Pemicu,
        induk: Jalannya | None = None,
        percakapan_id: UUID | None = None,
        persetujuan: frozenset[PersetujuanAksi] = frozenset(),
        pesan_id: UUID | None = None,
    ) -> Jalannya:
        """Tulis baris `agent_runs` (`running`) — id-nya sah dirujuk sejak saat ini."""
        manifest = self.registri.agent.get(agent)
        if manifest is None or agent not in self._program:
            raise ValueError(f"agent {agent} tidak punya program di runtime ini")
        if induk is not None and (induk.user_id != user_id or not induk.tersimpan):
            raise ValueError("run induk milik pengguna lain, atau belum tersimpan")
        j = Jalannya(
            uuid4(),
            user_id,
            manifest,
            pemicu,
            induk=induk,
            percakapan_id=percakapan_id,
            persetujuan=persetujuan if induk is None else induk.persetujuan,
            pesan_id=pesan_id if induk is None else induk.pesan_id,
        )
        async with platform.transaksi_pengguna(self.engine, user_id) as conn:
            await repository.mulai_run(
                conn,
                id=j.id,
                user_id=user_id,
                agent_id=manifest.id_katalog,
                agent_version=manifest.version,
                conversation_id=percakapan_id,
                parent_run_id=None if induk is None else induk.id,
                trigger=pemicu,
            )
        j.tersimpan = True
        return j

    async def lanjutkan(
        self, j: Jalannya, pesan: str, *, pendengar: Pendengar | None = None
    ) -> HasilRun:
        """Jalankan program agent run `j` lalu tutup barisnya — juga saat gagal atau dibatalkan."""
        mulai = time.perf_counter()
        k = KonteksAgent(self, j, pendengar)
        try:
            keputusan = await self._program[j.agent.name](k, pesan)
            periksa_keputusan(keputusan)
        except asyncio.CancelledError as galat:
            # Penutupnya sendiri tidak ikut dibatalkan: run tanpa akhir adalah jejak yang bohong.
            await asyncio.shield(self._tutup(j, "cancelled", None, _galat_run(galat), mulai))
            raise
        except Exception as galat:
            status: StatusRun = (
                "blocked"
                if isinstance(galat, AlatDitolak) and galat.kode in KODE_GERBANG
                else "failed"
            )
            await self._tutup(
                j,
                status,
                None,
                _galat_run(galat),
                mulai,
                aksi=_aksi_tertahan(galat) if status == "blocked" else None,
            )
            raise
        await self._tutup(j, "succeeded", keputusan, None, mulai)
        return HasilRun(j.id, keputusan, j.biaya_usd + j.biaya_turunan_usd)

    async def gagalkan(self, j: Jalannya, galat: BaseException) -> None:
        """Tutup run yang programnya TIDAK PERNAH berjalan: `mulai` sudah menulisnya, lalu
        langkah sesudahnya gagal atau dibatalkan (pesan pengguna ditolak, klien pergi). Tanpa
        ini barisnya `running` selamanya — tidak ada penyapu di V0 (E-200)."""
        status: StatusRun = "cancelled" if isinstance(galat, asyncio.CancelledError) else "failed"
        await self._tutup(j, status, None, _galat_run(galat), time.perf_counter())

    async def jalankan(
        self,
        user_id: UUID,
        agent: str,
        pesan: str,
        *,
        pemicu: Pemicu,
        induk: Jalannya | None = None,
        percakapan_id: UUID | None = None,
        pendengar: Pendengar | None = None,
        persetujuan: frozenset[PersetujuanAksi] = frozenset(),
    ) -> HasilRun:
        j = await self.mulai(
            user_id,
            agent,
            pemicu=pemicu,
            induk=induk,
            percakapan_id=percakapan_id,
            persetujuan=persetujuan,
        )
        return await self.lanjutkan(j, pesan, pendengar=pendengar)

    async def _tutup(
        self,
        j: Jalannya,
        status: StatusRun,
        keputusan: Keputusan | None,
        galat: Mapping[str, Any] | None,
        mulai: float,
        *,
        aksi: Mapping[str, NilaiAksi] | None = None,
    ) -> None:
        keputusan_run: dict[str, NilaiAksi] = (
            dict(keputusan.aksi) if keputusan is not None else dict(aksi or {"action": status})
        )
        if j.turun_kelas:
            keputusan_run["model_downgraded"] = True  # anggaran harian habis (4.9)
        async with platform.transaksi_pengguna(self.engine, j.user_id) as conn:
            tertutup = await repository.selesai_run(
                conn,
                id=j.id,
                status=status,
                tools_used=j.alat_dipakai,
                memory_scopes=sorted(j.scope_dipakai),
                model_used=",".join(j.model_dipakai) or None,
                risk_level=j.risiko_tertinggi,
                # Run yang DITAHAN: kolom ini jawaban atas pertanyaannya — NULL sampai dijawab,
                # sekali pakai. Run ulangan yang memakai persetujuan lalu ditahan lagi pun
                # menunggu jawaban baru (E-199); run lain: memakai aksi yang disetujui.
                confirmed_by_user=None if status == "blocked" else j.dikonfirmasi,
                decision=keputusan_run,
                confidence=None if keputusan is None else keputusan.confidence,
                error=galat,
                tokens_in=j.token_masuk,
                tokens_out=j.token_keluar,
                cost_usd=j.biaya_usd,
                latency_ms=round((time.perf_counter() - mulai) * 1000),
            )
        if not tertutup:
            raise RuntimeError(f"run {j.id} sudah ditutup — jejak tidak ditimpa")
