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
| urutan kerja pemilik | [#139](../../issues/139) Master Architecture v2.0 | soal waktu pemilik sendiri |

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

## K-3 · 127 nama event dipadankan — **naskah tidak diubah**

**Menutup:** [#149](../../issues/149) (**E-153**) · melanjutkan [#38](../../issues/38)

| | |
|---|---|
| **Keputusan** | Naskah **tidak** ditulis ulang. Tabel padanan `PascalCase → domain.verb` diterbitkan di [`../spec/03`](../spec/03-EVENT-CONTRACTS.md), dan **`spec/03` menjadi satu-satunya sumber nama yang sampai ke kode**. Padanannya mekanis: kata pertama → domain, sisanya → verb snake_case. |
| **Bukti** | [#38](../../issues/38) sudah memilih dua segmen huruf kecil; 127 nama pasca-keputusan memakai PascalCase ([`SENSUS-EVENT.md`](SENSUS-EVENT.md)). Belum ada kode, jadi belum ada nama yang terkunci. |
| **Bacaan yang DITOLAK** | *“Perbaiki saja nama-namanya langsung di naskah.”* **Ditolak** — aturan 1 repo ini menyatakan berkas naskah merekam kata pemilik apa adanya. Menyunting 127 nama di sana akan menghapus bukti bahwa keputusannya pernah dilanggar, dan itu justru satu-satunya alasan pola ini bisa ditemukan. |
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

## Yang sengaja **tidak** saya putuskan

| Butir | Kenapa |
|---|---|
| [#139](../../issues/139) Master Architecture v2.0 | soal **waktu pemilik**, bukan soal teknis. Angkanya sudah tersedia di issue-nya |
| [#3](../../issues/3) siapa mengerjakan V0 | orang dan waktu |
| [#20](../../issues/20) cek merek & domain | menuntut pencarian merek dan pembelian |
| **seluruh butir C** (hukum & privasi) | risikonya ditanggung orang yang tidak ikut memilih |
| §16.5 · §16.7 rantai humanoid | benda yang bisa melukai orang — gerbangnya bukan keputusan gaya |
| [#4](../../issues/4) Mental Wellness | cakupan produk |
| [#34](../../issues/34) ambang Confidence | butuh data nyata untuk dikalibrasi; menebak angkanya lebih buruk daripada membiarkannya terbuka |

💡 **Aturan yang saya pakai untuk memilah:** *kalau salahnya keputusan ini
ditanggung orang lain — pengguna, penerima pesan, atau pemilik uangnya —
keputusan itu bukan milik saya.*
