# 252 — §18.18–§18.21 Collective Intelligence, Marketplace, Trust & Reputation, Provenance

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.18 — Collective Intelligence

> Bukan satu AI yang mengetahui semuanya. Tetapi:
>
> ```
> Many specialized intelligences → Federation → Shared Context → Collective Reasoning
> ```

> Contoh: `Climate Agent + Energy Agent + Economy Agent + Transportation Agent +
> City Agent + Human Agent → Global Scenario`

---

> ⭐⭐⭐ **Menolak "satu AI yang mengetahui semuanya" secara eksplisit adalah
> pilihan arsitektur, bukan kerendahan hati.**
>
> Model tunggal yang menjawab tentang iklim, ekonomi, dan transportasi sekaligus
> tidak punya cara menyatakan **di mana ia lemah**. Beberapa mesin terspesialisasi
> yang harus saling menyampaikan kesimpulan memaksa setiap klaim melewati batas
> — dan batas itulah tempat `confidence`, `provenance`, dan `license` (§18.15,
> §18.16) bisa diperiksa. Kebenaran teknisnya: **spesialisasi menciptakan
> tempat pemeriksaan yang tidak ada di dalam satu model.**

> 🛑🛑 **Tetapi `consensus` (§18.32 G18.8) menarik ke arah yang BERLAWANAN
> dengan `UNRESOLVED` (§18.23), dan tidak ada yang menyatakan mana yang
> menang.**
>
> §18.23 memberi keluaran yang jarang sekali diizinkan sebuah sistem:
>
> ```
> Conflict detected. Current confidence: 0.61. Status: UNRESOLVED
> ```
>
> G18.8 memberi `consensus` sebagai milestone. Kedua mesin ini memakan masukan
> yang sama — beberapa sumber yang tidak sepakat — dan menghasilkan hal yang
> berlawanan: yang satu **mempertahankan** ketidaksepakatan, yang lain
> **menghapusnya**.
>
> Bahayanya bukan teoretis. Kalau `Climate Agent` dan `Economy Agent` tidak
> sepakat, ketidaksepakatan itu **adalah informasinya** — dan konsensus yang
> merata-ratakannya menghasilkan satu angka yang tidak dipercayai kedua mesin
> mana pun, disajikan dengan keyakinan yang tidak dimiliki keduanya.
>
> ⭐ Aturan yang menyelesaikannya sudah tersirat di §18.23 dan tinggal
> dinyatakan: **konsensus hanya boleh menyatukan hal yang sumbernya sepakat;
> ketidaksepakatan naik ke pengguna sebagai ketidaksepakatan.** `debate` dan
> `synthesis` (G18.8) adalah bentuk yang benar untuk itu; `consensus`
> satu-satunya yang berbahaya di antara ketiganya. Lihat **G-17** / [#121](../../issues/121).

> ⚠️ **`Human Agent` berdiri sederet dengan `Climate Agent` di daftar peserta.**
> Kalau ia berarti *agent milik manusia*, ia mewakili satu orang di antara lima
> mesin yang mewakili sistem — dan suaranya akan selalu kalah dalam skema
> penyatuan mana pun. Kalau ia berarti *model tentang manusia*, maka orang
> sungguhan tidak punya wakil sama sekali di `Global Scenario`.

---

## §18.19 — Intelligence Marketplace

```
Developer → Agent SDK → HumanVerse Registry → Security Verification
   → Evaluation → Certification → Marketplace
```

> Ini melanjutkan Developer Platform Phase 6 + Agent Marketplace Phase 14.

---

> ⭐⭐⭐ **`Security Verification → Evaluation → Certification` BERDIRI SEBELUM
> `Marketplace` — pemeriksaan sebagai pintu masuk, bukan sebagai tindakan
> sesudah ada keluhan.**
>
> Urutan ini menutup jalur yang menghancurkan hampir semua toko ekstensi:
> terbit dulu, diperiksa kalau ada yang melapor. Dan `Evaluation` sebagai
> langkah terpisah dari `Security Verification` mengakui dua pertanyaan yang
> berbeda — *"apakah ini berbahaya"* dan *"apakah ini bekerja"*. §17.36 sudah
> memberi bentuk untuk yang kedua (sepuluh metrik, *"accuracy saja tidak
> cukup"*).

> ⭐ **Dan naskah ini menyebut sendiri bahwa ia melanjutkan Phase 6 dan Phase
> 14** — pengakuan yang mencegah butir **A-15**/**C-7** terpecah menjadi tiga
> pasar. ⚠️ Tapi pengakuan bukan penggabungan: `HumanVerse Registry` di sini
> lawan Agent Marketplace §14, dan **belum ada satu kalimat pun yang menyatakan
> keduanya satu benda**. Riwayat repo ini menunjukkan dua nama yang tidak
> dinyatakan sama akan menjadi dua sistem (**E-136** · **E-141**).

> 🛑 **Tidak ada langkah PENCABUTAN, dan tanpa itu sertifikasi menjadi permanen
> pada barang yang berubah.**
>
> Agent yang lolos hari ini akan diperbarui besok; model di belakangnya akan
> bergeser (§17.36 `drift` sudah mengakui ini). §18.20 memberi skor kepercayaan
> yang bisa turun — tetapi **tidak ada anak panah dari skor yang turun kembali
> ke `Certification`**. Yang perlu ada: **sertifikat punya masa berlaku dan
> versi**, dan **turunnya trust di bawah ambang menarik agent dari marketplace
> secara otomatis** — bukan menunggu keputusan manusia yang tidak akan sempat.

> 🛑 **Dan lapisan bisnisnya masih hilang — naskah keempat berturut-turut.**
> **E-86**/**A-27** mencatat peta 15 fase §10.41 membuang seluruh blok
> *Subscription* dan *Revenue Platform* tanpa rumah baru. Sebuah *marketplace*
> disebut untuk ketiga kalinya tanpa satu kata tentang harga, bagi hasil,
> penagihan, atau pengembalian dana. Sertifikasi tanpa model komersial akan
> ditentukan oleh apa pun yang paling mudah dibangun ketika uang akhirnya jadi
> pertanyaan.

---

## §18.20 — Trust & Reputation System

> Karena sekarang banyak agent berkomunikasi, kita membutuhkan **Agent Trust
> Score.** Misalnya: `Accuracy 94 % · Reliability 97 % · Safety 99 % ·
> Latency 91 % · Provenance 98 % · User Rating 4.8`
>
> **Tetapi jangan menggunakan satu angka saja.** Lebih baik:
>
> ```
> Trust Vector
> T = { accuracy, reliability, safety, provenance, consistency, domain_expertise }
> ```

---

> ⭐⭐⭐⭐ **Menolak skor tunggal, di bagian yang baru saja menggambar skor
> tunggal — pemilik membantah contohnya sendiri dalam paragraf yang sama, dan
> itu benar.**
>
> Satu angka kepercayaan memaksa pertukaran yang tidak masuk akal: agent yang
> **cepat tetapi tidak aman** bisa menyamai skor agent yang **lambat tetapi
> aman**, dan begitu keduanya jadi satu angka, tidak ada cara memilih di
> antaranya. Vektor mempertahankan pertanyaan *"aman dalam hal apa"*.
>
> ⭐⭐ Dan `safety` sebagai dimensi tersendiri berarti ia **tidak bisa
> dikompensasi**: agent yang sangat akurat tidak boleh menutupi agent yang
> tidak aman. Itu bentuk yang sama dengan §17.36 (*"accuracy saja tidak
> cukup"*), dan dua naskah berturut-turut menolak metrik tunggal adalah pola
> yang layak dicatat sebagai kebiasaan, bukan kebetulan.

> ⚠️ **Tetapi enam nama di contoh tidak sama dengan enam nama di vektor.**
>
> | Hanya di contoh | Hanya di vektor |
> |---|---|
> | `latency` · `user_rating` | `consistency` · `domain_expertise` |
>
> Dua dimensi lahir dan dua hilang dalam sepuluh baris. `user_rating`
> khususnya bukan hal sepele untuk dibuang diam-diam: ia satu-satunya masukan
> yang datang dari manusia, dan satu-satunya yang bisa **dimanipulasi** — dua
> alasan yang berlawanan untuk memasukkannya, dan keduanya perlu diputuskan
> sadar. Ini gejala **H-9** yang berulang tiap naskah panjang: daftar yang
> bergeser di antara dua penyebutan berdekatan.

> ⚠️ **Dan tidak ada yang menyatakan SIAPA yang mengukur.** Kalau agent
> melaporkan sendiri, seluruh sistem bergantung pada kejujuran pihak yang
> paling diuntungkan dengan berbohong. §18.23 punya mesin untuk ini
> (`Cross Source Validation`) tetapi tidak diarahkan ke sini.

---

## §18.21 — Intelligence Provenance

> Setiap intelligence harus dapat ditelusuri.
>
> ```
> Insight → Evidence → Source → Transformation → Model → Agent → Policy
> ```

> *"Ada peningkatan risiko supply-chain."* HumanVerse harus bisa menunjukkan
> **Why?** — `Source A/B/C` · observed events `X/Y/Z` · Model
> `SupplyChainModel v4.2` · Confidence `0.81`

---

> ⭐⭐⭐⭐ **Tujuh mata rantai, dan `Transformation` ada di antara `Source` dan
> `Model` — itu mata rantai yang hampir selalu hilang, dan yang paling sering
> menjadi tempat kesalahan.**
>
> Kebanyakan sistem yang mengklaim provenance menunjuk sumbernya lalu berhenti.
> Tetapi antara dokumen mentah dan masukan model ada normalisasi, ekstraksi
> entitas, penggabungan, dan pembulatan (§18.4 punya delapan langkah di
> antaranya) — dan kesalahan yang lahir di situ **tidak terlihat pada sumbernya
> maupun pada modelnya**. Menamainya sebagai mata rantai berarti ia harus
> dicatat.
>
> ⭐ Dan `Policy` di ujung menjawab pertanyaan yang berbeda dari enam
> sebelumnya: bukan *"dari mana ini"* melainkan **"atas dasar aturan apa ini
> boleh sampai ke saya"**. Belum pernah ada di rantai provenance mana pun di
> repo ini.

> ⭐⭐ **`SupplyChainModel v4.2` — versi model muncul di dalam jawaban `Why?`,
> bukan di catatan teknis.** Itu tepat yang **B-34** ([#119](../../issues/119))
> tuntut untuk fitur turunan model, dan §17.35 sudah mewajibkan `version`.
> Kesimpulan yang tidak menyebut versi model tidak bisa ditinjau ulang ketika
> modelnya diperbaiki.

> 🛑 **Tetapi §18.28 tidak punya tabel registri model — dan itu kemunduran dari
> naskah 21.**
>
> §17.35 memberi `health_models` sebagai registri dengan `version` dan
> `approval`; §17.36 memberi metrik yang berlaku padanya. Naskah ini menyebut
> `SupplyChainModel v4.2` dalam prosa, tetapi tiga puluh tabel §18.28 **tidak
> memuat satu pun** tempat model dunia didaftarkan, diberi versi, atau
> disetujui. Akibatnya: `Model` di rantai provenance menunjuk ke sesuatu yang
> tidak punya baris di basis data, dan sepuluh metrik §17.36 tidak punya subjek
> di Phase 18.
>
> ⭐ Perbaikannya sudah jadi, tinggal disalin: **`world_models` dengan bentuk
> yang sama seperti `health_models`.** Lihat **E-141** / [#130](../../issues/130).
