# 137 — §7.14–§7.16 Processing Engine, Data Quality & Lineage

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.14 — Data Processing Engine

```
Events → Ingestion → Validation → Normalization → Transformation
      → Feature Engineering → Enrichment → Storage
```

> **Setiap tahap dapat diulang.** Ini penting untuk:
> `reproducibility · debugging · data quality · research`

> ⭐ *"Setiap tahap dapat diulang"* adalah syarat yang membuat aturan **D** di
> [`../spec/02`](../spec/02-ERD.md) benar — tabel domain boleh dibangun ulang
> dari event. Tanpa pipeline yang bisa diulang, klaim itu kosong.

---

## §7.15 — Data Quality Engine

> **AI yang hebat dengan data buruk tetap menghasilkan sistem buruk.**

| Metric | Tujuan |
|---|---|
| **Completeness** | data tidak banyak kosong |
| **Accuracy** | nilai benar |
| **Consistency** | tidak kontradiktif |
| **Freshness** | masih relevan |
| **Validity** | mengikuti schema |
| **Uniqueness** | tidak duplicate |

> ⭐ **`Freshness` dan `Uniqueness` langsung terpakai** di dua tempat yang sudah
> ditulis: *freshness* adalah yang membuat **B-14** (Context Engine gagal senyap
> saat satu sinyal mati) bisa terdeteksi, dan *uniqueness* adalah
> `events.idempotency_key`.
>
> ⚠️ **`Accuracy` untuk data perilaku manusia tidak punya acuan.** Tidak ada
> sumber kebenaran yang bisa mengatakan bahwa "user tidur 6 jam" itu benar —
> yang ada hanya apa yang dilaporkan atau diukur perangkat. Metrik ini hanya
> bisa diterapkan pada data yang punya acuan luar (cuaca, kalender), sama
> seperti masalah **B-10** pada evaluator.

---

## §7.16 — Data Lineage

> Kita harus bisa menjawab: **"Rekomendasi ini menggunakan data apa?"**

```
Recommendation → Model v2.4 → Feature → Event → Original User Action
```

> Ini sangat penting untuk **audit AI**.

> ⭐ **Rantai ini sudah setengah ada di V0.** `recommendations` menyimpan
> `score_breakdown`, `rationale`, dan `context_snapshot`; `agent_runs`
> menyimpan `tools_used`, `memory_scopes`, dan `decision`
> ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)). Yang belum: sambungan ke
> **versi model** dan ke **feature** yang dipakai.
>
> Menambahkan `model_version` dan `feature_set_version` ke `recommendations`
> sekarang jauh lebih murah daripada merekonstruksinya nanti — dan tanpa itu,
> pertanyaan *"kenapa dulu kamu menyarankan ini"* hanya bisa dijawab sampai
> setengah jalan.
>
> ⚠️ Lineage juga bertaut ke **C-9** (hak hapus vs jejak audit): kalau
> rekomendasi menyimpan tautan ke event asal, penghapusan event harus
> memutuskan apakah rekomendasi lamanya ikut hilang atau tinggal sebagai
> catatan tanpa sumber.
