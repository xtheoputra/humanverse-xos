# 138 — §7.17–§7.23 ML Platform, Serving, Inference & Flywheel

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.17 — ML Training Platform

```
Dataset → Training → Evaluation → Model Registry
       → Staging → Canary → Production
```

> Model **tidak boleh** langsung `training → production`.

> ⭐ **`Canary` adalah langkah baru** yang belum ada di Model Lifecycle
> (Layer 31 naskah 7: *Experiment → Evaluation → Approval → Deployment →
> Monitoring → Improvement*). Untuk model perilaku, canary penting justru
> karena kerusakannya tidak kelihatan langsung — rekomendasi yang lebih buruk
> tetap terlihat wajar. Yang perlu ditetapkan: **berapa lama** canary berjalan
> dan **metrik apa** yang membatalkannya (**B-10**).

---

## §7.18 — Model Registry

```
models/
  behavior-model · preference-model · recommendation-model
  ranking-model · embedding-model
```

```yaml
name: behavior-model
version: 2.3
dataset: behavior_dataset_v7
metrics:
  precision: ...
  recall: ...
status: staging
```

> ⭐ **`dataset: behavior_dataset_v7` di manifest model** adalah setengah dari
> lineage §7.16 — model tahu data mana yang melahirkannya. Yang melengkapinya:
> `feature_set_version`.

---

## §7.19–§7.20 — Model Serving & Online Inference

```
AI Gateway → Model Router → Inference Service → Model
```

| Task | Model |
|---|---|
| simple classification | small model |
| complex reasoning | large model |
| image understanding | vision model |
| embedding | embedding model |

```
User Request → Context Engine → Feature Store
    → Model Router → Inference → Recommendation
```

Target: **low latency · high availability · controlled cost**

> ℹ️ Ini pernyataan **keempat** untuk Model Router (naskah 4 §49, naskah 5 §22,
> naskah 7 Layer 32, dan di sini). Isinya konsisten — pengulangan, bukan
> tabrakan.
>
> ⚠️ Naskah 5 §22 masih yang paling hemat: *"catat mood"* di sana dirutekan ke
> **`deterministic`**, bukan model kecil. Versi itu yang sebaiknya dipakai.

---

## §7.21–§7.22 — Batch Inference & Orkestrasi

> **Tidak semua AI harus real-time.**

```
Setiap malam:  User behavior analysis → Update behavior profile → Generate insights
Setiap Minggu: Weekly Life Review
```

```
Daily 02:00   → Aggregate Events → Generate Features → Run Models → Update Profiles
Sunday 20:00  → Weekly Review → Generate Insights → Notify User
```

> **Batch inference menghemat biaya.**

> ⭐ Ini penerapan **AI Cost Engine** yang paling nyata: sebagian besar
> kecerdasan produk ini **tidak** perlu dijawab dalam satu detik.
>
> ⚠️ **`Daily 02:00` dan `Sunday 20:00` adalah waktu server, bukan waktu
> pengguna.** Untuk produk yang seluruh datanya berbasis tanggal lokal
> (`habit_completions.for_date`), pekerjaan harian harus berjalan per zona
> waktu pengguna — kalau tidak, "hari kemarin" akan salah untuk sebagian orang.
> `Sunday 20:00` juga akan mengirim notifikasi tengah malam bagi sebagian.

---

## §7.23 — AI Data Flywheel

```
HUMAN → ACTION → EVENT → DATA PLATFORM
                     ┌────────┼────────┐
                  Features  Graph   Vector
                     └────────┼────────┘
                          MODELS
                             ↓
                     PERSONALIZATION
                             ↓
                     RECOMMENDATION
                             ↓
                          HUMAN
```

> ⚠️ Roda ini **tidak punya gerbang umpan balik**. Naskah 4 §39 menutup
> flywheel-nya dengan peringatan *"lebih banyak data ≠ otomatis lebih pintar"*
> dan menuntut **Data Quality + Evaluation + Feedback + Privacy**. Di sini
> `RECOMMENDATION → HUMAN` langsung kembali ke `ACTION` tanpa melewati
> penerimaan pengguna — padahal `recommendation_feedback` justru sinyal yang
> membuat roda ini berputar ke arah yang benar, bukan sekadar berputar.
