# 117 — Pillar 4: Memory Compression

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> Ini salah satu **masalah besar AI**.
>
> Kalau user memakai HumanVerse selama **10 tahun**: jutaan event, ribuan chat,
> ratusan goal. **Kita tidak bisa mengirim semuanya ke LLM.**

---

## Solusi: memory bertingkat

```
Raw Memory
    ↓
Episode
    ↓
Summary
    ↓
Life Chapter
    ↓
Identity Memory
```

### Contoh

| Tingkat | Isi |
|---|---|
| **Raw** | `2026-09-03 · Gym` |
| **Episode** | *Workout consistency improved this week.* |
| **Chapter** | *August became the strongest workout month.* |
| **Identity** | *User is consistently committed to strength training.* |

---

## Compression Policy

| Level | Retention |
|---|---|
| Raw | penuh |
| Episode | penuh |
| Summary | penuh |
| Chapter | **permanen** |
| Identity | **permanen** |

---

> ⚠️ **Tabel retensi ini tidak mengompres apa pun.** Masalah yang dinyatakan di
> awal adalah *"jutaan event, tidak bisa dikirim semuanya ke LLM"* — tetapi
> kebijakannya menyimpan **Raw, Episode, dan Summary sama-sama \"penuh\"**,
> tanpa jendela waktu. Kalau Raw disimpan penuh selamanya, tingkatan ini
> menambah data, bukan menguranginya.
>
> Yang membuatnya benar-benar mengompres adalah **batas waktu per tingkat**,
> misalnya: Raw 90 hari → Episode 2 tahun → Summary 5 tahun → Chapter &
> Identity permanen. Angka itu belum ada. Lihat butir **B-20**.
>
> ⚠️ **Lima tingkat ini tegak lurus dengan enam `kind` memory** (working,
> episodic, semantic, behavioral, preference, procedural) di naskah 5 §17 —
> bukan penggantinya. Sebuah memori punya *jenis* **dan** *tingkat kompresi*.
> Tabel `memories` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) butuh satu
> kolom lagi. Bertaut butir **E-39**.
>
> 🛑 **\"Identity Memory\" permanen adalah butir yang paling perlu dipikirkan
> ulang.** *\"User is consistently committed to strength training\"* adalah
> **klaim tentang siapa seseorang**, disimpan selamanya, dan akan membentuk
> setiap rekomendasi sesudahnya. Tiga masalahnya:
>
> - **Menguatkan dirinya sendiri.** Kalau salah, ia tetap dipakai, dan
>   rekomendasi yang lahir darinya akan menghasilkan data yang seolah
>   membenarkannya.
> - **Orang berubah.** Prinsip pembuka pilar ini sendiri berkata *"preferensi
>   manusia berubah"* — identitas lebih lagi.
> - **Bertabrakan dengan hak hapus** (**C-9**) dan dengan prinsip penutup
>   naskah 4: *"jangan menilai apakah seseorang manusia yang baik atau buruk"*.
>   Ini belum penilaian, tetapi ia sudah **karakterisasi permanen**.
>
> Usul: Identity Memory tetap boleh ada, tetapi **tidak permanen** — ia harus
> punya `confidence`, `evidence_count`, `valid_until`, dan bisa dilihat serta
> dibantah pengguna di Privacy Center. Lihat butir **C-13**.
