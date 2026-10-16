"""Penjalan kerusakan buta S7 — terapkan, uji, catat, pulihkan."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path

AKAR = Path("E:/xtheoputra/hvx-s7-tinjau-buta")
spec = importlib.util.spec_from_file_location("umk", AKAR / "tools" / "uji_mutasi_kode.py")
umk = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["umk"] = umk
spec.loader.exec_module(umk)  # type: ignore[union-attr]

sys.path.insert(0, str(Path(__file__).parent))
import kerusakan  # noqa: E402

S = umk.Sunting


def main() -> None:
    pilih = set(sys.argv[1:])
    hasil_berkas = Path(__file__).parent / "hasil.jsonl"
    env = umk.lingkungan_mutasi()
    for k in kerusakan.DAFTAR:
        if pilih and k["kode"] not in pilih and k["kode"].split("-")[0] not in pilih:
            continue
        cadangan: dict = {}
        dir_baru: list = []
        mulai = time.time()
        try:
            for berkas, lama, baru in k["sunting"]:
                umk._terapkan(S(berkas, lama, baru), cadangan, dir_baru)
            perintah = [
                sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x",
                *k["uji"],
            ]
            kode, keluar = umk.jalankan_terbatas(perintah, AKAR, env, 400)
        except Exception as g:  # noqa: BLE001
            kode, keluar = -9, f"GALAT PENERAPAN: {g}"
        finally:
            umk._pulihkan(cadangan, dir_baru)
        status = "LOLOS" if kode == 0 else ("GALAT" if kode == -9 else "TERTANGKAP")
        ekor = "\n".join(keluar.strip().splitlines()[-6:])
        baris = {"kode": k["kode"], "maksud": k["maksud"], "status": status,
                 "detik": round(time.time() - mulai), "ekor": ekor}
        with hasil_berkas.open("a", encoding="utf-8") as f:
            f.write(json.dumps(baris, ensure_ascii=False) + "\n")
        print(f"{status:10} {k['kode']:8} {k['maksud']}", flush=True)
        if status != "LOLOS":
            print("    " + ekor.replace("\n", "\n    ")[-600:], flush=True)


if __name__ == "__main__":
    main()
