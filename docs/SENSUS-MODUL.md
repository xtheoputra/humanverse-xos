# Sensus modul lintas fase

> ⚠️ **Bukan kata pemilik.** Ini pengukuran, bukan naskah dan bukan usulan
> arsitektur. Ia **tidak memutuskan apa pun** — ia hanya menghitung apa yang
> sudah tertulis di 24 naskah, supaya keputusan
> [#139](../../issues/139) diambil di atas angka, bukan ingatan.
>
> Temuannya terbit sebagai **[#146](../../issues/146)** (E-151 — sensus &
> hitungan berurutan yang meleset) dan **[#147](../../issues/147)**
> (G-20 — `scenario/`+`counterfactual/` ganda di dalam `intelligence/`).

---

## Kenapa berkas ini ada

Penutup naskah 24 meminta **HumanVerse Master Architecture v2.0**, dan butir
pertamanya adalah *"menghapus overlap antar-modul"*. Untuk menghapus overlap,
overlap-nya harus dihitung dulu — dan **hitungan itu belum pernah ada**.

Yang ada selama ini adalah catatan **berurutan**: tiap kali sebuah naskah
menambah pohon repositori, [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md)
mencatat *"H-10 tergerus ke-N kalinya"* dan menyebut duplikasi yang terlihat
**saat itu**. Sepuluh catatan seperti itu tersebar di sepuluh berkas.

Berkas ini menghitungnya **sekali, sekaligus, atas seluruh `docs/`**.

---

## Cara mengukur, dan apa yang TIDAK terhitung

Tiap blok ber-fence di `docs/` diperiksa; sebuah blok dianggap pohon
repositori bila memuat **≥ 3 nama berakhir `/`** dan punya gambar pohon
(`├` `└` `│`) atau baris akar tanpa indentasi.

Dua bentuk penulisan dihitung:

| Bentuk | Contoh | Terhitung |
|---|---|---|
| token berakhir garis miring | `├── runtime/` | ✅ 709 sebutan |
| anak di dalam kurung | `data/ (ingestion · quality)` | ✅ 19 sebutan |

**Yang sengaja TIDAK terhitung**, jadi angka di bawah adalah **batas bawah**:

- nama modul yang disebut di prosa tanpa pernah digambar sebagai direktori;
- nama layanan/mesin (*Simulation Engine*, *Risk Engine*) yang tidak punya
  folder — itu perkara [#130](../../issues/130), bukan perkara sensus ini;
- pohon di `spec/`, yang cakupannya V0 saja dan memang tidak boleh dicampur.

---

## Tabel A — setiap pohon repositori di `docs/`

**38 blok pohon** tersebar di **36 dokumen**.

| Berkas | Bagian | Akar | Subdir |
|---|---|---|---|
| [`11`](11-STRUKTUR-REPO.md) | Pohon monorepo | `HumanVerse-X/` | 43 |
| [`31`](31-L06-AGENT-OS.md) | Folder | `agent-os/` | 9 |
| [`35`](35-L10-MCP-TOOL-ECOSYSTEM.md) | Tool Registry | `tools/` | 10 |
| [`38`](38-L13-PROMPTOPS.md) | Struktur | `prompts/` | 8 |
| [`43`](43-L19-HUMANVERSE-SDK.md) | Struktur | `humanverse-sdk/` | 6 |
| [`51`](51-HUMANVERSE-CORE.md) | — | `humanverse-core/` | 11 |
| [`83`](83-STRUKTUR-REPO-FINAL.md) | — | `humanverse-x/` | 85 |
| [`105`](105-L30-32-PROMPTOPS-MODEL.md) | Layer 30 — Prompt Engineering Framework | `prompts/` | 8 |
| [`109`](109-L41-43-DOKUMENTASI-PLAYBOOK-INSIDEN.md) | Layer 41 — Documentation Operating System | `docs/` | 9 |
| [`114`](114-PHASE-5-IKHTISAR.md) | Arsitektur Research Lab | `research/` | 13 |
| [`121`](121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md) | Pillar 13 — Benchmark Platform | `benchmarks/` | 6 |
| [`122`](122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md) | Research Repository Final | `research/` | 13 |
| [`124`](124-DP-L1-L3-PORTAL-API-GATEWAY.md) | DP-L1 — Developer Portal | `portal/` | 10 |
| [`126`](126-DP-L6-L9-SDK-AGENT-PLUGIN.md) | DP-L6 — HumanVerse SDK | `sdk/` | 8 |
| [`126`](126-DP-L6-L9-SDK-AGENT-PLUGIN.md) | DP-L7 — Agent SDK | `agent-sdk/` | 8 |
| [`130`](130-DP-L21-L25-DOKUMENTASI-KOMUNITAS-ENTERPRISE.md) | DP-L21 — Documentation Platform | `docs/` | 8 |
| [`131`](131-PHASE-6-ROADMAP-DAN-DELIVERABLE.md) | Struktur repository | `developer-platform/` | 12 |
| [`134`](134-EVENT-PLATFORM.md) | §7.5 — Event Schema Registry | `events/` | 5 |
| [`135`](135-LAKEHOUSE-WAREHOUSE-FEATURE.md) | §7.6 — Data Lakehouse | `data-lake/` | 14 |
| [`141`](141-PHASE-7-REPO-ROADMAP-DELIVERABLE.md) | §7.33 — Final Data Platform Repository | `data-platform/` | 22 |
| [`152`](152-REPO-DATA-MODEL-CONTROL-PLANE.md) | §8.39 — Security Architecture Repository | `security/` | 37 |
| [`162`](162-COGNITIVE-ORCHESTRATOR-DAN-RUNTIME.md) | §9.28 — Cognitive Runtime | `cognitive-runtime/` | 17 |
| [`164`](164-ARSITEKTUR-REPO-ROADMAP-DOD.md) | §9.38 — Repository final Fase 9 | `intelligence/` | 67 |
| [`175`](175-REPO-API-DB-ROADMAP-DOD.md) | §10.34 — Repository Architecture | `multimodal/` | 15 |
| [`187`](187-DATA-EVENT-REPO-ROADMAP-DOD.md) | §11.50 — Repository | `agents/` | 28 |
| [`196`](196-REPO-API-DB-AGENT.md) | §12.25 — Research Layer | `simulation-lab/` | 13 |
| [`196`](196-REPO-API-DB-AGENT.md) | §12.26 — Repository Phase 12 | **§12.26 — tujuh akar sekaligus** | 7 |
| [`198`](198-PHASE-13-IKHTISAR-DAN-HUMANOS-CORE.md) | §13.2 — HumanOS Core | `human-os/` | 18 |
| [`206`](206-REPO-SUBPHASE-DOD-DAN-POSISI.md) | §13.37 — Repository Architecture | `human-os/` | 14 |
| [`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) | §14.51 — Phase 14 Repository | `humanverse/` | 17 |
| [`226`](226-SDK-REPO-API-DATA-EVENT-DEPLOYMENT.md) | §15.25 — Repository Structure | `spatial-os/` | 21 |
| [`228`](228-PHASE-16-IKHTISAR-HRP-ABSTRAKSI.md) | §16.1 — HumanVerse Robotics Platform (HRP) | `robotics-platform/` | 14 |
| [`235`](235-DATA-EVENT-REPO-ROADMAP-DOD-POSISI.md) | §16.32 — Repository Structure | `robotics/` | 17 |
| [`244`](244-EVENT-DATABASE-API-REPO-RUNTIME.md) | §17.45 — Repository | `health-bio/` | 46 |
| [`245`](245-INTEGRASI-ROADMAP-DOD-DAN-EVOLUSI.md) | §17.51–§17.53 — Simulation Lab, Roadmap & Prioritas | `health-bio/research/` | 8 |
| [`254`](254-ARSITEKTUR-REPO-DATA-MODEL-DAN-API.md) | §18.27 — Repository Architecture | `global-intelligence/` | 23 |
| [`265`](265-REPO-DATABASE-API-MILESTONE-DOD-DAN-PHASE-20.md) | §19.30 — Repository Structure | `scientific-discovery/` | 24 |
| [`273`](273-API-EVENT-BUS-REPOSITORY-DAN-DATABASE.md) | §20.28 — Civilization Repository | `civilization-platform/` | 22 |

> §12.26 ([`196`](196-REPO-API-DB-AGENT.md)) adalah satu-satunya baris yang
> memberi **tujuh** akar dalam satu blok: `digital-twin/` · `world-model/` ·
> `causal-engine/` · `simulation/` · `decision-simulation/` ·
> `future-intelligence/` · `research/`. Lihat **E-101** /
> [#84](../../issues/84).

---

## Tabel B — nama direktori yang dipakai lebih dari satu pohon

Dari **424 nama direktori unik**, **128 dipakai oleh ≥ 2 pohon** —
**30 %**.

| | |
|---|---|
| nama unik seluruhnya | **424** |
| dipakai ≥ 2 pohon | **128** (30 %) |
| dipakai ≥ 3 pohon | **54** |
| dipakai tepat 2 pohon | 74 |

Yang dipakai **≥ 3 pohon**, lengkap:

| Direktori | Pohon | Di pohon mana |
|---|---|---|
| `sdk/` | **14** | `HumanVerse-X` · `civilization-platform` · `developer-platform` · `docs` · `global-intelligence` · `health-bio` · `human-os` · `humanverse-x` · `portal` · `robotics` · `robotics-platform` · `scientific-discovery` · `sdk` · `spatial-os` |
| `simulation/` | **13** | `agents` · `civilization-platform` · `cognitive-runtime` · `global-intelligence` · `health-bio` · `health-bio/research` · `humanverse-x` · `intelligence` · `research` · `robotics` · `robotics-platform` · `spatial-os` · `§12.26` |
| `agents/` | **10** | `agents` · `civilization-platform` · `docs` · `global-intelligence` · `health-bio` · `human-os` · `humanverse` · `humanverse-x` · `portal` · `scientific-discovery` |
| `memory/` | **8** | `agent-os` · `agent-sdk` · `agents` · `benchmarks` · `cognitive-runtime` · `human-os` · `humanverse-core` · `humanverse-x` |
| `evaluation/` | **7** | `agent-sdk` · `agents` · `cognitive-runtime` · `intelligence` · `prompts` · `research` · `simulation-lab` |
| `research/` | **7** | `civilization-platform` · `data-lake` · `global-intelligence` · `health-bio` · `humanverse` · `research` · `§12.26` |
| `runtime/` | **7** | `agent-sdk` · `agents` · `human-os` · `humanverse-x` · `robotics` · `robotics-platform` · `spatial-os` |
| `behavior/` | **6** | `benchmarks` · `data-lake` · `humanverse-core` · `humanverse-x` · `intelligence` · `research` |
| `privacy/` | **6** | `data-platform` · `global-intelligence` · `health-bio` · `multimodal` · `security` · `spatial-os` |
| `recommendation/` | **6** | `benchmarks` · `cognitive-runtime` · `health-bio` · `humanverse-x` · `intelligence` · `research` |
| `safety/` | **6** | `health-bio` · `prompts` · `robotics` · `robotics-platform` · `scientific-discovery` · `spatial-os` |
| `security/` | **6** | `HumanVerse-X` · `docs` · `global-intelligence` · `humanverse` · `humanverse-x` · `security` |
| `audit/` | **5** | `agents` · `civilization-platform` · `health-bio` · `humanverse-x` · `security` |
| `datasets/` | **5** | `HumanVerse-X` · `data-platform` · `health-bio/research` · `humanverse-x` · `scientific-discovery` |
| `docs/` | **5** | `HumanVerse-X` · `developer-platform` · `docs` · `humanverse-x` · `portal` |
| `events/` | **5** | `data-lake` · `data-platform` · `events` · `human-os` · `humanverse-x` |
| `experiments/` | **5** | `health-bio/research` · `intelligence` · `research` · `scientific-discovery` · `simulation-lab` |
| `identity/` | **5** | `agents` · `human-os` · `humanverse-core` · `humanverse-x` · `security` |
| `intelligence/` | **5** | `civilization-platform` · `health-bio` · `humanverse` · `humanverse-x` · `intelligence` |
| `permissions/` | **5** | `agents` · `human-os` · `humanverse-core` · `humanverse-x` · `security` |
| `planning/` | **5** | `agents` · `benchmarks` · `cognitive-runtime` · `intelligence` · `robotics-platform` |
| `world-model/` | **5** | `global-intelligence` · `humanverse` · `intelligence` · `research` · `§12.26` |
| `analytics/` | **4** | `data-lake` · `developer-platform` · `humanverse-x` · `portal` |
| `benchmarks/` | **4** | `benchmarks` · `health-bio/research` · `research` · `simulation-lab` |
| `context/` | **4** | `cognitive-runtime` · `human-os` · `humanverse-core` · `humanverse-x` |
| `edge/` | **4** | `health-bio` · `multimodal` · `robotics` · `robotics-platform` |
| `fashion/` | **4** | `benchmarks` · `humanverse-x` · `prompts` · `tools` |
| `goals/` | **4** | `data-lake` · `events` · `humanverse-core` · `humanverse-x` |
| `health/` | **4** | `events` · `humanverse-x` · `prompts` · `tools` |
| `ingestion/` | **4** | `data-platform` · `health-bio` · `multimodal` · `scientific-discovery` |
| `knowledge/` | **4** | `HumanVerse-X` · `cognitive-runtime` · `humanverse-x` · `intelligence` |
| `orchestrator/` | **4** | `HumanVerse-X` · `cognitive-runtime` · `humanverse-x` · `intelligence` |
| `prompts/` | **4** | `HumanVerse-X` · `docs` · `humanverse-x` · `prompts` |
| `registry/` | **4** | `agent-os` · `agents` · `health-bio` · `humanverse-x` |
| `agency/` | **3** | `cognitive-runtime` · `human-os` · `intelligence` |
| `api/` | **3** | `docs` · `humanverse-x` · `portal` |
| `consent/` | **3** | `health-bio` · `humanverse-core` · `security` |
| `digital-twin/` | **3** | `health-bio` · `humanverse` · `§12.26` |
| `embeddings/` | **3** | `HumanVerse-X` · `multimodal` · `research` |
| `forecasting/` | **3** | `health-bio` · `health-bio/research` · `simulation-lab` |
| `governance/` | **3** | `civilization-platform` · `data-platform` · `global-intelligence` |
| `graph/` | **3** | `data-platform` · `intelligence` · `research` |
| `lifestyle/` | **3** | `data-lake` · `events` · `humanverse-x` |
| `marketplace/` | **3** | `agents` · `developer-platform` · `humanverse-x` |
| `monte-carlo/` | **3** | `intelligence` · `scientific-discovery` · `simulation-lab` |
| `navigation/` | **3** | `robotics` · `robotics-platform` · `spatial-os` |
| `observability/` | **3** | `civilization-platform` · `human-os` · `humanverse-x` |
| `policies/` | **3** | `agent-os` · `agents` · `humanverse-x` |
| `prediction/` | **3** | `cognitive-runtime` · `humanverse-x` · `intelligence` |
| `provenance/` | **3** | `global-intelligence` · `multimodal` · `scientific-discovery` |
| `reasoning/` | **3** | `cognitive-runtime` · `humanverse-x` · `intelligence` |
| `state/` | **3** | `cognitive-runtime` · `human-os` · `intelligence` |
| `tools/` | **3** | `agent-os` · `agent-sdk` · `tools` |
| `trust/` | **3** | `civilization-platform` · `global-intelligence` · `security` |

Yang dipakai **tepat 2 pohon** (74 nama, tidak ditabelkan):

`activity/` · `agent-sdk/` · `agent-security/` · `ai/` · `apps/` · `architecture/` · `billing/` · `capabilities/` · `capability/` · `career/` · `causal/` · `cognitive-runtime/` · `data/` · `data-platform/` · `data-vault/` · `decision/` · `decisions/` · `desktop/` · `developer-platform/` · `docker/` · `examples/` · `execution/` · `feature-store/` · `federation/` · `feedback/` · `finance/` · `fitness/` · `flutter/` · `human-os/` · `infrastructure/` · `integration/` · `integrations/` · `intent/` · `knowledge-graph/` · `kotlin/` · `kubernetes/` · `locomotion/` · `manipulation/` · `mobile/` · `model-router/` · `models/` · `monitoring/` · `multimodal/` · `nutrition/` · `ontology/` · `orchestration/` · `pattern/` · `perception/` · `pipelines/` · `planner/` · `plugins/` · `portal/` · `preference/` · `profile/` · `protocols/` · `python/` · `quality/` · `recovery/` · `reputation/` · `ros/` · `sandbox/` · `scheduler/` · `simulation-lab/` · `social/` · `swift/` · `system/` · `terraform/` · `testing/` · `tests/` · `travel/` · `typescript/` · `understanding/` · `verification/` · `web/`

---

## 🔴 Yang berubah karena dihitung sekaligus: **hitungan berurutan meleset jauh**

Catatan audit melacak `simulation/` sebagai deret dan sampai pada
**“keenam kalinya”** di naskah 23 (**E-145**), dengan daftar
`spatial-os/` · `robotics/` · `health-bio/` · `global-intelligence/` · Phase 12.

Sensus atas seluruh `docs/` menemukan direktori bernama simulasi di
**lima belas pohon**:

| Pohon | Nama yang dipakai |
|---|---|
| `agents/` · `civilization-platform/` · `cognitive-runtime/` · `global-intelligence/` · `health-bio/` · `health-bio/research/` · `humanverse-x/` · `intelligence/` · `robotics/` · `robotics-platform/` · `spatial-os/` · `§12.26` | `simulation/` |
| `scientific-discovery/` | `simulations/` |
| `research/` ([`114`](114-PHASE-5-IKHTISAR.md)) | `simulation/` |
| `research/` ([`122`](122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md)) · `simulation-lab/` | `simulation-lab/` |
| `§12.26` | juga `decision-simulation/` |

**6 → 15.** Selisihnya bukan kesalahan siapa pun: tiap catatan hanya
membandingkan dengan pohon yang **kebetulan teringat saat itu**. Sembilan pohon
lain sudah lebih dulu memakai nama yang sama, dan tidak ada satu tempat pun
yang bisa memberi tahu.

> 💡 **Pelajaran yang bisa dipakai ulang:** menghitung *"ini yang ke berapa"*
> satu per satu, di berkas yang berbeda-beda, **secara sistematis meleset ke
> bawah**. Yang dibutuhkan bukan catatan yang lebih rajin, melainkan **satu
> sensus**. Pertanyaan yang berbuah bukan *"apakah ini duplikat?"* melainkan
> **"berapa banyak seluruhnya, dihitung sekali?"**

### Dan yang paling banyak diduplikasi ternyata bukan `simulation/`

| Direktori | Pohon | Pernah dicatat sebagai deret? |
|---|---|---|
| **`sdk/`** | **14** | ❌ tidak pernah — hanya disebut sebagai duplikat `developer-platform/` (**E-149**) |
| `simulation/` | 13 | ✅ dilacak, berhenti di 6 |
| **`agents/`** | **10** | ❌ hanya *“pohon tingkat-atas sejak naskah 2”*, tanpa angka |
| **`memory/`** | **8** | ❌ tidak pernah |
| `evaluation/` · `research/` · `runtime/` | 7 | ❌ tidak pernah |

`sdk/` muncul di **empat belas** pohon — lebih banyak daripada `simulation/`
yang sudah dilacak lima naskah berturut-turut, dan ia **tidak pernah sekali pun
dihitung**.

Terbit sebagai **[#146](../../issues/146)** (**E-151**).

---

## Tabel C — nama yang muncul dua kali **di dalam satu pohon**

Duplikasi lintas pohon bisa dibela: dua fase memang boleh punya `sdk/` sendiri.
Duplikasi **di dalam satu pohon** tidak — di sana ia berarti satu naskah
menaruh konsep yang sama di dua tempat sekaligus.

| Pohon | Nama | Di mana | Status |
|---|---|---|---|
| `security/` [`152`](152-REPO-DATA-MODEL-CONTROL-PLANE.md) | `consent/` | tingkat atas **dan** `privacy/consent/` | ✅ sudah dicatat (**E-73**) |
| `intelligence/` [`164`](164-ARSITEKTUR-REPO-ROADMAP-DOD.md) | `scenario/` | `world-model/` **dan** `simulation/` | 🆕 **belum pernah dicatat** |
| `intelligence/` [`164`](164-ARSITEKTUR-REPO-ROADMAP-DOD.md) | `counterfactual/` | `world-model/` **dan** `simulation/` | 🆕 **belum pernah dicatat** |
| `intelligence/` [`164`](164-ARSITEKTUR-REPO-ROADMAP-DOD.md) | `preference/` | `memory-engine/` **dan** `prediction/` | 🆕 **belum pernah dicatat** |

Ketiga yang baru terbit sebagai **[#147](../../issues/147)** (**G-20**).

> 🛑 **`scenario/` dan `counterfactual/` bukan dua nama yang kebetulan mirip —
> mereka pasangan yang sama, muncul utuh di dua modul bersebelahan dalam satu
> pohon.**
>
> ```
> ├── world-model/
> │   ├── state/  transition/  scenario/  counterfactual/
> ...
> ├── simulation/
> │   ├── scenario/  monte-carlo/  counterfactual/
> ```
>
> §9.38 memberi `world-model/` dan `simulation/` sebagai dua modul sejajar, dan
> keduanya memiliki skenario serta counterfactual. Pertanyaannya bukan gaya
> penamaan: **kalau pengguna bertanya *“bagaimana kalau saya tidur satu jam
> lebih lama?”*, modul mana yang menjawab, dan modul mana yang menyimpan
> jawabannya?** Selama dua-duanya ada, dua tim akan menulis dua mesin.
>
> Ini bentuk lokal dari **E-141** / [#130](../../issues/130) (*World Model
> lawan Global Twin*) dan **B-24** (*Counterfactual Engine tanpa sumber
> transisi*) — bedanya, di sini tabrakannya **di dalam satu diagram**, bukan
> antar-naskah.

### Yang diperiksa dan ternyata BUKAN cacat

Pemindai yang sama menandai enam nama ganda di
[`83`](83-STRUKTUR-REPO-FINAL.md) — `agents/` ×3, `security/` ×3, `api/`,
`events/`, `domain/`, `ai/`. **Semuanya sah**: induknya berbeda peran —
`agents/` (kode) lawan `prompts/agents/` (prompt) lawan `docs/agents/`
(dokumen); `platform/security/` lawan `tests/security/` lawan `docs/security/`.

⚠️ Dicatat di sini justru supaya pembaca berikutnya **tidak memperbaikinya**.
Pemindai duplikasi tanpa pemeriksaan induk akan menandainya lagi.

---

## Ejaan tunggal/jamak: satu konsep, dua folder

Di berkas nyata `simulation/` dan `simulations/` adalah **dua direktori**.
Sensus menemukan **16 pasangan** semacam itu. Sebagian sah (`decision/` sebagai
mesin lawan `decisions/` sebagai catatan ADR); yang tidak:

| Pasangan | Sebaran | Catatan |
|---|---|---|
| `simulation/` (13) lawan `simulations/` (1) | 14 pohon | `scientific-discovery/` sendirian memakai bentuk jamak |
| `benchmarks/` (4) lawan `benchmark/` (1) | 5 pohon | dan [`122`](122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md) memakai `benchmark-lab/` — bentuk ketiga |
| `world-model/` (5) lawan `world-models/` (1) | 6 pohon | `simulation-lab/` sendirian memakai bentuk jamak |
| `digital-twin/` (3) lawan `digital-twins/` (1) | 4 pohon | idem |
| `scenario/` lawan `scenarios/` · `counterfactual/` lawan `counterfactuals/` | 2 pohon | pasangan §9.38 lawan §12.25 |

> ⚠️ **`intents/` → `intent/` di [`206`](206-REPO-SUBPHASE-DOD-DAN-POSISI.md)
> BUKAN termasuk daftar ini** — naskahnya menyebut penggantian nama itu
> sendiri, jadi ia disengaja. Diperiksa satu per satu sebelum ditulis.

---

## Yang sensus ini **tidak** putuskan

Berkas ini tidak mengusulkan pohon final, tidak memilih nama, dan tidak
menutup satu butir pun. Usul yang berlaku tetap milik
[#55](../../issues/55), dan pertanyaan *“dikerjakan sekarang atau tidak”*
tetap milik [#139](../../issues/139) — keduanya keputusan pemilik.

Yang berubah hanya ini: kalau **Master Architecture v2.0** jadi dikerjakan,
langkah *“menghapus overlap antar-modul”* sekarang punya daftar yang bisa
dicoret satu per satu, dengan **128 nama** yang benar-benar bertabrakan —
bukan ingatan tentang sepuluh catatan di sepuluh berkas.

---

## Cara membangun ulang angka di berkas ini

Skrip pengukur **sengaja tidak disimpan di repo** — repo ini berkas kode nol,
dan itu disengaja. Metodenya ditulis lengkap di bagian
[*Cara mengukur*](#cara-mengukur-dan-apa-yang-tidak-terhitung) supaya siapa pun
bisa menulis ulang pemeriksanya dan mendapat angka yang sama.

Pemeriksaan yang harus lulus:

| Pemeriksaan | Hasil |
|---|---|
| Blok pohon di `docs/` | **38** di **36** dokumen |
| Nama direktori unik | **424** |
| Nama dipakai ≥ 2 pohon | **128** (30 %) |
| Nama dipakai ≥ 3 pohon | **54** |
| Pohon memuat direktori bernama simulasi | **15** |
| Duplikasi di dalam satu pohon, sesudah induk diperiksa | **4** (1 lama, 3 baru) |
