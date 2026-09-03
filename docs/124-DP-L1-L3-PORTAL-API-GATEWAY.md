# 124 — DP-L1–L3: Developer Portal, API Platform & Gateway

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## DP-L1 — Developer Portal

```
portal/
├── dashboard/   ├── agents/     ├── billing/
├── docs/        ├── plugins/    └── support/
├── api/         ├── analytics/
├── sdk/
```

Developer melihat: **API usage · Agent installs · Error rate · Revenue ·
Webhook status**.

| Metric | Value |
|---|---|
| API Calls | 120K |
| Active Users | 2.3K |
| Installed Agents | 580 |
| Revenue | Rp… |

---

## DP-L2 — HumanVerse API Platform

> Semua fitur HumanVerse dapat diakses melalui API.

| Gaya | Untuk |
|---|---|
| **REST** | resource utama |
| **Webhook** | event |
| **GraphQL** | hanya bila benar-benar diperlukan |

```
GET  /v1/profile
GET  /v1/habits
GET  /v1/goals
POST /v1/journal
GET  /v1/wardrobe
POST /v1/outfits/recommend
```

Semua API memiliki:

```
OpenAPI Specification · Versioning · Authentication
Rate Limiting · Permission Scope
```

> ⭐ **\"GraphQL hanya bila benar-benar diperlukan\"** adalah penahanan diri yang
> tepat. GraphQL di atas data pribadi berlapis izin membuat penegakan scope
> jauh lebih sulit daripada REST, karena satu query bisa menyentuh banyak
> sumber sekaligus.
>
> ℹ️ Format `/v1/<resource>` **cocok dengan Layer 22 naskah 7**
> (`/v1/fashion/outfits`). Dua naskah sepakat; spesifikasi V0 di
> [`../spec/04`](../spec/04-API-CONTRACTS.md) yang memakai `/api/v1/...`
> adalah yang menyimpang dan perlu diselaraskan. Bertaut **E-43** / issue #38.

---

## DP-L3 — API Gateway

Bertanggung jawab atas:

```
Authentication · Authorization · Rate Limit
Logging · Request Validation · API Versioning
```

```
Developer
    ↓
API Gateway
    ↓
Permission Check
    ↓
Service
    ↓
Response
```

> ⭐ **Permission Check berdiri sebagai langkah tersendiri setelah
> Authorization**, bukan digabung. Itu benar untuk produk ini: *authorization*
> menjawab \"aplikasi ini boleh memakai API\", *permission check* menjawab
> \"pengguna **ini** mengizinkan aplikasi itu menyentuh **scope ini**\". Dua
> pertanyaan berbeda, dan yang kedua yang menjaga janji kendali pengguna.
