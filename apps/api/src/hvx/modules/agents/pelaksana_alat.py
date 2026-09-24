"""Pelaksana tool — spec/07 4.3: *tool di luar registry tidak bisa dipanggil; pemanggilan
agent ikut melewati gerbang*.

SATU jalan untuk tiap pemanggilan tool — termasuk pemanggilan agent lain (`kind:
agent`, K-14) — dan urutannya tetap:

1. **terdaftar** — ada di tool registry DAN punya implementasi (keduanya satu lawan
   satu, diperiksa saat pelaksana dirakit); selainnya `tidak_terdaftar`;
2. **milik agent pemanggil** — tercantum di `tools:` manifest-nya; agent tidak bisa
   memanggil tool yang tidak ia nyatakan (dan yang karenanya tidak divalidasi pagunya);
3. **masukan** — tepat skema `input` tool: medan tak dikenal, wajib yang hilang, tipe
   yang salah, dan nilai di luar `enum`/`min`/`max`-nya DITOLAK, tidak dikoersi (E-170
   di sisi agent: model kelak menulis pemanggilan ini, dan model tidak ditaati karena
   yakin). Medan bernama `scope` adalah scope yang disentuh pemanggilan itu
   (`memory.write`): wajib di `scopes` tool DAN di pagu manifest pemanggil — izin
   pengguna tidak pernah melebarkan manifest (spec/05 aturan 2);
4. **batas laju** — `rate_limit` tool, per pengguna (spec/05 `60/min/user`);
5. **gerbang risiko** — `Gerbang.periksa` (spec/07 4.5);
6. lalu dijalankan, dan **keluarannya** diperiksa terhadap skema `output`: tool yang
   mengembalikan medan yang tidak dinyatakan (catatan bebas pengguna, misalnya)
   adalah cacat, bukan fitur.
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import memory, platform

from .jalannya import Jalannya
from .registri import Alat, RegistriAgent

_JENDELA_S = {"min": 60, "hour": 3_600}
_TANGGAL = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class AlatDitolak(RuntimeError):
    """Pemanggilan tool tidak dijalankan. `kode` — `tidak_terdaftar` · `bukan_alat_agent` ·
    `masukan_salah` · `terlalu_sering` · keputusan gerbang (4.5). Pesannya tanpa isi masukan."""

    def __init__(self, kode: str, pesan: str) -> None:
        super().__init__(pesan)
        self.kode = kode


class AlatGagal(RuntimeError):
    """Tool dijalankan dan menolak permintaannya (mis. habit tidak ditemukan) — bukan gerbang."""

    def __init__(self, kode: str, pesan: str) -> None:
        super().__init__(pesan)
        self.kode = kode


# Agent lain yang dipanggil lewat tool `kind: agent` — (nama agent, pesan, run induk).
PelaksanaAgent = Callable[[str, str, Jalannya], Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class LayananAlat:
    """Yang dibutuhkan implementasi tool di luar basis data — dirakit `hvx.main`."""

    pencari_memori: memory.PencariMemori | None = None
    pelaksana_agent: PelaksanaAgent | None = None


@dataclass(frozen=True)
class KonteksAlat:
    engine: AsyncEngine
    jalannya: Jalannya
    layanan: LayananAlat


ImplementasiAlat = Callable[[KonteksAlat, dict[str, Any]], Awaitable[dict[str, Any]]]


class Gerbang(Protocol):
    """Gerbang risiko (spec/05 *Risk gate*, spec/07 4.5) — `AlatDitolak` bila tidak boleh."""

    async def periksa(self, jalannya: Jalannya, alat: Alat, masukan: Mapping[str, Any]) -> None: ...


def _salah(nama: str, pesan: str) -> AlatDitolak:
    return AlatDitolak("masukan_salah", f"{nama}: {pesan}")


def _masukan_ke(tipe: str, nilai: Any) -> Any:
    """Nilai dari pemanggil → tipe skema, KETAT (tanpa koersi) — `ValueError` bila salah."""
    if tipe == "uuid":
        if not isinstance(nilai, str | UUID):
            raise ValueError
        return nilai if isinstance(nilai, UUID) else UUID(nilai)
    if tipe == "date":
        if isinstance(nilai, date):
            return nilai
        if not isinstance(nilai, str) or not _TANGGAL.fullmatch(nilai):
            raise ValueError
        return date.fromisoformat(nilai)
    if tipe == "integer":
        if isinstance(nilai, bool) or not isinstance(nilai, int):
            raise ValueError
        return nilai
    if tipe == "number":
        if isinstance(nilai, bool) or not isinstance(nilai, int | float):
            raise ValueError
        return nilai
    cocok = {"string": str, "boolean": bool, "array": list, "object": dict}[tipe]
    if not isinstance(nilai, cocok):
        raise ValueError
    return nilai


def periksa_masukan(alat: Alat, masukan: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(masukan, Mapping):
        raise _salah(alat.name, "masukan wajib objek")
    asing = sorted(set(masukan) - set(alat.input))
    if asing:
        raise _salah(alat.name, f"medan tak dikenal: {asing}")
    hasil: dict[str, Any] = {}
    for nama, medan in alat.input.items():
        if nama not in masukan or masukan[nama] is None:
            if medan.required:
                raise _salah(alat.name, f"medan wajib: {nama}")
            continue
        try:
            nilai = _masukan_ke(medan.type, masukan[nama])
        except (ValueError, TypeError):
            raise _salah(alat.name, f"{nama} wajib bertipe {medan.type}") from None
        if medan.enum is not None and nilai not in medan.enum:
            raise _salah(alat.name, f"{nama} wajib salah satu dari {medan.enum}")
        if (medan.min is not None and nilai < medan.min) or (
            medan.max is not None and nilai > medan.max
        ):
            raise _salah(alat.name, f"{nama} wajib {medan.min}–{medan.max}")
        hasil[nama] = nilai
    return hasil


def scope_panggilan(alat: Alat, masukan: Mapping[str, Any]) -> tuple[str, ...]:
    """Scope yang disentuh SATU pemanggilan — `scope` masukannya bila tool memintanya
    (`memory.write`), selainnya seluruh `scopes` tool. Yang ditanyakan gerbang (4.5)."""
    scope = masukan.get("scope")
    return (scope,) if isinstance(scope, str) else tuple(alat.scopes)


def _periksa_pagu_scope(jalannya: Jalannya, alat: Alat, masukan: Mapping[str, Any]) -> None:
    if "scope" not in alat.input:
        return
    memori = jalannya.agent.memory
    pagu = memori.write if alat.kind == "write" else memori.read
    for scope in scope_panggilan(alat, masukan):
        if scope not in alat.scopes or scope not in pagu:
            raise AlatDitolak(
                "scope_di_luar_manifest", f"{alat.name}: scope di luar {jalannya.agent.name}"
            )


_TIPE_KELUAR: dict[str, tuple[type, ...]] = {
    "uuid": (UUID, str),
    "integer": (int,),
    "number": (int, float),
    "string": (str,),
    "boolean": (bool,),
    "array": (list,),
    "object": (dict,),
}


def periksa_keluaran(alat: Alat, keluaran: Mapping[str, Any]) -> None:
    """Keluaran = skema `output` persis — cacat implementasi, bukan salah pemanggil."""
    asing = sorted(set(keluaran) - set(alat.output))
    if asing:
        raise RuntimeError(f"{alat.name} mengembalikan medan yang tidak dinyatakan: {asing}")
    for nama, tipe in alat.output.items():
        bagian = [t.strip() for t in tipe.split("|")]
        nilai = keluaran.get(nama)
        if nilai is None:
            if "null" not in bagian:
                raise RuntimeError(f"{alat.name}: medan keluaran {nama} kosong")
            continue
        boleh = tuple(t for b in bagian if b != "null" for t in _TIPE_KELUAR[b])
        if (isinstance(nilai, bool) and bool not in boleh) or not isinstance(nilai, boleh):
            raise RuntimeError(f"{alat.name}: medan keluaran {nama} bukan {tipe}")


class PelaksanaAlat:
    def __init__(
        self,
        registri: RegistriAgent,
        implementasi: Mapping[str, ImplementasiAlat],
        gerbang: Gerbang,
        pembatas: platform.PembatasLaju | None,
    ) -> None:
        tanpa_impl = sorted(set(registri.alat) - set(implementasi))
        tanpa_daftar = sorted(set(implementasi) - set(registri.alat))
        if tanpa_impl or tanpa_daftar:
            raise ValueError(
                f"tool registry ≠ implementasi — tanpa implementasi: {tanpa_impl}; "
                f"tanpa entri registry: {tanpa_daftar}"
            )
        self._registri = registri
        self._impl = dict(implementasi)
        self._gerbang = gerbang
        self._pembatas = pembatas

    async def _batasi(self, jalannya: Jalannya, alat: Alat) -> None:
        if self._pembatas is None:
            return
        jumlah, satuan, _per = alat.rate_limit.split("/")
        nama_batas = "alat-" + alat.name.replace(".", "-").replace("_", "-")
        batas = platform.BatasLaju(nama_batas, int(jumlah), _JENDELA_S[satuan])
        hasil = await self._pembatas.ambil(batas, str(jalannya.user_id))
        if not hasil.lolos:
            raise AlatDitolak("terlalu_sering", f"{alat.name}: batas {alat.rate_limit} terlampaui")

    async def panggil(
        self,
        engine: AsyncEngine,
        jalannya: Jalannya,
        nama: str,
        masukan: Mapping[str, Any],
        layanan: LayananAlat,
    ) -> dict[str, Any]:
        alat = self._registri.alat.get(nama)
        if alat is None:
            raise AlatDitolak("tidak_terdaftar", "tool tidak ada di tool registry")
        if nama not in jalannya.agent.tools:
            raise AlatDitolak(
                "bukan_alat_agent", f"{nama} tidak tercantum di manifest {jalannya.agent.name}"
            )
        bersih = periksa_masukan(alat, masukan)
        _periksa_pagu_scope(jalannya, alat, bersih)
        await self._batasi(jalannya, alat)
        await self._gerbang.periksa(jalannya, alat, bersih)
        jalannya.catat_alat(alat.name, alat.risk_level)
        try:
            keluaran = await self._impl[nama](KonteksAlat(engine, jalannya, layanan), bersih)
        except platform.GalatApi as galat:
            raise AlatGagal(galat.kode, str(galat)) from None
        periksa_keluaran(alat, keluaran)
        return keluaran
