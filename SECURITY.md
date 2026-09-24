# SECURITY.md

## Melaporkan kerentanan

Repo ini privat dan belum punya pengguna selain pemiliknya. Laporkan lewat
**GitHub Security Advisory privat** di repo ini (*Security → Report a
vulnerability*), atau langsung kepada pemilik repo. **Jangan** membuka issue
publik untuk kerentanan, dan jangan menyertakan data pengguna nyata di laporan.

## Versi yang didukung

Belum ada rilis. `master` adalah satu-satunya garis yang dipelihara.

---

## Yang dijaga sejak Sprint 0, 1, dan 2 — dan penegaknya

Setiap baris di bawah punya penegak yang **terbukti sanggup gagal**
(`tools/uji_mutasi.py` · `tools/uji_mutasi_kode.py`). Baris yang penegaknya
hanya sebagian ditulis dengan batasnya.

| Hal | Bentuk | Penegak |
|---|---|---|
| tidak ada DSN / lingkungan bawaan | `Settings` gagal mulai tanpa `HVX_DATABASE_URL`, `HVX_REDIS_URL`, **`HVX_ENV`** | `tests/unit/test_config.py` |
| rahasia tidak masuk berkas repo | pemindai rahasia `trivy fs` atas pohon repo (tanpa `.venv`, `.git`, cache) | `ci_lokal.py scan` · mutasi *token tertanam* |
| kredensial lokal | bernilai `*-dev-only`, port hanya di `127.0.0.1` | `docker-compose.yml` — ⚠️ tanpa uji |
| proses api | pengguna non-root `hvx` (uid 10001) | `api.Dockerfile` — ⚠️ tanpa uji |
| jalur keluar jaringan | klien jaringan (HTTP · `urllib` · `socket` · `ssl` · SMTP/FTP/IMAP/POP · xmlrpc · websockets) & SDK model hanya boleh diimpor `platform` — **seluruh paket `hvx`**, termasuk modul dan berkas baru | `import-linter` **B-2** + ruff banned-api (`http.client`, `asyncio.open_connection`, **`importlib.import_module`**) |
| `/health` tidak membocorkan infrastruktur | galat ketergantungan tidak pernah masuk jawaban HTTP | `test_health.py` |
| 500 tidak membocorkan galat | amplop `{error: {code, message}}` tanpa rincian; rincian hanya ke log | `test_log.py` |
| log tidak bisa disuntik lewat `X-Request-ID` | nilai klien yang bukan id diganti | `test_log.py` |
| dokumentasi API interaktif | terbuka hanya di `local` · `test` · `ci` (daftar izin); `/docs` · `/redoc` · `/openapi.json` → 404 di produksi | `tests/unit/test_main.py` (lewat HTTP) |
| dependensi produksi | `pip-audit --strict` atas `uv.lock` — **penanda platform dibuang dulu**, supaya paket yang hanya ada di citra Linux ikut diaudit di mesin Windows | `ci_lokal.py scan` |
| kunci dependensi | `uv lock --check` · `UV_LOCKED` di Actions · `uv sync --locked` di citra | `ci_lokal.py lint` · mutasi *dependensi tanpa kunci ulang* |
| kode | `bandit` + aturan `S` ruff | `ci_lokal.py lint` · `scan` |
| citra | `trivy image` — HIGH/CRITICAL yang sudah ada perbaikannya = gagal; citra diberikan sebagai **tar hanya-baca**, pemindai **tidak** mendapat soket Docker | `ci_lokal.py scan` |
| citra luar dipatok **digest** | `python`, `uv`, `postgres`, `redis`, `trivy` — tag bisa dipindahkan (trivy sendiri pernah: GHSA-69fq-xp46-6x23) | `tests/unit/test_rantai_pasok.py` |
| aksi CI dipatok **SHA commit** | + `persist-credentials: false` + `permissions: contents: read` | `tests/unit/test_rantai_pasok.py` |
| **data tiap pengguna milik pribadinya** (H-27) | RLS di 21 tabel: peran aplikasi hanya membaca, mengubah, dan menulis baris pengguna yang dilayani transaksi (`app_current_user_id()`); tanpa pengguna → **nol baris** | `test_kepemilikan_data.py` · mutasi *RLS dicabut*, *kebijakan `USING (true)`*, *pengguna bocor ke koneksi pool* |
| baris anak tidak menunjuk induk milik pengguna lain (B-41) | FK komposit `(induk_id, user_id)` di 11 relasi — menghapus induk tidak pernah menyentuh baris pengguna lain | idem · mutasi *FK kembali satu kolom* |
| api bukan superuser, pemilik, atau `BYPASSRLS` (B-40) | peran `hvx_app` sesempit `spec/01` §10; `audit_logs` & `events` **hanya-tambah**; api **menolak mulai** dengan peran yang melewati RLS | `test_kepemilikan_data.py` · `test_aplikasi_hidup.py` · mutasi *`GRANT UPDATE audit_logs`*, *penjaga peran dicabut* |
| **sandi** (1.1) | argon2id **di thread**; 15–128 karakter **tanpa aturan komposisi** — sandi simbol atau emoji tidak ditolak karena tak berhuruf; **daftar tolak** (konteks · pengulangan · urutan) + NFKC saat hashing **dan** saat mencocokkan — NIST SP 800-63B-4; hash lama diperbarui saat masuk | `test_sandi.py` · `test_auth.py` · mutasi *argon2i*, *daftar tolak tidak ditegakkan*, *NFKC dicabut* (dua sisi), *argon2 di event loop* (dua), *129 karakter*, *pengulangan dari kerangka saja* |
| login tidak membocorkan akun mana yang ada | email tak terdaftar tetap menjalankan **satu verifikasi argon2** dan **kueri basis data yang sama banyak** (`platform.transaksi_sistem`), dan dijawab **sama persis** dengan sandi salah; jejak auditnya baris sistem **tanpa email** | `test_auth.py` · `test_sandi.py` · mutasi *akun tak dikenal tanpa argon2*, *satu kueri lebih sedikit* |
| pencarian akun sebelum pengguna dikenali | fungsi `SECURITY DEFINER` sempit `auth_lookup_for_login` (`spec/01` §12) — `search_path` terpatok, `EXECUTE` dicabut dari `PUBLIC`; fungsi `SECURITY DEFINER` lain di luar daftar izin = gagal | `test_kepemilikan_data.py` · mutasi *`REVOKE … FROM PUBLIC` dicabut* |
| sesi (1.2) | token opak 256 bit; Redis hanya menyimpan **sidik** (di string, hash, dan himpunan); dicabut → 401 pada permintaan berikutnya — **juga bila keluar atau token bekas jatuh di tengah penyegaran, dan bila masuk baru jatuh di tengah cabut-semua**: tiap operasi yang membaca lalu menulis satu catatan sesi (putar · cabut) satu skrip Lua; token segar berotasi dan **pemakaian ulang mencabut seluruh sesi** (RFC 9700); token akses tidak pernah hidup lebih lama dari catatan sesinya (`Settings`); catatan sesi yang rusak tetap bisa dicabut — **K-21** | `test_sesi.py` (tiap celah antarperintah) · `test_auth.py` · `test_config.py` · 12 mutasi |
| galat tidak memantulkan masukan | galat validasi `400` hanya `loc` · `msg` · `type` — `loc` hanya nama yang dinyatakan api (kunci tak dikenal dari klien menjadi `*`), `msg` bawaan hanya untuk jenis galat yang tidak mengutip masukan (`uuid_parsing` mengutip karakternya — E-174); sandi tidak pernah muncul di jawaban; NUL di teks bebas → `400`, bukan galat basis data `500` | `test_galat.py` · `test_auth.py` · `test_profil.py` · mutasi *NUL lolos* (dua), *`msg` apa adanya*, *`loc` apa adanya* |
| **log tidak membawa nilai milik pengguna dari galat basis data** | `hide_parameters`; galat basis data — juga di dalam kelompok galat — dicatat **tanpa pesan**, sebab pesan PostgreSQL sendiri membawa isi baris (`DETAIL: Key (email)=…`). Yang tetap dicatat: jejak tumpukan, SQLSTATE, nama constraint · tabel · kolom, SQL statis | `test_galat_basis_data.py` · 3 mutasi |
| IP dan email tidak disimpan mentah | HMAC-SHA256 berkunci `HVX_IP_HASH_KEY` (wajib, ≥ 32 karakter) — di `audit_logs.ip_hash` **dan** di tiap kunci batas laju; sha256 polos atas IPv4 bisa dibalik dengan mencoba 2³² alamat | `test_sidik_ip.py` · `test_config.py` · `test_auth.py` (lewat HTTP: isi audit & kunci Redis) · mutasi *sha256 polos*, *IP mentah di audit*, *IP · email mentah di kunci*, *kunci HMAC pendek* |
| persetujuan (1.4) | hanya-tambah; pencabutan = baris baru, urutannya tentu di dalam satu transaksi; tujuan **dan** cakupan data wajib tercakup persetujuan terakhir **tiap jenis** yang belum kedaluwarsa — mencabut `privacy` tidak tertutup `terms` yang lebih baru | `test_persetujuan.py` · mutasi *cakupan tidak diperiksa*, *per tujuan saja*, *`now()`* |
| izin agent (1.5) | tanpa baris dan kedaluwarsa → `ask` (atau bawaan gerbang risiko — yang tidak pernah menimpa keputusan pengguna); cache Redis berumur sisa umur izin **saat dibaca − 1 dtk** (jeda menulisnya memakan margin itu, bukan izinnya); **pencabutan seketika**, juga terhadap pembaca yang sedang membaca | `test_izin.py` · 8 mutasi |
| audit (1.6) | perubahan **basis data** — akun, persetujuan, izin — dicatat **di transaksi yang sama**: audit yang gagal menggagalkan perubahannya. Perubahan **sesi** hidup di Redis, di luar transaksi — jejaknya bisa mendahului (`session.login_succeeded` · `session.revoked`) atau menyusul (`session.logged_out`) perubahannya, jadi Redis yang gagal di antara keduanya meninggalkan jejak tanpa perubahan atau sebaliknya. Metadata hanya skalar pendek — bukan isi | `test_identity_audit.py` · `test_audit.py` · `test_izin.py` · `test_persetujuan.py` · `test_auth.py` · mutasi *commit sebelum audit* (dua), *keluar tak tercatat*, *pendengar gagal ditelan* |
| masukan tidak dikoersi (Sprint 2, E-170) | angka · boolean · tanggal · waktu · desimal **ketat** di badan, kueri, dan jalur: `"on"` bukan persetujuan, `true` bukan angka, detik Unix bukan tanggal; tanggal & waktu 1900–2999 — `date.min` tidak menjadi `-infinity`, `+14:00` tahun 0001 tidak meluap menjadi 500 | `test_masukan_ketat_semua_rute.py` (skema inti tiap rute) · `test_masukan_ketat.py` (lewat HTTP) · 7 mutasi |
| ukuran permintaan (Sprint 2) | badan ≤ 1 MiB → `413` **sebelum** autentikasi dan sebelum dibaca — juga *chunked*; pohon goal, milestone, dan daftar habit dibatasi **saat menulis** (≤ 1.000 · 100 · 500, serial) — **K-24** | `test_batas_badan.py` · `test_batas_dan_balapan.py` · 5 mutasi |
| `Idempotency-Key` (Sprint 2, E-171) | kunci **milik pengguna**; Redis hanya menyimpan **rujukan** (sidik HMAC · status · id) — tidak ada isi tulisan pengguna di Redis/AOF sesudah hapus-keras; ulangan dibaca ulang di bawah RLS; ≤ 1.000 kunci baru per pengguna per 24 jam | `test_idempotensi.py` · `test_idempotensi_terpasang.py` (tiap rute tulis menyatakan **dan** memanggilnya) · 12 mutasi |
| CORS (Sprint 2) | mati kecuali `HVX_CORS_ORIGINS` menyebut asal **persis**; `*` ditolak `Settings`; tanpa kredensial peramban (token bearer, K-21) | `test_cors.py` · `test_config.py` |
| batas laju (1.7) | `429` + `Retry-After` per IP (`/v1/*`, IPv6 per /64) · per pengguna · daftar & masuk per IP · login gagal per akun: **100 sekaligus, lalu ±100 sehari** — jatahnya **dipakai sebelum argon2** (tebakan serentak tidak lolos bersama-sama), kuncinya email **sebagaimana `citext` membandingkannya** (`vİctim@` = `victim@`); jam Redis per kunci **tidak mundur** — langkah mundur ≤ 2 dtk diserap, sebab jam VM yang melangkah mundur membuat `429` palsu di ujung ledakan (tinjauan Sprint 2). Bukan batas 100 *beruntun* NIST — lihat bawah — **K-22** | `test_batas_laju.py` · `test_config.py` · 13 mutasi |

## 🛑 Yang BELUM dijaga — dan diketahui

| Celah | Akibat | Ditutup di |
|---|---|---|
| **batas login gagal per akun bukan batas *beruntun* NIST** (**B-42**) | NIST SP 800-63B-4 §3.2.2: ≤ 100 kegagalan beruntun. V0: 100 sekaligus, lalu satu tiap ±14 menit tanpa ujung, dan masuk yang berhasil mengosongkannya — setahun, puluhan ribu tebakan atas satu akun | pemulihan akun (belum punya tugas) — baru sesudahnya penguncian sungguhan aman. Sampai itu: sandi 15+ karakter berdaftar tolak, dan batas per IP |
| **batas per akun bisa dipakai mengunci** | jatah dipakai sebelum sandinya dicocokkan: 100 tebakan salah membuat pemilik akun menerima `429` — **juga dengan sandi yang benar** — dan penyerang yang terus mengirim satu tebakan tiap ±14 menit (±100 sehari, di bawah batas per IP) menahannya di sana **selama ia mau** | diterima untuk V0 (**K-22**) — tanpa batas per akun, tebakan terdistribusi tidak terhenti; mencabut penguncian ini butuh pemulihan akun atau kepercayaan per perangkat, yang belum ada |
| **token akses akun yang ditangguhkan** | status akun dibaca saat masuk dan tiap penyegaran, tidak tiap permintaan — token akses yang sudah terbit hidup sampai kedaluwarsa (bawaan 15 menit) | alur yang mengubah status (hapus akun 6.5, penangguhan) wajib memanggil `cabut_semua` |
| **klien yang mengulang penyegaran** sesudah kehilangan jawabannya | token bekas = pencurian: sesinya dicabut, pengguna masuk lagi | diterima (**K-21**, rotasi ketat RFC 9700) |
| **galat yang bukan galat basis data** dicatat apa adanya | pesan galat kode sendiri yang mengutip nilai pengguna akan sampai ke log | konvensi `AGENTS.md` — pesan galat tidak mengutip nilai; belum ada penegak |
| **batas per IP di balik penyeimbang beban** | uvicorn membaca `X-Forwarded-For` hanya dari `FORWARDED_ALLOW_IPS` (bawaan `127.0.0.1`); di belakang proksi lain, **semua klien berbagi IP proksi** — satu jatah untuk semua | D1+: isi `FORWARDED_ALLOW_IPS` dengan alamat proksi (arch/09) |
| **daftar tolak sandi berbasis aturan**, bukan daftar sandi bocor | pola dan kata konteks tertangkap; sandi 15+ karakter yang pernah bocor di layanan lain **tidak** | pemeriksaan sandi bocor butuh daftar besar atau layanan luar (B-2) — belum diputuskan |
| ekspor & hapus belum tercatat di audit | fiturnya belum ada | tugas 6.4 · 6.5 |
| **sandi peran login api di D0** tertulis di `.env` / bawaan compose | kredensial lokal `*-dev-only` | D1+: peran dibuat infrastruktur dengan sandi dari pengelola rahasia (arch/09 §5 aturan 3) |
| **PR merah tidak terhalang digabung** | merah-hijaunya kini **terlihat** sebagai status `ci-lokal` (gerbang lokal, **H-26** tanpa tagihan — Actions dimatikan, [#160](../../issues/160)), tetapi perlindungan branch & ruleset tidak tersedia untuk repo privat pada paket akun ini (HTTP 403). Status `ci-lokal` bukti kejujuran, bukan penghalang: siapa pun yang punya akses tulis bisa menempelkannya | pemilik — paket akun. Sampai itu: gerbangnya HUMAN REVIEW (H-25) |
| B-1 *kode agent tidak mengimpor `security/`* | belum bisa dinyatakan: V0 belum punya `security/` | tugas 4.5 |
| **id buatan klien membocorkan ada-tidaknya id** | `POST` dengan `id` yang sudah dipakai pengguna **lain** → `409 already_exists`: satu bit — *id ini ada di suatu tempat*. Tidak membocorkan isi, pemilik, atau jenisnya | diterima (tinjauan keamanan Sprint 2): id adalah uuid v4 acak 122 bit — menebak id orang lain sama mustahilnya dengan menebak kuncinya, dan id tetap global supaya klien luring bisa membuatnya sendiri (`spec/04`) |
| **jejak idempotensi milik akun yang dihapus** | rujukan (sidik HMAC · status · id — tanpa isi tulisan) dan jatah kuotanya hidup sampai 24 jam sesudah akunnya dihapus | penyapuan hapus akun menghapus `…:idem:<user_id>:*` (tugas 6.5) |
| eskalasi krisis untuk jurnal | `journal_entries.safety_flag` ada, jalurnya tidak | [#21](../../issues/21) — pemilik |
| pembangunan citra tidak sepenuhnya reprodusibel | `apt-get upgrade` saat membangun menarik tambalan Debian hari itu | dipilih sadar: citra dasar yang dipatok digest tidak pernah menerima tambalan sendiri |

Seluruh risiko hukum & privasi (butir **C** di
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md)) adalah keputusan
pemilik dan tidak diputuskan di kode.
