# 114 — Phase 5: HumanVerse Research Lab (ikhtisar naskah kesembilan)

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Target

> Membangun **fondasi teknologi AI** yang membuat HumanVerse semakin
> **personal**, semakin **akurat**, dan semakin **efisien** seiring waktu.

## Tujuan fase ini

> Pada fase sebelumnya kita membangun aplikasi, AgentOS, dan Behavior
> Intelligence. Sekarang kita membangun **Research Layer** — sekumpulan model,
> algoritma, eksperimen, dan evaluasi yang menjadi **keunggulan teknologi**
> HumanVerse.

### Empat prinsip utama

```
1.  Model yang tepat untuk masalah yang tepat
    (LLM bukan solusi untuk semuanya).

2.  Personalisasi berdasarkan data pengguna
    dengan izin pengguna.

3.  Prediksi berbasis probabilitas,
    bukan klaim kepastian.

4.  Semua model memiliki evaluasi, versi, dan rollback.
```

> ⭐ Keempatnya konsisten dengan naskah sebelumnya: prinsip 1 = Model Router
> (naskah 5 §22), prinsip 3 = *"prediksi bukan kepastian"* yang dipegang sejak
> naskah 1, prinsip 4 = Model Lifecycle (Layer 31).

---

## Arsitektur Research Lab

Repository khusus riset:

```
research/
├── behavior/
├── preference/
├── recommendation/
├── simulation/
├── world-model/
├── embeddings/
├── graph/
├── evaluation/
├── benchmarks/
├── experiments/
├── papers/
└── notebooks/
```

> ⚠️ Naskah ini memuat **dua pohon `research/` yang berbeda** — yang ini di
> awal, dan satu lagi di akhir ([`122`](122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md))
> dengan nama dan isi berbeda. Lihat butir **E-54**.

---

## Peta 15 Research Pillar

| # | Pillar | Berkas |
|---|---|---|
| **1** | Behavior Foundation Model (BFM) | [`115`](115-R1-BEHAVIOR-FOUNDATION-MODEL.md) |
| **2** | Preference Learning Engine | [`116`](116-R2-R3-PREFERENCE-DAN-GRAPH.md) |
| **3** | Human Knowledge Graph Intelligence | [`116`](116-R2-R3-PREFERENCE-DAN-GRAPH.md) |
| **4** | Memory Compression | [`117`](117-R4-MEMORY-COMPRESSION.md) |
| **5** | World Model | [`118`](118-R5-R7-WORLD-MODEL-SIMULASI.md) |
| **6** | Counterfactual Reasoning | [`118`](118-R5-R7-WORLD-MODEL-SIMULASI.md) |
| **7** | Simulation Engine | [`118`](118-R5-R7-WORLD-MODEL-SIMULASI.md) |
| **8** | Human Embedding System | [`119`](119-R8-R9-EMBEDDING-REPRESENTASI.md) |
| **9** | Personal Representation Layer | [`119`](119-R8-R9-EMBEDDING-REPRESENTASI.md) ⭐ |
| **10** | Adaptive Intervention Research | [`120`](120-R10-R12-INTERVENSI-XAI-EKSPERIMEN.md) |
| **11** | AI Explainability Lab | [`120`](120-R10-R12-INTERVENSI-XAI-EKSPERIMEN.md) |
| **12** | Human Experiment Framework | [`120`](120-R10-R12-INTERVENSI-XAI-EKSPERIMEN.md) |
| **13** | Benchmark Platform | [`121`](121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md) |
| **14** | Experiment Registry | [`121`](121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md) |
| **15** | Research Governance | [`121`](121-R13-R15-BENCHMARK-REGISTRY-GOVERNANCE.md) |
| — | Repo final · roadmap R1–R8 · deliverable | [`122`](122-PHASE-5-ROADMAP-DAN-DELIVERABLE.md) |

---

> 🛑 **Temuan terpenting fase ini ada di urutannya, bukan di isinya.**
> Seluruh dataset yang dibutuhkan Pillar 1 (`behavior_events`, `habit_events`,
> `sleep_events`, `mood_events`, `calendar_events`, `context_snapshots`) baru
> ada **setelah V0 dipakai orang selama berbulan-bulan**. Research Lab tidak
> bisa dimulai sebelum ada datanya. Lihat butir **B-21**.
>
> ⚠️ Angka liar `7`, `6`, `5`, `4` muncul lagi menempel di judul pilar —
> artefak salin-tempel yang sama seperti **A-1**/**H-9**, kini di naskah keenam
> berturut-turut. Dibuang dari dokumen rapi.
