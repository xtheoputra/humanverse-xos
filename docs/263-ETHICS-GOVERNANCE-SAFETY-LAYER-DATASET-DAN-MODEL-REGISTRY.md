# 263 — §19.22–§19.25 Ethics Governance, Scientific Safety Layer, Dataset Intelligence & Model Registry

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.22 — Ethics Governance

> **Komponen wajib.** Memeriksa: `human subjects · privacy · bias · consent ·
> **dual-use risk** · **environmental impact**`

```
Experiment → Ethics Review → Risk Classification
```

---

> ⭐⭐⭐ **`dual-use risk` dan `environmental impact` adalah dua butir yang hampir
> tidak pernah masuk daftar etika teknologi — dan keduanya tepat untuk fase
> ini.**
>
> **`dual-use`** adalah satu-satunya kategori yang tidak bisa dijawab dengan
> melihat niat penelitinya: pengetahuan yang sama melindungi dan melukai, dan
> pertanyaannya bukan *"apakah ini dimaksudkan untuk melukai"* melainkan
> *"apakah ini menurunkan biaya melukai"*. Untuk mesin yang **menghasilkan
> hipotesis dan protokol**, itu pertanyaan yang harus ada sejak awal, sebab
> keluarannya adalah instruksi.
>
> **`environmental impact`** juga bukan basa-basi di sini: §19.13 menjalankan
> simulasi delapan domain dan §19.14 menjalankan seribu iterasi per parameter.
> Biaya komputasinya nyata, dan menyebutnya berarti ia bisa masuk pertimbangan
> alih-alih menjadi kejutan tagihan.

> ⭐⭐ **`Risk Classification` sebagai KELUARAN, bukan sebagai gerbang biner.**
> Tinjauan yang menghasilkan *"boleh/tidak"* memaksa keputusan yang sama untuk
> semua yang lolos. Yang menghasilkan **kelas** membiarkan perlakuan berbeda
> mengikutinya — dan §19.23 memakai keluaran itu. Bentuk yang sama dengan tujuh
> kategori §17.38, yang dicatat sebagai rantai keselamatan terbaik di repo ini.

> 🛑🛑🛑 **Tetapi "komponen wajib" itu dijadwalkan PALING AKHIR — `S19.10` dari
> sepuluh — dan ini naskah KEEMPAT berturut-turut.**
>
> | Naskah | Milestone keselamatan/etika | Posisi |
> |---|---|---|
> | 20 (Phase 16) | `R16.10` | terakhir dari 10 — [#111](../../issues/111) |
> | 21 (Phase 17) | `H17.12` | di luar MVP — [#116](../../issues/116) |
> | 22 (Phase 18) | — | tidak ada — [#121](../../issues/121) |
> | **23 (Phase 19)** | **`S19.10`** | **terakhir dari 10** |
>
> Dan di sini kata *"wajib"* ditulis oleh naskahnya sendiri, dua bagian sebelum
> jadwalnya menaruhnya di urutan terakhir. **Sebuah komponen tidak bisa wajib
> dan terakhir sekaligus**: milestone 1–9 akan dibangun dan dijalankan tanpa
> ia ada, dan pada saat ia datang, sembilan hal sudah berjalan tanpanya.
>
> ⚠️ Diperberat karena §19.22 juga **tidak berdiri di rantai mana pun**: §19.2
> (pipeline sepuluh langkah) tidak melewatinya, §19.11 (Experiment Planner)
> tidak melewatinya, dan `Ethics Agent` §19.16 berdiri sederet dengan `Writing
> Agent`. Lihat **C-29** / [#131](../../issues/131).

---

## §19.23 — Scientific Safety Layer

> Kategori: `Low Risk · Medium · High · Human Subjects · Biosecurity ·
> Dangerous Capability`
>
> **Semakin tinggi risiko, semakin ketat governance.**

---

> ⭐⭐⭐⭐ **Kalimat penutup itu adalah prinsip yang sama dengan penutup §17.56 —
> dan ini KEDUA kalinya pemilik menuliskannya, di naskah yang berbeda.**
>
> §17.56 berbunyi: *"…secara bertahap, dengan **governance yang semakin ketat di
> setiap level**"*. §19.23 mengulanginya dalam kata yang hampir sama.
>
> Itu penting melebihi kalimatnya sendiri. **B-33** ([#116](../../issues/116))
> dan **G-17** ([#121](../../issues/121)) keduanya berdiri di atas pembacaan ini:
> **governance bukan milestone melainkan FUNGSI DARI TINGKAT**, sehingga ia
> tidak bisa *"belum sampai gilirannya"*. Ketika sebuah prinsip muncul di dua
> naskah yang terpisah, ia berhenti menjadi tafsir saya dan menjadi **posisi
> pemiliknya**.
>
> ⇒ Dan itu menjadikan penjadwalan `S19.10` bukan sekadar risiko, melainkan
> **naskah yang membantah dirinya sendiri di dua bagian berturutan**: §19.23
> menyatakan governance mengikat mengikuti tingkat risiko; §19.33 menaruhnya
> sesudah semua yang menghasilkan risiko itu.

> ⭐⭐ **`Biosecurity` dan `Dangerous Capability` sebagai kategori bernama adalah
> pengakuan paling tajam di dua puluh tiga naskah tentang apa yang sistem ini
> bisa hasilkan.** Fase yang menyebut dua kata itu tahu bahwa keluarannya bisa
> berupa protokol yang tidak boleh dijalankan — dan §19.15 adalah tempat
> protokol berubah menjadi perbuatan.

> 🛑 **Tetapi enam kategori ini bukan satu tangga — ia DUA SUMBU yang
> dijejalkan menjadi satu daftar.**
>
> | Sumbu | Isi | Sifat |
> |---|---|---|
> | **derajat** | `Low` · `Medium` · `High` | berurutan, bisa dibandingkan |
> | **jenis** | `Human Subjects` · `Biosecurity` · `Dangerous Capability` | sejajar, tidak berurutan |
>
> Akibatnya konkret: penelitian dengan subjek manusia bisa **berisiko rendah**
> (kuesioner anonim) atau **sangat tinggi** (uji klinis) — dan daftar ini tidak
> punya cara menyatakan keduanya. Kalau `Human Subjects` dianggap di atas
> `High`, maka kuesioner mendapat perlakuan uji klinis dan aturannya akan
> dilanggar karena tak masuk akal; kalau di bawah, uji klinis lolos sebagai
> kategori menengah.
>
> ⭐ Bentuk yang benar sudah ada di naskah sebelumnya, dan ia justru yang dipuji:
> **§18.24 memisahkan `Probability` dari `Impact` dari `Confidence`** alih-alih
> menjumlahkannya. Di sini: **`severity` (rendah/sedang/tinggi) × `category`
> (subjek manusia · biosekuriti · kemampuan berbahaya)**, dan governance
> ditentukan oleh keduanya. Tiga kategori itu terlalu penting untuk kehilangan
> derajatnya.

> 🛑 **Dan ini kosakata risiko KEEMPAT di repo ini** — §8.17 `R0–R4` (risiko
> aksi, **H-21**) · §17.38 `INFO…EMERGENCY` (sinyal kesehatan) · §18.24
> `probability/impact/confidence/horizon` (risiko dunia,
> **E-141**/[#130](../../issues/130)) · dan yang ini. Keempat bentuknya berbeda,
> keempatnya bernama *"risk"*. Lihat **E-146** / [#135](../../issues/135).

---

## §19.24 — Dataset Intelligence

> Mengelola: `metadata · **license** · provenance · quality · bias ·
> **missing values**`

---

> ⭐⭐⭐ **`license` muncul lagi — dan bersama §18.16, ini dua naskah
> berturut-turut yang memperlakukan lisensi sebagai field wajib.**
>
> **C-27** ([#122](../../issues/122)) mencatat §18.4 menarik `news`,
> `scientific publications`, dan `internet knowledge` tanpa satu gerbang
> lisensi, sementara §18.16 menyediakan tempat menyimpan jawabannya. Bagian ini
> mengulangi bentuk yang sama untuk dataset. ⚠️ Dan kekurangannya juga sama:
> **field yang dicatat bukan gerbang yang menolak.** Lisensi yang diperiksa
> sesudah data dipakai tidak mencegah apa pun; ia harus berdiri di `Document`
> §19.4, dan pemakaian yang tidak diizinkan harus **gagal**.

> ⭐⭐ **`missing values` sebagai hal yang dikelola, bukan dibersihkan diam-diam,
> menutup separuh B-14 untuk kelas data ini.**
>
> **B-14** ([#26](../../issues/26)) mencatat kegagalan senyap ketika satu sinyal
> mati; §17.19 menutup separuhnya dengan menjadikan `missing data` kategori
> tersendiri agar ia **berhenti terlihat seperti data yang normal**. Untuk
> dataset penelitian, akibatnya lebih tajam lagi: data yang hilang **jarang
> hilang secara acak** — ia hilang karena alat rusak pada kondisi tertentu, atau
> karena subjek yang keluar berbeda dari yang bertahan. Membuangnya diam-diam
> mengubah kesimpulan tanpa jejak.
>
> ⭐ Dan `bias` per dataset menyambung ke §19.25 dan ke §17.37 (Health Bias
> Engine), yang sudah menyebut **`data availability` sebagai sumbu bias yang
> paling jarang dipikirkan**.

---

## §19.25 — Model Registry

> `version · dataset · metrics · **bias** · **limitations** · deployment`

---

> ⭐⭐⭐⭐ **Registri model KEMBALI — dan ini menjawab langsung kemunduran yang
> tercatat satu naskah lalu.**
>
> §17.35 memberi `health_models` dengan `version` dan `approval`. Naskah 22
> **menghilangkannya**: tiga puluh tabel §18.28 tidak memuat satu pun tempat
> model dunia didaftarkan, sementara §18.21 menyebut `SupplyChainModel v4.2`
> dalam prosa — sehingga `Model` di rantai provenance menunjuk ke sesuatu yang
> tak berbaris, dan sepuluh metrik §17.36 kehilangan subjeknya
> (**B-35** / [#127](../../issues/127)).
>
> Naskah ini mengembalikannya, **dan lebih lengkap dari aslinya**: `bias` dan
> `limitations` belum pernah ada di registri mana pun.
>
> ⭐⭐ **`limitations` sebagai field registri adalah yang paling berharga di
> keenamnya.** Ia menjawab pertanyaan yang `metrics` tidak bisa jawab: *di mana
> model ini berhenti berlaku.* Sebuah model dengan metrik bagus dan batas
> pakai yang tidak tertulis akan dipakai di luar batasnya oleh orang yang tidak
> tahu batas itu ada — dan di sini konsumennya adalah **agent**, yang tidak akan
> bertanya. Ia juga simetris dengan §19.5 (mengekstrak `limitation` orang lain)
> dan §19.20 (mewajibkan menulis `Limitations` sendiri): **tiga tempat berbeda,
> satu sikap.**

> ⚠️ **Tetapi `approval` §17.35 tidak ikut kembali.** Registri tanpa persetujuan
> mencatat model yang ada; ia tidak menyatakan model mana yang **boleh dipakai**.
> §17.36 menuntut ambang per metrik dan §19.22 menghasilkan `Risk
> Classification` — keduanya hanya menggigit kalau ada field yang menahan model
> sampai lolos.

> ⚠️ **Dan pemulihan ini hanya berlaku untuk model penelitian.** `world_models`
> masih tidak ada; [#127](../../issues/127) tetap terbuka. Yang berubah adalah
> buktinya: **bentuk itu jelas bisa dibawa antar-fase** — ia sudah dibawa dua
> kali, dan sekali hilang di antaranya.
