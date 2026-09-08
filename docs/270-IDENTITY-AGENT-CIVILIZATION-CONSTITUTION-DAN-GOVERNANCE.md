# 270 — §20.14–§20.17 Civilization Identity, Agent Civilization, Agent Constitution & Governance Engine

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.14 — Civilization Identity

> `Human · Agent · Organization · Device · Institution · Service` — semuanya
> memiliki: `Identity · Authentication · Authorization · Capabilities ·
> Reputation · Trust · Audit`

---

> ⭐⭐⭐ **Satu skema identitas untuk enam jenis pelaku — termasuk manusia dan
> mesin di daftar yang sama — adalah keputusan yang menyederhanakan seluruh
> lapisan izin.**
>
> Sistem yang memberi manusia satu model identitas dan agent model lain akan
> punya dua jalur kewenangan, dan celah selalu ada di antaranya. Tujuh atribut
> yang sama untuk keenamnya berarti pertanyaan *"apakah pelaku ini boleh"*
> dijawab di satu tempat. ⭐ Dan **`Capabilities` sebagai atribut identitas**
> (bukan pemberian sesaat) menjadikan **Article 2** §20.16 (*least privilege*)
> punya tempat penyimpanan.

> ⚠️ **Tetapi `Trust` dan `Reputation` masih dua atribut terpisah tanpa ada yang
> menyatakan bedanya** — pertanyaan yang sudah tercatat di **E-141**
> ([#130](../../issues/130)) ketika §18.28 memberi `agent_trust_scores` dan
> `agent_reputation` sebagai dua tabel. §20.29 kini memberi `trust_records`
> **dan** `reputation_records`, jadi dua tabel itu bertahan tiga naskah tanpa
> definisi pembeda. Dua kolom untuk perbedaan yang belum ditulis akan diisi
> dengan hal yang sama.

---

## §20.15 — Agent Civilization

> `Personal · Organization · Research · City · Infrastructure · Economic ·
> Scientific · Environmental Agent` — tetapi semuanya:

```
Agent → Identity → Capability → Permission → Risk → Policy → Action
```

---

> ⭐⭐⭐ **`Risk` DAN `Policy` keduanya di rantai — dan ini kali ketiga
> berturut-turut `Risk` bertahan sesudah tujuh rantai kehilangannya.**
>
> §17.38 mengembalikannya pertama kali sejak §11.14; §18.17 mempertahankannya
> (`Agent Risk` melekat pada agent, bukan pada satu rantai); di sini keduanya
> berdiri bersama, dan `Policy` **sesudah** `Risk` — urutan yang benar: risiko
> dinilai dulu, kebijakan memutuskan berdasarkan nilainya.

> 🛑 **Tetapi tidak ada `Confirmation` di rantai ini, sementara §20.17 dan
> §20.35 keduanya punya `Approval`.**
>
> **H-15** menetapkan konfirmasi manusia wajib mulai **R3**. Rantai agent di
> sini berakhir langsung di `Action`. Dua bagian lain di naskah yang sama
> memberi persetujuan manusia — jadi ini bukan kelalaian rancangan melainkan
> **rantai yang tidak disambungkan**: yang perlu dinyatakan satu baris,
> ***aksi agent pada R3 ke atas masuk jalur §20.35, bukan jalur ini.***
> Lihat **E-150** / [#140](../../issues/140).

---

## §20.16 — Agent Constitution

> *"Saya menyarankan kita membuat sesuatu yang belum ada di fase sebelumnya
> secara eksplisit: **HumanVerse Agent Constitution**."*

| | Pasal | | | Pasal |
|---|---|---|---|---|
| 1 | **Human sovereignty** | | 6 | Safety |
| 2 | Least privilege | | 7 | Privacy |
| 3 | Transparency | | 8 | **No deceptive behavior** |
| 4 | Auditability | | 9 | **No unauthorized autonomy** |
| 5 | **Reversibility** | | 10 | **Human override** |

> Ini menjadi **governance layer tertinggi**.

---

> ⭐⭐⭐⭐⭐ **Ini yang paling penting di seluruh naskah 24 — dan tiga dari sepuluh
> pasalnya menutup butir yang sudah terbuka lama, dalam bentuk aturan alih-alih
> catatan.**
>
> | Pasal | Menutup |
> |---|---|
> | **5 — Reversibility** | **H-21** menetapkan `R4` = tak-terbalikkan = `DENY` bawaan. Selama ini itu sifat *tingkat risiko*; sebagai pasal, ia menjadi **syarat semua agent** |
> | **9 — No unauthorized autonomy** | **B-30**/[#99](../../issues/99) dan **E-130**/[#111](../../issues/111) — otonomi agent yang dibuka sebelum gerbangnya ada |
> | **10 — Human override** | **H-15** — dan `override` lebih kuat daripada `confirmation`: konfirmasi berlaku **sebelum** aksi, override berlaku **selama** aksi berlangsung |
>
> ⭐⭐ **Pasal 8 (*no deceptive behavior*) belum pernah ada di mana pun di repo
> ini, dan ia yang paling sulit dibuat sendiri kemudian.** Sembilan pasal lain
> membatasi **apa yang boleh dilakukan agent**; yang ini membatasi **bagaimana ia
> boleh menyampaikan**. Sebuah sistem yang mematuhi sembilan pasal pertama tetapi
> boleh menyesatkan dalam penyampaiannya bisa memperoleh persetujuan untuk hal
> yang tidak dipahami penggunanya — dan dengan itu **Pasal 1 dan 10 kehilangan
> artinya**, sebab kedaulatan yang dijalankan atas dasar gambaran yang keliru
> bukan kedaulatan. Menaruhnya sebagai pasal, bukan sebagai nilai, adalah
> perbedaan antara sesuatu yang diuji dan sesuatu yang diharapkan.

> ⭐⭐ **Dan bentuk "konstitusi" itu sendiri yang menyelesaikan pola yang sudah
> tercatat empat kali.** **B-33**/[#116](../../issues/116), **G-17**/
> [#121](../../issues/121), **C-29**/[#131](../../issues/131) semuanya berbunyi
> sama: *keselamatan dijadwalkan sesudah hal yang harus dijaganya*. Sebuah
> konstitusi tidak punya nomor urut — ia **berlaku pada semua yang datang
> sesudahnya, termasuk yang dibangun lebih dulu**. Itu jawaban struktural untuk
> masalah penjadwalan, dan ia sejalan dengan kalimat pemilik sendiri di §17.56
> dan §19.23: **governance adalah fungsi dari tingkat, bukan milestone.**

> 🛑 **Tetapi sepuluh pasal tanpa mekanisme penegakan tetap sepuluh kalimat —
> dan tiga hal yang membuatnya menggigit belum ada.**
>
> 1. **Siapa yang memeriksa kepatuhan, dan kapan.** §20.28 memberi
>    `governance/constitution/` sebagai direktori ⭐, tetapi tidak ada langkah di
>    rantai mana pun yang berbunyi *"periksa terhadap Konstitusi"*. Bandingkan
>    Pasal 4 (*Auditability*), yang menuntut jejak — dan §20.29 memang memberi
>    `audit/`.
> 2. **Apa akibat pelanggaran.** Konstitusi tanpa konsekuensi tidak berbeda dari
>    pedoman. §18.19 sudah menunjukkan bentuknya (sertifikasi sebelum
>    marketplace) dan kekurangannya (tidak ada pencabutan).
> 3. **Apakah `local policy` §20.11 bisa melonggarkannya.** Kalau bisa,
>    Konstitusi bukan lapisan tertinggi. Yang perlu ditulis: **kebijakan lokal
>    boleh memperketat, tidak pernah melonggarkan.**
>
> ⚠️ Ditambah: **`C20.7 Governance` adalah milestone ke-7 dari 12**, sesudah
> `C20.6 Coordination Network` — yaitu sesudah lapisan yang menjalankan tugas
> dan sumber daya. Lihat **G-19** / [#144](../../issues/144).

---

## §20.17 — Civilization Governance Engine

```
Intent → Policy → Risk → Impact → Stakeholders → Simulation
   → Decision → Approval → Execution → Audit
```

> Governance bukan hanya security. Ia mencakup: `ethical · social ·
> environmental · economic · technical · legal · human rights`.

---

> ⭐⭐⭐⭐ **`Approval` ADA — dan itu persetujuan manusia yang hilang dari LIMA
> rantai berturut-turut.**
>
> Riwayat yang sudah tercatat: §14.20 kehilangan `Confirmation`
> (**E-117**/[#93](../../issues/93)) · §15.22 (**E-124**/[#106](../../issues/106))
> · §16.18 dan §16.13 (**E-130**/[#111](../../issues/111)) · §18.30
> (**E-143**/[#125](../../issues/125)) · §19.11 dan §19.15
> (**C-29**/[#131](../../issues/131)). Rantai ini mengembalikannya, dan §20.35
> menamainya lebih terang lagi (`HUMAN APPROVAL`).

> ⭐⭐⭐ **Dan tiga gerbang di tengahnya belum pernah ada di rantai mana pun:
> `Impact`, `Stakeholders`, `Simulation`.**
>
> `Stakeholders` adalah yang paling menentukan: ia memaksa pertanyaan **"siapa
> yang terkena"** dijawab **sebelum** keputusan, bukan sesudah. Itu tepat yang
> hilang dari fungsi utilitas §20.9 — bobot yang disetel oleh pihak yang tidak
> menanggung `Externality` (**C-30** / [#141](../../issues/141)). Dan `Simulation` **di dalam** rantai tata
> kelola berarti keputusan besar harus dijalankan dulu di model sebelum
> dijalankan di dunia — bentuk yang sama dengan §16.26 (`Simulation → Safety
> Test → Hardware`) dan §19.13, kini pada keputusan alih-alih pada mesin.

> ⚠️ **Tetapi dibandingkan §11.14, rantai ini BUKAN yang terpanjang — ia
> tersusun berbeda, dan dua gerbang lama tidak kembali.**
>
> | | §11.14 Action Gateway | §20.17 |
> |---|---|---|
> | ada di keduanya | `Risk` · `Policy` · `Confirmation`/`Approval` | ✓ |
> | **hanya §11.14** | **`Consent`** · **`Rate Limit`** | — |
> | hanya §20.17 | — | `Impact` · `Stakeholders` · `Simulation` |
>
> **`Consent`** adalah kehilangan yang sama dengan §18.15 (HINP): `Policy`
> menjawab *"apakah ini diizinkan aturan"*, `Consent` menjawab **"apakah ORANG
> yang datanya ada di dalam pernah mengizinkan"** — dan §8.9/§8.17 memisahkan
> keduanya dengan tegas (**H-15**: izin di muka bukan konfirmasi). Untuk fase
> yang membangun `Family Twin` dan `City Twin`, justru itu yang paling
> dibutuhkan. ⭐ Bahannya ada: `federation_consents` §18.28 dan
> `sovereignty/consent/` §20.28.
>
> **`Rate Limit`** hilang di seluruh rantai sejak §14.20 — dan pada jaringan
> yang menjalankan agent kota dan infrastruktur, laju adalah salah satu dari
> sedikit hal yang membatasi kerusakan sebuah kekeliruan yang lolos gerbang
> lain.

> ⭐ **Tujuh dimensi tata kelola (`ethical` … `human rights`) juga menyatakan
> hal yang benar:** tata kelola di sini bukan cabang keamanan. `human rights`
> sebagai dimensi tersendiri belum pernah disebut di dua puluh empat naskah.
