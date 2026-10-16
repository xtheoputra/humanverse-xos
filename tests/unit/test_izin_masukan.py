"""spec/07 1.5 — masukan mesin izin yang salah bentuk ditolak SEBELUM Redis & basis data."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import pytest

from hvx.modules.identity import SCOPE_RESMI, IzinTidakSah, MesinIzin, Subjek


class _TidakBolehDisentuh:
    def __getattr__(self, nama: str) -> Any:
        raise AssertionError(f"disentuh sebelum masukan divalidasi: {nama}")


MESIN = MesinIzin(_TidakBolehDisentuh(), _TidakBolehDisentuh(), "uji", 300)  # type: ignore[arg-type]
UID = uuid.uuid4()
COACH = Subjek("agent", "coach-agent")


def test_nama_subjek_dari_spec05_diterima() -> None:
    Subjek("agent", "coach-agent")
    Subjek("tool", "habit.streak")
    Subjek("integration", "google_calendar")


@pytest.mark.parametrize(
    ("tipe", "id_"),
    [
        ("robot", "coach-agent"),
        ("agent", "Coach-Agent"),
        ("agent", "coach:agent"),
        ("agent", ""),
        ("tool", "x" * 101),
    ],
)
def test_subjek_berbentuk_salah_ditolak(tipe: Any, id_: Any) -> None:
    with pytest.raises(IzinTidakSah):
        Subjek(tipe, id_)


@pytest.mark.parametrize(
    ("scope", "aksi"),
    [
        ("Habits", "read"),
        ("habits:x", "read"),
        ("", "read"),
        ("habits", "destroy"),
        ("habit", "read"),  # salah ketik: berbentuk sah, tetapi bukan scope resmi (E-180)
    ],
)
async def test_scope_dan_aksi_tak_dikenal_ditolak(scope: Any, aksi: Any) -> None:
    with pytest.raises(IzinTidakSah):
        await MESIN.cek(UID, COACH, scope, aksi)
    with pytest.raises(IzinTidakSah):
        await MESIN.tetapkan(UID, COACH, scope, aksi, "allow")


def test_tiap_scope_resmi_lolos_pola_kunci_cache() -> None:
    """Kunci cache izin disusun dari scope — daftar resmi tidak boleh memuat `:`."""
    from hvx.modules.identity.izin import _POLA_SCOPE

    assert SCOPE_RESMI, "daftar scope resmi kosong"
    assert [s for s in SCOPE_RESMI if not _POLA_SCOPE.fullmatch(s)] == []
    assert SCOPE_RESMI["journal_raw"].sensitif, "jurnal mentah bukan scope sensitif"


async def test_user_id_bukan_uuid_ditolak() -> None:
    with pytest.raises(TypeError):
        await MESIN.cek(str(UID), COACH, "habits", "read")  # type: ignore[arg-type]


async def test_keputusan_asing_dan_waktu_tanpa_zona_ditolak() -> None:
    with pytest.raises(IzinTidakSah):
        await MESIN.tetapkan(UID, COACH, "habits", "read", "maybe")  # type: ignore[arg-type]
    with pytest.raises(IzinTidakSah, match="berzona"):
        await MESIN.tetapkan(
            UID, COACH, "habits", "read", "allow", expires_at=datetime(2026, 9, 17, 12)
        )
