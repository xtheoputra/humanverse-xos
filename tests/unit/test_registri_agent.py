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
    """habit-agent — hanya `habits`, juga lewat tool-nya. coach-agent membaca `mood` (C-32)
    dan `memory.search` menyentuh `journal_raw`: sebagai pihak ketiga ia melanggar aturan 6
    apa pun scope yang ditambahkan, jadi kasus per scope menjadi buta (8 Okt 2026)."""
    m["habit-agent"]["kind"] = "third_party"
    m["habit-agent"]["memory"]["read"].append(scope)


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
    ("6", "pihak ketiga meminta mood (C-32)", lambda a, m: _pihak_ketiga(m, "mood")),
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


# ── Tinjauan Sprint 4 (E-206 · E-207) ─────────────────────────────────────────────


def _pihak_ketiga_lewat_tool(a: Mentah, m: Mentah) -> None:
    """Scope yang diminta LEWAT tool — bukan lewat `memory.read` manifest."""
    a["jurnal.baca"] = {
        **copy.deepcopy(a["goal.list"]),
        "name": "jurnal.baca",
        "scopes": ["journal_raw"],
        "input": {},
    }
    m["coach-agent"]["kind"] = "third_party"
    m["coach-agent"]["tools"].append("jurnal.baca")


KASUS_TINJAUAN: list[tuple[str, str, Callable[[Mentah, Mentah], None]]] = [
    ("6", "pihak ketiga meminta journal_raw lewat tool", _pihak_ketiga_lewat_tool),
    (
        "bentuk",
        "capability bukan snake_case",
        lambda a, m: m["coach-agent"].update(capabilities=["Daily Coaching!"]),
    ),
    ("bentuk", "capability kosong", lambda a, m: m["coach-agent"].update(capabilities=[""])),
    (
        "bentuk",
        "keluaran array tanpa isinya",
        lambda a, m: a["habit.list"]["output"].update(items="array"),
    ),
    (
        "bentuk",
        "keluaran object tanpa medan",
        lambda a, m: a["checkin.get"]["output"].update(checkin={"type": "object", "fields": {}}),
    ),
    (
        "bentuk",
        "keluaran array dengan fields",
        lambda a, m: a["memory.search"]["output"].update(
            perlu_izin={"type": "array", "fields": {"x": "string"}}
        ),
    ),
    (
        "bentuk",
        "keluaran skalar yang tidak dikenal",
        lambda a, m: a["habit.streak"]["output"].update(current="bilangan"),
    ),
]


@pytest.mark.parametrize(
    ("aturan", "_maksud", "rusak"),
    KASUS_TINJAUAN,
    ids=[f"{k[0]}-{k[1]}" for k in KASUS_TINJAUAN],
)
def test_registry_yang_melanggar_ditolak_tinjauan(
    aturan: str, _maksud: str, rusak: Callable[[Mentah, Mentah], None]
) -> None:
    test_manifest_yang_melanggar_ditolak(aturan, _maksud, rusak)


def test_tool_tanpa_risk_level_tidak_menyembunyikan_pelanggaran_lainnya() -> None:
    """E-207 (K-29 (1): *SEMUA pelanggaran dilaporkan sekaligus*): tool tanpa `risk_level`
    dulu berhenti di aturan 8 — scope di luar daftar resmi di tool yang sama hilang."""
    alat, manifest = copy.deepcopy(ALAT), copy.deepcopy(MANIFEST)
    alat["goal.list"].pop("risk_level")
    alat["goal.list"]["scopes"] = ["finance"]

    with pytest.raises(RegistriTidakSah) as galat:
        validasi_registri(alat, manifest)

    aturan = {p.aturan for p in galat.value.pelanggaran if p.subjek == "goal.list"}
    assert aturan == {"8", "2"}, f"pelanggaran lain tersembunyi di balik aturan 8: {aturan}"


# ── Tinjauan penegak buta Sprint 4 (G2-registri) ──────────────────────────────────
# Tiap kasus di bawah dulu LOLOS seluruh suite bila pemeriksanya dirusak: kasus di
# atas memakai tool R0 untuk aturan 7, hanya `memory.read` untuk aturan 2 · 6 · 9, dan
# tidak pernah mengirim medan asing, teks di tempat angka, atau nama yang tidak cocok.


def _pihak_ketiga_menulis(m: Mentah, scope: str) -> None:
    """Scope terlarang lewat `memory.write` SAJA. `habit-agent`, bukan `coach-agent`:
    tool coach (`memory.search`) sudah menyentuh `journal_raw`, jadi aturan 6 berbunyi
    lewat tool-nya walau `memory.write` tidak diperiksa sama sekali."""
    m["habit-agent"]["kind"] = "third_party"
    m["habit-agent"]["memory"]["write"].append(scope)


KASUS_BUTA: list[tuple[str, str, Callable[[Mentah, Mentah], None]]] = [
    # Aturan 7 lahir dari *send low-risk message* — tool R2 yang sampai ke orang lain.
    (
        "7",
        "tool R2 yang menyentuh orang lain",
        lambda a, m: a["habit.complete"].update(reaches_third_party=True),
    ),
    # Aturan 2 untuk scope TOOL: gerbang menanyai mesin izin scope-scope ini (E-191).
    (
        "2",
        "scope tool di luar daftar resmi",
        lambda a, m: a["goal.list"]["scopes"].append("fashion"),
    ),
    (
        "2",
        "scope tulis manifest di luar daftar resmi",
        lambda a, m: m["coach-agent"]["memory"]["write"].append("fashion"),
    ),
    ("6", "pihak ketiga menulis journal_raw", lambda a, m: _pihak_ketiga_menulis(m, "journal_raw")),
    ("9", "pihak ketiga menulis lokasi", lambda a, m: _pihak_ketiga_menulis(m, "location")),
    # Bentuk ketat: medan yang tidak dikenal DITOLAK — janji yang salah tempat
    # (`requires_confirmation` di manifest) atau salah eja tidak berlaku diam-diam.
    (
        "bentuk",
        "medan manifest yang tidak dikenal",
        lambda a, m: m["coach-agent"].update(requires_confirmation=True),
    ),
    (
        "bentuk",
        "medan tool salah eja",
        lambda a, m: a["habit.list"].update(menyaring_ijin=True),
    ),
    # E-193: penyaring izin hanya BACAAN TANPA EFEK — tulisan selalu ditanya gerbang.
    (
        "bentuk",
        "tool penyaring izin yang menulis",
        lambda a, m: a["memory.search"].update(side_effects="writes_user_data"),
    ),
    ("A-1", "risk sebagai properti agent", lambda a, m: m["habit-agent"].update(risk=2)),
    # Dua berkas bernama sama saling menimpa diam-diam di `alat[a.name]`.
    (
        "bentuk",
        "nama tool berbeda dengan nama berkasnya",
        lambda a, m: a["habit.list"].update(name="habit.lists"),
    ),
    # Tanpa koersi: `'0'` bukan `0`, `'0.99'` bukan `0.99` (E-170 di sisi registry).
    (
        "bentuk",
        "risk_level berupa teks",
        lambda a, m: a["goal.list"].update(risk_level="0"),
    ),
    (
        "bentuk",
        "gerbang keselamatan berupa teks",
        lambda a, m: m["coach-agent"]["evaluation"]["gates"].update(safety="0.99"),
    ),
]


@pytest.mark.parametrize(
    ("aturan", "_maksud", "rusak"), KASUS_BUTA, ids=[f"{k[0]}-{k[1]}" for k in KASUS_BUTA]
)
def test_registry_yang_melanggar_ditolak_buta(
    aturan: str, _maksud: str, rusak: Callable[[Mentah, Mentah], None]
) -> None:
    test_manifest_yang_melanggar_ditolak(aturan, _maksud, rusak)


def test_nama_manifest_berbeda_dengan_berkasnya_dilaporkan_bukan_meledak() -> None:
    """Pelanggaran dilaporkan SEMUA sekaligus sebagai `RegistriTidakSah` (K-29 (1)) — nama
    manifest yang tidak cocok dengan berkasnya dulu hanya terlihat sebagai `KeyError` di
    tengah perakitan registry, tanpa satu pun pelanggaran lain."""
    manifest = copy.deepcopy(MANIFEST)
    manifest["coach"] = manifest.pop("coach-agent")

    try:
        validasi_registri(copy.deepcopy(ALAT), manifest)
    except RegistriTidakSah as galat:
        dilanggar = {(p.subjek, p.aturan) for p in galat.pelanggaran}
    except Exception as galat:
        pytest.fail(
            f"nama manifest ≠ nama berkas meledak sebagai {type(galat).__name__}"
            " — bukan pelanggaran yang dilaporkan"
        )
    else:
        dilanggar = set()

    assert ("coach", "bentuk") in dilanggar, (
        f"nama manifest ≠ nama berkas tidak dilaporkan: {dilanggar}"
    )


@pytest.mark.parametrize("status", ["draft", "deprecated", "disabled"])
def test_hanya_manifest_aktif_yang_dimuat(status: str) -> None:
    """Aturan 5 dihitung atas `status: active` saja, dan hanya itu yang boleh BERJALAN —
    draft yang dimuat adalah agent yang belum lulus evaluasinya menjawab pengguna."""
    manifest = copy.deepcopy(MANIFEST)
    manifest["orchestrator-agent"]["status"] = status

    r = validasi_registri(copy.deepcopy(ALAT), manifest)

    assert "orchestrator-agent" not in r.agent, (
        f"manifest `status: {status}` dimuat sebagai agent aktif"
    )
    assert "orchestrator-agent" not in r.mentah


def test_tool_tulis_dibatasi_lebih_ketat_daripada_bacaan() -> None:
    """Tiap tulisan agent yang lolos adalah baris baru atau aksi yang harus diurungkan
    pengguna; bacaan tidak. Tulisan dibatasi `20/min/user`, bacaan `60/min/user` —
    batas yang dilonggarkan tanpa sengaja tidak terlihat di uji mana pun selain ini
    (angkanya belum ada di tabel spec/05: tabel itu tidak punya kolom `rate_limit`)."""
    alat = muat_registri().alat
    tulis = {n: a.rate_limit for n, a in alat.items() if a.kind == "write"}

    assert tulis == dict.fromkeys(
        ("habit.complete", "memory.write", "recommendation.create"), "20/min/user"
    ), f"batas laju tool tulis ≠ 20/min/user: {tulis}"
    assert {a.rate_limit for a in alat.values() if a.kind == "read"} == {"60/min/user"}


def test_batas_laju_tiap_tool_sama_dengan_tabel_spec05() -> None:
    """Kolom *Batas laju* spec/05 = `rate_limit` YAML tiap tool — dulu angka ini hidup di
    YAML tanpa sumber di kontraknya (tinjauan penegak buta Sprint 4)."""
    import re
    from pathlib import Path

    teks = (Path(__file__).resolve().parents[2] / "spec/05-AGENT-CONTRACTS.md").read_text(
        encoding="utf-8"
    )
    tabel = dict(
        re.findall(r"^\| `([a-z][a-z0-9_.]*)` \|.*\| (\d+/(?:min|hour)/user) \|$", teks, re.M)
    )

    assert tabel, "kolom batas laju spec/05 tidak terbaca"
    assert {n: a.rate_limit for n, a in muat_registri().alat.items()} == tabel, (
        "batas laju tool ≠ tabel spec/05"
    )
