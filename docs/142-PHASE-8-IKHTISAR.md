# 142 — Phase 8: AI Safety, Security & Privacy (ikhtisar naskah keduabelas)

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Penomoran yang dipakai di berkas rapi

Naskah keduabelas menomori bagiannya **1–46** — nomor yang sudah dipakai
naskah 4 (§1–§58) dan naskah 5 (§1–§34). Supaya tidak menambah tabrakan
penomoran keenam (**E-59**, **E-63**, **E-64**), berkas rapi memakai awalan
fase seperti naskah 11: **`§8.1`–`§8.46`**, di mana `§8.16` berarti *bagian 16
naskah keduabelas*. Ini keputusan penulisan, bukan kata pemilik.

---

## Posisi pemilik

> Kita masuk ke salah satu fase **paling penting** dalam arsitektur
> HumanVerse X.

> Kalau fase 5–7 membangun **otak, data, dan infrastruktur**, maka fase 8
> membangun **sistem imun + pagar pengaman + governance**.

> Karena HumanVerse akan memproses data manusia yang sangat luas — kebiasaan,
> kesehatan, keuangan, lokasi, hubungan sosial, pekerjaan, preferensi, dan
> keputusan — maka **security tidak boleh menjadi fitur tambahan**.

> **Security, privacy, safety, dan governance harus menjadi bagian dari DNA
> HumanVerse.**

---

## §8.1 — Tujuan Fase 8

```
                    HUMANVERSE X
                         │
             ┌───────────┴───────────┐
             │                       │
        INTELLIGENCE              AGENTS
             │                       │
             └───────────┬───────────┘
                         │
                ┌────────▼────────┐
                │  SAFETY LAYER   │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │  POLICY ENGINE  │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
      SECURITY        PRIVACY        GOVERNANCE
          │              │              │
          └──────────────┼──────────────┘
                         │
                  HUMAN CONTROL
```

Prinsip utamanya:

> ## AI tidak boleh memiliki kekuasaan melebihi izin yang diberikan manusia.

---

> ⭐ **Ini menutup butir A-16 dan G-3 secara tidak langsung.** Sejak naskah 3,
> *Data Governance* dijanjikan sebagai lapisan tapi tidak pernah punya tempat
> (**G-3**), dan **A-16** menanyakan apakah ia jadi Layer sendiri. Diagram di
> atas menjawabnya: **Governance berdiri sejajar dengan Security dan Privacy**,
> ketiganya di bawah Policy Engine. Itu penempatan, bukan sekadar isi.

---

## §8.2 — Security Philosophy: Zero Trust

HumanVerse memakai prinsip **Zero Trust**:

> Tidak ada komponen yang **otomatis** dipercaya.

```
Agent A
   │
   ├── Who are you?
   ├── What are you trying to do?
   ├── What data do you need?
   ├── What permission do you have?
   ├── What risk level?
   ├── Is this action allowed?
   └── Should human confirmation be required?
```

Jadi bukan:

```
Agent → Database
```

tetapi:

```
Agent
  ↓
Identity
  ↓
Authentication
  ↓
Authorization
  ↓
Permission Engine
  ↓
Policy Engine
  ↓
Risk Engine
  ↓
Audit
  ↓
Database / Tool / Action
```

---

> ⭐⭐ **Rantai sembilan langkah ini adalah bentuk terkuat dari janji
> "Act selalu di bawah kontrol pengguna"** yang dibuka naskah 4 dan belum
> pernah punya urutan lengkap. Bandingkan dengan tiga versi sebelumnya:
>
> | Sumber | Rantai |
> |---|---|
> | naskah 4 §17 | Safety Classifier → Risk Engine → Policy Engine |
> | [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) risk gate | risk_level → requires_confirmation → permissions → jalankan & catat |
> | naskah 12 §8.2 | Identity → Authn → Authz → Permission → Policy → Risk → Audit |
>
> Yang **baru dan benar** di sini: `Identity` dan `Authentication` di depan
> (tiga naskah sebelumnya mulai dari agent yang sudah dianggap dikenal), dan
> `Audit` sebagai langkah **sebelum** aksi, bukan sesudahnya.
>
> ⚠️ Satu perbedaan urutan yang perlu diputuskan: di sini **Policy sebelum
> Risk**, di naskah 4 §17 **Risk sebelum Policy**, dan di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> risk dihitung lebih dulu lalu dipakai policy. Urutan naskah 4 dan spec lebih
> masuk akal — Policy Engine di §8.18 sendiri **menerima `risk` sebagai
> masukan**, jadi risk harus sudah dihitung sebelum policy memutuskan. Diagram
> §8.18 memang menempatkan Risk sebelum Policy. Dua diagram di naskah yang
> sama, dua urutan; yang dipakai sebaiknya versi §8.18.

---

## §8.3 — Security Architecture: HumanVerse Security Fabric

```
                         HUMANVERSE
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        Applications       AI Agents        APIs
             │                │                │
             └────────────────┼────────────────┘
                              │
                     SECURITY FABRIC
                              │
       ┌──────────┬───────────┼───────────┬───────────┐
       │          │           │           │           │
   Identity   Permission   Policy       Risk       Audit
       │          │           │           │           │
       └──────────┴───────────┼───────────┴───────────┘
                              │
                    Data / Tools / Actions
```

---

> ⭐ **Lima komponen Security Fabric adalah daftar tertutup pertama** untuk
> lapisan keamanan. Sebelum ini, komponen keamanan tersebar sebagai
> *Permission Engine* (naskah 4 §15), *Risk Engine* (§16), *Safety Layer*
> (§17), *Audit Trail* (§45), dan *Consent* (Layer 25) tanpa pernah disebut
> sebagai satu kesatuan yang punya nama.
>
> ⚠️ **Consent tidak ada di antara lima komponen itu** — padahal §8.9
> menjadikannya *engine* tersendiri, dan diagram §8.18 memasukkannya ke dalam
> rantai keputusan (`Identity → Permission → Consent → Risk → Policy`).
> Sekali lagi dua diagram di naskah yang sama tidak sepakat. Karena §8.9
> memberi Consent bentuk paling lengkap di seluruh dua belas naskah, ia
> semestinya jadi **komponen keenam** di Security Fabric.

---

## Yang membedakan naskah ini dari sebelas naskah sebelumnya

Naskah 8 memperkirakan Phase 8 sebagai **"AI Safety & Ethics Framework,
30+ dokumen"** dengan enam butir: *Consent Framework · Privacy Vault ·
Explainable AI · Safety Guardrails · **Bias Detection** · **Human Override***.

Yang datang jauh lebih besar dari itu — seluruh disiplin **security** ikut
masuk (Zero Trust, Identity, Authentication, Supply Chain, Red Team, Incident
Response, Kill Switch, Control Plane), dan judulnya berubah dari
*"AI Safety & **Ethics**"* menjadi *"AI Safety, **Security** & Privacy"*.

> 🛑 **Tetapi dua butir yang tidak datang justru dua yang paling penting
> untuk dicatat.** Butir **E-53** menyimpulkan bahwa dari enam butir Phase 8,
> empat sudah ditulis di tempat lain dan **hanya *Bias Detection* dan *Human
> Override* yang benar-benar baru**. Keduanya **tidak muncul satu kali pun**
> di 46 bagian naskah ini. Lihat butir **G-8**.
