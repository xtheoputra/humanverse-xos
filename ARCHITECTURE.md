# ARCHITECTURE.md — arsitektur KODE yang ada

> Arsitektur 20 fase ada di [`arch/`](arch/README.md); bentuk V0 di
> [`spec/`](spec/README.md). Berkas ini menjawab pertanyaan yang lebih sempit:
> **apa yang sudah dibangun, dan kenapa bentuknya begitu.** Setiap baris di
> bawah menunjuk penegaknya, supaya tidak ada yang hanya dinyatakan.

Keadaan: **Sprint 0 (Foundation)** — 8 dari 51 tugas `spec/07`.

---

## 1 · Satu proses, dua belas modul (D0)

```
docker compose                                   arch/09 §1
├── postgres   PostgreSQL 16         K1 · 23 tabel spec/01
├── redis      Redis 7               sesi · cache · Streams
├── migrate    alembic upgrade head  sekali jalan, SEBELUM api
└── api        uvicorn hvx.main:create_app --factory
```

V0 punya satu pengguna nyata. Yang dijaga sejak awal bukan proses terpisah,
melainkan **batas yang tidak boleh dilanggar** — supaya memecah satu modul
menjadi service nanti (V2) adalah pekerjaan sehari, bukan penulisan ulang
([`spec/06`](spec/06-MODULE-BOUNDARIES.md) *Jalan keluar ke V2*).

Citra `api` adalah **satu artefak untuk semua lingkungan** (arch/09 §5 aturan
1): yang berbeda hanya variabel `HVX_*`. Proses berjalan sebagai pengguna
non-root `hvx` (uid 10001).

## 2 · Lapisan modul — arah IMPOR

```
agents                                   ← tidak ada yang mengimpornya
intelligence
memory
goals | habits | checkins | journal | activities | profile   ← saling independen
events
identity
platform                                 ← tidak mengimpor siapa pun
```

Ditegakkan `import-linter` (`pyproject.toml`): **M-1** asiklik · **M-2**
hanya lewat `__init__.py` · **M-3** domain independen · **B-2** klien
HTTP/SDK model hanya di `platform`.

> 🔧 **`events` di bawah modul domain, padahal gambar `spec/06` meletakkannya
> di bawah secara visual sebagai tujuan aliran.** Gambar itu arah **data**.
> Arah **impor** ditentukan aturan 6 `spec/06`: *tiap tulisan domain wajib
> menerbitkan event* — jadi modul domain mengimpor `events`, bukan
> sebaliknya. `memory` di atas domain karena ekstraksi memori membaca jurnal
> dan mood (tugas 3.6). **Cara membalikkan:** ubah urutan `layers` kontrak
> `m1-m3-lapisan`, lalu jalankan `tools/uji_mutasi_kode.py`.

## 3 · Data

| | Di mana | Penegak |
|---|---|---|
| bentuk 23 tabel | [`spec/01`](spec/01-DATABASE-SCHEMA.md) | — sumber |
| migrasi | `data/migrations/versions/0001_v0_skema.{up,down}.sql` | `test_migrasi.py`: katalog migrasi **==** katalog DDL `spec/01` — tabel (persistensi · RLS · opsi · hak akses · komentar) · kolom (tipe · null · bawaan · collation · identity · generated) · hak akses & komentar kolom · constraint · index · pemicu (`pg_get_triggerdef` + menyala/mati) · kebijakan RLS · rule · sequence · fungsi · tipe · ekstensi (+ versi). **Tidak** dibandingkan: statistik, `STORAGE`/`COMPRESSION` kolom, kepemilikan, hak bawaan |
| naik & turun bersih | idem | `test_migrasi.py`: naik → turun (kosong, kecuali ekstensi — lihat bawah) → naik (identik) |
| parser P-1..P-3 melihat semua tabel | — | `test_migrasi.py`: nama tabel yang parser baca **==** tabel di katalog basis data sungguhan |
| anotasi retensi + `data_subject` (K-16) | komentar SQL di atas tiap `CREATE TABLE` | `periksa_dokumen.py` P-1 · P-2 · P-3 atas `spec/01` **dan** migrasi |
| `updated_at` diperbarui | 11 pemicu `set_updated_at()` | `test_migrasi.py`: tiap tabel ber-`updated_at` punya pemicu BEFORE · ROW · UPDATE · menyala · tanpa `WHEN` · tanpa `UPDATE OF` |

SQL migrasi hidup di berkas `.sql`, bukan `op.create_table`: anotasi P-1 adalah
**komentar SQL**, dan komentar tidak bertahan lewat DSL Python.

Aplikasi memakai **asyncpg**; migrasi memakai **psycopg 3** sinkron — satu
berkas SQL berisi banyak pernyataan hanya bisa dikirim lewat protokol kueri
sederhana. Satu DSN (`HVX_DATABASE_URL`), driver diturunkan di
`platform.db` — dan karena itu **DSN tidak boleh membawa parameter kueri**
(`?sslmode=…`): kedua driver menafsirkannya berbeda, dan yang semula terjadi
adalah migrasi berhasil lalu setiap kueri api gagal. Ditolak saat mulai; opsi
koneksi lewat variabel libpq (`PGSSLMODE`, `PGSSLROOTCERT`, …).

Turun (`downgrade base`) **tidak melepas `citext`**: 0001 memasangnya dengan
`IF NOT EXISTS` dan tidak bisa tahu apakah ekstensinya sudah ada sebelumnya.
Mode offline Alembic (`--sql`) ditolak dengan pesan jelas — SQL-nya sudah
tersedia apa adanya di berkas `.up.sql`/`.down.sql`.

## 4 · Operasional

| | Bentuk | Kenapa |
|---|---|---|
| `GET /health` | `200 {status, version, db, redis}`; **503** dengan bentuk sama kalau satu ketergantungan mati | pemeriksa kesehatan hanya membaca kode status — `200` untuk basis data mati berarti tak ada yang pernah tahu |
| batas waktu pemeriksaan | `HVX_HEALTH_TIMEOUT_S` (bawaan 1 dtk), **serentak**; pemeriksaan yang lewat waktu **dibatalkan di belakang**, laporan tidak menunggu pembatalannya | diukur: `asyncio.wait_for` menunggu pembatalan ping asyncpg yang tersangkut — `/health` menjawab sesudah **60 dtk** dengan batas 1 dtk |
| galat ketergantungan | hanya **jenis** galat ke log; tidak pernah ke jawaban HTTP | pesan galat bisa memuat DSN atau host internal |
| batas waktu Redis | `HVX_REDIS_SOCKET_TIMEOUT_S` (5 dtk) · `HVX_REDIS_CONNECT_TIMEOUT_S` (2 dtk) — **terpisah** dari `/health` | semula satu angka: `XREADGROUP BLOCK 5000` (tugas 3.3) akan gagal sesudah 1 dtk. Konsumen Streams wajib punya klien sendiri |
| log | JSON satu baris; `request_id` + `user_id` di **setiap** baris, `latency_ms` di baris penutup; level berlaku juga bagi pencatat uvicorn | spec/07 0.5 |
| `ikat_pengguna()` | **wajib dari `async def`** — dari konteks sinkron ia menolak dengan galat | FastAPI menjalankan `def` di threadpool dengan SALINAN contextvars; `user_id` hilang diam-diam |
| galat tak tertangani | middleware merender **500 `{error: {code, message}}`** + `X-Request-ID`, tanpa rincian galat | `ServerErrorMiddleware` Starlette berada DI LUAR middleware pengguna — 500-nya tidak pernah membawa `X-Request-ID`. ⚠️ Akibatnya `app.exception_handler(Exception)` **tidak akan pernah terpanggil** untuk galat yang sampai ke middleware |
| `X-Request-ID` | dipakai ulang kalau berbentuk id (`[A-Za-z0-9._-]{1,128}`), diganti kalau tidak | nilai klien masuk log apa adanya |
| middleware | ASGI murni, bukan `BaseHTTPMiddleware` | yang kedua memutus `contextvars` dan menahan SSE (tugas 4.8) |
| dokumentasi interaktif | terbuka **hanya** di `local` · `test` · `ci`; `HVX_ENV` **wajib** | daftar izin, bukan daftar tolak: lingkungan yang lupa diisi atau baru ditambahkan jatuh ke sisi tertutup |

## 5 · Gerbang

`tools/ci_lokal.py` — `lint → typecheck → test → build → scan`, satu sumber
untuk mesin lokal dan [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
Peta lengkap 26 pemeriksaan `arch/11`, mana yang jalan dan mana yang menunggu
apa: [`arch/11`](arch/11-PENEGAKAN.md) §6.

## 6 · Yang BELUM ada, dengan sengaja

| Belum ada | Datang di |
|---|---|
| autentikasi, izin, audit, batas laju | Sprint 1 (1.1–1.7) |
| `consents.purpose` + `kind='model_training'` (B-22) | Sprint 1 tugas 1.4 — **sebelum baris data pertama** |
| pohon `security/` — B-1 belum bisa dinyatakan | risk gate, tugas 4.5 |
| Qdrant | Sprint 3 tugas 3.5 |
| aplikasi Flutter | Sprint 2 tugas 2.7 |
