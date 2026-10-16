"""spec/04 — halaman berkursor `?cursor=` · `next_cursor`: kursor rusak → 400, bukan 500."""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from hvx.modules.platform import GalatApi, baca_kursor_waktu, kursor_waktu


def test_kursor_bolak_balik_utuh_termasuk_zona() -> None:
    saat = datetime(2026, 9, 24, 6, 30, 12, 345678, tzinfo=timezone(timedelta(hours=7)))
    id_ = uuid4()

    assert baca_kursor_waktu("goals", kursor_waktu("goals", saat, id_)) == (saat, id_)


def test_halaman_pertama_tanpa_kursor() -> None:
    assert baca_kursor_waktu("goals", None) is None


def test_waktu_tanpa_zona_ditolak_saat_membuat_kursor() -> None:
    with pytest.raises(ValueError, match="berzona"):
        kursor_waktu("goals", datetime(2026, 9, 24), uuid4())  # sengaja tanpa zona


_ID = "00000000-0000-0000-0000-000000000000"


def _k(isi: object) -> str:
    return base64.urlsafe_b64encode(json.dumps(isi).encode()).decode().rstrip("=")


@pytest.mark.parametrize(
    "teks",
    [
        "bukan-base64!!",
        "e30",  # {}
        "",
        _k(["goals", "2026-09-24T06:30:00", "x"]),  # tanpa zona + id rusak
        _k(["goals", "2026-09-24T06:30:00", _ID]),  # tanpa zona
        # Dirakit tangan (tinjauan keamanan Sprint 2): dulu AttributeError → 500.
        _k(["goals", "2026-09-24T06:30:00Z", 5]),
        _k(["goals", 5, _ID]),
        _k(["goals", "2026-09-24T06:30:00Z", {"a": 1}]),
        _k([["goals"], "2026-09-24T06:30:00Z", _ID]),
        _k(["goals", "2026-09-24T06:30:00Z"]),  # bentuk lama tanpa jenis
        _k("goals"),
        _k(None),
        # Waktu yang meluap saat diubah ke UTC → dulu 500 di asyncpg.
        _k(["goals", "0001-01-01T00:00:00+14:00", _ID]),
        _k(["goals", "9999-12-31T23:59:59-14:00", _ID]),
        _k(["goals", "0001-01-01T00:00:00+00:00", _ID]),
    ],
    ids=[
        "bukan-base64",
        "objek",
        "kosong",
        "tanpa-zona-id-rusak",
        "tanpa-zona",
        "id-angka",
        "waktu-angka",
        "id-objek",
        "jenis-daftar",
        "bentuk-lama",
        "string",
        "null",
        "meluap-plus14",
        "meluap-minus14",
        "tahun-0001",
    ],
)
def test_kursor_rusak_menjadi_galat_400(teks: str) -> None:
    with pytest.raises(GalatApi) as g:
        baca_kursor_waktu("goals", teks)
    assert (g.value.status, g.value.kode) == (400, "invalid_cursor")


def test_kursor_json_bersarang_dalam_bukan_500() -> None:
    """`json.loads` melempar RecursionError — bukan ValueError — untuk `[[[[…`."""
    teks = base64.urlsafe_b64encode(b"[" * 50_000).decode().rstrip("=")

    with pytest.raises(GalatApi) as g:
        baca_kursor_waktu("goals", teks)
    assert g.value.kode == "invalid_cursor"


def test_kursor_daftar_lain_ditolak() -> None:
    """Kursor `/goals` di `/moods` bukan halaman berikutnya dari apa pun (tinjauan kontrak D5)."""
    k = kursor_waktu("goals", datetime.now(UTC), uuid4())

    with pytest.raises(GalatApi) as g:
        baca_kursor_waktu("moods", k)
    assert g.value.kode == "invalid_cursor"


def test_kursor_opak_tanpa_padding() -> None:
    k = kursor_waktu("goals", datetime.now(UTC), uuid4())
    assert "=" not in k
    assert "/" not in k
    assert "+" not in k
