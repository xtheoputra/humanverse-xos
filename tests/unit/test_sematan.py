"""spec/07 3.5–3.7 — penyemat lokal `hvx-hash-v1` (K-26): berkunci, deterministik, ternormalkan.

Yang dijanjikan penyemat ini — dan yang TIDAK: kemiripan LEKSIKAL yang tahan
salah ketik, bukan kemiripan makna (lihat docstring `platform/sematan.py`).
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import pytest

from hvx.modules.platform import PenyematHash, Settings, penyemat_dari

KUNCI = b"k" * 32
P = PenyematHash(KUNCI)


def _kosinus(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def test_nama_membawa_dimensi_dan_sidik_kunci() -> None:
    lain = PenyematHash(b"x" * 32)

    assert P.dimensi == 384
    assert P.nama.startswith("hvx-hash-v1-384-")
    assert P.nama != lain.nama, "dua kunci, satu nama — ruang vektornya tercampur"


def test_ternormalkan_dan_teks_tanpa_kata_vektor_nol() -> None:
    v = P.semat("Lari pagi bikin lega")

    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-9)
    assert P.semat("  ... !!! ") == [0.0] * 384


def test_sama_di_tiap_proses_bukan_hash_python_yang_diacak() -> None:
    """`hash()` Python diacak per proses (PYTHONHASHSEED): vektor yang disimpan
    kemarin tidak akan cocok dengan kueri hari ini, dan tidak ada yang tahu."""
    kode = (
        "import json; from hvx.modules.platform import PenyematHash; "
        "print(json.dumps(PenyematHash(b'k' * 32).semat('capek sekali hari ini')))"
    )
    lain = subprocess.run(  # noqa: S603 - interpreter uji sendiri, argumen tetap
        [sys.executable, "-c", kode],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONHASHSEED": "12345"},
    )

    assert json.loads(lain.stdout) == P.semat("capek sekali hari ini")


def test_tanpa_kunci_yang_sama_kata_tidak_bisa_ditebak_dari_vektor() -> None:
    """Serangan kamus: penyerang yang memegang vektor dari Qdrant menyemat kata calon
    dengan penyemat MILIKNYA. Tanpa kunci yang sama, kemiripannya tidak lebih dari acak."""
    rahasia = P.semat("selingkuh")
    tebakan = PenyematHash(b"penyerang-tanpa-kunci-asli-00000").semat("selingkuh")

    assert abs(_kosinus(rahasia, tebakan)) < 0.5, "kata terbaca tanpa kunci"
    assert _kosinus(rahasia, P.semat("selingkuh")) > 0.999


def test_tahan_salah_ketik_dan_tidak_menyamakan_yang_asing() -> None:
    dasar = P.semat("lelah sekali sesudah rapat")

    salah_ketik = _kosinus(dasar, P.semat("leleh sekali sesudah rapat"))
    asing = _kosinus(dasar, P.semat("belanja sayur bulanan"))

    assert salah_ketik > 0.6
    assert asing < 0.2
    assert salah_ketik > asing


@pytest.mark.parametrize("kunci", [b"", b"k" * 31, b"k" * 65, "k" * 32])
def test_kunci_yang_salah_bentuk_ditolak(kunci: object) -> None:
    with pytest.raises(ValueError, match="32–64"):
        PenyematHash(kunci)  # type: ignore[arg-type]


def test_penyemat_proses_diturunkan_dari_setelan() -> None:
    dasar = {
        "database_url": "postgresql://x",
        "redis_url": "redis://x",
        "env": "test",
        "ip_hash_key": "i" * 32,
    }
    with pytest.raises(RuntimeError, match="HVX_SEMATAN_KEY"):
        penyemat_dari(Settings(**dasar))  # type: ignore[arg-type]

    a = penyemat_dari(Settings(**dasar, sematan_key="s" * 32))  # type: ignore[arg-type]
    b = penyemat_dari(Settings(**dasar, sematan_key="s" * 32))  # type: ignore[arg-type]
    assert a.nama == b.nama
    assert a.semat("lega") == b.semat("lega")
