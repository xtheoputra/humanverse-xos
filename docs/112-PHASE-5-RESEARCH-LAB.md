# 112 — Phase 5: HumanVerse AI Research Lab

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Posisi pemilik

> Masih ada **satu fase terakhir (Phase 5)**. Yang belum kita bahas sama sekali
> adalah **HumanVerse AI Research Lab**. Ini **bukan lagi soal membangun
> aplikasi, tetapi membangun perusahaan AI**.
>
> Di fase itu kita akan mendesain sekitar **500+ spesifikasi tingkat riset**.

---

## Sembilan arah riset

| # | Arah | Keterangan pemilik |
|---|---|---|
| 1 | **Behavior Foundation Model (BFM)** | model AI khusus perilaku manusia |
| 2 | **Human Graph Neural Network** | pembelajaran di atas Knowledge Graph |
| 3 | **Long-term Memory Compression** | memori bertahun-tahun tanpa membengkak |
| 4 | **World Model & Counterfactual Reasoning** | simulasi skenario *"bagaimana jika"* |
| 5 | **Multi-Agent Collective Intelligence** | puluhan agent berkolaborasi untuk satu tujuan |
| 6 | **Federated Personal AI** | personalisasi tanpa mengirim seluruh data mentah ke cloud |
| 7 | **On-device Foundation Models** | AI berjalan lokal untuk privasi |
| 8 | **Agent Marketplace Protocol** | standar agar developer pihak ketiga bisa membangun agent |
| 9 | **HumanVerse Research Roadmap (5 tahun)** | roadmap R&D seperti laboratorium AI kelas dunia |

---

## Catatan

> ⭐ **Butir 3 (Long-term Memory Compression) adalah masalah nyata yang sudah
> ada di V0**, bukan riset jauh. Tabel `memories` akan tumbuh setiap hari;
> kolom `valid_until` dan `last_reinforced_at` di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) adalah bentuk paling sederhana
> dari gagasan ini — memori bisa kedaluwarsa tanpa dihapus.
>
> ⭐ Butir **6** dan **7** adalah janji privasi yang selama ini ditunda ke V5
> (**A-14**). Menempatkannya di Phase 5 berarti ditunda **lebih jauh lagi**,
> bukan lebih dekat.
>
> ⚠️ **Hitungan dokumen sekarang: 100 → 160 → 300+ → 14 lapisan → +500.**
> Totalnya melewati **900 spesifikasi** sebelum satu baris kode ada.
> Lihat butir **A-13**, **A-23**, dan **A-24**.
>
> ⚠️ Butir 1, 2, dan 6 (**melatih model**, bukan memakainya) mengubah status
> hukum data pengguna: melatih model di atas data tidur, mood, dan jurnal orang
> membutuhkan dasar persetujuan yang **berbeda** dari sekadar memakainya untuk
> memberi rekomendasi. Lihat butir **C-11**.
