# 216 — §14.37–§14.41 Autonomous Organization, Project Engine, Task Market, A2A Commerce & Federation Protocol

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.37 — Autonomous Organization

> Ini adalah konsep **eksperimental** Phase 14.

Dari satu kalimat pengguna — *"Bangun produk AI untuk membantu mahasiswa"* —
HumanVerse dapat membentuk: **Product · Research · Market · UX · Architecture ·
Coding · QA · Security · Marketing · Finance Agent**.

```
Goal → Decomposition → Agent Team Formation → Planning
→ Execution → Evaluation → Human Approval
```

Tetapi agent **tidak otomatis** memiliki hak:

```
spend money        delete data
deploy production  sign contracts
contact customers
```

> tanpa **capability dan approval** yang sesuai.

---

> ⭐⭐⭐ **Lima larangan itu adalah daftar NEGATIF pertama di tingkat
> organisasi — dan `contact customers` adalah larangan pertama di delapan belas
> naskah yang melindungi orang SELAIN penggunanya.**
>
> Butir **C-19** ([#81](../../issues/81)) mencatat bahwa setiap pesan yang
> dikirim agent mendarat pada orang yang tidak pernah menyetujui apa pun, dan
> bahwa sisi **penerima** belum pernah dibahas. Di sini ia akhirnya muncul —
> bukan sebagai pembahasan, melainkan sebagai **larangan bawaan**. Itu bentuk
> yang lebih kuat daripada catatan.
>
> ⭐ Dan menuliskannya sebagai *"tidak otomatis memiliki hak"* — bukan
> *"sebaiknya dibatasi"* — menjadikannya **default deny**, sejajar dengan R4
> `DENY` (**H-21**). Kelimanya kebetulan juga persis lima hal yang paling sulit
> dibatalkan.

> 🛑 **`sign contracts` dan `contact customers` membuka wilayah hukum yang belum
> pernah disentuh: agent yang mengikat pengguna terhadap PIHAK KETIGA.**
>
> Tiga pertanyaan yang tidak punya jawaban di dokumen mana pun, dan yang
> jawabannya menentukan apakah fitur ini boleh ada:
>
> | Pertanyaan | Kenapa ia bukan soal teknis |
> |---|---|
> | Kontrak yang "ditandatangani" agent **mengikat siapa** | Kecakapan hukum ada pada orang/badan, bukan pada perangkat lunak. Yang terikat adalah penggunanya — dan ia harus tahu persis apa yang ia ikat. |
> | Apakah pihak ketiga **berhak tahu** ia berkorespondensi dengan agent | **C-19** menanyakan ini untuk email pribadi; *"contact customers"* menaikkannya ke skala komersial, tempat aturan pemasaran dan perlindungan konsumen berlaku. |
> | Siapa yang **bertanggung jawab** kalau agent salah | Pengguna, pengembang agent, atau HumanVerse. §14.4 menaruh agent di mesin orang lain, jadi jawabannya tidak bisa "kami". |
>
> Yang minimum harus diputuskan sebelum satu baris kode: **`sign contracts`
> tidak diberikan pada tingkat capability sama sekali di V0–V6**, dan
> `contact customers` hanya lewat aksi yang ditandai jelas berasal dari agent.
> Lihat **C-21** / [#95](../../issues/95).

> 🛑 **Rantainya menaruh `Human Approval` di ujung — SESUDAH `Execution`.**
> Ini pola yang berulang di §14.38 dan §14.46, dan ketiganya bersama-sama
> membalik urutan yang §11.14 tetapkan. Lihat **E-117** /
> [#93](../../issues/93).

---

## §14.38 — Autonomous Project Engine

```
Project Goal → Project Planner → Agent Team Builder → Task Allocation
→ Execution → Review → Integration → Testing → Human Approval
```

> Ini akan menjadi salah satu fitur paling **powerful** HumanVerse.

---

> ⭐ **`Review → Integration → Testing` sebelum approval adalah urutan yang
> benar untuk pekerjaan yang hasilnya berupa artefak** — kode, dokumen,
> rancangan. Manusia diminta menyetujui sesuatu yang **sudah diuji**, bukan
> sesuatu yang baru dijanjikan.
>
> ⚠️ Tapi itu hanya sah kalau `Execution` **tidak menyentuh dunia luar**.
> Menulis kode ke cabang: aman. Men-deploy, mengirim surat, atau membayar:
> tidak. §14.37 sudah menutup keempat hal itu lewat daftar larangannya — yang
> perlu ditambahkan cuma satu kalimat penghubung: **`Execution` sebelum
> approval hanya boleh berjalan di dalam sandbox tanpa efek luar** (§12.16
> sudah punya aturan yang sama untuk simulasi).

---

## §14.39 — Agent Task Market

```
Task: "Analyze this dataset"
        ↓
Agent Marketplace
        ↓
Agent A — $0.10   Agent B — $0.50   Agent C — $2.00
```

Selection engine: **Quality · Cost · Latency · Trust · Security ·
Specialization** — kemudian memilih agent terbaik.

---

> ⭐ **`Trust` dan `Security` sebagai dua sumbu TERPISAH adalah pembedaan yang
> benar.** *Trust* adalah rekam jejak (§14.10 — dan naskah ini tiga kali
> mengingatkan trust score **bukan** security boundary); *Security* adalah sifat
> yang bisa diperiksa sekarang: sandbox, sertifikasi, izin yang diminta.
> Agent baru bisa aman tanpa terpercaya; agent lama bisa terpercaya dan tetap
> tidak aman.

> ⚠️ **Enam kriteria dengan arah yang berlawanan, tanpa satu pun dinyatakan** —
> kemunculan **kelima** dari masalah yang sama (§10.29 · §11.32 · §11.54 ·
> §14.10). `Cost` dan `Latency` **kecil lebih baik**; empat sisanya besar lebih
> baik. Selama arahnya tidak ditulis, mesin seleksi apa pun yang menjumlahkan
> akan memilih agent yang mahal dan lambat.

> 🛑 **Pasar yang menawar harga menekan ke arah yang paling murah — dan yang
> memilih bukan penggunanya, melainkan orchestrator.** Uang pengguna
> dibelanjakan oleh mesin seleksi.
>
> Dua hal yang perlu ditulis: **`risk` harus mendominasi `cost`** untuk aksi di
> atas R2 — §14.24 sudah mendaftarkan `risk` sebagai kriteria tapi tidak
> arahnya, dan §11.54 sudah menetapkan *high-risk decision → multiple-model
> verification*, yang berarti **lebih mahal**. Dan **selisih harga 20×** antara
> Agent A dan Agent C bukan selisih yang bisa diabaikan diam-diam: pengguna
> berhak tahu bahwa pilihan termurah dipilih untuknya.

---

## §14.40 — Agent-to-Agent Commerce

```
Agent A → requests service → Agent B → executes task
→ returns result → billing
```

> Namun transaksi harus berada di bawah: **Economic Policy · Budget ·
> Permission · Risk · Audit**

---

> ⭐⭐ **Lima gerbang di atas transaksi antar-agent, dan `Economic Policy`
> sebagai yang pertama adalah benda baru** — bukan izin, bukan anggaran,
> melainkan aturan tentang **jenis transaksi apa yang boleh ada sama sekali**.

> 🛑 **Tetapi ini adalah kembaran ekonomi dari §14.31 — dan lubangnya sama
> persis: yang berbahaya adalah GABUNGANNYA, bukan langkahnya.**
>
> §14.31 menunjukkan A (baca) + B (tulis) = eksfiltrasi, meski tiap agent lolos
> gerbangnya masing-masing. Di sini: A membayar B $2, B membayar C $2, C
> membayar D $2 — **tiap transaksi di bawah pagu, dan tidak ada satu pun yang
> melihat totalnya**. Anggaran `daily_limit: 5` di manifest (§14.55) adalah pagu
> **per agent**, sama seperti `notification: 10/day` yang §14.25 sendiri
> tunjukkan sudah berhenti berarti apa-apa.
>
> ⭐ **Dan obatnya sudah ada di naskah ini, dua puluh bagian kemudian:
> `trace_id` (§14.57).** Anggaran yang benar diikatkan pada **jejak**, bukan
> pada agent — satu permintaan pengguna, satu pagu, dibagi ke seluruh rantai
> delegasi berapa pun panjangnya. Itu sekaligus membuat §14.56 (*"who
> initiated?"*) bisa menjawab *"berapa yang sudah dihabiskan permintaan ini"*.
>
> Sejalan dengan `Attention Budget` §14.25: **sumber daya langka dianggarkan per
> manusia, bukan per agent.** Uang dan perhatian butuh perlakuan yang sama.

---

## §14.41 — Federation Protocol

**HumanVerse Agent Protocol.** Minimal protocol harus mendukung:

```
DISCOVER   IDENTIFY   AUTHENTICATE   NEGOTIATE
REQUEST    RESPOND    STREAM         DELEGATE
CANCEL     VERIFY     AUDIT          REVOKE
```

---

> ⭐⭐⭐ **`CANCEL` dan `REVOKE` sebagai kata kerja protokol tingkat pertama —
> dan hampir tidak ada protokol agent yang punya keduanya.**
>
> Keduanya adalah **H-21** dan §14.68 yang diterjemahkan ke bentuk kawat:
> reversibility dan kill/revoke tidak bisa ditambahkan belakangan pada protokol
> yang tidak memikirkannya. `CANCEL` menghentikan pekerjaan yang sedang
> berjalan; `REVOKE` mencabut kewenangan yang sudah diberikan. Sebuah federasi
> tanpa keduanya berarti setiap agent eksternal yang pernah dipercaya dipercaya
> selamanya.
>
> ⭐ `AUDIT` sebagai kata kerja juga tidak biasa, dan ia masuk akal di sini:
> agent yang berjalan di mesin orang lain tidak bisa dibaca lognya — ia harus
> **bisa diminta menyerahkannya**. ⚠️ Yang perlu ditulis: **siapa boleh
> memanggil `AUDIT` pada siapa**, dan apa yang terjadi kalau agent eksternal
> menolak — jawaban yang benar hampir pasti: menolak `AUDIT` menurunkan trust
> dan mencabut akses, bukan diabaikan.

> ⚠️ **Tidak ada kata kerja untuk manusia.** Dua belas verb ini seluruhnya
> antar-mesin: tidak ada `ESCALATE`, `CONFIRM`, atau `ASK` — padahal §14.62
> mewajibkan `escalate_when: confidence < 0.6` dan §14.60 membangun seluruh
> Approval Center di atas gagasan bahwa sesuatu naik ke manusia.
>
> Akibatnya konkret: **agent eksternal tidak punya cara di protokol untuk
> mengatakan "ini perlu orangmu".** Yang tersisa baginya hanya `RESPOND`
> dengan hasil, atau gagal. Satu verb tambahan menutupnya — dan ia harus ada
> sejak versi pertama protokol, karena protokol adalah hal yang paling sulit
> diubah setelah ada pemakai di luar.
