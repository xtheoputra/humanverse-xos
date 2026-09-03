# 119 — Pillar 8–9: Human Embedding System & Personal Representation Layer

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pillar 8 — Human Embedding System

| Embedding | Fungsi |
|---|---|
| **Journal** | semantic search |
| **Preference** | personalization |
| **Outfit** | fashion |
| **Goal** | planning |
| **Memory** | retrieval |

### Pipeline

```
Text → Embedding Model → Vector DB → Semantic Search
```

> ℹ️ Kelima jenis ini cocok dengan koleksi Qdrant di naskah 5 §5
> (`journal_embeddings`, `preference_embeddings`, `fashion_embeddings`,
> `episodic_memory`, `semantic_memory`) — hanya `goal` yang belum punya
> koleksi. Konsisten, bukan tabrakan.
>
> ⚠️ Pipeline-nya hanya menerima **Text**. *Outfit embedding* untuk Vision Mode
> (Layer 28) berasal dari **gambar**, bukan teks. Jalur multimodalnya belum ada.

---

## Pillar 9 — Personal Representation Layer ⭐

> **Daripada satu skor**, gunakan **representasi multidimensi**.

```
Learning · Career · Health · Recovery
Lifestyle · Social · Finance
```

Setiap dimensi memiliki:

```
confidence · trend · evidence
```

---

> ⭐ **Ini kandidat jawaban terkuat untuk pertanyaan yang menggantung sejak
> naskah 1 (issue #2): model angka pengguna yang mana yang dipakai.**
>
> Bandingkan dengan Human Dashboard naskah 4 §28:
>
> | Human Dashboard (naskah 4) | Personal Representation (naskah 9) |
> |---|---|
> | Health · Learning · Finance · Social · Career · Recovery | Health · Learning · Finance · Social · Career · Recovery |
> | **Discipline** | **Lifestyle** |
> | — | + `confidence`, `trend`, `evidence` per dimensi |
>
> **Enam dari tujuh dimensinya identik.** Bedanya hanya satu butir
> (*Discipline* ↔ *Lifestyle*), dan versi baru menambahkan tepat apa yang
> selama ini kurang: **confidence, trend, dan evidence per dimensi**.
>
> Bentuknya juga langsung muat di kolom yang sudah dirancang —
> `human_states.metrics jsonb` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md)
> menyimpan `{value, confidence, evidence_count}` per metrik; tinggal
> menambahkan `trend`.
>
> Yang tersisa untuk diputuskan hanya **dua hal kecil**: *Discipline* atau
> *Lifestyle* (atau keduanya, jadi 8 dimensi), dan bagaimana hubungannya dengan
> **HumanState** (energy, focus, motivation, stress, …) — yang menurut saya
> memang berbeda dan harus tetap terpisah: HumanState adalah **keadaan hari
> ini**, Personal Representation adalah **kecenderungan jangka panjang**.
>
> Lihat butir **E-56** dan issue **#2**.
