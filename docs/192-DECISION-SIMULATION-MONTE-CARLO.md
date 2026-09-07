# 192 — §12.11–§12.13 Decision Simulation, Monte Carlo & Future State Projection

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.11 — Decision Simulation

> User bertanya: *"Saya harus mengambil keputusan A atau B?"* — HumanVerse
> **tidak langsung memberikan jawaban**.

```
Decision → Options → Constraints → Preferences → Current State
→ Historical Data → World State → Scenario Generation → Simulation
→ Outcome Distribution → Risk Analysis → Utility Analysis
→ Recommendation
```

---

> ⭐⭐ **Dua belas langkah, dan `Recommendation` di akhir — bukan di awal.**
> Itu penerapan paling lengkap dari *"decision support, bukan pengambil
> keputusan"* (naskah 4 §27). Bandingkan dengan **§9.24**, yang memisahkan
> *"saya menyarankan A"* dari *"mari kita bandingkan A, B, dan C"*: rantai ini
> adalah versi kedua, dengan sembilan langkah kerja sebelum satu kalimat saran.

> ⭐ **`Outcome Distribution`, bukan `Outcome`.** Satu kata yang menjaga seluruh
> disiplin: keluaran simulasi adalah **sebaran**, bukan satu angka. Itu yang
> membuat §12.12 masuk akal dan §12.15 bisa bekerja.

---

## §12.12 — Monte Carlo Simulation

```
Scenario A    Expected outcome = 72    Risk = 18
Scenario B    Expected outcome = 81    Risk = 35
Scenario C    Expected outcome = 76    Risk = 12
```

Bukan *"B pasti terbaik"*, tetapi:

> *"B memiliki expected outcome tertinggi, tetapi risikonya juga paling
> tinggi."*

---

> ⭐⭐⭐ **Kalimat itu adalah bentuk keluaran yang benar, dan ia menolak godaan
> terbesar dari seluruh fase ini: memberi peringkat.**
>
> Tiga baris angka hampir memaksa pembaca menyimpulkan pemenang. Kalimatnya
> menolak — dan yang menolaknya bukan basa-basi melainkan **fakta yang terbaca
> dari tabelnya sendiri**: B unggul di satu kolom dan kalah di kolom lain.
> Siapa yang menang bergantung pada seberapa besar seseorang menghargai risiko,
> dan itu **bukan milik sistem** — itu `w6 Risk` di Personal Utility Model
> §12.21, yang penggunanya sendiri tetapkan.
>
> ⚠️ Dan di situlah kehati-hatiannya harus dijaga: §12.11 langkah *Utility
> Analysis* **akan** menggabungkan dua kolom itu jadi satu angka. Begitu itu
> terjadi, kalimat jujur di atas berubah jadi peringkat lagi — kecuali bobotnya
> **terlihat dan bisa diubah** pengguna. Bertaut **C-16** /
> [#71](../../issues/71).

> ⚠️ **`Risk = 18` dan `Risk = 35` memakai skala yang belum pernah ada.**
> Skala yang sudah berjalan: persen · 100 poin · 0–1 · huruf `A` · `x/10` ·
> `R0–R4`. Ini yang ketujuh, dan arahnya terbalik dari yang lain (lebih besar
> = lebih buruk) tanpa penanda — masalah yang sama persis dengan `Risk: 4/10`
> di §9.24. Usul di [#32](../../issues/32) tetap: **simpan `0–1`, tampilkan apa
> saja, dan setiap dimensi membawa arahnya sendiri** (`higher_is_better`).

> ⚠️ **Monte Carlo menuntut sebaran masukan, bukan hanya nilai tengah.** Untuk
> menjalankan seribu putaran, sistem harus tahu **seberapa lebar** variasi tiap
> masukan — dan `volatility` §12.1 adalah kandidat yang tepat untuk itu.
> Hubungan keduanya belum ditulis, padahal keduanya lahir di naskah yang sama.

---

## §12.13 — Future State Projection

Horizon: **1 hari · 7 hari · 30 hari · 90 hari · 1 tahun · 3 tahun · 5 tahun**

```
Current Goal Progress: 32 %
30 days → 41 %      90 days → 57 %      1 year → 82 %
```

Setiap proyeksi memiliki: `probability · confidence interval · assumptions ·
uncertainties`

---

> ⭐ **Tujuh horizon menggantikan tiga angka tetap yang bertabrakan** — Digital
> Twin punya 30 hari (naskah 1), 14 hari (naskah 2), dan 30/90/365 (naskah 4
> §26), yang jadi butir **E-29**/**E-7**. Naskah 13 §9.18 sudah mengubahnya
> jadi **kelas** (Immediate/Short/Medium/Long); di sini kelasnya diberi angka.
> Butir itu praktis tertutup.

> 🛑 **Tetapi horizon 3 dan 5 tahun adalah klaim yang berbeda jenis dari yang
> lain, dan naskah tidak membedakannya.**
>
> Proyeksi 30 hari atas kemajuan tujuan bisa diperiksa dalam 30 hari — dan
> §12.20 memakainya untuk memperbaiki model. Proyeksi **5 tahun** tidak bisa
> diperiksa oleh siapa pun sampai lima tahun lewat; ia **tidak pernah masuk
> loop belajar**. Artinya ia satu-satunya keluaran sistem yang **tidak bisa
> dikalibrasi**, sementara ia justru yang paling memengaruhi keputusan besar.
>
> Ditambah: §12.10 memproyeksikan **wealth trajectory** dan kondisi kesehatan.
> Proyeksi keuangan lima tahun adalah bentuk yang paling mudah dibaca sebagai
> janji (**C-4**), dan proyeksi kesehatan mendekati garis **C-2**.
>
> Yang perlu diputuskan: **sampai horizon berapa proyeksi boleh ditampilkan**,
> dan apakah horizon yang tidak bisa dikalibrasi ditampilkan sama sekali.
> Lihat **A-29** / [#86](../../issues/86).

> 🛑 **`82 %` pada satu tahun adalah angka presisi untuk sesuatu yang tidak
> presisi — persis keluhan B-15.** Butir itu mencatat `"energy": 0.62` terlihat
> seperti fakta karena angkanya presisi; `1 year → 82 %` lebih jauh lagi,
> karena ia tentang masa depan.
>
> ⭐ Yang menyelamatkannya ada di baris berikutnya: **`confidence interval`**.
> Ini pertama kalinya di enam belas naskah sebuah angka datang dengan
> **rentang**, bukan hanya keyakinan. `82 %` sendirian menyesatkan; `82 % ±
> 15 %` tidak. Aturan yang mengikuti dan tinggal ditulis: **proyeksi ditampilkan
> sebagai rentang, tidak pernah sebagai satu angka** — dan makin jauh
> horizonnya, makin lebar rentangnya sampai titik di mana menampilkannya tidak
> lagi berguna.

> ⭐ **`assumptions` sebagai field wajib pada proyeksi** menyambung langsung ke
> §12.14, dan itu yang membuat proyeksi bisa dibantah: pengguna yang melihat
> *"asumsi: beban kerja tetap"* bisa berkata *"tidak, bulan depan saya pindah
> kerja"* — dan proyeksinya batal dengan benar, bukan diam-diam salah.
