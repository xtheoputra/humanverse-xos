# 81 — §2 System Context

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

```
                       ┌─────────────────────┐
                       │      HUMAN USER     │
                       └──────────┬──────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     HUMANVERSE APPS       │
                    │                           │
                    │ Mobile │ Web │ Desktop    │
                    │ Voice  │ Vision │ Wearable│
                    └─────────────┬─────────────┘
                                  │
                         ┌────────▼────────┐
                         │   API GATEWAY   │
                         └────────┬────────┘
                                  │
        ┌─────────────────────────┼──────────────────────────┐
        │                         │                          │
┌───────▼────────┐       ┌────────▼────────┐       ┌─────────▼───────┐
│ HUMAN DOMAIN   │       │ INTELLIGENCE    │       │ AGENT PLATFORM  │
│                │       │                 │       │                 │
│ Profile        │       │ Context Engine  │       │ Agent Registry  │
│ Goals          │       │ Behavior Engine │       │ Tool Registry   │
│ Habits         │       │ Recommendation  │       │ Agent Runtime   │
│ Health         │       │ Prediction      │       │ MCP             │
│ Fashion        │       │ Simulation      │       │ Permissions     │
│ Career         │       │ Memory          │       │ Marketplace     │
│ Learning       │       │ Personal Model  │       │ Evaluation      │
│ Finance        │       │                 │       │                 │
│ Social         │       │                 │       │                 │
└───────┬────────┘       └────────┬────────┘       └─────────┬───────┘
        │                         │                          │
        └─────────────────────────┼──────────────────────────┘
                                  │
                         ┌────────▼────────┐
                         │   EVENT BUS     │
                         └────────┬────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
       ┌──────▼─────┐      ┌──────▼──────┐     ┌──────▼─────┐
       │ PostgreSQL │      │ Vector DB   │     │ Graph DB   │
       │            │      │             │     │            │
       │ Core Data  │      │ Memories    │     │ Human KG   │
       └────────────┘      └─────────────┘     └────────────┘
```
