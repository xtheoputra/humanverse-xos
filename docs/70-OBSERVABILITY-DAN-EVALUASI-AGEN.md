# 70 — §46–§47 Agent Observability & Agent Evaluation

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §46 — Agent Observability

Dashboard **Agent Health**:

```
FashionAgent
├── Requests
├── Latency
├── Errors
├── Tool failures
├── User feedback
└── Recommendation acceptance

HealthAgent
...
```

> Kita memperlakukan **Agent seperti microservice production**.

---

## §47 — Agent Evaluation

> Setiap agent memiliki benchmark.

**FashionAgent Evaluation**

```
Accuracy · Relevance · Personalization · Consistency
Safety · Latency · Cost · User Satisfaction
```

Kemudian:

```
Agent Version 1.2
       ↓
Evaluation
       ↓
Score
       ↓
Production
```

> Kalau versi baru lebih buruk: **Automatic Rollback**.
