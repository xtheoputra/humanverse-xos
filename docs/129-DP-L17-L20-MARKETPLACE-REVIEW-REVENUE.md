# 129 — DP-L17–L20: Marketplace, Review, Revenue & Analytics

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L17 — Marketplace

Kategori:

```
Fashion · Fitness · Learning · Finance · Travel · Productivity
```

Setiap agent memiliki: **rating · installs · version · permissions**.

> ⭐ **`permissions` ditampilkan di halaman marketplace**, bukan disembunyikan
> di layar persetujuan. Itu yang membuat pengguna bisa membandingkan dua agent
> sejenis berdasarkan seberapa banyak data yang dimintanya.
>
> ⚠️ Enam kategori ini tidak cocok dengan daftar mana pun sebelumnya: 12 modul
> naskah 1, 14 agent naskah 4, 22 agent naskah 5. *Grooming*, *Health*,
> *Social*, dan *Nutrition* tidak punya kategori.

---

## DP-L18 — Review System

> Sebelum dipublikasikan, checklist:

```
Security · Permission · Stability · Documentation · Testing
```

> **Agent tidak langsung publish.**

> ⭐⭐ **Bersama Sandbox (DP-L14), ini bagian terbesar dari jawaban A-15/C-7**
> yang selama enam naskah hanya berupa kekhawatiran. Proses review akhirnya
> punya bentuk.
>
> ⚠️ Tiga hal yang masih hilang, dan ketiganya bagian termahal dari menjalankan
> marketplace sungguhan:
>
> - **Perjanjian pemroses data** dengan developer — begitu agent pihak ketiga
>   membaca data tidur atau jurnal, Anda menjadi pemroses data untuk mereka.
> - **Jalur banding** ketika agent ditolak atau dicabut.
> - **Tanggung jawab** ketika agent orang lain berbuat salah pada data
>   pengguna Anda.
>
> ⚠️ **Siapa yang mereview?** Untuk proyek satu orang, checklist ini akan
> dijalankan oleh orang yang sama yang membangun platformnya. Itu tidak apa-apa
> sekarang, tapi perlu ditulis — supaya kelak tidak dikira sudah ada
> pemeriksaan pihak kedua.

---

## DP-L19 — Revenue Platform

Kemungkinan model:

```
Free · Premium · Subscription · One-time Purchase
```

> Developer mendapat **payout**.

> ⚠️ **Belum ada angka bagi hasil**, dan ini sekarang tempat ketiga tempat
> monetisasi dibahas: enam paket harga naskah 1, `Billing` sebagai domain
> platform naskah 7 Layer 3, dan Phase 9 (*Subscription*, *Revenue Platform*).
> Ketiganya perlu satu tempat. Bertaut **A-6** dan **E-41**.

---

## DP-L20 — Analytics Platform

Developer melihat: **installs · retention · crashes · latency · revenue**.

```
Installs → Activation → Retention → Revenue
```

> ⚠️ **`retention` diberikan kepada developer pihak ketiga** sebagai metrik
> resmi. Layer 34 naskah 7 sendiri memperingatkan: *"jangan mengoptimalkan
> manipulasi; optimalkan pengalaman pengguna"* — dan retention adalah metrik
> yang paling mudah dinaikkan dengan cara yang merugikan pengguna.
>
> Kalau platform memberi developer alat untuk mengejar retention tanpa
> memberikan metrik penjaganya (**`annoyance`** dari Pillar 10 naskah 9), maka
> peringatan itu hanya berlaku untuk tim internal, tidak untuk ekosistem.
> Usul: `annoyance` dan `notifications per day` ikut ditampilkan di dasbor
> developer, bukan hanya di dasbor internal.
