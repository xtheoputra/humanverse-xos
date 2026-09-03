# 94 — §27–§28 Development Lifecycle & AI Coding Agent Ecosystem

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §27 — Development lifecycle

> AI agent Anda **tidak boleh** langsung melakukan `AI → production`.

```
Human
 ↓
Product Spec
 ↓
Architecture Agent
 ↓
Task Breakdown
 ↓
Coding Agent
 ↓
Implementation
 ↓
Unit Test
 ↓
Integration Test
 ↓
Security Scan
 ↓
AI Review Agent
 ↓
Human Review
 ↓
Merge
 ↓
Deploy
 ↓
Observability
 ↓
Feedback
```

> ## AI boleh mempercepat engineering, tetapi governance tetap manusia.

---

## §28 — AI Coding Agent ecosystem

```
Engineering Manager Agent
        │
        ├── Product Agent
        ├── Architect Agent
        ├── Backend Agent
        ├── Frontend Agent
        ├── AI Engineer Agent
        ├── Database Agent
        ├── QA Agent
        ├── Security Agent
        ├── DevOps Agent
        └── Reviewer Agent
```

> Tetapi mereka bekerja **dengan kontrak**:

| Agent | Keluaran |
|---|---|
| Architect Agent | `ARCHITECTURE.md` |
| Backend Agent | Implementation |
| QA Agent | **TEST REPORT** |
| Security Agent | **SECURITY REPORT** |
| Reviewer Agent | **CODE REVIEW** |

> ⭐ Ini menegaskan bahwa daftar 10 agent pengembangan di sini **bukan** bagian
> dari 22 agent produk di §12. Dua ekosistem berbeda: satu membangun produk,
> satu berjalan di dalam produk.
