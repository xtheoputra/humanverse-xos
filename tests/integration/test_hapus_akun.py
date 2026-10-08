"""spec/07 6.5 (Stage A) — DELETE /me + POST /me/restore + login pending_deletion.

Tahap 1 alur hapus akun: `pending_deletion` + jadwal 30 hari, SEMUA sesi dicabut
seketika. Pengguna masih bisa login dalam tenggang untuk membatalkan (keputusan
pemilik 5 Okt 2026). Status diperiksa di basis data (pemilik skema), bukan hanya
kode status.
"""

from __future__ import annotations

import asyncio
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, auth, psycopg_dsn
from test_auth import SANDI, _daftar_badan, _email

pytestmark = pytest.mark.integration


async def _daftar(api: ApiUji) -> tuple[str, str, str]:
    """(email, user_id, access_token) dari registrasi sungguhan — hash argon2 asli."""
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(_email()))
    assert r.status_code == 201, r.text
    isi = r.json()
    return isi["user"]["email"], isi["user"]["id"], isi["tokens"]["access_token"]


def _akun(api: ApiUji, uid: str) -> tuple[Any, ...]:
    with psycopg.connect(psycopg_dsn(api.db.dsn_pemilik)) as k:
        return k.execute(
            "SELECT status, deletion_scheduled_at FROM users WHERE id = %s", (uid,)
        ).fetchone()


async def test_hapus_menjadwalkan_dan_mencabut_semua_sesi(api_uji: ApiUji) -> None:
    email, uid, token1 = await _daftar(api_uji)
    # Sesi KEDUA: login lagi → dua token hidup, keduanya harus mati sesudah DELETE.
    masuk = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    token2 = masuk.json()["tokens"]["access_token"]

    r = await api_uji.klien.request(
        "DELETE", "/v1/me", json={"password": SANDI}, headers=auth(token2)
    )
    assert r.status_code == 202, r.text
    assert r.json()["deletion_scheduled_at"], "jadwal hapus tidak dikembalikan"

    status, dijadwalkan = _akun(api_uji, uid)
    assert status == "pending_deletion"
    assert dijadwalkan is not None, "deletion_scheduled_at tidak diisi"

    # Semua sesi dicabut SEKETIKA — kedua token ditolak.
    for t in (token1, token2):
        cek = await api_uji.klien.get("/v1/me", headers=auth(t))
        assert cek.status_code == 401, "sesi tidak dicabut seketika saat hapus akun"


async def test_sandi_salah_tidak_menjadwalkan(api_uji: ApiUji) -> None:
    _, uid, token = await _daftar(api_uji)

    r = await api_uji.klien.request(
        "DELETE", "/v1/me", json={"password": "sandi-salah-sekali-2026"}, headers=auth(token)
    )

    assert r.status_code == 403, f"akun dijadwalkan hapus tanpa sandi benar: {r.text}"
    assert r.json()["error"]["code"] == "invalid_credentials"
    assert _akun(api_uji, uid)[0] == "active", "akun dijadwalkan hapus tanpa sandi benar"


async def test_login_pending_deletion_lalu_restore(api_uji: ApiUji) -> None:
    email, uid, token = await _daftar(api_uji)
    await api_uji.klien.request("DELETE", "/v1/me", json={"password": SANDI}, headers=auth(token))
    assert _akun(api_uji, uid)[0] == "pending_deletion"

    # Login DIIZINKAN untuk pending_deletion — satu-satunya jalan membatalkan.
    masuk = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    assert masuk.status_code == 200, "login pending_deletion ditolak — restore jadi mustahil"
    token_baru = masuk.json()["tokens"]["access_token"]

    pulih = await api_uji.klien.post("/v1/me/restore", headers=auth(token_baru))
    assert pulih.status_code == 200, pulih.text
    assert pulih.json()["status"] == "active"
    status, dijadwalkan = _akun(api_uji, uid)
    assert status == "active"
    assert dijadwalkan is None, "jadwal hapus tidak dibatalkan saat restore"


async def test_restore_idempoten_pada_akun_aktif(api_uji: ApiUji) -> None:
    _, uid, token = await _daftar(api_uji)
    # Akun masih active — restore = no-op 200, bukan galat.
    r = await api_uji.klien.post("/v1/me/restore", headers=auth(token))
    assert r.status_code == 200, r.text
    assert _akun(api_uji, uid)[0] == "active"


# ── Tinjauan kontrak Sprint 5–6 (8 Okt 2026) ─────────────────────────────────


async def test_hapus_serentak_dua_kali_keduanya_202_dengan_jadwal_yang_sama(
    api_uji: ApiUji,
) -> None:
    """spec/04: `DELETE /me` *idempoten — saat sudah `pending_deletion` ia mengembalikan
    jadwal yang ada*. Ketukan ganda di aplikasi = dua permintaan serentak: yang kalah
    balapan tidak boleh menjawab galat (*“Akun tidak bisa dijadwalkan hapus.”*) untuk akun
    yang SUDAH dijadwalkan dihapus — pengguna mengira penghapusannya gagal."""
    _, uid, token = await _daftar(api_uji)

    async def hapus() -> Any:
        return await api_uji.klien.request(
            "DELETE", "/v1/me", json={"password": SANDI}, headers=auth(token)
        )

    a, b = await asyncio.gather(hapus(), hapus())

    kode = sorted((a.status_code, b.status_code))
    assert kode == [202, 202], (
        f"DELETE /me serentak tidak idempoten: {a.status_code} {a.text} · {b.status_code} {b.text}"
    )
    assert a.json()["deletion_scheduled_at"] == b.json()["deletion_scheduled_at"]
    assert _akun(api_uji, uid)[0] == "pending_deletion"


@pytest.mark.parametrize("status", ["suspended", "terhapus"])
async def test_restore_tidak_mengaku_aktif_untuk_akun_yang_tidak_aktif(
    api_uji: ApiUji, status: str
) -> None:
    """Tinjauan S5–6 (E-245, dicurigai lensa keamanan DAN kontrak): `UPDATE` restore hanya
    menyentuh `pending_deletion`, tetapi rutenya menjawab `200 {"status": "active"}` untuk
    akun `suspended` — atau yang barisnya sudah tiada — selama token aksesnya masih hidup.
    Statusnya tidak berubah, jadi jawabannya bohong; kini `403 account_not_active`."""
    _, uid, token = await _daftar(api_uji)
    with psycopg.connect(psycopg_dsn(api_uji.db.dsn_pemilik)) as k:
        if status == "suspended":
            k.execute("UPDATE users SET status = 'suspended' WHERE id = %s", (uid,))
        else:
            k.execute("DELETE FROM users WHERE id = %s", (uid,))

    r = await api_uji.klien.post("/v1/me/restore", headers=auth(token))

    assert r.status_code == 403, f"restore mengaku memulihkan akun {status}: {r.text}"
    assert r.json()["error"]["code"] == "account_not_active"
    if status == "suspended":
        assert _akun(api_uji, uid)[0] == "suspended", "restore mengaktifkan akun suspended"
