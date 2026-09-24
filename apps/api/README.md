# `apps/api` — HumanVerse XOS API (V0)

Satu proses FastAPI, dua belas modul di `src/hvx/modules/`
([`spec/06`](../../spec/06-MODULE-BOUNDARIES.md)). Arsitektur kode yang sudah
ada, dan kenapa bentuknya begitu: [`ARCHITECTURE.md`](../../ARCHITECTURE.md).

```bash
# butuh HVX_ENV, HVX_DATABASE_URL, HVX_REDIS_URL, HVX_IP_HASH_KEY
uv run --locked uvicorn hvx.main:create_app --factory --reload
# proses KEDUA, citra yang sama (spec/07 3.3–3.6): relay event → Redis Streams,
# konsumen `memori`, penyelaras memories → Qdrant (bila HVX_QDRANT_URL diisi).
# HVX_DATABASE_URL-nya login LAIN: anggota `hvx_app` DAN `hvx_pekerja` (S4) — api
# menolak mulai dengan login itu, pekerja menolak mulai tanpanya.
uv run --locked python -m hvx.pekerja
```

| Variabel | Wajib | Bawaan · catatan |
|---|---|---|
| `HVX_ENV` | ✅ | `local` · `test` · `ci` · `production` — **tanpa bawaan**; dokumentasi interaktif hanya terbuka di tiga yang pertama |
| `HVX_DATABASE_URL` | ✅ | `postgresql://…` peran login **anggota `hvx_app`** — api **menolak mulai** sebagai superuser, `BYPASSRLS`, atau pemilik tabel (B-40). **Tanpa parameter kueri**; opsi koneksi lewat `PGSSLMODE`, `PGSSLROOTCERT`, `PGCONNECT_TIMEOUT`, `PGAPPNAME` |
| `HVX_REDIS_URL` | ✅ | `redis://…` |
| `HVX_IP_HASH_KEY` | ✅ | ≥ 32 karakter, **tanpa bawaan** — kunci HMAC sidik IP untuk audit & batas laju. IP mentah tidak pernah disimpan; sha256 polos atas IPv4 bisa dibalik |
| `HVX_LOG_LEVEL` | | `INFO` — berlaku juga bagi pencatat uvicorn |
| `HVX_LOG_JSON` | | `true` |
| `HVX_HEALTH_TIMEOUT_S` | | `1.0` — hanya untuk `/health` |
| `HVX_REDIS_SOCKET_TIMEOUT_S` | | `5.0` — klien Redis bersama; konsumen Streams yang memblokir wajib punya klien sendiri |
| `HVX_REDIS_CONNECT_TIMEOUT_S` | | `2.0` |
| `HVX_REDIS_PREFIX` | | `hvx` — awalan semua kunci Redis proses ini (uji memakai awalan acak) |
| `HVX_ACCESS_TOKEN_TTL_S` | | `900` — token akses; **tidak boleh melebihi** `HVX_REFRESH_TOKEN_TTL_S` (api menolak mulai): token akses yang hidup lebih lama dari catatan sesinya tidak bisa dicabut |
| `HVX_REFRESH_TOKEN_TTL_S` | | `2592000` (30 hari) — token segar, **berotasi** tiap dipakai |
| `HVX_PERMISSION_CACHE_TTL_S` | | `300` — umur **maksimal** cache keputusan izin; pencabutan tidak menunggunya |
| `HVX_RATE_LIMIT_IP` | | `600/60` — `jumlah/detik` per IP di seluruh `/v1/*` (IPv6 per /64) |
| `HVX_RATE_LIMIT_USER` | | `300/60` — per pengguna di rute bersesi |
| `HVX_RATE_LIMIT_AUTH_IP` | | `30/600` — `register` + `login` per IP |
| `HVX_RATE_LIMIT_LOGIN_FAILURES` | | `100/86400` — login gagal per akun: 100 sekaligus (NIST SP 800-63B-4: ≤ 100), lalu satu tiap `detik/jumlah`; berhasil masuk menghapus hitungannya. ⚠️ Batas **laju**, bukan penguncian sesudah 100 kegagalan beruntun — **B-42** · K-22 |
| `FORWARDED_ALLOW_IPS` | | `127.0.0.1` — dibaca **uvicorn**, bukan `Settings`: hanya dari alamat ini `X-Forwarded-For` dipercaya. Di belakang penyeimbang beban (D1+) wajib diisi alamatnya — kalau tidak, semua klien berbagi satu jatah batas laju |
| `HVX_CORS_ORIGINS` | | kosong — asal peramban yang boleh memanggil api, dipisah koma (`http://localhost:5000` untuk `apps/mobile` versi web). Kosong = **tanpa CORS**; `*` dan asal berjalur **ditolak saat mulai** |
| `HVX_QDRANT_URL` | | kosong — basis data vektor memori (3.5). Kosong = memori tetap diekstrak ke PostgreSQL, **tidak** disemat; penyelaras menyusul begitu diisi |
| `HVX_QDRANT_API_KEY` | | kosong — kunci API Qdrant (wajib di luar D0 lokal) |
| `HVX_QDRANT_KOLEKSI` | | `memories` — nama koleksi (uji memakai koleksi sekali pakai) |
| `HVX_SEMATAN_KEY` | bila Qdrant | ≥ 32 karakter — kunci penyemat lokal (**K-26**), diturunkan per pengguna. Tanpa kunci, vektor di Qdrant bisa **dibalik menjadi kata** isi jurnal; menggantinya = seluruh memori disemat ulang |
| `HVX_MODEL_SIMPLE` | | `lokal/hvx-ringkas-v1` — model kelas *simple* (**K-28**), `penyedia/nama`. V0 hanya penyedia `lokal`: tanpa jaringan, tanpa biaya, merangkai fakta yang disiapkan agent |
| `HVX_MODEL_REASONING` | | `lokal/hvx-nalar-v1` — model kelas *reasoning* (**K-28**). Perintah berbentuk tetap (*“catat mood 3”*) tidak memanggil model mana pun |
| `HVX_AI_ANGGARAN_HARIAN_USD` | | `0.50` — biaya model per pengguna per **hari lokalnya** (**K-32**). Melewatinya **menurunkan** kelas model ke *simple*, tidak menolak (4.9); angka sebenarnya milik pemilik |
| `HVX_MODEL_HARGA` | | `{}` — JSON `{"penyedia/nama": [masuk, keluar]}`, USD per sejuta token. Model di luar penyedia `lokal` **tanpa harga ditolak saat mulai**: biaya yang tak terhitung tak bisa dibatasi (4.9) |

Rute yang ada — kontraknya [`spec/04`](../../spec/04-API-CONTRACTS.md):

| Rute | |
|---|---|
| `GET /health` | `200 {status, version, db, redis}`, atau `503` dengan bentuk sama kalau satu ketergantungan mati — **di luar** batas laju |
| `POST /v1/auth/register` · `login` · `refresh` · `logout` | tugas 1.1 — `logout` butuh sesi |
| `GET /v1/me` · `PATCH /v1/me/profile` | tugas 1.3 — butuh sesi |
| `GET·POST /v1/goals` · `GET·PATCH·DELETE /v1/goals/{id}` · `GET /v1/goals/{id}/tree` · `POST /v1/goals/{id}/milestones` · `PATCH /v1/milestones/{id}` | tugas 2.1 — pohon goal satu kueri |
| `GET·POST /v1/habits` (`?for_date=` → `day{}`) · `PATCH·DELETE /v1/habits/{id}` | tugas 2.2 — tier yang disarankan dari energi check-in |
| `POST /v1/habits/{id}/completions` · `DELETE …/completions/{for_date}` | tugas 2.3 — kirim ulang tanggal sama → `200` |
| `GET /v1/habits/{id}/streak` | tugas 2.4 — menurut zona profil saat ini |
| `GET /v1/checkins` · `PUT /v1/checkins/{for_date}` | tugas 2.5 — PUT = ganti, satu baris per tanggal |
| `GET·POST /v1/moods` | tugas 2.6 — tiap mood melahirkan memori episodik (3.6) |
| `GET·POST /v1/journal` · `GET·PATCH·DELETE /v1/journal/{id}` | tugas 3.4 — daftar **tanpa** `body`; sunting & hapus menjangkau memori jurnal (3.6) |
| `GET·POST /v1/activities` (`?source=`) | tugas 3.8 — klien hanya mencatat `manual` |
| `GET·POST /v1/conversations` · `GET·POST /v1/conversations/{id}/messages` · `GET …/stream` (SSE) · `POST …/confirmations` | tugas 4.8 — *“catat mood 3”* tanpa agent & tanpa model; giliran agent di latar; `done` memuat `cost_usd` (**K-31**, **E-194**, **E-195**) |

Tiap tulisan fakta perilaku menerbitkan event `spec/03` **di transaksi yang
sama** (3.2, peta aturan 6 `spec/06`); proses `hvx.pekerja` menyalurkannya.
Memori tidak punya rute HTTP di V0 — `memory.PencariMemori` (3.7) menunggu tool
`memory.search` Sprint 4.

Tulisan `POST`/`PATCH` domain menerima `Idempotency-Key` (spec/04, E-165) —
rute baru menyatakan `idem: platform.Idempoten` **dan** mengakhiri badannya
dengan `return await idem.jalankan(user_id, kerja, baca_ulang)`:
`tests/unit/test_idempotensi_terpasang.py` menolak rute tulis yang tidak
menerimanya atau tidak memanggilnya. Redis hanya mengingat **rujukan**
(sidik · status · id) — `baca_ulang` membaca sumber dayanya lagi saat diputar
ulang (E-171, K-24).

Masukan **ketat** (spec/04, E-170): medan angka/boolean/tanggal/waktu memakai
`platform.Bulat` · `Benar` · `Tanggal` · `WaktuBerzona` · `AngkaJson` —
`tests/unit/test_masukan_ketat_semua_rute.py` menelusuri skema inti tiap rute.
Badan lebih dari 1 MiB → `413` sebelum autentikasi (`platform.BatasBadanMiddleware`).

Galat selalu beramplop `{"error": {"code", "message", "details"?}}`; yang tak
tertangani dijawab `500` dengan `X-Request-ID`, tanpa rincian galat.

Rute baru yang butuh pengguna **menyatakannya** di tanda tangan:
`pengguna: identity.PenggunaDiperlukan` — sekaligus batas laju per pengguna.
Rute di bawah `/v1` terkena batas per IP tanpa perlu dipasang.

🔒 **Tiap kueri modul berjalan di dalam `platform.transaksi_pengguna`** (atau
`platform.transaksi_sistem` bila belum ada pengguna: baris sistem, pencarian
akun saat masuk)
(`spec/01` §11, H-27): RLS hanya meloloskan baris pengguna yang sedang
dilayani, dan kueri di luarnya melihat nol baris.
