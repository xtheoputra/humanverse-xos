# 140 — §7.27–§7.32 Multi-region, DR, Observability, Research & Governance

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.27 — Multi-Region Data Architecture

```
Global Router
      │
Region A · Region B · Region C
      │
Data Plane (per region)
```

> **Tetapi jangan dibangun pada V0.** Ini *future architecture*.

---

## §7.28 — Disaster Recovery

```
Backup · Replication · Recovery · Failover
```

| Istilah | Arti |
|---|---|
| **RPO** | berapa banyak data yang boleh hilang |
| **RTO** | berapa lama sistem boleh down |

> Angka final ditentukan berdasarkan **kebutuhan bisnis dan biaya**.

> ⭐ **Menolak menuliskan angka yang belum bisa didukung adalah keputusan yang
> benar** — dan berbeda dari Layer 44 naskah 7 yang menetapkan *99,9 % uptime*
> tanpa ada yang berjaga (**B-18**). Naskah ini lebih berhati-hati.

---

## §7.29 — Observability Data Platform

| Pipeline | AI Inference |
|---|---|
| throughput · latency · failure · backlog · **freshness** | latency · **token usage** · **cost** · error · **quality** |

> ⭐ `freshness` di pipeline dan `cost` di inference adalah dua metrik yang
> langsung menjawab masalah yang sudah dicatat: **B-14** (Context Engine gagal
> senyap) dan **AI Cost Engine**. `quality` masih butuh definisi — bertaut
> **B-10**.

---

## §7.30 — Research Data Environment

> Research **tidak boleh** langsung mengakses production database.

```
Production Data → Privacy Filter → Anonymization / Pseudonymization
    → Research Dataset → Experiments
```

> ## Production ≠ Research

> ⭐⭐ **Ini pemisahan yang paling dibutuhkan Phase 5.** Research Lab (naskah 9)
> memerlukan `behavior_events`, `mood_events`, dan `journal` — dan tanpa
> lapisan ini, riset berarti membuka data hidup orang kepada proses
> eksperimen.
>
> ⚠️ **Anonimisasi data perilaku jauh lebih sulit daripada menghapus nama.**
> Pola waktu tidur, jadwal olahraga, dan ritme jurnal seseorang adalah sidik
> jari tersendiri; dataset yang "dianonimkan" dengan membuang `user_id` sering
> masih bisa dikaitkan kembali. Untuk dataset perilaku, **pseudonimisasi +
> agregasi + batas ukuran kelompok** biasanya lebih jujur daripada mengklaim
> anonim.

---

## §7.31 — Synthetic Data

```
Synthetic User A · Synthetic User B · Synthetic User C
```

> Engineer dapat menguji **behavior model, recommendation, agents, pipelines**
> tanpa memakai data manusia nyata.

> ⭐ Konsisten dengan Synthetic User Simulator (Layer 36 naskah 7) dan Testing
> Sandbox (DP-L14 naskah 10). Tiga naskah, satu arah.
>
> ⚠️ Model yang dilatih di atas data sintetis hanya sebaik generatornya — untuk
> **pengujian** ini tepat, untuk **pelatihan** BFM ia tidak menggantikan data
> nyata (**B-21**).

---

## §7.32 — AI Data Governance

```yaml
dataset:
  name: behavior_events
owner: behavior-team
classification: sensitive
purpose:
  - behavior-model
source:
  - event-stream
quality:
  score: 0.94
retention:
  policy: ...
```

> ⭐ Manifest dataset ini menyatukan empat hal yang tersebar di naskah lain:
> klasifikasi (§7.2), tujuan (§7.24), kualitas (§7.15), dan retensi (§7.26) —
> dalam satu berkas yang bisa diperiksa mesin.
>
> ⚠️ `owner: behavior-team` mengandaikan ada tim. Untuk proyek satu orang,
> semua `owner` akan berisi nama yang sama — itu tidak apa-apa, tapi jangan
> sampai dikira ada pemisahan tanggung jawab yang sebenarnya belum ada.
