"""spec/07 1.2 — sesi di Redis + dependensi auth: token dicabut → 401 SEKETIKA.

Redis sungguhan; tiap uji memakai awalan kunci acak, jadi tidak ada sisa dari
uji lain yang bisa membuat hasil kebetulan benar.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from redis.asyncio import Redis

from hvx.modules.identity import PenggunaDiperlukan, PenyimpanSesi, Token, penyimpan_sesi
from hvx.modules.identity.sesi import sidik
from hvx.modules.platform import Settings, buat_redis, pasang_penangan_galat

pytestmark = pytest.mark.integration


@pytest.fixture
async def app_sesi(url_redis_uji: str) -> AsyncIterator[FastAPI]:
    app = FastAPI()
    pasang_penangan_galat(app)
    app.state.settings = Settings(
        env="test",
        database_url="postgresql://tidak-dipakai",
        redis_url=url_redis_uji,
        redis_prefix=f"uji-{uuid.uuid4().hex[:12]}",
        access_token_ttl_s=120,
        refresh_token_ttl_s=3_600,
    )
    app.state.redis = buat_redis(url_redis_uji, socket_timeout_s=5, connect_timeout_s=2)

    @app.get("/rahasia")
    async def rahasia(pengguna: PenggunaDiperlukan) -> dict[str, str]:
        return {"user_id": str(pengguna.user_id)}

    try:
        yield app
    finally:
        await app.state.redis.aclose()


def _penyimpan(app: FastAPI) -> PenyimpanSesi:
    class _Permintaan:  # cukup untuk platform.redis_dari/settings_dari
        def __init__(self, app: FastAPI) -> None:
            self.app = app

    return penyimpan_sesi(_Permintaan(app))  # type: ignore[arg-type]


async def _get(app: FastAPI, token: str | None) -> httpx.Response:
    header = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://uji"
    ) as k:
        return await k.get("/rahasia", headers=header)


async def test_token_akses_yang_sah_meloloskan_pengguna_yang_benar(app_sesi: FastAPI) -> None:
    uid = uuid.uuid4()
    token = await _penyimpan(app_sesi).buat(uid)

    r = await _get(app_sesi, token.access_token)

    assert r.status_code == 200
    assert r.json() == {"user_id": str(uid)}
    assert token.access_token.startswith("hvxa_")
    assert token.refresh_token.startswith("hvxr_")


@pytest.mark.parametrize("token", [None, "hvxa_palsu", "bukan-token"])
async def test_tanpa_token_atau_token_palsu_401_beramplop(
    app_sesi: FastAPI, token: str | None
) -> None:
    r = await _get(app_sesi, token)

    assert r.status_code == 401
    assert r.json()["error"]["code"] == "unauthenticated"
    assert r.headers["www-authenticate"].startswith("Bearer")


async def test_token_segar_tidak_bisa_dipakai_sebagai_token_akses(app_sesi: FastAPI) -> None:
    token = await _penyimpan(app_sesi).buat(uuid.uuid4())

    assert (await _get(app_sesi, token.refresh_token)).status_code == 401


async def test_sesi_dicabut_401_seketika(app_sesi: FastAPI) -> None:
    """DoD 1.2 — tidak menunggu kedaluwarsa token."""
    penyimpan = _penyimpan(app_sesi)
    uid = uuid.uuid4()
    token = await penyimpan.buat(uid)
    sesi = await penyimpan.periksa_akses(token.access_token)
    assert sesi is not None
    assert (await _get(app_sesi, token.access_token)).status_code == 200

    await penyimpan.cabut(sesi.sesi_id)

    assert (await _get(app_sesi, token.access_token)).status_code == 401
    assert (await penyimpan.segarkan(token.refresh_token)).token is None


async def test_penyegaran_merotasi_kedua_token(app_sesi: FastAPI) -> None:
    penyimpan = _penyimpan(app_sesi)
    lama = await penyimpan.buat(uuid.uuid4())

    hasil = await penyimpan.segarkan(lama.refresh_token)

    assert hasil.token is not None
    baru = hasil.token
    assert {baru.access_token, baru.refresh_token}.isdisjoint(
        {lama.access_token, lama.refresh_token}
    )
    assert (await _get(app_sesi, lama.access_token)).status_code == 401, "token akses lama hidup"
    assert (await _get(app_sesi, baru.access_token)).status_code == 200


async def test_token_segar_bekas_dipakai_lagi_mencabut_seluruh_sesi(app_sesi: FastAPI) -> None:
    """Pencuri memakai token segar lama sesudah pemiliknya merotasi: KEDUANYA kehilangan sesi."""
    penyimpan = _penyimpan(app_sesi)
    uid = uuid.uuid4()
    lama = await penyimpan.buat(uid)
    baru = (await penyimpan.segarkan(lama.refresh_token)).token
    assert baru is not None

    curian = await penyimpan.segarkan(lama.refresh_token)

    assert curian.token is None
    assert curian.dipakai_ulang is not None
    assert curian.dipakai_ulang.user_id == uid
    assert (await _get(app_sesi, baru.access_token)).status_code == 401
    assert (await penyimpan.segarkan(baru.refresh_token)).token is None


async def test_cabut_semua_mencabut_tiap_sesi_pengguna_saja(app_sesi: FastAPI) -> None:
    penyimpan = _penyimpan(app_sesi)
    a, b = uuid.uuid4(), uuid.uuid4()
    milik_a = [await penyimpan.buat(a) for _ in range(3)]
    milik_b = await penyimpan.buat(b)

    assert await penyimpan.cabut_semua(a) == 3

    for token in milik_a:
        assert (await _get(app_sesi, token.access_token)).status_code == 401
    assert (await _get(app_sesi, milik_b.access_token)).status_code == 200


async def test_redis_hanya_menyimpan_sidik_token(app_sesi: FastAPI) -> None:
    """Kunci DAN nilai tiap tipe — string, hash, himpunan — sesudah dibuat dan diputar.

    🔴 Versi pertama hanya membaca nilai bertipe string: token mentah di catatan
    sesi (hash) lolos (tinjauan Sprint 1).
    """
    penyimpan = _penyimpan(app_sesi)
    redis = app_sesi.state.redis
    awalan = app_sesi.state.settings.redis_prefix

    async def isi_redis() -> tuple[set[str], str]:
        jenis_ada: set[str] = set()
        teks: list[str] = []
        async for k in redis.scan_iter(match=f"{awalan}:*"):
            jenis = await redis.type(k)
            jenis_ada.add(jenis)
            teks.append(k)
            if jenis == "string":
                teks.append(await redis.get(k) or "")
            elif jenis == "hash":
                teks.extend((await redis.hgetall(k)).values())
            elif jenis == "set":
                teks.extend(await redis.smembers(k))
        return jenis_ada, " ".join(teks)

    lama = await penyimpan.buat(uuid.uuid4())
    jenis_dibuat, sesudah_dibuat = await isi_redis()
    baru = (await penyimpan.segarkan(lama.refresh_token)).token
    assert baru is not None
    _, sesudah_diputar = await isi_redis()

    assert jenis_dibuat >= {"string", "hash", "set"}, jenis_dibuat
    for keadaan, semua, token in (
        ("dibuat", sesudah_dibuat, lama),
        ("diputar", sesudah_diputar, lama),
        ("diputar", sesudah_diputar, baru),
    ):
        for t in (token.access_token, token.refresh_token):
            assert t not in semua, f"token mentah tersimpan di Redis (sesudah {keadaan})"


async def test_umur_token_akses_dan_segar_sesuai_pengaturan(app_sesi: FastAPI) -> None:
    """🔴 Tinjauan Sprint 1: tidak ada uji yang membaca umur token. Tertukar di skrip
    rotasi, token akses hidup 30 hari sementara `expires_in` tetap menulis 900 —
    dan akun yang ditangguhkan memakainya selama itu."""
    s = app_sesi.state.settings
    penyimpan = _penyimpan(app_sesi)
    redis = app_sesi.state.redis

    async def umur_ms(token: Token) -> tuple[int, int]:
        akses = await redis.pttl(f"{s.redis_prefix}:sesi:akses:{sidik(token.access_token)}")
        segar = await redis.pttl(f"{s.redis_prefix}:sesi:segar:{sidik(token.refresh_token)}")
        return akses, segar

    dibuat = await penyimpan.buat(uuid.uuid4())
    umur = {"dibuat": await umur_ms(dibuat)}
    diputar = (await penyimpan.segarkan(dibuat.refresh_token)).token
    assert diputar is not None
    umur["diputar"] = await umur_ms(diputar)

    akses_ms, segar_ms = s.access_token_ttl_s * 1000, s.refresh_token_ttl_s * 1000
    for asal, (akses, segar) in umur.items():
        assert akses_ms - 5_000 < akses <= akses_ms, (
            f"token akses {asal} hidup {akses} ms, bukan {akses_ms} ms"
        )
        assert segar_ms - 5_000 < segar <= segar_ms, (
            f"token segar {asal} hidup {segar} ms, bukan {segar_ms} ms"
        )
    assert dibuat.expires_in == diputar.expires_in == s.access_token_ttl_s


async def test_catatan_sesi_tanpa_user_id_tidak_bisa_diputar_dan_tetap_bisa_dicabut(
    app_sesi: FastAPI,
) -> None:
    """Bentuk rusak yang dibuat versi pertama (tinjauan Sprint 1) — Redis bertahan
    antar-pemasangan (`appendonly`), jadi catatan itu bisa hidup lebih lama dari kodenya."""
    penyimpan = _penyimpan(app_sesi)
    redis = app_sesi.state.redis
    awalan = app_sesi.state.settings.redis_prefix

    async def sesi_rusak() -> tuple[Token, str]:
        token = await penyimpan.buat(uuid.uuid4())
        sesi = await penyimpan.periksa_akses(token.access_token)
        assert sesi is not None
        await redis.hdel(f"{awalan}:sesi:{sesi.sesi_id}", "user_id")
        return token, str(sesi.sesi_id)

    diputar, _ = await sesi_rusak()
    assert (await penyimpan.segarkan(diputar.refresh_token)).token is None, (
        "catatan sesi tanpa user_id masih bisa diputar"
    )
    assert await penyimpan.periksa_akses(diputar.access_token) is None

    dicabut, sesi_id = await sesi_rusak()
    await penyimpan.cabut(uuid.UUID(sesi_id))
    assert await penyimpan.periksa_akses(dicabut.access_token) is None, (
        "catatan sesi tanpa user_id tidak bisa dicabut"
    )
    assert (await penyimpan.segarkan(dicabut.refresh_token)).token is None


# ── celah antarperintah: keluar · penyegaran · pencurian · cabut semua ────────


class _Sela:
    """Menyisipkan operasi lain SESUDAH perintah Redis ke-`ke` dari satu klien.

    Dipasang pada `execute_command` dan `pipeline().execute` — semua jalan
    `PenyimpanSesi` ke Redis, skrip Lua termasuk. Uji tidak tahu bagaimana
    operasinya ditulis (perintah lepas, MULTI, skrip): ia mencoba TIAP celah
    yang ada. 🔴 Versi pertama `sesi.py` membaca catatan sesi lalu menulis di
    MULTI terpisah — keluar yang jatuh di celah itu dihidupkan kembali oleh
    penyegaran (tinjauan Sprint 1).
    """

    def __init__(self, klien: Redis) -> None:
        self.dikirim = 0
        self._ke = 0
        self._sisipan: Callable[[], Awaitable[None]] | None = None
        kirim, pipa = klien.execute_command, klien.pipeline

        async def kirim_diamati(*args: Any, **opsi: Any) -> Any:
            hasil = await kirim(*args, **opsi)
            await self._sesudah_perintah()
            return hasil

        def pipa_diamati(*args: Any, **opsi: Any) -> Any:
            p = pipa(*args, **opsi)
            jalankan = p.execute

            async def jalankan_diamati(*a: Any, **o: Any) -> Any:
                hasil = await jalankan(*a, **o)
                await self._sesudah_perintah()
                return hasil

            p.execute = jalankan_diamati  # type: ignore[method-assign]
            return p

        klien.execute_command = kirim_diamati  # type: ignore[method-assign]
        klien.pipeline = pipa_diamati  # type: ignore[method-assign]

    async def _sesudah_perintah(self) -> None:
        self.dikirim += 1
        if self._sisipan is not None and self.dikirim == self._ke:
            sisipan, self._sisipan = self._sisipan, None
            await sisipan()

    async def jalankan(
        self, ke: int, amati: Callable[[], Awaitable[None]], sisip: Callable[[], Awaitable[None]]
    ) -> None:
        """`ke = 0`: sisipan sebelum operasi; `ke` melewati jumlah perintahnya: sesudahnya."""
        self.dikirim, self._ke = 0, ke
        if ke == 0:
            await sisip()
            await amati()
            return
        self._sisipan = sisip
        await amati()
        if self._sisipan is not None:
            self._sisipan = None
            await sisip()


@dataclass
class _Lakon:
    amati: Callable[[], Awaitable[None]]
    sisip: Callable[[], Awaitable[None]]
    token_hidup: Callable[[], Awaitable[list[str]]]


async def _lakon(nama: str, diamati: PenyimpanSesi, bersih: PenyimpanSesi) -> _Lakon:
    uid = uuid.uuid4()
    terbit: list[Token] = []

    async def segarkan(penyimpan: PenyimpanSesi, token_segar: str) -> None:
        hasil = await penyimpan.segarkan(token_segar)
        if hasil.token is not None:
            terbit.append(hasil.token)

    async def token_hidup() -> list[str]:
        if nama == "cabut-semua-diselingi-masuk":
            # sesi yang lahir di sela tidak wajib mati — wajib TERCATAT, supaya
            # "cabut semua" berikutnya (ganti sandi, hapus akun) masih mencapainya
            await bersih.cabut_semua(uid)
        hidup = [
            f"akses#{i}" for i, t in enumerate(terbit) if await bersih.periksa_akses(t.access_token)
        ]
        for i, t in enumerate(list(terbit)):
            try:
                if (await bersih.segarkan(t.refresh_token)).token is not None:
                    hidup.append(f"segar#{i}")
            except Exception as galat:  # sesi yang tidak bisa dicabut lagi juga hidup
                hidup.append(f"segar#{i} → {type(galat).__name__}: {galat}")
        return hidup

    awal = await bersih.buat(uid)
    terbit.append(awal)
    sesi = await bersih.periksa_akses(awal.access_token)
    assert sesi is not None
    sesi_id = sesi.sesi_id

    async def keluar(penyimpan: PenyimpanSesi) -> None:
        await penyimpan.cabut(sesi_id)

    if nama == "segarkan-diselingi-keluar":
        return _Lakon(
            lambda: segarkan(diamati, awal.refresh_token), lambda: keluar(bersih), token_hidup
        )
    if nama == "keluar-diselingi-segarkan":
        return _Lakon(
            lambda: keluar(diamati), lambda: segarkan(bersih, awal.refresh_token), token_hidup
        )
    if nama == "pencurian-diselingi-penyegaran-pencuri":
        # pemilik sudah memutar token; pencuri memegang pasangan TERBARU dan
        # memutarnya tepat saat token bekas pemilik memicu pencabutan
        terbaru = (await bersih.segarkan(awal.refresh_token)).token
        assert terbaru is not None
        terbit.append(terbaru)
        segar_pencuri = terbaru.refresh_token
        return _Lakon(
            lambda: segarkan(diamati, awal.refresh_token),
            lambda: segarkan(bersih, segar_pencuri),
            token_hidup,
        )
    assert nama == "cabut-semua-diselingi-masuk"
    terbit.append(await bersih.buat(uid))

    async def cabut_semua() -> None:
        await diamati.cabut_semua(uid)

    async def masuk_lagi() -> None:
        terbit.append(await bersih.buat(uid))

    return _Lakon(cabut_semua, masuk_lagi, token_hidup)


@pytest.mark.parametrize(
    "nama",
    [
        "segarkan-diselingi-keluar",
        "keluar-diselingi-segarkan",
        "pencurian-diselingi-penyegaran-pencuri",
        "cabut-semua-diselingi-masuk",
    ],
)
async def test_sesi_yang_dicabut_tidak_hidup_lagi_di_celah_mana_pun(
    app_sesi: FastAPI, url_redis_uji: str, nama: str
) -> None:
    """DoD 1.2 di bawah permintaan serentak: pencabutan tidak kalah balapan."""
    bersih = _penyimpan(app_sesi)
    klien = buat_redis(url_redis_uji, socket_timeout_s=5, connect_timeout_s=2)
    sela = _Sela(klien)
    s = app_sesi.state.settings
    diamati = PenyimpanSesi(klien, s.redis_prefix, s.access_token_ttl_s, s.refresh_token_ttl_s)
    try:
        # putaran kering: berapa perintah yang dikirim operasinya tanpa disela
        lakon = await _lakon(nama, diamati, bersih)
        await sela.jalankan(10**6, lakon.amati, lakon.sisip)
        celah = sela.dikirim
        for ke in range(celah + 1):
            lakon = await _lakon(nama, diamati, bersih)
            await sela.jalankan(ke, lakon.amati, lakon.sisip)
            hidup = await lakon.token_hidup()
            assert not hidup, (
                f"sesi yang dicabut hidup lagi — {nama}, disela sesudah perintah ke-{ke} "
                f"dari {celah}: {hidup}"
            )
    finally:
        await klien.aclose()
