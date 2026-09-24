"""spec/03 ⟷ `events.REGISTRY` — nama dan bentuk event V0 tidak bisa menyimpang dari dokumennya.

Baris ✅ tabel spec/03 dibaca DARI dokumennya (arch/11 §2 aturan 1), lalu
dibandingkan dengan registry kode: jenis yang sama, medan wajib yang sama, medan
opsional (`nama?`) yang sama. Kalau tabelnya hilang, uji ini GAGAL — bukan lulus
karena tidak menemukan apa pun untuk diperiksa.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from hvx.modules.events import REGISTRY, EventTidakSah, payload_sah

SPEC03 = Path(__file__).resolve().parents[2] / "spec" / "03-EVENT-CONTRACTS.md"


def _v0_dari_spec03() -> dict[str, tuple[set[str], set[str]]]:
    """{event_type: (medan wajib, medan opsional)} dari baris ✅ spec/03."""
    teks = SPEC03.read_text(encoding="utf-8")
    hasil: dict[str, tuple[set[str], set[str]]] = {}
    for jenis, isi in re.findall(r"^\| `([a-z_]+\.[a-z_]+)` \| ✅ \| `\{([^}]*)\}`", teks, re.M):
        medan = [m.strip() for m in isi.split(",") if m.strip()]
        wajib = {m for m in medan if not m.endswith("?")}
        opsional = {m.rstrip("?").removesuffix("[]") for m in medan if m.endswith("?")}
        hasil[jenis] = ({m.removesuffix("[]") for m in wajib}, opsional)
    return hasil


def test_tabel_spec03_terbaca() -> None:
    assert len(_v0_dari_spec03()) >= 8, "baris ✅ spec/03 tidak terbaca — pemeriksa buta"


def test_registry_sama_dengan_baris_v0_spec03() -> None:
    spec = _v0_dari_spec03()

    assert set(REGISTRY) == set(spec), (
        f"hanya di kode: {sorted(set(REGISTRY) - set(spec))} · "
        f"hanya di spec/03: {sorted(set(spec) - set(REGISTRY))}"
    )
    salah = []
    for jenis, (_versi, model) in REGISTRY.items():
        wajib = {n for n, f in model.model_fields.items() if f.is_required()}
        opsional = {n for n, f in model.model_fields.items() if not f.is_required()}
        if (wajib, opsional) != spec[jenis]:
            salah.append(f"{jenis}: kode {sorted(wajib)}/{sorted(opsional)} ≠ spec {spec[jenis]}")
    assert not salah, "payload kode ≠ spec/03:\n" + "\n".join(salah)


def test_isi_jurnal_tidak_pernah_masuk_event() -> None:
    """spec/03: `journal.created` hanya `word_count` — isi jurnal tidak mengalir ke konsumen."""
    with pytest.raises(EventTidakSah):
        payload_sah("journal.created", {"word_count": 3, "body": "isi pribadi"})


@pytest.mark.parametrize(
    ("jenis", "payload"),
    [
        ("habit.deleted", {}),  # tidak terdaftar
        ("mood.logged", {}),  # valence wajib
        ("mood.logged", {"valence": 9}),
        ("habit.completed", {"status": "skipped"}),  # skipped = habit.skipped
        ("goal.completed", {"days_taken": -1}),
        ("checkin.logged", {"energy": 3, "for_date": "2026-09-24", "mood": 2}),  # tak dikenal
        ("habit.completed", {"status": "done"}),  # for_date & completion_id wajib (3.2)
    ],
)
def test_payload_di_luar_kontrak_ditolak(jenis: str, payload: dict[str, object]) -> None:
    with pytest.raises(EventTidakSah):
        payload_sah(jenis, payload)


def test_payload_sah_dinormalkan_ke_json_tanpa_medan_kosong() -> None:
    versi, isi = payload_sah(
        "checkin.logged", {"energy": 2, "sleep_hours": 7.5, "for_date": "2026-09-24"}
    )

    assert versi == 1
    # `sleep_hours` angka JSON, seperti di spec/04 (E-170) — bukan string "7.5".
    assert isi == {"energy": 2, "sleep_hours": 7.5, "for_date": "2026-09-24"}
