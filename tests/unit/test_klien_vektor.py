"""`platform.KlienVektor` tanpa Qdrant — yang tidak terlihat oleh Qdrant uji tanpa kunci."""

from __future__ import annotations

from hvx.modules.platform import KlienVektor


async def test_kunci_api_dikirim_di_kepala_api_key() -> None:
    """Qdrant membaca kuncinya dari kepala `api-key` — nama lain = 401 di tiap panggilan
    produksi, dan Qdrant uji berjalan tanpa kunci (tinjauan penegak buta Sprint 3)."""
    klien = KlienVektor("http://127.0.0.1:9", kunci_api="rahasia-uji")
    try:
        assert klien._http.headers.get("api-key") == "rahasia-uji", "kunci tidak di kepala api-key"
    finally:
        await klien.tutup()
