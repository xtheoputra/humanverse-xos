"""spec/07 2.4 — rentetan & tingkat penyelesaian, sebagai fungsi murni dengan tanggal tetap.

Uji lewat HTTP (zona profil, jam basis data, pengguna yang pindah negara) ada
di `tests/integration/test_rentetan.py`; di sini aturannya sendiri, tanpa jam.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from hvx.modules.habits import hitung_rentetan

SENIN = date(2026, 9, 21)  # Senin, minggu ISO 39


def _hari(n: int) -> date:
    return SENIN + timedelta(days=n)


def _harian(
    penyelesaian: dict[date, str],
    *,
    hari_ini: date,
    mulai: date | None = None,
    weekdays: list[int] | None = None,
) -> tuple[int, int, float | None]:
    r = hitung_rentetan(
        period="day",
        target_count=1,
        weekdays=weekdays,
        mulai=mulai or min([hari_ini, *penyelesaian]),
        hari_ini=hari_ini,
        penyelesaian=penyelesaian,
    )
    return r.current, r.longest, r.completion_rate_30d


# ─────────────────────────────────────────────────────────── harian ──


def test_tanpa_penyelesaian_nol_dan_tanpa_tingkat() -> None:
    assert _harian({}, hari_ini=SENIN) == (0, 0, None)


def test_berturut_sampai_hari_ini() -> None:
    catatan = {_hari(i): "done" for i in range(5)}
    assert _harian(catatan, hari_ini=_hari(4)) == (5, 5, 1.0)


def test_hari_ini_yang_belum_dijalankan_tidak_memutus_rentetan() -> None:
    catatan = {_hari(i): "done" for i in range(5)}
    current, longest, tingkat = _harian(catatan, hari_ini=_hari(5))
    assert (current, longest) == (5, 5), "hari ini yang belum berakhir memutus rentetan"
    assert tingkat == 1.0, "hari ini yang belum dijalankan masuk penyebut"


def test_hari_yang_terlewat_memutus_rentetan_tetapi_terpanjang_tetap() -> None:
    catatan = {_hari(i): "done" for i in range(5)}
    assert _harian(catatan, hari_ini=_hari(6)) == (0, 5, round(5 / 6, 3))


def test_skipped_netral_tidak_menambah_dan_tidak_memutus() -> None:
    catatan = {_hari(0): "done", _hari(1): "skipped", _hari(2): "done"}
    current, longest, tingkat = _harian(catatan, hari_ini=_hari(2))
    assert (current, longest) == (2, 2), "skipped memutus rentetan"
    assert tingkat == 1.0, "skipped masuk penyebut tingkat penyelesaian"


def test_partial_dan_tier_ringan_memenuhi() -> None:
    catatan = {_hari(0): "done", _hari(1): "partial", _hari(2): "done"}
    assert _harian(catatan, hari_ini=_hari(2))[:2] == (3, 3)


def test_rentetan_terpanjang_di_masa_lalu() -> None:
    catatan = {**{_hari(i): "done" for i in range(4)}, **{_hari(i): "done" for i in (6, 7)}}
    assert _harian(catatan, hari_ini=_hari(7))[:2] == (2, 4)


def test_jadwal_hanya_hari_terjadwal_yang_dihitung() -> None:
    """Senin/Rabu/Jumat: Selasa & Kamis bukan hari habit ini — tidak memutus."""
    catatan = {_hari(0): "done", _hari(2): "done", _hari(4): "done", _hari(7): "done"}
    assert _harian(catatan, hari_ini=_hari(7), weekdays=[1, 3, 5]) == (4, 4, 1.0)


def test_jadwal_hari_terjadwal_yang_terlewat_memutus() -> None:
    catatan = {_hari(0): "done", _hari(1): "done", _hari(4): "done"}  # Rabu terlewat
    current, longest, tingkat = _harian(catatan, hari_ini=_hari(4), weekdays=[1, 3, 5])
    assert (current, longest) == (1, 1), "penyelesaian hari Selasa menutupi Rabu yang terlewat"
    assert tingkat == round(2 / 3, 3)


def test_tingkat_tidak_menghitung_hari_sebelum_habit_ada() -> None:
    catatan = {_hari(9): "done"}
    assert _harian(catatan, hari_ini=_hari(10), mulai=_hari(9)) == (1, 1, 1.0)


def test_tingkat_hanya_tiga_puluh_hari_terakhir() -> None:
    lama = {_hari(i): "done" for i in range(20)}  # jauh di luar jendela
    baru = {_hari(i): "done" for i in range(50, 60)}
    current, _longest, tingkat = _harian({**lama, **baru}, hari_ini=_hari(59), mulai=SENIN)
    assert current == 10
    assert tingkat == round(10 / 30, 3)


# ─────────────────────────────────────────── lintas zona waktu (2.4) ──


def test_tanggal_sesudah_hari_ini_menurut_profil_tetap_dihitung() -> None:
    """Perangkat di zona lebih timur dari profilnya mencatat "besok" — hari yang sudah terjadi."""
    catatan = {_hari(0): "done", _hari(1): "done", _hari(2): "done"}
    assert _harian(catatan, hari_ini=_hari(1))[:2] == (3, 3)


def test_pindah_ke_barat_tanggal_yang_berulang_tidak_menggandakan() -> None:
    """Jakarta → New York: tanggal lokal "mundur"; satu tanggal tetap satu penyelesaian."""
    catatan = {_hari(i): "done" for i in range(4)}  # Senin–Kamis di Jakarta
    # Kamis malam terbang, tiba masih Kamis di New York, lalu Jumat dan Sabtu di sana.
    catatan.update({_hari(4): "done", _hari(5): "done"})
    assert _harian(catatan, hari_ini=_hari(5))[:2] == (6, 6)


def test_pindah_ke_timur_tanggal_terlompati_bisa_dicatat_mundur() -> None:
    """Menyeberang garis tanggal ke timur melompati satu tanggal kalender."""
    catatan = {_hari(0): "done", _hari(1): "done", _hari(3): "done"}
    assert _harian(catatan, hari_ini=_hari(3))[:2] == (1, 2)
    catatan[_hari(2)] = "done"  # dicatat mundur dari perangkat
    assert _harian(catatan, hari_ini=_hari(3))[:2] == (4, 4)


# ─────────────────────────────────────────── mingguan & bulanan ──


def _periode(
    period: str,
    target: int,
    penyelesaian: dict[date, str],
    hari_ini: date,
    mulai: date | None = None,
) -> tuple[int, int, float | None]:
    r = hitung_rentetan(
        period=period,
        target_count=target,
        weekdays=None,
        mulai=mulai or min([hari_ini, *penyelesaian]),
        hari_ini=hari_ini,
        penyelesaian=penyelesaian,
    )
    return r.current, r.longest, r.completion_rate_30d


def test_mingguan_terpenuhi_per_minggu_iso() -> None:
    catatan = {
        _hari(-14): "done",
        _hari(-12): "done",  # minggu -2: 2 ✓
        _hari(-7): "done",
        _hari(-1): "done",  # minggu -1 (Senin & Minggu): 2 ✓
    }
    current, longest, _t = _periode("week", 2, catatan, hari_ini=_hari(2))
    assert (current, longest) == (2, 2), "minggu ini yang belum selesai memutus rentetan"


def test_mingguan_di_bawah_target_memutus() -> None:
    catatan = {_hari(-14): "done", _hari(-12): "done", _hari(-7): "done"}  # minggu -1: 1 ✗
    assert _periode("week", 2, catatan, hari_ini=_hari(2))[:2] == (0, 1)


def test_mingguan_skipped_tidak_menambah_jumlah() -> None:
    catatan = {_hari(-7): "done", _hari(-6): "skipped"}
    assert _periode("week", 2, catatan, hari_ini=_hari(0))[:2] == (0, 0)


def test_bulanan_melintasi_akhir_tahun() -> None:
    catatan = {date(2026, 11, 3): "done", date(2026, 12, 30): "done", date(2027, 1, 2): "done"}
    assert _periode("month", 1, catatan, hari_ini=date(2027, 1, 15))[:2] == (3, 3)


def test_bulanan_bulan_yang_terlewat_memutus() -> None:
    catatan = {date(2026, 10, 3): "done", date(2026, 12, 30): "done"}
    assert _periode("month", 1, catatan, hari_ini=date(2027, 1, 15))[:2] == (1, 1)


# ─────────────────────────────────────────────────────── sifat ──


@pytest.mark.parametrize("hari_ini", [_hari(n) for n in (0, 3, 10, 40)])
def test_terpanjang_tidak_pernah_kurang_dari_saat_ini(hari_ini: date) -> None:
    catatan = {_hari(i): ("done" if i % 3 else "skipped") for i in range(0, 40, 1) if i % 7}
    r = hitung_rentetan(
        period="day",
        target_count=1,
        weekdays=None,
        mulai=SENIN,
        hari_ini=hari_ini,
        penyelesaian=catatan,
    )
    assert r.longest >= r.current
    assert r.completion_rate_30d is None or 0 <= r.completion_rate_30d <= 1


def test_riwayat_sangat_lama_tidak_ditelusuri_tanpa_batas() -> None:
    catatan = {date(1, 1, 1): "done", _hari(0): "done"}
    assert _harian(catatan, hari_ini=_hari(0))[:2] == (1, 1)


# ─────────────── tinjauan kontrak Sprint 2: F7 (`skipped` per kejadian) · F8 (awal habit) ──


def test_mingguan_skipped_memaafkan_satu_kali_dan_tidak_memutus() -> None:
    """spec/04: `skipped` netral — pada habit mingguan juga, bukan hanya harian (F7)."""
    catatan = {
        _hari(-14): "done",
        _hari(-13): "done",  # minggu -2: 2 ✓
        _hari(-7): "done",
        _hari(-6): "skipped",  # minggu -1: 1 + 1 dimaafkan
    }
    hasil = _periode("week", 2, catatan, hari_ini=_hari(2))
    assert hasil == (1, 1, 1.0), f"skipped memutus rentetan mingguan: {hasil}"


def test_mingguan_skipped_yang_tidak_mencukupi_target_tetap_memutus() -> None:
    catatan = {_hari(-14): "done", _hari(-7): "skipped"}  # minggu -1: 0 + 1 < 3
    assert _periode("week", 3, catatan, hari_ini=_hari(2), mulai=_hari(-14)) == (0, 0, 0.0)


def test_bulanan_skipped_netral() -> None:
    catatan = {date(2026, 7, 5): "done", date(2026, 8, 9): "skipped"}
    assert _periode("month", 1, catatan, hari_ini=date(2026, 9, 3))[:2] == (1, 1)


def test_tingkat_hari_sebelum_habit_dibuat_hanya_dihitung_bila_terpenuhi() -> None:
    """Habit dibuat hari ini, satu catatan mundur sepuluh hari lalu: dulu 0,1 (F8)."""
    catatan = {_hari(0): "done"}
    tingkat = _harian(catatan, hari_ini=_hari(10), mulai=_hari(10))[2]
    assert tingkat == 1.0, f"hari sebelum habit ada dihitung gagal: {tingkat}"


def test_tingkat_minggu_pembuatan_yang_tidak_utuh_tidak_menjadi_gagal() -> None:
    kamis = _hari(-4)  # habit dibuat Kamis minggu lalu
    catatan = {_hari(-3): "done"}  # minggu itu 1 dari 2
    assert _periode("week", 2, catatan, hari_ini=_hari(1), mulai=kamis)[2] is None


def test_tingkat_sesudah_habit_ada_tetap_menghitung_yang_terlewat() -> None:
    catatan = {_hari(8): "done"}
    assert _harian(catatan, hari_ini=_hari(10), mulai=_hari(5))[2] == round(1 / 5, 3)
