# 106 — Layer 33–35: Feature Flag, Experimentation & AI Evaluation Lab

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 33 — Feature Flag Platform

> **Jangan langsung merilis fitur ke semua orang.**

```
Feature Flags

AI_COACH_V2
FASHION_AGENT
VOICE_MODE
DIGITAL_TWIN
```

Keuntungan:

```
A/B testing · Rollback cepat · Eksperimen aman
```

---

## Layer 34 — Experimentation Platform

> Setiap perubahan bisa diuji.

```
Reminder A   vs   Reminder B
```

Ukur:

```
completion rate · retention · engagement
```

> ## Jangan mengoptimalkan manipulasi; optimalkan pengalaman pengguna.

> ⭐ Kalimat itu penting dan jarang ditulis orang. *Retention* dan *engagement*
> adalah dua metrik yang paling mudah dinaikkan dengan cara yang merugikan
> pengguna; menyebutkan batasnya di baris yang sama dengan metriknya adalah
> pilihan yang benar.
>
> ⚠️ Tetapi batas itu belum punya bentuk yang bisa diperiksa. Yang membuatnya
> nyata: **metrik penjaga** (*guardrail metric*) yang ikut diukur di setiap
> eksperimen dan bisa membatalkannya — misalnya notifikasi per hari,
> waktu-di-aplikasi yang **tidak** boleh naik, dan rasio pengguna yang mematikan
> pengingat.

---

## Layer 35 — AI Evaluation Laboratory

> Setiap agent memiliki **test suite**.

Contoh **FashionAgent**:

```
Input:
  Meeting formal
  Hot weather

Expected:
  Formal outfit
  Breathable fabric
  Dark shoes
```

> Semua agent memiliki **benchmark**.

> ⚠️ Ini **lapisan evaluasi ketiga** di proyek yang sama: Layer 14 (naskah 3,
> terpotong), §23 Agent Evaluation (naskah 5), dan Layer 35 di sini. Ketiganya
> perlu disatukan jadi satu tempat. Lihat butir **E-47**.
>
> ⚠️ Contoh di atas juga memperlihatkan masalah lama **B-10**: *"Formal outfit"*
> dan *"Dark shoes"* tidak punya kebenaran acuan objektif, sementara
> *"Breathable fabric"* untuk cuaca panas punya. Test suite hanya bisa dibuat
> untuk yang jenis kedua.
