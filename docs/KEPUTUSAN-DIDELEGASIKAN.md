# Keputusan yang didelegasikan

> ⚠️ **Bukan kata pemilik.** Berkas ini memuat keputusan yang **saya ambil
> sendiri** atas permintaan pemilik (*“beri keputusan sendiri sesuai aturan”*,
> 9 September 2026), lengkap dengan **bacaan yang ditolak** dan **cara
> membalikkannya**.
>
> 🔧 Setiap butir bertanda **usulan** — pemilik boleh membatalkannya, dan tiap
> butir menyebutkan biaya pembatalannya.

---

## Batas yang saya pegang

Yang **saya putuskan**: pertanyaan **engineering** yang punya bukti terukur,
akibatnya bisa dibatalkan, dan salah-benarnya bisa diperiksa dari repo.

Yang **tetap milik pemilik**, dan tidak saya sentuh:

| Jenis | Contoh | Kenapa |
|---|---|---|
| waktu & orang | [#3](../../issues/3) siapa mengerjakan V0 | bukan soal teknis |
| uang & hukum | [#20](../../issues/20) cek merek · seluruh butir **C** | menuntut pembelian, nasihat hukum, atau menanggung risiko orang lain |
| cakupan produk | [#4](../../issues/4) Mental Wellness dibuang atau ditunda | pemilik yang menanggung akibatnya |
| urutan kerja pemilik | ~~[#139](../../issues/139)~~ — ✅ diperintahkan 10 Sep 2026 | ~~soal waktu pemilik sendiri~~ |

⇒ **Nol butir C saya putuskan.** Semuanya menyangkut orang yang tidak ikut
memilih.

---

## K-1 · Kapabilitas yang menyentuh pihak ketiga = **minimum R3**

**Menutup:** [#152](../../issues/152) (**B-39**) · menyentuh [#81](../../issues/81)

| | |
|---|---|
| **Keputusan** | Setiap kapabilitas yang akibatnya sampai kepada **orang selain pemegang akun** berada di **`risk_level` minimum 3**, sampai ada definisi tertulis yang bisa diuji untuk *“low-risk”*. Ditegakkan sebagai **aturan validasi 7** di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) — ditolak validator, bukan oleh kebijakan tertulis. |
| **Bukti** | Tiga dari empat tangga risiko menaruh *“kirim pesan”* di **3/R3** ([`SENSUS-TANGGA.md`](SENSUS-TANGGA.md)); **H-15** ([#5](../../issues/5)) menetapkan konfirmasi wajib mulai R3; kata *“low-risk”* **tidak pernah didefinisikan** di seluruh `docs/`; tetangganya di baris yang sama (`purchase low-value item`) **diselamatkan** `amount_limit: 0`, pesan tidak. |
| **Bacaan yang DITOLAK** | *“Percayai kata sifatnya — agent bisa menilai sendiri mana pesan berisiko rendah.”* **Ditolak** karena risikonya ditanggung **penerima**, yang tidak pernah menyetujui apa pun dan tidak tahu apakah yang menulis manusia atau mesin (**C-19**). Penilai dan penanggung risiko bukan pihak yang sama. |
| **Yang TIDAK berubah** | Teks naskah §11.15 tetap apa adanya — berkas naskah merekam kata pemilik. Yang berubah hanya **penegakannya** di `spec/`. |
| **Cara membalikkan** | Tulis definisi *“low-risk message”* yang bisa diuji mesin (mis. penerima ada di kontak pengguna **dan** isi pesan tidak memuat data Level 3–4 **dan** tidak mengikat apa pun), lalu hapus aturan 7. Satu baris di `spec/05`. |

> ⚠️ Untuk **V0 ini tidak mengubah apa pun** — `spec/05` menyatakan V0 tidak
> punya satu pun tool level 3 atau 4. Aturan ini berlaku begitu Phase 11 mulai
> dikodekan.

---

## K-2 · `scenario/` dan `counterfactual/` milik `simulation/`, bukan `world-model/`

**Menutup:** [#147](../../issues/147) (**G-20**)

| | |
|---|---|
| **Keputusan** | **`world-model/` menyimpan; `simulation/` menjalankan.** `world-model/` memegang `state/` dan `transition/` dan bersifat **durable**. `scenario/` dan `counterfactual/` hidup **hanya** di bawah `simulation/`, dan `simulation/` **tidak menyimpan apa pun yang durable** — keluarannya selalu bisa dibangun ulang dari `world-model/` + parameter. |
| **Bukti** | §9.38 memberi keduanya sebagai modul sejajar dan **keduanya** memiliki `scenario/` + `counterfactual/`. Selama dua-duanya ada, dua tim menulis dua mesin dan jawabannya berbeda tergantung pintu masuk. |
| **Bacaan yang DITOLAK** | *“Taruh keduanya di `world-model/`, sebab skenario adalah keadaan yang mungkin.”* **Ditolak** karena itu menjadikan `world-model/` sekaligus penyimpan **dan** mesin — persis pencampuran yang membuat **B-24** sulit dijawab (*Counterfactual Engine tanpa sumber model transisi*). Dengan pembagian ini, sumber transisi punya alamat: `world-model/transition/`. |
| **Juga menyelesaikan** | `preference/` ganda di `memory-engine/` dan `prediction/` → **`memory-engine/preference/` menyimpan** preferensi yang teramati; `prediction/` **membacanya**, tidak menyimpan salinan. |
| **Cara membalikkan** | Satu kalimat di §9.38 yang menyatakan pembagian lain. Belum ada kode, jadi biayanya nol. |

---

## K-3 · 128 nama event dipadankan — **naskah tidak diubah**

**Menutup:** [#149](../../issues/149) (**E-153**) · melanjutkan [#38](../../issues/38)

| | |
|---|---|
| **Keputusan** | Naskah **tidak** ditulis ulang. Tabel padanan `PascalCase → domain.verb` diterbitkan di [`../spec/03`](../spec/03-EVENT-CONTRACTS.md), dan **`spec/03` menjadi satu-satunya sumber nama yang sampai ke kode**. Padanannya mekanis: kata pertama → domain, sisanya → verb snake_case. |
| **Bukti** | [#38](../../issues/38) sudah memilih dua segmen huruf kecil; **128** nama pasca-keputusan memakai PascalCase ([`SENSUS-EVENT.md`](SENSUS-EVENT.md) — angkanya 127 saat K-3 diputuskan; `MeetingCreated` ditambahkan 11 Sep 2026 lewat **E-5**). Belum ada kode, jadi belum ada nama yang terkunci. |
| **Bacaan yang DITOLAK** | *“Perbaiki saja nama-namanya langsung di naskah.”* **Ditolak** — aturan 1 repo ini menyatakan berkas naskah merekam kata pemilik apa adanya. Menyunting 128 nama di sana akan menghapus bukti bahwa keputusannya pernah dilanggar, dan itu justru satu-satunya alasan pola ini bisa ditemukan. |
| **Tiga tabrakan KOSAKATA** | Diselesaikan ke arah `spec/03`, sebab nama itu **sudah ada di DDL**: `SleepEnded` → **`sleep.completed`** · `MeetingEnded` → **`meeting.completed`** · `MoodChanged` → **`mood.logged`**. Ketiganya bukan beda bentuk melainkan beda kata kerja. |
| **Cara membalikkan** | Ubah tabel padanan di `spec/03`. Naskah tidak perlu disentuh sama sekali. |

---

## K-4 · Tabel berdefinisi ganda — **yang ada di `spec/` menang; sisanya yang paling awal**

**Menutup:** [#151](../../issues/151) (**E-156**)

| | |
|---|---|
| **Keputusan** | Untuk **19 nama tabel** yang didefinisikan lebih dari sekali: (1) kalau namanya sudah ada di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md), **definisi `spec/01` yang berlaku**; (2) kalau tidak, **definisi fase paling awal** yang kanonik. Fase berikutnya boleh **menambah kolom**, tidak boleh **mendefinisikan ulang**. |
| **Bukti** | `agent_capabilities` dan `agent_trust_scores` masing-masing didefinisikan **empat kali** (Phase 8·11·14·18). Tanpa aturan, empat bentuk kolom untuk tabel yang menentukan **apa yang boleh dilakukan sebuah agent**. |
| **Bacaan yang DITOLAK** | *“Yang terbaru menang — fase belakangan tahu lebih banyak.”* **Ditolak** karena fase belakangan menulis tanpa membaca apa yang sudah disimpan fase terdahulu; menang-terbaru menghapus kolom yang mungkin sudah dipakai. Menambah kolom aman; mengganti bentuk tidak. |
| **Cara membalikkan** | Sebut fase pemenangnya secara eksplisit per tabel. |

---

## K-5 · Kriteria **agent** lawan **service** — tiga uji yang bisa diperiksa

**Menutup:** [#89](../../issues/89) (**G-13**) · menjawab sebagian [#150](../../issues/150)

| | |
|---|---|
| **Keputusan** | Sebuah komponen adalah **agent** hanya bila **ketiganya** benar: **(a)** ia merencanakan lebih dari satu langkah; **(b)** ia **memilih** di antara beberapa tool saat berjalan, bukan memanggil urutan tetap; **(c)** ia bisa **dihentikan di tengah** dan meninggalkan jejak yang bisa dilanjutkan (`agent_runs`). Kalau salah satu tidak terpenuhi, ia **service deterministik** dan tidak masuk registry agent. |
| **Bukti** | §12.29 sendiri memperingatkan *“jangan membuat semuanya sebagai autonomous agent; sebagian lebih baik sebagai deterministic/model services”* — satu-satunya peringatan semacam itu dalam 24 naskah. Dan **44 dari 59 nama agent hanya pernah disebut sekali** ([`SENSUS-AGENT.md`](SENSUS-AGENT.md)). |
| **Kenapa ketiganya, bukan satu** | Uji (b) sendirian meloloskan pipeline bercabang; uji (c) sendirian meloloskan job antrean biasa. Yang membuat sesuatu **agent** adalah ketiganya bersamaan — dan ketiganya juga persis yang membuat **risk gate** bermakna: sesuatu yang tidak memilih tool tidak perlu gerbang tool. |
| **Bacaan yang DITOLAK** | *“Apa pun yang memakai model bahasa adalah agent.”* **Ditolak** karena itu membuat registry tak terbatas (§12.29 sudah menuju 59 nama) dan menjadikan `risk_level` per-agent tak bermakna: peringkas teks dan pengirim pesan akan duduk di daftar yang sama. |
| **Cara membalikkan** | Ubah ketiga uji. Belum ada satu agent pun yang terdaftar di kode. |

---

## K-6 · Tujuh kata kerja kapabilitas untuk Phase 2–8 🔧

**Menutup sebagian:** [#142](../../issues/142) (**E-148**) · [#133](../../issues/133)

Peta §20.36 memberi kata kerja untuk Phase 9–20. Nama Phase 2–8 sudah ada
([`PETA-FASE.md`](PETA-FASE.md)); yang belum ada **kata kerjanya**. Diturunkan
dari nama masing-masing fase:

| Fase | Nama yang sudah ada | Kata kerja 🔧 |
|---|---|---|
| **1** | ❌ **tidak ada nama, di mana pun** | — **satu-satunya celah nyata** |
| 2 | Enterprise Blueprint | **STRUCTURE** |
| 3 | AI-Native Human Ecosystem | **CONNECT** |
| 4 | Enterprise Operating System | **STANDARDISE** |
| 5 | HumanVerse AI Research Lab | **RESEARCH** |
| 6 | HumanVerse Developer Platform | **EXTEND** |
| 7 | Data & AI Infrastructure | **STORE** |
| 8 | AI Safety, Security & Privacy | **PROTECT** |

⚠️ **Tidak bertabrakan dengan Phase 9–20**: `OPERATE` sudah dipakai Phase 13,
jadi Phase 4 memakai `STANDARDISE`, bukan `OPERATE`; `REMEMBER` dihindari sebab
memori masuk `THINK` (Phase 9).

| | |
|---|---|
| **Bacaan yang DITOLAK** | *“Beri Phase 1 nama juga supaya petanya genap.”* **Ditolak** — tidak ada satu kalimat pun di 24 naskah yang menamai Phase 1. Mengarang namanya akan menutup celah dengan tebakan, dan celah yang jujur lebih berguna daripada peta yang genap. |
| **Cara membalikkan** | Ganti kata kerjanya. Tidak ada yang bergantung padanya. |

---

## K-7 · §15.15 mendapat simpul `Permission`

**Menutup sebagian:** [#153](../../issues/153) (**E-157**)

| | |
|---|---|
| **Keputusan** | Rantai §15.15 menjadi `Hand Tracking → Gesture Recognition → Intent → **Permission** → Action` — memakai simpul yang **sudah dipakai §15.22 di naskah yang sama**. Tidak ada mekanisme baru yang diperkenalkan. |
| **Bukti** | §15.22 (Spatial Safety) di naskah yang sama **punya** `Permission`; §15.15 tidak. Dua rantai, satu naskah, satu dijaga satu tidak — dan yang tidak dijaga justru yang dipicu **gerakan tubuh**, masukan yang paling mudah keliru terbaca (*Wave → Dismiss*). |
| **Bacaan yang DITOLAK** | *“Gestur itu masukan langsung pengguna, jadi izinnya sudah tersirat.”* **Ditolak** karena gestur **tidak punya niat yang bisa dibatalkan sebelum terjadi** — pengguna tidak bisa menarik lambaian tangan. Pengetikan bisa dihapus sebelum dikirim; gerakan tidak. |
| **Yang TIDAK saya putuskan** | **§16.5 dan §16.7** (humanoid) sengaja **tidak** saya putuskan sendiri: keduanya menyangkut benda yang bisa melukai orang, dan gerbang yang tepat untuk itu menuntut penilaian yang bukan milik saya. Keduanya digabungkan ke [#111](../../issues/111). |
| **Cara membalikkan** | Hapus simpulnya. |

---

## K-8 · Awalan rute API `/v1` — **sudah dijalankan**

**Melanjutkan:** [#38](../../issues/38)

Bukan keputusan baru: menjalankan janji yang **sudah tercatat** di komentar
penutup [#38](../../issues/38) dan tidak pernah dijalankan.
[`../spec/04`](../spec/04-API-CONTRACTS.md) kini berawalan `/v1`, sejalan
standar penamaan pemilik sendiri (naskah 7 Layer 22) dan **111 rute naskah
lawan nol**. Endpoint di dalamnya ditulis tanpa awalan, jadi perubahannya satu
baris.

---

## K-9 · Aturan komposisi pohon repositori — **satu monorepo, dan uji naik-turun**

**Menutup:** [#55](../../issues/55) (**E-66**) · menyelesaikan deret H-10 yang
tergerus sepuluh kali ([#109](../../issues/109) · [#120](../../issues/120) ·
[#129](../../issues/129) · [#138](../../issues/138) · [#143](../../issues/143) ·
[#84](../../issues/84) · [#51](../../issues/51))

[#55](../../issues/55) menanyakan satu hal yang memblokir **Sprint 0 tugas
0.1**: pohon fase baru itu **folder di dalam monorepo** atau **repo terpisah**?

### Keputusan 1 — satu monorepo, nol repo terpisah

Tiap pohon fase menjadi **folder tingkat-atas** di `humanverse-x/`.

| | |
|---|---|
| **Bukti** | Sensus menemukan **38 pohon** di 24 naskah ([`SENSUS-MODUL.md`](SENSUS-MODUL.md)). Repo terpisah berarti **38 daur rilis** dan pembuatan kontrak antar-repo — masalah baru yang lebih besar daripada yang dipecahkannya. |
| **Bacaan yang DITOLAK** | *“Pisahkan yang jelas berbeda — `robotics/` tidak ada urusan dengan `health-bio/`.”* **Ditolak** karena janji *Backward-compatible* (naskah 10) berlaku **ke dalam**, bukan hanya kepada developer luar; begitu ada dua repo, tiap perubahan kontrak menuntut versi, jadwal, dan matriks kompatibilitas — sebelum satu baris kode pun ditulis. |
| **Cara membalikkan** | Pisahkan satu folder menjadi repo sendiri. Selama aturan 2 dipatuhi, batasnya sudah bersih dan pemisahan itu murah. |

### Keputusan 2 — **uji naik-turun**, dan ia punya tiga hasil, bukan dua

Ini aturan yang membuat keputusan 1 bisa ditegakkan, dan yang selama ini tidak
ada (*“empat pohon repo tanpa aturan komposisi”*):

| Kalau… | Maka |
|---|---|
| dua fase memakai nama itu untuk **hal yang SAMA** | **naik** ke tingkat atas, dipakai bersama — **tidak disalin** |
| hanya satu fase membutuhkannya | **tinggal** di dalam fase |
| dua fase memakai nama yang sama untuk **hal yang BERBEDA** | **salah satunya diganti namanya** — tidak digabung, tidak dibiarkan |

⭐ **Hasil ketiga itu yang menyelamatkan aturan ini dari menjadi “gabungkan
semuanya”.** Contohnya `simulation/`, nama yang paling banyak berulang
(**15 pohon**): `robotics/simulation/` adalah simulasi **fisika**,
`intelligence/simulation/` simulasi **perilaku**, `health-bio/simulation/`
simulasi **fisiologi**. Tiga mesin berbeda dengan satu kata. Menggabungkannya
akan menghasilkan modul yang tak seorang pun bisa memiliki.
⇒ **Diganti nama**, bukan digabung.

### Keputusan 3 — keluarga keamanan naik **seluruhnya**, menjadi **satu** pohon

Dua belas nama tersebar di **19 pohon**: `security` (6) · `safety` (6) ·
`privacy` (6) · `audit` (5) · `permissions` (5) · `consent` (3) ·
`policies` (3) · `trust` (3) · `governance` (3) · `policy` · `compliance` ·
`ethics`.

🛑 **Selama itu benar, aturan impor §8.42 — *“kode agent tidak boleh mengimpor
`security/`”* — tidak bisa dinyatakan**, sebab tidak ada satu `security/` untuk
dirujuk. Itu bukan soal kerapian: aturan itu satu-satunya yang memisahkan
Control Plane dari kode agent.

⇒ Satu `security/` tingkat-atas menyerap `safety` · `privacy` · `consent` ·
`audit` · `permissions` · `policies` · `trust` · `compliance` · `ethics`
sebagai submodul.

**Kecuali `governance/`** — ia **naik** tetapi **berdiri sendiri**, bukan di
dalam `security/`. Alasannya bukan selera: *security menjawab **apa yang
boleh**, governance menjawab **siapa yang memutuskan***. Dan catatan audit sudah
membuktikan **tiga kali** bahwa `governance/` yang hidup di dalam pohon fase
**tidak diwarisi** fase berikutnya ([#138](../../issues/138)).

### Yang langsung terselesaikan

| Nama | Sebelum | Sesudah |
|---|---|---|
| `sdk/` | **14 pohon** | **satu**, submodul per domain (`sdk/spatial/`, `sdk/robotics/`) |
| `agents/` · `memory/` · `runtime/` · `evaluation/` | 10 · 8 · 7 · 7 | **satu** masing-masing |
| keluarga keamanan | **19 pohon** | **satu** `security/` + `governance/` |
| `simulation/` | 15 pohon | **diganti nama per fase** — bukan digabung |
| `robotics/locomotion/` · `spatial-os/slam/` · `health-bio/biometrics/` | — | **tetap** di dalam fasenya |

⚠️ **Sisa ~40 nama di ≥3 pohon** ([`SENSUS-MODUL.md`](SENSUS-MODUL.md) Tabel B)
diselesaikan **mekanis oleh uji yang sama** ketika pohonnya benar-benar
dibangun. Yang diputuskan di sini **aturannya**, bukan tiap nama satu per satu —
sebab memutuskan 128 nama tanpa kode yang memakainya berarti menebak.

### Yang TIDAK berubah

**Nol untuk V0.** [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) tetap
mengatur modular monolith V0 apa adanya; aturan ini berlaku bagi pohon **lintas
fase**, yang belum satu pun ditulis sebagai kode.

---

## K-10 · Satu amplop event; `SecurityEvent` menjadi domain `security.*`

**Menutup:** [#63](../../issues/63) (**E-69/E-70**)

| | |
|---|---|
| **Keputusan** | Ada **satu** amplop event, yaitu milik [`../spec/03`](../spec/03-EVENT-CONTRACTS.md). Security event memakainya juga, dengan `event_type: security.*` (mis. `security.permission_denied`, `security.injection_detected`). Medan `action` dan `resource` §8.41 turun menjadi isi `payload`, bukan bentuk amplop tersendiri. |
| **Bukti** | §8.26 memasukkan security event ke **bus yang sama** tetapi dengan bentuk lain sama sekali. Dua bentuk di satu bus berarti **setiap consumer harus tahu lebih dulu jenis event mana yang sedang dibacanya** — persis yang dihindari dengan memakai amplop bersama. |
| **Bacaan yang DITOLAK** | *“Security event itu khusus, wajar punya bentuk sendiri.”* 🛑 **Ditolak dengan alasan yang membalik arahnya:** empat medan yang hilang dari `SecurityEvent` — `schema_version`, `idempotency_key`, `user_id`, dan pemisahan `occurred_at`/`recorded_at` — justru **medan yang membuat sebuah event bisa diaudit**. Dan security event adalah jenis yang **paling mungkin diaudit**. Bentuk khusus itu menghapus tepat kemampuan yang paling dibutuhkannya. |
| **Cara membalikkan** | Nyatakan amplop kedua secara eksplisit, lengkap dengan registry dan aturan versinya sendiri — bukan dibiarkan berbeda diam-diam. |

---

## K-11 · Setiap tangga bernomor membawa **awalan yang menyebut sumbunya**

**Menutup:** [#54](../../issues/54) (**E-59**) · [#56](../../issues/56) (**E-63/E-64**)

Tiga tabrakan penomoran punya satu bentuk yang sama: **satu nomor, banyak arti.**

| Tabrakan | Sekarang | Keputusan |
|---|---|---|
| `Layer 6·11·14·20·22·25` berarti dua hal (naskah 3 lawan naskah 10) | nomor global | **awalan per fase**: `P2-L6` · `P4-L22` · `DP-L6` |
| `V1–V5` berarti **tiga** hal (lingkup produk · kematangan arsitektur · kematangan data) | satu tangga `V` | `V0–V6` **tetap lingkup produk** (H-13, sudah ditutup); arsitektur → **`ARCH1–ARCH4`**; infrastruktur data → **`INFRA1–INFRA5`** |
| `D1–D8` dipakai dua kali (naskah 10 & 11) | tanpa awalan | **`D6.1–D6.8`** dan **`D7.1–D7.8`** — awalan = nomor fasenya |

| | |
|---|---|
| **Bukti** | Naskah 7 Layer 41 menyatakan tujuan dokumentasinya *“dibaca AI coding agent tanpa kehilangan konteks”*. Nomor yang berarti dua hal **menghapus tepat kemampuan itu** — pembaca tanpa konteks tidak punya cara memilih. |
| **Bacaan yang DITOLAK** | *“Pakai nomor global yang terus naik saja.”* **Ditolak** — dengan 20 fase nomornya sampai ratusan, dan angka besar itu **tidak memberi tahu apa pun tentang fasenya**. Awalan membawa informasi; nomor urut global tidak. |
| **Cara membalikkan** | Ganti awalannya. Tidak ada kode yang bergantung pada nomor ini. |

---

## K-12 · `risk_level` wajib pada setiap tool, dan larangan scope diperluas

**Menutup sebagian:** [#77](../../issues/77) (bagian **G-11**)

| | |
|---|---|
| **Keputusan** | Dua aturan validasi baru di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md): **(8)** tool tanpa `risk_level` **ditolak** saat registrasi — tidak ada bawaan diam-diam; **(9)** larangan scope untuk `kind: third_party` (aturan 6) diperluas dengan **`spatial`, `location`, `people`, `csi`**. |
| **Bukti** | **G-11** mencatat 13 tool persepsi §10.26 tanpa satu pun `risk_level`, dan §15.24 mengulanginya untuk lima panggilan SDK spasial yang mengembalikan **denah rumah** dan **posisi pengguna**. Skema `spec/05` memang punya medan itu — tetapi **medan yang ada di skema bukan medan yang ditegakkan**; itu pelajaran repo ini sendiri, berkali-kali. |
| **Bacaan yang DITOLAK** | *“Beri bawaan `risk_level: 0` supaya tool lama tetap sah.”* 🛑 **Ditolak** — bawaan nol berarti tool yang lupa diberi tingkat risiko otomatis menjadi **yang paling tidak dijaga**. Kalau harus ada bawaan, ia mesti ke sisi yang lebih aman; lebih baik lagi **tidak ada bawaan sama sekali**, sehingga kelalaian berhenti di validator, bukan di produksi. |
| **Yang TIDAK saya putuskan** | Bagian **B-25** issue itu — *pengulangan memperkuat kesalahan sistematis* (sudut pasang kamera membuat berdiri terbaca duduk, lalu **naik pangkat menjadi pola**). Itu menuntut rancangan deteksi bias yang salahnya **ditanggung pengguna**, dan bukan keputusan penamaan. [#77](../../issues/77) tetap terbuka untuknya. |
| **Cara membalikkan** | Hapus aturan 8 atau 9. |

---

## K-13 · Bahasa backend = **Python + FastAPI**

**Menutup celah yang belum pernah dicatat:** [`../spec/`](../spec/README.md)
berganti bahasa tanpa menyebutnya. Memblokir **Sprint 0 tugas 0.3**.

| | |
|---|---|
| **Keputusan** | Backend ditulis dalam **Python** dengan **FastAPI**. [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) dan [`../spec/07`](../spec/07-BACKLOG-V0.md) **diselaraskan**, bukan dibiarkan berbeda. |
| **Bukti** | `grep -rl "FastAPI" docs/` → **1 berkas** ([`05`](05-ARSITEKTUR.md), naskah 1, disebut di tabel **dan** diagram). `grep -rlo "Node.js\|NestJS\|Express\|Golang" docs/` → **0 berkas**. FastAPI adalah **satu-satunya kerangka backend yang pernah dinamai dalam 24 naskah**. Ditambah **ADR-004** yang sudah mengunci **LangGraph** (Python lebih dulu), dan **enam dari dua puluh fase natively Python** — Phase 10 · 12 · **16 (ROS 2: `rclpy`/`rclcpp`, tak ada klien Node resmi)** · 17 · 19 · sebagian 5 & 9. |
| **Bacaan yang DITOLAK** | *“`spec/` sudah ditulis untuk TypeScript, jadi TypeScript yang menang.”* 🛑 **Ditolak dengan alasan yang membalik arahnya:** `spec/` tidak pernah **memutuskan** bahasa — ia **mengasumsikannya**, diam-diam, di dua berkas (`index.ts`, `npm test`). Asumsi yang tidak pernah dinyatakan tidak bisa mengalahkan keputusan yang dinyatakan dua kali. |
| **Yang TIDAK berubah** | `spec/01`–`05` **bebas bahasa**: 23 tabel, ERD, 22 event, endpoint, manifest — tidak satu pun disentuh oleh keputusan ini. |
| **Biaya** | **Nol baris kode.** Ini kesempatan terakhir biaya itu nol. |
| **Cara membalikkan** | Balik tabel padanan di [`../arch/05`](../arch/05-TECHNOLOGY-STACK.md) §2. Sesudah Sprint 0 selesai, biayanya seluruh Sprint 0. |

⭐ **Satu keuntungan yang tidak disengaja:** `import-linter` menggantikan
`no-restricted-imports` **dan** `madge --circular` sekaligus — sehingga batas
modul (`spec/06` aturan 1–4) dan **enam batas keras**
([`../arch/04`](../arch/04-DEPENDENCY-GRAPH.md) §2) menjadi **satu berkas
kontrak** yang dibaca satu perintah CI.

---

## K-14 · Memanggil agent lain **adalah** pemanggilan tool

**Menutup:** [#97](../../issues/97) (**E-119**) · menutup lubang gerbang yang
ditemukan saat **menguji K-5 terhadap keempat agent V0**

| | |
|---|---|
| **Keputusan** | Agent yang bisa dipanggil agent lain **wajib terdaftar di tool registry** dengan `kind: agent`, dan `risk_level` entri itu = **`max_risk`** agent yang dipanggil. Pemanggilannya melewati rantai gerbang seperti tool lain. Ditambah: properti agent adalah **`max_risk`** (pagu), bukan `risk_level`; aturan validasi 3 `spec/05` ditulis ulang menjadi **setiap tool wajib `risk_level <= max_risk`**. |
| **Bukti** | `spec/05` menutup bagian K-5 dengan *“keempat agent V0 lulus ketiga uji”* — **dinyatakan, tidak diperiksa**. Diperiksa: `orchestrator-agent` punya `tools: —` (nol tool) sementara uji (b) menuntut *“memilih di antara beberapa **tool**”*. Ia memilih **agent**. ⇒ sisi-sisi pohon eksekusi (`parent_run_id`) **tidak pernah melewati risk gate**, tepat di simpul yang melihat seluruh pohon. |
| **Bacaan yang DITOLAK** | *“Longgarkan uji (b) menjadi ‘tool **atau agent**’.”* **Ditolak** — itu memperbaiki definisinya tetapi **membiarkan lubang gerbangnya**: orchestrator akan lulus sebagai agent dan tetap memanggil tanpa gerbang. |
| **Akibat nyata di V0** | `orchestrator-agent` mendapat tiga entri tool `kind: agent`, dan `max_risk`-nya **naik R0 → R2** — sebab ia memanggil `agent.habit` (R2). Angka lama tampak benar hanya selama pemanggilan agent tidak dihitung. |
| **Cara membalikkan** | Longgarkan uji (b), dan terima bahwa sisi pohon eksekusi tidak digerbang. |

> 💡 **Cara menemukannya layak diingat: JALANKAN aturan yang baru dibuat pada
> kasus yang terasa paling sepele.** Dua agent pertama lulus dengan mudah; kalau
> pemeriksaannya berhenti di sana, K-5 akan tampak selesai. Yang ketiga —
> `orchestrator-agent`, yang “jelas-jelas agent” — justru yang gagal, dan
> kegagalannya menunjuk lubang di **gerbangnya**, bukan di definisinya.

---

## K-15 · Domain event diambil dari **registry**, bukan dari kata pertama nama

> Diputuskan 11 September 2026. Mempersempit **K-3**; tidak membukanya kembali.

K-3 memadankan 127 nama `PascalCase` menjadi `domain.verb` dengan aturan
*“kata pertama → domain, sisanya → verb `snake_case`”*. Aturan itu **mekanis dan
benar sebagai transkripsi** — dan tidak pernah dijalankan terhadap registry
domain [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2, yang lahir sehari
sesudahnya.

| | |
|---|---|
| **Keputusan** | Kalau kata pertama sebuah nama **adalah domain terdaftar**, ia menjadi domain dan sisanya menjadi verb. Kalau **bukan**, domainnya diambil dari [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §4 (domain tujuan per fase) dan **seluruh nama** menjadi verb. Verb wajib berakhir kata kerja **lampau**. Satu-satunya domain yang ditambahkan ke registry adalah **`health`**, dan ia bukan domain baru: catatan kaki §4 sudah menyatakannya milik `human-core` sejak awal — tabel §2 yang melewatkannya. |
| **Bukti** | Dijalankan mesin: **66 dari 127 baris** mendarat di domain yang tidak ada di registry, dan **enam nama** berakhir bukan kata kerja lampau. Yang paling menentukan bukan jumlahnya melainkan isinya: `LargeScaleScenarioCreated` → domain **`large`**, `InterestRateChanged` → **`interest`**, `OilPriceChanged` → **`oil`**. ⇒ **kata pertama sebuah nama tidak selalu subjeknya.** |
| **Arahnya ditentukan aturan yang sudah ada, bukan selera** | [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2 sudah menulis: *“Domain baru ditambahkan hanya bersama konteks pemiliknya — dan penambahan itu adalah perubahan arsitektur, bukan penamaan.”* ⇒ **namanya yang pindah, bukan registry yang tumbuh.** Kalau ditempuh sebaliknya, registry membengkak dari 46 menjadi 96 dan berhenti menjadi registry: seluruh alasannya ada supaya `stuff.happened` **tidak** lolos. |
| **Bacaan yang DITOLAK** | *“Tambahkan saja 50 domain itu ke registry — toh naskah memang menyebutnya.”* **Ditolak** dua kali: (a) aturan §2 di atas, (b) `large`, `oil`, `interest`, `heart`, `supply`, `scientific` **bukan konteks apa pun** — memasukkannya berarti menyatakan bahwa ada konteks bernama `large`, dan tidak ada yang bisa memilikinya. |
| **Akibat nyata** | **64 nama diganti**, tiga di antaranya **menyatu** dengan baris lain (`TaskCompleted` → `agent.task_completed` · `MapUpdated` → `spatial.map_updated` · `SupplyChainDisruption` → `world.supply_chain_disrupted`) ⇒ dua nama naskah, satu `event_type`. **Nol perubahan untuk V0: 22 event tetap 22**, sebab ke-22-nya sudah memakai domain terdaftar. |
| **Biayanya nol hari ini** | Aturan §5 melarang mengganti nama event **sesudah diterbitkan**. Repo ini nol baris kode ⇒ nol baris data ⇒ **tidak ada yang diterbitkan**. Sesudah baris pertama masuk tabel `events`, biaya yang sama menjadi migrasi riwayat atau kehilangan perilaku. |
| **Cara membalikkannya** | Kembalikan aturan K-3 apa adanya dan tambahkan 50 domain ke [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §2. Keduanya satu suntingan; yang hilang adalah kemampuan menjawab *“domain ini milik konteks mana”* untuk separuh nama. |

> 💡💡 **Cara menemukannya adalah bentuk yang sudah berbuah empat kali di repo
> ini, dan kali ini paling murah: JALANKAN DUA DOKUMEN YANG TIDAK PERNAH SALING
> DIUJI TERHADAP SATU SAMA LAIN.** `spec/03` konsisten sendiri. `arch/07` §2
> konsisten sendiri. Keduanya ditulis pada hari yang sama oleh orang yang sama.
> Tabrakan 66 baris itu **tidak muncul saat salah satunya dibaca** — ia muncul
> saat yang satu dijalankan sebagai aturan atas yang lain.
>
> ⚠️ **Dan `arch/07` §4 mengaku sudah melakukannya.** Kolom *“Domain tujuan”*
> menuliskan apa yang seharusnya terjadi (Phase 11 → `agent`·`approval`·`tool`)
> — sebuah klaim, bukan hasil. Diukur: ke-22 nama Phase 11 mendarat di `agent`
> saja; `approval` dan `tool` **nol**. ⇒ pelajaran [#38](../../issues/38) sekali
> lagi, dalam bentuk paling halus: **sebuah tabel yang MENGGAMBARKAN hasil
> terbaca persis seperti tabel yang MENGUKURNYA.**

---

## K-16 · `data_subject` dan anotasi retensi masuk 23 tabel V0 sekarang

> Diputuskan 11 September 2026. Menerapkan [`../arch/06`](../arch/06-DATA-ARCHITECTURE.md)
> §5 dan §6, yang sudah ditetapkan 10 September dan **tidak pernah sampai ke DDL**.

| | |
|---|---|
| **Keputusan** | Ke-23 tabel V0 [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) mendapat kolom `data_subject` dan tiga anotasi `@retention` · `@who-can-set` · `@on-delete`. `audit_logs` — satu-satunya tabel V0 yang barisnya bisa milik pengguna **atau** milik sistem — menegakkan aturan §6 sebagai `CHECK ((data_subject = 'user') = (user_id IS NOT NULL))`, bukan sebagai `NOT NULL` kolom. |
| **Bukti** | Dijalankan mesin atas DDL: **P-1 gagal 23 dari 23**, **P-2 gagal 23 dari 23**, **P-3 gagal 1**. Semuanya gerbang CI yang sudah dinyatakan [`../arch/11`](../arch/11-PENEGAKAN.md) §3 — dan DDL yang akan dimigrasikan Sprint 0 tugas 0.4 melanggar ketiganya sejak baris pertama. |
| **Nilainya tidak dikarang** | `until-account-deleted` + `hard` untuk seluruh tabel milik pengguna datang dari **Prosedur hapus akun** `spec/01` tahap 3 (`DELETE FROM users` cascade); `forever` + `anonymise` untuk `audit_logs` dari tahap 5 (*“`audit_logs` tetap, `user_id` diacak jadi id semu”*). `who-can-set` memakai contoh yang [`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §5 berikan sendiri: `journal_entries` = `user`, `agent_runs` = `system`. |
| **Bacaan yang DITOLAK** | *“V0 hanya punya data pemilik akun, jadi `data_subject` mubazir sampai Phase 15.”* **Ditolak** — benar tentang V0 dan salah tentang biayanya. Menambahkannya nanti berarti **menebak** subjek tiap baris yang sudah terlanjur ditulis, dan RLS yang ditulis Sprint 1 sudah mengandaikan `user_id` sebagai satu-satunya sumbu kepemilikan. |
| **Yang TIDAK berubah** | **23 tabel tetap 23 · 22 event tetap 22 · 51 tugas tetap 51.** Yang bertambah kolom dan komentar, bukan tabel. |
| **Cara membalikkan** | Hapus kolom dan anotasinya, lalu cabut P-1/P-2/P-3 dari [`../arch/11`](../arch/11-PENEGAKAN.md) §3 — keduanya harus dilakukan bersama, sebab meninggalkan gerbang yang DDL-nya gagal adalah keadaan yang lebih buruk daripada keduanya. |

> 🔑 **Uji yang dipakai untuk memutuskan, dan ia menolak sesuatu di hari yang
> sama: yang boleh ditambahkan ke V0 hanyalah hal yang TIDAK BISA ditambahkan
> nanti.** `consents.purpose` lulus (persetujuan masa lalu tak bisa direka
> ulang). `data_subject` lulus. **`tool.failed` sebagai event DITOLAK** — sebuah
> event bisa mulai diterbitkan kapan saja tanpa kehilangan apa pun yang sudah
> ada, dan [`../arch/07`](../arch/07-EVENT-CONTRACTS.md) §7 yang menuntutnya
> justru menunjuk tugas 4.3 yang tidak menyebut event sama sekali.
>
> 💡 **Cara menemukannya adalah pertanyaan yang sama dengan K-15, satu lapis
> lebih tinggi:** [`../arch/11`](../arch/11-PENEGAKAN.md) §2 menggolongkan
> kelompok **P** sebagai *“butuh kode: ya”* — dan itu benar untuk artefak yang
> **berjalan**. Tetapi yang diperiksa P-1/P-2/P-3 adalah **DDL**, dan DDL-nya
> sudah ada sebagai **dokumen** sejak `spec/01` ditulis. ⇒ ***apakah yang
> diperiksanya sudah ada dalam bentuk lain?*** — pertanyaan itu memindahkan
> **delapan** pemeriksaan dari “menunggu kode” ke “jalan hari ini”.

---

## Yang sengaja **tidak** saya putuskan

| Butir | Kenapa |
|---|---|
| ~~[#139](../../issues/139) Master Architecture v2.0~~ | ✅ **pemilik memerintahkannya 10 Sep 2026** (*“kerjakan semua tugas dan fase yang masih tersisa”*) — dikerjakan, hasilnya [`../arch/`](../arch/README.md) |
| [#3](../../issues/3) siapa mengerjakan V0 | orang dan waktu |
| [#20](../../issues/20) cek merek & domain | menuntut pencarian merek dan pembelian |
| **seluruh butir C** (hukum & privasi) | risikonya ditanggung orang yang tidak ikut memilih |
| §16.5 · §16.7 rantai humanoid | benda yang bisa melukai orang — gerbangnya bukan keputusan gaya |
| [#4](../../issues/4) Mental Wellness | cakupan produk |
| [#34](../../issues/34) ambang Confidence | butuh data nyata untuk dikalibrasi; menebak angkanya lebih buruk daripada membiarkannya terbuka |

💡 **Aturan yang saya pakai untuk memilah:** *kalau salahnya keputusan ini
ditanggung orang lain — pengguna, penerima pesan, atau pemilik uangnya —
keputusan itu bukan milik saya.*
