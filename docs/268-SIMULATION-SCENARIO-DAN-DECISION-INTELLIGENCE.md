# 268 — §20.7–§20.9 Civilization Simulation, Scenario Engine & Decision Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.7 — Civilization Simulation Engine

```
Civilization State → Scenario → Causal Model → Agent Simulation
   → Economic Simulation → Social Simulation → Environmental Simulation
   → Technology Simulation → Outcome Distribution
```

> Contoh: *"Apa kemungkinan dampak adopsi AI secara besar-besaran?"*
>
> ```
> AI Adoption → Productivity → Labor Market → Education
>    → Income Distribution → Consumption → Energy Demand → Infrastructure
> ```
>
> Sekali lagi: **simulation ≠ prediction certainty.**

---

> ⭐⭐⭐ **`Causal Model` berdiri sebagai langkah tersendiri sesudah `Scenario` —
> dan itu satu-satunya cara pertanyaan *"apa yang terjadi kalau X berubah"* bisa
> dijawab berbeda dari *"apa yang biasanya terjadi"*.**
>
> Ini pengulangan bentuk §18.10, yang juga menaruh `Causal Model` sebagai
> masukan berdiri sendiri. Dua naskah yang memperlakukan sebab sebagai komponen
> — bukan sesuatu yang tersirat di dalam model dunia — menjadikan §17.9/§18.9
> punya konsumen, alih-alih berhenti sebagai taksonomi.

> ⭐⭐ **`Outcome Distribution` di ujung, bukan daftar skenario berjumlah
> seratus.** §18.10 memberi `31 % · 46 % · 23 %` yang menyatakan ketiganya
> menghabiskan kemungkinan; §19.14 memperbaikinya dengan `Distribution`; naskah
> ini **mempertahankan perbaikan itu**. Untuk sistem yang keluarannya tentang
> lapangan kerja dan pendapatan, ekor sebaran yang terlihat adalah selisih antara
> peringatan dan kejutan.

> 🛑 **Tetapi empat simulasi domain dirangkai BERURUTAN, padahal keempatnya
> saling mengumpani — dan rantai satu arah tidak bisa menyatakan itu.**
>
> `Economic → Social → Environmental → Technology` digambar seperti pipeline.
> Di dunia yang dimodelkan, keempatnya adalah **gelung**: tekanan lingkungan
> mengubah ekonomi, teknologi mengubah tekanan lingkungan, keadaan sosial
> mengubah laju adopsi teknologi. Sebuah rantai sekali-lewat akan menghasilkan
> satu arah sebab dan **kehilangan justru dinamika yang membuat sistem
> peradaban sulit diramalkan** — umpan balik yang menguatkan dan yang meredam.
>
> ⭐ Naskah ini menyebut namanya sendiri di tempat lain: §20.28 memberi
> **`simulation/system-dynamics/`** sebagai direktori — dan dinamika sistem
> justru cabang yang dibangun untuk gelung umpan balik. Yang perlu: **rantai
> ini dinyatakan sebagai satu iterasi, dijalankan berulang sampai stabil**,
> bukan sebagai urutan.

> ⚠️ **Dan contoh rantai delapan langkahnya berakhir di `Infrastructure`, bukan
> di manusia** — padahal §20.2 menetapkan manusia di kedua ujung. `Income
> Distribution` di tengah adalah simpul yang paling menyentuh orang, dan ia
> lewat begitu saja menuju `Energy Demand`. Untuk keluaran sebesar ini,
> **siapa yang menanggung akibatnya** adalah bagian dari hasilnya, bukan
> catatan kaki. §20.18 punya bentuknya (`Affected Stakeholders`) — belum
> disambungkan ke sini.

---

## §20.8 — Civilization Scenario Engine

```yaml
scenario:
  assumptions:   []      probability:  0.31
  interventions: []      uncertainty:  0.28
  risks:         []      horizon:      "10 years"
  opportunities: []
```

---

> ⭐⭐⭐⭐ **`interventions` dipisahkan dari `assumptions` — dan itu pembedaan
> yang menentukan jenis pertanyaan yang bisa dijawab.**
>
> `assumptions` menjawab *"kalau dunia ternyata begini"*; `interventions`
> menjawab **"kalau KITA melakukan ini"**. Yang pertama adalah ramalan, yang
> kedua adalah **pilihan** — dan hanya yang kedua yang berguna untuk keputusan.
> Sebagian besar sistem skenario hanya punya yang pertama, lalu penggunanya
> harus menebak tuas mana yang bisa ia tarik. Menaruh keduanya sebagai field
> sejajar menjadikan §20.9 mungkin.

> ⭐⭐ **`probability` dan `uncertainty` berdiri terpisah**, meneruskan pembedaan
> §18.24 (`Probability` ≠ `Confidence`) — sebaran boleh sempit dan modelnya tetap
> rapuh. ⭐ Dan **`opportunities` sejajar dengan `risks`**: sistem yang hanya
> mendaftar risiko akan selalu menyarankan tidak melakukan apa-apa, dan itu juga
> pilihan yang berakibat.

> ⚠️ **Tetapi `assumptions: []` dan `interventions: []` adalah daftar kosong
> tanpa bentuk isinya.** Untuk field yang memikul seluruh perbedaan antara
> ramalan dan pilihan, bentuknya menentukan: sebuah intervensi perlu menyebut
> **siapa yang melakukannya** dan **apakah pelakunya punya kewenangan itu** —
> tanpa itu, skenario bisa mengandaikan tindakan yang tidak dimiliki siapa pun
> yang membacanya. §19.9 sudah memberi `Assumptions` bentuk yang sama, dan
> keduanya belum dinyatakan sebagai skema yang sama.

> ⚠️ **`horizon: "10 years"` adalah rentang di mana hampir semua model
> peradaban berhenti bisa diperiksa.** §18.24 memberi `Horizon: 90 days` dan itu
> dicatat sebagai kekuatannya — klaimnya **bisa diperiksa ketika 90 hari lewat**.
> Sepuluh tahun berarti tidak ada yang akan pernah mengukur benar-salahnya, dan
> mesin yang tidak pernah dinilai tidak bisa dikalibrasi. ⭐ Yang perlu:
> **skenario jangka panjang membawa penanda antara** — klaim yang jatuh tempo
> di tahun ke-1 dan ke-3, supaya modelnya bisa belajar sebelum sepuluh tahun
> lewat.

---

## §20.9 — Civilization Decision Intelligence

> Bukan hanya *"Apa yang akan terjadi?"* tetapi **"Apa pilihan yang
> tersedia?"** — Option A (high growth, high risk) · B (moderate/moderate) ·
> C (slow growth, low risk).

```
Utility = Benefit − Risk − Cost − Externality + Resilience
```

> Namun **utility weight harus dapat dikontrol manusia.**

---

> ⭐⭐⭐⭐ **`Externality` dan `Resilience` berada DI DALAM fungsi utilitas — dan
> keduanya justru yang paling sering ditinggalkan.**
>
> `Externality` adalah biaya yang ditanggung **pihak yang tidak ikut
> memutuskan**; ia tidak muncul di neraca siapa pun, dan itulah sebabnya ia
> diabaikan. `Resilience` bertanda **plus**, yang berarti ketahanan dihitung
> sebagai nilai, bukan sebagai biaya efisiensi — dan itu berlawanan dengan cara
> hampir semua sistem optimasi bekerja. Menaruh keduanya di rumus berarti
> **sistem tidak bisa merekomendasikan pilihan yang menang dengan memindahkan
> biayanya ke luar**.

> ⭐⭐⭐ **Dan *"utility weight harus dapat dikontrol manusia"* adalah pengaman
> yang tepat sasaran.** Pada rumus lima suku, **bobotnyalah yang memutuskan**,
> bukan rumusnya. Menyatakan bobot sebagai hal yang dipegang manusia berarti
> sistem tidak menyembunyikan nilai di balik aritmetika — itu bentuk konkret
> dari §20.2 (*Human sovereignty*).

> 🛑🛑 **Tetapi lima suku itu bersatuan berbeda, dan penjumlahannya menyembunyikan
> konversi yang menentukan jawabannya.**
>
> | Suku | Satuan alaminya |
> |---|---|
> | `Benefit`, `Cost` | uang |
> | `Risk` | peluang × dampak |
> | `Externality` | kerugian pihak ketiga — sering bukan uang |
> | `Resilience` | sifat sistem |
>
> Menjumlahkannya menuntut nilai tukar di antaranya, dan **nilai tukar itulah
> keputusan yang sebenarnya**. Sebuah bobot yang menukar `Externality` dengan
> `Benefit` sedang menetapkan harga bagi sesuatu yang ditanggung orang lain.

> 🛑🛑🛑 **Dan pertanyaan yang belum ditanyakan: MANUSIA YANG MANA yang memegang
> bobot itu.**
>
> *"Dikontrol manusia"* menjawab *bukan mesin*; ia tidak menjawab **siapa**.
> Pada keputusan skala peradaban, **yang menetapkan bobot dan yang menanggung
> `Externality` hampir tidak pernah orang yang sama** — itu justru definisi
> eksternalitas. Sistem yang membiarkan satu pihak menyetel bobot untuk pilihan
> yang berakibat pada pihak lain akan menghasilkan rekomendasi yang secara
> aritmetika benar dan secara akibat sepihak.
>
> ⭐ Naskah ini punya dua bahan yang menutupnya, keduanya belum disambungkan ke
> sini: **§20.17 memasukkan `Stakeholders` ke rantai tata kelola**, dan
> **§20.18 menghasilkan `Affected Stakeholders`** sebagai keluaran. Yang perlu
> dinyatakan: **bobot utilitas tidak sah tanpa daftar pihak terdampak, dan
> pilihan yang memindahkan biaya ke pihak yang tidak menyetel bobotnya
> memerlukan persetujuan terpisah.** Lihat **C-30** / [#141](../../issues/141).

> ⚠️ **Tiga opsi contohnya juga tersusun pada SATU sumbu** — pertumbuhan tinggi/
> sedang/rendah berbanding risiko tinggi/sedang/rendah. Itu bukan tiga pilihan
> melainkan tiga titik pada satu garis, dan ia menyembunyikan pilihan yang paling
> berharga: **yang mengubah bentuk pertukarannya**, bukan posisinya di garis
> yang sama.
