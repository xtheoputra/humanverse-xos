# 206 — Repository, Sub-Phase, Definition of Done & Posisi (naskah ketujuhbelas)

> Merekam **§13.37–§13.40**.
> 🛑 **Berkas ini memuat temuan KEDUA terberat naskah ini** — `Rollback` yang
> hilang. Lihat catatan di bawah §13.39.

---

## §13.37 — Repository Architecture

```
human-os/
│
├── kernel/          → runtime · state · identity · context · lifecycle
├── intent/          → parser · classifier · goal-mapper · intent-memory
├── memory/          → working · episodic · semantic · procedural · behavioral · preference
├── life-graph/      → entities · relationships · goals · projects · tasks · outcomes
├── scheduler/       → calendar · energy · attention · priority · optimization
├── automation/      → triggers · workflows · rules · execution
├── agents/          → runtime · registry · orchestration · lifecycle
├── devices/         → abstraction · mobile · desktop · wearable · iot · sensors
├── applications/    → core · marketplace · sandbox
├── interfaces/      → chat · voice · dashboard · notifications · command-center
├── sdk/             → python · typescript · flutter · kotlin · swift
├── control-plane/   → permissions · policies · risk · budgets · audit
└── observability/
```

> 🛑 **Ini pohon `human-os/` KEDUA di naskah yang sama, dan ia tidak cocok
> dengan [§13.2](198-PHASE-13-IKHTISAR-DAN-HUMANOS-CORE.md).** §13.2 memberi
> **17 direktori datar**; ini **13 bersarang**.
>
> Sebagian besar selisihnya hanya penataan ulang — `runtime`, `identity`,
> `state`, `context` masuk ke `kernel/`; `permissions` dan `policy` masuk ke
> `control-plane/`; `scheduling` → `scheduler/`; `intents` → `intent/`;
> `workflows` → `automation/workflows/`. Itu wajar.
>
> **Tiga direktori benar-benar HILANG, tanpa penampung:**
>
> | Hilang dari §13.37 | Kenapa itu berarti |
> |---|---|
> | `capability/` | §13.9 menjadikan Capability System **primitif keamanan inti** — objek yang memegang `risk_level`, `required_permissions`, dan `allowed_agents` |
> | `agency/` | *Agency* adalah nama Phase 11 dan kotak terakhir di kernel diagram §13.18 |
> | `events/` | §13.12 menjadikan **Event Bus arsitektur utamanya** |
>
> Dan enam direktori muncul yang tidak ada di §13.2: `life-graph/`, `agents/`,
> `devices/`, `sdk/`, `control-plane/`, `observability/`.
>
> ⭐ Yang versi kedua ini **lebih baik** dalam satu hal penting: `control-plane/`
> mengumpulkan `permissions · policies · risk · budgets · audit` di satu tempat.
> Itu bentuk yang benar — kelima gerbang adalah satu bidang tanggung jawab, dan
> §13.2 menyebarkannya. **Pilih §13.37**, lalu kembalikan `capability/`,
> `agency/`, dan `events/` ke dalamnya.
>
> Ini pola yang sudah berulang di naskah panjang: **daftar ganda.** Jangan
> ditambal diam-diam — catat mana yang dibuang.

---

## §13.38 — Sub-Phase Implementation

| Kode | Isi |
|---|---|
| **H13.1** | HumanOS Kernel — runtime, lifecycle, identity, state |
| **H13.2** | Intent OS — natural language → intent → goal/action |
| **H13.3** | Context & Memory OS |
| **H13.4** | Life Graph |
| **H13.5** | Personal Scheduler — time + energy + attention |
| **H13.6** | Workflow & Automation |
| **H13.7** | Personal Agent Runtime |
| **H13.8** | Device OS |
| **H13.9** | HumanOS Applications |
| **H13.10** | HumanOS SDK |
| **H13.11** | HumanOS Marketplace |
| **H13.12** | Personal AI Command Center |

> 🛑 **Huruf KEENAM untuk benda yang sama — dan yang ini bertabrakan dengan
> penomoran berkas audit itu sendiri.**
>
> `S8.x` (sprint) · `C1–C10` · `M10.x` (milestone) · `A11.x` · `T12.x` ·
> sekarang **`H13.x`**.
>
> Lima yang pertama sekadar melelahkan. Yang keenam berbahaya: berkas
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) memakai **`H-nn`** untuk
> *keputusan yang sudah ditutup*, dan di dalamnya ada **`H-13`** — butir tentang
> *"Phase 1/2/3 atau V0–V6"*. Sekarang **`H13.1`** berarti *"HumanOS Kernel"*.
>
> `H-13` dan `H13.1` berbeda satu tanda hubung, dan keduanya hidup di repo yang
> sama, dalam kalimat yang sama-sama membahas fase. Usul **E-107** tetap yang
> terbaik dan sekarang mendesak: pakai **`S<fase>.<n>`** — di sini `S13.1`–`S13.12` —
> berlaku surut untuk kelima sumbu lainnya.

---

## §13.39 — Definition of Done

Phase 13 dianggap selesai jika HumanVerse sudah mampu:

```
✓ Understand natural human intent    ✓ Maintain personal context
✓ Maintain personal memory           ✓ Maintain life graph
✓ Understand goals                   ✓ Schedule intelligently
✓ Manage attention                   ✓ Create workflows
✓ Coordinate agents                  ✓ Use external tools
✓ Interact with devices              ✓ Simulate decisions
✓ Execute bounded actions            ✓ Verify outcomes
✓ Learn from feedback                ✓ Respect permissions
✓ Enforce safety                     ✓ Audit every sensitive action
✓ Support third-party apps           ✓ Support third-party agents
✓ Provide unified AI interface
```

> 🛑🛑🛑 **`Rollback` HILANG — pengaman yang baru saja mengisi lubang G-8 /
> [#65](../../issues/65) satu naskah lalu.**
>
> **G-8** mencatat *Human Override* sebagai salah satu dari dua butir yang
> dijanjikan untuk Phase 8 dan tidak pernah datang: §8.17 mencegah **sebelum**
> aksi, §8.35 menghentikan **semuanya**, dan tidak ada yang membatalkan atau
> membalik **satu** keputusan yang sudah berjalan.
>
> **§11.61 mengisinya**, dengan enam kata kerja kendali:
>
> ```
> Control = Pause · Resume · Cancel · Revoke · Kill · Rollback
> ```
>
> **§13.34 memberi Safety Kernel enam kekuasaan juga** — tetapi bukan enam yang
> sama:
>
> ```
> DENY · BLOCK · PAUSE · REQUIRE_CONFIRMATION · REVOKE · KILL
> ```
>
> | | Phase 11 §11.61 | Phase 13 §13.34 |
> |---|---|---|
> | Mencegah sebelum | — | `DENY` `BLOCK` `REQUIRE_CONFIRMATION` |
> | Menghentikan saat berjalan | `Pause` `Cancel` `Kill` `Revoke` | `PAUSE` `REVOKE` `KILL` |
> | **Membalik sesudah** | **`Rollback`** | **— tidak ada** |
> | Melanjutkan | `Resume` | — |
>
> Naskah ini **menambah tiga kekuasaan pencegahan dan membuang tiga kekuasaan
> korektif** — termasuk satu-satunya yang bekerja **sesudah** tindakan terjadi.
> Kata *rollback*, *undo*, dan *revert* tidak muncul satu kali pun di
> keseluruhan naskah ketujuh belas; state machine §13.36 pun hanya menawarkan
> `FAILED → RECOVERING → REPLAN`, yang **mengulang**, bukan **membatalkan**.
>
> **Kenapa ini bersenyawa dengan temuan §13.10 dan menjadi lebih berat daripada
> jumlah keduanya:**
>
> [§13.10](200-LIFE-GRAPH-CAPABILITY-DAN-PERMISSION.md) menurunkan pembelian
> dan kontrol perangkat dari **R4 = `DENY`** menjadi **"Ask Every Time"**. §13.39
> menghapus `Rollback`. Digabung, keduanya menghasilkan keadaan yang persis
> ingin dicegah §11.15:
>
> > sebuah tindakan **yang tidak bisa ditarik** kini bisa lewat dengan **satu
> > ketukan**, dan **tidak ada jalan kembali** sesudahnya.
>
> §11.15 menaruh dua kunci pada pintu itu — R4 ditolak, dan Rollback tersedia
> kalau sesuatu tetap lolos. Naskah ini melepas keduanya, di dua bagian yang
> berbeda, sehingga tak satu pun terlihat sebagai keputusan besar saat dibaca
> sendiri-sendiri.
>
> Yang minimum harus diputuskan sebelum satu baris kode Phase 13: **`Rollback`
> masuk kembali ke daftar kekuasaan Safety Kernel**, atau ditulis di mana ia
> tinggal sekarang.

> ⚠️ **Dua puluh satu kriteria, nol angka.** *"Schedule intelligently"*,
> *"Manage attention"*, *"Enforce safety"* — tak satu pun bisa dijawab dengan
> ya/tidak oleh orang lain. **§8.45 dan §9.40** memberi bentuk yang benar: baris
> yang bisa dijawab ya/tidak, bukan sifat. Dua naskah berturut-turut sudah
> melakukannya; kebiasaan itu tidak diteruskan di sini.
>
> ⚠️ Ditambah: **`Respect permissions` dan `Enforce safety` adalah dua baris
> yang paling tidak boleh kabur di seluruh daftar**, dan keduanya paling kabur.

---

## §13.40 — Posisi HumanVerse setelah Phase 13

```
                    HUMAN
                      │
                      ▼
                ┌───────────┐
                │ HumanOS   │
                │           │
                │ Intent    │
                │ Context   │
                │ Memory    │
                │ LifeGraph │
                │ Scheduler │
                │ Workflow  │
                │ Agents    │
                └─────┬─────┘
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
  PERCEPTION      COGNITION       AGENCY
       │              │              │
       └──────────────┼──────────────┘
                      ▼
                DIGITAL TWIN
                      │
                WORLD MODEL
                      │
                 SIMULATION
                      │
                 DECISION
                      │
                 REAL WORLD
                      │
                   FEEDBACK
                      │
                  LEARNING
                      │
                  HUMANOS
```

> HumanVerse bukan lagi sekadar *"AI personal assistant"*. Lebih tepat:
> **HumanVerse — Personal AI Operating System.**
> *One AI. Infinite Human Growth.*

Phase 9–13 pada dasarnya membangun **otak, mata, tangan, simulator, dan
operating system** HumanVerse.

Berikutnya: **Phase 14 — HumanVerse Autonomous Intelligence & Collective Agent
Ecosystem** — jaringan agent yang bekerja lintas domain, organisasi, aplikasi,
dan berkolaborasi dengan agent pihak ketiga, tetap di bawah governance
HumanVerse.

> ⭐⭐ **Diagram ini menutup gelang: `LEARNING → HUMANOS`.** Untuk pertama
> kalinya dalam lima naskah fase, arsitekturnya digambar sebagai lingkaran, bukan
> tumpukan. Itu bentuk yang benar untuk sistem yang mengaku beradaptasi.

> ⭐ **Slogan `One AI. Infinite Human Growth.` sama persis dengan README.**
> Positioning bertahan tujuh belas naskah — salah satu dari sedikit hal di repo
> ini yang tidak pernah bergeser.

> ⚠️ **Phase 14 disebut sebagai "berikutnya yang sangat logis", dan peta 15 fase
> memang menempatkan Marketplace di sana.** Tetapi §13.27 sudah membangun
> HumanOS Store di Phase 13. Kalau Store lahir di 13 dan Marketplace di 14,
> perbedaan keduanya harus ditulis — kalau tidak, dua fase mengerjakan benda yang
> sama.

---

## Catatan penomoran temuan

Temuan di seluruh berkas `198`–`206` **sengaja belum diberi nomor `E-`**. Saat
naskah ini direkam, naskah keenam belas (Phase 12) masih di pohon kerja dan
belum di-commit; nomor `E-` terakhirnya (`E-107`) belum final.

Yang harus dikerjakan sesudah naskah 16 mendarat:

1. Lipat temuan ini ke [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) dengan nomor
   `E-` berikutnya.
2. Perbarui `README.md` — jumlah dokumen, jumlah naskah, dan daftar naskah.
3. Buat GitHub Issue untuk dua temuan terberat: **"Ask Every Time" vs R4=DENY**
   (§13.10) dan **`Rollback` hilang** (§13.39) — keduanya menyentuh keselamatan
   dan saling menguatkan.
