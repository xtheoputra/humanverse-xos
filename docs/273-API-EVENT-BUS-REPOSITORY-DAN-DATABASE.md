# 273 — §20.26–§20.29 Civilization API, Event Bus, Repository & Database

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.26 — Civilization API

```
GET  /v1/civilization/state       POST /v1/civilization/simulations
GET  /v1/civilization/entities    POST /v1/civilization/impact-assessment
GET  /v1/civilization/events      GET  /v1/civilization/risks
POST /v1/civilization/scenarios   GET  /v1/civilization/resilience
POST /v1/civilization/coordination            GET /v1/civilization/provenance
```

---

> ⭐⭐ **`POST /v1/civilization/impact-assessment` menjadikan §20.18 sebagai
> ANTARMUKA** — sesuatu yang bisa diminta oleh siapa pun sebelum keputusan, bukan
> langkah internal yang bisa diam-diam dilewati. Bersama
> `GET …/provenance`, ini bentuk yang sudah dua kali dicatat sebagai butir **F**
> (§17.5 *"melihat siapa yang mengakses"*, §18.29): **jaminan yang bisa
> diperiksa dari luar.**

> 🛑 **Tetapi `POST /v1/civilization/coordination` adalah satu-satunya endpoint
> yang MENGGERAKKAN sesuatu — dan ia tidak menyebut persetujuan di mana pun.**
>
> Sembilan endpoint lain membaca atau mensimulasikan. Yang satu ini memicu
> `coordination_tasks` dan `coordination_sessions` (§20.29) — yaitu lapisan yang
> §20.28 taruh di `coordination/{task,resource,organization,emergency}/`.
> **`emergency/` di dalamnya.**
>
> §20.35 menetapkan bahwa jalur `ACTION` melewati `POLICY → RISK → IMPACT
> ASSESSMENT → HUMAN APPROVAL`. Sebuah endpoint HTTP yang bisa dipanggil
> langsung adalah **jalan pintas yang melewati keempatnya**, kecuali dinyatakan
> tidak. Ini bentuk **B-32** ([#110](../../issues/110)) — Safety Kernel di sisi
> yang salah dari adapter — pada permukaan API. ⭐ Perbaikannya konvensional:
> **`POST …/coordination` menghasilkan usulan berstatus `pending_approval`,
> bukan tindakan**, dan eksekusinya menuntut endpoint kedua yang membawa
> rujukan persetujuan. Lihat **E-150** / [#140](../../issues/140).

> 🛑 **Dan semuanya `/v1/…`, bukan `/api/v1`** ([`spec/04`](../spec/04-API-CONTRACTS.md))
> — **naskah KEEMPAT berturut-turut** sesudah §17.44, §18.29, dan §19.32.

---

## §20.27 — Civilization Event Bus

`CivilizationEventDetected · WorldStateChanged · EconomicStateChanged ·
TechnologyBreakthroughDetected · ScientificDiscoveryPublished ·
InfrastructureFailureDetected · ClimateSignalDetected · SupplyChainDisruption ·
CivilizationRiskChanged · PolicyChanged · LargeScaleScenarioCreated ·
**ImpactAssessmentCompleted**`

---

> ⭐⭐⭐ **`ImpactAssessmentCompleted` dan `LargeScaleScenarioCreated` menjadikan
> TATA KELOLA sebagai peristiwa — dan itu belum pernah ada.**
>
> Semua event sebelumnya di repo ini mengabarkan **apa yang terjadi di dunia**
> atau **apa yang dilakukan pengguna**. Dua ini mengabarkan **apa yang dilakukan
> sistem tata kelolanya sendiri**. Akibatnya konkret dan besar: penilaian dampak
> yang **tidak pernah terjadi** menjadi terlihat sebagai event yang tidak
> muncul, dan itu satu-satunya cara Pasal 4 Konstitusi (*Auditability*) bisa
> ditegakkan tanpa memercayai komponen yang diaudit.

> ⚠️ **Tetapi tidak ada satu pun event untuk KONSTITUSI itu sendiri.** Tidak ada
> `ConstitutionViolationDetected`, tidak ada `ApprovalGranted` maupun
> `ApprovalDenied`, tidak ada `OverrideInvoked` — padahal Pasal 10 menetapkan
> *human override* dan §20.35 menetapkan `HUMAN APPROVAL`. Sebuah persetujuan
> yang tidak menghasilkan peristiwa tidak bisa dihitung, diaudit, maupun
> ditinjau ulang. ⭐ Ini kekurangan yang paling murah ditutup di seluruh naskah:
> **tiga nama event.**

> 🛑 **Dan seluruhnya PascalCase**, sementara
> [`spec/03`](../spec/03-EVENT-CONTRACTS.md) menetapkan `domain.verb` huruf
> kecil. Pelanggaran [#38](../../issues/38) yang berulang untuk kesekian kalinya
> — bersama `/v1/` di §20.26, naskah ini melanggarnya di **dua** sumbu
> sekaligus, seperti naskah 21 dan 22. Lihat **E-150**.

---

## §20.28 — Civilization Repository

```
civilization-platform/
├── civilization-core/  ├── coordination/    ├── resilience/     ├── protocols/
├── civilization-twin/  ├── governance/      ├── sustainability/ ├── sdk/
├── civilization-model/ │   └── constitution/├── resource-intel/ ├── observability/
├── simulation/         ├── trust/           ├── civilization-   ├── audit/
├── collective-         ├── sovereignty/     │   agents/         └── research/
│   intelligence/       │   └── data-vault/  ├── federation/
│   └── disagreement/
```

---

> ⭐⭐⭐⭐ **Tiga direktori di sini mengubah prinsip menjadi TEMPAT — dan itu
> kebiasaan terbaik naskah ini.**
>
> | Direktori | Prinsip yang diberi tempat |
> |---|---|
> | **`governance/constitution/`** | sepuluh pasal §20.16 punya kode, bukan paragraf |
> | **`collective-intelligence/disagreement/`** | **G-17** / [#121](../../issues/121) — ketidaksepakatan yang dipertahankan |
> | **`sovereignty/{privacy,consent,data-vault,ownership}/`** | §20.13, dan `ownership` belum pernah ada |
>
> Yang kedua paling menonjol: sebuah usul yang ditulis dua naskah lalu kini
> punya direktori. ⭐ Dan **`observability/` serta `audit/` sebagai pohon tingkat
> pertama** juga baru — keduanya menjadikan Pasal 3 dan 4 (Transparency,
> Auditability) sesuatu yang punya rumah.

> 🛑 **Tetapi `civilization-platform/` menggerus H-10 untuk KESEPULUH kalinya —
> naskah KEDUA BELAS berturut-turut yang menyentuh struktur repo.**
>
> | Direktori | Sudah ada di |
> |---|---|
> | `simulation/` | `spatial-os/` · `robotics/` · `health-bio/` · `global-intelligence/` · `scientific-discovery/` · Phase 12 — **ketujuh kalinya** |
> | `trust/` · `federation/` · `protocols/` · `sdk/` | `global-intelligence/` |
> | `research/` | pohon tingkat-atas sejak naskah 9 · `health-bio/` · `scientific-discovery/` |
> | `governance/` | `global-intelligence/` (naskah 22) |
>
> Dan `sovereignty/privacy/` menjadikan **pohon keamanan/privasi SEBELAS**.

> 🛑 **`governance/` berada DI DALAM pohon fase untuk KETIGA kalinya — dan pola
> itu sudah terbukti tidak diwariskan.**
>
> Naskah 22 menaruhnya di `global-intelligence/`; **E-139**
> ([#129](../../issues/129)) mengusulkan menaikkannya satu tingkat sebab tata
> kelola yang hidup di satu fase hanya mengatur fase itu. Naskah 23 **tidak
> mewarisinya** dan memakai `ethics/` + `safety/` sendiri (**E-145** /
> [#138](../../issues/138)). Naskah 24 membuat salinan ketiga.
>
> Yang menjadikannya lebih berat kali ini: **§20.16 menyatakan Konstitusi
> sebagai *"governance layer tertinggi"***, dan `constitution/` berada di dalam
> `civilization-platform/governance/` — yaitu **di dalam satu fase, mengatur
> semua fase**. Sebuah lapisan tertinggi yang bersarang di dalam salah satu
> lapisan yang diaturnya tidak bisa ditegakkan oleh struktur; ia bergantung pada
> kesediaan. Lihat **E-149** / [#143](../../issues/143).

---

## §20.29 — Database

`civilization_states · entities · relationships · twins · **snapshots** ·
scenarios · simulations · risks · warnings · impacts` ·
`coordination_{tasks,sessions,decisions}` · `resource_{states,dependencies}` ·
`governance_{policies,decisions}` · `impact_assessments` ·
`identity_nodes · trust_records · reputation_records` ·
`federation_{nodes,messages,policies}` · `resilience_models · crisis_events ·
recovery_plans`

---

> ⭐⭐⭐ **`civilization_snapshots` dan `governance_decisions` adalah dua tabel
> yang menjadikan sistem ini bisa ditanyai tentang masa lalunya.**
>
> `snapshots` menyimpan **keadaan pada suatu waktu**, bukan hanya keadaan
> sekarang — dan tanpa itu, `MEASURE` §20.24 tidak punya pembanding: mustahil
> mengukur akibat sebuah tindakan kalau keadaan sebelum tindakan sudah ditimpa.
> `governance_decisions` + `impact_assessments` menjadikan keputusan tata kelola
> **punya baris**; sesuatu yang hanya berupa langkah proses akan hilang tanpa
> jejak ketika dilewati, sedangkan baris meninggalkan lubang yang terlihat.

> 🛑 **Tetapi tidak ada satu pun tabel untuk KONSTITUSI, persetujuan, maupun
> override.**
>
> Sepuluh pasal §20.16 disebut *"governance layer tertinggi"*, dan §20.35
> menaruh `HUMAN APPROVAL` sebagai gerbang wajib jalur aksi. Tak satu pun punya
> tempat penyimpanan: tidak ada `approvals`, `constitution_checks`, maupun
> `override_events`. ⇒ Persetujuan yang tidak tersimpan **tidak bisa diaudit
> (Pasal 4)**, dan pelanggaran yang tidak tercatat tidak bisa ditindaklanjuti.
> ⭐ Perbaikannya tiga tabel, dan `audit/` §20.28 sudah menyediakan rumahnya.

> 🛑 **Dan tidak ada kolom retensi, kedaluwarsa, maupun klasifikasi — untuk
> KEEMPAT kalinya berturut-turut** (§17.43 punya, §18.28 tidak, §19.31 tidak,
> §20.29 tidak). Yang menjadikannya khusus di sini: **§20.13 memberi pengguna
> kendali `How long`** — sebuah kendali yang tidak punya kolom penyimpanan tidak
> bisa ditegakkan (**B-35** / [#127](../../issues/127), **C-9** /
> [#22](../../issues/22)).

> ⚠️ `trust_records` dan `reputation_records` bertahan sebagai dua tabel untuk
> pembedaan yang belum pernah ditulis — **naskah ketiga** (§18.28 · §19 · di
> sini).
