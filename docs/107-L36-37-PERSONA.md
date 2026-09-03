# 107 — Layer 36–37: Synthetic User Simulator & Human Personas

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 36 — Synthetic User Simulator

> Ini salah satu **fitur paling menarik**. Kita membuat **"user virtual"**.

Persona:

```
Student
Office Worker
Gym Enthusiast
Freelancer
Traveler
```

Mereka digunakan untuk:

```
testing · UX · AI evaluation
```

> ## Bukan data pengguna sungguhan.

---

## Layer 37 — Human Personas

> Kita membuat **persona library**.

| Persona | Fokus |
|---|---|
| **Student** | Learning |
| **Young Professional** | Career |
| **Creator** | Productivity |
| **Athlete** | Fitness |
| **Minimalist** | Lifestyle |

> AI dapat **diuji pada setiap persona**.

---

> ⚠️ **Dua daftar persona berbeda di dua lapisan berdampingan.** Layer 36:
> Student · Office Worker · Gym Enthusiast · Freelancer · Traveler.
> Layer 37: Student · Young Professional · Creator · Athlete · Minimalist.
> **Hanya *Student* yang muncul di keduanya.**
>
> Kemungkinan besar keduanya memang bermaksud sama (*Office Worker* ≈ *Young
> Professional*, *Gym Enthusiast* ≈ *Athlete*), tetapi *Freelancer*, *Traveler*,
> *Creator*, dan *Minimalist* tidak berpasangan. Satu daftar harus dipilih —
> ini akan jadi nama berkas uji. Lihat butir **E-48**.
>
> ⭐ Kalimat **"Bukan data pengguna sungguhan"** layak dipertahankan sebagai
> aturan keras: persona sintetis adalah satu-satunya cara menguji AI perilaku
> tanpa memakai data tidur, uang, dan jurnal orang untuk mengembangkan produk.
