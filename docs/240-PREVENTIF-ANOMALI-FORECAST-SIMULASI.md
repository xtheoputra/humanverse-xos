# 240 — §17.18–§17.22 Preventive Intelligence, Anomaly Detection, Forecasting, Simulation & Counterfactual

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.18 — Preventive Intelligence

```
Longitudinal Data → Pattern Detection → Change Detection → Risk Signal
→ Human Explanation → Recommended Next Step
```

> *"Ada perubahan pola yang cukup konsisten selama beberapa minggu. Jika ini
> berlanjut atau mengganggu aktivitas, pertimbangkan membicarakannya dengan
> tenaga kesehatan."*

---

> ⭐⭐⭐ **`Human Explanation` sebagai LANGKAH DI DALAM PIPELINE — bukan sebagai
> lapisan tampilan di ujungnya — adalah penempatan yang benar dan jarang
> dibuat.**
>
> Sebuah `Risk Signal` yang tidak bisa dijelaskan **tidak lolos ke langkah
> berikutnya**. Itu menjadikan keterjelasan sebagai **syarat**, bukan fitur —
> dan untuk sinyal kesehatan, sinyal yang tidak bisa dijelaskan adalah sinyal
> yang hanya bisa menakuti.

> ⭐⭐ **Kalimat contohnya adalah rumusan terbaik di seluruh naskah untuk hal
> yang paling sulit dirumuskan.** Ia memuat empat hal sekaligus: apa yang
> teramati (*perubahan pola*), seberapa kuat (*cukup konsisten*), berapa lama
> (*beberapa minggu*), dan **syarat untuk bertindak** (*jika berlanjut atau
> mengganggu aktivitas*) — lalu menyerahkan langkahnya ke **tenaga kesehatan**,
> bukan ke sistem.
>
> Yang membuatnya bekerja adalah **syaratnya**: ia tidak menyuruh orang pergi ke
> dokter setiap kali angkanya bergerak, dan itu satu-satunya cara peringatan
> preventif tidak berubah menjadi kecemasan berlangganan.

> ⚠️ **`Risk Signal` di sini adalah arti KEDUA dari kata "risk" di repo ini.**
> `R0–R4` (**H-21**) adalah risiko **aksi**; ini risiko **kesehatan**. Keduanya
> lewat gerbang yang sama di §17.38 (`Risk Engine`), dan satu kata untuk dua
> besaran adalah pola yang sudah tiga kali menimbulkan masalah (**E-77** dua
> tangga 0–4 · **E-105** empat "sandbox" · **E-120** tiga "KILL"). Usul:
> **`health_signal` untuk yang ini**, `risk` tetap untuk aksi.

---

## §17.19 — Anomaly Detection

```
Baseline → Current → Deviation → Confidence
```

Kategori: **sudden change · gradual change · repeated anomaly · missing data ·
sensor anomaly.**

> **Sensor anomaly harus dibedakan dari human anomaly. Ini sangat penting.**

---

> ⭐⭐⭐⭐ **Kalimat itu menjawab B-25 — dan pemilik menuliskannya sendiri, tanpa
> diminta.**
>
> Butir **B-25** mencatat: *"pengulangan menyaring kesalahan acak dan
> MEMPERKUAT kesalahan sistematis — dan hanya yang pertama yang pernah
> dipikirkan."* Contohnya waktu itu kamera yang salah membaca posisi karena
> sudut pemasangannya salah setiap hari; pengulangan justru menaikkan
> keyakinannya. Untuk perangkat yang dipakai di badan, bentuknya persis sama:
> jam tangan yang longgar salah membaca **setiap malam**, dan tiga puluh malam
> data buruk terlihat seperti pola yang kuat.
>
> §17.19 menolaknya secara eksplisit, menjadikan `sensor anomaly` **kategori
> tersendiri**, dan menandainya *"sangat penting"*. ⭐ Ditambah `missing data`
> sebagai kategori terpisah — yang menutup separuh **B-14**
> ([#26](../../issues/26)): data yang hilang berhenti terlihat seperti data yang
> normal.

> ⭐⭐ **Dan bahan untuk membedakannya sudah lengkap di naskah ini:** `source`
> per state (§17.6) · `quality` per pengukuran (§17.32) · `Subjective Feedback`
> sebagai masukan (§17.11) · `Bio Signal` quality (§17.33). Empat sumber bukti,
> dan yang terakhir menentukan: **kalau orangnya bilang ia baik-baik saja dan
> alatnya bilang tidak, yang berubah lebih dulu adalah kepercayaan pada
> alatnya.**

> ⚠️ **`Baseline` tidak punya definisi — dari berapa lama, dan apa yang terjadi
> pada pengguna baru.** Ini **B-1** (cold start) pada fase yang paling
> membutuhkannya: seorang pengguna di minggu pertama tidak punya baseline, jadi
> setiap nilai adalah "deviasi" atau tidak ada satupun. §17.53 menaruh
> `H17.9 Anomaly & Forecasting` di jalur MVP — jadi pertanyaannya perlu dijawab
> sebelum fitur ini dirilis, bukan sesudah.

---

## §17.20 — Health Forecasting

```
Current State → Historical Pattern → Behavior → Context → Forecast
```

Horizon: **hari · minggu · bulan.**

> *"Jika pola tidur saat ini berlanjut, kemungkinan konsistensi tidur minggu
> depan akan menurun."*
>
> **Bukan prediksi penyakit.**

---

> ⭐⭐⭐ **Horizon `hari · minggu · bulan` menyelesaikan A-29 dengan cara yang
> paling sederhana: dengan tidak membuatnya.**
>
> Butir **A-29** ([#86](../../issues/86)) mencatat bahwa horizon **3 dan 5
> tahun** §12.10 **tidak pernah masuk loop belajar** §12.20 — sehingga ia
> satu-satunya keluaran yang tidak bisa dikalibrasi, padahal ia yang paling
> memengaruhi keputusan besar.
>
> Horizon terpanjang di sini adalah **sebulan**, yang berarti **setiap ramalan
> bisa diperiksa terhadap kenyataan dalam waktu yang sama** — dan itu membuat
> `Prediction Error` §12.20 dan `Prediction Calibration` §9.34 benar-benar
> berlaku. Ramalan yang bisa salah dengan cepat adalah ramalan yang bisa
> diperbaiki.

> ⭐ **Kalimat contohnya juga meramalkan HAL YANG SAMA yang ia amati** —
> konsistensi tidur, bukan berat badan, bukan penyakit. Ramalan yang tetap
> berada di dalam besaran yang diukurnya sendiri adalah ramalan yang tidak
> meminjam model kausal yang §9.17 melarang menyimpulkannya (**B-24**/**H-23**).

---

## §17.21 — Health Simulation

> Menggunakan **Phase 12.** *"Bagaimana jika saya olahraga 4× seminggu?"*

```
Current Twin → Scenario → Training Load → Recovery Model
→ Lifestyle Constraints → Projected Outcomes
```

> Output berupa **distribusi kemungkinan.**

---

> ⭐⭐⭐ **"Distribusi kemungkinan", bukan satu angka — dan ini pertama kalinya
> sebuah bagian menyatakan BENTUK keluarannya, bukan hanya isinya.**
>
> §12.13 memberi `confidence interval` sebagai medan; di sini rentang menjadi
> **bentuk jawabannya**. Perbedaannya besar: satu angka mengundang orang
> mengambil keputusan atas nilai tengah, sedangkan distribusi memaksa pertanyaan
> *"seberapa mungkin"* muncul di permukaan.

> ⭐⭐ **`Lifestyle Constraints` sebagai langkah wajib** adalah yang membedakan
> simulasi ini dari kalkulator kebugaran: rencana yang benar secara fisiologis
> tetapi tidak muat di hidup seseorang tidak lolos. Ia juga penerapan §17.23
> (*kehidupan nyata penuh trade-off*) di dalam mesin, bukan hanya di prinsip.

---

## §17.22 — Health Counterfactual

*"Bagaimana jika saya tidur 1 jam lebih awal?"*

```
Scenario A  Current Pattern
Scenario B  Earlier Sleep
Scenario C  Earlier Sleep + Lower Evening Workload
```

Kemudian: **Expected Benefit · Risk · Uncertainty · Assumptions.**

---

> ⭐⭐⭐ **Empat keluaran itu — dan khususnya `Assumptions` — menutup B-24 pada
> bentuk yang paling sulit.**
>
> Butir **B-24** mencatat bahwa Counterfactual Engine §9.14 menjanjikan jawaban
> yang §9.17 melarang memberikannya, karena sumber model transisinya tidak ada.
> **H-23** menutupnya lewat §12.20 (galat prediksinya sendiri) dan §12.14
> *Assumption Engine* (*"simulation without assumptions is misleading"*).
>
> §17.22 memakai keduanya sekaligus, dan **menampilkan `Assumptions` sebagai
> bagian dari jawaban** — bukan sebagai catatan kaki. Pertanyaannya bahkan sama
> persis dengan contoh **B-24** (*"apa yang berbeda jika saya tidur satu jam
> lebih lama"*), dan jawabannya kini datang dengan asumsinya terbuka.
>
> ⭐ **`Scenario C` adalah tambahan yang tidak diminta dan justru paling
> berguna:** ia menunjukkan bahwa mengubah satu hal jarang cukup, dan bahwa
> sistem boleh **mengusulkan skenario yang tidak ditanyakan**. Untuk pertanyaan
> *"bagaimana jika saya tidur lebih awal"*, jawaban yang jujur hampir selalu
> memuat *"apa yang harus berubah supaya itu mungkin"*.

> ⚠️ **Counterfactual tentang MASA LALU tetap perlu dibedakan dari skenario masa
> depan** — keberatan yang **B-24** catat dan yang belum dijawab di mana pun:
> *"Anda akan tidur lebih nyenyak kalau minggu lalu berhenti lebih awal"* adalah
> **penyesalan yang dihitung**, merugikan meski benar, untuk sistem yang
> berjanji tidak menilai penggunanya. Ketiga skenario di sini menghadap ke
> depan; aturannya tinggal ditulis supaya tetap begitu.
