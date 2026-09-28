"""spec/07 4.3 — *tool di luar registry tidak bisa dipanggil; pemanggilan agent lewat gerbang*.

Tanpa basis data: yang diuji di sini adalah JALAN tiap pemanggilan — registry, manifest
pemanggil, masukan ketat, gerbang, keluaran — dengan implementasi dan gerbang tiruan
yang mencatat apakah mereka disentuh. Implementasi sungguhan: `test_alat_v0.py`.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any, get_args
from uuid import uuid4

import pytest

from hvx.modules import goals, habits, intelligence, memory, platform
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
    periksa_masukan,
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


def _nilai_sah(spek: Any) -> Any:
    """Nilai terkecil yang sah menurut skema keluaran — termasuk susunan bersarang."""
    tipe = spek if isinstance(spek, str) else spek.type
    if "null" in tipe:
        return None
    if isinstance(spek, str):
        return _NILAI[tipe.strip()]()
    if spek.items is not None:
        return []
    return {n: _nilai_sah(s) for n, s in spek.fields.items()}


def _tiruan(alat: Alat) -> Any:
    """Implementasi yang selalu berhasil dengan keluaran sah — kerusakan di JALAN
    pemanggilannya terbaca sebagai "tidak ditolak", bukan sebagai galat lain."""

    async def jalan(k: KonteksAlat, m: dict[str, Any]) -> dict[str, Any]:
        return {n: _nilai_sah(s) for n, s in alat.output.items()}

    return jalan


def _pelaksana(gerbang: _GerbangPencatat, *, pembatas: Any = None, **ganti: Any) -> PelaksanaAlat:
    tiruan = {n: _tiruan(a) for n, a in REGISTRI.alat.items() if a.kind != "agent"}
    agent = {n: i for n, i in IMPLEMENTASI.items() if n.startswith("agent.")}
    return PelaksanaAlat(REGISTRI, {**tiruan, **agent, **ganti}, gerbang, pembatas)


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
        (  # …juga untuk `number`: dulu lolos, lalu meledak `internal` di Decimal pemiliknya
            "recommendation.create",
            {"domain": "habit", "title": "t", "confidence": True, "rationale": ["a"]},
        ),
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


# ── Tinjauan Sprint 4: E-204 (pemeriksa pemilik, NaN, rentang tanggal) · E-206 (bersarang) ──

_PASTI_DITOLAK = [
    # platform.Tanggal (spec/04 1900-01-01 … 2999-12-31) — juga untuk tool BACA
    ("habit-agent", "habit.complete", {"habit_id": str(uuid4()), "for_date": "0999-12-31",
                                       "status": "done"}),
    ("coach-agent", "habit.list", {"for_date": "3000-01-01"}),
    # CatatPenyelesaian: tier_used tidak berarti untuk skipped — hanya pemiliknya yang tahu
    ("habit-agent", "habit.complete", {"habit_id": str(uuid4()), "for_date": "2026-09-24",
                                       "status": "skipped", "tier_used": 0}),
    # memory.periksa_ingatan: isi 1–4.000 karakter berisi
    ("memory-agent", "memory.write", {"scope": "coaching_notes", "isi": "   "}),
    ("memory-agent", "memory.write", {"scope": "coaching_notes", "isi": "x" * 4001}),
    # `number` min 0 max 1 — NaN lolos kedua perbandingan; tak hingga bukan bilangan hingga
    ("coach-agent", "recommendation.create", {"domain": "habit", "title": "t",
                                              "confidence": float("nan"), "rationale": ["a"]}),
    ("coach-agent", "recommendation.create", {"domain": "habit", "title": "t",
                                              "confidence": float("inf"), "rationale": ["a"]}),
    # intelligence.periksa_rekomendasi: judul berisi, alasan berisi
    ("coach-agent", "recommendation.create", {"domain": "habit", "title": "   ",
                                              "confidence": 0.5, "rationale": ["a"]}),
    ("coach-agent", "recommendation.create", {"domain": "habit", "title": "t",
                                              "confidence": 0.5, "rationale": []}),
]  # fmt: skip


@pytest.mark.parametrize(("agent", "nama", "masukan"), _PASTI_DITOLAK)
async def test_masukan_yang_pasti_ditolak_pemiliknya_tidak_sampai_ke_gerbang(
    agent: str, nama: str, masukan: dict[str, Any]
) -> None:
    """E-204 (tinjauan kontrak Sprint 4): tidak ada konfirmasi R2 untuk aksi yang pasti
    ditolak pemilik datanya — implementasi SUNGGUHAN, dengan pemeriksanya."""
    gerbang = _GerbangPencatat()
    pelaksana = PelaksanaAlat(REGISTRI, IMPLEMENTASI, gerbang, None)

    try:
        await _panggil(pelaksana, _jalannya(agent), nama, masukan)
    except AlatDitolak as galat:
        kode: str | None = galat.kode
    except Exception as galat:
        kode = type(galat).__name__
    else:
        kode = None

    assert (kode, gerbang.ditanya) == ("masukan_salah", []), (
        f"{nama} ({kode}) sampai ke gerbang — pengguna diminta mengizinkan aksi yang pasti ditolak"
    )


@pytest.mark.parametrize(
    ("agent", "nama", "masukan"),
    [
        ("habit-agent", "habit.complete",
         {"habit_id": str(uuid4()), "for_date": "2026-09-24", "status": "done", "tier_used": 0}),
        ("memory-agent", "memory.write", {"scope": "coaching_notes", "isi": "aku alergi kacang"}),
        ("coach-agent", "recommendation.create",
         {"domain": "habit", "title": "Tidur lebih awal", "confidence": 0.5, "rationale": ["a"]}),
    ],
)  # fmt: skip
async def test_masukan_sah_lolos_pemeriksa_dan_ditanyakan_gerbang(
    agent: str, nama: str, masukan: dict[str, Any]
) -> None:
    """Pemeriksa tidak menolak yang sah — pemanggilannya sampai ke gerbang."""
    gerbang = _GerbangPencatat(tolak_mulai=0)

    with pytest.raises(AlatDitolak, match="risk"):
        await _panggil(
            PelaksanaAlat(REGISTRI, IMPLEMENTASI, gerbang, None), _jalannya(agent), nama, masukan
        )

    assert gerbang.ditanya == [nama]


_BOCOR_BERSARANG = [
    ("mood.recent", {"terpotong": False, "items": [
        {"valence": 3, "label": None, "occurred_at": "2026-09-24T06:30:00+00:00",
         "note": "tulisan bebas pengguna"}]}),
    ("checkin.get", {"checkin": {
        "for_date": "2026-09-24", "energy": 2, "focus": 3, "sleep_hours": 5.5,
        "note": "tulisan bebas pengguna"}}),
    ("habit.list", {"items": [
        {"id": str(uuid4()), "title": "Lari", "period": "daily", "target_count": 1, "tiers": [],
         "day": {"for_date": "2026-09-24", "status": None, "suggested_tier": None,
                 "energy": None, "note": "tulisan bebas pengguna"}}]}),
    ("memory.search", {"perlu_izin": [], "items": [
        {"id": str(uuid4()), "kind": "episodic", "scope": "mood", "content": "x", "skor": 1.0,
         "user_id": str(uuid4())}]}),
    ("agent.coach", {"teks": "x", "confidence": 0.5, "rationale": [{"isi": "bukan kalimat"}]}),
    ("goal.list", {"terpotong": False, "items": ["bukan objek"]}),
]  # fmt: skip


@pytest.mark.parametrize(("nama", "keluaran"), _BOCOR_BERSARANG)
def test_keluaran_bersarang_di_luar_skema_adalah_cacat(nama: str, keluaran: dict[str, Any]) -> None:
    """E-206: `items: array` saja tidak menyatakan isinya — catatan bebas (C-32) di dalam
    `items[]` atau `checkin{}` lolos pemeriksa yang dijanjikan menjaganya."""
    with pytest.raises(RuntimeError, match=r"tidak dinyatakan|bukan"):
        periksa_keluaran(REGISTRI.alat[nama], keluaran)


def test_keluaran_bersarang_yang_sah_diterima() -> None:
    periksa_keluaran(
        REGISTRI.alat["habit.list"],
        {"items": [
            {"id": str(uuid4()), "title": "Lari", "period": "daily", "target_count": 1,
             "tiers": ["jalan kaki", None],
             "day": {"for_date": "2026-09-24", "status": "done", "suggested_tier": 0,
                     "energy": 2}},
            {"id": str(uuid4()), "title": "Baca", "period": "daily", "target_count": 1,
             "tiers": []},
        ]},
    )  # fmt: skip
    periksa_keluaran(REGISTRI.alat["checkin.get"], {"checkin": None})


@pytest.mark.parametrize("nilai", [float("nan"), float("inf"), float("-inf")])
def test_bilangan_tak_hingga_ditolak_semua_tool(nilai: float) -> None:
    """E-204: `NaN` lolos `min`/`max` — kedua perbandingannya False. Ditolak di pelaksana,
    untuk tiap medan `number`, bukan hanya di pemilik data yang kebetulan memeriksanya."""
    alat = REGISTRI.alat["recommendation.create"]
    masukan = {"domain": "habit", "title": "t", "confidence": nilai, "rationale": ["x"]}

    with pytest.raises(AlatDitolak, match="confidence wajib bertipe number"):
        periksa_masukan(alat, masukan)


def test_pemeriksa_pemilik_data_menolak_yang_ditolak_layanannya() -> None:
    """Pemeriksa murni modul pemilik = aturan yang SAMA dengan layanannya (E-204)."""
    from decimal import Decimal

    with pytest.raises(ValueError, match="bilangan hingga"):
        intelligence.periksa_rekomendasi(
            domain="habit", title="t", body=None, confidence=Decimal("NaN"), rationale=["x"]
        )
    with pytest.raises(ValueError, match="isi memori"):
        memory.periksa_ingatan(scope="coaching_notes", isi=" \n ")
    assert memory.periksa_ingatan(scope="coaching_notes", isi=" a   b ") == "a b"


# ── Penegak buta Sprint 4 (G3): batas laju per tool · kapan jatah dipakai · boolean
# ketat · risiko run = yang tertinggi ─────────────────────────────────────────────


class _PembatasHitung:
    """Pembatas laju tiruan: tepat `jumlah` jatah per (nama batas, subjek), TANPA pengisian
    ulang. Yang diuji di sini JALAN pemanggilan — ember mana yang dipakai, dan kapan —
    bukan GCRA-nya (1.7, `test_batas_laju.py`): GCRA sungguhan mengisi satu jatah tiap
    detik, jadi uji "60 lalu yang ke-61" di mesin yang lambat berkedip."""

    def __init__(self) -> None:
        self.dipakai: Counter[tuple[str, str]] = Counter()

    async def ambil(self, batas: platform.BatasLaju, subjek: str) -> platform.HasilLaju:
        kunci = (batas.nama, subjek)
        if self.dipakai[kunci] >= batas.jumlah:
            return platform.HasilLaju(lolos=False, sisa=0, coba_lagi_ms=1_000)
        self.dipakai[kunci] += 1
        return platform.HasilLaju(
            lolos=True, sisa=batas.jumlah - self.dipakai[kunci], coba_lagi_ms=0
        )


async def _kode(p: PelaksanaAlat, j: Jalannya, nama: str, masukan: dict[str, Any]) -> str | None:
    """Kode penolakan satu pemanggilan; `None` bila dijalankan."""
    try:
        await _panggil(p, j, nama, masukan)
    except AlatDitolak as galat:
        return galat.kode
    return None


def _selesai_sah() -> dict[str, Any]:
    return {"habit_id": str(uuid4()), "for_date": "2026-09-24", "status": "done"}


async def test_batas_laju_milik_tiap_tool_bukan_satu_ember() -> None:
    """spec/05: `rate_limit` adalah milik TIAP tool. Satu ember untuk semua tool membuat
    agent yang banyak membaca (habit.list 60/min) kehabisan jatah untuk MENULIS
    (habit.complete 20/min) — dan batas tool tulis yang lebih ketat tidak berarti apa-apa."""
    p = _pelaksana(_GerbangPencatat(), pembatas=_PembatasHitung())
    j = _jalannya("habit-agent")

    for _ in range(60):
        assert await _kode(p, j, "habit.list", {}) is None
    ke_61 = await _kode(p, j, "habit.list", {})
    tulis = await _kode(p, j, "habit.complete", _selesai_sah())

    assert ke_61 == "terlalu_sering", "batas laju habit.list tidak ditegakkan"
    assert tulis is None, (
        f"jatah habit.list menghabiskan jatah habit.complete ({tulis}) — batas laju bukan per tool"
    )


async def test_batas_laju_dipakai_sebelum_gerbang() -> None:
    """spec/07 4.3 — urutannya batas laju LALU gerbang. Terbalik, pemanggilan yang ditolak
    gerbang tidak memakai jatah: agent yang terus memanggil tool yang di-deny ditanyakan
    ke gerbang — dan menulis `audit_logs` `tool_denied` — tanpa batas."""
    gerbang = _GerbangPencatat(tolak_mulai=0)
    p = _pelaksana(gerbang, pembatas=_PembatasHitung())
    j = _jalannya("habit-agent")

    kode = [await _kode(p, j, "habit.complete", _selesai_sah()) for _ in range(21)]

    assert kode[-1] == "terlalu_sering", (
        f"penolakan gerbang tidak memakai jatah batas laju — panggilan ke-21: {kode[-1]}"
    )
    assert len(gerbang.ditanya) == 20, "gerbang ditanya melewati batas laju tool"


_SALAH_TANPA_JATAH = [
    # ditolak skema tool (enum `status`)
    ("skema tool", {"habit_id": str(uuid4()), "for_date": "2026-09-24", "status": "x"}),
    # ditolak pemeriksa pemilik datanya (E-204): tier_used tidak berarti untuk skipped
    ("pemilik data", {"habit_id": str(uuid4()), "for_date": "2026-09-24", "status": "skipped",
                      "tier_used": 0}),
]  # fmt: skip


@pytest.mark.parametrize(
    ("maksud", "salah"), _SALAH_TANPA_JATAH, ids=[s[0] for s in _SALAH_TANPA_JATAH]
)
async def test_masukan_salah_ditolak_tanpa_memakai_jatah(
    maksud: str, salah: dict[str, Any]
) -> None:
    """spec/07 4.3 — masukan diperiksa SEBELUM batas laju: model yang salah menulis
    pemanggilan (20× berturut-turut) tidak boleh menghabiskan jatah pemanggilan sah
    pengguna. Implementasi sungguhan, supaya pemeriksa pemilik datanya ikut berjalan."""
    gerbang = _GerbangPencatat(tolak_mulai=0)
    p = PelaksanaAlat(REGISTRI, IMPLEMENTASI, gerbang, _PembatasHitung())  # type: ignore[arg-type]
    j = _jalannya("habit-agent")

    for _ in range(20):
        assert await _kode(p, j, "habit.complete", salah) == "masukan_salah"
    sah = await _kode(p, j, "habit.complete", _selesai_sah())

    assert sah == "perlu_izin", (
        f"masukan salah ({maksud}) memakai jatah batas laju — pemanggilan sah berikutnya: {sah}"
    )


def _alat_boolean() -> Alat:
    """Tak ada tool V0 bermasukan boolean — tool uji: goal.list dengan satu medan boolean."""
    mentah = REGISTRI.alat["goal.list"].model_dump(by_alias=True)
    mentah["input"] = {"arsip": {"type": "boolean", "required": True}}
    return Alat.model_validate(mentah)


@pytest.mark.parametrize("nilai", [1, 0])
def test_boolean_ketat_bilangan_bukan_boolean(nilai: int) -> None:
    """E-170 di sisi agent: `1` bukan `true` — model yang menulis pemanggilan tidak
    ditaati karena nilainya kebetulan bisa dikoersi."""
    alat = _alat_boolean()

    try:
        diterima: Any = periksa_masukan(alat, {"arsip": nilai})
    except AlatDitolak as galat:
        diterima = galat.kode

    assert diterima == "masukan_salah", f"medan boolean menerima bilangan {nilai!r}: {diterima}"
    assert periksa_masukan(alat, {"arsip": True}) == {"arsip": True}


async def test_risiko_run_yang_tertinggi_bukan_yang_terakhir() -> None:
    """spec/07 4.4 — `agent_runs.risk_level` = risiko TERTINGGI yang dipakai run: tool R2
    lalu tool R0 tetap run R2. Alur V0 kebetulan memanggil tool dengan risiko naik."""
    p = _pelaksana(_GerbangPencatat())
    j = _jalannya("habit-agent")

    await _panggil(p, j, "habit.complete", _selesai_sah())
    await _panggil(p, j, "habit.list", {})

    assert j.risiko_tertinggi == 2, (
        f"risk_level run = risiko tool terakhir ({j.risiko_tertinggi}), bukan yang tertinggi"
    )
