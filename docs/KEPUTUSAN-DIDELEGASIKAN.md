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

## K-17 · Arah IMPOR modul V0: `events` di bawah modul domain

> Diputuskan 16 September 2026, saat Sprint 0 tugas 0.8 menuliskan batas modul
> [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) sebagai kontrak `import-linter`.

| | |
|---|---|
| **Keputusan** | Lapisan impor V0, atas boleh mengimpor bawah dan tidak pernah sebaliknya: `agents` › `intelligence` › `memory` › `goals \| habits \| checkins \| journal \| activities \| profile` (saling independen) › `events` › `identity` › `platform`. Ditegakkan kontrak `m1-m3-lapisan` di `pyproject.toml`. |
| **Bukti** | `spec/06` aturan 6: *“setiap tulisan ke tabel domain **wajib** menerbitkan event”* — sebuah modul yang wajib menerbitkan harus bisa **memanggil** penerbitnya. Aturan 4: *“tidak ada modul yang mengimpor `agents`”* ⇒ `agents` di puncak. `platform` *“boleh dipakai semua”* dan (arch/04 §1 aturan 7) tidak boleh tahu aturan domain ⇒ di dasar. `memory` membaca **isi** jurnal untuk ekstraksi (tugas 3.6) — dan isi jurnal sengaja tidak pernah masuk event (`spec/03`: `journal.created` hanya membawa `word_count`) ⇒ `memory` wajib bisa mengimpor `journal`, jadi di atas domain. `intelligence`: 5.3 menulis `human_states` milik `profile`, 5.5 membaca subjek habit & goal ⇒ di atas `memory`. |
| **Bacaan yang DITOLAK** | *“Gambar `spec/06` menaruh `events` di bawah modul domain dengan panah ke bawah, dan arch/04 §1 menaruh `events` di L2 di atas `services/*` L1 — jadi `events` lapisan yang lebih TINGGI.”* 🛑 **Ditolak:** kedua gambar menggambarkan arah **data** (kejadian mengalir dari domain ke `events` lalu ke `memory`). Kalau arah itu dipakai sebagai arah impor, modul domain tidak bisa menerbitkan event tanpa `events` mengimpor tiap modul domain — kebalikan dari *“komunikasinya lewat event”*. |
| **Yang TIDAK berubah** | 12 modul · 23 tabel · kepemilikan tabel `spec/06` · aturan 3 (domain tidak saling impor) — seluruhnya tetap. |
| **Cara membalikkan** | Ubah urutan `layers` kontrak `m1-m3-lapisan`, lalu jalankan `uv run python tools/uji_mutasi_kode.py`. Selama modul domain belum menerbitkan event (Sprint 3), biayanya nol. |

> ⚠️ **Satu hal yang berkas ini TIDAK putuskan, dan akan datang di Sprint 1:**
> di mana alur *register* membuat baris `profiles` — `identity` di bawah
> `profile`, jadi `identity` tidak boleh memanggilnya. Dua jalan sah: titik
> rakit `hvx.main` mengorkestrasi keduanya, atau `profile` mendengarkan
> kejadian pendaftaran. Dipilih saat tugas 1.1/1.3 ditulis, dengan uji.
>
> ✅ **Dijawab 17 Sep 2026, saat 1.1 ditulis — gabungan keduanya.** `identity`
> mengumumkan pendaftaran lewat **pendengar** (`PendengarPendaftaran`) yang
> dijalankan di **transaksi pendaftaran yang sama**; titik rakit `hvx.main`
> memasang `profile.buat_profil_awal` sebagai pendengarnya. `identity` tidak
> tahu siapa yang mendengar, dan pendengar yang gagal menggagalkan seluruh
> pendaftaran — akun tanpa profil tidak pernah tercipta. Bukan event: kejadian
> yang diproses sesudah commit tidak bisa menjamin itu.

---

## K-18 · Satu commit per tugas; PR boleh satu per sprint

> Diputuskan 16 September 2026, saat Sprint 0 (delapan tugas) dibuka sebagai PR.

| | |
|---|---|
| **Keputusan** | Unit tinjauan adalah **commit**: tiap tugas `spec/07` satu commit, dengan nomor tugasnya di pesan commit. Satu PR boleh memuat seluruh tugas satu sprint. Baris HUMAN REVIEW §27 tidak berubah — **pemilik yang menggabungkan** (H-25). |
| **Bukti** | `spec/07` semula menulis *“setiap tugas: satu PR”*. Delapan tugas Sprint 0 saling bergantung dalam satu berkas bersama (`pyproject.toml` memegang konfigurasi uji 0.6, kontrak 0.8, dan dependensi 0.1 sekaligus) — delapan PR bertumpuk akan menuntut pemilik menggabungkan secara berurutan, dan tiap PR sebelum yang terakhir tidak bisa lulus gerbang penuh sendirian. |
| **Bacaan yang DITOLAK** | *“Satu PR per sprint berarti tinjauan lebih kasar.”* Ditolak sebagian: tinjauan per commit tetap mungkin di antarmuka PR. ⚠️ **Harga yang diakui:** hanya commit TERAKHIR yang dijamin lulus gerbang penuh; commit di tengah tidak diverifikasi satu per satu, dan itu dinyatakan di deskripsi PR. |
| **Cara membalikkan** | Pecah PR menurut commit (satu branch per tugas, bertumpuk), lalu kembalikan kalimat `spec/07`. |

---

## K-19 · Kepemilikan data dijaga basis data: RLS berbasis pengguna-transaksi, FK komposit, peran aplikasi

> Diputuskan 17 September 2026, menerapkan kata pemilik **H-27** — *“data
> masing-masing pengguna milik pribadi user”* — dan menutup **B-40** · **B-41**.

| | |
|---|---|
| **Keputusan** | **(1)** RLS di tiap tabel milik pengguna: `user_id = app_current_user_id()`, dengan `app_current_user_id()` membaca `hvx.user_id` yang diisi aplikasi **per transaksi** (`set_config(…, true)`, `platform.transaksi_pengguna`) — tidak diisi ⇒ `NULL` ⇒ nol baris. **(2)** FK antara dua tabel milik pengguna selalu pasangan `(induk_id, user_id) → induk(id, user_id)`. **(3)** api tersambung sebagai anggota `hvx_app` — hak akses tabel demi tabel, `audit_logs`/`events` hanya-tambah — dan **menolak mulai** sebagai superuser, `BYPASSRLS`, atau pemilik (termasuk pewaris pemilik) tabel. |
| **Bukti** | H-27. **B-40**: sebagai superuser pemilik tabel, `REVOKE` tidak berlaku dan RLS dilewati — diverifikasi. **B-41**: diukur, anak B menempel ke goal A lalu ikut terhapus. PostgreSQL: pemeriksaan FK **tidak menerapkan RLS** ⇒ RLS saja tidak menutup B-41; FK komposit saja tidak mencegah **membaca** baris orang lain ⇒ keduanya dibutuhkan, dan keduanya tak berarti tanpa (3). |
| **Bacaan yang DITOLAK** | **(a)** *“Satu peran PostgreSQL per pengguna, RLS pada `current_user`”* — ditolak: ribuan peran login yang berlaku sekluster, dan pool koneksi tidak bisa dipakai bersama antarpengguna. **(b)** *“Cukup aturan repository `WHERE user_id = :me`, dijaga uji”* — ditolak: satu kueri yang lupa membocorkan data pengguna lain; dengan RLS, kelupaan yang sama memulangkan nol baris. **(c)** *“`FORCE ROW LEVEL SECURITY` supaya pemilik tabel pun terkena”* — ditolak untuk V0: migrasi dan pemeliharaan (sapuan hapus akun) butuh melihat semua baris, dan api tidak pernah memakai peran pemilik — dijaga penjaga mulai. |
| **Harga yang diakui** | Tiap kueri wajib di dalam `transaksi_pengguna`. Pencarian **sebelum** pengguna dikenali (login per email) dan sapuan **lintas akun** (hapus akun 6.5) butuh fungsi `SECURITY DEFINER` yang sempit, satu per kebutuhan — bukan kebijakan yang dilonggarkan. |
| **Cara membalikkan** | Migrasi baru yang `DROP POLICY` + `DISABLE ROW LEVEL SECURITY`; FK komposit boleh dibiarkan (tidak merugikan apa pun). `test_kepemilikan_data.py` akan merah — ubah bersamanya, dengan catatan kenapa. |

---

## K-20 · CI tanpa tagihan: status commit dari gerbang lokal

> Diputuskan 17 September 2026, menerapkan kata pemilik **H-26** — *“gunakan
> alternatif versi gratis jangan ada tagihan”* — untuk [#160](../../issues/160).

| | |
|---|---|
| **Keputusan** | `tools/ci_lokal.py --lapor-github` menjalankan gerbang PENUH lalu menempelkan hasilnya ke commit HEAD sebagai status **`ci-lokal`** lewat API status commit. Laporan ditolak untuk gerbang sebagian, pohon kerja kotor, atau commit yang belum menjadi ujung cabang di `origin`. Alur GitHub Actions hanya `workflow_dispatch`, dijaga `test_rantai_pasok.py`. |
| **Bukti** | H-26. Actions pada repo privat memakai menit berbayar, dan akun ini terhalang tagihan: tiap PR menampilkan job merah **0 langkah** yang tidak pernah dimulai (PR #163). API status commit adalah fitur dasar repo — tidak memakai menit Actions. |
| **Bacaan yang DITOLAK** | **(a)** *“Runner self-hosted di mesin pemilik”* — ditolak untuk sekarang: layanan yang berjalan terus di mesin pribadi dan menjalankan kode alur kerja, sementara apakah ia lolos dari blokir tagihan akun **belum diverifikasi**. **(b)** *“Jadikan repo publik — Actions dan perlindungan branch gratis”* — bukan milik saya: membuka seluruh naskah pemilik. **(c)** *“Layanan CI pihak ketiga paket gratis”* — butuh akun baru dan akses ke repo privat: keputusan pemilik. |
| **Harga yang diakui** | Status `ci-lokal` **bisa ditempelkan siapa pun** yang punya akses tulis — ia bukti kejujuran pengembang, bukan penghalang. PR merah tetap tidak terhalang digabung; penghalangnya HUMAN REVIEW. |
| **Cara membalikkan** | Kembalikan pemicu `pull_request`/`push` di `ci.yml` dan uji `test_alur_actions_tanpa_pemicu_otomatis_supaya_tidak_ada_tagihan` — sesudah pemilik membereskan tagihan atau membuat repo publik. |

---

## K-21 · Sesi: token opak di Redis, bukan JWT

> Diputuskan 17 September 2026, saat Sprint 1 tugas 1.2 ditulis.

| | |
|---|---|
| **Keputusan** | Token akses dan token segar adalah string acak 256 bit berawalan (`hvxa_` · `hvxr_`). Redis menyimpan **sidik** sha256-nya, tidak pernah tokennya. Akses 15 menit; segar 30 hari dan **berotasi** tiap dipakai (`GETDEL`, atomik); token segar bekas yang dipakai lagi dianggap dicuri — **seluruh sesi dicabut**, termasuk pasangan terbarunya. Tiap operasi yang **membaca lalu menulis** catatan sesi (putar · cabut) adalah **satu skrip Lua**; token akses tidak boleh hidup lebih lama dari catatan sesinya; status akun dibaca **sebelum** tiap rotasi, dan akun yang tidak aktif kehilangan **semua** sesinya. |
| **Bukti** | `spec/07` 1.2: *“token dicabut → 401 seketika”* menuntut pemeriksaan penyimpanan di **tiap** permintaan. Kalau pemeriksaan itu tetap ada, tanda tangan JWT hanya menambah hal yang bisa salah (algoritme, kunci, `alg: none`). RFC 9700 §4.14.2: klien publik — aplikasi seluler V0 — butuh rotasi token segar dengan deteksi pemakaian ulang. |
| **Bacaan yang DITOLAK** | **(a)** *“JWT berumur pendek tanpa pemeriksaan penyimpanan”* — ditolak: pencabutan baru berlaku sesudah token kedaluwarsa, melanggar 1.2. **(b)** *“JWT + daftar cabut di Redis”* — ditolak: satu panggilan Redis tiap permintaan tetap ada, ditambah seluruh kerumitan JWT. **(c)** *“Token mentah sebagai kunci Redis”* — ditolak: salinan Redis yang bocor langsung bisa dipakai; sidik atas 256 bit acak tidak bisa dibalik. **(d)** *“Baca catatan sesi, lalu tulis dalam `MULTI`”* — bentuk pertama, ditolak tinjauan Sprint 1: keluar yang jatuh di celahnya dihidupkan kembali oleh penyegaran, dan sesinya tidak bisa dicabut lagi. **(e)** *“`Idempotency-Key` untuk `refresh`”* — ditolak (E-165): memutar ulang jawabannya berarti menyimpan token mentah. |
| **Harga yang diakui** | Redis menjadi ketergantungan autentikasi: Redis mati → rute bersesi gagal, tidak tetap melayani. Layanan terpisah di V2 yang ingin memeriksa token harus bertanya ke `identity`. **Rotasi ketat** (RFC 9700 §4.14.2): klien yang kehilangan jawaban penyegaran lalu mengulangnya dengan token yang sama dianggap pencuri — sesinya dicabut, pengguna masuk lagi. Penyegaran kini butuh basis data (status akun); tersendat → `500`, tetapi tokennya **tidak** terbakar. Skrip Lua menyentuh kunci yang namanya dibaca di dalamnya — sah untuk satu Redis, **tidak** untuk Redis Cluster (kunci satu sesi wajib berbagi hash tag). |
| **Cara membalikkan** | Ganti `PenyimpanSesi` (`identity/sesi.py`); kontraknya `pengguna_saat_ini` dan `test_sesi.py`. Belum ada token di tangan klien mana pun — biayanya nol sampai rilis pertama. |

---

## K-22 · Sandi dan batas laju: angka yang dipilih, dan penguncian per akun

> Diputuskan 17 September 2026, saat Sprint 1 tugas 1.1 dan 1.7 ditulis.

| | |
|---|---|
| **Keputusan** | **Sandi** — 15–128 karakter tanpa aturan komposisi, **daftar tolak** (kata konteks · pengulangan · urutan), NFKC sebelum hashing. **Batas laju** — GCRA, `jumlah/detik`, boleh meledak sampai `jumlah`: per IP `600/60` di seluruh `/v1/*` (IPv6 per /64) · per pengguna `300/60` · `register` + `login` per IP `30/600` · login **gagal** per akun `100/86400` — jatahnya **dipakai sebelum argon2**, kuncinya email **sebagaimana `citext` membandingkannya** (`lower()` basis data), dihapus begitu berhasil masuk. Semua angka variabel `HVX_RATE_LIMIT_*`. Daftar tolak menilai pengulangan dari yang **diketik**, bukan hanya kerangka huruf-angkanya — sandi simbol atau emoji tidak ditolak karena tak berhuruf. |
| **Bukti** | NIST SP 800-63B-4 §3.1.1.2 (panjang minimal 15 untuk sandi faktor tunggal, daftar tolak *SHALL*, NFKC *SHOULD*) dan batas ≤ 100 kegagalan beruntun per akun — yang **tidak** dipenuhi V0, lihat harga di bawah (**B-42**). `spec/07` 1.7 menuntut per pengguna **dan** per IP tanpa angka: per IP saja tidak menghentikan tebakan terdistribusi atas satu akun; per akun saja tidak menghentikan satu IP yang mencoba ribuan akun. `refresh` sengaja **di luar** batas kredensial: ia butuh token acak 256 bit, dan semua klien di balik satu NAT operator menyegarkan dari IP yang sama. |
| **Bacaan yang DITOLAK** | **(a)** *“Jendela tetap per menit”* — ditolak: meloloskan 2× batas di perbatasan dua jendela, dan `Retry-After`-nya hanya bisa menunjuk awal menit berikutnya. **(b)** *“Kunci akun permanen sesudah N kegagalan”* — ditolak: V0 belum punya jalur pemulihan akun, jadi siapa pun yang tahu sebuah email bisa mengunci akunnya selamanya. **(c)** *“Kunci per IP dari `X-Forwarded-For`”* — ditolak: header itu dikarang klien; uvicorn `--proxy-headers` membacanya hanya dari proksi tepercaya (`FORWARDED_ALLOW_IPS`). **(d)** *“Tanya jatah sebelum argon2, hitung sesudah gagal”* — bentuk pertama, ditolak tinjauan Sprint 1: dua belas tebakan serentak lolos pertanyaan sebelum satu pun dihitung. **(e)** *“Kunci = `email.lower()` Python”* — ditolak: `İ` menjadi `i` di PostgreSQL dan `i̇` di Python, dan tiap `i` di email menggandakan jatah. |
| **Harga yang diakui** | 🔴 **Ini batas LAJU, bukan batas 100 kegagalan beruntun NIST §3.2.2 (*SHALL*)** — dan versi pertama keputusan ini mengklaim sebaliknya (tinjauan Sprint 1). `100/86400` meloloskan 100 tebakan sekaligus, lalu satu tiap ±14 menit tanpa ujung, dan tiap masuk yang berhasil mengosongkannya: setahun, puluhan ribu tebakan atas satu akun. Memenuhi *SHALL* itu berarti mengunci akun — bacaan (b) yang ditolak di atas — sampai jalur pemulihan akun ada (**B-42**). Batas per akun juga **bisa disalahgunakan**, dan tidak selunak yang semula ditulis: jatah dipakai sebelum sandinya dicocokkan, jadi 100 tebakan salah membuat pemilik akun menerima `429` — juga dengan sandi yang benar — dan penyerang yang terus mengirim satu tebakan tiap ±14 menit (±100 permintaan sehari) menahannya di sana **selama ia mau**. Bacaan (b) ditolak karena mengunci selamanya dengan satu ledakan; pilihan ini mengunci selama penyerang bertahan. Diterima untuk V0: menebak sandi 15+ karakter yang lolos daftar tolak jauh lebih mahal daripada mengunci. Angka per IP **belum diukur** terhadap NAT operator seluler — kalau banyak pengguna berbagi satu IP, angkanya yang dinaikkan, bukan kuncinya yang dicabut. |
| **Cara membalikkan** | Angka: ubah variabel `HVX_RATE_LIMIT_*`, tanpa kode. Satu kunci: hapus pemanggilnya di `identity/laju.py` atau middleware di `hvx.main` — `test_batas_laju.py` merah dan wajib diubah bersamanya. Daftar tolak: `identity/sandi.py` — sebelum baris akun pertama, NFKC boleh dicabut tanpa biaya; sesudahnya, hash yang ada patah. |

---

## K-23 · Bacaan lintas modul domain lewat titik rakit; energi check-in ke tier adaptif

> Diputuskan 24 September 2026, saat Sprint 2 tugas 2.2 dan 2.4 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Modul domain yang butuh MEMBACA data modul domain lain di transaksi yang sama menerima **fungsi pembaca** dari titik rakit `hvx.main` lewat `app.state` — bukan impor, bukan SQL ke tabel milik modul lain. Pertama: `habits` menerima `profile.zona_waktu` (*“hari ini”* rentetan, 2.4) dan `checkins.energi_pada` (tier yang disarankan, 2.2/2.5). Pembaca berjalan di koneksi pemanggil — satu transaksi, satu RLS. Rute yang butuh pembaca **menolak berjalan** bila titik rakit lupa memasangnya (tidak jatuh ke UTC atau "tanpa energi" diam-diam). **(2)** Energi check-in 1–5 dipetakan ke tiga kondisi naskah 4 §34: **3–5 atau belum check-in** = normal (tier 0) · **2** = rendah (tier 1) · **1** = sangat rendah (tier paling ringan). |
| **Bukti** | `spec/06` aturan 3 (domain tidak saling impor) dan aturan 5 (SQL hanya tabel sendiri) — keduanya ditegakkan mesin. Tetapi event (jalur yang aturan 3 sebut) melayani **tulisan**, bukan **bacaan**: tidak ada event `profile.*` di 22 event V0 (E-166), dan zona waktu dibutuhkan pada saat membaca. Preseden: **K-17** — pendengar pendaftaran yang dipasang titik rakit. Pemetaan energi: naskah 4 §34 menyebut *rendah* dan *sangat rendah* tanpa skala; skala `daily_checkins.energy` 1–5 dengan 3 sebagai titik tengah. |
| **Bacaan yang DITOLAK** | **(a)** *“Klien mengirim `?today=` dan `?energy=`”* — ditolak: agent (Sprint 4, tool `habit.streak`) tidak punya perangkat, dan aturan bisnis pindah ke klien. **(b)** *“`habits` membaca `profiles.timezone` langsung”* — ditolak: melanggar aturan 5, dan pemisahan layanan V2 menjadi penulisan ulang. **(c)** *“Proyeksi zona waktu di tabel `habits`”* — ditolak: menambah kolom demi menyalin data milik modul lain, dan butuh event profil yang belum ada. **(d)** *“Belum check-in = energi rendah”* — ditolak: sistem tidak menurunkan target seseorang karena ia belum menjawab (*“Bukan menyalahkan user”*, naskah 4 §33). |
| **Harga yang diakui** | Ketergantungan antarmodul yang **tidak terlihat** oleh `import-linter`: ia hidup di `hvx.main`, dan pemisahan layanan V2 mengganti tiap pembaca dengan panggilan jaringan. Karena itu tiap pembaca dijaga uji titik rakit (`test_main.py`) — dan jumlahnya kecil dengan sengaja. |
| **Cara membalikkan** | Hapus baris `app.state.pembaca_*` di `hvx.main` dan parameternya di `habits/service.py`; `test_main.py` dan uji rentetan/tier merah dan wajib diubah bersamanya. Pemetaan energi: `habits/tier.py`. |

---

## K-24 · Ukuran yang dibatasi saat menulis, dan `Idempotency-Key` yang mengingat rujukan

> Diputuskan 24 September 2026, saat temuan tinjauan Sprint 2 dibetulkan (E-171, E-172).

| | |
|---|---|
| **Keputusan** | **(1)** Batas yang ditegakkan **saat menulis** — diperiksa serial dengan kunci penasihat per pemilik, jadi tulisan serentak tidak bisa bersama melewatinya: **1.000** goal hidup per pengguna · **100** milestone per goal · **500** habit hidup per pengguna (`422 goal_limit_reached` · `milestone_limit_reached` · `habit_limit_reached`). **(2)** Badan permintaan paling besar **1 MiB** → `413 payload_too_large`, sebelum autentikasi dan sebelum badan dibaca. **(3)** `Idempotency-Key` mengingat **rujukan** selama 24 jam — sidik HMAC permintaan, status, id sumber daya — **bukan isi jawaban**; ulangan membaca ulang sumber daya itu di bawah RLS pengguna yang sama. Paling banyak **1.000 kunci baru per pengguna per 24 jam** (`429 rate_limited`); ulangan kunci lama tidak memakai kuota. |
| **Bukti** | Tinjauan keamanan Sprint 2, diukur: `GET /goals/{id}/tree` atas 20 ribu goal = jawaban 86 MB dan event loop tertahan; badan jawaban ~5,2 KiB tersimpan untuk permintaan 19 byte, di Redis `noeviction` yang sama dengan sesi — batas laju per pengguna `300/60` (K-22) berarti 432 ribu entri sehari per akun; catatan pengguna tinggal di Redis dan AOF-nya 24 jam sesudah hapus-keras; FastAPI membaca badan utuh sebelum dependensi autentikasi berjalan. Tinjauan kontrak: `GET /habits` memotong di 500 tanpa tanda (F9). |
| **Bacaan yang DITOLAK** | **(a)** *“Beri halaman pada pohon dan daftar habit”* — ditolak: pohon adalah satu jawaban dengan sengaja (E-168), dan layar hari ini butuh semua habit hari itu. **(b)** *“Potong saat membaca”* — ditolak: itu tepat pemotongan diam-diam yang E-168 larang. **(c)** *“Simpan isi jawaban, dengan batas ukuran”* — ditolak: isi pengguna tetap tinggal di Redis sesudah dihapus, dan batas per entri tetap berlipat per permintaan. **(d)** *“Batas laju saja cukup”* — ditolak: batas laju menghitung permintaan, bukan memori yang ditinggalkannya. **(e)** *“Redis cache tersendiri berkebijakan eviction”* — ditunda: tambah satu layanan untuk masalah yang kuota + rujukan sudah batasi. |
| **Harga yang diakui** | Ulangan menerima keadaan **sekarang**: `PATCH` lain di antaranya ikut terlihat, dan sumber daya yang sudah dihapus menjawab `404`. Draf IETF membolehkan server menyimpan jawaban; yang ini memilih tidak menyimpan isi pengguna di luar PostgreSQL. Pengguna yang sungguh butuh lebih dari 500 habit atau 1.000 goal ditolak; jurnal lebih dari 1 MiB teks (±500 halaman) ditolak; antrean luring lebih dari 1.000 tulisan berkunci sehari menerima `429` sampai jendelanya lewat. Kunci penasihat menyerialkan pembuatan goal/habit **satu** pengguna — bukan antarpengguna. |
| **Cara membalikkan** | Angka: `MAKS_GOAL` · `MAKS_MILESTONE` (`goals/service.py`), `DAFTAR_MAKS` (`habits/repository.py`), `MAKS_BADAN_BYTE` (`platform/batas_badan.py`), `KUOTA_KUNCI` (`platform/idempotensi.py`) — `test_batas_dan_balapan.py`, `test_masukan_ketat.py`, `test_idempotensi.py` diubah bersamanya. Menyimpan isi jawaban lagi: `Idempotensi.jalankan` — `test_redis_hanya_menyimpan_rujukan_tanpa_isi_tulisan` merah dan wajib dihapus bersama alasannya. |

---

## K-25 · Relay kotak keluar dan grup konsumen: stream membawa rujukan, angka-angkanya

> Diputuskan 24 September 2026, saat Sprint 3 tugas 3.3 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Satu stream Redis `{prefix}:events` berisi **rujukan** (id · pemilik · jenis) — isi event dibaca konsumen dari PostgreSQL di bawah RLS pemiliknya, di transaksi yang sama dengan tulisan penangannya; pesan di-ACK **sesudah** commit. **(2)** Relay di proses terpisah (`python -m hvx.pekerja`), kursor `(recorded_at, id)` di Redis, dan **menoleh ke belakang 60 detik** tiap putaran; penanda terkirim (`ZADD NX` ke satu himpunan terurut, skornya `recorded_at`) dan `XADD` dalam **satu** skrip Lua; penanda dibuang begitu kursor melewati jendela belakangnya — bukan menurut jam. **(3)** Konsumen mengklaim pesan yang menganggur **30 detik** (`XAUTOCLAIM`); sesudah diserahkan **5 kali** pesan pindah ke stream **mati** `{prefix}:events:mati`. **(4)** Stream dipangkas tiap ±1 menit **tepat** (`XTRIM MINID`, bukan `~`) sampai pesan tertua yang masih ditunggu satu pun grup. **(5)** Penyelaras memori → Qdrant berjalan tiap 2 detik di proses yang sama. **(6)** Stream mati menyimpan rujukan **7 hari** (`UMUR_MATI_S`). **(7)** Hanya peran `hvx_pekerja` yang boleh memanggil fungsi relay & penyelaras — login pekerja anggotanya, login api **tidak** (api menolak mulai sebagai anggotanya). |
| **Bukti** | spec/07 3.3 *“consumer mati → event tidak hilang saat hidup lagi”*; spec/03 *Consumer V0* (Redis Streams + consumer group, konsumen “boleh gagal” wajib idempoten). Transaksi yang lebih dulu menyisip bisa lebih akhir commit — relay yang hanya maju melompatinya selamanya (diukur, `test_relay.py`). `XTRIM ~` hanya membuang simpul radix utuh (±100 entri): stream kecil tidak pernah terpangkas (diukur). E-171: data pengguna tidak tinggal di Redis. 🔴 **Tinjauan keamanan & kontrak Sprint 3:** penanda per event berumur 24 jam menumpuk ±50 MB per akun sehari di Redis `noeviction` (S3) — dan karena jendela belakang dihitung dari KURSOR, relay yang sepi 24 jam mengirim ulang event terakhirnya (K1); peran api yang menghadap internet bisa memanggil fungsi relay dan membaca linimasa semua pengguna (S4). |
| **Bacaan yang DITOLAK** | **(a)** *“Payload event di stream”* — ditolak: isi pengguna tinggal di Redis/AOF sesudah akun dihapus, dan konsumen tidak lagi membaca di bawah RLS. **(b)** *“Relay di proses api”* — ditolak: tiap replika api menjalankan relay-nya sendiri, dan `XREADGROUP BLOCK` bersaing dengan permintaan HTTP. **(c)** *“LISTEN/NOTIFY PostgreSQL”* — ditolak: notifikasi hilang saat pendengar mati, jadi tetap butuh kursor — dua mekanisme untuk satu hal. **(d)** *“Penanda dengan TTL pendek (mis. 10 menit)”* — ditolak: relay yang berhenti lebih lama dari TTL-nya mengirim ulang jendela belakangnya; memangkas menurut kursor tidak bergantung pada jam. |
| **Harga yang diakui** | Transaksi yang commit **lebih dari 60 detik** sesudah menyisip event-nya tidak pernah dikirim (tulisan api selesai dalam milidetik). Jendela belakang dibaca paling banyak 1.000 event per putaran. Penyelaras memindai `memories` penuh tiap putaran (`embedding_model IS DISTINCT FROM`) — cukup untuk V0 (satu pengguna nyata); V1 butuh kolom penanda berindeks. Pesan di stream mati belum punya alat pemutar ulang, dan hilang sesudah 7 hari. Kursor relay hidup di Redis: Redis yang kehilangan datanya memutar ulang riwayat — konsumen wajib idempoten (spec/03). |
| **Cara membalikkan** | Angka: `LIHAT_BELAKANG_S` (`events/relay.py`), `min_idle_ms` · `maks_kirim` · `UMUR_MATI_S` (`events/stream.py`), `JEDA_*` · `PANGKAS_TIAP` (`hvx/pekerja.py`) — `test_relay.py` diubah bersamanya. Payload di stream: `_KIRIM` + `KonsumenStream._proses`; `test_relay_menyalin_rujukan_sekali_tanpa_payload` merah dan wajib dihapus bersama alasannya. |

---

## K-26 · Penyemat memori V0: lokal, deterministik, BERKUNCI

> Diputuskan 24 September 2026, saat Sprint 3 tugas 3.5 ditulis.

| | |
|---|---|
| **Keputusan** | Memori disemat `hvx-hash-v1-384`: *feature hashing* bertanda atas kata · pasangan kata · trigram huruf, 384 dimensi, dinormalkan — `blake2b` **berkunci** `HVX_SEMATAN_KEY` (wajib bila `HVX_QDRANT_URL` diisi), dengan kunci **turunan per pengguna** (`HMAC(kunci, user_id)`): penyemat proses sendiri tidak menyemat apa pun. Sidik kunci ikut di nama penyemat (`memories.embedding_model` dan payload `model` Qdrant): vektor dari kunci lain tidak pernah dibandingkan, dan penyelaras menyemat ulang memori yang disemat penyemat lain. Yang disemat paling banyak **20.000 karakter pertama** tiap memori, di thread — bukan di event loop pekerja. Qdrant lewat REST (`httpx`, di `platform` — B-2). |
| **Bukti** | Penyedia model milik pemilik (arch/05 §6, A-6/#18 — tarif & bagi hasil): memilih API sematan berbayar berarti mengambil keputusan itu. CI tanpa tagihan (H-26): uji tidak boleh memanggil layanan berbayar. Rancangan pemilik menyemat jurnal ke basis data vektor (naskah [`84`](84-DATABASE-ARCHITECTURE.md) `journal_embeddings`, [`119`](119-R8-R9-EMBEDDING-REPRESENTASI.md) *Journal → semantic search*) — dan jurnal adalah Level 3 *Sensitive* ([`133`](133-DATA-CLASSIFICATION.md)). *Feature hashing* tanpa kunci bisa **dibalik dengan kamus**: siapa pun yang memegang vektornya menghitung hash tiap kata calon (diuji: `test_tanpa_kunci_yang_sama_kata_tidak_bisa_ditebak_dari_vektor`). Qdrant tidak punya RLS. 🔴 **Tinjauan keamanan Sprint 3 (S1):** dengan SATU kunci untuk semua pengguna, penyerang yang bisa membaca Qdrant cukup membuat akun biasa, menulis kata-kata kamus sebagai jurnalnya sendiri, dan membandingkan vektor yang disemat server dengan vektor korban — diuji: mood dan keenam kata jurnal korban terbaca. **(S2):** 40 jurnal 100 ribu karakter dari satu pengguna menahan event loop pekerja 6,5 dtk. |
| **Bacaan yang DITOLAK** | **(a)** *“Model sematan sungguhan (sentence-transformers)”* — ditolak untuk V0: ratusan MB bobot di citra api, PyTorch di rantai pasok, dan unduhan model di CI. **(b)** *“`hash()` Python”* — ditolak: diacak per proses, vektor kemarin tidak cocok dengan kueri hari ini. **(c)** *“Kunci diturunkan dari `HVX_IP_HASH_KEY`”* — ditolak: memutar kunci IP (mis. sesudah bocor) diam-diam menyemat ulang seluruh memori. **(d)** *“`qdrant-client`”* — ditolak: empat panggilan tidak sepadan dengan gRPC dan numpy. **(e)** *“`model_version` sebagai nama penyemat”* — bentuk pertama, ditolak tinjauan kontrak (K4): kolom itu tempat ambang keyakinan #34 (arch/README), dan penyelaras menimpanya; kini `embedding_model` kolom sendiri. |
| **Harga yang diakui** | ⚠️ Kemiripan **leksikal**, bukan makna: *“lelah”* dan *“capek”* tidak berdekatan. Kunci per pengguna melindungi vektor dari pembacaan kata dan dari kamus akun lain, **bukan** dari perbandingan di dalam satu pengguna: dua teks sama milik satu pengguna tetap berjarak nol. Kata sesudah karakter ke-20.000 sebuah jurnal tidak bisa ditemukan pencarian. Enkripsi sematan itu sendiri — catatan di naskah [`145`](145-DATA-VAULT-ENKRIPSI-PRIVACY-AI.md) — tetap keputusan pemilik (butir C). |
| **Cara membalikkan** | Kelas penyemat lain dengan `nama` lain di `platform/sematan.py` (antarmuka `Penyemat`); penyelaras menyemat ulang semuanya sendiri karena `embedding_model` berbeda. |

---

## K-27 · Memori V0 dari jurnal & mood: episodik, keyakinan 1.000, ekstraksinya service

> Diputuskan 24 September 2026, saat Sprint 3 tugas 3.6 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Tiap `mood.logged` dan `journal.created` melahirkan tepat satu memori `kind='episodic'` — isi yang **dilaporkan** atau **ditulis** pengguna (mood: `"Mood dilaporkan 2/5 (cemas): …"`; jurnal: judul + isi), `valid_from` = waktu kejadiannya, `scope` `mood` / `journal_raw`. **(2)** `confidence = 1.000`, `evidence_count = 1`, `model_version = hvx-episodik-v1` (cara memori dan keyakinannya lahir — tempat ambang #34, arch/README): yang diyakini adalah **bahwa** pengguna melaporkan atau menulisnya — bukan bahwa isinya benar tentang dirinya. **(3)** Jalur ekstraksi adalah **service** (konsumen stream `memori`), bukan agent: ia selalu menulis dan tidak memilih tool — separuh jawaban [`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §2.2. **(4)** Jurnal yang disunting → memorinya mengikuti; dihapus → isinya dikosongkan di transaksi yang sama, titik Qdrant dan barisnya dibuang penyelaras. |
| **Bukti** | spec/07 3.6 menuntut lima medan pada tiap memori. Naskah [`15`](15-MEMORY.md): *Episodic = kejadian*; [`163`](163-CONFIDENCE-UNCERTAINTY-EVALUASI-FEEDBACK.md): tiap **inferensi** membawa `confidence` dan `source` — dan catatan laporan sendiri bukan inferensi; spec/01 E-34: mood *dilaporkan*, bukan ditaksir. Naskah [`139`](139-PRIVACY-DELETION-RETENTION.md): hapus tidak boleh berhenti di baris PostgreSQL. |
| **Bacaan yang DITOLAK** | **(a)** *“Biarkan bawaan kolom 0.500”* — ditolak: angka yang tidak dipilih siapa pun terbaca sebagai keraguan yang tidak ada. **(b)** *“Ekstrak fakta dengan leksikon emosi”* — ditolak: menyimpulkan keadaan batin dari tulisan pribadi dengan daftar kata adalah inferensi tanpa dasar, dan naskah 4 §7 menuntut keluaran asosiatif yang bisa dijelaskan. **(c)** *“Memori jurnal tidak disemat sampai pemilik memutuskan”* — ditolak: rancangan pemilik sudah menyemat jurnal (K-26); yang terbuka adalah enkripsinya. |
| **Harga yang diakui** | Memori **turunan** (`semantic`, `preference`) belum ada: tanpa model bahasa V0 hanya mengingat kejadian. Isi jurnal kini ada **dua kali** di basis data (jurnal + memorinya) — sama-sama di bawah RLS, retensi, dan hapus yang sama. Ini **bukan** ambang keyakinan untuk bertindak — itu [#34](../../issues/34), milik pemilik. |
| **Cara membalikkan** | `KEYAKINAN_LAPORAN_SENDIRI` · `VERSI_EKSTRAKSI` · `teks_mood` · `teks_jurnal` (`memory/ekstraksi.py`); `test_memori.py` diubah bersamanya. Berhenti mengingat jurnal: hapus `journal.created` dari `JENIS_EVENT` — memori yang sudah ada dihapus lewat migrasi. |

---

## K-28 · AI Gateway V0: rute tanpa model untuk perintah, penyedia lokal untuk sisanya

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.1 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Tiga rute, diputuskan pengenal niat **berbentuk aturan** sebelum model mana pun disentuh (`agents/niat.py`): **`deterministic`** — perintah berbentuk tetap dijalankan layanan biasa tanpa model (V0: *“catat mood 3 cemas”* → `checkins.catat_mood`, dengan `mood.logged`-nya); **`reasoning`** — permintaan analisis (pola · kenapa · evaluasi · rencana) atau pesan ≥ 40 kata; **`simple`** — selainnya. **(2)** Satu gerbang model di `platform` (`GerbangModel`, B-2): kelas → model `penyedia/nama` (`HVX_MODEL_SIMPLE` · `HVX_MODEL_REASONING`) → penyedia; tiap panggilan membawa pulang model · token masuk & keluar · latensi · **biaya** dari tabel harga `HVX_MODEL_HARGA` (USD per sejuta token). Model di luar penyedia `lokal` **tanpa harga ditolak** saat gerbang dirakit. **(3)** Penyedia V0 = **`lokal`**: tanpa jaringan, tanpa bobot model, deterministik — ia merangkai `bahan` (kalimat fakta yang disiapkan agent sesudah gerbang izin) dan **tidak menambah satu fakta pun**; tanpa bahan ia menjawab *belum ada data* (arch/08 Pasal 8). Token = kata, biaya 0 kecuali diberi harga. |
| **Bukti** | Naskah 5 §22 (`docs/92`): *“Catat mood saya” → cheap model / **deterministic*** — *mencatat mood adalah `INSERT`, bukan inferensi*; naskah 4 §48–§49: *jangan memakai model paling mahal untuk semua hal*. Penyedia LLM **milik pemilik** — tarif & bagi hasil, dan ke mana data pengguna boleh dikirim ([`../arch/05`](../arch/05-TECHNOLOGY-STACK.md) §6, A-6/[#18](../../issues/18), butir C). CI tanpa tagihan (**H-26**): uji tidak boleh memanggil layanan berbayar. |
| **Bacaan yang DITOLAK** | **(a)** *“Pasang API model berbayar sekarang, kuncinya menyusul”* — ditolak: memilih penyedia = memilih tarif **dan** mengirim isi percakapan pengguna ke pihak ketiga; keduanya bukan milik agent. **(b)** *“Model bobot-terbuka lokal (llama.cpp dsb.)”* — ditolak untuk V0: ratusan MB–GB bobot di citra, GPU/CPU di CI, dan tetap memutuskan model mana yang menjawab pengguna — alasan yang sama dengan K-26 (a). **(c)** *“Pengenal niat memakai model kecil”* — ditolak: memanggil model untuk memutuskan apakah perlu model menggagalkan tujuan rute itu (biaya, latensi), dan pengenal aturan bisa diuji kalimat demi kalimat. **(d)** *“Penyedia lokal mengarang jawaban bertemplat yang terdengar cerdas”* — ditolak: jawaban tanpa sumber adalah pelanggaran Pasal 8 yang sama persis dengan model yang berhalusinasi. |
| **Harga yang diakui** | ⚠️ **V0 tidak menalar.** Jawaban *reasoning* adalah daftar fakta yang dikumpulkan agent, bukan analisis bahasa; yang nyata adalah jalurnya — rute, pilihan model, token, biaya, aliran token — supaya penyedia sungguhan kelak masuk tanpa mengubah satu agent pun. Pengenal aturan salah menilai sebagian kalimat; salahnya diarahkan ke sisi yang murah (`simple`), dan `deterministic` hanya untuk perintah yang diawali kata perintahnya dengan valensi yang utuh. |
| **Cara membalikkan** | Penyedia baru: kelas di `platform/model.py` dengan `nama` = awalan id model, dipasang `gerbang_model_dari`; `HVX_MODEL_*` + `HVX_MODEL_HARGA`. Rute: `agents/niat.py`; `tests/unit/test_niat.py` diubah bersamanya. |

---

## K-29 · Katalog agent: manifest YAML di paket api, dibekukan migrasi, dibandingkan saat mulai

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.2 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Manifest agent dan tool registry spec/05 adalah YAML di paket api (`agents/manifest/`, `agents/alat/`, E-190), divalidasi **9 aturan spec/05 + A-1 + K-14** saat api dibuat — **semua** pelanggaran sekaligus; satu pelanggaran = api tidak bisa dibuat. **(2)** Katalog basis data (`agents` · `agent_tools`) diisi **migrasi** (`0007`) dengan salinan beku tiap manifest (`manifest jsonb` kanonik, `id = uuid5('nama@versi')`); api membandingkannya saat mulai dan **menolak mulai** bila berbeda — pagu, tool, versi, maupun isi manifest. **(3)** Manifest yang berubah = **versi baru + migrasi baru**; baris versi lama turun ke `deprecated` (satu aktif per nama, aturan 5 + `agents_one_active_idx`). |
| **Bukti** | spec/01 §10: `GRANT SELECT ON agents, agent_tools TO hvx_app` — *katalog sistem: dikelola migrasi*. `agent_runs.agent_id` menunjuk `agents(id)`, jadi katalog harus berbaris sebelum run pertama (4.4). Docstring pemeriksa A-1: *“validator manifest (Sprint 4 tugas 4.2) kelak memeriksa MANIFEST SUNGGUHAN dengan aturan yang sama”*. |
| **Bacaan yang DITOLAK** | **(a)** *“Api mendaftarkan manifestnya sendiri saat mulai (UPSERT)”* — ditolak: hak menulis katalog sistem berarti api yang disusupi bisa menaikkan `max_risk` agentnya sendiri; spec/01 §10 sengaja tidak memberikannya. **(b)** *“Katalog hanya di memori”* — ditolak: `agent_runs` butuh baris untuk dirujuk, dan audit butuh tahu **versi** mana yang bertindak. **(c)** *“Migrasi membaca YAML saat dijalankan”* — ditolak: migrasi yang isinya mengikuti berkas lain tidak menghasilkan hal yang sama bila diulang besok. **(d)** *“Berhenti di pelanggaran pertama”* — ditolak: aturan 9 (pihak ketiga meminta lokasi) tersembunyi di balik aturan 2 (scope di luar daftar resmi) selama `location` belum resmi. |
| **Harga yang diakui** | Manifest tertulis dua kali (YAML + migrasi) — dijaga uji kesamaan (`test_katalog_agent.py`) dan penolakan saat mulai, bukan ingatan. Menyunting manifest butuh migrasi, juga untuk perubahan kecil — sengaja: tiap versi manifest yang pernah bertindak tetap terbaca di `agents`. |
| **Cara membalikkan** | `agents.pastikan_katalog` (`hvx.main`) dan migrasi `0007`; `tests/integration/test_katalog_agent.py` diubah bersamanya. |

---

## K-30 · Program agent V0: jawaban dari fakta tool, keyakinan = banyaknya bukti

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.7 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** `coach-agent` membaca lima sumber lewat tool (habit hari ini · check-in hari ini · mood 7 hari · goal aktif · ingatan yang cocok) dan menyerahkan **kalimat fakta** dari sumber itu sebagai `bahan` AI Gateway — tidak ada kalimat lain. Sumber yang **ditolak** pengguna (`deny`) dilewati **dan dinyatakan** di `rationale`; sumber yang pengguna minta **ditanyakan** (`ask`) tidak dilewati — gilirannya ditahan gerbang. **(2)** **Keyakinan V0 = banyaknya bukti, bukan peluang yang dikalibrasi**: coach `0,10 · 0,35 · 0,50 · 0,65 · 0,75 · 0,85` untuk 0–5 sumber berisi; habit `0,95` judul persis · `0,80` judul yang memuat; memory `0,10 · 0,50 · 0,75` untuk 0 · 1 · ≥2 ingatan; hal yang dibaca/ditulis apa adanya `0,95`. Angka ini **dilaporkan**, tidak pernah dipakai memutuskan. **(3)** `habit-agent` menulis hanya bila **tepat satu** habit aktif cocok, dan tidak menulis tanggal yang sudah tercatat — balasannya mengatakan apa yang terjadi, bukan apa yang diminta. **(4)** `memory-agent` menulis ke `coaching_notes` hanya bila isinya belum diingat. |
| **Bukti** | Konstitusi Pasal 3 & 8 ([`../arch/08`](../arch/08-AGENT-CONTRACTS.md) §4): *tiap keluaran wajib `rationale` + `confidence`*; *dilarang mengarang data*. spec/04 SSE `done` memuat keduanya di **setiap** balasan. Ambang untuk bertindak atas keyakinan = [#34](../../issues/34), **milik pemilik** (butuh data nyata untuk dikalibrasi). |
| **Bacaan yang DITOLAK** | **(a)** *“Keyakinan tetap 0,7 untuk semua jawaban”* — ditolak: keyakinan yang tidak berubah dengan buktinya tidak memberi tahu pengguna apa pun, dan Confidence Layer (§19) kehilangan artinya sejak baris pertama. **(b)** *“Keyakinan dari model”* — ditolak: V0 tidak punya model yang menalar (K-28), dan keyakinan yang dilaporkan model atas dirinya sendiri tidak dikalibrasi. **(c)** *“Habit agent memilih judul yang paling mirip”* — ditolak: menebak berarti MENULIS sesuatu yang mungkin tidak dimaksud; bertanya murah. **(d)** *“Menjawab ‘ditandai’ karena tulisan tidak gagal”* — ditolak: `POST …/completions` mengembalikan baris LAMA untuk tanggal yang sudah tercatat (spec/04); balasan yang mengaku mengubahnya bohong. |
| **Harga yang diakui** | Keyakinan V0 bisa tinggi untuk jawaban yang faktanya banyak tetapi tidak relevan dengan pertanyaan — V0 tidak menilai relevansi. Habit agent tidak bisa MENGUBAH catatan yang sudah ada: tidak ada tool pembatalan di 9 tool V0. |
| **Cara membalikkan** | `agents/program_v0.py` (angka di satu tempat, `KEYAKINAN_*`); `tests/integration/test_agent_v0.py` diubah bersamanya. |

---

## K-31 · Aliran percakapan di dalam proses, satu giliran per percakapan

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.8 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** Token SSE mengalir lewat perantara **di dalam proses api** yang menjalankan gilirannya (`agents.AliranPercakapan`), bukan lewat Redis: token adalah kalimat untuk pengguna — isi, bukan rujukan. **(2)** Peristiwa satu giliran disimpan sampai giliran selesai **+ 60 dtk**, jadi klien yang menyambung sesudah `POST …/messages` menerima seluruhnya dari token pertama. **(3)** **Satu giliran per percakapan** — pesan kedua saat yang pertama berjalan → `409 turn_in_progress`. **(4)** Giliran agent berjalan di **tugas latar** proses itu; klien yang memutus SSE tidak membatalkannya — balasannya tetap tersimpan dan terbaca di `GET …/messages`. Api yang berhenti membatalkan giliran yang masih berjalan; run-nya ditutup `cancelled`. |
| **Bukti** | K-25: *stream Redis membawa rujukan, bukan isi*; spec/04: *`POST /messages` → 202, balasan lewat stream*. V0 = satu proses api (compose). |
| **Bacaan yang DITOLAK** | **(a)** *“Redis pub/sub untuk token”* — ditolak: isi percakapan pengguna di Redis `noeviction` bersama, dan pub/sub tidak menyimpan apa pun untuk klien yang tersambung terlambat. **(b)** *“Aliran dari `POST` itu sendiri”* — ditolak: spec/04 memisahkan keduanya, dan klien seluler yang putus di tengah `POST` kehilangan jawabannya sama sekali. **(c)** *“Klien yang putus membatalkan giliran”* — ditolak: tulisan yang sudah diizinkan pengguna berhenti di tengah hanya karena sinyal hilang. |
| **Harga yang diakui** | ⚠️ **Lebih dari satu proses api = klien bisa tersambung ke proses yang salah** dan menerima `204`; balasannya tetap bisa dibaca dari `GET …/messages`. Run yang terputus karena proses MATI (bukan berhenti) tetap `running` — tidak ada penyapu lintas pengguna di V0. |
| **Cara membalikkan** | `agents/aliran.py` di belakang antarmuka yang sama (`mulai` · `kirim` · `ikuti`); rute tidak berubah. |

---

## Yang sengaja **tidak** saya putuskan

| Butir | Kenapa |
|---|---|
| ~~[#139](../../issues/139) Master Architecture v2.0~~ | ✅ **pemilik memerintahkannya 10 Sep 2026** (*“kerjakan semua tugas dan fase yang masih tersisa”*) — dikerjakan, hasilnya [`../arch/`](../arch/README.md) |
| ~~[#3](../../issues/3) siapa mengerjakan V0~~ | ✅ **pemilik memutuskannya 16 Sep 2026** — AI coding agent di branch + PR, pemilik yang menggabungkan (**H-25**). Yang tetap bukan milik saya: **waktu** pemilik untuk meninjau |
| [#20](../../issues/20) cek merek & domain | menuntut pencarian merek dan pembelian |
| **seluruh butir C** (hukum & privasi) | risikonya ditanggung orang yang tidak ikut memilih |
| §16.5 · §16.7 rantai humanoid | benda yang bisa melukai orang — gerbangnya bukan keputusan gaya |
| [#4](../../issues/4) Mental Wellness | cakupan produk |
| [#34](../../issues/34) ambang Confidence | butuh data nyata untuk dikalibrasi; menebak angkanya lebih buruk daripada membiarkannya terbuka |

💡 **Aturan yang saya pakai untuk memilah:** *kalau salahnya keputusan ini
ditanggung orang lain — pengguna, penerima pesan, atau pemilik uangnya —
keputusan itu bukan milik saya.*
