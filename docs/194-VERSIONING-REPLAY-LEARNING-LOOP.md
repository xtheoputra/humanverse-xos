# 194 — §12.17–§12.20 Twin Versioning, Twin Replay, Decision Replay & Learning Loop

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.17 — Digital Twin Versioning

```
Twin v1 → Twin v2 → Twin v3 → …

Twin Snapshot
2026-09-07 09:00
```

> Simulation memakai snapshot tersebut. **Ini membuat hasil bisa
> direproduksi.**

---

> ⭐⭐⭐ **Reproducibility adalah sifat rekayasa yang belum pernah disebut di
> enam belas naskah — dan ia menyelesaikan masalah yang saya catat tiga sesi
> lalu.**
>
> Di berkas [`156`](156-MEMORY-KONSOLIDASI-DECAY.md) saya menulis: peluruhan
> memori (§9.9) bertabrakan dengan jejak audit, karena *"kalau memori yang
> mendasari sebuah rekomendasi sudah luruh, jejak auditnya tetap menunjuk
> memori yang sudah tidak berbunyi sama seperti dulu"* — dan usul saya waktu
> itu adalah menyimpan `strength` **pada saat itu** di `audit_logs`.
>
> Snapshot lebih baik daripada menyalin nilai: `audit_logs` cukup menunjuk
> **`twin_snapshot_id`**, dan seluruh keadaan pada saat keputusan diambil
> terpelihara utuh — bukan satu field, melainkan delapan belas komponen beserta
> `confidence` dan `volatility`-nya.
>
> Itu juga yang membuat **E-75** ([#64](../../issues/64)) bisa ditutup dengan
> benar: `rationale` yang berantai sampai ke sumbernya (§10.25) sekarang punya
> sumber yang **tidak berubah** untuk ditunjuk.

---

## §12.18 — Twin Replay

> *"Apa yang sebenarnya terjadi selama 30 hari terakhir?"*

```
Day 1 → State → Events → Decision → Action → Outcome
Day 2 → …
```

---

> ⭐ **Replay adalah bentuk yang benar untuk tinjauan mingguan §11.41** —
> `Sunday: Review` sekarang punya bahan yang bisa dijalankan ulang, bukan
> ringkasan yang dibuat sekali lalu dipercaya.
>
> ⚠️ Dan ia langsung memberi alat untuk **B-26** ([#83](../../issues/83)):
> tinjauan yang dibangun dari dua hari data karena sinyal mati hari Rabu akan
> **terlihat** di replay — hari-hari kosong tidak bisa disembunyikan ketika
> ditampilkan hari per hari. Yang perlu ditambahkan hanya kewajiban
> melaporkannya.

---

## §12.19 — Decision Replay

```
Decision made:  2026-08-01
Expected:       Outcome = 75
Actual:         Outcome = 61
        ↓
Expected vs Actual → Error Analysis → Model Update
```

---

## §12.20 — Simulation → Learning Loop

```
Simulation → Prediction → Real World → Actual Outcome
→ Prediction Error → Evaluation → Model Update → Better Simulation
```

> Ini adalah salah satu **AI flywheel terpenting** HumanVerse.

---

> ⭐⭐⭐ **Ini yang menutup B-24 / [#70](../../issues/70) — dan jawabannya lebih
> baik daripada ketiga pilihan yang saya ajukan.**
>
> Keberatan saya: *Counterfactual Engine menjanjikan jawaban yang §9.17
> melarang memberikannya*, karena **sumber data untuk model transisi tidak
> ada**. Saya menawarkan tiga jalan keluar:
>
> | Jalan yang saya usulkan | Masalahnya |
> |---|---|
> | (a) transisi dari eksperimen pengguna sendiri | paling benar, berbulan-bulan per hubungan |
> | (b) transisi dari pengetahuan umum | rata-rata populasi dijual sebagai jawaban personal |
> | (c) hanya perbandingan relatif tanpa angka absolut | paling jujur, tapi terbatas |
>
> Naskah memilih jalan **keempat**: kekuatan panah kausal dipelajari dari
> **galat prediksinya sendiri**. Sistem menebak, mencatat tebakannya,
> mengamati kenyataan, mengukur selisihnya, dan memperbaiki modelnya.
>
> Itu memutus lingkaran tanpa butuh eksperimen terkendali maupun pinjaman dari
> rata-rata populasi — dan ia **prinsip yang sama** dengan `Prediction
> Calibration` §9.34 yang menutup **B-10** ([#27](../../issues/27)): kebenaran
> acuan tidak perlu dicari, ia **dihasilkan sistem sendiri** dari hasil yang
> teramati.
>
> `Expected 75 → Actual 61` adalah satu baris data yang tidak butuh penilai
> manusia, tidak butuh model menilai model, dan datang gratis setiap kali
> sebuah keputusan berbuah. Dicatat sebagai **H-23**.

> ⭐ **`prediction_errors` sebagai tabel tersendiri** (§12.28) menandakan ini
> dirancang untuk dipakai, bukan disebut. Dan `simulation_evaluations`
> melengkapinya.

> 🛑 **Tetapi loop ini butuh titik mulai, dan titik mulainya belum ada.**
> Sebelum ada galat prediksi pertama, tidak ada yang bisa dikalibrasi — dan
> prediksi pertama harus datang dari **suatu tempat**. Tiga kemungkinan, dan
> yang mana dipakai menentukan apa yang boleh ditampilkan di bulan-bulan
> pertama:
>
> | Titik mulai | Konsekuensi |
> |---|---|
> | pengetahuan umum (*tidur memengaruhi fokus*) | cepat, tapi itu jalan (b) yang saya keberatan — **kecuali** ditandai sebagai asumsi awal di §12.14 dan `confidence`-nya rendah |
> | tanpa panah sama sekali | hanya perbandingan relatif (jalan c) sampai data cukup — paling jujur |
> | menolak menyimulasi | aman, tapi seluruh fase tidak bisa dipakai sampai berbulan-bulan |
>
> Yang kedua paling masuk akal untuk V0–V2, dan ia **sudah punya bentuknya**:
> §12.7 membandingkan delapan dimensi antar-skenario tanpa perlu angka absolut.
>
> Ini juga **B-1** (cold start) dan **B-21** ([#48](../../issues/48)) dalam
> bentuk baru. Lihat **B-27** / [#88](../../issues/88).

> ⚠️ **`Model Update` yang otomatis menyentuh B-10 dari sisi lain.** Butir itu
> memperingatkan *Automatic Rollback* yang skornya sekadar model menilai model.
> Di sini yang menilai adalah **kenyataan**, jadi keberatannya tidak berlaku —
> tapi satu pengaman tetap perlu: **model tidak boleh memperbarui dirinya dari
> satu galat.** Prinsipnya sudah ada dua kali di naskah lain (§9.8 *"satu kali
> beli kopi bukan preferensi"*, §11.31 *"rejected ≠ tidak suka, butuh repeated
> evidence"*), dan berlaku sama di sini.
