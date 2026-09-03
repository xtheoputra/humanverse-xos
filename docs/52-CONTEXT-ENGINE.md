# 52 — §2–§3 Human Context Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §2 — Kenapa konteks, bukan sekadar preferensi

> Ini sangat penting.
>
> AI tidak boleh hanya mengetahui: *"User suka fashion."*
> **AI harus mengetahui konteks saat ini.**

Contoh:

```
Current Context

Time       : 07:30
Weather    : Hot
Location   : Jakarta
Calendar   : Office meeting
Mood       : Low
Energy     : Medium
Sleep      : 5h 40m
Goal       : Improve appearance
Style      : Minimalist
Budget     : Moderate
```

Kemudian:

> Fashion Agent **tidak** memberikan rekomendasi generik.
> Ia memberikan rekomendasi **berdasarkan konteks**.

---

## §3 — Context Engine Architecture

```
                     Context Engine
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
    Temporal          Environmental       Personal
         │                 │                 │
       Time              Weather          Profile
       Day               Location         Preference
       Event             Season           Goals
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                     Context Vector
                           │
                           ▼
                       AI Agents
```

---

## Tiga lapis konteks

Context berubah terus-menerus. Karena itu dibutuhkan:

```
Real-Time Context
       +
Historical Context
       +
Predicted Context
```
