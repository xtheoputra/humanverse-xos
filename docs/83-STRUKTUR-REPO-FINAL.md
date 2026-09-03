# 83 — §4 Repository Structure (final)

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> Saya akan membuatnya sebagai **monorepo**.

```
humanverse-x/
│
├── apps/
│   ├── mobile/
│   ├── web/
│   ├── desktop/
│   ├── admin/
│   └── api/
│
├── services/
│   ├── identity/
│   ├── profile/
│   ├── behavior/
│   ├── goals/
│   ├── habits/
│   ├── journal/
│   │
│   ├── health/
│   ├── fitness/
│   ├── nutrition/
│   ├── fashion/
│   ├── wardrobe/
│   ├── grooming/
│   ├── lifestyle/
│   │
│   ├── career/
│   ├── learning/
│   ├── finance/
│   ├── social/
│   └── travel/
│
├── intelligence/
│   ├── orchestrator/
│   ├── planner/
│   ├── reasoning/
│   ├── memory/
│   ├── context/
│   ├── behavior-model/
│   ├── preference-model/
│   ├── recommendation/
│   ├── prediction/
│   ├── simulation/
│   ├── personalization/
│   └── model-router/
│
├── agents/
│   ├── runtime/
│   ├── registry/
│   ├── factory/
│   ├── evaluator/
│   ├── permissions/
│   ├── policies/
│   └── marketplace/
│
├── platform/
│   ├── events/
│   ├── notifications/
│   ├── search/
│   ├── analytics/
│   ├── observability/
│   ├── security/
│   └── audit/
│
├── data/
│   ├── migrations/
│   ├── seeds/
│   ├── pipelines/
│   ├── datasets/
│   ├── feature-store/
│   └── knowledge/
│
├── packages/
│   ├── domain/
│   ├── contracts/
│   ├── events/
│   ├── sdk/
│   ├── ai/
│   └── common/
│
├── prompts/
│   ├── system/
│   ├── agents/
│   ├── evaluators/
│   └── versions/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── ai/
│   ├── security/
│   └── performance/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── terraform/
│   └── monitoring/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── agents/
│   ├── domain/
│   ├── security/
│   └── decisions/
│
├── AGENTS.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md
```

---

> ⭐ **Ini menutup butir E-27.** Dua struktur yang sebelumnya bertabrakan —
> monorepo naskah 2 (`apps/ services/ agents/`) dan struktur dokumen naskah 4
> §52 (`/docs /architecture /contracts /prompts /adr /tests`) — **digabung**:
> monorepo tetap, dan berkas wajib untuk AI coding agent (`AGENTS.md`,
> `ARCHITECTURE.md`, `CONTRIBUTING.md`) ikut masuk. `adr/` menjadi
> `docs/decisions/`.
>
> ⚠️ Nama akar masih `humanverse-x/`, sedangkan nama resmi proyek sudah
> **HumanVerse XOS**. Lihat butir **C-5** dan issue penyelarasan nama.
