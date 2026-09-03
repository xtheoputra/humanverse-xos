# 56 — §10–§12 Agent Factory, Manifest & Registry

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10 — Agent Factory

> Ini bagian besar. **Kita membuat sistem untuk membuat agent.**

```
Agent Specification
        ↓
Capability Generator
        ↓
Tool Assignment
        ↓
Prompt Generator
        ↓
Memory Policy
        ↓
Evaluation Suite
        ↓
Security Policy
        ↓
Deployment
```

Misalnya kita ingin **Travel Agent**. Factory membuat:

```
TravelAgent
├── planner
├── destination-research
├── budget
├── itinerary
├── weather
├── booking-tools
└── evaluator
```

---

## §11 — Agent Manifest

> **Setiap agent wajib memiliki manifest.**

```yaml
name: FashionAgent
version: 1.0.0

purpose:
  - outfit recommendation
  - wardrobe analysis
  - trend discovery

capabilities:
  - analyze_outfit
  - recommend_outfit
  - analyze_wardrobe

tools:
  - wardrobe
  - weather
  - calendar
  - trend_engine

memory:
  read:
    - fashion_preferences
    - wardrobe
  write:
    - outfit_feedback

risk_level:
  low
```

> Ini membuat agent bisa dikelola **seperti software package**.

> ⭐ Naskah ketiga menjanjikan "setiap tool memiliki manifest" tanpa pernah
> menunjukkan satu pun. Ini contoh manifest pertama di seluruh proyek.

---

## §12 — Agent Registry

```
Agent Registry
│
├── HealthAgent
├── HabitAgent
├── FashionAgent
├── GroomingAgent
├── FitnessAgent
├── NutritionAgent
├── LearningAgent
├── CareerAgent
├── FinanceAgent
├── SocialAgent
├── TravelAgent
├── ProductivityAgent
├── EntertainmentAgent
└── ResearchAgent
```

Nantinya bisa menjadi: **Agent Marketplace**.

> ⚠️ Registry ini berisi **14 agent**. Naskah kedua hanya memberi agen kepada
> 8 modul. Lihat butir **A-8** dan **E-24** di berkas audit — *Grooming*,
> *Nutrition*, dan *Productivity* kembali muncul, sementara **Mental Wellness**
> dan **Lifestyle** tetap tidak punya agent.
