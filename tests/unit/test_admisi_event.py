"""spec/08 7.1 — uji admisi `events` (arch/06 §3) ditegakkan mesin, ketiga syaratnya.

Sebelum 7.1 hanya syarat 3 yang dijaga, dan hanya terhadap empat sumber sekaligus;
syarat 1 (*pengguna bisa mengenalinya*) tersirat dari registry tertutup — jenis baru
cukup ditambahkan ke `REGISTRY` dan baris ✅ spec/03. Kini tiap jenis wajib punya baris
*Uji admisi per event* spec/03 yang lengkap, dan baris itu wajib sama dengan
`events.ADMISI` yang ditegakkan penerbit saat terbit.

Tabel dibaca DARI dokumennya (arch/11 §2 aturan 1). Kalau tabelnya hilang, uji ini
GAGAL — bukan lulus karena tidak menemukan apa pun untuk diperiksa.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from hvx.modules.events import (
    ADMISI,
    REGISTRY,
    SUMBER,
    Admisi,
    EventTidakSah,
    admisi_sah,
    terbitkan,
)

SPEC03 = Path(__file__).resolve().parents[2] / "spec" / "03-EVENT-CONTRACTS.md"


def _teks() -> str:
    return SPEC03.read_text(encoding="utf-8")


def _tabel_admisi() -> dict[str, tuple[str, str, frozenset[str]]]:
    """{event_type: (kalimat dikenali pengguna, templat kunci, sumber sah)}."""
    teks = _teks()
    awal = teks.index("## Uji admisi per event")
    akhir = teks.index("\n## ", awal + 1)
    hasil: dict[str, tuple[str, str, frozenset[str]]] = {}
    for baris in teks[awal:akhir].splitlines():
        m = re.fullmatch(r"\| `([a-z_]+\.[a-z_]+)` \| (.*?) \| `([^`]*)` \| (.*?) \|", baris)
        if m:
            jenis, kalimat, kunci, sumber = m.groups()
            hasil[jenis] = (
                kalimat.strip(),
                kunci,
                frozenset(re.findall(r"`([a-z]+)`", sumber)),
            )
    return hasil


def _aturan_1() -> dict[str, str]:
    """{event_type: templat} dari blok kode aturan 1 spec/03 (`a.b · c → templat`)."""
    teks = _teks()
    awal = teks.index("**1 · Idempotensi.**")
    blok = teks[teks.index("```", awal) + 3 : teks.index("```", teks.index("```", awal) + 3)]
    hasil: dict[str, str] = {}
    for baris in blok.strip().splitlines():
        kiri, templat = (b.strip() for b in baris.split("→"))
        nama = [n.strip() for n in kiri.split("·")]
        domain = nama[0].split(".")[0]
        for n in nama:
            hasil[n if "." in n else f"{domain}.{n}"] = templat
    return hasil


def test_tabel_admisi_terbaca() -> None:
    assert len(_tabel_admisi()) >= 9, "tabel *Uji admisi per event* spec/03 tidak terbaca"
    assert len(_aturan_1()) >= 9, "blok aturan 1 spec/03 tidak terbaca"


def test_tiap_jenis_registry_punya_baris_admisi_dan_sebaliknya() -> None:
    tabel = _tabel_admisi()
    assert set(REGISTRY) == set(tabel), (
        f"terbit tanpa baris admisi: {sorted(set(REGISTRY) - set(tabel))} · "
        f"baris admisi tanpa jenis terbit: {sorted(set(tabel) - set(REGISTRY))}"
    )
    assert set(ADMISI) == set(REGISTRY), "events.ADMISI ≠ REGISTRY"


def test_syarat_1_kalimat_yang_dikenali_pengguna() -> None:
    """Kalimat orang kedua tentang apa yang PENGGUNA lakukan — dan tiap jenis punya kalimat
    sendiri: dua jenis dengan kalimat sama adalah satu kejadian yang dicatat dua kali."""
    tabel = _tabel_admisi()
    salah = [
        j
        for j, (kalimat, _k, _s) in tabel.items()
        if not re.fullmatch(r"\*“Anda [^”]{8,}”\*", kalimat)
    ]
    assert not salah, f"kalimat syarat 1 kosong atau bukan *“Anda …”*: {salah}"
    kalimat = [k for k, _t, _s in tabel.values()]
    assert len(set(kalimat)) == len(kalimat), "dua jenis berbagi satu kalimat syarat 1"


def test_syarat_2_kunci_sama_di_aturan_1_tabel_dan_kode() -> None:
    tabel, aturan = _tabel_admisi(), _aturan_1()
    salah = [
        f"{j}: aturan 1 {aturan.get(j)!r} · tabel {tabel[j][1]!r} · kode {ADMISI[j].kunci!r}"
        for j in ADMISI
        if not (aturan.get(j) == tabel[j][1] == ADMISI[j].kunci)
    ]
    assert not salah, "templat idempotency_key berbeda:\n" + "\n".join(salah)


def test_syarat_3_sumber_sama_di_tabel_dan_kode() -> None:
    tabel = _tabel_admisi()
    salah = {j: (sorted(tabel[j][2]), sorted(a.sumber)) for j, a in ADMISI.items()}
    salah = {j: v for j, v in salah.items() if v[0] != v[1]}
    assert not salah, f"sumber sah tabel ≠ kode: {salah}"
    assert all(a.sumber <= SUMBER for a in ADMISI.values())


@pytest.mark.parametrize(
    ("jenis", "kunci", "sumber"),
    [
        ("habit.completed", f"habit-completion:{uuid4()}", "agent"),
        ("goal.completed", f"goal:{uuid4()}:completed:2026-09-24T06:30:00.123456+00:00", "app"),
        ("checkin.logged", "checkin:2026-09-24:2026-09-24T06:30:00.123456+00:00", "app"),
    ],
)
def test_kunci_dan_sumber_yang_sah_diterima(jenis: str, kunci: str, sumber: str) -> None:
    admisi_sah(jenis, kunci, sumber)


@pytest.mark.parametrize(
    ("jenis", "kunci", "sumber", "alasan"),
    [
        ("mood.logged", f"mood:{uuid4()}", "agent", "source"),  # tak satu agent mencatat mood
        ("mood.logged", f"goal:{uuid4()}:created", "app", "idempotency_key"),
        ("goal.created", f"goal:{uuid4()}:completed:2026", "app", "idempotency_key"),
        ("habit.completion_retracted", f"habit-completion:{uuid4()}", "app", "idempotency_key"),
        ("mood.logged", f"mood:{uuid4()}/lain", "app", "idempotency_key"),  # templat UTUH
        ("habit.deleted", "habit:x:deleted", "app", "tanpa uji admisi"),
        # Identitas `<…>` tidak boleh MENELAN bagian harfiah templat lain (tinjauan kontrak
        # S7, K1): `habit.completed` berkunci pembatalan menelan pembatalan sungguhan nanti.
        (
            "habit.completed",
            f"habit-completion:{uuid4()}:retracted",
            "app",
            "idempotency_key",
        ),
        ("mood.logged", f"mood:{uuid4()}:created", "app", "idempotency_key"),
        ("goal.created", f"goal:{uuid4()}:completed:x:created", "app", "idempotency_key"),
        # `<for_date>` tanggal, `<…_at>` waktu berzona — bukan identitas sembarang
        ("checkin.logged", "checkin:kemarin:2026-09-24T06:30:00+00:00", "app", "idempotency_key"),
        ("goal.completed", f"goal:{uuid4()}:completed:segera", "app", "idempotency_key"),
    ],
)
def test_kunci_atau_sumber_yang_tidak_sah_ditolak(
    jenis: str, kunci: str, sumber: str, alasan: str
) -> None:
    with pytest.raises(EventTidakSah, match=alasan):
        admisi_sah(jenis, kunci, sumber)


class _KoneksiTerlarang:
    """Koneksi yang tidak boleh disentuh — uji admisi berjalan SEBELUM basis data."""

    def __getattr__(self, nama: str) -> Any:
        raise AssertionError("penerbit menyentuh basis data sebelum uji admisi")


async def test_penerbit_menolak_sebelum_menyentuh_basis_data() -> None:
    """`mood.logged` bersumber `agent` lulus E-3 (sumbernya di `CHECK`) — hanya uji admisi
    per jenis yang menolaknya, dan ia wajib menolak sebelum koneksi dipakai."""
    with pytest.raises(EventTidakSah, match="source"):
        await terbitkan(
            _KoneksiTerlarang(),  # type: ignore[arg-type]
            user_id=uuid4(),
            event_type="mood.logged",
            occurred_at=datetime.now(UTC),
            idempotency_key=f"mood:{uuid4()}",
            payload={"valence": 3},
            source="agent",
        )


def test_isian_templat_tanpa_bentuk_ditolak() -> None:
    """Isian baru (`<nama>`) wajib diberi bentuk — bukan jatuh ke identitas sembarang."""
    with pytest.raises(ValueError, match="tanpa bentuk"):
        Admisi("sleep:<sesuatu>", frozenset({"app"}))
