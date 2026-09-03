# 122 — Phase 5: repo final, roadmap R1–R8 & deliverable

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Research Repository Final

```
research/
├── behavior-lab/
├── preference-lab/
├── simulation-lab/
├── world-model-lab/
├── graph-lab/
├── memory-lab/
├── explainability-lab/
├── intervention-lab/
├── benchmark-lab/
├── experiment-registry/
├── evaluation/
└── papers/
```

> ⚠️ **Ini pohon `research/` kedua di naskah yang sama.** Yang di awal
> ([`114`](114-PHASE-5-IKHTISAR.md)) berbunyi `behavior/ preference/
> recommendation/ simulation/ world-model/ embeddings/ graph/ evaluation/
> benchmarks/ experiments/ papers/ notebooks/`.
>
> Perbedaannya bukan sekadar akhiran `-lab`:
> **hilang** — `recommendation/`, `embeddings/`, `notebooks/`;
> **muncul** — `memory-lab/`, `explainability-lab/`, `intervention-lab/`.
>
> Keduanya berjumlah 12, jadi sekilas terlihat cocok padahal tidak — pola yang
> sama persis dengan **E-13** (tabel MCP tool vs foldernya). Lihat **E-54**.

---

## Roadmap Implementasi Research Lab

| Sprint | Fokus |
|---|---|
| **R1** | Behavior Prediction |
| **R2** | Preference Learning |
| **R3** | Memory Compression |
| **R4** | Graph Intelligence |
| **R5** | Explainability |
| **R6** | Simulation |
| **R7** | Adaptive Intervention |
| **R8** | Benchmark Platform |

> 🛑 **Urutan ini tidak bisa dimulai dari R1.** Behavior Prediction membutuhkan
> `behavior_events`, `habit_events`, `sleep_events`, `mood_events`,
> `calendar_events`, dan `context_snapshots` — semuanya baru terisi setelah V0
> **dipakai orang selama berbulan-bulan**, dan dua di antaranya tidak ada di V0
> sama sekali.
>
> Yang **bisa** dikerjakan tanpa data pengguna: **R8 Benchmark Platform** dan
> **R5 Explainability** (keduanya soal kerangka, bukan model), lalu
> **R3 Memory Compression** (aturan retensi, bukan pembelajaran).
> Lihat butir **B-21**.

---

## Deliverables Phase 5

| Deliverable | Status |
|---|---|
| Research Repository | **Blueprint** |
| Behavior Foundation Model Spec | **Blueprint** |
| Preference Learning Spec | **Blueprint** |
| Memory Compression Spec | **Blueprint** |
| World Model Spec | **Blueprint** |
| Simulation Engine Spec | **Blueprint** |
| Explainability Framework | **Blueprint** |
| Experiment Registry | **Blueprint** |
| Benchmark Framework | **Blueprint** |
| Research Governance | **Blueprint** |

> ✅ **Kesepuluhnya jujur ditandai *Blueprint*, bukan *Done*.** Ini pertama
> kalinya sebuah naskah menyertakan kolom status yang mengakui bahwa isinya
> belum dibangun.

---

## Apa yang berubah setelah Phase 5?

> Sebelum fase ini, HumanVerse adalah **platform AI yang memahami pengguna**.
>
> Setelah fase ini, HumanVerse memiliki **lapisan R&D internal** yang
> memungkinkan setiap kemampuan AI — prediksi perilaku, personalisasi,
> simulasi, hingga explainability — **dikembangkan sebagai proyek riset yang
> terukur, memiliki benchmark, versi, dan evaluasi**.
>
> Dengan begitu, **inovasi baru tidak langsung masuk ke produksi**; setiap
> model harus melewati siklus:
>
> ```
> eksperimen → evaluasi → deployment → monitoring → rollback
> ```
>
> Fase 5 juga menyiapkan fondasi untuk fase berikutnya, karena semua model,
> eksperimen, dan benchmark sudah memiliki struktur yang dapat dipakai oleh
> **AI coding agents** maupun tim engineering **tanpa kehilangan konteks**.
