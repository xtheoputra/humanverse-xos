# 170 — §10.18–§10.20 Spatial Intelligence, 3D & Sensor Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.18 — Spatial Intelligence

Representasi:

```
World
│
├── Building
│   ├── Floor
│   │   ├── Room
│   │   │   ├── Object
│   │   │   └── Human
```

Relationship:

```
Laptop  on      Desk
Desk    inside  Room
Person  near    Desk
```

---

> ⭐ **`on`, `inside`, `near` adalah relasi spasial — jenis keenam di graf, dan
> yang pertama yang tidak berbahaya.** Butir **E-18** melacak dua set relasi
> yang terputus (kausal vs struktural), dan **E-81** mencatat `influences`
> kembali tanpa bukti kausal. Relasi spasial berbeda sifatnya: ia **terukur
> langsung**, tidak menyimpulkan sebab, dan bisa salah tanpa menyesatkan.
>
> Ia juga memberi Knowledge Graph sesuatu yang belum pernah dimilikinya:
> **hierarki tempat**. `World → Building → Floor → Room` adalah pohon, bukan
> graf — dan menyimpannya sebagai pohon (satu kolom induk) jauh lebih murah
> daripada Neo4j yang baru datang di V4.

> ⚠️ **`Human` sebagai simpul di dalam `Room` — dan simpul itu tidak selalu
> penggunanya.** Ini kali keempat naskah ini menyentuh orang lain (setelah
> kamera §10.6, mikrofon §10.8, dokumen §10.12), dan yang ini paling eksplisit:
> peta ruangan yang mencatat **siapa ada di mana**. Lihat **C-17** /
> [#75](../../issues/75).

---

## §10.19 — 3D Spatial Intelligence

```
2D Image → Depth → Point Cloud → 3D Scene → Spatial Graph
```

```
3D Scene
├── Walls   ├── Doors     ├── Objects
├── Floor   ├── Windows   └── Humans
├── Ceiling └── Furniture
```

Kemudian **Spatial Graph** menjadi bagian dari **Human Knowledge Graph**.

---

> 🛑 **Denah rumah adalah data yang tidak bisa ditarik kembali.** Foto bisa
> dihapus; peta 3D yang sudah dibuat darinya adalah **informasi turunan** yang
> tetap membawa isi aslinya — letak pintu, jendela, dan berapa kamar. Butir
> **§7.25** sudah mencatat bahwa nilai turunan tetap membawa jejak meski event
> aslinya hilang, dan §8.38 memasukkan `Feature Store` ke rantai hapus.
> **Peta spasial harus masuk daftar yang sama**, dan §10.36 memberinya empat
> tabel (`spatial_maps` dan tiga lainnya) yang belum ada di rantai hapus mana
> pun. Bertaut **C-9** / [#22](../../issues/22).

> ⚠️ **Depth dari satu gambar 2D adalah taksiran, bukan pengukuran.** Ia
> `Inference` pada tangga §10.5, bukan `Perception` — dan peta yang dibangun
> darinya mewarisi ketidakpastiannya. Kalau `Spatial Graph` masuk ke Knowledge
> Graph tanpa membawa `confidence`, kesalahan taksir kedalaman akan tampak
> sebagai fakta ruangan. Sama seperti **E-81**: sisi graf butuh `confidence`.

---

## §10.20 — Sensor Intelligence

Input: **Wearable · IoT · Phone · Smartwatch · Environmental Sensor**

```
Heart Rate · Steps · Sleep · Temperature · Acceleration
Gyroscope · GPS · Light · Noise · Air Quality
```

Pipeline:

```
Sensor → Ingestion → Normalization → Quality Check → Feature Extraction
→ State Estimation → Context
```

Penting:

> ## Sensor tidak selalu berarti ground truth.

Setiap observation memiliki: `value · confidence · source · timestamp ·
quality`

---

> ⭐⭐ **"Sensor tidak selalu berarti ground truth" adalah kalimat yang jarang
> ditulis, dan ia benar.** Kebiasaan umum adalah memperlakukan angka dari
> perangkat sebagai fakta dan angka dari model sebagai taksiran. Jam tangan
> yang longgar salah membaca detak jantung; GPS di dalam gedung meleset puluhan
> meter; deteksi tidur salah menghitung berbaring diam sebagai tidur.
>
> `quality` sebagai field terpisah dari `confidence` adalah pembedaan yang
> tepat: **`quality` adalah sifat pengukurannya, `confidence` adalah keyakinan
> pada kesimpulan yang dibangun darinya.** Sensor berkualitas buruk bisa
> menghasilkan kesimpulan berkeyakinan tinggi bila banyak sumber sepakat, dan
> sebaliknya.

> ⭐ **Ini juga menutup separuh B-6.** Butir itu mencatat bahwa tiap ekosistem
> wearable (Apple Health, Google Fit, Garmin, Fitbit) punya izin dan proses
> persetujuannya sendiri. `Normalization` + `Quality Check` memberi tempat
> untuk perbedaan antar-perangkat; yang tetap belum ada adalah **proses
> persetujuan per ekosistem**, dan itu urusan produk, bukan arsitektur.

> ⚠️ **`Noise` dan `Air Quality` adalah sensor lingkungan — mereka mengukur
> ruangan, bukan orangnya.** `Noise` khususnya: sensor kebisingan yang
> merekam tingkat suara terus-menerus berada satu langkah dari mikrofon, dan
> pengguna biasanya tidak menganggapnya begitu. Kalau ia ada, ia butuh izin
> mikrofon, bukan izin sensor.

> ⚠️ **GPS memberi lokasi terus-menerus.** Klasifikasi data naskah 11
> menempatkan *location history* di **Level 3**, dan §8.12 menuntut proteksi
> lebih kuat. §10.27 memberi izin untuk kamera dan mikrofon tetapi **tidak
> menyebut izin lokasi sama sekali** — padahal `LocationChanged` ada di daftar
> event §10.30.
