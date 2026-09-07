# 162 — §9.27–§9.31 Cognitive Orchestrator, Runtime, State Machine, Request & Context Object

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.27 — Cognitive Orchestrator

```
                  USER REQUEST
                       │
                       ▼
              ┌─────────────────┐
              │ COGNITIVE       │
              │ ORCHESTRATOR    │
              └────────┬────────┘
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Context          Memory          Understanding
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                  Reasoning
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Prediction        Simulation
              │                 │
              └────────┬────────┘
                       ▼
                    Decision
                       │
                       ▼
                 Recommendation
                       │
                       ▼
                    Action
```

---

> ⚠️ **Tidak ada Policy/Risk di diagram ini** — padahal §9.29 memasukkannya
> sebagai keadaan wajib (`POLICY_CHECK`), dan §9.20 menjadikannya satu dari
> tiga jalur. Ini pola yang sama seperti di naskah 12: diagram ikhtisar
> melewatkan komponen yang bagian rincinya wajibkan (§8.3 tanpa Consent).
> Yang berlaku sebaiknya versi rinci — **§9.29**.

---

## §9.28 — Cognitive Runtime

> Subsystem baru: `cognitive-runtime/`

```
cognitive-runtime/
│
├── orchestrator/
├── intent/
├── context/
├── state/
├── memory/
├── understanding/
├── knowledge/
├── reasoning/
├── planning/
├── prediction/
├── simulation/
├── decision/
├── recommendation/
├── agency/
├── feedback/
└── evaluation/
```

---

> ⚠️ **Pohon ini berbeda dengan §9.38**, yang menempatkan `cognitive-runtime/`
> sebagai **satu dari lima belas** kelompok di dalam `intelligence/` — bukan
> sebagai pembungkus semuanya. Dua pohon di satu naskah, pola **E-54** (dua
> pohon `research/`) yang berulang. Yang lebih rinci dan lebih baru dalam
> urutan naskah adalah §9.38.

---

## §9.29 — Cognitive State Machine

```
RECEIVED
   ↓
UNDERSTANDING
   ↓
CONTEXT_LOADING
   ↓
RETRIEVING
   ↓
REASONING
   ↓
PLANNING
   ↓
POLICY_CHECK
   ↓
DECISION
   ↓
ACTION
   ↓
OBSERVATION
   ↓
LEARNING
```

Jika terjadi masalah:

```
FAILED · WAITING_FOR_USER · BLOCKED · REQUIRES_CONFIRMATION
```

---

> ⭐⭐ **Ini menutup E-45 / [#42](../../issues/42) — persis di tempat yang
> diminta.** Butir itu mencatat bahwa alur percakapan sembilan langkah Layer 29
> (naskah 7) melewati Safety, Risk, dan Policy sepenuhnya, dan mengusulkan
> gerbangnya disisipkan **setelah Planning, sebelum Execution**. Bandingkan:
>
> | Layer 29 (naskah 7) | §9.29 (naskah 13) |
> |---|---|
> | User Input | `RECEIVED` |
> | Intent Detection | `UNDERSTANDING` |
> | Context Retrieval | `CONTEXT_LOADING` |
> | Memory Retrieval | `RETRIEVING` |
> | — | ⭐ `REASONING` |
> | Planning | `PLANNING` |
> | **— (tidak ada)** | ⭐⭐ **`POLICY_CHECK`** |
> | — | ⭐ `DECISION` |
> | Agent Execution | `ACTION` |
> | Feedback | `OBSERVATION` |
> | Memory Update | `LEARNING` |
>
> `POLICY_CHECK` berdiri **tepat setelah PLANNING dan sebelum DECISION/ACTION**
> — urutan yang diusulkan, tanpa perubahan. Ditambah `REQUIRES_CONFIRMATION`
> sebagai keadaan tersendiri, yang membuat §8.17 punya tempat di runtime.

> ⚠️ **Tetapi keselamatan jalur MASUK tidak ada.** §8.20 mewajibkan konten
> eksternal melewati `Content Classifier → Untrusted Context → Policy Boundary`
> **sebelum** sampai ke agent. Di mesin keadaan ini, apa pun yang masuk
> langsung dari `RECEIVED` ke `UNDERSTANDING`. Untuk V0 belum ada permukaannya
> (tidak ada tool yang membaca email/kalender/web), tapi urutannya perlu
> ditetapkan sekarang — keadaan tidak bisa disisipkan diam-diam nanti.
> Ini juga separuh dari [#21](../../issues/21): jurnal masuk lewat jalur ini.

> ⚠️ **`Response` tidak punya keadaan.** Layer 29 punya langkah *Response*;
> di sini alurnya `ACTION → OBSERVATION`. Kemungkinan besar jawaban ke pengguna
> **adalah** aksinya — kalau begitu, sebaiknya ditulis, karena "action" pada
> naskah 12 berarti sesuatu yang berisiko dan butuh gerbang.

---

## §9.30 — Cognitive Request Object

```json
{
  "request_id": "req_001",
  "user_id": "user_001",
  "intent": "career_decision",
  "context": {},
  "state": {},
  "memory_scope": [ "career", "learning", "goals" ],
  "reasoning_mode": "deep",
  "risk_level": "R2"
}
```

> Ini menjadi **contract antara subsystem**.

---

> ⭐ **`risk_level: "R2"` memakai notasi naskah 12 apa adanya** — pertama
> kalinya sebuah naskah memakai penomoran naskah sebelumnya tanpa
> mengubahnya. ⚠️ Sayangnya itu justru menegaskan **E-77**: di sini `R2`
> berarti risiko, sementara §9.26 memakai `Level 2` untuk otonomi. Satu
> dokumen, dua tangga, dan hanya salah satunya diberi awalan.

> ⭐ **`memory_scope: ["career","learning","goals"]` menguatkan jawaban
> [#33](../../issues/33):** scope adalah **lapisan di atas** enam `kind`, bukan
> penggantinya — di sini ia dipakai untuk memilih memori mana yang diambil,
> di §8.14 untuk memilih siapa yang boleh membacanya. Satu kolom, dua kegunaan,
> keduanya sah.

> ⚠️ **`reasoning_mode: "deep"` adalah nilai keempat yang tak berpadanan.**
> §9.20 memberi tiga jalur (*Fast · Cognitive · High-stakes*); `deep` bukan
> salah satunya. Kalau `deep` = *Cognitive Path*, samakan namanya sekarang —
> nama mode akan masuk ke basis data dan log, dan nama yang berbeda untuk hal
> yang sama akan bertahan bertahun-tahun.

---

## §9.31 — Cognitive Context Object

> Daripada setiap agent mengambil data sendiri-sendiri:

```json
{
  "user": {},
  "state": {},
  "goals": [],
  "recent_events": [],
  "relevant_memories": [],
  "preferences": [],
  "constraints": [],
  "environment": {},
  "uncertainties": []
}
```

> Context Engine membuat **context package**. Agent menerima context yang
> sudah:

```
filtered · scoped · ranked · sanitized
```

> Ini sangat mengurangi **data leakage**.

---

> ⭐⭐⭐ **Ini menutup E-71 / [#62](../../issues/62) — dan caranya lebih baik
> daripada kedua pilihan yang saya ajukan.**
>
> Issue itu mencatat dua model akses yang bertabrakan di naskah 12: §8.6
> memberi agent **READ tingkat tabel**, §8.11 menyatakan agent **tidak pernah
> menerima baris**. Saya mengusulkan keduanya dilapis. Kalimat pembuka §9.31
> menyelesaikannya dengan cara ketiga:
>
> > *"Daripada setiap agent mengambil data sendiri-sendiri…"*
>
> **Agent tidak mengambil data sama sekali.** Context Engine yang mengambil,
> lalu menyerahkan paket. Dengan itu kedua bagian naskah 12 jadi masuk akal
> sekaligus:
>
> ```
> §8.6  permissions(agent, scope)  → menentukan apa yang BOLEH MASUK paket
> §8.11 minimum necessary data     → menentukan bentuk isi paket
> §9.31 context package            → satu-satunya yang diterima agent
> ```
>
> Keuntungannya besar dan tidak disebutkan: izin diperiksa **satu kali, di satu
> tempat**, bukan di setiap pemanggilan tool oleh setiap agent. Itu jauh lebih
> mudah dibuat benar — dan jauh lebih mudah dicatat untuk `data_access_logs`.
>
> ⚠️ Satu hal yang harus ditulis supaya penutupan ini sah: **Context Engine
> adalah tempat pemeriksaan izin**, dan agent tidak punya kredensial untuk
> menembusnya. Kalau agent masih bisa memanggil tool baca sendiri, paket ini
> hanya kenyamanan, bukan pengaman.

> ⭐ **`uncertainties` sebagai field bawaan adalah keputusan yang jarang
> dibuat.** Sebagian besar sistem mengirim apa yang diketahui; ini juga
> mengirim **apa yang tidak diketahui**. Itu yang membuat §9.33 bisa bekerja —
> dan itu juga jawaban untuk **B-14**: sinyal konteks yang mati muncul di sini
> sebagai ketidakpastian, bukan sebagai ketiadaan yang senyap.

> ⭐ **`sanitized` menyambung ke §8.20.** Konten tak tepercaya (email, jurnal
> yang ditempel dari mana saja) dibersihkan **saat paket dibangun** — satu
> tempat, bukan di setiap agent. Itu tempat yang benar untuk pertahanan
> prompt injection.

> ⚠️ **`constraints` belum pernah punya sumber.** Delapan field lain punya
> tabel atau mesin yang menghasilkannya; batasan (waktu, uang, kesehatan,
> kewajiban) tidak pernah dikumpulkan di mana pun dalam tiga belas naskah.
> Padahal ia yang membuat rekomendasi realistis — saran belajar 3 jam/hari
> kepada orang yang bekerja dua sif adalah saran yang salah, bukan saran yang
> ambisius.
