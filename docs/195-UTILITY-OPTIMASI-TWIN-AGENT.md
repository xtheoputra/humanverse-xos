# 195 — §12.21–§12.24 Personal Utility, Life Optimization, Twin+Agent & World Simulator

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.21 — Personal Utility Model

> Tidak semua orang mengoptimalkan hal yang sama.

```
Utility =
 w1 Goal Progress + w2 Money + w3 Health + w4 Time
+w5 Happiness + w6 Risk + w7 Freedom + w8 Social
```

Contoh bobot:

```
Career     0.30      Freedom    0.15
Financial  0.25      Social     0.10
Health     0.20
```

> **User dapat mengubah weight.** Maka rekomendasi benar-benar personal.

---

> ⭐ **Bobot contoh berjumlah tepat 1,00** (0,30+0,25+0,20+0,15+0,10) — sama
> seperti §9.25. Diperiksa karena repo ini punya riwayat angka yang tidak
> berjumlah.

> 🛑 **Tetapi rumusnya punya DELAPAN suku dan contohnya punya LIMA bobot, dan
> namanya tidak cocok.**
>
> | Rumus §12.21 | Contoh §12.21 |
> |---|---|
> | Goal Progress | Career ? |
> | Money | Financial ? |
> | Health | Health ✅ |
> | **Time** | — |
> | **Happiness** | — |
> | **Risk** | — |
> | Freedom | Freedom ✅ |
> | Social | Social ✅ |
>
> Tiga suku hilang dari contoh (*Time*, *Happiness*, *Risk*), dan dua lainnya
> berganti nama. Ini pola **E-37** yang sama persis: rumus *Recommendation
> Score* naskah 5 §11 menyebut **7 komponen** sementara contohnya memakai
> **5** — dan butir itu masih terbuka di [#32](../../issues/32).
>
> Ditambah: bobot §9.25 punya daftar yang lain lagi (*Career Growth · Income ·
> Learning · Stability · Work-Life Balance*). **Tiga daftar, satu model.**
> Lihat **E-104**.

> ⚠️ **`w6 Risk` dengan bobot positif adalah kesalahan arah.** Risiko biasanya
> **mengurangi** utilitas; menjumlahkannya dengan bobot positif berarti makin
> berisiko makin baik. Ini masalah yang sama dengan `Risk: 4/10` §9.24 dan
> `Risk = 18` §12.12 — **setiap dimensi butuh arahnya sendiri**
> (`higher_is_better`), atau tabel perbandingan akan dijumlahkan terbalik.

> ⭐⭐ **"User dapat mengubah weight" — kedua kalinya naskah menuntut ini.**
> §9.25 sudah menulis *"tetapi user harus dapat mengubahnya"*. Dua naskah,
> satu tuntutan yang sama, dan **antarmukanya masih belum ada**: `Edit` hilang
> dari Privacy Center §8.36 (**E-74** / [#64](../../issues/64)). §11.28 memberi
> `[Edit]` untuk **aksi**, §11.10 untuk **rencana** — belum untuk **kesimpulan
> tentang diri pengguna**.

---

## §12.22 — Life Optimization Engine

```
maximize:
    expected_goal_utility

subject_to:
    time   <= available_time
    money  <= budget
    risk   <= acceptable_risk
    energy >= minimum
    health_constraints
    user_preferences
```

---

> ⭐ **Ini pernyataan optimasi formal pertama di enam belas naskah**, dan
> batasannya memakai `constraints` + `resources` yang baru mendapat rumah di
> §12.1. Rangkaiannya rapi: twin menyimpan batas, optimizer memakainya.

> 🛑🛑 **Tetapi ini eskalasi besar untuk Personal Utility Model, dan ia
> membuat syarat C-16 tidak bisa ditawar lagi.**
>
> Butir **C-16** ([#71](../../issues/71)) mempersoalkan model utilitas yang
> menyimpulkan **apa yang seseorang hargai** dari keputusan yang mungkin
> diambil dalam keadaan terpaksa — *"orang yang menerima lembur karena butuh
> uang tidak dengan sendirinya menghargai uang di atas keluarga"*.
>
> Di §9.24/§9.25 model itu dipakai untuk **membandingkan** pilihan: pengguna
> melihat tabel, pengguna memutuskan. Di §12.22 ia dipakai untuk
> **memaksimalkan** — sistem mencari jawaban terbaik menurut bobot yang **ia
> sendiri simpulkan**, lalu §12.23 menyerahkannya ke agent untuk dijalankan.
>
> Bedanya bukan derajat. Perbandingan menyerahkan penilaian kepada orangnya;
> optimasi mengambilnya. Dan `maximize expected_goal_utility` adalah kalimat
> yang, kalau dijalankan atas bobot yang keliru, akan **mengarahkan hidup
> seseorang ke arah yang tidak pernah ia pilih** — dengan efisien.
>
> Tiga syarat C-16 karena itu berubah dari usul menjadi prasyarat:
> **bobot terlihat sebelum dipakai · bisa diubah · sistem menyatakan ia
> menebak.** Ditambah satu yang baru: **optimasi tidak dijalankan atas bobot
> yang disimpulkan — hanya atas bobot yang dikonfirmasi pengguna.**

> ⚠️ **`expected_goal_utility` mengoptimalkan **tujuan**, bukan kesejahteraan.**
> Batasan kesehatan ada (`health_constraints`, `energy >= minimum`) dan itu
> benar — tapi ia **batas**, bukan yang dimaksimalkan. Sistem seperti ini akan
> selalu mendorong sampai tepat di batas: tidur minimum, energi minimum, waktu
> habis. Itu optimal secara matematis dan salah secara manusia.
>
> §12.7 sudah punya penawarnya: **`Sustainability`** sebagai dimensi
> perbandingan. Ia sebaiknya masuk ke fungsi tujuan, bukan tinggal di tabel
> perbandingan.

---

## §12.23 — Digital Twin + Agent

```
Digital Twin → Simulation → Best Scenario → Planner → Agent → Action
→ Real World
```

*"Saya ingin menyelesaikan project dalam 30 hari"*:

```
cek skill → cek waktu → cek workload → simulate beberapa strategi
→ pilih strategi terbaik → buat plan → Agent menjalankan task
→ monitor progress → re-simulate → adapt
```

---

> ⭐⭐ **`re-simulate` di akhir adalah yang membuat rantai ini loop, bukan
> jalur.** Rencana yang dibuat dari simulasi akan meleset; yang menyelamatkannya
> bukan rencana yang lebih baik melainkan **simulasi ulang atas keadaan baru**.
> Itu sejalan dengan §11.46 (`OBSERVE → MEASURE → REFLECT → ADAPT → REPLAN`).

> ⭐ **Dan ini menjawab kenapa Phase 12 datang setelah Phase 11, bukan
> sebelumnya.** `Best Scenario → Planner → Agent` menyambung ke §11.8 Planning
> Engine dan §11.11 Plan Verification: simulasi memilih **strategi**, planner
> menurunkannya jadi **langkah**, Action Gateway §11.14 menjaga **tiap
> langkah**. Tiga lapisan, tiga tanggung jawab berbeda.

> ⚠️ **`pilih strategi terbaik` melewati manusia.** Rantai ini tidak punya
> langkah persetujuan antara *simulate* dan *buat plan* — padahal §12.11
> berakhir di `Recommendation` (bukan `Decision`), §12.12 menolak menyatakan
> pemenang, dan §11.28 memberi Action Center untuk persetujuan.
>
> Kemungkinan besar ini penyederhanaan contoh. Tapi karena kalimatnya
> berbunyi *"pilih strategi terbaik"* — bukan *"tunjukkan perbandingan"* —
> ia perlu diperbaiki, atau ia membatalkan disiplin yang dijaga tiga bagian
> sebelumnya di naskah yang sama.

---

## §12.24 — Personal World Simulator

```
                  HUMAN
    ┌───────────────┼───────────────┐
  HEALTH         CAREER          FINANCE
    │               │               │
  ENERGY         SKILLS           MONEY
    └───────────────┼───────────────┘
              DECISIONS → ACTIONS → OUTCOMES → FUTURE STATE
```

---

> ⭐ **Tiga cabang yang menyatu di `DECISIONS`** adalah gambar paling ringkas
> dari kenapa konflik §11.22 (Health vs Learning vs Career) tidak terhindarkan:
> ketiganya menarik sumber daya yang sama — waktu dan energi — dan bertemu di
> satu titik keputusan.
>
> ⚠️ Dan gambar ini **menghilangkan tiga cabang** yang §12.10 punya: *Learning*
> dan *Social* dilebur, *Lifestyle* hilang. Lima rantai jadi tiga. Perbedaan
> kecil, dicatat supaya tidak dikira salah salin — pola **G-4**/**G-5** yang
> berulang.
