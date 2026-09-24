"""H-27 — data tiap pengguna milik pribadi pengguna itu. spec/01 §10–§11, B-40, B-41.

Pemilik, 17 Sep 2026: *“data milik satu pengguna harus milik pengguna tersebut,
data masing-masing pengguna milik pribadi user.”* Tiga lapis menegakkannya, dan
berkas ini menguji ketiganya terhadap PostgreSQL sungguhan:

| lapis | pertanyaan yang dijawab |
|---|---|
| RLS | bisakah peran aplikasi yang melayani A membaca/mengubah/menulis baris B? |
| FK komposit | bisakah baris anak milik B menunjuk induk milik A? (FK tidak menerapkan RLS) |
| peran aplikasi | adakah jalan memutari keduanya — superuser, pemilik, BYPASSRLS, GRANT lebar? |

Uji katalog memastikan TABEL KE-24 tidak bisa lupa; uji perilaku memastikan
katalog itu berarti apa yang kita kira.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from typing import Any

import psycopg
import pytest
from _bantuan_db import BasisDataV0, psycopg_dsn
from psycopg import errors
from sqlalchemy import text

from hvx.modules.platform import buat_engine, transaksi_pengguna

pytestmark = pytest.mark.integration

# Katalog sistem tanpa pemilik pengguna (spec/README prinsip 6, spec/02 aturan A).
TABEL_SISTEM = frozenset({"agents", "agent_tools"})
# Hanya-tambah bagi aplikasi: baris lama tidak pernah diubah atau dihapus.
HANYA_TAMBAH = frozenset(
    {"consents", "events", "ai_messages", "recommendation_feedback", "audit_logs"}
)
# Dihapus lewat prosedur hapus akun / audit AI, bukan oleh aplikasi.
TANPA_HAPUS = frozenset({"users", "profiles", "agent_runs"})


def _katalog(dsn: str, kueri: str) -> list[tuple[Any, ...]]:
    with psycopg.connect(psycopg_dsn(dsn)) as k:
        return k.execute(kueri).fetchall()


# ─────────────────────────────────────────────────────────── katalog ──


def test_tiap_tabel_milik_pengguna_dilindungi_rls_dan_katalog_sistem_tidak(
    v0_bersama: BasisDataV0,
) -> None:
    baris = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT c.relname, c.relrowsecurity,
               (SELECT count(*) FROM pg_policy p WHERE p.polrelid = c.oid),
               EXISTS (SELECT 1 FROM pg_attribute a
                       WHERE a.attrelid = c.oid AND a.attname = 'user_id' AND NOT a.attisdropped)
        FROM pg_class c
        WHERE c.relnamespace = 'public'::regnamespace AND c.relkind IN ('r', 'p')
          AND c.relname <> 'alembic_version'
        """,
    )
    assert len(baris) == 23, f"tabel V0 yang terbaca: {len(baris)}"

    tanpa_rls = sorted(t for t, rls, n, _u in baris if t not in TABEL_SISTEM and not (rls and n))
    sistem_ber_rls = sorted(t for t, rls, _n, _u in baris if t in TABEL_SISTEM and rls)
    tanpa_pemilik = sorted(
        t for t, _r, _n, punya_user_id in baris
        if t not in TABEL_SISTEM | {"users"} and not punya_user_id
    )  # fmt: skip

    assert not tanpa_rls, f"tabel milik pengguna tanpa RLS atau tanpa kebijakan: {tanpa_rls}"
    assert not sistem_ber_rls, (
        f"katalog sistem diberi RLS — daftar TABEL_SISTEM basi?: {sistem_ber_rls}"
    )
    assert not tanpa_pemilik, f"tabel bukan katalog sistem tanpa user_id: {tanpa_pemilik}"


def test_isi_tiap_kebijakan_rls_membatasi_pada_pengguna_yang_dilayani(
    v0_bersama: BasisDataV0,
) -> None:
    """Kebijakan yang ADA tidak cukup: `USING (true)` lolos uji keberadaan dan membuka semuanya.

    Tiap tabel milik pengguna tepat satu kebijakan PERMISSIVE untuk semua
    perintah dan semua peran, dengan USING dan WITH CHECK yang sama persis.
    `audit_logs` satu-satunya pengecualian, dan bentuknya dinyatakan penuh.
    """
    baris = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT c.relname, p.polname, p.polcmd::text, p.polpermissive, p.polroles::text,
               pg_get_expr(p.polqual, p.polrelid), pg_get_expr(p.polwithcheck, p.polrelid)
        FROM pg_policy p JOIN pg_class c ON c.oid = p.polrelid
        WHERE c.relnamespace = 'public'::regnamespace
        """,
    )
    per_tabel: dict[str, list[tuple[Any, ...]]] = {}
    for tabel, *sisa in baris:
        per_tabel.setdefault(tabel, []).append(tuple(sisa))

    milik = "(user_id = app_current_user_id())"
    salah: list[str] = []
    for tabel, kebijakan in sorted(per_tabel.items()):
        if tabel == "audit_logs":
            diharapkan = {
                ("audit_logs_read_own", "r", True, "{0}", milik, None),
                ("audit_logs_append", "a", True, "{0}", None,
                 "((user_id IS NULL) OR (user_id = app_current_user_id()))"),
            }  # fmt: skip
            if set(kebijakan) != diharapkan:
                salah.append(f"audit_logs: {sorted(kebijakan, key=str)}")
            continue
        syarat = "(id = app_current_user_id())" if tabel == "users" else milik
        if kebijakan != [(kebijakan[0][0], "*", True, "{0}", syarat, syarat)]:
            salah.append(f"{tabel}: {kebijakan}")

    assert set(per_tabel) == {t for t, *_ in baris}
    assert len(per_tabel) == 21, f"tabel berkebijakan: {sorted(per_tabel)}"
    assert not salah, (
        "kebijakan RLS yang tidak membatasi pada pengguna yang dilayani:\n" + "\n".join(salah)
    )


def test_tiap_fk_antar_tabel_milik_pengguna_membawa_user_id_berpasangan(
    v0_bersama: BasisDataV0,
) -> None:
    """B-41 — FK dari tabel ber-user_id ke induk ber-user_id wajib (induk_id, user_id)."""
    fk = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT con.conrelid::regclass::text, con.conname,
               array_position(con.conkey, anak.attnum),
               array_position(con.confkey, induk.attnum)
        FROM pg_constraint con
        JOIN pg_attribute anak  ON anak.attrelid  = con.conrelid  AND anak.attname  = 'user_id'
        JOIN pg_attribute induk ON induk.attrelid = con.confrelid AND induk.attname = 'user_id'
        WHERE con.contype = 'f'
          AND con.connamespace = 'public'::regnamespace
          AND con.confrelid <> 'public.users'::regclass
        """,
    )
    assert len(fk) >= 11, (
        f"relasi induk-anak milik pengguna yang terbaca: {len(fk)} — pemeriksa buta?"
    )

    satu_kolom = sorted(
        f"{tabel}.{nama}"
        for tabel, nama, posisi_anak, posisi_induk in fk
        if posisi_anak is None or posisi_anak != posisi_induk
    )
    assert not satu_kolom, (
        "FK yang membiarkan baris anak menunjuk induk milik pengguna LAIN "
        f"(user_id tidak berpasangan): {satu_kolom}"
    )


def test_hak_akses_peran_aplikasi_sesempit_yang_dinyatakan(v0_bersama: BasisDataV0) -> None:
    """B-40 — matriks hak akses `hvx_app`; melebar tanpa alasan = merah."""
    baris = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT c.relname,
               has_table_privilege('hvx_app', c.oid, 'SELECT'),
               has_table_privilege('hvx_app', c.oid, 'INSERT'),
               has_table_privilege('hvx_app', c.oid, 'UPDATE'),
               has_table_privilege('hvx_app', c.oid, 'DELETE'),
               has_table_privilege('hvx_app', c.oid, 'TRUNCATE'),
               has_table_privilege('hvx_app', c.oid, 'REFERENCES'),
               has_table_privilege('hvx_app', c.oid, 'TRIGGER'),
               pg_has_role('hvx_app', c.relowner, 'USAGE')
        FROM pg_class c
        WHERE c.relnamespace = 'public'::regnamespace AND c.relkind IN ('r', 'p')
          AND c.relname <> 'alembic_version'
        """,
    )
    salah: list[str] = []
    for tabel, pilih, sisip, ubah, hapus, kosongkan, rujuk, pemicu, pemilik in baris:
        if not pilih:
            salah.append(f"{tabel}: tanpa SELECT — aplikasi tidak bisa membacanya sama sekali")
        if kosongkan or rujuk or pemicu or pemilik:
            salah.append(f"{tabel}: TRUNCATE/REFERENCES/TRIGGER/kepemilikan diberikan")
        if tabel in TABEL_SISTEM and (sisip or ubah or hapus):
            salah.append(f"{tabel}: katalog sistem bisa ditulis aplikasi")
        if tabel in HANYA_TAMBAH and (ubah or hapus or not sisip):
            salah.append(
                f"{tabel}: hanya-tambah, tetapi UPDATE={ubah} DELETE={hapus} INSERT={sisip}"
            )
        if tabel in TANPA_HAPUS and hapus:
            salah.append(f"{tabel}: DELETE diberikan kepada aplikasi")

    (peran,) = _katalog(
        v0_bersama.dsn_pemilik,
        "SELECT rolsuper, rolbypassrls, rolcanlogin FROM pg_roles WHERE rolname = 'hvx_app'",
    )
    assert peran == (False, False, False), f"atribut hvx_app (super, bypassrls, login): {peran}"
    assert not salah, "\n".join(salah)


# Tiap fungsi SECURITY DEFINER melewati RLS atas nama pemiliknya — satu per
# kebutuhan, dengan alasannya di spec/01 §12. Nama baru di sini = keputusan baru.
# Tiap fungsi SECURITY DEFINER: satu kebutuhan lintas RLS, alasannya di spec/01 §12.
DEFINER_DIIZINKAN = frozenset(
    {
        "auth_lookup_for_login",  # login: mencari akun per email sebelum pengguna dikenali
        "events_untuk_relay",  # relay 3.3: RUJUKAN event semua pengguna, tanpa payload
    }
)
NL = chr(10)


def test_fungsi_security_definer_hanya_daftar_izin_terpatok_dan_bukan_untuk_public(
    v0_bersama: BasisDataV0,
) -> None:
    baris = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT p.proname,
               COALESCE(array_to_string(p.proconfig, ','), ''),
               p.proacl IS NULL
                 OR EXISTS (SELECT 1 FROM aclexplode(p.proacl) a
                            WHERE a.grantee = 0 AND a.privilege_type = 'EXECUTE'),
               has_function_privilege('hvx_app', p.oid, 'EXECUTE')
        FROM pg_proc p
        WHERE p.pronamespace = 'public'::regnamespace AND p.prosecdef
        """,
    )
    nama = {b[0] for b in baris}
    salah = [
        f"{n}: search_path={konfig!r} public_boleh={untuk_public} hvx_app_boleh={aplikasi}"
        for n, konfig, untuk_public, aplikasi in baris
        if "search_path=" not in konfig or untuk_public or not aplikasi
    ]

    assert nama == DEFINER_DIIZINKAN, (
        f"SECURITY DEFINER di luar daftar izin: {sorted(nama ^ DEFINER_DIIZINKAN)}"
    )
    assert not salah, "fungsi SECURITY DEFINER yang tidak terkunci:" + NL + NL.join(salah)


# ──────────────────────────────────────────────── perilaku: B-41 ──

_AGENT = (
    "INSERT INTO agents (name, version, manifest) VALUES (%(nama)s, '1.0.0', '{}') RETURNING id"
)

INDUK: dict[str, str] = {
    "goals": "INSERT INTO goals (user_id, title) VALUES (%(u)s, 'induk') RETURNING id",
    "habits": "INSERT INTO habits (user_id, title) VALUES (%(u)s, 'induk') RETURNING id",
    "events": (
        "INSERT INTO events (user_id, event_type, occurred_at, idempotency_key) "
        "VALUES (%(u)s, 'habit.completed', now(), gen_random_uuid()::text) RETURNING id"
    ),
    "ai_conversations": "INSERT INTO ai_conversations (user_id) VALUES (%(u)s) RETURNING id",
    "recommendations": (
        "INSERT INTO recommendations (user_id, domain, title) "
        "VALUES (%(u)s, 'habit', 'induk') RETURNING id"
    ),
    "agent_runs": (
        "INSERT INTO agent_runs (user_id, agent_id, agent_version, trigger) "
        "VALUES (%(u)s, %(agent)s, '1.0.0', 'user') RETURNING id"
    ),
}

# (relasi, tabel induk, INSERT anak) — %(p)s induk · %(u)s pemilik anak · %(c)s percakapannya
ANAK: list[tuple[str, str, str]] = [
    ("goals.parent_id", "goals",
     "INSERT INTO goals (user_id, title, parent_id) VALUES (%(u)s, 'anak', %(p)s)"),
    ("goal_milestones.goal_id", "goals",
     "INSERT INTO goal_milestones (goal_id, user_id, title) VALUES (%(p)s, %(u)s, 'anak')"),
    ("habits.goal_id", "goals",
     "INSERT INTO habits (user_id, title, goal_id) VALUES (%(u)s, 'anak', %(p)s)"),
    ("habit_completions.habit_id", "habits",
     "INSERT INTO habit_completions (habit_id, user_id, for_date, status) "
     "VALUES (%(p)s, %(u)s, current_date, 'done')"),
    ("memories.source_event_id", "events",
     "INSERT INTO memories (user_id, kind, scope, content, source_event_id) "
     "VALUES (%(u)s, 'episodic', 'uji', 'anak', %(p)s)"),
    ("ai_messages.conversation_id", "ai_conversations",
     "INSERT INTO ai_messages (conversation_id, user_id, role, content) "
     "VALUES (%(p)s, %(u)s, 'user', 'anak')"),
    ("ai_messages.agent_run_id", "agent_runs",
     "INSERT INTO ai_messages (conversation_id, user_id, role, content, agent_run_id) "
     "VALUES (%(c)s, %(u)s, 'assistant', 'anak', %(p)s)"),
    ("recommendations.agent_run_id", "agent_runs",
     "INSERT INTO recommendations (user_id, domain, title, agent_run_id) "
     "VALUES (%(u)s, 'habit', 'anak', %(p)s)"),
    ("recommendation_feedback.recommendation_id", "recommendations",
     "INSERT INTO recommendation_feedback (recommendation_id, user_id, action) "
     "VALUES (%(p)s, %(u)s, 'accepted')"),
    ("agent_runs.conversation_id", "ai_conversations",
     "INSERT INTO agent_runs (user_id, agent_id, agent_version, trigger, conversation_id) "
     "VALUES (%(u)s, %(agent)s, '1.0.0', 'user', %(p)s)"),
    ("agent_runs.parent_run_id", "agent_runs",
     "INSERT INTO agent_runs (user_id, agent_id, agent_version, trigger, parent_run_id) "
     "VALUES (%(u)s, %(agent)s, '1.0.0', 'agent', %(p)s)"),
]  # fmt: skip


def _pengguna_baru(k: psycopg.Connection[Any]) -> uuid.UUID:
    (uid,) = k.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, 'x') RETURNING id",
        (f"{uuid.uuid4().hex}@uji.id",),
    ).fetchone() or (None,)
    assert isinstance(uid, uuid.UUID)
    return uid


@pytest.fixture
def pemilik(v0_bersama: BasisDataV0) -> Iterator[psycopg.Connection[Any]]:
    """Koneksi PEMILIK skema (tidak terkena RLS) — untuk menyiapkan data dan menguji FK saja."""
    with psycopg.connect(psycopg_dsn(v0_bersama.dsn_pemilik), autocommit=True) as k:
        yield k


def test_populasi_relasi_uji_sama_dengan_katalog(v0_bersama: BasisDataV0) -> None:
    """Daftar ANAK di atas ditulis tangan — ia wajib sama dengan katalog, bukan lebih sempit."""
    fk = _katalog(
        v0_bersama.dsn_pemilik,
        """
        SELECT con.conrelid::regclass::text, a.attname
        FROM pg_constraint con
        JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = con.conkey[1]
        JOIN pg_attribute induk ON induk.attrelid = con.confrelid AND induk.attname = 'user_id'
        WHERE con.contype = 'f' AND con.connamespace = 'public'::regnamespace
          AND con.confrelid <> 'public.users'::regclass
        """,
    )
    assert {f"{t}.{kolom}" for t, kolom in fk} == {relasi for relasi, _i, _a in ANAK}


@pytest.mark.parametrize(("relasi", "induk", "sisip_anak"), ANAK, ids=[a[0] for a in ANAK])
def test_baris_anak_tidak_bisa_menunjuk_induk_milik_pengguna_lain(
    pemilik: psycopg.Connection[Any], relasi: str, induk: str, sisip_anak: str
) -> None:
    a, b = _pengguna_baru(pemilik), _pengguna_baru(pemilik)
    (agent,) = pemilik.execute(_AGENT, {"nama": f"uji-{uuid.uuid4().hex[:8]}"}).fetchone() or (
        None,
    )

    def _induk(u: uuid.UUID) -> uuid.UUID:
        (pid,) = pemilik.execute(INDUK[induk], {"u": u, "agent": agent}).fetchone() or (None,)
        assert isinstance(pid, uuid.UUID)
        return pid

    def _percakapan(u: uuid.UUID) -> uuid.UUID:
        (cid,) = pemilik.execute(INDUK["ai_conversations"], {"u": u}).fetchone() or (None,)
        assert isinstance(cid, uuid.UUID)
        return cid

    # Kontrol: anak yang menunjuk induk MILIKNYA SENDIRI diterima — supaya
    # penolakan di bawah pasti karena pemilik yang berbeda, bukan INSERT yang rusak.
    pemilik.execute(sisip_anak, {"p": _induk(a), "u": a, "c": _percakapan(a), "agent": agent})

    with pytest.raises(errors.ForeignKeyViolation):
        pemilik.execute(sisip_anak, {"p": _induk(a), "u": b, "c": _percakapan(b), "agent": agent})


# ──────────────────────────────────────────────── perilaku: RLS ──


def _sebagai_aplikasi(db: BasisDataV0, user_id: uuid.UUID | str | None) -> psycopg.Connection[Any]:
    k = psycopg.connect(psycopg_dsn(db.dsn_aplikasi))
    if user_id is not None:
        k.execute("SELECT set_config('hvx.user_id', %s, true)", (str(user_id),))
    return k


def test_aplikasi_yang_melayani_a_tidak_melihat_mengubah_atau_menulis_baris_b(
    v0_bersama: BasisDataV0, pemilik: psycopg.Connection[Any]
) -> None:
    a, b = _pengguna_baru(pemilik), _pengguna_baru(pemilik)
    for u in (a, b):
        pemilik.execute("INSERT INTO goals (user_id, title) VALUES (%s, 'rahasia')", (u,))
        pemilik.execute("INSERT INTO journal_entries (user_id, body) VALUES (%s, 'isi')", (u,))

    with _sebagai_aplikasi(v0_bersama, a) as k:
        assert k.execute("SELECT DISTINCT user_id FROM goals").fetchall() == [(a,)]
        assert k.execute("SELECT id FROM users").fetchall() == [(a,)]
        assert k.execute("UPDATE goals SET title = 'diubah' WHERE user_id = %s", (b,)).rowcount == 0
        assert k.execute("DELETE FROM journal_entries WHERE user_id = %s", (b,)).rowcount == 0
        assert (
            k.execute("UPDATE goals SET title = 'milikku' WHERE user_id = %s", (a,)).rowcount == 1
        )

    with _sebagai_aplikasi(v0_bersama, a) as k, pytest.raises(errors.InsufficientPrivilege):
        k.execute("INSERT INTO goals (user_id, title) VALUES (%s, 'sisipan')", (b,))

    with _sebagai_aplikasi(v0_bersama, a) as k, pytest.raises(errors.InsufficientPrivilege):
        # memindahkan baris sendiri ke pengguna lain juga ditolak (WITH CHECK)
        k.execute("UPDATE goals SET user_id = %s WHERE user_id = %s", (b, a))

    (judul,) = pemilik.execute("SELECT title FROM goals WHERE user_id = %s", (b,)).fetchone() or (
        None,
    )
    assert judul == "rahasia", "baris B berubah lewat aplikasi yang melayani A"


def test_tanpa_pengguna_yang_dilayani_aplikasi_tidak_melihat_apa_pun(
    v0_bersama: BasisDataV0, pemilik: psycopg.Connection[Any]
) -> None:
    """Gagal-tertutup: kueri yang lupa mengisi hvx.user_id melihat nol baris, bukan semua."""
    a = _pengguna_baru(pemilik)
    pemilik.execute("INSERT INTO habits (user_id, title) VALUES (%s, 'h')", (a,))

    with _sebagai_aplikasi(v0_bersama, None) as k:
        assert k.execute("SELECT count(*) FROM habits").fetchone() == (0,)
        assert k.execute("SELECT count(*) FROM users").fetchone() == (0,)

    with (
        _sebagai_aplikasi(v0_bersama, "bukan-uuid") as k,
        pytest.raises(errors.InvalidTextRepresentation),
    ):
        k.execute("SELECT count(*) FROM habits")


def test_aplikasi_tidak_bisa_mengubah_jejak_audit_maupun_event(
    v0_bersama: BasisDataV0, pemilik: psycopg.Connection[Any]
) -> None:
    """B-40 — yang dulu LOLOS sebagai superuser pemilik tabel."""
    a, b = _pengguna_baru(pemilik), _pengguna_baru(pemilik)
    audit = (
        "INSERT INTO audit_logs (data_subject, actor_type, actor_id, user_id, action) "
        "VALUES (%s, %s, 'uji', %s, 'uji.audit')"
    )

    with _sebagai_aplikasi(v0_bersama, a) as k:
        k.execute(audit, ("user", "user", a))
        k.execute(audit, ("system", "system", None))
        k.execute(
            "INSERT INTO events (user_id, event_type, occurred_at, idempotency_key) "
            "VALUES (%s, 'habit.completed', now(), 'k1')",
            (a,),
        )
        # Masih di transaksi yang sama: hvx.user_id berlaku sampai transaksi selesai.
        assert k.execute("SELECT count(*) FROM audit_logs").fetchone() == (1,), (
            "aplikasi yang melayani A membaca baris sistem atau baris pengguna lain"
        )

    for terlarang in (
        "UPDATE audit_logs SET action = 'dipalsukan'",
        "DELETE FROM audit_logs",
        "UPDATE events SET event_type = 'habit.skipped'",
        "DELETE FROM events",
    ):
        with _sebagai_aplikasi(v0_bersama, a) as k, pytest.raises(errors.InsufficientPrivilege):
            k.execute(terlarang)

    with _sebagai_aplikasi(v0_bersama, a) as k, pytest.raises(errors.InsufficientPrivilege):
        k.execute(audit, ("user", "user", b))


async def test_transaksi_pengguna_membatasi_kueri_dan_tidak_bocor_ke_koneksi_berikutnya(
    v0_bersama: BasisDataV0, pemilik: psycopg.Connection[Any]
) -> None:
    """`platform.transaksi_pengguna` — jalur yang akan dipakai tiap repository (asyncpg + pool)."""
    a, b = _pengguna_baru(pemilik), _pengguna_baru(pemilik)
    for u in (a, b):
        pemilik.execute("INSERT INTO mood_entries (user_id, valence) VALUES (%s, 3)", (u,))

    engine = buat_engine(v0_bersama.dsn_aplikasi)
    try:
        async with transaksi_pengguna(engine, a) as conn:
            baris = (await conn.execute(text("SELECT user_id FROM mood_entries"))).all()
        assert [r[0] for r in baris] == [a]

        # Pool memakai ulang koneksi yang sama; pengaturan lokal transaksi tidak ikut.
        async with engine.connect() as conn:
            sisa = (await conn.execute(text("SELECT count(*) FROM mood_entries"))).scalar()
        assert sisa == 0, "pengguna transaksi sebelumnya bocor ke koneksi berikutnya dari pool"

        with pytest.raises(TypeError, match=r"uuid\.UUID"):
            async with transaksi_pengguna(engine, str(a)):  # type: ignore[arg-type]
                pass
    finally:
        await engine.dispose()
