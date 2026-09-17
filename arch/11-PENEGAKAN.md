# 11 — Penegakan

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Berkas ini tidak diminta naskah 24. Ia ada karena pelajaran repo ini sendiri,
> yang sudah muncul lebih dari sepuluh kali: **aturan yang dinyatakan tetapi
> tidak dijaga akan dilanggar, dan pelanggarannya baru ditemukan berkas-berkas
> kemudian.**

---

## §1 Kenapa berkas ini ada

| Aturan yang pernah dinyatakan | Berapa kali dilanggar sesudahnya |
|---|---|
| nama event `domain.verb` ([#38](../../issues/38)) | **128 nama**, sembilan dari sembilan naskah yang punya model event |
| monorepo final (**H-10**) | **sepuluh kali** |
| *“kode agent tidak boleh mengimpor `security/`”* (§8.42) | 🛑 tak pernah bisa **dinyatakan** — ada 19 pohon keamanan |
| `risk_level` ada di skema manifest | **13 tool persepsi** tanpa satu pun mengisinya |
| `Rollback` di daftar kendali (§11.61) | **hilang satu naskah kemudian** (§13.34) |
| awalan API `/v1` | janji di komentar penutup [#38](../../issues/38), **tak pernah dijalankan** sampai [K-8](../docs/KEPUTUSAN-DIDELEGASIKAN.md) |

> 🔑 **Pola tunggalnya:** semuanya adalah aturan yang **benar**, ditulis oleh
> orang yang **serius**, dan tidak satu pun punya sesuatu yang berkata *tidak*
> ketika dilanggar.
>
> 💡 **Karena itu satu baris tambahan berlaku untuk seluruh `arch/`: sebuah
> aturan di folder ini tidak dihitung SELESAI sampai barisnya ada di tabel §3.**

---

## §2 Kapan tiap pemeriksaan dipasang

> 🔨 **Diperbarui 16 September 2026 — Sprint 0 dikodekan** (branch
> `v0/sprint-0-foundation`, menunggu HUMAN REVIEW). Kolom ketiga kini menulis
> keadaan, bukan rencana; rinciannya per pemeriksaan di blok ` ```penegak `
> §6, yang dibaca `tests/unit/test_penegak.py`.

| Kelompok | Dipasang di | Keadaan |
|---|---|---|
| **B** batas keras (6) | Sprint 0 tugas **0.8** | ✅ **B-2** kontrak `import-linter` · ✅ **B-6** pohon `03` **dan repo nyata** · ⏳ B-1 (tugas 4.5) · B-3 (T5) · B-4 (T10) · B-5 (T2) |
| **M** modul & nama (4) | Sprint 0 **0.7 · 0.8** | ✅ **4 dari 4** — M-1 · M-2 · M-3 `import-linter`; M-4 atas repo nyata |
| **P** penyimpanan & migrasi (6) | Sprint 0 **0.4** | ✅ P-1 · P-2 · P-3 atas [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) **dan berkas migrasi** · ⏳ P-4 (T2) · P-5 (D5) · P-6 (T9) |
| **E** event (5) | Sprint 3 **3.1** | ✅ E-1 · E-2 · E-4 · E-5 · ✅ **E-3 separuh DDL** — uji admisinya menunggu 3.1 |
| **A** agent & tool (3) | Sprint 4 **4.2** | ✅ A-1 · A-2 · A-3 atas [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) + DDL — validator manifest sungguhan menunggu 4.2 |
| **G** governance (1) | **SUDAH JALAN** atas tabel [`08`](08-AGENT-CONTRACTS.md) §4 | ✅ |
| **R** roadmap (1) | **SUDAH JALAN** atas tiap roadmap di `docs/` & `arch/` | ✅ — merah: keputusan cakupan pemilik |

> 💡 **Pertanyaan sesi 28 ditanyakan sekali lagi pada keempat belas sisanya —
> *apakah yang diperiksanya sudah ada dalam bentuk lain?* — dan memindahkan dua
> lagi tanpa menunggu tugasnya:** **E-3** membaca `CHECK` kolom
> `events.source` di DDL, dan **A-1** membaca skema manifest `spec/05` yang
> sudah memisahkan `max_risk` (R) dari `autonomy.max_level` (L). Keempat
> sisanya (M-1 · M-2 · M-3 · B-2) memang menunggu kode — dan kodenya kini ada.

### 🔴🔴 Kolom ketiga pernah salah untuk DELAPAN pemeriksaan

Sampai 11 September 2026 tabel di atas menjawab *“butuh kode? **ya**”* untuk
seluruh kelompok **P**, **A**, dan untuk **B-6** — dan jawaban itu benar untuk
**artefak yang BERJALAN**. Tetapi yang diperiksa P-1/P-2/P-3 adalah **DDL**,
A-2/A-3 adalah **manifest**, B-6 adalah **pohon direktori** — dan ketiganya
**sudah ada, sebagai dokumen**, sejak `spec/01`, `spec/05`, dan
[`03`](03-MONOREPO-FINAL.md) ditulis.

> 💡💡 **Pertanyaan yang terlewat bukan *“apakah aturannya benar”* melainkan
> ***“apakah yang diperiksanya sudah ada dalam bentuk lain?”*** Delapan
> pemeriksaan menunggu kode yang belum ditulis, sementara yang mereka periksa
> sudah tergeletak di repo selama berhari-hari.**

⇒ yang bisa jalan tanpa kode produksi: **4 → 12 dari 26.**

### ✅ Lima pemeriksaan berhenti menjadi rencana — 11 September 2026

[`../tools/periksa_dokumen.py`](../tools/periksa_dokumen.py) menjalankan
**E-1 · E-2 · E-5 · G-1 · R-1** dengan **nol baris kode produksi**. Ia keluar
dengan kode **1** kalau ada yang gagal, jadi ia bisa dipasang sebagai gerbang CI
sebelum berkas kode pertama ditulis.

```
$ python tools/periksa_dokumen.py                      # 16 Sep 2026
B-6  28 direktori arch/03 + 24 repo nyata    ✅ LULUS
M-4  33 direktori repo nyata                 ✅ LULUS
P-1  46 tabel (spec/01 23 · migrasi 23)      ✅ LULUS
P-2  46 tabel                                ✅ LULUS
P-3  40 kolom user_id                        ✅ LULUS
E-1 · E-2 · E-4 · E-5                        ✅ LULUS
E-3  2 tabel events (spec/01 · migrasi)      ✅ LULUS
A-1  manifest + 2 tabel agents               ✅ LULUS
A-2 · A-3 · G-1                              ✅ LULUS
R-1  10 pasangan          🛑 GAGAL — 7 temuan (keputusan cakupan pemilik)

$ uv run lint-imports                                  # pyproject.toml
M-1 · M-3 lapisan modul · M-1 siklus · M-2 ×12 · B-2   15 kept, 0 broken
```

### ✅ Dan MERAHnya dibuktikan, bukan diandaikan

```
$ python tools/uji_mutasi.py
25 mutasi · 25 terbukti BERBUNYI — tiap mutasi wajib melahirkan temuan BARU

$ uv run python tools/uji_mutasi_kode.py
42 mutasi · 42 terbukti BERBUNYI — dengan ALASAN yang dimaksud
   19 import-linter (satu per id kontrak + modul baru, siklus, stdlib, berkas baru)
    1 ruff banned-api · 3 peta penegak §6 · 4 rantai pasok & tanpa-tagihan · 1 pemindai rahasia
   14 basis data — 8 migrasi · 6 kepemilikan data (FK komposit · RLS · isi kebijakan · GRANT · peran api · kebocoran pool)
```

> 🔴 **Dua hal yang uji mutasi ajarkan di Sprint 0 — keduanya tentang alat
> ukurnya sendiri.** (1) Versi pertama `uji_mutasi.py` membaca dan menulis
> berkas lewat `read_text`/`write_text`; di Windows keduanya menerjemahkan
> akhir baris, sehingga **berkas ber-LF yang "dikembalikan" diam-diam menjadi
> CRLF**. Kini dibaca dan dikembalikan sebagai byte. (2) Kode keluar `1` saja
> tidak membuktikan penegak menangkap hal yang dimaksud — uji yang gagal karena
> galat lingkungan juga keluar `1`. `uji_mutasi_kode.py` menuntut **keluarannya
> memuat alasan yang dimaksud**, bukan hanya kodenya.
>
> 🔴 **Dan P-3 ternyata bisa dibohongi komentar.** Penjaganya dicari sebagai
> *baris yang memuat `CHECK`, `data_subject`, dan `user_id`* — dan sebuah
> komentar SQL yang menyebut ketiganya lolos sebagai penjaga. Migrasi 0001
> memang punya komentar semacam itu tepat di atas CHECK-nya. Komentar kini
> dibuang sebelum diperiksa, dan mutasi *“penjaga tinggal KOMENTAR”*
> membuktikannya.

> 🔑 **Dua belas LULUS tidak berarti apa pun sampai bisa ditunjukkan bahwa
> kedua belasnya SANGGUP GAGAL.** Regex yang tidak pernah cocok dan tabel yang
> tidak pernah terbaca memulangkan LULUS dengan tenang —
> [`../tools/uji_mutasi.py`](../tools/README.md) merusak satu hal yang tiap
> pemeriksaan **klaim** deteksi, lalu menuntut kode keluar 1.
>
> 🔴 **Putaran pertamanya menuduh G-1 buta.** Mutasinya mengubah **nama** pasal
> (`Reversibility` → `Reversibility X`) dan G-1 diam — padahal G-1 memang tidak
> memeriksa nama pasal, ia memeriksa **adanya penegak**. Yang cacat mutasinya.
> ⇒ **sebuah uji yang tidak menguji apa yang dikiranya diuji akan menuduh yang
> benar**, dan itu lebih berbahaya daripada uji yang tidak ada.

> 🛑🛑 **DAN GERBANGNYA SENDIRI TIDAK PERNAH BERJALAN.** Jalan pertama
> `.github/workflows/periksa-dokumen.yml` — satu-satunya yang pernah ada di repo
> ini — berhenti sebelum langkah pertama: *“The job was not started because
> recent account payments have failed or your spending limit needs to be
> increased.”* Repo privat ⇒ menit Actions ditagih.
> ⇒ **skripnya hijau (diverifikasi lokal), gerbangnya mati.** Yang salah bukan
> tagihannya melainkan urutan saya: workflow dipasang, lalu **hijaunya
> diasumsikan**. Pertanyaan yang seharusnya ditanyakan bukan *“apakah berkasnya
> benar”* melainkan ***“apakah ia benar-benar JALAN”*** — dan itu pertanyaan
> yang sama yang hari ini sudah menemukan tiga hal lain.
> **Sampai [#160](../../issues/160) dibuka pemilik, pemeriksaannya MANUAL:**
> `python tools/periksa_dokumen.py` sebelum tiap commit.
>
> 🔧 **17 Sep 2026 — pemilik menjawab #160 dengan cara lain (H-26):** *“gunakan
> alternatif versi gratis, jangan ada tagihan.”* Pemicu otomatis Actions
> dimatikan (dijaga `test_rantai_pasok.py`); gerbang penuh
> `tools/ci_lokal.py --lapor-github` berjalan di mesin pengembang dan
> menempelkan status `ci-lokal` ke commit — gratis, lewat API status commit.
> Yang tetap tidak ada: **penghalang** penggabungan PR merah (perlindungan branch
> tidak tersedia untuk repo privat pada paket akun ini).

> 🔑 **Tiga aturan rancangan yang membuatnya tidak menjadi salinan kedua dari
> dokumen:**
>
> 1. **Registry dibaca DARI dokumennya.** Daftar 46 domain diambil dari
>    [`07`](07-EVENT-CONTRACTS.md) §2, daftar pasal dari
>    [`08`](08-AGENT-CONTRACTS.md) §4, daftar pasangan gerbang dari blok
>    ```` ```r1 ```` di [`10`](10-URUTAN-IMPLEMENTASI.md) §2.1. Tidak satu pun
>    ditulis ulang di dalam kodenya. Kalau dokumennya berubah, pemeriksa ikut;
>    **kalau dokumennya hilang, pemeriksa GAGAL dengan galat — bukan lulus
>    karena tidak menemukan apa pun untuk diperiksa.**
> 2. **Populasi yang diperiksa dinyatakan.** `--senarai` mencetak tiap nama
>    beserta baris asalnya, dan daftar pengecualian menyertakan **alasan per
>    baris** — supaya pengecualian tidak menjadi tempat menyembunyikan temuan.
> 3. **Angka di prosa diperiksa terhadap tabel di atasnya.** Itu yang menangkap
>    *“39 domain”* di §2 [`07`](07-EVENT-CONTRACTS.md) yang tabelnya memuat 45.

### 🔴 Dan alat ukurnya sendiri salah dua kali sebelum benar

Dicatat karena bentuknya berulang di repo ini, dan karena laporan yang tidak
menyebutkan ini akan terbaca lebih kuat daripada yang sebenarnya:

| | Yang keliru | Akibat kalau tidak ketahuan |
|---|---|---|
| 1 | panen butir roadmap **ikut membaca catatan audit saya sendiri** ⇒ `G18.11 Safety, Privacy & Governance` — milestone yang hanya saya **usulkan** — terhitung sebagai milestone yang **ada** | Phase 18 akan tampak punya gerbang keselamatan. **Alat yang mencari kegagalan justru menutupinya** |
| 2 | panen nama event **hanya membaca token di dalam backtick** ⇒ kedelapan nama `security.*` (K-10) tidak pernah diperiksa | seluruh keluarga event **keamanan** lolos E-1 dan E-2 — keluarga yang paling mungkin diaudit |

> 💡💡 **Pembeda untuk keliru 1 tidak dikarang: `docs/SENSUS-EVENT.md` sudah
> mengujinya** — percobaan *“semua baris `>` itu catatan saya”* SALAH (naskah
> juga mengutip pemilik dengan `>`), dan yang lulus validasi silang adalah
> menilai blok dari **baris pertamanya**. Aturan itu dipakai ulang apa adanya.
>
> 💡💡 **Keduanya ditemukan dengan satu pertanyaan yang sama, dan ia layak
> ditanyakan setiap kali sesuatu berubah menjadi hijau: *apa yang alat ukur ini
> TIDAK PERNAH lihat?*** Bukan *“apakah hasilnya benar”* — hasilnya benar untuk
> populasi yang dilihatnya. Yang salah populasinya.

✅ **Bukti kedua pembetulan sah:** sesudahnya, kedelapan roadmap memulangkan
jumlah butir yang **sama dengan angka yang dokumennya sendiri sebutkan** —
A14 10 · R16 10 · H17 12 · G18 10 · S19 10 · C20 12 · `spec/07` **51 tugas** ·
`arch/10` **13 tahap**.

---

## §3 Dua puluh enam pemeriksaan

### B · Batas keras — [`04`](04-DEPENDENCY-GRAPH.md) §2

| # | Memeriksa | Caranya | Gagal berarti |
|---|---|---|---|
| **B-1** | kode agent tidak mengimpor `security/` | `import-linter` kontrak `forbidden`: `agents.*` ✗→ `security.*` | Control Plane dan Data Plane menyatu |
| **B-2** | tidak ada jalur keluar selain Action Gateway | `forbidden`: modul mana pun ✗→ klien HTTP/SDK eksternal, kecuali `platform.gateway` | seluruh rantai gerbang menjadi opsional |
| **B-3** | simulasi tidak menulis ke penyimpanan nyata | `forbidden`: `simulation.*` ✗→ `*.repository`; ditambah uji integrasi yang menjalankan skenario dan memastikan **nol** baris berubah | *“bagaimana kalau”* menjadi *“sudah terjadi”* |
| **B-4** | `Code → Simulation → Safety Test → Hardware` | artefak biner untuk `embodiment/drivers/` **hanya dibangun** dari commit yang punya laporan `Safety Test` hijau untuk commit itu | kode yang belum pernah disimulasikan menggerakkan benda di dekat orang |
| **B-5** | kebijakan lokal hanya memperketat | tiap berkas policy diuji terhadap Konstitusi: himpunan izinnya wajib **⊆** himpunan izin induknya | Konstitusi berhenti menjadi lapisan tertinggi |
| **B-6** | tepat satu pohon `security/` | hitung direktori bernama `security`/`safety`/`privacy`/`consent`/`audit`/`permissions`/`policies`/`trust`/`compliance`/`ethics` di tingkat atas → **wajib 1** | B-1 tidak bisa dinyatakan |

> ⚠️ **B-4 sengaja menempel pada ARTEFAK, bukan pada PR.** Gerbang yang menempel
> pada PR bisa dilewati dengan menggabungkan lewat jalan lain; gerbang yang
> menempel pada artefak berarti **binernya tidak pernah ada**.

### M · Modul & nama — [`03`](03-MONOREPO-FINAL.md)

| # | Memeriksa | Caranya |
|---|---|---|
| **M-1** | tidak ada impor melingkar | `import-linter` kontrak `independence` |
| **M-2** | impor hanya lewat pintu keluar modul | `forbidden` ke `*.internal.*`; hanya `__init__.py` yang publik |
| **M-3** | modul domain tidak saling mengimpor | `independence` atas `services.*` — komunikasi lewat event |
| **M-4** | tidak ada nama direktori “telanjang” dari kamus tabrakan | daftar dari [`02`](02-BOUNDED-CONTEXT.md) §4; sebuah direktori bernama `simulation`/`state`/`planning`/`registry`/`graph` **di luar pemilik sahnya** = gagal |

### P · Penyimpanan & migrasi — [`06`](06-DATA-ARCHITECTURE.md) · [`09`](09-DEPLOYMENT-TOPOLOGY.md)

| # | Memeriksa | Gagal berarti |
|---|---|---|
| **P-1** | tiap `CREATE TABLE` punya `@retention`, `@who-can-set`, `@on-delete` | tabel tanpa retensi — sudah tercatat **empat kali** |
| **P-2** | tiap tabel punya kolom `data_subject` | tidak bisa dibedakan baris pengguna dari baris orang yang tak punya akun |
| **P-3** | tidak ada `user_id` yang nullable | RLS `user_id = current_user` **meloloskan `NULL`** pada sebagian konfigurasi |
| **P-4** | tabel `sensitivity >= 3` diakses hanya lewat `security/vault/` | keuangan mendapat perlindungan berbeda dari kesehatan **karena ada yang lupa** |
| **P-5** | tiap modul menyatakan `deploy: edge \| cloud \| both` | pengaman berakhir di cloud dan mati pada pemicunya sendiri |
| **P-6** | data kelas **K3** tidak punya jalur keluar perangkat | CSI mentah dan point cloud meninggalkan rumah |

### E · Event — [`07`](07-EVENT-CONTRACTS.md)

| # | Memeriksa | Caranya |
|---|---|---|
| **E-1** | segmen pertama `event_type` ada di registry domain | registry [`07`](07-EVENT-CONTRACTS.md) §2, dibaca dari dokumennya; **jalan** atas `spec/03` & `arch/07` |
| **E-2** | format dua segmen, huruf kecil, kata kerja lampau | regex; **jalan** |
| **E-3** | tidak ada `source='sensor'` di `events` | `CHECK` kolom `source` di DDL (`spec/01` + migrasi) — **jalan**; uji admisi saat terbit — tugas 3.1 |
| **E-4** | tiap kata kerja pengubah keadaan punya kembaran kegagalan/pemulihan | daftar pasangan wajib [`07`](07-EVENT-CONTRACTS.md) §6; **jalan sekarang** — namanya dicari di [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) SAJA, sebab mencarinya di `07` berarti pemeriksa membaca daftar tuntutannya sendiri |
| **E-5** 🆕 | tiap nama event di naskah punya baris di tabel padanan [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) | panen PascalCase seluruh `docs/`, disaring kata kerja penutup yang tabel itu sendiri pakai; **jalan sekarang** |

> 🔑 **E-5 ada karena pertanyaan yang ditujukan kepada E-1 dan E-2 sendiri:
> *apa yang keduanya TIDAK PERNAH lihat?*** Jawabannya tajam: keduanya hanya
> membaca nama yang **sudah** masuk tabel padanan. Sebuah nama yang tidak pernah
> masuk **tidak punya `event_type` sama sekali**, jadi tidak ada yang bisa
> ditolak — ia lolos karena tak terlihat, bukan karena benar.
>
> 🔴 **Dijalankan pertama kali, ia langsung menemukan satu: `MeetingCreated`**
> ([`../docs/167`](../docs/167-AUDIO-VOICE-VIDEO-TEMPORAL.md) L29) — nama event
> tulisan pemilik, di ujung alur `Speech → … → Event`, yang **tidak pernah
> sampai ke tabel padanan**. Ia terlewat sebab
> [`../docs/SENSUS-EVENT.md`](../docs/SENSUS-EVENT.md) memanen **bagian yang
> JUDULNYA menyebut “Event”**, dan nama ini berdiri di sebuah **contoh**.
> ⇒ sensusnya benar untuk populasi yang dipanennya; **populasinya yang kurang
> satu naskah.**

### A · Agent & tool — [`08`](08-AGENT-CONTRACTS.md)

| # | Memeriksa | Gagal berarti |
|---|---|---|
| **A-1** | satu angka tidak dipakai untuk `R` **dan** `L` | `risk: R2` sebagai properti agent membalik **H-21** |
| **A-2** | tiap tool di `tools:` punya `risk_level <= max_risk` | manifest bisa berbohong tentang apa yang bisa dilakukannya |
| **A-3** | agent yang memanggil agent lain punya entri `kind: agent` di tool registry | sisi pohon eksekusi tidak melewati gerbang — **K-14** |

### G · Governance

| # | Memeriksa |
|---|---|
| **G-1** | tiap pasal Konstitusi §20.16 punya **≥ 1** penegak di tabel [`08`](08-AGENT-CONTRACTS.md) §4. Pasal tanpa penegak = gagal; pasal yang penegaknya **sebagian** wajib menyebutkan bagian yang tidak bisa diperiksa mesin |

### R · Roadmap

| # | Memeriksa |
|---|---|
| **R-1** | untuk tiap roadmap, tiap pasangan (gerbang **G**, hal yang dijaga **T**): `index(G) < index(T)`. Daftar pasangannya dari [`10`](10-URUTAN-IMPLEMENTASI.md) §2 |

---

## §4 🔴 Apa yang R-1 temukan — dan sekarang ia DIHITUNG, bukan dibaca

> ✅ **Diperbarui 11 September 2026.** Tabel ini semula dihitung tangan.
> [`../tools/periksa_dokumen.py`](../tools/periksa_dokumen.py) `R-1`
> menghitungnya sendiri sekarang, dari daftar pasangan di
> [`10`](10-URUTAN-IMPLEMENTASI.md) §2.1 dan dari nomor butir yang dipanen
> langsung dari `docs/`. **Vonis tangan terbukti benar untuk kedelapan
> roadmap** — dan satu angkanya bertambah tajam: yang gagal bukan enam
> *roadmap* melainkan **tujuh pasangan gerbang**, sebab Phase 16 melanggar
> **dua** aturan sekaligus, bukan satu.

| Roadmap | Pasangan | Hasil |
|---|---|---|
| `A14.x` Phase 14 | federasi (A14.1) ← Security Mesh (A14.7) | 🛑 **GAGAL** — [#99](../../issues/99) |
| `R16.x` Phase 16 | humanoid · drone · manipulasi ← `R16.10` Safety Kernel | 🛑 **GAGAL** — [#111](../../issues/111) |
| `R16.x` Phase 16 | manipulasi · humanoid · drone · armada ← `R16.9` Simulation | 🛑 **GAGAL** — §16.26 `Code → Simulation → Safety Test → Hardware` |
| `H17.x` Phase 17 | seluruh MVP ← `H17.12` Health Safety (**di luar MVP**) | 🛑 **GAGAL** — [#116](../../issues/116) |
| Phase 18 | §18.30 Query Engine ← §18.22 Safety Kernel (**tanpa milestone**) | 🛑 **GAGAL** — [#121](../../issues/121) |
| `S19.x` Phase 19 | Digital Laboratory ← `S19.10` Ethics & Safety | 🛑 **GAGAL** — [#131](../../issues/131) |
| `C20.x` Phase 20 | `C20.6` Coordination ← `C20.7` Governance | 🛑 **GAGAL** — [#144](../../issues/144) |
| **`../spec/07` Sprint 0–6** | kode domain ← 0.8 lint; agent (4.6–4.7) ← 4.5 risk gate | ✅ **LULUS** |
| **`arch/10` T0–T12** | tiap tahap ← **T2** PROTECT | ✅ **LULUS** |

> 🔑 **Enam roadmap gagal (tujuh pasangan), dua lulus — dan yang lulus
> keduanya ditulis sebagai pekerjaan engineering, bukan sebagai peta fase.** Itu perbedaan yang lebih
> berguna daripada menyalahkan naskah mana pun: roadmap yang ditulis untuk
> **dikerjakan** menaruh gerbangnya lebih dulu; roadmap yang ditulis untuk
> **menggambarkan** menaruh yang paling menarik lebih dulu.

⚠️ Keenam kegagalan itu **sudah punya issue** dan **tetap milik pemilik** —
mengurutkan ulang roadmap fase adalah keputusan cakupan. Yang berubah karena
R-1: ia berhenti menjadi enam catatan terpisah di enam berkas, dan menjadi
**satu pemeriksaan yang berbunyi setiap kali roadmap baru ditulis**.

---

## §5 Yang penegakan ini **tidak** bisa lakukan

Ditulis supaya tidak ada yang mengira daftar §3 lebih kuat daripada yang
sebenarnya.

| Tidak terjaga | Kenapa | Tempatnya |
|---|---|---|
| apakah sebuah penjelasan **menyesatkan** (Pasal 8) | penilaian, bukan pola | `evaluation/red-team/` |
| apakah `social cohesion 0.68` **berarti** apa pun | angka tanpa rumus tetap lolos tipe | [#145](../../issues/145) — pemilik |
| apakah **batas gaya** robot cukup rendah | butuh angka yang belum ada | [#112](../../issues/112) — pemilik |
| apakah pengulangan **memperkuat kesalahan sistematis** | kamera salah sudut salah **setiap hari**, lalu naik pangkat jadi *pola* | [#77](../../issues/77) **B-25** — butuh rancangan deteksi bias |
| apakah `bystander` **boleh ada** | hukum | [#40](../../issues/40) · [#76](../../issues/76) — pemilik |

> 💡 **Pola yang sama pada kelimanya:** yang tidak bisa diperiksa mesin adalah
> yang menuntut **penilaian tentang akibat pada orang lain** — dan itu tepat
> kelas keputusan yang aturan pemilah serahkan kepada pemiliknya. Kebetulan itu
> bukan kebetulan.

---

## §6 Pemeriksaan yang harus lulus

| | Hasil |
|---|---|
| Jumlah pemeriksaan | **26** |
| Batas keras tanpa penegak **yang dinyatakan** | **NIHIL** — 6 dari 6 punya baris di blok `penegak` di bawah: 2 jalan, 4 menunggu pemicu yang disebut namanya |
| Aturan 🔧 di `arch/` tanpa baris di §3 | **NIHIL** |
| Pemeriksaan yang **benar-benar dijalankan** | **19 dari 26** — di **branch Sprint 0**; di `master` tetap 12 sampai branch itu digabung, sebab ketujuh tambahannya (B-2 · M-1 · M-2 · M-3 · M-4 · E-3 · A-1) lahir di sana |
| Pemeriksaan yang **terbukti sanggup GAGAL** | **19 dari 19** — [`../tools/uji_mutasi.py`](../tools/README.md) (25 mutasi) · `uji_mutasi_kode.py` (42 mutasi) |
| Pemeriksaan yang menunggu | **7** — B-1 · B-3 · B-4 · B-5 · P-4 · P-5 · P-6; tiap baris menyebut pemicunya |
| Perkakas yang dibutuhkan | **1** — `import-linter` menangani B-2 · M-1 · M-2 · M-3 hari ini, dan B-1 · B-3 begitu modulnya ada |
| Roadmap yang lulus R-1 | **2 dari 8** — dan keduanya ditulis untuk dikerjakan |

### Blok `penegak` — dibaca mesin, bukan dibaca orang

Satu baris per pemeriksaan §3. `tests/unit/test_penegak.py` menuntut:
himpunan kodenya **sama persis** dengan §3; tiap `import-linter:<id>` ada di
`pyproject.toml`; tiap `periksa_dokumen:<kode>` ada di
`tools/periksa_dokumen.py` **dan** dijalankan `tools/ci_lokal.py`; tiap baris
`MENUNGGU` menyebut pemicunya; dan **tidak ada kontrak `import-linter` yang
tidak disebut di sini**.

```penegak
# kode  status      penegak                                          pemicu / catatan
B-1     MENUNGGU    —                                                tugas 4.5 — V0 belum punya `security`; risk gate menentukan letaknya
B-2     JALAN       import-linter:b2-jalur-keluar
B-3     MENUNGGU    —                                                T5 — V0 tidak punya modul `simulation`
B-4     MENUNGGU    —                                                T10 — menempel pada artefak `embodiment/drivers/`
B-5     MENUNGGU    —                                                T2 — belum ada berkas kebijakan untuk diuji terhadap Konstitusi
B-6     JALAN       periksa_dokumen:B-6
M-1     JALAN       import-linter:m1-m3-lapisan import-linter:m1-siklus-dalam
M-2     JALAN       import-linter:m2-identity import-linter:m2-profile import-linter:m2-goals import-linter:m2-habits import-linter:m2-checkins import-linter:m2-journal import-linter:m2-activities import-linter:m2-events import-linter:m2-memory import-linter:m2-intelligence import-linter:m2-agents import-linter:m2-platform
M-3     JALAN       import-linter:m1-m3-lapisan
M-4     JALAN       periksa_dokumen:M-4
P-1     JALAN       periksa_dokumen:P-1
P-2     JALAN       periksa_dokumen:P-2
P-3     JALAN       periksa_dokumen:P-3
P-4     MENUNGGU    —                                                T2 — `security/vault/` & anotasi `sensitivity` belum ada
P-5     MENUNGGU    —                                                D5 — modul belum punya manifest `deploy`
P-6     MENUNGGU    —                                                T9 — V0 tidak punya data K3
E-1     JALAN       periksa_dokumen:E-1
E-2     JALAN       periksa_dokumen:E-2
E-3     JALAN       periksa_dokumen:E-3                              separuh DDL; uji admisi saat terbit — tugas 3.1
E-4     JALAN       periksa_dokumen:E-4
E-5     JALAN       periksa_dokumen:E-5
A-1     JALAN       periksa_dokumen:A-1                              skema manifest + DDL; manifest sungguhan — tugas 4.2
A-2     JALAN       periksa_dokumen:A-2                              manifest sungguhan — tugas 4.2
A-3     JALAN       periksa_dokumen:A-3                              registry sungguhan — tugas 4.3
G-1     JALAN       periksa_dokumen:G-1
R-1     JALAN       periksa_dokumen:R-1                              merah — keputusan cakupan pemilik; dilaporkan, tidak menggagalkan
```

> 🛑 **Tabel di atas sengaja tidak punya baris *“bisa jalan”* — hanya
> *“dijalankan”* dan *“terbukti sanggup gagal”*, dua baris terpisah.** Sampai
> 10 September 2026 berkas ini menulis *“4 pemeriksaan bisa jalan tanpa kode”* —
> dan **nol** di antaranya pernah dijalankan. Itu bentuk yang sama dengan seluruh §1: aturan
> yang benar, ditulis serius, tanpa sesuatu yang berkata *tidak*. Sebuah berkas
> penegakan adalah tempat paling tidak masuk akal untuk mengulanginya, dan ia
> mengulanginya selama satu hari.
