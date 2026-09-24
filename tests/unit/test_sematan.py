"""spec/07 3.5–3.7 — penyemat lokal `hvx-hash-v1` (K-26): berkunci, per pengguna, deterministik.

Yang dijanjikan penyemat ini — dan yang TIDAK: kemiripan LEKSIKAL yang tahan
salah ketik, bukan kemiripan makna (lihat docstring `platform/sematan.py`).
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from uuid import UUID, uuid4

import pytest

from hvx.modules.platform import PenyematHash, Settings, penyemat_dari

KUNCI = b"k" * 32
P = PenyematHash(KUNCI)
U = UUID(int=1)
S = P.untuk(U)


def _kosinus(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def test_nama_membawa_dimensi_dan_sidik_kunci_proses() -> None:
    lain = PenyematHash(b"x" * 32)

    assert P.dimensi == 384
    assert P.nama.startswith("hvx-hash-v1-384-")
    assert P.nama != lain.nama, "dua kunci, satu nama — ruang vektornya tercampur"
    assert S.nama == P.nama, "nama per pengguna berbeda — pencarian tidak menemukan apa pun"


def test_penyemat_proses_tidak_menyemat_sendiri() -> None:
    """S1: satu kunci untuk semua pengguna = kamus bagi siapa pun yang punya akun."""
    assert not hasattr(P, "semat")
    with pytest.raises(TypeError, match="user_id"):
        P.untuk("bukan-uuid")  # type: ignore[arg-type]


def test_tiap_pengguna_ruang_vektornya_sendiri() -> None:
    """Tinjauan keamanan Sprint 3 (S1): teks yang sama dari dua pengguna tidak sebanding —
    akun penyerang tidak bisa menyemat kamus lalu membandingkannya dengan vektor korban."""
    lain = P.untuk(uuid4()).semat("ingin berhenti")

    assert abs(_kosinus(S.semat("ingin berhenti"), lain)) < 0.3, "vektor dua pengguna sebanding"
    assert S.semat("ingin berhenti") == P.untuk(U).semat("ingin berhenti")


def test_ternormalkan_dan_teks_tanpa_kata_vektor_nol() -> None:
    v = S.semat("Lari pagi bikin lega")

    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-9)
    assert S.semat("  ... !!! ") == [0.0] * 384


def test_sama_di_tiap_proses_bukan_hash_python_yang_diacak() -> None:
    """`hash()` Python diacak per proses (PYTHONHASHSEED): vektor yang disimpan
    kemarin tidak akan cocok dengan kueri hari ini, dan tidak ada yang tahu."""
    kode = (
        "import json, uuid; from hvx.modules.platform import PenyematHash; "
        "print(json.dumps(PenyematHash(b'k' * 32).untuk(uuid.UUID(int=1))"
        ".semat('capek sekali hari ini')))"
    )
    lain = subprocess.run(  # noqa: S603 - interpreter uji sendiri, argumen tetap
        [sys.executable, "-c", kode],
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "PYTHONHASHSEED": "12345"},
    )

    assert json.loads(lain.stdout) == S.semat("capek sekali hari ini")


def test_tanpa_kunci_yang_sama_kata_tidak_bisa_ditebak_dari_vektor() -> None:
    """Serangan kamus: penyerang yang memegang vektor dari Qdrant menyemat kata calon
    dengan penyemat MILIKNYA. Tanpa kunci yang sama, kemiripannya tidak lebih dari acak."""
    rahasia = S.semat("selingkuh")
    tebakan = PenyematHash(b"penyerang-tanpa-kunci-asli-00000").untuk(U).semat("selingkuh")

    assert abs(_kosinus(rahasia, tebakan)) < 0.5, "kata terbaca tanpa kunci"
    assert _kosinus(rahasia, S.semat("selingkuh")) > 0.999


def test_huruf_besar_dan_kecil_kata_yang_sama() -> None:
    """Pengguna menulis "Rapat" di jurnal dan mencari "rapat" (tinjauan penegak buta)."""
    assert S.semat("Rapat Pagi") == S.semat("rapat pagi"), "Rapat ≠ rapat"


def test_tahan_salah_ketik_dan_tidak_menyamakan_yang_asing() -> None:
    dasar = S.semat("lelah sekali sesudah rapat")

    salah_ketik = _kosinus(dasar, S.semat("leleh sekali sesudah rapat"))
    asing = _kosinus(dasar, S.semat("belanja sayur bulanan"))

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
    assert a.untuk(U).semat("lega") == b.untuk(U).semat("lega")
