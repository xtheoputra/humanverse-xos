# 238 — §17.10–§17.13 Sleep, Recovery, Fitness Intelligence & Adaptive Workout Engine

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.10 — Sleep Intelligence

> Bukan hanya menghitung jam tidur.

Analisis: **duration · consistency · sleep timing · wake timing · variability ·
sleep debt estimates · recovery indicators · relationship dengan aktivitas.**

Output: **Sleep Score · Sleep Consistency · Recovery Estimate · Sleep Trend.**

> ⚠️ Angka lepas `6` di bagian ini (**H-9**).

---

> ⭐⭐ **`consistency` dan `variability` sebagai keluaran tersendiri — terpisah
> dari `duration` — adalah pembedaan yang jarang dibuat dan hampir selalu benar.**
> Tidur tujuh jam setiap hari dan tidur rata-rata tujuh jam dengan sebaran lima
> sampai sepuluh adalah dua hal berbeda, dan hanya yang pertama terlihat pada
> angka rata-rata. Ini juga yang membuat contoh §17.20 (*"konsistensi tidur
> minggu depan akan menurun"*) bisa diramalkan sama sekali.

> ⚠️ **`Sleep Score` sebagai satu angka mewarisi keberatan B-29
> ([#96](../../issues/96)) dalam bentuk kecil**: delapan hal dianalisis, satu
> angka keluar, dan arah tiap komponennya tidak dinyatakan. Untuk skor yang
> ditampilkan tiap pagi, yang perlu dibawa bukan hanya angkanya melainkan
> **komponen mana yang menurunkannya** — dan §17.40 sudah memberi bentuknya
> (`Evidence`).

> ⚠️ **`sleep debt estimates` adalah satu-satunya keluaran di daftar ini yang
> memuat model yang tidak disebut sumbernya.** Utang tidur menuntut asumsi
> tentang kebutuhan tidur seseorang — angka yang berbeda per orang dan berubah
> seiring usia. Itu persis bentuk **B-1** (cold start): sebelum ada data
> berbulan-bulan, satu-satunya sumbernya adalah rata-rata populasi yang dijual
> sebagai jawaban personal. §12.14 *Assumption Engine* sudah menyediakan
> tempatnya — asumsinya perlu **terlihat dan bisa dibantah**, bukan tertanam.

---

## §17.11 — Recovery Intelligence

```
Sleep + Activity + HRV + Rest + Training Load + Subjective Feedback
        ↓
Recovery Estimate
```

> Recovery rendah → workout intensity diturunkan.
>
> Ini adalah **adaptive recommendation, bukan diagnosis.**

---

> ⭐⭐⭐ **`Subjective Feedback` berdiri sejajar dengan HRV dan Training Load —
> dan itu keputusan yang jarang dibuat oleh sistem yang punya sensor.**
>
> Godaan setiap produk kebugaran adalah memperlakukan angka sebagai kebenaran
> dan laporan orangnya sebagai gangguan. Menaruh keduanya di masukan yang sama
> berarti **orang boleh membantah jam tangannya** — dan itu satu-satunya jalur
> koreksi yang §17.19 butuhkan untuk membedakan *sensor anomaly* dari *human
> anomaly*, serta bentuk `Edit` yang **E-74** minta, muncul di tempat yang tepat.

> ⭐ **"Adaptive recommendation, bukan diagnosis" adalah pengulangan kedua dari
> prinsip §17.7** — dan pengulangan di tempat yang berbeda adalah tanda bahwa
> prinsipnya sedang benar-benar dipakai, bukan hanya dinyatakan sekali di
> pembuka.

> ⚠️ **Enam masukan, satu keluaran, dan bobotnya tidak disebut** — bentuk yang
> sama dengan `Sleep Score`. Yang lebih penting di sini: **apa yang terjadi
> kalau HRV tidak tersedia?** Sebagian besar perangkat tidak mengukurnya
> semalaman, dan §17.3 sendiri menandai beberapa sinyal sebagai opsional.
> Sebuah estimasi yang diam-diam berjalan tanpa dua dari enam masukannya adalah
> **B-14** ([#26](../../issues/26)) persis — dan obatnya sudah dua kali
> diusulkan: **`confidence` turun sebanding dengan bagian masukan yang benar-benar
> ada.**

---

## §17.12 — Fitness Intelligence

```
Fitness Twin
├── Strength   ├── Endurance     ├── Mobility
├── Activity   ├── Training Load ├── Recovery
└── Progress
```

```
Current → Goal → Gap → Training Plan
```

---

> ⭐ **`Gap` sebagai langkah tersendiri antara `Goal` dan `Training Plan`**
> memaksa sistem menyatakan **jaraknya** sebelum menyusun rencana — dan jarak
> yang dinyatakan bisa dibantah pengguna, sementara rencana yang langsung keluar
> tidak.

> ⚠️ **`Strength`, `Endurance`, dan `Mobility` tidak punya cara diukur dari
> wearable mana pun di §17.3.** Ketiganya menuntut tes yang dilakukan sengaja
> (angkat beban tertentu, lari jarak tertentu, rentang gerak) atau laporan
> pengguna. Naskah tidak menyebut dari mana angkanya datang — dan tanpa itu,
> `Progress` adalah grafik tanpa sumber. Ini bentuk **A-19** yang khas fase ini:
> model dengan medan yang tidak punya produsen.

---

## §17.13 — Adaptive Workout Engine

> Ini mengintegrasikan **Phase 11 Agent + Phase 12 Simulation.**

```
Goal → Current Fitness → Recovery → Available Time → Simulation
→ Workout Recommendation
```

```
Normal day        → Full workout
Low recovery      → Reduced intensity
Very low readiness → Recovery / rest recommendation
```

---

> ⭐⭐⭐ **Tiga baris keluaran itu adalah tangga yang berakhir pada ISTIRAHAT —
> dan sistem yang bisa merekomendasikan tidak melakukan apa-apa adalah sistem
> yang berbeda jenis dari yang tidak bisa.**
>
> Ini pola yang sudah muncul tiga kali dan pantas disebut sebagai sifat proyek:
> `Stop?` sebagai keluaran setara (§14.63) · degradasi berakhir di **diam**
> (§14.35) · `Robot slows → Wait` (§16.11) · **`Wait` sebagai skill setara
> `Pick`** (§16.24). Untuk mesin rekomendasi kebugaran, godaan komersialnya
> justru sebaliknya — keterlibatan naik kalau ada sesuatu untuk dilakukan setiap
> hari.

> ⭐⭐ **`Available Time` sebagai masukan sejajar dengan `Recovery`** adalah
> pengakuan bahwa rencana yang benar secara fisiologis tetapi tidak muat di hari
> seseorang adalah rencana yang salah. Ia juga jembatan pertama ke §17.47
> (*Health ↔ HumanOS*), karena waktu yang tersedia hanya diketahui penjadwal.

> ⚠️ **`Very low readiness` memakai kata `readiness` yang tidak ada di
> `bio_state` §17.7 maupun di `Health Twin` §17.6** — keduanya memakai
> `recovery` dan `fatigue`. Satu kata ketiga untuk hal yang tampaknya sama.
> Pola yang sudah berulang (tiga arti "HumanOS" **E-114**, empat "sandbox"
> **E-105**, tiga "KILL" **E-120**), dan di sini ia murah diperbaiki karena
> istilahnya baru lahir.

> 🛑 **Dan ini tempat pertama di naskah ini di mana sistem MENURUNKAN sesuatu
> yang diinginkan pengguna** — intensitas latihan yang sudah direncanakan.
> Itu benar secara fisiologis dan tetap perlu satu aturan: **pengguna boleh
> menolak penurunan itu**, dan penolakannya bukan kesalahan. §17.7 sudah
> menetapkan *State ≠ diagnosis*; konsekuensinya, sebuah skor tidak boleh
> menjadi izin. Tanpa kalimat itu, `Recovery Estimate` yang dihitung dari enam
> sinyal — dua di antaranya mungkin tidak ada — berhenti menjadi saran dan
> menjadi pagar.
