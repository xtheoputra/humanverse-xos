"""Alat operator stream mati — spec/08 7.4: *“event di stream mati diputar ulang per id”*.

    python -m hvx.stream_mati daftar            # entri terlama dulu: id · grup · jenis
    python -m hvx.stream_mati putar <id> [...]   # serahkan kembali ke penangan grupnya

Dijalankan dengan lingkungan proses PEKERJA (`HVX_*`, peran anggota `hvx_pekerja`) —
konsumennya dirakit `hvx.pekerja.rakit_konsumen` yang sama, jadi penangan yang memutar
ulang = penangan yang dulu gagal (sesudah dibetulkan). Keluarannya hanya rujukan (id
entri, grup, jenis event) — tidak pernah isi event milik pengguna.

Kode keluar 1 bila ada entri yang `gagal` (penangannya masih gagal — entrinya kembali
ke stream mati) atau tidak ditemukan; `event_hilang` (akun atau datanya sudah dihapus)
bukan kegagalan: tidak ada yang perlu diputar.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from hvx import pekerja
from hvx.modules import events, platform

_SELESAI = frozenset({"diputar", "event_hilang"})


async def jalankan(settings: platform.Settings, perintah: str, ids: list[str], batas: int) -> int:
    engine = platform.buat_engine(settings.database_url)
    redis = platform.buat_redis(
        settings.redis_url,
        socket_timeout_s=settings.redis_socket_timeout_s,
        connect_timeout_s=settings.redis_connect_timeout_s,
    )
    try:
        await platform.pastikan_peran_aplikasi(engine, pekerja=True)
        if perintah == "daftar":
            for id_mati, isi in await events.daftar_mati(redis, settings.redis_prefix, batas=batas):
                sys.stdout.write(f"{id_mati}\t{isi.get('grup')}\t{isi.get('event_type')}\n")
            return 0
        konsumen = {k.grup: k for k in pekerja.rakit_konsumen(engine, redis, settings)}
        kode = 0
        for id_mati in ids:
            hasil = await events.putar_ulang_mati(
                engine, redis, settings.redis_prefix, id_mati, konsumen
            )
            sys.stdout.write(f"{id_mati}\t{hasil}\n")
            if hasil not in _SELESAI:
                kode = 1
        return kode
    finally:
        await redis.aclose()
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hvx.stream_mati", description=__doc__)
    sub = ap.add_subparsers(dest="perintah", required=True)
    daftar = sub.add_parser("daftar", help="entri stream mati, terlama dulu")
    daftar.add_argument("--batas", type=int, default=100)
    putar = sub.add_parser("putar", help="putar ulang entri per id")
    putar.add_argument("id", nargs="+")
    a = ap.parse_args(argv)
    settings = platform.Settings()  # dari lingkungan (HVX_*), sama dengan pekerja
    return asyncio.run(
        jalankan(settings, a.perintah, getattr(a, "id", []), getattr(a, "batas", 100))
    )


if __name__ == "__main__":
    sys.exit(main())
