"""spec/07 6.3 — notifikasi *bisa dimatikan per jenis*: gerbang kirim dan preferensinya (K-44).

V0 tidak mengirim apa pun (A-28); yang diuji adalah gerbang yang WAJIB dilewati pengirim
mana pun kelak — jenis yang dimatikan diam, jam tenang menunda, pagu harian §11.17 berhenti
(*Do nothing*, §11.44), dan keamanan akun tidak bisa dibungkam.
"""

from __future__ import annotations

from datetime import time

import pytest

from hvx.modules import profile


def _pref(**jenis: bool) -> dict[str, object]:
    return {"types": jenis}


def test_bawaan_hanya_yang_diharapkan_pengguna_menyala() -> None:
    nyala = {k for k, j in profile.JENIS_NOTIFIKASI.items() if j.bawaan}
    assert nyala == {"weekly_review", "account_security"}, (
        "notifikasi proaktif menyala tanpa diminta (privacy by default, GDPR Art. 25(2))"
    )
    assert [k for k, j in profile.JENIS_NOTIFIKASI.items() if j.wajib] == ["account_security"]


@pytest.mark.parametrize("jenis", ["habit_reminder", "weekly_review", "recommendation"])
def test_tiap_jenis_bisa_dimatikan_sendiri(jenis: str) -> None:
    lain = [k for k in profile.JENIS_NOTIFIKASI if k not in (jenis, "account_security")]
    pref = _pref(**{jenis: False}, **dict.fromkeys(lain, True))

    assert profile.keputusan_kirim(pref, jenis, time(12, 0), 0) == "silent"
    for k in lain:
        assert profile.keputusan_kirim(pref, k, time(12, 0), 0) == "now", (
            f"mematikan {jenis} ikut membungkam {k}"
        )


def test_keamanan_akun_tidak_bisa_dibungkam_dan_melewati_jam_tenang_juga_pagu() -> None:
    pref = {"types": {"account_security": False}, "quiet_hours": {"start": "00:00", "end": "23:59"}}
    assert profile.keputusan_kirim(pref, "account_security", time(3, 0), 999) == "now"


@pytest.mark.parametrize(
    ("jam", "hasil"),
    [(time(21, 59), "now"), (time(22, 0), "later"), (time(3, 0), "later"), (time(7, 0), "now")],
)
def test_jam_tenang_melintasi_tengah_malam_menunda(jam: time, hasil: str) -> None:
    assert profile.keputusan_kirim(None, "weekly_review", jam, 0) == hasil  # bawaan 22:00–07:00


def test_jam_tenang_siang_dan_tanpa_jam_tenang() -> None:
    siang = {"quiet_hours": {"start": "13:00", "end": "15:00"}}
    assert profile.keputusan_kirim(siang, "weekly_review", time(14, 0), 0) == "later"
    assert profile.keputusan_kirim(siang, "weekly_review", time(15, 0), 0) == "now"
    tanpa = {"quiet_hours": None}
    assert profile.keputusan_kirim(tanpa, "weekly_review", time(3, 0), 0) == "now"


def test_pagu_harian_naskah_berhenti_bukan_menunda() -> None:
    pagu = profile.PAGU_HARIAN_NOTIFIKASI
    assert pagu == 10, "pagu §11.17 `notification: send: 10/day` diubah tanpa naskah"
    assert profile.keputusan_kirim(None, "weekly_review", time(12, 0), pagu - 1) == "now"
    assert profile.keputusan_kirim(None, "weekly_review", time(12, 0), pagu) == "silent"


def test_jenis_tak_dikenal_ditolak_bukan_dikirim() -> None:
    with pytest.raises(ValueError, match="tak dikenal"):
        profile.keputusan_kirim(None, "promo", time(12, 0), 0)
