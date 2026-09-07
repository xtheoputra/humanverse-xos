# 149 — §8.28–§8.31 Agent Trust, Sandbox, Supply Chain & Secure AI Lifecycle

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.28 — Agent Reputation & Trust

> Ketika marketplace dibangun, agent third-party **tidak boleh semuanya
> dianggap sama**.

Setiap agent mempunyai:

```
Trust Score
Security Score
Permission Scope
Developer Reputation
Evaluation Score
Incident History
Version History
```

Contoh:

```
Agent: Personal Finance Coach

Trust:
████████░░ 82%

Security:
A

Permissions:
Medium

Incidents:
0

Verified:
✓
```

---

> ⭐ **`Incident History` adalah field yang paling berat dan paling benar.**
> Ia berarti kesalahan sebuah agent **menempel padanya**, dan pada
> developernya lewat `Developer Reputation`. Itu satu-satunya mekanisme di
> dua belas naskah yang memberi konsekuensi kepada penulis agent, bukan hanya
> kepada agentnya.

> ⚠️ **Tujuh atribut di sini vs lima butir checklist review DP-L18** (*Security ·
> Permission · Stability · Documentation · Testing*). Hanya *Security* dan
> *Permission* yang muncul di keduanya; *Stability*, *Documentation*, dan
> *Testing* tidak punya skor, dan *Trust*, *Developer Reputation*,
> *Incident History*, *Version History* tidak punya butir review. Dua daftar
> yang mengurus hal yang sama dengan anggota berbeda — pola yang sama seperti
> **E-48** dan **E-54**.

> ⚠️ **Tidak satu pun dari tujuh skor punya rumus, dan `Security: A` adalah
> skala kelima.** Butir **B-15** mencatat bahwa lima model angka **pengguna**
> tidak punya rumus; sekarang angka **agent** menyusul. `Trust: 82%` yang
> ditampilkan di marketplace adalah angka yang akan dipakai orang untuk
> memutuskan — kalau ia tidak punya rumus, ia adalah tebakan yang terlihat
> seperti pengukuran. Yang **sudah** punya dasar: `Evaluation Score` bisa
> diambil dari `evaluation.gates` di
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md), dan `Incidents` bisa dihitung
> dari `security_incidents` (§8.40).

---

## §8.29 — Agent Sandbox

> Third-party agent harus berjalan dalam **sandbox**.

```
Marketplace Agent
       ↓
Sandbox
       ↓
Restricted Tools
       ↓
Restricted Network
       ↓
Restricted Memory
       ↓
Restricted Data
```

Jangan pernah memberikan:

```
full database access
root access
arbitrary filesystem
unrestricted network
```

kepada agent marketplace.

---

> ⭐ **`Restricted Network` menutup lubang yang tidak pernah disebut.**
> Sebelas naskah membatasi **data apa** yang boleh dibaca agent; tak satu pun
> membatasi **ke mana agent boleh mengirim**. Agent dengan izin baca yang
> sempit tetapi jaringan bebas bisa mengirim apa pun yang dibacanya ke server
> penulisnya — itu `Data exfiltration` di §8.27, dan hanya pembatasan jaringan
> yang menghentikannya.

> ⚠️ **"Sandbox" sekarang berarti dua hal berbeda.** DP-L14 (naskah 10) adalah
> **sandbox pengujian**: data palsu, dipakai developer **saat membangun**,
> supaya tidak pernah menyentuh data orang sungguhan. §8.29 adalah **sandbox
> runtime**: tool, jaringan, memori, dan data dibatasi **saat berjalan di
> produksi**, di atas data sungguhan.
>
> Keduanya diperlukan dan tidak saling menggantikan — tapi keduanya bernama
> sama. Ini pola **E-32** (*"Agent Factory"* tiga makna) dan **E-22**
> (*Tool Registry* tiga tempat) yang berulang. Di berkas rapi sebaiknya
> ditulis **sandbox-uji** dan **sandbox-jalan**.

> 🛑 **Tiga hal termahal dari menjalankan marketplace masih belum disentuh
> setelah dua belas naskah** — dan naskah inilah yang seharusnya
> menyentuhnya: **perjanjian pemroses data** dengan developer, **jalur
> banding** ketika agent ditolak atau dicabut, dan **tanggung jawab** ketika
> agent orang lain merugikan pengguna Anda. §8.28 dan §8.29 memperkuat sisi
> teknis A-15/C-7 lagi; sisi hukumnya tetap kosong. Lihat
> [#24](../../issues/24).

---

## §8.30 — Supply Chain Security

Karena HumanVerse adalah ecosystem:

```
Dependency scanning
Container scanning
SBOM
Code signing
Artifact signing
Secret scanning
SAST
DAST
SCA
Image scanning
License compliance
```

Pipeline:

```
Code
 ↓
SAST
 ↓
Dependency Scan
 ↓
Secret Scan
 ↓
Build
 ↓
Container Scan
 ↓
Sign Artifact
 ↓
Deploy
```

---

> ⭐ **`Secret scanning` adalah satu-satunya butir di daftar ini yang berharga
> sejak commit pertama** — dan biayanya nyaris nol. Repo ini sekarang berisi
> 128 dokumen tanpa kode; begitu kode pertama masuk, kunci API model, kredensial
> basis data, dan token webhook akan ikut lewat. Sisanya (SBOM, DAST, SCA,
> container scanning, license compliance) baru berarti setelah ada artefak
> yang dibangun dan dirilis.

> ⚠️ **`Code signing` dan `Artifact signing` di sini bertaut dengan `signed
> manifest` §8.5** — ketiganya bagian dari rantai yang sama, tapi ditulis di
> dua tempat terpisah tanpa saling merujuk. Yang menentukan untuk marketplace:
> **manifest yang lolos review harus yang sama dengan manifest yang
> dijalankan**. Tanpa itu, review DP-L18 menjaga versi yang tidak pernah
> berjalan.

---

## §8.31 — Secure AI Development Lifecycle (SAIDLC)

```
Idea
 ↓
Threat Modeling
 ↓
Architecture
 ↓
Data Risk Assessment
 ↓
Implementation
 ↓
Security Testing
 ↓
AI Evaluation
 ↓
Red Team
 ↓
Human Approval
 ↓
Deployment
 ↓
Monitoring
 ↓
Incident Response
 ↓
Continuous Improvement
```

---

> ⭐ **`Human Approval` sebagai langkah wajib sebelum Deployment adalah
> penerapan prinsip §8.46 pada proses, bukan hanya pada aksi agent.** Manusia
> mengendalikan bukan cuma apa yang dilakukan AI, tapi juga apa yang boleh
> dirilis.

> ⚠️ **Tiga belas langkah untuk setiap fitur adalah proses tim, dijalankan
> oleh satu orang.** Butir yang sama sudah dicatat untuk DP-L18: reviewer
> agent adalah orang yang menulis platformnya. Di sini `Threat Modeling`,
> `Red Team`, dan `Human Approval` semuanya akan dijalankan oleh orang yang
> sama yang menulis kodenya. Itu tidak apa-apa untuk sekarang — tapi harus
> **ditulis**, supaya kelak tidak dikira sudah ada pemeriksaan pihak kedua.
> Bertaut **A-17** / [#3](../../issues/3) dan **B-18**.

> ⚠️ **Ini lapisan pengembangan ketiga.** Layer 22 naskah 7 (*Engineering
> Standards*), §94 *Development Lifecycle* blueprint, dan sekarang SAIDLC.
> Ketiganya menjelaskan cara kerja yang sama dengan langkah berbeda — pola
> **E-47** (tiga lapisan evaluasi). Perlu satu tempat kanonik.
