# 219 — §15.1–§15.4 SpatialOS, Spatial Intelligence Runtime, Sensor Fusion & AetherScan

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Visi Phase 15

> **"The world becomes an interface."**
>
> Jika **HumanOS (Phase 13)** adalah sistem operasi untuk kehidupan digital,
> maka **SpatialOS** adalah sistem operasi untuk **ruang fisik**.

Target akhirnya HumanVerse mampu:

- memahami ruang **3D real-time**,
- **mengingat** posisi objek dan manusia,
- menampilkan informasi lewat **AR**,
- berinteraksi lewat **gesture, suara, tatapan mata, pergerakan tubuh**,
- menghubungkan **Digital Twin** dengan dunia nyata.

Contoh pengalaman pengguna:

> *"Di mana saya meletakkan dompet kemarin?"*
>
> HumanVerse **tidak menebak**. Ia membuka **Spatial Memory**, melihat lokasi
> terakhir dompet di meja ruang tamu, lalu menampilkan **panah AR** menuju
> lokasi tersebut.

---

> ⭐⭐⭐ **"HumanVerse tidak menebak" adalah kalimat pembuka terbaik yang pernah
> dipakai sebuah naskah di sini, karena ia menyatakan syarat, bukan janji.**
>
> Menjawab *"di mana dompet saya"* dengan tebakan yang masuk akal adalah persis
> kegagalan yang §14.35 larang (*"tidak boleh mengarang data"*) dan yang **B-14**
> ([#26](../../issues/26)) catat sebagai kegagalan **senyap**. Fitur ini
> menariknya justru karena ia tidak punya jalan tengah: panah AR yang menunjuk
> ke tempat yang salah lebih buruk daripada tidak ada panah sama sekali, dan
> penggunanya akan tahu dalam sepuluh detik.
>
> Itu membuat Phase 15 **fase pertama yang keluarannya bisa dibuktikan salah
> oleh penggunanya seketika** — berbeda dari rekomendasi, proyeksi, atau skor
> yang tidak pernah bisa dibantah. Untuk produk yang seluruh kredibilitasnya
> berdiri di atas `confidence`, itu kabar baik.

> ⚠️ **Tapi contoh yang sama juga menunjukkan syarat yang belum ditulis:
> menjawabnya menuntut kamera yang melihat meja ruang tamu kemarin.** Fitur
> "di mana dompet saya" dan fitur "rumah saya tidak diawasi" adalah fitur yang
> sama dilihat dari dua sisi — dan §15.23 adalah satu-satunya tempat naskah ini
> membahas sisi keduanya.

---

## §15.1 — Arsitektur Besar SpatialOS

> 🛑 **BAGIAN INI KOSONG DI NASKAH.** Judulnya ada; isinya tidak — tidak ada
> diagram, tidak ada daftar, tidak ada kalimat.
>
> **Sengaja tidak ditambal**, sesuai aturan berkas dokumen repo ini: bagian yang
> hilang di naskah ditandai sebagai hilang. Lihat **G-15** /
> [#103](../../issues/103).
>
> Yang hilang di sini bukan bagian sembarangan: ia **arsitektur besar fase
> ini**, dan setiap naskah sebelumnya membukanya dengan diagram tingkat atas
> (§8.42 · §11.51 · §13.2 · §14.3). Tanpa itu, hubungan antara *SpatialOS*,
> *HumanOS*, *Digital Twin*, dan *World Model* hanya bisa dibaca dari diagram
> penutup di §15.32 — dan diagram itu **rantai satu jalur**, bukan arsitektur.

---

## §15.2 — Spatial Intelligence Runtime

> Ini adalah **"otak ruang"**.

Fungsinya: memahami geometri ruangan · melacak objek · melacak manusia ·
memahami posisi · memahami orientasi · menggabungkan semua sensor.

```
Sensor → Sensor Fusion → Localization → Mapping → Object Detection
→ Human Tracking → World Model → Spatial Memory → Spatial Decision
```

---

> ⭐⭐ **Rantai sembilan langkah ini berakhir di `Spatial Decision`, bukan di
> `Spatial Action` — dan bedanya besar.** Runtime ini **memutuskan**;
> pelaksanaannya diserahkan ke tempat lain (§15.22). Pemisahan yang sama sudah
> benar di §11.14 (Action Gateway terpisah dari agent) dan §13.24 (`prepare`
> dan `execute` jadi dua endpoint).

> ⚠️ **Tapi rantai ini tidak memuat satu pun gerbang.** Bandingkan sebelas
> gerbang §14.20 atau sembilan gerbang §11.14: di sini `Sensor → … → Spatial
> Decision` berjalan tanpa `Policy`, `Permission`, `Risk`, atau `Consent`.
>
> Untuk aliran yang **hanya membaca**, itu bisa dibela — tetapi §15.23 sendiri
> menetapkan bahwa **ruangan punya policy** (`bedroom: camera:false`), dan
> policy itu harus ditegakkan **sebelum `Sensor Fusion`**, bukan sesudah
> `Spatial Decision`. Tempatnya belum ada di rantai mana pun.

---

## §15.3 — Sensor Fusion Engine

> Salah satu kekuatan HumanVerse adalah **tidak bergantung pada satu sensor**.

| Sensor | Fungsi |
|---|---|
| Camera | Visual |
| LiDAR | Kedalaman |
| UWB | Presisi posisi |
| WiFi (AetherScan) | Occupancy & motion |
| IMU | Gerakan perangkat |
| GPS | Outdoor |
| Microphone | Audio |
| Bluetooth | Nearby devices |

> Semua digabung menjadi **satu representasi**.

---

> ⭐⭐ **"Tidak bergantung pada satu sensor" adalah prinsip yang benar, dan ia
> punya konsekuensi yang belum ditulis: sensor yang tidak sepakat.**
>
> Delapan sensor yang mengukur hal yang sama akan berbeda — LiDAR bilang kursi
> di `x=1.2`, kamera bilang `x=1.35`, UWB bilang orangnya di ruangan sebelah.
> §15.5 menyimpan `confidence: 0.94` per objek, jadi bentuknya ada; yang belum
> ada adalah **aturan penggabungannya**: rata-rata berbobot, sensor paling
> presisi menang, atau konflik dilaporkan sebagai konflik.
>
> Bahannya sudah ada di dua tempat: §14.12 memperlihatkan bahwa **menampilkan
> perselisihan** lebih berguna daripada meratakannya, dan §12.15 `Main
> uncertainty` sudah punya tempat menyimpannya. Untuk ruang, jawaban yang benar
> hampir pasti: **presisi menang untuk posisi** (tabel §15.12 sudah
> memeringkatnya), **tetapi ketidaksepakatan menurunkan `confidence`**.

> ⚠️ **`Microphone` berdiri di daftar sensor spasial tanpa penjelasan.** Tujuh
> sensor lain menghasilkan geometri; mikrofon menghasilkan **isi percakapan**.
> Kalau ia dipakai untuk lokalisasi bunyi (arah sumber, gema ruangan), itu wajar
> dan sebaiknya dikatakan; kalau tidak, ia sensor kategori lain yang masuk lewat
> pintu yang salah. **C-17** ([#75](../../issues/75)) sudah menandai pemantauan
> berkelanjutan di dalam rumah, dan mikrofon adalah bagiannya yang paling berat.

> ⚠️ Naskah menaruh angka lepas **`7`** setelah tabel ini, sementara tabelnya
> berisi **delapan** baris. Artefak salin-tempel — gejala **H-9** yang berulang
> di tiap naskah panjang. Dicatat, tidak ditambal; lihat **G-15**.

---

## §15.4 — AetherScan Integration

> Ini bagian yang **paling relevan dengan proyekmu**. AetherScan menjadi salah
> satu **provider sensor**.

```
WiFi CSI → Signal Processing → Motion Detection → Occupancy Detection
→ Pose Estimation (future) → 3D Spatial Map → HumanVerse World Model
```

**Kemampuan awal:** deteksi keberadaan manusia · estimasi jumlah orang ·
deteksi gerakan · zona aktivitas · rekonstruksi occupancy map.

**Kemampuan masa depan:** pose estimation · **breathing detection** · gesture
detection · **through-wall sensing** *(dengan batasan fisika dan hardware)*.

---

> ⭐ **Menjadikan AetherScan sebagai *provider sensor*, bukan sebagai fitur
> tersendiri, adalah keputusan arsitektur yang benar.** Ia masuk lewat
> `Sensor Fusion` bersama tujuh sensor lain, jadi ia tunduk pada aturan yang
> sama dan bisa dimatikan seperti sensor lain — setidaknya secara bentuk.

> 🛑🛑 **Tetapi dua kemampuan di daftar "masa depan" mengubah kelas seluruh
> fase ini, dan keduanya ditulis sebagai butir teknis biasa.**
>
> **`through-wall sensing`** — WiFi menembus dinding; itu sifat fisiknya, bukan
> fitur yang dinyalakan. Artinya alat ini **mendeteksi orang di properti
> tetangga** dan di ruangan yang penggunanya sendiri tidak berhak awasi. Butir
> **C-18** ([#76](../../issues/76)) sudah mencatat bahwa RF sensing menangkap
> orang yang tidak memakai HumanVerse **dan tidak bisa menyadarinya**; kata
> *through-wall* menaikkannya dari masalah persetujuan menjadi **masalah
> hukum**, karena di banyak yurisdiksi memantau ruang milik orang lain adalah
> pelanggaran tersendiri terlepas dari apa yang dilakukan pada datanya.
>
> **`breathing detection`** — laju napas adalah **tanda vital**. Ia data
> kesehatan menurut definisi mana pun, dikumpulkan **tanpa perangkat apa pun di
> badan orangnya**, tanpa layar, tanpa tombol, tanpa cara orang itu tahu ia
> sedang diukur. Tangga sensitivitas §8.16 menempatkan data kesehatan di Level
> 3–4; larangan §8.10 menutup *insurance scoring* — dan laju napas malam hari
> adalah persis turunan yang paling berguna bagi penanggung asuransi.
>
> ⚠️ *"Dengan batasan fisika dan hardware"* adalah keterangan yang benar dan
> tidak cukup: ia membatasi **seberapa baik** ini bekerja, bukan **apakah ia
> boleh**. Yang minimum perlu diputuskan sebelum satu baris kode: **`through-wall
> sensing` dan `breathing detection` tidak dibangun tanpa keputusan tersendiri**,
> terpisah dari keputusan membangun AetherScan. Lihat **C-22** /
> [#102](../../issues/102).

> ⚠️ **Dan `Pose Estimation (future)` berada di TENGAH pipeline, bukan di
> ujungnya.** Rantai §15.4 menaruhnya sebelum `3D Spatial Map` — artinya peta
> spasial yang dijanjikan **melewati** langkah yang belum ada. Kalau langkah itu
> memang belum dibangun, rantainya untuk sekarang adalah
> `Occupancy Detection → 3D Spatial Map` dan sebaiknya digambar begitu; kalau
> tidak, seluruh keluaran AetherScan bergantung pada kotak bertanda *(future)*.

> ⚠️ Naskah menaruh angka lepas **`6`** setelah kalimat pembuka bagian ini —
> artefak yang sama dengan §15.3. Lihat **G-15**.
