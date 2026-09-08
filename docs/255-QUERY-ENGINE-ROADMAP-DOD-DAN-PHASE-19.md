# 255 — §18.30–§18.34 Query Engine, Contoh, Roadmap, Definition of Done & Phase 19

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.30 — Intelligence Query Engine

> User dapat bertanya: *"Apa yang berubah di dunia yang relevan terhadap saya?"*

```
Question → Intent → Personal Context → World Context → Knowledge Retrieval
   → World Model → Reasoning → Simulation → Personal Relevance → Answer
```

> Ini jauh lebih powerful daripada search engine biasa.

---

> ⭐⭐⭐ **`Personal Context` diambil SEBELUM `World Context`, dan urutan itu
> menentukan jenis sistemnya.**
>
> Mesin yang mencari dunia dulu lalu menyaringnya untuk pengguna adalah mesin
> pencari dengan penyaring. Mesin yang **tahu siapa yang bertanya sebelum
> mencari** dapat menanyakan pertanyaan yang berbeda ke dunia — dan itu
> perbedaan yang dijanjikan kalimat penutupnya. §18.31 hanya mungkin dengan
> urutan ini.

> 🛑 **Tetapi sepuluh langkah ini tidak melewati satu gerbang pun, sementara
> §18.22 berdiri dua belas bagian sebelumnya.**
>
> Sudah dibahas di [`253`](253-SAFETY-KERNEL-INFORMATION-INTEGRITY-RISK-EARLY-WARNING.md):
> ini pola rantai-tanpa-gerbang yang kelima, tetapi **satu-satunya di mana
> gerbangnya ada di naskah yang sama** — jadi ia masalah perkabelan, bukan
> rancangan. `Reasoning` di sini adalah `Reasoning` yang sama di §18.22.
> Lihat **E-143** / [#125](../../issues/125).

> ⚠️ **`Personal Relevance` berdiri tepat sebelum `Answer` — sebagai penyaring
> terakhir.** Itu berarti apa yang pengguna lihat ditentukan oleh skor yang
> §18.8 sendiri akui tanpa rumus. Sistem yang menyaring dengan angka yang tidak
> bisa dijelaskan akan menyembunyikan hal-hal tanpa bisa mengatakan mengapa —
> dan pengguna tidak punya cara meminta yang tersaring. Perlu: **ambang yang
> bisa dilihat dan diubah pengguna**, atau setidaknya *"ada N hal lain yang
> saya anggap kurang relevan"*.

---

## §18.31 — Contoh penggunaan

> User: *"Kenapa hidup saya terasa semakin mahal?"*

```
Personal Spending → Local Inflation → Commodity Prices → Energy Prices
   → Global Economy → Personal Financial Context
```

> Observed: `Food expenditure +12 %` · Local: `Food inflation +7 %` ·
> Global: `Commodity prices increased` · Personal: `Consumption pattern changed`
>
> HumanVerse dapat membedakan: **"Bagian mana yang berasal dari dunia dan bagian
> mana yang berasal dari perubahan perilaku Anda."**

---

> ⭐⭐⭐⭐⭐ **Ini contoh terbaik dalam dua puluh dua naskah, dan ia satu-satunya
> yang menjelaskan mengapa Phase 18 harus ada.**
>
> `+12 %` yang dialami, `+7 %` yang berasal dari dunia — sisanya perilaku. Itu
> **pengurangan yang tidak bisa dilakukan oleh sistem mana pun yang hanya
> mengenal penggunanya, maupun oleh sistem mana pun yang hanya mengenal dunia.**
> Ia menuntut kedua model sekaligus, dan itulah pembenaran seluruh fase ini
> dalam satu baris aritmetika.
>
> ⭐⭐ Yang membuatnya lebih baik lagi: **ia menjawab pertanyaan yang benar-benar
> orang tanyakan**, dengan kata-kata yang benar-benar orang pakai (*"terasa
> semakin mahal"*), dan jawabannya **tidak menyalahkan siapa pun**. Sistem yang
> berkata *"Anda boros"* akan ditutup; sistem yang berkata *"tujuh dari dua
> belas itu bukan Anda"* akan dipercaya — dan kebetulan itu juga yang lebih
> jujur.
>
> ⭐ Dan ini penerapan pertama yang nyata dari anak panah dua arah §18.11:
> pembagian ini **hanya mungkin** pada tangga yang bisa dibaca dari atas ke
> bawah.

> ⚠️ **Tetapi seluruh contoh ini berdiri di atas data yang belum punya
> lemari.** `Personal Spending` dan `Food expenditure` adalah data keuangan
> pribadi — Level 3–4 menurut §8.16, sama dengan kesehatan. Naskah 21 membangun
> Health Vault lengkap (§17.4–§17.5) untuk kelas yang setara; di sini tidak ada
> padanannya, dan §18.28 tidak punya satu tabel pun untuknya. Lihat **A-33** / [#128](../../issues/128).

> ⚠️ **Dan pembagian `dunia lawan perilaku` menuntut tepat yang §18.9 belum
> selesaikan.** Menyatakan *"7 % dari dunia"* adalah klaim **kausal**, bukan
> korelasi — dan menurut §17.9 hanya `Causal evidence` yang boleh mendasari
> pernyataan seperti itu. Contoh ini tidak menyebut tingkat buktinya di mana
> pun. Kalau tangga lima tingkat (**E-138** / [#124](../../issues/124)) tidak melekat di sini, ia tidak
> akan melekat di mana pun.

---

## §18.32 — Phase 18 Roadmap

| | Milestone | Isi |
|---|---|---|
| **G18.1** | World Data Foundation | ingestion · schemas · source registry · **provenance** |
| **G18.2** | World Knowledge Graph | entities · relationships · events · temporal graph |
| **G18.3** | World Intelligence Engine | trend · anomaly · event intelligence · forecasting |
| **G18.4** | Global World Model | world · regional · industry · city state |
| **G18.5** | **Information Integrity** | source validation · contradiction detection · evidence ranking · claim verification |
| **G18.6** | Global Risk Intelligence | risk models · early warning · risk propagation |
| **G18.7** | Intelligence Federation | HINP · node discovery · secure exchange · federation policies |
| **G18.8** | Collective Intelligence | multi-agent reasoning · consensus · debate · synthesis |
| **G18.9** | World Simulation | global scenarios · causal models · counterfactuals · Monte Carlo |
| **G18.10** | Human ↔ World Intelligence | integrasi World → City → Organization → Industry → Human → Digital Twin → HumanOS → Agent |

---

> ⭐⭐⭐⭐ **`provenance` di milestone PERTAMA dan `Information Integrity` di
> tengah — dan keduanya mendahului setiap milestone yang menalar di atas
> datanya. Ini urutan roadmap terbaik dalam lima naskah.**
>
> G18.5 berdiri **sebelum** risiko (G18.6), federasi (G18.7), penalaran kolektif
> (G18.8), dan simulasi (G18.9). Artinya data diverifikasi sebelum ada yang
> menyimpulkan darinya — kebalikan langsung dari pola yang sudah dicatat tiga
> kali (**B-30**/[#99](../../issues/99) · **E-130**/[#111](../../issues/111) ·
> **B-33**/[#116](../../issues/116)). Dan `provenance` di G18.1 berarti asal-usul
> dibangun sebagai **fondasi**, bukan ditambahkan ketika seseorang menanyakan
> *"dari mana ini"* — sesuatu yang hampir mustahil dipasang belakangan.

> 🛑🛑🛑 **Tetapi §18.22 Global Intelligence Safety Kernel — yang naskahnya
> sendiri sebut *"sangat penting"* — TIDAK PUNYA MILESTONE, dan tidak ada di
> Definition of Done.**
>
> G18.5 mencakup §18.23 (Information Integrity), bukan §18.22. Delapan ancaman
> yang §18.22 daftar — `malicious agents`, `prompt injection`,
> `poisoned knowledge`, `unsafe autonomous decisions` — tidak tersentuh oleh
> `source validation · contradiction detection · evidence ranking ·
> claim verification`. Keduanya menjawab pertanyaan yang berbeda: yang satu
> *"apakah informasi ini benar"*, yang lain *"apakah masukan ini menyerang
> saya"*.
>
> Ini **naskah KETIGA berturut-turut** yang menempatkan keselamatan paling
> belakang, dan lintasannya menurun secara tetap:
>
> | Naskah | Milestone keselamatan | Posisi |
> |---|---|---|
> | 20 (Phase 16) | `R16.10` | terakhir dari 10 — [#111](../../issues/111) |
> | 21 (Phase 17) | `H17.12` | di luar MVP — [#116](../../issues/116) |
> | **22 (Phase 18)** | **—** | **tidak ada sama sekali** |
>
> ⭐ Dan seperti pada #116, **jawabannya sudah ditulis pemilik sendiri**: penutup
> §17.56 menjadikan governance *"semakin ketat di setiap level"* — **fungsi dari
> tingkat, bukan milestone**. Kalau aturan itu diberlakukan, §18.22 tidak
> mungkin absen, karena Phase 18 adalah tingkat tertinggi yang pernah ada.
> Lihat **G-17** / [#121](../../issues/121).

> ⚠️ **G18.6 menelan `early warning` sebagai satu butir di dalam milestone
> risiko.** §18.25 adalah satu-satunya bagian naskah ini yang keluarannya
> menyentuh keselamatan publik (**C-28** / [#123](../../issues/123)); menjadikannya sub-butir berarti ia
> akan dibangun sebagai fitur pelaporan, bukan sebagai kewenangan yang butuh
> gerbang.

---

## §18.33 — Definition of Done

> Phase 18 selesai ketika HumanVerse mampu: memahami world events · membangun
> World Knowledge Graph · memahami temporal changes · mendeteksi global trends ·
> mendeteksi anomalies · menghubungkan event → entity → impact ·
> evidence-based reasoning · information integrity checking · global risk
> analysis · early warning · World Model · world simulation · menghubungkan
> World Model dengan Digital Twin · federated intelligence · berkomunikasi
> dengan external agents · memiliki agent trust/reputation · memiliki
> provenance · **memiliki privacy boundaries** · **memiliki governance** ·
> secure intelligence protocol · collective intelligence.

---

> ⭐⭐ **Dua puluh satu butir, dan tujuh belas di antaranya punya milestone yang
> jelas** — kerapian yang jauh di atas rata-rata repo ini.

> 🛑 **Tetapi EMPAT butir tidak punya milestone mana pun** — dan tiga dari empat
> adalah yang paling menentukan apakah fase ini boleh menyentuh orang:
>
> | Butir DoD | Milestone |
> |---|---|
> | `memiliki privacy boundaries` | **tidak ada** |
> | `memiliki governance` | **tidak ada** |
> | `memiliki agent trust/reputation` (§18.20) | **tidak ada** |
> | *(Safety Kernel §18.22 — bahkan tidak masuk DoD)* | **tidak ada** |
>
> Ini pengulangan persis **B-33** ([#116](../../issues/116)): §17.54 menuntut
> `escalation`, `emergency`, dan `audit` sebagai kriteria selesai tanpa satu pun
> milestone membangunnya. **Naskah kedua berturut-turut**, dan kesimpulannya
> tidak berubah: **kriteria yang tidak punya milestone tidak akan pernah
> diperiksa** — ia akan dicentang oleh orang yang ingin fase ini dinyatakan
> selesai.
>
> ⭐ Perbaikannya murah: **satu milestone `G18.11 Safety, Privacy & Governance`,
> dan ia bukan yang terakhir.** Bahannya sudah ada seluruhnya — §18.22, §18.20,
> `privacy/`, `governance/` (§18.27), `federation_consents` (§18.28).

---

## §18.34 — Evolusi HumanVerse setelah Phase 18

```
              HUMANVERSE
    HUMAN   ·   WORLD   ·   PHYSICAL
      ↓          ↓            ↓
Digital Twin  World Model  Robotics
              ↓
        Intelligence → Agents → HumanOS
```

> Dan seluruh sistem:
>
> ```
> PERCEIVE → UNDERSTAND → THINK → SIMULATE → DECIDE → ACT → OBSERVE → LEARN
> ```

---

> ⭐⭐⭐ **Delapan langkah itu MENUTUP menjadi lingkaran — `OBSERVE → LEARN`
> kembali ke `PERCEIVE` — dan ini pertama kalinya arsitektur besar repo ini
> digambar sebagai putaran, bukan tangga.**
>
> Semua ringkasan sebelumnya (§10.41, §17.56, §18.2) berbentuk urutan fase yang
> berakhir di suatu tempat. Putaran menyatakan hal yang berbeda dan lebih benar:
> **sistem melihat akibat tindakannya sendiri dan berubah karenanya.** Itu juga
> satu-satunya bentuk yang membuat kalibrasi (§17.36) dan `Horizon` (§18.24)
> punya arti — klaim yang dibuat hari ini diperiksa oleh `OBSERVE` besok.

> 🛑 **Tetapi `DECIDE → ACT` bersebelahan tanpa apa pun di antaranya, dan ini
> diagram KETIGA di naskah ini tanpa `GOVERNANCE MESH` maupun `ACTION
> GATEWAY`.**
>
> §14.69 menetapkan keduanya sebagai lapisan wajib **tepat di celah itu**.
> §18.3, §18.26, dan §18.34 melewatinya — dan naskah 19, 20, 21 juga. Empat
> naskah, tujuh diagram. Ketika sebuah lapisan yang dinyatakan wajib tidak
> pernah muncul di gambar mana pun selama empat naskah, yang berlaku adalah
> gambarnya. Lihat **E-143** / [#125](../../issues/125).

> ⚠️ **Dan `HumanOS` berada di ujung, sesudah `Agents`** — sementara §18.26
> menaruh `HUMANOS` sesudah `DIGITAL TWIN`, dan Phase 13 mendefinisikannya
> sebagai sistem operasi yang **menjalankan** agent, bukan yang dijalankan
> sesudahnya. Ini arti keempat untuk *"HumanOS"* (**E-114** mencatat tiga).

---

## Penutup — dan Phase 19

> Sebelumnya: *"AI yang memahami manusia."* Sekarang: **"AI yang memahami
> manusia dalam konteks dunia."**
>
> Dan ini membuka **Phase 19 — HumanVerse Civilization Intelligence**: memahami
> interaksi `Human ↕ Family/Community ↕ Organization ↕ City ↕ Country ↕ Global
> Economy ↕ Technology ↕ Environment ↕ AI Agents ↕ Robotics ↕ Civilization`
> sebagai satu sistem kompleks.

---

> 🛑 **Peta fase diperpanjang untuk kali KEEMPAT berturut-turut, di kalimat
> penutup, tanpa menyebut §10.41.**
>
> naskah 19 → Phase 16 · naskah 20 → Phase 17 · naskah 21 → Phase 18 ·
> naskah 22 → **Phase 19**. **E-128** ([#108](../../issues/108)) sudah
> menyimpulkan petanya terbuka-ujung; empat kali berturut-turut menjadikan usul
> **memberi VERSI pada peta fase** bukan lagi kerapian melainkan syarat agar
> dokumen bisa menyebut rencana mana yang dipakainya. Lihat **E-142** /
> [#101](../../issues/101).

> ⚠️ **Dan tangga sebelas tingkat Phase 19 adalah tangga §18.11 yang
> diperpanjang — dengan urutan KEEMPAT.** `Family/Community` dan `Country` muncul
> sebagai tingkat baru, `Industry` hilang, `Technology` dan `Environment`
> disisipkan sebagai "tingkat" padahal keduanya bukan cakupan melainkan domain.
> Empat susunan untuk satu sumbu dalam satu naskah dan penutupnya. Lihat
> **E-141** / [#130](../../issues/130).

> ⭐ **Tapi kalimat pembeda di penutup ini tepat, dan ia yang layak dibawa:**
> *"AI yang memahami manusia **dalam konteks dunia**"*. Itu perumusan yang
> membenarkan fase ini tanpa menjanjikan kendali — konsisten dengan prinsip
> pembukanya, dua puluh enam bagian sebelumnya. Dalam naskah sepanjang ini,
> pembuka dan penutup yang masih menyatakan hal yang sama adalah tanda bahwa
> rancangannya utuh.
