# 82 — §3 Domain Architecture

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Sepuluh bounded context utama

| Domain | Fungsi |
|---|---|
| **Identity** | account, authentication, consent |
| **Human Profile** | identitas, preferensi, personal attributes |
| **Behavior** | aktivitas dan pola perilaku |
| **Goals** | goal, milestone, project, habit |
| **Lifestyle** | fashion, grooming, food, travel |
| **Health** | sleep, workout, nutrition, wellness |
| **Career** | career, skills, projects |
| **Learning** | courses, knowledge, learning progress |
| **Social** | relationship, social activities |
| **Intelligence** | AI, memory, prediction, recommendation |

---

## Domain infrastruktur

```
Platform
├── Agent
├── Event
├── Notification
├── Search
├── Analytics
├── Security
├── Observability
└── Billing
```

> ⚠️ **Billing muncul pertama kali di sini** — tidak pernah ada di empat naskah
> sebelumnya, dan tidak punya pasangan di tangga harga naskah 1. Lihat butir
> **A-6**.
>
> ⚠️ **Health dan Lifestyle adalah domain di sini**, tetapi **tidak punya agent**
> di daftar §12. Lihat butir **E-35**.
