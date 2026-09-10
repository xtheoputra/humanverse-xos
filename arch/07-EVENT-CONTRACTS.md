# 07 — Event Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“event contracts”* naskah 24. Melanjutkan
> [#38](../../issues/38) dan [K-3](../docs/KEPUTUSAN-DIDELEGASIKAN.md) ·
> [K-10](../docs/KEPUTUSAN-DIDELEGASIKAN.md); menutup bagian **G-14** dari
> [#98](../../issues/98) dan [#149](../../issues/149).

---

## §1 Satu amplop — dan tidak ada yang kedua

[K-10](../docs/KEPUTUSAN-DIDELEGASIKAN.md) sudah memutuskannya; berkas ini
menegakkannya lintas dua puluh fase. Amplopnya milik
[`../spec/03`](../spec/03-EVENT-CONTRACTS.md), tidak diubah:

```
id · event_type · schema_version · user_id · occurred_at · recorded_at
source · idempotency_key · subject_type · subject_id · payload
```

| Yang pernah punya bentuk sendiri | Menjadi |
|---|---|
| `SecurityEvent` §8.41 (`action`, `resource`, bentuk terpisah) | `event_type: security.*`; `action` & `resource` turun ke `payload` |

🛑 **Alasan penolakan amplop kedua membalik arah keberatannya:** empat medan
yang **hilang** dari `SecurityEvent` — `schema_version`, `idempotency_key`,
`user_id`, dan pemisahan `occurred_at`/`recorded_at` — justru medan yang
membuat sebuah event bisa **diaudit**. Dan security event adalah jenis yang
**paling mungkin diaudit**.

⚠️ **`user_id` boleh kosong** untuk event yang subjeknya bukan pemegang akun
(`spatial.person_entered`, `robot.human_detected`) — tetapi ia kosong dengan
cara yang dinyatakan: `data_subject` di sisi tabelnya
([`06`](06-DATA-ARCHITECTURE.md) §6), bukan `user_id: null` yang menyamar.

---

## §2 `<domain>` wajib terdaftar, dan tiap domain dimiliki tepat satu konteks

Ini yang mengubah [#38](../../issues/38) dari **konvensi penamaan** menjadi
**sesuatu yang bisa diperiksa mesin**. Format `domain.verb` saja tidak cukup:
tanpa daftar domain yang sah, `stuff.happened` lolos.

> 🔑 **Segmen pertama `event_type` wajib ada di registry di bawah, dan tiap
> domain dimiliki tepat satu bounded context.**

| Konteks pemilik | Domain event |
|---|---|
| `identity` | `identity` · `consent` · `permission` · `session` |
| `human-core` | `profile` · `goal` · `habit` · `checkin` · `mood` · `journal` · `activity` · `meal` · `sleep` · `workout` · `travel` · `learning` · `meeting` · `outfit` · `purchase` |
| `events` | — (ia bus-nya) |
| `memory` | `memory` |
| `context` | — (tidak menerbitkan apa pun) |
| `intelligence` | `insight` · `recommendation` · `prediction` · `pattern` · `twin` |
| `knowledge` | `knowledge` |
| `world-model` | `world` |
| `simulation` | `simulation` |
| `agents` | `agent` · `approval` · `delegation` · `message` |
| `tools` | `tool` |
| `perception` | `perception` |
| `spatial` | `spatial` · `presence` |
| `embodiment` | `robot` · `mission` · `emergency` |
| `security` | `security` |
| `governance` | `governance` · `constitution` |
| `platform` | `platform` · `billing` · `notification` |

**39 domain, 15 konteks penerbit.** Domain baru ditambahkan hanya bersama
konteks pemiliknya — dan penambahan itu adalah perubahan arsitektur, bukan
penamaan.

⚠️ **Bentuk tiga segmen tidak dipakai.** [#38](../../issues/38) menawarkan
`fashion.outfit.selected`; pencarian atas seluruh `docs/` menemukannya **hanya
di berkas yang mendefinisikan standarnya sendiri** — **nol event pernah dinamai
begitu**. Yang dipakai: **dua segmen**, dan versi ditulis di `schema_version`,
bukan di nama.

---

## §3 Apa yang **bukan** event

Uji admisinya di [`06`](06-DATA-ARCHITECTURE.md) §3, dan ia satu-satunya hal
yang menjaga `events` tetap bisa menjadi *sumber kebenaran perilaku*:

> **`events` hanya menerima kejadian yang bermakna bagi manusia.**

| Bukan event | Ke mana |
|---|---|
| 14 event persepsi §10.30 (bingkai, deteksi per detik) | diringkas dulu di `perception/summarizer/`, lalu `perception.*` |
| `wifi_csi` · point cloud · audio mentah | **K3**, dan tidak meninggalkan perangkat (§15.29) |
| pembacaan biometrik berkelanjutan | **K2**, ringkasan hariannya menjadi `sleep.completed` dll. |

⇒ **E-89** ([#74](../../issues/74)) tertutup bukan dengan memperbesar `events`,
melainkan dengan menyatakan apa yang tidak pernah masuk.

---

## §4 128 nama dalam format yang ditolak — dipadankan, naskah tidak diubah

[K-3](../docs/KEPUTUSAN-DIDELEGASIKAN.md) sudah memutuskan bentuknya
(padanan mekanis, tabel di `spec/03`, naskah utuh). Yang ditambahkan di sini:
**tiap nama juga mendapat DOMAIN dari §2**, sehingga padanannya lengkap.

| Fase | Nama PascalCase | Domain tujuan |
|---|---|---|
| 8 | `SecurityEvent` | `security` |
| 10 | 14 nama persepsi | `perception` — **sesudah lulus §3** |
| 11 | 22 nama agent | `agent` · `approval` · `tool` |
| 13 | 15 nama otomasi | `agent` · `notification` |
| 14 | 16 nama kolektif | `agent` · `delegation` · `message` |
| 15 | 13 nama spasial | `spatial` · `presence` |
| 16 | 13 nama robotik | `robot` · `mission` · `emergency` |
| 17 | 15 nama kesehatan | `health`⁽¹⁾ |
| 18 | 14 nama dunia | `world` · `knowledge` |
| 20 | 12 nama peradaban | `governance` · `world` |

⁽¹⁾ `health` sebagai **domain event** dimiliki `human-core`; data klinis Level
3–4 tidak diterbitkan sebagai event sama sekali — ia hidup di
`security/vault/` ([`06`](06-DATA-ARCHITECTURE.md) §7).

### Tiga tabrakan yang bukan soal ejaan

Sudah diputuskan [K-3](../docs/KEPUTUSAN-DIDELEGASIKAN.md), diulang di sini
sebab ia satu-satunya bagian yang **tidak** mekanis:

| PascalCase | Sudah ada di `spec/03` | Berlaku |
|---|---|---|
| `SleepEnded` | `sleep.completed` | **`sleep.completed`** |
| `MeetingEnded` | `meeting.completed` | **`meeting.completed`** |
| `MoodChanged` | `mood.logged` | **`mood.logged`** |

🛑 Ketiganya beda **kata kerja**, bukan beda gaya. Kalau keduanya dikodekan,
**satu kejadian punya dua event** — dan proyeksi yang membaca salah satunya akan
selalu kehilangan separuh riwayat, tanpa galat.

---

## §5 Versi — dan satu aturan yang lebih penting daripada nomornya

`spec/03` aturan 3 tetap berlaku: consumer wajib mengabaikan medan yang tidak
dikenalnya; perubahan yang melanggar kontrak **menerbitkan `event_type` baru**,
bukan menaikkan versi diam-diam.

🔧 **Yang ditambahkan v2.0** — konsekuensi dari dua puluh fase:

| Aturan | Kenapa |
|---|---|
| **Nama event tidak pernah diganti**, sekali diterbitkan | proyeksi bisa dibangun ulang dari nol (`spec/README` prinsip 3) hanya kalau namanya stabil sepanjang riwayat |
| **Menambah medan opsional tidak menaikkan `schema_version`** | kalau tiap tambahan menaikkan versi, consumer akan berhenti memutakhirkan |
| **Menghapus medan = event baru**, bukan versi baru | penghapusan senyap adalah bentuk kegagalan yang tidak menghasilkan galat |
| **`event_type` yang ditinggalkan wajib punya baris `deprecated_at` di schema registry** | supaya *“masih dipakai?”* bisa dijawab tanpa membaca kode |

---

## §6 🔴 Setiap kata kerja yang mengubah keadaan wajib punya kembaran kegagalan

**Menutup bagian G-14 dari [#98](../../issues/98).**

Pola yang sudah tercatat **empat kali**: sesuatu **didaftarkan lengkap** dalam
prosa, lalu **diskemakan sebagian** sebagai event.

| Didaftarkan | Diskemakan | Yang hilang |
|---|---|---|
| **7** tindakan watchdog §14.28 | **3** event §14.53 | **`AgentRestored`** — padahal §14.29 menjadikan `RESTORE` **setara** `RETIRE` |
| **11** unsur Autonomy Contract §14.62 | **6** di YAML | `scope` · `data boundary` · `risk level` · `success criteria` · **`kill condition`** |
| `Attention Budget` · `Autonomy Contract` | — | **tanpa tabel** (§14.52), **tanpa butir DoD** (§14.68) |

🛑 **Akibatnya lebih berat daripada kerapian: jejak audit hanya merekam tindakan
TERBERAT.** Agent yang di-`THROTTLE` setiap hari selama sebulan tidak
meninggalkan **satu baris pun** — padahal itu persis pola yang §14.32 ingin
dideteksi. Sebuah sistem deteksi yang hanya mencatat kejadian besar tidak bisa
melihat pola yang tersusun dari kejadian kecil.

🔧 **Aturan, ditegakkan CI** ([`11`](11-PENEGAKAN.md) E-4):

> **Setiap kata kerja kendali yang mengubah keadaan menerbitkan event —
> termasuk yang ringan. Dan setiap kata kerja yang bisa GAGAL punya kembaran
> kegagalan; setiap keadaan yang bisa DIPULIHKAN punya kembaran pemulihan.**

| Aksi | Kembaran wajib |
|---|---|
| `agent.retired` | **`agent.restored`** |
| `agent.throttled` | `agent.unthrottled` |
| `agent.paused` | `agent.resumed` |
| `mission.completed` | **`mission.failed`** |
| `emergency.stopped` | **`recovery.started`** · `recovery.completed` |
| `tool.called` | `tool.failed` |

⭐ **Modelnya sudah ada di repo ini, dan patut disebut:** Phase 16 menulis
`MissionFailed` **berdampingan** `MissionCompleted`, dan `RecoveryStarted`
bersama `EmergencyStop` ⇒ jalur gagal dan jalur pulih punya event **sejak
awal**. Itu satu-satunya fase yang melakukannya, dan ia yang dipakai sebagai
contoh.

⚠️ **Dan satu perkabelan yang masih putus:** `BatteryLow` ada sebagai event
Phase 16, tetapi **tidak ada** di daftar pemicu darurat §16.20. Sebuah event
yang tidak didengar siapa pun bukan pengaman — ia catatan.

---

## §7 🛑 Nol perubahan untuk V0

| | |
|---|---|
| Event V0 | **22**, tidak berubah — [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) |
| Amplop | tidak berubah |
| Domain V0 yang dipakai | 12, semuanya milik `human-core` + `memory` |
| Kembaran kegagalan yang dituntut untuk V0 | **`tool.failed`** saja — Sprint 4 tugas 4.3 |

---

## §8 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Amplop event | **1** |
| Domain terdaftar | **39**, tiap domain **tepat satu** konteks pemilik |
| `event_type` di luar registry | ditolak CI — [`11`](11-PENEGAKAN.md) E-1 |
| `event_type` bukan `domain.verb` huruf kecil | ditolak CI — E-2 |
| Nama tiga segmen | **NIHIL** — tidak pernah dipakai |
| Aliran mentah masuk `events` | ditolak CI — E-3 (`source='sensor'` tidak ada) |
| Kata kerja pengubah keadaan tanpa kembaran | ditolak CI — E-4 |
| Nama event yang pernah diganti | **NIHIL** — aturan §5 |
| Event V0 | **22**, tidak berubah |
