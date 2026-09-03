# 12 — AI Multi-Agent Hierarchy

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Tiga lapis

```
┌──────────────────────────────────────────────────────────┐
│ LAYER 1   Supreme Orchestrator            — otak utama   │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│ LAYER 2   Core Intelligence Agents                       │
│           Planner · Memory · Reasoning · Guardrail       │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│ LAYER 3   Specialist Agents                              │
│  Health · Habit · Fashion · Trend · Career · Finance     │
│  Learning · Social                                       │
└──────────────────────────────────────────────────────────┘
```

---

# Layer 1 — Supreme Orchestrator

Ini adalah **otak utama**.

**Tugasnya:**

- menerima permintaan pengguna
- menentukan agent yang dipanggil
- menggabungkan hasil
- mengingat konteks
- menjaga konsistensi jawaban

### Contoh

> "Besok meeting penting."

Orchestrator akan memanggil:

- Calendar Agent
- Fashion Agent
- Sleep Agent
- Weather Agent

Lalu menyusun **satu jawaban**.

---

# Layer 2 — Core Intelligence Agents

| Agent | Tugas |
|---|---|
| **Planner Agent** | Memecah goal besar menjadi langkah-langkah kecil |
| **Memory Agent** | Mengelola Short-Term, Long-Term, dan Episodic Memory |
| **Reasoning Agent** | Melakukan analisis, evaluasi, dan penalaran multi-step |
| **Guardrail Agent** | Memastikan privasi, keamanan, dan etika rekomendasi |

---

# Layer 3 — Specialist Agents

> **Inilah kekuatan HumanVerse.**

---

## Health Agent

**Kemampuan:**

- Sleep Analysis
- Recovery Score
- Energy Prediction
- Workout Suggestion
- Water Reminder
- Stress Trend

| Input | Output |
|---|---|
| wearable | Health Score |
| sleep | Recovery Plan |
| steps | |
| heart rate | |

---

## Habit Agent

**Kemampuan:**

- Habit Prediction
- Streak Recovery
- Atomic Habit Builder
- Failure Analysis

AI belajar **pola keberhasilan**.

---

## Fashion Agent

Ini **jauh lebih kompleks** — ia sendiri punya sub-agent.

**Sub Agent:**

- Outfit Agent
- Color Agent
- Trend Agent
- Grooming Agent

| Input | Output |
|---|---|
| foto pakaian | |
| tinggi badan | |
| bentuk tubuh | **Outfit terbaik hari ini** |
| cuaca | |
| acara | |

---

## Trend Intelligence Agent

Agent ini **terus memantau** kategori seperti:

| | |
|---|---|
| fashion | teknologi |
| sneakers | musik |
| skincare | film |
| cafe | |

Lalu membuat **personal trend**.

---

## Career Agent

**Fitur:**

- Resume Review
- LinkedIn Optimization
- Interview Simulation
- Skill Gap

---

## Finance Behavior Agent

**Bukan trading.** Fokusnya **perilaku**. Misalnya:

- impulsive spending
- payday effect
- saving consistency

---

## Learning Agent

**AI membangun:**

- roadmap
- review
- quiz
- spaced repetition

---

## Social Agent

Membantu **menjaga hubungan**.

### Contoh

> "Sudah lama belum menghubungi ibu."

AI mengingatkan.
