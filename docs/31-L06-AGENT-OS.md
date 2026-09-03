# 31 — Layer 6: Agent Operating System (AgentOS)

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Ini adalah sistem operasi khusus untuk AI Agent.**

---

## Komponen

| Service | Fungsi |
|---|---|
| **Agent Registry** | Daftar seluruh agent |
| **Agent Scheduler** | Menjalankan agent |
| **Task Queue** | Antrian pekerjaan |
| **Workflow Engine** | Alur agent |
| **Tool Registry** | Semua tool |
| **Memory Manager** | Memori |
| **Event Bus** | Komunikasi |
| **Policy Engine** | Rule |

---

## Folder

```
agent-os/
├── scheduler/
├── registry/
├── executor/
├── event-bus/
├── memory/
├── policies/
├── workflow/
└── tools/
```

---

## Cara kerja

| # | Langkah |
|---|---|
| 1 | User meminta sesuatu |
| 2 | **Planner** membuat task |
| 3 | **Scheduler** memilih agent |
| 4 | Agent mengambil **memory** |
| 5 | Agent memakai **tools** |
| 6 | **Evaluator** mengecek hasil |
| 7 | **Orchestrator** menggabungkan jawaban |

```
  User
    │
    ▼
 Planner ──▶ Scheduler ──▶ Agent ──┬──▶ Memory
                                   └──▶ Tools
                                        │
                                        ▼
                                   Evaluator
                                        │
                                        ▼
                                  Orchestrator
                                        │
                                        ▼
                                    Jawaban
```
