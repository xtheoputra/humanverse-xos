# 196 — §12.25–§12.29 Research Layer, Repository, API, Database & Agent

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.25 — Research Layer

```
simulation-lab/
├── scenarios/       ├── monte-carlo/     ├── replay/
├── causal-models/   ├── optimization/    └── evaluation/
├── counterfactuals/ ├── experiments/
├── world-models/    ├── benchmarks/
├── digital-twins/   ├── forecasting/
```

---

## §12.26 — Repository Phase 12

```
digital-twin/         world-model/        causal-engine/
simulation/           decision-simulation/
future-intelligence/  research/
```

---

> 🛑🛑 **TUJUH pohon tingkat-atas sekaligus — dan LIMA di antaranya ditarik
> keluar dari `intelligence/` naskah 13.**
>
> Sebelum ini setiap naskah menambah **satu** pohon. Naskah 16 menambah tujuh,
> dan lima di antaranya bukan folder baru melainkan **folder yang dipindahkan
> keluar** dari pohon yang baru didefinisikan tiga naskah lalu:
>
> | §12.26 | Sebelumnya di `intelligence/` §9.38 |
> |---|---|
> | `world-model/` | ✅ `intelligence/world-model/` |
> | `simulation/` | ✅ `intelligence/simulation/` |
> | `decision-simulation/` | ✅ `intelligence/decision/` |
> | `future-intelligence/` | ✅ `intelligence/prediction/` |
> | `causal-engine/` | ✅ `intelligence/reasoning/causal/` |
> | `digital-twin/` | 🆕 benar-benar baru |
> | `research/` | ⚠️ **sudah ada** sebagai pohon tingkat-atas sejak naskah 9 — didefinisikan ulang dengan isi berbeda |
>
> Butir **E-79** mencatat naskah 13 **membuang empat folder** dari
> `intelligence/`; sekarang naskah 16 **mengeluarkan lima lagi**. Dari lima
> belas kelompok yang §9.38 tetapkan, tersisa sembilan.
>
> Total pohon tingkat-atas: `humanverse-x/` · `research/` ·
> `developer-platform/` · `data-platform/` · `security/` · `intelligence/` ·
> `multimodal/` · `agents/` + tujuh di atas = **lima belas**. Delapan naskah
> berturut-turut menyentuh struktur repo, dan Sprint 0 tugas 0.1 masih
> menunggu ([#55](../../issues/55)). Lihat **E-101** / [#84](../../issues/84).

> 🛑 **Dan §12.25 menduplikasi §12.26 di dalam naskah yang sama.**
> `simulation-lab/` berisi `scenarios/`, `causal-models/`, `counterfactuals/`,
> `world-models/`, `digital-twins/`, `forecasting/`, `monte-carlo/`,
> `optimization/`, `replay/`, `evaluation/` — **sepuluh dari dua belasnya**
> punya padanan langsung di tujuh pohon §12.26.
>
> Pola **E-54** (dua pohon `research/` di naskah 9) yang berulang untuk ketiga
> kalinya. ⭐ Tapi kali ini pembagiannya **jelas dan sudah pernah saya usulkan**:
> `-lab` adalah tempat mencari cara, pohon produksi adalah tempat
> menjalankannya. Tinggal ditulis sebagai aturan — dan `simulation-lab/`
> sebaiknya berada **di dalam** `research/`, bukan sejajar dengannya.

---

## §12.27 — API

```
POST /v1/twin/snapshot        POST /v1/simulation/run
GET  /v1/twin/state           POST /v1/simulation/scenario
GET  /v1/twin/history         POST /v1/simulation/counterfactual

POST /v1/decision/simulate    GET  /v1/future/projection
POST /v1/decision/compare     GET  /v1/future/uncertainty

POST /v1/causal/query         POST /v1/causal/intervention
```

---

> ⚠️ **`/v1/...` lagi** — naskah 7, 10, 14, dan sekarang 16 memakai `/v1/`,
> sementara [`../spec/04`](../spec/04-API-CONTRACTS.md) memakai `/api/v1/`.
> **Empat naskah lawan satu spesifikasi**; yang menyimpang adalah spesifikasi
> saya, dan sebaiknya diselaraskan sebelum endpoint pertama ditulis.

> ⭐ **`POST /v1/decision/compare` — kata kerjanya `compare`, bukan `decide`.**
> Konsisten dengan §12.11 yang berakhir di `Recommendation` dan §12.12 yang
> menolak menyatakan pemenang. Penamaan endpoint yang menjaga disiplin.

> ⚠️ **`POST /v1/causal/intervention` adalah endpoint yang paling perlu
> dijaga.** *Intervention* dalam arti kausal berarti *"paksa variabel X ke
> nilai ini, lalu hitung akibatnya"* — dan itu operasi **simulasi**, bukan
> operasi dunia nyata. Namanya bisa dibaca sebagai keduanya. Kalau ia menyentuh
> apa pun di luar sandbox §12.16, ia melanggar batas *"simulation tidak boleh
> mengubah data dunia nyata"*.

---

## §12.28 — Database

**Twin:** `digital_twins` · `twin_snapshots` · `twin_states` · `twin_versions`

**World:** `world_entities` · `world_relationships` · `world_states` ·
`world_events`

**Causal:** `causal_graphs` · `causal_nodes` · `causal_edges` ·
`causal_interventions`

**Simulation:** `simulation_runs` · `simulation_scenarios` ·
`simulation_parameters` · `simulation_assumptions` · `simulation_outcomes`

**Future:** `counterfactual_runs` · `future_projections` ·
`uncertainty_estimates`

**Decision:** `decision_models` · `decision_options` · `decision_outcomes` ·
`utility_models`

**Evaluation:** `simulation_evaluations` · `prediction_errors`

---

> 🛑 **Dua puluh enam tabel baru — hitungannya sekarang 99.**
>
> | | Tabel |
> |---|---|
> | V0 ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)) | **23** |
> | + Fase 8 · 10 · 11 | 73 |
> | + Fase 12 §12.28 | **99** |
>
> Bertaut **A-25** / [#58](../../issues/58). ⭐ Dan seperti Fase 10 dan 11:
> **nol dari 26 dibutuhkan V0** — tidak ada satu pun dari 12 fitur V0 yang
> menjalankan simulasi.

> ⭐⭐ **`simulation_assumptions` dan `prediction_errors` adalah dua tabel yang
> paling menentukan**, dan keduanya menunjukkan bahwa §12.14 dan §12.20
> dirancang untuk dipakai, bukan disebut. Tanpa yang pertama, asumsi hilang
> setelah simulasi selesai; tanpa yang kedua, loop belajar tidak punya bahan.

> ⚠️ **`utility_models` akhirnya punya tabel** — §9.25 memperkenalkan Personal
> Utility Model tanpa satu pun tabel. Itu berarti bobot pengguna **tersimpan**,
> yang merupakan prasyarat untuk *"user dapat mengubahnya"* ([#71](../../issues/71)).

> ⚠️ **`world_states` berdampingan dengan `human_states`** (spec/01) — dua tabel
> keadaan, dan §12.2 menyebut keadaan twin sebagai `twin_states`. **Tiga tabel
> keadaan**: manusia, twin, dunia. Kemungkinan besar `twin_states` dan
> `human_states` adalah benda yang sama dengan dua nama; kalau ya, satu dibuang.

> ⚠️ **`simulation_*` menduplikasi tiga tempat lain:** `intelligence/simulation/`
> (§9.38), `research/simulation-lab/` (naskah 9), dan `agents/simulation/`
> (§11.50). Empat tempat untuk satu gagasan.

---

## §12.29 — Agent yang diperlukan

```
DigitalTwinAgent      ScenarioAgent        ForecastingAgent
WorldModelAgent       SimulationAgent      OptimizationAgent
CausalReasoningAgent  CounterfactualAgent  DecisionSimulationAgent
RiskSimulationAgent   LifePlanningAgent    SimulationEvaluatorAgent
```

> Tetapi **jangan membuat semuanya sebagai autonomous agent sejak awal.
> Sebagian lebih baik sebagai deterministic/model services.**

---

> ⭐⭐⭐ **Kalimat peringatan itu adalah pertama kalinya dalam enam belas naskah
> sebuah naskah memperingatkan agar sesuatu TIDAK dijadikan agent.**
>
> Dan ia datang tepat waktu. Hitungan agent: 14 (naskah 4) → 22 (naskah 5) →
> 25 berhierarki (§11.4) + **tujuh yang muncul di contoh tanpa terdaftar**
> (**E-95**) + dua belas di sini = **lebih dari empat puluh**. Butir **B-12**
> mencatat bahwa ratusan agent pada satu graf akan saling menimpa tanpa aturan
> kepemilikan simpul — dan naskah 5 §58 sudah memperingatkan *"jangan langsung
> 50 agent"*.
>
> Peringatan ini juga benar secara teknis: `SimulationAgent` dan
> `ForecastingAgent` **deterministik** — masukan yang sama menghasilkan
> keluaran yang sama (itu justru yang §12.17 janjikan lewat snapshot). Sesuatu
> yang deterministik tidak butuh otonomi, tidak butuh `autonomy.max_level`,
> tidak butuh watchdog, dan tidak butuh identitas sendiri. Menjadikannya agent
> hanya menambah lapisan tanpa menambah kemampuan.

> ⚠️ **Tapi kriterianya tidak diberikan** — mana yang agent, mana yang service?
> Aturan yang bisa ditulis sekarang dari bahan yang sudah ada:
>
> | Jadi **service** kalau | Jadi **agent** kalau |
> |---|---|
> | deterministik (masukan sama → keluaran sama) | perlu memutuskan di antara pilihan |
> | tidak memanggil tool | memanggil tool lewat Action Gateway §11.14 |
> | tidak menulis apa pun | punya `risk_level` di atas R0 |
> | tidak butuh identitas untuk jejak audit | perlu muncul di rantai delegasi §11.7 |
>
> Dengan aturan itu, dari dua belas nama di atas kemungkinan besar hanya
> **LifePlanningAgent** dan **DecisionSimulationAgent** yang benar-benar agent;
> sepuluh sisanya service. Lihat **G-13** / [#89](../../issues/89).
