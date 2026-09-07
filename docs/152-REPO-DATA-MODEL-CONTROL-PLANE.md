# 152 — §8.39–§8.43 Security Repository, Data Model, Event Model & Control Plane

> Berkas ini merekam kata pemilik apa adanya (naskah keduabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §8.39 — Security Architecture Repository

```
security/
│
├── identity/
├── authentication/
├── authorization/
├── permissions/
├── consent/
├── policy-engine/
├── risk-engine/
├── data-vault/
├── encryption/
├── secrets/
├── key-management/
│
├── privacy/
│   ├── data-classification/
│   ├── minimization/
│   ├── retention/
│   ├── deletion/
│   ├── export/
│   └── consent/
│
├── ai-safety/
│   ├── input-safety/
│   ├── output-safety/
│   ├── prompt-injection/
│   ├── tool-safety/
│   ├── pii-detection/
│   └── sensitive-domain/
│
├── agent-security/
│   ├── sandbox/
│   ├── capability/
│   ├── trust/
│   ├── signing/
│   └── isolation/
│
├── threat-modeling/
├── red-team/
├── incident-response/
├── kill-switch/
├── audit/
└── compliance/
```

---

> 🛑 **Pohon tingkat-atas kelima — dan H-10 tergerus lagi.** Butir **E-27**
> ditutup sebagai **H-10** ketika naskah 5 §4 menetapkan monorepo final.
> Sejak itu: `research/` (naskah 9) · `developer-platform/` (naskah 10) ·
> `data-platform/` (naskah 11) · dan sekarang `security/`. **Empat naskah
> berturut-turut menambah pohon sendiri, tak satu pun menempatkannya di dalam
> monorepo.** Lihat **E-66** / [#55](../../issues/55), yang menahan Sprint 0
> tugas 0.1.

> ⚠️ **`consent/` muncul dua kali di dalam pohon yang sama** — sekali di
> tingkat atas, sekali di dalam `privacy/`. Dua folder dengan nama sama di
> satu repo akan berisi hal berbeda cepat atau lambat, dan tidak ada yang tahu
> mana yang benar. Ini pola **E-13** (tabel ≠ folder) dan **E-54** (dua pohon
> `research/`) yang berulang untuk ketiga kalinya.

> ⚠️ **Enam kelompok, 30 folder, nol berkas.** Untuk membandingkan: seluruh
> spesifikasi V0 yang sudah selesai muat di **8 berkas**. Struktur ini benar
> untuk sistem yang sudah jadi; sebagai titik awal ia adalah 30 folder kosong
> yang harus dijaga tetap relevan. Bertaut **A-23** / [#37](../../issues/37).

---

## §8.40 — Security Data Model

Tambahkan entity:

```
users
identities
devices
sessions

permissions
permission_grants
permission_requests

consents
consent_versions
consent_events

policies
policy_rules
policy_decisions

risk_assessments
risk_events

security_events
security_incidents

agent_security_profiles
agent_capabilities
agent_trust_scores

audit_logs
data_access_logs

deletion_requests
data_export_requests
```

---

> 🛑 **Dua puluh empat entity, dan empat di antaranya sudah ada — sisanya
> 20 tabel baru untuk skema V0 yang berisi 23 tabel.**
>
> | | Jumlah |
> |---|---|
> | Sudah ada di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) | **4** — `users`, `permissions`, `consents`, `audit_logs` |
> | Baru | **20** |
> | Skema V0 sekarang | 23 tabel |
> | Skema V0 + Fase 8 penuh | **43 tabel** |
>
> Mengerjakan Fase 8 seutuhnya berarti **hampir menggandakan skema V0**, dan
> §8.44 memberinya **8 sprint** sendiri — sementara seluruh V0 adalah 7 sprint
> dalam 4–6 minggu (**A-17** / [#3](../../issues/3)). Kalau Fase 8 dikerjakan
> penuh lebih dulu, V0 tidak pernah dimulai; kalau tidak, seseorang harus
> memilih mana yang minimum. Belum ada yang memilih. Lihat **A-25** /
> [#58](../../issues/58).
>
> Yang **sudah cukup untuk V0 tanpa tabel baru sama sekali**: `users` +
> `permissions` + `consents` + `audit_logs` sudah menopang empat agent, empat
> scope memory, dan risk gate. Yang paling murah ditambahkan sekarang karena
> mahal ditambahkan nanti: `consents.purpose` (**B-22**) dan `sessions`.

> ⚠️ **`agent_capabilities` menduplikasi `agent_tools`** yang sudah ada, dan
> `permission_grants` vs `permissions` vs `permission_requests` adalah tiga
> tabel untuk satu gagasan. Yang biasanya benar: satu tabel `permissions`
> (keadaan sekarang) + satu tabel peristiwa (`permission_events`) — bukan
> tiga.

---

## §8.41 — Security Event Model

Canonical event:

```yaml
SecurityEvent:
  id:
  timestamp:
  actor:
  actor_type:
  action:
  resource:
  resource_type:
  risk_level:
  policy:
  decision:
  ip:
  device:
  correlation_id:
```

Dengan ini kita dapat melakukan:

```
Security Analytics
+
Forensics
+
Audit
+
Compliance
```

---

> ⭐ **Empat field yang tidak pernah ada dan langsung berguna**: `risk_level`
> dan `decision` membuat setiap keputusan bisa dihitung ulang belakangan
> (*"berapa kali policy menolak agent ini minggu ini"*); `correlation_id`
> naik ke tingkat atas — di naskah 11 ia terkubur di `metadata` — sehingga
> satu permintaan pengguna bisa dirangkai melintasi agent, tool, dan
> penyimpanan; `device` melengkapi jejak masuk.

> 🛑 **Ini bukan amplop event keempat — ini model event *kedua*, dan §8.26
> memasukkannya ke event bus yang sama.**
>
> | | Amplop biasa ([`../spec/03`](../spec/03-EVENT-CONTRACTS.md)) | SecurityEvent §8.41 |
> |---|---|---|
> | Bentuk | `event_type` + `payload` | `action` + `resource` |
> | Waktu | `occurred_at` **dan** `recorded_at` | `timestamp` (yang mana?) |
> | Versi | `schema_version` | ❌ tidak ada |
> | Anti-ganda | `idempotency_key` | ❌ tidak ada |
> | Pemilik data | `user_id` | ❌ hanya `actor` |
>
> Dua bentuk berbeda di satu bus berarti setiap consumer harus tahu lebih dulu
> jenis event mana yang sedang dibacanya — persis yang dihindari dengan
> memakai amplop bersama. Dua jalan keluar: **(a)** security event memakai
> amplop yang sama dengan `event_type: "permission.denied"` dan sisanya di
> `payload`, atau **(b)** ia diakui sebagai aliran terpisah dengan bus sendiri.
> Yang (a) lebih murah dan tidak kehilangan apa pun.
>
> **`user_id` yang hilang adalah yang paling menentukan.** `audit_logs` di
> spesifikasi memisahkan `actor_id` (*siapa yang bertindak*) dari `user_id`
> (*data siapa yang disentuh*) — dan pemisahan itu persis yang dibutuhkan
> begitu **Coaches** (**C-10**) atau **Company Wellness** (**C-12**) ada:
> aktor dan pemilik data bukan orang yang sama. `resource` tidak
> menggantikannya. Lihat **E-69** / [#63](../../issues/63).

> 🔴 **`ip` mentah, sementara spesifikasi menyimpan `ip_hash`.** Itu keputusan
> yang sengaja diambil di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md): hash
> cukup untuk mengenali pola *"masuk dari tempat yang tidak biasa"* tanpa
> menyimpan lokasi orang. Menyimpan IP mentah di tabel yang **tidak ikut
> terhapus** (§8.34 *Preserve evidence*, dan §8.38 tidak menyebut tabel log
> sama sekali) menambah data pribadi permanen di satu-satunya tempat yang
> tidak bisa dibersihkan pengguna. Bertaut **C-9** / [#22](../../issues/22).

---

## §8.42 — HumanVerse Security Control Plane

> Ini konsep yang **sangat penting**. Pisahkan:

**Data Plane**

```
User data
AI inference
Agent execution
Applications
```

dengan **Security Control Plane**

```
Identity
Permission
Policy
Consent
Risk
Audit
Security monitoring
Kill switch
```

Sehingga:

```
             CONTROL PLANE
      ┌─────────────────────────┐
      │ Identity                │
      │ Permission              │
      │ Policy                  │
      │ Consent                 │
      │ Risk                    │
      │ Audit                   │
      │ Security                │
      └────────────┬────────────┘
                   │
            controls access
                   │
                   ▼
             DATA PLANE
```

> Ini harus menjadi **boundary arsitektur yang sangat kuat**.

---

> ⭐⭐ **Ini yang memberi §8.35 gigi.** *"Bahkan orchestrator tidak boleh
> menonaktifkan kill switch sendiri"* hanya bisa ditepati kalau kill switch
> berada di sisi lain sebuah batas yang tidak bisa diseberangi kode agent.
> Control Plane adalah batas itu. Ia juga menjelaskan kenapa `security/`
> pantas jadi pohon tersendiri (§8.39) meski itu menggerus H-10: ia memang
> **tidak boleh** bisa diimpor oleh kode agent.
>
> ⭐ Dan **Consent akhirnya masuk daftar** — di sini ia sejajar dengan
> Identity, Permission, Policy, Risk, dan Audit, sementara di Security Fabric
> §8.3 ia tidak ada. Daftar delapan komponen inilah yang sebaiknya dipakai.

> ⚠️ **Diagramnya membuang satu**: teks menyebut delapan komponen (termasuk
> `Security monitoring` dan `Kill switch`), gambarnya menampilkan tujuh dan
> menggabungkan dua terakhir jadi `Security`. Perbedaan kecil, dicatat supaya
> tidak dikira salah salin — pola yang sama seperti **G-4**/**G-5**.

> ⚠️ **Untuk V0 ini bukan dua kluster, melainkan dua modul.** Pemisahan
> control plane biasanya dibayangkan sebagai layanan terpisah; di modular
> monolith V0 ia cukup berupa **batas modul yang ditegakkan CI** — persis
> mekanisme yang sudah ada di
> [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md). Aturan barunya satu
> kalimat: *tidak ada modul agent yang boleh mengimpor `security/`; ia hanya
> boleh dipanggil lewat gerbang.*

---

## §8.43 — HumanVerse Security Stack

```
┌──────────────────────────────────────────┐
│              USER / HUMAN                │
└───────────────────┬──────────────────────┘
                    │
             HUMAN INTERFACE
                    │
┌───────────────────▼──────────────────────┐
│             AI / AGENT LAYER             │
└───────────────────┬──────────────────────┘
                    │
             SAFETY GATEWAY
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   Permission    Policy       Risk
        │           │           │
        └───────────┼───────────┘
                    ▼
             SECURITY FABRIC
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Data Vault    Tool       External API
        │
        ▼
┌──────────────────────────────────────────┐
│       HUMANVERSE DATA PLATFORM           │
└──────────────────────────────────────────┘
```

---

> ⭐ **`SAFETY GATEWAY` sebagai satu pintu adalah bentuk paling ringkas dari
> seluruh fase ini** — dan ia yang paling mungkin benar-benar dibangun di V0,
> karena ia satu tempat, bukan tiga puluh folder.
>
> ⚠️ Perhatikan bahwa **Consent tidak muncul lagi** di antara Permission,
> Policy, dan Risk. Empat diagram di naskah ini (§8.3, §8.18, §8.42, §8.43)
> memberi empat daftar komponen berbeda; hanya §8.18 dan §8.42 yang memuat
> Consent. Yang paling lengkap adalah §8.42.
