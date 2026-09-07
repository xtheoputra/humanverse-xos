# 203 — Application Model, API, SDK, Manifest & Marketplace (naskah ketujuhbelas)

> Merekam **§13.23–§13.28**.
> 🛑 **Berkas ini memuat manifest KEENAM** — lihat §13.26.

---

## §13.23 — HumanOS Application Model

Aplikasi pihak ketiga menjadi **HumanOS Apps**.

```
HumanOS
   ├── Core Apps
   ├── HumanVerse Apps
   └── Third-Party Apps
```

Misalnya: `CareerOS` · `LearningOS` · `FitnessOS` · `FinanceOS` · `TravelOS` ·
`FashionOS` · `SocialOS` · `ProductivityOS`

Semua menggunakan HumanOS core.

> ⚠️ **Delapan nama ber-akhiran `OS` untuk benda yang bukan operating system.**
> Naskah ini sudah memakai *OS* untuk lima hal berbeda: HumanOS (kernel),
> Context OS, Memory OS, Knowledge OS, Attention OS — sekarang ditambah delapan
> aplikasi. *OS* berhenti menandai apa pun. Ini kecil dibanding tabrakan
> penomoran, tapi ia menyentuh dokumen yang akan dibaca developer luar.

---

## §13.24 — HumanOS API

```
POST /v1/intents          GET  /v1/context
GET  /v1/state            GET  /v1/memory

POST /v1/goals            POST /v1/workflows
POST /v1/automations

POST /v1/agents/tasks
POST /v1/actions/prepare
POST /v1/actions/execute

GET /v1/life-graph        GET /v1/digital-twin
POST /v1/simulations      POST /v1/decisions

GET /v1/attention         POST /v1/notifications
```

> ⭐⭐⭐ **`/actions/prepare` dan `/actions/execute` DIPISAH menjadi dua
> endpoint.** Ini tangga L yang ditegakkan oleh **bentuk API**, bukan oleh
> kebijakan: L2 (*Prepare*) dan L4 (*Execute*) tidak bisa tertukar karena
> alamatnya berbeda. Pengaman yang ditegakkan tipe/bentuk jauh lebih kuat
> daripada yang ditegakkan komentar — dan ini contoh terbaiknya di seluruh
> naskah.

> ⚠️ **`GET /v1/memory` tanpa parameter scope di daftar ini.** §13.6 memberi
> memory delapan medan termasuk `scope` dan `sensitivity`; endpoint yang
> mengambil "memory" tanpa menyebut scope adalah persis bentuk yang **E-39**
> khawatirkan. Daftar endpoint memang ringkas, tapi ini yang akan disalin orang.

---

## §13.25 — HumanOS SDK

```
humanverse.intent(...)    humanverse.context(...)
humanverse.memory(...)    humanverse.goal(...)
humanverse.agent(...)     humanverse.workflow(...)
humanverse.action(...)
```

Contoh konsep:

```python
goal = hv.goals.create(
    name="Learn AI",
    horizon="6_months"
)

hv.workflow.create(
    trigger="goal.created",
    action="generate_learning_plan"
)
```

---

## §13.26 — HumanOS App Manifest

Setiap application harus mendeklarasikan:

```yaml
name: learning-app

permissions:
  - profile.read
  - goals.read
  - calendar.read
  - calendar.write

capabilities:
  - learning.plan
  - learning.progress

risk_level: R1
```

Kemudian HumanOS **sandbox** aplikasi tersebut.

> 🛑🛑 **Manifest KEENAM, dan ia lebih lemah daripada yang kelima — yang baru
> dipulihkan satu naskah lalu.**
>
> [`177`](177-HIERARKI-REGISTRY-IDENTITAS.md) melacak riwayat medan manifest
> lintas naskah, dan naskah 15 (§11.5) **memulihkan** dua medan yang sempat
> hilang. Manifest di sini menjatuhkan empat:
>
> | Medan | n4 | n5 | n10 | n12 | **n15 §11.5** | **n17 §13.26** |
> |---|---|---|---|---|---|---|
> | `purpose` | ✅ | ✅ | ❌ | ❌ | ✅ **kembali** | ❌ **hilang lagi** |
> | `memory.read` / `.write` | ✅ dua | ✅ dua | ⚠️ read | 🛑 satu | ✅ **dua lagi** | ❌ **tidak ada** |
> | `autonomy.max_level` | — | — | — | — | ✅ **baru** | ❌ |
> | `tools` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
> | `risk_level` | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
> | `capabilities` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
>
> **Bantahan yang harus dipertimbangkan lebih dulu:** *app* ≠ *agent*, jadi
> manifest yang berbeda mungkin memang disengaja. Itu masuk akal — tapi tidak
> menyelamatkannya, karena **§13.27 menaruh apps, agents, dan plugins di SATU
> marketplace**, dan §13.26 menutup dirinya dengan *"HumanOS sandbox aplikasi
> tersebut"*. Dua benda yang disandbox oleh mekanisme yang sama, dijual di
> etalase yang sama, tetapi satu mendeklarasikan lebih sedikit.
>
> Akibat langsungnya: **manifest yang paling lemah menjadi jalan yang paling
> mudah.** Developer yang tidak ingin mendeklarasikan `purpose`, batas memory,
> dan tingkat otonomi cukup mengemas pekerjaannya sebagai *app*, bukan *agent*.
>
> Yang paling mahal hilangnya adalah **`memory.read`/`.write`**. `permissions`
> di sini hanya memuat `profile.read`, `goals.read`, `calendar.read/write` —
> tidak ada satu pun yang menyebut memory. Naskah 15 baru saja memulihkan
> pemisahan baca/tulis itu karena `memory_scope` tunggal membatalkan dua batas
> paling halus di [`spec/05`](../spec/05-AGENT-CONTRACTS.md): `coach-agent`
> hanya menulis `coaching_notes`, dan `memory-agent` membaca semua **kecuali**
> `journal_raw`. Manifest app tidak punya tempat untuk menyatakan keduanya.

---

## §13.27 — HumanOS Store

Terhubung dengan **Phase 6 Developer Platform**.

```
                 HUMANVERSE
                     │
              HUMANOS PLATFORM
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Apps         Agents       Plugins
        │            │            │
        └────────────┼────────────┘
                     ▼
                Marketplace
```

Developer dapat membuat: AI agents · workflows · apps · integrations · tools ·
models · knowledge packs.

> ⚠️ **Marketplace punya rumah di Phase 14, bukan 13.** **E-86**/**H-20**
> mencatat *Marketplace → Phase 14* saat peta 15 fase menggantikan peta 12 fase,
> dan **A-15/C-7** menunggu di sana. Naskah ini membangunnya di Phase 13.
> Kemungkinan besar yang dimaksud adalah *fondasinya*, bukan etalasenya — tapi
> peta fase adalah satu-satunya sumbu penomoran yang sejauh ini stabil, dan
> sebaiknya tetap begitu.

> 🛑 **`models` dan `knowledge packs` dijual oleh pihak ketiga.** Keduanya
> membawa pertanyaan lisensi dan provenance yang belum pernah dibahas: sebuah
> *knowledge pack* adalah kumpulan pengetahuan yang **diterbitkan ulang**, dan
> bagian **C** (risiko hukum) sudah memuat butir sejenis untuk sumber luar.
> Sebuah *model* pihak ketiga yang berjalan di atas memory pribadi menuntut
> jawaban yang belum ada di mana pun.

---

## §13.28 — Personal Automation Marketplace

User bisa memasang automation:

*"Morning Intelligence"* · *"Weekly Life Review"* · *"AI Study Coach"* ·
*"Travel Planner"* · *"Wardrobe Assistant"* · *"Career Growth Agent"* ·
*"Personal Research Agent"*

> Tetapi setiap automation tetap tunduk pada permission/security HumanOS.

> ⭐⭐ **Kalimat penutupnya adalah pengaman, dan ia ditulis pemilik sendiri.**
> Automation pihak ketiga yang berjalan di atas data pribadi adalah permukaan
> serangan terbesar di seluruh Phase 13; menegaskan bahwa ia tetap lewat gerbang
> yang sama adalah kalimat yang tepat.
>
> ⚠️ Yang belum ada: automation dipasang **pengguna**, bukan developer — jadi
> ia butuh layar izin, dan layar izin satu-satunya di naskah ini adalah §13.10,
> yang justru melonggarkan pembelian dan kontrol perangkat menjadi *"Ask Every
> Time"*.
