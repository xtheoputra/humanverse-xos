# 178 — §11.8–§11.11 Planning Engine, Hierarchical Planning, Plan Representation & Verification

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.8 — Agent Planning Engine

> Planner adalah **jantung agency**.

```
Input:   Goal + Context + Constraints + Resources + Preferences + Time
Output:  Plan
```

Contoh — *"Saya ingin belajar AI 2 jam malam ini."*

```
Goal → Available Time → Current Energy → Learning History
→ Skill Level → Select Topic → Create Session → Schedule
```

```
19:30–19:45  Review
19:45–20:30  Study
20:30–20:40  Break
20:40–21:20  Practice
21:20–21:30  Review
```

---

> ⭐⭐ **`Current Energy` sebagai masukan perencanaan adalah tempat pertama di
> lima belas naskah di mana Human State benar-benar dipakai untuk sesuatu.**
> Sepuluh field §9.5 selama ini disimpan, ditampilkan, dan diberi
> `confidence` — tapi tidak pernah **mengubah keputusan**. Di sini `energy`
> menentukan panjang sesi.
>
> ⚠️ Dan itu langsung mengaktifkan **B-15**: kalau `energy: 0.62` (taksiran,
> `confidence: 0.78`) memendekkan sesi belajar seseorang, taksiran itu berhenti
> jadi angka di layar dan mulai punya akibat. Aturan §9.33 berlaku penuh:
> **di bawah ambang, sistem tidak boleh memakainya diam-diam** — ia harus
> bertanya atau memakai bawaan.

> ⭐ **Rencana 2 jam berisi 2× Review dan 1× Break** — bukan 120 menit belajar
> lurus. Itu tanda planner yang memodelkan manusia, bukan mengisi kalender.

> ⚠️ **Menjumlahkan lima langkah: 15+45+10+40+10 = 120 menit ✅** — tepat 2 jam
> seperti diminta. Diperiksa karena empat belas naskah punya riwayat angka yang
> tidak berjumlah.

---

## §11.9 — Hierarchical Planning

```
Goal → Objective → Milestone → Project → Task → Subtask → Action
```

Contoh:

```
Goal:       Become AI Engineer
Objective:  Build ML capability
Milestone:  Complete ML fundamentals
Project:    Build recommendation engine
Tasks:      dataset · preprocessing · feature engineering
            model · evaluation · deployment
```

---

> ⚠️ **Tujuh tingkat di sini, lima tingkat di §9.23** (*Goal → Milestone →
> Project → Task*, dengan Habit menggantung di bawah Milestone). Yang baru:
> **Objective** di atas Milestone, dan **Subtask** + **Action** di bawah Task.
>
> Dan **`Habit` hilang** dari pohon ini — padahal §9.23 menempatkannya sejajar
> Project, dan itu yang saya catat sebagai jalur murah untuk menjawab
> *"kebiasaan mana yang menggerakkan tujuan saya"* dengan satu kolom
> `habits.milestone_id`, tanpa menunggu Neo4j di V4.
>
> Tujuh tingkat untuk V0 terlalu dalam: [`../spec/01`](../spec/01-DATABASE-SCHEMA.md)
> punya `goals` (dengan `parent_id`) dan `goal_milestones`, dan itu sudah cukup
> untuk empat tingkat pertama. Yang perlu diputuskan bukan berapa tingkat yang
> **benar**, melainkan berapa yang **dibangun sekarang**.

---

## §11.10 — Plan Representation

```json
{
  "plan_id": "plan_001",
  "goal": "learn_ai",
  "constraints": { "time": "2h", "budget": 0 },
  "steps": [
    { "id": "step_1", "action": "review", "duration": 15 },
    { "id": "step_2", "action": "study",  "duration": 45 }
  ]
}
```

> Plan harus: **versioned · traceable · editable · cancelable · resumable**

---

> ⭐⭐ **`editable` adalah kata yang selama ini hilang di tempat lain.** Butir
> **E-74** ([#64](../../issues/64)) melacak `Edit` yang hilang dari Privacy
> Center; di sini rencana **wajib** bisa disunting pengguna. Itu preseden yang
> tepat, dan sebaiknya dipakai sebagai argumen untuk mengembalikan `Edit` di
> tempat lain: kalau rencana boleh disunting, kesimpulan tentang diri seseorang
> semestinya juga.
>
> `cancelable` dan `resumable` juga menjawab separuh **G-8**
> ([#65](../../issues/65)) — *Human Override* yang tidak datang di Fase 8.
> Membatalkan rencana yang sedang berjalan adalah persis yang hilang antara
> §8.17 (mencegah sebelum) dan §8.35 (menghentikan semua).

> ⚠️ **`budget: 0` di `constraints`** — bagus, dan konsisten dengan
> `purchases: { amount_limit: 0 }` §11.17. Yang perlu ditetapkan: apakah `0`
> berarti *tidak boleh mengeluarkan uang* atau *belum ditetapkan*. Dua arti,
> satu nilai.

---

## §11.11 — Plan Verification

> Agent **tidak boleh** langsung menjalankan plan hasil LLM.

```
Generated Plan → Schema Validation → Constraint Check → Permission Check
→ Risk Check → Policy Check → Plan Verification → Execution
```

> Ini sangat penting untuk mencegah **hallucinated actions**.

---

> ⭐⭐⭐ **Ini bagian terpenting di seluruh naskah, dan ia menutup lubang yang
> belum pernah dinyatakan dengan jelas.**
>
> Sampai sekarang seluruh rantai keselamatan memeriksa **aksi**: risk gate
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md), §8.21 tool security, §9.29
> `POLICY_CHECK`. Tidak satu pun memeriksa **rencana**.
>
> Bedanya nyata. Sebuah rencana adalah **banyak aksi yang masing-masing lolos**
> — dan tetap salah sebagai keseluruhan: sepuluh aksi R1 yang setiap satunya
> tak berbahaya bisa menjadi rencana yang menghabiskan seluruh malam seseorang.
> Gerbang per-aksi tidak bisa melihat itu; `Constraint Check` di sini bisa.
>
> Dan *"tidak boleh langsung menjalankan plan hasil LLM"* menyatakan hal yang
> sama untuk sisi lain: model yang mengarang langkah yang tidak mungkin
> dijalankan (`tool` yang tidak ada, waktu yang bertabrakan) dihentikan oleh
> `Schema Validation` sebelum satu pun aksi dicoba.

> ⚠️ **Tetapi urutannya menaruh `Permission Check` dan `Risk Check` di tingkat
> rencana, sementara §11.14 Action Gateway memeriksa keduanya lagi di tingkat
> aksi.** Itu benar dan disengaja (rencana bisa berumur panjang; izin bisa
> dicabut di tengah jalan) — tapi harus dinyatakan, karena kalau tidak,
> seseorang akan menganggap salah satunya berlebihan dan membuangnya. Aturannya:
> **pemeriksaan di tingkat rencana adalah penyaring awal; yang mengikat adalah
> pemeriksaan di tingkat aksi, saat aksi itu dijalankan.**

> ⚠️ **`Plan Verification` sebagai langkah terpisah setelah lima pemeriksaan
> tidak dijelaskan isinya.** Kalau ia berarti *"apakah rencana ini benar-benar
> mencapai goal-nya"*, itu langkah yang paling sulit dan paling berharga di
> seluruh daftar — dan ia butuh kriteria sukses yang §11.41 sebut sebagai
> `success criteria` tapi tidak pernah didefinisikan.
