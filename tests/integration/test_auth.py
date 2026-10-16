"""spec/07 1.1 — register · login · refresh · logout: argon2id; refresh token berotasi.

Semua lewat HTTP ke create_app yang tersambung sebagai PERAN APLIKASI —
termasuk RLS, fungsi SECURITY DEFINER login, dan GRANT hanya-tambah audit.
"""

from __future__ import annotations

import re
import secrets
import uuid
from typing import Any

import httpx
import psycopg
import pytest
from _bantuan_db import ApiUji, psycopg_dsn
from argon2 import PasswordHasher
from sqlalchemy import event

from hvx.modules.identity import repository

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


@pytest.mark.parametrize(
    "ubah",
    [
        pytest.param({"display_name": "Na\u0000dia"}, id="nama"),
        pytest.param(
            {"consents": {"policy_version": "v\u00001", "terms": True, "privacy": True}},
            id="versi-kebijakan",
        ),
    ],
)
async def test_nul_di_teks_bebas_ditolak_400_bukan_500(
    api_uji: ApiUji, ubah: dict[str, Any]
) -> None:
    """🔴 Tinjauan Sprint 1: PostgreSQL menolak NUL di `text` — nilai yang lolos validasi
    gagal di basis data sebagai 500 (dan tercatat sebagai galat server)."""
    r = await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(_email(), **ubah))

    assert r.status_code == 400, f"NUL lolos validasi sampai basis data: {r.status_code}"
    assert r.json()["error"]["code"] == "invalid_request"


async def test_sandi_yang_mudah_ditebak_422_dengan_alasan_tanpa_mengutipnya(
    api_uji: ApiUji,
) -> None:
    email = _email()

    r = await api_uji.klien.post(
        "/v1/auth/register", json=_daftar_badan(email, password="passwordpassword")
    )

    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "password_rejected"
    assert r.json()["error"]["details"] == {"reason": "repetitive"}
    assert "passwordpassword" not in r.text
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


async def test_gagal_masuk_akun_ada_dan_tidak_ada_menjalankan_kueri_yang_sama(
    api_uji: ApiUji,
) -> None:
    """Satu verifikasi argon2 untuk keduanya menyamakan WAKTU — kerja basis data pun harus sama.

    🔴 Versi pertama mencatat kegagalan akun yang ada di `transaksi_pengguna`
    (set_config + INSERT) dan akun tak dikenal di transaksi biasa (INSERT saja):
    jawaban untuk email terdaftar selalu satu perjalanan basis data lebih lambat
    (tinjauan Sprint 1).
    """
    email, _ = await _daftar(api_uji)
    kueri: list[str] = []
    mesin = api_uji.app.state.engine.sync_engine

    def catat(_k: Any, _kursor: Any, pernyataan: str, *_: Any) -> None:
        kueri.append(" ".join(pernyataan.split())[:48])

    event.listen(mesin, "before_cursor_execute", catat)
    try:
        salah = {"email": email, "password": "sandi-yang-keliru-sekali"}
        assert (await api_uji.klien.post("/v1/auth/login", json=salah)).status_code == 401
        akun_ada, kueri[:] = list(kueri), []
        asing = {"email": _email(), "password": "sandi-yang-keliru-sekali"}
        assert (await api_uji.klien.post("/v1/auth/login", json=asing)).status_code == 401
        akun_tak_ada = list(kueri)
    finally:
        event.remove(mesin, "before_cursor_execute", catat)

    assert len(akun_ada) == len(akun_tak_ada), (
        f"gagal masuk akun yang ada menjalankan kueri berbeda: {akun_ada} ≠ {akun_tak_ada}"
    )


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


async def test_akun_yang_tidak_lagi_aktif_tidak_bisa_memperpanjang_sesinya(api_uji: ApiUji) -> None:
    """Status akun dibaca di tiap penyegaran — token akses berumur 15 menit, sesi 30 hari.

    🔴 Versi pertama hanya membaca status saat login: akun yang ditangguhkan
    tetap menyegarkan sesinya tanpa batas. Perbaikan pertamanya hanya mencabut
    sesi yang sedang disegarkan — sesi lain akun itu tetap memakai API
    (tinjauan Sprint 1).
    """
    email, akun = await _daftar(api_uji)
    uid = akun["user"]["id"]
    masuk = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": SANDI})
    assert masuk.status_code == 200
    sesi_lain = {"Authorization": f"Bearer {masuk.json()['tokens']['access_token']}"}
    with _pemilik(api_uji) as k:
        k.execute("UPDATE users SET status = 'suspended' WHERE id = %s", (uid,))

    r = await api_uji.klien.post(
        "/v1/auth/refresh", json={"refresh_token": akun["tokens"]["refresh_token"]}
    )

    assert r.status_code == 401, "akun yang ditangguhkan memperpanjang sesinya sendiri"
    assert r.json()["error"]["code"] == "invalid_refresh_token"
    assert (await api_uji.klien.get("/v1/me", headers=sesi_lain)).status_code == 401, (
        "sesi lain akun yang ditangguhkan tetap memakai API"
    )
    redis = api_uji.app.state.redis
    assert not await redis.smembers(f"{api_uji.awalan_redis}:sesi:pengguna:{uid}")
    with _pemilik(api_uji) as k:
        jejak = k.execute(
            "SELECT metadata->>'alasan' FROM audit_logs "
            "WHERE user_id = %s AND action = 'session.revoked'",
            (uid,),
        ).fetchall()
    assert jejak == [("suspended",)]


async def test_basis_data_tersendat_saat_penyegaran_tidak_membakar_token_segar(
    api_uji: ApiUji, monkeypatch: pytest.MonkeyPatch
) -> None:
    """🔴 Tinjauan Sprint 1: status akun dibaca SESUDAH token diputar — galat basis data
    di langkah itu menjawab 500 dengan token yang sudah terbakar, dan ulangan klien
    dicatat sebagai pencurian (`session.refresh_reused`), sesinya dicabut."""
    _, akun = await _daftar(api_uji)
    segar = {"refresh_token": akun["tokens"]["refresh_token"]}
    ambil_asli = repository.ambil_pengguna
    sisa_gagal = [ConnectionError("basis data tersendat")]

    async def tersendat_sekali(*args: Any, **kwargs: Any) -> Any:
        if sisa_gagal:
            raise sisa_gagal.pop()
        return await ambil_asli(*args, **kwargs)

    monkeypatch.setattr(repository, "ambil_pengguna", tersendat_sekali)

    assert (await api_uji.klien.post("/v1/auth/refresh", json=segar)).status_code == 500
    ulangan = await api_uji.klien.post("/v1/auth/refresh", json=segar)

    assert ulangan.status_code == 200, (
        "penyegaran yang gagal membakar token segar — ulangan klien dianggap pencurian"
    )


async def test_pendengar_pendaftaran_yang_gagal_menggagalkan_seluruh_pendaftaran(
    api_uji: ApiUji,
) -> None:
    """K-17: `identity` tidak mengimpor `profile` — tetapi akun tanpa profil tidak boleh ada.

    🔴 Klaim ini tertulis di K-17 dan ARCHITECTURE.md tanpa satu uji pun: tiap
    pendaftaran yang ditolak di uji lain ditolak SEBELUM transaksinya dibuka
    (tinjauan Sprint 1).
    """

    async def gagal(_conn: Any, _baru: Any) -> None:
        raise RuntimeError("pendengar gagal sesudah profil ditulis")

    api_uji.app.state.pendengar_pendaftaran = (*api_uji.app.state.pendengar_pendaftaran, gagal)

    r = await api_uji.klien.post("/v1/auth/register", json=_daftar_badan(_email()))

    with _pemilik(api_uji) as k:
        sisa = {
            tabel: k.execute(f"SELECT count(*) FROM {tabel}").fetchone()
            for tabel in ("users", "consents", "profiles", "audit_logs")
        }
    assert sisa == dict.fromkeys(sisa, (0,)), (
        f"pendaftaran setengah jadi tersimpan — pendengar yang gagal tidak menggagalkannya: {sisa}"
    )
    assert r.status_code == 500


async def test_sandi_128_karakter_diterima_129_ditolak(api_uji: ApiUji) -> None:
    """NIST SP 800-63B-4: maksimal ≥ 64 — dan batas atas supaya hashing bukan alat DoS."""
    panjang = secrets.token_urlsafe(120)[:128]
    email = _email()

    daftar = await api_uji.klien.post(
        "/v1/auth/register", json=_daftar_badan(email, password=panjang)
    )
    masuk = await api_uji.klien.post("/v1/auth/login", json={"email": email, "password": panjang})
    lewat = await api_uji.klien.post(
        "/v1/auth/register", json=_daftar_badan(_email(), password=panjang + "Q")
    )

    assert (daftar.status_code, masuk.status_code) == (201, 200), daftar.text
    assert lewat.status_code == 400, f"sandi 129 karakter diterima: {lewat.status_code}"
    assert panjang not in lewat.text


async def test_ip_dan_email_tidak_pernah_disimpan_mentah(api_uji: ApiUji) -> None:
    """`audit_logs.ip_hash` dan kunci batas laju — sidik HMAC, bukan nilai mentah.

    🔴 Tinjauan Sprint 1: `test_sidik_ip.py` menguji FUNGSI sidiknya saja. Rute yang
    menulis IP mentah ke audit, atau kunci batas laju yang memuat IP atau email
    apa adanya, lulus semua uji.
    """
    ip = "203.0.113.77"
    email = _email()
    transport = httpx.ASGITransport(app=api_uji.app, client=(ip, 50_000))
    async with httpx.AsyncClient(transport=transport, base_url="http://uji") as klien:
        assert (await klien.post("/v1/auth/register", json=_daftar_badan(email))).status_code == 201
        salah = {"email": email, "password": "sandi-yang-keliru-sekali"}
        assert (await klien.post("/v1/auth/login", json=salah)).status_code == 401

    with _pemilik(api_uji) as k:
        sidik_ip = [
            h
            for (h,) in k.execute(
                "SELECT DISTINCT ip_hash FROM audit_logs WHERE ip_hash IS NOT NULL"
            )
        ]
    kunci = [k async for k in api_uji.app.state.redis.scan_iter(match=f"{api_uji.awalan_redis}:*")]

    assert sidik_ip, "tidak ada baris audit — uji ini tidak memeriksa apa pun"
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in sidik_ip), (
        f"audit_logs.ip_hash bukan sidik HMAC: {sidik_ip}"
    )
    assert any(":laju:" in k for k in kunci), "tidak ada kunci batas laju — uji ini buta"
    mentah = [k for k in kunci if ip in k or email in k]
    assert not mentah, f"IP atau email mentah di kunci Redis: {mentah}"


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
    with _pemilik(api_uji) as k:
        (jumlah,) = k.execute(
            "SELECT count(*) FROM audit_logs WHERE user_id = %s AND action = 'session.logged_out'",
            (akun["user"]["id"],),
        ).fetchone() or (0,)
    assert jumlah == 1, "keluar tidak tercatat di audit"
