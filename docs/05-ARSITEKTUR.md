# 05 — Enterprise-Grade Technology Architecture

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Tumpukan yang ditetapkan pemilik

| Teknologi | Peran |
|---|---|
| **Flutter** | Mobile & Web |
| **FastAPI** | Backend |
| **PostgreSQL** | Behavioral Database |
| **Qdrant** | AI Memory |
| **Neo4j** | Human Knowledge Graph |
| **ClickHouse** | Analytics |
| **LangGraph** | AI Workflow |
| **Docker + Kubernetes** | Cloud Native |

---

## Bentuk kasar

```
                 ┌───────────────────────────┐
                 │  Flutter — Mobile & Web   │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │      FastAPI — Backend    │
                 └─────────────┬─────────────┘
                               │
                 ┌─────────────▼─────────────┐
                 │   LangGraph — AI Workflow │
                 └──┬────────┬────────┬──────┘
                    │        │        │
      ┌─────────────▼──┐ ┌───▼─────┐ ┌▼──────────────┐
      │  PostgreSQL    │ │ Qdrant  │ │    Neo4j      │
      │  Behavioral DB │ │ AI Mem. │ │ Knowledge Grf │
      └────────────────┘ └─────────┘ └───────────────┘
                    │
            ┌───────▼────────┐
            │   ClickHouse   │
            │    Analytics   │
            └────────────────┘

        semuanya di atas Docker + Kubernetes (Cloud Native)
```

---

## Kenapa empat penyimpanan berbeda

| Penyimpanan | Menyimpan apa |
|---|---|
| PostgreSQL | Fakta perilaku: habit, log tidur, catatan makan, transaksi |
| Neo4j | **Hubungan** antar perilaku — inti dari Human Knowledge Graph |
| Qdrant | Ingatan AI: embedding preferensi, gaya, refleksi |
| ClickHouse | Analitik deret waktu bervolume besar |
