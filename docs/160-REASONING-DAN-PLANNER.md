# 160 — §9.20–§9.23 Reasoning Engine, Hybrid Reasoning, Planner & Hierarchical Planning

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.20 — Layer 9: Reasoning Engine

> Tidak semua masalah harus menggunakan LLM reasoning panjang.

**Fast Path**

```
Rule · Lookup · Cache · Simple model
```

**Cognitive Path**

```
Retrieval · Graph · LLM · Planning · Simulation
```

**High-stakes Path**

```
Multiple checks · Policy · Risk · Human confirmation
```

---

> ⭐⭐ **Tiga jalur ini adalah §9.2 yang dijalankan — dan ia yang membuat pagu
> biaya mungkin ditepati.** Butir **B-2** dan **H-6** mencatat bahwa biaya
> inferensi berlipat dengan jumlah modul; *Fast Path* menjawabnya dengan cara
> yang paling langsung: sebagian besar permintaan **tidak memanggil LLM sama
> sekali**.
>
> Untuk V0 ini bukan optimasi melainkan kebutuhan: paket Free (Habit + Mood)
> harus dirancang supaya nyaris tidak memanggil model besar. *"Berapa rentetan
> habit saya?"* adalah `habit.streak` — sebuah pertanyaan Fast Path yang tidak
> perlu satu token pun.
>
> 🛑 Justru karena itu, **hilangnya `model-router/` dari pohon §9.38 adalah
> kehilangan yang nyata** — pemilih jalur inilah yang menjalankan tiga jalur di
> atas. Lihat **E-79** / [#69](../../issues/69).

> ⭐ **`High-stakes Path` menyambung langsung ke Fase 8**: `Policy · Risk ·
> Human confirmation` adalah risk gate [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> dan §8.17. Ini pertama kalinya sebuah naskah menyebut jalur keselamatan
> sebagai **mode reasoning**, bukan sebagai lapisan terpisah yang ditempel di
> akhir.

---

## §9.21 — Hybrid Reasoning Architecture

```
                  QUERY
                    │
                    ▼
             Intent Classifier
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Rule       RAG      Agent
          │         │         │
          └─────────┼─────────┘
                    ▼
               Reasoner
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Graph     Simulator   Tools
          │         │         │
          └─────────┼─────────┘
                    ▼
              Decision Layer
```

---

> ⚠️ **`Intent Classifier` memikul beban yang lebih berat daripada
> kelihatannya.** Ia yang memilih jalur — dan salah memilih ke Fast Path untuk
> pertanyaan berisiko berarti melewati `Policy · Risk · Human confirmation`
> sepenuhnya. Itu menjadikannya **komponen keselamatan**, bukan komponen
> perutean, dan ia layak diperlakukan begitu: kalau klasifikasi intent
> ber-`confidence` rendah, jalur bawaan harus yang **lebih ketat**, bukan yang
> lebih murah.
>
> Aturan itu belum ditulis, dan ia satu kalimat.

---

## §9.22 — Planner

> Reasoning menjawab *"Apa yang masuk akal?"*
> Planner menjawab *"Bagaimana kita mencapainya?"*

Contoh — goal **Become AI Engineer**:

```
Goal
 ↓
Skills
 ↓
Projects
 ↓
Courses
 ↓
Weekly schedule
 ↓
Daily tasks
 ↓
Feedback
```

---

## §9.23 — Hierarchical Planning

> Planner tidak membuat satu task besar.

```
Goal
 │
 ├── Milestone
 │     ├── Project
 │     │     ├── Task
 │     │     └── Task
 │     └── Habit
 │
 └── Milestone
```

Ini terhubung langsung dengan **Goal Intelligence** yang dibangun sebelumnya.

---

> ⭐ **Pohon ini cocok dengan skema V0 tanpa perubahan apa pun.**
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) sudah punya `goals`,
> `goal_milestones`, dan `habits`; `goals.parent_id` menampung sarangnya. Yang
> belum ada hanyalah **Project** dan **Task** sebagai entitas tersendiri — dan
> keduanya bukan V0.
>
> ⚠️ Perhatikan bahwa **Habit menggantung langsung di bawah Milestone**,
> sejajar dengan Project. Itu berarti sebuah habit bisa dimiliki milestone,
> sementara di V0 habit berdiri sendiri. Kalau hubungan itu dibangun, ia
> memberi jawaban untuk pertanyaan yang §9.11 ajukan lewat graf (*kebiasaan
> mana yang menggerakkan tujuan*) — **tanpa perlu graf sama sekali**, cukup
> satu kolom `habits.milestone_id`. Itu jalur yang jauh lebih murah untuk V0
> daripada menunggu Neo4j di V4.

> ⚠️ **Rencana yang dibuat mesin adalah tulisan ke data pengguna.** Di tangga
> risiko §8.16 itu jatuh di R1 (*"mengubah habit"*) setelah kalibrasi ulang —
> artinya planner boleh membuat, mengubah, dan mungkin menghapus milestone
> seseorang **tanpa satu pun konfirmasi**. Untuk rencana karier enam bulan itu
> berlebihan. Bertaut **E-67** / [#60](../../issues/60).
