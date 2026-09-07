# 198 — Phase 13: Ikhtisar & HumanOS Core (naskah ketujuhbelas)

> Berkas ini merekam kata pemilik apa adanya (naskah ketujuhbelas, 7 Sep 2026).
> Merekam **§13.1–§13.2**.
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Posisi Phase 13

> Jika Phase 12 membuat HumanVerse mampu mensimulasikan kemungkinan masa depan,
> maka Phase 13 membuat seluruh kemampuan tersebut menjadi sebuah operating
> system AI pribadi.

| Fase | Kata kerja |
|---|---|
| Phase 9 | Think |
| Phase 10 | Perceive |
| Phase 11 | Act |
| Phase 12 | Simulate |
| **Phase 13** | **Operate** |

Target akhir:

```
                  HUMAN
                    │
                    ▼
              ┌───────────┐
              │ HumanOS   │
              │   Core    │
              └─────┬─────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
  Perception     Cognition     Agency
       │            │            │
       └────────────┼────────────┘
                    ▼
              DIGITAL TWIN
                    │
                    ▼
              WORLD MODEL
                    │
                    ▼
               SIMULATION
                    │
                    ▼
              DECISION CORE
                    │
                    ▼
              PERSONAL AI
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
     Apps         Agents       Devices
       │            │            │
       └────────────┼────────────┘
                    ▼
                REAL LIFE
```

> ⭐⭐⭐ **Peta 15 fase bertahan untuk naskah KEEMPAT.** §10.41, §11.64, dan
> §12.31 sama-sama menempatkan **Phase 13 = HumanOS**, dan naskah ini memang
> itu. Setelah enam sumbu penomoran yang bertabrakan, satu sumbu yang stabil
> empat naskah berturut-turut layak dicatat sebagai keberhasilan — **H-20**
> bertahan.

---

## §13.1 — Apa sebenarnya HumanOS?

HumanOS bukan sekadar aplikasi. Konsepnya: **lapisan intelligence yang menjadi
operating layer antara manusia, AI, aplikasi, data, agent, dan dunia nyata.**

Sehingga pengguna tidak perlu berpikir *"Saya harus membuka aplikasi X"*,
tetapi *"Saya ingin mencapai X"* — dan HumanOS menentukan bagaimana mencapainya.

Contoh: *"Saya ingin meningkatkan skill AI dalam 6 bulan."*

```
Understand Goal
      ↓
Analyze Digital Twin
      ↓
Skill Gap
      ↓
Simulate Strategies
      ↓
Create Roadmap
      ↓
Schedule
      ↓
Find Resources
      ↓
Create Projects
      ↓
Monitor Progress
      ↓
Adapt
```

> 🛑 **"HumanOS" kini punya ARTI KETIGA, dan dua di antaranya adalah tahap
> dalam dua rencana kanonik yang saling bersaing.**
>
> [`10-IDENTITAS.md`](10-IDENTITAS.md) sudah mencatat dua:
>
> | Arti | Sumber |
> |---|---|
> | Nama produk naskah **1** | `10-IDENTITAS.md` baris 53 |
> | Nama **tahap V5** | `10-IDENTITAS.md` baris 71 |
> | **Lapisan OS yang lahir di Phase 13** | **naskah ini** |
>
> Yang membuatnya lebih dari sekadar kata yang dipakai ulang: **V5 = HumanOS**
> berasal dari rencana **V0–V6**, dan **Phase 13 = HumanOS** berasal dari
> **peta 15 fase**. Keduanya adalah rencana kanonik yang sedang bertabrakan di
> **E-87 / H-13**. Satu kata sekarang menandai posisi berbeda di dua peta yang
> berbeda, dan tidak ada satu kalimat pun yang mengatakan apakah keduanya
> milestone yang SAMA.
>
> Kalau V0–V6 masih berlaku, naskah ini pada dasarnya adalah spesifikasi V5 —
> dan itu harus dinyatakan, bukan disimpulkan pembaca.

> 🛑 **V0–V6 tidak disebut, naskah KELIMA berturut-turut** (**E-87**). Empat
> naskah sudah dinilai "cukup lama untuk berhenti menyebutnya kelalaian";
> yang kelima menutup ruang itu sepenuhnya.

---

## §13.2 — HumanOS Core

> Ini adalah kernel dari HumanVerse.

Repository:

```
human-os/
├── kernel/
├── runtime/
├── identity/
├── state/
├── context/
├── memory/
├── capability/
├── permissions/
├── policy/
├── agency/
├── scheduling/
├── events/
├── intents/
├── workflows/
├── automation/
├── applications/
└── interfaces/
```

> 🛑 **Naskah ini memuat DUA pohon repositori `human-os/` yang BERBEDA, dan
> keduanya ditulis sebagai satu-satunya.** §13.2 (di atas) memberi **17
> direktori datar**; [§13.37](206-REPO-SUBPHASE-DOD-DAN-POSISI.md) memberi
> **13 direktori bersarang**. Perbandingan lengkapnya ada di berkas itu.
>
> Yang paling berkonsekuensi: **`capability/`, `agency/`, dan `events/` ada di
> §13.2 dan HILANG SEPENUHNYA di §13.37** — padahal §13.9 menjadikan Capability
> System primitif keamanan inti, dan §13.12 menjadikan Event Bus sebagai
> arsitekturnya. Dua benda yang naskah ini sebut fondasi tidak punya rumah di
> pohon repo versi keduanya.
>
> Ini pola yang sudah dicatat berulang: **naskah panjang selalu punya daftar
> ganda.** Jangan ditambal diam-diam — pilih satu, dan catat yang dibuang.

> 🛑 **`human-os/` adalah pohon repo BARU — H-10 (monorepo final) tergerus
> untuk keputusan KELIMA.** [#55](../../issues/55) sudah meninjau ulang H-10
> karena tiga pohon baru dari naskah 9, 10, 11; naskah 12 menambah satu lagi.
> Ini yang kelima. Pada titik ini pertanyaannya bukan lagi *"apakah H-10
> tergerus"* melainkan *"apakah H-10 masih ada"*.

---

## Catatan penomoran

Temuan di berkas `198`–`206` **sudah diberi nomor** `E-108`–`E-115` di
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) setelah naskah keenam belas
(Phase 12) mendarat di `41f553b`. Dua temuan terberat sudah jadi GitHub Issue:
[#90](../../issues/90) (**E-108**) dan [#91](../../issues/91) (**E-109**).
