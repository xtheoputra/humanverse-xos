# 164 — §9.37–§9.41 Arsitektur Lengkap, Repository, Roadmap C1–C10 & Definition of Done

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.37 — Cognitive Architecture lengkap

```
                         HUMAN
                           │
                           ▼
                    ┌────────────┐
                    │ INTERFACE  │
                    └─────┬──────┘
                          │
                          ▼
                 COGNITIVE ORCHESTRATOR
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
     CONTEXT            MEMORY            STATE
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                    UNDERSTANDING
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
         KNOWLEDGE     WORLD MODEL   BEHAVIOR
             │            │            │
             └────────────┼────────────┘
                          ▼
                       REASONING
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          PLANNING    PREDICTION   SIMULATION
             │            │            │
             └────────────┼────────────┘
                          ▼
                       DECISION
                          │
                          ▼
                    RECOMMENDATION
                          │
                          ▼
                        ACTION
                          │
                          ▼
                      FEEDBACK
                          │
                          └──────► LEARNING
```

Dan di sekeliling semuanya:

```
Security · Privacy · Consent · Policy · Risk · Audit · Governance
```

---

> ⭐ **Tujuh hal di sekeliling adalah Fase 8 yang diakui sebagai pembungkus,
> bukan sebagai fase yang sudah lewat.** Itu penting: keamanan yang digambar
> sebagai lapisan mengelilingi lebih sulit dilupakan daripada keamanan yang
> digambar sebagai kotak di tengah alur.

> ⚠️ **`Kill Switch` dan `Identity` tidak ada di tujuh itu**, padahal §8.42
> mendaftar delapan komponen Control Plane (Identity · Permission · Policy ·
> Consent · Risk · Audit · Security monitoring · **Kill switch**). Yang masuk
> di sini justru dua yang bukan komponen: *Privacy* dan *Governance* sebagai
> nama bidang.
>
> Hilangnya Kill Switch dari gambar "di sekeliling semuanya" perlu diperhatikan
> justru karena naskah ini memperkenalkan **bounded autonomy** (§9.26): tombol
> berhenti paling dibutuhkan tepat ketika AI boleh bertindak sendiri.
> Daftar yang sebaiknya dipakai tetap **§8.42**.

---

## §9.38 — Repository final Fase 9

```
intelligence/
│
├── cognitive-runtime/
│   ├── orchestrator/
│   ├── state-machine/
│   ├── request-context/
│   └── execution/
│
├── context-engine/
│   ├── context-builder/
│   ├── context-ranking/
│   ├── temporal-context/
│   └── environmental-context/
│
├── memory-engine/
│   ├── working/  episodic/  semantic/  procedural/
│   ├── behavioral/  preference/
│   ├── consolidation/
│   └── decay/
│
├── understanding/
│   ├── situation/  temporal/  pattern/  uncertainty/
│
├── knowledge/
│   ├── personal/  general/  ontology/  graph/
│
├── world-model/
│   ├── state/  transition/  scenario/  counterfactual/
│
├── reasoning/
│   ├── symbolic/  neural/  hybrid/  causal/  evidence/
│
├── planning/
│   ├── goal-planner/  task-planner/  hierarchical/
│
├── prediction/
│   ├── behavior/  preference/  goal/  outcome/
│
├── simulation/
│   ├── scenario/  monte-carlo/  counterfactual/
│
├── decision/
│   ├── utility/  ranking/  tradeoff/  decision-lab/
│
├── recommendation/
│
├── agency/
│   ├── autonomy/  action/  verification/
│
├── feedback/
│
└── evaluation/
    ├── cognitive/  calibration/  benchmark/  experiments/
```

---

> 🛑 **`intelligence/` sudah ada di monorepo naskah 5 §4 — dan versi ini
> MEMBUANG empat foldernya.**
>
> | Monorepo naskah 5 §4 | Naskah 13 §9.38 |
> |---|---|
> | `orchestrator/` | ➡️ `cognitive-runtime/orchestrator/` |
> | `planner/` | ➡️ `planning/` |
> | `reasoning/` · `recommendation/` · `prediction/` · `simulation/` | ✅ tetap |
> | `memory/` · `context/` | ➡️ `memory-engine/` · `context-engine/` |
> | **`behavior-model/`** | ❌ **hilang** |
> | **`preference-model/`** | ❌ **hilang** |
> | **`personalization/`** | ❌ **hilang** |
> | **`model-router/`** | ❌ **hilang** |
>
> Dua yang pertama adalah **L2 dari tumpukan §9.3 naskah ini sendiri**
> (*BEHAVIOR & PREFERENCE*), dan `state/` untuk **L3** juga tidak ada di mana
> pun kecuali sebagai sub-folder `world-model/state/` yang artinya lain.
> **Tumpukan dua belas lapisan punya dua lapisan tanpa rumah.**
>
> 🔴 **`model-router/` yang paling berat.** Ia jawaban **B-2**/**H-6** (biaya
> inferensi berlipat), dan naskah ini justru **memperkuat kebutuhannya**: §9.2
> berkata LLM hanya salah satu komponen, §9.20 memberi tiga jalur yang harus
> ada yang memilih. Perutean model dijelaskan lebih rinci dari sebelumnya, lalu
> foldernya dihapus. Lihat **E-79** / [#69](../../issues/69).

> ⚠️ **Tiga pasang tumpang tindih dengan `research/` naskah 9** — dan ini
> membuat **E-66** / [#55](../../issues/55) berubah sifat: bukan lagi sekadar
> pohon tanpa aturan komposisi, melainkan **konsep yang sama di dua pohon**.
>
> | `intelligence/` | `research/` |
> |---|---|
> | `world-model/` | `world-model-lab/` |
> | `memory-engine/` | `memory-lab/` |
> | `simulation/` | `simulation-lab/` |
> | `evaluation/` | `evaluation/` |
>
> Pembagian yang masuk akal ada dan tinggal ditulis: **`research/` adalah
> tempat mencari cara, `intelligence/` adalah tempat menjalankannya di
> produksi.** Akhiran `-lab` sebenarnya sudah mengatakan itu — tinggal
> dijadikan aturan, bukan kebetulan penamaan.

> ⚠️ **Pohon keenam.** `humanverse-x/` · `research/` · `developer-platform/` ·
> `data-platform/` · `security/` · dan sekarang `intelligence/` — walaupun yang
> terakhir ini **redefinisi folder yang sudah ada**, bukan pohon baru.

---

## §9.39 — Implementation Roadmap: 10 sprint

| Sprint | Isi |
|---|---|
| **C1** — Cognitive Runtime | Orchestrator + cognitive state machine |
| **C2** — Context Intelligence | Context package + context ranking |
| **C3** — Cognitive Memory | Memory retrieval + consolidation + decay |
| **C4** — Human Understanding | Situation understanding + temporal patterns |
| **C5** — Knowledge & World Model | Personal knowledge + graph + scenario model |
| **C6** — Reasoning | Hybrid reasoning + evidence + uncertainty |
| **C7** — Planning | Goal → milestone → project → task |
| **C8** — Prediction & Simulation | Prediction + counterfactual + scenario simulation |
| **C9** — Decision Intelligence | Utility model + trade-off analysis + recommendations |
| **C10** — Cognitive Evaluation | Calibration + benchmark + feedback learning |

---

> ⚠️ **Skema sprint keenam — dan awalan berfase yang baru diperkenalkan naskah
> 12 tidak dipakai.** Sudah berjalan: `Sprint 0–6` (V0) · `R1–R8` (naskah 9) ·
> `D1–D8` **dua kali** (naskah 10 & 11) · `S8.1–S8.8` (naskah 12) · dan kini
> `C1–C10`.
>
> `S8.x` adalah satu-satunya yang membawa nomor fasenya sendiri sehingga tidak
> bisa disalahartikan; satu naskah kemudian obatnya tidak dipakai. Usul:
> **`S9.1`–`S9.10`**. Lihat **E-84** / [#56](../../issues/56).

> ⭐⭐ **Tetapi sepuluh sprint ini berbeda sifatnya dari delapan sprint Fase
> 8 — dan itu mengubah jawaban [#58](../../issues/58).**
>
> Fase 8 menambah pekerjaan **di atas** V0: 20 tabel baru yang tidak dibutuhkan
> satu pun dari 12 fitur V0. Fase 9 sebagian besar adalah **cara membangun V0
> itu sendiri**:
>
> | Sprint | Sudah ada di V0? |
> |---|---|
> | **C2** Context Intelligence | ✅ Context Engine ada di Sprint 4–5 V0 |
> | **C3** Cognitive Memory | ✅ *Basic Memory* adalah fitur V0, `memories` sudah ada |
> | **C9** Decision Intelligence | ✅ *Recommendation* adalah fitur V0 |
> | **C1** Cognitive Runtime | ⚠️ sebagian — orchestrator-agent ada di V0 |
> | C4 · C5 · C6 · C7 · C8 · C10 | ❌ menunggu data & V2+ |
>
> Artinya membaca Fase 9 sebagai "fase kesembilan yang menunggu giliran" keliru.
> Tiga sprintnya adalah pekerjaan V0 yang sudah dijadwalkan, dan naskah ini
> memberi **bentuk yang lebih baik** untuk mengerjakannya — terutama
> `context package` (§9.31) yang menyederhanakan izin dan pencatatan sekaligus.

---

## §9.40 — Definition of Done

Fase 9 selesai jika HumanVerse sudah mampu:

```
✓ Understand the current user context
✓ Retrieve relevant memory
✓ Represent human state
✓ Connect personal knowledge
✓ Understand behavioral patterns
✓ Reason over multiple domains
✓ Handle uncertainty
✓ Generate plans
✓ Predict possible outcomes
✓ Simulate scenarios
✓ Compare decisions
✓ Recommend actions
✓ Respect permissions
✓ Ask for confirmation when necessary
✓ Observe outcomes
✓ Learn from feedback
```

---

> ⭐ **Bentuk yang sama dengan §8.45 — enam belas baris yang bisa dijawab ya
> atau tidak.** Dua naskah berturut-turut memakai kriteria keluar yang bisa
> diperiksa alih-alih taksiran persen (**A-24** / [#43](../../issues/43)).
> Ini kebiasaan baru yang layak dipertahankan.
>
> ⭐ Dua baris terakhir dari Fase 8 ikut dibawa: *"Respect permissions"* dan
> *"Ask for confirmation when necessary"* — keamanan tidak ditinggalkan begitu
> fasenya lewat.

> ⚠️ **Empat baris tidak punya alat ukur:**
>
> | Baris | Yang kurang |
> |---|---|
> | *Handle uncertainty* | ambang `confidence` belum ada (**§9.33**, [#34](../../issues/34)) |
> | *Reason over multiple domains* | berapa domain, dan bagaimana "reason" dinilai benar |
> | *Learn from feedback* | §9.35 sendiri tidak punya sumber untuk `Real Outcome` |
> | *Simulate scenarios* | model transisi belum punya sumber data (**B-24**) |
>
> Dan yang **hilang** dari daftar: tidak ada satu baris pun tentang
> **memperbaiki kesimpulan yang salah** — sama seperti §8.45. Padahal naskah
> ini menambah dua hal yang menuntutnya: memory yang meluruh (§9.9) dan bobot
> utility yang *"user harus dapat mengubahnya"* (§9.25). Bertaut **E-74** /
> [#64](../../issues/64).

---

## §9.41 — Yang kita bangun sebenarnya

> Setelah Fase 9, HumanVerse bukan lagi sekadar **Chatbot**, bukan juga sekadar
> **AI Assistant**:

```
              HUMANVERSE COGNITIVE SYSTEM

                    Perceive
                       ↓
                    Context
                       ↓
                     Memory
                       ↓
                  Understand
                       ↓
                    Reason
                       ↓
                   Simulate
                       ↓
                   Predict
                       ↓
                    Decide
                       ↓
                  Recommend
                       ↓
                    Act
                       ↓
                   Observe
                       ↓
                    Learn
                       ↺
```

> ## HumanVerse tidak mencoba menjadi manusia. HumanVerse menjadi sistem yang memahami konteks manusia dengan semakin baik, membantu manusia berpikir lebih baik, dan tetap membiarkan manusia memegang kendali.

---

> ⭐ **Kalimat penutup itu konsisten dengan prinsip penutup naskah 4**
> (*"jangan menilai apakah seseorang manusia yang baik atau buruk"*) dan dengan
> §8.46 (*"semakin pintar AI-nya, semakin besar kebutuhan terhadap
> kontrolnya"*). Tiga naskah, tiga kalimat penutup, satu arah yang sama.

---

## Progress menurut pemilik

| Fase | Sistem | Status |
|---|---|---|
| 1–8 | Core → Security | ✅ |
| **9** | **Cognitive Architecture** | 🔵 **Sekarang** |

## Fase berikutnya menurut pemilik

> **Fase 10 — HumanVerse Multimodal Intelligence & Perception Layer.** Mata,
> telinga, suara, vision, sensor, wearable, camera, document understanding,
> spatial intelligence, dan multimodal fusion — sehingga cognitive architecture
> Fase 9 tidak hanya menerima teks dan database event, tetapi mampu mengamati
> dunia nyata secara multimodal.

---

> 🛑 **Peta fase naskah 8 sudah tidak berlaku untuk Phase 9 ke atas — dua fase
> berturut-turut tergeser, dan yang tergeser tidak diberi rumah baru.**
>
> | | Peta naskah 8 | Yang benar-benar datang |
> |---|---|---|
> | **Phase 9** | Enterprise & Business Platform — *Team Workspace · Enterprise Admin · Family Mode · Subscription · **Company Wellness** · Revenue Platform* | **Cognitive Architecture** |
> | **Phase 10** | AI Automation Engine — *Cross-App Actions · Calendar Automation · **Email Automation*** | **Multimodal & Perception** |
>
> Konsekuensinya langsung mengenai dua issue terbuka yang menyebut nomor fase:
>
> - **[#46](../../issues/46)** (**C-12**) menulis *"Phase 9 mendaftarkan Company
>   Wellness bersama Team Workspace"* — Phase 9 sekarang bukan itu.
> - **[#47](../../issues/47)** (**B-19**) berjudul *"Phase 10 adalah ujian
>   pertama janji Act di bawah kontrol pengguna"* — Phase 10 sekarang bukan
>   itu.
>
> Keduanya tetap **masalah yang sah**; yang hilang adalah **kapan** ia datang.
> Perlu satu keputusan: peta naskah 8 direvisi, atau dinyatakan sudah tidak
> berlaku dari Phase 9. Lihat **E-85** dan **A-26** / [#66](../../issues/66).

> ⭐ **Urutan barunya sendiri lebih masuk akal daripada peta lama.** Multimodal
> setelah Cognitive berarti mata dan telinga dipasang pada otak yang sudah ada
> — bukan sebaliknya. Dan menunda Enterprise berarti menunda **C-10**
> (*Coaches*) dan **C-12** (*Company Wellness*), dua butir hukum terberat, ke
> waktu ketika model izin sudah punya kata untuk *"data orang lain"*
> ([#40](../../issues/40)). Penggeseran ini kemungkinan besar perbaikan; yang
> perlu hanyalah menuliskannya.
