# 267 — §20.4–§20.6 Civilization Knowledge Graph, State Engine & Civilization Digital Twin

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.4 — Civilization Knowledge Graph

Node: `Human · Community · Organization · Company · Institution · City ·
Country · Infrastructure · Technology · Resource · Knowledge ·
Scientific Discovery · Environment · Agent · Robot · Policy · Economic System`

Relasi: `works_for · lives_in · **depends_on** · produces · consumes ·
regulates · **influences** · collaborates_with · competes_with · affects ·
discovers · uses · owns · governs`

> ```
> Technology → Industry → Organization → Employment → Human → Family → Community → City
> ```
>
> Dengan ini HumanVerse dapat memahami **dependency chain**.

---

> ⭐⭐⭐ **`depends_on` sebagai relasi kelas satu adalah yang menjadikan §20.19
> (Resilience) mungkin — dan ia belum pernah ada di graf mana pun di repo ini.**
>
> §18.6 memberi `affects` dan `potentially_affects`; keduanya menyatakan
> **pengaruh**, yang arahnya bisa lemah dan bisa kuat. `depends_on` menyatakan
> sesuatu yang berbeda jenis: **kalau yang ini hilang, yang itu berhenti.** Dari
> relasi itulah rambatan kegagalan §20.19 (`Failure → Dependency Graph → Impact
> Propagation → Alternative Paths`) bisa dihitung, dan tanpa itu ketahanan cuma
> nama bagian.
>
> ⭐ `competes_with` juga bukan pelengkap: ia satu-satunya relasi di daftar yang
> menyatakan **kepentingan yang berlawanan**. Graf yang hanya memodelkan
> kerja sama akan menghasilkan rekomendasi yang mengandaikan semua pihak mau
> hal yang sama.

> 🛑🛑 **Tetapi `influences` KEMBALI sebagai tepi telanjang — dan itu butir
> tertua di repo ini, yang §17.9 sudah tutup.**
>
> **E-81** ([#7](../../issues/7)) mencatat `influences` muncul berulang tanpa
> bukti kausal. §17.9 menutupnya dengan **empat tingkat** (`Observed
> relationship · Correlation · Hypothesis · Causal evidence`) dan aturan tegas:
> hanya tingkat keempat yang boleh menjadi dasar rekomendasi. §18.9 memberi lima
> (**E-138** / [#124](../../issues/124)).
>
> Di sini `influences` dan `affects` berdiri **bersebelahan di satu daftar,
> tanpa satu pun membawa tingkat bukti** — dan §20.7 membaca graf ini untuk
> merambatkan dampak lintas ekonomi, sosial, dan lingkungan. Rambatan yang tidak
> tahu kekuatan tepinya akan memperlakukan dugaan sama dengan bukti, pada skala
> di mana kekeliruannya paling mahal.
>
> ⭐ Perbaikannya sudah dinyatakan dua kali dan tetap sama: **tiap tepi membawa
> `evidence_level` + `confidence` + `sources`** — tiga hal yang §18.5 sudah
> lekatkan pada event.

> ⚠️ **`Human` dan `Family` berdiri sebagai simpul di graf peradaban** — untuk
> **ketiga** kalinya pola ini muncul (`Company employs Human` §18.6 · `Disease`
> dan `Gene` §19.3 · di sini), dan tiap kali usulnya sama: **graf skala besar
> berhenti di organisasi; penautan ke individu terjadi di sisi pribadi**, tempat
> §17.4 dan Personal Data Vault berlaku. Naskah ini justru punya bagian yang
> menegakkannya — §20.13 *Human Data Sovereignty* — tetapi kedua bagian itu
> tidak saling menyebut.

---

## §20.5 — Civilization State Engine

```yaml
civilization_state:
  economic:        { stability: 0.71 }
  technological:   { acceleration: 0.89 }
  environmental:   { pressure: 0.62 }
  scientific:      { discovery_rate: 0.83 }
  infrastructure:  { resilience: 0.77 }
  social:          { cohesion: 0.68 }
  uncertainty: 0.34
```

> Ini bukan **"angka kebenaran"**. Ia merupakan model keadaan **dengan
> confidence dan provenance**.

---

> ⭐⭐⭐⭐ **Kalimat penyangkalannya ditulis PEMILIK SENDIRI, tepat di bawah
> angkanya — dan ia menyebut dua hal yang benar, bukan satu.**
>
> *"Bukan angka kebenaran"* saja akan menjadi peringatan yang bisa diabaikan.
> Menambahkan **`confidence` dan `provenance`** menjadikannya syarat bentuk:
> sebuah angka yang wajib membawa keyakinan dan asal-usulnya **tidak bisa
> disajikan telanjang**, dan pembacanya selalu punya bahan untuk membantah.
> Ini kebiasaan yang sudah muncul di §18.8 (*relevance ≠ certainty*), §18.10
> (*bukan prediksi absolut*), dan §20.7 (*simulation ≠ prediction certainty*) —
> **empat naskah berturut-turut membantah angkanya sendiri.**

> ⭐⭐ **`uncertainty` sebagai field TINGKAT ATAS, sejajar dengan enam sumbu
> lain, belum pernah ada.** Ia menyatakan ketidakpastian **tentang keadaan
> secara keseluruhan** — bukan per angka — dan itu hal yang berbeda: enam sumbu
> bisa masing-masing terukur baik sementara model yang menyatukannya tetap
> rapuh. §18.24 sudah memisahkan `Probability` dari `Confidence`; ini
> perluasannya yang benar.

> 🛑🛑 **Tetapi tujuh angka itu tidak punya satu pun rumus — dan `social
> cohesion` adalah yang paling mustahil dan paling berakibat.**
>
> Bagian **D** sudah mencatat lima model angka pengguna tanpa rumus; §18.8
> menambah satu (empat relevansi berdesimal dua); ini menambah **tujuh
> sekaligus**, pada objek yang paling besar. Dan ketujuhnya bukan sekelas:
>
> | Sumbu | Ada ukuran yang disepakati? |
> |---|---|
> | `economic stability`, `discovery_rate` | ada, meski banyak versinya |
> | `technological acceleration`, `infrastructure resilience` | sebagian, dan bergantung definisi |
> | **`social cohesion`** | **tidak — ia diperdebatkan di bidangnya sendiri** |
>
> Menyatakan kohesi sosial sebuah masyarakat sebagai **satu angka** bukan
> penyederhanaan teknis; ia mengambil posisi dalam perdebatan yang belum selesai,
> lalu **memberi angka itu ke §20.7 (simulasi) dan §20.9 (pilihan keputusan)**.
> Kekeliruannya tidak akan terlihat sebagai kekeliruan — ia akan terlihat seperti
> pengukuran. ⭐ Yang perlu minimum: **tiap sumbu menyebut apa yang diukurnya dan
> dari mana**, dan sumbu yang tidak punya ukuran disepakati **disajikan sebagai
> beberapa indikator, bukan satu angka**. Lihat **B-38** / [#145](../../issues/145) dan **C-30**.

---

## §20.6 — Civilization Digital Twin

```
Human → Family → Community → Organization → City → Region → Country
   → Global System → Civilization Twin
```

---

> ⭐⭐ **Sembilan tingkat, dan `Community` akhirnya punya tempat.** Tangga
> sebelumnya melompat dari orang ke organisasi; komunitas adalah tempat sebagian
> besar hal yang berarti bagi orang benar-benar terjadi, dan ia yang
> menjembatani `Personal Relevance` §18.8 dengan skala kota.

> 🛑 **Tetapi ini susunan KEENAM untuk tangga cakupan yang sama, dalam satu
> repo.**
>
> | # | Sumber | Ciri |
> |---|---|---|
> | 1 | §18.11 diagram 1 | Organization → City → Industry → Regional |
> | 2 | §18.11 diagram 2 | Company → Industry → City (`Regional` hilang) |
> | 3 | §18.26 | Regional → City → Organization → Industry |
> | 4 | penutup Phase 19 | + `Family/Community`, + `Country`, − `Industry` |
> | 5 | §20.3 | `City · Organization · Industry` **sejajar** |
> | 6 | **§20.6** | sembilan tingkat, **`Industry` hilang lagi** |
>
> **E-141** ([#130](../../issues/130)) sudah mencatat empat; enam menjadikan
> pertanyaannya bukan lagi soal kerapian: **§20.7 merambatkan dampak menaiki
> tangga ini**, jadi susunannya menentukan hasil simulasinya. Dan `Industry` —
> yang punya `industry-intelligence/` sendiri sejak naskah 22 — hilang dari
> susunan yang paling rinci.

> 🛑 **Dan `Family` sebagai tingkat kembaran adalah kelas data yang belum pernah
> dibahas: model tentang ORANG LAIN yang tidak pernah menjadi pengguna.**
>
> Seluruh mesin persetujuan repo ini (§8.9 `consent` · §8.10 `purpose` ·
> §17.4 per data · Privacy Center **H-4**) mengandaikan **orang yang datanya
> dipakai adalah orang yang menekan tombol**. Untuk `Organization Twin` dan
> `City Twin` masalah itu sudah tercatat (**C-27** / [#122](../../issues/122)).
> `Family Twin` adalah bentuknya yang paling tajam: **anggota keluarga tidak
> memberi persetujuan, tidak punya akun, dan sebagian tidak bisa memberi
> persetujuan sama sekali** — anak-anak, dan orang yang dirawat.
>
> ⭐ Naskah ini punya bahan untuk membatasinya: §20.13 memberi enam sumbu kendali
> (`Who · What · Why · When · Where · How long`) dan §20.12 memberi
> `Data Minimization`. Yang perlu ditulis: **kembaran keluarga dibangun dari data
> penggunanya sendiri tentang hubungannya, bukan dari data orang lain** —
> dan kalau bukan itu yang dimaksud, ia menuntut dasar hukum yang berbeda,
> bukan persetujuan. Lihat **C-30** / [#141](../../issues/141).
