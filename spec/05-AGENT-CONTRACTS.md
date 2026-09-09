# 05 — Agent Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menurunkan manifest naskah 5 §14 menjadi skema yang bisa divalidasi.

---

## Skema manifest

```yaml
# agents/<name>/manifest.yaml
name:        coach-agent          # ^[a-z][a-z0-9-]{2,39}$
version:     1.0.0                # semver, wajib
kind:        core                 # core | domain | third_party
status:      active               # draft | active | deprecated | disabled

purpose:                          # 1-5 baris, untuk manusia
  - daily coaching conversation
  - weekly review

capabilities:                     # kontrak mesin; nama snake_case
  - daily_coaching
  - weekly_review

tools:                            # harus ada di tool registry
  - habit.list
  - habit.streak
  - memory.search
  - checkin.get

memory:
  read:  [ habits, goals, checkins, mood ]
  write: [ coaching_notes ]

model:
  class:    reasoning             # simple | reasoning | vision | embedding
  fallback: simple

risk_level: 1                     # 0-4
requires_confirmation: []         # daftar capability yang selalu minta izin

evaluation:
  suite: coach-agent-v1
  gates:
    safety:          0.99         # turun di bawah ini = tidak boleh production
    user_satisfaction: 0.70
  budget:
    p95_latency_ms:  4000
    cost_usd_per_run: 0.02
```

Aturan validasi yang ditegakkan saat registrasi:

| # | Aturan |
|---|---|
| 1 | Setiap nama di `tools` **harus ada** di tool registry. Manifest dengan tool tak dikenal ditolak. |
| 2 | Setiap scope di `memory.read`/`write` **harus ada** di daftar scope resmi. |
| 3 | `risk_level >= 3` **wajib** punya isi `requires_confirmation`. |
| 4 | `evaluation.gates.safety` **wajib** ada dan `>= 0.95`. |
| 5 | Satu `name` hanya boleh punya **satu** baris `status: active`. |
| 6 | `kind: third_party` **tidak boleh** meminta scope `journal`, `finance`, atau `health`. |
| 7 🔧 | Tool yang akibatnya sampai kepada **orang selain pemegang akun** (`reaches_third_party: true`) **wajib** `risk_level >= 3`. Manifest yang menurunkannya **ditolak**. |
| 8 🔧 | Tool **tanpa** `risk_level` **ditolak** saat registrasi. **Tidak ada bawaan** — kelalaian berhenti di validator, bukan di produksi. |
| 9 🔧 | Perluasan aturan 6: `kind: third_party` juga **tidak boleh** meminta scope `spatial`, `location`, `people`, atau `csi`. |

> Aturan 6 adalah penegakan **C-7/A-15** di lapisan yang paling murah:
> selama marketplace belum punya proses review, sandbox, dan perjanjian
> pemroses data, agent pihak ketiga tidak bisa meminta data paling sensitif —
> ditolak oleh validator, bukan oleh kebijakan tertulis.

> 🔧 **Aturan 7 (ditambahkan 9 Sep 2026, keputusan didelegasikan K-1).**
> §11.15 menaruh `send low-risk message` di **R2** — di bawah ambang
> konfirmasi yang **H-15** ([#5](../../issues/5)) tetapkan di R3 — sementara
> tiga tangga risiko sebelumnya menaruh pengiriman pesan di **3/R3**, dan kata
> *“low-risk”* tidak pernah didefinisikan di mana pun. Tetangganya di baris yang
> sama, `purchase low-value item`, punya penyelamat berupa angka
> (`amount_limit: 0`); pesan tidak punya padanannya.
>
> **Yang menanggung risikonya adalah penerima**, yang tidak pernah menyetujui
> apa pun (**C-19**). Karena penilai dan penanggung risiko bukan pihak yang
> sama, bawaannya diambil ke sisi yang lebih aman sampai ada definisi yang bisa
> diuji mesin.
>
> ⚠️ **Untuk V0 aturan ini tidak mengubah apa pun** — V0 tidak punya satu pun
> tool level 3 atau 4. Ia berlaku begitu Phase 11 mulai dikodekan.
> Cara membalikkannya ada di
> [`../docs/KEPUTUSAN-DIDELEGASIKAN.md`](../docs/KEPUTUSAN-DIDELEGASIKAN.md) K-1.

> 🔧 **Aturan 8 dan 9 (K-12).** **G-11** mencatat 13 tool persepsi §10.26 tanpa
> satu pun `risk_level`, dan §15.24 mengulanginya untuk lima panggilan SDK
> spasial yang mengembalikan **denah rumah** dan **posisi pengguna**. Medan
> `risk_level` memang sudah ada di skema — tetapi **medan yang ada di skema
> bukan medan yang ditegakkan**.
>
> Bawaan `risk_level: 0` sengaja **tidak** dipakai: bawaan nol berarti tool yang
> lupa diberi tingkat risiko otomatis menjadi **yang paling tidak dijaga**.
>
> Aturan 9 memperluas larangan scope aturan 6 ke data spasial, sesuai usul yang
> sudah dicatat di [`../docs/226`](../docs/226-SDK-REPO-API-DATA-EVENT-DEPLOYMENT.md).

---

## 🔧 Kapan sesuatu adalah agent, dan kapan ia service (K-5)

> Ditambahkan 9 September 2026 — **keputusan didelegasikan K-5**, menutup
> **G-13** / [#89](../../issues/89).

Sebuah komponen masuk registry agent **hanya bila ketiganya benar**:

| # | Uji | Kalau tidak |
|---|---|---|
| a | merencanakan **lebih dari satu langkah** | urutan tetap ⇒ service |
| b | **memilih** di antara beberapa tool saat berjalan | pemanggilan tetap ⇒ service |
| c | bisa **dihentikan di tengah** dan meninggalkan jejak yang bisa dilanjutkan (`agent_runs`) | sekali jalan ⇒ service |

⭐ **Ketiganya juga persis yang membuat risk gate bermakna**: sesuatu yang tidak
memilih tool tidak butuh gerbang tool. Uji (b) sendirian meloloskan pipeline
bercabang; uji (c) sendirian meloloskan job antrean biasa.

Dasarnya kata pemilik sendiri, §12.29: *“jangan membuat semuanya sebagai
autonomous agent sejak awal — sebagian lebih baik sebagai deterministic/model
services.”* Itu satu-satunya peringatan semacam itu dalam 24 naskah, dan
sensus menemukan **44 dari 59 nama agent hanya pernah disebut sekali**
([`../docs/SENSUS-AGENT.md`](../docs/SENSUS-AGENT.md)).

⚠️ Keempat agent V0 lulus ketiga uji. Kriteria ini **tidak** mengubah V0.

---

## Tool registry

```yaml
# tools/<name>.yaml
name:        habit.streak
version:     1.0.0
kind:        read                  # read | write | external
description: Hitung rentetan dan tingkat penyelesaian sebuah habit
scopes:      [ habits ]            # scope memory/data yang disentuh
risk_level:  0
input:
  habit_id:  { type: uuid, required: true }
  window:    { type: integer, default: 30 }
output:
  current:            integer
  longest:            integer
  completion_rate:    number
side_effects: none                 # none | writes_user_data | external_call
reaches_third_party: false         # 🔧 K-1: true bila akibatnya sampai ke orang
                                   #     selain pemegang akun. true ⇒ risk_level >= 3
rate_limit:   60/min/user
```

> 🔧 **`reaches_third_party` (K-1).** Medan ini yang ditegakkan aturan 7. Ia
> sengaja **bukan** turunan dari `side_effects`: `external_call` bisa berarti
> memanggil API cuaca (tak menyentuh siapa pun) **atau** mengirim pesan kepada
> orang lain — dua hal yang risikonya berbeda jauh, dan satu medan tidak bisa
> memisahkannya. Seluruh tool V0 bernilai `false`.

Tool V0:

| Tool | Kind | Risk | Dipakai |
|---|---|---|---|
| `habit.list` | read | 0 | Coach, Habit |
| `habit.streak` | read | 0 | Coach, Habit |
| `habit.complete` | write | 2 | Habit |
| `goal.list` | read | 0 | Coach |
| `checkin.get` | read | 0 | Coach |
| `mood.recent` | read | 0 | Coach |
| `memory.search` | read | 0 | Coach, Memory |
| `memory.write` | write | 2 | Memory |
| `recommendation.create` | write | 1 | Coach |

> **`weather.get` dan `calendar.get` tidak ada di V0** — keduanya tool
> (butir **H-11**), tapi Fashion dan Context baru masuk V2. Ditulis di
> registry V2.

---

## Empat agent V0

| Agent | Risk | Tools | Memory read | Memory write |
|---|---|---|---|---|
| `orchestrator-agent` | 0 | — (hanya memanggil agent lain) | — | — |
| `coach-agent` | 1 | habit.list, habit.streak, goal.list, checkin.get, mood.recent, memory.search, recommendation.create | habits, goals, checkins, mood, coaching_notes | coaching_notes |
| `habit-agent` | 2 | habit.list, habit.streak, habit.complete | habits | — |
| `memory-agent` | 2 | memory.search, memory.write | semua scope **kecuali** `journal_raw` | memories |

> **`memory-agent` boleh membaca hampir semua scope tetapi tidak `journal_raw`.**
> Ia mengekstrak memori **dari** jurnal lewat pipeline tertutup, bukan dengan
> membaca sesuka hati. Itu penerapan naskah 5 §15: *private journal* ada di
> daftar DENY bahkan untuk agent yang bekerja di atasnya.

---

## Risk gate

Alur wajib sebelum aksi dijalankan:

```
capability diminta
      ↓
risk_level agent & tool  → ambil yang TERTINGGI
      ↓
capability ada di requires_confirmation?  → ya → minta izin
      ↓
permissions(user, agent, scope, action) → 'deny' → tolak & catat
                                        → 'ask'  → minta izin
                                        → 'allow'→ lanjut
      ↓
jalankan · catat agent_runs · catat audit_logs
```

**Default V0** 🔧 — menjawab issue #5 dengan pilihan paling aman:

| Risk | Default V0 |
|---|---|
| 0 · informasi | `allow` |
| 1 · rekomendasi | `allow` |
| 2 · aksi reversibel | **`ask`** sekali per jenis aksi, lalu boleh diingat |
| 3 · aksi berdampak | **`ask` setiap kali** |
| 4 · high-impact | **tidak ada di V0** — tidak ada tool yang bisa mencapainya |

> V0 tidak punya satu pun tool level 3 atau 4. Itu disengaja: janji *"Act
> selalu di bawah kontrol pengguna"* paling mudah ditepati dengan tidak
> memberi agent kemampuan yang belum perlu.
