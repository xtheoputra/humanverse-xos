# 18 — Database, AI Pipeline & Recommendation Engine

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).
>
> Naskah pertama menyebut tumpukan yang lebih ringkas di
> [`05-ARSITEKTUR.md`](05-ARSITEKTUR.md); berkas ini menambah **Redis** dan
> **S3**.

---

## Enterprise Database Architecture

| Database | Fungsi |
|---|---|
| **PostgreSQL** | Transaction |
| **Neo4j** | Human Graph |
| **Qdrant** | Memory |
| **ClickHouse** | Analytics |
| **Redis** | Cache |
| **S3** | Media |

---

## AI Pipeline

Delapan tahap, berputar terus:

```
 1. Data Collection
 2. Event Processing
 3. Feature Engineering
 4. Embedding
 5. Graph Update
 6. Prediction
 7. Recommendation
 8. Feedback Learning
          │
          └──────▶ kembali ke 1
```

---

## Recommendation Engine

Scoring menggunakan **banyak sinyal**.

| Signal | Bobot |
|---|---|
| Habit | **25 %** |
| Preference | **25 %** |
| Sleep | 20 % |
| Mood | 15 % |
| Calendar | 10 % |
| Weather | 5 % |
| **Total** | **100 %** |

> AI menghasilkan **keputusan personal**.

Dua sinyal terberat — **Habit** dan **Preference** (25 % masing-masing) —
bersama-sama menentukan separuh keputusan.
