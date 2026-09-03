# 89 — §17 Memory Architecture

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Memory bukan hanya vector database.**

```
                    MEMORY
                       │
      ┌────────────────┼─────────────────┐
      │                │                 │
 Working           Episodic          Semantic
 Memory            Memory            Memory
      │                │                 │
 current task      past events       knowledge
      │                │                 │
      └────────────────┼─────────────────┘
                       │
                 Behavioral
                    Memory
                       │
                 Preferences
                       │
                Procedural Memory
```

---

## Contoh tiap jenis

| Jenis | Contoh dari pemilik |
|---|---|
| **Episodic** | *"User memilih outfit hitam pada meeting minggu lalu."* |
| **Semantic** | *"User menyukai gaya minimalis."* |
| **Behavioral** | *"User lebih sering memakai warna gelap."* |
| **Procedural** | *"Jika besok ada meeting pagi, siapkan outfit malam sebelumnya."* |

---

> ⚠️ **Ini hitungan memory yang kelima.** 3 jenis (Memory Agent) · 5 (naskah 2)
> · 7 (naskah 3) · memory **bernama** (naskah 4 §14) · dan **6 di sini**
> (Working, Episodic, Semantic, Behavioral, Preferences, Procedural).
>
> Bedanya: versi ini punya **contoh untuk empat di antaranya**, jadi paling
> mudah diuji. Tapi hubungannya dengan memory bernama di manifest §14
> (`fashion_preferences`, `wardrobe`, `outfit_history`) belum dijelaskan —
> apakah nama itu *scope* di atas jenis, atau penggantinya. Lihat butir
> **E-33** dan **E-39**.
