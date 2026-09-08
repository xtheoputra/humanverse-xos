# 254 — §18.26–§18.29 Arsitektur, Repository, Data Model & API

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.26 — Global Intelligence + HumanVerse

> Personal intelligence **ME** sekarang berada di dalam **WORLD**.

```
GLOBAL WORLD MODEL → REGIONAL MODEL → CITY MODEL → ORGANIZATION MODEL
   → INDUSTRY MODEL → PERSONAL WORLD MODEL → DIGITAL TWIN → HUMANOS
```

---

> ⭐⭐ **`PERSONAL WORLD MODEL` sebagai lapisan tersendiri, terpisah dari
> `DIGITAL TWIN`, adalah pembedaan yang halus dan benar.**
>
> Kembaran digital adalah model **tentang orangnya**; model dunia pribadi adalah
> model **tentang dunia sebagaimana ia menyentuh orang itu** — industri tempat
> ia bekerja, kota tempat ia tinggal, harga yang ia bayar. Dua hal yang berbeda,
> dan menaruhnya sebagai dua lapisan mencegah dunia ditulis ke dalam profil
> orangnya.

> 🛑 **Tetapi urutannya lagi-lagi berbeda dari §18.11 — sumbu yang sama, urutan
> KETIGA.**
>
> | Tempat | Urutan tengah |
> |---|---|
> | §18.11 diagram 1 | Organization → **City → Industry** → Regional |
> | §18.11 diagram 2 | Company → **Industry → City** |
> | **§18.26** | Regional → **City → Organization → Industry** |
>
> Tiga susunan untuk satu tangga, dalam satu naskah. Dan §18.26 satu-satunya
> yang menaruh `Regional` di atas `City` — yang secara geografis benar, dan
> yang justru membuat dua diagram §18.11 terlihat keliru. Lihat **E-141** / [#130](../../issues/130).

> 🛑 **Dan ini diagram KEDUA di naskah ini tanpa `GOVERNANCE MESH` maupun
> `ACTION GATEWAY`** (§18.3 yang pertama, §18.34 yang ketiga). Rantainya
> berakhir di `HUMANOS` — sistem operasi yang menjalankan agent — sehingga
> jalur dari model dunia ke tindakan menjadi lurus tanpa satu gerbang pun
> tergambar. §14.69 menetapkan keduanya wajib. Naskah keempat berturut-turut.
> Lihat **E-143** / [#125](../../issues/125).

---

## §18.27 — Repository Architecture

```
global-intelligence/
├── world-model/            ├── organization-intelligence/  ├── provenance/
├── world-intelligence/     ├── city-intelligence/          ├── information-integrity/
├── knowledge-federation/   ├── industry-intelligence/      ├── security/
├── intelligence-network/   ├── global-risk/                ├── privacy/
├── collective-intelligence/├── early-warning/              ├── governance/
├── simulation/             ├── causal-intelligence/        ├── agents/
├── trust/                  ├── reputation/                 ├── protocols/
├── sdk/                    └── research/
```

Isi yang dirinci: `world-model/` (entities · relationships · events · temporal ·
states · resources) · `world-intelligence/` (ingestion · normalization ·
entity-resolution · event-detection · trend-detection · anomaly-detection ·
forecasting) · `knowledge-federation/` (protocols · exchange · provenance ·
synchronization) · `intelligence-network/` (nodes · discovery · routing ·
communication · federation) · `collective-intelligence/` (collaboration ·
consensus · aggregation · debate · synthesis) · `agents/` (world · economy ·
science · climate · city · industry) · `protocols/` (HINP · intelligence-message ·
capability-protocol).

---

> ⭐⭐ **`world-intelligence/` dipecah menjadi tujuh langkah yang PERSIS sama
> dengan pipeline §18.4** — `ingestion`, `normalization`, `entity-resolution`,
> `event-detection`, `trend-detection`, `anomaly-detection`, `forecasting`.
> Struktur direktori yang mencerminkan rantai pemrosesannya adalah bentuk yang
> membuat kode sulit ditulis di tempat yang salah. Ini pertama kalinya sebuah
> pohon fase disusun mengikuti pipeline-nya sendiri, bukan mengikuti daftar
> fitur.

> 🛑 **Tetapi `global-intelligence/` menggerus H-10 untuk KEDELAPAN kalinya —
> dan ini naskah KESEPULUH berturut-turut yang menyentuh struktur repo.**
>
> Duplikasi dengan pohon yang sudah ada:
>
> | Direktori | Sudah ada di |
> |---|---|
> | `simulation/` | `spatial-os/` · `robotics/` · `health-bio/` · Phase 12 — **kelima kalinya** |
> | `agents/` | pohon tingkat-atas sejak naskah 2 |
> | `research/` | pohon tingkat-atas sejak naskah 9 · juga di `health-bio/` |
> | `sdk/` | `developer-platform/` (naskah 10) |
>
> Dan **pohon keamanan menjadi SEMBILAN**: `security/` · `agent-security/` ·
> `spatial-os/safety/` · `spatial-os/privacy/` · `robotics/safety/` ·
> `health-bio/safety/` · `health-bio/privacy/` · dan dua di sini.
> **E-127**/**E-129** ([#109](../../issues/109)) mencatat **empat** saja sudah
> membuat aturan impor **§8.42** (*kode agent tidak boleh mengimpor
> `security/`*) tidak punya satu sisi; **E-134** ([#120](../../issues/120))
> mencatat tujuh menjadikannya tak bisa dinyatakan. Sembilan menjadikan
> pertanyaannya tidak bermakna. Lihat **E-139** / [#129](../../issues/129) / [#55](../../issues/55).

> 🛑 **Dua direktori muncul DUA KALI di dalam pohon yang sama.**
>
> `protocols/` ada sebagai anak `knowledge-federation/` **dan** sebagai pohon
> tingkat pertama; `provenance/` juga — anak `knowledge-federation/` **dan**
> tingkat pertama. Keduanya bukan nama yang mirip, melainkan nama yang identik
> di dua kedalaman.
>
> Ini bukan kerapian: **§18.21 menjadikan provenance sebagai rantai yang
> melintasi seluruh sistem**, jadi menaruhnya sekaligus sebagai komponen umum
> dan sebagai bagian dari federasi berarti dua salinan aturan yang akan
> berbeda. Yang benar hampir pasti: **`provenance/` dan `protocols/` di tingkat
> pertama; `knowledge-federation/` memakainya, tidak memilikinya.**

> ⭐⭐⭐ **`governance/` akhirnya muncul — pertama kalinya sejak diminta di
> naskah 18 — tetapi ia muncul DI DALAM pohon fase, dan itu menghapus gunanya.**
>
> **E-134** ([#120](../../issues/120)) mengusulkan `governance/` sebagai **pohon
> tingkat-atas**, karena tata kelola yang hidup di dalam satu fase hanya bisa
> mengatur fase itu. `global-intelligence/governance/` tidak bisa mengatur
> `robotics/`, `health-bio/`, maupun `agents/` — padahal ketiganya justru yang
> paling membutuhkannya.
>
> Kemunculannya tetap kabar baik: **pemilik menerima bahwa governance adalah
> komponen, bukan sikap.** Yang perlu dilakukan cuma menaikkannya satu tingkat.
> ⭐ Dan penutup §17.56 sudah memberi alasannya (*governance yang semakin ketat
> di setiap level*): tata kelola yang merupakan **fungsi dari tingkat** tidak
> mungkin menjadi milik satu fase.

> ⚠️ **`trust/` dan `reputation/` sebagai dua direktori terpisah membekukan
> pembedaan yang belum pernah ditulis** (§18.17 mendaftar keduanya, §18.28
> memberi dua tabel). Dua direktori untuk perbedaan yang tak terdefinisi akan
> diisi dengan hal yang sama, oleh dua orang yang berbeda.

---

## §18.28 — Data Model

`world_entities · world_relationships · world_events · world_states ·
world_observations · world_trends · world_anomalies` ·
`intelligence_nodes · intelligence_messages · intelligence_networks` ·
`knowledge_sources · knowledge_claims · knowledge_evidence ·
knowledge_provenance` · `organization_models · city_models · industry_models ·
regional_models` · `global_risks · risk_signals · early_warnings` ·
`agent_trust_scores · agent_reputation · agent_capabilities` ·
`federation_requests · federation_consents · federation_policies` ·
`world_simulations · world_scenarios · world_forecasts`

---

> ⭐⭐⭐ **`knowledge_claims` terpisah dari `knowledge_evidence` — klaim dan
> buktinya sebagai dua tabel adalah bentuk yang membuat §18.23 mungkin.**
>
> Sistem yang menyimpan kesimpulan saja tidak bisa mendeteksi kontradiksi,
> karena kontradiksi hidup di antara klaim dan bukti yang mendukungnya, bukan di
> dalam salah satunya. Dan `knowledge_provenance` sebagai tabel ketiga berarti
> penarikan kembali sebuah sumber bisa **merambat** ke semua klaim yang
> berdiri di atasnya.

> ⭐⭐ **`federation_consents` ada** — dan itu satu-satunya tabel persetujuan
> untuk data yang menyeberangi batas organisasi di seluruh repo. Ia yang
> membuat usul di §18.15 (menaruh `Consent` di rantai HINP) bisa dilaksanakan
> tanpa menambah apa pun.

> 🛑 **Tetapi tidak ada registri model — dan §17.35 sudah punya bentuknya.**
> Tiga puluh tabel, nol tempat untuk mendaftarkan `SupplyChainModel v4.2`
> (§18.21). Akibatnya sepuluh metrik §17.36 tidak punya subjek di Phase 18, dan
> `Model` dalam rantai provenance menunjuk ke sesuatu yang tak berbaris.
> Usul: **`world_models`, disalin dari `health_models`.**

> 🛑 **Dan tidak ada satu pun kolom retensi, kedaluwarsa, atau klasifikasi di
> tingkat tabel.** `world_observations` adalah tabel yang paling cepat tumbuh di
> seluruh proyek (**B-35** / [#127](../../issues/127)) dan ia tidak punya aturan buang. `world_events`
> menyimpan `confidence` yang akan berubah ketika §18.23 menemukan kontradiksi,
> tanpa cara menyatakan versi. Bandingkan §17.4 yang mewajibkan `retention` dan
> `sensitivity` **per data**: bentuk itu ada, ia hanya tidak dibawa ke sini.

> ⚠️ `organization_models` · `city_models` · `industry_models` ·
> `regional_models` sebagai empat tabel terpisah membekukan tangga §18.11 yang
> urutannya sendiri belum tetap — dan menutup kemungkinan menambah tingkat
> tanpa migrasi. Satu tabel `scope_models` dengan kolom `scope_type` melakukan
> hal yang sama tanpa membekukannya.

---

## §18.29 — API

```
GET  /v1/world/state          GET  /v1/world/risks        POST /v1/intelligence/query
GET  /v1/world/events         GET  /v1/world/warnings     POST /v1/intelligence/federate
GET  /v1/world/trends         POST /v1/world/simulations  GET  /v1/intelligence/nodes
GET  /v1/world/entities/{id}  GET  /v1/intelligence/agents
GET  /v1/intelligence/provenance/{id}                     POST /v1/intelligence/verify
```

---

> ⭐⭐ **`GET /v1/intelligence/provenance/{id}` menjadikan §18.21 sebagai
> ANTARMUKA, bukan janji internal.**
>
> Selama provenance hanya hidup di dalam mesin, ia bisa diam-diam berhenti
> lengkap tanpa ada yang tahu. Endpoint yang bisa dipanggil siapa pun untuk
> setiap kesimpulan menjadikan ketidaklengkapannya **terlihat**. Ini bentuk
> yang sama dengan §17.5 (*"melihat siapa yang mengakses"*): jaminan yang bisa
> diperiksa dari luar.

> ⭐ **`POST /v1/intelligence/verify` sebagai endpoint tersendiri** memberi
> §18.23 pintu masuk — sesuatu bisa diminta diperiksa, bukan hanya diperiksa
> ketika kebetulan lewat pipeline.

> 🛑 **Tetapi semuanya `/v1/…`, bukan `/api/v1` —
> [`spec/04-API-CONTRACTS.md`](../spec/04-API-CONTRACTS.md) menetapkan
> `/api/v1`.** §17.44 melakukan hal yang sama satu naskah lalu (**E-135**).
> Dua naskah berturut-turut memakai awalan yang berbeda dari kontrak yang sudah
> ditulis; kalau keduanya dikodekan, ada dua pohon rute. Lihat **E-140**.

> ⚠️ **Semua endpoint dunia adalah `GET` tanpa parameter cakupan.**
> `GET /v1/world/risks` mengembalikan risiko **siapa** — dunia, kota pemanggil,
> atau orangnya? §18.24 memasukkan `Personal Risk` ke daftar yang sama, jadi
> satu endpoint bisa mengembalikan dua kelas data dengan sensitivitas yang jauh
> berbeda. Ini bentuk **H-19** ([#62](../../issues/62)) yang sudah ditutup untuk
> agent (*Context Engine yang menyusun, bukan agent yang mengambil*) dan kini
> terbuka lagi lewat HTTP.

> ⚠️ **Tidak ada endpoint untuk menarik atau membantah.** §18.23 bisa
> menghasilkan `UNRESOLVED` dan §18.16 memberi `version` pada knowledge, tetapi
> tidak ada cara bagi sumber untuk menyatakan *"klaim saya salah, tarik"*.
