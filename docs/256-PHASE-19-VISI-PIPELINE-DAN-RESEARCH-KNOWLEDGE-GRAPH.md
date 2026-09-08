# 256 — Visi, §19.1–§19.3 Posisi, Scientific Cognitive Pipeline & Research Knowledge Graph

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pembuka — dan perubahan peta fase

> Sekarang kita masuk ke fase paling ambisius sebelum puncak HumanVerse. Saya
> akan mengubah sedikit fokus agar arsitektur tetap konsisten dengan **roadmap
> 20 fase yang sudah kita tetapkan sebelumnya**.
>
> - **Phase 18: Global Intelligence Network** → memahami dunia yang sedang berjalan.
> - **Phase 19: Scientific Discovery Engine** → membantu manusia menemukan
>   pengetahuan baru melalui AI yang bekerja seperti tim peneliti.
> - **Phase 20: Civilization Platform** → infrastruktur AI-native untuk masyarakat.
>
> Alasan perubahan ini adalah agar Phase 19 tidak terlalu tumpang tindih dengan
> Phase 18.

---

> ⭐⭐⭐⭐ **Ini PERTAMA KALINYA dalam lima naskah sebuah perubahan peta fase
> DIUMUMKAN dengan alasannya — dan itu persis yang [#101](../../issues/101) dan
> [#108](../../issues/108) minta.**
>
> Bandingkan bagaimana peta berubah sebelumnya: §10.41 menamai **Phase 15 =
> Global Intelligence Platform**; naskah 19 memakai nomor itu untuk SpatialOS
> **tanpa menyebut ke mana yang lama pergi** (**E-123**, dan **H-20** patah
> karenanya). Naskah 20, 21, dan 22 masing-masing menambah satu fase **di
> kalimat penutup**, tanpa satu pun menyatakan peta lama diganti.
>
> Di sini pemilik: **(a)** menyatakan bahwa ia mengubah sesuatu, **(b)** memberi
> alasannya (*tumpang tindih dengan Phase 18*), **(c)** menunjukkan susunan
> barunya, dan **(d)** menyebut Phase 20 sebagai **fase terakhir**. Empat hal
> yang tak satu pun ada di empat perubahan sebelumnya.
>
> ⭐⭐ Dan alasannya benar secara teknis: *"tidak terlalu tumpang tindih"*.
> Phase 18 §18.4 sudah menelan `scientific publications`, dan §18.16 sudah
> memberi `Scientific Knowledge` sebagai sumber federasi. Sebuah fase yang cuma
> menambah lebih banyak pembacaan literatur memang akan menjadi Phase 18 dengan
> nama lain. Memindahkannya ke **memproduksi** pengetahuan adalah pembedaan yang
> nyata, bukan kosmetik.

> 🛑🛑🛑 **Tetapi "roadmap 20 fase yang sudah kita tetapkan sebelumnya" TIDAK
> PERNAH ADA. Nol dokumen menyebutnya, dan "Phase 20" belum pernah muncul satu
> kali pun sebelum kalimat ini.**
>
> Yang benar-benar pernah ditetapkan:
>
> | | Isi | Sumber |
> |---|---|---|
> | **v1** | **lima belas** fase, berhenti di *Global Intelligence Platform* | §10.41 (naskah 14) — satu-satunya peta kanonik yang pernah ditulis |
> | **v2** | **terbuka-ujung** — naskah 19→P16, 20→P17, 21→P18, 22→P19 | empat kalimat penutup, tanpa satu pun menyebut §10.41 |
> | **20 fase** | — | **tidak ada** |
>
> Pemeriksaannya sederhana dan sudah dijalankan: `grep -rioE "dua puluh
> fase|20 fase|phase 20"` atas seluruh `docs/`, `spec/`, dan `README.md`
> mengembalikan **nol**. Nomor fase tertinggi yang pernah disebut adalah
> **Phase 19**, dan naskah 22 memberinya isi yang **berbeda**:
> *HumanVerse Civilization Intelligence*.
>
> ⇒ Naskah ini melakukan tiga hal sekaligus: **mengganti isi Phase 19**
> (Civilization → Scientific Discovery), **memindahkan Civilization ke Phase
> 20**, dan **menyandarkan keduanya pada peta yang belum pernah ditulis**.
>
> Ini bukan tuduhan bahwa pemiliknya keliru mengingat — ini **akibat yang
> **E-128** ([#108](../../issues/108)) ramalkan**: peta yang terbuka-ujung dan
> tak pernah diberi versi akan melahirkan rujukan balik ke rencana yang tidak
> punya berkas. Ketika tidak ada dokumen yang bisa dibuka untuk memeriksa
> *"apa yang sudah kita tetapkan"*, yang tersisa cuma ingatan — dan ingatan
> tidak bisa di-`grep`.
>
> ⭐ **Kabar baiknya besar: naskah ini juga membawa obatnya.** *"Phase 20 …
> fase terakhir"* adalah **pertama kalinya sebuah ujung dinyatakan** sejak
> §10.41. Kalau pemilik menegaskannya, pertanyaan ketiga #101 (*berapa fase
> lagi*) tertutup, dan peta bisa diberi versi: **`v3` = dua puluh fase,
> tertutup**. Yang perlu dilakukan cuma **menuliskannya sebagai daftar**, sekali
> saja, di satu berkas. Lihat **E-144** / [#132](../../issues/132) dan **A-34** / [#133](../../issues/133).

---

## Visi — Scientific Discovery Engine

> *"From consuming knowledge to creating knowledge."*
>
> SDE adalah lapisan AI yang membantu proses penelitian dari awal hingga akhir:
> membaca jutaan paper · membangun Knowledge Graph ilmiah · menemukan hubungan
> tersembunyi · menghasilkan hipotesis · merancang eksperimen · menjalankan
> simulasi · mengevaluasi hasil · membantu menulis laporan ilmiah.
>
> **Targetnya bukan menggantikan ilmuwan, tetapi menjadi AI Research Partner
> yang mempercepat penelitian.**

---

> ⭐⭐⭐ **Pengaman pemilik yang KESEMBILAN, dan KETIGA berturut-turut yang
> diletakkan sebelum satu bagian pun ditulis.**
>
> *"Bukan menggantikan ilmuwan"* menyusul *"tidak mengontrol dunia"* (naskah 22)
> dan *"bukan AI dokter yang serba tahu"* (naskah 21). Tiga naskah berturut-turut
> membuka dengan batas, bukan dengan kemampuan — dan batas yang datang lebih
> dulu **membentuk** rancangannya alih-alih melawan rancangan yang sudah jadi.
>
> ⭐ Kata **"partner"** juga dipilih dengan tepat untuk domain ini: yang menahan
> penelitian bukan kekurangan jawaban melainkan **waktu untuk memeriksa**, dan
> mitra yang mempercepat pemeriksaan berbeda secara jenis dari mesin yang
> memberi kesimpulan.

> ⚠️ **Tapi berbeda dari dua pendahulunya, batas ini belum punya bentuk yang
> bisa diperiksa di dalam naskahnya sendiri.** *"Bukan AI dokter"* diterjemahkan
> naskah 21 menjadi larangan pada KELUARAN (§17.7 *"State ≠ diagnosis"*, dengan
> kalimat penggantinya diberikan). *"Bukan menggantikan ilmuwan"* belum: tidak
> ada daftar keluaran yang dilarang, dan §19.20 justru menghasilkan naskah
> ilmiah lengkap sementara §19.21 menghasilkan tinjauan sejawat.
>
> ⭐ Bahannya ada satu bagian kemudian: **§19.20 melarang mengarang referensi**
> — itu larangan pada keluaran, dan bentuk yang benar. Yang perlu menyusul:
> **apa lagi yang tidak boleh dihasilkan sistem ini tanpa manusia di ujungnya.**

---

## §19.1 — Posisi dalam Arsitektur HumanVerse

*(Bagian ini tidak berisi apa-apa di naskahnya.)*

---

> 🛑 **Bagian KOSONG untuk ketiga kalinya — dan ketiganya jenis yang SAMA:
> bagian yang menempatkan fase baru di dalam arsitektur yang sudah ada.**
>
> | Naskah | Bagian | Butir |
> |---|---|---|
> | 19 | §15.1 *"Arsitektur Besar SpatialOS"* | **G-15** ([#103](../../issues/103)) |
> | 20 | §16.33 *"Integrasi dengan HumanVerse"* | **G-16** ([#113](../../issues/113)) |
> | **23** | **§19.1 *"Posisi dalam Arsitektur HumanVerse"*** | **G-18** / [#137](../../issues/137) |
>
> Naskah 21 dan 22 memutus polanya — §17.2 memberi arsitektur pembuka lengkap
> dan §17.47–§17.50 mengisi keempat bagian integrasi. Naskah ini
> mengembalikannya, dan justru di fase yang **paling banyak bertumpang tindih
> dengan fase lain**: `simulations/` sudah ada di empat pohon, `models/` di
> tiga, `statistics/` menyentuh §18.7, dan §19.28 memberi `Health Lab`,
> `Robot Lab`, serta `Climate Lab` yang menduplikasi Phase 17, Phase 16, dan
> §18.18.
>
> ⇒ **Bagian yang kosong ini justru bagian yang paling dibutuhkan naskah ini.**
> Ia ditandai, tidak ditambal — sesuai kebiasaan repo ini.

> ⚠️ **Tiga belas angka lepas** juga tersebar di naskah (`6` sembilan kali, `5`
> empat kali), menempel di judul bagian dan di akhir paragraf. **H-9** sudah
> mencatat gejala ini berulang tiap naskah panjang (naskah 4 dan 7); ini
> jumlah terbanyak sejauh ini. Artefak salin-tempel, tidak mengubah isi — tetapi
> dicatat karena H-9 menyuruh selalu memeriksanya.

---

## §19.2 — Scientific Cognitive Pipeline

```
Question → Literature Retrieval → Evidence Extraction → Knowledge Graph
   → Gap Detection → Hypothesis Generation → Experiment Planning
   → Simulation → Evaluation → Scientific Report
```

> Ini menjadi **"otak ilmiah" HumanVerse**.

---

> ⭐⭐⭐ **`Gap Detection` berdiri SEBELUM `Hypothesis Generation`, dan urutan itu
> yang membedakan mesin ini dari mesin yang mengarang.**
>
> Hipotesis yang lahir dari pola dalam data akan selalu bisa dibuat — model
> bahasa mana pun bisa menghasilkan seribu. Hipotesis yang lahir dari **celah
> yang teridentifikasi** membawa alasan keberadaannya sendiri: ia menjawab
> pertanyaan *"mengapa ini belum diketahui"* sebelum menjawab *"apa
> jawabannya"*. Menaruh `Gap Detection` di hulu berarti novelty diperiksa
> **sebelum** hipotesis dibuat, bukan dinilai sesudahnya.
>
> ⭐ Dan `Evidence Extraction` berdiri sebelum `Knowledge Graph` — bukti masuk
> graf sebagai bukti, bukan sebagai fakta. Itu prasyarat §19.6 dan §19.7.

> 🛑 **Tetapi sepuluh langkah ini berakhir di `Scientific Report` tanpa satu pun
> gerbang — dan naskah ini punya DUA gerbang yang seharusnya berdiri di
> dalamnya.**
>
> §19.22 (Ethics Review) dan §19.23 (Scientific Safety Layer) tidak muncul di
> pipeline utama. Begitu juga §19.21 (Peer Review Assistant) dan §19.19
> (Reproducibility Engine), padahal keempatnya ada di naskah yang sama.
>
> Ini **persis bentuk E-143** ([#125](../../issues/125)) yang tercatat satu
> naskah lalu: §18.30 Query Engine melewati §18.22 Safety Kernel yang berdiri
> dua belas bagian sebelumnya. Kesimpulannya juga sama, dan tetap
> menguntungkan: **gerbangnya ADA, ia hanya tidak dipasang di jalurnya** —
> masalah perkabelan, bukan rancangan.
>
> ⚠️ Di sini ada satu yang lebih berat: **`Experiment Planning` menghasilkan
> protokol yang §19.15 kirimkan ke laboratorium fisik.** Untuk langkah yang
> berujung pada mesin yang menangani zat, ketiadaan `Ethics Review` di jalur
> adalah hal yang berbeda kelas dari ketiadaan gerbang pada jawaban teks.
> Lihat **C-29** / [#131](../../issues/131).

---

## §19.3 — Research Knowledge Graph

> **Berbeda dengan World Knowledge Graph.**

Node: `Paper · Author · Institution · Dataset · Method · Experiment · Material ·
Disease · Gene · Molecule · Algorithm · Result · Claim`

```
Paper ── cites · supports · contradicts · extends · uses_dataset · introduces_method
```

> Ini memungkinkan **reasoning lintas disiplin**.

---

> ⭐⭐⭐⭐ **Empat kata *"Berbeda dengan World Knowledge Graph"* adalah pertama
> kalinya sebuah naskah MENDAHULUI tabrakan penamaan alih-alih menciptakannya.**
>
> Riwayat repo ini panjang dan seragam: *"HumanOS"* dengan tiga arti
> (**E-114**), `Risk Engine` di tiga tempat (**E-141**/[#130](../../issues/130)),
> `World Model` lawan `Global Twin` di satu bagian, empat makna *"sandbox"*
> (**E-105**), tiga arti *"KILL"* (**E-120**). Semuanya lahir karena dua benda
> diberi satu nama tanpa ada yang menyatakan hubungannya.
>
> Di sini pemilik menyatakannya **di kalimat pertama**, sebelum satu node pun
> didaftar. Itu kebiasaan yang layak dicatat dan dipertahankan.

> ⭐⭐ **`Claim` sebagai node tersendiri, terpisah dari `Result` dan `Paper`,
> adalah keputusan pemodelan yang membuat §19.7 mungkin.**
>
> Sebuah paper bisa memuat banyak klaim; dua paper bisa bertentangan pada satu
> klaim sambil sepakat pada yang lain. Graf yang hanya punya simpul `Paper`
> memaksa pertentangan dinyatakan di tingkat dokumen — terlalu kasar untuk
> berguna. §18.28 sudah memberi bentuk yang sama (`knowledge_claims` terpisah
> dari `knowledge_evidence`), jadi dua naskah berturut-turut memodelkan klaim
> sebagai benda tersendiri. **Konsistensi yang jarang di repo ini.**

> ⭐ **`supports` dan `contradicts` sebagai relasi setara** juga tepat: sitasi
> yang membantah dan sitasi yang mendukung dihitung sama oleh hampir semua
> metrik yang ada di dunia nyata, dan itu sumber kekeliruan yang terkenal.
> §19.6 (`citation context`) menyebutnya secara eksplisit.

> ⚠️ **Tetapi enam relasi itu tidak membawa tingkat bukti, sementara naskah ini
> punya dua tangga yang berlaku padanya.** `supports` dan `contradicts` adalah
> klaim tentang hubungan antar-klaim — persis jenis tepi yang **E-138**
> ([#124](../../issues/124)) catat sebagai telanjang di §18.6, dan yang tangga
> kausal §18.9/§17.9 seharusnya beri tingkat. §19.6 menghasilkan
> `strength`/`confidence` per bukti; yang belum dinyatakan adalah bahwa
> **angka itu melekat pada TEPI grafnya**, bukan berdiri di tabel sebelah.

> ⚠️ **`Disease` · `Gene` · `Molecule` menempatkan graf ini di wilayah yang
> Phase 17 tangani dengan sangat hati-hati.** Naskah 21 membangun Health Vault,
> `processing_location`, dan tangga sensitivitas tersendiri untuk data
> kesehatan. Simpul-simpul ini berasal dari literatur, bukan dari pengguna —
> jadi sensitivitasnya berbeda. Yang perlu ditulis: **graf riset tidak pernah
> memuat simpul pasien**, dan penautan ke orang terjadi di sisi pribadi, tempat
> §17.4 berlaku. Bentuknya sama dengan usul untuk `Company ── employs → Human`
> di §18.6.
