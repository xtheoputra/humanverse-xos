# 222 — §15.12–§15.13 Indoor Positioning & Spatial Reasoning

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.12 — Indoor Positioning Engine

Teknologi: **UWB · BLE · WiFi RTT · Visual localization · IMU dead reckoning**

Target akurasi:

| Teknologi | Target |
|---|---|
| GPS | 3–10 m |
| WiFi RTT | 1–2 m |
| BLE | 1–5 m |
| **UWB** | **10–30 cm** |
| **LiDAR** | **cm-level** |

---

> ⭐⭐⭐ **Ini tabel target berangka pertama dalam beberapa naskah — dan ia
> membantah keberatan yang sudah dua kali saya catat.**
>
> Butir **E-112** mencatat *Definition of Done* naskah 17: **21 kriteria, nol
> angka**. §14.68 mengulanginya dengan 31 kriteria tanpa satu angka pun. Di sini
> naskah yang sama tiba-tiba memberi lima target yang **bisa diuji dengan meteran
> di lantai** — dan target itu masuk akal secara teknis, bukan angka bulat yang
> dikarang.
>
> Artinya kemampuan menyatakan target terukur **ada**; ia hanya tidak dipakai di
> tempat yang paling membutuhkannya. Itu membuat **E-112 lebih kuat, bukan lebih
> lemah**: §15.32 di naskah yang sama kembali memberi **10 kriteria tanpa satu
> angka pun**, padahal §15.12 baru saja membuktikan naskah ini bisa.

> ⚠️ **Daftar teknologi dan tabel target tidak cocok.** Daftar menyebut lima
> (UWB · BLE · WiFi RTT · Visual localization · IMU dead reckoning); tabel
> memberi lima juga, tetapi **bukan lima yang sama**: `GPS` dan `LiDAR` muncul di
> tabel tanpa ada di daftar, sementara **`Visual localization` dan `IMU dead
> reckoning` punya target nol**.
>
> Yang kedua itu yang penting: *dead reckoning* adalah satu-satunya teknik di
> daftar yang **galatnya menumpuk seiring waktu** — akurasinya bukan angka
> tunggal melainkan fungsi durasi sejak koreksi terakhir. Ia tidak bisa masuk
> tabel ini tanpa kolom kedua, dan justru itu yang perlu ditulis.

> ⚠️ **Tidak ada baris untuk AetherScan/WiFi CSI**, padahal §15.4 menjadikannya
> provider sensor dan §15.31 menyebutnya *"salah satu keunggulan unik
> HumanVerse"*. `WiFi RTT` bukan hal yang sama — RTT mengukur jarak ke titik
> akses yang bekerja sama; CSI sensing menyimpulkan keberadaan orang dari
> perubahan sinyal. Keunggulan yang diklaim unik adalah satu-satunya yang tidak
> punya target akurasi.

> ⭐ **Menyusun teknologi dari yang paling kasar ke paling presisi juga memberi
> aturan penggabungan yang §15.3 butuhkan**: kalau dua sensor tidak sepakat soal
> posisi, **yang lebih presisi menang** — dan tabel ini adalah urutannya. Tinggal
> ditulis satu kalimat.

---

## §15.13 — Spatial Reasoning

HumanVerse harus bisa menjawab: *"Apakah kursi menghalangi jalan?"*

```
Scene Graph → Geometry → Collision → Reasoning → Answer
```

> Ini membuka jalan menuju **robotika**.

---

> ⭐⭐ **Pertanyaan contohnya dipilih dengan baik: ia bisa dijawab dari geometri
> saja.** *"Apakah kursi menghalangi jalan"* tidak menuntut model kausal, tidak
> menuntut menebak niat, dan bisa **dibuktikan salah** dengan berjalan ke sana.
> Bandingkan pertanyaan-pertanyaan Phase 12 (*"apa yang berbeda jika saya tidur
> satu jam lebih lama"*) yang menuntut model transisi yang §9.17 melarang
> menyimpulkannya. Spatial reasoning adalah wilayah tempat sistem ini akhirnya
> boleh menjawab dengan pasti.

> ⭐ **Rantainya berakhir di `Answer`, bukan di `Action`** — konsisten dengan
> §15.2 yang berakhir di `Spatial Decision`. Penalaran dan pelaksanaan tetap
> dipisah.

> 🛑 **Tapi kalimat *"ini membuka jalan menuju robotika"* mengubah taruhan
> seluruh fase, dan ia ditulis sebagai catatan kaki.**
>
> Penutup naskah menegaskannya: **Phase 16 = Robotics & Embodied Intelligence**,
> dan *"robot tidak bisa bergerak dengan aman tanpa SpatialOS, Scene Graph,
> SLAM, dan World Model yang sudah dibangun di fase ini."*
>
> Artinya semua yang dibangun di Phase 15 akan menjadi **dasar keselamatan
> benda yang bergerak di ruangan yang sama dengan manusia** — dan dua hal di
> fase ini belum siap memikulnya:
>
> 1. **§15.22 `Spatial Safety` tidak punya `Risk` maupun `Confirmation`** dalam
>    rantainya, sementara ia berakhir di `Execute`. Lihat **E-124** /
>    [#106](../../issues/106).
> 2. **`MOVING_TO` (§15.11) adalah prediksi yang diperlakukan seperti
>    pengukuran.** Untuk AR itu berarti panah yang salah; untuk robot itu berarti
>    menghindar ke arah yang salah.
>
> Keduanya murah diperbaiki sekarang dan mahal diperbaiki setelah ada perangkat
> keras yang bergerak.

> ⚠️ **`Collision` muncul di rantai ini dan di §15.22, tetapi tidak pernah
> didefinisikan atas apa.** Tabrakan antara dua objek di peta, antara manusia dan
> objek, atau antara **elemen AR dan pandangan pengguna**? §15.22 memberi contoh
> ketiga (*"AR tidak menampilkan objek yang menutupi jalan"*), yang berarti
> "collision" di sini menanggung dua arti sekaligus — pola yang sama dengan empat
> makna "sandbox" (**E-105**) dan tiga arti "KILL" (**E-120**).
