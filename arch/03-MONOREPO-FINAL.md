# 03 — Monorepo Final & Penghapusan Overlap

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab dua butir naskah 24 sekaligus: *“menghapus overlap antar-modul”* dan
> *“monorepo final”*. Menutup [#109](../../issues/109) · [#120](../../issues/120)
> · [#129](../../issues/129) · [#130](../../issues/130) · [#138](../../issues/138)
> · [#143](../../issues/143) — yaitu deret **H-10 yang tergerus sepuluh kali**.

---

## §1 Titik awal, dan apa yang berubah darinya

Titik awalnya **bukan** salah satu dari 38 pohon fase, melainkan
[`../docs/83`](../docs/83-STRUKTUR-REPO-FINAL.md) — pohon `humanverse-x/`
(85 subdirektori) dari naskah 5. Alasannya tiga:

1. ia satu-satunya pohon yang **bukan milik sebuah fase** (naskah 5 tidak
   memetakan ke fase mana pun — [`01`](01-PETA-20-FASE.md) §5);
2. ia yang **ditunjuk Sprint 0 tugas 0.1** ([`../spec/07`](../spec/07-BACKLOG-V0.md));
3. ia satu-satunya yang punya `apps/`, `packages/`, `tests/`, `infrastructure/`
   — kerangka repo, bukan daftar fitur.

**Empat perubahan terhadapnya**, semuanya turunan
[K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md):

| # | Perubahan | Alasan |
|---|---|---|
| 1 | `platform/security/` + `platform/audit/` → **`security/` tingkat-atas** | §8.42 (*kode agent tidak boleh mengimpor `security/`*) menuntut **satu** `security/` untuk dirujuk. Selama ada 19 pohon keamanan, aturan itu tak bisa **dinyatakan**, apalagi ditegakkan |
| 2 | **`governance/` tingkat-atas, di luar `security/`** | *security menjawab apa yang boleh, governance menjawab siapa yang memutuskan*. Dan `governance/` di dalam pohon fase terbukti **tidak diwarisi** — tiga kali ([#138](../../issues/138)) |
| 3 | `packages/sdk/` → **`sdk/` tingkat-atas** | ia artefak yang **diterbitkan** dengan daur rilisnya sendiri; 14 pohon memilikinya |
| 4 | `platform/events/` → **`events/` tingkat-atas** | ia bus **dan** schema registry; menaruhnya di dalam `platform/` membuat `platform` tahu bentuk domain |

⚠️ **Sisanya dipertahankan apa adanya.** `apps/` · `services/` · `packages/` ·
`prompts/` · `tests/` · `infrastructure/` · `docs/` · `data/` tidak disentuh.

---

## §2 Prosedur — uji naik-turun, dan syarat sebelum menjalankannya

[K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md) keputusan 2, apa adanya:

| Kalau… | Maka |
|---|---|
| dua fase memakai nama itu untuk hal yang **SAMA** | **NAIK** ke tingkat atas, dipakai bersama — tidak disalin |
| hanya satu fase membutuhkannya | **TINGGAL** di dalam fase |
| dua fase memakai nama yang sama untuk hal yang **BERBEDA** | **GANTI NAMA** salah satunya — tidak digabung, tidak dibiarkan |

### 🔑 Satu syarat yang harus diperiksa lebih dulu, dan tidak ada di K-9

> **Uji ini hanya dijalankan atas nama yang dipakai TANPA induknya.**

Sebabnya terukur. `runtime/` ada di **7** pohon, tetapi tidak seorang pun pernah
menulis *“Runtime Engine”* tanpa menyebut runtime **apa** — ia selalu *“agent
runtime”* atau *“robot runtime”*. Sebaliknya `simulation/` ditulis telanjang:
[#130](../../issues/130) merekam *“**Simulation Engine** dengan lima arti”*.

| Nama | Pernah ditulis telanjang di naskah/audit? | Uji dijalankan? |
|---|---|---|
| `simulation` · `state` · `planning` · `registry` · `graph` · `memory` · `sandbox` · `kill` · `research` · `navigation` · `identity` | ✅ ya | **ya** |
| `runtime` · `api` · `docs` · `health` · `fashion` · `lifestyle` | ❌ tidak — selalu dengan induknya | **tidak** — induk sudah mengualifikasi |

⇒ Ini juga yang menjelaskan **6 dari 10 positif palsu** pemindai duplikasi
sebelumnya ([`../docs/SENSUS-MODUL.md`](../docs/SENSUS-MODUL.md) Tabel C):
`tools/health/` dan `prompts/health/` tidak pernah bertabrakan dalam percakapan,
karena tak seorang pun menyebutnya *“modul health”*.

---

## §3 Pohon final

**28 folder tingkat-atas.** Yang bergaris bawah adalah **bounded context**
([`02`](02-BOUNDED-CONTEXT.md)); sisanya kerangka repo.

```
humanverse-x/
│
├── apps/                mobile · web · desktop · admin · api
│
├── services/            ← human-core + domain vertikal
│   ├── identity/  profile/  goals/  habits/  checkins/  journal/  activities/
│   └── health/  fitness/  nutrition/  fashion/  wardrobe/  grooming/
│       lifestyle/  career/  learning/  finance/  social/  travel/
│
├── events/              bus/  schema-registry/  projections/  replay/
├── memory/              store/  retrieval/  extraction/  decay/  tiers/  scopes/
├── context/             builder/  scope-filter/  ranker/  sanitizer      ← nol tabel
│
├── intelligence/        reasoning/  planning/  patterns/  prediction/  forecasting/
│                        recommendation/  behavior-model/  preference-model/
│                        personalization/  digital-twin/  sim-behavior/
│                        model-registry/  collective/
│
├── knowledge/           graph/  ontology/  provenance/  evidence/  ranking/
│
├── world-model/         world-state/  transition/  entities/  relationships/
│                        civilization-twin/  early-warning/  global-risk/
│
├── simulation/          ← MESIN BERSAMA, bukan sebuah simulator
│                        scenario/  counterfactual/  assumption/  monte-carlo/
│                        seed/  determinism/  isolation/  engine-api/
│
├── agents/              runtime/  registry/  manifests/  factory/  orchestrator/
│                        agency/  execution/  watchdog/  recovery/  sandbox/
│                        agent-identity/  agent-graph/  approvals/  budgets/
│                        reputation/  communication/  negotiation/  delegation/
│
├── tools/               registry/  adapters/  mcp/  test-harness/
│
├── perception/          capture/  vision/  audio/  wifi-csi/  fusion/
│                        summarizer/  perception-state/  privacy-filter/
│
├── spatial/             slam/  mapping/  localization/  scene-graph/  anchors/
│                        navigation/  object-tracking/  human-tracking/  xr-ui/
│
├── embodiment/          drivers/  ros/  locomotion/  manipulation/
│                        motion-planning/  obstacle/  skills/  fleet/
│                        smart-home/  sim-physics/  safety-kernel/
│
├── health-bio/          clinical/  biometrics/  medical-records/  sim-physiology/
├── civilization/        coordination/  resilience/  sustainability/  resource-intel/
│
├── security/            ← SATU pohon; menyerap sembilan keluarga
│                        policy-engine/  risk-engine/  permissions/  consent/
│                        privacy/  vault/  audit/  safety/  trust/  compliance/
│                        ethics/  kill-switch/  quarantine/  threat-model/
│
├── governance/          constitution/  contracts/  risk-agent/  disagreement/
│                        sovereignty/  escalation/
│
├── platform/            runtime/  edge/  observability/  model-router/  gateway/
│                        notifications/  search/  analytics/  billing/  jobs/
│                        federation/  protocols/  marketplace/
│
├── research/            experiments/  hypothesis/  literature/  benchmarks/
│                        papers/  labs/{health,robot,climate,materials}/
│
├── evaluation/          evaluators/  metrics/  scenario-runs/  red-team/
│                        certification/  harness/
│
├── sdk/                 python/  typescript/  flutter/  kotlin/  swift/
│                        spatial/  robotics/  agent/
│
├── data/                migrations/  seeds/  pipelines/  datasets/  feature-store/
│                        lakehouse/  embeddings/  ingestion/  quality/  lineage/
│
├── packages/            domain/  contracts/  events/  ai/  common/
├── prompts/             system/  agents/  evaluators/  versions/
├── tests/               unit/  integration/  e2e/  ai/  security/  performance/
├── infrastructure/      docker/  kubernetes/  terraform/  monitoring/
└── docs/                architecture/  api/  agents/  domain/  security/  decisions/
```

### ⭐ Kenapa `simulation/` menjadi mesin bersama, bukan salah satu simulator

Nama yang paling banyak berulang di seluruh repo (**13 pohon**) ternyata
**lima mesin** ([`02`](02-BOUNDED-CONTEXT.md) §4). Tetapi ketika kelimanya
dibandingkan isi per isi, yang **berbeda** hanya mesin fisikanya; yang **sama**
justru bagian yang paling penting untuk dijaga:

| Sama di kelima | Berbeda |
|---|---|
| `scenario` · `counterfactual` · `assumption` · `monte-carlo` · **`seed`** · **determinisme** · **isolasi dari data nyata** | model fisika · model perilaku · model fisiologi · model masyarakat |

⇒ **Yang naik adalah bagian yang samanya; yang tinggal adalah mesinnya.**

```
simulation/                        ← scenario · counterfactual · seed · ISOLASI
    ▲          ▲          ▲          ▲
    │          │          │          │   (engine-api)
embodiment/  intelligence/  health-bio/  civilization/
sim-physics/ sim-behavior/  sim-physiology/ sim-society/
```

> 🔑 **Dan pemecahan ini yang membuat §12.16 bisa ditegakkan.** Aturan
> *“simulasi tidak boleh mengubah data dunia nyata”* adalah salah satu dari
> empat batas keras repo ini. Selama ada lima simulator, ia harus ditegakkan
> **lima kali** dan akan gagal di salah satunya. Dengan isolasi di mesin
> bersama, ia satu pemeriksaan CI ([`11`](11-PENEGAKAN.md) B-3).

---

## §4 Vonis 54 nama yang dipakai ≥ 3 pohon

**NAIK 38 · TINGGAL 6 · GANTI NAMA 9 · PECAH 1.**

| Nama | Pohon | Vonis | Menjadi |
|---|---|---|---|
| `sdk/` | 14 | **NAIK** | `sdk/` — submodul per bahasa & per domain |
| `simulation/` | 13 | **PECAH** | `simulation/` (mesin) + 4 plugin bernama |
| `agents/` | 10 | **NAIK** | `agents/` — 5 kemunculan lain adalah **faset** (`docs/`, `prompts/`, `portal/`) |
| `memory/` | 8 | **NAIK** | `memory/` — 2 faset sah; `embodiment/` memakai `skills/` |
| `evaluation/` | 7 | **NAIK** | `evaluation/` |
| `research/` | 7 | **NAIK** | `research/` — satu organisasi riset, banyak domain (`labs/`) |
| `runtime/` | 7 | **TINGGAL** | induk mengualifikasi — §2 |
| `behavior/` | 6 | **NAIK** | `intelligence/behavior-model/` |
| `privacy/` | 6 | **NAIK** | `security/privacy/` |
| `recommendation/` | 6 | **NAIK** | `intelligence/recommendation/` |
| `safety/` | 6 | **GANTI NAMA** | `security/safety/` (aturan) **vs** `embodiment/safety-kernel/` (waktu-nyata, di tepi) — lihat §5 |
| `security/` | 6 | **NAIK** | `security/` |
| `audit/` | 5 | **NAIK** | `security/audit/` |
| `datasets/` | 5 | **NAIK** | `data/datasets/` |
| `docs/` | 5 | **NAIK** | `docs/` |
| `events/` | 5 | **NAIK** | `events/` |
| `experiments/` | 5 | **NAIK** | `research/experiments/` |
| `identity/` | 5 | **GANTI NAMA** | `services/identity/` (**manusia**) **vs** `agents/agent-identity/` (**agent**) — lihat §5 |
| `intelligence/` | 5 | **NAIK** | `intelligence/` |
| `permissions/` | 5 | **NAIK** | `security/permissions/` |
| `planning/` | 5 | **GANTI NAMA** | `intelligence/planning/` (tugas) **vs** `embodiment/motion-planning/` (lintasan) |
| `world-model/` | 5 | **NAIK** | `world-model/` — menutup [#130](../../issues/130), lihat §5 |
| `analytics/` | 4 | **NAIK** | `platform/analytics/` |
| `benchmarks/` | 4 | **NAIK** | `evaluation/benchmarks/` |
| `context/` | 4 | **NAIK** | `context/` |
| `edge/` | 4 | **NAIK + ATRIBUT** | `platform/edge/` (runtime) — “berjalan di tepi” menjadi **atribut deployment**, bukan folder di tiap pohon ([`09`](09-DEPLOYMENT-TOPOLOGY.md)) |
| `fashion/` | 4 | **TINGGAL** | faset sah |
| `goals/` | 4 | **NAIK** | `services/goals/` |
| `health/` | 4 | **TINGGAL** | faset sah — ≠ `health-bio/` (klinis) |
| `ingestion/` | 4 | **GANTI NAMA** | `data/ingestion/` (batch/ETL) **vs** `perception/capture/` (waktu-nyata) |
| `knowledge/` | 4 | **NAIK** | `knowledge/` |
| `orchestrator/` | 4 | **NAIK** | `agents/orchestrator/` |
| `prompts/` | 4 | **NAIK** | `prompts/` |
| `registry/` | 4 | **GANTI NAMA** | 4 arti → `agents/registry/` · `tools/registry/` · `events/schema-registry/` · `intelligence/model-registry/` |
| `agency/` | 3 | **NAIK** | `agents/agency/` |
| `api/` | 3 | **TINGGAL** | faset sah |
| `consent/` | 3 | **NAIK** | `security/consent/` |
| `digital-twin/` | 3 | **GANTI NAMA** | `intelligence/digital-twin/` (**orang**) **vs** `world-model/civilization-twin/` (**dunia**) |
| `embeddings/` | 3 | **NAIK** | `data/embeddings/` |
| `forecasting/` | 3 | **NAIK** | `intelligence/forecasting/` |
| `governance/` | 3 | **NAIK** | `governance/` — berdiri sendiri |
| `graph/` | 3 | **GANTI NAMA** | `knowledge/graph/` · `spatial/scene-graph/` · `agents/agent-graph/` |
| `lifestyle/` | 3 | **TINGGAL** | faset sah |
| `marketplace/` | 3 | **NAIK** | `platform/marketplace/` — §20.32 sendiri sudah menggabungkan tiga pasar |
| `monte-carlo/` | 3 | **NAIK** | `simulation/monte-carlo/` |
| `navigation/` | 3 | **NAIK** | `spatial/navigation/` — `embodiment/` **memakainya**, tidak menyalinnya |
| `observability/` | 3 | **NAIK** | `platform/observability/` |
| `policies/` | 3 | **NAIK** | `security/policies/` |
| `prediction/` | 3 | **NAIK** | `intelligence/prediction/` |
| `provenance/` | 3 | **NAIK** | `knowledge/provenance/` |
| `reasoning/` | 3 | **NAIK** | `intelligence/reasoning/` |
| `state/` | 3 | **GANTI NAMA** | 4 arti → `human-state` · `world-state` · `session-state` · `perception-state` |
| `tools/` | 3 | **NAIK** | `tools/` |
| `trust/` | 3 | **NAIK** | `security/trust/` |

---

## §5 Empat vonis yang bukan sekadar kerapian

### `safety/` — dan kenapa ia satu-satunya keluarga keamanan yang TIDAK naik seluruhnya

Delapan keluarga keamanan naik utuh ke `security/`. `safety/` **tidak**, dan
alasannya bukan selera:

| | `security/safety/` | `embodiment/safety-kernel/` |
|---|---|---|
| menjawab | **aturan apa yang berlaku** | **hentikan sekarang** |
| berjalan di | cloud / server | **perangkat itu sendiri** |
| anggaran waktu | ratusan ms | **milidetik** |
| ketika jaringan putus | tidak bisa dihubungi | **tetap bekerja** |

🛑 §16.20 mendaftarkan **`communication loss`** sebagai salah satu pemicu
darurat. Pengaman darurat yang hidup di cloud akan **mati justru pada
pemicunya**. §16.21 sudah menaruh `emergency` di tepi; berkas ini menarik
konsekuensi yang belum ditulis: **Safety Kernel juga.**

⭐ Dan itu sekaligus menjawab **B-32** ([#110](../../issues/110)). §16.22
menggambar `HumanVerse → ROS Adapter → ROS2 → Robot`, sehingga siapa pun yang
bisa bicara ke ROS2 menggerakkan robot **tanpa** melewati pengaman di sisi
HumanVerse. Nyata, sebab DDS ROS 2 bawaan menerima peserta se-jaringan tanpa
autentikasi kuat, dan alat diagnostik pabrikan bicara langsung ke lapisan itu.

🔧 **Tiga aturan yang menutupnya, dan ketiganya soal LETAK, bukan kebijakan:**

| # | Aturan | Kenapa letak, bukan aturan |
|---|---|---|
| 1 | **`embodiment/safety-kernel/` berada DI BAWAH adapter, di sisi robot** | jalur pintas tertutup **secara fisik** — tidak ada jalan dari ROS 2 ke aktuator yang tidak melewatinya |
| 2 | **domain ROS 2 terisolasi, SROS 2 menyala** (autentikasi & enkripsi DDS) | tanpa ini, “se-jaringan” berarti siapa pun di jaringan yang sama |
| 3 | **Emergency Stop bukan pesan ROS biasa** — ia jalur terpisah di `safety-kernel/`, tidak antre di belakang lalu lintas ROS | rem yang menunggu giliran bukan rem |

⚠️ Dan `POST /v1/robot/emergency-stop` §16.29 lewat HTTP **hilang saat jaringan
putus** — yaitu pemicu darurat nomor empat §16.20. Ia **kenyamanan, bukan
pengaman**.

### `identity/` — manusia dan agent bukan hal yang sama

`agents/identity/` (§11.50) dan `services/identity/` sama-sama menyimpan *siapa
ini*. Tetapi:

- manusia punya **hak** (hapus data, override, persetujuan);
- agent punya **kewenangan** (dipinjamkan, berjangka, bisa dicabut).

Menyatukannya berarti tabel yang menjawab *“siapa yang boleh menghapus akun
ini”* dan tabel yang menjawab *“agent ini boleh bertindak atas nama siapa”*
hidup di satu modul. ⇒ **`agents/agent-identity/`**, dan tak pernah bare
`identity/` di dalam `agents/`.

> ⚠️ Ini juga permukaan teknis untuk **Pasal 8 Konstitusi** (*no deceptive
> behavior*) dan **C-19** ([#81](../../issues/81)): penerima pesan berhak tahu
> ia bicara dengan agent. Selama identitas agent adalah kolom di tabel identitas
> manusia, pertanyaan itu tidak punya tempat untuk dijawab.

### `world-model/` — menutup [#130](../../issues/130)

*World Model* (Phase 12) dan *Global Twin* (Phase 18) dicatat sebagai dua nama
untuk hal yang mungkin sama. Uji naik-turun menjawabnya: keduanya menyimpan
**keadaan dunia di luar penggunanya**, berbeda hanya pada **skala**. Skala bukan
alasan membuat modul kedua — ia alasan membuat **partisi**.

⇒ satu `world-model/`, dengan `civilization-twin/` sebagai submodul, dan
`intelligence/digital-twin/` (kembaran **orang**) tetap terpisah. Tiga nama, dua
benda, satu batas yang jelas.

### `edge/` — sebuah folder yang seharusnya sebuah atribut

`edge/` muncul di 4 pohon dan setiap kemunculannya berarti hal yang sama:
*“bagian ini berjalan di perangkat”*. Itu **properti deployment**, bukan modul.
Empat folder `edge/` berarti empat runtime tepi, dan pengaman yang harus tetap
hidup ketika segalanya gagal akan bergantung pada empat implementasi.

⇒ **satu `platform/edge/`**, dan tiap modul menyatakan `deploy: edge | cloud |
both` di manifestnya ([`09`](09-DEPLOYMENT-TOPOLOGY.md) §3).

---

## §6 74 nama yang dipakai tepat 2 pohon — diselesaikan aturan, bukan satu per satu

Memutuskan 74 nama tanpa kode yang memakainya berarti menebak. Yang ditetapkan
di sini **prosedurnya**, dan ia dijalankan **saat pohonnya benar-benar dibangun**:

```
untuk tiap nama N yang muncul di 2 pohon:
  1. apakah N pernah ditulis TANPA induknya di docs/ atau di audit?
     tidak → SELESAI, biarkan (induk mengualifikasi)
  2. apakah kedua kemunculan menjawab pertanyaan yang sama?
     ya   → NAIK ke konteks pemiliknya (02-BOUNDED-CONTEXT.md §3)
     tidak→ GANTI NAMA yang lebih muda; yang lebih tua menyimpan namanya
```

⚠️ **Langkah 3 memakai “yang lebih muda”, bukan “yang lebih tepat”** — sama
dengan [K-4](../docs/KEPUTUSAN-DIDELEGASIKAN.md) untuk tabel. Menilai mana yang
lebih tepat adalah selera; usia bisa diperiksa.

**Enam yang sudah bisa divonis sekarang** karena sudah tercatat sebagai
tabrakan di audit:

| Nama | Vonis |
|---|---|
| `agent-security/` | **DIHAPUS** — diserap `security/`; keberadaannya yang membuat §8.42 ambigu (**E-121**) |
| `delegation/` (muncul 2× di satu pohon, §14.51) | **SATU** — `agents/delegation/` |
| `protocols/` + `provenance/` (2× di pohon yang sama, §18.27) | **SATU** masing-masing — `platform/protocols/`, `knowledge/provenance/` |
| `decision/` vs `decisions/` | **SAH** — mesin lawan catatan ADR (`docs/decisions/`) |
| `intent/` vs `intents/` | **SAH** — naskah [`206`](../docs/206-REPO-SUBPHASE-DOD-DAN-POSISI.md) menyebut penggantian namanya sendiri |
| `model-router/` | **NAIK** — `platform/model-router/`, memulihkan yang **E-79** ([#69](../../issues/69)) catat hilang |

---

## §7 Tunggal/jamak — satu konsep, satu ejaan

Di berkas nyata `simulation/` dan `simulations/` adalah **dua direktori**.
Sensus menemukan **16 pasangan**.

🔧 **Aturan: nama direktori memakai bentuk TUNGGAL**, kecuali ia jelas-jelas
kumpulan artefak yang dihitung (`tests/`, `docs/`, `migrations/`, `seeds/`,
`prompts/`, `datasets/`, `experiments/`).

| Pasangan | Menjadi |
|---|---|
| `simulation/` · `simulations/` | `simulation/` |
| `world-model/` · `world-models/` | `world-model/` |
| `digital-twin/` · `digital-twins/` | `digital-twin/` |
| `benchmark/` · `benchmarks/` · `benchmark-lab/` | `benchmarks/` ⁽¹⁾ |
| `scenario/` · `scenarios/` | `scenario/` |
| `counterfactual/` · `counterfactuals/` | `counterfactual/` |

⁽¹⁾ pengecualian yang disengaja — ia kumpulan artefak.

---

## §8 🛑 Nol perubahan untuk V0

Diperiksa baris per baris terhadap
[`../spec/06`](../spec/06-MODULE-BOUNDARIES.md):

| `spec/06` | Pohon final |
|---|---|
| `apps/api/src/modules/identity/` | `services/identity/` — **nama sama** |
| `…/profile · goals · habits · checkins · journal · activities` | `services/*` — **nama sama** |
| `…/events · memory · intelligence · agents` | `events/` · `memory/` · `intelligence/` · `agents/` — **naik satu tingkat, nama sama** |
| `…/platform` | `platform/` — **nama sama** |

⇒ **V0 tetap modular monolith dengan 12 modul yang sama.** Yang berubah hanya
**letak** modul di monorepo ketika V0 tumbuh melewati satu proses — dan itu
justru jalan keluar yang `spec/06` sudah rancang (*“ketika satu modul perlu
dipisah jadi service”*).

⚠️ **Satu-satunya penyesuaian:** `spec/06` menaruh `platform` sebagai modul yang
boleh dipakai semua. Di pohon final, `security/` **keluar** dari `platform/`.
Untuk V0 itu nol biaya (belum ada `security/` sebagai kode); untuk V1+ ia
prasyarat §8.42.

---

## §9 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Folder tingkat-atas | **28** |
| Pohon keamanan | **1** — turun dari **19** |
| `governance/` di dalam pohon fase | **NIHIL** |
| Nama dipakai bare di >1 tempat | **NIHIL** — tiap entri kamus [`02`](02-BOUNDED-CONTEXT.md) §4 punya nama final |
| Nama di §4 tanpa vonis | **NIHIL** — 54 dari 54 |
| Direktori bernama `simulation/` | **1** (mesin) + 4 plugin **bernama berbeda** |
| Modul V0 yang berganti nama | **NIHIL** — §8 |
| Pasangan tunggal/jamak tersisa | **NIHIL** dari 6 yang tidak sah |
| Aturan komposisi untuk pohon ke-39 | ✅ ada — §2 + §6, mekanis |
