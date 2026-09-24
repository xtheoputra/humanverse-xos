"""spec/04 — halaman berkursor `?cursor=` · `next_cursor`: kursor rusak → 400, bukan 500."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest

from hvx.modules.platform import GalatApi, baca_kursor_waktu, kursor_waktu


def test_kursor_bolak_balik_utuh_termasuk_zona() -> None:
    saat = datetime(2026, 9, 24, 6, 30, 12, 345678, tzinfo=timezone(timedelta(hours=7)))
    id_ = uuid4()

    assert baca_kursor_waktu(kursor_waktu(saat, id_)) == (saat, id_)


def test_halaman_pertama_tanpa_kursor() -> None:
    assert baca_kursor_waktu(None) is None


def test_waktu_tanpa_zona_ditolak_saat_membuat_kursor() -> None:
    with pytest.raises(ValueError, match="berzona"):
        kursor_waktu(datetime(2026, 9, 24), uuid4())  # sengaja tanpa zona


@pytest.mark.parametrize(
    "teks",
    [
        "bukan-base64!!",
        "e30",  # {}
        "WyIyMDI2LTA5LTI0VDA2OjMwOjAwIiwieCJd",  # tanpa zona + id rusak
        "WyIyMDI2LTA5LTI0VDA2OjMwOjAwIiwiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIl0",
        "",
    ],
)
def test_kursor_rusak_menjadi_galat_400(teks: str) -> None:
    with pytest.raises(GalatApi) as g:
        baca_kursor_waktu(teks)
    assert (g.value.status, g.value.kode) == (400, "invalid_cursor")


def test_kursor_opak_tanpa_padding() -> None:
    k = kursor_waktu(datetime.now(UTC), uuid4())
    assert "=" not in k
    assert "/" not in k
    assert "+" not in k
