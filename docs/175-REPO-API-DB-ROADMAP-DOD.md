# 175 — §10.34–§10.41 Repository, API, Database, Roadmap, DoD & Peta Fase Baru

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.34 — Repository Architecture

```
multimodal/
├── ingestion/      text · image · audio · video · document · sensor · spatial
├── perception/     vision · speech · audio · video · document · sensor · spatial
├── embeddings/     text · image · audio · video · multimodal
├── fusion/         early · intermediate · late · hybrid
├── retrieval/      visual · audio · multimodal · cross-modal
├── document-intelligence/
├── wearable-intelligence/
├── spatial-intelligence/
├── perception-state/
├── provenance/
├── confidence/
├── privacy/
├── edge/
└── model-router/
```

---

> 🛑 **Pohon tingkat-atas ketujuh, dan LIMA foldernya menduplikasi pohon
> lain.**
>
> | `multimodal/` | Sudah ada di |
> |---|---|
> | `privacy/` | `security/privacy/` (§8.39) |
> | `model-router/` | `intelligence/model-router/` (naskah 5 §4, **dihapus** §9.38 — lihat **E-79**) |
> | `confidence/` | `intelligence/understanding/uncertainty/` (§9.38) |
> | `embeddings/` | `research/embeddings/` (naskah 9) + lapisan vektor `data-platform/` |
> | `retrieval/` | lapisan retrieval `data-platform/` (§7.16) |
>
> Riwayat pohon tingkat-atas sekarang: `humanverse-x/` (monorepo, **H-10**) ·
> `research/` · `developer-platform/` · `data-platform/` · `security/` ·
> `intelligence/` (didefinisikan ulang) · `multimodal/`. **Enam naskah
> berturut-turut menyentuh struktur repo**, dan Sprint 0 tugas 0.1 masih
> menunggu ([#55](../../issues/55)).
>
> ⭐ Aturan pembagian yang saya usulkan untuk `research/` vs `intelligence/`
> (*mencari cara* vs *menjalankan di produksi*) tidak menolong di sini —
> `multimodal/` adalah produksi juga. Yang membedakannya hanya **jenis
> masukan**, dan itu argumen lemah untuk pohon tersendiri. Kandidat yang lebih
> masuk akal: `intelligence/perception/`. Lihat **E-90**.

> ⭐ **`provenance/`, `confidence/`, dan `edge/` sebagai folder tersendiri
> adalah keputusan yang baik** — ketiganya lintas-modality, dan menempatkannya
> di tingkat atas mencegah tujuh salinan di tujuh pipeline.

---

## §10.35 — API Layer

```
POST /v1/perception/image        POST /v1/vision/analyze
POST /v1/perception/audio        POST /v1/audio/transcribe
POST /v1/perception/video        POST /v1/video/analyze
POST /v1/perception/document     POST /v1/document/extract
GET  /v1/perception/{id}
                                 POST /v1/multimodal/search
GET  /v1/spatial/scene           POST /v1/multimodal/fuse
GET  /v1/spatial/objects
```

---

> ⚠️ **`/v1/...` vs `/api/v1/...`** — [`../spec/04`](../spec/04-API-CONTRACTS.md)
> memakai `/api/v1/`, sementara naskah 7, 10, dan sekarang 14 memakai `/v1/`.
> **Tiga naskah lawan satu spesifikasi**; yang menyimpang adalah spesifikasi
> saya, dan sebaiknya diselaraskan sebelum endpoint pertama ditulis.

> ⚠️ **Semua endpoint persepsi adalah unggah berkas** — dan tak satu pun dari
> empat belas naskah membahas batas ukuran, jenis berkas yang diterima, virus
> scanning, atau apa yang terjadi pada berkas mentah setelah diproses. Yang
> terakhir paling menentukan untuk **C-9**: `/v1/perception/image` menerima
> foto, dan `GET /v1/perception/{id}` menyiratkan foto itu **tetap ada**.

---

## §10.36 — Database Extension

**Operational:** `perceptions` · `observations` · `visual_observations` ·
`audio_observations` · `video_observations` · `document_observations` ·
`sensor_observations` · `spatial_observations`

**Embeddings:** `visual_embeddings` · `audio_embeddings` ·
`video_embeddings` · `multimodal_embeddings`

**Spatial:** `spatial_objects` · `spatial_relationships` · `spatial_scenes` ·
`spatial_maps`

---

> 🛑 **Enam belas tabel baru — dan hitungannya sekarang menjadi 59.**
>
> | | Tabel |
> |---|---|
> | V0 ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)) | **23** |
> | + Fase 8 §8.40 (20 baru) | 43 |
> | + Fase 10 §10.36 (16 baru) | **59** |
>
> Bertaut **A-25** / [#58](../../issues/58). Yang perlu ditegaskan: **nol dari
> enam belas ini dibutuhkan V0** — tidak ada satu pun fitur V0 yang menyentuh
> kamera, mikrofon, dokumen, atau sensor.

> ⚠️ **Tujuh tabel `*_observations` di samping satu `observations`** adalah pola
> tabel-per-jenis yang cepat menjadi mahal: setiap kueri lintas-modality
> menjadi tujuh `UNION`. Alternatifnya satu tabel `observations` dengan
> `modality` + `payload jsonb` — sama seperti `events` yang sudah memakai
> `payload jsonb` untuk 22 jenis event. Konsisten dengan yang sudah ada, dan
> jauh lebih murah untuk fusi lintas-modality yang justru menjadi inti fase
> ini.

---

## §10.37 — Implementation Roadmap

| Milestone | Isi |
|---|---|
| **M10.1** Multimodal Foundation | Ingestion · Canonical Object · Metadata · Storage · Privacy |
| **M10.2** Vision Intelligence | Object · Scene · Human · Pose · Image Embedding |
| **M10.3** Audio & Voice | VAD · ASR · Speaker · Audio Events · Voice Interface |
| **M10.4** Video Intelligence | Frame Processing · Tracking · Action · Temporal Events |
| **M10.5** Document Intelligence | OCR · Layout · Tables · Entity Extraction · Embeddings |
| **M10.6** Multimodal Embeddings | Image · Text · Audio · Video · Cross-modal Retrieval |
| **M10.7** Multimodal Fusion | Early · Intermediate · Late · Hybrid |
| **M10.8** Spatial Intelligence | Depth · 3D · Spatial Graph · Scene Mapping · Localization |
| **M10.9** Wearable & Sensor | Wearable · IoT · Environmental · Sensor Fusion · State |
| **M10.10** Cognitive Integration | Perception → Context → Memory → Understanding → Reasoning → Decision |

---

> ⭐ **Awalannya membawa nomor fase — lebih baik daripada `C1`–`C10` naskah
> 13.** Praktiknya sekarang 2 dari 3: `S8.x` ✅ · `C1–C10` ❌ · `M10.x` ✅.

> ⚠️ **Tapi `M10.1` bertabrakan dengan milestone GitHub repo ini sendiri.**
> Repo memakai **M1 · M2 · M3** untuk *Keputusan sebelum kode* · *Blueprint &
> Platform* · *Sebelum ada pengguna nyata*. *"M10"* akan dibaca sebagai
> milestone kesepuluh. Dan naskah 12 memakai **S** untuk hal yang sama
> (*sprint*), naskah ini memakai **M** (*milestone*) — dua huruf, satu
> gagasan. Usul: **`S10.1`–`S10.10`**. Lihat **E-91** /
> [#56](../../issues/56).

> 🛑 **`M10.1` memuat `Privacy`, tetapi on-device (§10.28) tidak ada di
> milestone mana pun.** Seperti dicatat di berkas [`173`](173-PRIVACY-ON-DEVICE-MODEL-ROUTER.md):
> untuk kamera dan mikrofon, pemrosesan lokal bukan optimasi melainkan
> prasyarat. Menempatkan Vision di M10.2 sementara `edge/` tidak dijadwalkan
> berarti versi pertama akan mengirim bingkai mentah ke cloud.

---

## §10.38 — Definition of Done

**Perception** — memahami image · video · audio · speech · dokumen; menerima
sensor; memahami spatial data.

**Intelligence** — object detection · scene understanding · activity
recognition · speech recognition · temporal understanding · document
understanding · multimodal embeddings · cross-modal retrieval.

**Cognitive Integration** — perception → context · memory · behavior · state ·
reasoning · recommendation.

**Safety** — granular permission · consent · privacy filtering · retention ·
encryption · provenance · confidence · audit trail · on-device processing.

---

> ⭐⭐ **Bagian Safety adalah yang terkuat dari tiga Definition of Done
> berturut-turut** (§8.45, §9.40, §10.38). Sembilan butir, dan dua di antaranya
> **belum pernah ada di DoD mana pun**: `provenance` dan `on-device
> processing`. Keduanya tepat untuk fase ini.
>
> ⭐ Perhatikan juga bahwa Safety tidak menyusut ketika fasenya bukan tentang
> keamanan — pola yang sama seperti §9.40 yang tetap membawa *"respect
> permissions"* dan *"ask for confirmation"*.

> ⚠️ **Tetapi ini DoD pertama dari tiga yang tidak bisa dijawab ya/tidak.**
> §8.45 dan §9.40 memberi kalimat yang bisa diperiksa (*"Data can be deleted"*,
> *"Handle uncertainty"*). Di sini sebagian besar adalah **nama kemampuan**:
> *"object detection"*, *"scene understanding"* — selesai pada akurasi berapa,
> pada data siapa, diuji bagaimana? `evaluation.gates`
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) punya bentuknya
> (`safety >= 0.95`); daftar ini belum memakainya.

> ⚠️ **Tidak ada satu butir pun tentang menghapus atau memperbaiki.** Ada
> `retention` dan `audit trail`, tetapi tidak ada *"perception data can be
> deleted"* maupun *"a wrong observation can be corrected"* — padahal §10.22
> membuat satu deteksi keliru mengendap jadi pola. Ini ketiga kalinya `Edit`
> absen dari kriteria selesai (**E-74** / [#64](../../issues/64)).

---

## §10.39 — Posisi Phase 10

```
                    HUMANVERSE X
             ┌───────────┴───────────┐
         PERCEPTION               COGNITION
      ┌──────┼──────┐          ┌─────┼─────┐
    Vision Audio Spatial     Memory Reasoning
      └──────┼──────┘          └─────┼─────┘
             └──────────┬────────────┘
                  HUMAN STATE → WORLD MODEL → DIGITAL TWIN
                  → DECISION INTELLIGENCE → AGENTS → ACTION
                  → FEEDBACK → LEARNING
```

---

## §10.40 — Hubungan dengan AetherScan

> Ada hubungan menarik dengan proyek Anda yang lain, **AetherScan**, tetapi
> saya **tidak akan mencampurkan keduanya menjadi satu sistem**.

```
                    HUMANVERSE
                 Perception Layer
        ┌────────────────┼────────────────┐
      Camera          Wearable        AetherScan
        │                │                │
      Vision          Sensors       RF/Wi-Fi Sensing
        └────────────────┼────────────────┘
                  Multimodal Fusion → Spatial Intelligence → Human State
```

> **AetherScan = salah satu "sensor/indera" HumanVerse, bukan HumanVerse itu
> sendiri.** Ini justru membuat kedua proyek memiliki boundary yang jauh lebih
> profesional.

---

> ⭐⭐ **Keputusan ini benar, dan penting bahwa ia diambil sekarang.** Dua
> proyek yang digabung karena keduanya menarik adalah cara tercepat membuat
> keduanya tidak selesai. Memposisikan AetherScan sebagai **penyedia sensor**
> memberi keduanya kontrak yang jelas: HumanVerse menerima *perception object*
> §10.3, dan tidak perlu tahu bagaimana ia dihasilkan.
>
> Ini juga catatan pertama tentang AetherScan di seluruh repo — sebelumnya
> tidak pernah disebut.

> 🛑 **Tetapi RF/Wi-Fi sensing membawa masalah izin yang berbeda jenis dari
> kamera, dan ia perlu ditulis sekarang justru karena keputusan batasnya sudah
> benar.**
>
> | | Kamera | RF/Wi-Fi sensing |
> |---|---|---|
> | Terlihat sedang aktif | ✅ ada lampu, ada lensa | ❌ tidak ada indikator |
> | Bisa ditutup | ✅ | ❌ |
> | Bekerja dalam gelap | sebagian | ✅ |
> | **Menembus dinding** | ❌ | ✅ |
> | **Menangkap orang lain** | ya, bila terlihat | **ya, siapa pun di jangkauan** |
>
> Baris terakhir yang menentukan. Kamera menangkap siapa yang ada di depannya
> dan orang itu **bisa tahu**. RF sensing menangkap **siapa pun di dalam
> jangkauan** — tamu, anak, pasangan, tetangga di balik dinding — tanpa satu
> pun dari mereka bisa menyadarinya, apalagi menyetujuinya.
>
> Model izin HumanVerse tidak punya kata untuk ini: `scope: user-owned` (§8.7)
> hanya bisa menyatakan data milik penggunanya, dan tujuh jenis identity §8.4
> tidak memuat satu pun manusia yang bukan pengguna (**C-10** /
> [#40](../../issues/40)). Selama ini butir itu tentang *Coaches* — masalah
> masa depan. RF sensing membuatnya menjadi masalah **hari pertama alat itu
> dinyalakan**. Lihat **C-18** / [#76](../../issues/76).

---

## §10.41 — Peta fase baru

> Dengan Phase 10 selesai secara arsitektural, urutan besarnya menjadi:

| Fase | Isi |
|---|---|
| 1–4 | Foundation |
| 5 | Research Lab |
| 6 | Developer Platform |
| 7 | Data & AI Infrastructure |
| 8 | Safety / Security / Privacy |
| 9 | Cognitive Architecture |
| 10 | Multimodal Perception |
| **11** | **Autonomous Agent & Agency Layer** |
| **12** | **Digital Twin & World Simulation** |
| **13** | **HumanOS** |
| **14** | **Ecosystem & Marketplace** |
| **15** | **Global Intelligence Platform** |

> Phase 11 akan menjadi sangat penting: **merencanakan, menggunakan tools,
> menjalankan workflow, berkolaborasi antar-agent, meminta izin, mengambil
> tindakan terbatas, mengamati hasilnya, lalu belajar dari outcome** — fondasi
> untuk menjadikan HumanVerse sebagai **Agentic Human Operating System**.

---

> ⭐ **Ini menutup A-26 / [#66](../../issues/66): petanya diganti, bukan
> digeser.** Dua belas fase jadi **lima belas**, dan tiga pertanyaan issue itu
> terjawab sekaligus. Tiga blok akhirnya punya rumah yang jelas:
> **Agency → Phase 11** (menjawab kapan **B-19** / [#47](../../issues/47)
> diuji), **Digital Twin → Phase 12**, **Marketplace → Phase 14** (rumah untuk
> **A-15/C-7** / [#24](../../issues/24)).

> 🛑 **Tetapi empat blok dari peta lama TIDAK punya rumah baru:**
>
> | Blok peta naskah 8 | Isinya | Nasib |
> |---|---|---|
> | Phase 9 **Enterprise & Business** | Team Workspace · Enterprise Admin · Family Mode · **Subscription** · **Company Wellness** · **Revenue Platform** | ❌ hilang |
> | Phase 10 **AI Automation** | Cross-App · Calendar · Email Automation | ⚠️ sebagian ke Phase 11 (Agency) |
> | Phase 11 **HumanVerse Cloud** | Multi-region · DR · Edge Computing | ❌ hilang (`edge/` ada di §10.34) |
> | Phase 12 **Blueprint Implementation** | spec pada skala penuh | ❌ hilang |
>
> Yang paling berkonsekuensi: **seluruh lapisan bisnis lenyap dari peta.**
> *Subscription* dan *Revenue Platform* tidak muncul di satu pun dari lima
> belas fase. Sementara itu **H-6** mengakui biaya inferensi berlipat, **A-6**
> (tangga harga) masih terbuka, dan **E-41** mencatat `Billing` muncul entah
> dari mana. Sebuah proyek dengan model biaya yang diakui dan **tanpa fase
> pendapatan**. Lihat **A-27** / [#73](../../issues/73).

> 🛑🛑 **Dan ini menggerus H-13 — rencana kanonik kembali menjadi Phase, bukan
> V0–V6.**
>
> Butir **A-18** ditutup sebagai **H-13** dengan alasan yang jelas: naskah 5
> memakai tangga V dari awal sampai akhir dan **tidak menyebut Phase 1/2/3
> satu kali pun**, sehingga *"Phase 1–3 menjadi sejarah penyusunan, bukan
> rencana kerja"*.
>
> §10.41 memberi **lima belas fase sebagai urutan besar pekerjaan**, dan
> naskah ini tidak menyebut V0–V6 sama sekali. Dua rencana kanonik lagi — dan
> yang lebih menentukan: **V0 tidak punya tempat di dalamnya.** V0 adalah
> satu-satunya lingkup tertutup yang pernah ditetapkan (12 fitur, 23 tabel,
> 51 tugas, [`../spec/07`](../spec/07-BACKLOG-V0.md)); "Phase 1–4 Foundation"
> tidak memetakan ke sana.
>
> Ini H ketiga yang tergerus setelah **H-8** (dibatalkan) dan **H-10**
> (monorepo). Polanya jelas dan layak diingat: **keputusan yang ditutup perlu
> ditinjau ulang tiap beberapa naskah.** Lihat **E-87** /
> [#72](../../issues/72).
