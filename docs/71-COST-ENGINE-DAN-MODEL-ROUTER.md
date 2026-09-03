# 71 — §48–§49 AI Cost Engine & Model Router

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §48 — AI Cost Engine

> Ini **sering dilupakan**.

Kalau 50 agent berjalan setiap hari:

```
LLM Cost
Embedding Cost
Storage
Compute
Search
Observability
```

> Bisa **sangat mahal**.

Maka kita buat **Model Router**:

| Jenis tugas | Model |
|---|---|
| Simple task | Small model |
| Reasoning task | Large model |
| Vision | Vision model |
| Embedding | Embedding model |

> **Jangan menggunakan model paling mahal untuk semua hal.**

---

## §49 — Model Router

```
                  Request
                     │
                     ▼
               Complexity
               Classifier
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
       Small       Medium      Large
       Model       Model       Model
```

Optimasi terhadap:

```
Quality · Latency · Cost · Privacy
```
