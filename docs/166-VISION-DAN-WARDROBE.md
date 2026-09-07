# 166 — §10.5–§10.7 Vision Intelligence, Human Vision & Wardrobe Vision

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.5 — Vision Intelligence

```
Vision Intelligence
├── Object Detection      ├── Facial Analysis        ├── Visual Search
├── Object Classification ├── Gesture Recognition    ├── Spatial Relationships
├── Object Tracking       ├── OCR                    └── Visual Context
├── Scene Understanding   ├── Visual Question Answering
├── Image Classification  ├── Image Embedding
├── Image Segmentation    ├── Visual Similarity
├── Pose Estimation
└── Human Detection
```

Namun kita harus memisahkan:

| Tingkat | Contoh |
|---|---|
| **Perception** | *"Ada seseorang berdiri."* |
| **Interpretation** | *"Kemungkinan sedang menunggu."* |
| **Inference** | *"Kemungkinan akan pergi."* |

> Semakin tinggi level inferensi, semakin tinggi kebutuhan **confidence** dan
> **validation**.

---

> ⭐⭐⭐ **Tiga tingkat ini adalah sumbangan konseptual terbesar naskah ini, dan
> ia berlaku jauh di luar penglihatan.** Selama empat belas naskah, setiap
> kesimpulan sistem diperlakukan sebagai satu jenis benda dengan satu angka
> `confidence` di sebelahnya. Tangga ini menyatakan bahwa **jarak sebuah klaim
> dari datanya** adalah sifat yang berdiri sendiri:
>
> ```
> Perception     jarak 0  — terbaca langsung dari sensor
> Interpretation jarak 1  — tafsir atas yang terbaca
> Inference      jarak 2  — dugaan tentang yang belum terjadi
> ```
>
> Ia menjelaskan sesuatu yang **B-15** keluhkan sejak naskah 1: `"energy":
> 0.62` terlihat sama presisinya dengan `"steps": 8420`, padahal yang satu
> Inference dan yang lain Perception. Dua angka dengan bentuk sama, jarak
> berbeda.
>
> Usul yang mengikuti langsung: **setiap nilai turunan membawa `level`**
> (`perception` / `interpretation` / `inference`), dan **ambang confidence
> §9.33 berbeda per tingkat** — inference menuntut ambang lebih tinggi
> daripada perception untuk boleh dinyatakan. Itu melengkapi
> [#34](../../issues/34) dengan sumbu yang belum pernah ada.

> 🛑 **`Facial Analysis` masuk daftar tanpa satu kalimat pun tentang
> batasnya.** Wajah adalah kategori data khusus (GDPR Pasal 9; BIPA di
> Illinois) — **C-1** sudah mencatatnya, dan Level 4 klasifikasi data masih
> kosong (**G-6** / [#57](../../issues/57)) justru karena kandidat utamanya
> adalah ini. Analisis wajah juga berbeda dari deteksi manusia: yang satu
> menghitung berapa orang, yang lain **mengenali siapa**. Naskah tidak
> membedakan keduanya. Lihat **C-17** / [#75](../../issues/75).

---

## §10.6 — Human Vision

```
Human
├── Presence      ├── Gesture       ├── Interaction
├── Position      ├── Clothing      └── Object Relationships
├── Pose          ├── Accessories
├── Activity      ├── Environment
```

```
Camera → Person Detection → Pose → Activity → Context → Behavior Model
```

Tetapi jangan langsung *"User sedang malas"*. Lebih aman:

```
Observed:
movement low
activity duration high
posture unchanged

Inference:
possible inactivity

Confidence:
0.71
```

---

> ⭐⭐ **Ini kali ketiga berturut-turut prinsip anti-karakterisasi muncul dengan
> kata yang hampir sama.** §9.35 (*"jangan langsung menyimpulkan **User
> malas**"* ketika rekomendasi tidak dikerjakan) · §9.4 (*Preference ≠
> permanent identity*) · dan sekarang di jalur penglihatan. Tiga naskah, tiga
> konteks berbeda, satu arah — salah satu prinsip paling stabil di proyek ini.
>
> Bentuknya juga tepat: `Observed` memisahkan apa yang terbaca dari
> `Inference`, persis tangga §10.5.

> 🛑 **Tetapi rantai `Camera → … → Behavior Model` menuntut kamera menyala
> terus-menerus, dan itu jenis pengamatan yang belum pernah ada di empat belas
> naskah.** *"activity duration high"* dan *"posture unchanged"* tidak bisa
> diketahui dari satu foto — keduanya menuntut **pengamatan berkelanjutan**.
> §10.11 mengukur 90 menit, §10.25 mengukur 118 menit, §10.22 menuntut
> pengulangan **30 hari**.
>
> **C-1** menyangkut foto yang dikirim pengguna. Ini lain: **kehadiran dan
> perilaku seseorang di dalam rumahnya sendiri, dipantau berminggu-minggu.**
> Lihat **C-17** / [#75](../../issues/75).

---

## §10.7 — Wardrobe Vision

```
Wardrobe Image → Person Segmentation → Clothing Detection
→ Garment Classification → Color → Pattern → Material → Style
→ Brand/Object Recognition → Outfit Composition → Wardrobe Graph
```

```
Outfit
├── Top       ├── Outerwear
├── Bottom    ├── Accessories
├── Shoes     └── Grooming
```

Kemudian masuk ke **Preference Model + Weather + Occasion + Calendar + Trend
Intelligence + Historical Feedback**, sehingga *Outfit Recommendation* menjadi
benar-benar contextual.

---

> ⭐ **`Grooming` muncul lagi — sebagai komponen outfit, bukan sebagai agent.**
> Butir **E-5**/**E-35** melacak GroomingAgent yang hilang, kembali, lalu
> hilang lagi (**H-8 dibatalkan** karena itu). Di sini ia hadir sebagai bagian
> dari komposisi outfit. Itu tempat yang lebih masuk akal daripada agent
> tersendiri, dan sebaiknya dicatat sebagai penyelesaian yang mungkin untuk
> **A-20** / [#4](../../issues/4): Grooming = **fitur di dalam Fashion**, bukan
> modul sendiri.

> 🛑 **B-17 tidak hanya bertahan — ia menjadi struktural.** Butir itu mencatat
> bahwa satu salah hitung Wardrobe Vision (*"kamera melihat 12 shirts"*)
> mengendap di Wardrobe Graph dan meracuni setiap rekomendasi sesudahnya.
>
> Sekarang polanya berlaku untuk **setiap aliran persepsi**, bukan hanya
> lemari: §10.22 mengubah deteksi berulang menjadi *pola perilaku* setelah 30
> hari. Sebuah deteksi yang salah secara **sistematis** — kamera yang selalu
> salah membaca posisi duduk karena sudut pemasangannya — tidak akan pernah
> terkoreksi oleh pengulangan. Ia justru **diperkuat** olehnya, karena
> §9.8 menaikkan kepercayaan berdasarkan **frekuensi**.
>
> Konsolidasi berbasis pengulangan (§9.8) adalah pertahanan yang baik terhadap
> kesalahan **acak**, dan tidak berdaya sama sekali terhadap kesalahan
> **sistematis**. Bedanya belum pernah ditulis. Lihat **B-25** /
> [#77](../../issues/77) dan [#29](../../issues/29).

> ⚠️ **`Brand Recognition` membawa kepentingan komersial masuk ke penglihatan.**
> Butir **E-50** mencatat *Brands* sebagai peserta ekonomi yang membawa
> kepentingan komersial ke dalam rekomendasi yang sudah berjanji *"popular ≠
> suitable for the user"*. Mengenali merek dari foto lemari seseorang membuat
> data itu **ada** — dan begitu ada, ia bernilai bagi pihak lain. Aturan
> **§8.10** (*purpose limitation*) adalah satu-satunya yang menahannya, dan ia
> harus disebut di sini.
