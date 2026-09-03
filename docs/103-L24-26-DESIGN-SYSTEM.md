# 103 — Layer 24–26: Design System, Component Library & Motion

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 24 — Design System (HumanVerse Design Language)

> Ini adalah **"bahasa visual"** seluruh aplikasi.

### Design Principles

```
Calm Intelligence
Minimal Cognitive Load
Human First
Adaptive Personalization
Accessible by Default
```

### Design Tokens

```
color.primary      spacing.4       radius.md      font.heading
color.secondary    spacing.8       radius.lg      font.body
color.success      spacing.16      radius.xl      font.caption
color.warning
color.error
```

> **Semua UI menggunakan token.**

> ⭐ *Calm Intelligence* dan *Minimal Cognitive Load* adalah pasangan yang
> tepat untuk produk yang menolak satu angka Life Score (naskah 4 §28) —
> prinsip visualnya sejalan dengan prinsip produknya.

---

## Layer 25 — Component Library

> Kita buat **reusable component**.

```
Button          Habit Card       AI Chat Bubble
Card            Mood Card        Outfit Card
Progress Ring   Insight Card     Goal Card
                                 Timeline
```

Setiap komponen memiliki:

```
variant · state · accessibility · animation
```

> ⚠️ Dari 10 komponen ini, **Outfit Card** milik V2 (Fashion). Sembilan
> sisanya relevan untuk V0/V1.

---

## Layer 26 — Motion System

> HumanVerse harus **terasa hidup**. **Animation bukan dekorasi.**

| Event | Animation |
|---|---|
| Habit completed | **Ripple** |
| AI insight | **Glow** |
| Goal achieved | **Confetti** |
| Card expand | **Spring** |

> Gunakan **durasi konsisten**.

> ⚠️ Durasi konsistennya **belum ditetapkan angkanya**, padahal itu satu-satunya
> instruksi yang bisa dilanggar. Token `motion.fast/base/slow` layak masuk ke
> daftar Design Token di Layer 24.
>
> ⚠️ *Accessible by Default* (Layer 24) menuntut animasi menghormati
> `prefers-reduced-motion` — belum disebut. Untuk pengguna yang sensitif
> terhadap gerakan, Confetti bukan hal sepele.
