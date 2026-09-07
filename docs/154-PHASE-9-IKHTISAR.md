# 154 — Phase 9: Human Intelligence & Cognitive Architecture (ikhtisar naskah ketigabelas)

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Penomoran yang dipakai di berkas rapi

Naskah ketigabelas menomori bagiannya **1–41** — nomor yang sudah dipakai
naskah 4, 5, dan 12. Berkas rapi memakai awalan fase seperti dua naskah
sebelumnya: **`§9.1`–`§9.41`**. Ini keputusan penulisan, bukan kata pemilik.

---

## Posisi pemilik

> Fase 9 adalah titik di mana seluruh fondasi sebelumnya mulai **disatukan
> menjadi "otak"** HumanVerse X.

| Fase | Memberi |
|---|---|
| 5 | Research Intelligence |
| 6 | Developer Ecosystem |
| 7 | Data & AI Infrastructure |
| 8 | Safety, Security & Privacy |

> Sekarang kita bangun **HumanVerse Cognitive Architecture** — sistem yang
> mengubah data manusia menjadi *context, memory, understanding, reasoning,
> prediction, decision,* dan *action*.

---

## §9.1 — Visi Fase 9: cognitive loop

```
                    HUMAN
                      │
                      ▼
              ┌───────────────┐
              │  OBSERVATION  │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    CONTEXT    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   MEMORY      │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ UNDERSTANDING │
              └───────┬───────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
       ┌───────────┐     ┌───────────┐
       │ REASONING │     │ PREDICTION│
       └─────┬─────┘     └─────┬─────┘
             │                 │
             └────────┬────────┘
                      ▼
              ┌───────────────┐
              │   DECISION    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ RECOMMENDATION│
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    ACTION     │
              └───────┬───────┘
                      │
                      ▼
                 FEEDBACK
                      │
                      └──────────► LEARNING
```

> Ini adalah **cognitive loop** HumanVerse.

---

> ⭐ **Ini janji pembuka yang akhirnya punya bentuk.** Slogan repo sejak naskah
> 1 adalah `Observe → Understand → Reason → Predict → Recommend → Act → Learn`
> — tujuh kata yang belum pernah punya komponen. Loop di atas menambahkan
> **Context**, **Memory**, **Decision**, dan **Feedback** di antaranya, dan
> memisahkan *Decision* dari *Recommendation* (lihat §9.24).

---

## §9.2 — Prinsip fundamental

> Kita **jangan** membuat satu LLM raksasa yang melakukan semuanya.

Sebaliknya:

```
LLM
+
Memory
+
Knowledge
+
Context
+
Behavior Models
+
World Model
+
Tools
+
Policies
+
User Preferences
+
Feedback
```

menjadi satu sistem kognitif. Dengan kata lain:

> ## LLM bukan otak tunggal HumanVerse. LLM adalah salah satu komponen dalam cognitive architecture.

---

> ⭐⭐ **Ini prinsip paling berkonsekuensi di seluruh naskah, dan ia menyentuh
> biaya.** Kalau LLM hanya salah satu komponen, sebagian besar permintaan
> **tidak perlu memanggilnya sama sekali** — dan itulah yang membuat pagu biaya
> (**B-2**, **H-6**) bisa ditepati. §9.20 menurunkannya jadi tiga jalur
> (*Fast Path* tanpa LLM · *Cognitive Path* · *High-stakes Path*).
>
> ⚠️ Justru karena itu, hilangnya **`model-router/`** dari pohon §9.38 janggal —
> ia komponen yang menjalankan prinsip ini. Lihat **E-79**.

---

## §9.3 — HumanVerse Cognitive Stack (12 layer)

```
L12  ┌────────────────────────────┐
     │      HUMAN INTERFACE       │
L11  ├────────────────────────────┤
     │     ACTION & AGENCY        │
L10  ├────────────────────────────┤
     │ DECISION & RECOMMENDATION  │
L9   ├────────────────────────────┤
     │ REASONING & PLANNING       │
L8   ├────────────────────────────┤
     │ PREDICTION & SIMULATION    │
L7   ├────────────────────────────┤
     │ UNDERSTANDING ENGINE       │
L6   ├────────────────────────────┤
     │ KNOWLEDGE & WORLD MODEL    │
L5   ├────────────────────────────┤
     │ MEMORY SYSTEM              │
L4   ├────────────────────────────┤
     │ CONTEXT ENGINE              │
L3   ├────────────────────────────┤
     │ STATE & REPRESENTATION     │
L2   ├────────────────────────────┤
     │ BEHAVIOR & PREFERENCE      │
L1   └────────────────────────────┘
              DATA FOUNDATION
```

---

> 🛑 **Tumpukan ini tidak cocok dengan judul bagiannya sendiri — melesetnya
> tepat satu.** Dihitung dari gambar: L1 *Data Foundation* · L2 *Behavior &
> Preference* · L3 *State* · L4 *Context* · L5 *Memory* · L6 *Knowledge & World
> Model*. Tetapi judul bagiannya menulis:
>
> | Judul bagian | Gambar §9.3 |
> |---|---|
> | §9.4 **"Layer 1"** — Behavior & Preference | **L2** |
> | §9.5 **"Layer 2"** — Human State | **L3** |
> | §9.6 **"Layer 3"** — Context Engine | **L4** |
> | §9.7 **"Layer 4"** — Memory System | **L5** |
> | §9.10 **"Layer 5"** — Knowledge System | **L6** (digabung) |
> | §9.12 **"Layer 6"** — World Model | **L6** (digabung) |
> | §9.15 "Layer 7" — Understanding | L7 ✅ |
> | §9.18 "Layer 8" — Prediction | L8 ✅ |
> | §9.20 "Layer 9" — Reasoning | L9 ✅ |
> | §9.24 "Layer 10" — Decision | L10 ✅ |
> | §9.26 "Layer 11" — Agency | L11 ✅ |
>
> Tujuh sampai sebelas cocok; satu sampai enam meleset satu karena gambar
> memberi **Data Foundation** tempat di L1 sementara judul mulai berhitung dari
> *Behavior*. Dan **tidak ada bagian "Layer 12 — Human Interface"** sama
> sekali. Lihat **G-10**.

> ⚠️ **L9–L12 bertabrakan langsung dengan Layer 9–12 naskah 3** — dan kali ini
> di rentang yang sama persis, bukan rentang berbeda:
>
> | Nomor | Naskah 3 | Naskah 13 |
> |---|---|---|
> | **L9** | Memory Hierarchy | Reasoning & Planning |
> | **L10** | MCP Tool Ecosystem | Decision & Recommendation |
> | **L11** | Workflow Engine | Action & Agency |
> | **L12** | Decision Engine | Human Interface |
>
> Perhatikan barisnya: *Decision Engine* naskah 3 adalah **L12**, sedangkan
> *Decision* naskah 13 adalah **L10**. Dua dokumen yang sama-sama menyebut
> "Layer 12" berarti hal yang berbeda, dan keduanya membahas keputusan.
> Ini kali **keempat** penomoran Layer dimulai ulang (**G-7**). Lihat
> **E-78**.

---

## Yang perlu diketahui sebelum membaca sepuluh berkas berikutnya

**Fase 9 berbeda sifatnya dari Fase 8.** Fase 8 menambahkan pekerjaan baru di
atas V0 (20 tabel, 8 sprint — **A-25**). Fase 9 sebagian besar **bukan
pekerjaan tambahan, melainkan arsitektur dari pekerjaan yang sudah
dijadwalkan**: *Context Engine*, *Memory*, dan *Recommendation* sudah ada di
dalam 12 fitur V0, dan Sprint 3–5 V0 memang membangunnya.

Artinya naskah ini lebih tepat dibaca sebagai **cara membangun V0**, bukan
sebagai fase kesembilan yang menunggu giliran. Itu mengubah jawaban
[#58](../../issues/58).
