"""`tools/uji_mutasi_kode.py` — mutasi yang menggantung dihentikan, bukan ditunggu selamanya.

Tinjauan Sprint 3: satu mutasi membuat ujinya menggantung (pekerja yang tidak menolak
peran yang salah berjalan terus), dan seluruh putaran mutasi berhenti di sana tanpa
batas — sampai prosesnya dimatikan tangan.
"""

from __future__ import annotations

import os
import sys
import time

from test_jangkar_mutasi import AKAR, _alat


def test_proses_turunan_yang_menggantung_ikut_dihentikan() -> None:
    """Cucu yang memegang pipa keluaran — bentuk peluncur `python.exe` venv di Windows."""
    alat = _alat()
    cucu = (
        "import subprocess, sys; "
        "subprocess.run([sys.executable, '-c', 'import time; time.sleep(15)'])"
    )
    mulai = time.monotonic()

    kode, keluaran = alat.jalankan_terbatas(
        [sys.executable, "-c", cucu], AKAR, dict(os.environ), batas_s=1
    )

    lama = time.monotonic() - mulai
    assert kode == -1, f"proses yang menggantung terhitung selesai (keluar {kode})"
    assert "MENGGANTUNG" in keluaran
    assert lama < 10, f"menunggu cucunya {lama:.0f} dtk — pohon prosesnya tidak dihentikan"


def test_proses_yang_selesai_membawa_kode_dan_keluarannya() -> None:
    alat = _alat()

    kode, keluaran = alat.jalankan_terbatas(
        [sys.executable, "-c", "import sys; print('halo'); sys.exit(3)"], AKAR, dict(os.environ)
    )

    assert (kode, keluaran.strip()) == (3, "halo")
