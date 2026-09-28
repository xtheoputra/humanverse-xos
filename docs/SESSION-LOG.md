# Catatan Sesi

> Ringkasan tiap sesi kerja. Yang terbaru di atas.

---

## Sesi 34 — 28 September 2026

**Pemilik: *“lanjutkan”*** — meneruskan catatan serah-terima Sesi 33: tinjauan tiga
lensa Sprint 4 → gerbang penuh → PR.

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Keputusan pemilik | tidak ada yang baru |
| Keputusan sendiri | **K-32 diubah** — anggaran per 24 jam **bergulir**, jatah terburuk dipesan di bawah kunci per pengguna (hari lokal bisa digeser lewat zona waktu profil) · K-28 · K-29 · K-30 · K-31 ditambahi temuan tinjauan |
| Temuan ditutup | 🆕 **E-196 … E-213** — 16 dari tinjauan keamanan & kontrak, 2 (E-212 · E-213) dari pekerja penegak buta, 1 (E-211) dari uji Sprint 1 yang berkedip |
| `spec/` diubah | `01` (bentuk `decision`/`error` run yang tidak berhasil · `confirmed_by_user` · jatah di `cost_usd` · indeks percakapan) · `04` (id kembar 409 · kode galat SSE · `status` `failed` · token dua izin · urutan riwayat) · `05` (nama jawaban · pemeriksa pra-gerbang · jejak tulisan agent · keluaran bersarang · aturan 6 lewat tool · kolom *Batas laju*) · `07` (status Sprint 4) |
| Kode | 🔧 perbaikan tinjauan di `v0/sprint-4-ai`, migrasi **0009** — **1.138 uji Python** (958 → 1.138) + 40 uji Flutter, mutasi kode **476 → 612**, semuanya berbunyi |
| Tinjauan sebelum PR | 🔍 **tiga lensa serentak** — keamanan (6: pengenal niat ReDoS membekukan proses api 75 dtk, anggaran dikosongkan lewat zona waktu & dilewati giliran serentak) · kontrak (17: giliran dua izin tak bisa diselesaikan, tulisan agent tanpa `audit_logs`, catatan bebas bersarang lolos skema keluaran) · penegak buta (**91 dari 175 kerusakan lolos seluruh suite** — kini tiap satu punya uji & mutasi, dikerjakan lima pekerja serentak) |
| Uji yang berkedip | empat, tak satu pun dibiarkan: jam Redis & PostgreSQL VM Docker **mundur ±3 dtk tiap ±28 dtk** (E-211 · E-213), batas laju GCRA yang terisi ulang tiap detik, kemiripan acak dua ruang vektor; plus satu asersi yang selalu lolos |

---

## Sesi 33 — 24 September 2026

**Pemilik: *“kerjakan semua tugas yang belum terselesaikan dengan sempurna”*** —
sesi yang sama, berlanjut ke Sprint 4. PR Sprint 3 dibuka (#166) sesudah gerbang
penuh hijau.

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Keputusan pemilik | tidak ada yang baru |
| Keputusan sendiri | **K-28** AI Gateway V0 · **K-29** katalog agent · **K-30** program agent & keyakinan V0 · **K-31** aliran percakapan · **K-32** anggaran biaya |
| Temuan ditutup | 🆕 **E-190 … E-195** (menulis Sprint 4) |
| Butir pemilik | **C-32** diperluas — catatan mood sampai ke coach lewat memori episodiknya |
| `spec/` diubah | `01` (`ai_messages.confidence` · `rationale`, isi `agent_runs`) · `04` (percakapan, SSE, rute konfirmasi) · `05` (letak manifest · kolom scope · pelaksana tool · runtime · gerbang · orchestrator · program V0 · `menyaring_izin`) · `07` (status Sprint 4) |
| Kode | 🔨 **Sprint 4 — 4.1–4.9 seluruhnya**, branch `v0/sprint-4-ai`: AI Gateway · registry & katalog · pelaksana tool · runtime & `agent_runs` · gerbang risiko & konfirmasi · orchestrator · program agent V0 · percakapan & SSE · anggaran, migrasi 0007–0008 — **958 uji Python + 40 uji Flutter**, **132 mutasi baru, semuanya berbunyi** (kode: 344 → 476) |
| Gerbang Sprint 3 | tiga gerbang penuh berturut-turut menemukan sesuatu, semuanya dibetulkan — penegak yang lemah, **bytecode mutan basi** di alat ukurnya sendiri, dan uji regresi E-189 yang jendelanya hanya 200 ms |
| ⏸️ Berhenti di | sesi diakhiri pemilik sesudah Sprint 4 selesai dikodekan dan ter-push. **Langkah berikutnya, berurutan:** tinjauan tiga lensa Sprint 4 (keamanan · kontrak · penegak buta) → gerbang penuh `ci_lokal.py --lapor-github` → PR Sprint 4 (base `v0/sprint-3-memory-event`) → Sprint 5 → Sprint 6. PR #163–#166 menunggu HUMAN REVIEW |

---

## Sesi 32 — 24 September 2026

**Pemilik: *“kerjakan semua tugas yang belum terselesaikan dengan sempurna”*** —
sesi yang sama dengan Sesi 31, berlanjut ke Sprint 3.

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Keputusan pemilik | tidak ada yang baru — yang diikuti: H-25 · H-26 · H-27 · *“betulkan saja menurut anda benarnya dimana”* |
| Keputusan sendiri | **K-25** relay kotak keluar & grup konsumen · **K-26** penyemat lokal berkunci per pengguna · **K-27** memori episodik |
| Temuan ditutup | 🆕 **E-177 … E-181** (menulis Sprint 3) · 🆕 **E-182 … E-188** (tinjauan sebelum PR) · 🆕 **E-189** (cacat Sprint 1 yang ketahuan lewat uji yang berkedip di gerbang penuh) |
| Butir pemilik | 🆕 **C-33** teks bebas di payload event · **C-31** · **C-32** baru di sprint ini, diperluas tinjauan |
| `spec/` diubah | `01` (`embedding_model` · fungsi relay & penyelaras · peran `hvx_pekerja`) · `03` (kunci per kejadian · `habit.completion_retracted` · `for_date` & `completion_id` · bentuk konsumen V0 · 23 event) · `04` (`journal` · `activities`: `?source=`, `ended_at`) · `05` (daftar scope resmi · aturan 6 `journal_raw`) · `06` (aturan 6 dipersempit ke fakta perilaku · tiga tulisan tanpa event · pendengar jurnal) · `07` (status Sprint 3) |
| Kode | 🔨 **Sprint 3 — 3.1–3.8 seluruhnya**, branch `v0/sprint-3-memory-event`: `events` · relay & konsumen di **proses pekerja** · `journal` · Qdrant + penyemat · `memory` · `activities`, migrasi 0005–0006 — **767 uji Python + 40 uji Flutter**, **127 mutasi baru, semuanya berbunyi** (kode: 217 → 344) |
| Tinjauan sebelum PR | 🔍 **tiga lensa serentak** — keamanan (5 terbukti) · kontrak (9 terbukti) · penegak buta (**49 dari 68 kerusakan lolos seluruh suite**, kini tiap kerusakan punya uji dan mutasi). Yang paling mahal: satu kunci penyemat untuk semua pengguna — akun biasa membaca vektor orang lain dengan kamusnya sendiri |

---

### 🔴 Tiga hal yang “cukup” di kepala tetapi tidak di mesin

| Yang diandaikan | Yang terjadi |
|---|---|
| vektor berkunci tidak bisa dibaca tanpa kunci | benar — tetapi dengan SATU kunci untuk semua pengguna, server sendiri menyematkan kamus milik akun penyerang |
| penanda relay 24 jam cukup untuk jendela 60 detik | ±52 MB per akun sehari di Redis `noeviction` — dan relay yang sepi 24 jam mengirim ulang menit terakhirnya |
| uji mutasi selalu selesai | satu mutasi membuat ujinya menggantung, dan seluruh putaran berhenti tanpa satu baris keluaran — kini dibatasi 600 dtk, seluruh pohon prosesnya dihentikan |

Ketiganya ditutup — dengan uji yang **merah pada kode lama** dan mutasi.

---

## Sesi 31 — 24 September 2026

**Pemilik: *“kerjakan semua tugas yang belum terselesaikan dengan sempurna”*.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Keputusan pemilik | tidak ada yang baru — yang diikuti: H-25 (branch + PR, pemilik menggabungkan) · H-26 · H-27 · *“betulkan saja menurut anda benarnya dimana”* |
| Keputusan sendiri | **K-23** bacaan & pendengar lintas modul domain lewat titik rakit; energi check-in → tier adaptif · **K-24** ukuran dibatasi saat menulis; `Idempotency-Key` mengingat rujukan, bukan isi |
| Temuan ditutup | 🆕 **E-168** · **E-169** (rute yang `spec/07` tuntut, `spec/04` tidak punya) · 🆕 **E-170 … E-176** (tinjauan sebelum PR) · **E-165** kini diterapkan |
| `spec/` diubah | `01` (`goals_parent_not_self` · arti `for_date`) · `04` (pohon goal · habit pada tanggal · bentuk habit · penyelesaian · arti rentetan · check-in · mood · masukan ketat · ukuran badan · `Idempotency-Key` berujuk · kursor per daftar · galat validasi) · `05` (`habit.streak`) · `06` (aturan 3 & titik rakit · aturan 6 ditunda sampai 3.2) · `07` (status Sprint 2) |
| Kode | 🔨 **Sprint 2 — 2.1–2.7 seluruhnya**, branch `v0/sprint-2-human-core`: api (`goals` · `habits` · `checkins`, migrasi 0004) + **aplikasi Flutter pertama** (`apps/mobile`) — **579 uji Python + 40 uji Flutter**, **109 mutasi baru, semuanya berbunyi** (kode: 108 → 217) |
| Tinjauan sebelum PR | 🔍 **tiga lensa serentak** — keamanan (9 terbukti · 4 dugaan) · kontrak (19 terbukti · 5 dugaan) · penegak buta (**39 kerusakan lolos seluruh suite**, kini tiap kerusakan punya uji dan mutasi). Yang paling mahal: masukan yang dikoersi diam-diam (`"on"` menjadi persetujuan pelatihan model), goal anak yatim **40 dari 40** saat induknya dihapus serentak, dan cache `Idempotency-Key` yang menyimpan isi jawaban 24 jam di Redis bersama sesi |

---

### 🔑 Layar pertama, dan bukti bahwa manusia bisa memakainya

2.7 menuntut *“bisa dipakai manusia, bukan hanya curl”*. Uji widget memakai
layanan palsu; uji ujung-ke-ujung memakai klien asli tanpa layar — dan tinjauan
kontrak mencatat celah di antara keduanya. Kini `apps/mobile/test/ujung/`
merakit **layar yang sama** dengan `main.dart`, mengetuknya — daftar, tambah
habit, tandai selesai, keluar — terhadap api hidup di tahap smoke, lalu
memeriksa hasilnya **dari sesi lain di server**, bukan dari keadaan layar.

⚠️ **Yang diakui:** *enak dipakai* belum diukur — layar itu belum pernah
dipakai orang selain pengujinya.

---

### 🔴 Tiga hal yang “cukup” di kepala tetapi tidak di mesin

| Yang diandaikan | Yang terjadi |
|---|---|
| pydantic menolak tipe yang salah | mode **python** — yang dipakai FastAPI untuk badan — menerima `true` sebagai 1 dan detik Unix sebagai tanggal **UTC**; persetujuan tercatat dari string `"on"` |
| hapus-lunak menaikkan anak goal menjadi akar | ya — kecuali anak yang ditulis **serentak**: 40 dari 40 yatim tanpa kunci `FOR SHARE` |
| `Idempotency-Key` hanya cache | cache itu menyimpan catatan pengguna 24 jam sesudah dihapus, ~5 KiB per permintaan 19 byte, di Redis `noeviction` yang sama dengan sesi |

Ketiganya ditutup — dengan uji yang **merah pada kode lama** dan mutasi.

---

## Sesi 30 — 17 September 2026

**Pemilik membaca ringkasan PR #163 dan menjawab tiga hal sekaligus: *“gunakan alternatif versi gratis jangan ada tagihan”* · *“menulis kode dan menemukan kesalahan, betulkan saja menurut anda benarnya dimana. kerjakan b-40, b-41”* · *“data milik satu pengguna harus milik pengguna tersebut, data masing-masing pengguna milik pribadi user”* — lalu *“lanjutkan tugas yang belum selesai lainnya”*.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Keputusan pemilik | **H-26** CI tanpa tagihan · **H-27** data tiap pengguna milik pribadinya · aturan kerja: kesalahan spec yang ketemu saat coding **dibetulkan** |
| Keputusan sendiri | **K-19** kepemilikan data dijaga basis data · **K-20** status commit dari gerbang lokal · **K-21** sesi token opak, bukan JWT · **K-22** angka sandi & batas laju, penguncian per akun — keduanya dikoreksi sesudah tinjauan · pertanyaan terbuka **K-17** dijawab |
| Temuan ditutup | **B-40** ✅ · **B-41** ✅ · 🆕 **E-163** ✅ · 🆕 **E-164** ✅ · 🆕 **E-165** ✅ · 🆕 **E-166** ✅ · 🆕 **E-167** ✅ |
| Temuan dicatat | 🆕 **B-42** batas login gagal per akun bukan batas *beruntun* NIST — dinyatakan, bukan lagi diklaim |
| `spec/` diubah | `01` (§10 hak akses · §11 RLS · FK komposit · peran `hvx_app` · `consents.purpose` · §12 fungsi login) · `02` (aturan G · H · I) · `04` (`consents` saat daftar · galat `/auth` · batas laju · `subject_type` di jalur izin · `Idempotency-Key` · `DELETE /me` ⏳ 6.5) · `05` (bawaan gerbang risiko) · `06` (aturan 5 kini ditegakkan · aturan 6 dicakupkan) · `07` (status Sprint 1 · 6.5) · `01` (persetujuan per jenis) |
| Penjaga baru | `test_kepemilikan_data.py` (20 uji) · penjaga peran api saat mulai · uji tanpa-tagihan — **7 mutasi baru** (kode: 35 → 42) |
| Kode | 🔨 **Sprint 1 — 1.1–1.7 seluruhnya**, branch `v0/sprint-1-identity`: 12 commit, **277 uji** — **66 mutasi baru, semuanya berbunyi** (kode: 42 → 108) |
| Tinjauan sebelum PR | 🔍 **dua lensa** — keamanan: **11 temuan** (8 dari peninjau + 3 ditemukan saat mengujinya), 1 high: keluar di tengah penyegaran menghidupkan sesi kembali · lensa kedua (verifikator · kontrak · penegak buta): **7 cacat kode · 3 E · 1 B · 10 penegak buta** · lensa dokumen: **12 kalimat** yang tidak tepat. Cacat kode **dibuktikan merah dulu**, celah penegak dengan mutasi |

---

### 🔑 “Gratis” tanpa berhenti menjadi gerbang

Actions dimatikan — tetapi gerbang yang hanya berjalan di mesin pengembang tidak terlihat oleh peninjau. Jalan tengahnya fitur dasar repo yang tidak pernah ditagih: **API status commit**. `ci_lokal.py --lapor-github` menempelkan hasil gerbang penuh ke commit PR sebagai `ci-lokal` — dan **menolak** menempel pada gerbang sebagian, pohon kerja kotor, atau commit yang belum di-push, sebab status hijau pada pohon yang tidak diuji lebih buruk daripada tidak ada status.

⚠️ **Yang diakui:** status itu bukti kejujuran, bukan penghalang — siapa pun yang punya akses tulis bisa menempelkannya, dan PR merah tetap tidak terhalang digabung.

---

### 🔒 Tiga lapis, sebab masing-masing menutup lubang yang lain biarkan

| Lapis | Tanpa lapis ini |
|---|---|
| **RLS** — aplikasi hanya melihat baris pengguna yang dilayani transaksi | satu kueri yang lupa `WHERE user_id` membocorkan semua pengguna |
| **FK komposit** `(induk_id, user_id)` | RLS tidak menolong: **pemeriksaan FK PostgreSQL tidak menerapkan RLS** — anak B tetap bisa menunjuk induk A |
| **peran aplikasi** + penjaga mulai | superuser dan pemilik tabel **melewati RLS** — dua lapis di atas hanya berlaku bagi yang mau mematuhinya |

> 💡 **B-41 semula “sengaja tidak dibetulkan” dengan alasan yang jujur — dua jalan, dua harga.** Jawabannya ternyata sudah ada di kalimat pemilik: kalau data milik pribadi pengguna, maka itu sifat yang dijaga **basis data**, bukan disiplin penulis `repository.py`.

---

### 🔨 Sprint 1 — tujuh tugas, dan yang ditemukan dengan menuliskannya

| | Hasil |
|---|---|
| 1.1–1.7 | register · login · refresh · logout · sesi · `/me` · persetujuan bertujuan · mesin izin · audit · batas laju — seluruhnya sebagai peran aplikasi di bawah RLS |
| Ketidakcocokan antar-`spec` | **E-163** `PUT /privacy/permissions` tanpa `subject_type` · **E-164** `register` tanpa tempat untuk persetujuan — dibetulkan di `spec/04` |
| Yang tetap milik pemilik | kosakata `purpose` & teks kebijakan (#59 butir 2) · persetujuan sebagai atap izin (#59 butir 3) · seluruh butir C |

> 💡 **Tiga hal yang “cukup” di kepala, dan tidak cukup di mesin.** Cache izin yang dihapus sebelum & sesudah commit tetap bisa **menghidupkan kembali izin yang baru dicabut** — pembaca yang membaca sebelum commit menulis cache sesudahnya; kini kuncinya bergenerasi, diuji dengan pembaca yang ditahan di tengah pencabutan. NIST SP 800-63B-4 dikutip untuk panjang sandi sambil melewatkan **daftar tolak** di pasal yang sama — `passwordpassword` lolos. Dan `SECURITY.md` hampir mengklaim *“IP tidak disimpan mentah”* dengan penegak yang tidak memeriksanya.
>
> 🔴 **`bandit` tahap scan akan merah** — dua kueri `profile` dirakit dengan f-string. Tertangkap karena tahap scan dijalankan sebelum PR, bukan sesudahnya; diganti SQL statis, **tanpa** `# nosec`.

---

### 🔍 Tinjauan adversarial — dan sesi yang terputus di tengahnya

Sebelum PR: peninjau keamanan terpisah dengan probe ke PostgreSQL & Redis sungguhan — **8 temuan**. Sesi terputus tepat saat laporannya tiba, sebelum satu pun ditindaklanjuti; pemilik: *“lanjutkan tugas yang belum selesai”*. Laporannya ternyata tersimpan utuh di transkrip peninjau — dilanjutkan dari sana, bukan diulang.

Aturannya: **temuan tidak dipercaya dari laporannya.** Tiap temuan ditulis dulu sebagai uji yang merah pada kode lama dengan alasan yang dimaksud; baru kodenya dibetulkan; lalu mutasi membuktikan ujinya sanggup merah lagi.

| | Yang paling mahal kalau lolos |
|---|---|
| 🔴 high | **keluar di tengah penyegaran menghidupkan sesi kembali** — token baru sah, catatan sesi tanpa `user_id`, dan sesi itu tidak bisa dicabut lagi (logout 500). Kini tiap operasi yang membaca lalu menulis satu catatan sesi satu skrip Lua; ujinya menyela **tiap celah antarperintah** |
| medium | batas 3 login gagal per akun meloloskan **12 dari 12** tebakan serentak · `vİctim@…` masuk ke akun `victim@…` yang sedang terkunci |
| 🆕 × 3 | pencabutan karena token bekas melewatkan pasangan yang diputar pencuri · `cabut_semua` melupakan sesi yang lahir di sela · **pesan PostgreSQL sendiri membawa email ke log** (`DETAIL: Key (email)=…`) |

> 💡 **Tiga temuan baru lahir dari menulis uji untuk temuan lama.** Yang paling tajam: perbaikan `hide_parameters` untuk temuan 5 lulus — sampai ujinya memakai galat UNIQUE sungguhan, dan email itu tetap muncul, kali ini dari PostgreSQL. Perbaikan yang diuji hanya terhadap kasus yang dibayangkan penulisnya adalah pola §1 `arch/11` lagi.

**Lensa kedua — tiga peninjau serentak, dan perbaikan yang ikut ditinjau.**

| | Yang paling tajam |
|---|---|
| verifikator | perbaikan pertama **tidak bobol** — tetapi perbaikan temuan 6 sendiri membuat regresi (status dibaca sesudah token diputar: galat basis data membakar token klien), dan *“≤ 100 gagal beruntun, NIST”* ternyata **batas laju** — B-42; klaimnya dicabut, dan lensa dokumen masih menemukannya di empat tempat lagi |
| kontrak | **E-165** `Idempotency-Key` dijanjikan juga di rute yang mengeluarkan token · **E-166** aturan 6 `spec/06` dilanggar `profiles` sejak tulisan pertama · **E-167** gerbang risiko `spec/05` butuh bawaan yang tak bisa dijawab mesin izin · sandi emoji ditolak sebagai *“repetitive”* |
| penegak buta | token akses 30 hari, IP mentah di audit, `now()` untuk riwayat, hash tanpa NFKC — **semuanya lulus uji** · dan `uji_mutasi_kode.py` membaca alasan dari **sumber uji** yang dicetak pytest, bukan dari galatnya |

> 💡💡 **Pertanyaan yang dua putaran ini ajarkan: *“diukur di mana?”*** Uji sesi benar, tetapi tidak pernah menanyakan pencabutan yang serentak dengan penyegaran. Perbaikan log benar untuk galat yang dibayangkan, tetapi pesan PostgreSQL sendiri membawa email. Dan tuntutan *“gagal dengan alasan yang dimaksud”* benar — sampai terlihat bahwa alasannya bisa dibaca dari baris sumber yang lulus.

**Lensa dokumen — tiap angka benar, dua belas kalimat tidak.** Yang paling tajam: *“klaim NIST dibetulkan di mana pun ia tertulis”* — ditulis tanpa `grep`, dan salah di empat tempat; penguncian per akun ditulis *“±14 menit”*, padahal penyerang yang terus mencoba menahan pemilik akun di `429` selama ia mau; dan *“tiap kueri lewat transaksi pengguna”* — pencarian akun saat masuk tidak, dan itu dibetulkan di kode.

⚠️ **Yang diakui tidak dikerjakan:** hitungan ringkasan butir **B/E/G** di README (39 · 158 · 20) dan di header `docs/99` (41→42 · 153 · 21) sudah tidak cocok satu sama lain sejak **sebelum** Sprint 0, dan id E sudah mencapai E-167. Butir baru dinomori berurutan; hitungan lamanya **tidak** disensus ulang di sesi ini.

---

### 🔴 Dua penjaga baru hampir lahir buta — keduanya tertangkap sebelum commit

1. **Uji keberadaan RLS** lulus untuk kebijakan `USING (true)` — ada, tetapi membuka semuanya. Ditambah uji **isi** kebijakan, dengan mutasinya.
2. **Mutasi “FK kembali satu kolom”** versi pertama mengganti kolom anak tanpa kolom induk; migrasinya gagal `InvalidForeignKey`, dan `uji_mutasi_kode.py` **menolak** menghitungnya berbunyi — tuntutan *“gagal dengan alasan yang dimaksud”* dari Sprint 0 menangkap cacat mutasinya sendiri.

---

## Sesi 29 — 16–17 September 2026

**Pemilik: *“lanjutkan semua tugas dan fase yang belum selesai sesuai dokumen yang tertulis”* — dan, sesudah sesi pertama terputus di tengah sapuan dokumen, *“lanjutkan tugas yang belum selesai”*. Menurut [`arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md), tahap berikutnya adalah T0 — kode V0 — dan satu-satunya penahannya [#3](../../issues/3): siapa yang mengerjakan. Itu ditanyakan, bukan ditebak. Pemilik memilih **AI coding agent di branch + PR, pemilik yang menggabungkan** (**H-25**). Sprint 0 dikodekan penuh.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Kode **produksi** | **0 di `master`** · **Sprint 0 — 8 dari 51 tugas** di branch `v0/sprint-0-foundation`, satu commit per tugas, **menunggu HUMAN REVIEW** |
| Pemeriksaan `arch/11` yang jalan | 12 → **19 dari 26** — B-2 · M-1 · M-2 · M-3 (`import-linter`) · M-4 · E-3 · A-1 |
| Yang **terbukti sanggup GAGAL** | 12 → **19 dari 19** — 25 mutasi dokumen · 35 mutasi kode |
| Gerbang | [`../tools/ci_lokal.py`](../tools/README.md) `lint → typecheck → test → build → scan` **hijau di mesin lokal**; Actions tetap terhalang ([#160](../../issues/160)) |
| `spec/` diubah | **3 dari 8** — `01` (pemicu `updated_at`, pagar SQL, `pgcrypto`) · `06` (penegak aturan 1–4) · `07` (status Sprint 0 · B-40 · B-41 · K-18) |
| `arch/` diubah | **3 dari 12** — `06` (E-162) · `10` (#3 terjawab) · `11` (blok ` ```penegak ` yang dibaca uji) |
| Issue | tidak bertambah — **PR Sprint 0** dibuka |
| Keputusan | **H-25** (pemilik) · **K-17** arah impor modul · **K-18** satu commit per tugas, PR per sprint |
| Temuan | **E-161** · **E-162** · **G-24** · **B-40** · **B-41** |

---

### 🔑 Pertanyaan yang HARUS ditanyakan, bukan dijawab sendiri

Seratus dua issue terbuka, dan yang tidak diblokir keputusan pemilik tinggal satu: **mulai menulis kode**. Tetapi *siapa yang menulis* adalah soal orang dan waktu — bukan milik agent. Tiga pilihan ditawarkan: **mulai di branch + PR** · *belum, dokumen saja* · *langsung ke `master`* (yang terakhir melewati HUMAN REVIEW naskah 5 §27). Pemilik memilih yang pertama.

⚠️ **Yang tetap terbuka di #3, dan kini lebih nyata:** 4–6 minggu itu taksiran atau tenggat, dan berapa jam per minggu tersedia untuk **meninjau** — sebab sekarang ada PR yang menunggu.

---

### 🔴 Menulis kode menemukan empat hal yang tujuh sesi membaca tidak temukan

| | Temuan | Kenapa pemeriksa lolos |
|---|---|---|
| **E-161** | `set_updated_at()` didefinisikan, **nol `CREATE TRIGGER`** — 11 kolom `updated_at` berisi waktu pembuatan selamanya | P-1..P-3 memeriksa anotasi, bukan pemicu |
| **G-24** | 21 baris markdown **di dalam** blok SQL `spec/01` sejak 10 Sep — DDL-nya **tidak bisa dijalankan** | regex tabel tetap cocok; tidak ada yang pernah **menjalankan** DDL itu |
| **E-162** | `arch/06` §3 menyebut himpunan `CHECK` milik `activities`, dan menyuruh *summarizer* memakai nilai yang `CHECK` `events` **tolak** | ditemukan **E-3** begitu ia membaca `CHECK` dari DDL |
| 🛑 **B-40** | `REVOKE … FROM PUBLIC` di `audit_logs` **tidak menghalangi** role yang dipakai api — `UPDATE` & `DELETE` lolos; superuser melewati RLS | penjaganya benar, tidak pernah dijalankan terhadap pelaku yang sebenarnya |

> 💡 **Pola E-42 berulang di DDL yang sudah diperiksa mesin.** Pemeriksa benar untuk yang ia periksa — dan tidak satu pun pernah menjalankan DDL-nya ke basis data. Kini `test_migrasi.py` melakukannya: DDL `spec/01` dan migrasi 0001 ke dua basis data, katalognya dibandingkan.

🚨 **Pindai citra merah di percobaan pertama** — 2 CVE HIGH (libpcre2) di citra dasar Debian. Gerbangnya berbunyi; citranya kini menambal paket saat dibangun, dan harganya (pembangunan tidak sepenuhnya reprodusibel) ditulis di `SECURITY.md`.

---

### 🔍 Tinjauan adversarial — penegak yang lulus tanpa melihat

Sebelum PR dibuka: enam lensa, dan tiap temuan diserahkan ke verifikator yang **berusaha membantahnya**. **35 temuan · 2 terbantah · 33 bertahan (16 medium · 17 low · 0 high) · 32 dibetulkan · 1 dicatat (B-41).**

Yang paling mahal kalau lolos: `/health` dengan batas 1 dtk **menjawab sesudah 60 dtk** saat PostgreSQL berhenti menjawab. Yang paling memalukan bagi repo ini: **separuh temuan medium adalah penegak yang lulus tanpa melihat** — modul ke-13 lolos keempat kontrak, 10 dari 12 kontrak M-2 tak pernah dibuktikan sanggup gagal, pembanding katalog buta terhadap sepuluh perbedaan skema, dan mutasi R-1 dihitung berbunyi sambil **menghapus** temuan.

> 💡💡 **`uji_mutasi.py` dibangun untuk menjawab *“apakah pemeriksa ini bisa merah?”* — dan satu mutasinya sendiri tidak bisa.** Kini tiap mutasi dokumen wajib melahirkan temuan **baru**, dan tiap mutasi kode wajib gagal dengan **alasan yang dimaksud**.

🛑 **B-41** — sebelas FK satu kolom membiarkan baris anak milik B menempel ke induk milik A, dan terhapus saat A menghapus induknya (diukur ulang 17 Sep). **Sengaja tidak dibetulkan di Sprint 0**: belum ada tulisan baris anak, dan dua jalannya (FK komposit, atau aturan repository yang dijaga uji) punya harga berbeda. Dicatat di `spec/07` tepat sebelum tugas 2.1.

---

### 🔴 Sesi pertama terputus — dan sapuan lanjutannya menemukan yang tertinggal

Sesi 16 Sep berhenti di tengah pembaruan dokumen, sebelum satu commit pun dibuat. Yang dilanjutkan 17 Sep: gerbang dijalankan ulang dari nol atas pohon kerja yang ada (**hijau**), lalu dokumen yang belum tersapu — `tools/README.md` masih menulis 21 dan 12 mutasi (kini 25 dan 35), README tanpa **K-18** dan masih menyebut `uv sync --frozen`, ringkasan `docs/99` masih menulis 21 · 12 mutasi dan tujuh bagian katalog (kini 13), dan catatan `arch/10` menunjuk pemisahan *“bisa jalan”* di `arch/11` yang barisnya sudah dihapus.

> 💡 **Angka ringkasan yang ditulis di tengah perbaikan basi sebelum perbaikannya selesai.** Yang menangkapnya bukan ingatan, melainkan `grep` atas setiap angka yang pernah berubah di sesi yang sama.

---

### 🛑 Yang TETAP milik pemilik

**HUMAN REVIEW dan merge PR Sprint 0.** [#160](../../issues/160) — Actions terhalang tagihan, dan perlindungan branch tidak tersedia untuk repo privat pada paket akun ini: **PR merah pun tidak terhalang digabung**. Sisa [#3](../../issues/3) soal waktu. **Nol butir C diputuskan.** R-1 tetap 7 temuan (keputusan cakupan).

---

## Sesi 28 — 11 September 2026

**Pemilik mengulang: *“lanjutkan semua tugas dan fase”*. Sesi 27 menutup dengan kalimat *“yang tersisa dan tidak diblokir cuma satu, dan sudah dikerjakan”* — dan kalimat itu berhenti benar begitu satu pertanyaan ditanyakan pada `arch/11` sendiri: *apakah yang diperiksa tiap aturan sudah ada dalam bentuk lain?* Jawabannya memindahkan DELAPAN pemeriksaan dari “menunggu kode” ke “jalan hari ini”.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Kode **produksi** | tetap **0** — menunggu [#3](../../issues/3) |
| Pemeriksaan yang jalan tanpa kode produksi | 5 → **12 dari 26** |
| Pemeriksaan yang **terbukti sanggup GAGAL** | 0 → **12 dari 12** ([`../tools/uji_mutasi.py`](../tools/README.md)) |
| `spec/` diubah | **4 dari 8** — `01` (23 tabel) · `03` · `05` · `07` |
| `arch/` diubah | **4 dari 12** — `06` · `07` · `10` · `11` |
| Issue | 160 → **162**; **#161** & **#162** baru |
| Keputusan | **K-16** (`data_subject` + retensi masuk V0 sekarang) |
| Temuan | **B-39** · **E-160** · **G-23** |

---

### 🔑🔑 SATU PERTANYAAN, DELAPAN PEMERIKSAAN

[`../arch/11`](../arch/11-PENEGAKAN.md) §2 menjawab *“butuh kode?”* dengan **ya** untuk kelompok **P**, **A**, dan **B-6**. Jawaban itu benar — untuk **artefak yang BERJALAN**.

Tetapi yang diperiksa **P-1/P-2/P-3** adalah **DDL**, **A-2/A-3** adalah **manifest**, **B-6** adalah **pohon direktori** — dan ketiganya **sudah ada, sebagai dokumen**, sejak `spec/01`, `spec/05`, dan `arch/03` ditulis.

> 💡💡 **Pertanyaan yang terlewat bukan *“apakah aturannya benar”* melainkan ***“apakah yang diperiksanya sudah ada dalam bentuk lain?”*** Delapan pemeriksaan menunggu kode yang belum ditulis, sementara yang mereka periksa sudah tergeletak di repo selama berhari-hari.**

---

### 🔴🔴 TEMUAN TERBESAR: DDL V0 gagal gerbangnya sendiri, 23 dari 23

| | Hasil |
|---|---|
| **P-1** tiap tabel menyatakan `@retention` · `@who-can-set` · `@on-delete` | 🛑 **23 dari 23** — nol anotasi |
| **P-2** tiap tabel punya `data_subject` | 🛑 **23 dari 23** — nol kolom |
| **P-3** tidak ada `user_id` nullable tanpa penjaga | 🛑 **1** — `audit_logs` |

[`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §8 sudah menulis *“tabel tanpa `data_subject` → ditolak CI — P-2”*. **DDL yang akan dimigrasikan Sprint 0 tugas 0.4 melanggarnya sejak baris pertama.**

⚠️ Dan [`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §4 menyatakan sebaliknya: *“ini **satu-satunya** tambahan yang seluruh `arch/` tuntut terhadap V0”*. **Bentuk yang sama dengan [#158](../../issues/158)**: ringkasan yang benar-sendiri, tidak pernah dijalankan terhadap detail yang diringkasnya.

⇒ **K-16.** Nilainya **tidak dikarang**: `until-account-deleted`+`hard` dari **Prosedur hapus akun** tahap 3, `forever`+`anonymise` untuk `audit_logs` dari tahap 5, `who-can-set` dari contoh yang `arch/06` §5 berikan sendiri. [#161](../../issues/161)

---

### 🔴 `audit_logs` membongkar aturan yang menuntut kolomnya

`arch/06` §6: *“setiap tabel wajib punya `data_subject`; kalau `'user'`, `user_id` WAJIB TIDAK NULL; kalau tidak, `user_id` TIDAK BOLEH ADA.”*

`audit_logs` memuat baris yang pelakunya **pengguna** dan baris yang pelakunya **sistem** — satu tabel, dua subjek.

⇒ **`data_subject` adalah sifat BARIS, bukan tetapan TABEL.** Aturannya sendiri sudah ditulis dalam bentuk baris; yang keliru menganggapnya bisa diwujudkan di tingkat kolom. Penegakannya `CHECK ((data_subject = 'user') = (user_id IS NOT NULL))`.

💡 **Contoh tandingannya ada DI DALAM V0 — dan §6 tidak melihatnya karena ia hanya memeriksa tabel Phase 15+ yang menjadi alasannya ditulis.**

---

### 🔴 K-14 mendarat di dua tempat dan melewatkan yang ketiga — SEHARI sesudah diputuskan

`spec/05` tabel agent ✅ mencantumkan tiga entri · `spec/07` 4.3 ✅ menghitungnya (*“9 tool + 3 entri `kind: agent`”*) · **registry tool `spec/05` sendiri 🛑 tetap 9 baris.**

🛑 Akibatnya: aturan validasi 3 (*tiap tool `risk_level <= max_risk`*) **tidak bisa dijalankan** untuk `orchestrator-agent`. **Gerbangnya ada, angkanya tidak.**

> 💡 **Kali KEEMPAT bentuk yang sama** (#52 · H-21/#67 · B-22/#59). Yang baru: keputusannya dibuat **sehari sebelumnya**, oleh orang yang menulis catatannya sendiri. ⇒ **kedekatan waktu bukan penjaga.** [#162](../../issues/162)

---

### 🔴 Dua kalimat `arch/07` yang tidak bisa keduanya benar

`agent.paused` di tabel kembaran §6 **tidak pernah ada di naskah mana pun**; yang ada `agent.suspended`, **dan kembarannya `agent.resumed` sudah lengkap sejak awal**. ⇒ pasangannya benar, **daftar tuntutannya** yang salah.

§7 satu tabel dua baris: *“Event V0: 22, tidak berubah”* **dan** *“`tool.failed` dituntut untuk V0 — tugas 4.3”*. Tugas 4.3 **tidak menyebut event sama sekali**.

⭐ **Uji yang menyelesaikannya, dan ia berlaku umum:**

> **Yang boleh ditambahkan ke V0 hanyalah hal yang TIDAK BISA ditambahkan nanti.**

`consents.purpose` ✅ · `data_subject` ✅ · **`tool.failed` 🛑 ditolak** — sebuah event bisa mulai diterbitkan kapan saja tanpa kehilangan apa pun.

⚠️ **Tetapi kekosongan yang ditunjuknya nyata dan tersisa:** `agent_runs` menyimpan `tools_used` dan `status` **pada tingkat RUN** — satu tool gagal di tengah run yang akhirnya sukses **tidak meninggalkan satu baris pun**. Di tabel yang `spec/07` 4.4 sebut *“`agent_runs` sebagai audit”*.

---

### 🚨🚨 DAN SEBELAS HIJAU TIDAK BERARTI APA PUN SAMPAI MERAHNYA DIBUKTIKAN

[`../tools/uji_mutasi.py`](../tools/README.md) merusak **satu** hal yang tiap pemeriksaan **klaim** deteksi, lalu menuntut kode keluar 1. **12 mutasi, 12 berbunyi.**

> 🔑 **Regex yang tidak pernah cocok dan tabel yang tidak pernah terbaca memulangkan LULUS dengan tenang** — dan itu bentuk kegagalan yang seluruh `arch/11` dibangun untuk menutupnya.

🔴 **Putaran pertamanya menuduh G-1 buta.** Mutasinya mengubah **nama** pasal (`Reversibility` → `Reversibility X`) dan G-1 diam — padahal G-1 tidak memeriksa nama pasal, ia memeriksa **adanya penegak**. Yang cacat mutasinya.

> 💡💡 **Sebuah uji yang tidak menguji apa yang dikiranya diuji akan MENUDUH YANG BENAR** — dan itu lebih berbahaya daripada uji yang tidak ada, sebab ia menghasilkan pekerjaan perbaikan atas sesuatu yang tidak rusak.

🔴 **E-4 juga sempat LULUS secara melingkar**: ia membaca daftar tuntutannya dari `arch/07` §6, lalu mencari namanya di himpunan yang **ikut memanen `arch/07`**. Semua ada, tentu saja. Diperbaiki: E-4 mencari **hanya di `spec/03`** — dan langsung menemukan dua.

---

### 🛑 Yang TETAP milik pemilik

**Nol butir C diputuskan.** R-1 tetap 7 temuan (keputusan cakupan). **#160** (Actions terhalang tagihan) belum dibuka ⇒ **gerbangnya masih MANUAL**. Kode produksi menunggu [#3](../../issues/3).

---

## Sesi 27 — 11 September 2026

**Pemilik: *“lanjutkan semua tugas dan fase”*. Yang tersisa dan TIDAK diblokir keputusan pemilik cuma satu: [#157](../../issues/157) butir 1 — *“jalankan E-1, E-2, G-1, R-1 sekarang sebagai satu skrip pemeriksa dokumen”*. Dikerjakan. Dan menjalankannya menemukan enam hal yang membaca tidak akan menemukan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Berkas baru | **`tools/`** — `periksa_dokumen.py` + `README.md` |
| Kode **produksi** | tetap **0** — menunggu [#3](../../issues/3) |
| Pemeriksaan `arch/11` | 25 → **26**; yang bisa jalan tanpa kode 4 → **5**; yang **benar-benar dijalankan** 0 → **5** |
| `spec/` diubah | **1 dari 8** — `03` (64 nama diganti, 1 nama ditambah) |
| `arch/` diubah | **4 dari 12** — `07` · `10` · `11` · `README` |
| Issue | 157 → **160**; **#157 DITUTUP**, **#158** · **#159** · **#160** baru |
| Keputusan | **K-15** (domain event diambil dari registry, bukan dari kata pertama nama) |
| Temuan | **E-159** · **G-22** · **A-38** |

---

### 🔑 Kenapa justru butir ini, dan bukan yang lain

`arch/10` §2 sudah menjawabnya pada sesi sebelumnya: **T0–T5 tidak diblokir satu pun keputusan yang belum diambil, kecuali [#3](../../issues/3) — siapa yang mengerjakan.** Sembilan puluh delapan issue terbuka, dan yang bisa dikerjakan tanpa pemilik tinggal satu baris: butir 1 #157.

> 🛑 **Dan bentuknya sendiri adalah temuan.** [`arch/11`](../arch/11-PENEGAKAN.md) dibangun dari satu pelajaran — *aturan yang dinyatakan tetapi tidak dijaga akan dilanggar* — lalu menyatakan **25 aturan dan menjaga NOL**. §2-nya menulis *“empat pemeriksaan bisa dijalankan hari ini”*, dan tidak satu pun dijalankan. **Berkas penegakan adalah tempat paling tidak masuk akal untuk mengulangi pelanggaran yang ia daftar sendiri**, dan ia mengulanginya selama satu hari.

---

### 🔴🔴 TEMUAN TERBESAR: 66 dari 127 nama event mendarat di domain yang tidak ada

`spec/03` memadankan 127 nama `PascalCase` dengan aturan **K-3** (*kata pertama → domain*). `arch/07` §2 menetapkan registry domain, dan menyatakan nama di luarnya **ditolak CI**. **Keduanya konsisten sendiri-sendiri. Tidak satu pun pernah dijalankan terhadap yang lain.**

| Nama naskah | K-3 menghasilkan | Domainnya |
|---|---|---|
| `LargeScaleScenarioCreated` | `large.scale_scenario_created` | **`large`** |
| `OilPriceChanged` | `oil.price_changed` | **`oil`** |
| `InterestRateChanged` | `interest.rate_changed` | **`interest`** |
| `HeartRateRecorded` | `heart.rate_recorded` | **`heart`** |

> 🔑 **Kata pertama sebuah nama tidak selalu SUBJEKNYA.** K-3 benar sebagai aturan **transkripsi**; ia tidak pernah menjadi aturan **kepemilikan**.

⭐ **Arahnya tidak dipilih — ia sudah tertulis di `arch/07` §2 sejak awal:** *“Domain baru ditambahkan hanya bersama konteks pemiliknya — penambahan itu perubahan arsitektur, bukan penamaan.”* ⇒ **namanya yang pindah, bukan registry yang tumbuh.** Bacaan yang ditolak (*“tambahkan saja 50 domain itu”*) membengkakkan registry 46 → 96 dan menghapus seluruh alasannya ada: supaya `stuff.happened` **tidak** lolos.

⇒ **K-15**, 64 nama diganti, **V0 tidak bergeser — 22 event tetap 22.** Biayanya nol hari ini; sesudah baris pertama masuk `events` ia menjadi migrasi riwayat. [#158](../../issues/158)

---

### 🔴 TEMUAN KEDUA: `arch/07` §4 MENGAKU sudah memeriksanya

Kolom *“Domain tujuan”* menuliskan Phase 11 → `agent` · `approval` · `tool`. Diukur: ke-22 nama Phase 11 mendarat di **`agent` saja**; `approval` dan `tool` **nol**.

> 💡 **Sebuah tabel yang MENGGAMBARKAN hasil terbaca persis seperti tabel yang MENGUKURNYA.** Itu pelajaran [#38](../../issues/38) dalam bentuk paling halus, dan bentuk yang sama dengan *“keempat agent V0 lulus ketiga uji”* di sesi 26.

Plus: §2 menulis ***“39 domain”*** untuk tabel berisi **45** — hitungan yang berhenti dipelihara, persis *“99 tabel”* yang ternyata 247.

---

### 🔴 TEMUAN KETIGA: `emergency.stop` bertabrakan dengan §6-nya sendiri

E-2 menolak enam nama yang berakhir bukan kata kerja lampau: `battery.low` · `emergency.stop` · `deadline.approaching` · `supply.chain_disruption` · `agent.policy_violation` · `agent.security_violation`.

🛑 Yang kedua bukan soal tata bahasa: `arch/07` §6 menuntut kembaran untuk **`emergency.stopped`**. Dua berkas, satu kejadian, **dua nama** — dan proyeksi yang membaca salah satunya akan selalu kehilangan separuh riwayat, **tanpa galat**.

---

### 🔴 TEMUAN KEEMPAT: satu nama event pemilik tak pernah sampai ke tabel padanan

**Ditemukan E-5 — pemeriksaan yang lahir dari pertanyaan yang ditujukan kepada E-1 dan E-2 sendiri:** *apa yang keduanya TIDAK PERNAH lihat?* Jawabannya tajam: keduanya memeriksa `event_type`, jadi keduanya hanya melihat nama yang **sudah** masuk tabel. Nama yang tidak pernah masuk **tidak punya `event_type` sama sekali** — ia lolos karena **tak terlihat**, bukan karena benar.

**`MeetingCreated`** — [`167`](167-AUDIO-VOICE-VIDEO-TEMPORAL.md) L29, penutup alur `Speech → … → Event`. Terlewat sebab [`SENSUS-EVENT.md`](SENSUS-EVENT.md) memanen **bagian yang JUDULNYA menyebut “Event”**, dan naskah 167 tidak punya satu pun — namanya berdiri di sebuah **contoh**.

⇒ populasi pemilik **133 → 134**; pelanggaran sesudah #38 **128 → 129**; baris tabel **127 → 128**. Kesimpulan sensus tidak berubah; besarannya naik. [#159](../../issues/159)

---

### 🔴🔴 DAN ALAT UKURNYA SENDIRI SALAH DUA KALI SEBELUM BENAR

Ditulis di sini karena laporan yang tidak menyebutkannya akan terbaca lebih kuat daripada yang sebenarnya.

| | Yang keliru | Kalau tidak ketahuan |
|---|---|---|
| 1 | panen butir roadmap ikut membaca **catatan audit saya sendiri** ⇒ `G18.11 Safety, Privacy & Governance` — milestone yang hanya **saya usulkan** — terhitung **ada** | Phase 18 tampak punya gerbang keselamatan. **Alat yang mencari kegagalan justru menutupinya** |
| 2 | panen nama event **hanya membaca token di dalam backtick** ⇒ kedelapan nama `security.*` (K-10) hidup di blok kode **tanpa** backtick | seluruh keluarga event **keamanan** lolos E-1 dan E-2 — keluarga yang paling mungkin diaudit |

💡 Pembeda untuk keliru 1 **tidak dikarang**: `SENSUS-EVENT.md` sudah mengujinya — percobaan *“semua baris `>` itu catatan saya”* **salah** (naskah juga mengutip pemilik dengan `>`); yang lulus validasi silang adalah menilai blok dari **baris pertamanya**. Dipakai ulang apa adanya.

✅ **Bukti pembetulannya sah:** sesudahnya kedelapan roadmap memulangkan jumlah butir yang **sama dengan angka yang dokumennya sendiri sebutkan** — A14 10 · R16 10 · H17 12 · G18 10 · S19 10 · C20 12 · `spec/07` **51 tugas** · `arch/10` **13 tahap**.

---

### ✅ G-1 dan R-1 MEMBENARKAN vonis tangan — dan satu angka bertambah tajam

Sepuluh pasal Konstitusi punya penegak; Pasal 8 **sebagian** dan batasnya dinyatakan. Enam roadmap gagal, `spec/07` dan `arch/10` lulus — persis yang `arch/11` §4 tulis tangan.

🔴 Yang berubah: yang gagal **tujuh pasangan gerbang**, bukan enam. **Phase 16 melanggar dua aturan sekaligus** — `R16.10` Safety Kernel (indeks 10, menjaga 8 butir) **dan** `R16.9` Simulation (indeks 9, menjaga manipulasi · humanoid · drone · armada), yang kedua atas dasar §16.26: `Code → Simulation → Safety Test → Hardware` adalah **urutan wajib**. ⇒ dari enam roadmap yang gagal, Phase 16 yang **paling** terlambat. [#111](../../issues/111)

---

### 🛑🛑 TEMUAN KELIMA, dan ia tentang sesi ini sendiri: **gerbangnya tidak pernah berjalan**

`.github/workflows/periksa-dokumen.yml` dipasang supaya aturannya berhenti menjadi sesuatu yang harus **diingat seseorang**. Jalan pertamanya — dan satu-satunya yang pernah ada di repo ini — berhenti sebelum langkah pertama:

```
X periksa in 4s
  The job was not started because recent account payments have failed
  or your spending limit needs to be increased.
```

Repo privat ⇒ menit Actions ditagih. ⇒ **skripnya hijau (diverifikasi lokal, keluar `0`), gerbangnya mati.**

> 🛑 **Yang salah bukan tagihannya, melainkan urutan saya: workflow dipasang, lalu hijaunya DIASUMSIKAN.** Pertanyaan yang seharusnya ditanyakan bukan *“apakah berkasnya benar”* melainkan ***“apakah ia benar-benar JALAN”*** — pertanyaan yang **sama** yang hari ini sudah menemukan tiga hal lain, dan yang tidak saya tanyakan pada hal yang baru saja saya buat sendiri.
>
> 💡 **Dan bentuknya persis yang dilaporkan di paragraf pembuka sesi ini:** sebuah gerbang yang tidak pernah berbunyi adalah aturan tanpa penjaga. Kali ini penjaganya **ada** — dan tetap tidak berbunyi. Itu versi paling halus dari pola yang `arch/11` §1 daftar enam kali, dan ia lolos justru karena berkasnya **benar**.

⇒ [#160](../../issues/160) — **milik pemilik**, sebab ia soal tagihan (*uang ⇒ bukan keputusan saya*). Sampai dibuka: **pemeriksaannya MANUAL**, `python tools/periksa_dokumen.py` sebelum tiap commit. ⚠️ Ia juga memblokir **tugas 0.7** `spec/07` (CI), yang seluruh gunanya adalah berjalan otomatis.

---

### 🔧 Tiga aturan rancangan yang membuat alatnya bukan salinan kedua dokumen

| | |
|---|---|
| 1 | **Registry dibaca DARI dokumennya.** 46 domain dari `arch/07` §2; 10 pasal dari `arch/08` §4; pasangan gerbang dari blok ` ```r1 ` di `arch/10` §2.1. **Kalau dokumennya hilang, pemeriksa GAGAL dengan galat — bukan lulus karena tidak menemukan apa pun untuk diperiksa.** |
| 2 | **Populasi yang diperiksa dinyatakan.** `--senarai` mencetak tiap nama + baris asalnya; tiap pengecualian menyertakan **alasannya**, supaya ia tidak jadi tempat menyembunyikan temuan. |
| 3 | **Angka di prosa diperiksa terhadap tabel di atasnya.** Itu yang menangkap *“39 domain”*. |

⚠️ **R-1 tidak menebak pasangan gerbangnya sendiri.** Roadmap baru yang belum punya baris di blok ` ```r1 ` **tidak diperiksa** — disengaja: gerbang yang ditebak mesin akan salah menuduh, lalu diabaikan orang.

---

### 🛑 Yang TETAP milik pemilik — tidak bergerak

**Nol butir C diputuskan.** Ketujuh temuan R-1 adalah keputusan **cakupan** ([#99](../../issues/99) · [#111](../../issues/111) · [#116](../../issues/116) · [#121](../../issues/121) · [#131](../../issues/131) · [#144](../../issues/144)). **21 dari 26** pemeriksaan menunggu kode, dan kode menunggu [#3](../../issues/3).

> 💡💡 **Dua kalimat yang layak dibawa keluar dari sesi ini:**
>
> **1 · Jalankan dua dokumen yang tidak pernah saling diuji terhadap satu sama lain.** Tabrakan 66 baris tidak muncul saat salah satunya **dibaca** — ia muncul saat yang satu **dijalankan sebagai aturan** atas yang lain.
>
> **2 · Setiap kali sesuatu berubah menjadi hijau, tanyakan: apa yang alat ukur ini TIDAK PERNAH lihat?** Bukan *“apakah hasilnya benar”* — hasilnya benar untuk populasi yang dilihatnya. Yang salah **populasinya**. Pertanyaan itu berbuah **tiga kali** dalam satu sesi.

---

## Sesi 26 — 10 September 2026

**Pemilik memerintahkan: *“kerjakan semua tugas dan fase yang masih tersisa”*. Yang tersisa adalah [#139](../../issues/139) — Master Architecture v2.0, permintaan penutup naskah 24, dan permintaan KELIMA dalam deret yang isinya sebagian besar sama; dua yang pertama dikerjakan, tiga terakhir hilang tanpa keputusan. Dikerjakan: [`../arch/`](../arch/README.md), dua belas berkas, sebelas butir yang pemilik sebut dijawab satu per satu.**

**Dan mengerjakannya menemukan tiga hal yang membaca tidak akan menemukan — semuanya di `spec/`, bukan di naskah.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Folder baru | **`arch/`** — 12 berkas, cakupan **Phase 1–20** (`spec/` tetap V0 saja) |
| Dokumen total | **272** di `docs/` · **8** di `spec/` · **12** di `arch/` |
| Berkas kode | tetap **0** |
| `spec/` diubah | **5 dari 8** — `01` (`max_risk`) · `05` (aturan 3 ditulis ulang, manifest v2) · `06` (Python) · `07` (Python, B-22, K-14) · `README` |
| Issue | 153 → **157** (98 terbuka, **59 ditutup** — **26 ditutup sesi ini**); **#154**–**#157** baru |
| Keputusan | **K-13** (bahasa backend) · **K-14** (pemanggilan agent = pemanggilan tool) |
| Temuan | **E-158** · **A-36** · **A-37** · **G-21** |

### 🔑 Aturan pengutamaan — tiga lapis dokumen, dan itu yang pertama ditetapkan

Tanpa ini, `docs/` · `spec/` · `arch/` akan dibaca sebagai tiga jawaban untuk satu pertanyaan.

> **`arch/` mengikat NAMA dan BATAS. `spec/` mengikat BENTUK. Untuk V0, `spec/` menang. Naskah tidak pernah menang atas keduanya, dan tidak pernah diubah.**

⚠️ Aturan ketiga punya biaya yang harus disebut: pembaca naskah Phase 16 akan menemukan `robotics/planning/`, sementara `arch/03` menamainya `robotics/motion-planning/`. Itu **disengaja** — menyunting naskah menghapus bukti bahwa tabrakannya pernah ada, dan bukti itu satu-satunya alasan tabrakannya bisa ditemukan.

---

### 🔴🔴 TEMUAN TERBESAR: `spec/` berganti bahasa backend tanpa mencatatnya

```
grep -rl  "FastAPI" docs/                        →  1 berkas  (naskah 1, di tabel DAN diagram)
grep -rlo "Node.js|NestJS|Express|Golang" docs/  →  0 berkas
```

**FastAPI adalah satu-satunya kerangka backend yang pernah dinamai dalam 24 naskah.** Namun `spec/06` memakai `index.ts`/`routes.ts` dan `spec/07` menuntut `npm test` — **tanpa satu kalimat pun yang menyatakan pergantiannya.**

🛑 Dan ia memblokir **Sprint 0 tugas 0.3** — *kerangka `apps/api`*, berkas pertama yang akan ditulis di repo ini.

💡 **Bentuknya sama dengan pola terbesar repo ini — sebuah klaim berhenti benar tanpa memberi tahu pembacanya — tetapi kali ini terjadi di berkas yang seluruh tugasnya adalah memberi tahu pembacanya apa yang harus dikoding.**

🔑 **Dan cara menemukannya layak diingat:** bukan dengan membaca `spec/` (di sana ia konsisten dengan dirinya sendiri), melainkan dengan **membandingkan `spec/` terhadap naskah tentang hal yang `spec/` tidak pernah nyatakan**. *Kekosongan tidak muncul saat dibaca; ia muncul saat dibandingkan.*

⇒ **K-13: Python + FastAPI.** ADR-004 sudah mengunci LangGraph (Python lebih dulu), dan **enam dari dua puluh fase natively Python** — terutama **Phase 16, karena ROS 2 tidak punya klien Node yang didukung resmi**. `spec/06` dan `spec/07` diselaraskan; `spec/01`–`05` bebas bahasa dan tidak disentuh.

⭐ Keuntungan tak disengaja: **`import-linter` menggantikan `no-restricted-imports` DAN `madge --circular` sekaligus** ⇒ batas modul **dan** enam batas keras menjadi **satu berkas kontrak, satu perintah CI**.

---

### 🔴 TEMUAN KEDUA: menguji K-5 pada empat agent V0 menemukan lubang di GERBANGNYA

`spec/05` menutup bagian K-5 dengan *“keempat agent V0 lulus ketiga uji”* — **dinyatakan, tidak diperiksa.**

| Agent V0 | (b) memilih tool saat jalan | Vonis |
|---|---|---|
| `coach-agent` | ✅ 7 tool | agent |
| `habit-agent` | ✅ 3 tool | agent |
| `memory-agent` | ⚠️ 2 tool, pemakaian hampir selalu tetap | **perbatasan** → [#155](../../issues/155) |
| **`orchestrator-agent`** | 🛑 **`tools: —`** | 🛑 **GAGAL** |

Lubangnya bukan di orchestrator melainkan **di kata *“tool”***: ia memilih **agent**. Dan akibatnya bukan perkara istilah —

> 🛑 **Selama memanggil agent bukan pemanggilan tool, sisi-sisi pohon eksekusi (`parent_run_id`) tidak pernah melewati risk gate — tepat di simpul yang melihat seluruh pohon.**

⇒ **K-14.** Dan penerapannya langsung menemukan angka yang salah di V0: `orchestrator-agent` naik **R0 → R2**, sebab ia memanggil `agent.habit` (R2). Angka lama tampak benar **hanya selama pemanggilan agent tidak dihitung**.

💡 **Dua agent pertama lulus dengan mudah.** Kalau pemeriksaannya berhenti di sana, K-5 akan tampak selesai. **Jalankan aturan yang baru dibuat pada kasus yang terasa paling sepele — itu yang menguji ALASANNYA, bukan hasilnya.**

---

### 🔴 TEMUAN KETIGA: tiga keputusan yang sudah DITUTUP tidak pernah sampai ke `spec/`

| Keputusan | Ditutup sejak | Belum diterapkan di |
|---|---|---|
| [#52](../../issues/52) `requires_confirmation` pindah ke Policy Engine | naskah 15 | `spec/01` masih punya kolomnya |
| **H-21** / [#67](../../issues/67) `R` ≠ `L` | naskah 15 | `agents.risk_level` masih satu angka |
| **B-22** / [#59](../../issues/59) `consents.purpose` sebelum baris data pertama | (terbuka) | `spec/07` tugas 1.4 tidak menyebutnya |

Ketiganya kini diterapkan. **Pelajaran [#38](../../issues/38) muncul lagi: janji di issue tertutup tidak punya penjaga.** Dan ditemukan bukan dengan membaca daftar issue, melainkan dengan **membandingkan `spec/` terhadap keputusan yang mengaku sudah berlaku atasnya.**

---

### Angka yang berubah karena diukur ulang lalu diselesaikan

| Sumbu | Sebelum | Sesudah |
|---|---|---|
| pohon repositori | **38** di 24 naskah | **28 folder** tingkat-atas |
| **pohon keluarga keamanan** | 🛑 **19** | ✅ **1** (+ `governance/` berdiri sendiri) |
| nama dipakai >1 pohon | **128** | **0 tabrakan konsep** |
| `simulation/` | 13 pohon, **5 arti** | 1 mesin bersama + 4 plugin bernama |
| nama tabel | **247**, 19 berdefinisi ganda | 19 divonis; **4 kelas penyimpanan** |
| nama agent | **59**, 44 disebut sekali | **6 agent + 53 kandidat** — bawaan `service` |
| rantai keselamatan | 9 · 11 · 5 · 5 gerbang | **satu rantai kanonik, 12 gerbang** |
| peta fase | tiga peta, tak satu pun kanonik | **satu peta, versi 3, tertutup, BERNOMOR VERSI** |

### ⭐ Empat butir yang bentuknya paling layak dipakai ulang

**1 · `world-model` MENYIMPAN, `simulation` MENJALANKAN — dan `simulation/` dipecah menurut apa yang SAMA, bukan apa yang berbeda.** Nama yang paling banyak berulang (13 pohon) ternyata lima mesin. Tetapi yang **sama** di kelimanya justru bagian yang paling penting dijaga: `scenario` · `counterfactual` · `seed` · determinisme · **isolasi dari data nyata**. ⇒ yang **naik** bagian samanya; yang **tinggal** mesinnya. Dan itu yang membuat §12.16 bisa ditegakkan **satu kali**, bukan lima kali.

**2 · Uji naik-turun butuh satu syarat yang tidak ada di K-9: ia hanya dijalankan atas nama yang dipakai TANPA induknya.** `runtime/` ada di 7 pohon tetapi tak seorang pun menulis *“Runtime Engine”* telanjang; `simulation/` ditulis telanjang, dan [#130](../../issues/130) merekam *“Simulation Engine dengan lima arti”*. Syarat ini juga menjelaskan **6 dari 10 positif palsu** pemindai duplikasi sebelumnya.

**3 · Sebuah GERBANG dijadwalkan SEBELUM hal yang dijaganya — dan itu bisa diperiksa mesin.** Enam catatan di enam naskah melaporkan bentuk yang sama (keselamatan dijadwalkan terakhir). ⇒ **R-1**: untuk tiap pasangan (gerbang **G**, hal yang dijaga **T**), `index(G) < index(T)`. Dijalankan hari ini: **enam roadmap fase GAGAL, `spec/07` dan `arch/10` LULUS.** 🔑 **Yang lulus keduanya ditulis sebagai PEKERJAAN, bukan sebagai peta fase** — roadmap yang ditulis untuk dikerjakan menaruh gerbangnya lebih dulu; yang ditulis untuk menggambarkan menaruh yang paling menarik lebih dulu.

**4 · Bawaan `max_risk: 0` berlawanan arah dengan K-12, dan justru itu buktinya prinsipnya benar.** K-12 menolak bawaan `risk_level: 0` untuk **tool** (tool yang lupa diisi jadi paling tidak dijaga). `max_risk` adalah **pagu**, jadi `0` berarti agent yang lupa diisi **tidak bisa memanggil apa pun di atas R0**. 💡 Yang ditanyakan bukan *“berapa bawaannya”* melainkan ***“kalau seseorang lupa mengisinya, ke sisi mana ia jatuh?”***

### ⚠️ Satu tabrakan nama yang HAMPIR saya buat sendiri

`arch/06` sempat memakai `subject_type` untuk *siapa yang datanya* — sementara amplop event `spec/03` **sudah** memakai `subject_type` untuk *jenis entitas* (`"habit"`, `"goal"`). Itu akan menambah satu baris ke kamus tabrakan, **di berkas yang tugasnya menghapusnya**. Diganti `data_subject`. 💡 Tertangkap dengan **memeriksa nama usulan terhadap `spec/` sebelum menulisnya** — murah, dan layak diulang untuk tiap nama kolom baru.

### 🔑 Satu baris yang paling berguna dari seluruh sesi ini

> **T0 sampai T5 tidak diblokir oleh satu pun keputusan yang belum diambil — kecuali [#3](../../issues/3), yaitu siapa yang mengerjakannya. Mulai T6 ke atas, setiap tahap menunggu keputusan yang hanya bisa diambil pemilik.**

Bentuknya konsisten: T6–T12 adalah tahap yang datanya menyangkut **orang yang tidak punya akun** (tetangga, tamu, pejalan kaki, karyawan, penduduk kota) atau **badan orang** (biometrik, gaya, gerak). Persis kelas keputusan yang aturan pemilah serahkan kepada pemiliknya.

Dan [#20](../../issues/20) memblokir **peluncuran**, bukan pengkodean ⇒ **penghambat untuk MEMULAI tinggal satu.**

### Yang sengaja TIDAK diputuskan

**Nol butir C.** Ditambah: **Phase 1 tetap tanpa nama** (K-6 dipertahankan — tetapi bentuk celahnya berubah: penomoran fase dimulai di naskah 3, jadi isi Phase 1 sudah bisa **ditunjuk**; yang hilang cuma **labelnya**) · §16.5 dan §16.7 · lima angka keselamatan fisik [#112](../../issues/112) · empat urutan tangga cakupan [#130](../../issues/130) · L5 lawan Autonomy Contract [#98](../../issues/98) · urutan ulang enam roadmap fase.

---

## Sesi 25 — 9 September 2026

**Tidak ada naskah baru. DELAPAN hal diukur untuk pertama kalinya — overlap antar-modul · peta fase · nama event · rute API · daftar agent · nama tabel · tangga risiko · rantai keputusan — dan semuanya membalik angka yang dipakai. Polanya: hitungan BERURUTAN meleset ke bawah · KEJADIAN bukan AKIBAT · PENJUMLAHAN bukan HIMPUNAN · hitungan yang BERHENTI DIPELIHARA · tuduhan yang ARAHNYA TERBALIK · dan kegagalan yang dilaporkan TANPA DENOMINATOR.**

**Lalu pemilik mendelegasikan keputusan, dan DUA BELAS butir K diambil — sebelas issue ditutup karenanya, dan empat butir ditegakkan sebagai aturan validasi di `spec/`.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** |
| Dokumen ditambah | **8 berkas** (+ [`GERBANG-SKEMA.md`](GERBANG-SKEMA.md) diperiksa ulang) — [`KEPUTUSAN-DIDELEGASIKAN.md`](KEPUTUSAN-DIDELEGASIKAN.md) 308 · [`SENSUS-MODUL.md`](SENSUS-MODUL.md) 321 · [`PETA-FASE.md`](PETA-FASE.md) 187 · [`SENSUS-EVENT.md`](SENSUS-EVENT.md) 164 · [`SENSUS-AGENT.md`](SENSUS-AGENT.md) 122 · [`SENSUS-TABEL.md`](SENSUS-TABEL.md) 139 · [`SENSUS-TANGGA.md`](SENSUS-TANGGA.md) 116 · [`SENSUS-RANTAI.md`](SENSUS-RANTAI.md) 119 |
| Dokumen total | 264 → **272** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** — skrip pengukur sengaja **tidak** disimpan di repo |
| `spec/` diubah | **4 berkas** — `01` presedensi tabel (K-4) · `03` tabel padanan 127 nama (K-3) + amplop `security.*` (K-10) · `04` awalan `/v1` (K-8) · `05` **aturan 7·8·9** (K-1, K-12) + medan `reaches_third_party` + kriteria agent (K-5) |
| Issue | 145 → **153** (120 terbuka, **33 ditutup** — **13 ditutup sesi ini**: **sebelas** oleh keputusan K, **dua** karena **jawabannya sudah ada di `spec/` tapi issue-nya tak pernah ditutup**); **#146**–**#153** baru, plus komentar bukti di **#1**, **#38**, **#139**, **#142** |
| Temuan | **E-151**–**E-157** · **G-20** · **B-39** · 5 cacat indeks diperbaiki · **2 koreksi atas pekerjaan saya sendiri** (klaim #142; awalan `spec/04`) |
| Keputusan | **12 butir K** diambil sendiri atas permintaan pemilik → [`KEPUTUSAN-DIDELEGASIKAN.md`](KEPUTUSAN-DIDELEGASIKAN.md). **K-9 membuka blokir Sprint 0 tugas 0.1.** Nol dari 12 mengubah V0 |

### 🔴🔴 Temuan terbesar: hitungan BERURUTAN meleset ke bawah secara sistematis

Sepuluh kali `99-CATATAN-AUDIT.md` mencatat *“H-10 tergerus ke-N kalinya”* —
sepuluh catatan di sepuluh berkas, masing-masing menyebut duplikasi yang
terlihat **saat itu**. Tidak pernah ada satu sensus.

Sensus atas seluruh `docs/` (38 blok pohon di 36 dokumen):

| | Catatan berurutan | Sensus |
|---|---|---|
| `simulation/` | **6** (*“keenam kalinya”*, E-145) | **15 pohon** |
| `sdk/` | tidak pernah dihitung | **14 pohon** |
| `agents/` | *“sejak naskah 2”*, tanpa angka | **10 pohon** |
| `memory/` | tidak pernah | **8 pohon** |

⭐ **Yang paling banyak diduplikasi ternyata `sdk/`, bukan `simulation/`** — dan
`sdk/` tidak pernah sekali pun dihitung, sementara `simulation/` dilacak lima
naskah berturut-turut.

💡 **Pelajaran yang bisa dipakai ulang:** menghitung *“ini yang ke berapa”* satu
per satu, di berkas yang berbeda-beda, **meleset ke bawah**. Yang dibutuhkan
bukan catatan yang lebih rajin melainkan **satu sensus**. Pertanyaannya bukan
*“apakah ini duplikat?”* melainkan **“berapa banyak seluruhnya, dihitung
sekali?”** → **E-151** / [#146](../../issues/146).

### 🛑 Pemeriksaan yang belum pernah dijalankan: duplikat DI DALAM satu pohon

§9.38 menaruh `scenario/` **dan** `counterfactual/` di `world-model/` **dan** di
`simulation/` — pasangan yang sama, utuh, dua kali, di dalam satu diagram.
Ditambah `preference/` di `memory-engine/` dan `prediction/`.

Kalau pengguna bertanya *“bagaimana kalau saya tidur satu jam lebih lama?”* —
modul mana yang **menjawab**, modul mana yang **menyimpan**? →
**G-20** / [#147](../../issues/147).

✅ **Dan tiga perempat temuan pemindai itu ternyata BUKAN cacat.** Enam nama
ganda di [`83`](83-STRUKTUR-REPO-FINAL.md) (`agents/`×3, `security/`×3, …)
semuanya sah — induknya berbeda peran (kode · `prompts/` · `docs/` · `tests/`).
Dicatat justru supaya pembaca berikutnya tidak “memperbaikinya”.

### 🔴 Sapuan Sesi 24 membuktikan `docs/` — dan tidak pernah menyentuh `spec/`

Sembilan pemeriksaan Sesi 24 semuanya bercakupan `docs/`. Diperiksa dengan
pemeriksaan yang setara, `spec/` menyimpan **lima cacat**, semuanya di berkas
**indeks**:

| Cacat | Yang benar |
|---|---|
| `00-DAFTAR-ISI.md` — `02-ERD.md` = *“Mesin keadaan”* | tidak ada mesin keadaan di sana; isinya **relasi + 6 aturan kepemilikan** |
| `00-DAFTAR-ISI.md` — `06-MODULE-BOUNDARIES.md` = *“51 tugas V0”* | itu isi `07`; `06` = **6 aturan ketergantungan** |
| `00-DAFTAR-ISI.md` — `07-BACKLOG-V0.md` = *“Kriteria selesai V0”* | `07` = **51 tugas** dalam 7 sprint (dihitung: 8+7+7+8+9+6+6 = 51) |
| `00-DAFTAR-ISI.md` — baris `README.md` **kosong** | diisi |
| `spec/README.md` — *“21 event”* | **22** (dihitung; berkasnya sendiri berjudul *“22 event — 21 dari naskah 5 §7 + 1 usulan”*) |

⭐ **Deretnya konsisten: keterangan `02`, `06`, `07` bergeser satu baris.**
Tabel `docs/` dibangun dari isi direktori; Lampiran B `spec/` ditulis tangan —
dan yang ditulis tangan itulah yang melenceng.

💡 **Pertanyaan yang menemukannya:** *“sapuan yang membuktikan kelengkapan itu
mencakup berkas jenis apa — dan jenis apa yang tidak pernah dibukanya?”*

### ⭐ 262 dari 263 hitungan baris tepat; yang meleset justru berkas yang mustahil dipelihara

`SESSION-LOG.md` ditulis **1.726** padahal saat commit yang sama selesai isinya
sudah **1.795** — ia satu-satunya berkas yang masih bertambah **sesudah** daftar
isi menghitungnya. Angkanya diganti penanda `—` dengan catatan kaki, bukan
diperbarui: **angka yang mustahil dipelihara lebih baik tidak ditulis daripada
salah tiap sesi.**

### 🔴🔴 Peta fase juga diukur — dan dua peta gagal dengan cara yang PERSIS SAMA

Untuk `Phase` ternyata ada **tiga** peta, bukan dua: naskah 8
([`113`](113-PETA-FASE-5-12.md)) · §10.41 ([`175`](175-REPO-API-DB-ROADMAP-DOD.md)) ·
§20.36 ([`275`](275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md)).

| Peta | Fase diramalkan | Tepat | Pola kesalahan |
|---|---|---|---|
| naskah 8 | 8 (Phase 5–12) | **4** | empat **terdekat** benar, empat **terjauh** salah |
| §10.41 | 5 (Phase 11–15) | **3** (+1 sebagian) | yang **terjauh** salah |

⇒ **Jangkauan andal sebuah peta fase di repo ini ± 3–4 fase.** Dua peta, ditulis
enam naskah berjarak, gagal identik.

⭐ Bukan alasan berhenti membuat peta — **7 dari 13 ramalan benar**, dan yang
benar itulah yang dipakai orang. Alasan untuk **tidak menggantungkan keputusan
pada baris TERJAUH sebuah peta**. → **E-152** / [#148](../../issues/148).

### 🔴 Koreksi yang MEMPERKECIL pekerjaan: sisa #142 satu nama, bukan delapan baris

[#142](../../issues/142) menyimpulkan *“Phase 1–8 belum pernah didaftar dalam 24
naskah”* dari:

```
grep -rohE "Phase [1-8] +[A-Z]{3,}" docs/  →  0
```

Angka nolnya **benar** — diverifikasi ulang. Tetapi polanya menuntut **huruf
besar semua** sesudah nomor fase, sehingga ia **mustahil** cocok dengan
*“Phase 5: HumanVerse Research Lab”*. Yang diukur **kesesuaian FORMAT**, bukan
keberadaan.

**Tujuh dari delapan fase sudah punya nama** — dan sudah terkumpul di
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) baris 17–20 sejak lama. Yang
benar-benar tidak ada cuma **Phase 1**.

💡 **Pelajaran: `grep` yang mengembalikan NOL membuktikan *“tidak ada yang
berbentuk ini”*, bukan *“tidak ada”*. Periksa apa yang polanya MUSTAHIL cocoki
sebelum menyimpulkan dari angka nol.**

### 🔴🔴 Permintaan yang sama sudah diajukan pemilik TIGA KALI

Belum pernah dicatat sebagai deret. Ditelusuri dari penutup tiap naskah:

| # | Kapan | Yang diminta | Nasib |
|---|---|---|---|
| 1 | naskah 4 | Blueprint Engineering v1.0 | ✅ **dikerjakan** |
| 2 | naskah 5 | Engineering Specification v1.0 | ✅ **dikerjakan** |
| 3 | naskah 8 | **Phase 12 “Blueprint Implementation”** — *“ini yang paling besar”* | ❌ digantikan |
| 4 | naskah 18 | arsitektur teknis Phase 14 | ❌ tidak pernah dimulai |
| 5 | naskah 24 | **Master Architecture v2.0** | ⏳ [#139](../../issues/139) |

**Empat butir muncul UTUH di ketiga permintaan yang belum dikerjakan** — skema
basis data · skema/kontrak event · Docker/Kubernetes·deployment topology ·
urutan implementasi. ⚠️ Kontrak API dan struktur repositori hanya 2 dari 3;
**dua sel kosong itu sengaja tidak dibulatkan** jadi klaimnya empat, bukan tujuh.

🛑 **Yang membedakan bukan isi permintaan melainkan apa yang datang sesudahnya:
dua yang dikerjakan dijawab SEBELUM naskah berikutnya tiba.** Naskah 18 bahkan
sudah menuliskan bahwa pekerjaannya *“bisa dimulai tanpa keputusan baru dari
pemilik”* ([`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) L682) — enam naskah
kemudian ia belum dimulai. Bukti ini dipasang sebagai komentar di
[#139](../../issues/139), bukan issue baru, supaya ia berada di tempat
keputusannya diambil.

### 🔴🔴 Sensus KETIGA: nama event — "kesepuluh" ternyata **128 nama**

[#38](../../issues/38) sudah **ditutup** (`domain.verb`, huruf kecil, dua
segmen). Pelanggarannya dicatat sampai *“kesepuluh”* — tetapi yang dihitung
selama ini **kejadian** (satu naskah = satu pelanggaran), bukan **nama**.

| Populasi | sesuai | PascalCase |
|---|---|---|
| **kata pemilik di naskah** | **21** | **133** |
| catatan audit saya | 31 | 59 |

Lima PascalCase hanya di [`16`](16-EVENT-DRIVEN.md) (naskah 1–2, **sebelum**
keputusan) ⇒ **128 nama ditulis dalam format yang ditolak sesudah keputusan.**

⭐ **Yang lebih menentukan: ke-21 nama yang sesuai SEMUANYA (21 dari 21)
berasal dari [`85`](85-BEHAVIOR-DAN-EVENT.md) — naskah 5 §7.** Naskah sesudahnya
hanya mengutip ulang. 🛑 **Sejak naskah 5 pemilik menamai 128 event baru, dan
nol memakai format yang dipilih.** Formatnya bukan diperdebatkan — ia tidak
pernah dipakai lagi.

⚠️ Phase 12 dan Phase 19 tidak muncul di sebaran **bukan karena terlewat**:
keduanya tidak mendefinisikan model event sama sekali (diperiksa langsung).
⇒ **sembilan dari sembilan** naskah yang punya model event memakai PascalCase.

💰 Biaya masih nol (belum ada kode) — **kecuali tiga tabrakan KOSAKATA** yang
tidak selesai dengan mengubah bentuk: `sleep.completed`↔`SleepEnded` ·
`meeting.completed`↔`MeetingEnded` · `mood.logged`↔`MoodChanged`.
→ **E-153** / [#149](../../issues/149).

### ⚠️ Dua kekeliruan alat ukur saya sendiri, keduanya condong ke arah yang sama

Sensus event butuh **tiga** percobaan, dan dua yang pertama membuat format yang
dipilih tampak **lebih banyak dipakai daripada kenyataannya**:

| Percobaan | Kekeliruan | Akibat |
|---|---|---|
| 1 | tak memisahkan kata pemilik dari catatan audit saya | `spatial_map.updated` terhitung “sesuai” padahal itu **usul saya** |
| 2 | menganggap semua baris `>` = catatan saya | **salah** — naskah juga mengutip pemilik dengan `>`; §18.5 kehilangan **13 nama** |
| 3 | blok `>` diklasifikasi dari **baris pertamanya** (catatan audit selalu dibuka penanda vonis) | ✅ dipakai — dan divalidasi silang |

✅ **Validasi silang** menyelamatkannya: hasil sensus dicocokkan dengan
pemeriksaan manual yang sudah ada di naskah — §13.12 *“lima belas event”* → 15 ·
§16.31 *“13 event”* → 13 · §18.5 → 14. **Ketiganya cocok.**

💡 **Pembeda populasi harus DIUJI, bukan diasumsikan.** Percobaan 2 terdengar
masuk akal dan gagal diam-diam.

### 🔴🔴 Sensus KEEMPAT: daftar agent — "> 40" ternyata **59**, dan irisannya **enam**

Jumlah agent ditaksir dengan **penjumlahan** (25 §11.4 + 7 tak terdaftar + 12
§12.29 = *“> 40”*), yang mengabaikan dua daftar lebih tua **dan** menganggap tak
ada nama berulang.

Lima daftar, nama dinormalkan (`FashionAgent` = `Fashion`):

| | |
|---|---|
| baris mentah | **80** |
| **nama unik** | **59** |
| muncul di 4–5 daftar | **NIHIL** |
| muncul di 3 daftar | **6** |
| hanya sekali | **44 — 75 %** |

⭐ **Irisan ketiga registry umum — yang berisi 14, 22, dan 25 agent — tepat
ENAM:** `Career · Fashion · Habit · Learning · Social · Travel` — dan
**keenamnya agent DOMAIN**. Tak satu pun agent inti/sistem bertahan di
ketiganya.

⚠️ Tiga pasang nyaris-kembar (`Orchestrator`↔`Supreme Orchestrator` ·
`Planner`↔`Planning` · `Finance`↔`Finance Behavior`) akan menaikkannya jadi
tujuh — **sengaja tidak dipakai**: menyamakannya KEPUTUSAN, bukan pengukuran.

⇒ Untuk [#89](../../issues/89) (*mana agent, mana service*): **44 dari 59 nama
cuma pernah disebut sekali** — kandidat terkuat untuk *bukan agent*.
💡 **Menjumlahkan daftar bukan menghitung himpunan.**
→ **E-154** / [#150](../../issues/150).

### 🔴🔴 Separuh kedua #38 — dan janji yang tercatat lalu tidak dijalankan

[#38](../../issues/38) punya dua sumbu; yang kedua **awalan rute API**. Sepuluh
catatan menandainya sebagai *“`/v1/…` lagi, bukan `/api/v1`”* — kalimat yang
menempatkan **naskah** di pihak yang menyimpang.

Sensus mengatakan sebaliknya: **111 rute `/v1/…` unik di 12 naskah, dan NOL
`/api/v1`.** 92 di antaranya berbentuk `/v1/<domain>/<...>` — persis bentuk
yang ditetapkan **standar penamaan pemilik sendiri**
([`101`](101-L22-ENGINEERING-STANDARDS.md) Layer 22 `/v1/fashion/outfits`).

⇒ Naskahnya **konsisten**: 111 rute, satu bentuk, nol pengecualian. Yang
menyimpang [`../spec/04`](../spec/04-API-CONTRACTS.md) — **berkas saya**.

🛑 **Dan janjinya sudah tercatat.** Komentar yang **MENUTUP** #38 menulis:
*“yang menyimpang justru `spec/04` yang saya tulis `/api/v1/…`; **itu bagian
saya, akan diselaraskan**”*. Janji itu **tidak pernah dijalankan** — dan sepuluh
catatan sesudahnya terus menandai sisi yang tidak dijanjikan berubah.

✅ **Diselesaikan hari ini**: `spec/04` berawalan `/v1`; endpoint di dalamnya
ditulis tanpa awalan sehingga perubahannya **satu baris**. Bukan keputusan
baru — menjalankan janji yang sudah tercatat.

💡 **PELAJARAN: janji perbaikan yang ditulis di komentar issue yang DITUTUP
tidak punya penjaga.** Issue tertutup berhenti dibaca; catatan berikutnya
mengulang gejalanya tanpa memeriksa apakah pihak yang berjanji sudah bergerak.
**Tanyakan: “ada janji tercatat di sini — siapa yang memeriksanya?”**
→ **E-155**, komentar di [#38](../../issues/38).

### 🔴🔴 Sensus KELIMA: nama tabel — "99" berhenti dipelihara di Phase 12

**E-106** menjumlahkan `23 (V0) + 20 (Fase 8) + 16 (Fase 10) + 14 (Fase 11) +
26 (§12.28) = 99`. ⭐ **Metodenya BENAR** — tiap suku neto, sudah dikurangi yang
sudah ada (§11.48 memberi 18 entitas, empat sudah ada ⇒ 14).

🛑 **Yang salah bukan aritmetikanya, melainkan bahwa ia berhenti di Phase 12.**

| | |
|---|---|
| **nama tabel unik** | **247** di 14 dokumen |
| union sampai Phase 12 | 108 (taksiran neto: 99) |
| **baru sesudah Phase 12** | **139 — belum pernah dihitung** |

Tujuh fase terakhir menyumbang **155 sebutan** — lebih banyak daripada seluruh
hitungan yang pernah diterbitkan.

🛑 **`agent_capabilities` dan `agent_trust_scores` didefinisikan EMPAT kali**
(Phase 8·11·14·18). Audit sudah menandai dua; sensus menemukan dua lagi. Untuk
tabel yang memegang **kapabilitas** dan **kepercayaan** agent, empat definisi =
empat kemungkinan bentuk kolom. Total **19 nama** berdefinisi ganda.

✅ **Divalidasi ENAM kali**, dan yang terkuat mengejutkan: sensus mereproduksi
sendiri pernyataan provenans [`../spec/01`](../spec/01-DATABASE-SCHEMA.md)
(*19 naskah 5 + 3 naskah 6 + 1 usulan*) — tepat 19 ditemukan di naskah 5, dan
tepat tiga nama `spec/01` yang tak ada di naskah mana pun.

⚠️ **Dua kekeliruan alat ukur dilewati dulu:** menuntut garis bawah (membuang
`robots`·`joints`·`missions`; `235` terhitung 11 padahal 17), lalu hanya
memanen fence (`254` §18.28 memakai **backtick** dan hilang seluruhnya).
💡 **Satu format penulisan yang tak diantisipasi bisa menghapus SATU FASE PENUH
dari hasil pengukuran.** → **E-156** / [#151](../../issues/151).

### 🛑🛑 Sensus KEENAM: tangga risiko — dan satu tindakan berpindah MELEWATI ambang konfirmasi

Tangga risiko ditulis **empat kali**, dan jumlah anak tangganya **stabil** —
lima, empat kali berturut-turut (kestabilan yang jarang di repo ini). Yang
bergeser **isinya**: di naskah 4/5 anak tangga 1 adalah *Rekomendasi*; sejak
Phase 8 ia *tindakan berdampak rendah*, dan setiap tindakan turun satu takik
(**E-67**).

Melacak **satu tindakan yang sama** melintasi keempatnya:

| Naskah | “kirim pesan kepada orang lain” |
|---|---|
| naskah 4 §16 | 3 |
| naskah 5 §16 | **3** |
| Phase 8 §8.16 | **R3** — audit di berkas itu mencatat *“Level 3 ǀ R3 ✅ sama”* |
| **Phase 11 §11.15** | 🛑 **R2** — *“send low-risk message”* |

**H-15 ([#5](../../issues/5)) sudah menutup ambangnya: otomatis sampai R2,
konfirmasi wajib mulai R3.** ⇒ **pemindahan itu melewati ambangnya.**

🛑 §11.15 bahkan menaruh pesan di **DUA tingkat dalam satu tabel** — R2
*low-risk message* lawan R3 *important communication* — dipisahkan hanya oleh
kata sifat. Pencarian seluruh `docs/`: **`low-risk` tak pernah didefinisikan.**

⭐ **Tetangganya di baris yang sama DISELAMATKAN, pesan tidak.**
`purchase low-value item` punya cacat identik dan sudah ditandai audit, tetapi
§11.17 memberinya `amount_limit: 0`. §11.17 memberi bawaan untuk kalender,
notifikasi (kepada penggunanya sendiri), dan pembelian — **tak ada entri untuk
pesan kepada pihak ketiga**; §11.18 mendaftar `Messages` tanpa pernah memberinya
nilai.

🔴 **Dari tiga kategori di baris R2, yang tidak mendapat definisi maupun angka
bawaan justru satu-satunya yang punya ORANG LAIN di ujung penerimanya.**
**C-19** ([#81](../../issues/81)) mengandalkan R3⇒konfirmasi untuk melindungi
penerima dan mencatat *“important communication di R3”* — **ia tidak melihat
baris R2 di tabel yang sama.** → **B-39** / [#152](../../issues/152).

💡 **Teknik yang menemukannya: ambil SATU tindakan konkret, lacak nilainya di
tiap versi tangga, lalu bandingkan dengan AMBANG yang sudah ditutup.**
Membandingkan tangganya saja hanya memperlihatkan "turun satu takik";
melacak satu tindakan memperlihatkan **yang mana yang menyeberang**.

### ⭐ Sensus KETUJUH: rantai keputusan — dan yang ini membawa kabar BAIK

Tujuh catatan melaporkan *“rantai tanpa gerbang”* (*kelima · keenam · ketujuh*)
**tanpa pernah menyebut penyebutnya**. *“Rantai ketujuh”* tidak bisa dibaca
tanpa tahu **dari berapa**.

| | |
|---|---|
| rantai ber-panah di naskah | **387** |
| berakhir di tindakan | **36** (31 berkas) |
| **punya gerbang** | **20** |
| tidak | 16 |

⭐ **Dua puluh dari tiga puluh enam SUDAH dijaga** — angka itu belum pernah
ditulis. Catatan sebelumnya hanya melaporkan yang gagal.

🔍 **Dari 16 yang ditandai, 10 BUKAN cacat**: dekomposisi tujuan yang berakhir
di tindakan **penggunanya sendiri**, gelung observasi, rantai **provenans**
(arahnya mundur), pipeline CI/CD, **kill-switch**, dan rantai **lapisan
keselamatan** itu sendiri. Dua lagi sudah tertangani (§16.26 di hulu; #140).

🛑 **Tiga benar-benar baru, dan ketiganya menggerakkan benda fisik** — di luar
cakupan [#106](../../issues/106) (§15.22) dan [#111](../../issues/111)
(§16.18·§16.13·§16.34):

- **§15.15** `Hand Tracking → Gesture Recognition → Intent → Action` —
  **lambaian tangan menjadi tindakan tanpa satu simpul pun di antaranya**,
  sementara §15.22 di naskah yang sama punya `Permission`;
- **§16.5** `Human Goal → World Model → Motion Planner → Joint Controller →
  Execution` — pipa utama humanoid, **dari tujuan manusia langsung ke kendali
  sendi**, dan kemampuannya termasuk *“membuka pintu”*;
- **§16.7** `… → Collision Check → Optimization → Execution` — ⭐ punya
  `Collision Check`, 🛑 tapi itu menjawab *“aman secara fisik”*, bukan
  *“boleh dilakukan”*.

⚠️ **Dua kekeliruan alat ukur, keduanya membuat hasil tampak lebih aman:**
(a) hanya membaca rantai MENDATAR — rantai VERTIKAL (`↓` 507, `▼` 311)
terlewat, padahal itu bentuk yang dipakai naskah 5 untuk jalur konfirmasi;
(b) kata `HUMAN` diperlakukan gerbang sehingga **`Human Detection` terhitung
sebagai persetujuan manusia**.
💡 **Kata yang sama bisa menandai pengaman ATAU sensor yang MEMICU tindakan —
`Human Detection` di rantai robot adalah pemicu, bukan rem.**
→ **E-157** / [#153](../../issues/153).

### ✅ Pemeriksaan penutup: delapan sensus, **nol penghambat skema baru**

[`GERBANG-SKEMA.md`](GERBANG-SKEMA.md) seluruh tugasnya menjawab *“apakah ada
yang terhalang”*. Delapan pengukuran dengan angka besar (247 tabel · 128 event ·
59 agent) **mudah terbaca sebagai delapan penghambat baru**, jadi tiap temuan
diperiksa satu per satu terhadap `spec/`:

| Temuan | Menyentuh V0? |
|---|---|
| 247 nama tabel | ❌ `spec/01` tetap **23**; 139 nama baru milik Phase 14–20 |
| 128 nama event | ❌ `spec/03` tetap **22** dua segmen |
| 59 nama agent | ❌ V0 memakai **4**; 44 dari 59 cuma disebut sekali |
| **B-39** pesan di R2 | ❌ untuk V0 — `spec/05`: **V0 tidak punya tool level 3/4**. ⚠️ mendesak untuk Phase 11+ |
| 3 rantai tanpa gerbang | ❌ Phase 15 & 16 |
| awalan API | ✅ **diperbaiki**, satu baris |

⇒ **Penghambat V0 tetap dua dan tetap bukan soal skema:
[#3](../../issues/3) dan [#20](../../issues/20).**

💡 Ini menerapkan aturan berkas itu sendiri kepada diri sendiri: **sebelum
menyatakan sesuatu terhalang, buka berkas yang paling berkepentingan
membantahnya.**

### 🔧 DUA BELAS keputusan diambil sendiri — atas permintaan pemilik

Pemilik mendelegasikan: *“beri keputusan sendiri sesuai aturan”*. Batas yang
saya pegang: **yang engineering saya putuskan; yang salahnya ditanggung orang
lain tetap milik pemilik.** Semuanya di
[`KEPUTUSAN-DIDELEGASIKAN.md`](KEPUTUSAN-DIDELEGASIKAN.md), tiap butir dengan
**bacaan yang DITOLAK** dan **cara MEMBALIKKANNYA**.

| | Keputusan | Ditegakkan di | Issue |
|---|---|---|---|
| **K-1** | kapabilitas menyentuh **pihak ketiga** = min **R3** | `spec/05` aturan 7 + medan `reaches_third_party` | [#152](../../issues/152) ✅ |
| **K-2** | `world-model/` **menyimpan**, `simulation/` **menjalankan** | — | [#147](../../issues/147) ✅ |
| **K-3** | **127 nama event** dipadankan; naskah **tak diubah** | `spec/03` tabel padanan | [#149](../../issues/149) ✅ |
| **K-4** | tabel ganda: `spec/01` menang, lalu fase terawal | `spec/01` | [#151](../../issues/151) ✅ |
| **K-5** | **tiga uji** agent lawan service | `spec/05` | [#89](../../issues/89) ✅ |
| **K-6** | tujuh **kata kerja** Phase 2–8 | — | [#142](../../issues/142) sebagian |
| **K-7** | §15.15 dapat `Permission` | — | [#153](../../issues/153) sebagian |
| **K-8** | awalan API `/v1` | `spec/04` | [#38](../../issues/38) |
| **K-9** | **satu monorepo** + **uji naik-turun**; keamanan **19 pohon → satu** | — | [#55](../../issues/55) ✅ |
| **K-10** | **satu amplop event**; `SecurityEvent` → `security.*` | `spec/03` | [#63](../../issues/63) ✅ |
| **K-11** | tiap tangga bernomor membawa **awalan** | — | [#54](../../issues/54) ✅ [#56](../../issues/56) ✅ |
| **K-12** | `risk_level` **wajib**; larangan scope diperluas | `spec/05` aturan 8 & 9 | [#77](../../issues/77) sebagian |

⚠️ **Nol dari dua belas mengubah V0** — `spec/01` tetap 23 tabel, `spec/03` tetap
22 event V0, keempat agent V0 lulus ketiga uji K-5. Diperiksa sesudahnya.

⭐⭐ **K-9 membuka blokir Sprint 0 tugas 0.1.** [#55](../../issues/55) menanyakan
satu hal: pohon fase baru itu **folder di dalam monorepo** atau **repo
terpisah**? Jawabannya **satu monorepo**, dan yang membuatnya bisa ditegakkan
adalah **uji naik-turun dengan TIGA hasil**: naik (hal yang sama) · tinggal
(khas fase) · **diganti nama** (kata yang sama untuk hal berbeda).
🔑 **Hasil ketiga itu yang menyelamatkan aturannya dari menjadi “gabungkan
semuanya”** — `simulation/` di 15 pohon ternyata **tiga mesin berbeda dengan
satu kata** (fisika · perilaku · fisiologi), jadi ia diganti nama, bukan
digabung.
🛑 Dan alasan terkuatnya bukan kerapian: keluarga keamanan tersebar di
**19 pohon**, dan selama itu benar **aturan impor §8.42 (*kode agent tidak boleh
mengimpor `security/`*) tidak bisa DINYATAKAN** — tidak ada satu `security/`
untuk dirujuk.

⭐⭐ **Dua keputusan menolak bawaan yang “masuk akal”, dan alasannya sama:**
K-12 menolak `risk_level: 0` sebagai bawaan — **tool yang LUPA diberi tingkat
risiko akan otomatis menjadi yang paling tidak dijaga**; K-10 menolak amplop
khusus untuk security event — **empat medan yang hilang darinya justru yang
membuat event bisa DIAUDIT**, dan security event yang paling mungkin diaudit.
💡 **Tanyakan pada tiap bawaan: kalau seseorang LUPA mengisinya, ke sisi mana
ia jatuh?**

🛑 **Yang sengaja TIDAK saya putuskan**, dan alasannya satu: **kalau salahnya
ditanggung orang lain, keputusannya bukan milik saya.**
[#139](../../issues/139) (waktu pemilik) · [#3](../../issues/3) (orang) ·
[#20](../../issues/20) (merek) · **seluruh butir C** · **§16.5 & §16.7**
(humanoid — benda yang bisa melukai orang) · [#34](../../issues/34) (menebak
ambang lebih buruk daripada membiarkannya terbuka) · **B-25** di
[#77](../../issues/77) (deteksi bias sistematis — salahnya ditanggung pengguna).

⭐ **Yang paling menentukan dari delapan: K-1 dan K-5 ditegakkan VALIDATOR,
bukan prosa.** Pelajaran repo ini sendiri — *“aturan yang dinyatakan tetapi
tidak dijaga”* — sudah muncul berkali-kali; keputusan yang cuma ditulis akan
bernasib sama.

### 📋 Daftar tutup sesi — apa yang menunggu sesi berikutnya

**Sisa milik pemilik, dan hanya pemilik:**

| Butir | Kenapa |
|---|---|
| **[#139](../../issues/139)** Master Architecture v2.0 | soal **waktu pemilik**. Bukti 3× permintaan + ringkasan 8 pengukuran sudah dipasang di issue-nya |
| [#3](../../issues/3) siapa mengerjakan V0 · [#20](../../issues/20) cek merek | orang, uang, pembelian |
| **seluruh butir C** | risikonya ditanggung orang yang tidak ikut memilih |
| **B-25** di [#77](../../issues/77) · §16.5 & §16.7 di [#153](../../issues/153) | salahnya ditanggung pengguna, atau benda yang bisa melukai orang |
| [#34](../../issues/34) ambang Confidence | butuh data nyata; menebak lebih buruk daripada membiarkannya terbuka |
| Nama **Phase 1** · apakah §10.41 digantikan ([#142](../../issues/142)) | tak ada bahannya di repo |

**Yang bisa dikerjakan tanpa pemilik, kalau sesi berikutnya mau lanjut:**

- terapkan **uji naik-turun K-9** ke ~40 nama sisa di ≥3 pohon
  ([`SENSUS-MODUL.md`](SENSUS-MODUL.md) Tabel B) — mekanis, aturannya sudah ada;
- **[#30](../../issues/30)** PromptOps 7 dari 14 agent — angkanya berubah sesudah
  **K-5** menyaring mana yang benar-benar agent;
- **[#41](../../issues/41)** batas Knowledge lawan Memory — uji K-9 berlaku,
  tetapi batas isinya masih perlu dibaca dari naskah.

⚠️ **Sebelum menyentuh apa pun**: `git status` · `git log` ·
`grep -n "^## Sesi" docs/SESSION-LOG.md`. Sesi paralel sudah terjadi 3×, dan
selama sesi ini pun entri memori proyek lain diperbarui sesi lain.

---

### Yang menunggu keputusan pemilik

Tidak berubah: **[#139](../../issues/139) — Master Architecture v2.0 dimulai
sekarang atau tidak.** Yang berubah hanya bahannya — butir pertamanya
(*“menghapus overlap antar-modul”*) sekarang punya **daftar 128 nama** yang bisa
dicoret satu per satu.

---

## Sesi 24 — 8 September 2026

**Tidak ada naskah baru. Seluruh dokumen disusun berurutan dan kelengkapannya dibuktikan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **tidak ada** — pemilik menghentikan perekaman di Phase 20 |
| Dokumen ditambah | **1 berkas** ([`00-DAFTAR-ISI.md`](00-DAFTAR-ISI.md)) |
| Dokumen total | 263 → **264** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | tetap **145** (125 terbuka, 20 ditutup) |
| README | 735 → **481 baris** (−254): bagian *Peta dokumen* yang tak lengkap diganti penunjuk |

### ✅ Kelengkapan DIBUKTIKAN, bukan diklaim

Diperiksa dengan skrip, dan diperiksa ulang dengan **pemeriksa kedua yang
terpisah** dari pembangunnya:

| Pemeriksaan | Hasil |
|---|---|
| Berkas `docs/` terdaftar di daftar induk | **263 = 263** |
| Berkas terdaftar >1 kali di tabel pendaftaran | **NIHIL** |
| Berkas ada tapi tidak terdaftar | **NIHIL** |
| Berkas terdaftar tapi tidak ada | **NIHIL** |
| Nomor ganda | **NIHIL** |
| Berkas tanpa `H1`, atau `H1` yang nomornya tak cocok nama berkas | **NIHIL** |
| Berkas yang tak bisa ditelusuri ke commit penambahnya | **NIHIL** |
| Tautan `.md` rusak di seluruh 264 berkas | **NIHIL** |
| Jangkar `#naskah-N` mati | **NIHIL** |

### 🔍 Empat belas nomor yang tampak hilang ternyata bukan dokumen hilang

`8–9` · `23–29` · `47–49` · `78–79` tidak ada di `docs/`. Dua pemeriksaan
menutup pertanyaannya:

1. `git log --all --diff-filter=D` — **tidak pernah** ada berkas dengan nomor
   itu yang dihapus;
2. pencarian tautan di seluruh `docs/` — **nol** rujukan kepadanya.

⇒ Keempat celah jatuh **persis di batas antar blok naskah** (naskah 1→2,
2→3, 3→4, 4→5): ruang yang sengaja disisakan. **Nol dokumen hilang.**

### 🛑 Yang benar-benar kurang: peta dokumen di README

Bagian *Peta dokumen* README memuat **126 dari 263** berkas — ia berhenti
dipelihara di berkas `141` (naskah 11), dan 137 dokumen dari naskah 12–24
tidak pernah masuk. Keterangannya ditulis tangan dan lebih kaya daripada judul
`H1`, jadi ia **tidak dibuang**: 126 keterangan itu diekstrak dan digabungkan ke
daftar induk, dengan judul `H1` sebagai isian untuk 137 sisanya. Kolom *Isi*
kini terisi untuk **semua** baris.

### ⚠️ Nama berkas SENGAJA tidak dinomori ulang

Penomoran campur dua/tiga digit membuat urutan abjad `ls` salah
(`10` · `100` · `101` · `11` · `99`). Penomoran ulang menjadi tiga digit
seragam akan memperbaikinya — tetapi **34 GitHub Issue yang sudah terbit menaut
berkas dua digit**, dan isinya tidak bisa diperbaiki dari sisi repo. Biaya itu
lebih besar daripada manfaatnya, jadi urutan yang benar diberikan lewat daftar
induk, dan alasannya dicatat di Lampiran C.

### Yang menunggu keputusan pemilik

Tidak berubah dari sesi lalu, dan kini menjadi satu-satunya pekerjaan di depan:
**[#139](../../issues/139) — Master Architecture v2.0 dimulai sekarang atau
tidak.** Pemilik sendiri yang mengusulkannya di penutup naskah 24
(*“jangan langsung membuat Phase 21”*).

---

## Sesi 23 — 8 September 2026

**Phase 20 direkam — fase terakhir, dan naskahnya menutup lebih banyak butir daripada yang dibukanya.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 20: Civilization Platform**, 39 bagian — **fase TERAKHIR** |
| Dokumen ditambah | **10 berkas** (`266`–`275`) |
| Dokumen total | 253 → **263** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 138 → **145** (125 terbuka, 20 ditutup); **#139**–**#145** baru |
| Temuan | **A-35** · **B-38** · **C-30** · **E-148**–**E-150** · **G-19** · **empat belas** butir **F** |

### ⭐⭐⭐⭐⭐ Penutupnya adalah paragraf terpenting dalam 24 naskah

Pemilik mengusulkan sendiri: *“sesudah Phase 20 **jangan langsung membuat Phase
21** … buat **HumanVerse Master Architecture v2.0**”* — menyatukan Phase 1–20,
menghapus overlap antar-modul, bounded context final, dependency graph, monorepo
final, event contracts, agent contracts, dan **urutan implementasi nyata dari
V0 → production**.

Itu menyentuh hampir tiap penghambat terbuka: **H-10 yang tergerus SEPULUH kali**
([#55](../../issues/55) · [#129](../../issues/129) · [#138](../../issues/138) ·
[#143](../../issues/143)) · [#38](../../issues/38) · sepuluh pasal Konstitusi
tanpa penegakan · **H-13**/[#72](../../issues/72) — satu-satunya penghambat yang
memisahkan repo ini dari baris kode pertama · **A-34**/[#133](../../issues/133).

⭐⭐ Dan yang paling bernilai: **sepuluh naskah terakhir masing-masing menambah
satu fase dan satu pohon tingkat-atas; ini pertama kalinya pemilik mengusulkan
BERHENTI MENAMBAH.** → **A-35** / [#139](../../issues/139).

### ⭐⭐⭐⭐⭐ Dua jawaban struktural yang belum pernah ada

**§20.16 Agent Constitution** — sepuluh pasal, dan **tiga menutup butir lama
sebagai ATURAN**: Pasal 5 *Reversibility* (**H-21**) · Pasal 9 *No unauthorized
autonomy* ([#99](../../issues/99), [#111](../../issues/111)) · Pasal 10
*Human override* (**H-15**, dan override lebih kuat daripada konfirmasi: ia
berlaku **selama** aksi). Pasal 8 *no deceptive behavior* belum pernah ada di
mana pun — tanpanya Pasal 1 dan 10 kehilangan artinya. ⭐⭐ **Dan bentuk
“konstitusi” menyelesaikan pola yang muncul LIMA kali** (keselamatan dijadwalkan
sesudah yang dijaganya): **konstitusi tidak punya nomor urut.**

**§20.35 Safety Boundary** — memisahkan `ANALYSIS` dari `ACTION` sebagai dua
**cabang**, dan hanya membebani cabang kedua (`POLICY → RISK → IMPACT
ASSESSMENT → HUMAN APPROVAL`), dengan `AUDIT` menampung keduanya. **Lebih baik
daripada semua usul sebelumnya, termasuk milik saya**: menganalisis tetap murah
(pengaman yang memperlambat segalanya akan dilonggarkan — itu cara pengaman
biasanya mati), dan bertindak tak punya jalan pintas.

🛑 **Tetapi lima jalur menuju tindakan di naskah yang sama tidak
melewatinya** — §20.3, §20.24, §20.38, §20.23, dan
`POST /v1/civilization/coordination`. Ketiga kalinya berturut-turut gerbangnya
ADA dan tidak dipasang. ⭐ §20.38 memberi slotnya: **`DELIBERATE`**.
→ **E-150** / [#140](../../issues/140).

### 🛑 Temuan berat lain

**C-30** ([#141](../../issues/141)) — `Utility = Benefit − Risk − Cost −
Externality + Resilience` menjumlahkan **lima satuan berbeda**, dan
*“dikontrol manusia”* menjawab *bukan mesin*, bukan **siapa**: pada skala
peradaban, **yang menetapkan bobot dan yang menanggung eksternalitas hampir
tidak pernah orang yang sama** — itu justru definisi eksternalitas. Tiga bentuk
lain: `Family` sebagai tingkat kembaran (anggota keluarga tak punya akun, dan
sebagian **tidak bisa** memberi persetujuan) · **`Human Labor` di daftar sumber
daya yang akan *dioptimalkan*** (bentuk [#122](../../issues/122) pada skala
terbesarnya) · `Government / Institution` sebagai simpul setara. Dan **§20.22
adalah fungsi tujuan KEDUA**, beririsan dengan §20.9 hanya pada `Resilience`.

**E-148** ([#142](../../issues/142)) — *“Peta Akhir 20 Fase”* memuat **dua belas**
baris; `grep "Phase [1-8] +[A-Z]{3,}"` → **nol** di 24 naskah.
[#133](../../issues/133) **setengah** terjawab.

**G-19** ([#144](../../issues/144)) — naskah ini **tidak punya Definition of
Done**, pertama sejak naskah 20. ⭐ Tapi governance **NAIK** dari posisi terakhir
untuk pertama kali dalam empat naskah: `R16.10` → `H17.12` di luar MVP → nol →
`S19.10` → **`C20.7` dari 12**. 🛑 `C20.6 Coordination` tetap sebelumnya —
kelima berturut-turut.

### ⭐ Sebelas butir F lain

§20.30 **jawaban delapan bagian** (`EVIDENCE` · `HOW CERTAIN` · `WHAT OPTIONS` ·
`WHAT YOU CAN DO`) — memberi `Answer` §18.30 bentuk wajib · §20.20 **menjawab
sebagian besar [#123](../../issues/123)** (`Verification` + `Response Options`
jamak + *“bukan otoritas tunggal”*) · §20.12 **tujuh mekanisme privasi bernama**,
dua di antaranya tepat yang [#126](../../issues/126) minta · §20.10 +
`collective-intelligence/disagreement/` **menutup sisa [#121](../../issues/121)**
— prinsipnya kini di **tiga** tempat berturut-turut · §20.17 mengembalikan
`Approval` (hilang dari lima rantai) dan menambah `Impact`/`Stakeholders`/
`Simulation` · §20.37 berakhir di **`HUMAN SOVEREIGNTY`** · §20.19 `resilience`
sebagai tujuan yang berbeda dari efisiensi · §20.32 **menggabungkan tiga pasar**
dan `Billing` akhirnya muncul · §20.34 *“tidak boleh menjadi closed
ecosystem”* — pengaman pertama yang membatasi **kekuasaan platformnya sendiri**.

---

## Sesi 22 — 8 September 2026

**Phase 19 direkam — dan naskahnya merujuk peta fase yang tidak pernah ada, sambil memperbaiki cara peta itu diubah.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 19: Scientific Discovery Engine**, §19.1–§19.34 |
| Dokumen ditambah | **10 berkas** (`256`–`265`) |
| Dokumen total | 243 → **253** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 130 → **138** (118 terbuka, 20 ditutup); **#131**–**#138** baru |
| Temuan | **A-34** · **B-37** · **C-29** · **E-144**–**E-147** · **G-18** · dua belas butir **F** |

### 🛑🛑🛑 Temuan terbesar: peta yang dirujuk tidak punya berkas

Naskah 23 membuka dengan *“roadmap **20 fase** yang sudah kita tetapkan
sebelumnya”*, lalu mengubah isi **Phase 19** (Civilization Intelligence →
Scientific Discovery Engine) dan memindahkan Civilization ke **Phase 20**.

```
grep -rioE "dua puluh fase|20 fase|phase 20" docs/ spec/ README.md
→ 0
```

Nomor fase tertinggi yang pernah disebut adalah **Phase 19** — dengan isi
**berbeda**, dari naskah 22. Yang pernah ditulis cuma **v1** (15 fase, §10.41)
dan **v2** (terbuka-ujung).

⇒ Ini **akibat yang E-128/[#108](../../issues/108) ramalkan**, bukan kekeliruan
mengingat: peta terbuka-ujung tanpa versi melahirkan rujukan balik ke rencana
yang tidak bisa dibuka. **Ketika tidak ada dokumen untuk memeriksa *“apa yang
sudah kita tetapkan”*, yang tersisa cuma ingatan — dan ingatan tidak bisa
di-`grep`.** → **E-144** / [#132](../../issues/132), **A-34** /
[#133](../../issues/133).

### ⭐⭐⭐⭐ Tapi ini juga perubahan peta PERTAMA yang diumumkan dengan alasannya

Pemilik menyatakan ia mengubah sesuatu, memberi alasannya (*agar Phase 19 tidak
tumpang tindih dengan Phase 18* — benar secara teknis: §18.4 sudah menelan
`scientific publications`), menunjukkan susunan barunya, dan menyebut **Phase 20
sebagai fase TERAKHIR**. Empat hal yang tak satu pun ada pada
§10.41→SpatialOS (**E-123**, yang mematahkan **H-20**) maupun tiga perpanjangan
sesudahnya. Ini persis yang [#101](../../issues/101) minta — dan **ujung pertama
yang dinyatakan sejak §10.41**. Yang perlu tinggal: **tuliskan kedua puluh
fasenya sebagai daftar di satu berkas.**

### 🛑🛑🛑 Keselamatan terakhir untuk naskah KEEMPAT — dan kali ini menggerakkan materi fisik

§19.22 menyebut Ethics Governance ***“komponen wajib”***; §19.33 menaruhnya di
`S19.10`, terakhir dari sepuluh.

| Naskah | Milestone | Posisi |
|---|---|---|
| 20 | `R16.10` | terakhir dari 10 — [#111](../../issues/111) |
| 21 | `H17.12` | di luar MVP — [#116](../../issues/116) |
| 22 | — | tidak ada — [#121](../../issues/121) |
| **23** | **`S19.10`** | **terakhir dari 10** |

🔴 Yang menjadikannya kelas tersendiri: **§19.15 Digital Laboratory**
(`robotic pipette` · `liquid handler` · `experiment scheduler`) — *“HumanVerse
**mengirimkan protocol** ke lab automation”*. **Satu-satunya tempat di 23 naskah
di mana HumanVerse menggerakkan materi fisik atas dasar kesimpulannya sendiri**,
dan tiga pengaman absen: `ACTION GATEWAY`/`GOVERNANCE MESH` (naskah **kelima**
berturut tanpanya), `Confirmation` (**H-15**), dan §19.22 sendiri — yang tidak
berdiri di rantai mana pun. → **C-29** / [#131](../../issues/131).

⭐⭐⭐⭐ **Jawabannya ditulis pemilik sendiri dua bagian sebelumnya**, §19.23:
***“Semakin tinggi risiko, semakin ketat governance”*** — kalimat yang sama
dengan penutup §17.56. **Naskah ini memuat aturannya dan pelanggarannya
sekaligus**, dan karena prinsip itu kini muncul di **dua naskah terpisah**, ia
berhenti menjadi tafsir dan menjadi posisi pemiliknya.

### ⭐⭐⭐⭐⭐ §19.17 menutup separuh #121 — usul satu naskah lalu, dipakai

**G-17** mengusulkan: *“konsensus hanya menyatukan hal yang sumbernya sepakat;
ketidaksepakatan naik ke pengguna sebagai ketidaksepakatan.”* §19.17 memberi
`Debate → **Consensus** → **Remaining Disagreement**` — bukan memilih di antara
keduanya, melainkan **mengeluarkan keduanya**. Lebih baik daripada usulnya.
⚠️ Sisa: G18.8 sendiri belum diperbaiki.

Bersamanya, sebelas butir **F** lain — di antaranya **§19.20 *“sitasi harus
nyata, tidak boleh mengarang referensi”*** (larangan pada KELUARAN, jenis yang
bisa diuji) · **§19.10** menuliskan kekeliruan menegaskan konsekuen dengan BENAR
lalu menolaknya · **§19.25 mengembalikan registri model** yang naskah 22
hilangkan ([#127](../../issues/127)), lebih lengkap dari aslinya (`bias`,
`limitations`) · **§19.14 `Distribution`** memperbaiki `31+46+23=100` §18.10 ·
**§19.19 `seed tercatat`** · **§19.3 *“Berbeda dengan World Knowledge Graph”*** —
pertama kalinya sebuah naskah MENDAHULUI tabrakan penamaan.

### 🔴 AetherScan naik pangkat lagi — satu naskah sesudah diturunkan

§18.13 menurunkannya menjadi *“salah satu spatial sensing provider, bukan bagian
inti”*, dan saya mencatatnya sebagai butir **F berbintang empat** karena ia
keputusan pemilik yang **mengurangi cakupan**. Satu naskah kemudian §19.30
memberi **`scientific-discovery/labs/aetherscan/`**.

⇒ **Ini H-8 dalam bentuk terbaliknya**, dan pelajarannya baru: **keputusan yang
MEMPERKECIL cakupan juga perlu diperiksa ulang di naskah berikutnya — ia tidak
lebih tahan daripada keputusan yang memperbesar.** Dicatat sekaligus sebagai
koreksi atas penilaian saya sendiri. → **E-147** / [#136](../../issues/136).

### ⚠️ Sisanya

**§19.1 *“Posisi dalam Arsitektur HumanVerse”* KOSONG** — ketiga kalinya, dan
ketiganya jenis yang sama (§15.1 → #103, §16.33 → #113); justru di fase yang
paling banyak bertumpang tindih. Plus **empat butir DoD tanpa milestone**,
termasuk `provenance` — kemunduran dari `G18.1` naskah 22 yang menaruhnya
**pertama**. → **G-18** / [#137](../../issues/137).

**§19.27 membalik DUA urutan yang naskahnya sendiri tetapkan**: hipotesis
sebelum literatur (§19.2 memberi kebalikannya) dan eksperimen sebelum simulasi
(§19.13 membuka dengan *“Simulation sebelum eksperimen”*). → [#136](../../issues/136).

**Rantai provenance kedua kehilangan `Transformation` dan `Policy`** — tepat dua
mata yang menjadikan §18.21 berbintang empat; `Evidence Ranking` kini di **tiga**
tempat; kosakata risiko jadi **empat**. → **E-146** / [#135](../../issues/135).

**`scientific-discovery/` = H-10 kesembilan**, pohon keamanan jadi **sepuluh**,
dan `governance/` naskah 22 **tidak diwarisi** — pembuktian langsung atas
keberatan [#129](../../issues/129), satu naskah kemudian.
→ **E-145** / [#138](../../issues/138).

---

## Sesi 21 — 8 September 2026

**Phase 18 direkam — dan Safety Kernel yang naskahnya sendiri sebut “sangat penting” tidak punya milestone sama sekali.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 18: Global Intelligence Network**, §18.1–§18.34 |
| Dokumen ditambah | **10 berkas** (`246`–`255`) |
| Dokumen total | 233 → **243** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 114 → **130** (110 terbuka, 20 ditutup); **#115**–**#120** menutup utang Sesi 20, **#121**–**#130** baru |
| Temuan | **A-33** · **B-35**–**B-36** · **C-27**–**C-28** · **E-138**–**E-143** · **G-17** · tujuh butir **F** |

### 🛑 Utang Sesi 20 dibayar lebih dulu — dan urutannya tidak bisa dibalik

Sesi 20 menulis sepuluh dokumen dan 107 baris audit, lalu **berhenti sebelum
membuat issue-nya, menulis catatan sesi, dan commit**. Akibatnya **14 tautan
menggantung di 7 berkas**: dokumen sudah menulis `#115`–`#120`, sementara GitHub
masih berhenti di 114.

Nomor issue GitHub diberikan **berurutan dan tidak bisa dipilih**. Kalau naskah
22 diproses lebih dulu dan membuat issue apa pun, keenam nomor itu terpakai dan
ke-14 tautan **patah permanen**. Jadi #115–#120 dibuat lebih dulu, satu per satu,
sesuai pemetaan yang sudah saling-rujuk konsisten di dalam dokumennya sendiri
(C-25 menunjuk B-33 sebagai #116, B-33 menunjuk C-25 sebagai #115).

→ Verifikasi akhir: **109 nomor issue dirujuk seluruh `docs/`, nol menggantung**,
dan **seluruh 16 issue baru dirujuk dokumen**.

### 🛑🛑🛑 Keselamatan turun untuk naskah KETIGA — dan lintasannya tetap

| Naskah | Milestone keselamatan | Posisi |
|---|---|---|
| 20 (Phase 16) | `R16.10` | terakhir dari 10 — #111 |
| 21 (Phase 17) | `H17.12` | di luar MVP — #116 |
| **22 (Phase 18)** | **—** | **tidak ada sama sekali** |

§18.22 Global Intelligence Safety Kernel tidak muncul di sepuluh milestone
§18.32 maupun di 21 butir DoD §18.33. `G18.5 Information Integrity` mencakup
**§18.23**, bukan §18.22 — keduanya menjawab pertanyaan yang berbeda:
*“apakah informasi ini benar”* lawan *“apakah masukan ini menyerang saya”*.

Ditambah **empat butir DoD tanpa milestone**: `privacy boundaries` ·
`governance` · `agent trust/reputation` · dan Safety Kernel yang bahkan tak masuk
DoD. Pengulangan persis **B-33** (#116) — naskah kedua berturut-turut.
→ **G-17** / #121.

### 🛑🛑🛑 `productivity` atas `People` adalah larangan §8.10 yang datang sebagai fitur

§8.10 menyebut tiga tujuan terlarang secara harfiah: `advertising` ·
`insurance scoring` · **`employment scoring`**. §18.12 menaruh `productivity`
paling depan di delapan analisis, dan `People` paling depan di sembilan komponen
organisasi.

Lebih berat dari **C-12** (#46): Phase 17 sudah menambahkan `recovery_score`,
`training_load`, `stress`, dan `sleep` ke sistem yang sama.

🔴 Dan **seluruh model persetujuan dua puluh dua naskah terbalik di bagian ini
tanpa disebut**: di semua fase sebelumnya yang membayar dan yang datanya dipakai
adalah orang yang sama — itu yang membuat `consent`, `purpose`, dan Privacy
Center masuk akal. Organization Intelligence memperkenalkan pihak ketiga:
**organisasi pelanggannya, karyawan subjek datanya**. → **C-27** / #122.

### 🛑🛑 Tangga kausal KEDUA — lima tingkat, satu naskah sesudah empat tingkat

§17.9 memberi empat tingkat dan menutup **E-81** (#7), butir tertua di repo ini,
dengan aturan: **hanya `Causal evidence` yang boleh menjadi dasar rekomendasi.**
§18.9 menambahkan **`Causal Conclusion`** di atasnya ⇒ aturan itu berhenti bisa
dibaca.

Pola **ketiga** pada sumbu berbeda (**E-77**/H-21 · **E-133**/#117 · di sini) —
dan yang ini **paling tajam sebab jaraknya SATU naskah**. → **E-138** / #124.

### ⭐ Yang paling berharga: gerbangnya ADA, cuma tidak dipasang

§18.30 Query Engine (sepuluh langkah) dan §18.10 Simulation keduanya berakhir di
pengguna **tanpa `Safety`, `Policy`, maupun `Risk`** — rantai kelima yang
begitu. Tetapi berbeda dari **E-117**/**E-124**/**E-130**, di sini gerbangnya
**ada di naskah yang sama** (§18.22), dua belas bagian sebelumnya.

⇒ Ini **masalah perkabelan, bukan rancangan**, dan karenanya jauh lebih murah.
→ **E-143** / #125.

### ⭐⭐⭐⭐⭐ `UNRESOLVED` sebagai keluaran yang sah — belum pernah ada

§18.23 mengizinkan sistem **berhenti tanpa jawaban**: *“Conflict detected ·
confidence 0.61 · Status: UNRESOLVED”*. Setiap mekanisme keyakinan sebelumnya
berakhir dengan **memilih**. Ini yang paling berlawanan dengan tekanan produk,
dan yang paling menaikkan kelayakan dipercaya.

Bersamanya: **§18.24 memisahkan `Probability` dari `Confidence`** dan menambah
`Horizon` (klaimnya bisa diperiksa ketika 90 hari lewat) · **§18.32 urutan
roadmap terbaik dalam lima naskah** (`provenance` di milestone pertama,
Information Integrity mendahului semua yang menalar) · **§18.31 contoh terbaik
di 22 naskah** (memisahkan sebab dunia dari sebab perilaku) · **§18.15 rantai
keamanan terlengkap di sembilan naskah** · **§18.13 menurunkan pangkat
AetherScan** — keputusan pemilik yang **mengurangi** cakupan, jenis paling
jarang di repo ini.

### ⚠️ Peta fase diperpanjang KEEMPAT kali — Phase 19 Civilization Intelligence

naskah 19 → Phase 16 · naskah 20 → Phase 17 · naskah 21 → Phase 18 ·
**naskah 22 → Phase 19**. Usul **E-128** (#108) — beri versi pada peta fase —
berhenti menjadi kerapian dan menjadi syarat agar sebuah dokumen bisa menyebut
rencana mana yang dipakainya. → **E-142**.

Dan `global-intelligence/` menggerus **H-10 untuk kedelapan kalinya** (pohon
keamanan jadi **sembilan**; `protocols/` dan `provenance/` muncul **dua kali di
dalam pohon yang sama**). ⭐ Tapi **`governance/` akhirnya muncul** — pertama
kali sejak diminta di naskah 18 — sayangnya **di dalam pohon fase**, sehingga ia
tidak bisa mengatur `robotics/`, `health-bio/`, maupun `agents/`.
→ **E-139** / #129.

---

## Sesi 20 — 7 September 2026

**Phase 17 direkam — fase paling sensitif dari semuanya, dan naskah yang paling banyak menjawab butir lama.**

> ⚠️ **Sesi ini berhenti sebelum menutup diri.** Sepuluh dokumen dan 107 baris
> audit ditulis, tetapi **issue-nya tidak dibuat, catatan sesi tidak ditulis, dan
> tidak ada commit** — sehingga 14 tautan ke `#115`–`#120` menggantung sampai
> Sesi 21 membayarnya. Baris di bawah ini direkonstruksi dari berkasnya.

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 17: Human Health & Bio Intelligence**, §17.1–§17.56 |
| Dokumen ditambah | **10 berkas** (`236`–`245`) |
| Dokumen total | 223 → **233** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | direncanakan **#115**–**#120** — baru benar-benar dibuat di Sesi 21 |
| Temuan | **B-33**–**B-34** · **C-25**–**C-26** · **E-133**–**E-137** · empat butir **F** berbintang empat |

### ⭐⭐⭐⭐ Naskah yang paling banyak menutup butir lama

**§17.9 menutup E-81** — butir tertua di repo ini — dengan **empat tingkat
bukti**, dan menutupnya lebih baik daripada usul saya. **§17.38 mengembalikan
`Risk Engine` ke rantai** untuk pertama kalinya sejak §11.14, sesudah tujuh
rantai berturut-turut kehilangannya, ditambah `Evidence Check` yang belum pernah
ada di mana pun. **§17.36–§17.37 memberi metrik evaluasi model PERTAMA di
seluruh repo** (sepuluh metrik, *“accuracy saja tidak cukup”*), dengan
`data availability` sebagai sumbu bias yang paling tajam dan paling jarang
dipikirkan.

### 🛑 Tetapi keselamatan dikeluarkan dari MVP

`H17.12 Health Safety & Governance` tidak ada di jalur MVP §17.53, sementara
§17.54 **menuntut** `escalation`, `emergency`, dan `audit` sebagai kriteria
selesai. → **B-33** / #116. Dan **Mental Health Safety Layer §17.17** — yang
batasnya benar — kehilangan ketiga hal yang menentukan apakah ia bekerja.
→ **C-25** / #115.

---

## Sesi 19 — 7 September 2026

**Phase 16 direkam — fase yang paling mungkin melukai orang, dan kata “risk” tidak muncul satu kali pun di dalamnya.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 16: Robotics & Embodied Intelligence**, §16.1–§16.35 |
| Dokumen ditambah | **8 berkas** (`228`–`235`) |
| Dokumen total | 215 → **223** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 107 → **114** (94 terbuka, 20 ditutup); **#108**–**#114** baru |
| Temuan | **A-32** · **B-32** · **C-24** · **E-128**–**E-132** · **G-16** · enam butir **F** |

### 🛑🛑🛑 Ramalan E-124 terbukti — dan rantainya kehilangan satu gerbang lagi

Butir **E-124** ([#106](../../issues/106)) ditutup satu naskah lalu dengan kalimat: *“rantai keselamatan tanpa `Risk` yang diwarisi benda bergerak adalah kesalahan yang mahal diperbaiki setelah ada perangkat kerasnya.”* Naskah 20 memberi rantainya:

| Rantai | Gerbang |
|---|---|
| §11.14 Action Gateway | **9**, termasuk `Risk`, `Consent`, `Rate Limit`, **`Confirmation`** |
| §14.20 Agent Security Mesh | **11**, kehilangan tiga (**E-117**) |
| §15.22 Spatial Safety | **5**, punya `Permission`, tanpa `Risk`/`Confirmation` |
| **§16.18 Robot Safety Kernel** | **5**, punya `Emergency Rules`, **tanpa `Risk`, `Confirmation`, MAUPUN `Permission`** |
| **§16.13 Smart Home** | **3**, dan `pintu` sederet dengan `lampu` |

**Kata “risk” tidak muncul satu kali pun di seluruh naskah 20.** Dan §16.34 menjadwalkan **`R16.10 Safety Kernel` di urutan TERAKHIR** — sesudah humanoid, drone, manipulasi, dan armada — padahal §16.18 sendiri menyebutnya *“komponen paling kritis”*. Itu **B-30** ([#99](../../issues/99)) yang lebih berat: di naskah 18 yang dibuka lebih dulu adalah pintu; di sini **mesin yang bergerak di dekat orang**.

⭐ Yang **ditambahkan** naskah ini nyata: `Emergency Rules` + mesin keadaan §16.20 adalah **pengaman REAKTIF pertama** dalam 20 naskah — sesuatu yang menghentikan tindakan **yang sedang berlangsung**. Tapi reaktif bukan pengganti preventif.

### 🛑 Tiga temuan berat lainnya

- **A-32 / [#112](../../issues/112)** — **Phase 16 tanpa satu pun angka.** Lima besaran yang menentukan apakah seseorang terluka tidak ditulis di mana pun: **jarak henti · latensi reaksi · batas gaya · personal space · kecepatan per zona**. §16.8 menyebut `force` tanpa batas atas; §16.20 hanya mendeteksi gaya **tak terduga**, bukan gaya yang **direncanakan** terlalu besar — dan §16.23 menutup lingkarannya: robot menaikkan gayanya sendiri (`Future: Adjust force`), sehingga gaya baru itu kini “terduga” dan pengaman tidak berbunyi. Diperberat §16.27: empat variasi latihan sintetis semuanya soal **penampilan**, nol soal **perilaku** ⇒ `Safety Test` hanya bisa menguji apa yang disimulasikan.
- **B-32 / [#110](../../issues/110)** — diagram `HumanVerse → ROS Adapter → ROS2 → Robot` menempatkan **ROS2 lebih dekat ke robot daripada HumanVerse** ⇒ siapa pun yang bisa bicara ke ROS2 menggerakkan robot **tanpa melewati** Safety Kernel, Safe Zones, maupun Emergency Controller. Bentuk fisik dari *“agent tidak boleh bypass gateway”* §11.14.
- **C-24 / [#114](../../issues/114)** — **robot membawa sensornya sendiri MASUK ke ruangan**, sehingga policy yang terpasang pada ruangan tidak mengikatnya: §16.12 menuntut kamera ke wajah orang; §16.5 memberi humanoid kemampuan **membuka pintu** ⇒ `child_room: restricted:true` berhenti jadi batas fisik; §16.15 memberi drone `monitoring` di luar batas properti — dan naskah **tidak menyebut aturan penerbangan satu kali pun**.

### ⭐ Yang justru bertahan — enam butir F

- **§16.26 `Code → Simulation → Safety Test → Hardware`** — keputusan keselamatan terpenting naskah ini, dan **batas keras keempat yang perlu CI**; satu-satunya yang mencegah cedera fisik.
- **§16.21 menaruh `emergency` di EDGE** — konsisten dengan pemicunya sendiri (`communication loss`): pengaman darurat di cloud akan mati justru pada pemicunya. Digabung §15.29 ⇒ **apa pun yang harus tetap bekerja ketika segalanya gagal, berjalan paling dekat dengan dunia.**
- **§16.10 *“prioritas keselamatan tertinggi diberikan pada manusia”*** — memperbaiki lubang terbesar Phase 15 (`Person` di pohon objek yang sama dengan `Sofa`), dan memperbaikinya dengan **peringkat**, bukan penjelasan.
- **§16.11 `Robot slows → Wait`** — ketika sistem tidak yakin, jawabannya **melambat dan berhenti**. Satu-satunya tempat di naskah ini di mana prediksi yang salah tidak berbahaya. Sejalan: **`Wait` sebagai skill yang setara dengan `Pick`** (§16.24).
- **§16.12 *“ekspresi robot harus transparan, bukan berpura-pura punya emosi manusia”*** — pengaman pemilik yang **keenam berturut-turut**, dan ia mengenai godaan terbesar robotika sosial.
- **Naskah KEDUA berturut-turut memakai yang SUDAH ADA** — §16.7 (MoveIt/OMPL/RRT*/CHOMP/TrajOpt) · §16.14 (MQTT/Matter/Zigbee/Thread/BLE) · §16.22 (*“HumanVerse tidak menggantikan ROS”*) · §16.26 (Isaac Sim/Gazebo/Webots/MuJoCo).

### 🛑 Phase 17 diumumkan — petanya terbuka-ujung

Naskah 19 mengumumkan Phase 16; naskah 20 mengumumkan **Phase 17 — Human Health & Bio Intelligence**. Dua naskah berturut-turut menambah satu fase di kalimat penutupnya, tanpa satu pun menyebut §10.41. Pertanyaan ketiga [#101](../../issues/101) (*berapa fase lagi*) terjawab dengan perbuatan: **tidak ada ujungnya yang ditulis.**

⇒ **Berhenti mencatat “peta bertahan” sebagai butir F**, dan **beri versi pada peta fase** (`v1` 15 fase §10.41, `v2` terbuka-ujung). ⚠️ Phase 17 juga fase paling sensitif dari semuanya — *Health Digital Twin* menggabungkan wearable, biometrik, gaya hidup, dan perilaku, keempatnya Level 3–4. ⭐ Tiga butir sudah menunggu **sebelum naskahnya ditulis**: **C-20** ([#85](../../issues/85)) · **C-22** ([#102](../../issues/102)) · larangan §8.10.

### Teknik yang berbuah sesi ini

**Ambil butir yang saya tulis sebagai RAMALAN di naskah sebelumnya, lalu periksa apakah ia terjadi.** E-124 memperkirakan tiga hal untuk Phase 16; naskah 20 memperbaiki satu (`Person` ≠ `Sofa`, §16.10) dan mewarisi dua. Itu cara termurah menilai apakah sebuah naskah membaik — dan lebih jujur daripada membaca ulang dari nol, karena ramalannya ditulis sebelum jawabannya ada.

### Catatan kerja

Sesi lain menutup [#100](../../issues/100) dan [#14](../../issues/14) selagi sesi ini berjalan (tidak ada commit baru). Hitungan issue di berkas audit dan README karena itu diambil ulang dari `gh` sesudah pekerjaan selesai, bukan dari angka yang dibawa dari awal sesi.

---

## Sesi 18 — 7 September 2026

**Phase 15 direkam — dan peta 15 fase, satu-satunya sumbu penomoran yang bertahan lima naskah, patah di kalimat penutupnya.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 15: Spatial Intelligence & XR Universe**, §15.1–§15.32 |
| Dokumen ditambah | **9 berkas** (`219`–`227`) |
| Dokumen total | 206 → **215** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 100 → **107** (89 terbuka, 18 ditutup); **#101**–**#107** baru |
| Temuan | **A-31** · **B-31** · **C-22**–**C-23** · **E-123**–**E-127** · **G-15** · enam butir **F** |

### 🛑🛑🛑 H-20 patah — E-123 / [#101](../../issues/101)

Peta kanonik §10.41 ([`175`](175-REPO-API-DB-ROADMAP-DOD.md)) menetapkan **lima belas** fase dan menamai yang terakhir **Global Intelligence Platform**. Naskah 19 memberi **Phase 15 = Spatial Intelligence & XR Universe**, lalu menutup dengan **Phase 16 — Robotics & Embodied Intelligence**.

Dua hal sekaligus, keduanya di kalimat penutup: **isi fase terakhir diganti**, dan **petanya berhenti berjumlah lima belas**.

Yang jadi soal bukan isinya — SpatialOS masuk akal, dan *Global Intelligence Platform* memang tidak pernah punya isi selain namanya. Yang jadi soal adalah **cara ia berubah**: bagian F mencatat **lima kali berturut-turut** bahwa peta ini bertahan, dan nilainya seluruhnya terletak pada kestabilannya — ia satu sumbu stabil di antara lima yang bertabrakan. Ini butir **H kelima** yang tergerus (H-8 · H-10 · H-11 · H-13 · H-20).

### 🛑🛑 Privasi: sakelar yang mematikan sensor yang salah — C-23 / [#104](../../issues/104)

Temuan terberat sesi ini, dan seluruh buktinya ada **di dalam naskah yang sama**:

| Bagian | Yang dinyatakan |
|---|---|
| §15.23 | `bedroom: {camera:false, audio:false}` — lalu *“User tetap mengontrol”* |
| §15.4 | AetherScan membaca **WiFi CSI** — tidak butuh kamera maupun mikrofon |
| §15.4 | dan ia **menembus dinding**, jadi tidak perlu berada di dalam kamar |
| §15.10 | **`Sleeping`** ada di daftar aktivitas yang dilacak |
| §15.4 | **`breathing detection`** = laju napas, tanda vital |

**Pengguna yang mematikan kamera dan mikrofon di kamar tidurnya tetap terpantau tidur dan bernapas — sambil mengira sudah mematikan pemantauan.**

Ini bukan celah implementasi melainkan **bentuk policy-nya**: daftar `camera`/`audio` adalah daftar **perangkat**, sementara yang perlu dikendalikan adalah **kemampuan**. Bentuk yang benar sudah dipakai di repo ini — `deny` eksplisit §14.21 dan default deny §14.37 ⇒ **policy ruangan menyebut kemampuan yang DIIZINKAN, apa pun yang tidak disebut ditolak**, plus **ruangan yang menolak sebuah kemampuan menolaknya juga dari luar ruangan itu.**

§15.30 juga **tidak menjadwalkan privasi sebagai milestone sama sekali**, sementara `S15.8 AetherScan Integration` punya miliknya sendiri ⇒ urutan bawaannya adalah **sensor dibangun sebelum sakelar yang mematikannya**.

### 🛑 Tiga temuan berat lainnya

- **C-22 / [#102](../../issues/102)** — `through-wall sensing` dan `breathing detection` menaikkan **C-18** dari soal persetujuan menjadi **soal hukum**: yang pertama mendeteksi orang di properti tetangga (persetujuan pengguna tidak bisa memberi izin atas ruang yang bukan miliknya); yang kedua adalah **tanda vital yang diukur tanpa perangkat apa pun di badan orangnya**.
- **E-124 / [#106](../../issues/106)** — §15.22 adalah rantai **kelima** yang berakhir di tindakan tanpa `Risk` maupun `Confirmation`, setelah empat yang [#93](../../issues/93) catat di naskah 18. Bedanya: penutup naskah menyatakan **Phase 16 = Robotics**, jadi rantai ini akan menjadi rantai keselamatan **benda yang bergerak di ruangan yang sama dengan manusia**.
- **B-31 / [#107](../../issues/107)** — `wifi_csi` (10–100 Hz) dan `point_clouds` di PostgreSQL. Pembandingnya sudah ada: `PersonDetected` 1 Hz = 2,6 juta baris/30 hari untuk satu kamera; CSI berjalan satu sampai dua **orde** lebih cepat. ⭐ Penawarnya juga ada di naskah yang sama, §15.29.

### ⭐ Yang justru bertahan — enam butir F

- **“HumanVerse tidak menebak”** sebagai kalimat pembuka: menyatakan **syarat**, bukan janji. Dan panah AR bisa **dibuktikan salah dalam sepuluh detik** — fase pertama yang keluarannya bisa dibantah seketika.
- **§15.6 menyebut pustaka yang SUDAH ADA** (ARKit · ARCore · OpenVSLAM · ORB-SLAM3 · RTAB-Map) alih-alih merancang komponen baru — pertama kalinya dalam sembilan belas naskah, dan penghematan pekerjaan terbesar di fase ini.
- **§15.29 = pernyataan privasi-oleh-arsitektur pertama di repo ini** (*“edge melakukan processing sensitif”*) — satu-satunya bentuk perlindungan yang tetap berlaku saat terjadi kebocoran, penyitaan, atau permintaan aparat.
- **§15.11 Scene Graph: enam relasi geometris**, tidak satu pun kausal — graf **ketiga**, dan yang paling aman. ⚠️ Kecuali `MOVING_TO`, yang **prediksi**, bukan pengukuran.
- **§15.12 memberi lima target akurasi berangka** yang bisa diuji dengan meteran di lantai — dan sekaligus memberi aturan yang §15.3 butuhkan (**sensor lebih presisi menang**). 🔴 Tapi itu justru memperkuat **E-112**: §15.32 di naskah yang sama kembali memberi **10 kriteria DoD tanpa satu angka pun**.
- **§15.18 Spatial Notifications** = penerapan pertama `Attention Budget` §14.25 pada permukaan nyata, dan bentuknya benar: **notifikasi tidak mengejar orangnya, ia menunggu di tempat.**

### Teknik yang berbuah sesi ini

**Baca satu bagian sambil memegang bagian lain di naskah yang sama, lalu tanyakan apakah keduanya bisa benar bersamaan.** C-23 seluruhnya lahir dari itu — §15.23 (policy kamar) melawan §15.4 (sensor tembus dinding) dan §15.10 (`Sleeping`); tidak satu pun dari ketiganya mencurigakan kalau dibaca sendiri-sendiri. Sama untuk E-112 (§15.12 punya angka, §15.32 tidak) dan E-124 (§15.22 tanpa `Risk`, penutup mengumumkan robot).

### Catatan kerja

Sesi lain menulis `GERBANG-SKEMA.md` dan [#100](../../issues/100) selagi sesi ini berjalan, dan **menomori entrinya “Sesi 16”** — bertabrakan dengan entri naskah 18. Entri itu **dinomori ulang menjadi Sesi 17** dan dipindah ke atas sesuai aturan *“yang terbaru di atas”*; isinya tidak diubah sama sekali.

---

## Sesi 17 — 7 September 2026

**Daftar penghambat Engineering Spec ternyata salah — dan koreksi pertama saya JUGA salah. Kenyataannya: TIDAK ADA yang mengunci.**

| Hal | Hasil |
|---|---|
| Dokumen ditambah | **1 berkas** (`GERBANG-SKEMA.md`) |
| Dokumen total | 205 → **206** di `docs/` |
| Berkas kode | tetap **0** |
| Issue | **#100** baru |

`README` menyebut empat butir yang mengunci Engineering Spec *"karena keempatnya menentukan skema basis data"*. Diperiksa satu per satu terhadap berkas audit, daftar itu **sudah tidak akurat**:

| Butir | Kata README | Kenyataan |
|---|---|---|
| **E-39** | mengunci | ✅ **sudah DITUTUP** naskah 13 → H-16 (`kind`/`scope`/`tier`) |
| **E-16** | mengunci | ✅ **praktis tertutup** — tiga lawan satu |
| **E-17/E-18** | mengunci | 🛑 masih terbuka |
| **A-19** | mengunci | 🛑 masih terbuka, **memburuk jadi enam model** |
| **E-37** | mengunci | 🛑 masih terbuka, **memburuk** |

Pekerjaan yang tampak terhalang empat pintu sebenarnya terhalang dua.

### Ketiganya bisa dijawab tanpa naskah baru

[`GERBANG-SKEMA.md`](GERBANG-SKEMA.md) menyusunnya jadi tiga pertanyaan yang bisa dijawab ya/tidak, masing-masing dengan usul yang memakai **pola yang sudah terbukti di repo ini sendiri**:

1. **`HumanState` jadi satu-satunya yang disimpan?** — lima lainnya jadi tampilan turunan, tiap angka turunan wajib membawa `confidence` (B-15/B-1).
2. **Satu tabel sisi dengan kolom `kind`?** — kausal dan struktural bukan pilihan yang saling meniadakan, melainkan dua jenis sisi; `kind` adalah pola yang **sudah dipilih sekali dan berhasil** di H-16.
3. **Skor disimpan `0–1`?** — §12.21 sudah membuktikan bobot berjumlah 1,00; persen dan poin adalah cara *menampilkan*, bukan *menyimpan*.

**A-17 sengaja dikeluarkan** dari daftar gerbang: ia keputusan **cakupan**, bukan **skema**, dan tidak menghalangi satu baris DDL pun.

### 🔴 Koreksi dalam sesi yang sama: saya mengulang kesalahan yang baru saya temukan

Kesimpulan pertama — *"tiga pertanyaan tersisa"* — **terlalu tinggi**. Sebabnya bisa disebut persis: saya memeriksa `99-CATATAN-AUDIT.md` dan `README.md`, **tetapi tidak memeriksa [`spec/README.md`](../spec/README.md)** — berkas yang seluruh tugasnya justru menjawab pertanyaan itu.

Berkas itu punya bagian tersendiri, *"Empat keputusan yang mengunci skema — dan cara saya menanganinya"*, dan menutupnya dengan **"Artinya V0 bisa dimulai sekarang."**

Buktinya ada di DDL, bukan di prosa:

| Butir | Kata saya | Kenyataan di `spec/01` |
|---|---|---|
| **#32** skala skor | masih terbuka, usul `0–1` | **sudah** `numeric(4,3) CHECK (score BETWEEN 0 AND 1)` + `confidence` + `scoring_version` |
| **#2** model angka | masih terbuka, usul `HumanState` kanonik | **sengaja tidak diputuskan** — `metrics jsonb` + `model_version`; enam model hidup berdampingan tanpa migrasi |
| **#7** model graf | masih terbuka | **tidak menyentuh V0** — Neo4j baru V2 |

Dua dari tiga usul saya **sudah ada di DDL**, ditulis lebih dulu dan dengan alasan yang lebih baik — khususnya *"100-poin dan persen lossless dikonversi ke 0–1; sebaliknya tidak."*

**Bentuk kesalahannya sama persis dengan yang saya temukan di `README.md`:** percaya pada daftar ringkasan alih-alih memeriksa sumbernya. Ditemukan di dokumen orang lain, lalu diulang di dokumen sendiri, dalam sesi yang sama.

Aturan sesudah ini: **sebelum menyatakan sesuatu terhalang, buka berkas yang paling berkepentingan membantahnya.**

### Penghambat V0 yang sebenarnya

Cuma dua, dan keduanya bukan soal skema: **#3** (siapa mengerjakan 12 fitur dalam 4–6 minggu) dan **#20** (cek merek, domain, nama paket).

### Catatan

Tidak ada temuan baru di sesi ini — seluruhnya menyusun ulang butir yang sudah ada. Yang bertambah cuma satu: kesadaran bahwa **daftar penghambatnya sendiri tidak pernah diperbarui saat butirnya ditutup**. Itu kelas kesalahan yang layak dijaga: sebuah daftar penghalang yang basi membuat pekerjaan tampak lebih terkunci daripada kenyataannya.

---

## Sesi 16 — 7 September 2026

**Phase 14 direkam — naskah terpanjang (69 bagian), dan aturan yang saya catat sebagai hilang di naskah 15 datang lengkap.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 14: Autonomous Intelligence & Collective Agent Ecosystem**, §14.1–§14.69 |
| Dokumen ditambah | **12 berkas** (`207`–`218`) |
| Dokumen total | 193 → **205** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 91 → **99** (81 terbuka, 18 ditutup); **#92**–**#99** baru, **#73 ditutup** |
| Temuan | **H-24** · **A-30** · **B-28**–**B-30** · **C-21** · **E-117**–**E-122** · **G-14** · enam butir **F** |

### ⭐⭐⭐ Aturan yang hilang di naskah 15 datang — dan lebih baik daripada usul saya

Di [`181-MULTI-AGENT.md`](181-MULTI-AGENT.md) saya menulis bahwa satu aturan belum ada, dan ia satu kalimat: *"lingkup pesan tidak boleh lebih luas daripada lingkup pengirimnya"*. Tanpa itu, agent berlingkup sempit bisa meminta agent lain melakukan hal yang ia sendiri tidak boleh — **privilege escalation lewat delegasi**.

§14.42 menjawabnya:

> ## Delegation cannot exceed the authority of the delegator.

Rumusan pemilik **lebih kuat** daripada usul saya. Usul saya adalah aturan tentang **field di dalam pesan**, jadi penegakannya bergantung pada field itu diisi benar. Rumusan pemilik adalah aturan tentang **kewenangan**, jadi ia berlaku lewat jalur apa pun — pesan, panggilan langsung, tool, atau protokol federasi §14.41. Itu juga sebabnya hilangnya `authorization.scope` dari amplop §14.7 **bukan kemunduran**: yang dibuang field, yang datang invarian.

Dan naskah ini memberi **dua** penangkal, bukan satu: **aturan** (§14.42 + §14.43 *capability attenuation* + `max_depth: 2`) dan **deteksi** (graf kapabilitas §14.32/§14.33 mencari jalur `A → B → C → Sensitive Database`).

### 🛑 Lubang terbesar: deteksi graf buta di batas federasi — B-28 / [#94](../../issues/94)

Graf kapabilitas hanya bisa memuat agent yang kapabilitasnya **diketahui**. Untuk agent internal itu manifest yang tervalidasi registry; untuk agent **federasi** (§14.4) kapabilitas **dideklarasikan sendiri** oleh agent yang berjalan di mesin orang lain — dan §14.5 bahkan menaruh `trust_level: certified` di dalam deklarasi itu.

Jalur eskalasi terdeteksi selama A, B, dan C internal. Begitu satu simpul eksternal, **jalurnya hilang dari graf** — bukan karena tidak ada, melainkan karena satu simpul tidak melaporkan apa yang benar-benar bisa ia lakukan.

### 🛑 Empat rantai tanpa titik tahan manusia — E-117 / [#93](../../issues/93)

§14.20 (Security Mesh kehilangan `Consent`, `Rate Limit`, `Confirmation`) · §14.37 dan §14.38 (`Human Approval` **sesudah** `Execution`) · §14.46 (Collective Cognitive Runtime **tanpa `POLICY_CHECK`**).

Yang keempat paling perlu diperhatikan: **H-18** ditutup justru karena §9.29 menaruh `POLICY_CHECK` setelah `PLANNING` dan sebelum `DECISION`/`ACTION`. Empat kali dalam satu naskah bukan kelalaian penulisan — itu pola, dan rantai yang digambar lengkap akan dibangun seperti yang digambar.

### 🛑 Naskah membatalkan hukumnya sendiri — B-29 / [#96](../../issues/96)

§14.64 menetapkan sebagai **foundational law**: *"More agents must not automatically mean more autonomy"*, karena `collective risk > individual risk`.

§14.50 **menjumlahkan** `Safety` dengan tujuh hal lain menjadi satu *Collective Intelligence Score*. Team yang cepat, murah, dan terkoordinasi baik bisa menyamai team yang aman — dan kalau skor itu dipakai memilih team (§14.48) atau menaikkan otonomi (§14.61), sistem bergerak ke arah yang salah **tanpa ada aturan yang dilanggar**. Bentuk yang benar sudah dipakai di tempat lain: **keselamatan adalah gerbang, bukan suku** (Risk Engine §8.17 menolak, tidak menjumlahkan).

### 🛑 Roadmap membuka pintu enam langkah sebelum penjaganya — B-30 / [#99](../../issues/99)

`A14.1 Agent Federation Foundation` pertama; `A14.7 Agent Security Mesh` ketujuh. Di antaranya dibangun komunikasi, delegasi, kolaborasi, negosiasi, dan kecerdasan kolektif — semuanya dengan peserta yang berjalan di mesin orang lain dan belum diawasi.

### ⭐ Yang ditutup dan yang akhirnya diberi angka

- **A-27 / [#73](../../issues/73) DITUTUP → H-24.** §14.23 memberi tujuh model pendapatan, dan §14.17–§14.18 mengembalikan Enterprise. Dua blok yang **E-86** catat hilang dari peta 15 fase kini keduanya punya rumah. ⚠️ Tarif dan bagi hasil tetap milik **A-6** / [#18](../../issues/18).
- **Ambang `confidence` pertama setelah delapan naskah:** §14.62 menulis `escalate_when: confidence < 0.6`, dan ia berada di tempat yang tepat — di dalam kontrak yang bisa dibaca dan diubah pemiliknya, bukan di kode. Dikirim sebagai komentar ke [#34](../../issues/34).
- **`private.journal` akhirnya disebut dengan namanya** di dalam aturan (`deny:` §14.21), memperbaiki masalah kata pengganti **G-9**.
- **"Tidak boleh mengarang data" (§14.35)** menutup bentuk paling berbahaya dari **B-14** / [#26](../../issues/26): degradasi berakhir di **diam**, bukan di karangan.

### Teknik yang berbuah sesi ini

**Bandingkan rantai yang sama di dua naskah, hitung langkahnya, lalu tanyakan langkah mana yang hilang.** Tiga dari empat temuan berat sesi ini datang dari sana — E-117 (empat rantai), E-119 (`risk: level` vs `max_risk`), dan G-14 (tujuh tindakan → tiga event). Bukan membaca apa yang ditulis, melainkan **membandingkan panjang dua daftar yang seharusnya sama**.

### Langkah berikutnya menurut pemilik

Pemilik menutup naskah ini dengan permintaan yang **berbeda jenisnya** dari tujuh belas naskah sebelumnya:

> Namun saya **tidak menyarankan kita langsung melompat ke Phase 15.** … Sebelum melanjutkan, secara engineering kita sebaiknya memecah Phase 14 menjadi arsitektur teknis tingkat implementasi: protocol specification · agent message schema · federation protocol · security model · delegation model · consensus algorithm · database schema · API contract · event schema · repository · Docker/Kubernetes topology · sprint-by-sprint implementation.

Itu persis bentuk artefak yang sudah ada di [`../spec/`](../spec/README.md) untuk V0 — jadi pekerjaannya bisa dimulai tanpa keputusan baru. ⚠️ Dengan satu syarat: **empat butir harus diputuskan lebih dulu karena keempatnya soal bentuk, bukan selera** — [#93](../../issues/93) (titik tahan), [#97](../../issues/97) (`max_risk`), [#98](../../issues/98) (L5 & kontrak), [#99](../../issues/99) (urutan roadmap).

---

## Sesi 15 — 7 September 2026

**Phase 13 direkam — dan dua pengaman naskah 15 dilepas di dua bagian berbeda.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 13: HumanOS — Personal AI Operating System**, §13.1–§13.40 |
| Dokumen ditambah | **9 berkas** (`198`–`206`) |
| Dokumen total | 184 → **193** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 89 → **91** (74 terbuka, 17 ditutup); **#90** dan **#91** baru |
| Temuan | **E-108**–**E-116** · delapan butir **F** |

### 🛑🛑🛑 Dua pengaman dilepas, dan keduanya bersenyawa

Ini temuan terpenting sesi ini, dan nilainya justru pada **gabungannya** — masing-masing sendiri tampak seperti penyesuaian kecil.

**E-108 / [#90](../../issues/90) — "Ask Every Time".** §11.15 baru saja menaikkan R4 dari *"wajib konfirmasi"* menjadi **`DENY`**, dengan definisi baru **`irreversible`**, dan catatannya eksplisit: *"tingkat tertinggi tidak bisa dikonfirmasi."* §11.17 menambah `purchases: { amount_limit: 0 }` sebagai bawaan. §13.10 memberi pembelian dan kontrol perangkat **"Ask Every Time"** — tepat konstruksi yang ditolak §11.15 — dan **tanpa satu angka pun**, sehingga bawaan nol tidak punya tempat untuk dinyatakan.

**E-109 / [#91](../../issues/91) — `Rollback` hilang.** **G-8** ([#65](../../issues/65)) mencatat *Human Override* tidak pernah datang di Fase 8; §11.61 mengisinya dengan enam kata kerja termasuk **`Rollback`**. §13.34 memberi enam kekuasaan juga, tapi bukan enam yang sama: tiga kekuasaan **pencegahan** ditambah, tiga kekuasaan **korektif** dibuang. Kata *rollback*, *undo*, *revert* nol kali di seluruh naskah 17.

Digabung, keduanya menghasilkan keadaan yang persis ingin dicegah §11.15:

> tindakan **yang tidak bisa ditarik** lewat dengan **satu ketukan**, dan **tidak ada jalan kembali**.

§11.15 memasang dua kunci pada pintu itu. Naskah ini melepas keduanya, **di dua bagian yang berbeda** — dan itulah sebabnya tak satu pun terlihat sebagai keputusan besar saat dibaca sendiri-sendiri.

### 🛑 Empat temuan lain

- **E-110** — manifest **keenam**, dan lebih lemah daripada yang kelima. §11.5 baru memulihkan `purpose` dan memisahkan lagi `memory.read`/`.write` (menutup E-68/#61); §13.26 menjatuhkan keduanya plus `autonomy.max_level` dan `tools`. Bantahan *"app ≠ agent"* tidak menyelamatkannya: §13.27 menaruh apps, agents, dan plugins di **satu marketplace**, jadi manifest terlemah jadi jalan termudah. Diperkuat §13.35 yang **mewajibkan** kolom `Why` di audit trail — yaitu `purpose` dengan nama lain.
- **E-111** — **dua pohon `human-os/` di naskah yang sama** (§13.2 = 17 direktori datar; §13.37 = 13 bersarang). Tiga hilang tanpa penampung: `capability/`, `agency/`, `events/` — padahal §13.9 menjadikan Capability primitif keamanan inti dan §13.12 menjadikan Event Bus arsitekturnya.
- **E-113** — **`H13.x` adalah huruf KEENAM**, dan ia bertabrakan dengan penomoran berkas audit sendiri: `H-13` (butir keputusan) vs `H13.1` (sub-fase), beda satu tanda hubung.
- **E-114** — **"HumanOS" kini punya arti ketiga**, dan dua di antaranya adalah tahap di dua rencana kanonik yang sedang bertabrakan: **V5 = HumanOS** (V0–V6) vs **Phase 13 = HumanOS** (peta 15 fase). Kalau V0–V6 masih berlaku, naskah ini pada dasarnya spesifikasi **V5**. 🛑 V0–V6 tetap tidak disebut, **naskah kelima berturut-turut**.

### 🛑 Sapuan kedua menemukan E-116 — dan ini yang pertama menabrak spesifikasi

Sapuan pertama memakai tiga dari empat teknik yang paling berbuah di repo ini. Sapuan kedua memakai yang keempat — **cari daftar yang IDENTIK di dua naskah, jangan banding labelnya** — dan langsung berbuah.

§13.12 memberi **15 event, semuanya PascalCase**: pelanggaran [#38](../../issues/38) yang **keempat berturut-turut** (sesudah E-70, E-88, E-98). Tapi yang membuatnya berbeda kelas: **delapan di antaranya sudah ada di `spec/03`** — kontrak yang sudah ditulis, bukan dokumen visi.

Lima identik modulo huruf. **Tiga bukan sekadar beda huruf:** `sleep.completed` ↔ **`SleepEnded`**, `meeting.completed` ↔ **`MeetingEnded`**, `mood.logged` ↔ **`MoodChanged`**. Itu kosakata kedua — kalau keduanya dikodekan, satu kejadian punya dua event.

Separuh kedua #38 juga diambil ke sisi non-spec: §13.24 memakai `/v1/…`, `spec/04` menyatakan `/api/v1`.

Bukti lengkapnya dikirim sebagai komentar di [#38](../../issues/38), karena butir itu memang keputusan yang menunggu — dan #38 sendiri memperingatkan bahwa nama event **tidak boleh diganti setelah dipakai**.

### ⭐ Yang justru bertahan — delapan butir F

Setelah lima naskah yang menggerus keputusan tertutup, naskah ini juga membawa kabar baik yang layak dicatat setara:

- **Peta 15 fase bertahan naskah KEEMPAT** — §10.41, §11.64, §12.31 menempatkan Phase 13 = HumanOS, dan naskah ini memang itu. **H-20** aman.
- **Tabrakan paling berbahaya tidak kambuh.** §13.33 **memanggil** tangga L dan menyebut sumbernya alih-alih mendefinisikan ulang — **E-77 / #67** tetap tertutup.
- **`/actions/prepare` dan `/actions/execute` dipisah jadi dua endpoint.** Tangga L ditegakkan **bentuk API**, bukan kebijakan.
- **State machine §13.36 menaruh tiga gerbang sebagai STATE**, bukan pemeriksaan di dalam kode — dan jalur kegagalan berakhir di `WAITING_CONFIRMATION`, bukan `EXECUTING`.
- **§13.32 menutup bagian proaktif dengan *"Bukan langsung melakukan sesuatu."*** — pengaman yang ditulis pemilik sendiri.

### Catatan kerja

Naskah 16 (Phase 12) masih di pohon kerja saat sesi ini dimulai, ditulis sesi lain yang berjalan bersamaan. Dokumen `198`–`206` karena itu ditulis di rentang nomor yang tidak bertabrakan, dan penomoran `E-` sengaja ditunda sampai naskah 16 di-commit — supaya `E-107` sudah final sebelum `E-108` dipakai.

---

## Sesi 14 — 7 September 2026

**Phase 12 direkam — B-24 ditutup lewat jalan keempat, dan `intelligence/` dibongkar.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 12: Digital Twin & World Simulation**, §12.1–§12.31 |
| Dokumen ditambah | **10 berkas** (`188`–`197`) |
| Dokumen total | 174 → **184** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 83 → **89** (72 terbuka, 17 ditutup); **#70** ditutup |

### ⭐⭐⭐ H-23 — B-24 ditutup, dan jawabannya jalan **keempat**

Saya menawarkan tiga jalan keluar untuk model transisi yang tidak punya sumber:
eksperimen pengguna · pengetahuan umum · perbandingan relatif. §12.20 memilih
yang keempat:

```
Simulation → Prediction → Real World → Actual Outcome
→ Prediction Error → Evaluation → Model Update
```

Kekuatan panah kausal **dipelajari dari galat prediksinya sendiri**. Prinsip
yang sama dengan `Prediction Calibration` §9.34 yang menutup B-10: **kebenaran
acuan dihasilkan sistem sendiri** dari hasil teramati — tanpa penilai manusia,
tanpa model menilai model. `Expected 75 → Actual 61` datang gratis.

⭐⭐ Ditambah **§12.14 Assumption Engine** (*"simulation without assumptions is
misleading"*) yang membuat yang dipinjam jadi **terlihat dan bisa dibantah**,
dan §12.7 yang membandingkan **delapan dimensi antar-skenario** — termasuk
**`Sustainability`**, kata yang belum pernah ada dan yang menangkap kegagalan
paling umum dari rencana buatan mesin.

### 🛑 E-101 — tujuh pohon sekaligus, dan LIMA ditarik keluar dari `intelligence/`

Sebelum ini tiap naskah menambah **satu** pohon. §12.26 menambah tujuh — dan
lima di antaranya adalah folder yang **dipindahkan keluar** dari pohon yang
baru didefinisikan tiga naskah lalu: `world-model/` · `simulation/` ·
`decision/` · `prediction/` · `reasoning/causal/`.

**E-79** mencatat naskah 13 membuang empat folder dari `intelligence/`; naskah
16 mengeluarkan lima lagi. Dari lima belas kelompok §9.38, **tersisa sembilan**.
Total pohon tingkat-atas: **lima belas**, dan delapan naskah berturut-turut
menyentuh struktur repo.

⭐ Tapi ketujuhnya **muat sebagai submodul `intelligence/`** — usulan saya jadi
lebih sederhana, bukan lebih rumit.

### 🛑 C-20 — proyeksi masa depan adalah kelas data baru

§12.13 menyimpan `future_projections`; §12.10 memproyeksikan **wealth
trajectory**, karier, dan kesehatan sampai **lima tahun**. §8.10 melarang
memakai data untuk *insurance/employment scoring* — dan **proyeksi adalah
persis bentuk turunan yang paling berguna bagi mereka**. Larangan tujuan
menahan pemakaiannya; ia tidak menahan **keberadaannya**.

🔴 Ditambah **§12.22 Life Optimization Engine** yang menaikkan taruhan C-16:
model utilitas yang bobotnya **disimpulkan** kini dipakai bukan untuk
**membandingkan** (§9.24) melainkan untuk **memaksimalkan** — dan §12.23
menyerahkan hasilnya ke agent. **Perbandingan menyerahkan penilaian kepada
orangnya; optimasi mengambilnya.**

### 🛑 A-29 — horizon 3 dan 5 tahun tidak pernah masuk loop belajar

Proyeksi 30 hari bisa diperiksa dalam 30 hari dan dipakai memperbaiki model.
Proyeksi **5 tahun** tidak bisa diperiksa siapa pun sampai lima tahun lewat —
satu-satunya keluaran sistem yang **tidak bisa dikalibrasi**, sementara ia yang
paling memengaruhi keputusan besar. Dan §12.10 memproyeksikan kekayaan (**C-4**)
dan kesehatan (**C-2**).

⭐ Penyelamatnya ada di naskah yang sama: **`confidence interval`** — pertama
kalinya di enam belas naskah sebuah angka datang dengan **rentang**.

### Temuan lain

- **E-102** — Human State versi **keempat**: 8 → 7 → 10 → **8**, `mood` keluar
  untuk kedua kalinya, `financial pressure` juga hilang. ⭐ Keduanya
  kemungkinan **benar** dibuang; masalahnya tidak dinyatakan.
- **E-103** — Digital Twin versi keempat: 8 → 8 → 9 → **18**, dan
  **`Perception` hilang** setelah satu naskah (pola H-8). ⭐⭐ Tapi
  **`constraints`** dan **`resources`** akhirnya punya rumah — `constraints`
  adalah satu-satunya field context package §9.31 yang belum pernah punya
  sumber di tiga belas naskah.
- ⭐⭐ **`volatility`** per atribut menjawab pertanyaan terbuka di #49: ia
  **laju peluruhan per atribut**. Empat besaran akhirnya berpasangan rapi:
  `value` · `confidence` · `quality` · `volatility`.
- **E-104** — Personal Utility Model: rumus **8 suku**, contoh **5 bobot**,
  nama tidak cocok, dan §9.25 punya daftar ketiga. Pola **E-37** persis. ⚠️
  `w6 Risk` berbobot **positif** = kesalahan arah.
- **E-105** — "sandbox" kini **empat** makna (uji · runtime · sertifikasi ·
  simulasi). ⭐ Yang keempat batas keras: *"simulation tidak boleh mengubah
  data dunia nyata"*.
- **E-106** — 26 tabel baru ⇒ **99 tabel**. Nol dari 26 dibutuhkan V0.
- **G-13 / #89** — 12 agent baru, total **> 40**. ⭐⭐⭐ Dan naskahnya sendiri
  memperingatkan **untuk pertama kalinya di enam belas naskah**: *"jangan
  membuat semuanya sebagai autonomous agent — sebagian lebih baik sebagai
  deterministic/model services."* ⚠️ Tapi kriterianya tidak diberikan; saya
  tulis empat baris, dan dengan itu **sepuluh dari dua belas** kemungkinan
  service.
- **B-27 / #88** — loop belajar §12.20 butuh **titik mulai**; sebelum ada galat
  pertama tidak ada yang bisa dikalibrasi.

### ⭐⭐⭐ Prinsip penutup — kontribusi konseptual terbesar naskah ini

```
Observed  ≠  Predicted  ≠  Simulated  ≠  Certain
```

Ia memperluas tangga §10.5 (*Perception → Interpretation → Inference*) ke sumbu
**waktu**. Yang paling menentukan: **`Predicted ≠ Simulated`** — prediksi
mengatakan *apa yang mungkin terjadi*; simulasi mengatakan *apa yang mungkin
terjadi **jika** asumsinya berlaku*. Dan `Certain` di ujung **tanpa padanan**
adalah pengakuan bahwa tidak ada keluaran sistem ini yang pernah masuk kategori
itu.

Lima naskah berturut-turut menutup dengan kalimat yang searah — n4 *"jangan
menilai baik atau buruk"* · §8.46 · §9.41 · §11.63 · dan ini.

### ✅ Yang diperiksa dan ternyata benar

Rantai kausal §12.5 identik dengan naskah 4 §36 dan §9.17 (**tiga naskah**), dan
bahasanya **melunak di tempat yang tepat** (*"repeated controlled experiments"*
→ *"hubungan konsisten"*) · `Sleep → Energy → Focus` §12.6 membuat **E-16 jadi
tiga lawan satu** · bobot utility berjumlah tepat 1,00 · tujuh horizon §12.13
menyelesaikan **E-29/E-7** · peta 15 fase bertahan **naskah ketiga**.

🛑 Tapi **V0–V6 tetap tidak disebut — naskah KEEMPAT berturut-turut** (#72).
Empat naskah cukup lama untuk berhenti menyebutnya kelalaian.

### Langkah berikutnya menurut pemilik

**Phase 13 — HumanVerse Personal AI Operating System / HumanOS.**

---

## Sesi 13 — 7 September 2026

**Phase 11 direkam — dua tabrakan terberat ditutup, dan keputusan keempat tergerus.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 11: Agentic Intelligence & Agency**, §11.1–§11.64 — **naskah terpanjang dari lima belas** |
| Dokumen ditambah | **12 berkas** (`176`–`187`) |
| Dokumen total | 162 → **174** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 77 → **83** (67 terbuka, 16 ditutup); **#67** dan **#61** ditutup |

### ⭐⭐⭐ H-21 — tabrakan paling berbahaya dari lima belas naskah, ditutup

Sesi lalu saya catat **E-77** sebagai yang paling berbahaya: naskah 12 memberi
`R4 = Critical, wajib konfirmasi`; naskah 13 memberi `Level 4 = Bounded
autonomy, bertindak sendiri`. *"Agent ini Level 4"* berarti dua hal berlawanan.

§11.15 membuka dengan *"kita sudah memiliki R0–R4"* lalu §11.16 memberi tangga
otonomi **terpisah** — dan §11.5 menaruh keduanya di satu berkas:

```yaml
risk_level: R1          # risiko AKSI
autonomy:
  max_level: L2         # kewenangan AGENT
```

⭐ Kelima tingkat L **identik dengan §9.26** — daftar yang diulang tanpa
bergeser. ⭐⭐ Dan §11.15 **memperketat**: R4 kini `DENY` sebagai bawaan, dengan
definisi baru **"irreversible"** — bukan "berdampak besar".

### ⭐⭐ H-22 — manifest keenam memulihkan dua field yang saya keluhkan

`purpose` kembali (hilang sejak naskah 10) dan `memory.read`/`memory.write`
kembali jadi **dua field** (diruntuhkan naskah 12 jadi `memory_scope` tunggal).
Itu membuat dua batas paling halus di `spec/05` bisa dinyatakan lagi:
`coach-agent` hanya menulis `coaching_notes`; `memory-agent` membaca semua
**kecuali** `journal_raw`.

⭐ Ditambah §11.37 yang memberi `require_confirmation` bentuk policy konkret,
dengan tiga kata yang menutup satu kelas kesalahan: **"Bukan LLM."**

### 🛑 E-94 — H-11 tergerus, keputusan KEEMPAT yang tergerus

**H-11** ditutup dengan tegas: *"Weather & Calendar = TOOL, bukan agent."*
Butir **E-28** mencatat kenapa butir itu pernah terbuka: naskah 4 §13 memakai
`WeatherAgent` sebagai contoh komunikasi antar-agent, **lengkap dengan pesan
`"to": "WeatherAgent"`**.

§11.20 sekarang: `{"from": "travel-agent", "to": "weather-agent"}` —
**konstruksi yang sama persis, di peran yang sama persis.** Dan §11.4
menempatkan *Calendar Agent* di Action Agents, sementara calendar adalah
**tool** di tiga tempat lain di naskah yang sama.

H yang tergerus berurutan: **H-8** (Grooming) · **H-10** (monorepo) ·
**H-13** (rencana kanonik) · **H-11**. Polanya cukup jelas untuk dijadikan
kebiasaan: **tinjau ulang butir H setiap beberapa naskah.**

### 🛑 E-95 — daftar agent versi kelima, tujuh agent di contoh tanpa terdaftar

25 agent berhierarki. ⭐ **Health kembali** dan **Lifestyle mendapat agent
untuk pertama kalinya** — separuh jawaban A-20/#4. ⭐ **Action Agents** sebagai
kategori tersendiri memberi B-19 batas per kategori.

🛑 Tapi tujuh agent hidup di contoh tanpa ada di hierarki: *Productivity*
(§11.59), *Weather · Transportation · Hotel · Budget* (§11.19), *Location ·
Preference* (§11.21) — pola **E-38** pada skala tujuh kali lipat. Dan
**Mental Wellness masih tanpa agent setelah lima belas naskah**, dijaga lewat
kata pengganti dua kali (*"private documents"*, *"private conversations"*)
tanpa pernah dinamai.

### Temuan lain

- **A-28 / #80** — §11.41 (tugas Senin–Minggu) dan §11.42 (proaktif) adalah
  komponen **pertama yang bekerja sendiri tanpa diminta**. Tiga hal yang
  dibutuhkan belum ada: izin lokasi (tidak pernah didaftarkan), push
  notification, dan preferensi gangguan. ⭐ Pengamannya sudah dirancang:
  anggaran `notification: 10/day`, Interruption Manager, dan **"Do Nothing
  adalah kemampuan penting bagi agent."**
- **C-19 / #81** — Communication Agent dan Booking Agent bertindak **kepada
  orang ketiga**, dan penerima **tidak bisa tahu** apakah yang menulis manusia
  atau agent. B-19 selalu dari sisi pengguna; ini sisi penerima, dan belum
  pernah dibahas di lima belas naskah.
- **B-26 / #83** — tugas seminggu membuat **B-14 struktural**: sinyal mati hari
  Rabu menghasilkan `Review` hari Minggu dari dua hari data, tanpa apa pun yang
  mewajibkan agent menyadarinya.
- **E-96/E-99 / #82** — Fase 8 dan Fase 11 mendefinisikan hal yang sama dua
  kali: **dua Control Plane** berbagi empat komponen, dan **dua tabel**
  (`agent_capabilities`, `agent_trust_scores`) didefinisikan dua fase.
  Duplikasi pertama di tingkat **skema**, bukan folder.
- **E-97** — pohon tingkat-atas **kedelapan** (`agents/`, 28 folder) dengan
  **dua belas duplikasi**, terbanyak dari semua pohon. ⭐ Tapi naskah ini
  sendiri memberi aturannya: **`security/` memiliki mesinnya, `agents/` hanya
  memanggil** — dengan itu enam folder tidak perlu ada.
- **E-98** — 22 event agent PascalCase, naskah **ketiga** berturut-turut
  melanggar #38; dua di antaranya menduplikasi event keamanan §8.26.
- **G-12** — `requires_confirmation` kini di **tiga tempat** tanpa satu pun
  menyatakan mana yang otoritatif.

### ⭐ Yang paling berharga secara konseptual

**Lima kata sifat di prinsip pembuka** — *earned, bounded, observable,
**reversible**, revocable* — dan tiga di antaranya belum pernah ada.
§11.27 **Reversibility Engine** yang paling menjelaskan: empat belas naskah
mengukur risiko dari **akibat** aksi; ini menambahkan **seberapa sulit
dibatalkan**. Itu sebabnya R4 = `DENY`.

Dan **§11.61 memberi enam kata kerja kendali** — Pause · Resume · Cancel ·
Revoke · Kill · **Rollback** — yang adalah *Human Override* yang **G-8**/#65
catat tidak datang di Fase 8. Bias Detection masih nol.

### Langkah berikutnya menurut pemilik

**Phase 12 — Digital Twin & World Simulation Engine.** ⭐ Peta 15 fase
**bertahan untuk naskah kedua** (§11.64 = §10.41) — H-20 aman.

---

## Sesi 12 — 7 September 2026

**Phase 10 direkam — peta fase diganti, dan V0 kehilangan tempatnya.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 10: Multimodal Intelligence & Perception**, §10.1–§10.41 |
| Dokumen ditambah | **11 berkas** (`165`–`175`) |
| Dokumen total | 151 → **162** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 71 → **77** (63 terbuka, 14 ditutup); **#66** ditutup |

### ✅ A-26 ditutup → H-20: petanya **diganti**, bukan digeser

Dua belas fase menjadi **lima belas**. Tiga blok akhirnya punya rumah:
**Agency → Phase 11** (menjawab kapan **B-19**/#47 diuji) · **Digital Twin →
Phase 12** · **Marketplace → Phase 14** (rumah untuk A-15/C-7).

### 🛑🛑 Tapi jawabannya menggerus H-13 — dan ini H **ketiga** yang tergerus

**A-18** ditutup sebagai **H-13** karena naskah 5 memakai tangga V dari awal
sampai akhir dan **tidak menyebut Phase 1/2/3 satu kali pun**. Naskah 13 dan 14
sekarang tidak menyebut **V0–V6** sama sekali, dan §10.41 memberi lima belas
fase sebagai urutan besar pekerjaan.

🔴 **V0 tidak punya tempat di dalamnya** — padahal V0 adalah satu-satunya
lingkup tertutup yang pernah ditetapkan (12 fitur, 23 tabel, 51 tugas).
*"Phase 1–4 Foundation"* tidak memetakan ke sana. Setelah **H-8** (dibatalkan)
dan **H-10** (monorepo), polanya jelas: **keputusan yang ditutup perlu ditinjau
ulang tiap beberapa naskah.** → **E-87** / #72.

### 🛑 Empat blok peta lama tanpa rumah baru — termasuk seluruh lapisan bisnis

*Subscription* dan *Revenue Platform* tidak muncul di satu pun dari lima belas
fase, bersama *Team Workspace*, *Enterprise Admin*, *Family Mode*, dan **Company
Wellness**. Sementara **H-6** mengakui biaya inferensi berlipat, **A-6** masih
terbuka, dan **E-41** mencatat `Billing` muncul entah dari mana.

**Model biaya yang diakui, nol fase pendapatan.** → **A-27** / #73.

### 🛑 Empat belas event persepsi tidak muat di tabel `events`

Tiga alasan, semuanya bisa diperiksa terhadap `spec/01`:

1. **`source` tidak punya nilainya** — `CHECK (... 'app','agent','integration',
   'backfill')`, tidak ada `sensor`. Setiap event persepsi ditolak constraint.
2. **Volumenya 3–4 orde lebih besar** — `PersonDetected` pada 1 Hz = **86.400
   per hari**; §10.22 menuntut 30 hari ⇒ **≈2,6 juta baris** untuk satu
   pengguna, satu kamera, satu jenis event.
3. **`idempotency_key` kehilangan artinya** — untuk aliran bingkai satu-satunya
   pembeda adalah waktunya.

⭐ **Jawabannya ada di naskah itu sendiri, hanya tidak disambungkan:** §10.10
mengubah lima bingkai jadi **satu** event, §10.11 mengubah 5.400 pembacaan jadi
**satu** kalimat. → **E-89** / #74.

### 🛑 Pemantauan berkelanjutan — dan izin `Always` yang ditambahkan karena fiturnya membutuhkannya

§10.11 mengukur **90 menit**, §10.25 mengukur **118 menit**, §10.22 menuntut
**30 hari**. Tak satu pun bisa dicapai dengan izin *while using*; ketiganya
**hanya berjalan pada `Always`** — opsi yang tidak pernah ada di naskah 4 §15
maupun §8.37.

Jadi opsi paling invasif bukan pilihan tambahan melainkan **prasyarat**.
Bedanya dengan **C-1** bukan derajat melainkan jenis: C-1 tentang kategori data
khusus di dalam sebuah gambar; ini tentang **kehadiran dan perilaku seseorang di
rumahnya sendiri yang terus dicatat**. → **C-17** / #75.

⭐ Jawabannya sudah ada — §10.28 (`Privacy Filtering` **di perangkat**) — tapi
§10.37 menempatkan Vision di M10.2 dan on-device di **tidak satu pun milestone**.

### 🛑 AetherScan: keputusan batasnya benar, konsekuensi izinnya belum ditulis

§10.40 memposisikan proyek pemilik yang lain sebagai **penyedia sensor**, bukan
sistem yang digabung — ⭐ keputusan yang benar dan penting diambil sekarang.
Catatan pertama tentang AetherScan di seluruh repo.

Tapi RF/Wi-Fi sensing berbeda jenis dari kamera: **tanpa indikator aktif, tidak
bisa ditutup, bekerja dalam gelap, menembus dinding**. Ia menangkap **siapa pun
di jangkauan** — tamu, anak, tetangga di balik dinding — tanpa satu pun bisa
menyadarinya. **C-10** berhenti jadi masalah masa depan. → **C-18** / #76.

### Temuan lain

- **B-25** — pengulangan menyaring kesalahan **acak** dan **memperkuat**
  kesalahan **sistematis**. §10.22 membuat **B-17** berlaku untuk setiap aliran
  persepsi, dan di sini kesalahannya tidak sekadar mengendap — ia naik pangkat
  jadi pola. ⭐ Bentuk jawabannya sudah ada: kalibrasi sensor terhadap laporan
  pengguna, prinsip yang sama dengan `Prediction Calibration` §9.34.
- **G-11** — tiga belas tool persepsi tanpa `risk_level`, dan itu memperlihatkan
  lubang di tangganya sendiri: **tangga risiko mengukur akibat aksi, bukan
  sensitivitas data yang disentuh**. `habit.complete` (menulis satu baris) =
  risk 2; `vision.analyze_scene()` (membaca isi kamar tidur) = tanpa angka.
- **E-88** — nama event PascalCase, konvensi **ketiga** setelah #38 ditutup.
  ⭐ Tapi yang ini mudah diperbaiki: `ImageCaptured` → `image.captured`.
- **E-90** — pohon tingkat-atas **ketujuh** (`multimodal/`), lima foldernya
  menduplikasi pohon lain. Enam naskah berturut-turut menyentuh struktur repo.
- **E-91** — `M10.1`–`M10.10` bertabrakan dengan milestone GitHub repo ini
  sendiri (M1/M2/M3). ⭐ Tapi awalannya membawa fase — praktik 2 dari 3.
- ⭐ **Model Router KEMBALI** (§10.29 + §10.34) — separuh **E-79**/#69 terjawab.
  ⚠️ Tapi sekarang ada dua perutean dan hanya satu punya rumah: *modality* vs
  *effort* (§9.20 Fast/Cognitive/High-stakes).
- ⭐ **§10.25 Provenance mengembalikan alasan yang tersimpan** — separuh
  **E-75**/#64 terjawab, dan bentuknya lebih baik dari kalimat bebas karena
  berantai sampai ke sumbernya.
- ⭐ **§10.5 Perception / Interpretation / Inference** — sumbangan konseptual
  terbesar naskah ini: **jarak sebuah klaim dari datanya** sebagai sifat yang
  berdiri sendiri. Ia menjelaskan **B-15** (`"energy": 0.62` terlihat sama
  presisinya dengan `"steps": 8420`), dan menuntut ambang confidence yang
  **berbeda per tingkat**.

### ✅ Yang diperiksa dan ternyata benar

Delapan komponen Digital Twin §10.32 **identik dengan naskah 4 §25** (diperiksa
satu per satu) · enam jenis memory H-16 **tidak bertambah** — delapan baris
§10.23 adalah `modality`, sumbu **keempat** yang tegak lurus, bukan taksonomi
keenam · bentuk `{value, confidence}` dipertahankan utuh · batas *"bukan
mind-reading, bukan clone manusia"* dipegang di naskah kelima berturut-turut.

### Langkah berikutnya menurut pemilik

**Phase 11 — Autonomous Agent & Agency Layer**: merencanakan, memakai tools,
menjalankan workflow, berkolaborasi antar-agent, meminta izin, mengambil
tindakan terbatas, mengamati hasilnya, belajar dari outcome.

---

## Sesi 11 — 7 September 2026

**Phase 9 direkam — empat butir lama ditutup sekaligus, dan satu tabrakan
penomoran yang membalik arah keselamatan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 9: Human Intelligence & Cognitive Architecture**, §9.1–§9.41 |
| Dokumen ditambah | **11 berkas** (`154`–`164`) |
| Dokumen total | 140 → **151** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 65 → **71** (58 terbuka, 13 ditutup); **#33, #42, #50, #62** ditutup |

### ⭐ Empat butir ditutup — terbanyak dari naskah mana pun

| Issue | Ditutup oleh | Kenapa akhirnya bisa |
|---|---|---|
| **#33** memory: jenis atau scope | §9.7 | Enam jenisnya **identik dengan naskah 5 §17** — daftar memory pertama yang diulang tanpa bergeser setelah lima hitungan berbeda. Jawabannya **tiga sumbu tegak lurus**: `kind` · `scope` · `tier` |
| **#50** Identity Memory permanen | §9.9 + §9.4 | *"Memory lama tidak boleh menjadi dogma"* + `Preference(user, item, context, time)` — sesuatu yang punya argumen waktu tidak bisa permanen **secara bentuk**, bukan secara kebijakan |
| **#42** alur percakapan tanpa keselamatan | §9.29 | `POLICY_CHECK` berdiri **tepat setelah PLANNING**, persis di tempat yang saya usulkan, plus keadaan `REQUIRES_CONFIRMATION` |
| **#62** akses tabel vs vault | §9.31 | *"Daripada setiap agent mengambil data sendiri-sendiri…"* — **agent tidak mengambil data sama sekali**; Context Engine menyerahkan paket |

**#62 layak dicatat khusus: jawabannya lebih baik daripada kedua pilihan yang
saya ajukan.** Saya mengusulkan dua model dilapis. Yang benar adalah keduanya
bukan cara agent *mengambil* data, melainkan dua sisi dari cara Context Engine
*menyiapkan* data. Izin jadi diperiksa **satu kali di satu tempat**, dan
katalog pertanyaan yang saya khawatirkan tidak lagi dibutuhkan.

### 🛑🛑 Tabrakan paling berbahaya dari tiga belas naskah

| Nomor | Naskah 12 §8.16 — **risiko** | Naskah 13 §9.26 — **otonomi** |
|---|---|---|
| 3 | High impact → **wajib konfirmasi** | **Ask confirmation** |
| **4** | Critical → **wajib konfirmasi** | **Bounded autonomy** — bertindak sendiri |

*"Agent ini Level 4"* berarti **"selalu minta izin"** dengan naskah 12, dan
**"boleh jalan sendiri"** dengan naskah 13. Dua tangga 0–4, sumbu berbeda,
**terbalik di ujung atas**. Kalau masuk ke kode, ia melewati konfirmasi tepat
di tempat yang paling membutuhkannya. Usul: otonomi `A0`–`A4`, risiko tetap
`R0`–`R4`, plus satu baris pengikat. Lihat **E-77** / #67.

### 🛑 Peta fase naskah 8 mati untuk Phase 9 ke atas

Phase 9 seharusnya *Enterprise & Business Platform*, Phase 10 *AI Automation
Engine*. Yang datang: Phase 9 = **Cognitive**, Phase 10 diumumkan =
**Multimodal**. **Dua fase berturut-turut tergeser tanpa rumah baru** — dan dua
issue terbuka menyebut nomor lamanya (#46 Company Wellness, #47 Email
Automation). ⭐ Urutan barunya lebih masuk akal (mata dipasang pada otak yang
sudah ada); yang perlu hanya menuliskannya. **A-26** / #66.

### 🛑 `model-router/` hilang justru ketika naskah memperkuat kebutuhannya

Pohon `intelligence/` §9.38 membuang empat folder monorepo naskah 5:
`behavior-model/` · `preference-model/` · `personalization/` ·
**`model-router/`**. Dua yang pertama adalah **L2 dari tumpukan §9.3 naskah ini
sendiri** — tumpukan dua belas lapisan punya dua lapisan tanpa rumah.

`model-router/` paling berat: §9.2 berkata LLM hanya salah satu komponen, §9.20
memberi tiga jalur (*Fast · Cognitive · High-stakes*) yang harus ada yang
memilih. Perutean dijelaskan **lebih rinci dari sebelumnya, lalu foldernya
dihapus**. **E-79** / #69.

### ⭐⭐⭐ `Prediction Calibration` menjawab B-10 — butir yang menggantung sejak naskah 4

B-10 bertanya *"akurat terhadap apa"*, dan memperingatkan *Automatic Rollback*
yang skornya sekadar model menilai model.

Kalibrasi **tidak butuh kebenaran acuan tentang jawaban yang benar** — hanya
hasil teramati: dari semua yang disebut berpeluang 70 %, apakah ~70 % terjadi?
Untuk `habit completion tomorrow = 0.68`, jawabannya datang **besok** dari
`habit_completions` yang sudah ada. Kebenaran acuan yang dihasilkan sistem
sendiri, tanpa penilai manusia, **dan bisa dijalankan sejak V0**.

### Temuan lain

- **G-10** — tumpukan 12 lapisan §9.3 **meleset satu dari judul bagiannya
  sendiri** (§9.4 ditulis "Layer 1" tapi gambar menaruhnya di L2, karena
  *Data Foundation* mengambil L1). Layer 7–11 cocok; 1–6 meleset. Dan tidak ada
  bagian "Layer 12". Ketahuan hanya dari **menghitung kotaknya**.
- **E-78** — L9–L12 bertabrakan dengan Layer 9–12 naskah 3, di rentang yang
  sama persis: *Decision Engine* naskah 3 adalah **L12**, *Decision* naskah 13
  adalah **L10**.
- **E-80** — HumanState versi ketiga: 8 → 7 → **10**, dan `mood` kembali
  setelah E-34 mencatat penghapusannya kemungkinan disengaja. ⭐ Tapi bentuk
  `{value, confidence}` per field adalah jawaban penyimpanan yang dicari A-19.
- **E-81** — `influences` kembali ke graf setelah naskah 9 membuangnya (E-55
  mencatat itu sebagai kabar baik), sementara §9.17 di naskah yang sama menuntut
  bukti kausal.
- **B-24** — Counterfactual Engine menjanjikan jawaban yang §9.17 melarang;
  sumber data `Transition` tidak ada. Dan counterfactual **mundur** adalah
  penyesalan yang dihitung.
- **C-16** — Personal Utility Model menyimpulkan **apa yang seseorang hargai**,
  lebih dalam dari Identity Memory: *"Anda menghargai Income 0,25"* tidak bisa
  dibantah dengan data apa pun. ⭐ Naskah menyelamatkannya: *"user harus dapat
  mengubahnya"* — `Edit` yang hilang, kini dituntut dua bagian naskah.

### 🔧 Koreksi saya sendiri

Di komentar #7 saya menulis *"penutupan issue ini tetap berlaku"* — **#7 tidak
pernah ditutup**. Yang tetap berlaku adalah temuannya (graf tidak menyentuh
V0), bukan penutupan. Sudah dikoreksi di issue-nya.

### ⭐ Yang berbeda dari Fase 8 — dan mengubah jawaban #58

Fase 8 menambah pekerjaan **di atas** V0 (20 tabel, 8 sprint). Fase 9 sebagian
besar **bukan pekerjaan tambahan melainkan arsitektur dari pekerjaan yang sudah
dijadwalkan**: C2 Context, C3 Memory, dan C9 Decision semuanya sudah ada di
dalam 12 fitur V0. Membacanya sebagai "fase kesembilan yang menunggu giliran"
keliru.

### Langkah berikutnya menurut pemilik

**Fase 10 — HumanVerse Multimodal Intelligence & Perception Layer** (mata,
telinga, suara, vision, sensor, wearable, camera, document understanding,
spatial intelligence, multimodal fusion).

---

## Sesi 10 — 7 September 2026

**Phase 8 direkam — satu keputusan besar ditutup, dua pengaman lama hilang.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 8: AI Safety, Security & Privacy**, §8.1–§8.46 |
| Dokumen ditambah | **12 berkas** (`142`–`153`) |
| Dokumen total | 128 → **140** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |
| Issue | 57 → **65** (56 terbuka, 9 ditutup); **#5** dan **#52** ditutup |

### ⭐ Dua bagian terkuat

**§8.10 Purpose Limitation.** Data yang diberikan untuk rekomendasi tidur tidak
otomatis boleh dipakai untuk *advertising*, *insurance scoring*, atau
*employment scoring*. Digabung dengan §7.24 (`purpose` menempel pada data) dan
§8.9 (`purpose` menempel pada persetujuan), penegakannya jadi **satu operasi
himpunan**: `data.purpose ⊆ consent.purpose`. Tidak ada naskah yang menuliskan
perbandingan itu, tetapi itulah mekanismenya — dan ia menutup **C-11** serta
separuh **C-12** (*employment scoring* dilarang dengan kata pemilik sendiri).

**§8.17 Human Confirmation → H-15.** *"AI tidak boleh langsung membeli hanya
karena sebelumnya user berkata: kalau murah, belikan."* Ini memisahkan dua hal
yang selama ini tercampur:

```
Consent      → mengizinkan AKSES ke data,      berjangka waktu (§8.9)
Confirmation → mengizinkan satu AKSI tertentu, sekali pakai   (§8.17)
```

Menutup **A-22** / #5: otomatis sampai R2, konfirmasi wajib mulai R3.

### 🛑 Dua butir yang dijanjikan Phase 8 tidak datang — dan justru dua yang baru

Naskah 8 memetakan Phase 8 sebagai *AI Safety & **Ethics*** dengan enam butir.
Butir **E-53** menyimpulkan empat di antaranya sudah ditulis di tempat lain,
sehingga **hanya *Bias Detection* dan *Human Override* yang benar-benar baru**.

Keduanya **tidak muncul satu kali pun** di 46 bagian. Judulnya sendiri berubah
jadi *AI Safety, **Security** & Privacy* — separuh etika ditukar keamanan.
*Human Override* punya kerabat tapi bukan penggantinya: §8.17 terjadi
**sebelum** aksi, §8.35 menghentikan **semuanya**; tidak ada yang membalik
**satu** keputusan yang sudah berjalan. Lihat **G-8**.

### 🛑 Jurnal: nol kali disebut di naskah keselamatan

§8.23 menjaga *Health* dan *Finance*. Tidak ada Mental Wellness, tidak ada
krisis, dan **jurnal tidak disebut sekali pun**. Padahal Journal masuk V0,
ada di Level 3 klasifikasi data, satu-satunya tempat yang bisa memuat isyarat
krisis (**C-3**), dan ditawarkan ke developer pihak ketiga (**E-61**). Daftar
DENY §8.6 pun tidak memuatnya, padahal naskah 5 §15 menempatkannya di DENY
bahkan untuk agent internal. Lihat **G-9**.

### 🛑 Tangga risiko turun satu takik — buktinya contoh yang identik

*Rekomendasi outfit* adalah contoh yang **sama persis** di dua naskah, dan ia
pindah dari **Level 1** (naskah 4 §16) ke **R0** (§8.16). Menulis ke data
pengguna turun dari Level 2 jadi **R1**; pembelian naik dari Level 3 jadi
**R4**. Ujung bawah turun, ujung atas naik.

Akibatnya nyata: `habit.complete` dan `memory.write` di `spec/05` adalah
**risk 2** dengan default `ask`. Kalau *mengubah habit* adalah R1 dan
konfirmasi baru mulai R3, **setiap tulisan ke data pengguna di V0 berjalan
tanpa satu pun konfirmasi**. Lihat **E-67**.

### 🛑 Dua pengaman lama hilang — dan keduanya dasar penutupan butir H

| Hilang | Dari | Yang tergerus |
|---|---|---|
| **`Edit`** di Privacy Center | naskah 4 §43 punya *View · Edit · Export · Delete · Revoke*; §8.36 punya delapan kata kerja tanpa satu pun cara **memperbaiki** | **H-4** ditutup atas dasar lima kata kerja itu. Dan `Edit` justru yang diminta **C-13** (*Identity Memory* harus bisa dibantah) dan **B-17** (koreksi manual Wardrobe) |
| **Alasan ringkas** di Audit Trail | naskah 4 §45 menyimpan *"audit metadata **dan alasan ringkas yang dapat diverifikasi**"*; 12 field §8.25 tidak memuat satu pun alasan | **H-7** ditutup persis karena §45 menyimpan alasan. Tanpanya, jejak audit tahu *apa* yang diputuskan tapi tidak pernah tahu **kenapa** |

Ini pola yang sudah tiga kali terjadi (**H-8** dulu dibatalkan cara yang sama):
**satu naskah memulihkan sesuatu bukan berarti sudah tetap — dan naskah baru
bisa menghapus pengaman tanpa menyebutnya.**

### Temuan lain

- **E-71** — naskah bertabrakan dengan dirinya sendiri: §8.6 memberi akses
  **tingkat tabel**, §8.11 berkata agent tidak pernah menerima baris. §8.15,
  §8.25, dan §8.37 semuanya memakai model §8.6 — jadi Personal Data Vault
  berdiri **sendirian melawan tiga bagian lain di naskahnya sendiri**.
- **E-69** — `SecurityEvent` bukan amplop keempat melainkan **model event
  kedua** (`action`+`resource`, bukan `event_type`+`payload`), dan §8.26
  memasukkannya ke bus yang sama. `user_id` hilang — padahal pemisahan
  *siapa yang bertindak* dari *data siapa yang disentuh* persis yang
  dibutuhkan **C-10**/**C-12**. `ip` mentah, sementara `spec/01` sengaja
  menyimpan `ip_hash`.
- **E-73** — pohon tingkat-atas **kelima** (`security/`, 30 folder). Empat
  naskah berturut-turut menambah pohon sendiri; **H-10** tergerus lagi (#55).
- **A-25** — Fase 8 meminta **8 sprint** dan **20 tabel baru** di atas 23 tabel
  V0, sementara seluruh V0 adalah 7 sprint dalam 4–6 minggu.
- ⭐ **S8.1–S8.8** adalah penomoran pertama yang membawa fasenya sendiri —
  usul yang sama sebaiknya berlaku surut untuk `R1–R8` dan dua `D1–D8`.

### 🔧 Koreksi saya sendiri

Butir **E-60** saya tulis sebagai kehilangan murni: DP-L8 membuang
`requires_confirmation`, dan `spec/05` aturan 3 mempertahankannya di manifest.
§8.18 menunjukkan tempat yang lebih benar — **Policy Engine**, bukan manifest.
Selama field itu ada di manifest, **penulis agent** yang menentukan kapan
penggunanya dimintai izin, dan agent pihak ketiga tinggal menuliskan daftar
kosong. Jadi yang perlu diperbaiki bukan naskahnya, melainkan **aturan 3 di
spesifikasi saya sendiri**: ia memeriksa manifest, seharusnya memeriksa ada
tidaknya baris policy.

### ✅ Yang terbukti benar

`backup` yang saya tambahkan sendiri di sesi 9 — di luar tujuh tempat naskah 11
— muncul di §8.38 sebagai langkah nyata, bersama **Identity Verification** dan
**Deletion Verification** yang juga belum pernah ada.

### Langkah berikutnya menurut pemilik

**Fase 9 — HumanVerse Intelligence & Cognitive Architecture.** ⚠️ Ini **bukan**
Phase 9 di peta naskah 8, yang berisi *Enterprise & Business Platform*. Perlu
dinyatakan: fase berikutnya menyela urutan peta, atau petanya yang berubah.

---

## Sesi 9 — 3 September 2026

**Phase 7 Data & AI Infrastructure direkam — dan satu keputusan lama tergerus.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 7: Data & AI Infrastructure**, §7.0–§7.35 |
| Dokumen ditambah | **10 berkas** (`132`–`141`) |
| Dokumen total | 118 → **128** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### ⭐ Dua bagian terkuat

**§7.24 Privacy metadata.** Data membawa `data_class`, `purpose`, `retention`,
`consent_required`. Ini **pembatasan tujuan yang bisa ditegakkan mesin** — data
ber-`purpose: [personalization]` tidak bisa dipakai melatih model tanpa
`purpose` baru. Persis yang diminta **C-11**.

**§7.25 Deletion Engine.** Cascade ke 7 tempat, memperluas prosedur hapus akun
di `spec/01` dengan **empat tempat yang belum saya cakup**: Lakehouse (Parquet
tidak punya `DELETE`), Features (nilai turunan tetap membawa jejak), Graph
(simpul yatim), Caches (Redis tidak ikut transaksi). Saya tambahkan satu lagi
yang belum disebut siapa pun: **backup**.

### 🛑 H-10 perlu ditinjau ulang — keputusan yang saya tutup, tergerus

Naskah 5 §4 menetapkan monorepo final, dan saya menutup **E-27** sebagai
**H-10**. Sejak itu **tiga naskah menambah pohon tingkat-atas sendiri**:
`research/` (naskah 9), `developer-platform/` (naskah 10), `data-platform/`
(naskah 11, 21 folder) — tanpa satu pun menempatkannya di dalam monorepo.
`data/` dan `data-platform/` bahkan tumpang tindih di tiga folder.

### 🛑 Dua tabrakan penomoran baru

- **E-63** — tangga V0–V5 §7.0 memberi **makna ketiga** untuk nomor versi
  (V3 = *Lakehouse* di sini, *Multi-Agent Platform* di naskah 5 §33,
  *Agent Platform* di §1). Butir **A-18** ditutup dengan *"V0–V6 kanonik"* —
  tapi kalau nomornya sendiri berarti tiga hal, itu tidak menolong.
- **E-64** — **`D1`–`D8` dipakai dua kali**: Developer Platform (naskah 10) dan
  Data Platform (naskah 11). *"Kita di D4"* berarti *Agent SDK* **dan**
  *AI Data*.

### Temuan lain

- **G-6** — Level 4 *Highly Sensitive* **tanpa satu contoh pun**, padahal
  justru level ini yang menentukan aturan paling ketat.
- **E-65** — envelope event ketiga. ⭐ `actor{type,id}` adalah perbaikan nyata
  (membedakan event dari agent vs dari orang), ⚠️ tapi `idempotency_key` dan
  `recorded_at` hilang.
- 🔧 **Koreksi saya sendiri:** di #7 saya menulis Neo4j relevan di **V2**;
  §7.0 menempatkan Knowledge Graph di **V4**. Kesimpulan tidak berubah (tidak
  menghalangi V0), tapi jaraknya lebih jauh.

---

## Sesi 8 — 3 September 2026

**Phase 6 Developer Platform direkam — satu issue tertutup, dua pengaman hilang.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 6: Developer Platform**, 25 layer |
| Dokumen ditambah | **9 berkas** (`123`–`131`) |
| Dokumen total | 109 → **118** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### ⭐ #38 tertutup — format nama event dua segmen

DP-L12 memakai `habit.completed`, `goal.completed`, **`outfit.selected`**,
`journal.created`. Yang menentukan: naskah 7 Layer 22 menulis event yang **sama
persis** sebagai `fashion.outfit.selected` (tiga segmen); naskah ini menulisnya
`outfit.selected`.

**Dua naskah dua segmen melawan satu naskah tiga segmen** — dan dua segmen
sudah dipakai di `spec/03`. Batas waktu "sebelum Sprint 3" tidak lagi jadi
soal.

### ⭐ Sandbox + Review System menjawab beban hukum marketplace

DP-L14 (**Testing Sandbox** dengan mock data) dan DP-L18 (**Review System**:
Security, Permission, Stability, Documentation, Testing) adalah jawaban
terbesar untuk **A-15/C-7** setelah enam naskah hanya berupa kekhawatiran.

Yang masih hilang: perjanjian pemroses data, jalur banding, dan tanggung jawab
saat agent pihak ketiga berbuat salah.

### 🛑 Dua pengaman hilang justru di tempat paling dibutuhkan

- **E-60** — Manifest marketplace (DP-L8) **membuang `risk_level` dan
  `requires_confirmation`** yang ada di naskah 5 §14. Keduanya adalah field yang
  membuat aksi agent bisa dikendalikan, dan menghilang tepat di manifest untuk
  agent **pihak ketiga**.
- **E-61** — **`journal.read` ditawarkan sebagai scope developer pihak ketiga**,
  bertabrakan dengan naskah 5 §15 (jurnal ada di daftar DENY bahkan untuk agent
  internal) dan aturan 6 `spec/05`.
- **C-14** — webhook **`journal.created`** dikirim ke server developer;
  meski muatannya hanya `word_count`, keberadaan event itu memberi tahu pihak
  ketiga **kapan seseorang menulis jurnal**.

### Temuan lain

- **E-59** — tabrakan penomoran: Phase 6 memulai **Layer 1** lagi, sehingga
  *"Layer 22"* berarti Engineering Standards **dan** Example Library.
- **E-62** — SDK naik dari 5 bahasa jadi 7 (+ go, rust).
- **E-57** — skema penomoran keempat: V0–V6 · Sprint 0–6 · R1–R8 · D1–D8.
- Format API `/v1/<resource>` cocok dengan naskah 7; yang menyimpang justru
  `spec/04` (`/api/v1/...`) — itu bagian saya, perlu diselaraskan.

---

## Sesi 7 — 3 September 2026

**Phase 5 Research Lab direkam — 15 pilar, dan satu masalah urutan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 5: HumanVerse Research Lab**, 15 research pillar |
| Dokumen ditambah | **9 berkas** (`114`–`122`) |
| Dokumen total | 100 → **109** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### ⭐ Kabar terbaik: Pillar 9 hampir menutup #2

*Personal Representation Layer* punya **6 dari 7 dimensi identik** dengan Human
Dashboard naskah 4 §28 — bedanya cuma *Discipline* ↔ *Lifestyle* — dan
menambahkan tepat apa yang selama ini kurang: **`confidence`, `trend`,
`evidence` per dimensi**. Bentuknya langsung muat di `human_states.metrics
jsonb` yang sudah dirancang.

Setelah enam naskah beradu model angka pengguna, ini yang pertama **mendekat**,
bukan menjauh.

### ⭐ Pillar 7 praktis menutup #7 (arah sebab-akibat)

Rantai `Sleep → Energy → Workout → Mood → Productivity` **sama persis** dengan
Layer 8 naskah 3, dan berbeda dari naskah 1. Sekarang **2 naskah vs 1**, dan
yang dua adalah yang lebih baru. Ditambah *"semua node memiliki confidence"*.

Pillar 3 juga **membuang `causes`, `influences`, `predicts`** dari daftar
relasi graf — sejalan dengan naskah 4 §7.

### 🛑 Temuan terpenting: urutannya, bukan isinya (B-21)

Roadmap dimulai dari **R1 Behavior Prediction** — justru pilar yang paling
bergantung pada data. Seluruh dataset BFM (`behavior_events`, `habit_events`,
`sleep_events`, `mood_events`, `calendar_events`, `context_snapshots`) baru ada
**setelah V0 dipakai berbulan-bulan**, dan `sleep_events` + `calendar_events`
**tidak ada di V0 sama sekali**.

Yang bisa dikerjakan lebih dulu tanpa data: **R8 Benchmark**, **R5
Explainability**, lalu **R3 Memory Compression**.

### Temuan lain

- **B-20** — Compression Policy **tidak mengompres apa pun**: Raw, Episode,
  dan Summary sama-sama disimpan *"penuh"* tanpa jendela waktu, padahal
  masalahnya justru *"jutaan event tidak bisa dikirim semuanya ke LLM"*.
- **C-13** — **Identity Memory permanen** (*"User is consistently committed to
  strength training"*) adalah karakterisasi yang tidak bisa kedaluwarsa,
  menguatkan dirinya sendiri, dan bertabrakan dengan hak hapus.
- **E-54** — dua pohon `research/` berbeda **di dalam naskah yang sama**;
  keduanya berjumlah 12 sehingga sekilas terlihat cocok (pola **E-13**).
- **E-57** — sekarang ada tiga skema penomoran berjalan berdampingan:
  V0–V6 · Sprint 0–6 · R1–R8.

---

## Sesi 6 — 3 September 2026

**Naskah kedelapan direkam — peta Phase 5–12, dan satu angka bertabrakan 10×.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Peta Phase 5–12** + taksiran kemajuan 45 % → berkas `113` |
| Dokumen total | 99 → **100** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### Yang diperiksa dan benar

- **Aritmetika delapan fase benar**: 50+40+50+30+30+40+40+100 = **380**, tepat
  di dalam rentang "300–500 dokumen".
- **"Tidak ingin memperpanjang hanya demi panjang"** — pertama kalinya dalam
  delapan naskah pemilik membatasi dirinya sendiri sebelum diminta.
- **Bias Detection** dan **Human Override** benar-benar baru. *Human Override*
  khususnya adalah pasangan yang selama ini hilang dari janji *"Act di bawah
  kontrol pengguna"*: yang ditulis baru **izin sebelum** aksi, belum
  **pembatalan sesudah**.

### Tiga temuan

- **E-51** — Phase 5 berbeda **sepuluh kali lipat** antara dua naskah: naskah 7
  menulis *500+ spesifikasi*, naskah 8 menulis *50+ dokumen*. Aritmetika naskah
  8 sendiri membuktikan 50+ yang benar (total 380), tapi butuh konfirmasi.
- **E-52** — **Multi-Agent Collective Intelligence hilang** dari Phase 5.
  Itu justru riset di balik janji pembuka naskah 2: *"ratusan AI Agent bekerja
  secara bersamaan"*.
- **E-53** — Phase 8, 11, dan 12 **sebagian mengulang** yang sudah ditulis.
  Phase 12 (*Event Schema, Agent Contracts, Sprint Backlog, CI/CD, Docker*)
  adalah pekerjaan yang **sudah selesai untuk V0** di `spec/` — bedanya hanya
  skala (23 tabel vs 100+, ~40 endpoint vs 500+).

### 🔧 Koreksi hitungan saya sendiri

Sesi lalu saya menulis "lewat **900 dokumen**". Itu **terlalu besar** — saya
menjumlahkan lingkup yang tumpang tindih. Naskah 8 memberi angka yang lebih
tepat: **380** untuk delapan fase tersisa, dan sebagiannya mengulang yang sudah
ada. Butir **A-24** diperbaiki.

### Dua risiko baru

- **C-12** — *Company Wellness* (Phase 9) berarti **pemberi kerja** menyentuh
  data kesehatan pekerja. Berbeda dari *Coaches* karena ada ketimpangan
  kekuasaan: persetujuan kepada atasan tidak pernah sepenuhnya bebas.
- **B-19** — Phase 10 (*Email Automation*, *Cross-App Actions*) adalah **ujian
  pertama** janji kendali manusia. Itu Risk Level 3, tingkat yang sengaja tidak
  punya satu pun tool di V0.

---

## Sesi 5 — 3 September 2026

**Naskah ketujuh direkam — dan lubang naskah 3 terulang persis.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 4 Enterprise OS**, Layer 21–50 + teaser Phase 5 |
| Dokumen ditambah | **13 berkas** (`100`–`112`) |
| Dokumen total | 86 → **99** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### ⚠️ Dua lubang, bentuknya sama seperti naskah 3

| Naskah 3 | Naskah 7 |
|---|---|
| Layer 14 terpotong di tengah tabel (**G-1**) | Layer 44 terpotong di tengah tabel (**G-4**) |
| Layer 15/16 hilang + fragmen tanpa judul (**G-2**) | Layer 45 hilang + fragmen *"jangan lompat ke Kubernetes"* (**G-5**) |

Dua naskah panjang, dua tabel terpotong di tempat yang sama macamnya.
Kemungkinan besar batas salin-tempel. **Ditandai hilang, tidak ditambal.**

### Yang paling berguna dari naskah ini

- **Layer 40: Memory ≠ Knowledge.** *Memory = pengalaman pengguna, Knowledge =
  pengetahuan dunia.* Menjelaskan kekaburan lama *Semantic Memory*, dan punya
  konsekuensi nyata: pengetahuan dunia tidak ikut terhapus saat akun dihapus.
- **Layer 50: empat fondasi** — rumusan visi paling tajam dari tujuh naskah,
  dan tiga dari empat sudah punya bentuk teknis di V0.
- **Layer 34:** *"Jangan mengoptimalkan manipulasi; optimalkan pengalaman
  pengguna"* — ditulis di baris yang sama dengan *retention* dan *engagement*.
- **ADR-004** mengunci LangGraph; disebut sejak naskah 2, baru sekarang jadi
  keputusan.

### Delapan ketidakcocokan baru (E-43..E-50)

Yang paling mendesak: **E-43** — format nama event **tiga segmen**
(`fashion.outfit.selected`) bertabrakan dengan **dua segmen** di naskah 5 §7
(21 event, semuanya dua segmen). **Nama event tidak boleh diganti setelah
dipakai**, jadi harus dipilih sebelum Sprint 3.

Juga: **E-48** dua daftar persona di dua lapisan berdampingan (hanya *Student*
yang sama), dan **E-45** rantai percakapan 9 langkah yang melewatkan
Safety/Risk.

### Hitungan yang perlu diperhatikan

Phase 5 menambah **500+ spesifikasi riset**. Total: 100 → 160 → 300+ →
14 lapisan → +500 = lewat **900 dokumen**, dengan **0 baris kode**
(butir **A-24**).

---

## Sesi 4 — 3 September 2026

**Naskah keenam direkam — lalu lapisan 04 dikerjakan: Engineering Spec v1.0.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Peta 14 lapisan engineering + Operating Model** → berkas `98` |
| Hasil kerja baru | **`spec/`** — 8 berkas, **bukan kata pemilik** |
| Dokumen total | 85 → **86** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### Isi `spec/`

23 tabel PostgreSQL dengan DDL lengkap · ERD + 6 aturan kepemilikan data ·
22 event dengan versi/urutan/idempotensi · endpoint REST V0 + Privacy Center ·
manifest agent dengan 6 aturan validasi + risk gate · batas modul yang
ditegakkan CI · **51 tugas** dalam 7 sprint.

### Temuan terbesar sesi ini

**Tiga issue yang saya kira memblokir ternyata tidak perlu diputuskan sekarang** —
skemanya bisa menampung kedua kemungkinan tanpa biaya:

| Issue | Ternyata |
|---|---|
| #33 memory: jenis atau scope | **keduanya** — menjawab pertanyaan berbeda (`kind` = pengambilan, `scope` = izin) |
| #32 tiga skala skor | simpan **0–1** — 100-poin & persen lossless ke sini, sebaliknya tidak |
| #2 lima model angka | `metrics jsonb`, bukan 7 kolom tetap |
| #7 model graf | **tidak menyentuh V0** — Neo4j baru V2 |

Artinya **V0 bisa dimulai sekarang**; penghambat nyata tinggal #3 (waktu) dan
#20 (merek). ⚠️ Tapi menunda bukan menjawab — selama #2 belum dipilih, tidak
ada yang bisa **menghitung** angkanya.

### Cacat yang ditemukan dari menulis spesifikasi (E-42)

Daftar 19 tabel V0 naskah 5 §31 **tidak cukup untuk arsitektur V0 sendiri**:
tidak ada `events` (padahal §30 menggambar *Event System* sebagai lapisan wajib
dan §7 berkata *"setiap aktivitas menjadi event"*), dan `agent_runs` menunjuk
tabel `agents` yang tidak ada. Ditemukan hanya karena mencoba menulis DDL-nya —
tidak terlihat saat membaca naskah.

---

## Sesi 3 — 3 September 2026

**Blueprint Engineering v1.0 direkam — lima butir ditutup, satu dibatalkan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Blueprint Engineering v1.0**, 34 bagian |
| Dokumen ditambah | **18 berkas** (`80`–`97`) |
| Dokumen total | 67 → **85 berkas** di `docs/` |
| Berkas kode | tetap **0** |

### Yang naskah 5 tutup

| # | Butir | Jawaban |
|---|---|---|
| H-10 | E-27 struktur repo | Monorepo final — **menggabungkan** struktur naskah 2 dan naskah 4 |
| H-11 | E-2/E-28 Weather & Calendar | **Tool**, bukan agent |
| H-12 | A-10 Kafka vs Redis Streams | **Empat penyimpanan**: PostgreSQL · Qdrant · Neo4j · Redis |
| H-13 | A-18 Phase vs V0–V6 | **V0–V6** — Phase 1/2/3 tidak disebut sekali pun |
| H-14 | B-15/B-1 angka taksiran & cold start | **Confidence Layer** — `confidence` + `evidence_count`, low → tanya pengguna |

### ❌ Yang dibatalkan

**H-8 gugur.** GroomingAgent yang kembali di naskah 4 **hilang lagi** di daftar
22 agent naskah 5, bersama HealthAgent, ProductivityAgent, EntertainmentAgent,
dan ResearchAgent. Satu naskah memulihkan sesuatu bukan berarti sudah tetap.

### Yang naskah 5 buka (E-34..E-41)

- **A-19 memburuk**: kini **lima** model angka pengguna, HumanState turun jadi
  7 field (`mood` keluar), DigitalTwin tukar Social → Lifestyle.
- **E-37** tiga sistem skoring dengan skala berbeda (100 % · 100 poin · 0–1).
- **E-39** memory: 6 jenis (§17) vs nama scope (§14) — tabel `memories` butuh
  salah satunya.
- **E-40** V0 bertambah jadi **12 fitur**, targetnya tetap 4–6 minggu, dan
  §32 memecahnya jadi **7 sprint** ≈ 4–6 hari per sprint.
- **E-38** `PreparationAgent` di §13 tidak ada di daftar 22 agent.
- **E-41** `Billing` muncul sebagai domain platform tanpa pernah dibahas.

### Langkah berikutnya menurut pemilik

**Engineering Specification v1.0** — schema PostgreSQL lengkap, ERD, event
contract, API endpoint, Agent Registry schema, MCP Tool Registry, permission
schema, prompt architecture, Docker Compose, CI/CD, backlog task V0.
Lihat [`97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md`](97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md).

---

## Sesi 2 — 3 September 2026

**Naskah keempat direkam · nama diputuskan · repo dibuat.**

| Hal | Hasil |
|---|---|
| Nama proyek | ✅ **HumanVerse XOS** diputuskan pemilik (menutup **A-7**) |
| Folder | `E:\xtheoputra\HumanOS AI` → `E:\xtheoputra\HumanVerse XOS` |
| Naskah baru | **Phase 3 — AI-Native Human Ecosystem**, 58 bagian |
| Dokumen ditambah | **28 berkas** (`50`–`77`) |
| Dokumen total | 38 → **67 berkas** di `docs/` (termasuk berkas ini) |
| Berkas kode | tetap **0** (disengaja) |
| Git | diinisialisasi, repo privat dibuat, di-push |

### Yang naskah 4 tutup

- **A-2 (MVP)** → **V0 HumanVerse Foundation**, 10 fitur + 4 agent, 4–6 minggu.
- **A-7 (nama)** → HumanVerse XOS.
- Manifest agent pertama (§11), jalan keluar data (§43), contoh event (§37).
- Beban operasional (B-7) dan biaya inferensi (B-8) diakui & dijadwalkan
  bertahap oleh pemilik sendiri (§38, §48, §49, §51, §58).

### Yang naskah 4 buka

- **A-17** siapa yang mengerjakan V0 dalam 4–6 minggu
- **A-18** Phase 1/2/3 atau V0–V6 sebagai rencana kanonik
- **A-19** empat model angka pengguna yang saling terpisah
- **A-20** Mental Wellness & Lifestyle: dibuang atau ditunda
- **A-21 / A-22** ambang eksperimen · level risiko yang boleh otomatis
- 10 ketidakcocokan baru (**E-24**…**E-33**), termasuk naskah 4 yang
  bertabrakan dengan dirinya sendiri (**E-25**)

### Langkah berikutnya menurut pemilik

**Blueprint Engineering v1.0** — repo final, 100+ modul, seluruh schema, event
schema, API contract, permission model, urutan task untuk AI coding agent.
Lihat [`77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md`](77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md).

---

## Sesi 1 — 3 September 2026

Tiga naskah pemilik (HumanOS · HumanVerse X · Phase 2 Blueprint) direkam
menjadi **39 berkas**, nol baris kode. Disiplin dokumen ditetapkan: berkas
naskah merekam kata pemilik apa adanya, semua keraguan masuk
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).
