"""Id semu jejak audit akun yang dihapus — satu arah, berkunci, stabil (spec/01 tahap 5, C-9).

Jejak audit DIPERTAHANKAN sesudah akun dihapus (membuktikan penghapusan terjadi), tetapi
`user_id`-nya diganti. Pengganti yang bisa dibalik — sha256 polos atas id akun — bukan
penyamaran: siapa pun yang pernah melihat id itu (cadangan, log lama, tautan) mencocokkannya
lagi dalam sekejap.
"""

from __future__ import annotations

import hashlib
import hmac
from uuid import UUID, uuid4

from hvx.modules.identity import id_semu
from hvx.modules.platform import Settings


def _settings(kunci: str = "k" * 32) -> Settings:
    return Settings(
        env="test", database_url="postgresql://x", redis_url="redis://x", ip_hash_key=kunci
    )  # type: ignore[arg-type]


def test_id_semu_berkunci_bukan_hash_polos() -> None:
    uid = uuid4()

    semu = id_semu(_settings(), uid)

    assert isinstance(semu, UUID)
    assert semu != uid
    assert semu != UUID(hashlib.sha256(str(uid).encode()).hexdigest()[:32]), (
        "id semu = sha256 polos id akun — bisa dicocokkan siapa pun yang pernah melihat id itu"
    )
    assert (
        semu.hex
        == hmac.new(b"k" * 32, f"akun-terhapus\x00{uid}".encode(), hashlib.sha256).hexdigest()[:32]
    )


def test_id_semu_stabil_untuk_akun_dan_kunci_yang_sama_dan_berbeda_untuk_lainnya() -> None:
    a, b = uuid4(), uuid4()

    assert id_semu(_settings(), a) == id_semu(_settings(), a), (
        "baris audit satu akun tak lagi bisa dipertemukan"
    )
    assert id_semu(_settings(), a) != id_semu(_settings(), b)
    assert id_semu(_settings(), a) != id_semu(_settings("j" * 32), a)


def test_id_semu_tidak_memuat_id_asli() -> None:
    uid = uuid4()

    assert str(uid) not in str(id_semu(_settings(), uid))
    assert uid.hex[:8] not in id_semu(_settings(), uid).hex
