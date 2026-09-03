# 60 — §21–§22 Wardrobe Intelligence & Trend Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keempat, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §21 — Wardrobe Intelligence

```
Wardrobe
│
├── Shirts
├── Pants
├── Shoes
├── Jackets
└── Accessories
```

Setiap item memiliki:

```
color
brand
category
material
season
style
usage_count
last_used
```

Kemudian AI bisa menemukan:

> *"Kamu memiliki 3 pakaian yang sangat mirip dan 7 item yang hampir tidak
> pernah dipakai."*

> Ini sangat powerful.

---

## §22 — Trend Engine

> Untuk fashion/trend, **jangan hanya scraping satu sumber.**

```
Public Sources
      ↓
Data Ingestion
      ↓
Normalization
      ↓
Entity Extraction
      ↓
Trend Detection
      ↓
Trend Scoring
      ↓
Personal Relevance
```

### Rumus

```
Trend Score =
    Growth
  + Velocity
  + Engagement
  + Recency
  + Cross-platform presence
```

```
Personal Trend Score = Trend Score × User Relevance
```

> Jadi **"trending" belum tentu berarti "cocok untuk kamu"**.

> ⚠️ Bobot tiap komponen dan definisi *User Relevance* belum ditulis. Sumber
> "Public Sources" juga masih butir terbuka **A-5** di berkas audit.
