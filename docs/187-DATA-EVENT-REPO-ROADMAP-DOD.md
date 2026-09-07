# 187 — §11.48–§11.64 Data Model, Event, Repository, Control Plane, Roadmap & DoD

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.48 — Agentic Data Model

```
agents · agent_versions · agent_capabilities · agent_permissions
agent_policies · agent_tasks · agent_plans · agent_steps · agent_actions
agent_runs · agent_messages · agent_failures · agent_evaluations
agent_budgets · agent_trust_scores · agent_approvals · agent_checkpoints
agent_outcomes
```

---

> 🛑 **Delapan belas entitas, dan empat di antaranya sudah didefinisikan di
> tempat lain — dua di spesifikasi, dua di Fase 8.**
>
> | Entitas | Sudah ada di |
> |---|---|
> | `agents` · `agent_runs` | [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) |
> | **`agent_capabilities`** | §8.40 (Fase 8) **dan** §11.48 (Fase 11) |
> | **`agent_trust_scores`** | §8.40 (Fase 8) **dan** §11.48 (Fase 11) |
>
> Dua tabel didefinisikan oleh **dua fase**, tanpa satu pun menyebut yang lain.
> Ini pertama kalinya duplikasi terjadi di tingkat **skema**, bukan folder —
> dan skema yang didefinisikan dua kali akan dibangun dua kali. Lihat **E-99**.
>
> ⚠️ Sebaliknya, **`agent_tools` yang ADA di spesifikasi hilang dari daftar
> ini**, digantikan `agent_capabilities`. Butir **E-79** sudah mencatat
> keduanya menduplikasi satu gagasan; sekarang satu menggantikan yang lain
> tanpa dinyatakan.
>
> **Hitungan tabel:** 23 (V0) + 20 (Fase 8) + 16 (Fase 10) + **14 baru** =
> **73 tabel**. Bertaut **A-25** / [#58](../../issues/58).

> ⭐ **Empat entitas yang benar-benar baru dan berharga:** `agent_approvals`
> (jejak persetujuan manusia — bukti bahwa §8.17 dijalankan),
> `agent_checkpoints` (§11.41), `agent_budgets` (§11.17), dan `agent_outcomes`
> — yang terakhir memisahkan **apa yang dilakukan** (`agent_actions`) dari
> **apa akibatnya**, persis pemisahan `VERIFY` vs `OBSERVE` §11.1.

---

## §11.49 — Event Model

```
AgentCreated · AgentStarted · AgentStopped · AgentTaskCreated
AgentPlanGenerated · AgentPlanApproved · AgentActionRequested
AgentActionApproved · AgentActionRejected · AgentActionExecuted
AgentActionFailed · AgentActionVerified · AgentTaskCompleted
AgentTaskFailed · AgentPermissionRequested · AgentPermissionGranted
AgentPermissionRevoked · AgentPolicyViolation · AgentBudgetExceeded
AgentSuspended · AgentResumed · AgentKilled
```

---

> ⚠️ **PascalCase lagi — naskah ketiga berturut-turut melanggar keputusan
> #38** (dua segmen, huruf kecil, sekali dipakai tidak pernah diganti). Naskah
> 12 memakai prosa (**E-70**), naskah 14 PascalCase (**E-88**), sekarang 22
> nama lagi.
>
> ⭐ Semuanya menerjemah bersih: `agent.created`, `agent.plan_generated`,
> `agent.action_executed`, `agent.permission_revoked`, `agent.killed`.

> ⚠️ **Dua di antaranya menduplikasi event keamanan §8.26**:
> `AgentPolicyViolation` ↔ *Policy Violation*, dan `AgentBudgetExceeded`
> ↔ tidak ada padanan tapi jelas milik jalur keamanan yang sama. Satu kejadian
> tidak boleh punya dua nama event; kalau tidak, Security Analytics §8.26 akan
> melewatkan separuhnya.

> ⭐ **Sebelas dari 22 event ini adalah jejak persetujuan dan izin**
> (`ActionRequested/Approved/Rejected`, `PermissionRequested/Granted/Revoked`,
> `PlanApproved`). Itu artinya seluruh jalur konfirmasi manusia **tercatat
> sebagai event**, bukan hanya sebagai baris audit — dan itu yang membuat
> pertanyaan *"kapan saya menyetujui ini"* bisa dijawab.

---

## §11.50 — Repository

```
agents/
├── runtime/        ├── permissions/   ├── memory/
├── registry/       ├── policies/      ├── evaluation/
├── manifests/      ├── risk/          ├── simulation/
├── capabilities/   ├── approvals/     ├── sandbox/
├── identity/       ├── budgets/       ├── reputation/
├── orchestration/  ├── watchdog/      ├── marketplace/
├── planning/       ├── verification/  └── audit/
├── execution/      ├── recovery/
├── task-engine/    ├── communication/
├── workflow-engine/├── collaboration/
                    └── negotiation/
```

---

> 🛑 **Pohon tingkat-atas KEDELAPAN — dan dengan DUA BELAS duplikasi, yang
> terbanyak dari semua pohon.**
>
> | `agents/` | Sudah ada di |
> |---|---|
> | `identity/` · `permissions/` | `security/identity/`, `security/permissions/` |
> | `policies/` · `risk/` | `security/policy-engine/`, `security/risk-engine/` |
> | `audit/` | `security/audit/` |
> | `sandbox/` | `security/agent-security/sandbox/` **dan** DP-L14 |
> | `reputation/` | `security/agent-security/trust/` |
> | `memory/` | `intelligence/memory-engine/` |
> | `planning/` | `intelligence/planning/` |
> | `simulation/` | `intelligence/simulation/` **dan** `research/simulation-lab/` |
> | `evaluation/` | `intelligence/evaluation/` **dan** `research/evaluation/` |
> | `marketplace/` | `developer-platform/` |
>
> Riwayat pohon: `humanverse-x/` · `research/` · `developer-platform/` ·
> `data-platform/` · `security/` · `intelligence/` · `multimodal/` ·
> `agents/`. **Tujuh naskah berturut-turut menyentuh struktur repo**, dan
> Sprint 0 tugas 0.1 masih menunggu ([#55](../../issues/55)).
>
> ⭐ **Tapi ada bacaan yang menyelesaikan sebagian besarnya, dan naskah ini
> sendiri yang memberikannya.** §11.51 memisahkan Agent Control Plane dari
> Agent Data Plane, dan §11.38 mendaftarkan Policy/Risk/Permission sebagai
> komponen runtime — bukan sebagai implementasi baru.
>
> Aturannya satu baris: **`security/` memiliki mesinnya; `agents/` hanya
> memanggil.** Dengan itu enam folder di atas (`identity/`, `permissions/`,
> `policies/`, `risk/`, `audit/`, `reputation/`) tidak perlu ada sama sekali —
> yang tersisa hanya klien tipis di `runtime/`. Lihat **E-97**.

> ⭐ **Delapan folder yang benar-benar milik lapisan ini** dan tidak ada di
> mana pun: `manifests/` · `orchestration/` · `task-engine/` ·
> `workflow-engine/` · `communication/` · `collaboration/` · `negotiation/` ·
> `recovery/`.

---

## §11.51 — Agent Control Plane

```
AGENT CONTROL PLANE
Registry · Policy · Identity
Scheduler · Risk · Permissions
Deployment · Budget · Credentials
        ↓
AGENT DATA PLANE → Agent Execution → Tools
```

---

> 🛑 **Control Plane kedua — dan empat komponennya sama persis dengan yang
> pertama.** §8.42 memberi Security Control Plane: *Identity · Permission ·
> Policy · Consent · Risk · Audit · Security monitoring · Kill switch*.
>
> Yang muncul di **kedua** daftar: **Identity · Policy · Risk · Permissions**.
>
> Dua kemungkinan, dan yang mana berlaku menentukan berapa banyak yang
> dibangun:
>
> | Bacaan | Konsekuensi |
> |---|---|
> | **satu benda, dilihat dua kali** | `agents/` memanggil `security/`; empat komponen dibangun sekali |
> | **dua implementasi** | kebijakan agent dan kebijakan sistem bisa berbeda — dan itu persis cara lubang keamanan lahir |
>
> Yang benar hampir pasti yang pertama, dan §8.42 sudah menetapkan batasnya:
> *tidak ada modul agent yang boleh mengimpor `security/`; ia hanya boleh
> dipanggil lewat gerbang.* Lihat **E-96**.

> ⭐ **`Credentials` dan `Deployment` adalah dua yang benar-benar baru** — dan
> `Credentials` yang menentukan: §11.24 mewajibkan `Revoke credentials` saat
> watchdog memicu, dan itu hanya mungkin kalau agent punya kredensialnya
> sendiri (§11.7), bukan memakai milik pengguna.

---

## §11.52–§11.54 — Deployment, Isolation & Model Routing

> Agent **tidak diberikan direct network access** tanpa policy.

Isolasi berdasarkan: **Namespace · Identity · Network Policy · Filesystem ·
Secrets · Tools · Memory · Data Scope · CPU · Memory · Runtime**

Model routing: `Task → Complexity → Risk → Model Router` — *simple
classification → small model · planning → stronger reasoning model ·
high-risk decision → **multiple-model verification***

---

> ⭐⭐ **`high-risk decision → multiple-model verification` adalah pemakaian
> anggaran yang benar:** hemat di tempat yang murah supaya bisa boros di tempat
> yang penting. Itu juga jawaban parsial untuk **B-10** — *"model menilai
> model"* berbahaya kalau satu model menilai dirinya, jauh kurang berbahaya
> kalau beberapa model harus sepakat.

> ⭐ **Ini perutean ketiga, dan akhirnya jelas bahwa ketiganya sumbu berbeda:**
> *effort* (§9.20 Fast/Cognitive/High-stakes) · *modality* (§10.29) ·
> *risk* (§11.54). Butir **E-79** mencatat `model-router/` dihapus dari
> `intelligence/` lalu muncul di `multimodal/`; sekarang jelas ia **satu
> komponen dengan tiga masukan**, dan tempatnya bukan di dalam salah satu
> konsumennya.

> ⚠️ **`Network Policy` adalah pengaman yang paling menentukan di daftar
> isolasi** — ia yang menghentikan `Data exfiltration` (§8.27). Agent dengan
> izin baca sempit tapi jaringan bebas bisa mengirim apa saja ke mana saja.
> Sejalan dengan `Restricted Network` §8.29.

---

## §11.55–§11.58 — Evaluation Matrix, Lifecycle, Agent Factory & Personal Agent

Lifecycle: `IDEA → SPECIFICATION → GENERATION → TESTING → SECURITY REVIEW →
RED TEAM → SIMULATION → CERTIFICATION → SANDBOX → LIMITED RELEASE →
MONITORING → PRODUCTION → EVALUATION → VERSION UPDATE → RETIREMENT`

---

> ⭐⭐ **`LIMITED RELEASE` dan `RETIREMENT` adalah dua tahap yang belum pernah
> ada.** Yang pertama memberi jalan tengah antara sandbox dan produksi penuh —
> satu-satunya cara aman melepas agent ke pengguna nyata. Yang kedua menjawab
> pertanyaan yang tidak pernah diajukan: **apa yang terjadi pada memori,
> rencana berjalan, dan tugas panjang milik agent yang dipensiunkan.**
>
> ⚠️ Ini juga daur hidup pengembangan **keempat** (Layer 22 naskah 7 · §94
> blueprint · SAIDLC §8.31 · ini) — pola **E-47** lagi. Yang ini khusus untuk
> agent, jadi punya alasan; tapi lima belas tahap yang dijalankan satu orang
> tetap perlu dinyatakan sebagai cita-cita, bukan proses.

> ⭐ **§11.57 Agent Factory + Agency:** *"agent tidak hanya dibuat — ia
> dikontrol sejak lahir."* Delapan langkah dari Specification ke Deployment,
> dengan `Autonomy Profile` dan `Risk Profile` sebagai keluaran generator.
> Itu **E-32** (*Agent Factory* tiga makna) yang akhirnya menetap di makna
> ketiga: pipeline generator yang dijalankan manusia.

---

## §11.59 — Contoh End-to-End

*"Saya ingin minggu depan lebih produktif."* → Understand · Context · Analyze ·
Plan · Multi-agent · Policy · Execute · Observe · Learn · Adapt

---

> ⭐⭐ **Sepuluh langkah, dan ini jejak lengkap pertama di lima belas naskah** —
> dari kalimat pengguna sampai rencana minggu berikutnya. Langkah 6
> (**Policy**) berdiri sebelum langkah 7 (**Execute**), dan daftar aksi yang
> diizinkan disebut satu per satu: *calendar · reminders · habit adjustment*.
> Tidak ada aksi keluar, tidak ada pembelian — persis batas yang §11.15 tetapkan
> untuk R1/R2.

> ⚠️ **`Productivity Agent` di langkah 5 tidak ada di hierarki §11.4** —
> bersama Weather, Transportation, Hotel, Budget, Location, dan Preference
> Agent, itu **tujuh** agent yang hidup di contoh tanpa terdaftar. Lihat
> **E-95**.

---

## §11.61 — Definition of Done

**Understand · Plan · Collaborate · Act · Protect · Adapt · Control**

Dengan **Control** = `Pause · Resume · Cancel · Revoke · Kill · Rollback`

---

> ⭐⭐⭐ **Enam kata kerja kendali itu adalah *Human Override* yang G-8 /
> [#65](../../issues/65) catat tidak datang di Fase 8.**
>
> Butir itu mencatat: §8.17 mencegah **sebelum** aksi, §8.35 menghentikan
> **semuanya**, dan tidak ada yang membatalkan atau membalik **satu** keputusan
> yang sudah berjalan. `Cancel`, `Kill`, dan terutama **`Rollback`** mengisi
> tepat lubang itu — dan §11.27 Reversibility Engine memberi `Rollback`
> mekanismenya.
>
> 🛑 **Butir kedua G-8 masih hilang: *Bias Detection* tidak muncul sekali pun
> di lima belas naskah.** Dan permukaannya bertambah di naskah ini: §11.22
> memutuskan *apa yang lebih penting* bagi seseorang, §11.44 memutuskan *kapan
> layak mengganggu*, §11.45 menilai *seberapa mampu seseorang*.

> ⭐ **`Protect` sebagai kategori setara dengan `Act`** — permission, policy,
> risk, budget, sandbox, audit. Empat DoD berturut-turut (§8.45, §9.40, §10.38,
> §11.61) mempertahankan bagian keselamatan tanpa menyusut, bahkan ketika
> fasenya bukan tentang keamanan.

> ⚠️ **Tetapi ini DoD kedua yang tidak bisa dijawab ya/tidak** (setelah
> §10.38). Ia daftar **kemampuan**, bukan kriteria: *"Plan · Generate ·
> Validate · Prioritize · Schedule"* — selesai pada tingkat keberhasilan
> berapa? §11.55 punya matriksnya; DoD ini belum memakainya.

---

## §11.62–§11.64 — Arsitektur akhir, Posisi Human & Evolusi

```
HUMAN
  ├── CONTROL  → Permission · Approval · Override · Kill Switch
  └── BENEFIT  → Intelligence · Automation · Personalization · Adaptation
```

> HumanVerse bukan sistem yang mengambil alih manusia. **AI yang meningkatkan
> kemampuan manusia sambil mempertahankan manusia sebagai pemegang kendali.**

> Tahap berikutnya: **Phase 12 — Digital Twin & World Simulation Engine.**

---

> ⭐ **`Kill Switch` kembali di diagram.** Ia hilang dari §9.37 dan dari
> seluruh naskah 14; di sini ia berdiri sebagai salah satu dari empat bentuk
> kendali manusia. Dan `Override` disebut dengan namanya untuk pertama kalinya.

> ⭐ **Peta fase bertahan untuk naskah kedua.** §10.41 menetapkan 15 fase;
> §11.64 mengulangi urutan yang sama dan menempatkan Phase 12 = *Digital Twin &
> World Simulation*. Setelah lima sumbu penomoran yang bertabrakan, satu yang
> stabil dua naskah berturut-turut layak dicatat. **H-20** bertahan.
>
> ⚠️ Satu pergeseran kecil: §10.41 menulis *"Phase 1–4 Foundation"*, §11.64
> menulis *"Phase 1–4 Application Platform"*. Nama yang berbeda untuk rentang
> yang sama.

> ⚠️ **`A11.1`–`A11.12` (§11.60) adalah huruf keempat untuk benda yang sama:**
> `S8.x` (sprint) · `C1–C10` · `M10.x` (milestone) · `A11.x`. ⭐ Tiga dari
> empat membawa nomor fase, jadi arahnya membaik — tapi satu huruf sudah cukup.
> Usul tetap **`S<fase>.<n>`**. Lihat **E-100**.

> 🛑 **Dan §11.64 kembali menegaskan apa yang E-87 / [#72](../../issues/72)
> persoalkan:** seluruh evolusi ditulis sebagai **Phase 1–11**, dan **V0–V6
> tidak disebut sekali pun** — naskah ketiga berturut-turut. V0 tetap
> satu-satunya lingkup tertutup yang pernah ditetapkan, dan tetap tanpa tempat
> di peta.
