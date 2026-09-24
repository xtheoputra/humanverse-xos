# `apps/`

Aplikasi yang dijalankan atau dipasang — [`arch/03`](../arch/03-MONOREPO-FINAL.md) §3.

| Folder | Isi | Keadaan |
|---|---|---|
| [`api/`](api/README.md) | backend V0 — FastAPI, satu proses, 12 modul ([`spec/06`](../spec/06-MODULE-BOUNDARIES.md)) | ✅ Sprint 0–2 |
| [`mobile/`](mobile/README.md) | Flutter (ADR-001) — **satu basis kode untuk seluler dan web** (`flutter build web`) | ✅ layar pertama, tugas 2.7 |
| `admin/` | Flutter web yang sama ([`arch/05`](../arch/05-TECHNOLOGY-STACK.md) §4) | ⏳ |
| `desktop/` | belum punya kebutuhan sebelum V5 | — |

> 🔧 **`web/` tidak dibuat sebagai folder terpisah** (24 Sep 2026, tugas 2.7):
> aplikasi web adalah target `web` proyek Flutter yang sama di `mobile/` —
> dua folder untuk satu basis kode akan menyimpang tanpa ada yang tahu.
> Halaman publik ber-SEO tetap di luar `apps/` ([`arch/05`](../arch/05-TECHNOLOGY-STACK.md) §4, B-5).

Folder yang belum berisi kode sengaja belum dibuat.
