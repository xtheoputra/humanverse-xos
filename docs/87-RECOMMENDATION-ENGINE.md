# 87 — §11 Recommendation Engine

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Semua recommendation harus melewati scoring.**

```
Recommendation Score =
    Trend Relevance
  + Personal Preference
  + Context Fit
  + Historical Success
  + Weather Fit
  + Occasion Fit
  + Availability
```

Contoh:

```
Outfit A
Trend             0.80
Preference        0.95
Context           0.92
Weather           0.90
History           0.87

Final = 0.89
```

> Sehingga AI tidak sekadar berkata *"Saya rasa outfit A bagus"* — sistem
> punya **alasan terstruktur**.

---

> ✅ Angkanya konsisten: rata-rata lima nilai contoh
> (0.80 + 0.95 + 0.92 + 0.90 + 0.87) ÷ 5 = **0,888 → 0,89**.
>
> ⚠️ Tetapi rumusnya menyebut **tujuh** komponen sementara contohnya memakai
> **lima** — *Occasion Fit* dan *Availability* tidak muncul, dan **bobot tiap
> komponen belum ada** (contoh ini memperlakukan semuanya sama berat).
>
> ⚠️ Ini **sistem skoring ketiga** di proyek yang sama: bobot mesin rekomendasi
> naskah 2 (berjumlah 100 %), Outfit Score naskah 3 (berjumlah 100), dan
> Recommendation Score ini (rata-rata 0–1). Lihat butir **E-14** dan **E-37**.
