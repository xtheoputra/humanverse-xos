# Sensus nama event lintas fase

> ⚠️ **Bukan kata pemilik.** Pengukuran. Ia **tidak membuka ulang**
> [#38](../../issues/38) — keputusan itu sudah ditutup (`domain.verb`, huruf
> kecil, dua segmen). Ia hanya menghitung **berapa besar** akibatnya.

---

## Kenapa berkas ini ada

Pelanggaran format nama event dicatat **satu per satu**: *“pelanggaran
ketujuh”*, *“kesembilan”*, *“kesepuluh”* — sepuluh catatan di komentar
[#38](../../issues/38) dan di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

Setiap catatan itu menghitung **kejadian** (satu naskah = satu pelanggaran).
Tidak ada satu pun yang menghitung **nama**. Berkas ini menghitung namanya.

---

## Cara mengukur — dan dua kekeliruan yang harus dilewati dulu

Yang dipanen: bagian yang **judulnya menyebut “Event”**, lalu semua nama di
dalamnya, diklasifikasikan `domain.verb` (sesuai) atau `PascalCase`.

**Dua percobaan pertama salah, dan keduanya salah ke arah yang sama —
membuat format yang dipilih tampak lebih banyak dipakai daripada kenyataannya:**

| Percobaan | Kekeliruan | Akibat |
|---|---|---|
| 1 | tidak memisahkan **kata pemilik** dari **catatan audit saya** | `spatial_map.updated` terhitung “sesuai”, padahal itu **usul perbaikan saya** di [`174`](174-EVENT-GRAPH-DIGITAL-TWIN-LOOP.md) L46 — bukan yang ditulis naskah |
| 2 | menganggap semua baris `>` = catatan saya | **salah**: naskah juga mengutip pemilik dengan `>` — §18.5 [`247`](247-WORLD-INTELLIGENCE-EVENT-ENGINE-KNOWLEDGE-GRAPH.md) menulis *“Event lain: `CompanyAcquired · …`”* di dalam `>`. Tiga belas nama pemilik hilang dari hitungan |
| 3 | blok `>` diklasifikasi dari **baris pertamanya** — catatan audit selalu dibuka penanda vonis (⭐ 🛑 ⚠️) atau kata *Butir* | ✅ dipakai |

> 💡 **Pelajaran: pembeda populasi harus diuji, bukan diasumsikan.** Percobaan 2
> tampak masuk akal (*“`>` itu catatan saya”*) dan diam-diam membuang tiga belas
> nama pemilik.

**Validasi silang** — hasil sensus dicocokkan dengan pemeriksaan manual yang
sudah ada di catatan audit, dan **ketiganya cocok**:

| Naskah menyebut | Sensus |
|---|---|
| §13.12 *“memberi lima belas event”* | `201` → **15** ✅ |
| §16.31 *“memberi 13 event”* | `235` → **13** ✅ |
| §18.5 → `OilPriceChanged` + 13 nama lain | `247` → **14** ✅ |

---

## 🔴🔴 Hasil: 21 lawan 128

| Populasi | `domain.verb` (sesuai) | `PascalCase` |
|---|---|---|
| **kata pemilik di naskah** | **21** | **133** |
| catatan audit saya | 31 | 59 |

Dari 133 nama PascalCase, **5 hanya ada di [`16`](16-EVENT-DRIVEN.md)** (naskah
1–2, ditulis **sebelum** keputusan — itu asal-usulnya, bukan pelanggaran).

⇒ **128 nama event ditulis dalam format yang ditolak, sesudah keputusan
ditutup.**

### ⭐ Dan angka yang lebih menentukan: ke-21 nama yang sesuai berasal dari SATU naskah

```
goal.completed · goal.created · habit.completed · habit.created · habit.skipped
journal.created · learning.completed · learning.started · meal.logged
meeting.completed · meeting.started · mood.logged · outfit.selected
outfit.worn · purchase.created · sleep.completed · sleep.started
travel.completed · travel.started · workout.completed · workout.started
```

**Semuanya — 21 dari 21 — muncul di [`85`](85-BEHAVIOR-DAN-EVENT.md) (naskah 5
§7).** Naskah berikutnya hanya mengutip ulang sebagian; tidak satu pun menambah
nama baru dalam format itu.

🛑 **Artinya: sejak naskah 5, pemilik menamai 128 event baru — dan NOL di
antaranya memakai format yang dipilih.** Formatnya bukan diperdebatkan, ia
tidak pernah dipakai lagi.

---

## Sebarannya per naskah

| Berkas | Fase | Nama PascalCase |
|---|---|---|
| [`16`](16-EVENT-DRIVEN.md) | naskah 1–2 — **sebelum** keputusan | 7 |
| [`152`](152-REPO-DATA-MODEL-CONTROL-PLANE.md) | Phase 8 | 1 — `SecurityEvent`, sudah tercatat **E-69** / [#63](../../issues/63) |
| [`174`](174-EVENT-GRAPH-DIGITAL-TWIN-LOOP.md) | Phase 10 | 14 |
| [`187`](187-DATA-EVENT-REPO-ROADMAP-DOD.md) | Phase 11 | **22** |
| [`201`](201-AUTOMATION-EVENT-WORKFLOW-SCHEDULER.md) | Phase 13 | 15 |
| [`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) | Phase 14 | 16 |
| [`226`](226-SDK-REPO-API-DATA-EVENT-DEPLOYMENT.md) | Phase 15 | 13 |
| [`235`](235-DATA-EVENT-REPO-ROADMAP-DOD-POSISI.md) | Phase 16 | 13 |
| [`244`](244-EVENT-DATABASE-API-REPO-RUNTIME.md) | Phase 17 | 15 |
| [`247`](247-WORLD-INTELLIGENCE-EVENT-ENGINE-KNOWLEDGE-GRAPH.md) | Phase 18 | 14 |
| [`273`](273-API-EVENT-BUS-REPOSITORY-DAN-DATABASE.md) | Phase 20 | 12 |

**Sembilan naskah, Phase 10 → Phase 20.** Phase 12 dan Phase 19 tidak ada di
tabel bukan karena terlewat: **keduanya tidak mendefinisikan model event sama
sekali** (tak satu pun bagiannya berjudul *Event*) — diperiksa langsung.

⇒ Jadi klaimnya lebih keras daripada *“sembilan naskah berturut-turut”*:
**setiap naskah yang mendefinisikan model event sejak Phase 10 memakai
PascalCase — sembilan dari sembilan.**

---

## Pilihan ketiga yang ditawarkan #38 tidak pernah dipakai sekali pun

[#38](../../issues/38) menawarkan dua bentuk:

1. **dua segmen** `workout.completed` — dipilih, dipakai [`../spec/03`](../spec/03-EVENT-CONTRACTS.md);
2. **tiga segmen** `fashion.outfit.selected` — usul naskah 7 Layer 22.

Pencarian atas seluruh `docs/`: `fashion.outfit.selected` hanya muncul di
[`101`](101-L22-ENGINEERING-STANDARDS.md) L47 — **berkas yang mendefinisikan
standarnya sendiri** — dan di catatan audit yang membicarakannya.
**Nol event pernah dinamai dengan bentuk itu.**

Satu-satunya nama tiga segmen yang benar-benar ada adalah bentuk **berversi** di
[`134`](134-EVENT-PLATFORM.md) §7.5 — `workout.completed.v1`, `sleep.completed.v1`,
`outfit.selected.v1`, `purchase.created.v1` — yaitu nama dua segmen **ditambah
versi**, hal yang berbeda.

---

## Apa artinya untuk biaya

[#38](../../issues/38) menutup butir ini dengan alasan yang masih berlaku:
**nama event tidak boleh diganti setelah dipakai** — begitu baris pertama masuk
tabel `events`, mengganti nama berarti migrasi riwayat atau kehilangan
perilaku.

Kabar baiknya tidak berubah: **belum ada satu baris kode pun**, jadi 128 nama
itu masih bisa ditulis ulang dengan biaya nol.

⚠️ Kabar yang perlu diperhatikan: **tiga tabrakan bukan sekadar beda bentuk —
kata kerjanya berbeda untuk kejadian yang sama** (sudah tercatat di
[`201`](201-AUTOMATION-EVENT-WORKFLOW-SCHEDULER.md) L96–98):

| [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) | naskah | Selisih |
|---|---|---|
| `sleep.completed` | `SleepEnded` | `completed` lawan `Ended` |
| `meeting.completed` | `MeetingEnded` | `completed` lawan `Ended` |
| `mood.logged` | `MoodChanged` | `logged` lawan `Changed` |

Mengubah **bentuk** tidak menyelesaikan ketiganya — ia menyelesaikan 125 sisanya.
🛑 Dan `SleepEnded` tidak hanya muncul sekali: ia ditulis di §13.12
([`201`](201-AUTOMATION-EVENT-WORKFLOW-SCHEDULER.md) L72) lalu **muncul lagi
tanpa berubah** di §17.42 ([`244`](244-EVENT-DATABASE-API-REPO-RUNTIME.md) L11),
**empat fase kemudian** — tabrakan kosakata yang bertahan melewati catatan
auditnya sendiri.

---

## Yang sensus ini **tidak** putuskan

Tidak membuka ulang [#38](../../issues/38), tidak mengusulkan penggantian nama,
dan tidak memilih format. Ia hanya mengganti kalimat *“pelanggaran kesepuluh”*
dengan angka: **128 nama, sembilan dari sembilan naskah yang mendefinisikan
model event, nol nama baru dalam format yang dipilih sejak naskah 5.**

Terbit sebagai **[#149](../../issues/149)** (**E-153**).
