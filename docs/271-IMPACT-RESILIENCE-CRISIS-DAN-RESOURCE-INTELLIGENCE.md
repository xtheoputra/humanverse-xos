# 271 — §20.18–§20.21 Impact Assessment, Resilience Engine, Crisis Intelligence & Resource Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.18 — Impact Assessment Engine

> `Decision → Impact Simulation →` `Human · Economic · Social · Environmental ·
> Security · Technology Impact`
>
> Kemudian: `Impact Score · Risk Score · Uncertainty · **Affected Stakeholders**`

---

> ⭐⭐⭐⭐ **`Affected Stakeholders` sebagai KELUARAN — dan itu yang paling
> dibutuhkan fungsi utilitas §20.9.**
>
> §20.9 menjumlahkan `Externality` ke dalam satu angka, dan **C-30** mencatat
> masalahnya: eksternalitas menurut definisinya ditanggung pihak yang tidak ikut
> menyetel bobotnya. Sebuah keluaran yang **menyebutkan siapa saja yang terkena**
> mengubah pertanyaannya dari *"berapa besar biayanya"* menjadi **"siapa yang
> membayarnya"** — dan yang kedua bisa dibantah oleh orang yang namanya ada di
> daftar.
>
> ⭐ Bersama `Stakeholders` sebagai gerbang di §20.17, ini bahan lengkap untuk
> aturan yang belum ditulis: **pilihan yang memindahkan biaya ke pihak yang
> tidak menyetel bobotnya memerlukan persetujuan terpisah.**

> ⭐⭐ **`Uncertainty` dilaporkan sejajar dengan `Impact Score` dan `Risk
> Score`**, meneruskan pembedaan §18.24 dan §20.5. Penilaian dampak yang tidak
> menyebut seberapa yakin ia pada dirinya sendiri akan dipakai seolah pasti.

> ⚠️ **Tetapi `Impact Score` dan `Risk Score` adalah dua angka tunggal yang
> meratakan enam dimensi — dan naskah ini sendiri menolak angka tunggal di
> tempat lain.**
>
> `Human Impact` dan `Economic Impact` tidak bisa saling menggantikan: sebuah
> keputusan yang sangat baik secara ekonomi dan buruk bagi manusia akan
> menghasilkan skor menengah, **dan skor menengah tidak menyerupai keduanya**.
> Ini persis alasan §18.20 menolak skor kepercayaan tunggal (**Trust Vector**),
> §17.36 menolak *accuracy* sendirian, dan §19.18 menaruh `effect size` di
> samping uji hipotesis — dan persis keberatan yang sama sudah dicatat untuk
> `Reproducibility Score` §19.19 (**G-18** / [#137](../../issues/137)).
> ⭐ Bentuknya sudah jadi: **vektor enam dimensi, dengan `Human` sebagai dimensi
> yang tidak bisa dikompensasi** — sama seperti `safety` di Trust Vector.

---

## §20.19 — Civilization Resilience Engine

> Sistem tidak hanya mengejar **efisiensi**. Tetapi: **resilience.**

```
Failure → Dependency Graph → Impact Propagation → Alternative Paths → Recovery Plan
```

---

> ⭐⭐⭐⭐ **Menyatakan ketahanan sebagai tujuan yang BERBEDA dari efisiensi
> adalah pilihan yang menentukan, dan naskah ini menaruhnya di dua tempat.**
>
> Efisiensi dan ketahanan **saling menukar**: sistem yang paling efisien adalah
> yang paling sedikit cadangannya, dan cadangan itulah yang menahan kegagalan.
> Optimasi yang hanya melihat efisiensi akan menghapus ketahanan **sebagai
> pemborosan** — itu mekanisme di balik sebagian besar kegagalan rantai pasok
> yang pernah terjadi. §20.9 sudah menaruh `+ Resilience` di dalam fungsi
> utilitas; bagian ini memberinya mesin.

> ⭐⭐⭐ **Dan rantainya memakai `depends_on` §20.4 — bukan `affects`.**
>
> Itu sambungan yang benar dan jarang dibuat: rambatan kegagalan menuntut relasi
> yang menyatakan *"kalau yang ini hilang, yang itu berhenti"*, bukan relasi
> pengaruh. `Alternative Paths` lalu menjadi pertanyaan graf yang **bisa
> dihitung**, bukan penilaian. Untuk tujuh sistem yang didaftar (`Food · Energy ·
> Healthcare · Transportation · Communication · Cloud · Supply Chain`), itu
> selisih antara daftar kekhawatiran dan alat.

> ⚠️ **Tetapi `Cloud Infrastructure` ada di daftar sistem kritis — dan
> HumanVerse sendiri berjalan di atasnya.** Sebuah mesin ketahanan yang
> memodelkan kegagalan awan tetapi tidak memodelkan **kegagalan dirinya
> sendiri** akan berhenti tepat ketika ia dibutuhkan. §20.11 (node lokal)
> adalah jawaban arsitekturalnya, dan keduanya belum saling menyebut.

---

## §20.20 — Crisis Intelligence

```
Signal → Detection → **Verification** → Classification → Simulation
   → **Response Options** → Coordination → Recovery
```

> HumanVerse berperan sebagai **decision-support and coordination
> infrastructure, bukan otoritas tunggal.**

---

> ⭐⭐⭐⭐⭐ **`Verification` di dalam rantai, `Response Options` dalam bentuk
> jamak, dan *"bukan otoritas tunggal"* — tiga hal yang menjawab sebagian besar
> C-28.**
>
> **C-28** ([#123](../../issues/123)) mencatat §18.25 mengeluarkan peringatan
> *"tanpa gerbang dan tanpa penerima yang ditentukan"*, dengan empat pertanyaan:
> siapa penerimanya · ambang mana yang memicu · **apakah manusia meninjau
> sebelum keluar** · apa yang terjadi kalau keliru.
>
> | Yang terjawab | Bagaimana |
> |---|---|
> | tinjauan sebelum keluar | **`Verification` sebagai langkah wajib**, sesudah `Detection` dan sebelum apa pun yang keluar |
> | kewenangan | *"bukan otoritas tunggal"* — HumanVerse **menyarankan**, tidak memutuskan |
> | bentuk keluaran | **`Response Options`**, bukan `Response` — sistem memberi pilihan, orang memilih |
>
> `Response Options` khususnya: satu huruf jamak yang memindahkan keputusan dari
> mesin ke manusia, konsisten dengan §20.2 dan §20.9. Dan menaruh `Simulation`
> **sebelum** pilihan berarti setiap pilihan datang dengan perkiraan akibatnya.

> ⚠️ **Yang masih terbuka dari C-28: ambang pemicu dan penerima.** *"Signal →
> Detection"* tidak menyatakan seberapa kuat sinyal harus sebelum rantai
> berjalan, dan `Coordination` tidak menyatakan **siapa yang dikoordinasi** —
> satu pengguna, organisasi, atau kota. Untuk `natural disaster` dan
> `infrastructure failure` yang naskah sebut sendiri, keduanya adalah pertanyaan
> hukum, bukan hanya teknis. ⭐ Bahannya kini ada: §20.18 memberi
> `Affected Stakeholders`, §17.38 memberi tujuh kategori escalation berjenjang.

---

## §20.21 — Civilization Resource Intelligence

Sumber daya: `Energy · Food · Water · Materials · Land · **Computing** ·
**Human Labor** · Capital · Knowledge`

```
Energy → Computing → AI → Industry → Economy → Human
```

---

> ⭐⭐⭐ **`Computing` sebagai sumber daya sejajar dengan `Energy` dan `Water`
> adalah kejujuran yang jarang ditulis oleh sistem AI tentang dirinya sendiri.**
>
> Rantai `Energy → Computing → AI` menempatkan HumanVerse **di dalam** model
> sumber dayanya sendiri — ia mengakui bahwa kecerdasan yang dijalankan sistem
> ini memakai listrik yang sama dengan yang dimodelkannya. Itu sejalan dengan
> `environmental impact` §19.22 dan dengan `+ Resilience` §20.9, dan ia
> mencegah kekeliruan yang khas: memperlakukan komputasi sebagai sesuatu yang
> tak terbatas ketika menyarankan lebih banyak komputasi.

> 🛑🛑 **Tetapi `Human Labor` berdiri di daftar SUMBER DAYA yang akan
> dioptimalkan — dan §8.10 melarang `employment scoring` dengan kata-kata itu
> sendiri.**
>
> Delapan butir lain adalah benda, energi, atau modal. Yang satu ini adalah
> orang. Dan kalimat penutup bagian ini berbunyi *"memungkinkan **resource
> optimization** lintas sistem"* — yaitu, dalam bacaan yang paling langsung,
> **mengoptimalkan tenaga manusia sebagai masukan produksi.**
>
> Ini bentuk **C-27** ([#122](../../issues/122)) pada skala terbesarnya: di sana
> `productivity` dihitung atas komponen `People` sebuah organisasi; di sini
> tenaga kerja menjadi variabel dalam optimasi lintas sistem. §8.10 menutup
> **menilai**; ia belum menutup **mengoptimalkan**, dan yang kedua justru lebih
> jauh.
>
> ⭐ Dan naskah ini punya penawarnya sendiri, tiga bagian kemudian: **§20.22
> menaruh `Human Wellbeing` sebagai suku PERTAMA fungsi tujuannya**, bukan
> `GDP`. Yang perlu dinyatakan agar keduanya tidak bertabrakan: **manusia
> adalah TUJUAN fungsi itu, bukan suku di dalam masukannya** — dan `Human
> Labor` sebagai sumber daya hanya sah pada agregat, tidak pernah pada orang.
> Lihat **C-30** / [#141](../../issues/141).

> ⚠️ **`Knowledge` sebagai sumber daya juga menuntut kehati-hatian yang berbeda
> dari delapan lainnya:** ia satu-satunya yang **tidak berkurang ketika
> dipakai**, dan memodelkannya dengan mesin yang sama seperti `Water` akan
> menghasilkan aturan kelangkaan untuk hal yang tidak langka. §19 seluruhnya
> dibangun di atas sifat sebaliknya.
