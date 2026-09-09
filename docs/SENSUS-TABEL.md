# Sensus nama tabel lintas fase

> ⚠️ **Bukan kata pemilik.** Pengukuran. Ia tidak memilih tabel mana yang masuk
> V0 dan tidak menggabungkan tabel kembar — itu tetap
> [#139](../../issues/139) dan [`../spec/01`](../spec/01-DATABASE-SCHEMA.md).

---

## Kenapa berkas ini ada

Jumlah tabel dicatat sebagai **penjumlahan berjalan** di
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) (**E-106**):

```
23 (V0) + 20 (Fase 8) + 16 (Fase 10) + 14 (Fase 11) + 26 (§12.28) = 99
```

⭐ **Metodenya benar** — tiap suku adalah tabel **baru**, sudah dikurangi yang
sudah didefinisikan sebelumnya. (§11.48 memberi 18 entitas; empat sudah ada di
`spec/01` dan Fase 8, jadi masuk sebagai **14**. §8.40 memberi 24; empat sudah
ada di V0, jadi **20**.)

🛑 **Yang salah bukan aritmetikanya — melainkan bahwa ia berhenti di Phase 12.**
Delapan fase sesudahnya menambah tabel, dan tidak ada satu pun yang masuk
hitungan.

---

## Cara mengukur, dan dua kekeliruan yang harus dilewati

Yang dipanen: bagian yang judulnya menyebut *Data Model · Database · Tabel ·
Schema*, dari **kata pemilik saja** (blok `>` diklasifikasi dari baris
pertamanya — pelajaran dari [`SENSUS-EVENT.md`](SENSUS-EVENT.md)).

| Percobaan | Kekeliruan | Akibat |
|---|---|---|
| 1 | menuntut nama ber-garis-bawah | `robots`, `joints`, `missions` terbuang — [`235`](235-DATA-EVENT-REPO-ROADMAP-DOD-POSISI.md) terhitung **11** padahal daftarnya **17** |
| 2 | hanya memanen blok ber-fence | [`254`](254-ARSITEKTUR-REPO-DATA-MODEL-DAN-API.md) §18.28 menulis daftarnya dalam **backtick**, bukan fence — **hilang seluruhnya** |
| 3 | memanen **keduanya** | ✅ dipakai |

### ✅ Divalidasi lima kali terhadap angka yang sudah tertulis

| Sumber menyebut | Sensus | |
|---|---|---|
| naskah 5 §31 — *“19 tabel”* | [`95`](95-V0-SPESIFIKASI.md) → **19** | ✅ |
| §8.40 — *“20 tabel baru”* atas 24 nama | [`152`](152-REPO-DATA-MODEL-CONTROL-PLANE.md) → **24** | ✅ |
| §11.48 — *“Delapan belas entitas”* | [`187`](187-DATA-EVENT-REPO-ROADMAP-DOD.md) → **18** | ✅ |
| §12.28 — 26 tabel | [`196`](196-REPO-API-DB-AGENT.md) → **26** | ✅ |
| §18.28 — dihitung tangan | [`254`](254-ARSITEKTUR-REPO-DATA-MODEL-DAN-API.md) → **30** | ✅ |

⭐ **Dan validasi keenam yang paling meyakinkan:**
[`../spec/01`](../spec/01-DATABASE-SCHEMA.md) menyatakan asal-usulnya sendiri —
*“naskah 5 §31 (19 tabel) + naskah 6 (`events`, `agents`, `agent_tools`) +
1 usulan (`human_states`)”*. Sensus menemukan **tepat 19** di naskah 5, dan
**tepat tiga** nama `spec/01` yang tidak ada di bagian data model naskah mana
pun: `events` · `agent_tools` · `human_states`. Pernyataan provenans itu
terverifikasi tanpa dibaca lebih dulu oleh pengukurnya.

---

## 🔴🔴 Hasil: 99 → **247**

| | |
|---|---|
| **nama tabel unik** | **247** |
| dokumen yang memuatnya | **14** |
| sebutan (dengan pengulangan) | 270 |
| union sampai Phase 12 | **108** (taksiran neto audit: 99) |
| **nama BARU sesudah Phase 12** | **139 — belum pernah masuk hitungan mana pun** |

### Sebaran per fase

| Berkas | Fase | Nama tabel |
|---|---|---|
| [`84`](84-DATABASE-ARCHITECTURE.md) | naskah 5 | 4 |
| [`95`](95-V0-SPESIFIKASI.md) | naskah 5 — V0 | 19 |
| [`134`](134-EVENT-PLATFORM.md) | Phase 7 | 8 |
| [`152`](152-REPO-DATA-MODEL-CONTROL-PLANE.md) | Phase 8 | 24 |
| [`175`](175-REPO-API-DB-ROADMAP-DOD.md) | Phase 10 | 16 |
| [`187`](187-DATA-EVENT-REPO-ROADMAP-DOD.md) | Phase 11 | 18 |
| [`196`](196-REPO-API-DB-AGENT.md) | Phase 12 | 26 |
| [`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md) | Phase 14 | **27** |
| [`226`](226-SDK-REPO-API-DATA-EVENT-DEPLOYMENT.md) | Phase 15 | 18 |
| [`235`](235-DATA-EVENT-REPO-ROADMAP-DOD-POSISI.md) | Phase 16 | 17 |
| [`244`](244-EVENT-DATABASE-API-REPO-RUNTIME.md) | Phase 17 | 24 |
| [`254`](254-ARSITEKTUR-REPO-DATA-MODEL-DAN-API.md) | Phase 18 | **30** |
| [`265`](265-REPO-DATABASE-API-MILESTONE-DOD-DAN-PHASE-20.md) | Phase 19 | 17 |
| [`273`](273-API-EVENT-BUS-REPOSITORY-DAN-DATABASE.md) | Phase 20 | 22 |

**Tujuh fase terakhir menyumbang 155 sebutan** — lebih banyak daripada seluruh
hitungan yang pernah diterbitkan.

---

## Sembilan belas nama didefinisikan di lebih dari satu tempat

| Kali | Nama | Di fase |
|---|---|---|
| **4×** | `agent_capabilities` | Phase 8 · 11 · 14 · 18 |
| **4×** | `agent_trust_scores` | Phase 8 · 11 · 14 · 18 |
| 2× | `agents` · `agent_versions` · `agent_messages` | Phase 11 · 14 |
| 2× | `world_entities` · `world_events` · `world_relationships` · `world_states` | Phase 12 · 18 |
| 2× | `users` · `permissions` · `consents` · `audit_logs` | V0 · Phase 8 |
| 2× | `agent_runs` | V0 · Phase 11 |
| 2× | `policies` · `sessions` | Phase 8 · 20 |
| 2× | `navigation_paths` | Phase 15 · 16 |
| 2× | `spatial_maps` | Phase 10 · 15 |
| 2× | `simulations` | Phase 19 · 20 |

> 🛑 **`agent_capabilities` dan `agent_trust_scores` didefinisikan EMPAT kali,
> di empat fase berbeda.** Catatan audit sudah menandainya muncul dua kali
> (§8.40 dan §11.48); sensus menemukan dua kemunculan lagi di Phase 14 dan
> Phase 18. Untuk tabel yang memegang **kapabilitas** dan **kepercayaan** agent
> — dua hal yang menentukan apa yang boleh dilakukan sebuah agent — empat
> definisi berarti empat kemungkinan bentuk kolom.

---

## Apa artinya

Untuk [#139](../../issues/139) butir *data architecture*: skema ditulis untuk
**himpunan**, dan himpunannya **247 nama**, bukan 99. Yang perlu diselesaikan
lebih dulu bukan menambah tabel melainkan **19 nama yang punya lebih dari satu
definisi**.

⭐ Dan kabar baik yang tidak berubah: **belum ada satu baris kode pun**, jadi
tidak ada satu pun dari 247 yang sudah mengunci migrasi.

---

## Yang sensus ini **tidak** putuskan

Tidak memilih tabel mana yang masuk V0 (itu tetap `spec/01`, 23 tabel, dan
tidak berubah), tidak menggabungkan definisi kembar, dan tidak menilai mana
yang seharusnya bukan tabel. Ia hanya mengganti **99** dengan **247**, dan
menunjukkan bahwa hitungan itu berhenti dipelihara delapan fase yang lalu.

Terbit sebagai **[#151](../../issues/151)** (**E-156**).
