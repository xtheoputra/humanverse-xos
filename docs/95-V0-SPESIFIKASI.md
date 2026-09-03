# 95 — §29–§32 Spesifikasi V0

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §29 — V0 yang benar-benar kita bangun

> Walaupun arsitektur besarnya seperti di atas, V0 cukup:

```
HumanVerse X V0
│
├── Authentication
├── User Profile
├── Goals
├── Habits
├── Daily Check-in
├── Mood
├── Journal
├── Activity Tracking
├── AI Coach
├── Basic Memory
├── Recommendation
└── Dashboard
```

Agent:

```
OrchestratorAgent
HabitAgent
CoachAgent
MemoryAgent
```

> **Itu saja.** Jangan FashionAgent + CareerAgent + 30 agent sekaligus di V0.

> ⚠️ **Daftar V0 bertambah dua** dibanding naskah 4: **Activity Tracking** dan
> **Recommendation** — sementara target waktunya tetap **4–6 minggu**. Lihat
> butir **E-40** dan issue A-17.

---

## §30 — V0 architecture

```
                     MOBILE / WEB
                           │
                           ▼
                     API GATEWAY
                           │
             ┌─────────────┼──────────────┐
             │             │              │
             ▼             ▼              ▼
          Profile        Goals          Habits
             │             │              │
             └─────────────┼──────────────┘
                           ▼
                     Event System
                           │
                           ▼
                    Behavior Engine
                           │
                           ▼
                     Memory System
                           │
                           ▼
                   AI Orchestrator
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         CoachAgent    HabitAgent   MemoryAgent
                           │
                           ▼
                         User
```

---

## §31 — V0 database

> Minimal tetapi **future-proof**.

```
users                      profiles
goals                      goal_milestones
habits                     habit_completions
daily_checkins             mood_entries
journal_entries            activities
memories
ai_conversations           ai_messages
recommendations            recommendation_feedback
agent_runs
permissions                consents
audit_logs
```

> **Belum perlu 100 tabel.**

> ⭐ 19 tabel. Perhatikan `permissions`, `consents`, dan `audit_logs` **sudah
> ada sejak V0** — privasi tidak ditunda ke fase belakang.

---

## §32 — V0 development sequence

| Sprint | Nama | Isi |
|---|---|---|
| **0** | Foundation | Repository · Docker · PostgreSQL · Redis · CI/CD · Environment config · Logging · Testing |
| **1** | Identity | Auth · User · Profile · Session · Permission |
| **2** | Human Core | Goals · Milestones · Habits · Habit completion · Daily check-in · Mood |
| **3** | Memory | Journal · Memory extraction · Semantic memory · Episodic memory · Memory retrieval |
| **4** | AI | AI Gateway · Model Router · Orchestrator · CoachAgent · HabitAgent |
| **5** | Intelligence | Behavior events · Pattern detection · Recommendations · Personalization |
| **6** | Product | Dashboard · Weekly review · Notifications · UX refinement |

> ⚠️ **Tujuh sprint dalam 4–6 minggu** berarti kira-kira **4–6 hari per
> sprint**, termasuk Sprint 0 (repo, Docker, CI/CD) dan Sprint 4 (AI Gateway +
> Model Router + 3 agent). Ini perlu dicek ulang terhadap waktu nyata yang
> tersedia — lihat butir **A-17**.
>
> ⚠️ **MemoryAgent tidak muncul di Sprint mana pun**, padahal ia salah satu
> dari 4 agent V0. Sprint 3 membangun *sistem* memory, bukan agent-nya.
