"""spec/07 6.2 — tinjauan mingguan menjawab 5 pertanyaan naskah 4 §31, tanpa basis data.

Aturan yang diuji di fungsi murni `susun_tinjauan` (K-45): periode dihitung seperti rentetan
2.4 (`partial` memenuhi, `skipped` netral, hari di luar jadwal dan sebelum habit ada tidak
dihitung, yang belum berakhir belum gagal); Confidence Layer 5.4 (tanpa butir → `ask`);
*“Kenapa?”* tidak pernah dijawab sistem; tak satu kalimat sistem pun mengklaim sebab (§7).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest

from hvx.modules import checkins, habits, intelligence

SENIN = date(2026, 9, 28)  # 2026-W40
HARI_INI = date(2026, 10, 7)  # minggu W40 sudah selesai, W41 berjalan


def _habit(
    judul: str = "Lari pagi",
    *,
    period: str = "day",
    target: int = 1,
    hari: tuple[int, ...] | None = None,
    mulai: date = date(2026, 9, 1),
    tier: tuple[str, ...] = (),
    catatan: dict[date, tuple[str, str | None]] | None = None,
) -> habits.HabitDalamRentang:
    return habits.HabitDalamRentang(
        id=uuid.uuid4(),
        title=judul,
        period=period,
        target_count=target,
        weekdays=hari,
        status="active",
        mulai=mulai,
        adaptive_tiers=tier,
        catatan=catatan or {},
    )


def _checkin(d: date, energi: int | None, fokus: int | None = None) -> checkins.Checkin:
    t = datetime(2026, 9, 1, tzinfo=UTC)
    return checkins.Checkin(
        id=uuid.uuid4(),
        for_date=d,
        energy=energi,
        focus=fokus,
        sleep_hours=None,
        note=None,
        created_at=t,
        updated_at=t,
    )


def _hari(n: int) -> date:
    return SENIN + timedelta(days=n)


def _tanya(t: dict[str, Any], kunci: str) -> dict[str, Any]:
    (p,) = [q for q in t["questions"] if q["key"] == kunci]
    return p


def test_minggu_kosong_bertanya_di_kelima_pertanyaan_tanpa_angka() -> None:
    t = intelligence.susun_tinjauan(SENIN, HARI_INI, [], [], [])

    assert t["week"] == "2026-W40"
    assert (t["start"], t["end"], t["complete"]) == (SENIN, _hari(6), True)
    assert [q["key"] for q in t["questions"]] == [
        "went_well",
        "changed",
        "failed",
        "why",
        "change_next_week",
    ], "lima pertanyaan §31 tidak lengkap atau tidak berurutan"
    assert all(q["stance"] == "ask" and not q["items"] for q in t["questions"]), (
        "tanpa data sistem menyatakan sesuatu (Confidence Layer 5.4)"
    )
    assert all(q["prompt"] for q in t["questions"])
    assert t["axes"] == [], "sumbu tanpa bukti ditampilkan sebagai angka"
    assert {s["key"] for s in t["not_measured"]} == {
        "learning",
        "finance",
        "social",
        "career",
        "lifestyle",
    }


def test_periode_harian_mengikuti_aturan_rentetan() -> None:
    h = _habit(
        hari=(1, 2, 3, 4, 5),  # Senin–Jumat
        mulai=_hari(1),  # Senin sebelum habit ada TIDAK dihitung
        catatan={
            _hari(1): ("done", None),
            _hari(2): ("partial", None),  # partial memenuhi (naskah 4 §34)
            _hari(3): ("skipped", "lembur"),  # netral — dimaafkan, bukan gagal
            _hari(5): ("done", None),  # Sabtu: di luar jadwal — tidak dihitung
        },
    )
    n = intelligence.nilai_habit(h, SENIN, HARI_INI)

    assert n is not None
    assert (n.terpenuhi, n.terlewat, n.dimaafkan, n.berjalan) == (2, 1, 1, 0)
    assert n.hari_terlewat == (_hari(4),)
    assert n.alasan == ("lembur",)


def test_minggu_berjalan_belum_gagal() -> None:
    h = _habit(catatan={_hari(0): ("done", None)})
    n = intelligence.nilai_habit(h, SENIN, _hari(2))  # Rabu: Rabu–Minggu belum berakhir

    assert n is not None
    assert (n.terpenuhi, n.terlewat, n.berjalan) == (1, 1, 5)


@pytest.mark.parametrize(
    ("catatan", "hasil"),
    [
        ({_hari(0): ("done", None), _hari(3): ("done", None)}, (1, 0, 0)),
        ({_hari(0): ("done", None), _hari(3): ("skipped", "sakit")}, (0, 0, 1)),
        ({_hari(0): ("done", None)}, (0, 1, 0)),
    ],
)
def test_periode_mingguan_satu_periode(
    catatan: dict[date, tuple[str, str | None]], hasil: tuple[int, int, int]
) -> None:
    n = intelligence.nilai_habit(_habit(period="week", target=2, catatan=catatan), SENIN, HARI_INI)

    assert n is not None
    assert (n.terpenuhi, n.terlewat, n.dimaafkan) == hasil


def test_habit_bulanan_tidak_dihakimi_per_minggu() -> None:
    assert intelligence.nilai_habit(_habit(period="month"), SENIN, HARI_INI) is None


def test_lima_pertanyaan_dijawab_dari_bukti_dan_kenapa_tetap_bertanya() -> None:
    baik = _habit("Minum air", catatan={_hari(i): ("done", None) for i in range(7)})
    lalu_lemah = {SENIN - timedelta(days=7 - i): ("done", None) for i in range(2)}
    lemah = _habit(
        "Meditasi",
        tier=("Meditasi 20 menit", "Tarik napas 1 menit"),
        catatan={
            **lalu_lemah,
            _hari(0): ("done", None),
            _hari(1): ("done", None),
            _hari(2): ("skipped", "lembur"),
        },
    )
    catatan = [
        _checkin(_hari(0), 4),
        _checkin(_hari(1), 5),
        _checkin(_hari(3), 2),
        _checkin(_hari(4), 1),
        _checkin(_hari(5), 2),
        _checkin(SENIN - timedelta(days=3), 2),
    ]
    t = intelligence.susun_tinjauan(SENIN, HARI_INI, [baik, lemah], catatan, [])

    assert _tanya(t, "went_well")["stance"] == "state"
    assert any(
        "“Minum air” terpenuhi 7 dari 7 hari" in b["text"] for b in _tanya(t, "went_well")["items"]
    )
    gagal = _tanya(t, "failed")["items"]
    assert [b["text"] for b in gagal] == ["“Meditasi” belum terpenuhi di 4 dari 6 hari."]
    kenapa = _tanya(t, "why")
    assert kenapa["stance"] == "ask", "sistem menjawab “Kenapa?” atas nama pengguna"
    teks = [b["text"] for b in kenapa["items"]]
    assert any("“lembur”" in x for x in teks), "alasan yang dicatat pengguna tidak disodorkan"
    assert any("energimu rata-rata 4,5" in x and "terlewat, 1,7" in x for x in teks), teks
    ubah = _tanya(t, "change_next_week")["items"]
    assert any("“Tarik napas 1 menit”" in b["text"] for b in ubah), (
        "saran versi minimum di hari energi rendah tidak muncul"
    )
    energi = next(s for s in t["axes"] if s["key"] == "energy")
    assert (energi["value"], energi["previous"], energi["evidence_count"]) == (2.8, 2.0, 5)
    assert all(b["evidence_count"] >= 1 for q in t["questions"] for b in q["items"])


def test_kalimat_sistem_tidak_mengklaim_sebab() -> None:
    """Naskah 4 §7 — judul & alasan netral, supaya yang diperiksa kalimat SISTEM saja."""
    h = _habit(
        "Jalan",
        tier=("Jalan 30 menit", "Jalan 5 menit"),
        catatan={
            SENIN - timedelta(days=7): ("done", None),
            SENIN - timedelta(days=6): ("done", None),
            _hari(0): ("done", None),
            _hari(1): ("done", None),
            _hari(2): ("skipped", "hujan"),
        },
    )
    catatan = [_checkin(_hari(i), e) for i, e in ((0, 5), (1, 5), (3, 1), (4, 1), (5, 1))]
    t = intelligence.susun_tinjauan(SENIN, HARI_INI, [h], catatan, [])
    semua = [b["text"] for q in t["questions"] for b in q["items"]] + [s["why"] for s in t["axes"]]

    assert semua, "pembanding buta — tidak ada kalimat yang diperiksa"
    kausal = [x for x in semua if not intelligence.tanpa_klaim_kausal(x)]
    assert not kausal, f"kalimat sistem yang mengklaim sebab (§7): {kausal}"


def test_mood_dan_perubahan_antar_minggu() -> None:
    mood = [
        (SENIN - timedelta(days=4), 2),
        (SENIN - timedelta(days=2), 2),
        (_hari(1), 4),
        (_hari(2), 4),
    ]
    t = intelligence.susun_tinjauan(SENIN, HARI_INI, [], [], mood)

    m = next(s for s in t["axes"] if s["key"] == "mood")
    assert (m["value"], m["previous"], m["unit"]) == (4.0, 2.0, "1-5")
    berubah = [b["text"] for b in _tanya(t, "changed")["items"]]
    assert "Rata-rata mood naik dari 2,0 ke 4,0." in berubah


@pytest.mark.parametrize("teks", ["2026-W00", "2026-W54", "2026-40", "W40-2026", "2026-W4"])
def test_minggu_cacat_ditolak(teks: str) -> None:
    with pytest.raises(ValueError, match="YYYY-Www"):
        intelligence.awal_minggu(teks)


def test_minggu_53_hanya_di_tahun_yang_punya() -> None:
    assert intelligence.awal_minggu("2026-W53") == date(2026, 12, 28)
    with pytest.raises(ValueError, match="53"):
        intelligence.awal_minggu("2027-W53")
