# 159 — §9.18–§9.19 Prediction Engine & Prediction Types

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.18 — Layer 8: Prediction Engine

Beberapa horizon:

```
Immediate    → Hours
Short-term   → Days
Medium-term  → Weeks
Long-term    → Months
```

Contoh:

```
Prediction:
Probability of habit completion tomorrow = 0.68
```

bukan:

```
You will definitely complete it.
```

---

> ⭐ **Empat horizon ini menyelesaikan E-29 / E-7 tanpa menyebutnya.** Digital
> Twin punya tiga horizon berbeda di tiga naskah: **30 hari** (naskah 1) ·
> **14 hari** (naskah 2) · **30/90/365 hari** (naskah 4 §26). Semuanya angka
> tetap. Di sini horizon menjadi **kelas**, bukan angka — dan angka spesifik
> menjadi urusan tiap jenis prediksi. Itu bentuk yang benar: prediksi
> penyelesaian habit besok dan prediksi kemajuan goal enam bulan tidak
> semestinya dipaksa memakai jendela yang sama.

> ⚠️ **`Probability of habit completion tomorrow = 0.68` adalah prediksi
> pertama di dua belas naskah yang bisa langsung diuji benar-salahnya** — dan
> itu penting jauh melebihi contohnya sendiri. Lihat §9.34.

---

## §9.19 — Prediction Types

```
Behavior Prediction
Preference Prediction
Goal Progress Prediction
Habit Completion Prediction
Engagement Prediction
Energy Prediction
Context Prediction
Outcome Prediction
```

Setiap prediction:

```json
{
  "prediction": "...",
  "probability": 0.73,
  "horizon": "7d",
  "confidence": 0.68,
  "evidence": []
}
```

---

> ⭐⭐ **`probability` dan `confidence` dipisahkan — dan itu benar.** Keduanya
> sering dikira sama. Bedanya menentukan:
>
> ```
> probability = seberapa mungkin hal itu terjadi
> confidence  = seberapa yakin sistem pada angka probability-nya
> ```
>
> *"Kemungkinan 50 %, keyakinan tinggi"* (koin) sama sekali berbeda dari
> *"kemungkinan 50 %, keyakinan rendah"* (tidak tahu apa-apa). Sistem yang
> hanya punya satu angka tidak bisa membedakan keduanya — dan justru yang kedua
> yang harus memicu *"tanya pengguna"* (**H-14**).
>
> `evidence: []` melengkapinya: prediksi tanpa bukti terlihat sama dengan
> prediksi berbukti kalau hanya angkanya yang ditampilkan.

> ⚠️ **`Engagement Prediction` adalah satu-satunya di daftar ini yang melayani
> produk, bukan pengguna.** Tujuh lainnya memprediksi sesuatu tentang hidup
> penggunanya; yang ini memprediksi seberapa sering ia akan memakai aplikasi.
> Begitu angka itu ada, ia akan menarik keputusan ke arah *"apa yang membuat
> orang kembali"* — dan itu berlawanan dengan janji naskah 4 (*"popular ≠
> suitable for the user"*) serta dengan **Brands** di **E-50**.
>
> Kalau ia tetap ada, tempatnya adalah metrik operasional, **bukan masukan
> untuk rekomendasi**. Perbedaan itu harus ditulis, karena secara teknis tidak
> ada yang mencegahnya masuk ke §9.25 sebagai komponen utility.

> ⚠️ **Delapan jenis prediksi berarti delapan model yang perlu data.**
> Seluruhnya bergantung pada riwayat pengguna — dan butir **B-1** (cold start)
> serta **B-21** / [#48](../../issues/48) berlaku penuh di sini. Yang bisa
> jalan paling awal adalah **Habit Completion**, karena `habit_completions`
> terisi sejak hari pertama V0 dan hasilnya terverifikasi keesokan harinya.
> Itu juga jenis yang paling cocok untuk membangun kalibrasi lebih dulu.
