# 11 — Complete Repository Architecture

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pohon monorepo

```
HumanVerse-X/
│
├── apps/
│   ├── mobile/
│   ├── web/
│   ├── desktop/
│   └── admin-dashboard/
│
├── backend/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── user-service/
│   ├── behavior-service/
│   ├── recommendation-service/
│   ├── notification-service/
│   ├── analytics-service/
│   ├── fashion-service/
│   ├── health-service/
│   ├── career-service/
│   ├── social-service/
│   └── finance-service/
│
├── ai/
│   ├── orchestrator/
│   ├── planner-agent/
│   ├── memory-agent/
│   ├── reasoning-agent/
│   ├── retrieval-agent/
│   ├── evaluator-agent/
│   ├── guardrail-agent/
│   └── specialist-agents/
│
├── knowledge/
│   ├── human-graph/
│   ├── embeddings/
│   ├── ontology/
│   └── datasets/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── terraform/
│   ├── monitoring/
│   └── security/
│
├── prompts/
├── sdk/
├── tests/
└── docs/
```

---

## Alasan bentuk ini

> Monorepo ini memisahkan **aplikasi, microservices, AI agents, knowledge
> system, dan infrastruktur**, sehingga **puluhan agen dapat dikembangkan
> secara paralel**.

---

## Ringkasan isi tiap wilayah

| Wilayah | Jumlah | Isi |
|---|---|---|
| `apps/` | 4 | mobile, web, desktop, admin-dashboard |
| `backend/` | 12 | 7 layanan fondasi + 5 layanan domain |
| `ai/` | 8 | orchestrator + 6 agen inti + wadah agen spesialis |
| `knowledge/` | 4 | human-graph, embeddings, ontology, datasets |
| `infrastructure/` | 5 | docker, kubernetes, terraform, monitoring, security |
| akar | 4 | `prompts/`, `sdk/`, `tests/`, `docs/` |

**Layanan fondasi:** api-gateway, auth, user, behavior, recommendation,
notification, analytics.
**Layanan domain:** fashion, health, career, social, finance.
