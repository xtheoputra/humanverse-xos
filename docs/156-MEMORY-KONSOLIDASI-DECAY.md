# 156 — §9.7–§9.9 Cognitive Memory, Consolidation & Decay

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.7 — Layer 4: Memory System

```
                 MEMORY
                    │
     ┌──────────────┼──────────────┐
     │              │              │
 Working        Episodic       Semantic
 Memory         Memory         Memory
     │              │              │
     ├──────────────┼──────────────┤
     │              │              │
Procedural      Behavioral     Preference
     │              │              │
     └──────────────┼──────────────┘
                    │
              Memory Manager
```

Tetapi ada satu hal penting:

> ## Memory ≠ database.

Database menyimpan **fakta**. Memory harus menyimpan:

```
what happened
when
context
importance
source
confidence
outcome
relationship
```

---

> ⭐⭐ **Enam jenis ini IDENTIK dengan naskah 5 §17 — dan itu menutup E-39 /
> [#33](../../issues/33).** Working · Episodic · Semantic · Procedural ·
> Behavioral · Preference: himpunan yang sama persis, dalam dua naskah yang
> terpisah delapan naskah. Setelah lima hitungan berbeda (3 / 5 / 7 / nama
> scope / 6), ini pertama kalinya sebuah daftar memory **diulang tanpa
> berubah**.
>
> Dan naskah ini memberi apa yang sebenarnya ditanyakan issue itu — **kolomnya**:
>
> | Yang dituntut §9.7 | Kolom |
> |---|---|
> | what happened | `content` |
> | when | `occurred_at` |
> | context | `context jsonb` |
> | importance | `importance` |
> | source | `source` |
> | confidence | `confidence` |
> | outcome | `outcome` |
> | relationship | tautan ke graf |
>
> ⚠️ Dari delapan itu, **`importance`, `outcome`, dan `relationship` belum ada**
> di tabel `memories` [`../spec/01`](../spec/01-DATABASE-SCHEMA.md).
> `importance` yang paling menentukan — ia yang dipakai §9.8 untuk memilih apa
> yang naik ke long-term.

> ⭐ **Jawaban lengkap untuk #33: tiga sumbu, bukan tiga saingan.**
>
> ```
> kind   → 6 jenis di atas                    (bagaimana diambil)
> scope  → nama seperti 'career', 'wardrobe'  (siapa boleh membaca; §9.30, §8.14)
> tier   → Raw/Episode/Summary/Chapter/Identity (naskah 9 — seberapa dipadatkan)
> ```
>
> Ketiganya tegak lurus. Sebuah memori punya jenis **dan** scope **dan**
> tingkat kompresi. Selama ini ketiganya dikira saling menggantikan.

---

## §9.8 — Memory Consolidation

> Seperti manusia, tidak semua pengalaman harus dipertahankan dengan bobot
> sama.

```
Raw Events
    ↓
Short-term Memory
    ↓
Importance Scoring
    ↓
Consolidation
    ↓
Long-term Memory
```

Contoh — user membeli kopi **sekali**. Tidak perlu menjadi:

```
"User selalu suka kopi X."
```

Tetapi setelah **20 kali**:

```
Repeated behavior + Positive feedback + Context consistency
      ↓
Preference confidence ↑
```

---

> ⭐⭐ **Ini mekanisme yang B-20 / [#49](../../issues/49) minta.** *Compression
> Policy* naskah 9 menyimpan Raw, Episode, dan Summary sama-sama "penuh"
> sehingga **menambah** data alih-alih menguranginya. `Importance Scoring`
> adalah gerbang yang hilang: tidak semua yang masuk short-term naik ke
> long-term.
>
> ⚠️ Yang masih belum ada tetap **angkanya** — ambang importance, dan berapa
> lama short-term bertahan. Naskah 11 §7.26 memberi satu-satunya angka konkret
> di dua belas naskah (`retention: 90d`). Itu titik awal, bukan jawaban.

> ⭐ **"Satu kali ≠ preferensi, dua puluh kali = preferensi" adalah aturan
> anti-karakterisasi yang bisa diuji.** Ia mencegah kesalahan yang paling mudah
> dilakukan sistem seperti ini: menyimpulkan siapa seseorang dari satu
> peristiwa. Bandingkan dengan **B-17** (satu salah hitung Wardrobe meracuni
> semua rekomendasi) — konsolidasi berbasis pengulangan adalah pertahanan
> alami terhadapnya, karena satu deteksi keliru tidak pernah cukup untuk naik.

---

## §9.9 — Memory Decay

> Preferensi manusia berubah. Maka memory harus memiliki:

```
strength · recency · frequency · importance · confidence · decay
```

Contoh:

```
User liked minimalist fashion in 2024.

2026:
rarely chooses minimalist outfits.
```

> **Memory lama tidak boleh menjadi dogma.**

```
Memory Strength(t)
=
Initial Strength × Decay(t)
+
Reinforcement
```

---

> ⭐⭐ **Kalimat "memory lama tidak boleh menjadi dogma" membatalkan
> "permanen" di naskah 9 — dan itu menutup C-13 / [#50](../../issues/50).**
>
> Naskah 9 Pillar 4 menetapkan **Chapter: permanen** dan **Identity:
> permanen**. Rumus di atas tidak memberi pengecualian untuk keduanya: setiap
> memori punya `Decay(t)`. Digabung dengan §9.4 (*Preference ≠ permanent
> identity*), klaim permanen itu gugur di naskah yang sama-sama kata pemilik —
> bukan lewat catatan audit.
>
> ⚠️ Karena naskah 9 dan naskah 13 sekarang bertentangan langsung soal
> "permanen", yang berlaku sebaiknya dinyatakan sekali: **naskah 13**, karena
> ia lebih baru **dan** karena arah perubahannya adalah arah yang aman.

> ⭐ **`Reinforcement` di rumus itu yang membuatnya benar.** Peluruhan murni
> akan menghapus preferensi yang masih hidup hanya karena lama; penguatan
> membuat yang masih dipakai tetap kuat. Itu juga jalan keluar otomatis dari
> kesalahan yang dikhawatirkan C-13: karakterisasi yang salah **tidak akan
> diperkuat**, jadi ia luruh sendiri.

> ⚠️ **Tiga hal yang masih dibutuhkan sebelum rumus ini bisa dijalankan:**
>
> 1. **Bentuk `Decay(t)`** — eksponensial dengan paruh waktu berapa? Preferensi
>    fashion dan preferensi makanan hampir pasti tidak sama.
> 2. **Ambang lupa** — di bawah `strength` berapa sebuah memori berhenti
>    dipakai, dan apakah ia dihapus atau hanya diabaikan. Ini menyentuh
>    **C-9**: memori yang "dilupakan" tapi masih tersimpan tetap data pribadi.
> 3. **Hubungan `strength` dengan `confidence`** — keduanya ada di daftar yang
>    sama, dan keduanya turun seiring waktu. Kalau berbeda, bedanya perlu
>    ditulis; kalau sama, salah satunya sebaiknya dibuang.

> ⚠️ **Peluruhan bertabrakan dengan jejak audit, dan arah tabrakannya baru.**
> §8.25 mencatat `data_accessed` dan keputusan; kalau memori yang mendasari
> sebuah rekomendasi sudah luruh, jejak auditnya tetap menunjuk memori yang
> **sudah tidak berbunyi sama seperti dulu**. Untuk bisa menjelaskan
> rekomendasi lama, `audit_logs` perlu menyimpan `strength` **pada saat itu**,
> bukan menunjuk nilai sekarang. Bertaut **E-75** / [#64](../../issues/64).
