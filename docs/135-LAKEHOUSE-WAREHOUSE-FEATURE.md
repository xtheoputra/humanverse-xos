# 135 — §7.6–§7.9 Lakehouse, Warehouse & Feature Store

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.6 — Data Lakehouse

> PostgreSQL **tidak boleh** menjadi tempat seluruh data analytics.

```
Operational Database → CDC/Event → Data Lake
    → Transformations → Lakehouse
```

```
data-lake/
  raw/        events/ · integrations/ · imports/
  processed/  behavior/ · lifestyle/ · goals/ · activity/
  curated/    features/ · analytics/ · research/
```

---

## §7.7 — Data Warehouse

| Fact | Dimension |
|---|---|
| `fact_habit_completion` | `dim_user` |
| `fact_workout` | `dim_date` |
| `fact_sleep` | `dim_goal` |
| `fact_recommendation` | `dim_habit` |
| `fact_user_activity` | `dim_context` |

> Sehingga bisa dijawab: *"Pada konteks seperti apa habit completion paling
> tinggi?"* — **tanpa membebani database transaksi**.

> ⭐ **`dim_context` adalah dimensi yang paling menentukan di seluruh gudang
> ini**, dan sekaligus yang paling sulit: konteks (cuaca, kalender, lokasi,
> mood) berubah terus-menerus, sedangkan dimensi gudang biasanya lambat
> berubah. Perlu diputuskan apakah ia dimensi bertingkat (*slowly changing*)
> atau justru disimpan sebagai cuplikan di tabel fakta — dan
> `recommendations.context_snapshot` di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) sudah memilih yang kedua.

---

## §7.8 — Feature Store

```
user_sleep_avg_7d            morning_energy_avg
habit_completion_rate_30d    fashion_preference_confidence
workout_frequency_14d
```

```
Feature Store → Behavior Model → Prediction
```

| | Untuk |
|---|---|
| **Offline Features** | training dan research |
| **Online Features** | real-time inference |

> ⭐ **Pemisahan offline/online adalah bagian yang paling sering dilewatkan
> orang, dan penyebab kegagalan model yang paling sulit dilacak** —
> *training/serving skew*: model dilatih dengan `sleep_avg_7d` yang dihitung
> dari data lengkap, lalu di produksi menerima angka yang dihitung berbeda.
> Menyebutkan keduanya sejak blueprint adalah keputusan yang matang.
>
> ⚠️ Yang belum ditulis: **satu definisi feature dipakai kedua jalur**. Kalau
> `habit_completion_rate_30d` dihitung dua kali di dua tempat, skew itu justru
> yang terjadi.
>
> ℹ️ `fashion_preference_confidence` menyambung ke Confidence Layer — feature
> yang membawa keyakinannya sendiri, bukan hanya nilainya.

---

## §7.9 — Feature Engineering Pipeline

```
Raw Events → Cleaning → Aggregation → Feature Engineering
    → Validation → Feature Store
```

```
habit.completed → completion_count_7d → completion_rate_7d → behavior_feature
```

> ⚠️ **`Cleaning` perlu aturan tertulis.** Membersihkan data perilaku manusia
> berarti memutuskan mana yang dianggap *"tidak valid"* — dan pilihan itu bisa
> menghapus justru pola nyata (workout jam 3 pagi bukan galat; ia mungkin
> pekerja giliran malam). Untuk produk yang dasarnya *"AI melihat apa yang
> benar-benar dilakukan user"*, aturan pembersihan adalah keputusan produk,
> bukan keputusan teknis.
