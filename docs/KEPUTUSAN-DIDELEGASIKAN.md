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

⇒ **Nol butir C saya putuskan sendiri.** Semuanya menyangkut orang yang tidak ikut
memilih. 🔧 **Satu pengecualian, atas delegasi pemilik 7 Okt 2026 (H-28):** C-31 · C-32 ·
C-34 — **K-46**. Delegasi itu tidak meluas ke butir C lain.

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
| **Harga yang diakui** | ⚠️ **V0 tidak menalar.** Jawaban *reasoning* adalah daftar fakta yang dikumpulkan agent, bukan analisis bahasa; yang nyata adalah jalurnya — rute, pilihan model, token, biaya, aliran token — supaya penyedia sungguhan kelak masuk tanpa mengubah satu agent pun. Pengenal aturan salah menilai sebagian kalimat; salahnya diarahkan ke sisi yang murah (`simple`), dan `deterministic` hanya untuk perintah yang diawali kata perintahnya dengan valensi yang utuh — 🔧 kata perintahnya WAJIB sejak tinjauan kontrak Sprint 4 (E-198: *“mood 3 hari lalu buruk”* dulu tercatat sebagai mood baru). 🔧 **Pengenal aturan ada di event loop** — tiap pola wajib linear atas pesan terpanjang yang sah (E-197: satu pesan 4.000 karakter pernah membekukan proses api 75 detik). ⚠️ **`bahan` memuat tulisan pengguna** (judul habit & goal, isi ingatan) apa adanya: penyedia lokal V0 tidak menalar dan tidak memilih tool, jadi tidak bisa diperintah lewat bahannya — penyedia sungguhan **bisa** (*prompt injection* tersimpan, tinjauan keamanan Sprint 4). Saat penyedia sungguhan masuk: bahan diperlakukan sebagai DATA berpembatas, dan pemanggilan tool yang ditulis model tetap lewat pelaksana + gerbang yang sama — yang sudah menolak tanpa koersi (E-170, E-204). |
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
| 🔧 **Ditambahkan 28 Sep 2026** | (tinjauan kontrak sebelum PR, E-209) Yang dibandingkan saat mulai kini juga **aksi tiap tool** (`agent_tools.permission` = `read` · `write` · `execute` menurut `kind`, `agents.AKSI_IZIN` — yang ditanyakan gerbang): migrasi `0007` memakai bawaan kolom `execute` untuk semuanya, dibetulkan migrasi `0009`. Tool registry sendiri (risiko, scope, skema) adalah **kode** — berubah lewat PR dan ujinya, bukan lewat katalog basis data, yang hanya mencatat tool mana milik agent mana dan aksinya. |

---

## K-30 · Program agent V0: jawaban dari fakta tool, keyakinan = banyaknya bukti

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.7 ditulis.

| | |
|---|---|
| **Keputusan** | **(1)** `coach-agent` membaca lima sumber lewat tool (habit hari ini · check-in hari ini · mood 7 hari · goal aktif · ingatan yang cocok) dan menyerahkan **kalimat fakta** dari sumber itu sebagai `bahan` AI Gateway — tidak ada kalimat lain. Sumber yang **ditolak** pengguna (`deny`) dilewati **dan dinyatakan** di `rationale`; sumber yang pengguna minta **ditanyakan** (`ask`) tidak dilewati — gilirannya ditahan gerbang. 🔧 **Kecuali scope ingatan** (tinjauan kontrak Sprint 4, E-208): `memory.search` menyaring izinnya sendiri dan tidak menahan jawaban (E-193), jadi scope *“tanya aku”*-nya **dinyatakan** di `rationale` (*“ingatan yang belum kamu izinkan kubaca: …”*), tidak ditanyakan — dulu coach diam saja, dan alasannya malah berbunyi *“belum ada … ingatan yang tercatat”*. **(2)** **Keyakinan V0 = banyaknya bukti, bukan peluang yang dikalibrasi**: coach `0,10 · 0,35 · 0,50 · 0,65 · 0,75 · 0,85` untuk 0–5 sumber berisi; habit `0,95` judul persis · `0,80` judul yang memuat; memory `0,10 · 0,50 · 0,75` untuk 0 · 1 · ≥2 ingatan; hal yang dibaca/ditulis apa adanya `0,95`. Angka ini **dilaporkan**, tidak pernah dipakai memutuskan. **(3)** `habit-agent` menulis hanya bila **tepat satu** habit aktif cocok, dan tidak menulis tanggal yang sudah tercatat — balasannya mengatakan apa yang terjadi, bukan apa yang diminta. **(4)** `memory-agent` menulis ke `coaching_notes` hanya bila isinya belum diingat. |
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
| **Cara membalikkan** | `agents/aliran.py` di belakang antarmuka yang sama (`mulai` · `kirim` · `ikuti` · `urungkan`); rute tidak berubah. |
| 🔧 **Ditambahkan 28 Sep 2026** | (tinjauan keamanan & kontrak sebelum PR) **(a)** *Satu giliran per percakapan* juga hanya **per proses** — dua proses api bisa menjalankan dua giliran di satu percakapan; harga yang sama dengan (1), dan keduanya diangkat bersama. **(b)** Permintaan yang ditolak sebelum apa pun tercatat (`409` · `422`) **di-`urungkan`** — aliran kembali ke giliran sebelumnya (E-202). |

---

## K-32 · Anggaran biaya model: per pengguna per 24 jam bergulir, jatah dipesan dari `agent_runs`

> Diputuskan 24 September 2026, saat Sprint 4 tugas 4.9 ditulis. 🔧 **Diubah 28 September
> 2026** (tinjauan keamanan sebelum PR, **E-201**) — dua cara melewati anggaran yang
> versi pertama biarkan terbuka: pengguna menggeser **hari lokal**nya lewat zona waktu
> profil (anggaran harian menjadi per jam), dan **giliran serentak** di percakapan lain
> tidak melihat biaya satu sama lain (empat giliran, empat panggilan besar, anggaran
> untuk satu).

| | |
|---|---|
| **Keputusan** | **(1)** Sebelum TIAP panggilan model, di bawah **kunci anggaran per pengguna** (`pg_advisory_xact_lock`), runtime menjumlahkan `cost_usd` run pengguna yang dimulai dalam **24 jam terakhir** — yang sudah ditutup (biaya akhirnya) **dan** yang masih berjalan (biaya sejauh ini + jatah panggilan yang sedang berjalan). Bila jumlah itu sudah ≥ `HVX_AI_ANGGARAN_HARIAN_USD`, atau jumlah itu ditambah **perkiraan TERBURUK** panggilan ini (token masuk + `maks_token` keluar, harga kelasnya) melewatinya, kelas model **diturunkan** ke `simple` — jawaban tetap ada, tidak ada galat. **(2)** **Jatah dipesan**: perkiraan kelas yang dipakai ditulis ke `cost_usd` run ini SEBELUM kunci dilepas, lalu diganti biaya sebenarnya sesudah panggilan (penutup run menulis biaya akhirnya apa pun yang terjadi). **(3)** Turun kelas tercatat: `model_used` memuat model yang benar-benar menjawab, dan `decision.model_downgraded = true`. **(4)** Bawaan **0,50 USD** per pengguna per 24 jam — longgar, dan penyedia lokal V0 gratis; **angka sebenarnya milik pemilik** (uang, A-6/#18). |
| **Bukti** | spec/07 4.9: *melewati batas → turun ke model kecil, bukan gagal*; *4.9 sering dilupakan sampai tagihan pertama datang … yang penting jalurnya ada sejak awal*. arch/04 §3: anggaran diikat pada jejak — `agent_runs` adalah jejak yang sama dengan audit. Tinjauan keamanan Sprint 4: `PATCH /v1/me/profile` mengganti zona waktu kapan saja; zona dengan tengah malam yang baru lewat selalu ada (UTC−12 … UTC+14). |
| **Bacaan yang DITOLAK** | **(a)** *“Penghitung biaya di Redis”* — ditolak: satu lagi angka yang bisa menyimpang dari jejak audit, dan hilang bila Redis dikosongkan. **(b)** *“Hari UTC”* — ditolak: pengguna di Jakarta akan mendapat anggaran baru pukul 07.00. **(c)** *“Tolak permintaan saat anggaran habis”* — ditolak oleh spec/07 sendiri. **(d)** *“Hanya biaya run yang sudah ditutup”* — ditolak: satu giliran dengan beberapa panggilan akan melewati anggaran tanpa satu pun terlihat. **(e)** 🔧 *“Hari lokal pengguna”* (versi pertama keputusan ini) — ditolak sesudah tinjauan: batas harinya bisa digeser pemiliknya sendiri. **(f)** 🔧 *“Kunci per pengguna sepanjang panggilan model”* — ditolak: semua percakapan satu pengguna menunggu satu aliran selesai; jatah yang dipesan memberi hasil yang sama tanpa antrean. |
| **Harga yang diakui** | Model kecil pun berbayar bila diberi harga — anggaran yang habis memperlambat tagihan, tidak menghentikannya. Jatah TERBURUK lebih ketat daripada biaya yang biasanya terjadi: sisa anggaran yang cukup untuk jawaban pendek tetapi tidak untuk `maks_token`-nya sudah turun kelas. Anggaran tidak lagi "baru" tiap tengah malam — pulih sedikit demi sedikit, 24 jam sesudah tiap biaya. Run yang prosesnya MATI memegang jatahnya sampai 24 jam lewat (K-31). Dua transaksi tambahan per panggilan model. |
| **Cara membalikkan** | `RuntimeAgent.pesan_model` · `lunasi_model` · `JENDELA_ANGGARAN` · `GerbangModel.perkiraan_biaya` · `HVX_AI_ANGGARAN_HARIAN_USD`; `tests/integration/test_anggaran.py` diubah bersamanya. |

---

## K-33 · Behavior projector: konvergen dari `events`, id deterministik, dibangun ulang per pengguna

> Direncanakan 1 Oktober 2026 ([`SESSION-LOG.md`](SESSION-LOG.md) Sesi 35), dikodekan 2 Oktober
> 2026 saat Sprint 5 tugas 5.1 ditulis (`ea89c68`). Ditulis di berkas ini 8 Oktober 2026 dari
> kodenya — yang tercatat di sini bentuk yang **dikodekan**, bukan rencananya.

| | |
|---|---|
| **Keputusan** | **(1)** Projector adalah konsumen **wajib** atas **semua** jenis event (spec/03 *Consumer V0*) di `hvx.pekerja`. V0 baru memproyeksikan siklus penyelesaian habit: `habit.completed` → satu baris `activities` ber-`source='inferred'`; jenis lain ditelan tanpa efek, jadi proyeksi baru kelak tidak mengubah perkabelan pekerja. **(2)** `id` baris proyeksi **deterministik** — `uuid5` dari penyelesaian sumbernya — dan tulisannya `ON CONFLICT DO NOTHING`, hanya atas baris `inferred` (`activities.catat_proyeksi` · `hapus_proyeksi` · `kosongkan_proyeksi`). **(3)** **Konvergen, bukan sisip/hapus menurut urutan tiba:** tiap event habit menghitung keadaan AKHIR penyelesaian itu dari `events` — ada `habit.completed` dan tak ada `habit.completion_retracted` → barisnya ada; selain itu → tidak ada. **(4)** `bangun_ulang_proyeksi(engine, user_id)` mengosongkan proyeksi seorang pengguna lalu memutar ulang seluruh event-nya dalam **satu transaksi** — tidak ada jendela saat proyeksinya kosong. **(5)** `intelligence` memanggil pintu keluar `events` (`untuk_proyeksi` · `cari_penyelesaian`, di bawah RLS pemiliknya, tanpa `SECURITY DEFINER`) dan `activities` langsung — lapisannya di atas keduanya (M-1). |
| **Bukti** | spec/07 5.1: *“proyeksi bisa dibangun ulang dari nol dan hasilnya sama”*; spec/02 aturan D: `events` adalah sumber kebenaran; naskah 4 §5 *Behavior Engine*. Uji: `test_proyektor.py` — `test_bangun_ulang_dari_nol_identik_dan_tanpa_duplikat` · `test_cabut_sesudah_proyeksi_menghapusnya_dan_putar_ulang_tak_menghidupkannya` · `test_pekerja_memproyeksikan_habit_selesai_menjadi_aktivitas_inferred`. |
| **🔧 8 Okt 2026** | Projector dan Habit streak dipasang **`wajib=True`** — kegagalannya menahan event, tidak membuangnya ke stream mati sesudah 5 kali (**E-240**, `spec/03`). Hapus `habits`/`history` membawa proyeksinya (**E-232**). |
| **Bacaan yang DITOLAK** | **(a)** *“Sisip saat `completed`, hapus saat `retracted`”* — ditolak: `completed` yang disalurkan ulang SESUDAH `retracted` (celah ACK stream, K-25) menghidupkan kembali penyelesaian yang sudah dicabut. **(b)** *“Id acak per baris proyeksi”* — ditolak: penyaluran ulang stream dan pemutaran ulang akan melahirkan baris kedua. |
| **Harga yang diakui** | Tiap event habit membaca riwayat penyelesaian itu dari `events` — lebih mahal daripada sisip buta, sengaja. Pemutaran ulang memegang seluruh riwayat seorang pengguna dalam satu transaksi. V0 hanya punya satu lajur `inferred` (penyelesaian habit). |
| **Cara membalikkan** | `intelligence/proyektor.py` + pintu keluar `activities` · `events`; `tests/integration/test_proyektor.py` diubah bersamanya. |

---

## K-34 · Pola perilaku V0: tiga pola habit sebagai memori `behavioral`, asosiatif, diluruhkan bukan dihapus

> Direncanakan 1 Oktober 2026 (Sesi 35), dikodekan 2 Oktober 2026 saat Sprint 5 tugas 5.2
> ditulis (`0e8d623`).

| | |
|---|---|
| **Keputusan** | **(1)** Tiga pola per habit, dihitung dari penyelesaian yang HIDUP (tidak dicabut): **hari-dalam-minggu** (dari `for_date`), **bagian hari** penyelesaian itu **dicatat** (jam `occurred_at` di zona profil: pagi 05–11 · siang 11–15 · sore 15–19 · malam) — waktu catat, bukan waktu laku — dan **konsistensi 30 hari + rentetan** (`habits.rentetan_pada`, satu sumber logika rentetan bagi tool dan pola). **(2)** Ditulis sebagai `memories(kind='behavioral', scope='habits')` lewat `memory.catat_pola` — tanpa tabel baru. **(3)** `confidence` = keterpusatan pola (bagian penyelesaian pada nilai terbanyak; untuk konsistensi = `completion_rate_30d`), `evidence_count` = banyaknya penyelesaian; keduanya disimpan apa adanya. **(4)** Kalimatnya **asosiatif** — *“paling sering … pada …”* — dan `tanpa_klaim_kausal` menolak kata sebab (*menyebabkan · penyebab · sebab · karena · akibat · mengakibatkan · memicu · membuat*). **(5)** Id memori deterministik per (pengguna, habit, jenis pola): menghitung ulang **menguatkan** baris yang sama (upsert). Nol penyelesaian, atau habitnya dihapus → pola **diluruhkan** (`valid_until = now()`, `memory.luruhkan_pola`), bukan dihapus. **(6)** Pemicu: grup konsumen `pola` atas `habit.completed` · `habit.skipped` · `habit.completion_retracted`. |
| **Bukti** | spec/07 5.2: *“keluarannya asosiatif, bukan kausal”* (naskah 4 §7, docs/54); naskah 4 §6 *Behavioral Pattern Mining*; Confidence Layer §19. Uji: `test_pola.py::test_pekerja_menulis_pola_lalu_meluruhkannya` · `test_pola_murni.py`. |
| **Bacaan yang DITOLAK** | **(a)** *“Pola sebagai tabel sendiri”* — ditolak: `memories` sudah membawa `confidence` + `evidence_count` per baris dan sudah disaring scope di pencarian (3.7). **(b)** *“Menghapus pola yang kehilangan dasarnya”* — ditolak: *“dulu begini”* tetap sejarah; meluruhkan menyimpan kapan pola berhenti berlaku. **(c)** *“Pola hanya dinyatakan di atas ambang keyakinan”* — ditolak di sini: ambang di atas nol milik pemilik ([#34](../../issues/34)); yang ditegakkan hanya aturan keras nol bukti (5.4, `intelligence.keyakinan`). |
| **Harga yang diakui** | *Bagian hari* memakai waktu **catat**, bukan waktu kebiasaan itu dilakukan — penyelesaian yang dicatat belakangan menggeser polanya. Pemeriksa kata sebab berbasis daftar kata — penjaga kalimat sistem sendiri, bukan pemahaman bahasa. |
| **Cara membalikkan** | `intelligence/pola.py` · `memory/perilaku.py`; `tests/integration/test_pola.py` · `tests/unit/test_pola_murni.py` diubah bersamanya. |

---

## K-35 · `human_states` harian dari check-in: laporan sendiri, satu bukti per hari, tanggal check-in

> Direncanakan 1 Oktober 2026 (Sesi 35), dikodekan 2 Oktober 2026 saat Sprint 5 tugas 5.3
> ditulis (`9cf78ef`).

| | |
|---|---|
| **Keputusan** | **(1)** Konsumen `checkin.logged` menghitung metrik dari check-in **otoritatif** (`checkins.checkin_pada`), bukan dari payload event. **(2)** Metrik V0: `energy` dan `focus` — masing-masing `{value, confidence, evidence_count}`: `value` = skala 1–5 dinormalkan ke 0–1 (`(x−1)/4`), `confidence` = **1,0** (laporan pengguna sendiri, bukan taksiran — sejalan `memory.KEYAKINAN_LAPORAN_SENDIRI`), `evidence_count` = **1** (satu check-in = satu bukti untuk hari itu). Jam tidur tidak menjadi metrik. **(3)** `for_date` = **tanggal check-in itu** — tanggal lokal yang dilaporkan perangkat — bukan tanggal menurut zona profil, bukan UTC. **(4)** Ditulis lewat pintu keluar baru `profile.simpan_human_state` (tabel milik `profile`, spec/06), yang **menolak** metrik tanpa tepat tiga medan itu; upsert per (pengguna, `for_date`, `model_version='human-state@v1'`) — dua versi model boleh hidup berdampingan (§23). **(5)** Check-in tanpa energi dan fokus → tidak ada metrik → **tidak ada baris**. |
| **Bukti** | spec/07 5.3: *“tiap metrik punya `value`, `confidence`, `evidence_count`”*; spec/01 §6 (`metrics jsonb`); spec/06 kepemilikan tabel. Uji: `test_human_state.py::test_pekerja_menghitung_human_state_dari_checkin_lalu_memperbaruinya` · `test_human_state_murni.py`. |
| **🔧 8 Okt 2026** | Check-in yang **diganti** tanpa energi & fokus menghapus `human_states` hari itu (`profile.hapus_human_state`) — tidak meninggalkan keadaan lama (**E-236**). |
| **Bacaan yang DITOLAK** | **(a)** *“Hitung dari payload event”* — ditolak: payload bisa basi (penyaluran ulang sesudah `PUT` yang lebih baru); dari baris otoritatif, hasilnya konvergen. **(b)** *“Tanggal menurut zona profil atau UTC”* — ditolak: hari yang pengguna laporkan adalah hari yang dimaksudnya, dan zona profil bisa diganti kapan saja (lihat K-32). **(c)** *“Tren berjendela beberapa hari”* — bukan V0: menyatukan hari menjadi tren, dan keyakinan yang tumbuh bersama buktinya, dikerjakan sesudah V0. |
| **Harga yang diakui** | Human State V0 adalah keadaan **per hari**, bukan tren. `confidence` 1,0 hanya berarti *“ini laporanmu sendiri”* — tidak berkata apa pun tentang ketepatannya. |
| **Cara membalikkan** | `intelligence/keadaan.py` (`MODEL`, `metrik_harian`) · `profile.simpan_human_state`; `tests/integration/test_human_state.py` diubah bersamanya. |

---

## K-36 · Mesin rekomendasi: skor sistem dari sinyal V0, terpisah dari saran agent

> Direncanakan 1 Oktober 2026 (Sesi 35), dikodekan 5 Oktober 2026 saat Sprint 5 tugas 5.5
> ditulis (`4ec7114`).

| | |
|---|---|
| **Keputusan** | **(1)** Grup konsumen `rekomendasi` atas `habit.skipped` dan `checkin.logged` (spec/03 *Recommendation trigger* — boleh gagal, diulang). **(2)** `habit.skipped` → **satu** rekomendasi *“Kembali ke ‘…’”* (domain & subjek `habit`) untuk habit yang dilewati; isinya menyarankan versi lebih ringan menurut tier energi hari itu (K-23), atau *“coba lagi besok”*. **(3)** `score` 0–1 = rata-rata komponen **bobot sama** (K-38); `score_breakdown` membawa tiap komponen + `"weights":"equal"`; `scoring_version='v1'`; `rationale` terisi (penyelesaian 30 hari, energi, *“dilewati hari itu”*); `context_snapshot` menyimpan komponennya. **`confidence` dibiarkan kosong** — skor mesin bukan keyakinan agent. **(4)** Idempoten: `id` = `uuid5` per (habit, tanggal) + `ON CONFLICT DO NOTHING` — event yang disalurkan ulang tidak menumpuk baris, dan status yang sudah diubah pengguna tidak pernah tertimpa. **(5)** `checkin.logged` **menyegarkan** komponen `context` rekomendasi mesin yang masih `pending` untuk tanggal itu — `history` dari snapshot dipertahankan, energi terakhir menang. **(6)** `recommendation.create` (tool coach, 4.3) tetap jalur terpisah: agent memasok `confidence` + `rationale`-nya sendiri, `score` kosong. |
| **Bukti** | spec/07 5.5: *“skor 0–1, `scoring_version`, `rationale` terisi”*; docs/87 §11: *“semua recommendation harus melewati scoring”*, contohnya rata-rata lima komponen; spec/01 §7. Uji: `test_rekomendasi.py::test_pekerja_menyekor_rekomendasi_dari_skip_lalu_menyegarkannya_dari_checkin` (memuat asersi *“skor mesin bukan confidence agent (K-36)”*) · `test_mesin_rekomendasi.py`. |
| **🔧 8 Okt 2026** | Penyegaran membaca check-in **otoritatif** (`checkins.checkin_pada`), bukan payload event — urutan tiba tidak memutar skor mundur (**E-237**); dan menulis ulang `rationale` + saran tier bersama skornya (**E-238**). `GET /recommendations` berkursor (**E-239**). |
| **Bacaan yang DITOLAK** | **(a)** *“Agent mengisi skor”* — ditolak: skor adalah keluaran mesin, bukan angka yang dikarang agent (Pasal 8, K-30). **(b)** *“Satu rekomendasi baru per event”* — ditolak: penyaluran ulang stream menumpuk saran yang sama. **(c)** *“Check-in menghitung ulang semua rekomendasi”* — ditolak: rekomendasi yang sudah dilihat atau diputuskan pengguna tidak diganggu; hanya `pending`. |
| **Harga yang diakui** | V0 punya **satu** jenis rekomendasi mesin (kembali ke habit yang dilewati). Bobot sama adalah titik awal tanpa kalibrasi — `scoring_version` membuat rumus boleh berganti tanpa migrasi. |
| **Cara membalikkan** | `intelligence/mesin.py` (`SKOR_VERSI`, `nilai_rekomendasi`); `tests/integration/test_rekomendasi.py` · `tests/unit/test_mesin_rekomendasi.py` diubah bersamanya. |

---

## K-37 · Umpan balik rekomendasi: hanya-tambah, dan status berubah hanya untuk `accepted`/`rejected`

> Direncanakan 1 Oktober 2026 (Sesi 35), dikodekan 5 Oktober 2026 saat Sprint 5 tugas 5.6
> ditulis (`d025832`).

| | |
|---|---|
| **Keputusan** | **(1)** `POST /v1/recommendations/{id}/feedback {action, reason?, outcome?}` menambah satu baris `recommendation_feedback` (hanya-tambah) **dan** menyesuaikan `recommendations.status` dalam **satu transaksi**. **(2)** Peta status: `accepted` → `accepted` · `rejected` → `rejected` · `modified` · `snoozed` · `ignored` → **status tidak disentuh** — umpan baliknya tercatat sebagai bukti, rekomendasinya tetap bisa diterima nanti. **(3)** Berjalur `Idempotency-Key` (E-165): kunci yang sama tidak melahirkan umpan balik kedua. **(4)** Rekomendasi milik orang lain tak terlihat di bawah RLS → `404 recommendation_not_found`, tanpa menulis apa pun. **(5)** `reason` ≤ 2.000 karakter tanpa NUL; `outcome` objek ≤ 4.000 byte tanpa NUL bersarang. |
| **Bukti** | spec/07 5.6: *“`modified` dan `snoozed` tidak dihitung sebagai penolakan”*; naskah 4 §24; spec/01 §7. Uji: `test_umpan_balik.py` — `test_accepted_dan_rejected_mengubah_status` · `test_modified_snoozed_ignored_bukan_penolakan` · `test_idempotency_key_tidak_melahirkan_umpan_balik_kedua` · `test_umpan_balik_append_only_banyak_baris` · `test_rekomendasi_tak_dikenal_404_tanpa_menulis` · `test_tak_bisa_umpan_balik_rekomendasi_pengguna_lain`. |
| **Bacaan yang DITOLAK** | **(a)** *“`modified`/`snoozed` = `rejected`”* — ditolak oleh spec/07 sendiri: memilih B setelah disarankan A bukan penolakan, menunda bukan mengabaikan. **(b)** *“Status saja, tanpa riwayat umpan balik”* — ditolak: umpan balik berulang atas satu rekomendasi adalah bukti yang dibutuhkan evaluasi kelak; baris hanya-tambah menyimpannya. |
| **Harga yang diakui** | `ignored` tidak mengubah status — rekomendasi yang diabaikan tetap `pending`/`shown` sampai pengguna menerima atau menolaknya. |
| **Cara membalikkan** | `intelligence/umpan_balik.py` (`_STATUS_BARU`); `tests/integration/test_umpan_balik.py` diubah bersamanya. |

---

## K-38 · Komponen skor V0: `history` + `context`; nol komponen → tidak ada rekomendasi

> Diputuskan 5 Oktober 2026, bersama K-36 (Sprint 5 tugas 5.5, `4ec7114`).

| | |
|---|---|
| **Keputusan** | **(1)** Dua komponen — satu-satunya yang V0 punya datanya: **`history`** = `completion_rate_30d` habit itu (rentetan 2.4; padanan *Historical Success* docs/87) dan **`context`** = energi check-in hari itu, dinormalkan 1–5 → 0–1 seperti 5.3 (padanan *Context Fit*). **(2)** Komponen tanpa data **dilewati**, bukan diisi nol; skor = rata-rata komponen yang ada. **(3)** **Nol komponen → tidak ada skor → tidak ada rekomendasi** (`nilai_rekomendasi` → `None`, `cukup_untuk_menyatakan` — Confidence Layer 5.4). |
| **Bukti** | docs/87: *Trend Relevance · Personal Preference · Context Fit · Historical Success · Weather Fit · Occasion Fit · Availability*, contohnya dirata-rata sama berat; lima sisanya tidak punya data di V0, dan mengarangnya dilarang (Pasal 8). Uji: `test_mesin_rekomendasi.py` — `test_tanpa_komponen_none` · `test_satu_komponen_skor_komponen_itu` · `test_rata_rata_bobot_sama` · `test_skor_selalu_0_sampai_1`. |
| **Bacaan yang DITOLAK** | **(a)** *“Komponen tanpa data = 0”* — ditolak: ketiadaan data akan terbaca sebagai nilai buruk dan menarik skor turun. **(b)** *“Komponen lain diisi taksiran”* — ditolak: tidak ada sinyalnya di V0 (Pasal 8). |
| **Harga yang diakui** | Rekomendasi dengan satu komponen berskor sama dengan komponen itu — skornya tidak membawa tanda seberapa sedikit dasarnya, kecuali lewat `score_breakdown`. |
| **Cara membalikkan** | `intelligence/mesin.py` (`_rekomendasi_habit`, `nilai_rekomendasi`); naikkan `scoring_version` bila komponennya berubah. |

---

## K-39 · Sapuan hapus akun: proses pekerja lewat tiga fungsi sempit, Qdrant dibuang selagi akun terkunci

> Diputuskan 6 Oktober 2026, saat 6.5 Stage B ditulis. (K-33 … K-38 — Sprint 5 — semula hanya
> dirujuk kode dan [`SESSION-LOG.md`](SESSION-LOG.md) Sesi 35; 🔧 ditulis di atas pada 8 Oktober 2026.)
>
> Yang dipertanyakan: spec/01 *Prosedur hapus akun* menyebut tahap 3–6 dijalankan *“peran
> pemeliharaan (bukan api)”* tanpa bentuk — peran login baru? alat `tools/` dengan kredensial
> pemilik skema? proses yang sudah ada? Dan `hvx_app` sengaja tidak punya `DELETE` atas `users`
> (spec/01 §10). **Bukan** yang dipertanyakan: tenggang 30 hari, enam tahap, dan bahwa jejak audit
> dipertahankan — itu spec dan keputusan pemilik.

| | |
|---|---|
| **Keputusan** | **(1)** Tahap 3–6 dikerjakan **proses pekerja** (`hvx.pekerja`, anggota `hvx_pekerja`), tiap lima menit, lewat **tiga fungsi `SECURITY DEFINER`** (spec/01 §12): `akun_jatuh_tempo` (siapa) · `kunci_akun_jatuh_tempo` (kunci baris, periksa ulang) · `hapus_akun_jatuh_tempo` (tahap 5 · 3 · 6 satu transaksi). **Masing-masing menolak akun yang bukan `pending_deletion` dengan tenggang habis** — penegakannya di basis data, bukan di kode sapuan. **(2)** Urutan: kunci (`FOR NO KEY UPDATE`) → **tahap 4**, titik Qdrant dibuang menurut saringan `user_id` **selagi terkunci** → fungsi hapus → sesi dan jejak idempotensi Redis dibuang sesudah commit. Gagal sebelum commit membatalkan semuanya; akunnya masih jatuh tempo dan diulang. **(3)** Jejak audit dialihkan ke **id semu = HMAC-SHA256 berkunci** (`HVX_IP_HASH_KEY`, label `akun-terhapus`, 128 bit) di `user_id`, `actor_id`, `subject_id`, dan teks `metadata`; satu baris `account.deleted` menutupnya. **(4)** `POST /me/restore` hanya selama `deletion_scheduled_at > now()`; sesudahnya `409 deletion_grace_expired`. **(5)** Penyelaras vektor melewati akun `pending_deletion`. **(6)** Tanpa Qdrant terpasang di pekerja, akun yang pernah punya titik **ditunda**, bukan dihapus. **(7)** Asisten berhenti melayani akun `pending_deletion` di pintu giliran (`kirim`, `jawab` → `403 account_pending_deletion`). |
| **Bukti** | spec/01: *“Tahap 4 adalah jebakan paling mudah terlewat: Qdrant tidak ikut cascade”* dan *“kumpulkan `embedding_id` lebih dulu, atau titik memori pengguna akan tertinggal selamanya”*; spec/01 §10: *`DELETE` pada `users` … dijalankan peran pemeliharaan, bukan aplikasi*; pemilik 5 Okt 2026 (Stage A): login `pending_deletion` diizinkan, kolom jadwal tersendiri. `audit()` menulis `str(user_id)` ke `actor_id` pada tiap aksi pengguna — menganonimkan `user_id` saja (bunyi tahap 5) meninggalkan id asli di sana (**E-215**). |
| **🔧 8 Okt 2026** | Token segar atau sesi lama sesudah sapuan tidak lagi menulis jejak atas id asli — penulisnya memegang baris akun `FOR KEY SHARE` (**E-235**). Restore akun `suspended`/terhapus → `403 account_not_active` (**E-245**). Kunci Redis lain milik akun terhapus hidup sampai TTL — **C-38** (pemilik). |
| **Bacaan yang DITOLAK** | **(a)** *“Alat `tools/` memakai kredensial pemilik skema”* — ditolak: kredensial yang melewati RLS dan semua hak hidup panjang di proses terjadwal; tiga fungsi yang menolak akun belum jatuh tempo memberi batas sekecil itu tanpa kredensial baru. **(b)** *“Peran login ketiga (`hvx_pemeliharaan`)”* — ditolak: permukaan baru (compose, `peran-lokal.sql`, `pastikan_peran_aplikasi`) untuk kerja yang sudah punya rumah di pekerja. **(c)** *“Hapus baris dulu, Qdrant sesudah commit”* — ditolak: gagal di antaranya meninggalkan titik tanpa pemilik yang tak bisa lagi dicari (`user_id`-nya sudah tiada; menyimpan daftarnya butuh tabel ke-24). **(d)** *“Kunci `FOR UPDATE`”* — ditolak: foreign key tulisan anak mengambil `FOR KEY SHARE`, jadi penulis anak ikut menunggu Qdrant. **(e)** *“Hash polos id akun sebagai id semu”* — ditolak: id yang pernah terlihat (cadangan, log lama) langsung cocok lagi. **(f)** *“Restore tanpa batas”* (Stage A) — ditolak: akun yang dipulihkan sesudah titiknya dibuang hidup kembali tanpa vektor memorinya, diam-diam (**E-216**). |
| **Harga yang diakui** | ⚠️ Baris akun terkunci selama panggilan Qdrant (batas waktu 5 dtk): login atau restore pada akun yang sedang disapu menunggu sebanyak itu. Akun jatuh tempo dihapus ≤ 5 menit sesudah waktunya. Sapuan tanpa Qdrant menunda akun bertitik **tanpa batas** (peringatan di log) — dipilih daripada titik tanpa pemilik. Satu akun yang terus gagal tidak menahan yang lain, tetapi mengulang galatnya tiap lima menit. Pembersihan Redis sesudah commit boleh gagal tanpa bisa diulang (akunnya sudah tiada; jejaknya mati sendiri dalam 24 jam). Rujukan stream tidak dibuang per akun. `ip_hash` baris audit tidak diubah (**C-34**). |
| **Cara membalikkan** | `identity/penghapusan.py` · migrasi 0011 · `pekerja.JEDA_SAPUAN_HAPUS_S`; `tests/integration/test_sapuan_hapus_akun.py` dan 20 mutasi `6.5b` diubah bersamanya. |
| 🔧 **Diubah 7 Okt 2026** | (6.4, **K-46**) **C-34** diputuskan atas delegasi pemilik: `hapus_akun_jatuh_tempo` kini juga mengosongkan `ip_hash` baris audit akun yang dihapus (migrasi 0013) — kalimat *“`ip_hash` baris audit tidak diubah”* di *Harga yang diakui* tidak berlaku lagi. |

---

## K-40 · Luring dasar: antrean penyelesaian habit di memori, hanya tindakan yang aman diulang

> Diputuskan 6 Oktober 2026, saat 6.6 ditulis.
>
> Yang dipertanyakan: `spec/07` 6.6 — *“catat habit tanpa jaringan → sinkron tanpa duplikat”* —
> tidak menyebut **apa** yang boleh menunggu, **di mana** antreannya disimpan, atau **apa yang
> terjadi** saat server menolak catatan yang menunggu. **Bukan** yang dipertanyakan: kontrak
> `spec/04` (`POST …/completions` → 200 dengan baris lama · `DELETE …/completions/{tanggal}` → 204 ·
> `id` buatan klien) dan `UNIQUE (habit_id, for_date)` `spec/01` — itulah yang sudah membuat
> pencatatan luring aman diulang.

| | |
|---|---|
| **Keputusan** | **(1)** Yang diantre **hanya tandai selesai dan batalkan** — tindakan harian, dan satu-satunya yang aman diulang. Check-in energi dan habit baru **tidak**: keduanya gagal sebagai `JaringanPutus` dengan pesan jaringan. **(2)** Catatan dibuang dari antrean **sesudah** server menjawab (*at-least-once*): jawaban yang hilang di jalan berarti dikirim **lagi**, dan server menjawab 200 dengan baris lama. **(3)** Urutan terjaga — catatan baru selalu di belakang; satu perkecualian: `batal` membuang catatan lama pada `(habit, tanggal)` yang sama (`DELETE` menghapus apa pun yang ada, akhirnya sama). `selesai` sesudah `batal` **tidak** dipadatkan: baris lama di server (mis. `skipped` dari perangkat lain) harus dihapus dulu. **(4)** `5xx` · `429` · `408` menahan **seluruh** antrean (dicoba lagi); `4xx` lain tak akan pernah berhasil, jadi catatan itu dibuang, **dihitung**, dan ditampilkan sampai pengguna mengakuinya. Galat jaringan (putus, atau tak dijawab **15 dtk**) adalah `JaringanPutus` — bukan penolakan, dan **tidak** melupakan token. **(5)** Antrean hidup di **memori** dan milik **satu akun**: masuk sebagai akun lain atau keluar membuangnya; *keluar* dengan catatan menunggu mencoba mengirim dulu, lalu bertanya. **(6)** Layar luring = jawaban server terakhir + catatan antrean ditumpangkan (yang terakhir menang); tanpa jawaban sebelumnya, galatnya diteruskan — bukan daftar kosong. **(7)** Pemicu kirim: tiap tindakan, muat ulang, dan tombol *Sinkronkan* — **tanpa** pewaktu. |
| **Bukti** | `spec/01`: *“`UNIQUE (habit_id, for_date)` mencegah pencatatan ganda saat aplikasi luring”* · `spec/04`: *“pencatatan habit dari perangkat luring harus selalu aman diulang”* · `spec/03`: *“ini yang membuat aplikasi luring aman menyinkron ulang”* · `apps/mobile/lib/api/klien.dart` (sebelum 6.6): penyimpanan lokal menunggu *“penyimpanan yang aman per platform”* — belum diputuskan siapa pun. Dibuktikan lawan api **sungguhan** (`test/ujung/luring_nyata_test.dart`): jaringan diputus → catatan menunggu → jawaban `POST` dihilangkan di tengah jalan → dikirim ulang → server tetap memegang **satu** penyelesaian bertier sama. |
| **Bacaan yang DITOLAK** | **(a)** *“Simpan antrean di penyimpanan lokal (`shared_preferences` · localStorage)”* — ditolak: tempat menyimpan data pengguna di perangkat (dan, bersamanya, token) adalah keputusan privasi yang salahnya ditanggung pengguna (**C-35**), localStorage web terbaca skrip mana pun di asal yang sama, dan paket pub baru menambah rantai pasok tanpa keputusan. **(b)** *“Antre juga check-in energi”* — ditolak: `PUT` mengganti seluruh baris, jadi salinan lama di layar yang dikirim belakangan menimpa perubahan dari perangkat lain. **(c)** *“Antre pembuatan habit”* — ditolak: `id` buatan klien memang aman diulang, tetapi catatan selesai di belakangnya bergantung pada habit yang belum ada di server; menuntut tampilan habit sementara dan urutan ketergantungan — di luar *“dasar”*. **(d)** *“Pemadatan penuh: selesai lalu batal = tak ada”* — ditolak: server bisa sudah memegang barisnya (perangkat lain), `DELETE` tetap harus dikirim. **(e)** *“Pewaktu berkala”* — ditolak: uji widget yang berpewaktu abadi tak pernah tenang (`pumpAndSettle`), dan pemicu dari tindakan pengguna sudah cukup untuk *dasar*. **(f)** *“Membuang catatan 4xx diam-diam”* — ditolak: catatan pengguna yang hilang tanpa jejak lebih buruk daripada spanduk yang mengganggu. |
| **Harga yang diakui** | ⚠️ **Antrean mati bersama proses**: aplikasi yang ditutup atau dimatikan sistem selagi luring kehilangan catatan yang belum terkirim — *keluar* bertanya dulu, proses yang dimatikan tidak. ⚠️ **Aplikasi yang dibuka tanpa jaringan tak bisa dipakai** (tak ada sesi: token juga hanya di memori — `klien.dart`); luring dasar = jaringan putus **selagi aplikasi berjalan**. Catatan luring menang atas perubahan perangkat lain yang lebih baru (dikirim apa adanya — server tak punya versi). `4xx` yang dibuang bisa jadi catatan yang sah bagi pengguna (habit dihapus di perangkat lain) — hanya dihitung dan diberitahukan. Tanpa pewaktu, antrean menunggu tindakan berikutnya. Waktu tunggu 15 dtk per permintaan menahan layar selama itu pada jaringan yang diam (bukan putus). |
| **Cara membalikkan** | `apps/mobile/lib/api/luring.dart` (satu berkas) · `LayarHabitHariIni.luring` · `main.dart`; penyimpanan lokal kelak = membaca/menulis `_antrean` lewat satu antarmuka — tambahan, bukan penulisan ulang. `test/api/luring_test.dart` · `test/layar/luring_layar_test.dart` · `test/ujung/luring_nyata_test.dart` dan 31 mutasi `6.6` diubah bersamanya. |

---

## K-41 · Privacy Center: tiap modul menyatakan bagiannya; ringkasan = jumlah, bukan isi; izin dari registry yang ditegakkan

> Diputuskan 7 Oktober 2026, saat 6.4 ditulis (`3db89f8`). Ditulis di berkas ini 8 Oktober 2026
> dari kode dan pesan commit-nya.
>
> Yang dipertanyakan: spec/04 *Privacy Center* memberi rutenya (`summary` · `permissions` ·
> `export` · `data/{category}`), tetapi tidak bagaimana satu modul meringkas data milik dua belas
> modul, padahal modul domain tidak saling impor (spec/06 aturan 3) dan SQL sebuah modul hanya
> menyebut tabel miliknya (aturan 5).

| | |
|---|---|
| **Keputusan** | **(1)** Rumahnya `identity` (izin, persetujuan, dan jejak audit miliknya): rute `/v1/privacy/*` di `identity.router_privasi`. **(2)** **Tiap modul menyatakan bagiannya sendiri**: `BAGIAN_PRIVASI` (`BagianData` — kategori, tabel, SQL hitung dan ekspor, ditulis di modul PEMILIK tabel) dan `PENGHAPUS_PRIVASI` (K-42). `hvx.main` merakitnya di `app.state` (K-23); tanpa sambungannya rute **menolak berjalan** (`RuntimeError`), bukan menjawab *“tidak ada data”*. **(3)** Tiap tabel ber-`user_id` di spec/01 dinyatakan **tepat sekali** — penegak `tests/unit/test_cakupan_privasi.py`: tabel baru yang lupa dinyatakan membuatnya merah. **(4)** `GET /privacy/summary` = **jumlah per kategori dan per tabel, bukan isi**; baris yang **diturunkan** sistem dihitung terpisah (`derived_count`); tiap kategori (13) membawa masa simpannya dalam kalimat untuk pengguna (GDPR Art. 13(2)(a)), `deletable`, dan alasannya bila tidak; plus `not_collected` — lokasi · kalender · keuangan · wearable (naskah 5 §26, tanda ○). Dibaca dalam **satu potret** (`REPEATABLE READ`, `transaksi_pengguna(…, satu_potret=True)`); baris arsip (`deleted_at`) ikut dihitung — masih tersimpan, jadi masih diketahui. **(5)** `GET /privacy/permissions` = tiap agent aktif dan tiap (scope, aksi) yang **sungguh bisa ditanyakan gerbang risiko** (4.5) — dibangun dari registry yang sama, bukan daftar kedua — dengan keputusan yang **BERLAKU** (`source: user` = tersimpan dan belum kedaluwarsa; `default` = bawaan gerbang: R0·R1 `allow`, R2 ke atas `ask`, scope sensitif selalu `ask`). `PUT` hanya untuk izin yang diminta agent — selain itu `404 permission_not_requested` — dan berlaku seketika di `MesinIzin`. |
| **Bukti** | naskah 5 §26 (*Profile ✓ · Goals ✓ · Journal ✓ …*, izin per agent); spec/04: *“`GET /privacy/summary` sengaja mengembalikan jumlah baris, bukan isinya”*; spec/06 aturan 3 · 5. Uji: `test_privacy_center.py` — `test_ringkasan_menghitung_semua_kategori_tanpa_isi` · `test_ringkasan_hanya_milik_pengguna_itu` · `test_izin_per_agent_menampilkan_bawaan_gerbang` · `test_ubah_izin_berlaku_seketika_di_mesin_izin` · `test_izin_yang_tidak_diminta_atau_cacat_ditolak`; `test_cakupan_privasi.py` (9 uji, termasuk `test_tiap_tabel_milik_pengguna_dinyatakan_tepat_sekali` · `test_tiap_modul_hanya_menyatakan_tabel_miliknya` · `test_katalog_izin_agent_sama_dengan_registry_yang_ditegakkan`). |
| **Bacaan yang DITOLAK** | **(a)** *“`identity` membaca semua tabel langsung”* — ditolak: melanggar aturan 5 (`test_batas_tabel`) dan menjadikan satu modul tahu bentuk semua tabel. **(b)** *“Daftar izin tersendiri untuk layar”* — ditolak: dua daftar menyimpang diam-diam; layar harus menampilkan yang ditegakkan gerbang. **(c)** *“Ringkasan menampilkan isi”* — ditolak oleh spec/04: layar ini menjawab *“apa yang kamu tahu tentang saya”* tanpa menumpahkan seluruh data. |
| **Harga yang diakui** | Tiap tabel baru wajib dinyatakan di modulnya — sengaja, uji yang menagihnya. Satu kueri hitung per tabel per permintaan ringkasan. Baris arsip terhitung walau tidak tampil di layar lain. |
| **Cara membalikkan** | `identity/privasi.py` · `routes_privasi.py` · `*/privasi.py` tiap modul · perakitan di `hvx.main`; `tests/integration/test_privacy_center.py` dan `tests/unit/test_cakupan_privasi.py` diubah bersamanya. |

---

## K-42 · Hapus per kategori: hapus KERAS beserta turunannya, satu transaksi, sandi diminta lagi

> Diputuskan 7 Oktober 2026, saat 6.4 ditulis (`3db89f8`, migrasi **0013**).

| | |
|---|---|
| **Keputusan** | **(1)** `DELETE /v1/privacy/data/{category} {password}` → `202 {category, deleted: {tabel: jumlah}}`. **Hapus KERAS**, bukan arsip. **(2)** Kategori SUMBER membawa **turunannya**, di transaksi yang sama, turunan dijalankan SESUDAH sumbernya (supaya memori yang baru diekstrak ekstraksi yang sedang berjalan ikut terlihat dan ikut dilupakan — K-27): **event** jenisnya · **memori** scope sumbernya (jurnal → `journal_raw`, mood → `mood`, habit · goal · check-in → scope masing-masing) dikosongkan seketika (`content=''`, `deleted_at`) · **`human_states`** (turunan check-in, 5.3) · **rekomendasi** (mesin: menurut domain/subjek/konteks; tulisan agent: ikut terhapus bersama SALAH SATU sumber yang mungkin, sebab sumber pastinya tidak tercatat per baris). Kategori `memories` (*“lupakan semua”*, sumbernya tetap) dan `history` (seluruh riwayat kejadian + pola `behavioral`) bisa dihapus sendiri. **(3)** `account` · `profile` · `audit` **tidak** bisa dihapus di sini → `409 category_not_deletable`, diperiksa **sebelum** sandi ditebak; jalannya hapus akun (6.5, K-39). **(4)** `events` tetap tanpa `UPDATE`/`DELETE` bagi `hvx_app` (spec/01 §10): satu fungsi `SECURITY DEFINER` sempit, `hapus_event_pengguna(jenis[], subjek_tipe, subjek_id)` — hanya event milik pengguna yang **sedang dilayani transaksi**, hanya jenis yang disebut; tanpa pengguna yang dilayani ia menolak. **(5)** Sandi diminta lagi (OWASP ASVS V3.7.1); tebakan lewat pintu ini berbagi jatah dengan login gagal (`PenjagaGagalMasuk`, **E-226**); penolakan berjejak `data.deletion_rejected`, keberhasilan `data.deleted` (metadata: jumlah baris) di transaksi yang sama. **(6)** Titik Qdrant memori yang dilupakan dibuang penyelaras sesudah commit (Qdrant tidak ikut transaksi, spec/01 §12) — karena itu `202`. |
| **Bukti** | naskah 11 §7.25 *Deletion Engine*: *“tidak boleh hanya menghapus row di PostgreSQL”* — event, memori → vektor, nilai turunan; dan *event boleh dihapus atas permintaan pemiliknya, tidak boleh diubah oleh sistem*. C-33: payload event membawa teks bebas yang tabel sumbernya sudah tidak punya. Uji: `test_privacy_center.py` — `test_hapus_kategori_membuang_tabelnya_dan_turunannya_saja` · `test_hapus_jurnal_membawa_event_dan_memorinya_bukan_milik_mood` · `test_hapus_mood_membuang_rekomendasi_agent_bukan_milik_mesin` · `test_hapus_percakapan_menyisakan_jejak_run_tanpa_tautan` · `test_hapus_kategori_butuh_sandi_yang_benar` · `test_kategori_yang_tidak_bisa_dihapus_ditolak_sebelum_sandi` · `test_tebakan_sandi_ulang_berbagi_jatah_dengan_login_gagal`; `test_cakupan_privasi.py` — `test_tiap_jenis_event_ikut_terhapus_bersama_kategori_sumbernya` · `test_memori_turunan_ikut_terlupa_bersama_kategori_sumbernya`. |
| **🔧 8 Okt 2026** | Proyeksi `inferred` ikut `habits` dan `history` (**E-232**); hapus kategori menunggu konsumen yang sedang menurunkan datanya — `platform.kunci_turunan` (**E-234**); memori `coaching_notes` dari percakapan belum dipetakan — **C-37** (pemilik). |
| **Bacaan yang DITOLAK** | **(a)** *“`GRANT DELETE ON events TO hvx_app`”* — ditolak: spec/01 §10 melarang membuka `events` dengan melebarkan `GRANT`; hak umum membuat tiap jalur kode api bisa menghapus riwayat, bukan hanya jalur permintaan pemiliknya — fungsi sempit hanya menghapus jenis yang disebut, untuk pengguna yang dilayani, dan tidak bisa **mengubah** event. **(b)** *“Hapus sumbernya saja”* — ditolak oleh §7.25: nilai turunan tetap membawa jejak perilaku walau sumbernya hilang. |
| **Harga yang diakui** | ⚠️ **Tidak bisa dibatalkan.** Rekomendasi agent ikut terhapus walau sumber sebenarnya mungkin kategori lain — dipilih sisi yang melindungi; rekomendasi bisa dihitung ulang, teks yang menginap tidak bisa ditarik. Menghapus check-in menghapus **seluruh** `human_states` (V0 tak punya sumber lain). Jejak kerja asisten (`agent_runs`) tidak dihapus di sini — ikut akun (kategori `audit`). |
| **Cara membalikkan** | `identity.privasi.hapus_kategori` · `PENGHAPUS_PRIVASI` tiap modul · migrasi 0013 (`hapus_event_pengguna`, spec/01 §12); uji di atas diubah bersamanya. |

---

## K-43 · Ekspor: sandi ulang, dibangun saat diunduh, sekali pakai, tanpa rahasia di URL

> Diputuskan 7 Oktober 2026, saat 6.4 ditulis (`3db89f8`).

| | |
|---|---|
| **Keputusan** | **(1)** `POST /v1/privacy/export {password}` → `202 {export_id, status: "ready", expires_at}`: sandi diminta lagi (berbagi jatah dengan login gagal), dibatasi **5 per pengguna per jam**, berjejak `data.export_requested`. Redis hanya menyimpan **status** di kunci ber-`user_id` (`…:ekspor:<user_id>:<export_id>`), umur **1 jam** — tidak pernah isi (prinsip E-171). Tanpa `Idempotency-Key`: ulangannya membuat catatan sekali-pakai lain, tidak menulis data domain. **(2)** `GET /privacy/export/{id}` → status, `expires_at`, dan `download_url` relatif selagi `ready`. **(3)** `GET /privacy/export/{id}/download` — butuh **sesi pemiliknya**, **sekali pakai** (satu skrip Lua: hanya `ready` → `downloaded`, umur tetap); yang kedua `410 export_already_downloaded`; gagal membangun sesudah catatannya diambil → dikembalikan ke `ready`. **(4)** Dokumen **dibangun saat diunduh** dari PostgreSQL di bawah RLS, dalam satu potret (`REPEATABLE READ`), dengan jejak `data.exported` di transaksi baca yang sama: JSON `{"format": "humanverse-export", "format_version": 1, exported_at, user_id, categories: {kategori: {tabel: [baris…]}}}` dari `BAGIAN_PRIVASI` yang sama dengan ringkasan (K-41) — **tanpa `password_hash`, selamanya**. `Content-Disposition: attachment` · `Cache-Control: no-store`. **(5)** Aplikasi web menyimpannya sebagai unduhan peramban (Blob, URL-nya dicabut sesudah diklik); platform lain belum — layarnya mengatakannya. |
| **Bukti** | spec/04: `POST /privacy/export → 202 { export_id } (async, tautan sekali pakai)` · `GET /privacy/export/{id}`; GDPR Art. 15 · 20; UU PDP Pasal 7 · 13; OWASP ASVS V3.7.1 (sandi ulang untuk tindakan sensitif) · V8.3.1 (data sensitif tidak di URL). Uji: `test_privacy_center.py` — `test_ekspor_sekali_pakai_memuat_isi_tanpa_hash_sandi` · `test_ekspor_milik_a_tidak_terlihat_dan_tidak_terunduh_oleh_b` · `test_ekspor_butuh_sandi_dan_dibatasi_per_jam` · `test_ekspor_tak_dikenal_404`; Flutter `test/ujung/privasi_nyata_test.dart` lawan api hidup. |
| **Bacaan yang DITOLAK** | **(a)** *“Bangun berkas di latar, simpan sampai diunduh”* — ditolak: salinan seluruh data seseorang yang menginap di Redis atau penyimpanan berkas adalah satu tempat bocor lagi. **(b)** *“Tautan unduh bertoken”* — ditolak: rahasia di URL masuk riwayat peramban, log proksi, dan `Referer` (ASVS V8.3.1). **(c)** *“Ekspor tanpa sandi ulang”* — ditolak: token yang dicuri tidak boleh cukup untuk menyalin seluruh hidup seseorang. |
| **Harga yang diakui** | Unduhan memegang satu transaksi baca selama dokumen dibangun — sebesar seluruh data pengguna. Tautan hanya 1 jam dan sekali unduh; unduhan yang terputus di jalan menuntut ekspor baru. Di aplikasi non-web ekspor belum bisa disimpan ke perangkat (penyimpanan perangkat: **C-35**). |
| **Cara membalikkan** | `identity/privasi.py` bagian *ekspor* (`UMUR_EKSPOR_S`, `BATAS_EKSPOR`, `VERSI_EKSPOR`) · `routes_privasi.py` · `apps/mobile/lib/api/simpan_berkas*.dart`; uji di atas diubah bersamanya. |

---

## K-44 · Notifikasi V0: pilihan per jenis dan satu gerbang kirim — tanpa pengiriman

> Diputuskan 7 Oktober 2026, saat 6.3 ditulis (`887170d`).
>
> Yang dipertanyakan: spec/07 6.3 *“bisa dimatikan per jenis”* — padahal V0 **tidak mengirim**
> notifikasi apa pun (A-28: V0 reaktif; kanal push menuntut aplikasi perangkat dan izin OS-nya).

| | |
|---|---|
| **Keputusan** | **(1)** Yang dikerjakan V0 adalah bagian yang harus ada **sebelum** satu notifikasi pun dikirim: pilihan pengguna per jenis, tersimpan, dan **satu gerbang murni** `profile.keputusan_kirim` → `now` · `later` · `silent` yang wajib dilewati pengirim mana pun kelak: dimatikan → `silent`; pagu harian habis → `silent` (*Do nothing*, §11.44); jam tenang → `later`. **(2)** Empat jenis: `habit_reminder` (bawaan **mati** — menunggu jam pengingat per habit), `weekly_review` (bawaan **nyala**), `recommendation` (bawaan **mati** — menunggu A-28), `account_security` (**nyala dan wajib** — tidak bisa dimatikan, melewati jam tenang dan pagu). Jam tenang bawaan **22:00–07:00** (boleh melintasi tengah malam, boleh `null`); pagu **10/hari** (naskah 11 §11.17). **(3)** `GET`/`PATCH /v1/me/notifications`; disimpan di `profiles.preferences.notifications` — **hanya pilihan pengguna**, bukan bawaan, supaya bawaan yang kelak berubah tetap berlaku bagi yang belum memilih. Dibaca lalu ditulis di bawah kunci baris (`FOR NO KEY UPDATE`): dua `PATCH` serentak untuk jenis berbeda tidak saling menimpa. `PATCH /me/profile` **menolak** menyentuh kunci itu — satu penulis per kunci. **(4)** Jawaban API menyatakan `delivery: "none"` — jujur bahwa V0 tidak mengirim. |
| **Bukti** | naskah 7 Layer 38 (*“Jangan spam”*, quiet hours) · naskah 11 §11.43 *Interruption Manager* (*Notify now · Notify later · Silent*) · §11.17 (`notification: send: 10/day`); *privacy/attention by default* GDPR Art. 25(2), izin notifikasi dalam konteks (Android 13 `POST_NOTIFICATIONS`, Apple HIG); keamanan akun sebagai perlindungan pemiliknya (lih. GDPR Art. 34). Uji: `test_notifikasi_murni.py` (7) · `test_notifikasi_dan_tinjauan.py` — `test_notifikasi_bawaan_dan_jujur_bahwa_v0_tidak_mengirim` · `test_tiap_jenis_dimatikan_sendiri_dan_tersimpan` · `test_profil_tidak_menimpa_pilihan_notifikasi` · `test_preferensi_notifikasi_cacat_ditolak` · `test_dua_perubahan_serentak_tidak_saling_menimpa`. |
| **Bacaan yang DITOLAK** | **(a)** *“Semua jenis menyala bawaan”* — ditolak: perhatian pengguna dilindungi secara bawaan; yang menyala hanya yang jelas ia harapkan. **(b)** *“Keamanan akun bisa dimatikan”* — ditolak: pemberitahuan bahwa akunmu dihapus, diekspor, atau dimasuki adalah perlindungan bagimu, bukan pemasaran. **(c)** *“Tabel preferensi tersendiri”* — tidak diperlukan: `profiles.preferences jsonb` (spec/01) sudah rumahnya, tanpa migrasi. **(d)** *“Menunda 6.3 sampai ada pengiriman”* — ditolak: gerbang lebih dulu daripada yang dijaganya (`AGENTS.md` §2). |
| **Harga yang diakui** | ⚠️ Gerbangnya belum pernah dilewati pengirim sungguhan — V0 tidak mengirim. Hitungan *terkirim hari ini* adalah masukan gerbang yang kelak dipasok pengirimnya; V0 belum menyimpannya. Pengingat habit belum punya jam per habit. |
| **Cara membalikkan** | `profile/notifikasi.py` (`JENIS`, `PAGU_HARIAN`, `JAM_TENANG_BAWAAN`) · `profile/routes.py` · `profile/repository.py`; uji di atas diubah bersamanya. |

---

## K-45 · Tinjauan mingguan: lima pertanyaan dari data, dihitung saat dibaca, “Kenapa?” tetap bertanya

> Diputuskan 7 Oktober 2026, saat 6.2 ditulis (`a354a70`).
>
> Yang dipertanyakan: spec/07 6.2 *“menjawab 5 pertanyaan naskah 4 §31”* — *What went well? ·
> What changed? · What failed? · Why? · What should change next week?* — padahal V0 tidak punya
> model yang menalar (K-28), dan *Why* adalah klaim sebab.

| | |
|---|---|
| **Keputusan** | **(1)** `GET /v1/reviews/weekly?week=YYYY-Www` — minggu ISO di zona profil; bawaannya minggu berjalan. Minggu cacat → `400 invalid_week`; minggu yang belum dimulai → `422 week_in_future`. **(2)** **Dihitung saat dibaca, tidak disimpan** — dari habit, check-in, dan mood lewat pintu keluar modul pemiliknya (`habits.habit_rentang` · `checkins.checkin_rentang` · `checkins.mood_rentang`). **(3)** Periode dihitung dengan aturan rentetan 2.4 (harian per hari, mingguan satu periode; habit bulanan tidak dihakimi per minggu; minggu berjalan belum *gagal*). Ambang V0: ≥ 0,8 periode terpenuhi → *berjalan baik*, < 0,5 → *belum berhasil*; perubahan antar-minggu dibandingkan hanya bila ≥ 2 periode terhitung di **kedua** minggu (0,2 untuk tingkat penyelesaian, 0,5 untuk rata-rata skala). **(4)** Tiap butir membawa `evidence_count`; tanpa butir, pertanyaannya ber-sikap `ask` (Confidence Layer 5.4). **(5)** **“Kenapa?” selalu `ask`**: sistem hanya memberi hal yang terjadi **bersamaan** (energi di hari terpenuhi vs terlewat, bila selisihnya ≥ 1) dan alasan yang pengguna **catat sendiri** saat melewatkan habit (≤ 3, dipotong 80 karakter) — tanpa klaim sebab. **(6)** Saran minggu depan: versi minimum di hari berenergi rendah (*Tiny Habits*, tier adaptif naskah 4 §34) dan ajakan rencana *jika–maka* (*implementation intentions*). **(7)** Sumbu §31 yang tidak diukur V0 (belajar · keuangan · sosial · karier · gaya hidup) dinyatakan `not_measured` — seperti dashboard 6.1. |
| **Bukti** | naskah 4 §31 · §7 (asosiatif, bukan kausal; `pola.tanpa_klaim_kausal`) · §34; minimisasi data GDPR Art. 5(1)(c); Gibbs (1988) dan *retrospective* Derby & Larsen (2006) — refleksi sendiri yang membuat tinjauan berguna; Fogg (2019); meta-analisis Gollwitzer & Sheeran (2006). Uji: `test_tinjauan_murni.py` (10, termasuk `test_lima_pertanyaan_dijawab_dari_bukti_dan_kenapa_tetap_bertanya` · `test_kalimat_sistem_tidak_mengklaim_sebab` · `test_habit_bulanan_tidak_dihakimi_per_minggu`) · `test_notifikasi_dan_tinjauan.py` — `test_tinjauan_tanpa_data_bertanya_di_kelima_pertanyaan` · `test_tinjauan_minggu_lalu_dari_data_sungguhan` · `test_minggu_cacat_atau_belum_dimulai_ditolak`. |
| **Bacaan yang DITOLAK** | **(a)** *“Sistem menjawab ‘Kenapa?’”* — ditolak: data observasional tidak membuktikan sebab (§7). **(b)** *“Simpan tinjauan tiap minggu”* — ditolak: salinan baru tentang pengguna yang tidak ikut terhapus bersama sumbernya di Privacy Center (K-42); refleksi pengguna sendiri tempatnya jurnal. **(c)** *“Tujuh sumbu §31 diberi angka”* — ditolak: lima belum punya ukuran (A-19/B-38), sama dengan 6.1. |
| **Harga yang diakui** | Ambang 0,8 · 0,5 · 0,2 · 0,5 · 1,0 adalah pilihan V0, belum dikalibrasi data nyata (#34 berlaku juga di sini). Tinjauan dihitung ulang tiap kali dibuka. |
| **Cara membalikkan** | `intelligence/tinjauan.py` (`VERSI`, ambang di kepala berkas) · rute di `intelligence/routes.py`; uji di atas diubah bersamanya. |

---

## K-46 · Tiga butir C diputuskan atas delegasi pemilik: hapus jurnal keras, mood sensitif, `ip_hash` dikosongkan

> Diputuskan 7 Oktober 2026, saat 6.4 ditulis (`3db89f8`), **atas delegasi pemilik**
> (dicatat sebagai **H-28** di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md)): *“keputusan di anda
> berikan pertimbangan internasional dari para pakar.”*
>
> ⚠️ **Satu-satunya entri di berkas ini yang memutuskan butir C.** Batas di atas (*“seluruh butir
> C tetap milik pemilik”*) tidak dicabut: delegasi itu diberikan untuk **C-31 · C-32 · C-34** — tiga
> butir yang 6.4 tidak bisa diselesaikan tanpanya — dan tidak meluas ke butir C lain (C-33 · C-35
> · C-36 tetap terbuka).

| | |
|---|---|
| **Keputusan** | **(C-31) Hapus jurnal = hapus KERAS.** `DELETE /journal/{id}` menghapus barisnya, event `journal.created`-nya (`hapus_event_pengguna` subjek itu), dan memori turunannya, di transaksi yang sama. Migrasi 0013 membuang jurnal yang **sudah** dihapus-lunak sebelumnya beserta event-nya. **(C-32) `mood` sensitif.** `SCOPE_RESMI["mood"].sensitif = True`: coach-agent membaca mood (`mood.recent`, `memory.search`) hanya sesudah pengguna menyimpan `allow` di Privacy Center — bawaan R0 tidak lagi membukanya; dan `mood` masuk larangan aturan 6 bagi agent pihak ketiga. Check-in harian (energi · fokus · tidur) **tidak** ikut. Delegasi antar-agent tidak ditanya untuk scope sensitif yang tidak dibacanya — yang membaca ditanya di run-nya sendiri (**E-227**, `MesinIzin.cek(delegasi=True)`). **(C-34) `ip_hash` dikosongkan** saat sapuan hapus akun (`hapus_akun_jatuh_tempo`, migrasi 0013); jejak audit tetap ada sebagai bukti dengan id semu (K-39). Masa simpan baris audit itu **tidak** diubah (`@retention: forever`, spec/01 §8) — dinyatakan apa adanya di Privacy Center (*“selama layanan berjalan … dianonimkan, tanpa jejak jaringan”*). |
| **Bukti** | **C-31:** GDPR Art. 17 (hak penghapusan) · Art. 5(1)(e) (pembatasan penyimpanan) · UU PDP No. 27/2022 Pasal 8; jurnal adalah Level 3 *Sensitive* (naskah [`133`](133-DATA-CLASSIFICATION.md)) dan tidak ada rute pemulihan — hapus-lunak menyimpannya bertahun-tahun tanpa jalan pulang. **C-32:** mood yang dilaporkan (valensi, label *“cemas”*, catatan bebas) adalah data kesehatan menurut GDPR Art. 4(15) · Art. 9 dan data pribadi spesifik menurut UU PDP Pasal 4 ayat (2) huruf a; garis check-in mengikuti lampiran WP29 (Feb 2015) tentang aplikasi gaya hidup. **C-34:** GDPR Recital 49 — kepentingan keamanan jaringan yang membenarkan `ip_hash` berakhir bersama akunnya. Uji: `test_jurnal.py` (hapus keras + event) · `test_izin.py` · `test_gerbang_risiko.py` (C-32 · E-227) · `test_alat_v0.py` · `test_memori.py` · `test_privacy_center.py` (`mood` sensitif di daftar izin) · `test_sapuan_hapus_akun.py::test_sapuan_menghapus_semua_jejak_akun_dan_hanya_akun_itu` (asersi `ip_hash` C-34). |
| **Bacaan yang DITOLAK** | **(C-31)** *“Hapus-lunak dengan jendela batal 30 hari”* dan *“tetap seperti sekarang, dinyatakan di Privacy Center”* (pilihan **(b)** · **(c)** di C-31) — ditolak: tulisan paling pribadi yang pemiliknya minta dihapus tidak menginap. **(C-32)** *“Check-in ikut sensitif”* — ditolak: penilaian diri gaya hidup, bukan status kesehatan (WP29). **(C-34)** *“Pertahankan `ip_hash` sebagai kepentingan sah forensik”* — ditolak: sesudah akunnya tiada, yang tersisa hanya kemampuan mempertemukan baris-baris itu dengan akun lain lewat jaringan yang sama. |
| **Harga yang diakui** | ⚠️ **C-31 tidak bisa dibalik** — jurnal yang dihapus, dan jurnal yang sudah dihapus-lunak sebelum migrasi 0013, hilang tanpa jendela batal. **C-32:** coach menjawab tanpa mood sampai pengguna mengizinkannya. **C-34:** korelasi forensik antar-akun sesudah penghapusan hilang. Ketiganya keputusan **hukum & privasi** yang diambil agent atas delegasi — pemilik tetap boleh membaliknya, dan yang menanggung akibatnya tetap pengguna. |
| **Cara membalikkan** | **C-31:** `journal/repository.py` (`_HAPUS`) + migrasi baru (pembersihan 0013 tidak bisa dibalik). **C-32:** `identity/scope.py` (`SCOPE_RESMI`) · `agents/registri.py` (`SCOPE_TERLARANG_PIHAK_KETIGA_6`) · spec/05 tabel scope. **C-34:** migrasi baru yang mengganti `hapus_akun_jatuh_tempo`. Uji di atas diubah bersamanya. |

---

## Yang sengaja **tidak** saya putuskan

| Butir | Kenapa |
|---|---|
| ~~[#139](../../issues/139) Master Architecture v2.0~~ | ✅ **pemilik memerintahkannya 10 Sep 2026** (*“kerjakan semua tugas dan fase yang masih tersisa”*) — dikerjakan, hasilnya [`../arch/`](../arch/README.md) |
| ~~[#3](../../issues/3) siapa mengerjakan V0~~ | ✅ **pemilik memutuskannya 16 Sep 2026** — AI coding agent di branch + PR, pemilik yang menggabungkan (**H-25**). Yang tetap bukan milik saya: **waktu** pemilik untuk meninjau |
| [#20](../../issues/20) cek merek & domain | menuntut pencarian merek dan pembelian |
| **seluruh butir C** (hukum & privasi) | risikonya ditanggung orang yang tidak ikut memilih — 🔧 kecuali C-31 · C-32 · C-34, didelegasikan pemilik 7 Okt 2026 (**H-28**, **K-46**) |
| §16.5 · §16.7 rantai humanoid | benda yang bisa melukai orang — gerbangnya bukan keputusan gaya |
| [#4](../../issues/4) Mental Wellness | cakupan produk |
| [#34](../../issues/34) ambang Confidence | butuh data nyata untuk dikalibrasi; menebak angkanya lebih buruk daripada membiarkannya terbuka |

💡 **Aturan yang saya pakai untuk memilah:** *kalau salahnya keputusan ini
ditanggung orang lain — pengguna, penerima pesan, atau pemilik uangnya —
keputusan itu bukan milik saya.*
