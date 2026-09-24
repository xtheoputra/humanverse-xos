"""spec/07 4.3 — *tool di luar registry tidak bisa dipanggil; pemanggilan agent lewat gerbang*.

Tanpa basis data: yang diuji di sini adalah JALAN tiap pemanggilan — registry, manifest
pemanggil, masukan ketat, gerbang, keluaran — dengan implementasi dan gerbang tiruan
yang mencatat apakah mereka disentuh. Implementasi sungguhan: `test_alat_v0.py`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, get_args
from uuid import uuid4

import pytest

from hvx.modules import goals, habits, intelligence, memory
from hvx.modules.agents import (
    IMPLEMENTASI,
    Alat,
    AlatDitolak,
    Jalannya,
    KonteksAlat,
    LayananAlat,
    PelaksanaAlat,
    muat_registri,
    periksa_keluaran,
)

REGISTRI = muat_registri()


class _GerbangPencatat:
    """Mencatat tiap pertanyaan; menolak tool dengan risk ≥ `tolak_mulai`."""

    def __init__(self, tolak_mulai: int = 99) -> None:
        self.ditanya: list[str] = []
        self._tolak = tolak_mulai

    async def periksa(self, jalannya: Jalannya, alat: Alat, masukan: Mapping[str, Any]) -> None:
        self.ditanya.append(alat.name)
        if alat.risk_level >= self._tolak:
            raise AlatDitolak("perlu_izin", f"{alat.name} risk {alat.risk_level}")


def _jalannya(agent: str) -> Jalannya:
    return Jalannya(uuid4(), uuid4(), REGISTRI.agent[agent], "user")


_NILAI = {
    "uuid": lambda: str(uuid4()),
    "integer": lambda: 0,
    "number": lambda: 0.0,
    "string": lambda: "",
    "boolean": lambda: False,
    "array": list,
    "object": dict,
}


def _tiruan(alat: Alat) -> Any:
    """Implementasi yang selalu berhasil dengan keluaran sah — kerusakan di JALAN
    pemanggilannya terbaca sebagai "tidak ditolak", bukan sebagai galat lain."""

    async def jalan(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
        return {
            n: None if "null" in tipe else _NILAI[tipe.split("|")[0].strip()]()
            for n, tipe in alat.output.items()
        }

    return jalan


def _pelaksana(gerbang: _GerbangPencatat, **ganti: Any) -> PelaksanaAlat:
    tiruan = {n: _tiruan(a) for n, a in REGISTRI.alat.items() if a.kind != "agent"}
    agent = {n: i for n, i in IMPLEMENTASI.items() if n.startswith("agent.")}
    return PelaksanaAlat(REGISTRI, {**tiruan, **agent, **ganti}, gerbang, None)


async def _panggil(
    p: PelaksanaAlat, j: Jalannya, nama: str, masukan: dict[str, Any], **layanan: Any
) -> Any:
    return await p.panggil(None, j, nama, masukan, LayananAlat(**layanan))  # type: ignore[arg-type]


def test_registry_dan_implementasi_satu_lawan_satu() -> None:
    """Tool berimplementasi tanpa entri registry = tool yang lolos tanpa risk_level."""
    with pytest.raises(ValueError, match="tanpa entri registry"):
        PelaksanaAlat(
            REGISTRI,
            {**IMPLEMENTASI, "weather.get": IMPLEMENTASI["goal.list"]},
            _GerbangPencatat(),
            None,
        )
    kurang = {k: v for k, v in IMPLEMENTASI.items() if k != "goal.list"}
    with pytest.raises(ValueError, match="tanpa implementasi"):
        PelaksanaAlat(REGISTRI, kurang, _GerbangPencatat(), None)


async def test_tool_di_luar_registry_tidak_bisa_dipanggil() -> None:
    gerbang = _GerbangPencatat()

    with pytest.raises(AlatDitolak) as galat:
        await _panggil(_pelaksana(gerbang), _jalannya("coach-agent"), "weather.get", {})

    assert galat.value.kode == "tidak_terdaftar", "tool di luar registry dijalankan"
    assert gerbang.ditanya == []


async def test_agent_hanya_memanggil_tool_manifestnya() -> None:
    """coach-agent (R1) tidak menyatakan habit.complete (R2) — pagunya tak pernah diuji untuknya."""
    gerbang = _GerbangPencatat()

    with pytest.raises(AlatDitolak) as galat:
        await _panggil(
            _pelaksana(gerbang),
            _jalannya("coach-agent"),
            "habit.complete",
            {"habit_id": str(uuid4()), "for_date": "2026-09-20", "status": "done"},
        )

    assert galat.value.kode == "bukan_alat_agent", "tool di luar manifest dijalankan"
    assert gerbang.ditanya == []


@pytest.mark.parametrize(
    ("nama", "masukan"),
    [
        ("habit.streak", {}),  # wajib hilang
        ("habit.streak", {"habit_id": "bukan-uuid"}),
        ("habit.streak", {"habit_id": str(uuid4()), "lain": 1}),  # medan tak dikenal
        ("habit.list", {"for_date": "2026-9-1"}),
        ("habit.list", {"for_date": "20260901"}),  # bentuk dasar ISO — fromisoformat menerimanya
        ("habit.list", {"for_date": 1758672000}),  # detik Unix bukan tanggal (E-170)
        ("mood.recent", {"hari": True}),  # boolean bukan bilangan
        ("mood.recent", {"hari": "7"}),
        ("memory.search", {"kueri": 3}),
        # batas NILAI skema — ditolak sebelum gerbang: tidak ada konfirmasi R2 yang sia-sia
        ("habit.complete", {"habit_id": str(uuid4()), "for_date": "2026-09-20", "status": "x"}),
        (
            "habit.complete",
            {"habit_id": str(uuid4()), "for_date": "2026-09-20", "status": "done", "tier_used": -1},
        ),
        ("mood.recent", {"hari": 0}),
        ("mood.recent", {"hari": 31}),
        ("goal.list", {"status": "selesai"}),
        ("memory.search", {"kueri": "tidur", "batas": 51}),
        (
            "recommendation.create",
            {"domain": "habit", "title": "t", "confidence": 1.5, "rationale": ["a"]},
        ),
        (
            "recommendation.create",
            {"domain": "keuangan", "title": "t", "confidence": 0.5, "rationale": ["a"]},
        ),
    ],
)
async def test_masukan_yang_salah_ditolak_sebelum_gerbang(
    nama: str, masukan: dict[str, Any]
) -> None:
    gerbang = _GerbangPencatat()
    agent = "habit-agent" if nama.startswith("habit") else "coach-agent"

    try:  # bukan pytest.raises: kerusakan terbaca sebagai "<masukan> diterima", bukan DID NOT RAISE
        await _panggil(_pelaksana(gerbang), _jalannya(agent), nama, masukan)
    except AlatDitolak as galat:
        kode: str | None = galat.kode
    else:
        kode = None

    assert kode == "masukan_salah", f"{nama} {masukan} diterima"
    assert gerbang.ditanya == [], "gerbang ditanya untuk masukan yang salah"


def _memory_agent(**memori: list[str]) -> Jalannya:
    m = REGISTRI.agent["memory-agent"]
    sempit = m.model_copy(update={"memory": m.memory.model_copy(update=memori)})
    return Jalannya(uuid4(), uuid4(), sempit, "user")


_PAGU = [
    ("DENY naskah 5 §15", lambda: _jalannya("memory-agent"), "journal_raw"),
    # Pagu manifest lebih sempit daripada `scopes` tool: manifest yang menang.
    ("pagu manifest sempit", lambda: _memory_agent(write=["coaching_notes"]), "habits"),
    # Manifest yang melebar ke journal_raw tetap dibatasi `scopes` tool-nya sendiri.
    (
        "manifest melebar",
        lambda: _memory_agent(write=["coaching_notes", "journal_raw"]),
        "journal_raw",
    ),
]


@pytest.mark.parametrize(("maksud", "jalannya", "scope"), _PAGU, ids=[p[0] for p in _PAGU])
async def test_scope_memory_write_di_luar_pagu_ditolak_sebelum_gerbang(
    maksud: str, jalannya: Any, scope: str
) -> None:
    gerbang = _GerbangPencatat()

    try:
        await _panggil(
            _pelaksana(gerbang), jalannya(), "memory.write", {"scope": scope, "isi": "x"}
        )
    except AlatDitolak as galat:
        kode: str | None = galat.kode
    else:
        kode = None

    assert kode == "scope_di_luar_manifest", f"memory.write ke {scope} diterima — {maksud}"
    assert gerbang.ditanya == [], "gerbang ditanya untuk scope di luar pagu"


async def test_scope_memory_write_di_dalam_pagu_sampai_ke_gerbang() -> None:
    gerbang = _GerbangPencatat()

    await _panggil(
        _pelaksana(gerbang),
        _jalannya("memory-agent"),
        "memory.write",
        {"scope": "coaching_notes", "isi": "x"},
    )

    assert gerbang.ditanya == ["memory.write"]


def test_batas_nilai_tool_sama_dengan_modul_pemiliknya() -> None:
    """Skema tool menyalin batas modul pemilik — salinan yang menyimpang menolak yang sah
    atau meneruskan yang pasti ditolak sesudah gerbang."""
    alat = REGISTRI.alat
    status_selesai = habits.CatatPenyelesaian.model_fields["status"].annotation
    salinan = {
        "habit.complete.status": (
            alat["habit.complete"].input["status"].enum,
            list(get_args(status_selesai)),
        ),
        "goal.list.status": (
            alat["goal.list"].input["status"].enum,
            list(get_args(goals.StatusGoal)),
        ),
        "recommendation.create.domain": (
            sorted(alat["recommendation.create"].input["domain"].enum or []),
            sorted(intelligence.DOMAIN),
        ),
        "memory.search.batas": (alat["memory.search"].input["batas"].max, memory.MAKS_HASIL),
    }
    menyimpang = sorted(n for n, (skema, modul) in salinan.items() if skema != modul)
    assert not menyimpang, f"skema tool menyimpang dari modul pemiliknya: {menyimpang}"


async def test_pemanggilan_agent_ikut_melewati_gerbang() -> None:
    """K-14 — agent.habit (R2) ditolak gerbang yang menolak R2; agent.coach (R1) lolos."""
    gerbang = _GerbangPencatat(tolak_mulai=2)
    dipanggil: list[tuple[str, str]] = []

    async def pelaksana_agent(nama: str, pesan: str, induk: Jalannya) -> dict[str, Any]:
        dipanggil.append((nama, pesan))
        return {"teks": "ok", "confidence": 0.5, "rationale": ["uji"]}

    p = _pelaksana(gerbang)
    orkestrator = _jalannya("orchestrator-agent")

    with pytest.raises(AlatDitolak) as galat:
        await _panggil(
            p, orkestrator, "agent.habit", {"pesan": "tandai lari"}, pelaksana_agent=pelaksana_agent
        )
    keluaran = await _panggil(
        p,
        orkestrator,
        "agent.coach",
        {"pesan": "bagaimana tidurku"},
        pelaksana_agent=pelaksana_agent,
    )

    assert galat.value.kode == "perlu_izin"
    assert gerbang.ditanya == ["agent.habit", "agent.coach"], "pemanggilan agent melewati gerbang"
    assert dipanggil == [("coach-agent", "bagaimana tidurku")], "agent yang ditolak tetap dipanggil"
    assert keluaran["teks"] == "ok"
    assert orkestrator.alat_dipakai == ["agent.coach"]
    assert orkestrator.risiko_tertinggi == 1


async def test_keluaran_di_luar_skema_adalah_cacat() -> None:
    """mood.recent tanpa catatan bebas (C-32): implementasi yang membocorkannya gagal keras."""

    async def bocor(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
        return {"items": [], "note": "tulisan pengguna"}

    with pytest.raises(RuntimeError, match="tidak dinyatakan"):
        await _panggil(
            _pelaksana(_GerbangPencatat(), **{"mood.recent": bocor}),
            _jalannya("coach-agent"),
            "mood.recent",
            {},
        )


def test_keluaran_kosong_hanya_bila_skemanya_nullable() -> None:
    periksa_keluaran(
        REGISTRI.alat["habit.streak"], {"current": 1, "longest": 2, "completion_rate_30d": None}
    )
    with pytest.raises(RuntimeError, match="kosong"):
        periksa_keluaran(REGISTRI.alat["habit.streak"], {"current": None, "longest": 2})
    with pytest.raises(RuntimeError, match="bukan integer"):
        periksa_keluaran(REGISTRI.alat["habit.streak"], {"current": True, "longest": 2})
