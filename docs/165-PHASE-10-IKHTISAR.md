# 165 — Phase 10: Multimodal Intelligence & Perception (ikhtisar naskah keempatbelas)

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Penomoran

Naskah ini **menomori bagiannya sendiri dengan awalan fase** — `10.1`–`10.41`.
Ini pertama kalinya pemilik memakai awalan berfase untuk bagian naskah, dan
berkas rapi memakainya apa adanya sebagai **`§10.1`–`§10.41`** (tanpa perlu
menerjemahkan seperti `§8.n` dan `§9.n`).

---

## Posisi pemilik

> Phase 9 membuat HumanVerse memiliki **"otak kognitif"**. Phase 10 sekarang
> membangun **"indra"** agar otak tersebut dapat memahami dunia nyata melalui
> teks, gambar, suara, video, sensor, wearable, dokumen, dan ruang.

**Core Principle:**

> ## HumanVerse should not only understand what a human tells it. It should understand what is happening around the human.

```
                    ┌──────────────────────────┐
                    │       HUMANVERSE         │
                    │    Cognitive Runtime     │
                    └────────────┬─────────────┘
                                 │
                         Perception API
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
             Vision            Audio            Video
                │                │                │
             Camera             Mic            Camera
                │                │                │
             Images            Speech          Events
                │                │                │
                └────────────────┼────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
           Documents          Sensors           Spatial
              │                  │                  │
            PDF/OCR          Wearables        Location/3D
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                         Multimodal Fusion
                                 │
                         Perception State
                                 │
                       Context Intelligence
                                 │
                     Cognitive Architecture
```

---

> ⭐ **`Perception API` sebagai satu pintu adalah bentuk yang benar** — dan ia
> sejalan dengan **H-19** (§9.31): agent tidak mengambil data sendiri, Context
> Engine menyerahkan paket. Di sini polanya diulang satu lapis lebih rendah:
> tujuh modality masuk lewat satu API, bukan tujuh jalur yang masing-masing
> menyentuh runtime.

> 🛑 **Tetapi kalimat pembuka adalah perubahan lingkup terbesar di empat belas
> naskah, dan konsekuensinya tidak dibahas.** *"Understand what is happening
> **around** the human"* berarti sistem mengamati **ruangan**, bukan lagi hanya
> pengguna — dan ruangan berisi orang lain. Sebelas naskah membangun model izin
> untuk data **satu** orang; `scope: user-owned` (§8.7) secara struktur tidak
> bisa menyatakan apa pun yang lain (**C-10** / [#40](../../issues/40)).
> Lihat **C-17** dan **C-18**.

---

## §10.1 — Tujuan Phase 10

Sebelum Phase 10, HumanVerse memperoleh informasi dari **User Input ·
Database · Events · APIs · Sensors**. Setelah Phase 10:

```
HumanVerse
    │
    ├── See
    ├── Hear
    ├── Read
    ├── Watch
    ├── Sense
    ├── Locate
    ├── Understand Space
    └── Fuse Everything
```

Contoh — user mengirim foto kamar. HumanVerse tidak hanya mengatakan *"Ini
kamar tidur"*, tetapi:

```
Image → Object Detection → Scene Understanding → Spatial Understanding
→ Object Relationship → Context → User Preference → Historical Data
→ Recommendation
```

Kemudian:

> *"Kamar terlihat memiliki meja kerja, tempat tidur, lemari dan area
> penyimpanan. Area meja memiliki beberapa objek yang kemungkinan mengurangi
> ruang kerja efektif. Berdasarkan pola produktivitas Anda, konfigurasi meja
> yang lebih minimal mungkin lebih cocok."*

> Itulah perbedaan **Computer Vision biasa** dengan **HumanVerse Perception
> Intelligence**.

---

> ⭐⭐ **Contoh ini adalah pembelaan terbaik untuk seluruh fase, dan bahasanya
> pun benar.** Perhatikan dua kata: *"kemungkinan mengurangi"* dan *"mungkin
> lebih cocok"* — bentuk **may** yang ditetapkan §9.15, dipakai konsisten di
> naskah berikutnya. Yang membuatnya bukan computer vision biasa bukan
> deteksinya, melainkan **`Historical Data` dan `User Preference` di dua
> langkah terakhir**: jawabannya berbeda untuk dua orang dengan foto yang sama.

---

## §10.2 — Multimodal Input Layer

```
Multimodal Input
├── Text          ├── Camera              ├── Location
├── Image         ├── Wearable            ├── Spatial Data
├── Video         ├── IoT                 ├── 3D Data
├── Audio         ├── Environmental Sensors └── External World Data
├── Speech
└── Documents
```

Setiap input masuk melalui:

```
Input → Ingestion → Validation → Normalization → Metadata Extraction
→ Privacy Check → Modality Processing → Feature Extraction → Embedding
→ Perception Object → Multimodal Fusion
```

---

> ⭐ **`Privacy Check` berdiri sebelum `Modality Processing`** — sebelum
> gambarnya diproses sama sekali. Itu urutan yang benar dan jarang ditulis:
> pemeriksaan izin yang terjadi **setelah** model melihat datanya sudah
> terlambat.

> ⚠️ **Empat belas sumber di daftar, tujuh folder di pohon §10.34.** Speech
> melebur ke audio, Camera ke image/video, Wearable/IoT/Environmental ke
> sensor, Location/3D ke spatial — semuanya wajar. Yang **tidak punya tempat
> sama sekali**: `External World Data`. Pola **E-13** (tabel ≠ folder) yang
> berulang.

---

## §10.3 — Canonical Multimodal Object

```json
{
  "perception_id": "perc_001",
  "user_id": "user_001",
  "modality": "image",
  "source": "camera",
  "timestamp": "2026-09-07T10:00:00Z",

  "content":  { "uri": "...", "hash": "..." },
  "context":  { "location": "...", "device": "...", "activity": "working" },

  "observations": [
    { "type": "object", "label": "laptop", "confidence": 0.98 }
  ],

  "embeddings": { "visual": "...", "semantic": "..." },
  "privacy":    { "classification": "sensitive", "retention": "30d" }
}
```

> Semua modality akhirnya berbicara dalam **bahasa internal HumanVerse yang
> sama**.

---

> ⭐⭐ **Blok `privacy` yang menempel pada objeknya sendiri adalah penerapan
> §7.24 yang paling langsung sejauh ini.** `classification` + `retention` ikut
> dengan datanya, jadi aturan retensi bisa ditegakkan tanpa tabel terpisah.
> ⚠️ Yang **hilang** dari empat field §7.24: **`purpose`** dan
> `consent_required`. Tanpa `purpose`, penegakan `data.purpose ⊆
> consent.purpose` (**B-22** / [#59](../../issues/59)) tidak bisa dijalankan
> pada data persepsi — justru data paling sensitif yang paling membutuhkannya.

> ⚠️ **`timestamp` tunggal, sementara amplop event [`../spec/03`](../spec/03-EVENT-CONTRACTS.md)
> memisahkan `occurred_at` dari `recorded_at`.** Untuk persepsi bedanya nyata:
> foto yang diambil kemarin dan diunggah hari ini punya dua waktu yang
> berbeda, dan analisis temporal §10.11 bergantung pada yang pertama.

> ⚠️ **`retention: "30d"` bertabrakan dengan §10.22**, yang menuntut pola
> muncul *"repeated over 30 days"*. Kalau pengamatan mentah dibuang pada hari
> ke-30, pola 30 hari tidak akan pernah selesai terbentuk. Salah satunya harus
> berubah — kemungkinan besar yang benar: **pengamatan mentah luruh cepat,
> ringkasannya yang bertahan** (§7.26 *raw pendek, agregat panjang*).

---

## §10.4 — Perception Pipeline

```
RAW INPUT → Ingestion → Preprocessing → Modality Detection
→ Feature Extraction → Semantic Understanding → Entity Detection
→ Relationship Detection → Temporal Analysis → Context Association
→ Confidence Estimation → Multimodal Fusion → Perception State
→ Cognitive Runtime
```

---

> ⭐ **`Confidence Estimation` sebagai langkah pipeline tersendiri**, bukan
> sebagai field yang diisi belakangan. Itu yang membuat §10.24 bisa menegakkan
> aturan *"observasi 0,97 dan 0,38 tidak boleh diperlakukan sama"*.

> ⚠️ **Tiga belas langkah untuk setiap masukan.** Untuk satu foto yang diunggah
> pengguna, itu wajar. Untuk aliran kamera yang berjalan terus (§10.11), tiga
> belas langkah per bingkai adalah biaya yang harus dijawab **sebelum**
> dibangun — dan jawabannya kemungkinan besar ada di §10.28 (proses di
> perangkat) dan §10.29 (jangan kirim semuanya ke LLM).
