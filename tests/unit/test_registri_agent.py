"""spec/07 4.2 — registry agent: *9 aturan validasi spec/05 ditegakkan; manifest salah DITOLAK*.

Tiap aturan dibuktikan dengan manifest atau tool yang melanggar HANYA aturan itu,
dibuat dari registry V0 yang sah — dan registry V0 itu sendiri dibandingkan dengan
tabel spec/05 yang dibaca pemeriksa dokumen (A-2, A-3): kode dan dokumen tidak
bisa menyimpang diam-diam.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from importlib import resources
from typing import Any

import pytest
import yaml
from test_penegak import _modul

from hvx.modules import identity
from hvx.modules.agents import RegistriTidakSah, muat_registri, validasi_registri

Mentah = dict[str, dict[str, Any]]


def _baca(sub: str) -> Mentah:
    akar = resources.files("hvx.modules.agents").joinpath(sub)
    return {
        b.name.removesuffix(".yaml"): yaml.safe_load(b.read_text(encoding="utf-8"))
        for b in akar.iterdir()
        if b.name.endswith(".yaml")
    }


ALAT, MANIFEST = _baca("alat"), _baca("manifest")


def test_registry_v0_termuat_empat_agent_dua_belas_tool() -> None:
    r = muat_registri()

    assert sorted(r.agent) == ["coach-agent", "habit-agent", "memory-agent", "orchestrator-agent"]
    assert len(r.alat) == 12
    assert {a.name for a in r.alat.values() if a.kind == "agent"} == {
        "agent.coach",
        "agent.habit",
        "agent.memory",
    }


def test_registry_sama_dengan_tabel_spec05() -> None:
    """Tabel yang dibaca pemeriksa dokumen A-2/A-3 — satu sumber bagi keduanya."""
    dok = _modul("periksa_dokumen")
    tool_spec, agent_spec = dok._registry_tool(), dok._agent_v0()
    r = muat_registri()

    assert tool_spec, "tabel tool spec/05 tidak terbaca — pemeriksa buta"
    assert {n: (a.kind, a.risk_level) for n, a in r.alat.items()} == tool_spec
    assert {n: (m.pagu_risiko, sorted(m.tools)) for n, m in r.agent.items()} == {
        n: (pagu, sorted(tools)) for n, (pagu, tools) in agent_spec.items()
    }


def test_memory_agent_tidak_pernah_menyentuh_journal_raw() -> None:
    """spec/05 — naskah 5 §15: *private journal* di daftar DENY, bahkan bagi agent ini."""
    m = muat_registri().agent["memory-agent"]

    assert "journal_raw" not in set(m.memory.read) | set(m.memory.write)
    assert set(m.memory.read) == set(identity.SCOPE_RESMI) - {"journal_raw"}


def _pihak_ketiga(m: Mentah, scope: str) -> None:
    m["coach-agent"]["kind"] = "third_party"
    m["coach-agent"]["memory"]["read"].append(scope)


def _agen_kedua(m: Mentah) -> None:
    m["coach-agent-v2"] = {**copy.deepcopy(m["coach-agent"]), "version": "1.1.0"}


def _tool_menyentuh_orang_lain(a: Mentah, m: Mentah) -> None:
    a["habit.list"]["reaches_third_party"] = True


KASUS: list[tuple[str, str, Callable[[Mentah, Mentah], None]]] = [
    ("1", "tool di luar registry", lambda a, m: m["coach-agent"]["tools"].append("weather.get")),
    (
        "2",
        "scope di luar daftar resmi",
        lambda a, m: m["coach-agent"]["memory"]["read"].append("fashion"),
    ),
    (
        "3",
        "tool lebih berisiko dari pagu",
        lambda a, m: m["coach-agent"]["tools"].append("habit.complete"),
    ),
    (
        "4",
        "gerbang keselamatan di bawah 0,95",
        lambda a, m: m["coach-agent"]["evaluation"]["gates"].update(safety=0.9),
    ),
    (
        "4",
        "tanpa gerbang keselamatan",
        lambda a, m: m["coach-agent"]["evaluation"]["gates"].pop("safety"),
    ),
    ("5", "dua versi aktif satu nama", lambda a, m: _agen_kedua(m)),
    ("6", "pihak ketiga meminta journal_raw", lambda a, m: _pihak_ketiga(m, "journal_raw")),
    ("7", "tool menyentuh orang lain di bawah R3", _tool_menyentuh_orang_lain),
    ("8", "tool tanpa risk_level", lambda a, m: a["goal.list"].pop("risk_level")),
    ("9", "pihak ketiga meminta lokasi", lambda a, m: _pihak_ketiga(m, "location")),
    (
        "A-1",
        "risk_level sebagai properti agent",
        lambda a, m: m["habit-agent"].update(risk_level=2),
    ),
    (
        "K-14",
        "entri agent lebih murah dari agent yang dipanggil",
        lambda a, m: a["agent.habit"].update(risk_level=1),
    ),
    ("K-14", "entri agent tanpa agent", lambda a, m: m.pop("memory-agent")),
    (
        "bentuk",
        "tangga R dipakai untuk otonomi L",
        lambda a, m: m["coach-agent"]["autonomy"].update(max_level="R2"),
    ),
    # Batas nilai masukan (4.3) — batas yang salah tempat diam-diam tidak pernah berlaku.
    (
        "bentuk",
        "enum pada medan bilangan",
        lambda a, m: a["mood.recent"]["input"]["hari"].update(enum=["7"]),
    ),
    (
        "bentuk",
        "min pada medan teks",
        lambda a, m: a["goal.list"]["input"]["status"].update(min=1),
    ),
    (
        "bentuk",
        "tulisan yang menyaring izinnya sendiri",
        lambda a, m: a["memory.write"].update(menyaring_izin=True),
    ),
    (
        "bentuk",
        "min lebih besar daripada max",
        lambda a, m: a["mood.recent"]["input"]["hari"].update(min=31, max=1),
    ),
]


@pytest.mark.parametrize(
    ("aturan", "_maksud", "rusak"), KASUS, ids=[f"{k[0]}-{k[1]}" for k in KASUS]
)
def test_manifest_yang_melanggar_ditolak(
    aturan: str, _maksud: str, rusak: Callable[[Mentah, Mentah], None]
) -> None:
    alat, manifest = copy.deepcopy(ALAT), copy.deepcopy(MANIFEST)
    rusak(alat, manifest)

    try:
        validasi_registri(alat, manifest)
    except RegistriTidakSah as galat:
        dilanggar = {p.aturan for p in galat.pelanggaran}
    else:
        dilanggar = set()  # diterima utuh

    assert aturan in dilanggar, (
        f"aturan {aturan} tidak ditegakkan — {_maksud} — yang terbaca: {dilanggar}"
    )


def test_semua_pelanggaran_dilaporkan_sekaligus() -> None:
    """Aturan 9 tidak boleh tersembunyi di balik aturan 2 — keduanya dilaporkan."""
    alat, manifest = copy.deepcopy(ALAT), copy.deepcopy(MANIFEST)
    _pihak_ketiga(manifest, "location")

    with pytest.raises(RegistriTidakSah) as galat:
        validasi_registri(alat, manifest)

    assert {"2", "9"} <= {p.aturan for p in galat.value.pelanggaran}


def test_galat_bentuk_tidak_memantulkan_isi_manifest() -> None:
    manifest = copy.deepcopy(MANIFEST)
    manifest["coach-agent"]["max_risk"] = "RAHASIA-SEKALI"

    with pytest.raises(RegistriTidakSah) as galat:
        validasi_registri(copy.deepcopy(ALAT), manifest)

    assert "RAHASIA" not in str(galat.value), str(galat.value)
