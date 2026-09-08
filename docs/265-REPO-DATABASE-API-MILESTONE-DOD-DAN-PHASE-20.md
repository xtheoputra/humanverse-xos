# 265 — §19.30–§19.34 Repository, Database, API, Milestone, Definition of Done & Phase 20

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.30 — Repository Structure

```
scientific-discovery/
├── literature/   ├── knowledge-graph/ ├── statistics/       ├── models/
├── ingestion/    ├── hypothesis/      ├── reproducibility/  ├── provenance/
├── parsing/      ├── experiments/     ├── writing/          ├── agents/
├── entities/     ├── variables/       ├── review/           ├── labs/
├── citations/    ├── simulations/     ├── ethics/           │   ├── ai · robotics
│               ├── monte-carlo/     ├── safety/           │   ├── bio · materials
│                                     ├── datasets/         │   └── aetherscan
└── sdk/
```

---

> ⭐⭐ **Lima direktori pertama mengikuti pipeline §19.4 persis** — `literature`,
> `ingestion`, `parsing`, `entities`, `citations`. Kebiasaan yang naskah 22
> mulai (`world-intelligence/` mengikuti pipeline §18.4) berlanjut, dan ia yang
> membuat kode sulit ditulis di tempat yang salah.

> 🛑 **Tetapi `scientific-discovery/` menggerus H-10 untuk KESEMBILAN kalinya —
> naskah KESEBELAS berturut-turut yang menyentuh struktur repo.**
>
> | Direktori | Sudah ada di |
> |---|---|
> | `simulations/` | `spatial-os/` · `robotics/` · `health-bio/` · `global-intelligence/` · Phase 12 — **keenam kalinya** |
> | `provenance/` | `global-intelligence/` (dua kali di sana sendiri) — **ketiga** |
> | `models/` | `health-bio/` · `intelligence/` · `data-platform/` |
> | `agents/` | pohon tingkat-atas sejak naskah 2 |
> | `sdk/` | `developer-platform/` (naskah 10) · `global-intelligence/` |
> | `datasets/` · `statistics/` | bertumpang tindih `data-platform/` dan §18.7 |
>
> Dan `safety/` di sini menjadikan **pohon keamanan SEPULUH**.
> **E-134** ([#120](../../issues/120)) mencatat tujuh sudah menjadikan aturan
> impor **§8.42** tak bisa dinyatakan; **E-139** ([#129](../../issues/129))
> mencatat sembilan menjadikan pertanyaannya tidak bermakna.

> 🛑 **`governance/` TIDAK IKUT — padahal naskah 22 baru saja
> memperkenalkannya.**
>
> **E-139** mencatat sisi baiknya: `governance/` akhirnya muncul di naskah 22
> (pertama kali sejak diminta di naskah 18), sayangnya di dalam pohon fase
> sehingga ia hanya mengatur fasenya sendiri. Usulnya: **naikkan satu tingkat.**
>
> Yang terjadi justru sebaliknya — naskah 23 tidak memakainya sama sekali dan
> menggantinya dengan `ethics/` + `safety/`. ⇒ Sebuah direktori tata kelola yang
> hidup di dalam satu fase memang **tidak diwarisi fase berikutnya**; itu
> pembuktian langsung atas keberatan #129, satu naskah kemudian.
>
> ⚠️ Dan `ethics/` sebagai direktori tingkat pertama sebenarnya **tepat** untuk
> fase ini (sejalan `consent/` dan `audit/` di `health-bio/`). Masalahnya bukan
> ia ada, melainkan **tidak ada satu pohon tata kelola yang berlaku lintas
> fase.** Lihat **E-145** / [#138](../../issues/138).

---

## §19.31 — Database

`papers · authors · institutions · datasets · experiments · hypotheses ·
claims · citations · variables · simulations · statistics · reviews ·
ethics_reviews · reproducibility_scores · research_projects ·
research_timeline · scientific_agents`

---

> ⭐⭐⭐ **`claims` terpisah dari `papers`, dan `ethics_reviews` sebagai tabel
> tersendiri.**
>
> Yang pertama menjadikan §19.7 mungkin (dua paper bisa bertentangan pada satu
> klaim sambil sepakat pada yang lain) dan konsisten dengan `knowledge_claims`
> §18.28 — dua naskah berturut-turut memodelkan klaim sebagai benda tersendiri.
>
> Yang kedua lebih menentukan daripada terlihat: **tinjauan etika yang punya
> baris bisa ditanya *"mana tinjauannya"*.** Sesuatu yang hanya berupa langkah
> proses akan hilang tanpa jejak ketika dilewati; sesuatu yang berupa baris
> meninggalkan lubang yang bisa dilihat.

> 🛑 **Tetapi `citations` tidak punya kolom yang menyatakan sebuah sitasi sudah
> DICOCOKKAN dengan sumbernya — dan §19.20 melarang mengarang referensi.**
>
> Larangan tanpa tempat menyimpan hasil pemeriksaannya tidak bisa ditegakkan.
> ⭐ Perbaikannya satu kolom: **`citations.resolved_paper_id` yang wajib**, dan
> aturan bahwa keluaran §19.20 hanya boleh memuat sitasi yang punya nilai di
> sana. Bahan penyelesainya sudah ditarik §19.4 (`Crossref`, `Semantic
> Scholar`, `OpenAlex`). Lihat **B-37** / [#134](../../issues/134).

> ⚠️ **`scientific_agents` sebagai tabel terpisah menjawab pertanyaan §19.16
> secara diam-diam: ada DUA registri agent.** Sepuluh agent riset tidak masuk
> registri yang sudah ada. Keputusan itu mungkin benar, tetapi ia diambil oleh
> nama tabel, bukan oleh kalimat.

> ⚠️ **Dan tidak ada tabel untuk lisensi maupun retensi** — §19.24 mengelola
> `license` per dataset, tetapi tidak ada tempat menyimpannya untuk `papers`,
> yang justru kelas paling berhak cipta di antara keduanya (**C-27** /
> [#122](../../issues/122)).

---

## §19.32 — API

```
POST /v1/research/question     POST /v1/research/simulation   GET  /v1/research/review
GET  /v1/research/papers       GET  /v1/research/evidence     POST /v1/research/statistics
POST /v1/research/hypothesis   POST /v1/research/experiment   GET  /v1/research/provenance
```

---

> ⭐ **`GET /v1/research/provenance` dan `GET /v1/research/evidence` sebagai
> endpoint tersendiri** menjadikan §19.26 dan §19.6 **antarmuka**, bukan janji
> internal — bentuk yang sama dengan `GET /v1/intelligence/provenance/{id}`
> §18.29 dan §17.5 (*"melihat siapa yang mengakses"*): jaminan yang bisa
> diperiksa dari luar.

> 🛑 **Tetapi semuanya `/v1/…`, bukan `/api/v1` — pelanggaran
> [#38](../../issues/38) yang KESEPULUH berturut-turut**, dan naskah **ketiga
> berturut-turut** sesudah §17.44 dan §18.29. Lihat **E-147** / [#136](../../issues/136).

> ⚠️ **`POST /v1/research/experiment` tidak punya pasangan yang menjalankan —
> dan itu justru benar.** §19.15 mengirim protokol ke lab automation, tetapi
> tidak ada endpoint `execute`. Kalau itu disengaja, ia layak **ditulis sebagai
> keputusan**: eksekusi fisik tidak punya jalur API. Kalau tidak, ia akan
> ditambahkan oleh orang pertama yang membutuhkannya, tanpa gerbang. Lihat
> **C-29** / [#131](../../issues/131).

---

## §19.33 — Milestone Implementasi

| | Fokus | | | Fokus |
|---|---|---|---|---|
| **S19.1** | Literature Engine | | **S19.6** | Experiment Planner |
| **S19.2** | Knowledge Graph | | **S19.7** | Simulation Lab |
| **S19.3** | Evidence Ranking | | **S19.8** | Multi-Agent Research |
| **S19.4** | Gap Detection | | **S19.9** | Writing & Review |
| **S19.5** | Hypothesis Engine | | **S19.10** | **Ethics & Safety** |

---

> ⭐⭐ **`S19.3 Evidence Ranking` berdiri sebelum `S19.4 Gap Detection` dan
> `S19.5 Hypothesis Engine`** — bukti dinilai sebelum ada yang menyimpulkan
> darinya, urutan yang sama benarnya dengan `G18.5` di naskah 22.

> 🛑🛑🛑 **Tetapi `Ethics & Safety` di urutan TERAKHIR — naskah KEEMPAT
> berturut-turut — di fase yang menamai `Biosecurity` dan `Dangerous
> Capability`.**
>
> naskah 20 `R16.10` terakhir ([#111](../../issues/111)) → naskah 21 `H17.12` di
> luar MVP ([#116](../../issues/116)) → naskah 22 tanpa milestone
> ([#121](../../issues/121)) → **naskah 23 `S19.10` terakhir**.
>
> Dan §19.23 dua bagian sebelumnya menulis: *"**Semakin tinggi risiko, semakin
> ketat governance**"* — prinsip yang sama dengan penutup §17.56. **Naskah ini
> memuat aturannya dan pelanggarannya sekaligus.** Lihat **C-29**.

> 🛑 **Empat butir Definition of Done tidak punya milestone mana pun** — dan
> salah satunya adalah kemunduran langsung dari naskah 22:
>
> | Butir DoD §19.34 | Milestone |
> |---|---|
> | `melakukan analisis statistik` (§19.18) | **tidak ada** |
> | `memeriksa reproducibility` (§19.19) | **tidak ada** |
> | **`menjaga provenance`** (§19.26) | **tidak ada** |
> | `mendukung lab automation di masa depan` (§19.15) | **tidak ada** |
>
> ⭐ Naskah 22 menaruh `provenance` di **milestone PERTAMA** (`G18.1`), dan itu
> dicatat sebagai alasan roadmap-nya *"terbaik dalam lima naskah"*: asal-usul
> dibangun sebagai fondasi, sesuatu yang hampir mustahil dipasang belakangan.
> Satu naskah kemudian ia **tidak punya milestone sama sekali**, sementara DoD
> tetap menuntutnya.
>
> ⇒ Ini **naskah KETIGA berturut-turut** yang DoD-nya menuntut apa yang tidak
> dibangun milestone mana pun (§17.54 → **B-33**/[#116](../../issues/116);
> §18.33 → **G-17**/[#121](../../issues/121); di sini). Kesimpulannya tidak
> berubah: **kriteria yang tidak punya milestone tidak akan pernah diperiksa.**
> Lihat **G-18** / [#137](../../issues/137).

---

## §19.34 — Definition of Done & Evolusi

> Phase 19 selesai ketika HumanVerse mampu: membaca dan mengindeks jutaan paper ·
> membangun Research Knowledge Graph · menemukan research gaps · menghasilkan
> hipotesis berbasis evidence · merancang eksperimen · menjalankan simulasi ·
> melakukan analisis statistik · memeriksa reproducibility · membantu penulisan
> ilmiah · peer-review assistance · menjaga provenance · menjalankan ethics
> governance · mendukung lab automation di masa depan.

> Sekarang HumanVerse memiliki kemampuan lengkap untuk memahami manusia · ruang ·
> tubuh · dunia, dan **membantu menciptakan pengetahuan baru**.

---

> ⭐⭐ **Ringkasan lima kemampuan itu tepat dan bisa diperiksa satu per satu** —
> dan ia memakai kata kerja yang sama dengan sepuluh kata kerja §18.2, jadi
> keduanya bisa disandingkan tanpa penerjemahan.

> ⚠️ **`membaca dan mengindeks jutaan paper` adalah satu-satunya butir DoD yang
> berangka, dan angkanya menentukan biaya seluruh fase.** Jutaan naskah lengkap
> berarti penyimpanan, penguraian, dan penyematan pada skala yang berbeda dari
> apa pun di repo ini — sementara **B-35** ([#127](../../issues/127)) sudah
> mencatat `world_observations` tumbuh tanpa pembatas di PostgreSQL + Redis
> (**H-12**), dan §19.31 tidak menyebut retensi. ⭐ Bedanya menguntungkan di
> sini: **metadata dan naskah bisa dipisah** — `Crossref`/`OpenAlex` memberi
> metadata jutaan makalah tanpa naskahnya, dan yang perlu diurai penuh hanya
> yang benar-benar dipakai. Yang perlu dinyatakan: **indeks penuh ≠ salinan
> penuh.** Lihat **B-37**.

---

## Penutup — Phase 20

> Ini menjadi fondasi langsung untuk **Phase 20 — HumanVerse Civilization
> Platform**, yaitu **fase terakhir** yang menyatukan seluruh sistem menjadi
> infrastruktur AI-native untuk individu, organisasi, kota, dan masyarakat pada
> skala global.

---

> ⭐⭐⭐ **"Fase terakhir" adalah PERTAMA kalinya sebuah ujung dinyatakan sejak
> §10.41 — dan kalau pemilik menegaskannya, ia menutup pertanyaan ketiga
> [#101](../../issues/101).**
>
> **E-128** ([#108](../../issues/108)) menyimpulkan petanya terbuka-ujung
> **dengan perbuatan**: empat naskah berturut-turut menambah satu fase di
> kalimat penutup, tanpa satu pun menyebut ujungnya. Kalimat ini membalikkannya.
>
> ⇒ Usul yang tidak berubah dan kini bisa dilaksanakan sekaligus: **beri VERSI
> pada peta fase** — `v1` (15 fase, §10.41) dan **`v3` (dua puluh fase,
> tertutup)** — lalu **tuliskan kedua puluhnya sebagai daftar di satu berkas.**
> Selama daftar itu tidak ada, *"roadmap 20 fase"* tetap tidak bisa dibuka oleh
> siapa pun, termasuk oleh naskah berikutnya. Lihat **E-144** / [#132](../../issues/132) dan **A-34** / [#133](../../issues/133).

> ⚠️ **Dan Phase 20 mewarisi seluruh cakupan `Civilization Intelligence` yang
> naskah 22 berikan kepada Phase 19** — `Human ↕ Family/Community ↕ Organization
> ↕ City ↕ Country ↕ Global Economy ↕ Technology ↕ Environment ↕ AI Agents ↕
> Robotics ↕ Civilization`. Tangga sebelas tingkat itu sudah tercatat sebagai
> **urutan KEEMPAT** untuk satu sumbu cakupan (**E-141** /
> [#130](../../issues/130)). Fase terakhir yang berisi tangga yang belum tetap
> bentuknya adalah tempat yang paling mahal untuk menemukannya.
