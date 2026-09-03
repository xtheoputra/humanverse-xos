# 54 — §5–§7 Behavior Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §5 — Behavior Engine

> Ini salah satu **IP terpenting** HumanVerse.
>
> AI tidak hanya melihat apa yang **dikatakan** user.
> AI melihat: **apa yang benar-benar dilakukan user.**

Contoh:

```
Goal:   Workout 4x/week

Actual:
Mon  ✓
Tue  ✓
Wed  ✗
Thu  ✗
Fri  ✓
Sat  ✗
Sun  ✓
```

AI menemukan pola:

```
Workout failure probability ↑ after poor sleep
```

Maka:

```
Poor Sleep
    ↓
Low Energy
    ↓
Workout Skip
```

> Inilah **Behavior Intelligence**.

---

## §6 — Behavioral Pattern Mining

| Jenis pola | Contoh dari pemilik |
|---|---|
| **Temporal Pattern** | habit failure → Friday night |
| **Environmental Pattern** | habit success → gym near office |
| **Emotional Pattern** | stress ↑ → spending ↑ |
| **Social Pattern** | social event → sleep delay |
| **Behavioral Pattern** | late sleep → late wake → missed workout |

---

## §7 — Behavior Causality Engine

> Kita harus **berhati-hati dengan istilah "penyebab"**.
>
> Jangan mengatakan: *"Tidur menyebabkan produktivitas turun."*
>
> Kalau data hanya observasional, lebih tepat: *"Dalam datamu, tidur lebih
> pendek berasosiasi dengan produktivitas yang lebih rendah."*

Jadi engine memiliki:

```
Correlation
Association
Temporal Relationship
Causal Hypothesis
```

> **Bukan langsung menganggap semuanya causal.**
> Ini akan membuat platform jauh lebih ilmiah.

> ⭐ Bagian ini mengubah cara rantai `Tidur → Mood → Produktivitas → Olahraga`
> dari naskah pertama harus dibaca. Lihat butir **E-16** di berkas audit.
