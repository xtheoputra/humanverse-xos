-- Peran LOGIN api dan pekerja untuk D0 (compose lokal) — B-40, S4, spec/01 §10 §12.
--
-- Dijalankan layanan compose `db-roles` SESUDAH migrasi (yang membuat peran
-- NOLOGIN `hvx_app` dan `hvx_pekerja` beserta seluruh hak aksesnya), sebagai
-- pemilik skema:
--
--   psql -v ON_ERROR_STOP=1 -f peran-lokal.sql
--
-- Nama & sandi dibaca dari lingkungan (HVX_API_DB_USER, HVX_API_DB_PASSWORD,
-- HVX_PEKERJA_DB_USER, HVX_PEKERJA_DB_PASSWORD), tidak pernah ditulis di berkas
-- ini, dan tidak lewat argumen baris perintah.
-- ⚠️ KHUSUS D0: di D1+ peran ini dibuat infrastruktur dengan sandi dari
-- pengelola rahasia (arch/09 §5 aturan 3).
--
-- Aman dijalankan berulang: peran dibuat kalau belum ada, atributnya DIPAKSA
-- kembali aman (bukan superuser, tanpa BYPASSRLS) setiap kali — peran yang
-- pernah diubah tangan menjadi berbahaya dibetulkan, bukan dibiarkan.
--
-- Dua login, sengaja: api menghadap internet dan hanya anggota `hvx_app`;
-- pekerja juga anggota `hvx_pekerja` — satu-satunya yang boleh memanggil fungsi
-- relay & penyelaras (linimasa semua pengguna di luar RLS). Satu login untuk
-- keduanya membuat api menolak mulai (`platform.pastikan_peran_aplikasi`).

\getenv api_pengguna HVX_API_DB_USER
\getenv api_sandi HVX_API_DB_PASSWORD
\getenv pekerja_pengguna HVX_PEKERJA_DB_USER
\getenv pekerja_sandi HVX_PEKERJA_DB_PASSWORD

SELECT (:'api_pengguna' = :'pekerja_pengguna') AS sama \gset
\if :sama
  DO $$ BEGIN RAISE EXCEPTION 'HVX_API_DB_USER dan HVX_PEKERJA_DB_USER wajib berbeda (S4)'; END $$;
\endif

SELECT format('CREATE ROLE %I LOGIN', :'api_pengguna')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'api_pengguna')
\gexec

SELECT format(
  'ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT PASSWORD %L',
  :'api_pengguna', :'api_sandi')
\gexec

SELECT format('GRANT hvx_app TO %I', :'api_pengguna')
\gexec

-- Api yang pernah dijadikan anggota `hvx_pekerja` dikembalikan: bukan anggota.
SELECT format('REVOKE hvx_pekerja FROM %I', :'api_pengguna')
 WHERE pg_has_role(:'api_pengguna', 'hvx_pekerja', 'MEMBER')
\gexec

SELECT format('CREATE ROLE %I LOGIN', :'pekerja_pengguna')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'pekerja_pengguna')
\gexec

SELECT format(
  'ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT PASSWORD %L',
  :'pekerja_pengguna', :'pekerja_sandi')
\gexec

SELECT format('GRANT hvx_app, hvx_pekerja TO %I', :'pekerja_pengguna')
\gexec
