"""Registry agent & tool — spec/07 4.2: *9 aturan spec/05 ditegakkan; manifest salah DITOLAK*.

Dua katalog, dibaca dari YAML di paket ini (lokasinya: E-190):

* `alat/<nama>.yaml` — tool registry spec/05: 9 tool V0 + 3 entri `kind: agent` (K-14);
* `manifest/<nama>.yaml` — manifest agent (spec/05 *Skema manifest*).

Keduanya divalidasi SEBELUM satu agent pun berjalan, dan **semua** pelanggaran
dilaporkan sekaligus — aturan 9 tidak boleh tersembunyi di balik aturan 2 hanya
karena yang kedua diperiksa lebih dulu. Selain sembilan aturan spec/05:

* **A-1 / H-21** — `risk_level` (atau `risk`) sebagai properti AGENT ditolak; agent
  memakai PAGU `max_risk` R0–R4, dan otonominya tangga terpisah `L0`–`L5`.
* **K-14** — tiap entri `agent.<x>` menunjuk agent `<x>-agent` yang terdaftar, dan
  `risk_level`-nya SAMA dengan `max_risk` agent itu: pemanggilan agent tidak bisa
  lebih murah di gerbang daripada yang dipanggilnya.

Katalog di basis data (`agents` · `agent_tools`) dikelola **migrasi** (spec/01 §10:
`hvx_app` hanya `SELECT`) — `pastikan_katalog` membandingkannya dengan registry ini
saat api mulai, dan menolak mulai bila berbeda: manifest yang disunting tanpa migrasi
tidak berjalan diam-diam dengan katalog lama. Manifest yang berubah = versi baru +
migrasi baru (K-29).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from typing import Annotated, Any, Literal
from uuid import UUID, uuid5

import yaml
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, ValidationError, model_validator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from hvx.modules import identity, platform

KindAlat = Literal["read", "write", "external", "agent"]
# Aksi mesin izin (spec/01 `permissions.action`, `agent_tools.permission`) tiap `kind` tool —
# yang ditanyakan gerbang risiko (4.5) DAN yang tercatat di katalog (E-209).
AKSI_IZIN: Mapping[str, identity.Aksi] = {
    "read": "read",
    "write": "write",
    "external": "execute",
    "agent": "execute",
}
EfekSamping = Literal["none", "writes_user_data", "external_call"]
TipeMedan = Literal["uuid", "date", "integer", "number", "string", "boolean", "array", "object"]

# spec/05 aturan 6 · 9 — larangan scope bagi `kind: third_party`, BERLAKU walau scope-nya
# belum ada di daftar resmi V0: kelak ditambahkan, larangannya sudah menunggu.
SCOPE_TERLARANG_PIHAK_KETIGA_6 = frozenset({"journal", "journal_raw", "finance", "health"})
SCOPE_TERLARANG_PIHAK_KETIGA_9 = frozenset({"spatial", "location", "people", "csi"})
AMBANG_KESELAMATAN = 0.95  # spec/05 aturan 4

# Ruang nama uuid5 id baris katalog `agents` — TETAP: id = uuid5(ruang, "nama@versi").
RUANG_ID_AGENT = UUID("7d0f4f8e-5a53-4c0e-9d3f-2a6b1e0c4b21")

_SEMVER = r"^\d+\.\d+\.\d+$"
_KETAT = ConfigDict(extra="forbid", frozen=True, strict=True)
# Tipe keluaran skalar; `array`/`object` wajib menyatakan isinya (`_Susunan`, E-206).
_SKALAR = frozenset({"uuid", "integer", "number", "string", "boolean"})
_SUSUNAN = frozenset({"array", "object"})


def bagian_tipe(tipe: str) -> list[str]:
    """`"string | null"` → `["string", "null"]`."""
    return [t.strip() for t in tipe.split("|")]


class _Medan(BaseModel):
    model_config = _KETAT
    type: TipeMedan
    required: bool
    # 🔧 4.3 — batas NILAI ikut kontrak tool, supaya pemanggilan yang pasti gagal ditolak
    # pelaksana SEBELUM gerbang: tidak ada konfirmasi R2 untuk aksi yang lalu ditolak.
    enum: list[str] | None = None  # hanya `string`
    min: int | None = None  # hanya `integer` · `number`
    max: int | None = None

    @model_validator(mode="after")
    def _batas_sesuai_tipe(self) -> _Medan:
        if self.enum is not None and (self.type != "string" or not self.enum):
            raise ValueError("enum hanya untuk string, dan tidak kosong")
        berbatas = self.min is not None or self.max is not None
        if berbatas and self.type not in ("integer", "number"):
            raise ValueError("min/max hanya untuk integer dan number")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min lebih besar daripada max")
        return self


class _Susunan(BaseModel):
    """Keluaran `array`/`object` BESERTA isinya — `items` (tipe tiap unsur) atau `fields`
    (tiap medan objek). 🔧 E-206 (tinjauan kontrak Sprint 4): `items: array` saja tidak
    menyatakan apa pun tentang isinya, jadi catatan bebas pengguna (`note`) di dalam
    `items[]` lolos pemeriksa keluaran yang dijanjikan menjaganya (C-32)."""

    model_config = _KETAT
    type: str
    items: Keluaran | None = None
    fields: dict[str, Keluaran] | None = None

    @model_validator(mode="after")
    def _isi_sesuai_tipe(self) -> _Susunan:
        bagian = bagian_tipe(self.type)
        inti = [b for b in bagian if b != "null"]
        if len(inti) != 1 or inti[0] not in _SUSUNAN or len(bagian) != len(set(bagian)):
            raise ValueError("susunan wajib `array` atau `object`, boleh `| null`")
        if inti[0] == "array" and (self.items is None or self.fields is not None):
            raise ValueError("array wajib `items`, tanpa `fields`")
        if inti[0] == "object" and (not self.fields or self.items is not None):
            raise ValueError("object wajib `fields` berisi, tanpa `items`")
        return self


def _skalar_sah(tipe: str) -> str:
    bagian = bagian_tipe(tipe)
    inti = [b for b in bagian if b != "null"]
    if len(inti) != 1 or inti[0] not in _SKALAR or len(bagian) != len(set(bagian)):
        raise ValueError("keluaran skalar wajib satu tipe skalar, boleh `| null`")
    return tipe


Keluaran = Annotated[str, AfterValidator(_skalar_sah)] | _Susunan
_Susunan.model_rebuild()


class Alat(BaseModel):
    """Satu entri tool registry (spec/05 *Tool registry*)."""

    model_config = _KETAT

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
    version: str = Field(pattern=_SEMVER)
    kind: KindAlat
    description: str = Field(min_length=1, max_length=200)
    scopes: list[str]
    # Aturan 8: TANPA bawaan — kelalaian berhenti di validator, bukan di produksi (K-12).
    risk_level: int = Field(ge=0, le=4)
    input: dict[str, _Medan]
    output: dict[str, Keluaran]
    side_effects: EfekSamping
    reaches_third_party: bool
    rate_limit: str = Field(pattern=r"^[1-9][0-9]{0,4}/(min|hour)/user$")
    # 🔧 4.7 (E-193): tool BACA yang menanyai mesin izin sendiri, per scope — scope yang
    # ditolak atau belum diputuskan dikeluarkan dari hasilnya dan dilaporkan
    # (`memory.search`, 3.7). Gerbang lalu tidak menanyakannya lagi untuk seluruh
    # pemanggilan: satu scope `ask` tidak boleh menahan jawaban dari scope yang diizinkan.
    menyaring_izin: bool = False


class _Memori(BaseModel):
    model_config = _KETAT
    read: list[str]
    write: list[str]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, populate_by_name=True)
    kelas: Literal["simple", "reasoning", "vision", "embedding"] = Field(alias="class")
    fallback: Literal["simple", "reasoning", "vision", "embedding"]


class _Otonomi(BaseModel):
    model_config = _KETAT
    max_level: str = Field(pattern=r"^L[0-5]$")  # H-21 — bukan angka tangga R
    kill_condition: list[str]


class _Anggaran(BaseModel):
    model_config = _KETAT
    p95_latency_ms: int = Field(gt=0)
    cost_usd_per_run: float = Field(ge=0)


class _Evaluasi(BaseModel):
    model_config = _KETAT
    suite: str = Field(min_length=1)
    gates: dict[str, float]
    budget: _Anggaran


class Manifest(BaseModel):
    """Manifest agent (spec/05 *Skema manifest*) — bentuknya; aturannya di `_periksa_manifest`."""

    model_config = _KETAT

    name: str = Field(pattern=r"^[a-z][a-z0-9-]{2,39}$")
    version: str = Field(pattern=_SEMVER)
    kind: Literal["core", "domain", "third_party"]
    status: Literal["draft", "active", "deprecated", "disabled"]
    purpose: list[str] = Field(min_length=1, max_length=5)
    # spec/05: *kontrak mesin; nama snake_case* (tinjauan kontrak Sprint 4).
    capabilities: list[Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")]] = Field(
        min_length=1
    )
    tools: list[str]
    memory: _Memori
    model: _Model
    max_risk: str = Field(pattern=r"^R[0-4]$")
    autonomy: _Otonomi
    deploy: Literal["edge", "cloud", "both"]
    evaluation: _Evaluasi

    @property
    def pagu_risiko(self) -> int:
        return int(self.max_risk[1])

    @property
    def id_katalog(self) -> UUID:
        return uuid5(RUANG_ID_AGENT, f"{self.name}@{self.version}")


@dataclass(frozen=True)
class Pelanggaran:
    subjek: str  # nama manifest atau tool
    aturan: str  # "1".."9" (spec/05) · "A-1" · "K-14" · "bentuk"
    pesan: str

    def __str__(self) -> str:
        return f"{self.subjek}: aturan {self.aturan} — {self.pesan}"


class RegistriTidakSah(ValueError):
    """Satu atau lebih manifest/tool melanggar aturan — SEMUA pelanggarannya di `pelanggaran`."""

    def __init__(self, pelanggaran: list[Pelanggaran]) -> None:
        self.pelanggaran = tuple(pelanggaran)
        super().__init__("registry agent ditolak:\n" + "\n".join(str(p) for p in pelanggaran))


@dataclass(frozen=True)
class RegistriAgent:
    alat: Mapping[str, Alat]
    agent: Mapping[str, Manifest]  # hanya yang `status: active` (aturan 5: satu per nama)
    mentah: Mapping[str, Mapping[str, Any]]  # manifest apa adanya — isi kolom `agents.manifest`


def _bentuk(subjek: str, galat: ValidationError) -> list[Pelanggaran]:
    # Hanya lokasi & jenis galat — nilai manifest tidak dipantulkan (sama dengan E-174).
    return [
        Pelanggaran(subjek, "bentuk", f"{'.'.join(str(x) for x in e['loc'])}: {e['type']}")
        for e in galat.errors(include_input=False, include_url=False)
    ]


def _periksa_alat(
    nama_berkas: str, mentah: Mapping[str, Any]
) -> tuple[Alat | None, list[Pelanggaran]]:
    salah: list[Pelanggaran] = []
    if "risk_level" not in mentah:
        # Aturan 8 dilaporkan — dan pemeriksaan BERLANJUT dengan risiko sementara, supaya
        # pelanggaran lain tool yang sama tidak bersembunyi di baliknya (E-207). Tool-nya
        # tetap tidak terdaftar: tanpa `risk_level` ia tidak pernah bisa dipanggil.
        salah.append(Pelanggaran(nama_berkas, "8", "tool tanpa `risk_level` — tidak ada bawaan"))
        _alat, lain = _periksa_alat(nama_berkas, {**mentah, "risk_level": 0})
        return None, salah + lain
    try:
        alat = Alat.model_validate(mentah)
    except ValidationError as galat:
        return None, _bentuk(nama_berkas, galat)
    if alat.name != nama_berkas:
        salah.append(Pelanggaran(nama_berkas, "bentuk", f"berkas {nama_berkas}, nama {alat.name}"))
    if alat.reaches_third_party and alat.risk_level < 3:
        salah.append(
            Pelanggaran(
                alat.name,
                "7",
                "akibatnya sampai ke orang lain (`reaches_third_party`) — wajib risk ≥ 3",
            )
        )
    asing = sorted(set(alat.scopes) - identity.SCOPE_RESMI.keys())
    if asing:
        salah.append(Pelanggaran(alat.name, "2", f"scope di luar daftar resmi: {asing}"))
    if alat.menyaring_izin and (alat.kind != "read" or alat.side_effects != "none"):
        # Hanya BACAAN yang boleh menyaring izinnya sendiri: tulisan selalu ditanya gerbang.
        salah.append(
            Pelanggaran(alat.name, "bentuk", "menyaring_izin hanya untuk tool baca tanpa efek")
        )
    return alat, salah


def _periksa_manifest(
    nama_berkas: str, mentah: Mapping[str, Any], alat: Mapping[str, Alat]
) -> tuple[Manifest | None, list[Pelanggaran]]:
    salah: list[Pelanggaran] = [
        Pelanggaran(
            nama_berkas,
            "A-1",
            f"`{terlarang}` sebagai properti AGENT membalik H-21 — agent memakai PAGU `max_risk`",
        )
        for terlarang in ("risk_level", "risk")
        if terlarang in mentah
    ]
    bersih = {k: v for k, v in mentah.items() if k not in ("risk_level", "risk")}
    try:
        m = Manifest.model_validate(bersih)
    except ValidationError as galat:
        return None, salah + _bentuk(nama_berkas, galat)
    if m.name != nama_berkas:
        salah.append(Pelanggaran(nama_berkas, "bentuk", f"berkas {nama_berkas}, nama {m.name}"))
    for t in m.tools:  # aturan 1 · 3 (aturan 7 di tool-nya sendiri: `_periksa_alat`)
        if t not in alat:
            salah.append(Pelanggaran(m.name, "1", f"tool {t} tidak ada di tool registry"))
            continue
        if alat[t].risk_level > m.pagu_risiko:
            salah.append(
                Pelanggaran(
                    m.name, "3", f"tool {t} risk {alat[t].risk_level} > max_risk {m.max_risk}"
                )
            )
    scope = set(m.memory.read) | set(m.memory.write)
    asing = sorted(scope - identity.SCOPE_RESMI.keys())  # aturan 2
    if asing:
        salah.append(Pelanggaran(m.name, "2", f"scope di luar daftar resmi: {asing}"))
    keselamatan = m.evaluation.gates.get("safety")  # aturan 4
    if keselamatan is None or keselamatan < AMBANG_KESELAMATAN:
        salah.append(
            Pelanggaran(
                m.name, "4", f"evaluation.gates.safety wajib ada dan ≥ {AMBANG_KESELAMATAN}"
            )
        )
    if m.kind == "third_party":  # aturan 6 · 9
        # Scope yang DIMINTA juga lewat tool-nya (yang ditanyakan gerbang ke mesin izin,
        # E-191) — bukan hanya `memory.read/write` manifest (E-207).
        scope |= {s for t in m.tools if t in alat for s in alat[t].scopes}
        for aturan, terlarang in (
            ("6", SCOPE_TERLARANG_PIHAK_KETIGA_6),
            ("9", SCOPE_TERLARANG_PIHAK_KETIGA_9),
        ):
            diminta = sorted(scope & terlarang)
            if diminta:
                salah.append(
                    Pelanggaran(m.name, aturan, f"agent pihak ketiga meminta scope {diminta}")
                )
    return m, salah


def validasi_registri(
    alat_mentah: Mapping[str, Mapping[str, Any]],
    manifest_mentah: Mapping[str, Mapping[str, Any]],
) -> RegistriAgent:
    """Registry dari dokumen yang sudah diurai — `{nama berkas: isi}`. Murni, tanpa berkas."""
    salah: list[Pelanggaran] = []
    alat: dict[str, Alat] = {}
    for nama, isi in sorted(alat_mentah.items()):
        a, p = _periksa_alat(nama, isi)
        salah += p
        if a is not None:
            alat[a.name] = a
    semua: list[Manifest] = []
    for nama, isi in sorted(manifest_mentah.items()):
        m, p = _periksa_manifest(nama, isi, alat)
        salah += p
        if m is not None:
            semua.append(m)
    aktif: dict[str, Manifest] = {}
    for m in semua:  # aturan 5
        if m.status != "active":
            continue
        if m.name in aktif:
            salah.append(Pelanggaran(m.name, "5", "lebih dari satu versi `status: active`"))
        aktif[m.name] = m
    for a in alat.values():  # K-14
        if a.kind != "agent":
            continue
        dipanggil = aktif.get(a.name.removeprefix("agent.") + "-agent")
        if dipanggil is None:
            salah.append(Pelanggaran(a.name, "K-14", "tidak menunjuk agent aktif mana pun"))
        elif a.risk_level != dipanggil.pagu_risiko:
            salah.append(
                Pelanggaran(
                    a.name,
                    "K-14",
                    f"risk {a.risk_level} ≠ max_risk {dipanggil.max_risk} agent yang dipanggil",
                )
            )
    if salah:
        raise RegistriTidakSah(salah)
    mentah = {m.name: manifest_mentah[m.name] for m in aktif.values()}
    return RegistriAgent(alat, aktif, mentah)


def _baca_yaml(sub: str) -> dict[str, dict[str, Any]]:
    hasil: dict[str, dict[str, Any]] = {}
    for berkas in sorted(resources.files(__package__).joinpath(sub).iterdir(), key=str):
        if berkas.name.endswith(".yaml"):
            isi = yaml.safe_load(berkas.read_text(encoding="utf-8"))
            hasil[berkas.name.removesuffix(".yaml")] = isi if isinstance(isi, dict) else {}
    return hasil


def muat_registri() -> RegistriAgent:
    """Registry dari YAML paket ini — atau `RegistriTidakSah` dengan semua pelanggarannya."""
    return validasi_registri(_baca_yaml("alat"), _baca_yaml("manifest"))


def manifest_json(isi: Mapping[str, Any]) -> str:
    """Bentuk kanonik manifest untuk kolom `agents.manifest` dan pembandingnya."""
    return json.dumps(isi, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class KatalogBerbeda(RuntimeError):
    """Katalog `agents`/`agent_tools` basis data ≠ registry — api menolak mulai."""


_KATALOG = text(
    """
    SELECT a.id, a.name, a.version, a.kind, a.max_risk, a.manifest,
           coalesce(array_agg(t.tool_name || ':' || t.permission ORDER BY t.tool_name)
                    FILTER (WHERE t.tool_name IS NOT NULL), '{}') AS tools
    FROM agents a LEFT JOIN agent_tools t ON t.agent_id = a.id
    WHERE a.status = 'active'
    GROUP BY a.id
    """
)


async def pastikan_katalog(engine: AsyncEngine, registri: RegistriAgent) -> None:
    """Tolak mulai bila katalog basis data ≠ registry — manifest yang disunting tanpa
    migrasinya tidak berjalan diam-diam dengan pagu dan tool yang lama."""
    async with platform.transaksi_sistem(engine) as conn:
        baris = {b.name: b for b in await conn.execute(_KATALOG)}
    beda: list[str] = []
    for nama in sorted(set(baris) | set(registri.agent)):
        m, b = registri.agent.get(nama), baris.get(nama)
        if m is None or b is None:
            beda.append(
                f"{nama}: {'tidak ada di registry' if m is None else 'tidak ada di katalog'}"
            )
            continue
        # Tool beserta aksinya (`agent_tools.permission`, E-209) — `nama:aksi`.
        tools = sorted(f"{t}:{AKSI_IZIN[registri.alat[t].kind]}" for t in m.tools)
        harapan = (m.id_katalog, m.version, m.kind, m.pagu_risiko, tools)
        ada = (b.id, b.version, b.kind, b.max_risk, list(b.tools))
        if harapan != ada or json.loads(manifest_json(registri.mentah[nama])) != b.manifest:
            beda.append(f"{nama}: katalog basis data berbeda dengan manifest {m.version}")
    if beda:
        raise KatalogBerbeda(
            "katalog agent ≠ manifest (K-29) — manifest yang berubah butuh versi & migrasi baru: "
            + "; ".join(beda)
        )
