# 17 — AI Workflow Engine

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Gunakan

- **LangGraph**
- **MCP**
- **Tool Calling**
- **Function Routing**

---

## Contoh workflow

User berkata:

> "Besok saya interview."

| Urutan | Agent | Tindakan |
|---|---|---|
| 1 | **Planner** | membuat task |
| 2 | **Memory** | mengambil preferensi |
| 3 | **Fashion Agent** | memilih outfit |
| 4 | **Calendar Agent** | mengecek waktu |
| 5 | **Health Agent** | menyarankan tidur |

> **Semua menjadi satu jawaban.**

```
  "Besok saya interview."
            │
            ▼
      ┌──────────┐
      │ Planner  │  membuat task
      └────┬─────┘
           ▼
      ┌──────────┐
      │  Memory  │  mengambil preferensi
      └────┬─────┘
           ▼
   ┌───────┴────────┬──────────────┐
   ▼                ▼              ▼
Fashion         Calendar        Health
outfit           waktu           tidur
   └───────┬────────┴──────────────┘
           ▼
      SATU JAWABAN
```
