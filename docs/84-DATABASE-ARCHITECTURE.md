# 84 — §5–§6 Database Architecture & Core Data Model

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §5 — Polyglot persistence, tetapi bertahap

> **Jangan memakai satu database untuk semuanya.**

### Primary — PostgreSQL

```
users              profiles           goals
habits             activities         journal_entries
wardrobe_items     outfits            sleep_records
workouts           skills             projects
notifications      permissions        agent_runs
```

### Vector — Qdrant

```
episodic_memory        semantic_memory
journal_embeddings     preference_embeddings
fashion_embeddings     knowledge_embeddings
```

### Graph — Neo4j

```
User            User
  ↓               ↓
Goal            Style
  ↓               ↓
Habit           Clothing
  ↓               ↓
Behavior        Brand
  ↓               ↓
Outcome         Trend
                  ↓
                Outfit
```

### Cache — Redis

```
sessions · rate limits · temporary context
agent state · queues · cache
```

> ⭐ **Empat penyimpanan, bukan enam.** **Kafka dan ClickHouse hilang** dari
> naskah kelima; antrean pindah ke Redis. Ini menjawab butir **A-10** ke arah
> yang paling sederhana. Lihat butir **E-36**.

---

## §6 — Core data model

> User bukan sekadar:

```
User
 ├── name
 ├── email
 └── password
```

HumanVerse menggunakan:

```
User
│
├── Identity
├── Profile
├── Preferences
├── Goals
├── Behaviors
├── State
├── Memories
├── Skills
├── Relationships
├── Lifestyle
├── Health
├── Career
└── Decisions
```
