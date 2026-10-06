# 07 — Backlog V0 untuk AI coding agent

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Tujuh sprint naskah 5 §32 dipecah jadi tugas yang bisa diberikan **satu per
> satu**. Setiap tugas: **satu commit** (PR boleh satu per sprint — **K-18**),
> punya definisi selesai yang bisa diuji mesin.

**Aturan untuk setiap tugas** — dari naskah 5 §27 (*governance tetap manusia*):

```
Coding Agent → Implementation → Unit Test → Integration Test
→ Security Scan → AI Review → HUMAN REVIEW → Merge
```

Tidak ada tugas yang boleh masuk `main` tanpa baris **HUMAN REVIEW**.

---

## Sprint 0 — Foundation

| # | Tugas | Selesai bila |
|---|---|---|
| 0.1 | Monorepo + workspace sesuai [`../docs/83`](../docs/83-STRUKTUR-REPO-FINAL.md) | `apps/`, `services/`, `packages/`, `tests/`, `infrastructure/`, `docs/` ada; `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md` terisi |
| 0.2 | `docker-compose.yml`: PostgreSQL 16 + Redis 7 | `docker compose up` → keduanya sehat, port terdokumentasi |
| 0.3 | Kerangka `apps/api` + `/health` | `GET /health` → 200 `{status, version, db, redis}` |
| 0.4 | Alat migrasi + migrasi 0001 (23 tabel, **tiap tabel membawa `data_subject` + tiga anotasi retensi** — K-16) | migrasi naik & turun bersih; skema cocok dengan [`01`](01-DATABASE-SCHEMA.md); **P-1 · P-2 · P-3** [`../arch/11`](../arch/11-PENEGAKAN.md) hijau |
| 0.5 | Logging terstruktur + `request_id` | tiap baris log punya `request_id`, `user_id?`, `latency_ms` |
| 0.6 | Kerangka uji + cakupan | `pytest` jalan; gerbang cakupan ≥ 70 % |
| 0.7 | CI: lint → typecheck → test → build → scan | PR gagal kalau salah satu merah |
| 0.8 | Batas modul & **enam batas keras** — `import-linter` (aturan 1–4 [`06`](06-MODULE-BOUNDARIES.md) + B-1…B-6 [`../arch/11`](../arch/11-PENEGAKAN.md)) | impor yang melanggar **gagal di CI** |

> **0.8 sebelum kode domain ditulis, bukan sesudah.** Batas modul yang tidak
> ditegakkan mesin akan dilanggar dalam dua minggu.
>
> 🔧 **Backend: Python + FastAPI** (K-13) — lihat
> [`../arch/05`](../arch/05-TECHNOLOGY-STACK.md) §2.
> 🔧 **1.4 kini memuat B-22** ([#59](../../issues/59)): `consents.purpose`
> harus ada **sebelum baris data pertama**. Biayanya nol sekarang; data V0 yang
> dikumpulkan tanpa itu tidak bisa melatih model apa pun di Phase 5.
>
> 🔨 **Sprint 0 dikodekan 16 Sep 2026** — branch `v0/sprint-0-foundation`, satu
> commit per tugas, **menunggu HUMAN REVIEW**. Keadaan tiap "Selesai bila",
> tanpa dibulatkan:
>
> | | Dibuktikan | Yang BELUM |
> |---|---|---|
> | 0.1–0.6 | mesin — `tools/ci_lokal.py` tahap lint · typecheck · test · build | — |
> | 0.5 | tiap baris log punya `request_id` & `user_id`; **`latency_ms` di baris penutup permintaan** (baris lain belum punya latensi untuk dilaporkan) | tafsiran itu dinyatakan di `platform/log.py`, bukan diubah di baris tugasnya |
> | 0.7 | `ci_lokal.py` kelima tahap hijau **di mesin lokal**, dan merah-hijaunya **terlihat di PR** sebagai status `ci-lokal` (`--lapor-github`) — gratis, **H-26** | 🛑 PR merah **tidak terhalang digabung**: perlindungan branch tidak tersedia untuk repo privat pada paket akun ini. Gerbangnya HUMAN REVIEW (H-25). Actions dimatikan dengan sengaja ([#160](../../issues/160)) |
> | 0.8 | batas modul `spec/06` aturan 1–4 + **B-2** kontrak `import-linter`, **B-6** pohon repo — semuanya terbukti sanggup gagal | **B-1 · B-3 · B-4 · B-5** belum bisa dinyatakan di V0; pemicunya di blok `penegak` [`../arch/11`](../arch/11-PENEGAKAN.md) §6 |
>
> Dua hal yang menulis migrasinya temukan di [`01`](01-DATABASE-SCHEMA.md):
> 11 tabel ber-`updated_at` **tanpa satu pemicu pun** (E-161), dan catatan
> markdown **di dalam** blok SQL tabel `agents` (G-24) — keduanya kini
> dibetulkan dan dijaga uji.

---

## Sprint 1 — Identity

| # | Tugas | Selesai bila |
|---|---|---|
| 1.1 | Modul `identity`: register, login, refresh, logout | argon2id; refresh token berotasi; uji integrasi hijau |
| 1.2 | Sesi di Redis + middleware auth | token dicabut → 401 seketika |
| 1.3 | `profiles` + `GET /me`, `PATCH /me/profile` | timezone IANA divalidasi |
| 1.4 | `consents`: catat persetujuan saat daftar, **termasuk `purpose` + `kind='model_training'`** | riwayat append-only; pencabutan = baris baru; uji: `data.purpose ⊆ consent.purpose` ditegakkan |
| 1.5 | Permission engine: `check(user, subject, scope, action)` | default `ask`; hasil di-cache di Redis; uji untuk allow/deny/ask/expired |
| 1.6 | `audit_logs` + helper `audit()` | `UPDATE`/`DELETE` ditolak; login, izin, ekspor, hapus tercatat |
| 1.7 | Batas laju per pengguna & per IP | 429 dengan `Retry-After` |

> ✅ **B-40 — ditutup 17 Sep 2026, sebelum 1.5 dan 1.6 ditulis.** Sampai hari
> itu api tersambung sebagai **superuser pemilik tabel**, dan `UPDATE` **dan**
> `DELETE` atas `audit_logs` lolos. Kini api tersambung sebagai anggota
> `hvx_app` — bukan superuser, bukan pemilik, tanpa `BYPASSRLS` — dan **menolak
> mulai** kalau tidak; `audit_logs` dan `events` hanya-tambah bagi peran itu
> ([`01`](01-DATABASE-SCHEMA.md) §10).
>
> 🔑 **Untuk 1.1–1.7, tiga hal yang kini mengikat** (RLS §11, **H-27**):
> **(1)** tiap kueri di dalam `platform.transaksi_pengguna(engine, user_id)` —
> di luarnya RLS memulangkan nol baris; **(2)** login butuh **fungsi
> `SECURITY DEFINER` yang sempit** untuk mencari akun per email, sebab RLS di
> `users` tidak meloloskan pencarian sebelum pengguna dikenali — jangan
> melonggarkan kebijakannya; **(3)** uji 1.6 *“`UPDATE`/`DELETE` ditolak”*
> tersambung sebagai peran aplikasi (`basis_data_termigrasi` di
> `tests/integration/conftest.py`), bukan sebagai pemilik.
>
> 🔨 **Sprint 1 dikodekan 17 Sep 2026** — branch `v0/sprint-1-identity` (di atas
> `v0/sprint-0-foundation`), satu commit per tugas (**K-18**) — 1.1 dan 1.3 dengan commit susulan (daftar tolak & NFKC · uji sidik IP · SQL statis), lalu satu commit untuk seluruh perbaikan tinjauan, **menunggu HUMAN REVIEW**.
> Keadaan tiap "Selesai bila", tanpa dibulatkan:
>
> | | Dibuktikan | Yang BELUM |
> |---|---|---|
> | 1.1 | argon2id **di thread**; hash berparameter lama diperbarui saat masuk; token segar berotasi (`GETDEL`) dan token bekas **mencabut seluruh sesi**; sandi 15–128 karakter + **daftar tolak** tanpa aturan komposisi + NFKC di kedua sisi (NIST SP 800-63B-4); email tak terdaftar: satu verifikasi argon2 dan kueri yang sama banyak; pendengar pendaftaran yang gagal menggagalkan seluruh pendaftaran; NUL di teks bebas → 400; uji integrasi lewat HTTP sebagai peran aplikasi | — |
> | 1.2 | token dicabut → 401 pada permintaan berikutnya — **juga bila keluar atau token bekas jatuh di tengah penyegaran, dan bila masuk baru jatuh di tengah cabut-semua** (tiap celah antarperintah diuji); umur token akses & segar diukur; status akun dibaca sebelum tiap penyegaran, tidak aktif → semua sesi dicabut; Redis hanya menyimpan **sidik** token | token akses akun yang ditangguhkan hidup sampai kedaluwarsa — alur yang mengubah status wajib `cabut_semua` (6.5) |
> | 1.3 | timezone dari paket `tzdata`, peka huruf: `asia/jakarta` · `WIB` · `GMT+7` → 400 | — |
> | 1.4 | riwayat hanya-tambah (peran aplikasi tanpa `UPDATE`/`DELETE`), urutannya tentu di dalam satu transaksi; pencabutan = baris baru; `data.purpose ⊆ consent.purpose` **dan** cakupan data — per **jenis** persetujuan | kosakata `purpose` & teks kebijakan — pemilik ([#59](../../issues/59) butir 2); persetujuan `service` dicatat tanpa cakupan, jadi pertanyaan `service` bercakupan selalu ditolak sampai kosakata itu ada |
> | 1.5 | tanpa baris → `ask` (atau bawaan pemanggil — E-167); `allow` · `deny`; kedaluwarsa → `ask`; di-cache Redis paling lama sampai `expires_at` − 1 dtk, **mutlak** menurut jam basis data (**E-189**), dan **pencabutan berlaku seketika** — juga terhadap pembaca yang sedang membaca | `condition.consent` naskah 12 §8.7 — pemilik (#59 butir 3); rute `PUT /privacy/permissions` datang bersama layar 6.4 |
> | 1.6 | `UPDATE`/`DELETE` ditolak (SQLSTATE 42501, sebagai peran aplikasi); **login ✅ · izin ✅** tercatat — dan audit yang gagal menggagalkan perubahannya | **ekspor · hapus** belum tercatat — fiturnya belum ada (6.4 · 6.5) |
> | 1.7 | `429` + `Retry-After` per IP (`/v1/*`, IPv6 per /64) · per pengguna · daftar & masuk per IP · login gagal per akun — dipakai sebelum argon2, kunci = pembanding `citext` | angka batasnya keputusan teknis (**K-22**), belum diukur terhadap lalu lintas nyata; per IP bergantung proksi tepercaya di D1+; batas per akun **bukan** batas 100 *beruntun* NIST (**B-42**) |
>
> Dua hal yang menulisnya temukan di [`04`](04-API-CONTRACTS.md): badan
> `register` **tanpa tempat untuk persetujuan** yang dituntut 1.4 (E-164), dan
> `PUT /privacy/permissions` yang **tidak bisa menunjuk satu baris** izin
> (E-163) — keduanya kini dibetulkan.
>
> 🔍 **Tinjauan adversarial sebelum PR** (dua lensa, rinciannya
> [`../docs/99-CATATAN-AUDIT.md`](../docs/99-CATATAN-AUDIT.md)): tiap temuan kode
> dibuktikan **merah dulu**, tiap celah penegak dibuktikan dengan mutasi. Tiga
> ketidakcocokan antar-`spec` lagi — **E-165** `Idempotency-Key` di rute yang
> mengeluarkan token ([`04`](04-API-CONTRACTS.md)) · **E-166** aturan 6
> [`06`](06-MODULE-BOUNDARIES.md) dilanggar `profiles` · **E-167** bawaan risiko
> [`05`](05-AGENT-CONTRACTS.md) yang tak bisa dijawab mesin izin — dibetulkan. Rute
> `DELETE /me` · `POST /me/restore` di [`04`](04-API-CONTRACTS.md) kini ditandai
> datang bersama 6.5.

---

## Sprint 2 — Human Core

| # | Tugas | Selesai bila |
|---|---|---|
| 2.1 | Modul `goals` + milestone + `parent_id` | pohon goal 3 tingkat terbaca dalam satu query |
| 2.2 | Modul `habits` + jadwal + `adaptive_tiers` | uji: tier turun saat energi rendah |
| 2.3 | `habit_completions` + idempotensi tanggal | kirim ulang `for_date` sama → 200, bukan baris kedua |
| 2.4 | Rentetan & tingkat penyelesaian | benar melintasi zona waktu; uji pengguna yang pindah negara |
| 2.5 | `daily_checkins` (upsert per tanggal) | `PUT` dua kali → satu baris |
| 2.6 | `mood_entries` | — |
| 2.7 | Layar V0 pertama: daftar habit + tandai selesai | bisa dipakai manusia, bukan hanya curl |

> **2.7 disengaja ada di Sprint 2, bukan Sprint 6.** Kalau layar pertama baru
> muncul di sprint terakhir, tidak ada yang tahu apakah yang dibangun enak
> dipakai sampai waktunya habis.
>
> ✅ **B-41 — dibetulkan 17 Sep 2026, sebelum 2.1 ditulis.** Sebelas FK satu
> kolom di [`01`](01-DATABASE-SCHEMA.md) semula membiarkan baris anak milik
> pengguna B menunjuk induk milik A — diukur: milestone B menempel ke goal A,
> lalu **ikut terhapus** saat A menghapus goal-nya. Pemilik: *“data milik satu
> pengguna harus milik pengguna tersebut”* (**H-27**). Kini tiap relasi
> pasangan `(induk_id, user_id) → induk(id, user_id)` — basis data sendiri yang
> menolak — dijaga `tests/integration/test_kepemilikan_data.py` di katalog dan
> di ke-11 relasinya.
>
> 🔨 **Sprint 2 dikodekan 24 Sep 2026** — branch `v0/sprint-2-human-core` (di
> atas `v0/sprint-1-identity`), satu commit per tugas (**K-18**), lalu satu
> commit untuk seluruh perbaikan tinjauan, **menunggu HUMAN REVIEW**. Keadaan
> tiap "Selesai bila", tanpa dibulatkan:
>
> | | Dibuktikan | Yang BELUM |
> |---|---|---|
> | 2.1 | pohon 3 tingkat = **satu** pernyataan SQL yang sampai ke PostgreSQL (dihitung di driver, `test_goals.py`); kedalaman ≤ 10 ditegakkan saat menulis; `parent_id == id` ditolak skema **dan** `CHECK` (migrasi 0004); hapus-lunak menaikkan anak menjadi akar — juga anak yang dibuat **serentak** dengan hapus induknya (tinjauan: 40 dari 40 yatim, kini nol); ≤ 1.000 goal · ≤ 100 milestone per goal, serial (**K-24**) | — |
> | 2.2 | tier turun saat energi rendah — murni (`test_tier.py`) **dan** lewat HTTP dari check-in sungguhan (`test_habit_hari_ini.py`); `period` × `target_count` × `schedule` diperiksa terhadap baris tersimpan; habit hanya menaut goal yang **hidup**, dan hapus goal melepasnya (E-172) | angka pemetaan energi → tier keputusan teknis (**K-23**), belum diukur terhadap pengguna |
> | 2.3 | kirim ulang tanggal sama → `200` + baris lama, **sebelum** aturan lain diperiksa ulang (E-173); enam catatan serentak → satu baris, tanpa galat; `for_date` ditolak hanya bila belum terjadi di mana pun di Bumi | event penyelesaian — tugas 3.2 |
> | 2.4 | rentetan dari `for_date`, *“hari ini”* menurut zona profil saat ini dari jam basis data; **pengguna yang pindah** Pago Pago (UTC−11) → Kiritimati (UTC+14) diuji lewat HTTP; `skipped` netral per kejadian, juga mingguan; hari sebelum habit ada tidak menjadi gagal (E-173) | penyeberangan garis tanggal ke timur melompati satu tanggal (tercatat di `spec/04`); masa `paused` dihitung seperti hari biasa — riwayat jeda tidak disimpan |
> | 2.5 | `PUT` dua kali → satu baris, juga serentak; `PUT` identik tidak menulis ulang (`updated_at` tetap, E-176); `sleep_hours` angka JSON | event `checkin.logged` — tugas 3.2 |
> | 2.6 | — (tanpa kalimat *Selesai bila*); kontrak `spec/04` diuji: id buatan klien, halaman berkursor keyset, waktu wajib berzona, `from` inklusif / `to` eksklusif | event `mood.logged` — tugas 3.2 |
> | 2.7 | **layar yang dirakit `main.dart` diketuk terhadap api hidup** — daftar, tambah habit, tandai selesai, keluar — dan hasilnya diperiksa dari sesi lain di server (`apps/mobile/test/ujung/`, tahap smoke `tools/ci_lokal.py`); 39 uji widget dan klien (`TZ=WIB-7` di gerbang — uji tanggal lokal tidak bermakna di mesin UTC); alur klien ujung-ke-ujung terhadap citra CI, termasuk token lama yang **ditolak server** sesudah keluar | belum pernah dipakai orang selain pengujinya — *enak dipakai* belum diukur; layar hanya mencatat `done` (belum `skipped`/`partial`); penyimpanan token dan antrean luring datang bersama 6.6 |
>
> Dua rute yang tugas-tugas ini tuntut tidak ada di [`04`](04-API-CONTRACTS.md)
> sampai kodenya harus memanggilnya — **E-168** `GET /goals/{id}/tree` ·
> **E-169** `GET /habits?for_date=` — kini ditambahkan.
>
> 🔍 **Tinjauan adversarial sebelum PR** (keamanan · kontrak · penegak buta;
> rinciannya [`../docs/99-CATATAN-AUDIT.md`](../docs/99-CATATAN-AUDIT.md)): 28
> temuan terbukti dan **39 kerusakan yang lolos seluruh suite**, tiap temuan
> kode dibuktikan **merah dulu** lalu dijaga mutasi —
> **E-170** masukan yang dikoersi diam-diam (`true` menjadi valensi mood;
> detik Unix menjadi `for_date` UTC; persetujuan dari `"on"`) · **E-171**
> `Idempotency-Key` yang menyimpan isi jawaban 24 jam (kini rujukan + kuota,
> **K-24**) · **E-172** balapan hapus/tulis dan batas ukuran · **E-173** arti
> rentetan · **E-174** galat yang memantulkan masukan · **E-175** klien
> Flutter · **E-176** dokumen yang tertinggal. Aturan 6
> [`06`](06-MODULE-BOUNDARIES.md) **dilanggar dengan sengaja** sampai 3.2: enam
> tabel ber-event ditulis sebelum tabel `events` ada. Dan satu cacat Sprint 1
> yang ketahuan lewat uji yang berkedip: batas laju menolak permintaan di
> ujung ledakan saat jam Redis melangkah mundur ±1 dtk — kini jam per kunci
> tidak mundur (langkah ≤ 2 dtk diserap).

---

## Sprint 3 — Memory & event

| # | Tugas | Selesai bila |
|---|---|---|
| 3.1 | Modul `events` + envelope + idempotency | event ganda ditelan sebagai sukses |
| 3.2 | Penerbitan event dari `habits`, `checkins`, `goals` | aturan 6 [`06`](06-MODULE-BOUNDARIES.md): tiap tulisan menerbitkan event |
| 3.3 | Redis Streams + consumer group + retry | consumer mati → event tidak hilang saat hidup lagi |
| 3.4 | Modul `journal` (daftar tanpa `body`) | `GET /journal` tidak pernah mengembalikan `body` |
| 3.5 | Qdrant + koleksi `memories` | — |
| 3.6 | Ekstraksi memori dari jurnal & mood | tiap memori punya `kind`, `scope`, `confidence`, `evidence_count`, `source_event_id` |
| 3.7 | Pencarian memori (semantik + saring scope) | agent tanpa izin scope **tidak** menerima barisnya |
| 3.8 | `activities` | `source='inferred'` terpisah dari `manual` |

> 🔨 **Sprint 3 dikodekan 24 Sep 2026** — branch `v0/sprint-3-memory-event` (di
> atas `v0/sprint-2-human-core`), satu commit per tugas (**K-18**), lalu satu
> commit untuk seluruh perbaikan tinjauan, **menunggu HUMAN REVIEW**. Keadaan
> tiap "Selesai bila", tanpa dibulatkan:
>
> | | Dibuktikan | Yang BELUM |
> |---|---|---|
> | 3.1 | kunci yang sama dua kali → satu baris, galatnya ditelan sebagai sukses — juga serentak; kunci sama untuk kejadian **lain** — payload, subjek, atau jenis lain — ditolak keras; uji admisi saat terbit menolak jenis di luar tabel padanan, medan payload tak dikenal **atau bertipe lain** (`strict`, **E-187**), sumber di luar `spec/03`, waktu tanpa zona — sebelum menyentuh basis data; `recorded_at` = saat event masuk, bukan awal transaksinya; event ikut batal bersama tulisannya | — |
> | 3.2 | tiap baris peta aturan 6 [`06`](06-MODULE-BOUNDARIES.md) lewat HTTP, di transaksi yang sama (galat penerbitan membatalkan tulisannya); kirim ulang tidak menerbitkan apa pun; kunci per **kejadian** (**E-177**); pembatalan penyelesaian punya eventnya (**E-178**) | aturan 6 dipersempit ke fakta perilaku (**E-179**) — event konfigurasi belum ada |
> | 3.3 | konsumen yang mati sebelum ACK → pesannya diklaim konsumen lain dan diproses (`XAUTOCLAIM`); penangan yang selalu gagal → stream **mati** sesudah 5 kali — bawaan yang pekerja pakai, bukan angka uji; event yang commit **di belakang** kursor relay tetap terkirim (jendela 60 dtk), dan riwayat tidak terkirim ulang: penanda dipangkas menurut kursor (**E-185**); event akun yang dihapus di antara relay dan konsumen selesai tanpa stream mati; stream membawa **rujukan**, isi dibaca di bawah RLS (**K-25**); pangkas tidak membuang yang masih ditunggu, dan pekerja sungguh memangkas; stream mati 7 hari; fungsi relay hanya untuk peran `hvx_pekerja` — api menolak mulai sebagai anggotanya (**E-186**); proses `hvx.pekerja` diuji sebagai proses | transaksi yang commit > 60 dtk sesudah menyisip tidak terkirim; stream mati belum punya alat putar ulang |
> | 3.4 | `GET /journal` tanpa `body` di tiga lapis — jawaban tiap halaman, kontrak OpenAPI, dan **SQL yang sampai ke PostgreSQL** (**E-181**); isi jurnal tidak masuk event | hapus jurnal = hapus-lunak, isinya tersimpan sampai akun dihapus — **C-31**, milik pemilik |
> | 3.5 | saringan `user_id` **wajib** di tiap pencarian vektor (Qdrant tanpa RLS); scope kosong ≠ semua; galat Qdrant tanpa isi permintaan; koleksi berdimensi atau berjarak lain ditolak; penyemat lokal **berkunci per pengguna** (**K-26**, **E-182**) — kata tidak terbaca dari vektor tanpa kunci, juga oleh akun yang menyemat kamusnya sendiri; penyelaras menyemat di thread, paling banyak 20.000 karakter pertama, tanpa menahan kunci baris selama Qdrant — `PATCH /journal` tidak menunggu Qdrant yang lambat (**E-183**); menyemat ulang isi yang berubah, dan membuang titik memori yang dihapus | kemiripan **leksikal**, bukan makna; enkripsi sematan (naskah 145) milik pemilik |
> | 3.6 | dua mood + satu jurnal → tiga memori, **tiap** memori punya `kind` · `scope` · `confidence` · `evidence_count` · `source_event_id` yang menunjuk event sumbernya; isi dibaca dari barisnya (bukan dari event); event yang diserahkan lagi tidak menggandakan; jurnal dihapus sebelum diekstrak tidak diingat; `PATCH` serentak menunggu ekstraksi yang sedang membaca (**K-27**) | memori **turunan** (fakta, preferensi) — butuh model (4.1) |
> | 3.7 | agent **tanpa izin scope tidak menerima barisnya** — tiga jalan: scope sensitif tanpa `allow` tersimpan · scope yang pengguna **tolak** (dan tidak dilaporkan *perlu izin*) · izin pengguna yang **tidak** melebarkan manifest; dan buktinya: dengan manifest **dan** izin, baris yang sama diserahkan. Payload **dan vektor** Qdrant yang basi kalah oleh baris PostgreSQL — kata yang dihapus pemiliknya tidak cocok lagi (**E-184**); memori terhapus atau kedaluwarsa tidak diserahkan dan tidak menyingkirkan hasil yang sah; hasil dibatasi `batas`, terurut dari yang paling mirip; daftar scope resmi ditulis dan ditegakkan (**E-180**) | pemanggilnya (tool `memory.search`, gerbang risiko) — Sprint 4 |
> | 3.8 | klien **tidak bisa** mencatat `inferred` (badan dengan `source` → `400`); jalur sistem selalu `inferred`; `?source=` memisahkan keduanya — kontraknya kini di [`04`](04-API-CONTRACTS.md), bersama `ended_at` (masa depan → `422`, membantah `duration_seconds` → `400`) dan batas kedalaman `payload` (**E-187**) | pemanggil `catat_disimpulkan` — Behavior Engine (5.1) |
>
> 🔍 **Tinjauan adversarial sebelum PR** (keamanan · kontrak · penegak buta;
> rinciannya [`../docs/99-CATATAN-AUDIT.md`](../docs/99-CATATAN-AUDIT.md)): 14
> temuan terbukti dan **49 dari 68 kerusakan yang lolos seluruh suite**, tiap
> temuan kode dibuktikan **merah dulu** lalu dijaga mutasi — **E-182** satu
> kunci penyemat untuk semua pengguna (akun biasa membaca vektor orang lain
> dengan kamusnya sendiri) · **E-183** penyelaras yang menahan event loop dan
> kunci baris selama Qdrant · **E-184** pencarian yang memercayai vektor basi ·
> **E-185** penanda relay yang menumpuk 24 jam di Redis `noeviction` · **E-186**
> peran api yang bisa membaca linimasa semua pengguna lewat fungsi pekerja ·
> **E-187** masukan (`jsonb` tanpa batas kedalaman, `ended_at`, admisi event
> yang mengoersi) · **E-188** klaim *“dibuktikan”* tanpa uji. Dan satu cacat
> Sprint 1 yang ketahuan lewat uji yang berkedip di gerbang penuh: cache izin
> sementara yang ditulis > 1 dtk sesudah basis data dibaca menjawab `allow`
> sesudah izinnya habis — kini berakhir **mutlak** (**E-189**). Satu pertanyaan
> baru untuk pemilik — **C-33** teks bebas di payload event — dan dua yang
> diperluas: **C-31** · **C-32**.

---

## Sprint 4 — AI

| # | Tugas | Selesai bila |
|---|---|---|
| 4.1 | AI Gateway + Model Router (simple/reasoning) | "catat mood" **tidak** memanggil model besar |
| 4.2 | Registry agent: muat & validasi manifest | **9 aturan validasi** [`05`](05-AGENT-CONTRACTS.md) ditegakkan; manifest salah **ditolak** |
| 4.3 | Tool registry + 9 tool V0 + **3 entri `kind: agent`** (K-14) | tool di luar registry tidak bisa dipanggil; pemanggilan agent ikut melewati gerbang |
| 4.4 | Agent runtime + `agent_runs` sebagai audit | tiap run mencatat tools, scope, decision, confidence, cost |
| 4.5 | Risk gate + alur konfirmasi | risk 2 minta izin sekali; risk 3 minta setiap kali |
| 4.6 | `orchestrator-agent` | `parent_run_id` membentuk pohon eksekusi |
| 4.7 | `coach-agent` + `habit-agent` + `memory-agent` | tiap balasan membawa `confidence` + `rationale` |
| 4.8 | Percakapan + SSE | token mengalir; `done` memuat `cost_usd` |
| 4.9 | Anggaran biaya per pengguna per hari | melewati batas → turun ke model kecil, bukan gagal |

> **4.9 sering dilupakan sampai tagihan pertama datang.** Batasnya boleh
> longgar; yang penting jalurnya ada sejak awal.

> 🔨 **Sprint 4 dikodekan 24 Sep 2026** — branch `v0/sprint-4-ai` (di atas
> `v0/sprint-3-memory-event`), satu commit per tugas (**K-18**), **menunggu HUMAN
> REVIEW**. Keadaan tiap "Selesai bila", tanpa dibulatkan:
>
> | | Dibuktikan | Yang BELUM |
> |---|---|---|
> | 4.1 | *“catat mood 3”* dirutekan `deterministic` oleh pengenal **aturan** dan dijalankan layanan biasa — jalurnya tidak memegang gerbang model sama sekali; **ujung-ke-ujung lewat percakapan (4.8): penyedia model tidak disentuh**, `done.cost_usd = 0`, tanpa run; `simple`/`reasoning` → model kelasnya dengan token, latensi, dan biaya tiap panggilan; model tanpa harga ditolak saat mulai (**K-28**); 🔧 kata perintah **wajib** — *“mood 3 hari lalu buruk”* bercerita, tidak dicatat (**E-198**); pengenal niat **linear** atas pesan terpanjang yang sah, dibuktikan di proses anak berbatas waktu (**E-197**) | penyedia sungguhan — milik pemilik (A-6/#18); penyedia lokal V0 **tidak menalar** |
> | 4.2 | 9 aturan spec/05 + A-1 + K-14 — satu kasus per aturan, **semua** pelanggaran sekaligus; katalog `agents` dikelola **migrasi** `0007`, api menolak mulai bila berbeda — kini juga aksi tiap tool, migrasi `0009` (**K-29**, **E-209**); letak manifest (**E-190**) dan kolom *Scope* tool (**E-191**); aturan 8 tidak menyembunyikan pelanggaran lain, aturan 6·9 memeriksa scope tool, `capabilities` snake_case (**E-207**) | — |
> | 4.3 | tool di luar registry `tidak_terdaftar`; di luar manifest `bukan_alat_agent`; masukan **ketat** (tanpa koersi, `enum`/`min`/`max` skema, medan `scope` di pagu manifest **dan** `scopes` tool) ditolak **sebelum** gerbang dan tanpa memakai jatah — 🔧 juga batas pemilik datanya yang tidak bisa ditulis di skema, tanggal di luar 1900–2999, dan `NaN` (**E-204**); batas laju per pengguna; keluaran = skema persis **sampai ke medan bersarang** (**E-206**); **pemanggilan agent lewat gerbang yang sama** (K-14); tool coach tanpa catatan bebas check-in & mood; tulisan agent meninggalkan `audit_logs` di transaksi tulisannya, event-nya bersumber `agent` (**E-205**) | catatan mood masih sampai lewat memori episodiknya (`memory.search`) — **C-32** |
> | 4.4 | tiap run menulis `tools_used` · `memory_scopes` (yang **benar-benar** disentuh) · `decision` (skalar, bukan penalaran) · `confidence` · `cost_usd` · token · model · latensi — juga run yang **gagal**, **ditahan** gerbang (`blocked`), dan **dibatalkan** di tengah aliran (token yang sudah keluar tetap dibayar); ditutup sekali; galat hanya `{code, type}` — juga run `cancelled`; 🔧 run yang programnya **tidak pernah berjalan** (pesan ber-id kembar sesudah run ditulis) ditutup `failed` (**E-200**) | run yang prosesnya MATI (bukan berhenti) tetap `running` — **K-31** |
> | 4.5 | **R2 ditanya sekali** lalu diingat (`allow_always`), atau sekali pakai; **R3 ditanya setiap kali**, bahkan bila izinnya `allow`; R4 ditolak; `deny` ditolak & dicatat **sebelum** konfirmasi; persetujuan hanya untuk pemanggilan yang agent, tool, **dan sidik masukannya** sama, diwarisi run anak; token bertanda tangan, sekali pakai, milik satu pengguna; delegasi tidak ditanya dua kali (**E-192**); 🔧 **satu giliran bisa ditanya lebih dari sekali** — token membawa pesan giliran dan persetujuan sebelumnya (**E-199**); `allow_always` disimpan di transaksi jawabannya | tool V0 paling tinggi R2 — R3/R4 dibuktikan dengan registry yang menaikkannya |
> | 4.6 | satu permintaan = **satu pohon** `agent_runs`, ditelusuri rekursif dari akarnya; orchestrator memilih agent dari niat (aturan), `trigger='agent'`, biaya permintaan = seluruh pohon | — |
> | 4.7 | tiap balasan membawa `confidence` + `rationale` (ditegakkan runtime); coach dari fakta tool — sumber yang ditolak dilewati **dan dinyatakan**, “tanya aku” ditanyakan — 🔧 scope ingatan *“tanya aku”* **dinyatakan** di alasannya (**E-208**); habit agent tidak menebak dan tidak mengaku mengubah catatan yang sudah ada; memory agent hanya menulis yang belum diingat — arch/08 §2.2: **agent** (**K-30**); `memory.search` tidak lagi menahan tiap jawaban coach pada izin `journal_raw` (**E-193**) | keyakinan V0 = banyaknya bukti, bukan peluang terkalibrasi (#34) |
> | 4.8 | token **mengalir** (`tool_call` · `token` · `done`), klien yang tersambung sesudah `POST` menerima semuanya dari token pertama; **`done` memuat `cost_usd`** seluruh pohon; riwayat membawa `confidence` + `rationale` (**E-194**, migrasi `0008`); konfirmasi punya rute (**E-195**); satu giliran per percakapan; isi percakapan tidak ke Redis (**K-31**); 🔧 permintaan yang ditolak tidak menimpa aliran (**E-202**), id kembar `409` (tinjauan kontrak), `error.code` = kode API (**E-203**), giliran gagal yang diputar ulang `failed` (**E-212**), cap waktu riwayat monoton (**E-213**) | lebih dari satu proses api — klien bisa tersambung ke proses yang salah (**K-31**) |
> | 4.9 | 🔧 biaya **24 jam bergulir** pengguna (run yang sudah ditutup + **jatah** run yang masih berjalan, di pohon mana pun) — ditambah perkiraan terburuk panggilan ini — melewati anggaran → **turun ke `simple`** — dipesan di bawah kunci per pengguna: giliran serentak tidak melewatinya, ganti zona waktu tidak mengosongkannya (**E-201**); jawaban tetap ada, tercatat `decision.model_downgraded` (**K-32**); dirakit dari `HVX_AI_ANGGARAN_HARIAN_USD` | angka anggaran sebenarnya — milik pemilik (uang) |

---

## Sprint 5 — Intelligence

| # | Tugas | Selesai bila |
|---|---|---|
| 5.1 | Behavior projector dari event | proyeksi bisa dibangun ulang dari nol dan hasilnya sama |
| 5.2 | Deteksi pola: waktu, hari, rentetan | keluarannya **asosiatif**, bukan kausal (naskah 4 §7) |
| 5.3 | `human_states` harian + `metrics jsonb` | tiap metrik punya `value`, `confidence`, `evidence_count` |
| 5.4 | Ambang Confidence Layer (issue #34) | `evidence_count` rendah → sistem **bertanya**, bukan menyatakan |
| 5.5 | Recommendation engine + `score_breakdown` | skor 0–1, `scoring_version`, `rationale` terisi |
| 5.6 | Umpan balik rekomendasi | `modified` dan `snoozed` tidak dihitung sebagai penolakan |

---

## Sprint 6 — Product

| # | Tugas | Selesai bila |
|---|---|---|
| 6.1 | Dashboard (bukan satu angka Life Score) | mengikuti naskah 4 §28: beberapa dimensi, tiap skor punya **Why** |
| 6.2 | Weekly review | menjawab 5 pertanyaan naskah 4 §31 |
| 6.3 | Notifikasi | bisa dimatikan per jenis |
| 6.4 | Layar Privacy Center | `summary`, izin per agent, ekspor, hapus |
| 6.5 | Alur hapus akun (6 tahap [`01`](01-DATABASE-SCHEMA.md)) + `DELETE /me` · `POST /me/restore` | uji: titik Qdrant ikut terhapus; **semua sesi pengguna dicabut seketika** (`cabut_semua` — status hanya dibaca saat masuk & penyegaran) |
| 6.6 | Rapikan UX + luring dasar | catat habit tanpa jaringan → sinkron tanpa duplikat |

> 🔨 **Sprint 6 dikodekan sebagian — keadaan 6 Okt 2026** (branch
> `v0/sprint-5-intelligence`, belum ber-PR):
>
> | # | Keadaan |
> |---|---|
> | 6.1 | ✅ backend `f1f76bf` + layar Flutter `261d788`: beberapa dimensi ber-Why, hanya yang V0 ukur (sumbu tanpa data **tidak** ditampilkan) |
> | 6.5 | ✅ **kode lengkap.** Stage A `8d4bd84`: `DELETE /me` (sandi diminta lagi → `pending_deletion` + jadwal 30 hari + semua sesi dicabut), `POST /me/restore`, login `pending_deletion` diizinkan (keputusan pemilik 5 Okt), migrasi 0010. Stage B: **sapuan tahap 3–6** oleh proses pekerja — migrasi 0011, tiga fungsi `hvx_pekerja`, titik Qdrant dibuang selagi akun terkunci, jejak audit dianonimkan di semua kolom, sesi dan jejak idempotensi Redis dibersihkan (**K-39**, **E-215…E-218**, [`01`](01-DATABASE-SCHEMA.md) *Prosedur hapus akun*). Bukti: `tests/integration/test_sapuan_hapus_akun.py` (13 uji) + `test_id_semu.py`, 20 mutasi `6.5b` |
> | 6.2 · 6.3 · 6.4 · 6.6 | ⏳ belum. 6.2 butuh inferensi jawaban dan sumbu yang V0 tak punya; 6.3 V0 reaktif tanpa pengiriman (A-28); 6.4 menyentuh arti *“hapus”* dan retensi (**C-34**, butir C — pemilik); 6.6 pekerjaan Flutter (antrean luring + `Idempotency-Key` yang sudah ada) |
>
> **Yang 6.5 sengaja belum menutup:** rujukan stream (id · pemilik · jenis) milik akun
> yang dihapus tidak dibuang per akun — dipangkas menurut kursor relay dan, untuk stream
> mati, 7 hari ([`../SECURITY.md`](../SECURITY.md)). `ip_hash` baris audit yang
> dipertahankan tidak diubah (**C-34**).

---

## Yang TIDAK ada di backlog ini

Neo4j · Kafka · ClickHouse · Kubernetes · Fashion/Career/30 agent ·
marketplace · SDK · voice · vision · wearable · federated learning.

Semuanya ada di naskah, **tidak satu pun ada di V0**. Menambahkannya ke sprint
mana pun di atas adalah cara paling cepat membuat 4–6 minggu jadi 4–6 bulan.
