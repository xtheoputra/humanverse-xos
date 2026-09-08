# 259 — §19.10–§19.12 Scientific Reasoning, Experiment Planner & Variable Management

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.10 — Scientific Reasoning Engine

> Reasoning terdiri dari: `deductive · inductive · **abductive** · analogical ·
> causal reasoning`

```
Known      A → B
Observed   B
Possible explanations   A · C · D
```

> **AI tidak boleh langsung memilih satu jawaban.**

---

> ⭐⭐⭐⭐⭐ **Contoh tiga baris ini adalah bentuk kekeliruan logika yang paling
> sering dilakukan sistem AI — dan naskah ini menuliskannya dengan BENAR, lalu
> menolaknya.**
>
> Dari `A → B` dan `B`, menyimpulkan `A` adalah kekeliruan menegaskan
> konsekuen. Ia terasa benar, ia benar cukup sering untuk tidak ketahuan, dan ia
> **persis cara sebuah model menghasilkan penjelasan yang meyakinkan untuk
> pengamatan apa pun**. Menyebut `C` dan `D` di sebelah `A` — tanpa mengurutkan,
> tanpa memilih — adalah satu-satunya jawaban yang jujur untuk bentuk ini.
>
> Dan pemilik menamainya dengan benar: **`abductive`**, bukan *deduktif*. Ini
> satu-satunya tempat di dua puluh tiga naskah yang membedakan lima jenis
> penalaran, dan pembedaan itu bukan kerapian akademis — **tiap jenis punya
> syarat kesahihan yang berbeda**, dan sistem yang tidak membedakannya akan
> memberi keyakinan deduktif pada kesimpulan abduktif.

> ⭐⭐⭐ **`AI tidak boleh langsung memilih satu jawaban` adalah pengaman pemilik
> yang KESEPULUH — dan ia mengulangi bentuk yang sama dengan §18.23
> `UNRESOLVED`, di sumbu yang berbeda.**
>
> §18.23 mengizinkan sistem berhenti ketika **sumber-sumbernya** bertentangan.
> §19.10 mengizinkannya berhenti ketika **penjelasannya** lebih dari satu. Dua
> naskah berturut-turut menolak jawaban tunggal yang dipaksakan, dan itu
> berhenti menjadi kebetulan — ia menjadi sikap yang bisa dijadikan aturan.

> ⚠️ **Tetapi larangan ini belum punya bentuk keluaran.** *"Tidak boleh langsung
> memilih"* melarang; ia tidak menyatakan **apa yang disajikan sebagai
> gantinya**. §19.7 sudah punya jawabannya untuk kasus sebelahnya — empat status
> bernama, termasuk `mixed evidence` — dan §19.9 sudah membawa `Assumptions`.
> Bentuk yang konsisten: **daftar penjelasan yang bersaing, masing-masing dengan
> bukti dan asumsinya**, dan tidak ada satu pun yang naik menjadi jawaban tanpa
> langkah yang menyatakan mengapa yang lain gugur.

> ⚠️ **`causal reasoning` berdiri di daftar yang sama tanpa menyebut tangga
> yang sudah ada.** §17.9 memberi empat tingkat bukti kausal, §18.9 memberi lima
> (**E-138** / [#124](../../issues/124)). Bagian ini adalah tempat paling wajar
> untuk memakainya, dan ia tidak menyebut satu pun. Sebuah mesin penalaran yang
> punya `causal reasoning` sebagai mode tetapi tidak punya tingkat bukti akan
> menghasilkan klaim sebab tanpa cara menyatakan seberapa berhak ia.

---

## §19.11 — Experiment Planner

> **Input:** `hypothesis · constraints · resources · timeline`
>
> **Output:** `protocol · variables · controls · measurements ·
> sample considerations · **risks**`

---

> ⭐⭐⭐ **`resources` dan `timeline` sebagai MASUKAN adalah pengakuan yang jarang
> ditulis: eksperimen terbaik yang tidak bisa dijalankan bernilai nol.**
>
> Perencana yang hanya menerima hipotesis akan menghasilkan protokol ideal yang
> menuntut alat yang tidak dimiliki dan waktu yang tidak ada. Menjadikan batas
> sebagai masukan berarti keluarannya **bisa dikerjakan**, dan itu perbedaan
> antara alat bantu dan latihan pikiran. Ini bentuk yang sama dengan §18.14
> menolak pengumpulan terpusat sebagai keputusan arsitektur: **batas ditulis ke
> dalam rancangan, bukan diperiksa sesudahnya.**

> ⭐⭐ **`risks` ada di keluaran** — dan ini satu-satunya rantai di naskah ini
> yang menyebut risiko sama sekali. Ia memberi §19.22 dan §19.23 titik sambung
> yang wajar.

> 🛑 **Tetapi §19.22 Ethics Review TIDAK ADA di rantai ini, padahal keluarannya
> adalah protokol yang §19.15 kirimkan ke laboratorium fisik.**
>
> §19.22 menyebut dirinya *"komponen wajib"* dan memeriksa `human subjects`,
> `privacy`, `bias`, `consent`, `dual-use risk`, `environmental impact`.
> §19.11 menghasilkan `protocol` dan menyerahkannya ke §19.2 → `Simulation` →
> `Evaluation`. Tidak ada satu pun anak panah yang melewati §19.22.
>
> Sebuah komponen yang menyebut dirinya wajib tetapi tidak berdiri di jalur mana
> pun **bukan komponen wajib** — ia komponen yang tersedia. Ini bentuk yang sama
> dengan **E-143** ([#125](../../issues/125)): gerbangnya ada, tidak dipasang.
> Bedanya di sini yang lewat bukan kalimat melainkan **protokol yang akan
> dijalankan mesin**. Lihat **C-29** / [#131](../../issues/131).

> ⚠️ **`sample considerations` adalah satu-satunya butir keluaran yang tidak
> menyebutkan apa yang dihasilkan.** Lima butir lain adalah benda (`protocol`,
> `variables`, `controls`, `measurements`, `risks`); yang satu ini adalah
> *"pertimbangan"*. Padahal justru di sini angkanya paling menentukan: **berapa
> banyak sampel yang dibutuhkan agar efek sebesar ini bisa terdeteksi** adalah
> perhitungan yang bisa dilakukan di muka, dan eksperimen yang kekurangan daya
> statistik akan menghasilkan hasil nol yang tidak berarti apa-apa — lalu
> §19.8 akan membacanya sebagai celah.
>
> ⭐ §19.18 sudah memberi bahannya (`effect size`, `confidence intervals`).
> Yang perlu: **`sample size` sebagai keluaran berangka, dengan `power` dan
> `effect size` yang diasumsikan** — dan asumsi itu masuk ke `Assumptions`
> §19.9.

---

## §19.12 — Variable Management System

> Setiap eksperimen memiliki: `Independent Variable · Dependent Variable ·
> Control · **Confounders** · Constraints`
>
> ```
> WiFi Frequency → Detection Accuracy
> ```

---

> ⭐⭐⭐⭐ **`Confounders` disebut sebagai kelas variabel tersendiri — dan itu
> satu-satunya cara sebuah mesin perencana bisa gagal dengan cara yang
> berguna.**
>
> Variabel bebas, terikat, dan kontrol adalah hal yang **diketahui perancangnya**;
> perancu adalah hal yang **tidak diketahui, dan yang membatalkan kesimpulannya**.
> Memberinya tempat di skema berarti sistem harus **menuliskan apa yang tidak
> dikendalikannya** — dan daftar itu, bukan protokolnya, yang menentukan apakah
> hasilnya boleh dipercaya.
>
> Ia juga menyambung ke tiga tempat lain di naskah ini: perancu adalah tempat
> `Assumptions` §19.9 bersembunyi, ia yang membuat dua klaim §19.7 terlihat
> bertentangan padahal mengukur hal berbeda, dan ia yang §19.6
> `methodological strength` seharusnya nilai.

> ⭐⭐ **Dan contohnya benar untuk domain yang sulit.** `WiFi Frequency →
> Detection Accuracy` adalah rantai sebab yang sesungguhnya penuh perancu —
> tata letak ruangan, bahan dinding, jumlah orang, perangkat lain di pita yang
> sama. Contoh yang memilih kasus mudah tidak menguji skemanya; yang ini
> menguji.

> ⚠️ **Tetapi `Constraints` muncul di sini DAN sebagai masukan §19.11, dengan
> arti yang tampaknya berbeda.** Di §19.11 ia batas **sumber daya** (alat,
> waktu, dana); di §19.12 ia berdiri di daftar **variabel**, sejajar dengan
> perancu. Satu kata, dua tempat, dua arti — pola **E-105**/**E-114** yang sudah
> berulang. Kalau yang dimaksud sama, ia tidak perlu ada dua kali; kalau
> berbeda, salah satunya perlu nama lain.

> ⚠️ **Dan skema ini belum menyatakan bagaimana ia tersimpan bersama hasilnya.**
> §19.31 memberi tabel `variables` dan `experiments` terpisah, tetapi §19.5
> mengekstrak `Result: 92%` **tanpa** variabelnya. ⇒ Eksperimen yang HumanVerse
> rancang akan punya variabel lengkap; klaim yang HumanVerse baca dari
> literatur tidak. Dua kelas bukti dengan kelengkapan yang jauh berbeda, di satu
> graf, dibandingkan oleh §19.7 seolah setara.
