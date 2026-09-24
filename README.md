# HumanVerse XOS

> **AI-Native Human Development Platform**
> **One AI. Infinite Human Growth.**
> `Observe → Understand → Reason → Predict → Recommend → Act → Learn`

Bukan aplikasi *habit tracker* biasa. Seluruh domain kehidupan dihubungkan
menjadi satu **Human Knowledge Graph**, lalu di atasnya berdiri **AgentOS**,
**Memory Hierarchy**, **Context Engine**, **Behavior Engine**, **Decision
Engine**, dan **Digital Twin** — sebuah platform yang punya **runtime untuk
manusia + agent + data + knowledge + simulation + automation**.

> ✅ **Nama resmi diputuskan 3 September 2026: `HumanVerse XOS`.**
> Berkas naskah `01`–`77` tetap menulis nama versi masing-masing naskah
> (*HumanOS*, *HumanVerse X*) apa adanya. Lihat [`docs/10-IDENTITAS.md`](docs/10-IDENTITAS.md).

---

## Status proyek

| Hal | Keadaan |
|---|---|
| Tahap | 🔨 **Sprint 0 + Sprint 1 + Sprint 2 + Sprint 3 dikodekan** (16–24 Sep 2026) — branch `v0/sprint-0-foundation`, di atasnya `v0/sprint-1-identity`, `v0/sprint-2-human-core`, lalu `v0/sprint-3-memory-event` — **menunggu HUMAN REVIEW pemilik** |
| Berkas **kode produksi** | **0 di `master`** · **Sprint 0 + 1 + 2 + 3 (30 dari 51 tugas `spec/07`) di branch** — api Python + proses pekerja (`hvx.pekerja`) + aplikasi Flutter pertama (`apps/mobile`) — [#3](../../issues/3) dijawab pemilik untuk memulai (**H-25**): AI coding agent di branch + PR, pemilik yang menggabungkan |
| Berkas **perkakas** | **4** — [`tools/`](tools/README.md): `periksa_dokumen.py` · `uji_mutasi.py` · 🆕 `uji_mutasi_kode.py` · 🆕 `ci_lokal.py`. Di branch Sprint 0: **19 dari 26** pemeriksaan [`arch/11`](arch/11-PENEGAKAN.md) jalan (di `master`: 12) |
| Repo git | privat `xtheoputra/humanverse-xos`, branch `master` |
| Dokumen | **272 berkas** di `docs/` + **8 berkas** di `spec/` + **12 berkas** di [`arch/`](arch/README.md) |
| Gerbang yang **sudah dijalankan** | **14 ✅ · R-1 🛑 7 temuan** (keputusan cakupan pemilik) · **15 kontrak `import-linter`** · CI lokal **lint → typecheck → test → build → scan hijau** — `uv run python tools/ci_lokal.py`, **manual** |
| Merahnya **terbukti bisa terjadi** | **19 dari 19** — 25 mutasi dokumen (tiap mutasi wajib melahirkan temuan **baru**) + 344 mutasi kode (tiap mutasi wajib gagal dengan **alasan yang dimaksud**, dibaca dari baris galatnya — bukan dari mana pun di keluaran) · **tiap kontrak `import-linter` punya mutasinya sendiri** |
| Gerbang di PR | ✅ **gratis** — `tools/ci_lokal.py --lapor-github` menempelkan status **`ci-lokal`** ke commit PR; GitHub Actions **dimatikan** atas keputusan pemilik (**H-26** — tanpa tagihan, [#160](../../issues/160)) |
| Naskah pemilik | **24** — terakhir: **Phase 20 Civilization Platform** (39 bagian) — **fase TERAKHIR** |
| Keputusan tertutup | **27 butir H** — 🆕 **H-27 data tiap pengguna milik pribadinya** · 🆕 **H-26 CI tanpa tagihan** · **H-25 siapa mengerjakan V0** · nama · MVP · struktur repo · ambang konfirmasi · model memory · memory meluruh · gerbang policy · context package · dua tangga R/L · manifest dipulihkan · **model transisi belajar dari galat sendiri** · **monetisasi punya fase (Phase 14)**. ✅ **H-20 (peta fase) DIPULIHKAN sebagai [`arch/01`](arch/01-PETA-20-FASE.md) — peta versi 3, 20 baris TERTUTUP, dan peta kini BERNOMOR VERSI** sehingga *“roadmap yang sudah kita tetapkan”* selalu punya rujukan yang bisa dibuka ([#101](../../issues/101) · [#108](../../issues/108) · [#132](../../issues/132) · [#133](../../issues/133) · [#142](../../issues/142)). ✅ **H-13 ([#72](../../issues/72)) DISELESAIKAN:** `Phase` dan `V0–V6` bukan dua rencana yang bersaing melainkan **dua sumbu** — `Phase` menghitung dokumen, `V` menghitung rilis. ⚠️ **H-11** ([#78](../../issues/78)) masih perlu ditinjau ulang |
| Keputusan terbuka | **26 pertanyaan A** · **39 risiko B** · **167 ketidakcocokan E** · **20 lubang G** — dan **27 butir K** sudah saya putuskan sendiri |
| Tanggal dokumen | 24 September 2026 |

> ⚠️ **Nol baris kode di `master` itu disengaja sampai 16 Sep 2026 — dan kini
> tinggal menunggu HUMAN REVIEW Sprint 0.**
> Lima naskah sudah menjawab: **nama** (A-7), **MVP** (A-2), **struktur repo**
> (E-27), **Weather/Calendar = tool** (E-2/E-28), **empat penyimpanan bukan
> enam** (A-10), **V0–V6 sebagai rencana kanonik** (A-18), dan **Confidence
> Layer** untuk angka taksiran (B-15/B-1).
>
> ✅ **TIDAK ADA yang mengunci Engineering Spec.** Daftar "empat penghambat" di
> versi lama README ini **salah**, dan [`spec/README.md`](spec/README.md) sudah
> membantahnya sejak awal — lengkap dengan cara tiap butir ditangani di DDL:
> **#32** skala skor → `numeric(4,3) CHECK BETWEEN 0 AND 1` + `scoring_version` ·
> **#2** model angka → `metrics jsonb` + `model_version` (enam model boleh
> hidup berdampingan, tanpa migrasi) · **#7** model graf → **tidak menyentuh V0**,
> Neo4j baru di V2 · **#33** memory → **sudah ditutup** (`kind` + `scope`, plus
> `tier` dari H-16).
>
> ✅ **Penghambat untuk MEMULAI kode: NOL.** [#3](../../issues/3) dijawab pemilik
> 16 Sep 2026 (**H-25**) — AI coding agent mengerjakan di branch + PR, pemilik
> yang menggabungkan. Yang tersisa di #3 soal **waktu**, bukan soal siapa.
> [#20](../../issues/20) (merek & domain) memblokir **peluncuran**, bukan
> pengkodean ([`arch/10`](arch/10-URUTAN-IMPLEMENTASI.md) §2).
> ⭐ Dan **T0–T5** dari tiga belas tahap implementasi **tidak diblokir satu pun
> keputusan yang belum diambil**; mulai **T6** ke atas tiap tahap menunggu
> keputusan pemilik — dan semuanya menyangkut orang yang tidak punya akun atau
> badan orang.
>
> 🔑 Rekonsiliasi lengkap kedua dokumen ada di
> [`docs/GERBANG-SKEMA.md`](docs/GERBANG-SKEMA.md).
>
> ⭐ **11 Sep 2026 — aturan repo ini berhenti hanya dinyatakan.**
> [`tools/periksa_dokumen.py`](tools/README.md) menjalankan lima pemeriksaan
> [`arch/11`](arch/11-PENEGAKAN.md) atas dokumennya sendiri, dan menemukan
> **66 dari 127 nama event mendarat di domain yang tidak ada di registry**
> (`large` · `oil` · `interest` · `heart`), registry menulis *“39 domain”*
> untuk tabel berisi **45**, dan satu nama event tulisan pemilik
> (`MeetingCreated`) **tidak pernah sampai ke tabel padanan**. Ketiganya
> diselesaikan; **V0 tidak bergeser — 22 event tetap 22.**

---

## 🔨 Sprint 0 — kode pertama (16 Sep 2026)

Pemilik memilih: **AI coding agent mengerjakan di branch + PR, pemilik yang
menggabungkan** (**H-25**, [#3](../../issues/3)). Sprint 0
[`spec/07`](spec/07-BACKLOG-V0.md) dikerjakan penuh — satu commit per tugas.

| | Yang dibangun | Bukti mesin |
|---|---|---|
| 0.1 | monorepo + workspace `uv`; [`AGENTS.md`](AGENTS.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`SECURITY.md`](SECURITY.md) | `uv lock --check` · `uv sync --locked` |
| 0.2 | [`docker-compose.yml`](docker-compose.yml): PostgreSQL 16 · Redis 7 · migrate · api | `docker compose up --wait` → semua sehat |
| 0.3 | `apps/api` FastAPI + `GET /health` | `200 {status, version, db, redis}` · `503` kalau satu mati |
| 0.4 | Alembic + migrasi 0001 — 23 tabel, `data_subject` + anotasi retensi | katalog migrasi **==** DDL `spec/01`; naik → turun → naik identik |
| 0.5 | log JSON + `request_id` | tiap baris punya `request_id` & `user_id`; penutup punya `latency_ms` |
| 0.6 | `pytest` + cakupan | **≥ 70 %** (tercapai 93 %) |
| 0.7 | CI `lint → typecheck → test → build → scan` | [`tools/ci_lokal.py`](tools/ci_lokal.py) — satu sumber untuk lokal & Actions |
| 0.8 | batas modul + batas keras | **15 kontrak `import-linter`**, tiap kontrak terbukti sanggup gagal |

🔴 **Menulis kodenya menemukan empat hal yang tujuh sesi membaca tidak
temukan** — [`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md):
**E-161** `set_updated_at()` didefinisikan tetapi **nol pemicu** di 11 tabel ·
**G-24** 21 baris markdown **di dalam** blok SQL `spec/01` — DDL-nya tidak bisa
dijalankan · **E-162** `arch/06` §3 menyebut `CHECK` milik tabel lain ·
🛑 **B-40** `REVOKE` di `audit_logs` **tidak menghalangi** role yang dipakai api —
`UPDATE` & `DELETE` lolos, dan superuser melewati RLS. Yang terakhir
✅ **ditutup 17 Sep 2026** — lihat bagian berikut.

🚨 **Dan pindai citra merah di percobaan pertama**: 2 CVE HIGH (libpcre2) di
citra dasar Debian — gerbangnya berbunyi, citranya kini menambal paket saat
dibangun.

🔍 **Sebelum PR dibuka: tinjauan AI adversarial** — enam lensa, dan tiap temuan
diserahkan ke verifikator yang berusaha **membantahnya**. **35 temuan, 33
bertahan** (16 medium · 17 low · 0 high): **32 dibetulkan** di branch yang sama,
**1 dicatat** — **B-41** `user_id` baris anak tidak diikat ke induknya
(11 FK) — lalu ✅ **dibetulkan 17 Sep 2026** atas kata pemilik. Separuh temuan medium adalah
**penegak yang lulus tanpa melihat**: modul ke-13 lolos semua kontrak, 10 dari
12 kontrak M-2 tak pernah dibuktikan sanggup gagal, pembanding katalog buta
terhadap sepuluh perbedaan skema, dan satu mutasi R-1 dihitung berbunyi tanpa
menguji apa pun. Rinciannya:
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md).

---

## 🔒 Data tiap pengguna milik pribadinya (17 Sep 2026)

Pemilik: *“data milik satu pengguna harus milik pengguna tersebut, data
masing-masing pengguna milik pribadi user”* (**H-27**) — dan *“gunakan
alternatif versi gratis, jangan ada tagihan”* (**H-26**).

| Lapis | Menjaga | Bukti mesin |
|---|---|---|
| **RLS** di 21 tabel | aplikasi yang melayani pengguna A **tidak bisa** membaca, mengubah, atau menulis baris pengguna B — bahkan kalau `WHERE user_id` terlupa; tanpa pengguna → nol baris | `test_kepemilikan_data.py` |
| **FK komposit** — B-41 ✅ | baris anak milik B tidak bisa menunjuk induk milik A (11 relasi); menghapus induk tidak menyentuh baris orang lain | idem |
| **peran aplikasi** — B-40 ✅ | api bukan superuser, bukan pemilik tabel, tanpa `BYPASSRLS`; audit & event hanya-tambah; api **menolak mulai** kalau perannya salah | idem + `test_aplikasi_hidup.py` |
| **CI gratis** — H-26 | gerbang lokal menempelkan status `ci-lokal` ke PR; alur Actions hanya bisa dijalankan manual | `test_rantai_pasok.py` · `test_ci_lokal.py` |

Tiap penjaga baru terbukti sanggup gagal — **42 mutasi kode** (7 baru).

---

## 🔨 Sprint 1 — identitas (17 Sep 2026)

Pemilik: *“lanjutkan tugas yang belum selesai lainnya”*. Sprint 1
[`spec/07`](spec/07-BACKLOG-V0.md) dikerjakan penuh di branch
`v0/sprint-1-identity`, di atas Sprint 0 — satu commit per tugas (**K-18**) — 1.1 dan 1.3 dengan commit susulan (daftar tolak & NFKC · uji sidik IP · SQL statis), lalu satu commit untuk seluruh perbaikan tinjauan — dan **setiap
kueri berjalan sebagai peran aplikasi di bawah RLS** (H-27).

| | Yang dibangun | Bukti mesin |
|---|---|---|
| 1.1 | `POST /v1/auth/register · login · refresh · logout` — argon2id; sandi 15–128 karakter + daftar tolak + NFKC (NIST SP 800-63B-4); email tak terdaftar dijawab **sama persis** dengan sandi salah | `test_auth.py` · `test_sandi.py` |
| 1.2 | sesi: token opak di Redis, bukan JWT (**K-21**); token segar berotasi, pemakaian ulang mencabut seluruh sesi | dicabut → **401 seketika** — `test_sesi.py` |
| 1.3 | `GET /v1/me` · `PATCH /v1/me/profile` | timezone IANA divalidasi — `test_profil.py` |
| 1.4 | persetujuan hanya-tambah dengan `purpose` · `data_scopes` · `expires_at` (migrasi 0002, **B-22**); `model_training` tersendiri, tidak dikirim = ditolak | `data.purpose ⊆ consent.purpose` **dan** cakupan data — `test_persetujuan.py` |
| 1.5 | mesin izin `allow · deny · ask`, di-cache Redis | tanpa baris & kedaluwarsa → `ask`; **pencabutan seketika** — `test_izin.py` |
| 1.6 | `audit()` di transaksi yang sama dengan perubahannya | `UPDATE`/`DELETE` ditolak basis data — `test_identity_audit.py` |
| 1.7 | batas laju GCRA — per IP (IPv6 per /64), per pengguna, daftar & masuk, login gagal per akun (**K-22** · batas laju, **B-42**) | `429` + `Retry-After` — `test_batas_laju.py` |

🔴 **Menulisnya menemukan dua ketidakcocokan antar-`spec`** —
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md): **E-163**
`PUT /privacy/permissions` tidak bisa menunjuk satu baris izin · **E-164** badan
`register` tanpa tempat untuk persetujuan yang dituntut 1.4 — keduanya
dibetulkan di [`spec/04`](spec/04-API-CONTRACTS.md). Pertanyaan terbuka **K-17**
(di mana pendaftaran membuat profil) terjawab tanpa melanggar arah impor.

🔴 **Dan tiga hal yang “cukup” di kepala tetapi tidak di mesin** — cache izin yang
dihapus sebelum & sesudah commit masih bisa **menghidupkan kembali izin yang
baru dicabut**; NIST dikutip untuk panjang sandi sambil melewatkan **daftar
tolak** di pasal yang sama; dan klaim *“IP tidak disimpan mentah”* belum punya
uji yang akan merah. Ketiganya ditutup — dengan uji **dan** mutasi.

🔍 **Sebelum PR dibuka: tinjauan AI adversarial** — dan aturannya lebih keras
dari Sprint 0: **temuan tidak dipercaya dari laporannya**, tiap temuan ditulis
dulu sebagai uji yang **merah pada kode lama**, baru dibetulkan. **11 temuan,
ke-11-nya dibetulkan** — 8 dari peninjau (1 high · 2 medium · 5 low), 3 baru
ditemukan saat menulis uji untuk yang lain. Yang paling mahal kalau lolos:
**keluar di tengah penyegaran menghidupkan sesi kembali**, dan sesi itu tidak
bisa dicabut lagi — kini tiap operasi yang membaca lalu menulis satu catatan
sesi (putar · cabut) satu skrip Lua, dan ujinya
menyela **tiap celah antarperintah**. Yang paling tidak terduga: **pesan galat
PostgreSQL sendiri membawa email pengguna ke log** (`DETAIL: Key (email)=…`) —
kini galat basis data dicatat tanpa pesannya. Rinciannya:
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md).

🔍 **Lalu lensa kedua: tiga peninjau serentak** — verifikator yang berusaha
membantah perbaikan tadi, pembanding kontrak `spec/`, dan pemburu penegak buta.
Perbaikan pertama tidak bobol; tetapi **satu perbaikannya sendiri membuat
regresi** (status akun dibaca sesudah token diputar — galat basis data
membakar token klien), batas *“≤ 100 gagal beruntun, NIST”* ternyata **batas
laju** yang tidak memenuhi pasal itu (kini dinyatakan jujur: **B-42**), tiga
ketidakcocokan antar-`spec` lagi (**E-165** · **E-166** · **E-167**), dan
sepuluh penegak yang lulus tanpa melihat — termasuk **alat mutasi itu sendiri**,
yang bisa menghitung galat lingkungan sebagai *“berbunyi dengan alasan yang
dimaksud”*. Cacat kode dan penegak buta dibetulkan dengan uji **dan** mutasi;
ketidakcocokan `spec` dibetulkan di teksnya; B-42 diterima dan dinyatakan.

🔍 **Lensa terakhir memeriksa DOKUMENNYA** — tiap angka benar, tetapi **dua
belas kalimat** tidak: klaim NIST *“beruntun”* masih tersisa di empat tempat
sesudah ditulis *“dicabut di mana pun”*, penguncian per akun ditulis *“±14
menit”* padahal penyerang yang terus mencoba menahannya selama ia mau, dan
*“tiap kueri lewat transaksi pengguna”* padahal pencarian akun saat masuk
tidak — yang terakhir dibetulkan di **kode**.

Tiap penjaga baru terbukti sanggup gagal — **108 mutasi kode** (66 baru), **277 uji**.

---

## 🔨 Sprint 2 — Human Core (24 Sep 2026)

Pemilik: *“kerjakan semua tugas yang belum terselesaikan dengan sempurna”*.
Sprint 2 [`spec/07`](spec/07-BACKLOG-V0.md) dikerjakan penuh di branch
`v0/sprint-2-human-core`, di atas Sprint 1 — satu commit per tugas (**K-18**),
lalu satu commit untuk seluruh perbaikan tinjauan.

| | Yang dibangun | Bukti mesin |
|---|---|---|
| 2.1 | `goals` + milestone + `parent_id`; `GET /v1/goals/{id}/tree` (**E-168**) | pohon 3 tingkat = **satu** pernyataan SQL, dihitung di driver — `test_goals.py` |
| 2.2 | `habits` + jadwal + `adaptive_tiers`; `GET /v1/habits?for_date=` membawa tier yang disarankan **beserta alasannya** (**E-169**, **K-23**) | tier turun saat energi rendah — `test_tier.py` · `test_habit_hari_ini.py` |
| 2.3 | `habit_completions`, `for_date` = tanggal lokal **perangkat** | kirim ulang → `200` + baris lama, juga enam serentak — `test_penyelesaian.py` |
| 2.4 | rentetan & tingkat penyelesaian per hari · minggu ISO · bulan | pengguna yang pindah **Pago Pago → Kiritimati** (UTC−11 → UTC+14) lewat HTTP — `test_rentetan.py` |
| 2.5 | `daily_checkins`, `PUT` = ganti | `PUT` dua kali → satu baris — `test_checkin.py` |
| 2.6 | `mood_entries` — dilaporkan pengguna, waktu wajib berzona | kontrak `spec/04` — `test_mood.py` |
| 2.7 | **aplikasi Flutter pertama** — masuk/daftar, habit hari ini, energi, tandai selesai dengan tier | **layar diketuk terhadap api hidup** di tahap smoke — `apps/mobile/test/ujung/` |

🔴 **Menulisnya menemukan dua rute yang `spec/07` tuntut tetapi `spec/04` tidak
punya** — **E-168** pohon goal · **E-169** habit pada tanggal tertentu — dan
satu pola baru di titik rakit: bacaan lintas modul domain yang harus satu
transaksi (**K-23**).

🔍 **Tinjauan adversarial sebelum PR — tiga lensa serentak** (keamanan ·
kontrak · penegak buta), tiap temuan dibuktikan **merah dulu** lewat HTTP atau
basis data. Yang paling mahal kalau lolos: **FastAPI memvalidasi dalam mode
longgar** — `true` diterima sebagai valensi mood terburuk, detik Unix sebagai
`for_date` **UTC**, dan persetujuan pelatihan model tercatat dari string
`"on"` (**E-170**); **goal anak yang dibuat serentak dengan hapus induknya
menjadi yatim, 40 dari 40** (**E-172**); dan **cache `Idempotency-Key`
menyimpan isi jawaban 24 jam** di Redis yang sama dengan sesi — memori yang
murah dihabiskan, dan catatan pengguna yang tinggal sesudah dihapus
(**E-171**, kini rujukan + kuota, **K-24**). Lensa ketiga merusak kode satu
kerusakan per percobaan: **39 kerusakan lolos seluruh suite** — termasuk klien
yang tidak pernah memanggil `logout` dan tetap lulus uji ujung-ke-ujung lawan
api hidup. Tiap kerusakan kini punya uji yang merah padanya. Rinciannya:
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md).

Tiap penjaga baru terbukti sanggup gagal — **217 mutasi kode** (109 baru),
**579 uji Python + 40 uji Flutter**.

---

## 🔨 Sprint 3 — Memory & event (24 Sep 2026)

Sprint 3 [`spec/07`](spec/07-BACKLOG-V0.md) dikerjakan penuh di branch
`v0/sprint-3-memory-event`, di atas Sprint 2 — satu commit per tugas
(**K-18**), lalu satu commit untuk seluruh perbaikan tinjauan.

| | Yang dibangun | Bukti mesin |
|---|---|---|
| 3.1 | modul `events` — amplop `spec/03`, idempotensi, uji admisi saat terbit | event ganda ditelan sebagai sukses, juga serentak — `test_event.py` |
| 3.2 | tiap tulisan **fakta perilaku** menerbitkan event di transaksi yang sama (**E-177 … E-179**) | tiap baris peta aturan 6 lewat HTTP, dan batal bila eventnya gagal — `test_penerbitan_event.py` |
| 3.3 | relay kotak keluar → Redis Streams + grup konsumen, di **proses pekerja** (`python -m hvx.pekerja`, **K-25**) | konsumen mati → pesannya diklaim yang hidup; proses pekerja diuji sebagai proses — `test_relay.py` · `test_pekerja.py` |
| 3.4 | `journal` — daftar **tanpa** `body` | jawaban, kontrak OpenAPI, dan **SQL yang sampai ke PostgreSQL** (**E-181**) — `test_jurnal.py` |
| 3.5 | Qdrant lewat REST + penyemat lokal **berkunci per pengguna** (**K-26**) | saringan `user_id` wajib; kata tidak terbaca dari vektor tanpa kunci — `test_vektor.py` · `test_sematan.py` |
| 3.6 | memori **episodik** dari jurnal & mood (**K-27**) | tiap memori punya lima medannya — `test_memori.py` |
| 3.7 | pencarian memori bersaring scope + **daftar scope resmi** (**E-180**) | agent tanpa izin scope tidak menerima barisnya — tiga jalan, dan satu bukti bahwa izinlah pembedanya |
| 3.8 | `activities` — `inferred` terpisah dari `manual` | klien tidak bisa mencatat `inferred` — `test_aktivitas.py` |

🔴 **Menulisnya menemukan lima celah dokumen** — kunci idempotensi `spec/03`
yang menelan koreksi (**E-177**), pembatalan yang tidak meninggalkan jejak
(**E-178**), aturan 6 yang menuntut event yang tidak ada (**E-179**), *daftar
scope resmi* yang dirujuk tetapi tidak pernah ditulis (**E-180**), dan penegak
yang buta terhadap kueri yang memuat isi jurnal (**E-181**).

🔍 **Tinjauan adversarial sebelum PR — tiga lensa serentak.** Yang paling
mahal kalau lolos: **satu kunci penyemat untuk semua pengguna** — akun biasa
menyemat kamusnya sendiri lalu membaca mood dan kata-kata jurnal orang lain
dari vektornya, tanpa pernah menyentuh kunci (**E-182**, kini kunci per
pengguna); **peran api yang menghadap internet bisa memanggil fungsi pekerja**
dan membaca linimasa semua pengguna melewati RLS (**E-186**, kini peran
`hvx_pekerja`); dan **pencarian yang mencocokkan kata yang sudah dihapus
pemiliknya** dari jurnal (**E-184**). Lensa ketiga merusak kode satu
kerusakan per percobaan: **49 dari 68 kerusakan lolos seluruh suite** — tiap
kerusakan kini punya uji yang merah padanya. Dan satu cacat Sprint 1 yang
ketahuan lewat uji yang berkedip di gerbang penuh: **izin sementara yang sudah
habis masih dijawab `allow` dari cache** bila Redis ditulis > 1 dtk sesudah
basis data dibaca (**E-189**, kini berakhir mutlak). Rinciannya:
[`docs/99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md). Pertanyaan baru untuk
pemilik: **C-33** — teks bebas di payload event tidak bisa dicabut pemiliknya.

Tiap penjaga baru terbukti sanggup gagal — **344 mutasi kode** (127 baru),
**767 uji Python + 40 uji Flutter**.

---

## 📌 Pekerjaan terbuka = GitHub Issues

**157 issue** dalam 3 milestone — **59 ditutup, 98 terbuka**. Baca issue-nya,
jangan analisis ulang naskahnya.

> ⭐ **26 ditutup pada 10 Sep 2026** oleh [`arch/`](arch/README.md) — bukan
> dengan menjawabnya satu per satu, melainkan dengan **memberi bentuk kanonik**
> tempat masing-masing terjawab: satu peta fase · satu pohon monorepo · satu
> rantai gerbang · satu amplop event · empat kelas penyimpanan.

| Milestone | Isi | Issue |
|---|---|---|
| **M1 — Keputusan sebelum kode** | **28 terbuka, 15 ditutup** | [#1](../../issues/1)–[#9](../../issues/9), [#38](../../issues/38), [#58](../../issues/58)–[#59](../../issues/59), [#72](../../issues/72), [#80](../../issues/80), [#90](../../issues/90)–[#93](../../issues/93), [#98](../../issues/98)–[#101](../../issues/101), [#103](../../issues/103), [#105](../../issues/105), [#108](../../issues/108), [#111](../../issues/111)–[#113](../../issues/113) |
| **M2 — Blueprint & Platform** | **44 terbuka, 42 ditutup** | [#10](../../issues/10)–[#19](../../issues/19), [#26](../../issues/26)–[#37](../../issues/37), [#39](../../issues/39), [#41](../../issues/41)–[#45](../../issues/45), [#47](../../issues/47)–[#49](../../issues/49), [#51](../../issues/51), [#54](../../issues/54)–[#56](../../issues/56), [#60](../../issues/60)–[#70](../../issues/70), [#73](../../issues/73)–[#74](../../issues/74), [#77](../../issues/77)–[#79](../../issues/79), [#82](../../issues/82)–[#84](../../issues/84), [#87](../../issues/87)–[#89](../../issues/89), [#94](../../issues/94), [#96](../../issues/96)–[#97](../../issues/97), [#106](../../issues/106)–[#107](../../issues/107), [#109](../../issues/109)–[#110](../../issues/110) |
| **M3 — Sebelum ada pengguna nyata** | **26 terbuka, 2 ditutup** | [#20](../../issues/20)–[#25](../../issues/25), [#40](../../issues/40), [#46](../../issues/46), [#50](../../issues/50), [#52](../../issues/52)–[#53](../../issues/53), [#57](../../issues/57), [#71](../../issues/71), [#75](../../issues/75)–[#76](../../issues/76), [#81](../../issues/81), [#85](../../issues/85)–[#86](../../issues/86), [#95](../../issues/95), [#102](../../issues/102), [#104](../../issues/104), [#114](../../issues/114) |

✅ **H-10 SELESAI — [`arch/03`](arch/03-MONOREPO-FINAL.md).** Monorepo final
sempat tergerus **sepuluh kali** oleh sepuluh naskah berturut-turut, sehingga
pohon keluarga keamanan mencapai **sembilan belas** dan aturan impor §8.42
(*“kode agent tidak boleh mengimpor `security/`”*) **tidak bisa DINYATAKAN** —
tidak ada satu `security/` untuk dirujuk.

| | Sebelum | Sesudah |
|---|---|---|
| pohon repositori | **38** | **28 folder** tingkat-atas |
| **pohon keluarga keamanan** | 🛑 **19** | ✅ **1** (+ `governance/` berdiri sendiri) |
| nama dipakai >1 pohon | **128** | **0 tabrakan konsep** |
| `sdk/` · `simulation/` · `agents/` · `memory/` | 14 · 13 · 10 · 8 | 1 · 1 mesin + 4 plugin bernama · 1 · 1 |

Yang menutupnya bukan keputusan kesebelas melainkan **aturan komposisi**: uji
naik-turun [K-9](docs/KEPUTUSAN-DIDELEGASIKAN.md) dengan **tiga** hasil (naik ·
tinggal · **ganti nama**), ditambah satu syarat yang tidak ada di K-9 — **uji
hanya dijalankan atas nama yang dipakai TANPA induknya**. Ke-54 nama yang
dipakai ≥3 pohon divonis satu per satu; sisa 74 diselesaikan prosedur mekanis
saat pohonnya dibangun.

⇒ **Sprint 0 tugas 0.1 tidak menunggu apa pun lagi.**

🔴🔴 **Dan sekarang seluruhnya sudah DIHITUNG, bukan diingat** —
[`docs/SENSUS-MODUL.md`](docs/SENSUS-MODUL.md) ([#146](../../issues/146)):
**38 pohon repositori** di 36 dokumen · **424 nama direktori unik** ·
**128 (30 %) dipakai lebih dari satu pohon**. Sensus itu membalik dua angka
yang selama ini dipakai: `simulation/` dilacak lima naskah dan berhenti di
*“keenam kalinya”* — nyatanya **lima belas pohon**; dan yang paling banyak
diduplikasi bukan `simulation/` melainkan **`sdk/` di EMPAT BELAS pohon**, yang
**tidak pernah sekali pun dihitung**. 💡 Pelajarannya: menghitung *“ini yang ke
berapa”* satu per satu di berkas yang berbeda-beda **meleset ke bawah secara
sistematis** — yang dibutuhkan satu sensus, bukan catatan yang lebih rajin.

🔴🔴 **Peta fasenya juga diukur** — [`docs/PETA-FASE.md`](docs/PETA-FASE.md)
([#148](../../issues/148)): untuk `Phase` ada **tiga** peta, bukan dua, dan
kedua peta yang bisa diuji **gagal dengan cara yang persis sama** — benar untuk
fase-fase terdekat, meleset di ujung. Peta naskah 8 meramalkan 8 fase dan tepat
pada **empat yang terdekat**; §10.41 meramalkan 5 dan meleset pada **yang
terjauh**. ⇒ **jangkauan andal sebuah peta fase di repo ini ± 3–4 fase.**
⭐ Dan satu koreksi yang **memperkecil** pekerjaan: [#142](../../issues/142)
menyimpulkan *“Phase 1–8 belum pernah didaftar”* dari sebuah `grep` yang
menuntut huruf besar semua — pola itu **mustahil** cocok dengan *“Phase 5:
HumanVerse Research Lab”*. **Tujuh dari delapan fase sudah punya nama**, dan
sudah terkumpul di [`99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md) baris
17–20. Sisanya **satu nama (Phase 1) + tujuh kata kerja**, bukan delapan baris
kosong. 💡 *`grep` yang mengembalikan nol membuktikan “tidak ada yang berbentuk
ini”, bukan “tidak ada”.*

🔴🔴 **Nama event juga dihitung** — [`docs/SENSUS-EVENT.md`](docs/SENSUS-EVENT.md)
([#149](../../issues/149)). [#38](../../issues/38) sudah ditutup dengan format
`domain.verb`, dan pelanggarannya dicatat sampai *“kesepuluh”* — tetapi yang
dihitung selama ini **kejadian**, bukan **nama**. Sensus: **21 nama sesuai
lawan 128 nama PascalCase yang ditulis sesudah keputusan**. ⭐ Dan yang paling
menentukan: **ke-21 nama yang sesuai semuanya berasal dari naskah 5** — sejak
itu pemilik menamai 128 event baru dan **nol** memakai format yang dipilih.
Formatnya bukan diperdebatkan, ia tidak pernah dipakai lagi. 💰 Biayanya masih
nol karena belum ada kode — kecuali **tiga tabrakan kosakata**
(`sleep.completed`↔`SleepEnded` dan dua lainnya) yang tidak selesai hanya
dengan mengubah bentuk.

🔴🔴 **Daftar agent juga dihitung** — [`docs/SENSUS-AGENT.md`](docs/SENSUS-AGENT.md)
([#150](../../issues/150)). Jumlah agent selama ini ditaksir dengan
**penjumlahan** (*“> 40”* dari 25 + 7 + 12), yang mengabaikan dua daftar lebih
tua dan menganggap tak ada nama berulang. Himpunannya: **80 baris mentah → 59
nama unik**, **nol** muncul di semua daftar, dan **44 (75 %) hanya pernah
disebut sekali**. ⭐ Irisan ketiga registry umum — yang berisi 14, 22, dan 25
agent — tepat **enam**: `Career · Fashion · Habit · Learning · Social · Travel`,
**semuanya agent domain**. 💡 *Menjumlahkan daftar bukan menghitung himpunan —
dan yang menentukan bukan totalnya melainkan irisannya.*

🔴🔴 **Dan separuh kedua [#38](../../issues/38) ternyata terbalik arahnya.**
Sepuluh catatan menandai naskah sebagai *“`/v1/…` lagi, bukan `/api/v1`”* —
sensus: **111 rute `/v1/…` di 12 naskah, dan NOL `/api/v1`**, 92 di antaranya
persis bentuk yang ditetapkan **standar penamaan pemilik sendiri** (naskah 7
Layer 22, `/v1/fashion/outfits`). Naskahnya konsisten; yang menyimpang
`spec/04` — berkas saya. 🛑 Dan komentar yang **menutup** #38 sudah menuliskan
janjinya (*“itu bagian saya, akan diselaraskan”*) — janji itu tak pernah
dijalankan, sementara sepuluh catatan berikutnya menandai sisi yang tidak
dijanjikan berubah. ✅ **Diselesaikan: `spec/04` kini berawalan `/v1`** (satu
baris). 💡 *Janji perbaikan di komentar issue yang DITUTUP tidak punya penjaga —
tanyakan “ada janji tercatat di sini, siapa yang memeriksanya?”*

🔴🔴 **Jumlah tabel pun berhenti dipelihara delapan fase yang lalu** —
[`docs/SENSUS-TABEL.md`](docs/SENSUS-TABEL.md) ([#151](../../issues/151)).
Catatan **E-106** menjumlahkan `23+20+16+14+26 = 99`, dan **metodenya benar**
(tiap suku neto) — tetapi ia **berhenti di Phase 12**. Himpunannya
**247 nama tabel** di 14 dokumen; **139 di antaranya lahir sesudah Phase 12 dan
belum pernah masuk hitungan mana pun**. 🛑 Dan **`agent_capabilities` serta
`agent_trust_scores` didefinisikan EMPAT kali** (Phase 8·11·14·18) — untuk
tabel yang memegang kapabilitas dan kepercayaan agent, itu empat kemungkinan
bentuk kolom. ✅ Sensusnya divalidasi enam kali; yang terkuat: ia mereproduksi
sendiri pernyataan provenans [`spec/01`](spec/01-DATABASE-SCHEMA.md).

🛑🛑 **Dan satu temuan keselamatan yang lahir dari melacak SATU tindakan
melintasi empat tangga risiko** — [`docs/SENSUS-TANGGA.md`](docs/SENSUS-TANGGA.md)
([#152](../../issues/152)). *“Kirim pesan kepada orang lain”* adalah **level 3**
di naskah 4, **level 3** di naskah 5, dan **R3** di Phase 8 — lalu **R2** di
Phase 11 (*“send low-risk message”*). Ambangnya sudah ditutup sebagai **H-15**:
otomatis sampai R2, konfirmasi wajib mulai R3 — jadi **pemindahan itu melewati
ambangnya**. §11.15 bahkan menaruh pesan di **dua tingkat dalam satu tabel**,
dipisahkan hanya oleh kata sifat yang tak pernah didefinisikan. ⭐ Tetangganya
`purchase low-value item` punya cacat identik tetapi **diselamatkan**
`amount_limit: 0`; pesan tidak punya padanannya. ⇒ **Dari tiga kategori di baris
R2, yang tidak mendapat definisi maupun angka bawaan justru satu-satunya yang
punya orang lain di ujung penerimanya.**

⭐ **Dan satu sensus akhirnya membawa kabar BAIK** —
[`docs/SENSUS-RANTAI.md`](docs/SENSUS-RANTAI.md) ([#153](../../issues/153)).
Tujuh catatan melaporkan *"rantai tanpa gerbang"* tanpa pernah menyebut
penyebutnya. Sensus: **387 rantai**, **36 berakhir di tindakan**, dan
**20 di antaranya SUDAH punya gerbang**. Dari 16 yang ditandai, **10 bukan
cacat** (dekomposisi tujuan, pipeline CI, kill-switch, rantai provenans) dan
2 sudah tertangani. 🛑 **Tiga benar-benar baru, dan ketiganya menggerakkan
benda fisik**: §15.15 (*lambaian tangan menjadi tindakan tanpa satu simpul pun
di antaranya*), §16.5 (*tujuan manusia langsung ke kendali sendi*), §16.7
(*punya `Collision Check`, tetapi itu menjawab "aman secara fisik", bukan
"boleh dilakukan"*).

## 🔧 Dua puluh tujuh keputusan yang diambil sendiri — [`docs/KEPUTUSAN-DIDELEGASIKAN.md`](docs/KEPUTUSAN-DIDELEGASIKAN.md)

Atas permintaan pemilik (*"beri keputusan sendiri sesuai aturan"*, 9 Sep 2026),
**dua puluh** pertanyaan **engineering** diputuskan dan ditegakkan di `spec/`
dan `arch/` — tiap butir dengan **bacaan yang ditolak** dan **cara
membalikkannya**:

| | Keputusan | Ditegakkan di |
|---|---|---|
| **K-1** | Kapabilitas yang menyentuh **pihak ketiga** = minimum **R3** | `spec/05` aturan 7 + medan `reaches_third_party` |
| **K-2** | `world-model/` **menyimpan**, `simulation/` **menjalankan** | — |
| **K-3** | **128** nama event **dipadankan**; naskah **tidak** diubah | `spec/03` tabel padanan |
| **K-4** | Tabel berdefinisi ganda: `spec/01` menang, lalu fase terawal | `spec/01` |
| **K-5** | **Tiga uji** agent lawan service | `spec/05` |
| **K-6** | Tujuh **kata kerja** Phase 2–8 | — |
| **K-7** | §15.15 mendapat simpul `Permission` | — |
| **K-8** | Awalan API `/v1` | `spec/04` |
| **K-9** | **Satu monorepo** + **uji naik-turun**; keamanan (**19 pohon**) jadi satu | — · membuka blokir **Sprint 0 tugas 0.1** |
| **K-10** | **Satu amplop event**; `SecurityEvent` → domain `security.*` | `spec/03` |
| **K-11** | Tiap tangga bernomor membawa **awalan** (`DP-L6`, `ARCH1`, `D6.1`) | — |
| **K-12** | `risk_level` **wajib**; larangan scope + `spatial`·`location`·`people`·`csi` | `spec/05` aturan 8 & 9 |
| **K-13** 🆕 | Bahasa backend = **Python + FastAPI** — `spec/` diam-diam berganti bahasa | `spec/06` · `spec/07` |
| **K-14** | **Memanggil agent lain ADALAH pemanggilan tool**; agent memakai `max_risk`, bukan `risk_level` | `spec/01` · `spec/05` aturan 3 |
| **K-15** | **Domain event diambil dari registry, bukan dari kata pertama nama** — K-3 benar sebagai transkripsi, tidak pernah jadi aturan kepemilikan | `spec/03` (64 nama) · `arch/07` §2 §4 §6 |
| **K-16** | **`data_subject` + tiga anotasi retensi masuk 23 tabel V0 sekarang** — uji yang dipakai: *yang boleh masuk V0 hanyalah yang TIDAK BISA ditambahkan nanti* | `spec/01` · `spec/07` 0.4 · `arch/06` §5 §6 |
| **K-17** | **Arah IMPOR modul V0: `events` di bawah modul domain** — gambar `spec/06` arah data; aturan 6 (tiap tulisan domain menerbitkan event) menentukan arah impor | `pyproject.toml` kontrak `m1-m3-lapisan` |
| **K-18** | **Satu commit per tugas; PR boleh satu per sprint** — harga yang diakui: hanya commit terakhir yang dijamin lulus gerbang penuh | `spec/07` · `CONTRIBUTING.md` |
| **K-19** 🆕 | **Kepemilikan data dijaga basis data** — RLS berbasis pengguna-transaksi · FK komposit · api menolak mulai sebagai pemilik tabel | `spec/01` §10–§11 · `test_kepemilikan_data.py` |
| **K-20** | **CI tanpa tagihan** — gerbang lokal menempelkan status `ci-lokal`; alur Actions hanya manual | `tools/ci_lokal.py` · `test_rantai_pasok.py` |
| **K-21** | **Sesi: token opak di Redis, bukan JWT** — sidik saja di Redis; token segar berotasi, pemakaian ulang mencabut seluruh sesi | `identity/sesi.py` · `test_sesi.py` |
| **K-22** | **Sandi dan batas laju: angka yang dipilih** — 15–128 + daftar tolak + NFKC; GCRA per IP · pengguna · kredensial · akun (batas laju, bukan penguncian — **B-42**) | `identity/sandi.py` · `test_batas_laju.py` |
| **K-23** | **Bacaan lintas modul domain lewat titik rakit** — pembaca/pendengar di `app.state`, satu transaksi, bukan impor; energi check-in → tier adaptif | `hvx/main.py` · `test_main.py` |
| **K-24** | **Ukuran dibatasi saat menulis; `Idempotency-Key` mengingat rujukan** — 1.000 goal · 100 milestone · 500 habit · badan 1 MiB · 1.000 kunci/hari | `test_batas_dan_balapan.py` · `test_idempotensi.py` |
| **K-25** 🆕 | **Relay kotak keluar & grup konsumen** — stream membawa rujukan, bukan isi; jendela belakang 60 dtk, penanda dipangkas menurut kursor; klaim sesudah 30 dtk, stream mati sesudah 5 kali; peran `hvx_pekerja` | `hvx/pekerja.py` · `test_relay.py` |
| **K-26** 🆕 | **Penyemat memori V0: lokal, deterministik, berkunci per pengguna** — tanpa API berbayar (A-6/#18, H-26) | `platform/sematan.py` · `test_sematan.py` |
| **K-27** 🆕 | **Memori V0: episodik** — yang dilaporkan atau ditulis pengguna, keyakinan 1.000, bukti 1; ekstraksinya service, bukan agent | `memory/ekstraksi.py` · `test_memori.py` |

🛑 **Yang sengaja TIDAK saya putuskan:** [#139](../../issues/139) (waktu pemilik) ·
[#3](../../issues/3) (orang) · [#20](../../issues/20) (merek) · **seluruh butir C**
(hukum & privasi) · **§16.5 · §16.7** rantai humanoid · [#34](../../issues/34)
(butuh data nyata untuk dikalibrasi).

💡 **Aturan pemilahnya: kalau salahnya keputusan ini ditanggung orang lain —
pengguna, penerima pesan, atau pemilik uangnya — keputusan itu bukan milik saya.**

⚠️ **Nol dari dua belas mengubah V0**: `spec/01` tetap 23 tabel, `spec/03` tetap
22 event V0, keempat agent V0 lulus ketiga uji K-5.

✅ **Ditutup:** [#1](../../issues/1) rencana kanonik → V0–V6 ·
[#8](../../issues/8) struktur repo · [#12](../../issues/12) Weather/Calendar = tool ·
[#17](../../issues/17) empat penyimpanan · [#10](../../issues/10) blueprint ·
[#31](../../issues/31) Engineering Specification · [#38](../../issues/38) nama event dua segmen ·
[#5](../../issues/5) ambang konfirmasi → **otomatis sampai R2, konfirmasi mulai R3** ·
[#52](../../issues/52) `risk_level` kembali & konfirmasi pindah ke Policy Engine ·
[#33](../../issues/33) memory = **tiga sumbu** `kind`/`scope`/`tier` ·
[#50](../../issues/50) Identity Memory **meluruh**, tidak permanen ·
[#42](../../issues/42) `POLICY_CHECK` masuk rantai percakapan ·
[#62](../../issues/62) agent tidak mengambil data — **context package** ·
[#66](../../issues/66) peta fase **diganti**: 12 → **15 fase**, Agency→P11, Digital Twin→P12,
Marketplace→P14 ·
[#67](../../issues/67) **dua tangga dipisahkan** — `risk_level: R1` + `autonomy.max_level: L2` ·
[#61](../../issues/61) manifest memulihkan `purpose` + `memory.read`/`write` ·
[#70](../../issues/70) model transisi punya sumber — **galat prediksinya sendiri**.

🛑 **Penghambat V0 yang tersisa — tiga:**
[#3](../../issues/3) 12 fitur & 7 sprint dalam 4–6 minggu ·
[#20](../../issues/20) cek merek ·
🆕 [#59](../../issues/59) **`consents.purpose` + `model_training` harus ada sebelum baris data
pertama** — §8.10 melarang memakai data di luar tujuan pemberiannya, jadi data V0 yang tidak
pernah menanyakannya **tidak bisa melatih model apa pun di Phase 5**. Biayanya nol sekarang,
hampir mustahil nanti.
*(#38 format nama event ✅ ditutup naskah 10 — dua segmen. #5 ambang konfirmasi ✅ ditutup
naskah 12 — R3 ke atas.)*
Yang masih menunggu jawaban tapi tidak menahan Sprint 0–4:
[#2](../../issues/2) model angka pengguna (menahan Sprint 5) ·
[#21](../../issues/21) eskalasi krisis Journal (menahan rilis ke orang lain — dan naskah 12
lewat tanpa menyebut jurnal sekali pun) ·
[#58](../../issues/58) berapa banyak Fase 8 & 9 masuk V0 (punya default aman: pakai 23 tabel yang
sudah ada) ·
🆕 [#67](../../issues/67) **dua tangga 0–4 yang terbalik di ujung atas** — otonomi “Level 4”
(bertindak sendiri) vs risiko “R4” (wajib konfirmasi); belum mengikat V0 karena tidak ada tool
di atas level 2, tapi harus diselesaikan sebelum tangga mana pun masuk basis data ·
🆕 [#72](../../issues/72) **rencana kanonik: V0–V6 atau Phase 1–15?** Naskah 13 & 14 tidak
menyebut tangga V sama sekali, dan **V0 tidak punya tempat di daftar 15 fase** — padahal V0
satu-satunya lingkup tertutup yang pernah ditetapkan. Ini H ketiga yang tergerus ·
[#75](../../issues/75) pemantauan berkelanjutan di dalam rumah — izin `Always`; belum mengikat V0
(tidak ada kamera), tapi on-device (§10.28) harus mendahului Vision ·
[#80](../../issues/80) V0 reaktif atau proaktif? — jawaban aman: **V0 reaktif** ·
🆕 [#86](../../issues/86) **sampai horizon berapa proyeksi boleh ditampilkan?** §12.13 memberi
sampai **5 tahun**, dan horizon 3–5 tahun **tidak pernah masuk loop belajar** — satu-satunya
keluaran yang tidak bisa dikalibrasi ·
🆕 [#85](../../issues/85) **proyeksi masa depan = kelas data baru** yang paling diinginkan pihak
ketiga; dan §12.22 memakai bobot utilitas yang **disimpulkan** untuk **memaksimalkan**, bukan
lagi membandingkan.

---

## 🗺️ HumanVerse Master Architecture v2.0 — [`arch/`](arch/README.md)

**Dikerjakan 10 September 2026 atas perintah pemilik** (*“kerjakan semua tugas
dan fase yang masih tersisa”*), menjawab penutup naskah 24 dan
[#139](../../issues/139). Cakupannya **Phase 1–20**; `spec/` tetap **V0 saja**.

> 🔑 **Aturan pengutamaan: `arch/` mengikat NAMA & BATAS, `spec/` mengikat
> BENTUK. Untuk V0, `spec/` menang. Naskah tidak pernah diubah.**

| Berkas | Yang berubah dari “kalimat” menjadi “daftar” |
|---|---|
| [`arch/01`](arch/01-PETA-20-FASE.md) | **peta fase v3** — 20 baris tertutup, satu kata kerja per fase; `Phase` dan `V0–V6` **didamaikan** (dua sumbu, bukan dua rencana) |
| [`arch/02`](arch/02-BOUNDED-CONTEXT.md) | **17 bounded context**, tiap konteks memiliki kosakatanya; **kamus tabrakan** 9 kata |
| [`arch/03`](arch/03-MONOREPO-FINAL.md) | **54 nama** ≥3 pohon divonis satu per satu; **19 pohon keamanan → 1**; 38 pohon → **28 folder** |
| [`arch/04`](arch/04-DEPENDENCY-GRAPH.md) | graf asiklik + **6 batas keras** + **rantai tindakan kanonik 12 gerbang** |
| [`arch/05`](arch/05-TECHNOLOGY-STACK.md) | tumpukan final; **temuan: `spec/` berganti bahasa backend tanpa mencatatnya** |
| [`arch/06`](arch/06-DATA-ARCHITECTURE.md) | **247 nama tabel** → 4 kelas penyimpanan; **19 definisi ganda** selesai; retensi wajib |
| [`arch/07`](arch/07-EVENT-CONTRACTS.md) | satu amplop; **39 domain terdaftar**; aturan apa yang **bukan** event |
| [`arch/08`](arch/08-AGENT-CONTRACTS.md) | **59 nama** diuji K-5; Konstitusi §20.16 diberi **penegak per pasal** |
| [`arch/09`](arch/09-DEPLOYMENT-TOPOLOGY.md) | D0–D5 dengan **pemicu terukur**; apa yang tak boleh meninggalkan perangkat |
| [`arch/10`](arch/10-URUTAN-IMPLEMENTASI.md) | **T0–T12** — dan **T0–T5 tidak diblokir keputusan apa pun**; [#3](../../issues/3) dijawab (**H-25**) |
| [`arch/11`](arch/11-PENEGAKAN.md) | **26 pemeriksaan CI**; **19 jalan** di branch Sprint 0; blok ` ```penegak ` yang dibaca uji |

🛑 **Nol butir C diputuskan.** Yang menyangkut hukum, uang, orang, dan cakupan
produk tetap milik pemilik — `arch/` menyediakan **mekanisme yang menegakkan apa
pun yang pemilik putuskan**, bukan keputusannya.

---

## 🔧 Engineering Specification v1.0 — [`spec/`](spec/README.md)

Lapisan **04** dari peta 14 lapisan naskah 6, dikerjakan penuh. **Bukan kata
pemilik** — sengaja di luar `docs/` supaya berkas naskah tetap murni.

| Berkas | Isi |
|---|---|
| [`spec/01-DATABASE-SCHEMA.md`](spec/01-DATABASE-SCHEMA.md) | DDL PostgreSQL — **23 tabel**, tipe, PK, FK, index, constraint, prosedur hapus akun |
| [`spec/02-ERD.md`](spec/02-ERD.md) | Relasi + 6 aturan kepemilikan data |
| [`spec/03-EVENT-CONTRACTS.md`](spec/03-EVENT-CONTRACTS.md) | Envelope, **versi · urutan · idempotensi**, 22 event, consumer |
| [`spec/04-API-CONTRACTS.md`](spec/04-API-CONTRACTS.md) | Endpoint REST V0 + Privacy Center |
| [`spec/05-AGENT-CONTRACTS.md`](spec/05-AGENT-CONTRACTS.md) | Manifest schema (**9 aturan validasi**), tool registry, risk gate |
| [`spec/06-MODULE-BOUNDARIES.md`](spec/06-MODULE-BOUNDARIES.md) | Batas modul + 6 aturan yang **ditegakkan CI** |
| [`spec/07-BACKLOG-V0.md`](spec/07-BACKLOG-V0.md) | **51 tugas** dalam 7 sprint, siap diberikan ke AI coding agent |

**Tiga issue pengunci ternyata tidak perlu diputuskan sekarang** — skemanya
menampung kedua kemungkinan tanpa biaya:

| Issue | Cara ditangani |
|---|---|
| [#33](../../issues/33) memory: jenis atau scope | **keduanya** — `kind` untuk pengambilan, `scope` untuk izin |
| [#32](../../issues/32) tiga skala skor | simpan **0–1** + `scoring_version` + `score_breakdown` |
| [#2](../../issues/2) lima model angka pengguna | `human_states.metrics jsonb`, bukan kolom tetap |
| [#7](../../issues/7) model graf | **tidak menyentuh V0** — Neo4j baru masuk V2 |

> ⚠️ Menunda bukan menjawab. Selama #2 belum dipilih, tidak ada yang bisa
> **menghitung** angkanya — tabelnya hanya siap menampungnya.

---

## ⭐ MVP sudah ada namanya: V0 — HumanVerse Foundation

Untuk pertama kalinya dalam empat naskah, ada **daftar tertutup** yang bisa
dikerjakan. Target pemilik: **4–6 minggu**.

```
Authentication · Profile · Goals · Habits · Daily Check-in
Mood · Journal · AI Coach · Basic Memory · Dashboard

Agent:  Orchestrator · HabitAgent · CoachAgent · MemoryAgent
```

Selengkapnya: [`docs/75-URUTAN-PEMBANGUNAN-V0-V6.md`](docs/75-URUTAN-PEMBANGUNAN-V0-V6.md)

---

## Dua puluh empat naskah

```
  NASKAH 1   HumanOS — visi & 12 modul manusia          berkas 01–07
     │
  NASKAH 2   HumanVerse X — arsitektur eksekusi         berkas 10–22
     │       monorepo · 3 lapis agen · roadmap V0–V5
     │
  NASKAH 3   Phase 2 Enterprise Multi-Agent Platform    berkas 30–46
     │       Layer 6–20 · AgentOS · SDK · Marketplace
     │       160 dokumen engineering
     │
  NASKAH 4   Phase 3 AI-Native Human Ecosystem          berkas 50–77
     │       58 bagian · V0–V6 · HumanVerse Economy
     │       "arsitektur boleh besar, implementasinya bertahap"
     │
  NASKAH 5   Blueprint Engineering v1.0                 berkas 80–97
     │       34 bagian · monorepo final · 22 agent · 7 sprint V0
     │       "berhenti menambah visi/fitur"
     │
  NASKAH 6   Peta 14 lapisan engineering               berkas 98
     │       Operating Model · "jangan lompat ke fitur baru lagi"
     │       └──► lapisan 04 dikerjakan → spec/
     │
  NASKAH 7   Phase 4 Enterprise Operating System       berkas 100–112
     │       Layer 21–50 · standards · design system · AI Ops
     │
  NASKAH 8   Peta Phase 5–12                            berkas 113
     │       ≈380 dokumen tersisa · taksiran kemajuan 45 %
     │
  NASKAH 9   Phase 5 — HumanVerse Research Lab         berkas 114–122
     │       15 research pillar · BFM · memory compression
     │
  NASKAH 10  Phase 6 — Developer Platform              berkas 123–131
     │       25 layer · OAuth · SDK 7 bahasa · marketplace
     │
  NASKAH 11  Phase 7 — Data & AI Infrastructure        berkas 132–141
     │       event platform · lakehouse · feature store
     │       deletion engine · 18 deliverable (1 "Future")
     │
  NASKAH 12  Phase 8 — AI Safety, Security & Privacy   berkas 142–153
     │       46 bagian · identity · consent · data vault
     │       risk policy R0–R4 · kill switch · privacy center
     │
  NASKAH 13  Phase 9 — Intelligence & Cognitive Arch.  berkas 154–164
     │       41 bagian · memory 6 jenis · decay & konsolidasi
     │       cognitive runtime · POLICY_CHECK
     │
  NASKAH 14  Phase 10 — Multimodal Intelligence        berkas 165–175
     │       persepsi: vision · audio · spatial
     │       peta 15 fase (menggantikan peta naskah 8)
     │
  NASKAH 15  Phase 11 — Agentic Intelligence & Agency  berkas 176–187
     │       64 bagian · Action Gateway · dua tangga R & L
     │       budget · multi-agent · "autonomy must be earned"
     │
  NASKAH 16  Phase 12 — Digital Twin & World Simulation berkas 188–197
     │       31 bagian · assumption engine · learning loop
     │       "Observed ≠ Certain"
     │
  NASKAH 17  Phase 13 — HumanOS, Personal AI OS        berkas 198–206
     │       40 bagian · Attention OS · Approval Center
     │       state machine · app/agent/plugin
     │
  NASKAH 18  Phase 14 — Autonomous Intelligence &      berkas 207–218
     │       Collective Agent Ecosystem
     │       69 bagian (terpanjang) · federasi · agent team
     │       governance mesh · agent economy · L5 + autonomy contract
     │       "More agents must not automatically mean more autonomy"
     │
  NASKAH 19  Phase 15 — Spatial Intelligence &         berkas 219–227
     │       XR Universe
     │       32 bagian · SpatialOS · SLAM · scene graph
     │       spatial memory · AetherScan · XR · gesture/eye tracking
     │       "The world becomes an interface."
     │       ⚠️ mengumumkan Phase 16 → peta 15 fase patah (#101)
     │
  NASKAH 20  Phase 16 — Robotics & Embodied            berkas 228–235
             Intelligence
             35 bagian · HRP · SLAM/ROS2 · motion planning
             manipulasi · smart home/IoT · drone · fleet
             safety kernel · safe zones · simulation-first
             "Intelligence becomes embodied." — satu AI, banyak tubuh
             ⚠️ mengumumkan Phase 17 → peta terbuka-ujung (#108)
     │
  NASKAH 21  Phase 17 — Human Health & Bio             berkas 236–245
             Intelligence
             56 bagian · Health Digital Twin · Health Vault
             tidur/recovery · nutrisi · stress · anomali & forecast
             rekam medis · federasi · model registry · bias engine
             ⭐ Health Safety Kernel — rantai pertama dengan Risk
                DAN Evidence Check; metrik evaluasi model PERTAMA
             "HumanVerse tidak boleh menjadi AI dokter yang serba tahu."
             🛑 Safety & Governance di LUAR MVP ([#116](../../issues/116))
     │
  NASKAH 22  Phase 18 — Global Intelligence Network    berkas 246–255
             34 bagian · World Model · World Knowledge Graph
             HINP · federasi knowledge/agent · collective intelligence
             trust vector · provenance · global risk · early warning
             organization & city intelligence · marketplace
             ⭐⭐ `UNRESOLVED` sebagai KELUARAN yang sah (§18.23) —
                pertama kalinya sistem boleh berhenti tanpa jawaban
             "HumanVerse tidak mengontrol dunia."
             🛑 Safety Kernel §18.22 TANPA milestone ([#121](../../issues/121))
             🛑 `productivity` atas `People` = larangan §8.10 ([#122](../../issues/122))
             ⚠️ mengumumkan Phase 19 → perpanjangan KEEMPAT (#101)
     │
  NASKAH 23  Phase 19 — Scientific Discovery           berkas 256–265
             Engine (SDE)
             34 bagian · Research Knowledge Graph · evidence ranking
             gap detection · hypothesis · experiment planner
             Monte Carlo · reproducibility · writing & peer review
             ethics & safety · model registry · lab automation
             ⭐⭐ §19.17 `Remaining Disagreement` MENUTUP separuh
                [#121](../../issues/121) — usul satu naskah lalu, dipakai
             ⭐⭐ *“sitasi harus nyata, tidak boleh mengarang referensi”*
             "From consuming knowledge to creating knowledge."
             🛑 Ethics & Safety milestone TERAKHIR, di fase yang menamai
                Biosecurity & menggerakkan materi fisik ([#131](../../issues/131))
             🛑 “roadmap 20 fase” yang dirujuknya tidak pernah ada ([#132](../../issues/132))
             ⭐ mengumumkan Phase 20 sebagai fase TERAKHIR — ujung pertama
                yang dinyatakan sejak §10.41 ([#133](../../issues/133))
     │
  NASKAH 24  Phase 20 — Civilization Platform          berkas 266–275
             39 bagian · Civilization KG/State/Twin · simulasi & skenario
             collective intelligence · distributed AI · privasi & kedaulatan
             identity · governance · impact · resilience · crisis
             resource · sustainability · CivilizationOS · marketplace
             ⭐⭐ **AGENT CONSTITUTION** — sepuluh pasal; tiga menutup
                butir lama (Reversibility/H-21 · No unauthorized
                autonomy · Human override/H-15), dan **konstitusi
                tidak punya nomor urut**
             ⭐⭐ **§20.35 memisahkan ANALYSIS dari ACTION** — gerbang
                yang dicari lima naskah, akhirnya digambar
             "Human sovereignty over machine autonomy."
             🛑 lima jalur di naskah yang sama tak melewatinya ([#140](../../issues/140))
             🛑 peta 20 fase cuma 12 baris; Phase 1–8 nihil ([#142](../../issues/142))
             ⭐⭐⭐ **USUL: jangan buat Phase 21 — buat MASTER
                ARCHITECTURE v2.0** ([#139](../../issues/139))
```

> ℹ️ Penomoran berkas melewati 99. `99-CATATAN-AUDIT.md` tetap di tempatnya
> sebagai berkas audit; naskah 7 memakai `100`–`112`.
>
> ℹ️ **Peta dokumen di bawah baru mencakup naskah 1–11.** Untuk naskah 12–18
> (`142`–`235`), daftar berkas per naskah ada di
> [`docs/SESSION-LOG.md`](docs/SESSION-LOG.md) — satu entri per sesi.

---

## Aturan berkas dokumen

1. Berkas `01`–`275` merekam **kata pemilik apa adanya**. Susunannya dirapikan,
   isinya tidak ditambah-tambahi. Bagian yang hilang di naskah **ditandai
   sebagai hilang**, bukan ditambal.
2. Setiap keraguan, koreksi, risiko, atau usulan dari pihak lain (termasuk AI)
   masuk ke `99-CATATAN-AUDIT.md` — **tidak pernah disisipkan** ke berkas visi.
3. Kalau pemilik memutuskan sesuatu, keputusan itu **naik** ke berkas visi yang
   sesuai, lalu butirnya turun ke bagian **H** di berkas audit.
4. Tujuh berkas **bukan** rekaman naskah:
   [`00-DAFTAR-ISI.md`](docs/00-DAFTAR-ISI.md) (dibangun dari isi direktori),
   [`99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md),
   [`GERBANG-SKEMA.md`](docs/GERBANG-SKEMA.md),
   [`SENSUS-MODUL.md`](docs/SENSUS-MODUL.md),
   [`SENSUS-EVENT.md`](docs/SENSUS-EVENT.md),
   [`SENSUS-AGENT.md`](docs/SENSUS-AGENT.md),
   [`SENSUS-TABEL.md`](docs/SENSUS-TABEL.md),
   [`SENSUS-TANGGA.md`](docs/SENSUS-TANGGA.md),
   [`SENSUS-RANTAI.md`](docs/SENSUS-RANTAI.md) dan
   [`PETA-FASE.md`](docs/PETA-FASE.md) (ketujuhnya pengukuran — tidak
   memutuskan apa pun),
   [`KEPUTUSAN-DIDELEGASIKAN.md`](docs/KEPUTUSAN-DIDELEGASIKAN.md) (keputusan
   yang saya ambil sendiri, tiap butir bisa dibatalkan), dan
   [`SESSION-LOG.md`](docs/SESSION-LOG.md).

---

## Peta dokumen

> 📚 **Daftar lengkap ada di [`docs/00-DAFTAR-ISI.md`](docs/00-DAFTAR-ISI.md)** —
> **263 berkas**, berurutan, dikelompokkan per naskah, masing-masing dengan
> keterangan isi dan jumlah barisnya.

Bagian ini dulu memuat daftar berkas, tetapi berhenti dipelihara di berkas
`141` (naskah 11) — ia hanya mencakup **126 dari 263** berkas. Daftar induk
menggantikannya, dan dibangun ulang dari isi direktori sehingga tidak bisa
tertinggal lagi.

| Yang dijamin daftar induk | |
|---|---|
| Tiap berkas `docs/` muncul **tepat satu kali** | ✅ 263 = 263 |
| Nomor ganda | ✅ nihil |
| Berkas terdaftar tapi tidak ada | ✅ nihil |
| Berkas ada tapi tidak terdaftar | ✅ nihil |
| Nomor tak terpakai (`8–9`, `23–29`, `47–49`, `78–79`) | ✅ semuanya di batas antar-naskah, dijelaskan di Lampiran A |

### Aturan penomoran

- `01`–`99` dua digit, `100`–`275` tiga digit. Urutan abjad sebuah `ls`
  **tidak** sama dengan urutan nomor (`10`, `100`, `101`, `11`, `99`) — pakai
  daftar induk untuk urutan yang benar.
- Nama berkas **sengaja tidak dinomori ulang**: 34 GitHub Issue yang sudah
  terbit menaut berkas dua digit, dan penomoran ulang akan mematahkan tautan
  di isi issue tersebut.
- Tiap blok naskah menempati rentangnya sendiri, dengan celah di antaranya.

## Arsitektur sekilas

```
   ┌────────────────────────────────────────────────────────┐
   │  LAYER 1 · Supreme Orchestrator                        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 2 · Planner · Memory · Reasoning · Guardrail     │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 3 · Health · Habit · Fashion · Trend · Career    │
   │            Finance · Learning · Social                  │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 6 · AgentOS                                      │
   │  Registry · Scheduler · Queue · Workflow · Tools        │
   │  Memory Manager · Event Bus · Policy Engine            │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 7–9 · Ontology · Knowledge Graph · Memory        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 10–14 · Tools · Workflow · Decision · PromptOps  │
   │                Evaluation                               │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 17–20 · Trend · Marketplace · SDK · Simulation   │
   └────────────────────────────────────────────────────────┘
```

Naskah 4 menyusunnya ulang dari sudut lain:

```
                     HUMANVERSE XOS
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    HUMAN CORE        AI RUNTIME        DATA CORE
        │                 │                 │
    Behavior          Orchestrator      PostgreSQL
    Goals             Agents            Vector DB
    Memory            Tools             Graph
    Context           Evaluation        Analytics
```

---

## 12 Modul manusia (naskah 1) vs 14 Agent (naskah 4)

```
NASKAH 1 — 12 modul               NASKAH 4 — Agent Registry §12
 1. Habit Intelligence            Health · Habit · Fashion · Grooming
 2. Lifestyle Intelligence        Fitness · Nutrition · Learning · Career
 3. Fashion AI                    Finance · Social · Travel · Productivity
 4. Grooming AI                   Entertainment · Research
 5. Fitness Intelligence
 6. Nutrition Intelligence        Baru      : Travel, Entertainment, Research
 7. Mental Wellness               Kembali   : Grooming, Nutrition, Productivity
 8. Productivity Intelligence     Masih nol : Mental Wellness, Lifestyle
 9. Learning Intelligence
10. Career Intelligence
11. Social Intelligence
12. Finance Behavior
```

> ⚠️ **Mental Wellness dan Lifestyle masih belum punya agent** di tiga naskah
> berturut-turut — dan *Journal* justru masuk V0. Lihat butir **A-20** dan
> **C-3**.

---

## Tumpukan teknologi

| Lapisan | Teknologi |
|---|---|
| Aplikasi | Flutter (mobile & web) · desktop & admin-dashboard **belum ditetapkan** |
| Backend | **Python + FastAPI** (🔧 K-13) · V0 modular monolith, 12 modul |
| AgentOS | Registry · Scheduler · Task Queue · Workflow · Tool Registry · Memory Manager · Event Bus · Policy Engine |
| AI | LangGraph · MCP · Tool Calling · **Model Router** (small/medium/large) |
| Data | **PostgreSQL · Qdrant · Neo4j · Redis** — naskah 5 membuang ClickHouse & Kafka; deret waktu lewat **TimescaleDB** (ekstensi, bukan penyimpanan kelima) |
| Event | Event Bus; antrean di **Redis** (Kafka baru bila skalanya menuntut) |
| Infra | **D0 Docker Compose** → D1 Cloud VM → D2 Postgres terkelola → D3 worker → D4 Kubernetes → D5 tepi+cloud — tiap langkah punya **pemicu terukur** ([`arch/09`](arch/09-DEPLOYMENT-TOPOLOGY.md)) |
| Observability | OpenTelemetry · Prometheus · Grafana · Loki · Tempo · Sentry · **Agent Health** |
| Keamanan | OAuth · RBAC · Vault · AES-256 · TLS · Immutable Log · Permission Engine · Risk Engine |
| Privasi | Privacy Center · Personal Data Vault · On-device AI (V5) · Federated ML (V5) |
| SDK | Python · TypeScript · Flutter · Kotlin · Swift — **ditunda ke V6** |

---

## Tangga versi (naskah 4)

```
  V0  Foundation            ── auth, profile, goals, habits, mood, journal,
   │                           AI coach, memory, dashboard · 4–6 minggu
  V1  Behavior Intelligence ── event, analytics, pattern, prediksi, weekly review
   │
  V2  Lifestyle AI          ── fashion, wardrobe, trend, grooming, fitness, nutrisi
   │
  V3  Multi-Agent Platform  ── registry, SDK, MCP, tool registry, evaluation
   │
  V4  Digital Twin          ── human state, model perilaku, simulasi, decision lab
   │
  V5  HumanOS               ── voice, vision, wearable, on-device AI, privasi lanjut
   │
  V6  HumanVerse Ecosystem  ── developer SDK, marketplace, enterprise API
```

---

## Prinsip penutup pemilik

> **Jangan membuat HumanVerse menjadi mesin yang menilai apakah seseorang
> "manusia yang baik" atau "manusia yang buruk".**
>
> ## Manusia tetap menjadi pusat sistem.
