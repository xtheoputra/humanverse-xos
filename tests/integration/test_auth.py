"""spec/07 1.1 — register · login · refresh · logout: argon2id; refresh token berotasi.

Semua lewat HTTP ke create_app yang tersambung sebagai PERAN APLIKASI —
termasuk RLS, fungsi SECURITY DEFINER login, dan GRANT hanya-tambah audit.
"""

from __future__ import annotations

import uuid
from typing import Any

import psycopg
import pytest
from _bantuan_db import ApiUji, psycopg_dsn
from argon2 import PasswordHasher

pytestmark = pytest.mark.integration

SANDI = "sandi-panjang-uji-2026"
V = "2026-09-17"


def _daftar_badan(alamat: str, **ubah: Any) -> dict[str, Any]:
    badan: dict[str, Any] = {
        "email": alamat,
        "password": SANDI,
        "display_name": "Nadia",
        "timezone": "Asia/Jakarta",
        "consents": {"policy_version": V, "terms": True, "privacy": True},
    }
    badan.update(ubah)
    return badan


def _email() -> str:
    return f"{uuid.uuid4().hex[:12]}@uji.id"


def _pemilik(api: ApiUji) -> psycopg.Connection[Any]:
    return psycopg.connect(psycopg_dsn(api.db.dsn_pemilik), autocommit=True)


async def test_daftar_menulis_akun_persetujuan_profil_dan_audit_dalam_satu_langkah(
    api_uji: ApiUji,
) -> None:
    email = _email()

    r = await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(email))

    assert r.status_code == 201, r.text
    isi = r.json()
    uid = uuid.UUID(isi["user"]["id"])
    assert isi["user"]["email"] == email
    assert isi["tokens"]["token_type"] == "bearer"
    assert SANDI not in r.text
    with _pemilik(api_uji) as k:
        (h,) = k.execute("SELECT password_hash FROM users WHERE id = %s", (uid,)).fetchone() or (
            "",
        )
        persetujuan = k.execute(
            "SELECT kind, purpose, granted, data_scopes FROM consents WHERE user_id = %s "
            "ORDER BY created_at",
            (uid,),
        ).fetchall()
        profil = k.execute(
            "SELECT display_name, timezone FROM profiles WHERE user_id = %s", (uid,)
        ).fetchone()
        aksi = [
            r[0]
            for r in k.execute(
                "SELECT action FROM audit_logs WHERE user_id = %s ORDER BY id", (uid,)
            )
        ]
    assert h.startswith("$argon2id$")
    # model_training tidak dikirim = DITOLAK, dan tetap tercatat sebagai jawaban
    assert persetujuan == [
        ("terms", "service", True, []),
        ("privacy", "service", True, []),
        ("model_training", "model_training", False, []),
    ]
    assert profil == ("Nadia", "Asia/Jakarta")
    assert aksi == ["consent.granted", "consent.granted", "consent.declined", "account.registered"]

    saya = await api_uji.klien.get(
        "/v1/me", headers={"Authorization": f"Bearer {isi['tokens']['access_token']}"}
    )
    assert saya.status_code == 200
    assert saya.json()["user"]["id"] == str(uid)


async def test_daftar_dengan_persetujuan_pelatihan_bercakupan(api_uji: ApiUji) -> None:
    badan = _daftar_badan(_email())
    badan["consents"]["model_training"] = {"granted": True, "data_scopes": ["habits", "checkins"]}

    r = await api_uji.klien.post("/v1/auth/register", json=badan)

    assert r.status_code == 201, r.text
    with _pemilik(api_uji) as k:
        baris = k.execute(
            "SELECT granted, data_scopes FROM consents "
            "WHERE user_id = %s AND kind = 'model_training'",
            (r.json()["user"]["id"],),
        ).fetchone()
    assert baris == (True, ["checkins", "habits"])


@pytest.mark.parametrize(
    ("ubah", "status", "kode"),
    [
        ({"consents": {"policy_version": V, "terms": False, "privacy": True}},
         422, "consent_required"),
        ({"consents": {"policy_version": V, "terms": True, "privacy": False}},
         422, "consent_required"),
        ({"password": "pendek-14-krkt"}, 400, "invalid_request"),
        ({"timezone": "Asia/Batavia"}, 400, "invalid_request"),
        ({"email": "bukan-email"}, 400, "invalid_request"),
        ({"role": "admin"}, 400, "invalid_request"),
        (
            {"consents": {"policy_version": V, "terms": True, "privacy": True,
                          "model_training": {"granted": True}}},
            400, "invalid_request",
        ),
    ],
)  # fmt: skip
async def test_daftar_yang_ditolak_tidak_menulis_apa_pun(
    api_uji: ApiUji, ubah: dict[str, Any], status: int, kode: str
) -> None:
    email = _email()

    r = await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(email, **ubah))

    assert r.status_code == status, r.text
    assert r.json()["error"]["code"] == kode
    assert "pendek-14-krkt" not in r.text
    with _pemilik(api_uji) as k:
        assert k.execute("SELECT count(*) FROM users WHERE email = %s", (email,)).fetchone() == (0,)


async def test_email_yang_sama_tanpa_peduli_huruf_besar_409(api_uji: ApiUji) -> None:
    email = _email()
    assert (
        await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(email))
    ).status_code == 201

    r = await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(email.upper()))

    assert r.status_code == 409, r.text
    assert r.json()["error"]["code"] == "email_taken"


async def _daftar(api: ApiUji) -> tuple[str, dict[str, Any]]:
    email = _email()
    r = await api.klien.post("/v1/auth/register", json=_daftar_badan(email))
    assert r.status_code == 201, r.text
    return email, r.json()


async def test_masuk_berhasil_mencatat_waktu_dan_audit(api_uji: ApiUji) -> None:
    email, akun = await _daftar(api_uji)

    r = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})

    assert r.status_code == 200, r.text
    assert r.json()["user"]["id"] == akun["user"]["id"]
    assert r.json()["tokens"]["access_token"] != akun["tokens"]["access_token"]
    with _pemilik(api_uji) as k:
        (terakhir,) = k.execute(
            "SELECT last_login_at FROM users WHERE id = %s", (akun["user"]["id"],)
        ).fetchone() or (None,)
        (aksi,) = k.execute(
            "SELECT action FROM audit_logs WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            (akun["user"]["id"],),
        ).fetchone() or (None,)
    assert terakhir is not None
    assert aksi == "session.login_succeeded"


async def test_sandi_salah_dan_email_tak_dikenal_dijawab_sama_dan_diaudit_berbeda(
    api_uji: ApiUji,
) -> None:
    email, akun = await _daftar(api_uji)
    salah = await api_uji.klien.post(
        "/v1/auth/login", json={"email": email, "password": "sandi-yang-keliru-sekali"}
    )
    tak_dikenal = await api_uji.klien.post(
        "/v1/auth/login", json={"email": _email(), "password": "sandi-yang-keliru-sekali"}
    )

    assert salah.status_code == tak_dikenal.status_code == 401
    assert salah.json() == tak_dikenal.json()
    with _pemilik(api_uji) as k:
        milik_akun = k.execute(
            "SELECT metadata FROM audit_logs "
            "WHERE user_id = %s AND action = 'session.login_failed'",
            (akun["user"]["id"],),
        ).fetchall()
        sistem = k.execute(
            "SELECT metadata::text FROM audit_logs WHERE user_id IS NULL "
            "AND action = 'session.login_failed'"
        ).fetchall()
    assert milik_akun == [({"alasan": "kredensial"},)]
    assert sistem
    assert all("@" not in m for (m,) in sistem), "email tak dikenal masuk jejak audit"


async def test_akun_tidak_aktif_dengan_sandi_benar_403(api_uji: ApiUji) -> None:
    email, akun = await _daftar(api_uji)
    with _pemilik(api_uji) as k:
        k.execute("UPDATE users SET status = 'suspended' WHERE id = %s", (akun["user"]["id"],))

    r = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})

    assert r.status_code == 403
    assert r.json()["error"]["code"] == "account_not_active"


async def test_hash_berparameter_lama_diperbarui_saat_masuk(api_uji: ApiUji) -> None:
    email, akun = await _daftar(api_uji)
    lemah = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash(SANDI)
    with _pemilik(api_uji) as k:
        k.execute("UPDATE users SET password_hash = %s WHERE id = %s", (lemah, akun["user"]["id"]))

    r = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})

    assert r.status_code == 200, r.text
    with _pemilik(api_uji) as k:
        (baru,) = k.execute(
            "SELECT password_hash FROM users WHERE id = %s", (akun["user"]["id"],)
        ).fetchone() or ("",)
    assert baru != lemah
    assert "m=65536" in baru


async def test_segarkan_merotasi_dan_token_bekas_mencabut_sesi(api_uji: ApiUji) -> None:
    _, akun = await _daftar(api_uji)
    lama = akun["tokens"]

    r = await api_uji.klien.post("/v1/auth/refresh", json={"refresh_token": lama["refresh_token"]})
    assert r.status_code == 200, r.text
    baru = r.json()["tokens"]
    assert baru["refresh_token"] != lama["refresh_token"]

    curian = await api_uji.klien.post(
        "/v1/auth/refresh", json={"refresh_token": lama["refresh_token"]}
    )
    assert curian.status_code == 401
    assert curian.json()["error"]["code"] == "invalid_refresh_token"
    # pencurian terdeteksi → pasangan TERBARU pun mati
    saya = await api_uji.klien.get(
        "/v1/me", headers={"Authorization": f"Bearer {baru['access_token']}"}
    )
    assert saya.status_code == 401
    with _pemilik(api_uji) as k:
        (jumlah,) = k.execute(
            "SELECT count(*) FROM audit_logs "
            "WHERE user_id = %s AND action = 'session.refresh_reused'",
            (akun["user"]["id"],),
        ).fetchone() or (0,)
    assert jumlah == 1


async def test_keluar_204_dan_token_akses_401_seketika(api_uji: ApiUji) -> None:
    _, akun = await _daftar(api_uji)
    auth = {"Authorization": f"Bearer {akun['tokens']['access_token']}"}
    assert (await api_uji.klien.get("/v1/me", headers=auth)).status_code == 200

    r = await api_uji.klien.post("/v1/auth/logout", headers=auth)

    assert r.status_code == 204
    assert (await api_uji.klien.get("/v1/me", headers=auth)).status_code == 401
    segar = await api_uji.klien.post(
        "/v1/auth/refresh", json={"refresh_token": akun["tokens"]["refresh_token"]}
    )
    assert segar.status_code == 401
