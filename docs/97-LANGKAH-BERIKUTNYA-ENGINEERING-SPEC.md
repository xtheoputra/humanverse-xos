# 97 — Langkah berikutnya: Engineering Specification v1.0

> Berkas ini merekam kata pemilik apa adanya (naskah kelima, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Kata pemilik

> Blueprint di atas sudah menjadi **level arsitektur sistem**. Tahap berikutnya
> seharusnya **jauh lebih konkret lagi**: kita masuk ke **Engineering
> Specification v1.0**.

Isinya:

```
database schema PostgreSQL lengkap
ERD
event contract
API endpoint
folder/module structure
Agent Registry schema
MCP Tool Registry
permission schema
prompt architecture
Docker Compose
CI/CD
backlog task V0 yang bisa langsung diberikan ke AI coding agent satu per satu
```

> Itu yang akan mengubah HumanVerse X dari **ide besar** menjadi **repo yang
> benar-benar bisa mulai dicoding**.

---

## Status

| Hal | Keadaan |
|---|---|
| Blueprint Engineering v1.0 | ✅ **selesai** — berkas `80`–`96` |
| Engineering Specification v1.0 | **belum ditulis** |
| Kode | **masih nol** |
| Repo produk (`humanverse-x/`) | **belum dibuat** — repo ini masih repo dokumen |

---

## Yang harus diputuskan sebelum Engineering Spec ditulis

Engineering Spec akan **mengunci skema basis data**. Empat butir ini
menentukan isinya, dan mengubahnya setelah tabel dibuat berarti migrasi:

| Butir | Kenapa mengunci skema |
|---|---|
| **A-19** — model angka pengguna | Ada 5 model berbeda (Behavior Genome 6 · Profile Engine 5 · HumanState 7 · Dashboard 7 · DigitalTwin 8 model). Tabel `memories`, `profiles`, dan state harian bergantung pada pilihan ini. |
| **E-16..E-18** — model graf | Neo4j sudah ditetapkan sebagai penyimpanan graf, tetapi arah relasi dan daftar node belum satu. |
| **E-39** — memory: jenis atau nama | §17 memakai 6 **jenis**; manifest §14 memakai **nama scope**. Tabel `memories` butuh salah satunya sebagai kolom. |
| **E-37** — tiga sistem skoring | Tabel `recommendations` menyimpan skor — dalam skala 0–1 (§11), 0–100 (naskah 3), atau persen (naskah 2)? |

> ⚠️ Tiga hal berikut **tidak memblokir** skema, jadi boleh berjalan paralel:
> sumber data Trend (**A-5**), teknologi desktop/admin (**A-11**), dan cek
> merek (**C-5**).
