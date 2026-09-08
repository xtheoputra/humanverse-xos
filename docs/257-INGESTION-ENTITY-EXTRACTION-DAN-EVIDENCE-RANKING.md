# 257 — §19.4–§19.6 Research Ingestion, Scientific Entity Extraction & Evidence Ranking

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.4 — Research Ingestion Engine

> Sumber: `arXiv · PubMed · Crossref · Semantic Scholar · OpenAlex ·
> institutional repositories · conference proceedings · datasets ·
> code repositories`

```
Document → OCR (jika perlu) → Parsing → Section Detection
   → Citation Extraction → Entity Extraction → Knowledge Graph
```

---

> ⭐⭐⭐ **Sembilan sumber yang SEMUANYA punya nama, alamat, dan API sungguhan —
> dan itu perbaikan besar atas §18.4.**
>
> Bandingkan tujuh belas sumber Phase 18: `news`, `government data`, `internet
> knowledge` — kategori, bukan sistem. Di sini `Crossref`, `Semantic Scholar`,
> dan `OpenAlex` adalah **infrastruktur metadata yang benar-benar ada**, dengan
> antarmuka terbuka dan syarat pemakaian yang bisa dibaca sebelum satu baris
> kode ditulis. Ini kebiasaan yang sudah dua kali dicatat sebagai butir **F**
> (naskah 19 lima pustaka SLAM, naskah 20 ROS2 dan empat simulator): **memakai
> yang sudah ada alih-alih menamai kategori.**
>
> ⭐ Dan `code repositories` di daftar yang sama dengan `datasets` mengakui
> sesuatu yang benar tentang penelitian modern: **kode dan data adalah bagian
> dari klaimnya**, bukan lampiran. §19.19 lalu memakainya.

> ⚠️ **Tetapi kesembilan sumber itu tidak sekelas secara lisensi, dan pipeline
> ini tidak punya gerbangnya.**
>
> `arXiv` dan `PubMed` punya syarat yang jelas dan sebagian besar mengizinkan
> penambangan; **naskah lengkap di balik `Crossref` sering tidak** — yang
> terbuka adalah metadatanya. `institutional repositories` dan
> `conference proceedings` berbeda-beda per penerbit.
>
> Ini bentuk yang sama dengan **C-27** ([#122](../../issues/122)) untuk `news`
> dan `scientific publications` di §18.4. ⭐ Bedanya menguntungkan: **naskah ini
> membawa obatnya sendiri** — §19.24 Dataset Intelligence mewajibkan `license`
> dan `provenance`. Yang perlu dilakukan cuma **memberlakukannya di
> `Document`**, bukan hanya pada dataset: lisensi diperiksa **sebelum** naskah
> diurai, dan yang tidak mengizinkan **berhenti di situ**.

> 🛑 **Dan rantai tujuh langkah ini tidak punya langkah VERIFIKASI — pengulangan
> persis C-26.**
>
> **C-26** ([#118](../../issues/118)) mencatat §17.28 memberi
> `Document → OCR → Structure → Entity Extraction → Medical Knowledge Mapping →
> Timeline` sebagai *"tempat paling berbahaya untuk halusinasi di seluruh
> proyek, tanpa satu pun langkah verifikasi"*. Rantai di sini **berbentuk
> sama** dan berakhir di `Knowledge Graph`.
>
> Akibatnya juga sama: kesalahan ekstraksi **tidak terlihat seperti kesalahan**
> — ia menghasilkan metode, angka, dan kesimpulan yang tampak sah, masuk graf,
> lalu menjadi masukan §19.8 (gap detection) dan §19.9 (hipotesis). Dan di sini
> ia bertemu §19.20 yang **melarang mengarang referensi** — larangan yang
> benar, tetapi tanpa langkah yang menegakkannya di hulu.
>
> ⭐ Tiga perbaikan yang C-26 usulkan berlaku tanpa perubahan, dan lebih murah
> di sini karena sumbernya publik: **(a)** tiap entitas menyimpan **kutipan teks
> aslinya** beserta lokasi halaman/bagian — `provenance` yang bisa dibuka;
> **(b)** pipeline terdaftar sebagai model dan tunduk pada metrik; **(c)**
> ekstraksi ditandai **belum terverifikasi** sampai dibandingkan dengan
> naskahnya. Lihat **B-37** / [#134](../../issues/134).

---

## §19.5 — Scientific Entity Extraction

> Ekstrak: `metode · dataset · hasil · angka penting · kesimpulan ·
> **limitation** · **future work**`

```yaml
Paper
  Method:      Transformer
  Dataset:     ImageNet
  Result:      92%
  Limitation:  Small dataset transferability
```

---

> ⭐⭐⭐⭐ **`limitation` dan `future work` masuk daftar ekstraksi — dua bagian
> yang paling jarang dibaca manusia, dan tepat dua bagian tempat celah
> penelitian tinggal.**
>
> Hampir semua sistem literatur mengekstrak metode, data, dan hasil. Yang
> membuat SDE punya alasan berbeda adalah dua yang terakhir: **`future work`
> adalah daftar celah yang ditulis oleh orang yang paling tahu di mana celahnya**,
> dan `limitation` adalah pengakuan penulisnya sendiri tentang di mana
> klaimnya berhenti berlaku.
>
> Keduanya memberi §19.8 (Gap Detection) bahan yang tidak perlu disimpulkan
> dari pola — ia bisa dibaca langsung. Dan `limitation` memberi §19.6 masukan
> untuk `methodological strength` tanpa menilai sendiri.

> 🛑 **Tetapi contohnya menunjukkan masalahnya sendiri: `Result: 92%` bukan
> sebuah hasil.**
>
> Sembilan puluh dua persen **dari apa**, diukur pada pembagian data yang mana,
> dengan sebaran berapa, dibandingkan dengan dasar apa? Angka yang dicabut dari
> kalimatnya berhenti bisa dibandingkan — dan §19.7 (Contradiction Detection)
> bekerja **dengan membandingkan**. Dua paper yang melaporkan 92 % dan 88 % pada
> tugas yang berbeda akan terlihat bertentangan; dua yang melaporkan angka sama
> pada protokol berbeda akan terlihat sepakat.
>
> Ini gejala yang sudah tercatat berulang di repo ini: **angka tanpa cara
> menghitungnya** (bagian **D**, lima model angka pengguna tanpa rumus;
> **B-24**; §18.8 empat relevансi berdesimal dua). ⭐ Perbaikannya kecil dan
> sudah dipakai naskah ini di tempat lain: **`Result` membawa `metric`, `task`,
> `split`, dan `variance`** — dan §19.12 sudah memberi kosakata untuk itu
> (`Independent`/`Dependent Variable`, `Control`).

> ⚠️ **`kesimpulan` juga bukan entitas yang setara dengan `dataset`.** Nama
> dataset ada di halaman; kesimpulan adalah kalimat yang harus **ditafsirkan**,
> dan penafsirannya bisa keliru tanpa terlihat keliru. §19.3 sudah memberi
> `Claim` sebagai node tersendiri — kesimpulan seharusnya menjadi `Claim`
> dengan kutipan aslinya, bukan satu baris di bawah `Dataset`.

---

## §19.6 — Evidence Ranking Engine

> **Tidak semua paper sama kuatnya.** HumanVerse menghitung: `quality ·
> **replication** · consistency · **citation context** · publication venue ·
> methodological strength · recency`

```yaml
evidence:
  strength:    high
  confidence:  0.87
  replication: moderate
```

---

> ⭐⭐⭐⭐ **`replication` dan `citation context` adalah dua faktor yang paling
> menentukan dan paling jarang dihitung — dan keduanya ada di sini.**
>
> **`replication`** menjawab satu-satunya pertanyaan yang benar-benar memisahkan
> temuan yang bertahan dari yang tidak: *apakah ada orang lain yang mendapatkan
> hasil yang sama.* Metrik yang biasa dipakai (jumlah sitasi, nama jurnal)
> mengukur **perhatian**, bukan kebenaran — dan keduanya bisa tinggi untuk
> temuan yang kemudian gagal direplikasi.
>
> **`citation context`** memperbaiki kekeliruan yang lebih halus: sitasi yang
> **membantah** dihitung sama dengan sitasi yang mendukung oleh hampir semua
> sistem yang ada. Sebuah paper yang banyak dikutip **karena salah** akan
> tampak berpengaruh. §19.3 sudah menyediakan bentuknya (`supports` /
> `contradicts` sebagai relasi terpisah), jadi keduanya saling menopang.
>
> ⭐ Dan menaruh `publication venue` **di urutan kelima dari tujuh**, bukan
> pertama, adalah sikap yang benar terhadap ukuran yang paling mudah dan paling
> menyesatkan.

> 🛑 **Tetapi ini `Evidence Ranking` yang KETIGA di repo ini.**
>
> | Tempat | Menilai | Fase |
> |---|---|---|
> | §17.26 | bukti **kesehatan** | Phase 17 |
> | §18.23 | bukti **dunia** (dengan `UNRESOLVED`) | Phase 18 |
> | **§19.6** | bukti **ilmiah** | Phase 19 |
>
> **E-138** ([#124](../../issues/124)) sudah mencatat dua yang pertama tanpa ada
> yang menyatakan itu satu mesin atau dua. Tiga menjadikan pertanyaannya
> mendesak — terutama karena **ketiganya akan menilai bukti yang sama**: klaim
> ilmiah tentang kesehatan yang masuk ke Health Twin lewat §17.26, ke World
> Model lewat §18.23, dan ke Research KG lewat §19.6 bisa memperoleh **tiga
> peringkat berbeda** untuk satu makalah.
>
> ⭐ Perbaikannya: **satu mesin dengan profil per domain**, bukan tiga mesin.
> Tujuh faktor §19.6 adalah yang paling lengkap dari ketiganya, jadi ia calon
> yang benar untuk menjadi induknya. Lihat **E-146** / [#135](../../issues/135).

> ⚠️ **Dan tiga baris keluarannya memakai TIGA skala berbeda:** `strength`
> ordinal bernama (`high`), `confidence` desimal (`0.87`), `replication` ordinal
> lain (`moderate`). Tidak ada yang menyatakan hubungan di antaranya — apakah
> `strength: high` mungkin bersama `confidence: 0.4`? Apakah `replication: none`
> membatasi `strength`?
>
> Ini pola tangga yang sudah tiga kali muncul (**E-77**/H-21 · **E-133**/
> [#117](../../issues/117) · **E-138**/[#124](../../issues/124)), kini di dalam
> **satu blok tiga baris**. ⭐ Bentuk yang benar sudah ada di §18.24, yang
> memisahkan `Probability` dari `Confidence` dan menyatakan bedanya:
> **`strength` = seberapa kuat buktinya, `confidence` = seberapa yakin kita pada
> penilaian itu sendiri** — dan kalau itu yang dimaksud, ia layak ditulis, sebab
> keduanya akan tertukar dalam kode.
