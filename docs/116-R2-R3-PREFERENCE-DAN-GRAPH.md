# 116 — Pillar 2–3: Preference Learning & Graph Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pillar 2 — Preference Learning Engine

> **Preferensi manusia berubah.**

Jangan simpan:

```
favorite_color = black
```

Lebih baik:

```json
{
  "black": {
    "score": 0.91,
    "confidence": 0.84,
    "last_updated": "2026-09-03"
  }
}
```

### Preference Graph

```
User → Fashion → Minimal → Oversized → Dark Colors
```

### Domain

```
Fashion · Food · Learning · Music · Travel · Productivity
```

### Learning Loop

```
Recommendation → User Choice → Feedback → Preference Update
```

> **Satu pilihan tidak langsung mengubah profil; gunakan akumulasi perilaku.**

> ⭐ Bentuk `{score, confidence, last_updated}` **persis sama** dengan
> Confidence Layer (naskah 5 §19) dan langsung muat di tabel `memories`
> (`kind='preference'`, `confidence`, `evidence_count`, `last_reinforced_at`)
> di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md). Tidak butuh tabel baru.
>
> ⚠️ **Music** adalah domain baru — tidak pernah muncul di delapan naskah
> sebelumnya, dan tidak punya modul, agent, maupun tool.

---

## Pillar 3 — Human Knowledge Graph Intelligence

> Sebelumnya kita membuat graph. Sekarang kita membuat **Graph Intelligence**.

### Graph Structure

```
User
│
├── Goal      ├── Outfit    ├── Friend
├── Habit     ├── Food      ├── Place
├── Skill                   └── Activity
```

### Relationship

```
improves · supports · blocks · related_to · frequently_used
```

### Intelligent Query

> *"Habit apa yang paling sering muncul sebelum mood membaik?"*
>
> Graph dapat membantu menemukan hubungan **berdasarkan data yang tersedia**.

---

> ⭐ **`causes`, `influences`, dan `predicts` DIBUANG** dari daftar relasi
> naskah 2, diganti `supports`, `related_to`, dan `frequently_used`. Itu
> perbaikan nyata dan sejalan dengan naskah 4 §7 (*jangan menulis kausal untuk
> data observasional*). `frequently_used` bahkan jujur menyebut dirinya
> frekuensi, bukan sebab.
>
> ⚠️ Tetapi ini **daftar node keempat dan daftar relasi keempat**. Node: naskah 2
> punya 10 (User, Habit, Mood, Sleep, Workout, Outfit, Meeting, Friend, Money,
> Learning); di sini **Mood, Sleep, Workout, Meeting, Money, Learning hilang**
> dan **Goal, Skill, Food, Place, Activity muncul**.
>
> Ganjilnya, *Mood* justru dipakai di contoh query di halaman yang sama —
> padahal ia bukan node. Lihat butir **E-55**.
