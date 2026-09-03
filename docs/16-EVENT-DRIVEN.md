# 16 — Event Driven System

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Semua aktivitas menjadi event.**

---

## Contoh event

```
WakeUp
WorkoutCompleted
MoodLogged
OutfitChosen
CoffeePurchased
MeetingFinished
SleepStarted
```

---

## Jalur pengiriman

Event dikirim ke:

- **Kafka**
- **Redis Streams**

> **Semua agent bisa mendengarkan.**

---

## Bentuk kasar

```
   Aktivitas pengguna
           │
           ▼
    ┌─────────────┐
    │   Event     │
    └──────┬──────┘
           │
   ┌───────┴────────┐
   ▼                ▼
 Kafka        Redis Streams
   │                │
   └───────┬────────┘
           ▼
   semua agent mendengarkan
```
