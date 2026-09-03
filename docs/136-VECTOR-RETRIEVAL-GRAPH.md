# 136 — §7.10–§7.13 Vector Platform, Hybrid Retrieval & Knowledge Graph

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.10 — Vector Data Platform

Untuk: **Journal · Memory · Preference · Outfit · Goal · Knowledge**

```
Document → Chunking → Embedding → Vector DB
```

```json
{
  "id": "mem_123",
  "embedding": "...",
  "metadata": {
    "user_id": "user_123",
    "type": "journal",
    "created_at": "2026-09-03"
  }
}
```

> ⚠️ **`Knowledge` masuk daftar yang sama dengan `Journal` dan `Memory`.**
> Layer 40 naskah 7 memisahkan keduanya dengan tegas (*Memory = pengalaman
> pengguna, Knowledge = pengetahuan dunia*), dan konsekuensinya nyata:
> pengetahuan dunia **tidak** ikut terhapus saat akun dihapus dan **tidak**
> butuh izin per pengguna.
>
> Metadata di atas juga memaksa setiap titik punya `user_id` — yang tidak masuk
> akal untuk pengetahuan dunia. Keduanya perlu **koleksi terpisah**. Bertaut
> butir **E-49** / issue #41.

---

## §7.11 — Hybrid Retrieval

> **Jangan hanya menggunakan vector search.**

```
Keyword Search + Vector Search + Graph Search + Metadata Filtering
        ↓
    Reranker
        ↓
 Relevant Context
        ↓
       LLM
```

> Ini jauh lebih kuat daripada sekadar `query → vector DB → LLM`.

> ⭐ **Ini salah satu bagian paling matang di sebelas naskah.** Pencarian
> vektor sendirian gagal justru pada pertanyaan yang paling sering ditanyakan
> orang ke produk ini — *"kapan terakhir saya memakai blazer hitam?"* butuh
> **kata kunci** dan **tanggal**, bukan kemiripan makna.
>
> ⭐ **`Metadata Filtering` adalah tempat izin ditegakkan.** Saring scope
> **sebelum** reranker, bukan sesudah — kalau tidak, dokumen yang tidak boleh
> dibaca agent tetap ikut diperingkat dan bisa bocor lewat urutan hasilnya.

---

## §7.12 — Knowledge Graph Infrastructure

```
User
 ├── prefers   → Minimal Fashion
 ├── owns      → Black Oversized Shirt
 ├── works_at  → Company
 └── has_goal  → Become AI Engineer
```

Menghubungkan: **Person · Goal · Skill · Habit · Lifestyle · Knowledge**

> ⚠️ **Daftar relasi kelima.** Naskah 2: `improves`, `causes`, `influences`,
> `blocks`, `predicts`. Naskah 3: `hasHabit`, `prefersStyle`, … Naskah 9:
> `improves`, `supports`, `blocks`, `related_to`, `frequently_used`. Di sini:
> `prefers`, `owns`, `works_at`, `has_goal`.
>
> Yang di sini semuanya **struktural** (kepemilikan dan keterkaitan), bukan
> kausal — konsisten dengan arah perbaikan naskah 9. Tetapi `works_at → Company`
> adalah relasi baru yang menyentuh data pekerjaan, dan itu bertaut ke **C-12**
> (*Company Wellness*).

---

## §7.13 — Knowledge Graph + Vector DB

| | Menjawab |
|---|---|
| **Vector** | *"Apa yang mirip?"* |
| **Graph** | *"Apa yang berhubungan?"* |

Contoh: *"Carikan rekomendasi belajar AI yang sesuai dengan goal saya."*

```
Vector →  AI learning materials
Graph  →  User → Goal → Skill Gap → Learning Path
          lalu keduanya digabung
```

> ⭐ **Kalimat pembeda dua baris itu adalah penjelasan terbaik tentang kenapa
> proyek ini butuh keduanya** — dan sekaligus alasan kenapa butir **#7** (model
> graf) tetap penting meski tidak menghalangi V0.
>
> 🔧 **Koreksi catatan saya sendiri:** di issue #7 saya menulis graph baru
> relevan di **V2**. Menurut §7.0 naskah ini, Knowledge Graph ada di **V4**.
> Kesimpulannya tidak berubah (tidak menghalangi V0), tapi jaraknya lebih jauh
> daripada yang saya tulis.
