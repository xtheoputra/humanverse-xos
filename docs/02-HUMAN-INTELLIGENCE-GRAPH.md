# 02 — Human Intelligence Graph

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Gagasan inti

**Alih-alih membuat fitur terpisah, semua data dihubungkan.**

Inilah satu kalimat yang membedakan HumanOS dari kumpulan aplikasi biasa.
Sebuah habit tracker mencatat habit. HumanOS mencatat **hubungan antar
perilaku**.

---

## Contoh rantai sebab-akibat

```
        Tidur buruk
             │
             ▼
        Mood turun
             │
             ▼
    Produktivitas turun
             │
             ▼
      Olahraga gagal
```

AI menyarankan:

- tidur lebih awal
- mengurangi screen time
- mengganti olahraga berat menjadi **stretching**

**Semua rekomendasi muncul karena hubungan antar perilaku** — bukan karena
aturan yang ditulis satu per satu untuk tiap fitur.

---

## Konsekuensi rancangan

Karena grafnya yang menjadi inti, maka:

- setiap modul **wajib menyetor simpul dan sisi** ke graf yang sama;
- tidak ada modul yang boleh menyimpan datanya sendiri secara terisolasi;
- nilai produk tumbuh dari **kepadatan sambungan**, bukan dari jumlah fitur.
