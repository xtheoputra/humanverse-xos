"""`tools/uji_mutasi_kode.py` — tiap mutasi sungguh mengubah sesuatu yang ada.

Tinjauan Sprint 3: dua mutasi 3.2 memanggil `.replace()` pada potongan TERAKHIR
jangkarnya saja, jadi penggantinya sama persis dengan jangkarnya — mutasinya tidak
mengubah apa pun, dan baru ketahuan sebagai "DIAM" setelah pengujinya lulus. Jangkar
yang bergeser karena kode berubah juga baru ketahuan di tengah putaran mutasi. Uji
ini menangkap keduanya dalam hitungan detik, tanpa menjalankan satu mutasi pun.

Gerbang penuh 6 Okt 2026 (E-222): dua mutasi 4.7 menunjuk `test_coach_tanpa_data_
mengatakannya` — uji yang sudah diganti namanya oleh 5.4. `pytest` menjawab *“not
found”* (kode keluar 4), yang bagi alat mutasi berarti “diam”, dan baru ketahuan
di gerbang penuh ±20 menit kemudian. Nama ujinya kini diperiksa di sini juga.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

AKAR = Path(__file__).resolve().parents[2]


def _alat() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "uji_mutasi_kode", AKAR / "tools" / "uji_mutasi_kode.py"
    )
    assert spec is not None
    assert spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    sys.modules["uji_mutasi_kode"] = modul
    spec.loader.exec_module(modul)
    return modul


def test_tiap_jangkar_mutasi_ada_tepat_sekali_dan_penggantinya_berbeda() -> None:
    alat = _alat()
    buruk: list[str] = []
    for m in alat.MUTASI:
        for s in m.suntingan:
            if not s.lama:  # berkas baru, atau sisip di akhir berkas
                continue
            teks = (AKAR / s.berkas).read_text(encoding="utf-8").replace("\r\n", "\n")
            if (n := teks.count(s.lama)) != 1:
                buruk.append(f"{m.kode} {m.maksud}: jangkar cocok {n}x di {s.berkas}")
            if s.lama == s.baru:
                buruk.append(f"{m.kode} {m.maksud}: pengganti sama dengan jangkarnya")

    assert len(alat.MUTASI) > 200, "daftar mutasi tidak terbaca"
    assert not buruk, "mutasi yang tidak mengubah apa pun:\n" + "\n".join(buruk)


def test_tiap_mutasi_pytest_menunjuk_uji_yang_ada() -> None:
    """Nama uji di `_pytest(...)` masih ada di berkasnya (E-222).

    Uji yang diganti namanya membuat `pytest` keluar dengan kode 4 (*not found*) —
    tidak satu pun uji berjalan, dan mutasinya terbaca “diam”.
    """
    alat = _alat()
    buruk: list[str] = []
    for m in alat.MUTASI:
        if "pytest" not in m.perintah:
            continue
        berkas, _, sisa = m.perintah[-1].partition("::")
        if berkas in {s.berkas for s in m.suntingan if s.lama is None}:
            continue  # berkas ujinya dibuat mutasi itu sendiri
        jalur = AKAR / berkas
        if not jalur.is_file():
            buruk.append(f"{m.kode} {m.maksud}: berkas uji tidak ada: {berkas}")
            continue
        if not sisa:
            continue
        nama = sisa.split("::")[-1].split("[")[0]
        if not re.search(
            rf"^\s*(async\s+)?def {re.escape(nama)}\(", jalur.read_text("utf-8"), re.M
        ):
            buruk.append(f"{m.kode} {m.maksud}: {berkas} tidak punya uji `{nama}`")

    assert not buruk, "mutasi yang menunjuk uji yang tidak ada:\n" + "\n".join(buruk)
