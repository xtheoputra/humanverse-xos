# 141 — §7.33–§7.35 Repo, Roadmap & Deliverable Phase 7

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.33 — Final Data Platform Repository

```
data-platform/
├── ingestion/     ├── vector/       ├── privacy/
├── events/        ├── graph/        ├── ml-platform/
├── schemas/       ├── pipelines/    ├── model-registry/
├── streaming/     ├── datasets/     ├── inference/
├── lakehouse/     ├── quality/      ├── orchestration/
├── warehouse/     ├── lineage/      ├── synthetic-data/
├── feature-store/ ├── governance/   └── disaster-recovery/
```

> ⚠️ **Ini pohon tingkat-atas keempat, dan hubungannya dengan monorepo belum
> pernah dinyatakan.**
>
> | Naskah | Pohon |
> |---|---|
> | 5 §4 | `humanverse-x/` — `apps/ services/ intelligence/ agents/ platform/ **data/** packages/ …` |
> | 9 | `research/` — 12 lab |
> | 10 | `developer-platform/` — 11 folder |
> | 11 | `data-platform/` — 21 folder |
>
> `data/` (naskah 5) dan `data-platform/` (di sini) mengurus hal yang sama dan
> tumpang tindih di `pipelines/`, `datasets/`, `feature-store/`. Begitu pula
> `research/` dengan `intelligence/`.
>
> Butir **E-27** saya tutup sebagai **H-10** ketika naskah 5 menetapkan
> monorepo final. Tiga naskah sesudahnya menambah pohon sendiri-sendiri tanpa
> menempatkannya di dalam monorepo itu — jadi penutupan itu perlu ditinjau
> ulang. Lihat butir **E-66**.

---

## §7.34 — Implementation Roadmap

| Sprint | Fokus |
|---|---|
| **D1** | Event Foundation — schema, bus, consumers |
| **D2** | Data Pipeline — ingestion, normalization, storage |
| **D3** | Analytics — warehouse, analytics, data quality |
| **D4** | AI Data — feature store, vector DB, graph DB |
| **D5** | ML Platform — dataset, training, evaluation, registry |
| **D6** | Inference — serving, router, batch, online |
| **D7** | Governance — lineage, privacy, retention, deletion, audit |
| **D8** | Scale — multi-region, DR, global data plane |

> 🛑 **`D1`–`D8` sudah dipakai naskah 10 untuk hal yang sama sekali berbeda.**
>
> | | Naskah 10 (Developer Platform) | Naskah 11 (Data Platform) |
> |---|---|---|
> | D1 | Developer Portal | Event Foundation |
> | D4 | Agent SDK | AI Data |
> | D7 | Marketplace | Governance |
>
> Ini pengulangan **E-59** (tabrakan penomoran Layer) di sumbu yang berbeda.
> Sekarang *"kita di D4"* berarti dua hal. Lihat butir **E-64**.
>
> ⚠️ **D7 Governance ada di urutan ketujuh** — artinya lineage, privacy,
> retention, deletion, dan audit dibangun **setelah** data mengalir enam sprint.
> Menghapus data yang sudah tersebar ke lakehouse, feature store, vector, dan
> graph jauh lebih sulit daripada menyiapkan jalur hapusnya lebih dulu (§7.25
> sendiri menjelaskan kenapa). Minimal `retention` dan `deletion` sebaiknya
> ikut di **D2**.

---

## §7.35 — Deliverables Phase 7

| Component | Target |
|---|---|
| Event Platform · Schema Registry · Streaming | ✅ Blueprint |
| Data Lakehouse · Warehouse · Feature Store | ✅ Blueprint |
| Vector Platform · Knowledge Graph | ✅ Blueprint |
| Data Quality · Data Lineage | ✅ Blueprint |
| ML Platform · Model Registry · Model Serving | ✅ Blueprint |
| Data Governance · Privacy Pipeline | ✅ Blueprint |
| Synthetic Data · Disaster Recovery | ✅ Blueprint |
| **Multi-region** | 🔭 **Future** |

> ⭐ **Pertama kalinya sebuah deliverable ditandai berbeda.** Sepuluh naskah
> sebelumnya menandai semuanya sama; di sini *Multi-region* dipisahkan sebagai
> *Future*. Gradasi itu berguna — ia membedakan "belum dibangun" dari "belum
> waktunya dipikirkan".

---

## Posisi setelah Phase 7

```
PHASE 5 Research Lab → PHASE 6 Developer Ecosystem → PHASE 7 Data & AI Infra
                                  ↓
   Human Data → Event Platform → Data Platform → AI/ML Platform
             → Intelligence → Agents → Human Experience
```

> ## HumanVerse bukan sekadar aplikasi yang menggunakan AI.
> HumanVerse sedang dirancang sebagai **data + intelligence + agent platform
> yang kebetulan memiliki aplikasi sebagai interface utamanya.**

---

## Teaser Phase 8 — AI Safety, Security & Privacy Framework

```
Zero-Trust Architecture · consent engine · data vault · policy engine
agent permissions · risk engine · abuse prevention · model safety
privacy-preserving AI · auditability · incident response · governance
```

> Fase yang **tidak boleh diperlakukan sebagai tambahan belakangan** — karena
> HumanVerse berurusan dengan data dan keputusan yang **sangat dekat dengan
> kehidupan manusia**.

> ⭐ **`abuse prevention` dan `Zero-Trust` baru pertama kali muncul.**
> *Abuse prevention* mengisi lubang nyata: sepuluh naskah membahas melindungi
> pengguna **dari kesalahan AI**, belum pernah melindungi pengguna **dari orang
> lain** yang memakai platform ini — atau melindungi platform dari pengguna
> yang menyalahgunakannya.
>
> ⚠️ Enam dari dua belas butir itu **sudah ditulis di naskah sebelumnya**
> (consent engine, data vault, policy engine, agent permissions, risk engine,
> auditability, incident response). Seperti **E-53**, Phase 8 sebagian
> perluasan skala, bukan pekerjaan baru.
