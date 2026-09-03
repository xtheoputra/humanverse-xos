# 22 — Paket Dokumentasi Engineering (~100 dokumen)

> Berkas ini merekam kata pemilik apa adanya. Koreksi dan keraguan ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Alasan

> Agar pengembangan dengan AI agent benar-benar efisien, saya menyarankan
> proyek ini memiliki **dokumentasi engineering setara perusahaan teknologi
> besar, bukan hanya kode**.

Dengan struktur ini, AI coding agents seperti **Codex, Claude Code, Cursor,
atau Gemini CLI** dapat mengerjakan modul **secara paralel tanpa kehilangan
konteks**.

---

## Delapan belas dokumen yang disebut pemilik

Paket lengkapnya mencakup **sekitar 100 dokumen teknis**, antara lain:

### Produk & bisnis

| # | Dokumen |
|---|---|
| 1 | **PRD** — Product Requirement Document |
| 2 | **BRD** — Business Requirement Document |
| 3 | **SRS** — Software Requirement Specification |
| 4 | **Investor Pitch Deck** |

### Arsitektur

| # | Dokumen |
|---|---|
| 5 | **System Architecture** |
| 6 | **ADR** — Architecture Decision Records |
| 7 | **ERD Database** |
| 8 | **API OpenAPI Specification** |
| 9 | **Event Schema** |

### AI

| # | Dokumen |
|---|---|
| 10 | **AI Agent Specification** |
| 11 | **Prompt Engineering Guide** |
| 12 | **MCP Tool Registry** |
| 13 | **Knowledge Graph Ontology** |

### Infrastruktur & keamanan

| # | Dokumen |
|---|---|
| 14 | **Security Blueprint** |
| 15 | **CI/CD Blueprint** |
| 16 | **Kubernetes Manifest Guide** |
| 17 | **Terraform Infrastructure** |

### Mutu

| # | Dokumen |
|---|---|
| 18 | **QA Testing Framework** |

---

## Posisi berkas yang sudah ada

Dokumen `01`–`21` di folder ini **belum termasuk** ke-18 dokumen di atas.
Keduanya berbeda lapisan:

| Lapisan | Isi | Status |
|---|---|---|
| Visi & arsitektur (berkas `01`–`21`) | apa yang mau dibangun dan bentuk kasarnya | ✅ selesai |
| Paket engineering (~100 dokumen) | spesifikasi yang bisa dieksekusi agen | ⬜ belum satu pun |

> Berkas `01`–`21` adalah **bahan mentah** untuk menyusun PRD, SRS, dan System
> Architecture — bukan penggantinya.
