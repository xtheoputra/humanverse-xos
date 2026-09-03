# 33 — Layer 8: Human Knowledge Graph Engine

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).
>
> Skema graf versi naskah 2 ada di
> [`13-KNOWLEDGE-GRAPH.md`](13-KNOWLEDGE-GRAPH.md).

---

> **Ini bukan sekadar database.**

Gunakan **Neo4j**.

---

## Contoh Graph

```
   User
    │
    ▼
   Sleep
    │
    ▼
   Energy
    │
    ▼
   Workout
    │
    ▼
   Mood
    │
    ▼
   Productivity
    │
    ▼
   Career
```

---

## AI bisa menemukan pola

Contoh query:

> "Habit apa yang paling mempengaruhi produktivitasku?"

**Graph akan menjawab berdasarkan data.**
