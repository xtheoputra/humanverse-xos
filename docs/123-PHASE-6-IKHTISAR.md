# 123 — Phase 6: HumanVerse Developer Platform (ikhtisar naskah kesepuluh)

> Berkas ini merekam kata pemilik apa adanya (naskah kesepuluh, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Posisi pemilik

> Ini adalah fase yang mengubah HumanVerse **dari produk menjadi platform**
> yang bisa dikembangkan oleh developer lain — mirip **iOS ↔ App Store**,
> **GitHub ↔ GitHub Apps**, atau **OpenAI ↔ GPTs/Agents SDK**. Bedanya, fokus
> HumanVerse adalah **Human Intelligence Platform**.

> **Target Phase 6:** membangun ekosistem agar AI Agent, aplikasi, dan layanan
> pihak ketiga dapat terhubung ke HumanVerse **secara aman, konsisten, dan
> dapat dikontrol pengguna**.

---

## Tiga jenis pengguna

| Tipe | Peran |
|---|---|
| **End User** | Menggunakan AI Assistant |
| **Developer** | Membangun Agent & Plugin |
| **Enterprise** | Integrasi organisasi |

## Lima prinsip

```
API-first
SDK-first
Consent-first
AI-native
Backward-compatible
```

> ⭐ **`Backward-compatible` baru pertama kali muncul di sepuluh naskah**, dan
> ia tepat berada di sini: begitu ada developer pihak ketiga, kontrak tidak
> bisa diubah sepihak lagi. Ini juga alasan **#38** (format nama event) harus
> diselesaikan sebelum API publik pertama.

---

## Arsitektur

```
Developer Portal
        │
        ▼
  API Gateway
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
SDK   Agent   Plugin
      Runtime
        │
        ▼
  Marketplace
```

---

## Peta Layer 1–25

| Layer | Nama | Berkas |
|---|---|---|
| **1–3** | Developer Portal · API Platform · API Gateway | [`124`](124-DP-L1-L3-PORTAL-API-GATEWAY.md) |
| **4–5** | Authentication Platform · API Key Management | [`125`](125-DP-L4-L5-AUTH-DAN-KEY.md) |
| **6–9** | HumanVerse SDK · Agent SDK · Manifest Standard · Plugin SDK | [`126`](126-DP-L6-L9-SDK-AGENT-PLUGIN.md) |
| **10–11** | MCP Compatibility · Tool Registry | [`127`](127-DP-L10-L11-MCP-TOOL-REGISTRY.md) |
| **12–16** | Webhook · Event Subscription · Sandbox · CLI · Packaging | [`128`](128-DP-L12-L16-WEBHOOK-SANDBOX-CLI.md) |
| **17–20** | Marketplace · Review System · Revenue · Analytics | [`129`](129-DP-L17-L20-MARKETPLACE-REVIEW-REVENUE.md) |
| **21–25** | Documentation · Examples · Certification · Community · Enterprise | [`130`](130-DP-L21-L25-DOKUMENTASI-KOMUNITAS-ENTERPRISE.md) |
| — | Repo · roadmap D1–D8 · 13 deliverable | [`131`](131-PHASE-6-ROADMAP-DAN-DELIVERABLE.md) |

---

## ⚠️ Tabrakan penomoran Layer

Naskah ini memulai penomoran **Layer 1** lagi, padahal nomor itu sudah dipakai:

| Nomor | Naskah 3 (Phase 2) | Naskah 7 (Phase 4) | Naskah 10 (Phase 6) |
|---|---|---|---|
| Layer 6 | AgentOS | — | HumanVerse SDK |
| Layer 11 | Workflow Engine | — | Tool Registry |
| Layer 14 | Evaluation Framework | — | Testing Sandbox |
| Layer 20 | Simulation Engine | — | Analytics Platform |
| Layer 22 | — | Engineering Standards | Example Library |
| Layer 25 | — | Component Library | Enterprise Integration |

Untuk dokumentasi yang tujuannya **dibaca AI coding agent tanpa kehilangan
konteks** (Layer 41 naskah 7), *"Layer 22"* yang berarti dua hal berbeda adalah
masalah nyata. Di berkas ini nomornya ditulis **DP-L1…DP-L25**. Lihat butir
**E-59**.

> ⚠️ Angka liar `6` dan `5` muncul lagi menempel di judul — artefak
> salin-tempel yang sama seperti **A-1**/**H-9**, kini di naskah ketujuh
> berturut-turut.
