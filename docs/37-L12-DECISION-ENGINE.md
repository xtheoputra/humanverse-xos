# 37 — Layer 12: Decision Engine

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Ini membuat AI benar-benar terasa pintar.**
>
> AI menghitung skor.

---

## Contoh — Outfit Score

| Faktor | Bobot |
|---|---|
| **Acara** | 25 |
| **Cuaca** | 20 |
| **Warna** | 20 |
| **Preferensi** | 20 |
| **Trend** | 15 |
| **Total** | **100** |

**Output:**

> Outfit A lebih cocok.

---

> ℹ️ Bobot ini berjumlah tepat 100 — sudah diperiksa. Perhatikan bahwa ia
> **berbeda** dari bobot mesin rekomendasi umum di
> [`18-DATABASE-DAN-PIPELINE.md`](18-DATABASE-DAN-PIPELINE.md) (di sana Cuaca
> hanya 5 %). Keduanya beroperasi di tingkat berbeda — lihat butir **E-14**.
