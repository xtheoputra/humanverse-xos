# 239 — §17.14–§17.17 Nutrition, Hydration, Stress Intelligence & Mental Wellbeing

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.14 — Nutrition Intelligence

Input: **food photo · food log · nutrition database · activity · goals.**

```
Food → Vision → Food Recognition → Nutrition Estimation → Goal Context
→ Recommendation
```

> *"Makanan ini diperkirakan tinggi protein dan energi; cocok atau tidak
> tergantung target dan konteks harianmu."*
>
> Estimasi harus memiliki **confidence** dan **tidak berpura-pura presisi**.

> ⚠️ Angka lepas `6` di bagian ini (**H-9**).

---

> ⭐⭐⭐ **"Tidak berpura-pura presisi" adalah kalimat yang paling dibutuhkan di
> seluruh bidang ini, dan hampir tidak pernah ditulis.**
>
> Estimasi gizi dari foto adalah salah satu tugas paling tidak pasti yang bisa
> diberikan pada model penglihatan: porsi tidak terlihat, minyak tidak terlihat,
> isi di balik permukaan tidak terlihat. Produk yang menampilkan *"487 kkal"*
> memberi angka yang presisinya dikarang — dan penggunanya lalu mengambil
> keputusan atas tiga digit yang tidak ada dasarnya.
>
> Kalimat contohnya juga menghindari perangkap kedua: ia **tidak menilai
> makanannya** (*"tinggi protein dan energi"*), lalu menyerahkan penilaiannya
> pada konteks. Itu senapas dengan *"jangan menilai baik atau buruk"* naskah 4,
> dan penting justru di bidang di mana penilaian makanan mudah menjadi
> pengawasan diri yang merugikan.

> ⚠️ **Tapi `Nutrition Estimation` tetap menghasilkan angka yang masuk
> `nutrition_logs` (§17.43) dan lalu dipakai model lain.** Ketidakpastian yang
> dinyatakan di antarmuka tidak otomatis ikut ke basis data. Yang perlu
> ditulis: **estimasi gizi disimpan sebagai rentang, bukan sebagai nilai
> tunggal** — dan §17.6 sudah punya medannya (`uncertainty`).

> ⚠️ **`nutrition database` sebagai masukan berarti ada acuan luar**, dan basis
> data gizi berbeda antarnegara dan antarmasakan. Untuk pengguna Indonesia,
> acuan yang dipakai menentukan apakah angkanya masuk akal sama sekali. Ini
> keputusan yang bentuknya ADR, dan naskah tidak menyebut satu pun sumber —
> berbeda dari §15.6, §16.7, dan §16.22 yang menyebut pustaka nyata.

---

## §17.15 — Hydration Intelligence

Input: **activity · weather · exercise · user logging** → Output: **Hydration
Reminder.**

> **Tidak perlu selalu memberi angka absolut** jika datanya tidak cukup.

---

> ⭐⭐ **Ini bagian terpendek di naskah, dan kalimat penutupnya adalah salah satu
> yang paling penting: sistem boleh MENGINGATKAN tanpa MENGUKUR.**
>
> Hidrasi adalah hal yang tidak bisa diukur perangkat mana pun di §17.3.
> Sebagian besar produk tetap menampilkan angka target harian — angka yang
> berasal dari aturan umum, bukan dari tubuh penggunanya. Menolak memberi angka
> ketika datanya tidak ada adalah penerapan langsung dari *"tidak boleh
> mengarang data"* (§14.35), dan ia dipakai di tempat yang paling menggoda untuk
> mengarang.

> ⚠️ **`weather` sebagai masukan berarti lokasi, dan lokasi masuk Health Vault.**
> Itu bisa dibenarkan — cuaca memang memengaruhi kebutuhan cairan — tetapi ia
> harus lewat `purpose` §17.4, bukan sebagai akses lokasi umum. Bertaut
> catatan §17.3 dan **C-3** ([#21](../../issues/21)).

---

## §17.16 — Stress Intelligence

> Ini harus dirancang **sangat hati-hati.** HumanVerse dapat mendeteksi
> **indikator, bukan membaca pikiran.**

Input: **Sleep + Activity + Heart metrics + Voice signals + Journal + Schedule +
Self-report** → Output: **Stress Indicator.**

> *"Beberapa indikator dalam beberapa hari terakhir menunjukkan peningkatan
> stress dibanding baseline."*
>
> Bukan: *"Anda mengalami gangguan kecemasan."*

---

> ⭐⭐⭐ **Pasangan kalimat "bukan/tetapi" ini adalah bentuk pengaman terbaik di
> seluruh dua puluh satu naskah, dan ia muncul untuk KETIGA kalinya di naskah
> yang sama** (§17.7 fatigue · di sini · §17.20 forecasting).
>
> Yang membuatnya bekerja: ia tidak melarang **kemampuannya**, ia melarang
> **kalimatnya**. Sistem tetap boleh menghitung indikator; yang dilarang adalah
> menerjemahkannya menjadi nama penyakit. Larangan pada keluaran bisa diperiksa
> — larangan pada niat tidak.
>
> ⭐ Dan *"dibanding baseline"* menempatkan seluruh pernyataan pada **orang itu
> sendiri**, bukan pada populasi. Itu jawaban paling langsung untuk keberatan
> yang berulang di repo ini: rata-rata orang lain yang dijual sebagai jawaban
> personal (**B-1**, **B-24**, **B-27**).

> 🛑 **Tetapi `Voice signals` dan `Journal` sebagai masukan menyentuh dua hal
> yang sudah punya butir terbuka, dan keduanya adalah masukan paling sensitif di
> seluruh proyek.**
>
> **`Journal`** — naskah 5 §15 menempatkan *private journal* di daftar DENY
> bahkan untuk agent internal; §14.21 menuliskannya sebagai
> `deny: private.journal`; **G-9** mencatat dua naskah yang menghindarinya lewat
> kata pengganti. Di sini ia menjadi **masukan model**, dan naskah tidak menyebut
> pengecualian itu sama sekali.
>
> **`Voice signals`** — mikrofon berjalan terus-menerus, yang menyentuh
> **C-17** ([#75](../../issues/75)) dan **C-24** ([#114](../../issues/114),
> perangkat yang membawa sensornya sendiri).
>
> ⭐ Bahan penyelesaiannya sudah ada di naskah ini juga: §17.31 menyebut
> **`private voice processing`** sebagai contoh pemrosesan di perangkat. Yang
> perlu ditulis satu baris: **jurnal dan suara tidak pernah meninggalkan
> perangkat; yang naik hanya indikatornya** — dan §17.4
> `processing_location` sudah menjadi field yang bisa memeriksanya.

---

## §17.17 — Mental Wellbeing Intelligence

HumanVerse dapat membantu: **journaling · reflection · breathing exercise ·
routine · sleep · social connection · workload management.**

> Tetapi harus memiliki **Mental Health Safety Layer.**
>
> Jika sistem mendeteksi **situasi berisiko tinggi**, ia **tidak boleh mencoba
> menangani sendiri**; perlu **escalation yang sesuai.**

---

> ⭐⭐⭐ **"Tidak boleh mencoba menangani sendiri" adalah batas yang benar, dan
> menuliskannya sebelum ada satu baris kode adalah alasan seluruh disiplin
> dokumen ini ada.**
>
> Ia juga sejalan dengan tujuh hal yang sudah ditetapkan lebih dulu:
> *governance di luar jalur kepentingan* (§14.44), *Health Safety Agent di
> governance layer* (§17.25), dan `Emergency Rules` yang tidak bisa ditunda
> (§16.18).

> 🛑🛑🛑 **Tetapi ini butir dengan taruhan tertinggi di seluruh proyek, dan
> TIGA hal yang menentukan apakah ia bekerja tidak ada satu pun di naskah.**
>
> | Yang tidak ditulis | Kenapa ia menentukan |
> |---|---|
> | **Apa itu "situasi berisiko tinggi"** | kata pengganti — dan yang **ketujuh** di tiga naskah terakhir (*unrelated* §8.15 · *sembarangan* §14.45 · *bukti yang cukup* §15.10 · *keputusan sensitif* §15.16 · *sensitif* §15.29 · *transparan* §16.12 · di sini). Di enam tempat sebelumnya akibatnya adalah aturan yang lolos; di sini akibatnya adalah **deteksi yang tidak pernah menyala, atau menyala terlalu sering** |
> | **Escalation kepada SIAPA** | §17.39 memberi `Emergency Contact / Service` untuk darurat medis. Risiko menyakiti diri sendiri **bukan hal yang sama**, dan menghubungi kontak darurat tanpa persetujuan bisa memperburuk — sementara tidak menghubungi siapa pun juga bisa |
> | **Apa yang sistem lakukan SEMENTARA menunggu** | *"tidak boleh menangani sendiri"* melarang; ia tidak menyatakan apa yang boleh. Diam adalah keluaran yang juga punya akibat |
>
> 🛑 **Dan §17.53 mengeluarkan H17.8 *Wellbeing Intelligence* dari jalur MVP** —
> sementara §17.17 adalah satu-satunya tempat Mental Health Safety Layer hidup.
> Artinya, pada urutan pembangunan yang disarankan naskah ini sendiri,
> **`journaling` dan `reflection` bisa lahir tanpa lapisan keselamatannya**,
> karena keduanya juga fitur yang menarik dan mudah dibuat.
>
> Yang minimum perlu diputuskan sebelum satu baris kode: **fitur wellbeing tidak
> dirilis tanpa Safety Layer-nya, meski keduanya milik milestone yang
> berbeda** — dan kalau salah satunya harus lebih dulu, itu Safety Layer-nya.
> Lihat **C-25** / [#115](../../issues/115).

> ⚠️ **`journaling` di sini bertemu `Journal` sebagai masukan model di §17.16.**
> Sebuah fitur yang mengundang orang menulis hal paling pribadi, di sistem yang
> memakai tulisan itu sebagai sinyal — itu bukan kombinasi yang salah, tapi
> **penggunanya harus tahu**, dan §17.4 `purpose` adalah tempat menyatakannya.
