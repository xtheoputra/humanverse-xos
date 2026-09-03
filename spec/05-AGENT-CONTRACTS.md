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

> Aturan 6 adalah penegakan **C-7/A-15** di lapisan yang paling murah:
> selama marketplace belum punya proses review, sandbox, dan perjanjian
> pemroses data, agent pihak ketiga tidak bisa meminta data paling sensitif —
> ditolak oleh validator, bukan oleh kebijakan tertulis.

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
rate_limit:   60/min/user
```

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
