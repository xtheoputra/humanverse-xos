# 133 — §7.2 Data Classification

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> **Tidak semua data manusia diperlakukan sama.**

| Level | Nama | Isi |
|---|---|---|
| **1** | Public | fashion trends · public places · general knowledge |
| **2** | User Data | habits · goals · preferences · activities |
| **3** | Sensitive | journal · location history · financial behavior · health-related tracking |
| **4** | **Highly Sensitive** | ⚠️ *"Data yang membutuhkan perlindungan dan kontrol paling ketat"* — **tanpa satu contoh pun** |

Prinsip:

```
Data Sensitivity
       ↓
Access Policy
       ↓
Agent Permission
       ↓
Audit
```

---

> ⭐ **Rantai empat langkah itu benar dan berguna.** Ia mengikat klasifikasi ke
> penegakan: sensitivitas menentukan kebijakan akses, kebijakan menentukan izin
> agent, dan setiap akses tercatat. Tiga di antaranya sudah punya bentuk di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) (`permissions`, `audit_logs`);
> yang belum ada adalah **kolom sensitivitas** itu sendiri.
>
> ⚠️ **Level 4 kosong.** Tiga level pertama punya contoh, Level 4 hanya punya
> definisi. Padahal justru level inilah yang menentukan aturan paling ketat.
>
> Kandidat yang sudah disebut di naskah lain dan belum punya tempat:
> **data biometrik** — foto wajah, bentuk tubuh, warna kulit (**C-1**), yang di
> banyak yurisdiksi adalah kategori khusus dengan syarat persetujuan tersendiri.
> Ditambah kemungkinan: isyarat krisis dari jurnal (**C-3**), dan data anak
> di bawah umur bila *Family Mode* (Phase 9) jadi dibangun.
>
> Ditandai kosong, **tidak ditambal**. Lihat butir **G-6**.
>
> ⚠️ Perhatikan **`journal` ada di Level 3**, sementara naskah 10 DP-L4
> menawarkan `journal.read` sebagai scope developer pihak ketiga (**#53**).
> Klasifikasi ini justru menguatkan keberatan itu: data Level 3 seharusnya
> tidak masuk daftar scope biasa.
