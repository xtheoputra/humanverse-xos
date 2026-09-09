# Peta fase — apa yang sudah tertulis, dan apa yang benar-benar tidak ada

> ⚠️ **Bukan kata pemilik.** Pengukuran atas 24 naskah, bukan usulan. Ia
> **tidak memilih peta mana yang menang** — itu tetap
> [#133](../../issues/133) dan [#139](../../issues/139).

---

## Kenapa berkas ini ada

[#142](../../issues/142) menyimpulkan bahwa *“Peta Akhir 20 Fase”* naskah 24
memuat **dua belas baris** dan bahwa **delapan baris pertama tidak ada**.
Pemeriksaannya:

```
grep -rohE "Phase [1-8] +[A-Z]{3,}" docs/  →  0
```

Angka nol itu benar, dan saya sudah memverifikasinya ulang. Tetapi pola itu
menuntut **huruf besar semua** sesudah nomor fase — bentuk kata kerja
kapabilitas (`THINK`, `PERCEIVE`). Ia **mustahil** cocok dengan
*“Phase 5: HumanVerse Research Lab”*, karena `HumanVerse` hanya berhuruf besar
satu.

⇒ Yang diukur adalah **kesesuaian FORMAT**, bukan **keberadaan**. Kalimat di
[`275`](275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md)
menulisnya dengan tepat (*“didaftar sebagai **kapabilitas**”*); judul
[#142](../../issues/142) membuang kualifikasi itu dan karenanya terbaca lebih
keras daripada yang dibuktikan.

---

## 🔴 Tujuh dari delapan baris itu SUDAH punya nama — dan sudah terkumpul

| Fase | Nama menurut naskah | Bukti |
|---|---|---|
| **1** | ❌ **tidak ada, di mana pun** | — |
| 2 | Enterprise Blueprint | [`30`](30-PHASE-2-IKHTISAR.md) `H1` |
| 3 | AI-Native Human Ecosystem | [`50`](50-NASKAH-4-IKHTISAR.md) `H1` · didahului [`46`](46-PHASE-3.md) *“Level Google DeepMind”* |
| 4 | Enterprise Operating System | [`100`](100-PHASE-4-IKHTISAR.md) `H1` |
| 5 | HumanVerse AI Research Lab | [`112`](112-PHASE-5-RESEARCH-LAB.md) `H1` |
| 6 | HumanVerse Developer Platform | [`123`](123-PHASE-6-IKHTISAR.md) `H1` |
| 7 | Data & AI Infrastructure | [`132`](132-PHASE-7-IKHTISAR.md) `H1` |
| 8 | AI Safety, Security & Privacy | [`142`](142-PHASE-8-IKHTISAR.md) `H1` |

⭐ **Dan ketujuhnya sudah terkumpul di satu tempat sejak lama:**
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) baris 17–20 memuat daftar
naskah→fase yang menamai **Phase 2 sampai Phase 20** tanpa terputus.

⇒ **Sisa pekerjaan [#142](../../issues/142) lebih kecil daripada judulnya:**
bukan *“delapan baris hilang”*, melainkan

1. **satu** baris yang benar-benar tidak ada (**Phase 1**);
2. **tujuh** kata kerja kapabilitas yang belum dipilih untuk fase yang
   **namanya sudah ada** — dan memilih kata kerja adalah pekerjaan pemilik,
   bukan pekerjaan mencari;
3. pernyataan apakah §10.41 digantikan — tetap keputusan pemilik.

---

## Tiga peta fase, bukan dua

Selama ini dicatat ada dua rencana yang bersaing (`V0–V6` lawan `Phase`).
Untuk **Phase** sendiri ada **tiga** peta, ditulis di tiga waktu berbeda:

| | Peta | Sumber | Cakupan |
|---|---|---|---|
| **A** | peta naskah 8 | [`113`](113-PETA-FASE-5-12.md) | Phase 5–12 |
| **B** | §10.41 “peta fase baru” | [`175`](175-REPO-API-DB-ROADMAP-DOD.md) L275–292 | Phase 1–15 |
| **C** | §20.36 “Peta Akhir 20 Fase” | [`275`](275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md) L124–131 | Phase 9–20 (kata kerja) |

### Peta A lawan yang benar-benar terjadi

| Fase | Peta A (naskah 8) | Yang terjadi | |
|---|---|---|---|
| 5 | HumanVerse Research Lab | HumanVerse AI Research Lab | ✅ |
| 6 | Developer Platform | HumanVerse Developer Platform | ✅ |
| 7 | Data & AI Infrastructure | Data & AI Infrastructure | ✅ |
| 8 | AI Safety & Ethics Framework | AI Safety, Security & Privacy | ✅ |
| 9 | **Enterprise & Business Platform** | Human Intelligence & Cognitive Architecture | ❌ |
| 10 | **AI Automation Engine** | Multimodal Intelligence & Perception | ❌ |
| 11 | **HumanVerse Cloud** | Agentic Intelligence & Agency Layer | ❌ |
| 12 | **Blueprint Implementation** | Digital Twin & World Simulation | ❌ |

**4 dari 8 — dan tepat empat yang TERDEKAT.**
(Nasib keempat blok yang tergusur sudah dicatat di **E-86**,
[`175`](175-REPO-API-DB-ROADMAP-DOD.md) L308–315.)

### Peta B lawan yang benar-benar terjadi

Naskah 14 menulis peta B ketika Phase 2–10 sudah ada, jadi ia meramalkan
**lima** fase:

| Fase | Peta B (§10.41) | Yang terjadi | |
|---|---|---|---|
| 11 | Autonomous Agent & Agency Layer | Agentic Intelligence & Agency Layer | ✅ |
| 12 | Digital Twin & World Simulation | Digital Twin & World Simulation | ✅ |
| 13 | HumanOS | HumanOS — Personal AI Operating System | ✅ |
| 14 | Ecosystem & Marketplace | Autonomous Intelligence & Collective Agent Ecosystem | ⚠️ sebagian |
| 15 | **Global Intelligence Platform** | Spatial Intelligence & XR Universe | ❌ |

**3 tepat · 1 sebagian · 1 meleset — dan yang meleset adalah yang TERJAUH.**
(*Global Intelligence* akhirnya muncul, tetapi sebagai **Phase 18**.)

---

## ⭐ Yang diukur dari kedua peta: **jangkauan andal ± 3–4 fase**

| Peta | Fase yang diramalkan | Tepat | Pola kesalahan |
|---|---|---|---|
| A (naskah 8) | 8 | **4** | empat terdekat benar, empat terjauh salah |
| B (§10.41) | 5 | **3** (+1 sebagian) | yang terjauh salah |

Dua peta, ditulis enam naskah berjarak, **gagal dengan cara yang sama**: benar
untuk fase-fase terdekat, meleset di ujung.

> 💡 **Ini bukan alasan untuk tidak membuat peta** — dua peta itu benar untuk
> 7 dari 13 ramalan, dan yang benar adalah yang dipakai orang. Ini alasan untuk
> **tidak menggantungkan keputusan pada baris terjauh sebuah peta.**

🛑 **Dan satu akibat langsung untuk [#133](../../issues/133):** satu-satunya
klaim yang pernah dibuat tentang **UJUNG** peta — §10.41 *“lima belas fase”* —
adalah persis klaim yang meleset. Naskah 23 kini menyatakan **Phase 20 sebagai
yang terakhir**. Riwayat tidak membantahnya (ujungnya sudah tercapai, bukan
diramalkan), tetapi riwayat juga menunjukkan **pernyataan ujung adalah jenis
pernyataan yang sudah pernah gagal satu kali.**

---

## 🔴🔴 Permintaan yang sama sudah diajukan pemilik **tiga kali**

Ini belum pernah dicatat sebagai deret. Ditelusuri dari penutup tiap naskah:

| # | Kapan | Yang diminta | Nasib |
|---|---|---|---|
| 1 | naskah 4 → [`77`](77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md) | **Blueprint Engineering v1.0** | ✅ **dikerjakan** — naskah 5, berkas `80`–`96` |
| 2 | naskah 5 → [`97`](97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md) | **Engineering Specification v1.0** | ✅ **dikerjakan** — [`../spec/`](../spec/README.md), 8 berkas |
| 3 | naskah 8 → [`113`](113-PETA-FASE-5-12.md) L110 | **Phase 12 “Blueprint Implementation”**, 100+ dokumen — *“ini yang paling besar”*: ERD 100+ tabel · API 500+ endpoint · Event Schema · Agent Contracts · MCP Registry · Sprint Backlog · CI/CD · Docker & Kubernetes | ❌ **digantikan** — §10.41 memberi Phase 12 kepada *Digital Twin*; ditandai *“hilang”* di [`175`](175-REPO-API-DB-ROADMAP-DOD.md) L315 |
| 4 | naskah 18 penutup → [`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) L667 | **arsitektur teknis Phase 14**: protocol spec · agent message schema · federation protocol · security model · delegation model · consensus · **database schema · API contract · event schema · repository · Docker/Kubernetes topology · sprint-by-sprint** | ❌ **tidak pernah dimulai** — enam naskah datang sesudahnya |
| 5 | naskah 24 penutup → [`275`](275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md) L166 | **Master Architecture v2.0**: monorepo final · event contracts · agent contracts · deployment topology · data architecture · **V0 → production** | ⏳ [#139](../../issues/139) |

### Empat butir muncul UTUH di ketiganya — tiga lagi di dua dari tiga

Dibandingkan kata demi kata, bukan kesan:

| Butir | #3 naskah 8 | #4 naskah 18 | #5 naskah 24 |
|---|---|---|---|
| skema basis data / data architecture | ✅ *ERD lengkap (100+ tabel)* | ✅ *database schema* | ✅ *data architecture* |
| skema / kontrak event | ✅ *Event Schema* | ✅ *event schema* | ✅ *event contracts* |
| Docker/Kubernetes · deployment topology | ✅ *Docker & Kubernetes Manifest* | ✅ *Docker/Kubernetes topology* | ✅ *deployment topology* |
| urutan implementasi | ✅ *Sprint Backlog* | ✅ *sprint-by-sprint* | ✅ *V0 → production* |
| kontrak agent | ✅ *Agent Contracts* | ⚠️ *agent message schema* — pesan, bukan kontrak | ✅ *agent contracts* |
| kontrak API | ✅ *API 500+ endpoint* | ✅ *API contract* | ❌ **tidak disebut** |
| struktur repositori / monorepo | ❌ **tidak disebut** | ✅ *repository* | ✅ *monorepo final* |

⚠️ **Dua sel ❌ itu sengaja tidak dibulatkan.** Naskah 8 tidak pernah menyebut
struktur repositori, dan naskah 24 tidak pernah menyebut kontrak API — jadi
klaimnya **empat butir utuh**, bukan tujuh. Kalau ketiganya digabung nanti,
dua celah itu yang harus diisi dari tempat lain
([`../spec/04`](../spec/04-API-CONTRACTS.md) sudah punya kontrak API untuk V0).

> 🛑 **Dua permintaan pertama dikerjakan; tiga terakhir tidak — dan ketiganya
> meminta empat hal yang persis sama.**
>
> Bedanya bukan isi permintaan, melainkan **apa yang datang sesudahnya**.
> Permintaan 1 dan 2 dijawab sebelum naskah berikutnya tiba. Permintaan 3
> tergusur oleh peta fase baru; permintaan 4 tergusur oleh enam naskah.
>
> ⭐ Dan naskah 18 sendiri sudah mencatat bahwa pekerjaan itu **bisa dimulai
> tanpa keputusan baru** ([`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) L682).
> Enam naskah kemudian ia belum dimulai.

💡 **Pelajaran yang bisa dipakai ulang:** kalau sebuah permintaan sudah muncul
**tiga kali dengan isi yang sama**, yang perlu diperiksa bukan lagi apakah ia
penting, melainkan **apa yang secara berulang mendahuluinya.**

---

## Yang berkas ini **tidak** putuskan

Tidak memilih peta, tidak menamai Phase 1, tidak menetapkan kata kerja untuk
Phase 2–8, dan tidak menyatakan §10.41 digantikan. Keempatnya tetap milik
[#133](../../issues/133) · [#142](../../issues/142) · [#139](../../issues/139).

Yang berubah hanya ukurannya: sisa [#142](../../issues/142) adalah **satu nama
dan tujuh kata kerja**, bukan delapan baris kosong.
