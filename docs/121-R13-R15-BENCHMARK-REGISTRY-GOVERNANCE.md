# 121 — Pillar 13–15: Benchmark, Experiment Registry & Research Governance

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pillar 13 — Benchmark Platform

> **Semua model harus diuji.**

```
benchmarks/
  behavior/
  fashion/
  recommendation/
  memory/
  planning/
```

Contoh **Fashion Benchmark**:

| Input | Expected |
|---|---|
| Hot weather · Office · Minimal style | breathable · formal · dark shoes |

> ℹ️ Contoh ini **sama persis** dengan Layer 35 naskah 7 — konsisten antar
> naskah, jarang terjadi.
>
> ⚠️ Dan masalahnya juga sama (**B-10**): *breathable* untuk cuaca panas punya
> kebenaran acuan objektif; *formal* dan *dark shoes* tidak. Benchmark hanya
> bisa dibuat untuk yang jenis pertama; sisanya hanya bisa diukur dari umpan
> balik pengguna nyata.

---

## Pillar 14 — Experiment Registry

> **Semua eksperimen tercatat.**

```yaml
experiment:
  name: adaptive-reminder-v2

hypothesis:
  context-aware reminders improve completion

status:
  running

owner:
  behavior-lab
```

> ## Tidak ada eksperimen tanpa dokumentasi.

---

## Pillar 15 — Research Governance

> Setiap riset memiliki **checklist**.

```
Purpose
Data Used
Consent
Evaluation
Rollback Plan
Success Criteria
```

---

> ⭐ **`Consent` sebagai butir wajib di setiap riset menjawab sebagian C-11.**
> Melatih model di atas data tidur, mood, dan jurnal butuh dasar persetujuan
> yang berbeda dari sekadar memakainya untuk memberi rekomendasi — checklist
> ini memaksa pertanyaan itu ditanyakan sebelum riset dimulai, bukan sesudah.
>
> Untuk membuatnya benar-benar mengikat, dua hal perlu ditambahkan:
> **`consents.kind = 'model_training'`** sebagai izin tersendiri di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md), dan aturan bahwa menolaknya
> **tidak mengurangi layanan**.
>
> ⭐ **`Rollback Plan` wajib sejak tahap riset**, bukan hanya saat deployment —
> ini lebih ketat daripada Model Lifecycle (Layer 31) dan patut dipertahankan.
>
> ⚠️ Yang belum ada di checklist: **siapa yang menyetujui**. Untuk proyek satu
> orang, `owner: behavior-lab` dan penyetujunya adalah orang yang sama. Itu
> tidak masalah sekarang, tapi perlu ditulis supaya kelak tidak dikira sudah
> ada pemeriksaan pihak kedua.
