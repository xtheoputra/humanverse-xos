"""spec/07 0.4 — migrasi naik & turun bersih; skema cocok dengan spec/01.

"Cocok" di sini tidak dibaca mata. Dua basis data sekali pakai dibuat:

    hvx_uji_spec_*   ← seluruh blok ```sql spec/01, dijalankan apa adanya
    hvx_uji_mig_*    ← alembic upgrade head

lalu KATALOG keduanya dibandingkan, bagian per bagian (`KUERI_KATALOG`), dan
selisihnya dicetak.

🔴 Versi pertama menyatakan *“satu perbedaan di mana pun = gagal”* sambil hanya
membaca kolom, constraint, index, `information_schema.triggers`, dan hak akses
tingkat tabel. Diukur di tinjauan Sprint 0: sepuluh perbedaan yang mengubah
perilaku LOLOS — tabel `UNLOGGED`, pemicu yang dimatikan, pemicu `WHEN (false)`
atau `UPDATE OF` satu kolom, RLS menyala, `RULE … DO INSTEAD NOTHING`,
`COLLATE`, kolom `GENERATED`, `GRANT` tingkat kolom, opsi `IDENTITY`. Semuanya
kini dibaca. Yang TETAP tidak dibandingkan, dan dinyatakan supaya tidak
terbaca lebih kuat: statistik & target statistik kolom, parameter penyimpanan
kolom (`STORAGE`, `COMPRESSION`), kepemilikan objek, dan hak bawaan
(`ALTER DEFAULT PRIVILEGES`).
"""

from __future__ import annotations

import importlib.util
import re
import sys
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType
from typing import Any

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from psycopg import sql
from sqlalchemy.engine import make_url

from hvx.modules.platform import url_sync

pytestmark = pytest.mark.integration

AKAR = Path(__file__).resolve().parents[2]
SPEC01 = AKAR / "spec" / "01-DATABASE-SCHEMA.md"
ALEMBIC_INI = AKAR / "data" / "migrations" / "alembic.ini"

_PUBLIK = "relnamespace = 'public'::regnamespace"

KUERI_KATALOG: dict[str, str] = {
    "tabel": f"""
        SELECT relname, relkind, relpersistence, relrowsecurity, relforcerowsecurity,
               COALESCE(array_to_string(reloptions, ','), ''),
               COALESCE(relacl::text, '<bawaan>'),
               COALESCE(obj_description(oid, 'pg_class'), '')
        FROM pg_class
        WHERE {_PUBLIK} AND relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
          AND relname NOT LIKE 'alembic_version%'
    """,
    "kolom": """
        SELECT table_name, ordinal_position, column_name, data_type, udt_name,
               is_nullable, column_default, character_maximum_length,
               numeric_precision, numeric_scale, collation_name,
               is_identity, identity_generation, identity_start, identity_increment,
               identity_maximum, identity_minimum, identity_cycle,
               is_generated, generation_expression
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name <> 'alembic_version'
    """,
    "komentar_kolom": f"""
        SELECT c.relname, a.attname, col_description(c.oid, a.attnum)
        FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
        WHERE c.{_PUBLIK} AND a.attnum > 0 AND NOT a.attisdropped
          AND col_description(c.oid, a.attnum) IS NOT NULL
    """,
    "hak_akses_kolom": f"""
        SELECT c.relname, a.attname, a.attacl::text
        FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
        WHERE c.{_PUBLIK} AND a.attacl IS NOT NULL
    """,
    "constraint": """
        SELECT conrelid::regclass::text, conname, contype, convalidated, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE connamespace = 'public'::regnamespace
          AND conrelid <> COALESCE(to_regclass('public.alembic_version'), 0)
    """,
    "index": """
        SELECT tablename, indexname, indexdef FROM pg_indexes
        WHERE schemaname = 'public' AND tablename <> 'alembic_version'
    """,
    # pg_get_triggerdef memuat BEFORE/AFTER, FOR EACH ROW, UPDATE OF, WHEN;
    # tgenabled memuat keadaan nyala/mati — information_schema tidak memuat keduanya.
    "pemicu": f"""
        SELECT t.tgrelid::regclass::text, t.tgname, t.tgenabled, pg_get_triggerdef(t.oid)
        FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid
        WHERE NOT t.tgisinternal AND c.{_PUBLIK}
    """,
    "kebijakan": """
        SELECT tablename, policyname, permissive, roles::text, cmd, qual, with_check
        FROM pg_policies WHERE schemaname = 'public'
    """,
    "aturan": """
        SELECT tablename, rulename, definition FROM pg_rules WHERE schemaname = 'public'
    """,
    "urutan": f"""
        SELECT s.seqrelid::regclass::text, s.seqtypid::regtype::text, s.seqstart,
               s.seqincrement, s.seqmax, s.seqmin, s.seqcache, s.seqcycle
        FROM pg_sequence s JOIN pg_class c ON c.oid = s.seqrelid
        WHERE c.{_PUBLIK}
    """,
    "fungsi": """
        SELECT p.proname, pg_get_function_identity_arguments(p.oid), md5(pg_get_functiondef(p.oid))
        FROM pg_proc p
        WHERE p.pronamespace = 'public'::regnamespace AND p.prokind = 'f'
          -- fungsi milik ekstensi (citext) dibandingkan lewat bagian `ekstensi`
          AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.objid = p.oid AND d.deptype = 'e')
    """,
    "tipe": """
        SELECT typname, typtype FROM pg_type
        WHERE typnamespace = 'public'::regnamespace AND typtype IN ('e', 'd')
    """,
    "ekstensi": "SELECT extname, extversion, extnamespace::regnamespace::text FROM pg_extension",
}


# ─────────────────────────────────────────────────────────── bantuan ──


def ddl_spec01() -> str:
    teks = SPEC01.read_text(encoding="utf-8")
    blok = re.findall(r"```sql\n(.*?)```", teks, re.S)
    assert blok, "spec/01 tanpa satu blok ```sql pun — pembandingnya hilang"
    ddl = "\n".join(blok)
    nyasar = [b for b in ddl.splitlines() if b.lstrip().startswith(">")]
    assert not nyasar, (
        "baris markdown di DALAM blok ```sql spec/01 — pagar blok tidak ditutup:\n"
        + "\n".join(nyasar[:5])
    )
    return ddl


def _dsn_ke(dsn_admin: str, nama_db: str) -> str:
    return make_url(dsn_admin).set(database=nama_db).render_as_string(hide_password=False)


def _psycopg_dsn(dsn: str) -> str:
    return url_sync(dsn).replace("postgresql+psycopg://", "postgresql://", 1)


@pytest.fixture
def basis_data_sekali_pakai(dsn_admin_uji: str) -> Iterator[Callable[[str], str]]:
    dibuat: list[str] = []

    def _buat(awalan: str) -> str:
        nama = f"hvx_uji_{awalan}_{uuid.uuid4().hex[:10]}"
        with psycopg.connect(_psycopg_dsn(dsn_admin_uji), autocommit=True) as k:
            k.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nama)))
        dibuat.append(nama)
        return _dsn_ke(dsn_admin_uji, nama)

    yield _buat

    with psycopg.connect(_psycopg_dsn(dsn_admin_uji), autocommit=True) as k:
        for nama in dibuat:
            k.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(nama))
            )


def _alembic(dsn: str) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", dsn)
    cfg.attributes["konfigurasi_log"] = False
    return cfg


def katalog(dsn: str) -> dict[str, set[tuple[Any, ...]]]:
    with psycopg.connect(_psycopg_dsn(dsn)) as k:
        return {nama: set(k.execute(q).fetchall()) for nama, q in KUERI_KATALOG.items()}


def selisih(a: dict[str, set[tuple[Any, ...]]], b: dict[str, set[tuple[Any, ...]]]) -> str:
    keluar = []
    for bagian in KUERI_KATALOG:
        hanya_a, hanya_b = (
            sorted(a[bagian] - b[bagian], key=str),
            sorted(b[bagian] - a[bagian], key=str),
        )
        if hanya_a or hanya_b:
            keluar.append(f"── {bagian}")
            keluar += [f"   hanya di spec/01 : {r}" for r in hanya_a]
            keluar += [f"   hanya di migrasi : {r}" for r in hanya_b]
    return "\n".join(keluar)


def tabel_publik(dsn: str) -> set[str]:
    with psycopg.connect(_psycopg_dsn(dsn)) as k:
        return {
            r[0]
            for r in k.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        }


def _alat(nama: str) -> ModuleType:
    nama_modul = f"_alat_{nama}"
    if nama_modul in sys.modules:
        return sys.modules[nama_modul]
    spec = importlib.util.spec_from_file_location(nama_modul, AKAR / "tools" / f"{nama}.py")
    assert spec is not None
    assert spec.loader is not None
    modul = importlib.util.module_from_spec(spec)
    sys.modules[nama_modul] = modul
    spec.loader.exec_module(modul)
    return modul


# ─────────────────────────────────────────────────────────────── uji ──


def test_migrasi_menghasilkan_skema_yang_sama_persis_dengan_spec01(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    dsn_spec = basis_data_sekali_pakai("spec")
    dsn_mig = basis_data_sekali_pakai("mig")

    with psycopg.connect(_psycopg_dsn(dsn_spec), autocommit=True) as k:
        k.execute(ddl_spec01())
    command.upgrade(_alembic(dsn_mig), "head")

    k_spec, k_mig = katalog(dsn_spec), katalog(dsn_mig)

    assert len({r[0] for r in k_spec["kolom"]}) == 23, "spec/01 wajib memuat 23 tabel V0"
    assert k_spec == k_mig, "skema migrasi ≠ spec/01:\n" + selisih(k_spec, k_mig)


def test_parser_ddl_membaca_tepat_tabel_yang_ada_di_katalog(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    """P-1..P-3 hanya berarti untuk tabel yang PARSER-nya lihat.

    🔴 Tinjauan Sprint 0 membuat tabel yang tak terlihat parser pertama
    (`IF NOT EXISTS`, akhiran `WITH`) dan P-1..P-3 lulus tanpa temuan. Katalog
    basis data sungguhan adalah populasi yang tidak bisa dibohongi ejaan.
    """
    dsn = basis_data_sekali_pakai("parser")
    command.upgrade(_alembic(dsn), "head")
    di_katalog = tabel_publik(dsn) - {"alembic_version"}

    terbaca = _alat("periksa_dokumen")._tabel_ddl()
    dari_migrasi = {nama for label, nama, *_ in terbaca if label != "spec/01"}
    dari_spec = {nama for label, nama, *_ in terbaca if label == "spec/01"}

    assert dari_migrasi == di_katalog, (
        f"migrasi — tak terbaca parser: {sorted(di_katalog - dari_migrasi)} · "
        f"terbaca tapi tak ada: {sorted(dari_migrasi - di_katalog)}"
    )
    assert dari_spec == di_katalog, (
        f"spec/01 — tak terbaca parser: {sorted(di_katalog - dari_spec)} · "
        f"terbaca tapi tak ada: {sorted(dari_spec - di_katalog)}"
    )


def test_migrasi_turun_kembali_ke_basis_data_kosong_lalu_naik_lagi_identik(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    dsn = basis_data_sekali_pakai("naikturun")
    cfg = _alembic(dsn)
    ekstensi_awal = {r[0] for r in katalog(dsn)["ekstensi"]}

    command.upgrade(cfg, "head")
    pertama = katalog(dsn)
    command.downgrade(cfg, "base")
    kosong = katalog(dsn)
    command.upgrade(cfg, "head")
    kedua = katalog(dsn)

    assert tabel_publik(dsn) >= {"users", "audit_logs"}
    for bagian in ("tabel", "kolom", "constraint", "index", "pemicu", "urutan"):
        assert kosong[bagian] == set(), f"turun meninggalkan {bagian}: {sorted(kosong[bagian])[:3]}"
    assert kosong["fungsi"] == set(), "turun meninggalkan fungsi (set_updated_at?)"
    # Ekstensi SENGAJA tidak dilepas (lihat 0001_v0_skema.down.sql): turun tidak
    # boleh MENCABUT yang sudah ada, dan hanya boleh menyisakan yang 0001 pasang.
    ekstensi_sisa = {r[0] for r in kosong["ekstensi"]}
    assert ekstensi_awal <= ekstensi_sisa <= ekstensi_awal | {"citext"}
    assert pertama == kedua, "naik kedua ≠ naik pertama:\n" + selisih(pertama, kedua)


def test_turun_tidak_mencabut_ekstensi_yang_sudah_ada_sebelum_0001(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    dsn = basis_data_sekali_pakai("ekstensi")
    with psycopg.connect(_psycopg_dsn(dsn), autocommit=True) as k:
        k.execute("CREATE EXTENSION citext")
        k.execute("CREATE TABLE sudah_ada (e citext)")
    cfg = _alembic(dsn)

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")

    assert "sudah_ada" in tabel_publik(dsn)
    assert "citext" in {r[0] for r in katalog(dsn)["ekstensi"]}


# tgtype: ROW = 1 · BEFORE = 2 · UPDATE = 16 — pemicu yang BENAR bernilai tepat 19.
KUERI_PEMICU_UPDATED_AT = """
    SELECT c.relname, t.tgenabled, t.tgtype, t.tgqual IS NULL,
           cardinality(t.tgattr::int2[]), p.proname
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_proc p ON p.oid = t.tgfoid
    WHERE NOT t.tgisinternal AND c.relnamespace = 'public'::regnamespace
"""


def test_tiap_tabel_ber_updated_at_punya_pemicunya(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    """BEFORE · FOR EACH ROW · UPDATE · menyala · tanpa WHEN · tanpa UPDATE OF.

    🔴 Versi pertama menerima pemicu apa pun yang teksnya menyebut
    `set_updated_at()`. Diukur: pemicu AFTER, yang dimatikan, `WHEN (false)`, dan
    `UPDATE OF deleted_at` semuanya lulus — sementara `updated_at` tidak pernah
    berubah.
    """
    dsn = basis_data_sekali_pakai("pemicu")
    command.upgrade(_alembic(dsn), "head")
    ber_updated_at = {r[0] for r in katalog(dsn)["kolom"] if r[2] == "updated_at"}

    with psycopg.connect(_psycopg_dsn(dsn)) as k:
        benar = {
            tabel
            for tabel, nyala, tipe, tanpa_when, kolom_update_of, fungsi in k.execute(
                KUERI_PEMICU_UPDATED_AT
            )
            if fungsi == "set_updated_at"
            and nyala == "O"
            and tipe == 19
            and tanpa_when
            and kolom_update_of == 0
        }

    assert len(ber_updated_at) == 11
    assert ber_updated_at == benar, f"tanpa pemicu yang benar: {sorted(ber_updated_at - benar)}"


def test_pemicu_updated_at_benar_benar_memperbarui_kolomnya(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    dsn = basis_data_sekali_pakai("fungsi")
    command.upgrade(_alembic(dsn), "head")

    with psycopg.connect(_psycopg_dsn(dsn), autocommit=True) as k:
        (uid,) = k.execute(
            "INSERT INTO users (email, password_hash, created_at, updated_at) "
            "VALUES ('a@contoh.id', 'x', now() - interval '1 day', now() - interval '1 day') "
            "RETURNING id"
        ).fetchone()
        k.execute("UPDATE users SET status = 'suspended' WHERE id = %s", (uid,))
        (dibuat, diubah) = k.execute(
            "SELECT created_at, updated_at FROM users WHERE id = %s", (uid,)
        ).fetchone()

    assert diubah > dibuat


def test_audit_logs_menolak_baris_pengguna_tanpa_user_id(
    basis_data_sekali_pakai: Callable[[str], str],
) -> None:
    """arch/06 §6 sebagai CHECK — penjaga yang P-3 terima."""
    dsn = basis_data_sekali_pakai("audit")
    command.upgrade(_alembic(dsn), "head")

    with psycopg.connect(_psycopg_dsn(dsn), autocommit=True) as k:
        k.execute(
            "INSERT INTO audit_logs (data_subject, actor_type, actor_id, action) "
            "VALUES ('system', 'system', 'migrasi', 'uji.sistem')"
        )
        with pytest.raises(psycopg.errors.CheckViolation):
            k.execute(
                "INSERT INTO audit_logs (data_subject, actor_type, actor_id, action) "
                "VALUES ('user', 'user', 'u', 'uji.tanpa_user_id')"
            )


def test_mode_offline_ditolak_dengan_jelas() -> None:
    """Jalur `--sql` versi pertama tidak pernah bisa bekerja (AttributeError)."""
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", "postgresql://x:y@127.0.0.1:1/tidak_ada")
    cfg.attributes["konfigurasi_log"] = False

    with pytest.raises(RuntimeError, match="mode offline"):
        command.upgrade(cfg, "head", sql=True)
