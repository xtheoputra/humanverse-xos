# 251 — §18.14–§18.17 Federated Intelligence, HINP, Knowledge Federation & Agent Federation

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.14 — Federated Intelligence

> Ini sangat penting. **HumanVerse tidak harus mengumpulkan seluruh data ke satu
> server.**

```
HumanVerse A ──┐ privacy-preserving
               ├── Federated Intelligence ──┬── Organization
HumanVerse B ──┘                            └── City
```

> Yang dibagikan dapat berupa: `model updates · aggregated statistics ·
> anonymous signals · knowledge · patterns` — **bukan raw personal data.**

---

> ⭐⭐⭐ **Menolak pengumpulan terpusat sebagai keputusan ARSITEKTUR, bukan
> sebagai janji kebijakan, adalah pilihan yang paling menentukan di seluruh
> naskah ini.**
>
> Janji *"kami tidak akan menyalahgunakan data Anda"* bergantung pada niat
> pemiliknya sekarang dan selamanya. Arsitektur yang tidak pernah memindahkan
> datanya tidak bergantung pada siapa pun. Dan ia sejalan dengan
> `processing_location` §17.4 — satu-satunya field di repo ini yang menjadikan
> janji on-device **bisa diperiksa**. Untuk fase yang menghubungkan orang dengan
> organisasi dan kota, bawaan ini yang membuat sisanya bisa dipertahankan.

> 🛑 **Tetapi `model updates` BUKAN kategori yang aman, dan ia berdiri paling
> depan di daftar.**
>
> Pembaruan model membawa jejak data yang melatihnya; untuk model kecil dengan
> peserta sedikit, masukan aslinya dapat direkonstruksi dari pembaruan itu
> dengan derajat yang mengejutkan. Kalimat *"bukan raw personal data"* benar
> secara harfiah dan tidak cukup secara akibat — inilah bentuk paling murni dari
> prinsip §8.10 sendiri: **yang menentukan bukan bentuk datanya, melainkan apa
> yang bisa disimpulkan darinya.**
>
> ⚠️ `anonymous signals` menanggung masalah kedua: **anonim bukan sifat sebuah
> berkas, melainkan sifat berkas itu digabung dengan segala hal lain yang sudah
> diketahui.** Pola mobilitas kota (§18.13) adalah contoh bukunya.
>
> ⭐ Yang perlu ditambahkan sudah punya bentuk baku dan murah dinyatakan
> sekarang: **ambang jumlah peserta minimum** sebelum agregat apa pun boleh
> keluar, **batas anggaran privasi** untuk statistik yang dibagikan, dan
> **`model updates` diperlakukan seperti data, bukan seperti kode** — tunduk
> pada `classification` §18.15 yang sama. Lihat **B-36** / [#126](../../issues/126).

---

## §18.15 — Intelligence Federation Protocol (HINP)

> Kita membutuhkan protokol standar: **HINP — HumanVerse Intelligence Network
> Protocol.**

```json
{
  "message_id": "...",   "type": "INTELLIGENCE_EVENT",
  "sender": "...",       "classification": "PUBLIC",
  "receiver": "...",     "timestamp": "...",
  "payload": {},         "confidence": 0.92,
  "provenance": []
}
```

> Security:
>
> ```
> Identity → Authentication → Authorization → Policy
>    → Data Classification → Encryption → Audit
> ```

---

> ⭐⭐⭐⭐ **Tujuh gerbang, dan ini rantai keamanan TERLENGKAP di sembilan naskah
> terakhir — sekaligus pembalikan tren yang sudah tercatat empat kali.**
>
> Riwayat rantai yang menyusut: §14.20 kehilangan `Consent`, `Rate Limit`,
> `Confirmation` (**E-117**/[#93](../../issues/93)) · §15.22 tinggal lima
> tanpa `Risk` (**E-124**/[#106](../../issues/106)) · §16.18 tinggal lima tanpa
> `Risk`, `Confirmation`, maupun `Permission`, dan §16.13 tinggal tiga
> (**E-130**/[#111](../../issues/111)). Rantai ini **naik lagi** — dan yang
> penting bukan jumlahnya melainkan bahwa `Policy` berdiri **sebelum**
> `Data Classification` dan `Encryption`, yaitu urutan yang benar: kebijakan
> memutuskan boleh-tidaknya, klasifikasi menentukan perlakuannya, enkripsi
> melaksanakannya, `Audit` mencatat semuanya.

> ⭐⭐ **`confidence` dan `provenance` sebagai field TINGKAT PROTOKOL, bukan isi
> pesan.**
>
> Sekali keduanya berada di amplop, tidak ada simpul yang bisa meneruskan
> intelligence tanpa menyatakan seberapa yakin dan dari mana — dan penerima bisa
> menolak yang tak berasal **tanpa membuka payload-nya**. Itu menjadikan §18.21
> (Provenance) dan §18.23 (Information Integrity) bisa ditegakkan di tepi
> jaringan, bukan hanya di dalam mesin penalaran.

> 🛑 **Tetapi `classification: "PUBLIC"` menjadikan pilihan tangga sensitivitas
> sebagai bagian dari FORMAT KAWAT — dan tangga itu ada dua.**
>
> **E-133** ([#117](../../issues/117)) mencatat §17.4 memberi lima nama
> (`PUBLIC → … → HIGHLY-SENSITIVE`) sementara §8.16 memberi empat angka
> (`Level 1–4`), tanpa pemetaan. Selama itu cuma dokumen, biayanya kebingungan.
> Begitu ia menjadi field di pesan antar-organisasi, biayanya berubah: **dua
> pihak yang memakai tangga berbeda akan saling memberi izin yang tidak mereka
> maksud** — dan pihak yang menerima `SENSITIVE` dari tangga lima akan
> memperlakukannya sebagai tingkat 3 dari empat, padahal maksud pengirimnya
> tingkat 3 dari lima.
>
> ⇒ #117 berhenti menjadi kerapian dokumentasi dan menjadi **prasyarat
> protokol**. Perbaikannya tetap satu baris, dan sekaranglah waktunya.

> ⚠️ **`Consent` tidak ada di rantai tujuh gerbang itu, dan ini satu-satunya
> tempat di mana ketiadaannya benar-benar menggigit.**
>
> `Authorization` menjawab *"apakah pengirim berhak mengirim"*. `Consent`
> menjawab *"apakah ORANG yang datanya ada di dalam pernah mengizinkan ia
> keluar"* — dan §8.9/§8.17 sudah memisahkan keduanya dengan tegas (**H-15**:
> izin di muka bukan konfirmasi). Untuk pesan yang menyeberangi batas
> organisasi, pertanyaan kedua itulah yang menentukan. ⭐ Naskah ini punya
> bahannya: §18.28 memberi tabel `federation_consents`. Yang perlu dilakukan
> cuma menaruhnya di rantai, di antara `Authorization` dan `Policy`.

> ⚠️ `type: "INTELLIGENCE_EVENT"` adalah SCREAMING_SNAKE — bentuk **ketiga**
> untuk nama peristiwa di repo ini, setelah `domain.verb`
> ([`spec/03`](../spec/03-EVENT-CONTRACTS.md)) dan PascalCase (§18.5). Lihat
> **E-140**.

---

## §18.16 — Knowledge Federation

> Tidak semua intelligence harus berasal dari HumanVerse. Sumber:
> `HumanVerse ↕ Scientific Knowledge ↕ Public Data ↕ Organizations ↕ Agents ↕
> Devices`
>
> Tetapi setiap knowledge memiliki: `source · timestamp · confidence ·
> provenance · version · license · data classification`

---

> ⭐⭐⭐ **`license` sebagai field wajib pada setiap knowledge adalah yang PERTAMA
> di dua puluh dua naskah — dan ia menjawab separuh masalah terbesar §18.4.**
>
> §18.4 menarik `news`, `scientific publications`, `government data`, dan
> `internet knowledge` tanpa menyebut hak siapa pun. Bagian ini menyediakan
> tempat untuk menyimpan jawabannya. ⚠️ Yang belum: **lisensi belum menjadi
> gerbang.** Field yang dicatat sesudah data dipakai tidak mencegah apa pun; ia
> harus diperiksa di `INGESTION`, dan pemakaian yang tidak diizinkan lisensinya
> harus **gagal**, bukan tercatat. Itu selisih antara metadata dan penegakan —
> selisih yang sama dengan `processing_location` §17.4. Lihat **C-27** / [#122](../../issues/122).

> ⭐⭐ **`version` pada knowledge mengakui bahwa pengetahuan berubah, bukan
> bertambah.** Publikasi ilmiah ditarik kembali, angka ekonomi direvisi, data
> pemerintah diperbaiki. Sistem yang hanya menumpuk akan mempertahankan versi
> pertama selamanya karena ia yang lebih dulu masuk graf. Dengan `version` +
> `timestamp` + `provenance`, penarikan kembali bisa **merambat** — dan §18.23
> (Contradiction Detection) adalah yang akan memakainya.

> ⚠️ **Tujuh field ini hampir sama dengan delapan field §17.4, tetapi tidak
> sama — dan tidak ada yang menyatakan hubungannya.** Yang hilang di sini:
> `owner`, `purpose`, `retention`, `consent`, `processing_location`. Yang hanya
> ada di sini: `confidence`, `provenance`, `version`, `license`. Dua daftar
> metadata untuk dua kelas data yang **akan bertemu di satu graf**. Yang perlu
> dinyatakan: apakah ini satu skema dengan field opsional, atau dua skema dengan
> aturan penyeberangan.

---

## §18.17 — Agent Federation

> Ini merupakan evolusi Phase 14. Agent tidak hanya `Agent A ↔ Agent B` tetapi:
> `HumanVerse Agent ↕ External Agent ↕ Organization Agent ↕ City Agent ↕
> Service Agent`
>
> Namun tetap: `Agent Identity · Agent Capability · Agent Permission ·
> Agent Trust · Agent Reputation · Agent Risk · Agent Audit`

---

> ⭐⭐⭐ **`Agent Risk` kembali muncul — dan bersama §18.22 ini kali KEDUA dalam
> satu naskah, sesudah tujuh rantai berturut-turut kehilangannya.**
>
> §17.38 mengembalikannya pertama kali setelah §11.14. Naskah ini
> mempertahankannya, dan menaruhnya di tempat yang benar: **melekat pada agent,
> bukan pada satu rantai** — sehingga ia berlaku pada setiap pemanggilan, bukan
> hanya pada jalur yang kebetulan digambar.

> 🛑 **Tetapi `Agent Confirmation` tidak ada, dan justru di sinilah pertanyaan
> H-15 tidak punya jawaban.**
>
> **H-15** menetapkan: otomatis sampai R2, **konfirmasi manusia wajib mulai
> R3**. Untuk agent milik pengguna, "manusia" jelas siapa. Untuk `City Agent`
> yang bertindak lintas jaringan atas permintaan `Organization Agent` —
> **manusia yang mana?** Tidak ada satu orang pun yang berdiri di ujungnya.
>
> Ini bukan kekurangan yang bisa ditambal dengan satu field: ia menuntut
> keputusan tentang **aksi lintas-simpul mana yang boleh ada sama sekali**.
> ⭐ Bentuk paling murah yang konsisten dengan prinsip pembuka naskah ini:
> **federasi agent boleh bertukar INTELLIGENCE, tidak boleh memicu AKSI di
> simpul lain** — persis pembedaan *memahami* lawan *mengendalikan* yang
> §18 pembuka nyatakan, dinaikkan menjadi aturan protokol. Lihat **E-143** / [#125](../../issues/125).

> ⚠️ **`Agent Trust` dan `Agent Reputation` didaftar sebagai dua hal, dan
> §18.20 memperlakukannya sebagai dua hal juga — tetapi tidak ada tempat yang
> menyatakan bedanya.** §18.28 memberi `agent_trust_scores` **dan**
> `agent_reputation` sebagai dua tabel. Dua tabel untuk pembedaan yang belum
> ditulis akan diisi dengan hal yang sama.
