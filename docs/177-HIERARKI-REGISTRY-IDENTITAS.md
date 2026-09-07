# 177 — §11.4–§11.7 Agent Hierarchy, Registry, Capability & Identity

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.4 — Agent Hierarchy

> Jangan membuat semua agent sejajar. Gunakan **hierarchy**.

```
HumanVerse Supreme Orchestrator
│
├── Planning Agent · Reasoning Agent · Memory Agent · Context Agent
│
├── Domain Agents
│   Health · Habit · Learning · Career · Fashion · Travel
│   Finance Behavior · Social · Lifestyle
│
├── Action Agents
│   Calendar · Communication · Search · Booking · Automation · Device
│
└── Governance Agents
    Safety · Security · Policy · Evaluation · Audit
```

> Yang paling penting: **Governance layer bukan agent biasa.** Ia harus berada
> **di luar jalur kepentingan** agent yang melakukan action.

---

> ⭐⭐ **Kalimat tentang Governance itu adalah §8.42 (Control Plane) yang
> diterapkan pada agent** — dan ia menyelesaikan masalah yang tidak pernah
> dinyatakan: kalau SafetyAgent adalah agent biasa, ia bersaing memperebutkan
> sumber daya dan perhatian dengan agent yang diawasinya. Menempatkannya di
> luar jalur kepentingan membuat pengawasan berarti sesuatu.

> ⭐ **`Action Agents` sebagai kategori tersendiri adalah pembagian yang benar
> dan baru.** Enam agent yang seluruh pekerjaannya bertindak **keluar** —
> itu persis lingkup **B-19** ([#47](../../issues/47)), dan memisahkannya dari
> Domain Agents membuat batas risikonya bisa ditulis per kategori, bukan per
> agent.

> ⭐ **Health Agent dan Lifestyle Agent kembali.** Butir **E-35** mencatat
> naskah 5 kehilangan HealthAgent, GroomingAgent, ProductivityAgent,
> EntertainmentAgent, dan ResearchAgent. **Health kembali**, dan **Lifestyle
> mendapat agent untuk pertama kalinya** — itu separuh jawaban untuk **A-20** /
> [#4](../../issues/4) (*Mental Wellness & Lifestyle: dibuang atau ditunda*).
>
> 🛑 **Separuh yang lain tidak datang: Mental Wellness masih tanpa agent
> setelah lima belas naskah** — dan ia domain dengan beban hukum tertinggi
> (**C-3** / [#21](../../issues/21)). Journal tetap ada di V0.

> 🛑 **Lima agent muncul di contoh naskah ini tapi tidak ada di hierarki
> §11.4** — pola **E-38** (*PreparationAgent*) pada skala lima kali lipat:
>
> | Agent | Muncul di |
> |---|---|
> | **Productivity Agent** | §11.59 langkah 5 |
> | **Weather Agent** | §11.19, dan §11.20 sebagai `to: weather-agent` |
> | **Transportation Agent** | §11.19 |
> | **Hotel Agent** | §11.19 |
> | **Budget Agent** | §11.19, §11.21 |
>
> Daftar agent kini versi **kelima** (14 → 22 → 8 → 25), dan untuk kelima
> kalinya daftar dan contoh tidak sepakat. Lihat **E-95**.

> 🛑🛑 **Dan `Calendar Agent` + `Weather Agent` menggerus H-11 — keputusan
> keempat yang tergerus.**
>
> **H-11** ditutup dengan tegas: *"Weather & Calendar = **TOOL**, bukan agent."*
> Naskah 5 §13 secara khusus menulis *"Calendar disebut Tool di sini"*, dan
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) mendaftarkan `weather.get` dan
> `calendar.get` sebagai tool registry V2.
>
> Butir **E-28** mencatat kenapa butir ini pernah terbuka: naskah 4 §13 memakai
> `WeatherAgent` sebagai contoh komunikasi antar-agent, **lengkap dengan pesan
> `"to": "WeatherAgent"`**. Sekarang §11.20:
>
> ```json
> { "from": "travel-agent", "to": "weather-agent", "intent": "request_forecast" }
> ```
>
> **Konstruksi yang sama persis, di peran yang sama persis.** Dan §11.4
> menempatkan Calendar Agent di antara Action Agents.
>
> ⚠️ Sementara di naskah yang sama, calendar adalah **tool** di tiga tempat:
> `tools: [habit_api, calendar_api]` (§11.5) · *"Calendar Tool"* (§11.12) ·
> `tool: calendar.create_event` (§11.13).
>
> Bisa jadi maksudnya *agent tipis yang memiliki tool itu* — tapi itu harus
> ditulis, karena kalau tidak, dua orang akan membangun dua benda. Lihat
> **E-94**. H yang tergerus: **H-8** (dibatalkan) · **H-10** (monorepo) ·
> **H-13** (rencana kanonik) · sekarang **H-11**.

---

## §11.5 — Agent Registry

```yaml
agent:
  id: habit-coach
  version: 1.4.0

  purpose:
    - habit_tracking
    - habit_planning
    - habit_recommendation

  capabilities:
    - read_habits
    - create_habit
    - update_habit
    - analyze_behavior

  tools:
    - habit_api
    - calendar_api

  memory:
    read:  [ habit_memory, behavioral_memory ]
    write: [ habit_memory ]

  risk_level: R1

  autonomy:
    max_level: L2
```

> Ini menjadi **Agent Contract**.

---

> ⭐⭐⭐ **Ini menutup E-68 / [#61](../../issues/61) — dua field yang saya
> keluhkan kembali, dan satu field baru menyelesaikan #67.**
>
> | Field | n4 §11 | n5 §14 | n10 DP-L8 | n12 §8.14 | **n15 §11.5** |
> |---|---|---|---|---|---|
> | `purpose` | ✅ | ✅ | ❌ | ❌ | ✅ **kembali** |
> | `risk_level` | ✅ | ✅ | ❌ | ✅ | ✅ (kini `R1`) |
> | `memory.read` / `.write` | ✅ dua | ✅ dua | ⚠️ read | 🛑 **satu** | ✅ **dua lagi** |
> | `requires_confirmation` | — | ✅ | ❌ | ➡️ policy | ➡️ policy §11.37 |
> | **`autonomy.max_level`** | — | — | — | — | ✅ **baru** |
>
> `memory_scope` tunggal naskah 12 membuat agent yang boleh **membaca** sebuah
> scope otomatis boleh **menulisinya** — membatalkan dua batas paling halus di
> spesifikasi (`coach-agent` hanya menulis `coaching_notes`; `memory-agent`
> membaca semua **kecuali** `journal_raw`). Pemisahannya kembali.
>
> ⭐⭐ **Dan `risk_level: R1` berdampingan dengan `autonomy.max_level: L2` di
> satu berkas adalah jawaban untuk E-77 / [#67](../../issues/67)** — dua tangga
> yang di naskah 13 memakai penomoran yang sama dengan arti terbalik, kini
> punya huruf sendiri-sendiri dan hidup berdampingan tanpa bisa
> disalahartikan. Lihat **H-21**.

> ⚠️ **Tiga field spesifikasi tidak ada di sini:** `kind` (`core`/`domain`/
> `third_party`), `status`, dan `evaluation.gates`. Yang ketiga paling
> menentukan — aturan 4 [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> mewajibkan `evaluation.gates.safety >= 0.95` saat registrasi. §11.32 memberi
> KPI dan §11.55 memberi matriks evaluasi, tapi keduanya **pengukuran setelah
> jalan**, bukan **gerbang sebelum registrasi**. Keduanya perlu.

---

## §11.6 — Capability-Based Architecture

> Agent tidak boleh memiliki `"access_to_everything"`.

```
Agent → Capabilities → Specific Tools → Specific Resources
```

**Habit Agent**

```
CAN:     ✓ read habit  ✓ create habit  ✓ recommend schedule
CANNOT:  ✗ access bank  ✗ send email  ✗ delete account
         ✗ access private documents
```

---

> ⭐ **Tiga larangan pertama memetakan tepat ke tangga risiko §11.15**:
> `access bank` → R3/R4, `send email` → R3, `delete account` → R4. Larangan dan
> tangga akhirnya konsisten — sama seperti §8.8 yang juga cocok.

> ⚠️ **`access private documents` adalah larangan baru, dan ia menyentuh
> jurnal tanpa menyebutnya.** Naskah 5 §15 menempatkan *private journal* di
> daftar DENY bahkan untuk agent internal; naskah 12 §8.6 melewatkannya
> (**G-9**); di sini ia kembali dalam bentuk *"private documents"*. Kalau itu
> mencakup jurnal, sebaiknya ditulis dengan namanya.

---

## §11.7 — Agent Identity

```
Agent Identity
├── agent_id     ├── trust_score     ├── risk_level
├── owner        ├── capabilities    └── credentials
├── version      ├── permissions
├── developer
```

> **Jangan menggunakan identity user untuk semua action.**

```
USER          → requested
ORCHESTRATOR  → delegated
TRAVEL_AGENT  → prepared booking
BOOKING_AGENT → executed reservation
```

> Semuanya **traceable**.

---

> ⭐⭐⭐ **Rantai empat baris itu menyelesaikan masalah yang saya catat di
> E-69: `SecurityEvent` §8.41 membuang `user_id`, sehingga aktor dan pemilik
> data tidak bisa dibedakan.** Di sini bukan hanya dibedakan — ada **empat**
> aktor berbeda dalam satu permintaan, dan tiap langkah punya identitasnya.
>
> Itu juga yang dibutuhkan `audit_logs` spec/01 yang memisahkan `actor_id` dari
> `user_id`: dengan delegasi berantai, satu kolom `actor_id` tidak cukup — perlu
> **rantai delegasi**, bukan satu aktor. Field yang belum ada:
> `delegated_by`.
>
> Dan *"jangan menggunakan identity user untuk semua action"* adalah pernyataan
> yang menutup jalan pintas paling umum di sistem seperti ini: memberi agent
> token penggunanya. Kalau itu dilakukan, seluruh jejak audit runtuh menjadi
> *"pengguna melakukannya"*.

> ⭐ **`owner` dan `developer` sebagai field terpisah** — yang pertama
> bertanggung jawab, yang kedua menulis. Untuk marketplace (Phase 14) keduanya
> berbeda, dan `Developer Reputation` §11.33 bersandar pada yang kedua.

> ⚠️ **`owner` ada di sini tapi tidak di manifest §11.5**, sementara naskah 12
> §8.14 menempatkannya di manifest. Satu benda, dua tempat — dan identity vs
> manifest adalah pembedaan yang masuk akal (identity = siapa dia, manifest =
> apa yang boleh dia lakukan), asalkan dinyatakan.
