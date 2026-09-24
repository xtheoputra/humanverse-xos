"""spec/07 1.6 — bentuk baris audit ditolak SEBELUM menyentuh basis data (spec/02 aturan F)."""

from __future__ import annotations

from typing import Any

import pytest

from hvx.modules.identity import AuditTidakSah, audit


class _KoneksiTakTersentuh:
    """Kalau validasi lolos padahal seharusnya ditolak, uji ini gagal di sini."""

    async def execute(self, *_a: Any, **_k: Any) -> None:
        raise AssertionError("baris audit yang tidak sah sampai ke basis data")


@pytest.mark.parametrize("aksi", ["login", "Session.Login", "sesi.masuk.gagal", "sesi. masuk", ""])
async def test_aksi_wajib_domain_titik_kata_kerja(aksi: str) -> None:
    with pytest.raises(AuditTidakSah, match=r"domain.kata_kerja"):
        await audit(
            _KoneksiTakTersentuh(),  # type: ignore[arg-type]
            aksi=aksi,
            aktor_tipe="system",
            aktor_id="uji",
            user_id=None,
        )


@pytest.mark.parametrize(
    ("metadata", "pesan"),
    [
        ({"isi": "x" * 121}, "spec/02 aturan F"),
        ({"daftar": ["a", "b"]}, "skalar"),
        ({"objek": {"a": 1}}, "skalar"),
        ({f"k{i}": i for i in range(21)}, "maksimal 20"),
    ],
)
async def test_metadata_hanya_skalar_pendek(metadata: dict[str, Any], pesan: str) -> None:
    with pytest.raises(AuditTidakSah, match=pesan):
        await audit(
            _KoneksiTakTersentuh(),  # type: ignore[arg-type]
            aksi="uji.dicatat",
            aktor_tipe="system",
            aktor_id="uji",
            user_id=None,
            metadata=metadata,
        )
