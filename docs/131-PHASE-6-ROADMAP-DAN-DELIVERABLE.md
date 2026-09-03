# 131 — Phase 6: repo, roadmap D1–D8 & deliverable

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Struktur repository

```
developer-platform/
├── portal/       ├── cli/          ├── webhooks/
├── sdk/          ├── marketplace/  ├── examples/
├── agent-sdk/    ├── billing/      └── docs/
├── plugin-sdk/   ├── analytics/
```

---

## Roadmap Implementasi

| Sprint | Fokus |
|---|---|
| **D1** | Developer Portal |
| **D2** | REST API |
| **D3** | SDK |
| **D4** | Agent SDK |
| **D5** | CLI |
| **D6** | Sandbox |
| **D7** | Marketplace |
| **D8** | Analytics |

> ⚠️ **Skema penomoran keempat.** Sekarang berjalan berdampingan:
> **V0–V6** (versi produk) · **Sprint 0–6** (sprint V0) · **R1–R8** (sprint
> riset) · **D1–D8** (sprint developer platform). Belum ada aturan hubungan.
> Bertaut **E-57** / issue #51.
>
> ⚠️ **Urutannya perlu satu penyesuaian.** **D6 Sandbox** dan **D2 REST API**
> harus ada **sebelum** developer luar mana pun diberi akses — sementara
> Marketplace (D7) baru di akhir. Itu sudah benar. Yang belum: **review system
> (DP-L18) tidak muncul di roadmap sama sekali**, padahal ia yang menahan agent
> pihak ketiga sebelum publish.

---

## Deliverables Phase 6

| Deliverable | Status |
|---|---|
| Developer Portal | **Blueprint** |
| API Platform | **Blueprint** |
| OAuth Platform | **Blueprint** |
| SDK Multi-language | **Blueprint** |
| Agent SDK | **Blueprint** |
| Plugin SDK | **Blueprint** |
| MCP Compatibility | **Blueprint** |
| Tool Registry | **Blueprint** |
| Marketplace | **Blueprint** |
| Billing | **Blueprint** |
| Analytics | **Blueprint** |
| CLI | **Blueprint** |
| Documentation Platform | **Blueprint** |

> ✅ Ketiga belas jujur ditandai **Blueprint** — konsisten dengan Phase 5.
>
> ⚠️ **Review System dan Testing Sandbox tidak ada di daftar deliverable**,
> padahal keduanya adalah butir yang paling menjawab beban hukum marketplace
> (**A-15**, **C-7**). Keduanya justru yang paling perlu ditandai sebagai
> deliverable, supaya tidak hilang saat fase ini dipecah jadi tugas.

---

## Apa yang berubah setelah Phase 6?

> Sebelum fase ini, HumanVerse adalah **platform AI yang dibangun oleh satu
> tim**.
>
> Setelah Phase 6, HumanVerse memiliki **Developer Platform** yang memungkinkan
> developer pihak ketiga membuat Agent, Plugin, SDK, dan integrasi mereka
> sendiri melalui **API yang terversi, permission yang terkontrol, serta
> marketplace yang memiliki proses review dan analytics**.
>
> Dengan kata lain, HumanVerse mulai bertransformasi **dari produk menjadi
> ekosistem** yang dapat tumbuh melalui kontribusi pihak ketiga **tanpa
> mengorbankan keamanan dan kontrol pengguna**.
