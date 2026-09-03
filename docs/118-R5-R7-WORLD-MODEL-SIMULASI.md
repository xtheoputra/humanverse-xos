# 118 — Pillar 5–7: World Model, Counterfactual & Simulation

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pillar 5 — World Model

> Ini sering disalahpahami.
>
> ## World Model bukan meramal masa depan.
> Ia **mensimulasikan kemungkinan berdasarkan pola**.

User bertanya: *"Kalau saya belajar AI setiap malam selama 3 bulan?"*

```
Scenario

Learning Time
    ↓
Knowledge
    ↓
Portfolio
    ↓
Career Readiness
```

Output:

```
Expected Effects

Knowledge ↑
Portfolio Opportunity ↑
Time Cost ↑
Sleep Risk (if bedtime shifts)
```

> Ini adalah **scenario analysis**.

> ⭐ **`Sleep Risk (if bedtime shifts)` adalah bagian terbaik di pilar ini.**
> Simulasi yang hanya menunjukkan keuntungan adalah iklan. Menyebut **biaya**
> (waktu) dan **risiko** (tidur) di keluaran yang sama membuatnya jadi alat
> keputusan.

---

## Pillar 6 — Counterfactual Reasoning

> Fitur: *"Bagaimana kalau saya tidak membeli sepatu itu?"*

AI membandingkan **Current** vs **Alternative**:

| Factor | Current | Alternative |
|---|---|---|
| Budget | turun | stabil |
| Wardrobe Variety | naik | sama |
| Cost | naik | tetap |

> Ini membantu pengambilan keputusan.

> ⚠️ Contoh ini melihat **ke belakang** (pembelian yang sudah terjadi),
> sementara Decision Lab naskah 4 §27 melihat **ke depan** (pilihan yang belum
> diambil). Keduanya berguna, tetapi yang melihat ke belakang punya risiko
> khusus: menunjukkan bahwa pilihan yang **sudah** diambil ternyata lebih buruk
> tidak bisa diperbaiki lagi, hanya bisa disesali. Perlu aturan kapan sistem
> **tidak** menawarkannya.

---

## Pillar 7 — Simulation Engine

> Simulation berbeda dengan prediction.
>
> | | |
> |---|---|
> | **Prediction** | kemungkinan **terjadi** |
> | **Simulation** | apa yang mungkin terjadi **jika asumsi tertentu dipilih** |

```
Sleep
  ↓
Energy
  ↓
Workout
  ↓
Mood
  ↓
Productivity
```

> **Semua node memiliki confidence.**

---

> ⭐ **Rantai ini menjawab butir E-16 yang menggantung sejak naskah 1.**
> Arah `Sleep → Energy → Workout → Mood → Productivity` **sama persis** dengan
> Layer 8 naskah 3, dan **berbeda** dari naskah 1 (`Tidur → Mood →
> Produktivitas → Olahraga`) yang menempatkan Mood sebelum Workout.
>
> Sekarang **dua naskah memakai urutan yang sama, satu naskah memakai urutan
> lama** — dan yang dua adalah yang lebih baru. Ditambah *"semua node memiliki
> confidence"*, ini praktis menutup pertanyaan arah hipotesis awal.
> Lihat issue **#7**.
