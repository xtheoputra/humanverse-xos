"""IP klien tidak pernah disimpan mentah — HMAC-SHA256 berkunci `HVX_IP_HASH_KEY`.

spec/01 `audit_logs.ip_hash`: *“hash, bukan IP mentah”*. sha256 POLOS atas
IPv4 bukan penyamaran: keempat miliar alamat bisa dicoba dalam hitungan menit.
"""

from __future__ import annotations

import hashlib
import hmac
from types import SimpleNamespace
from typing import Any

from hvx.modules.platform import Settings, sidik_ip


def _permintaan(host: str | None, kunci: str = "k" * 32) -> Any:
    settings = Settings(
        env="test", database_url="postgresql://x", redis_url="redis://x", ip_hash_key=kunci
    )  # type: ignore[arg-type]
    klien = None if host is None else SimpleNamespace(host=host)
    return SimpleNamespace(
        client=klien, app=SimpleNamespace(state=SimpleNamespace(settings=settings))
    )


def test_sidik_ip_berkunci_bukan_sha256_polos() -> None:
    sidik = sidik_ip(_permintaan("203.0.113.7"))

    assert sidik != hashlib.sha256(b"203.0.113.7").hexdigest(), "sidik IP bisa dibalik tanpa kunci"
    assert sidik == hmac.new(b"k" * 32, b"203.0.113.7", hashlib.sha256).hexdigest()
    assert "203.0.113.7" not in (sidik or "")


def test_kunci_lain_sidik_lain() -> None:
    assert sidik_ip(_permintaan("203.0.113.7")) != sidik_ip(_permintaan("203.0.113.7", "j" * 32))


def test_klien_tanpa_alamat_tidak_diberi_sidik_karangan() -> None:
    assert sidik_ip(_permintaan(None)) is None
