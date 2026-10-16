"""Koneksi Redis 7 — sesi, cache, dan Streams (arch/09 §1).

Batas waktu soket klien ini SENGAJA terpisah dari batas waktu `/health`. Versi
pertama memakai `HVX_HEALTH_TIMEOUT_S` (1 dtk) sebagai `socket_timeout` klien
bersama — sehingga `XREADGROUP BLOCK 5000` yang direncanakan tugas 3.3 akan
gagal sesudah satu detik, dan mengubah batas pemeriksa kesehatan diam-diam
mengubah batas setiap perintah Redis. `/health` tidak membutuhkannya: ping-nya
sudah dibatasi `health._jalankan`.

⚠️ Konsumen Streams yang memblokir (3.3) wajib memakai klien tersendiri dengan
`socket_timeout` lebih panjang dari waktu BLOCK-nya — jangan memanjangkan
klien bersama ini, atau sesi dan cache kehilangan batasnya.
"""

from __future__ import annotations

from redis.asyncio import Redis


def buat_redis(url: str, socket_timeout_s: float, connect_timeout_s: float) -> Redis:
    return Redis.from_url(
        url,
        decode_responses=True,
        socket_timeout=socket_timeout_s,
        socket_connect_timeout=connect_timeout_s,
    )


async def ping_redis(klien: Redis) -> None:
    await klien.ping()
