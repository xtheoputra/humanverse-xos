# 153 — §8.44–§8.46 Roadmap 8 Sprint, Definition of Done & Prinsip Penutup

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.44 — Fase 8 Implementation Roadmap

> Saya sarankan **8 sprint**.

| Sprint | Isi |
|---|---|
| **S8.1 — Identity Foundation** | Identity · Authentication · Sessions · Service Identity · Agent Identity |
| **S8.2 — Authorization** | RBAC · ABAC · Permission Engine · Capability System |
| **S8.3 — Consent & Privacy** | Consent Engine · Data Vault · Data Classification · Privacy Center · Data Export · Data Deletion |
| **S8.4 — Policy & Risk** | Policy Engine · Risk Engine · Action Classification · Human Confirmation |
| **S8.5 — AI Safety** | Prompt Injection Defense · Input Safety · Output Safety · PII Detection · Tool Security · Sensitive Domain Guardrails |
| **S8.6 — Agent Security** | Sandbox · Capability Isolation · Agent Signing · Agent Trust · Marketplace Security |
| **S8.7 — Security Operations** | Audit · Security Events · Threat Detection · Incident Response · Kill Switch · Red Team |
| **S8.8 — Hardening** | Penetration Testing · Chaos Security Testing · Disaster Recovery · Security Review · Architecture Review · Production Readiness |

---

> ⭐ **Awalan `S8.` adalah penomoran pertama yang tidak bertabrakan dengan apa
> pun.** Sampai naskah 11, lima skema berjalan berdampingan tanpa awalan:
> V0–V6, Sprint 0–6, R1–R8, dan **D1–D8 dua kali** (**E-64**). Di sini
> nomornya membawa fasenya sendiri, sehingga *"kita di S8.4"* tidak bisa
> disalahartikan. Usul yang sama sebaiknya diberlakukan surut: `R1–R8` →
> `S5.1–S5.8`, `D1–D8` naskah 10 → `S6.1–S6.8`, naskah 11 → `S7.1–S7.8`.
> Lihat [#56](../../issues/56).

> ⭐ **Urutannya benar dan itu tidak sepele.** Identity sebelum Authorization,
> Authorization sebelum Consent, Consent sebelum Policy, Policy sebelum AI
> Safety — setiap sprint memakai yang dibangun sebelumnya. Bandingkan dengan
> roadmap Phase 5 yang memulai dari R1 *Behavior Foundation Model*, bagian
> yang paling bergantung pada data yang belum ada (**B-21**).

> 🛑 **Delapan sprint untuk fase ini, tujuh sprint untuk seluruh V0.** Naskah
> 5 §32 memecah V0 menjadi 7 sprint dengan target 4–6 minggu (**A-17**).
> Fase 8 sendirian meminta 8 sprint dan 20 tabel baru (§8.40). Dua angka itu
> tidak bisa berdiri berdampingan tanpa satu keputusan: **berapa banyak dari
> Fase 8 yang masuk V0.**
>
> Saran saya — yang perlu, dalam urutan yang sudah benar:
>
> | Masuk V0 | Kenapa |
> |---|---|
> | **S8.1** sebagian | `sessions` + identity agent; V0 tanpa sesi tidak bisa punya pengguna |
> | **S8.2** sebagian | `permissions` sudah ada di spesifikasi; tinggal ditegakkan di jalur tool |
> | **S8.3** sebagian | `consents.purpose` + `model_training` — **satu-satunya yang mahal kalau ditunda** (**B-22**) |
> | **S8.4** sebagian | risk gate sudah ada di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) |
> | **S8.5** sebagian | hanya prompt injection, dan hanya ketika tool eksternal pertama masuk |
>
> Yang **menunggu pengguna kedua**: S8.6 (marketplace belum ada), S8.7
> (kill switch & incident response tanpa pengguna hanya menjaga diri sendiri),
> S8.8 (hardening untuk sistem yang belum dirilis). Lihat **A-25** /
> [#58](../../issues/58).

---

## §8.45 — Definition of Done Fase 8

> Fase ini **belum selesai** hanya karena authentication sudah bekerja.

HumanVerse baru boleh menganggap fase 8 selesai jika:

```
✓ Every actor has identity
✓ Every action is authorized
✓ Every sensitive access is governed
✓ Consent is explicit and revocable
✓ Agents have scoped permissions
✓ High-risk actions require confirmation
✓ AI outputs are safety checked
✓ Tools are policy controlled
✓ Sensitive data is minimized
✓ Data can be exported
✓ Data can be deleted
✓ Agents can be revoked
✓ Security events are auditable
✓ Incidents can be contained
✓ AI can be globally stopped
✓ Third-party agents are sandboxed
✓ Red-team testing exists
```

---

> ⭐⭐ **Ini kriteria keluar pertama di dua belas naskah yang seluruh
> butirnya bisa dijawab ya atau tidak.** Bandingkan dengan taksiran kemajuan
> yang penyebutnya berubah tiap naskah (35 % → 45 %, **A-24**): tujuh belas
> baris di atas tidak bisa ditaksir, hanya bisa diperiksa. Ini bentuk yang
> semestinya dipakai juga untuk V0.

> ⚠️ **Empat butir tidak punya alat ukur, dan satu bertentangan dengan
> daftarnya sendiri:**
>
> | Butir | Yang kurang |
> |---|---|
> | *Every sensitive access is governed* | "sensitive" = Level 3, atau Level 4 yang masih kosong (**G-6**)? |
> | *Sensitive data is minimized* | minimisasi versi §8.6 (scope) atau versi §8.11 (pertanyaan)? Dua ukuran berbeda (**E-71**) |
> | *Red-team testing exists* | *"exists"* bisa dipenuhi satu berkas uji; §8.33 punya delapan jenis uji tanpa ambang |
> | *High-risk actions require confirmation* | "high-risk" = R3 ke atas (§8.17), tapi tangganya baru saja dikalibrasi ulang (**E-67**) |
>
> Dan yang hilang dari daftar: **tidak ada satu baris pun tentang
> memperbaiki data yang salah** — sejalan dengan `Edit` yang hilang dari
> Privacy Center (**E-74**). Daftar ini bisa lulus penuh sementara pengguna
> tidak punya cara membetulkan satu pun kesimpulan yang keliru tentang
> dirinya.

---

## §8.46 — Hal yang Paling Penting

> Ada satu **perubahan mindset** yang ingin saya tanamkan untuk HumanVerse X.

Jangan membangun:

```
AI
↓
Power
↓
Automation
```

Tetapi:

```
AI
 ↓
Capability
 ↓
Permission
 ↓
Policy
 ↓
Risk
 ↓
Human Control
 ↓
Action
```

> **Karena semakin pintar AI-nya, semakin besar kebutuhan terhadap
> kontrolnya.**

---

> ⭐⭐ **Rantai tujuh langkah ini adalah kalimat yang sama dengan janji
> pembuka naskah 4** — *"Act selalu berada di bawah kontrol pengguna"* —
> tetapi kali ini dalam bentuk yang bisa dibangun. Dua belas naskah, dan ini
> pertama kalinya *Human Control* muncul sebagai **langkah di dalam alur
> eksekusi**, bukan sebagai nilai di halaman pembuka.

---

## HumanVerse X — Progress menurut pemilik

| Fase | Fokus | Status |
|---|---|---|
| 1 | Core Architecture | ✅ |
| 2 | Intelligence & Agents | ✅ |
| 3 | Human Intelligence | ✅ |
| 4 | Platform & Ecosystem | ✅ |
| 5 | Research Lab | ✅ |
| 6 | Developer Platform | ✅ |
| 7 | Data & AI Infrastructure | ✅ |
| **8** | **Security, Safety & Privacy** | 🔵 **Sekarang** |

Setelah Fase 8, fondasinya menjadi:

```
             HUMANVERSE X
                  │
      ┌───────────┼───────────┐
      │           │           │
   HUMAN       DATA        AI/AGENT
      │           │           │
      └───────────┼───────────┘
                  │
        SECURITY + PRIVACY
                  │
           HUMAN CONTROL
```

---

## Langkah berikutnya menurut pemilik

> Setelah ini, **Fase 9** yang paling logis adalah **HumanVerse Intelligence
> & Cognitive Architecture** — menyatukan seluruh data, memory, knowledge
> graph, behavior model, world model, reasoning, prediction, dan agent system
> menjadi **"otak" HumanVerse X yang benar-benar terintegrasi**.

---

> ⚠️ **Fase 9 di sini bukan Fase 9 di peta naskah 8.** Peta Phase 5–12 naskah
> 8 menempatkan **Phase 9 = Enterprise & Business Platform** (*Team Workspace ·
> Enterprise Admin · Family Mode · Subscription · Company Wellness · Revenue
> Platform*). *Intelligence & Cognitive Architecture* tidak ada di peta itu
> sama sekali.
>
> Dua kemungkinan, dan keduanya perlu dinyatakan: fase berikutnya **menyela**
> urutan peta (Enterprise mundur jadi Phase 10), atau petanya yang berubah.
> Ini pengulangan **E-63**/**E-64** di sumbu fase: nomor yang sama menunjuk
> isi yang berbeda. Sekali lagi, awalan seperti `S8.` menyelesaikannya.

> ⚠️ **✅ pada Fase 1–7 berarti "naskahnya selesai", bukan "dibangun".**
> Delapan baris bertanda ✅ dan 🔵 di tabel kemajuan, dengan **nol baris kode**
> di repo — itu konsisten dengan disiplin yang dipilih sejak awal (dokumen
> dulu, kode kemudian), tapi tabelnya sendiri tidak mengatakannya. Bertaut
> **A-24** / [#43](../../issues/43): ukur kemajuan terhadap **V0**, satu-
> satunya lingkup tertutup yang pernah ditetapkan. Terhadap V0, kemajuan kode
> tetap **0 %**.
