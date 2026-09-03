# 88 — §12–§16 Arsitektur Agent

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12 — Agent architecture

> **Kita jangan membuat 100 agent sejak awal.**

### Initial production agents (12)

```
 1. OrchestratorAgent      7. RecommendationAgent
 2. PlannerAgent           8. ContextAgent
 3. MemoryAgent            9. GoalAgent
 4. CoachAgent            10. EvaluationAgent
 5. HabitAgent            11. SafetyAgent
 6. BehaviorAgent         12. PersonalizationAgent
```

### Domain agents (10)

```
13. FashionAgent          18. LearningAgent
14. WardrobeAgent         19. CareerAgent
15. TrendAgent            20. FinanceBehaviorAgent
16. FitnessAgent          21. SocialAgent
17. NutritionAgent        22. TravelAgent
```

> ⚠️ **Daftar agent berubah untuk kesekian kalinya.** Dibanding registry 14
> agent di naskah 4: **HealthAgent, GroomingAgent, ProductivityAgent,
> EntertainmentAgent, dan ResearchAgent hilang**; **WardrobeAgent dan
> TrendAgent muncul**; dan 12 agent inti/sistem masuk daftar untuk pertama
> kalinya. Lihat butir **E-35**.

---

## §13 — Orchestrator

> Ini adalah **otak koordinasi**, bukan agent yang melakukan semuanya.

Contoh permintaan: *"Besok saya ada meeting penting, bantu saya persiapkan."*

```
Understand request
       ↓
Identify required capabilities
       ↓
ContextAgent
       ↓
Calendar Tool
       ↓
FashionAgent
       ↓
PreparationAgent
       ↓
RecommendationAgent
       ↓
Response
```

```
Orchestrator
     │
     ├── ContextAgent
     ├── Calendar
     ├── FashionAgent
     ├── CareerAgent
     └── RecommendationAgent
```

> ⭐ **Calendar disebut Tool di sini** — menutup butir **E-2/E-28**: Calendar
> dan Weather adalah **tool**, bukan agent.
>
> ⚠️ **`PreparationAgent` tidak ada di daftar 22 agent** §12. Naskah kelima
> bertabrakan dengan dirinya sendiri. Lihat butir **E-38**.

---

## §14 — Agent Manifest

> Setiap agent memiliki **kontrak**.

```yaml
name: fashion-agent
version: 1.0.0

purpose:
  - recommend outfits
  - analyze wardrobe
  - analyze fashion trends

capabilities:
  - outfit_recommendation
  - wardrobe_analysis
  - trend_analysis

tools:
  - wardrobe.search
  - weather.get
  - calendar.get
  - trend.search

memory:
  read:
    - fashion_preferences
    - wardrobe
    - outfit_history

  write:
    - outfit_feedback
    - fashion_preferences

risk_level: 1

requires_confirmation:
  - purchase_clothing
```

> Sangat penting ketika nanti agent sudah puluhan/ratusan.

> ⭐ Dua tambahan dibanding manifest naskah 4: `risk_level` kini **angka**
> (bukan kata `low`), dan ada **`requires_confirmation`** — daftar aksi yang
> selalu butuh persetujuan manusia, apa pun risk level-nya.

---

## §15 — Agent Permission System

> **Jangan memberikan semua memory kepada semua agent.**

| Agent | READ | DENY |
|---|---|---|
| **FashionAgent** | wardrobe · fashion preferences · weather · calendar | private journal · financial records · medical records |
| **FinanceAgent** | financial behavior · goals | private journal · wardrobe · social messages |
| **CoachAgent** | context lebih luas — tetapi tetap melalui **permission policy** | — |

---

## §16 — Risk Engine

| Level | Jenis | Contoh naskah 5 |
|---|---|---|
| **0** | Information | *"Cuaca besok hujan."* |
| **1** | Recommendation | *"Pakai jaket."* |
| **2** | Low-impact action | *"Buat reminder gym."* |
| **3** | Meaningful external action | *"Kirim pesan kepada seseorang."* |
| **4** | High-impact action | *"Melakukan transaksi finansial."* |

Level tinggi:

```
AI
 ↓
Explain
 ↓
Ask confirmation
 ↓
Human approves
 ↓
Execute
```

> ⚠️ Contoh untuk Level 3 dan 4 **berubah** dari naskah 4 (dulu L3 *"Booking
> hotel"*, L4 *"keputusan medis, keuangan besar, hukum"*). Tangganya sama,
> isinya bergeser — dan **default untuk V0 masih belum ditetapkan**.
