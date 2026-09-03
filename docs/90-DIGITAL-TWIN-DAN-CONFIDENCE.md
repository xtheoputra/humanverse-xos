# 90 — §18–§19 Digital Twin & Confidence Layer

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18 — Digital Twin secara engineering

```
DigitalTwin
│
├── IdentityModel
├── BehaviorModel
├── PreferenceModel
├── GoalModel
├── StateModel
├── SkillModel
├── LifestyleModel
└── DecisionModel
```

Contohnya:

```yaml
User:
  energy_pattern:
      morning: high
      afternoon: medium
      night: low

  learning:
      preferred_time: night

  fashion:
      style: minimal
      colors: neutral

  behavior:
      gym_frequency: 3/week

  goal:
      improve_AI_skill
```

> **Digital Twin bukan berarti AI mengklaim mengetahui pikiran user.**
> Ia hanyalah **model probabilistik** dari data yang diberikan/diamati dan
> **harus memiliki confidence**.

> ⚠️ `SocialModel` (naskah 4) diganti `LifestyleModel` di sini. Delapan model
> tetap delapan, isinya bergeser. Lihat butir **E-34**.

---

## §19 — Confidence Layer

> **Ini saya anggap wajib.** AI harus mengetahui **seberapa yakin** ia terhadap
> sebuah kesimpulan.

```json
{
  "prediction": "User likely prefers dark outfits",
  "confidence": 0.87,
  "evidence_count": 34,
  "last_updated": "2026-09-01"
}
```

Sehingga:

| Confidence | Perilaku sistem |
|---|---|
| **High** | personalize strongly |
| **Medium** | personalize cautiously |
| **Low** | **ask user** |

> Ini mencegah AI membuat **asumsi berlebihan tentang manusia**.

---

> ⭐ **Bagian paling penting di naskah kelima.** Ini jawaban langsung untuk dua
> masalah lama sekaligus:
>
> - **B-15** — angka seperti `0.62` yang terlihat seperti fakta padahal
>   taksiran. Sekarang setiap taksiran wajib membawa `confidence` dan
>   `evidence_count`.
> - **B-1 cold start** — pengguna hari pertama punya `evidence_count: 0`, jadi
>   sistemnya **bertanya**, bukan menebak.
>
> Yang masih perlu ditetapkan: **ambang** untuk High/Medium/Low, dan cara
> menghitung `confidence` itu sendiri.
