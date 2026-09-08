# HumanVerse XOS

> **AI-Native Human Development Platform**
> **One AI. Infinite Human Growth.**
> `Observe → Understand → Reason → Predict → Recommend → Act → Learn`

Bukan aplikasi *habit tracker* biasa. Seluruh domain kehidupan dihubungkan
menjadi satu **Human Knowledge Graph**, lalu di atasnya berdiri **AgentOS**,
**Memory Hierarchy**, **Context Engine**, **Behavior Engine**, **Decision
Engine**, dan **Digital Twin** — sebuah platform yang punya **runtime untuk
manusia + agent + data + knowledge + simulation + automation**.

> ✅ **Nama resmi diputuskan 3 September 2026: `HumanVerse XOS`.**
> Berkas naskah `01`–`77` tetap menulis nama versi masing-masing naskah
> (*HumanOS*, *HumanVerse X*) apa adanya. Lihat [`docs/10-IDENTITAS.md`](docs/10-IDENTITAS.md).

---

## Status proyek

| Hal | Keadaan |
|---|---|
| Tahap | **Spesifikasi engineering siap** — belum ada kode (disengaja) |
| Berkas kode | 0 |
| Repo git | privat `xtheoputra/humanverse-xos`, branch `master` |
| Dokumen | **243 berkas** di `docs/` (naskah + audit + catatan sesi) + **8 berkas** di `spec/` |
| Naskah pemilik | **22** — terakhir: **Phase 18 Global Intelligence Network** (34 bagian) |
| Keputusan tertutup | **24 butir H** — nama · MVP · struktur repo · ambang konfirmasi · model memory · memory meluruh · gerbang policy · context package · peta 15 fase · dua tangga R/L · manifest dipulihkan · **model transisi belajar dari galat sendiri** · **monetisasi punya fase (Phase 14)**. 🛑 **H-20 PATAH, dan petanya TERBUKA-UJUNG** — **empat naskah berturut-turut masing-masing menambah satu fase** di kalimat penutupnya: naskah 19 → **Phase 16**, naskah 20 → **Phase 17**, naskah 21 → **Phase 18**, naskah 22 → **Phase 19 Civilization Intelligence** ([#101](../../issues/101), [#108](../../issues/108)). ⚠️ **H-13** ([#72](../../issues/72)) dan **H-11** ([#78](../../issues/78)) juga perlu ditinjau ulang |
| Keputusan terbuka | **24 pertanyaan A** · **142 ketidakcocokan E** · **17 lubang G** |
| Tanggal dokumen | 8 September 2026 |

> ⚠️ **Nol baris kode itu disengaja — dan penghambatnya terus berkurang.**
> Lima naskah sudah menjawab: **nama** (A-7), **MVP** (A-2), **struktur repo**
> (E-27), **Weather/Calendar = tool** (E-2/E-28), **empat penyimpanan bukan
> enam** (A-10), **V0–V6 sebagai rencana kanonik** (A-18), dan **Confidence
> Layer** untuk angka taksiran (B-15/B-1).
>
> ✅ **TIDAK ADA yang mengunci Engineering Spec.** Daftar "empat penghambat" di
> versi lama README ini **salah**, dan [`spec/README.md`](spec/README.md) sudah
> membantahnya sejak awal — lengkap dengan cara tiap butir ditangani di DDL:
> **#32** skala skor → `numeric(4,3) CHECK BETWEEN 0 AND 1` + `scoring_version` ·
> **#2** model angka → `metrics jsonb` + `model_version` (enam model boleh
> hidup berdampingan, tanpa migrasi) · **#7** model graf → **tidak menyentuh V0**,
> Neo4j baru di V2 · **#33** memory → **sudah ditutup** (`kind` + `scope`, plus
> `tier` dari H-16).
>
> 🛑 **Penghambat V0 yang sebenarnya cuma dua, dan keduanya bukan soal skema:**
> **[#3](../../issues/3)** (siapa mengerjakan 12 fitur dalam 4–6 minggu) dan
> **[#20](../../issues/20)** (cek merek, domain, nama paket).
>
> 🔑 Rekonsiliasi lengkap kedua dokumen ada di
> [`docs/GERBANG-SKEMA.md`](docs/GERBANG-SKEMA.md).

---

## 📌 Pekerjaan terbuka = GitHub Issues

**130 issue** dalam 3 milestone — **20 ditutup**. Baca issue-nya, jangan analisis
ulang naskahnya.

| Milestone | Isi | Issue |
|---|---|---|
| **M1 — Keputusan sebelum kode** | 27 terbuka, 5 ditutup | [#1](../../issues/1)–[#9](../../issues/9), [#38](../../issues/38), [#58](../../issues/58)–[#59](../../issues/59), [#72](../../issues/72), [#80](../../issues/80), [#90](../../issues/90)–[#93](../../issues/93), [#98](../../issues/98)–[#101](../../issues/101), [#103](../../issues/103), [#105](../../issues/105), [#108](../../issues/108), [#111](../../issues/111)–[#113](../../issues/113) |
| **M2 — Blueprint & Platform** | 58 terbuka, 13 ditutup | [#10](../../issues/10)–[#19](../../issues/19), [#26](../../issues/26)–[#37](../../issues/37), [#39](../../issues/39), [#41](../../issues/41)–[#45](../../issues/45), [#47](../../issues/47)–[#49](../../issues/49), [#51](../../issues/51), [#54](../../issues/54)–[#56](../../issues/56), [#60](../../issues/60)–[#70](../../issues/70), [#73](../../issues/73)–[#74](../../issues/74), [#77](../../issues/77)–[#79](../../issues/79), [#82](../../issues/82)–[#84](../../issues/84), [#87](../../issues/87)–[#89](../../issues/89), [#94](../../issues/94), [#96](../../issues/96)–[#97](../../issues/97), [#106](../../issues/106)–[#107](../../issues/107), [#109](../../issues/109)–[#110](../../issues/110) |
| **M3 — Sebelum ada pengguna nyata** | 25 terbuka, 2 ditutup | [#20](../../issues/20)–[#25](../../issues/25), [#40](../../issues/40), [#46](../../issues/46), [#50](../../issues/50), [#52](../../issues/52)–[#53](../../issues/53), [#57](../../issues/57), [#71](../../issues/71), [#75](../../issues/75)–[#76](../../issues/76), [#81](../../issues/81), [#85](../../issues/85)–[#86](../../issues/86), [#95](../../issues/95), [#102](../../issues/102), [#104](../../issues/104), [#114](../../issues/114) |

⚠️ **[#55](../../issues/55) meninjau ulang keputusan yang sudah ditutup:**
monorepo final (H-10) kini tergerus **delapan kali** — tiga pohon dari naskah
9/10/11, **enam** dari naskah 18, **`spatial-os/`** (naskah 19), **`robotics/`**
(naskah 20), **`health-bio/`** (naskah 21, [#120](../../issues/120)), dan
**`global-intelligence/`** (naskah 22, [#129](../../issues/129)) — sehingga pohon
keamanan menjadi **sembilan** (`security/` · `agent-security/` ·
`spatial-os/safety/` · `spatial-os/privacy/` · `robotics/safety/` ·
`health-bio/safety/` · `health-bio/privacy/` · `global-intelligence/security/` ·
`global-intelligence/privacy/`) dan aturan impor §8.42 tidak lagi bisa dinyatakan.
**Sepuluh naskah berturut-turut menyentuh struktur repo.** ⭐ `governance/`
akhirnya muncul di naskah 22 — tetapi **di dalam pohon fase**, sehingga ia tidak
bisa mengatur `robotics/`, `health-bio/`, maupun `agents/`.
🛑 Naskah 20 bahkan memberi struktur repo **dua kali di dalam satu naskah**
([#109](../../issues/109)).
Sprint 0 tugas 0.1 menunggu jawabannya.

✅ **Ditutup:** [#1](../../issues/1) rencana kanonik → V0–V6 ·
[#8](../../issues/8) struktur repo · [#12](../../issues/12) Weather/Calendar = tool ·
[#17](../../issues/17) empat penyimpanan · [#10](../../issues/10) blueprint ·
[#31](../../issues/31) Engineering Specification · [#38](../../issues/38) nama event dua segmen ·
[#5](../../issues/5) ambang konfirmasi → **otomatis sampai R2, konfirmasi mulai R3** ·
[#52](../../issues/52) `risk_level` kembali & konfirmasi pindah ke Policy Engine ·
[#33](../../issues/33) memory = **tiga sumbu** `kind`/`scope`/`tier` ·
[#50](../../issues/50) Identity Memory **meluruh**, tidak permanen ·
[#42](../../issues/42) `POLICY_CHECK` masuk rantai percakapan ·
[#62](../../issues/62) agent tidak mengambil data — **context package** ·
[#66](../../issues/66) peta fase **diganti**: 12 → **15 fase**, Agency→P11, Digital Twin→P12,
Marketplace→P14 ·
[#67](../../issues/67) **dua tangga dipisahkan** — `risk_level: R1` + `autonomy.max_level: L2` ·
[#61](../../issues/61) manifest memulihkan `purpose` + `memory.read`/`write` ·
[#70](../../issues/70) model transisi punya sumber — **galat prediksinya sendiri**.

🛑 **Penghambat V0 yang tersisa — tiga:**
[#3](../../issues/3) 12 fitur & 7 sprint dalam 4–6 minggu ·
[#20](../../issues/20) cek merek ·
🆕 [#59](../../issues/59) **`consents.purpose` + `model_training` harus ada sebelum baris data
pertama** — §8.10 melarang memakai data di luar tujuan pemberiannya, jadi data V0 yang tidak
pernah menanyakannya **tidak bisa melatih model apa pun di Phase 5**. Biayanya nol sekarang,
hampir mustahil nanti.
*(#38 format nama event ✅ ditutup naskah 10 — dua segmen. #5 ambang konfirmasi ✅ ditutup
naskah 12 — R3 ke atas.)*
Yang masih menunggu jawaban tapi tidak menahan Sprint 0–4:
[#2](../../issues/2) model angka pengguna (menahan Sprint 5) ·
[#21](../../issues/21) eskalasi krisis Journal (menahan rilis ke orang lain — dan naskah 12
lewat tanpa menyebut jurnal sekali pun) ·
[#58](../../issues/58) berapa banyak Fase 8 & 9 masuk V0 (punya default aman: pakai 23 tabel yang
sudah ada) ·
🆕 [#67](../../issues/67) **dua tangga 0–4 yang terbalik di ujung atas** — otonomi “Level 4”
(bertindak sendiri) vs risiko “R4” (wajib konfirmasi); belum mengikat V0 karena tidak ada tool
di atas level 2, tapi harus diselesaikan sebelum tangga mana pun masuk basis data ·
🆕 [#72](../../issues/72) **rencana kanonik: V0–V6 atau Phase 1–15?** Naskah 13 & 14 tidak
menyebut tangga V sama sekali, dan **V0 tidak punya tempat di daftar 15 fase** — padahal V0
satu-satunya lingkup tertutup yang pernah ditetapkan. Ini H ketiga yang tergerus ·
[#75](../../issues/75) pemantauan berkelanjutan di dalam rumah — izin `Always`; belum mengikat V0
(tidak ada kamera), tapi on-device (§10.28) harus mendahului Vision ·
[#80](../../issues/80) V0 reaktif atau proaktif? — jawaban aman: **V0 reaktif** ·
🆕 [#86](../../issues/86) **sampai horizon berapa proyeksi boleh ditampilkan?** §12.13 memberi
sampai **5 tahun**, dan horizon 3–5 tahun **tidak pernah masuk loop belajar** — satu-satunya
keluaran yang tidak bisa dikalibrasi ·
🆕 [#85](../../issues/85) **proyeksi masa depan = kelas data baru** yang paling diinginkan pihak
ketiga; dan §12.22 memakai bobot utilitas yang **disimpulkan** untuk **memaksimalkan**, bukan
lagi membandingkan.

---

## 🔧 Engineering Specification v1.0 — [`spec/`](spec/README.md)

Lapisan **04** dari peta 14 lapisan naskah 6, dikerjakan penuh. **Bukan kata
pemilik** — sengaja di luar `docs/` supaya berkas naskah tetap murni.

| Berkas | Isi |
|---|---|
| [`spec/01-DATABASE-SCHEMA.md`](spec/01-DATABASE-SCHEMA.md) | DDL PostgreSQL — **23 tabel**, tipe, PK, FK, index, constraint, prosedur hapus akun |
| [`spec/02-ERD.md`](spec/02-ERD.md) | Relasi + 6 aturan kepemilikan data |
| [`spec/03-EVENT-CONTRACTS.md`](spec/03-EVENT-CONTRACTS.md) | Envelope, **versi · urutan · idempotensi**, 22 event, consumer |
| [`spec/04-API-CONTRACTS.md`](spec/04-API-CONTRACTS.md) | Endpoint REST V0 + Privacy Center |
| [`spec/05-AGENT-CONTRACTS.md`](spec/05-AGENT-CONTRACTS.md) | Manifest schema (6 aturan validasi), tool registry, risk gate |
| [`spec/06-MODULE-BOUNDARIES.md`](spec/06-MODULE-BOUNDARIES.md) | Batas modul + 6 aturan yang **ditegakkan CI** |
| [`spec/07-BACKLOG-V0.md`](spec/07-BACKLOG-V0.md) | **51 tugas** dalam 7 sprint, siap diberikan ke AI coding agent |

**Tiga issue pengunci ternyata tidak perlu diputuskan sekarang** — skemanya
menampung kedua kemungkinan tanpa biaya:

| Issue | Cara ditangani |
|---|---|
| [#33](../../issues/33) memory: jenis atau scope | **keduanya** — `kind` untuk pengambilan, `scope` untuk izin |
| [#32](../../issues/32) tiga skala skor | simpan **0–1** + `scoring_version` + `score_breakdown` |
| [#2](../../issues/2) lima model angka pengguna | `human_states.metrics jsonb`, bukan kolom tetap |
| [#7](../../issues/7) model graf | **tidak menyentuh V0** — Neo4j baru masuk V2 |

> ⚠️ Menunda bukan menjawab. Selama #2 belum dipilih, tidak ada yang bisa
> **menghitung** angkanya — tabelnya hanya siap menampungnya.

---

## ⭐ MVP sudah ada namanya: V0 — HumanVerse Foundation

Untuk pertama kalinya dalam empat naskah, ada **daftar tertutup** yang bisa
dikerjakan. Target pemilik: **4–6 minggu**.

```
Authentication · Profile · Goals · Habits · Daily Check-in
Mood · Journal · AI Coach · Basic Memory · Dashboard

Agent:  Orchestrator · HabitAgent · CoachAgent · MemoryAgent
```

Selengkapnya: [`docs/75-URUTAN-PEMBANGUNAN-V0-V6.md`](docs/75-URUTAN-PEMBANGUNAN-V0-V6.md)

---

## Dua puluh naskah

```
  NASKAH 1   HumanOS — visi & 12 modul manusia          berkas 01–07
     │
  NASKAH 2   HumanVerse X — arsitektur eksekusi         berkas 10–22
     │       monorepo · 3 lapis agen · roadmap V0–V5
     │
  NASKAH 3   Phase 2 Enterprise Multi-Agent Platform    berkas 30–46
     │       Layer 6–20 · AgentOS · SDK · Marketplace
     │       160 dokumen engineering
     │
  NASKAH 4   Phase 3 AI-Native Human Ecosystem          berkas 50–77
     │       58 bagian · V0–V6 · HumanVerse Economy
     │       "arsitektur boleh besar, implementasinya bertahap"
     │
  NASKAH 5   Blueprint Engineering v1.0                 berkas 80–97
     │       34 bagian · monorepo final · 22 agent · 7 sprint V0
     │       "berhenti menambah visi/fitur"
     │
  NASKAH 6   Peta 14 lapisan engineering               berkas 98
     │       Operating Model · "jangan lompat ke fitur baru lagi"
     │       └──► lapisan 04 dikerjakan → spec/
     │
  NASKAH 7   Phase 4 Enterprise Operating System       berkas 100–112
     │       Layer 21–50 · standards · design system · AI Ops
     │
  NASKAH 8   Peta Phase 5–12                            berkas 113
     │       ≈380 dokumen tersisa · taksiran kemajuan 45 %
     │
  NASKAH 9   Phase 5 — HumanVerse Research Lab         berkas 114–122
     │       15 research pillar · BFM · memory compression
     │
  NASKAH 10  Phase 6 — Developer Platform              berkas 123–131
     │       25 layer · OAuth · SDK 7 bahasa · marketplace
     │
  NASKAH 11  Phase 7 — Data & AI Infrastructure        berkas 132–141
     │       event platform · lakehouse · feature store
     │       deletion engine · 18 deliverable (1 "Future")
     │
  NASKAH 12  Phase 8 — AI Safety, Security & Privacy   berkas 142–153
     │       46 bagian · identity · consent · data vault
     │       risk policy R0–R4 · kill switch · privacy center
     │
  NASKAH 13  Phase 9 — Intelligence & Cognitive Arch.  berkas 154–164
     │       41 bagian · memory 6 jenis · decay & konsolidasi
     │       cognitive runtime · POLICY_CHECK
     │
  NASKAH 14  Phase 10 — Multimodal Intelligence        berkas 165–175
     │       persepsi: vision · audio · spatial
     │       peta 15 fase (menggantikan peta naskah 8)
     │
  NASKAH 15  Phase 11 — Agentic Intelligence & Agency  berkas 176–187
     │       64 bagian · Action Gateway · dua tangga R & L
     │       budget · multi-agent · "autonomy must be earned"
     │
  NASKAH 16  Phase 12 — Digital Twin & World Simulation berkas 188–197
     │       31 bagian · assumption engine · learning loop
     │       "Observed ≠ Certain"
     │
  NASKAH 17  Phase 13 — HumanOS, Personal AI OS        berkas 198–206
     │       40 bagian · Attention OS · Approval Center
     │       state machine · app/agent/plugin
     │
  NASKAH 18  Phase 14 — Autonomous Intelligence &      berkas 207–218
     │       Collective Agent Ecosystem
     │       69 bagian (terpanjang) · federasi · agent team
     │       governance mesh · agent economy · L5 + autonomy contract
     │       "More agents must not automatically mean more autonomy"
     │
  NASKAH 19  Phase 15 — Spatial Intelligence &         berkas 219–227
     │       XR Universe
     │       32 bagian · SpatialOS · SLAM · scene graph
     │       spatial memory · AetherScan · XR · gesture/eye tracking
     │       "The world becomes an interface."
     │       ⚠️ mengumumkan Phase 16 → peta 15 fase patah (#101)
     │
  NASKAH 20  Phase 16 — Robotics & Embodied            berkas 228–235
             Intelligence
             35 bagian · HRP · SLAM/ROS2 · motion planning
             manipulasi · smart home/IoT · drone · fleet
             safety kernel · safe zones · simulation-first
             "Intelligence becomes embodied." — satu AI, banyak tubuh
             ⚠️ mengumumkan Phase 17 → peta terbuka-ujung (#108)
     │
  NASKAH 21  Phase 17 — Human Health & Bio             berkas 236–245
             Intelligence
             56 bagian · Health Digital Twin · Health Vault
             tidur/recovery · nutrisi · stress · anomali & forecast
             rekam medis · federasi · model registry · bias engine
             ⭐ Health Safety Kernel — rantai pertama dengan Risk
                DAN Evidence Check; metrik evaluasi model PERTAMA
             "HumanVerse tidak boleh menjadi AI dokter yang serba tahu."
             🛑 Safety & Governance di LUAR MVP ([#116](../../issues/116))
     │
  NASKAH 22  Phase 18 — Global Intelligence Network    berkas 246–255
             34 bagian · World Model · World Knowledge Graph
             HINP · federasi knowledge/agent · collective intelligence
             trust vector · provenance · global risk · early warning
             organization & city intelligence · marketplace
             ⭐⭐ `UNRESOLVED` sebagai KELUARAN yang sah (§18.23) —
                pertama kalinya sistem boleh berhenti tanpa jawaban
             "HumanVerse tidak mengontrol dunia."
             🛑 Safety Kernel §18.22 TANPA milestone ([#121](../../issues/121))
             🛑 `productivity` atas `People` = larangan §8.10 ([#122](../../issues/122))
             ⚠️ mengumumkan Phase 19 → perpanjangan KEEMPAT (#101)
```

> ℹ️ Penomoran berkas melewati 99. `99-CATATAN-AUDIT.md` tetap di tempatnya
> sebagai berkas audit; naskah 7 memakai `100`–`112`.
>
> ℹ️ **Peta dokumen di bawah baru mencakup naskah 1–11.** Untuk naskah 12–18
> (`142`–`235`), daftar berkas per naskah ada di
> [`docs/SESSION-LOG.md`](docs/SESSION-LOG.md) — satu entri per sesi.

---

## Aturan berkas dokumen

1. Berkas `01`–`235` merekam **kata pemilik apa adanya**. Susunannya dirapikan,
   isinya tidak ditambah-tambahi. Bagian yang hilang di naskah **ditandai
   sebagai hilang**, bukan ditambal.
2. Setiap keraguan, koreksi, risiko, atau usulan dari pihak lain (termasuk AI)
   masuk ke `99-CATATAN-AUDIT.md` — **tidak pernah disisipkan** ke berkas visi.
3. Kalau pemilik memutuskan sesuatu, keputusan itu **naik** ke berkas visi yang
   sesuai, lalu butirnya turun ke bagian **H** di berkas audit.

---

## Peta dokumen

### Naskah 1 — Visi (*HumanOS*)

| Berkas | Isi |
|---|---|
| [`01-VISI.md`](docs/01-VISI.md) | Big Vision, Moonshot Vision, pembeda utama |
| [`02-HUMAN-INTELLIGENCE-GRAPH.md`](docs/02-HUMAN-INTELLIGENCE-GRAPH.md) | Gagasan inti: semua data terhubung |
| [`03-MODUL.md`](docs/03-MODUL.md) | 12 Complete Human Modules |
| [`04-SISTEM-LANJUTAN.md`](docs/04-SISTEM-LANJUTAN.md) | Avatar, Digital Twin, Trend, Feed, Behavior Genome |
| [`05-ARSITEKTUR.md`](docs/05-ARSITEKTUR.md) | Enterprise-Grade Technology Architecture |
| [`06-MONETISASI.md`](docs/06-MONETISASI.md) | Enam paket, Free sampai Enterprise |
| [`07-PRINSIP.md`](docs/07-PRINSIP.md) | Privasi, transparansi, kendali, batas AI |

### Naskah 2 — Arsitektur eksekusi (*HumanVerse X*)

| Berkas | Isi |
|---|---|
| [`10-IDENTITAS.md`](docs/10-IDENTITAS.md) | Nama, AI Agent Factory, **keputusan nama resmi** |
| [`11-STRUKTUR-REPO.md`](docs/11-STRUKTUR-REPO.md) | Pohon monorepo lengkap |
| [`12-HIERARKI-AGEN.md`](docs/12-HIERARKI-AGEN.md) | Layer 1 Orchestrator, Layer 2 Core, Layer 3 Specialist |
| [`13-KNOWLEDGE-GRAPH.md`](docs/13-KNOWLEDGE-GRAPH.md) | Skema graf: 10 node, 5 relasi kausal |
| [`14-DIGITAL-TWIN-ENGINE.md`](docs/14-DIGITAL-TWIN-ENGINE.md) | Lima profil + simulasi |
| [`15-MEMORY.md`](docs/15-MEMORY.md) | Lima jenis memori |
| [`16-EVENT-DRIVEN.md`](docs/16-EVENT-DRIVEN.md) | Event, Kafka, Redis Streams |
| [`17-AI-WORKFLOW.md`](docs/17-AI-WORKFLOW.md) | LangGraph, MCP, Tool Calling |
| [`18-DATABASE-DAN-PIPELINE.md`](docs/18-DATABASE-DAN-PIPELINE.md) | 6 basis data, 8 tahap, bobot rekomendasi |
| [`19-DEVOPS-DAN-KEAMANAN.md`](docs/19-DEVOPS-DAN-KEAMANAN.md) | DevOps, Observability, Security |
| [`20-EVALUASI-AI.md`](docs/20-EVALUASI-AI.md) | Evaluator per agen |
| [`21-ROADMAP.md`](docs/21-ROADMAP.md) | V0 → V5 ⚠️ **digantikan sebagian oleh naskah 4** |
| [`22-PAKET-DOKUMENTASI.md`](docs/22-PAKET-DOKUMENTASI.md) | Rencana ~100 dokumen |

### Naskah 3 — Phase 2 Enterprise Blueprint

| Berkas | Layer | Isi |
|---|---|---|
| [`30-PHASE-2-IKHTISAR.md`](docs/30-PHASE-2-IKHTISAR.md) | — | Ikhtisar + peta 15 lapisan |
| [`31-L06-AGENT-OS.md`](docs/31-L06-AGENT-OS.md) | 6 | **AgentOS** — sistem operasi untuk AI Agent |
| [`32-L07-HUMAN-ONTOLOGY.md`](docs/32-L07-HUMAN-ONTOLOGY.md) | 7 | **Human Ontology** — 10 domain, 7 relasi struktural |
| [`33-L08-KNOWLEDGE-GRAPH-ENGINE.md`](docs/33-L08-KNOWLEDGE-GRAPH-ENGINE.md) | 8 | Knowledge Graph Engine (Neo4j) |
| [`34-L09-MEMORY-HIERARCHY.md`](docs/34-L09-MEMORY-HIERARCHY.md) | 9 | Memory Hierarchy — 7 jenis |
| [`35-L10-MCP-TOOL-ECOSYSTEM.md`](docs/35-L10-MCP-TOOL-ECOSYSTEM.md) | 10 | MCP Tool Ecosystem — 9 tool |
| [`36-L11-WORKFLOW-ENGINE.md`](docs/36-L11-WORKFLOW-ENGINE.md) | 11 | Workflow Engine (LangGraph) |
| [`37-L12-DECISION-ENGINE.md`](docs/37-L12-DECISION-ENGINE.md) | 12 | Decision Engine — Outfit Score |
| [`38-L13-PROMPTOPS.md`](docs/38-L13-PROMPTOPS.md) | 13 | PromptOps — prompt versioned |
| [`39-L14-EVALUATION-FRAMEWORK.md`](docs/39-L14-EVALUATION-FRAMEWORK.md) | 14 | AI Evaluation Framework ⚠️ **terpotong** |
| [`40-TANPA-NOMOR-PROFILE-ENGINE.md`](docs/40-TANPA-NOMOR-PROFILE-ENGINE.md) | ⚠️ ? | Profile Engine — **judul & nomor hilang di naskah** |
| [`41-L17-TREND-PLATFORM.md`](docs/41-L17-TREND-PLATFORM.md) | 17 | Trend Intelligence Platform — 12 kategori |
| [`42-L18-AI-MARKETPLACE.md`](docs/42-L18-AI-MARKETPLACE.md) | 18 | AI Marketplace — agen pihak ketiga |
| [`43-L19-HUMANVERSE-SDK.md`](docs/43-L19-HUMANVERSE-SDK.md) | 19 | HumanVerse SDK — 5 bahasa |
| [`44-L20-SIMULATION-ENGINE.md`](docs/44-L20-SIMULATION-ENGINE.md) | 20 | AI Simulation Engine |
| [`45-MASTER-DOCUMENTATION.md`](docs/45-MASTER-DOCUMENTATION.md) | — | 160 dokumen engineering |
| [`46-PHASE-3.md`](docs/46-PHASE-3.md) | — | Ringkasan Phase 3 → **dirinci naskah 4** |

> ⚠️ **Layer 15 dan Layer 16 tidak ada di naskah**, dan Layer 14 terpotong di
> tengah tabel. Tidak saya karang — lihat butir **G-1** dan **G-2**.

---

### Naskah 4 — Phase 3: AI-Native Human Ecosystem

| Berkas | § | Isi |
|---|---|---|
| [`50-NASKAH-4-IKHTISAR.md`](docs/50-NASKAH-4-IKHTISAR.md) | — | Core Philosophy + peta 58 bagian |
| [`51-HUMANVERSE-CORE.md`](docs/51-HUMANVERSE-CORE.md) | 1 | **HumanVerse Core** — semua agent bicara lewat sini |
| [`52-CONTEXT-ENGINE.md`](docs/52-CONTEXT-ENGINE.md) | 2–3 | Human Context Engine · Context Vector |
| [`53-HUMAN-STATE-ENGINE.md`](docs/53-HUMAN-STATE-ENGINE.md) | 4 | Human State — 8 field |
| [`54-BEHAVIOR-ENGINE.md`](docs/54-BEHAVIOR-ENGINE.md) | 5–7 | Behavior Engine · Pattern Mining · **Causality** |
| [`55-GOAL-INTELLIGENCE.md`](docs/55-GOAL-INTELLIGENCE.md) | 8–9 | Goal Intelligence · Goal Graph |
| [`56-AGENT-FACTORY.md`](docs/56-AGENT-FACTORY.md) | 10–12 | Agent Factory · **Manifest** · Registry 14 agent |
| [`57-AGENT-PROTOKOL-DAN-MEMORY-POLICY.md`](docs/57-AGENT-PROTOKOL-DAN-MEMORY-POLICY.md) | 13–14 | Protokol antar-agent · Memory Policy |
| [`58-PERMISSION-RISK-SAFETY.md`](docs/58-PERMISSION-RISK-SAFETY.md) | 15–17 | Permission · **Risk Level 0–4** · Safety Layer |
| [`59-MULTIMODAL-INTERFACE.md`](docs/59-MULTIMODAL-INTERFACE.md) | 18–20 | Multimodal · Voice HumanOS · AI Vision |
| [`60-WARDROBE-DAN-TREND-ENGINE.md`](docs/60-WARDROBE-DAN-TREND-ENGINE.md) | 21–22 | Wardrobe Intelligence · Trend Score |
| [`61-PERSONALIZATION-DAN-FEEDBACK-LOOP.md`](docs/61-PERSONALIZATION-DAN-FEEDBACK-LOOP.md) | 23–24 | Personalization · Feedback Loop |
| [`62-DIGITAL-TWIN-V2-DAN-SIMULASI.md`](docs/62-DIGITAL-TWIN-V2-DAN-SIMULASI.md) | 25–27 | Digital Twin V2 · World Model · **Decision Lab** |
| [`63-LIFE-SCORE-XAI-INSIGHT.md`](docs/63-LIFE-SCORE-XAI-INSIGHT.md) | 28–30 | **Tolak satu angka** · Explainable AI · Insight |
| [`64-REVIEW-MINGGUAN-DAN-BULANAN.md`](docs/64-REVIEW-MINGGUAN-DAN-BULANAN.md) | 31–32 | Weekly Review · Monthly Life Review |
| [`65-ROUTINE-DAN-HABIT-ADAPTIF.md`](docs/65-ROUTINE-DAN-HABIT-ADAPTIF.md) | 33–34 | Autonomous Routines · *Consistency > Perfection* |
| [`66-EXPERIMENT-DAN-PERSONAL-SCIENCE.md`](docs/66-EXPERIMENT-DAN-PERSONAL-SCIENCE.md) | 35–36 | Experiment Engine · Personal Science Lab |
| [`67-EVENT-DATA-PLATFORM-FLYWHEEL.md`](docs/67-EVENT-DATA-PLATFORM-FLYWHEEL.md) | 37–39 | Event · Data Lakehouse · Data Flywheel |
| [`68-PERSONAL-AI-MODEL-DAN-PRIVASI-ML.md`](docs/68-PERSONAL-AI-MODEL-DAN-PRIVASI-ML.md) | 40–42 | Personal AI Model · On-device · Federated |
| [`69-PRIVACY-CENTER-VAULT-AUDIT.md`](docs/69-PRIVACY-CENTER-VAULT-AUDIT.md) | 43–45 | **Privacy Center** · Data Vault · Audit Trail |
| [`70-OBSERVABILITY-DAN-EVALUASI-AGEN.md`](docs/70-OBSERVABILITY-DAN-EVALUASI-AGEN.md) | 46–47 | Agent Observability · Evaluation + rollback |
| [`71-COST-ENGINE-DAN-MODEL-ROUTER.md`](docs/71-COST-ENGINE-DAN-MODEL-ROUTER.md) | 48–49 | AI Cost Engine · Model Router |
| [`72-INFRASTRUKTUR-DAN-KUBERNETES.md`](docs/72-INFRASTRUKTUR-DAN-KUBERNETES.md) | 50–51 | HumanVerse Cloud · **jangan langsung K8s** |
| [`73-DEVELOPMENT-OS.md`](docs/73-DEVELOPMENT-OS.md) | 52–55 | Development OS · AI coding agent governance |
| [`74-EKOSISTEM-AKHIR-DAN-LOOP.md`](docs/74-EKOSISTEM-AKHIR-DAN-LOOP.md) | 56–57 | Final Agent Ecosystem · The HumanVerse Loop |
| [`75-URUTAN-PEMBANGUNAN-V0-V6.md`](docs/75-URUTAN-PEMBANGUNAN-V0-V6.md) | 58 | ⭐ **V0 → V6 — jangan langsung 50 agent** |
| [`76-HUMANVERSE-ECONOMY.md`](docs/76-HUMANVERSE-ECONOMY.md) | — | HumanVerse Economy · bentuk akhir · prinsip penutup |
| [`77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md`](docs/77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md) | — | Langkah berikutnya: **Blueprint Engineering v1.0** |

### Naskah 5 — Blueprint Engineering v1.0

| Berkas | § | Isi |
|---|---|---|
| [`80-BLUEPRINT-IKHTISAR.md`](docs/80-BLUEPRINT-IKHTISAR.md) | 1 | **Modular Monolith → Distributed Services → Agent Platform** |
| [`81-SYSTEM-CONTEXT.md`](docs/81-SYSTEM-CONTEXT.md) | 2 | System Context — apps → gateway → 3 blok → event bus → 3 penyimpanan |
| [`82-DOMAIN-ARCHITECTURE.md`](docs/82-DOMAIN-ARCHITECTURE.md) | 3 | 10 bounded context + 8 domain platform |
| [`83-STRUKTUR-REPO-FINAL.md`](docs/83-STRUKTUR-REPO-FINAL.md) | 4 | ⭐ **Monorepo final** — menutup E-27 |
| [`84-DATABASE-ARCHITECTURE.md`](docs/84-DATABASE-ARCHITECTURE.md) | 5–6 | PostgreSQL · Qdrant · Neo4j · Redis — **Kafka & ClickHouse dibuang** |
| [`85-BEHAVIOR-DAN-EVENT.md`](docs/85-BEHAVIOR-DAN-EVENT.md) | 7–8 | **21 event** + arsitektur event bus |
| [`86-HUMAN-STATE-DAN-CONTEXT.md`](docs/86-HUMAN-STATE-DAN-CONTEXT.md) | 9–10 | HumanState 7 field (`mood` keluar) · Context Engine |
| [`87-RECOMMENDATION-ENGINE.md`](docs/87-RECOMMENDATION-ENGINE.md) | 11 | Recommendation Score — 7 komponen |
| [`88-ARSITEKTUR-AGEN.md`](docs/88-ARSITEKTUR-AGEN.md) | 12–16 | **22 agent** · Orchestrator · Manifest · Permission · Risk 0–4 |
| [`89-MEMORY-ARCHITECTURE.md`](docs/89-MEMORY-ARCHITECTURE.md) | 17 | Memory 6 jenis, dengan contoh |
| [`90-DIGITAL-TWIN-DAN-CONFIDENCE.md`](docs/90-DIGITAL-TWIN-DAN-CONFIDENCE.md) | 18–19 | ⭐ **Confidence Layer** — low confidence → tanya pengguna |
| [`91-PERSONALIZATION-DAN-TREND.md`](docs/91-PERSONALIZATION-DAN-TREND.md) | 20–21 | Flywheel · *Popular ≠ suitable for the user* |
| [`92-MODEL-ROUTER-EVALUASI-AUDIT.md`](docs/92-MODEL-ROUTER-EVALUASI-AUDIT.md) | 22–24 | Model Router · Evaluation + rollback · Audit metadata |
| [`93-SECURITY-DAN-PRIVACY.md`](docs/93-SECURITY-DAN-PRIVACY.md) | 25–26 | Rantai keamanan · Privacy Center + izin per agent |
| [`94-DEVELOPMENT-LIFECYCLE.md`](docs/94-DEVELOPMENT-LIFECYCLE.md) | 27–28 | *Governance tetap manusia* · 10 agent pengembangan |
| [`95-V0-SPESIFIKASI.md`](docs/95-V0-SPESIFIKASI.md) | 29–32 | ⭐ **12 fitur · 4 agent · 19 tabel · 7 sprint** |
| [`96-SESUDAH-V0-DAN-TARGET-AKHIR.md`](docs/96-SESUDAH-V0-DAN-TARGET-AKHIR.md) | 33–34 | V1–V6 · target akhir dengan lapisan **HUMAN CONTROL** |
| [`97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md`](docs/97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md) | — | Langkah berikutnya: **Engineering Specification v1.0** |

---

### Naskah 7 — Phase 4: Enterprise Operating System (Layer 21–50)

| Berkas | Layer | Isi |
|---|---|---|
| [`100-PHASE-4-IKHTISAR.md`](docs/100-PHASE-4-IKHTISAR.md) | 21 | HumanVerse OS — 6 standar + peta Layer 21–50 |
| [`101-L22-ENGINEERING-STANDARDS.md`](docs/101-L22-ENGINEERING-STANDARDS.md) | 22 | Kontrak per folder · naming convention |
| [`102-L23-ADR.md`](docs/102-L23-ADR.md) | 23 | ADR-001…004 — **LangGraph akhirnya dikunci** |
| [`103-L24-26-DESIGN-SYSTEM.md`](docs/103-L24-26-DESIGN-SYSTEM.md) | 24–26 | Design tokens · 10 komponen · motion |
| [`104-L27-29-INTERAKSI.md`](docs/104-L27-29-INTERAKSI.md) | 27–29 | UX Intelligence · 4 mode · alur percakapan 9 langkah |
| [`105-L30-32-PROMPTOPS-MODEL.md`](docs/105-L30-32-PROMPTOPS-MODEL.md) | 30–32 | PromptOps · siklus hidup model · optimasi biaya |
| [`106-L33-35-EKSPERIMEN-EVALUASI.md`](docs/106-L33-35-EKSPERIMEN-EVALUASI.md) | 33–35 | Feature flag · eksperimen · lab evaluasi AI |
| [`107-L36-37-PERSONA.md`](docs/107-L36-37-PERSONA.md) | 36–37 | Synthetic user · persona library |
| [`108-L38-40-NOTIFIKASI-SEARCH-KNOWLEDGE.md`](docs/108-L38-40-NOTIFIKASI-SEARCH-KNOWLEDGE.md) | 38–40 | Notifikasi · search · ⭐ **Memory ≠ Knowledge** |
| [`109-L41-43-DOKUMENTASI-PLAYBOOK-INSIDEN.md`](docs/109-L41-43-DOKUMENTASI-PLAYBOOK-INSIDEN.md) | 41–43 | Documentation OS · playbook · AI incident response |
| [`110-L44-46-RELIABILITY-INFRA.md`](docs/110-L44-46-RELIABILITY-INFRA.md) | 44–46 | SRE ⚠️ **terpotong** · Layer 45 ⚠️ **hilang** · multi-region |
| [`111-L47-50-PLATFORM-EKONOMI-VISI.md`](docs/111-L47-50-PLATFORM-EKONOMI-VISI.md) | 47–50 | Enterprise API · developer platform · ⭐ **4 fondasi** |
| [`112-PHASE-5-RESEARCH-LAB.md`](docs/112-PHASE-5-RESEARCH-LAB.md) | — | Phase 5: 9 arah riset, **500+ spesifikasi** ⚠️ angkanya dibantah naskah 8 |

> ⚠️ **Layer 44 terpotong dan Layer 45 tidak ada** — bentuknya persis seperti
> lubang naskah 3 (Layer 14 terpotong, Layer 15/16 hilang). Tidak dikarang;
> lihat butir **G-4** dan **G-5**.

---

### Naskah 8 — Peta Phase 5–12

| Berkas | Isi |
|---|---|
| [`113-PETA-FASE-5-12.md`](docs/113-PETA-FASE-5-12.md) | Taksiran kemajuan 45 % + 8 fase tersisa, ≈**380 dokumen** |

```
Phase 5   Research Lab           50+    BFM · GNN · World Model · Federated
Phase 6   Developer Platform     40+    SDK · Plugin API · Marketplace · OAuth
Phase 7   Data & AI Infra        50+    Feature Store · Lakehouse · Model Registry
Phase 8   AI Safety & Ethics     30+    Bias Detection · Human Override ← BARU
Phase 9   Enterprise & Business  30+    Team · Family · Company Wellness
Phase 10  AI Automation Engine   40+    Cross-App · Calendar · Email Automation
Phase 11  HumanVerse Cloud       40+    Multi-region · DR · Edge
Phase 12  Blueprint Implementation 100+ ERD 100+ tabel · API 500+ endpoint
```

> ✅ Aritmetikanya benar: **380**, tepat di dalam rentang "300–500".
>
> ⚠️ Tapi **Phase 5 berbeda 10× dengan naskah 7** (500+ vs 50+ dokumen), dan
> **Phase 8/11/12 sebagian mengulang** yang sudah ditulis — Phase 12 justru
> pekerjaan yang **sudah selesai untuk V0** di [`spec/`](spec/README.md), hanya
> beda skala. Lihat **E-51** dan **E-53**.

---

### Naskah 9 — Phase 5: HumanVerse Research Lab

| Berkas | Pillar | Isi |
|---|---|---|
| [`114-PHASE-5-IKHTISAR.md`](docs/114-PHASE-5-IKHTISAR.md) | — | 4 prinsip riset · repo `research/` · peta 15 pilar |
| [`115-R1-BEHAVIOR-FOUNDATION-MODEL.md`](docs/115-R1-BEHAVIOR-FOUNDATION-MODEL.md) | 1 | **BFM** — struktur model, dataset, evaluasi (**Calibration**) |
| [`116-R2-R3-PREFERENCE-DAN-GRAPH.md`](docs/116-R2-R3-PREFERENCE-DAN-GRAPH.md) | 2–3 | Preference Learning · Graph Intelligence |
| [`117-R4-MEMORY-COMPRESSION.md`](docs/117-R4-MEMORY-COMPRESSION.md) | 4 | Raw → Episode → Summary → Chapter → **Identity** |
| [`118-R5-R7-WORLD-MODEL-SIMULASI.md`](docs/118-R5-R7-WORLD-MODEL-SIMULASI.md) | 5–7 | World Model · Counterfactual · Simulation |
| [`119-R8-R9-EMBEDDING-REPRESENTASI.md`](docs/119-R8-R9-EMBEDDING-REPRESENTASI.md) | 8–9 | Embedding · ⭐ **Personal Representation Layer** |
| [`120-R10-R12-INTERVENSI-XAI-EKSPERIMEN.md`](docs/120-R10-R12-INTERVENSI-XAI-EKSPERIMEN.md) | 10–12 | Adaptive Intervention (**annoyance**) · XAI · eksperimen |
| [`121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md`](docs/121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md) | 13–15 | Benchmark · Experiment Registry · **Research Governance** |
| [`122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md`](docs/122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md) | — | Repo final · roadmap R1–R8 · 10 deliverable |

> ⭐ **Pillar 9 hampir menutup issue [#2](../../issues/2)** — *Personal
> Representation Layer* punya **6 dari 7 dimensi identik** dengan Human
> Dashboard naskah 4, plus `confidence`/`trend`/`evidence` per dimensi.
>
> 🛑 **Tapi Research Lab tidak bisa dimulai sebelum V0 mengumpulkan datanya.**
> Seluruh dataset BFM baru ada setelah V0 dipakai berbulan-bulan, dan
> `sleep_events` + `calendar_events` tidak ada di V0 sama sekali (**B-21**).

---

### Naskah 10 — Phase 6: Developer Platform

| Berkas | Layer | Isi |
|---|---|---|
| [`123-PHASE-6-IKHTISAR.md`](docs/123-PHASE-6-IKHTISAR.md) | — | 3 tipe pengguna · 5 prinsip · ⚠️ **tabrakan penomoran Layer** |
| [`124-DP-L1-L3-PORTAL-API-GATEWAY.md`](docs/124-DP-L1-L3-PORTAL-API-GATEWAY.md) | 1–3 | Developer Portal · REST API · API Gateway |
| [`125-DP-L4-L5-AUTH-DAN-KEY.md`](docs/125-DP-L4-L5-AUTH-DAN-KEY.md) | 4–5 | OAuth 2.1 + PKCE · 🛑 scope `journal.read` · API key |
| [`126-DP-L6-L9-SDK-AGENT-PLUGIN.md`](docs/126-DP-L6-L9-SDK-AGENT-PLUGIN.md) | 6–9 | SDK 7 bahasa · Agent SDK · 🛑 **manifest tanpa `risk_level`** |
| [`127-DP-L10-L11-MCP-TOOL-REGISTRY.md`](docs/127-DP-L10-L11-MCP-TOOL-REGISTRY.md) | 10–11 | MCP · Tool Registry · Capability Discovery |
| [`128-DP-L12-L16-WEBHOOK-SANDBOX-CLI.md`](docs/128-DP-L12-L16-WEBHOOK-SANDBOX-CLI.md) | 12–16 | ⭐ **Webhook menutup #38** · Sandbox · CLI · `.hvap` |
| [`129-DP-L17-L20-MARKETPLACE-REVIEW-REVENUE.md`](docs/129-DP-L17-L20-MARKETPLACE-REVIEW-REVENUE.md) | 17–20 | Marketplace · **Review System** · revenue · analytics |
| [`130-DP-L21-L25-DOKUMENTASI-KOMUNITAS-ENTERPRISE.md`](docs/130-DP-L21-L25-DOKUMENTASI-KOMUNITAS-ENTERPRISE.md) | 21–25 | Dokumentasi · contoh · sertifikasi · komunitas · enterprise |
| [`131-PHASE-6-ROADMAP-DAN-DELIVERABLE.md`](docs/131-PHASE-6-ROADMAP-DAN-DELIVERABLE.md) | — | Repo · roadmap D1–D8 · 13 deliverable |

> ⭐ **Menutup [#38](../../issues/38):** DP-L12 memakai `outfit.selected` untuk
> event yang naskah 7 tulis `fashion.outfit.selected` — dua naskah dua segmen
> melawan satu naskah tiga segmen.
>
> ⭐ **Sandbox + Review System** adalah jawaban terbesar untuk beban hukum
> marketplace ([#24](../../issues/24)) setelah enam naskah hanya berupa
> kekhawatiran.
>
> 🛑 Tapi dua pengaman hilang justru di tempat paling dibutuhkan: manifest
> marketplace **membuang `risk_level` dan `requires_confirmation`**, dan
> **`journal.read` ditawarkan sebagai scope pihak ketiga**.

---

### Naskah 11 — Phase 7: Data & AI Infrastructure

| Berkas | § | Isi |
|---|---|---|
| [`132-PHASE-7-IKHTISAR.md`](docs/132-PHASE-7-IKHTISAR.md) | 7.0–7.1 | Tangga evolusi V0–V5 · data backbone |
| [`133-DATA-CLASSIFICATION.md`](docs/133-DATA-CLASSIFICATION.md) | 7.2 | 4 tingkat sensitivitas ⚠️ **Level 4 kosong** |
| [`134-EVENT-PLATFORM.md`](docs/134-EVENT-PLATFORM.md) | 7.3–7.5 | Streaming · **canonical envelope** · schema registry |
| [`135-LAKEHOUSE-WAREHOUSE-FEATURE.md`](docs/135-LAKEHOUSE-WAREHOUSE-FEATURE.md) | 7.6–7.9 | Lakehouse · warehouse · **feature store offline/online** |
| [`136-VECTOR-RETRIEVAL-GRAPH.md`](docs/136-VECTOR-RETRIEVAL-GRAPH.md) | 7.10–7.13 | Vector · **hybrid retrieval** · knowledge graph |
| [`137-PIPELINE-QUALITY-LINEAGE.md`](docs/137-PIPELINE-QUALITY-LINEAGE.md) | 7.14–7.16 | Processing · 6 metrik kualitas · lineage |
| [`138-ML-PLATFORM-DAN-INFERENCE.md`](docs/138-ML-PLATFORM-DAN-INFERENCE.md) | 7.17–7.23 | Training · registry · serving · batch · flywheel |
| [`139-PRIVACY-DELETION-RETENTION.md`](docs/139-PRIVACY-DELETION-RETENTION.md) | 7.24–7.26 | ⭐ **Privacy metadata · cascade deletion 7 tempat** |
| [`140-SKALA-OBSERVABILITY-RESEARCH.md`](docs/140-SKALA-OBSERVABILITY-RESEARCH.md) | 7.27–7.32 | Multi-region · DR · **Production ≠ Research** |
| [`141-PHASE-7-REPO-ROADMAP-DELIVERABLE.md`](docs/141-PHASE-7-REPO-ROADMAP-DELIVERABLE.md) | 7.33–7.35 | Repo 21 folder · roadmap D1–D8 · teaser Phase 8 |

> ⭐ **Bagian terkuat:** metadata privasi yang menempel pada datanya
> (`purpose`, `retention`, `consent_required`) — pembatasan tujuan yang bisa
> ditegakkan mesin — dan **cascade deletion ke 7 tempat**, yang memperluas
> prosedur hapus akun di [`spec/`](spec/README.md) dengan empat tempat yang
> belum tercakup.
>
> 🛑 **Dua tabrakan penomoran baru:** tangga V0–V5 memberi makna **ketiga**
> untuk nomor versi, dan **`D1`–`D8` dipakai dua kali** (Developer Platform
> naskah 10 vs Data Platform naskah 11).

---

### Catatan

| Berkas | Isi |
|---|---|
| [`99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md) | **Catatan, risiko & pertanyaan terbuka — bukan kata pemilik** |

---

## Arsitektur sekilas

```
   ┌────────────────────────────────────────────────────────┐
   │  LAYER 1 · Supreme Orchestrator                        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 2 · Planner · Memory · Reasoning · Guardrail     │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 3 · Health · Habit · Fashion · Trend · Career    │
   │            Finance · Learning · Social                  │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 6 · AgentOS                                      │
   │  Registry · Scheduler · Queue · Workflow · Tools        │
   │  Memory Manager · Event Bus · Policy Engine            │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 7–9 · Ontology · Knowledge Graph · Memory        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 10–14 · Tools · Workflow · Decision · PromptOps  │
   │                Evaluation                               │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 17–20 · Trend · Marketplace · SDK · Simulation   │
   └────────────────────────────────────────────────────────┘
```

Naskah 4 menyusunnya ulang dari sudut lain:

```
                     HUMANVERSE XOS
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    HUMAN CORE        AI RUNTIME        DATA CORE
        │                 │                 │
    Behavior          Orchestrator      PostgreSQL
    Goals             Agents            Vector DB
    Memory            Tools             Graph
    Context           Evaluation        Analytics
```

---

## 12 Modul manusia (naskah 1) vs 14 Agent (naskah 4)

```
NASKAH 1 — 12 modul               NASKAH 4 — Agent Registry §12
 1. Habit Intelligence            Health · Habit · Fashion · Grooming
 2. Lifestyle Intelligence        Fitness · Nutrition · Learning · Career
 3. Fashion AI                    Finance · Social · Travel · Productivity
 4. Grooming AI                   Entertainment · Research
 5. Fitness Intelligence
 6. Nutrition Intelligence        Baru      : Travel, Entertainment, Research
 7. Mental Wellness               Kembali   : Grooming, Nutrition, Productivity
 8. Productivity Intelligence     Masih nol : Mental Wellness, Lifestyle
 9. Learning Intelligence
10. Career Intelligence
11. Social Intelligence
12. Finance Behavior
```

> ⚠️ **Mental Wellness dan Lifestyle masih belum punya agent** di tiga naskah
> berturut-turut — dan *Journal* justru masuk V0. Lihat butir **A-20** dan
> **C-3**.

---

## Tumpukan teknologi

| Lapisan | Teknologi |
|---|---|
| Aplikasi | Flutter (mobile & web) · desktop & admin-dashboard **belum ditetapkan** |
| Backend | FastAPI · 12 microservice |
| AgentOS | Registry · Scheduler · Task Queue · Workflow · Tool Registry · Memory Manager · Event Bus · Policy Engine |
| AI | LangGraph · MCP · Tool Calling · **Model Router** (small/medium/large) |
| Data | **PostgreSQL · Qdrant · Neo4j · Redis** — naskah 5 membuang ClickHouse & Kafka |
| Event | Event Bus; antrean di **Redis** (Kafka baru bila skalanya menuntut) |
| Infra | **V0: Docker Compose** → Cloud VM → Kubernetes · ArgoCD · Terraform · Vault |
| Observability | OpenTelemetry · Prometheus · Grafana · Loki · Tempo · Sentry · **Agent Health** |
| Keamanan | OAuth · RBAC · Vault · AES-256 · TLS · Immutable Log · Permission Engine · Risk Engine |
| Privasi | Privacy Center · Personal Data Vault · On-device AI (V5) · Federated ML (V5) |
| SDK | Python · TypeScript · Flutter · Kotlin · Swift — **ditunda ke V6** |

---

## Tangga versi (naskah 4)

```
  V0  Foundation            ── auth, profile, goals, habits, mood, journal,
   │                           AI coach, memory, dashboard · 4–6 minggu
  V1  Behavior Intelligence ── event, analytics, pattern, prediksi, weekly review
   │
  V2  Lifestyle AI          ── fashion, wardrobe, trend, grooming, fitness, nutrisi
   │
  V3  Multi-Agent Platform  ── registry, SDK, MCP, tool registry, evaluation
   │
  V4  Digital Twin          ── human state, model perilaku, simulasi, decision lab
   │
  V5  HumanOS               ── voice, vision, wearable, on-device AI, privasi lanjut
   │
  V6  HumanVerse Ecosystem  ── developer SDK, marketplace, enterprise API
```

---

## Prinsip penutup pemilik

> **Jangan membuat HumanVerse menjadi mesin yang menilai apakah seseorang
> "manusia yang baik" atau "manusia yang buruk".**
>
> ## Manusia tetap menjadi pusat sistem.
