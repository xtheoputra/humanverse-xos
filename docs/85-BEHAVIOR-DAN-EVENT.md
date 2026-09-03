# 85 — §7–§8 Behavior Model & Event Architecture

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7 — Setiap aktivitas menjadi event

```json
{
  "event_type": "workout.completed",
  "user_id": "u_123",
  "timestamp": "2026-09-03T06:30:00Z",
  "payload": {
    "duration": 45,
    "exercise_type": "strength"
  }
}
```

### Daftar event

```
sleep.started          sleep.completed
habit.created          habit.completed        habit.skipped
mood.logged
journal.created
workout.started        workout.completed
meal.logged
outfit.selected        outfit.worn
purchase.created
goal.created           goal.completed
learning.started       learning.completed
meeting.started        meeting.completed
travel.started         travel.completed
```

Dengan ini HumanVerse tidak hanya mengetahui:

> *"User punya habit gym."*

Tetapi:

> *"User biasanya workout Senin, Rabu, Jumat pukul 18:00–20:00 dan
> probabilitas menyelesaikan workout turun ketika tidur <6 jam."*

> Itulah perbedaan **habit tracker biasa** vs **behavior intelligence
> platform**.

> ⭐ Naskah 4 hanya punya satu contoh event. Di sini ada **21 event**, dengan
> bentuk payload yang tetap. Yang **masih belum ada**: versi skema, urutan,
> idempotensi, dan consumer mana yang wajib. Lihat bagian **D**.

---

## §8 — Event architecture

```
                    USER
                     │
                     ▼
              ┌─────────────┐
              │ Application │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ Event Bus   │
              └──────┬──────┘
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   Behavior       Analytics     AI Engine
   Engine         Engine        Engine
        │            │             │
        ▼            ▼             ▼
  User Model     Dashboard    Recommendation
```

> Ini menjadi fondasi **real-time intelligence**.
