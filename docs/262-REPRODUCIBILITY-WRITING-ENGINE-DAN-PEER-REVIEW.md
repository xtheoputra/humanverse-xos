# 262 — §19.19–§19.21 Reproducibility Engine, Scientific Writing Engine & Peer Review Assistant

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.19 — Reproducibility Engine

> Checklist otomatis: `dataset tersedia · code tersedia · parameter
> terdokumentasi · environment terdokumentasi · **seed tercatat**`
>
> Output: **Reproducibility Score**

---

> ⭐⭐⭐⭐ **`seed tercatat` adalah satu butir yang membuktikan seluruh checklist
> ini ditulis oleh orang yang pernah mencoba mengulang percobaan orang lain.**
>
> Empat butir pertama muncul di hampir setiap daftar praktik baik. Yang kelima
> tidak — dan ia yang paling sering menjadi sebab dua orang menjalankan **kode
> yang sama, data yang sama, dan parameter yang sama**, lalu memperoleh angka
> yang berbeda. Menyebutnya berarti checklist ini bukan salinan dari daftar
> umum.
>
> ⭐ Dan `environment terdokumentasi` sebagai butir tersendiri, terpisah dari
> `code tersedia`, mengakui hal kedua yang sama tersembunyinya: kode yang sama
> pada versi pustaka yang berbeda bukan kode yang sama.

> ⭐⭐ **Reproducibility sebagai komponen bernama belum pernah ada di repo ini.**
> Kata itu muncul di dua berkas lama (`110` keandalan infrastruktur, `137`
> silsilah pipeline), keduanya dalam arti operasional — bukan sebagai
> pemeriksaan atas sebuah klaim. Dan ia melengkapi §19.6 dari sisi yang
> berlawanan: `replication` menilai **apakah orang lain sudah mengulang**,
> `Reproducibility Score` menilai **apakah orang lain BISA mengulang**. Yang
> kedua bisa dijawab hari ini, tanpa menunggu siapa pun.

> 🛑 **Tetapi `Reproducibility Score` adalah SATU ANGKA — dan naskah ini
> menolak angka tunggal di tiga tempat lain.**
>
> §19.18 menaruh `effect size` di samping `hypothesis testing` justru karena
> satu angka tidak cukup. §17.36 menutup daftarnya dengan *"accuracy saja tidak
> cukup"*. §18.20 menolak skor kepercayaan tunggal dan menggantinya dengan
> **Trust Vector**, dengan alasan yang berlaku persis di sini: agent yang
> **cepat tetapi tidak aman** tidak boleh menyamai yang **lambat tetapi aman**.
>
> Lima butir checklist ini juga tidak sepadan. Penelitian dengan `dataset`
> terbuka tetapi `seed` hilang berada di keadaan yang **berbeda jenis** dari
> yang punya seed tetapi datanya tertutup: yang pertama bisa didekati, yang
> kedua tidak bisa disentuh sama sekali. Satu angka meratakan keduanya, dan
> angka yang sama akan diperoleh dari dua kegagalan yang menuntut jawaban
> berbeda.
>
> ⭐ Perbaikannya sudah jadi dan tinggal disalin dari §18.20: **vektor lima
> dimensi, bukan skor** — dan `dataset` serta `code` sebagai dimensi yang
> **tidak bisa dikompensasi**, sama seperti `safety` di Trust Vector.

---

## §19.20 — Scientific Writing Engine

> Struktur: `Abstract · Introduction · Methods · Results · Discussion ·
> **Limitations** · References`
>
> Tetapi: **sitasi harus nyata, tidak boleh mengarang referensi.**

---

> ⭐⭐⭐⭐⭐ **Delapan kata itu menamai kegagalan model bahasa yang paling
> terkenal, di tempat yang paling mungkin ia terjadi, sebagai aturan keras —
> dan ini larangan pada KELUARAN, jenis yang bisa diperiksa.**
>
> Referensi yang dikarang punya sifat yang membuatnya khas berbahaya: ia
> **berbentuk benar**. Nama penulis yang masuk akal, jurnal yang ada, tahun yang
> wajar, judul yang cocok dengan kalimat yang dirujuknya. Pembacanya tidak punya
> tanda apa pun untuk curiga, dan pemeriksaannya menuntut membuka tiap rujukan
> satu per satu.
>
> Dan pemilik menuliskannya **sebagai larangan atas apa yang dihasilkan**, bukan
> sebagai niat. Itu bentuk yang sudah berulang dan yang membuat repo ini
> berbeda: §17.7 (*"State ≠ diagnosis"*), §18.25 (*"Early warning detected"*,
> bukan *"This definitely will happen"*), §19.10 (*"tidak boleh langsung memilih
> satu jawaban"*). **Larangan pada keluaran bisa dijadikan uji; larangan pada
> niat tidak.**

> ⭐⭐ **`Limitations` sebagai bagian WAJIB dari struktur tulisan menutup
> lingkaran dengan §19.5.**
>
> §19.5 mengekstrak `limitation` dan `future work` dari paper orang lain —
> dicatat sebagai dua bagian yang paling jarang dibaca dan justru tempat celah
> tinggal. §19.20 mewajibkan HumanVerse **menulisnya juga**. Sistem yang
> mengambil manfaat dari kejujuran orang lain tetapi tidak menghasilkannya
> sendiri akan menguras kolam yang diminumnya; ini simetri yang benar, dan
> tampaknya disengaja.

> 🛑🛑 **Tetapi larangannya tidak punya satu pun langkah yang menegakkannya —
> pengulangan persis C-26.**
>
> **C-26** ([#118](../../issues/118)) mencatat §17.28 mengekstrak rekam medis
> *"tanpa satu pun langkah verifikasi"*. Bentuk yang sama di sini:
>
> - **§19.2** (pipeline sepuluh langkah) berakhir di `Scientific Report`; tidak
>   ada langkah pemeriksaan sitasi.
> - **§19.31** memberi tabel `citations` — **tanpa kolom yang menyatakan sebuah
>   sitasi sudah dicocokkan dengan sumbernya.**
> - **§19.33** memberi `S19.9 Writing & Review` sebagai milestone kesembilan
>   dari sepuluh, tanpa menyebut verifikasi.
>
> ⭐ Dan yang membuat ini murah diperbaiki: **bahannya sudah ada, lengkap.**
> §19.4 melakukan `Citation Extraction`; §19.3 menyimpan `Paper` sebagai node;
> §19.4 menarik dari `Crossref`, `Semantic Scholar`, dan `OpenAlex` — tiga
> sistem yang justru ada untuk **menyelesaikan identitas sebuah rujukan**.
> ⇒ Aturannya bisa dibuat mutlak alih-alih dianjurkan: **tiap sitasi di keluaran
> harus menunjuk ke node `Paper` yang berasal dari ingestion; rujukan yang tidak
> punya simpul TIDAK BISA ditulis.** Larangan yang ditegakkan oleh bentuk data,
> bukan oleh kepatuhan model. Lihat **B-37** / [#134](../../issues/134).

---

## §19.21 — Peer Review Assistant

> Reviewer Agent memeriksa: `logical gaps · unsupported claims ·
> missing citations · statistical issues · unclear methods`

---

> ⭐⭐⭐ **Lima hal yang diperiksa adalah lima cara §19.20 bisa gagal — dan
> pasangan itu tampaknya disengaja.**
>
> | Diperiksa §19.21 | Menjaga dari |
> |---|---|
> | `missing citations` · `unsupported claims` | larangan §19.20 |
> | `statistical issues` | salah terjemah §19.18 |
> | `logical gaps` | lompatan abduktif §19.10 |
> | `unclear methods` | checklist §19.19 |
>
> Kelimanya menunjuk ke bagian lain di naskah yang sama. Untuk dokumen sepanjang
> ini, daftar yang **seluruhnya** punya pasangan di tempat lain adalah tanda
> rancangannya utuh, bukan daftar yang dikumpulkan.

> 🛑 **Tetapi penulis dan pemeriksanya adalah sistem yang sama — dan tidak ada
> satu kalimat pun yang mengakuinya.**
>
> `Writing Agent` dan `Reviewer Agent` (§19.16) berdiri di ekosistem yang sama,
> membaca graf yang sama, mewarisi ekstraksi yang sama. ⇒ **Sitasi yang dikarang
> karena `Paper` palsu masuk graf di §19.4 akan lolos §19.21**, sebab pemeriksa
> menemukan simpulnya persis seperti penulis menemukannya. Peninjauan yang
> berbagi titik buta dengan yang ditinjau **mengukur konsistensi, bukan
> kebenaran** — masalah yang sama dengan §19.17 (tiga agent yang tidak
> dinyatakan berbeda dalam hal apa).
>
> ⭐ Yang perlu dinyatakan: **`Reviewer Agent` memeriksa terhadap SUMBER, bukan
> terhadap graf** — sitasi dicocokkan ulang ke `Crossref`/`OpenAlex`, angka
> dicocokkan ulang ke naskah aslinya. Itu satu-satunya bentuk peninjauan yang
> bisa menangkap kesalahan yang lahir di hulu.

> ⚠️ **Dan sasaran tinjauannya tidak dinyatakan.** Kalau ia meninjau tulisan
> HumanVerse sendiri, ia bagian dari §19.20 dan seharusnya berdiri di jalurnya.
> Kalau ia meninjau **naskah orang lain** — dan *"Peer Review Assistant"*
> menyiratkan itu — maka keluarannya memengaruhi nasib pekerjaan orang, dan
> §19.22 (`bias`) berlaku padanya dengan cara yang sama sekali berbeda. Dua
> pembacaan, dua kelas tanggung jawab, satu nama.
