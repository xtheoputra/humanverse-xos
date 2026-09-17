-- Peran LOGIN api untuk D0 (compose lokal) — B-40, spec/01 §10.
--
-- Dijalankan layanan compose `db-roles` SESUDAH migrasi (yang membuat peran
-- NOLOGIN `hvx_app` beserta seluruh hak aksesnya), sebagai pemilik skema:
--
--   psql -v ON_ERROR_STOP=1 -f peran-lokal.sql
--
-- Nama & sandi dibaca dari lingkungan (HVX_API_DB_USER, HVX_API_DB_PASSWORD),
-- tidak pernah ditulis di berkas ini, dan tidak lewat argumen baris perintah.
-- ⚠️ KHUSUS D0: di D1+ peran ini dibuat infrastruktur dengan sandi dari
-- pengelola rahasia (arch/09 §5 aturan 3).
--
-- Aman dijalankan berulang: peran dibuat kalau belum ada, atributnya DIPAKSA
-- kembali aman (bukan superuser, tanpa BYPASSRLS) setiap kali — peran yang
-- pernah diubah tangan menjadi berbahaya dibetulkan, bukan dibiarkan.

\getenv api_pengguna HVX_API_DB_USER
\getenv api_sandi HVX_API_DB_PASSWORD

SELECT format('CREATE ROLE %I LOGIN', :'api_pengguna')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'api_pengguna')
\gexec

SELECT format(
  'ALTER ROLE %I WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT PASSWORD %L',
  :'api_pengguna', :'api_sandi')
\gexec

SELECT format('GRANT hvx_app TO %I', :'api_pengguna')
\gexec
