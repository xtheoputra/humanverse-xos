# 250 — §18.12–§18.13 Organization Intelligence & City Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.12 — Organization Intelligence

> HumanVerse dapat menyediakan framework untuk organisasi.

```
Organization
├── People      ├── Goals       ├── Risks
├── Projects    ├── Processes   ├── Infrastructure
├── Resources   ├── Knowledge   └── Agents
```

> Kemudian **Organization Intelligence** dapat menganalisis:
>
> `productivity · resource allocation · organizational risks · knowledge gaps ·
> workflow bottlenecks · project dependencies · operational changes ·
> strategic scenarios`

---

> ⭐⭐ **Tujuh dari delapan analisis itu menyasar SISTEM, bukan orang — dan itu
> pilihan yang sebagian besar sudah benar.**
>
> `workflow bottlenecks`, `project dependencies`, `resource allocation`,
> `knowledge gaps` semuanya menjawab pertanyaan tentang **bagaimana pekerjaan
> mengalir**, bukan tentang siapa yang lambat. Itu perbedaan yang menentukan:
> hambatan yang ditemukan pada proses menghasilkan perbaikan proses; hambatan
> yang ditemukan pada orang menghasilkan penilaian orang. Naskah ini
> mayoritasnya memilih yang pertama.

> 🛑🛑🛑 **Tetapi `productivity` berdiri paling depan, dan `People` adalah
> komponen pertama organisasinya — dan §8.10 melarang `employment scoring`
> dengan kata-kata itu sendiri.**
>
> §8.10 menyebut tiga tujuan terlarang secara harfiah:
>
> ```
> advertising
> insurance scoring
> employment scoring
> ```
>
> dengan prinsip penutupnya: ***"Data boleh digunakan untuk tujuan yang
> diizinkan, bukan semua tujuan yang secara teknis memungkinkan."***
>
> [`211`](211-MARKET-TEAM-ORGANISASI-TENANT.md) sudah menarik batasnya satu
> naskah lalu: larangan itu menutup **menilai**, ia tidak menutup **melihat**.
> `productivity` sebagai analisis yang ditawarkan kepada organisasi atas
> komponen bernama `People` berada persis di sisi yang ditutup — dan kali ini
> ia datang bukan sebagai risiko yang saya bayangkan, melainkan sebagai
> **fitur yang ditawarkan**.
>
> ⚠️ Yang membuatnya lebih berat dari **C-12** ([#46](../../issues/46)):
> di Phase 14 pertanyaannya adalah apa yang boleh **dibaca** HR Agent. Di sini
> Phase 17 sudah menambahkan `recovery_score`, `training_load`, `stress`, dan
> `sleep` ke dalam sistem yang sama — sehingga *"produktivitas"* yang dihitung
> organisasi bisa, tanpa satu baris kode yang berniat jahat, **berisi data
> kesehatan**. Itu persis pasangan yang §8.10 larang.
>
> ⭐ Perbaikannya tidak menuntut membuang fiturnya, dan bentuknya sudah dipakai
> di repo ini: **`productivity` adalah properti PROSES, bukan properti orang** —
> dihitung pada `Projects`/`Processes`, tidak pernah dipecah per individu; dan
> **data yang lahir di Personal Data Vault tidak pernah menyeberang ke
> Organization Intelligence**, apa pun izin yang diberikan majikan. Lihat
> **C-27** / [#122](../../issues/122).

> 🛑 **Dan seluruh model persetujuan dua puluh dua naskah terbalik di bagian
> ini, tanpa disebut.**
>
> Di semua fase sebelumnya, **yang membayar dan yang datanya dipakai adalah
> orang yang sama** — itu yang membuat `consent` (§8.9), `purpose` (§8.10), dan
> Privacy Center (**H-4**) masuk akal sebagai perlindungan. Organization
> Intelligence memperkenalkan pihak ketiga: **organisasi adalah pelanggan,
> karyawan adalah subjek datanya.** Persetujuan yang diberikan kepada majikan
> bukan persetujuan dalam arti yang sama — **C-3** ([#21](../../issues/21))
> sudah mencatat bahwa izin yang diminta ketika fiturnya membutuhkan akan selalu
> diberikan, dan ketimpangan kekuasaan di tempat kerja menjadikannya lebih
> tajam lagi.
>
> Yang perlu diputuskan sebelum kode: **apakah Organization Intelligence berdiri
> di atas data organisasi saja (proyek, proses, sumber daya, pengetahuan) — dan
> tidak pernah menyentuh Personal Data Vault siapa pun.** Kalau ya, seluruh
> masalah ini hilang, dan tujuh dari delapan analisis tetap bisa dikerjakan.

> ⚠️ **`Agents` sebagai komponen organisasi juga membuka pertanyaan yang belum
> punya jawaban: agent milik organisasi bertindak atas nama siapa.** §14.18
> memberi multi-tenant, `Executive Agent` memberi agent yang bertindak atas nama
> pimpinan. Ditambah §18.17 (Agent Federation) yang membuka agent organisasi ke
> jaringan, rantai kewenangannya menjadi tiga tingkat tanpa `Confirmation` di
> mana pun (**H-15**: R3 ke atas wajib konfirmasi manusia — manusia yang mana?).

---

## §18.13 — City Intelligence

> Ini menarik karena terhubung dengan **SpatialOS + AetherScan**.

```
City
├── Buildings   ├── Energy   ├── Weather      ├── Infrastructure
├── Roads       ├── Water    ├── Population   └── IoT
├── Transportation │ Air     ├── Events
```

> **City Intelligence** dapat memahami: `congestion · mobility · energy demand ·
> infrastructure · environmental conditions · public events · spatial risks ·
> urban patterns`

> **AetherScan** nantinya dapat menjadi salah satu **spatial sensing provider**,
> bukan bagian inti HumanVerse.

---

> ⭐⭐⭐⭐ **Satu kalimat tentang AetherScan menutup pertanyaan yang terbuka
> sejak naskah 19 — dan menutupnya dengan menurunkan pangkatnya sendiri.**
>
> Naskah 19 memperkenalkan AetherScan sebagai bagian dari fondasi penginderaan
> Phase 15 dan menjadwalkan `AetherScan Integration` sebagai milestone
> tersendiri, sehingga tidak jelas apakah ia komponen inti atau produk
> terpisah. Di sini pemilik menyatakannya: **penyedia, bukan inti.**
>
> Nilainya bukan cuma kejelasan. Sebuah lapisan penginderaan yang dinyatakan
> sebagai **salah satu** penyedia memaksa antarmukanya menjadi umum sejak awal
> — dan itulah yang membuat prinsip §16.1 (*"robot adalah hardware, HumanVerse
> adalah intelligence layer"*) berlaku juga untuk sensor kota. Ini pola yang
> sama dengan `drivers/` di **E-129**: batas yang bisa ditegakkan, bukan
> diniatkan.
>
> ⭐ Dan ini **keputusan pemilik yang mengurangi cakupan** — jenis yang paling
> jarang muncul dalam dua puluh dua naskah, dan paling berharga di repo yang
> setiap naskahnya menambah satu fase.

> 🛑 **Tetapi `Population` berdiri sederet dengan `Water` dan `Air`.**
>
> Tujuh komponen kota lainnya adalah infrastruktur dan lingkungan; yang satu ini
> adalah orang. Dan dua dari delapan analisisnya — `mobility` dan
> `urban patterns` — **hanya bisa dihitung dari pergerakan orang**.
>
> Data mobilitas kota adalah salah satu kelas data yang paling terkenal sulit
> dianonimkan: pola perjalanan berulang menunjuk ke tempat tinggal dan tempat
> kerja, dan pasangan itu sudah cukup mengidentifikasi sebagian besar orang.
> §18.14 menjanjikan yang dibagikan adalah *aggregated statistics* dan
> *anonymous signals* — tetapi **tidak ada ambang jumlah minimum**, dan
> agregat kecil bukan agregat. Lihat **B-36** / [#126](../../issues/126).
>
> ⚠️ Ditambah: penduduk sebuah kota **tidak pernah menyetujui apa pun**. Seluruh
> mesin persetujuan repo ini (§8.9 · §8.10 · §17.4 `consent`) mengandaikan ada
> orang yang menekan tombol. Untuk `City Intelligence` orang itu tidak ada, dan
> yang menggantikannya bukan persetujuan melainkan **dasar hukum yang
> berbeda** — hal yang belum disebut satu kali pun.

> ⭐ **`spatial risks` sebagai salah satu analisis adalah tautan yang benar ke
> §18.24**, dan ia satu-satunya di daftar ini yang keluarannya berupa
> peringatan. Itu menjadikannya kandidat pertama yang harus melewati §18.25 —
> dan lihat **C-28** / [#123](../../issues/123) untuk siapa yang boleh menerimanya.
