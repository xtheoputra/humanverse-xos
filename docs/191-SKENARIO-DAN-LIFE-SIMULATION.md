# 191 — §12.8–§12.10 Scenario Generator, Scenario Tree & Life Simulation Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.8 — Scenario Generator

Contoh — **Change Career**:

```
A: Stay current career     D: Invest full-time
B: Switch to AI Engineer   E: Hybrid career
C: Build AI startup
```

Kemudian **constraints + resources + skills + preferences + historical
behavior + external conditions** menghasilkan proyeksi masing-masing.

---

> ⭐ **Enam masukan itu semuanya sudah punya rumah**: `constraints` dan
> `resources` di Digital Twin §12.1 (yang baru saja mendapat tempatnya),
> `skills` dan `preferences` juga, `historical behavior` di Behavior Model
> §9.4, dan `external conditions` di World Model §12.3. Tidak ada yang perlu
> diciptakan — hanya dirangkai. Itu tanda arsitektur yang mulai menutup.

> ⚠️ **Opsi A (*"stay current career"*) wajib ada di setiap generator
> skenario, dan itu tidak dinyatakan sebagai aturan.** Sistem yang menghasilkan
> lima jalan berubah tanpa memasukkan *"tidak berubah"* sebagai pilihan setara
> sudah mendorong sebelum membandingkan. Di sini opsi itu ada — di daftar
> pertama, bahkan — tapi sebagai contoh, bukan sebagai kewajiban.
>
> Satu baris cukup: **skenario "tidak melakukan apa-apa" selalu dihasilkan dan
> selalu dibandingkan** — kerabat langsung dari *"Do Nothing adalah kemampuan
> penting bagi agent"* (§11.44).

---

## §12.9 — Scenario Tree

> Bukan hanya satu masa depan.

```
                    CURRENT
          ┌────────────┼────────────┐
        Path A       Path B       Path C
          │            │            │
       Outcome      Outcome      Outcome
       ┌───┴───┐    ┌───┴───┐
      A1      A2   B1      B2
```

> Ini membuat HumanVerse menjadi **decision exploration system**.

---

> ⭐⭐ **Istilah *decision exploration system* adalah penamaan yang tepat, dan
> ia menjaga janji lama.** Naskah 4 §27 menetapkan *"decision support, bukan
> pengambil keputusan"*; pohon skenario adalah bentuk teknis dari janji itu —
> yang ditawarkan adalah **ruang kemungkinan**, bukan satu jawaban.
>
> Ia juga melanjutkan §9.24 *Decision Intelligence* (*"mari kita bandingkan A,
> B, dan C"* alih-alih *"saya menyarankan A"*) satu tingkat lebih dalam:
> sekarang tiap cabang punya cabangnya sendiri.

> ⚠️ **Pohon bercabang tumbuh eksponensial, dan batasnya belum ada.** Tiga jalan
> × dua hasil × dua langkah berikutnya sudah dua belas daun; lima skenario
> §12.8 dengan tiga tingkat kedalaman menjadi ratusan. Setiap daun adalah satu
> simulasi, dan §12.12 menambahkan Monte Carlo di atasnya — yaitu banyak jalan
> per daun.
>
> Dua batas yang perlu ditetapkan sebelum dibangun: **kedalaman maksimum** dan
> **kriteria pemangkasan** (cabang yang melanggar `constraints` §12.22 tidak
> perlu dijelajahi sama sekali). Tanpa itu, biaya satu pertanyaan tidak bisa
> diperkirakan — dan `Budget Engine` §11.18 baru bisa menghentikannya
> **setelah** anggaran habis.

---

## §12.10 — Life Simulation Engine

**Career:** `Skill → Learning → Experience → Job → Income → Network → Opportunity`

**Finance:** `Income → Expenses → Savings → Investment → Risk → Wealth trajectory`

**Health/Lifestyle:** `Sleep → Energy → Exercise → Recovery → Productivity`

**Learning:** `Study → Skill acquisition → Project → Knowledge retention → Career opportunity`

**Social:** `Interaction → Relationship → Network → Opportunity`

---

> ⭐ **Lima rantai ini saling menyambung di ujungnya** — `Opportunity` muncul di
> Career, Learning, dan Social; `Skill` di Career dan Learning. Itu bukan lima
> simulator terpisah melainkan **satu graf dengan lima jalur**, dan §12.24
> menggambarnya begitu. Struktur yang benar.

> 🛑 **Tetapi `Finance` adalah rantai yang paling berbahaya di seluruh naskah,
> dan ia perlu batas yang belum ditulis.**
>
> `Income → Expenses → Savings → **Investment → Risk → Wealth trajectory**`
> menghasilkan proyeksi kekayaan seseorang. Batas **C-4** sudah ditetapkan
> sejak naskah 1 dan dipegang lima naskah berturut-turut: AI boleh analisis
> perilaku finansial, **jangan menjanjikan return investasi**; §8.23 menambahkan
> ✗ *guaranteed returns*, ✗ *autonomous high-risk trading*, ✗ *misleading
> financial certainty*.
>
> Sebuah *wealth trajectory* lima tahun (§12.13) adalah persis bentuk yang
> paling mudah dibaca sebagai janji — apalagi kalau ditampilkan sebagai satu
> garis. Yang menyelamatkannya sudah ada di naskah ini (§12.14 asumsi wajib,
> §12.15 ketidakpastian wajib), tetapi hubungannya dengan C-4 perlu dinyatakan:
> **proyeksi finansial selalu berupa rentang dengan asumsi terlihat, tidak
> pernah satu angka.**

> ⚠️ **Simulasi kesehatan menyentuh C-2** dengan cara yang sama. `Sleep →
> Energy → Exercise → Recovery` masih di wilayah *tracking* dan *wellness
> suggestion* yang §8.23 izinkan — tapi begitu ia memproyeksikan kondisi
> kesehatan berbulan-bulan ke depan, ia mendekati garis *"berpura-pura menjadi
> dokter"*. Horizon proyeksi kesehatan sebaiknya lebih pendek daripada horizon
> proyeksi tujuan. Lihat **A-29** / [#86](../../issues/86).

> ⚠️ **Kelima rantai butuh data berbulan-bulan yang belum ada.** `Wealth
> trajectory` menuntut riwayat pengeluaran; `Career` menuntut riwayat pekerjaan;
> `Knowledge retention` menuntut pengukuran yang belum pernah ada di mana pun.
> Ini **B-21** ([#48](../../issues/48)) dan **B-1** (cold start) berlaku penuh —
> dan §12.20 memberi jalan keluarnya hanya **setelah** ada galat prediksi
> pertama yang bisa dipelajari. Lihat **B-27** / [#88](../../issues/88).
