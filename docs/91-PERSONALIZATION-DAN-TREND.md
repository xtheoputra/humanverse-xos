# 91 — §20–§21 Personalization Engine & Trend Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20 — Personalization flywheel

```
                    GLOBAL WORLD
                         │
                 ┌───────▼────────┐
                 │ Trend Engine   │
                 └───────┬────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Personalization     │
              │ Engine              │
              └──────────┬──────────┘
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
     Profile          Behavior          Context
        │                │                 │
        └────────────────┼─────────────────┘
                         │
                         ▼
                  Recommendation
                         │
                         ▼
                       USER
                         │
                         ▼
                     FEEDBACK
                         │
                         ▼
                  MODEL UPDATE
```

---

## §21 — Trend Intelligence

> Jangan membuat: `FashionAgent → Google/search → answer`

Tapi:

```
Sources
   ↓
Ingestion
   ↓
Normalization
   ↓
Entity Extraction
   ↓
Trend Detection
   ↓
Trend Scoring
   ↓
Audience Analysis
   ↓
Personal Relevance
```

Trend object:

```json
{
  "trend": "oversized minimal streetwear",
  "category": "fashion",
  "global_score": 0.84,
  "regional_score": 0.72,
  "youth_score": 0.91,
  "personal_relevance": 0.88
}
```

Karena:

> ## Popular ≠ suitable for the user.

Itu prinsip penting HumanVerse.

> ⚠️ **Sumbernya masih hanya disebut "Sources".** Tiga naskah berturut-turut
> membahas Trend Engine tanpa menyebut satu sumber data pun. Lihat butir
> **A-5**.
