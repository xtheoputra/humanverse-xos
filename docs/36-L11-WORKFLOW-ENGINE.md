# 36 — Layer 11: Workflow Engine

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).
>
> Versi naskah 2 ada di [`17-AI-WORKFLOW.md`](17-AI-WORKFLOW.md).

---

Gunakan **LangGraph**.

---

## Contoh workflow

User berkata:

> "Besok meeting."

Workflow:

```
  Planner
     │
     ▼
  Calendar
     │
     ▼
  Weather
     │
     ▼
  Fashion
     │
     ▼
  Health
     │
     ▼
  Reminder
```

> **Semua otomatis.**
