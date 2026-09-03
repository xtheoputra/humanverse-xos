# 72 — §50–§51 HumanVerse Cloud & Kubernetes Architecture

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §50 — HumanVerse Cloud

Pada akhirnya infrastrukturnya:

```
                     Internet
                        │
                   CDN / WAF
                        │
                   API Gateway
                        │
                   Service Mesh
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
    Core Services    AI Runtime    Data Platform
         │              │              │
         ▼              ▼              ▼
    PostgreSQL      Agent Runtime   Data Lake
    Redis           Model Router    ClickHouse
    Object Storage  MCP             Vector DB
                    Evaluation      Graph DB
```

---

## §51 — Kubernetes Architecture

Nanti:

```
Kubernetes Cluster

namespace:
├── humanverse-core
├── ai-runtime
├── agents
├── data
├── observability
└── security
```

> ⚠️ **Tetapi untuk V0 jangan langsung Kubernetes.**

Mulai:

```
Docker Compose
      ↓
   Cloud VM
      ↓
  Kubernetes
```

> ⭐ Ini pelunakan paling nyata terhadap risiko **B-7** (beban operasional) di
> berkas audit.
