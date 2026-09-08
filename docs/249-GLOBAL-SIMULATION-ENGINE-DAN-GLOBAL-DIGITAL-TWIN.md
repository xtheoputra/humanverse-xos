# 249 — §18.10–§18.11 Global Simulation Engine & Global Digital Twin

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.10 — Global Simulation Engine

> Sekarang Phase 12 Digital Twin bertemu Phase 18 World Model.

```
World Model + Personal Digital Twin + Causal Model + Scenario → Simulation
```

> *"Apa yang mungkin terjadi jika suku bunga global naik?"*

```
Interest Rate +1% → Capital Cost → Investment → Company Growth
   → Employment → Income → Personal Scenario
```

> Output:
>
> ```
> Scenario A — Probability: 31%
> Scenario B — Probability: 46%
> Scenario C — Probability: 23%
> ```
>
> **Bukan prediksi absolut.**

---

> ⭐⭐⭐ **`Causal Model` disebut sebagai masukan simulasi yang berdiri sendiri —
> dan itu yang membedakan bagian ini dari ramalan biasa.**
>
> Simulasi yang hanya punya World Model + Scenario akan mengekstrapolasi apa
> yang terlihat; simulasi yang membawa model sebab bisa menjawab pertanyaan
> *"apa yang terjadi kalau X berubah"* — dan itu pertanyaan yang berbeda secara
> mendasar. Menyebutnya sebagai masukan keempat, bukan sebagai sesuatu yang
> tersirat di dalam World Model, adalah pilihan yang tepat: ia memaksa §18.9
> punya keluaran yang bisa dipakai, bukan sekadar taksonomi.

> ⭐⭐ **Tiga skenario berprobabilitas, bukan satu angka — dan `Bukan prediksi
> absolut` ditulis di bawahnya.**
>
> Ini bentuk penyajian yang benar untuk hal yang benar-benar tidak diketahui,
> dan ia konsisten dengan §12 (World Simulation) serta §18.7 `Possible
> Futures`. Sistem yang memberi satu angka mengundang orang bertindak seolah
> angka itu pasti; tiga skenario memaksa pembacanya melihat bahwa jawabannya
> **berbentuk sebaran**.

> ⚠️ **Tapi 31 + 46 + 23 = 100, dan itu menyatakan sesuatu yang hampir pasti
> tidak benar: bahwa ketiga skenario ini MENGHABISKAN kemungkinan.**
>
> Simulasi dunia nyata selalu punya kemungkinan keempat yang tidak terpikirkan —
> dan justru kemungkinan itu yang paling mahal. Menjumlahkan ke seratus
> menghapusnya dari layar. ⭐ Perbaikannya kecil dan sudah punya preseden di
> repo ini: **sisakan bagian untuk `lainnya / tidak termodelkan`**, persis
> seperti §17.19 menjadikan `missing data` kategori tersendiri alih-alih
> membiarkannya terlihat normal (yang menutup separuh **B-14**/[#26](../../issues/26)).
> Sebuah simulasi yang berkata *"31 · 46 · 23 · dan 0 % lainnya"* sedang
> mengklaim kelengkapan yang tidak dimilikinya.

> 🛑 **Dan rantai contohnya berakhir di `Personal Scenario` — melewati
> `Employment` dan `Income` — tanpa satu pun gerbang.**
>
> Keluaran dari rantai ini, dalam bentuknya yang paling wajar, adalah kalimat
> tentang pekerjaan dan penghasilan seseorang. Itu kelas keluaran yang naskah 21
> tangani dengan sangat hati-hati: §17.38 memberi **tujuh kategori
> `INFO → EMERGENCY`** justru karena untuk keluaran **informasi**, pertanyaannya
> bukan *"boleh atau tidak"* melainkan **seberapa keras ini disampaikan**.
>
> Di sini tidak ada padanannya. Simulasi menghasilkan skenario, skenario sampai
> ke pengguna. §18.22 memberi Safety Kernel — tetapi ia berdiri di jalur
> **masuk** (`World Data → … → Insight`), bukan di jalur keluar ini. Lihat
> **G-17** / [#121](../../issues/121).

> ⚠️ **`Interest Rate +1%` sebagai satu-satunya contoh skenario menyembunyikan
> pertanyaan siapa yang menyusun skenarionya.** Kalau penggunanya, ia perlu
> tahu skenario mana yang masuk akal untuk ditanyakan; kalau sistemnya, maka
> **pilihan skenario itu sendiri adalah keluaran yang membentuk kesimpulan** —
> menawarkan *"bagaimana kalau Anda kehilangan pekerjaan"* mengubah orang yang
> membacanya, terlepas dari probabilitasnya. §18.28 memberi `world_scenarios`
> sebagai tabel, tetapi tidak menyebut siapa penulisnya.

---

## §18.11 — Global Digital Twin

> Kita sekarang memiliki:
>
> ```
> Human Digital Twin → Organization Twin → City Twin
>    → Industry Twin → Regional Twin → World Model
> ```
>
> Misalnya:
>
> ```
> Personal Twin ↕ Company Twin ↕ Industry Twin ↕ City Twin ↕ Global Twin
> ```
>
> Dengan demikian HumanVerse dapat memahami **multi-scale intelligence**.

---

> ⭐⭐ **Anak panah dua arah (`↕`) di diagram kedua adalah koreksi yang benar
> terhadap diagram pertama, dan ia menyatakan hal yang tidak sepele.**
>
> Agregasi satu arah (orang → kota → dunia) hanya bisa menjawab *"seperti apa
> keseluruhannya"*. Dua arah menambahkan pertanyaan yang justru dipakai §18.31:
> *"berapa bagian dari yang saya alami yang berasal dari keseluruhan"*. Itu
> pembagian yang tidak bisa dilakukan model satu arah, dan ia inti dari nilai
> Phase 18 bagi pengguna perorangan.

> 🛑 **Tetapi dua diagram di bagian yang sama memberi URUTAN yang berbeda dan
> NAMA yang berbeda untuk benda yang sama.**
>
> | | Diagram 1 | Diagram 2 |
> |---|---|---|
> | urutan | Human → Organization → **City → Industry** → Regional → … | Personal → Company → **Industry → City** → … |
> | puncak | **`World Model`** | **`Global Twin`** |
> | tingkat | enam | lima (`Regional` hilang) |
>
> `City` dan `Industry` bertukar tempat, dan puncaknya punya dua nama. Kalau
> tangga ini dipakai untuk merambatkan dampak — dan §18.10 memang memakainya —
> maka urutannya **menentukan hasilnya**: dampak yang mengalir kota→industri
> tidak sama dengan industri→kota.
>
> Dan `World Model` lawan `Global Twin` adalah pola **E-136** yang persis: satu
> benda dua nama di dalam satu naskah (di sana `Health Intelligence Runtime`
> lawan `HealthOS`). Riwayatnya sudah panjang — *"HumanOS"* dengan tiga arti
> (**E-114**), `WorkOS` yang muncul sekali lalu hilang, empat makna "sandbox"
> (**E-105**), tiga arti "KILL" (**E-120**). Lihat **E-141** / [#130](../../issues/130).

> ⚠️ **Selain itu tangga ini sebenarnya bukan satu sumbu, melainkan dua yang
> disilangkan.** `Organization` dan `Industry` adalah pengelompokan **ekonomi**;
> `City` dan `Regional` adalah pengelompokan **geografis**. Sebuah perusahaan
> tidak berada "di dalam" sebuah kota dengan cara yang sama seperti kota berada
> di dalam wilayah — ia bisa berada di banyak kota sekaligus. Merangkainya
> sebagai satu rantai lurus akan memaksa salah satu hubungan menjadi palsu.
> ⭐ Bentuk yang benar sudah dipakai naskah 21 untuk masalah yang sama:
> §17.48 menaruh `Life Twin` dan `Health Twin` sebagai **dua sumbu di bawah satu
> Personal Digital Twin**, bukan sebagai mata rantai — dan itulah yang menutup
> **A-19** ([#2](../../issues/2)) tanpa membuat model ketujuh.

> ⚠️ **Dan `Organization Twin` / `City Twin` adalah model tentang kumpulan
> orang.** Naskah tidak menyebut siapa pemiliknya. §17.4 memberi `owner`
> sebagai field wajib untuk data kesehatan justru karena pertanyaan itu tidak
> boleh menggantung; di sini pertanyaannya lebih rumit, sebab kembaran sebuah
> kota dibangun dari data penduduk yang tidak pernah menyetujuinya satu per
> satu. Lihat **C-27** / [#122](../../issues/122) dan **B-36** / [#126](../../issues/126).
