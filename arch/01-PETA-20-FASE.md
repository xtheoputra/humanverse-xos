# 01 — Peta 20 Fase, versi 3

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menutup [#142](../../issues/142) (**E-148**) dan sisa
> [#133](../../issues/133) (**A-34**). Menjawab [#132](../../issues/132)
> (*“roadmap 20 fase” yang dirujuk naskah 23 tidak pernah ada*) dengan
> **membuatnya ada**.

---

## §1 Peta fase punya versi sekarang

Repo ini punya **tiga** peta fase yang ditulis di tiga waktu, dan tak satu pun
menyebut pendahulunya. Itu yang melahirkan
[#101](../../issues/101), [#108](../../issues/108), [#132](../../issues/132),
dan [#133](../../issues/133).

| Versi | Sumber | Cakupan | Status |
|---|---|---|---|
| **v1** | §10.41 · [`../docs/175`](../docs/175-REPO-API-DB-ROADMAP-DOD.md) L275–292 | Phase 1–15 | 🛑 **DIGANTIKAN** — Phase 15 ternyata SpatialOS, bukan *Global Intelligence Platform* |
| **v2** | naskah 19–22, terbuka-ujung | tak berujung | 🛑 **DIGANTIKAN** — peta tanpa ujung melahirkan rujukan ke rencana yang tak bisa dibuka |
| **v3** | **berkas ini** | Phase 1–20, **tertutup** | ✅ berlaku |

🔧 **Aturan yang menyertainya:** peta fase **selalu bernomor versi**, sama
seperti `scoring_version` di DDL. Peta baru **wajib** menyebut versi yang
digantikannya dan alasannya di baris pertama. Tanpa aturan itu, *“roadmap yang
sudah kita tetapkan sebelumnya”* tidak punya rujukan — dan itu persis yang
terjadi di naskah 23.

> ⚠️ **Riwayat memberi ukuran, dan ukurannya tidak menyenangkan.** Peta A
> (naskah 8) benar **4 dari 8**; peta B (§10.41) benar **3 dari 5**. Keduanya
> gagal dengan cara yang sama: **benar untuk fase terdekat, meleset di ujung**
> ([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)).
> ⇒ **Jangkauan andal ± 3–4 fase.** v3 berbeda dari keduanya dalam satu hal
> yang menentukan: ia **tidak meramalkan apa pun**. Kedua puluh fasenya sudah
> ditulis; berkas ini mencatat, bukan memperkirakan.

---

## §2 Kedua puluh fase, satu daftar

| Phase | Nama | Kata kerja | Naskah | Berkas |
|---|---|---|---|---|
| **1** | 🛑 **belum dinamai** — lihat §3 | — | 1–2 | [`01`](../docs/01-VISI.md)–[`22`](../docs/22-PAKET-DOKUMENTASI.md) |
| 2 | Enterprise Blueprint | **STRUCTURE** 🔧 | 3 | [`30`](../docs/30-PHASE-2-IKHTISAR.md)–`46` |
| 3 | AI-Native Human Ecosystem | **CONNECT** 🔧 | 4 | [`50`](../docs/50-NASKAH-4-IKHTISAR.md)–`77` |
| 4 | Enterprise Operating System | **STANDARDISE** 🔧 | 7 | [`100`](../docs/100-PHASE-4-IKHTISAR.md)–`112` |
| 5 | HumanVerse AI Research Lab | **RESEARCH** 🔧 | 9 | [`112`](../docs/112-PHASE-5-RESEARCH-LAB.md)–`122` |
| 6 | HumanVerse Developer Platform | **EXTEND** 🔧 | 10 | [`123`](../docs/123-PHASE-6-IKHTISAR.md)–`131` |
| 7 | Data & AI Infrastructure | **STORE** 🔧 | 11 | [`132`](../docs/132-PHASE-7-IKHTISAR.md)–`141` |
| 8 | AI Safety, Security & Privacy | **PROTECT** 🔧 | 12 | [`142`](../docs/142-PHASE-8-IKHTISAR.md)–`153` |
| 9 | Human Intelligence & Cognitive Architecture | **THINK** | 13 | `154`–`164` |
| 10 | Multimodal Intelligence & Perception | **PERCEIVE** | 14 | `165`–`175` |
| 11 | Agentic Intelligence & Agency Layer | **ACT** | 15 | `176`–`187` |
| 12 | Digital Twin & World Simulation | **SIMULATE** | 16 | `188`–`197` |
| 13 | HumanOS — Personal AI Operating System | **OPERATE** | 17 | `198`–`206` |
| 14 | Autonomous Intelligence & Collective Agent Ecosystem | **COLLABORATE** | 18 | `207`–`218` |
| 15 | Spatial Intelligence & XR Universe | **UNDERSTAND SPACE** | 19 | `219`–`227` |
| 16 | Robotics & Embodied Intelligence | **EMBODY** | 20 | `228`–`235` |
| 17 | Health & Bio Intelligence | **UNDERSTAND BIOLOGY** | 21 | `236`–`245` |
| 18 | Global Intelligence Network | **UNDERSTAND THE WORLD** | 22 | `246`–`255` |
| 19 | Scientific Discovery Engine | **DISCOVER KNOWLEDGE** | 23 | `256`–`265` |
| 20 | Civilization Platform | **COORDINATE CIVILIZATION** | 24 | [`266`](../docs/266-PHASE-20-POSITIONING-CORE-PRINCIPLE-DAN-ARSITEKTUR.md)–[`275`](../docs/275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md) |

**Sumber tiap kolom:**
nama Phase 2–8 dari judul `H1` naskahnya sendiri
([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)) ·
kata kerja Phase 9–20 dari §20.36 ·
kata kerja Phase 2–8 dari
[K-6](../docs/KEPUTUSAN-DIDELEGASIKAN.md) 🔧 ·
pemetaan naskah→fase dari
[`../docs/00-DAFTAR-ISI.md`](../docs/00-DAFTAR-ISI.md).

⚠️ **Empat naskah tidak memetakan ke fase mana pun**, dan itu bukan kelalaian:
naskah **5** (Blueprint Engineering + spesifikasi V0), **6** (peta 14 lapisan
engineering), **8** (peta fase 5–12), dan sebagian naskah **2**. Keempatnya
menulis **tentang** rencana, bukan **satu** fase. Lihat §3.

---

## §3 🔴 Phase 1 — celahnya lebih kecil daripada yang tercatat, dan bentuknya berbeda

[K-6](../docs/KEPUTUSAN-DIDELEGASIKAN.md) menolak mengarang nama untuk Phase 1,
dan penolakan itu tetap berlaku. Tetapi ada satu hal yang bisa **diukur** dan
belum pernah ditulis:

> 🔑 **Penomoran fase dimulai di naskah 3, bukan di naskah 1.**
> [`../docs/00-DAFTAR-ISI.md`](../docs/00-DAFTAR-ISI.md) memetakan naskah 3 →
> **Phase 2**. Maka apa pun isi Phase 1, ia adalah **yang ditulis sebelum
> naskah 3** — yaitu naskah **1 dan 2**, berkas [`01`](../docs/01-VISI.md)–`22`.

Isinya bisa dibaca dari daftar isi tanpa menebak: visi · **12 modul manusia** ·
Human Intelligence Graph · hierarki agent 3 lapis · Digital Twin · memory ·
event-driven · basis data · DevOps · evaluasi. Itu **platform dasarnya sendiri**
— dan **V0 adalah irisan pertamanya yang bisa dirilis**.

| Yang berubah | Sebelum | Sesudah |
|---|---|---|
| bentuk celah | *“satu baris peta hilang”* | **isinya sudah ada dan bisa ditunjuk; yang hilang cuma LABELNYA** |
| yang harus dikerjakan | mencari | pemilik menuliskan **satu nama + satu kata kerja** |

🛑 **Nama dan kata kerjanya tetap milik pemilik.** Menuliskannya di sini akan
mengubah pengukuran menjadi tebakan — dan celah yang jujur lebih berguna
daripada peta yang genap.

---

## §4 Dua rencana, dua sumbu — dan keduanya benar

**Menutup [#72](../../issues/72) (E-87 / H-13).**

Sejak naskah 14, `V0–V6` tidak disebut lagi sementara peta fase terus tumbuh.
Itu dibaca sebagai *“rencana kanonik kembali jadi Phase”*, dan dicatat sebagai
butir H **ketiga** yang tergerus.

🔧 **Pemeriksaan ulang menunjukkan keduanya tidak pernah bersaing — mereka
mengukur besaran yang berbeda:**

| | `Phase 1–20` | `V0–V6` |
|---|---|---|
| menjawab | **urutan arsitektur DITULIS** | **urutan produk DIRILIS** |
| satuannya | naskah | rilis yang bisa dipakai orang |
| siapa yang membacanya | perancang | pengguna & yang menjadwalkan |
| berapa banyak | 20 | 7 |
| sudah selesai? | ✅ **20 dari 20 ditulis** | ❌ **0 dari 7 dirilis** |

> 💡 **Pertanyaan yang menyelesaikannya sama dengan yang menyelesaikan delapan
> sensus:** *“yang dihitung ini apa?”* — `Phase` menghitung **dokumen**, `V`
> menghitung **rilis**. Dua besaran berbeda tidak bisa saling menggantikan, dan
> tidak perlu salah satu dibuang.

### Pemetaan — fase mana memberi isi ke rilis mana

| Rilis | Isi | Fase yang memberinya isi |
|---|---|---|
| **V0** Foundation | auth · profil · goals · habits · mood · jurnal · AI coach · memory · dashboard | **Phase 1** (dasar) — [`../spec/`](../spec/README.md) |
| **V1** Behavior Intelligence | event · analitik · pola · prediksi · weekly review | Phase 1 · **9** (THINK) |
| **V2** Lifestyle AI | fashion · wardrobe · trend · grooming · fitness · nutrisi | Phase 2–3 |
| **V3** Multi-Agent Platform | registry · SDK · MCP · tool registry · evaluation | Phase 4 · **6** · **11** (ACT) |
| **V4** Digital Twin | human state · model perilaku · simulasi · decision lab | **12** (SIMULATE) |
| **V5** HumanOS | voice · vision · wearable · on-device AI · privasi lanjut | **10** (PERCEIVE) · **13** (OPERATE) |
| **V6** HumanVerse Ecosystem | developer SDK · marketplace · enterprise API | **6** · **14** (COLLABORATE) |
| — | — | 🛑 **Phase 5 · 7 · 8 · 15–20 belum punya rilis** |

🛑 **Sembilan fase tidak muncul di kolom mana pun, dan itu temuan, bukan
kelalaian tabel.** Phase 15–20 (SpatialOS · Robotics · Health · Global ·
Science · Civilization) berada **di luar seluruh tangga versi yang pernah
ditulis**. Tangga `V` dibuat di naskah 4, ketika petanya masih 12 fase.

⇒ **Dua akibat langsung:**

1. **Phase 8 (PROTECT) tidak boleh menunggu rilis.** Ia keamanan; menaruhnya di
   `V7` mengulang pola yang sudah dicatat lima kali (*keselamatan dijadwalkan
   sesudah yang dijaganya* — [#116](../../issues/116) · [#121](../../issues/121)
   · [#131](../../issues/131) · [#111](../../issues/111) · [#99](../../issues/99)).
   Penyelesaiannya di [`10`](10-URUTAN-IMPLEMENTASI.md) §3: **Phase 8 bukan
   rilis, ia syarat tiap rilis.**
2. **Phase 15–20 menuntut tangga `V` diperpanjang — dan itu keputusan pemilik**
   (cakupan produk). Yang bisa dinyatakan tanpa memutuskannya: **tidak ada
   rilis yang boleh memuat Phase 16 atau 17 sebelum Phase 8 punya penegak**
   ([`11`](11-PENEGAKAN.md)), sebab keduanya menyentuh badan orang.

⚠️ **`V1–V5` juga pernah berarti tiga hal berbeda** (lingkup produk · kematangan
arsitektur · kematangan data). [K-11](../docs/KEPUTUSAN-DIDELEGASIKAN.md) sudah
memisahkannya: `V0–V6` **hanya** lingkup produk; arsitektur `ARCH1–ARCH4`;
infrastruktur data `INFRA1–INFRA5`.

---

## §5 Apa yang dibawa tiap fase — supaya “menyatukan” punya isi

Kolom terakhir adalah yang membuat berkas ini bisa dipakai
[`03`](03-MONOREPO-FINAL.md), [`06`](06-DATA-ARCHITECTURE.md), dan
[`08`](08-AGENT-CONTRACTS.md): **tiap fase menambahkan pohon, tabel, dan event,
dan jumlahnya sudah diukur.**

| Phase | Pohon repo yang diperkenalkan | Σ | Tabel | Event PascalCase |
|---|---|---|---|---|
| 1 | `HumanVerse-X/` (43 subdir) | 1 | — | 7 ⁽¹⁾ |
| 2 | `agent-os/` · `tools/` · `prompts/` · `humanverse-sdk/` | 4 | — | — |
| 3 | `humanverse-core/` | 1 | — | — |
| **—** | ⚠️ **naskah 5** — `humanverse-x/` (85 subdir) | 1 | 4 + **19 (V0)** | ✅ **21 sesuai format** |
| 4 | `prompts/` · `docs/` | 2 | — | — |
| 5 | `research/` ×2 · `benchmarks/` | 3 | — | — |
| 6 | `portal/` · `sdk/` · `agent-sdk/` · `docs/` · `developer-platform/` | 5 | — | — |
| 7 | `events/` · `data-lake/` · `data-platform/` | 3 | 8 | — |
| 8 | `security/` (37 subdir) | 1 | 24 | 1 |
| 9 | `cognitive-runtime/` · `intelligence/` (67 subdir) | 2 | — | — |
| 10 | `multimodal/` | 1 | 16 | 14 |
| 11 | `agents/` (28 subdir) | 1 | 18 | 22 |
| 12 | `simulation-lab/` + **tujuh akar sekaligus** | 2 | 26 | — |
| 13 | `human-os/` — **dua pohon berbeda di satu naskah** | 2 | — | 15 |
| 14 | `humanverse/` | 1 | 27 | 16 |
| 15 | `spatial-os/` | 1 | 18 | 13 |
| 16 | `robotics-platform/` · `robotics/` — **dua pohon berbeda** | 2 | 17 | 13 |
| 17 | `health-bio/` (46 subdir) · `health-bio/research/` | 2 | 24 | 15 |
| 18 | `global-intelligence/` | 1 | 30 | 14 |
| 19 | `scientific-discovery/` | 1 | 17 | — |
| 20 | `civilization-platform/` | 1 | 22 | 12 |
| | **424 nama direktori unik** | **38** | **247 nama unik** | **133 nama unik** |

⁽¹⁾ ditulis **sebelum** [#38](../../issues/38) memilih format — asal-usul, bukan
pelanggaran. Lima dari tujuh **hanya** ada di berkas itu, jadi 133 − 5 = **128
nama ditulis dalam format yang ditolak sesudah keputusan**.

> ⚠️ **Kolom tabel dan event TIDAK BOLEH DIJUMLAHKAN ke bawah.** Jumlah kolom
> tabel = 270 sebutan, tetapi himpunannya **247**; jumlah kolom event = 142
> sebutan, himpunannya **133**. Selisihnya adalah nama yang muncul di lebih dari
> satu fase — yaitu justru **masalah** yang [`06`](06-DATA-ARCHITECTURE.md) dan
> [`07`](07-EVENT-CONTRACTS.md) selesaikan.
> 💡 Ini pelajaran repo ini sendiri, dipakai pada tabelnya sendiri:
> **kejadian ≠ jumlah ≠ himpunan.**

> 🔑 **Baris tanpa nomor fase itu penting.** Pohon `humanverse-x/` — **yang
> paling besar (85 subdir) dan satu-satunya yang ditunjuk Sprint 0 tugas 0.1**
> ([`../spec/07`](../spec/07-BACKLOG-V0.md)) — ditulis di naskah 5, yang tidak
> memetakan ke fase mana pun. Ia bukan pohon sebuah fase; ia pohon **blueprint
> engineering**. Itu sebabnya [`03`](03-MONOREPO-FINAL.md) memakainya sebagai
> **titik awal**, bukan sebagai salah satu dari 38.

> 🛑 **Kolom pertama adalah seluruh soal “menghapus overlap”:** dua puluh fase
> memperkenalkan **38 pohon tingkat-atas**, dan **128 nama direktori dipakai
> lebih dari satu pohon**. Diselesaikan di [`03`](03-MONOREPO-FINAL.md).
> **Kolom kedua** diselesaikan di [`06`](06-DATA-ARCHITECTURE.md), **kolom
> ketiga** di [`07`](07-EVENT-CONTRACTS.md).

---

## §6 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Baris di §2 | **20**, bernomor 1–20 tanpa lompatan |
| Fase dengan nama | **19** — Phase 1 sengaja kosong |
| Fase dengan kata kerja | **19** — Phase 1 sengaja kosong |
| Kata kerja ganda | **NIHIL** — `OPERATE` (P13) ≠ `STANDARDISE` (P4) |
| Naskah yang tidak memetakan ke fase | **4** — naskah 2 (sebagian) · 5 · 6 · 8, seluruhnya menulis *tentang* rencana |
| Σ kolom pohon §5 | **38** — cocok dengan [`SENSUS-MODUL.md`](../docs/SENSUS-MODUL.md) Tabel A |
| Kolom tabel & event §5 dijumlahkan ke bawah | ❌ **dilarang** — 270 sebutan lawan 247 himpunan; 142 lawan 133 |
| Fase tanpa rilis `V` | **9** — Phase 5 · 7 · 8 · 15–20 |
| Peta ini menyebut versi yang digantikannya | ✅ §1 |
