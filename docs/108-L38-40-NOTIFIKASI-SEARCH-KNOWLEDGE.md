# 108 — Layer 38–40: Notification Intelligence, Search & Knowledge Platform

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Layer 38 — Notification Intelligence

> **Jangan spam.**

Engine menghitung:

```
urgency · relevance · timing · quiet hours
```

Contoh:

> Reminder gym jam 18:00. Kalau user sedang **meeting**, AI **menunda**.

> ⭐ Ini penerapan Context Engine yang paling mudah diukur benar-salahnya —
> dan metrik penjaga paling jelas untuk Layer 34: **jumlah notifikasi per hari
> tidak boleh naik** karena eksperimen.

---

## Layer 39 — Search Platform

Jenis search:

```
Semantic Search
Memory Search
Knowledge Search
Wardrobe Search
Journal Search
```

Contoh:

> *"Kapan terakhir saya memakai blazer hitam?"*
>
> AI dapat menjawab dari data pengguna.

> ⚠️ **Journal Search menyentuh tulisan paling pribadi.** Ia harus tunduk pada
> scope izin yang sama seperti memory — agent tanpa izin `journal` tidak boleh
> menerima hasilnya, bahkan lewat pencarian. Sudah ditegakkan di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md).

---

## Layer 40 — Knowledge Platform

> Ini **berbeda** dengan memory.
>
> ## Memory = pengalaman pengguna.
> ## Knowledge = pengetahuan dunia.

Contoh:

```
Fashion Knowledge
Health Knowledge
Career Knowledge
Learning Knowledge
Travel Knowledge
```

> Dipisahkan agar **lebih mudah diperbarui**.

---

> ⭐ **Pemisahan ini yang paling berguna di seluruh Layer 38–40**, dan
> menjelaskan satu kekaburan lama: *Semantic Memory* di naskah 3 dan 5 selalu
> ambigu antara "yang diketahui sistem tentang pengguna" dan "yang diketahui
> sistem tentang dunia".
>
> Keduanya tetap cocok: contoh Semantic Memory naskah 5 §17 adalah *"User
> menyukai gaya minimalis"* — itu **tentang pengguna**, jadi tetap `memories`.
> Pengetahuan dunia pindah ke Knowledge Platform.
>
> Konsekuensinya nyata: pengetahuan dunia **tidak** ikut terhapus saat pengguna
> menghapus akun, dan **tidak** perlu izin per pengguna. Batasnya harus ditulis
> sebelum keduanya sama-sama masuk Qdrant. Lihat butir **E-49**.
