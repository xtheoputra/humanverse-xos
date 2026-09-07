# 218 — §14.51–§14.69 Repositori, Data, Event, API, Manifest V2, Otonomi L5, Roadmap & Definition of Done

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.51 — Phase 14 Repository

```
humanverse/
├── human-os/          ├── intelligence/     ├── agents/
├── digital-twin/      ├── world-model/      ├── multimodal/
├── data-platform/     ├── security/         ├── developer-platform/
│
├── collective-intelligence/
│   runtime · orchestration · delegation · collaboration · negotiation ·
│   deliberation · consensus · conflict-resolution · team-builder ·
│   task-allocation · collective-memory · collective-learning · evaluation
│
├── federation/
│   gateway · protocol · discovery · identity · authentication ·
│   authorization · delegation · interoperability · adapters
│
├── agent-economy/     marketplace · billing · payments · pricing · usage · settlement
├── agent-trust/       reputation · trust · certification · incidents · scoring
├── agent-security/    sandbox · quarantine · watchdog · anomaly-detection ·
│                      coalition-security · red-team
├── organization/      tenants · teams · enterprise-agents ·
│                      organization-memory · organization-policies
└── research/          collective-intelligence · multi-agent · negotiation ·
                       consensus · agent-economy · benchmarks
```

---

> ⭐ **Enam pohon tingkat-atas baru sekaligus, dan tiap-tiapnya punya isi yang
> jelas.** `agent-security/coalition-security/` khususnya memberi §14.31 dan
> §14.32 satu rumah, sehingga kelas kerentanan yang paling sulit itu tidak
> tersebar.

> 🛑 **Tetapi tiga hal di pohon ini bertabrakan dengan aturan yang sudah
> ditetapkan — dan semuanya soal BATAS, bukan soal rapi-rapian.**
>
> | Yang terjadi | Kenapa penting |
> |---|---|
> | `security/` (Phase 8) dan `agent-security/` (Phase 14) berdiri sebagai **dua pohon terpisah** | §8.42 menetapkan **kode agent tidak boleh mengimpor `security/`** — batas keras yang harus ditegakkan CI. Dengan dua pohon, aturan itu tidak jelas berlaku ke yang mana: bolehkah `agents/` mengimpor `agent-security/`? Bolehkah `agent-security/` mengimpor `security/`? |
> | **Tidak ada `governance/`** | §14.44 menjadikan Governance Mesh sebagai pusat seluruh fase, dan §14.45 menaruh `Governance` di Control Plane. Ia tidak punya direktori. Kelima komponennya (Identity · Policy · Risk · Permission · Audit) tersebar. |
> | `delegation/` muncul **dua kali** — di `collective-intelligence/` dan di `federation/` | §14.42 adalah **satu** invarian. Dua implementasi berarti dua tempat untuk melanggarnya, dan yang federasi justru yang paling sulit ditegakkan (**B-28**). |
>
> Ketiganya bersama satu kata *"sembarangan"* di §14.45 membuat batas
> Control/Data Plane hanya ada di diagram. Lihat **E-121**.

> ⚠️ **Ini juga menambah enam pohon lagi ke perkara H-10 / [#55](../../issues/55)**
> — monorepo yang sudah "final" di naskah 5 kini digerus untuk keempat kalinya.

---

## §14.52–§14.53 — Data Model & Event Model

Sekitar **empat puluh entity baru**, antara lain `agents`, `agent_versions`,
`agent_capabilities`, `agent_identities`, `agent_relationships`,
`agent_dependencies`, `agent_messages`, `agent_delegations`, `agent_teams`,
`agent_team_memory`, `agent_negotiations`, `agent_proposals`,
`agent_agreements`, `agent_consensus`, `agent_conflicts`,
`agent_deliberations`, `agent_trust_scores`, `agent_incidents`,
`agent_federations`, `federated_sessions`, `agent_marketplace_listings`,
`agent_billing`, `agent_settlements`, `agent_quarantine`,
`agent_security_events`, `organization_agents`, `tenant_agent_permissions`.

Event baru mencakup `AgentDiscovered`, `AgentAuthenticated`, `AgentDelegated`,
`AgentDelegationRejected`, `AgentProposalCreated`, `AgentConflictDetected`,
`AgentConsensusReached`, `AgentConsensusFailed`, `AgentTrustUpdated`,
`AgentSecurityViolation`, `AgentQuarantined`, `AgentRevoked`, `AgentKilled`,
`AgentCertified`, `AgentUsageRecorded`, `AgentBillingCreated`.

---

> ⭐⭐ **`AgentConsensusFailed` berdampingan dengan `AgentConsensusReached`
> adalah detail kecil yang menyelamatkan banyak hal.** Kegagalan mencapai
> konsensus bukan error — ia hasil yang sah dan sering benar (§14.12 menunjukkan
> perselisihan itu sendiri berguna). Sistem yang hanya punya event untuk
> "berhasil" akan memperlakukan yang lain sebagai kerusakan.

> ⭐ **`agent_delegations` sebagai tabel tersendiri** memberi §14.42 dan §14.56
> tempat menyimpan siapa mendelegasikan apa kepada siapa — prasyarat untuk graf
> §14.33 dan untuk pertanyaan *"who delegated?"*.

> 🛑 **Tetapi daftar-daftar besar naskah ini punya satu cacat yang berulang:
> yang didaftarkan lengkap, yang diskemakan hanya sebagian.**
>
> | Didaftarkan | Yang sampai ke skema/contoh |
> |---|---|
> | Tujuh tindakan watchdog §14.28 (`ALLOW · WARN · PAUSE · THROTTLE · REVOKE · QUARANTINE · KILL`) | Hanya **tiga** jadi event (`AgentQuarantined`, `AgentRevoked`, `AgentKilled`). Tidak ada `AgentWarned`, `AgentPaused`, `AgentThrottled` — dan **tidak ada `AgentRestored`**, padahal §14.29 menjadikan `RESTORE` keluaran yang setara dengan `RETIRE`. |
> | Sebelas unsur Autonomy Contract §14.62 | **Enam** di contoh YAML. |
> | `Attention Budget` §14.25, dinyatakan *"sangat penting"* | **Tidak ada tabel** — padahal ia sumber daya bersama antar-agent, jadi ia harus punya tempat menyimpan. |
> | `autonomy_contract` §14.62, dinyatakan *"sangat penting"* | **Tidak ada tabel.** |
>
> Akibatnya konkret dan bukan soal kerapian: **jejak audit hanya merekam tindakan
> terberat.** Agent yang di-`THROTTLE` tiap hari selama sebulan tidak
> meninggalkan satu baris pun — dan itu persis pola yang §14.32 ingin
> dideteksi. Lihat **G-14** / [#98](../../issues/98).

---

## §14.54 — API

```
POST /v1/agents/discover · connect · delegate      POST /v1/agent-messages
POST /v1/agent-teams        GET /v1/agent-teams/{id}
POST /v1/agents/negotiate · deliberate · consensus
GET  /v1/agents/trust · reputation
POST /v1/federation/connect · discover · revoke
POST /v1/agents/quarantine · revoke
GET  /v1/agent-economy/usage · billing
```

---

> ⭐ **`POST /v1/federation/revoke` dan `POST /v1/agents/revoke` sebagai
> endpoint tersendiri** — pencabutan punya alamat, sejalan dengan `REVOKE`
> §14.41 dan dengan §14.68 yang menuntut *maintain kill/revoke capability*.

> ⚠️ **`POST /v1/agents/quarantine` dan `/revoke` adalah tulisan ke CONTROL
> PLANE yang berada di permukaan API yang sama dengan panggilan data plane.**
> §14.45 melarang data plane mengubah control plane; kalau agent runtime memegang
> kredensial ke `/v1/*` yang sama, larangan itu hanya ada di dokumen. Bagian dari
> **E-121**.

> ⚠️ Salah ketik: **`POST /v1/agent-teams/{id/tasks}`** — kurung kurawalnya
> salah tempat, seharusnya `/{id}/tasks`. Gejala **H-9** yang muncul lagi di
> naskah panjang; dicatat supaya tidak tersalin ke spesifikasi.

---

## §14.55 — Agent Manifest V2

```yaml
agent:        { id: travel.planner, version: 2.0.0 }
identity:     { developer: humanverse.dev, organization: humanverse }
purpose:      [travel planning]
capabilities: [travel.search, calendar.read, weather.read]
tools:        [flight.search, hotel.search, weather.current]
memory:
  read:  [travel.preferences, calendar]
  write: [travel.plans]
delegation:   { allowed: true, max_depth: 2 }
risk:         { level: R2 }
autonomy:     { level: L3 }
budget:       { daily_limit: 5 }
federation:   { allowed: true }
security:     { sandbox: required }
data:         { classification: [user] }
```

---

> ⭐⭐⭐ **Ini manifest paling lengkap dalam delapan naskah manifest, dan tiga
> bloknya baru serta benar.**
>
> `delegation.max_depth: 2` — batas panjang rantai, yang membuat pencarian jalur
> §14.32 punya ujung dan membuat §14.43 punya arti. `budget.daily_limit` —
> **manifest pertama yang membawa anggarannya sendiri**, sehingga pagu tidak
> hanya hidup di kebijakan. `federation.allowed` — agent menyatakan apakah ia
> boleh dipanggil dari luar, satu sakelar untuk seluruh permukaan federasi.
>
> ⭐ Dan `security.sandbox: required` menutup salah satu keberatan lama: sandbox
> menjadi properti yang dideklarasikan dan diperiksa registry, bukan pilihan
> operasional.

> 🛑 **Tetapi `risk: level: R2` sebagai properti AGENT membalik pemisahan yang
> H-21 baru saja selesaikan.**
>
> **H-21** memisahkan dua tangga yang sempat tercampur: **R0–R4 adalah risiko
> AKSI**, **L0–L4 adalah otonomi agent**. Manifest ini menaruh keduanya
> berdampingan sebagai sifat agent — dan `R2` tidak bisa benar untuk sebuah
> agent. Travel Planner membaca kalender: R0–R1. Travel Planner memesan hotel
> dengan uang: R3. Satu angka di manifest tidak bisa menjadi keduanya, dan kalau
> gerbang membacanya sebagai izin, agent ber-`R2` akan menjalankan aksi R3 tanpa
> konfirmasi — persis yang **H-15** larang.
>
> Yang benar: `risk` melekat pada **capability/tool**, seperti yang sudah
> diwajibkan [`../spec/05`](../spec/05-AGENT-CONTRACTS.md); yang boleh ada di
> manifest agent adalah **pagu** (`max_risk: R2` = agent ini tidak boleh
> menjalankan aksi di atas R2), bukan tingkat. Satu kata — `max_risk` alih-alih
> `level` — menyelamatkan pemisahan itu. Lihat **E-119** /
> [#97](../../issues/97).

> ⚠️ **`data.classification: [user]` tidak memakai kosakata §8.16** yang punya
> empat tingkat (Level 1–4). Dan tiga hal yang pernah ada di manifest sebelumnya
> tetap tidak kembali: **`requires_confirmation`** (**G-12** — kini di tiga
> tempat tanpa yang otoritatif), **`consent`/`retention`**, dan **`fallback`**
> (§14.35 mewajibkan tiap agent penting punya Primary/Fallback, tapi manifest
> tidak punya tempat menuliskannya).

---

## §14.56–§14.58 — Delegation Graph, Distributed Trace & Observability

Tiap task harus bisa dilacak `User → Orchestrator → Travel Agent → Hotel Agent
→ Hotel API`, dengan audit menjawab:

> *Who initiated? · Who delegated? · Who executed? · Which capability? · Which
> data? · Which policy? · Which risk? · What was the result?*

Dan **distributed tracing** dengan `trace_id`:

```
TRACE-92831
User
 └─ Orchestrator
     ├─ Career Agent
     │   └─ Research Agent
     ├─ Finance Agent
     └─ Simulation Agent
```

Dashboard: **Agents Online · Tasks Running · Tasks Failed · Average Latency ·
Token Usage · Tool Usage · Policy Violations · Security Incidents · Agent Cost ·
Consensus Rate · Human Intervention Rate** — ditambah **Agent Health · Team
Health · Federation Health**.

---

> ⭐⭐⭐ **`Which policy?` dan `Which risk?` di dalam catatan audit adalah dua
> pertanyaan yang membedakan jejak yang bisa dipertanggungjawabkan dari jejak
> yang hanya bisa dibaca.**
>
> Mencatat *apa yang terjadi* memberi tahu hasilnya. Mencatat **aturan mana yang
> berlaku** dan **tingkat risiko mana yang dinilai** memberi tahu apakah
> sistemnya bekerja benar — dan itulah satu-satunya cara menjawab pertanyaan
> yang benar-benar ditanyakan orang setelah sesuatu salah: *bukan* "apa yang
> dilakukannya", melainkan "kenapa itu diizinkan".

> ⭐⭐ **`trace_id` adalah kunci yang §14.40 butuhkan.** Satu permintaan
> pengguna = satu jejak = **satu pagu**, dibagi ke seluruh rantai delegasi.
> Dengan itu anggaran, perhatian (§14.25), dan kedalaman delegasi (§14.55)
> semuanya bisa diikat pada benda yang sama — dan §14.31 punya sumbu untuk
> melihat gabungan, bukan hanya langkah.

> ⚠️ **`Human Intervention Rate` adalah satu-satunya metrik di daftar ini yang
> berbahaya kalau dijadikan target.** Angkanya turun kalau sistem membaik — dan
> juga turun kalau sistem berhenti bertanya. Kedua sebab terlihat identik di
> dasbor.
>
> §14.64 melarang lebih banyak agent otomatis berarti lebih banyak otonomi;
> metrik yang memberi hadiah pada berkurangnya campur tangan mendorong persis
> ke sana. Yang menyelamatkannya cuma satu: **tampilkan bersama tingkat
> pembatalan dan penolakan** — kalau intervensi turun sementara penolakan naik,
> yang terjadi bukan perbaikan.

---

## §14.59–§14.60 — Agent Control Center & Human Approval Center V2

```
┌────────────────────────────────────┐
│       HUMANVERSE AGENT CENTER      │
├────────────────────────────────────┤
│ Active Agents: 17   Running: 6     │
│ Pending Approval: 2  Alerts: 0     │
├────────────────────────────────────┤
│ Travel Team ● Active               │
│ Research Team ● Active             │
│ Career Team ● Idle                 │
├────────────────────────────────────┤
│ Travel Agent → Weather Agent       │
│ Research Agent → Search Agent      │
└────────────────────────────────────┘
```

Approval kini bukan lagi *"Apakah Anda ingin mengizinkan action?"* melainkan:

```
COLLECTIVE ACTION
Requested by:     Travel Team
Agents involved:  Travel · Weather · Budget · Hotel
Action:           Book hotel
Cost:             $380
Risk:             R2
Data used:        Calendar · Travel preference · Budget
Reversible:       Yes
Consensus:        4/4

[Approve]  [Reject]  [Edit]  [Inspect]
```

---

> ⭐⭐⭐ **`Edit` dan `Inspect` sebagai tombol yang setara dengan Approve dan
> Reject mengubah persetujuan dari gerbang menjadi percakapan.**
>
> Selama tujuh belas naskah, peran manusia pada aksi adalah biner: izinkan atau
> tolak. `Edit` menjadikannya peserta — ubah hotelnya, turunkan anggarannya,
> buang satu agent dari rombongan — dan `Inspect` memberi jalan ke alasan di
> baliknya (§14.57 sudah punya jejaknya). Itu juga bentuk `Edit` yang **E-74**
> minta, muncul di tempat yang berbeda dari yang diduga.

> ⭐ **`Data used` di kartu persetujuan** adalah janji §8.11 yang akhirnya
> terlihat pengguna: ia menyetujui aksi **dan** melihat data apa yang dipakai
> untuk menyusunnya.

> ⚠️ **`Risk: R2` dan `Reversible: Yes` adalah dua penyandian untuk satu
> fakta.** **H-21** mendefinisikan **R4 sebagai tidak dapat dibatalkan** —
> artinya keterbalikan sudah tersirat di tingkat risiko. Dua field yang berisi
> fakta yang sama akan berbeda suatu saat, dan yang mana dipercaya tidak
> ditulis. Yang benar: **`Reversible` diturunkan dari `Risk`**, atau `Risk`
> dihitung dari keterbalikan — satu arah, bukan dua isian. Lihat **E-122**.

> ⚠️ **`Consensus: 4/4` menampilkan hitungan, bukan perselisihannya** — lihat
> catatan di berkas [`215`](215-GRAF-AGEN-RESILIENSI-APPROVAL.md). Kartu yang
> bisa menulis `4/4` bisa menulis `3/4`, dan yang berguna bagi orang yang
> memutuskan justru yang satu itu.

---

## §14.61–§14.62 — L5 Collective Autonomous & Autonomy Contract

Phase 11 punya **L0 Observe · L1 Recommend · L2 Prepare · L3 Confirm · L4
Bounded Autonomous**. Phase 14 menambahkan **L5 Collective Autonomous**.

> Tetapi **L5 bukan unrestricted autonomy.** L5 berarti banyak agent dapat
> bekerja secara autonomous **dalam sandbox/capability boundary yang telah
> diberikan**.

```
Goal:        "Research competitors"
Allowed:     Search · Read public data · Analyze · Summarize
Not allowed: Contact competitors · Purchase data · Publish results
             · Spend money
```

Setiap autonomous team memiliki **Autonomy Contract**: *Goal · Scope ·
Capabilities · Budget · Time limit · Data boundary · Risk level · Success
criteria · Forbidden actions · Human escalation rule · Kill condition.*

```yaml
autonomy_contract:
  goal:     "research competitor landscape"
  duration: 24h
  budget:   $10
  allowed:   [web.search, document.read, analysis]
  forbidden: [send.email, purchase, publish]
  escalate_when:
    - confidence < 0.6
    - cost > $10
    - sensitive_data_detected
```

> Ini **sangat penting**.

---

> ⭐⭐⭐ **`escalate_when: confidence < 0.6` adalah ANGKA PERTAMA untuk
> confidence dalam delapan naskah.**
>
> Butir [#34](../../issues/34) mencatat `confidence` dipakai sebagai masukan
> keputusan sejak naskah 5 §19 — *low confidence → ask user* — tanpa satu pun
> naskah pernah menyebut apa itu "low". Delapan naskah berturut-turut memakainya
> tanpa ambang. Di sini akhirnya ada bilangan, dan ia berada di tempat yang
> tepat: **bukan di kode, melainkan di kontrak yang bisa dibaca dan diubah
> pemiliknya per team.**
>
> ⚠️ Yang masih perlu: `0.6` **dari skala apa dan dihitung bagaimana** —
> **H-14** menutup *cara menyajikan* keyakinan, bukan *cara menghitungnya*.
> Ambang tanpa rumus adalah angka yang tidak bisa direproduksi.

> ⭐⭐ **`forbidden` sebagai daftar eksplisit di samping `allowed` mengulang
> pilihan yang benar dari §14.21** (`deny:` eksplisit) **dan §14.8**
> (`constraints: cannot_purchase`). Tiga tempat kini menyatakan larangan
> secara langsung alih-alih mengandalkan "yang tidak diizinkan berarti
> dilarang" — dan untuk otonomi yang berjalan **24 jam tanpa pengawasan**, itu
> perbedaan antara aturan yang bisa dibaca dan aturan yang harus disimpulkan.

> 🛑 **Tetapi contoh kontraknya membuang lima dari sebelas unsur — dan yang
> dibuang justru yang terberat.**
>
> Hilang dari YAML: **`scope`**, **`data boundary`**, **`risk level`**,
> **`success criteria`**, dan **`kill condition`**. Empat yang pertama
> menentukan apa yang boleh disentuh dan kapan pekerjaan dianggap selesai; yang
> terakhir menentukan **kapan ia dihentikan paksa** — dan itu satu-satunya unsur
> yang penting justru ketika segala sesuatunya salah.
>
> `escalate_when` bukan penggantinya: eskalasi **memanggil manusia**;
> kill condition **berhenti tanpa menunggu manusia**. Sebuah team yang berjalan
> 24 jam harus punya keduanya, karena manusia bisa sedang tidur.

> 🛑 **Dan hubungan L5 dengan Autonomy Contract tidak ditulis, padahal keduanya
> mendefinisikan hal yang sama.**
>
> Tangga L adalah **sifat agent** (H-21); Autonomy Contract adalah **perjanjian
> per team, per tugas, berbatas waktu**. Tiga pertanyaan tanpa jawaban:
> apakah L5 berarti "punya autonomy contract yang berlaku"? Apakah tangga L
> tetap berlaku pada tiap anggota **di dalam** kontrak — bolehkah agent L2 ikut
> team L5? Dan `autonomy: level: L3` di manifest (§14.55) menang atau kalah
> terhadap kontrak?
>
> Jawaban yang paling aman, dan ia satu kalimat: **kontrak tidak pernah
> menaikkan tingkat otonomi anggotanya, hanya membatasinya lebih jauh** —
> sehingga L5 bukan tingkat baru di atas L4 melainkan **cara mengoordinasi
> banyak agent yang masing-masing tetap di tingkatnya sendiri**. Lihat
> **E-118** / [#98](../../issues/98).

---

## §14.63 — Collective Failure Handling

```
Agent Failure → Failure Classification
→ Retry? · Alternative Agent? · Replan? · Human? · Stop?
```

```
Hotel Agent failed → Fallback Hotel Agent → Success
```

Tetapi jika **3 agents failed** maka: **Escalate to Human**.

---

> ⭐⭐ **Ini aturan eskalasi BERANGKA pertama untuk kegagalan kolektif**, dan ia
> mengenali sesuatu yang benar: kegagalan tunggal adalah kejadian biasa yang
> ditangani fallback (§14.35), sedangkan **kegagalan beruntun berarti asumsinya
> yang salah, bukan komponennya** — dan asumsi yang salah bukan urusan mesin
> yang mencoba lagi.
>
> ⭐ `Stop?` sebagai pilihan yang setara dengan `Retry?` juga penting: berhenti
> adalah hasil yang sah, sejalan dengan *"tidak boleh mengarang data"* §14.35.

> ⚠️ **"3 agents failed" tidak menyebut penyebutnya, dan tidak semua kegagalan
> berbobot sama.** Tiga dari tiga adalah kegagalan total; tiga dari dua puluh
> mungkin normal. Dan satu agent di **jalur kritis** yang gagal lebih berarti
> daripada tiga agent pinggiran.
>
> Bentuk yang lebih benar dan sudah punya bahannya: eskalasi kalau **agent di
> `Dependency Graph` §14.34 yang tidak punya fallback gagal**, ATAU kalau
> proporsi kegagalan melewati ambang — bukan hitungan mutlak.

---

## §14.64 — Collective Intelligence Safety Rule

> Ada prinsip yang saya sarankan kita jadikan **foundational law**:
>
> ## More agents must not automatically mean more autonomy.
>
> Karena `10 agents × individual risk` dapat menghasilkan
> **`collective risk > individual risk`**. Maka setiap collective action harus
> **dievaluasi ulang**.

---

> ⭐⭐⭐ **Ini kalimat terpenting di naskah kedelapan belas, dan ia satu-satunya
> tempat di seluruh dokumen HumanVerse yang menyebut sesuatu sebagai
> "foundational law".**
>
> Ia menolak asumsi yang paling wajar dan paling berbahaya di sistem
> multi-agent: bahwa kalau tiap bagian aman, gabungannya aman. §14.31 sudah
> memperagakan kebalikannya dengan tiga baris — A(baca) + B(tulis) =
> eksfiltrasi, meski tiap agent lolos gerbangnya. §14.40 memperagakannya lagi
> dengan uang. Hukum ini menamai polanya.
>
> ⭐ *"Setiap collective action harus dievaluasi ulang"* juga memberi
> mekanismenya, bukan hanya sikap: **risiko dinilai pada aksi kolektif sebagai
> satu benda**, bukan diwarisi dari penilaian per-agent. Itu bisa dibangun —
> dan `trace_id` §14.57 adalah tempat menggantungkannya.

> 🛑 **Tetapi §14.50 melanggarnya secara bentuk**: skor yang **menjumlahkan**
> `Safety` dengan tujuh hal lain memungkinkan team yang cepat dan murah
> menyamai team yang aman. Hukum di §14.64 dan rumus di §14.50 tidak bisa
> keduanya berlaku. Lihat **B-29** / [#96](../../issues/96).

> ⚠️ **`KILL` kini berarti tiga hal berbeda di tiga naskah, dan tak satu pun
> menghubungkannya:** *Kill Switch* §8.36 (pemilik mematikan sistem/agent) ·
> `KILL` §14.28 (tindakan watchdog terhadap satu agent) · `kill condition`
> §14.62 (syarat yang mengakhiri kontrak otonomi sebuah team). Tiga kewenangan,
> tiga pemicu, satu kata. Ini pola yang sama dengan lima skema penomoran yang
> bertabrakan. Lihat **E-120**.

---

## §14.65 — Phase 14 Research Area

**Multi-Agent Learning · Multi-Agent Planning · Agent Negotiation · Agent
Cooperation · Agent Competition · Collective Decision Making · Consensus
Algorithms · Agent Trust · Agent Reputation · Emergent Behavior · Multi-Agent
Safety · Agent Economics · Federated Agents · Collective Memory · Swarm
Intelligence**

---

> ⭐ **`Emergent Behavior` dan `Multi-Agent Safety` sebagai bidang penelitian
> tersendiri menunjukkan naskah ini tahu bahwa yang paling sulit di Phase 14
> bukan membuatnya bekerja, melainkan mengetahui apa yang akan terjadi ketika
> ia bekerja.**

> ⚠️ **`Agent Competition` perlu batas yang dinyatakan.** Persaingan antar-agent
> yang bekerja untuk **pengguna yang sama** bukan hal yang jelas diinginkan —
> §14.11 sudah memberi bentuk yang lebih baik untuk perbedaan pendapat
> (deliberasi dengan bukti), dan §14.39 sudah memberi bentuk yang benar untuk
> persaingan (pasar, sebelum penugasan). Di luar dua tempat itu, agent yang
> bersaing di dalam satu tugas berarti sumber daya pengguna dipakai untuk
> mengalahkan sesama agent.

---

## §14.66–§14.67 — Implementation Roadmap & Milestone

> Saya sarankan Phase 14 **tidak langsung membangun semuanya.**

| | Workstream | | Milestone |
|---|---|---|---|
| **A14.1** | Agent Federation Foundation | M14.1 | Federation |
| **A14.2** | Agent Communication | M14.2 | Communication |
| **A14.3** | Agent Collaboration | M14.3 | Collaboration |
| **A14.4** | Negotiation & Deliberation | M14.4 | Agent Teams |
| **A14.5** | Collective Intelligence | M14.5 | Negotiation |
| **A14.6** | Trust & Reputation | M14.6 | Consensus |
| **A14.7** | Agent Security Mesh | M14.7 | Trust |
| **A14.8** | Agent Economy | M14.8 | Security Mesh |
| **A14.9** | Enterprise Agents | M14.9 | Agent Economy |
| **A14.10** | Autonomous Agent Teams | M14.10–12 | Enterprise · Collective Intelligence · Autonomous Teams |

---

> ⭐ **"Jangan langsung membangun semuanya" adalah peringatan yang sama dengan
> §58 naskah 5 dan §12.29** — dan untuk fase sebesar ini, membaginya jadi
> sepuluh aliran kerja adalah yang membuatnya mungkin sama sekali.
>
> ⭐ `A14.10 Autonomous Agent Teams` **di urutan terakhir** juga benar: hal yang
> paling otonom dibangun setelah seluruh pengamannya ada.

> 🛑 **Tetapi Federation ada di urutan PERTAMA dan Security Mesh di urutan
> KETUJUH — dan itu membuka pintu enam langkah sebelum penjaganya dipasang.**
>
> A14.1 memasukkan agent yang berjalan **di mesin orang lain**; A14.7 membangun
> Cross-Agent Security, Delegation Security, Coalition Detection, Quarantine,
> Watchdog, dan Anomaly Detection. Di antara keduanya: komunikasi, delegasi,
> kolaborasi, negosiasi, dan kecerdasan kolektif — semuanya **dengan peserta
> eksternal yang belum diawasi**.
>
> Dan ini bukan risiko yang bisa ditambal belakangan: **B-28** menunjukkan graf
> koalisi buta di batas federasi, §14.31 menunjukkan kerentanan lahir dari
> gabungan agent, dan §14.29 mencatat agent eksternal tidak bisa dikarantina
> seperti agent internal.
>
> Urutan yang lebih aman memakai bahan yang sama: bangun A14.2–A14.5
> **antar-agent internal lebih dulu** — semuanya berguna tanpa federasi —
> jadikan A14.7 Security Mesh mendahului pembukaan federasi, dan turunkan A14.1
> menjadi *"protokol dan identitas, tanpa peserta eksternal di produksi"*.
> Lihat **B-30** / [#99](../../issues/99).

---

## §14.68 — Definition of Done — Phase 14

Phase 14 selesai ketika HumanVerse mampu: **discover · authenticate · authorize
agent · berkomunikasi antar-agent · delegate · membangun team · mengalokasikan
tugas · berjalan paralel · mengelola dependensi · bernegosiasi · menyelesaikan
konflik · berdeliberasi · mencapai konsensus · memverifikasi hasil · melacak
provenance · memelihara collective memory · mengevaluasi kinerja kolektif ·
menilai & memeringkat agent · memfederasi agent eksternal · men-sandbox-nya ·
mengarantina agent jahat · menegakkan cross-agent security · mengelola anggaran
agent · mendukung marketplace, agent economy, enterprise agents, dan autonomous
teams** — serta:

```
✓ Maintain human governance
✓ Maintain auditability
✓ Maintain reversibility
✓ Maintain kill/revoke capability
```

---

> ⭐⭐⭐ **Tiga puluh satu butir, dan empat yang terakhir bukan kemampuan
> melainkan JAMINAN — daftar yang diakhiri dengan apa yang tidak boleh hilang,
> bukan dengan apa yang berhasil ditambahkan.**
>
> Empatnya juga persis empat hal yang paling mudah tergerus oleh tiga puluh
> butir di atasnya: makin banyak agent, makin sulit satu manusia memerintah;
> makin banyak federasi, makin sulit mencatat; makin otonom, makin sulit
> membatalkan; makin terdistribusi, makin sulit mematikan.

> ⚠️ **Tidak ada butir untuk `Attention Budget` maupun `Autonomy Contract`** —
> dua hal yang naskah ini sendiri sebut *"sangat penting"*. Pola **G-14** lagi:
> disebut, lalu tidak sampai ke daftar yang menentukan kapan pekerjaan selesai.

---

## §14.69 — Posisi HumanVerse Setelah Phase 14

```
Phase 9  THINK  →  Phase 10 PERCEIVE  →  Phase 11 ACT
→ Phase 12 SIMULATE  →  Phase 13 OPERATE  →  Phase 14 COLLABORATE
```

> **A Personal AI Operating System powered by a governed collective intelligence
> ecosystem.**

```
                    HUMAN
                      ▼
                 HUMANVERSE
                      ▼
                   HumanOS
                      ▼
              Cognitive Runtime
                      ▼
   Perception · Intelligence · Digital Twin
                      ▼
             Supreme Orchestrator
                      ▼
  Personal Agents · Domain Agents · Collective Agent Teams
                      ▼
               Agent Federation
                      ▼
     HumanVerse Agents · External Agents
                      ▼
               GOVERNANCE MESH
   Identity · Policy · Risk · Permission · Security
                      ▼
                ACTION GATEWAY
                      ▼
                EXTERNAL WORLD
                      ▼
                 OBSERVATION
                      ▼
                   LEARNING
```

Dan ada satu **perubahan filosofis** penting:

> Sebelum Phase 14: **HumanVerse = AI untuk manusia.**
> Setelah Phase 14: **HumanVerse = infrastructure tempat manusia dan AI agents
> bekerja bersama.**

---

> ⭐⭐⭐ **Diagram ini menaruh GOVERNANCE MESH di antara agent dan dunia — dan
> di BAWAH federasi, bukan di atasnya.**
>
> Artinya agent eksternal maupun internal sama-sama harus melewatinya; tidak ada
> pintu samping. Digabung dengan §14.36 (`Human ↑ Governance ↑ Agent
> Ecosystem`), arah kewenangannya utuh dari atas ke bawah: manusia di puncak,
> governance tepat sebelum dunia, dan pembelajaran kembali ke atas lewat
> observasi. Ini gambar arsitektur paling lengkap yang pernah ada di delapan
> belas naskah, dan tidak satu pun panahnya bertentangan dengan yang lain.

> ⚠️ **Tapi `ACTION GATEWAY` muncul SETELAH `GOVERNANCE MESH`, sementara §11.14
> menempatkan Policy dan Risk DI DALAM Action Gateway.** Kemungkinan besar ini
> soal penggambaran, bukan perubahan rancangan — tapi karena §14.20 dan §14.46
> sudah kehilangan langkah di rantai masing-masing (**E-117**), lebih baik
> ditegaskan mana yang memuat mana daripada dibiarkan tersirat.

> ⭐⭐ **Perubahan filosofisnya menggeser siapa penggunanya.** *"Infrastructure
> tempat manusia dan AI agents bekerja bersama"* berarti HumanVerse punya dua
> jenis penghuni, dan **hanya satu di antaranya yang punya hak**. Justru itu
> yang membuat §14.36 dan §14.64 wajib ada lebih dulu: begitu agent menjadi
> penghuni, mereka akan diperlakukan seperti peserta kecuali sistemnya menolak
> secara eksplisit.

---

> ## Penutup pemilik
>
> > Namun saya **tidak menyarankan kita langsung melompat ke Phase 15.** Phase
> > 14 adalah fase yang sangat besar. Sebelum melanjutkan, secara engineering
> > kita sebaiknya memecah Phase 14 menjadi arsitektur teknis tingkat
> > implementasi: **protocol specification · agent message schema · federation
> > protocol · security model · delegation model · consensus algorithm ·
> > database schema · API contract · event schema · repository ·
> > Docker/Kubernetes topology · sprint-by-sprint implementation.**

> ⭐⭐⭐ **Ini permintaan yang berbeda jenisnya dari tujuh belas naskah
> sebelumnya — dan ia menyebutkan persis bentuk artefak yang sudah ada di
> [`../spec/`](../spec/README.md) untuk V0.**
>
> Spesifikasi Engineering v1.0 memuat skema basis data, ERD, kontrak event,
> endpoint REST, manifest agent + risk gate, batas modul, dan 51 tugas dalam 7
> sprint — untuk V0. Yang diminta sekarang adalah **artefak sejenis untuk Phase
> 14**, dan itu pekerjaan yang bisa dimulai tanpa keputusan baru dari pemilik.
>
> ⚠️ Dengan satu syarat yang bukan formalitas: **beberapa butir di daftar itu
> tidak bisa dispesifikasikan sebelum diputuskan.** Protokol tidak bisa dikunci
> selama §14.41 tidak punya verb untuk manusia; model delegasi tidak bisa
> ditulis selama §14.43 tidak menyatakan siapa memotong kapabilitas; skema
> basis data tidak bisa lengkap selama `Attention Budget` dan `Autonomy
> Contract` tidak punya tabel (**G-14**); dan model keamanan tidak bisa benar
> selama urutan A14.1-sebelum-A14.7 belum ditinjau (**B-30**).
>
> Urutan yang masuk akal: **putuskan [#93](../../issues/93),
> [#97](../../issues/97), [#98](../../issues/98), dan [#99](../../issues/99)
> dulu — keempatnya soal bentuk, bukan selera — lalu spesifikasinya bisa
> ditulis sekali dan benar.**
