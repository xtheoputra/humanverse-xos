# `data/migrations/` — Alembic (spec/07 tugas 0.4)

```bash
HVX_MIGRATION_DATABASE_URL=postgresql://… uv run alembic -c data/migrations/alembic.ini upgrade head
HVX_MIGRATION_DATABASE_URL=postgresql://… uv run alembic -c data/migrations/alembic.ini downgrade base
```

🔑 **`HVX_MIGRATION_DATABASE_URL`, bukan `HVX_DATABASE_URL`** (B-40): migrasi
berjalan sebagai PEMILIK skema; api berjalan sebagai anggota `hvx_app` dan
menolak mulai sebagai pemilik. Migrasi 0001 membuat peran NOLOGIN `hvx_app`
(sekluster — turun tidak melepasnya); peran LOGIN api dibuat di luar migrasi
(compose: layanan `db-roles`).

Di compose, layanan `migrate` menjalankan `upgrade head` sekali, **sebelum**
`api` mulai.

## Satu revisi = tiga berkas

```
versions/0001_v0_skema.py         ← hanya menjalankan SQL di sebelahnya
versions/0001_v0_skema.up.sql     ← DDL, dengan anotasi retensi di atas tiap CREATE TABLE
versions/0001_v0_skema.down.sql   ← kebalikannya, TANPA CASCADE
```

SQL sengaja tidak ditulis lewat `op.create_table`: anotasi `@retention` ·
`@who-can-set` · `@on-delete` adalah **komentar SQL** yang dibaca P-1
(`tools/periksa_dokumen.py`), dan komentar tidak bertahan lewat DSL Python.

## Yang menjaga

| Klaim | Uji |
|---|---|
| migrasi == DDL [`spec/01`](../../spec/01-DATABASE-SCHEMA.md), di tingkat katalog | `tests/integration/test_migrasi.py` |
| naik → turun → naik: bersih dan identik | idem |
| tiap tabel ber-`updated_at` punya pemicunya | idem |
| tiap `CREATE TABLE` punya `data_subject` + tiga anotasi | `tools/periksa_dokumen.py` P-1 · P-2 · P-3 |
| data tiap pengguna milik pribadinya — RLS + isi kebijakan · FK `(induk_id, user_id)` · hak akses `hvx_app` | `tests/integration/test_kepemilikan_data.py` |
| uji-uji di atas sanggup gagal | `tools/uji_mutasi_kode.py` · `tools/uji_mutasi.py` |
