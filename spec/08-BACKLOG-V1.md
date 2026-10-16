# 08 — Backlog V1 untuk AI coding agent · 🟡 DRAF

> ⚠️ **Bukan kata pemilik**, dan **belum disetujui pemilik** (**A-39**). Sampai
> disetujui, satu-satunya daftar pekerjaan kode tetap [`07`](07-BACKLOG-V0.md)
> ([`../AGENTS.md`](../AGENTS.md) §2), dan **tidak satu baris kode V1 pun ditulis.**
>
> Draf ini menurunkan **T1 Behavior Intelligence (V1)**
> ([`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §2) menjadi tugas yang bisa
> diberikan **satu per satu**, dengan aturan yang sama dengan `07`:
> satu tugas = satu commit (**K-18**), satu kolom **“Selesai bila”** yang bisa
> dibuktikan **mesin**, dan rantai governance yang sama:

```
Coding Agent → Implementation → Unit Test → Integration Test
→ Security Scan → AI Review → HUMAN REVIEW → Merge
```

---

## Dari mana isinya

**Kata pemilik tentang V1 hanya enam butir, tanpa uraian** —
[`../docs/75`](../docs/75-URUTAN-PEMBANGUNAN-V0-V6.md) §58:

> *Event System · Behavior Analytics · Pattern Detection · Habit Prediction ·
> Goal Engine · Weekly Review*

Naskah **tidak** memberi metrik, DoD, maupun urutan sprint V1. Yang ada adalah
batas-batas di naskah lain, dan batas itu yang mengikat draf ini:

| Batas pemilik | Naskah | Dipakai di |
|---|---|---|
| asosiasi, **bukan** sebab — *“berasosiasi dengan”*, bukan *“menyebabkan”* | [`54`](../docs/54-BEHAVIOR-ENGINE.md) §7 · `158` §9.17 | 9.2 |
| prediksi bukan kepastian — *“0.68”*, bukan *“you will definitely”*; bentuk `{prediction, probability, horizon, confidence, evidence}` | `159` §9.18–§9.19 | 10.1 · 10.2 |
| confidence wajib; rendah → **tanya pengguna**; *“tidak berpura-pura tahu”* | [`90`](../docs/90-DIGITAL-TWIN-DAN-CONFIDENCE.md) §19 · `163` §9.32 | semua |
| tiap angka harus punya **Why?** | `63` §28 · `120` Pillar 11 | 8.4 · 11.5 |
| jangan satu angka Life Score | `63` §28 | *TIDAK ada* |
| *“Preference ≠ permanent identity”* | `155` §9.4 · `61` §24 | 9.3 |
| bukan menyalahkan / menghakimi pengguna | `65` §33 · `76` · `163` §9.35 | 8.2 · 11.2 |
| jangan manipulasi; *“Do Nothing”* adalah kemampuan | `106` · `186` §11.43–44 | *TIDAK ada* (Engagement Prediction, nudge) |
| *“setiap malam … Sunday 20:00 → Weekly Review”* | `138` §7.21 | 7.3 · 11.4 |
| *“Jangan langsung memakai semuanya pada V1”* (Kafka/Spark/ClickHouse) | `67` §38 | *TIDAK ada* |

🔑 **V0 sudah memuat versi pertama dua butir V1** — pola (5.2) dan tinjauan
mingguan (6.2), keduanya disebut naskah 5 §32 untuk Sprint 5–6. Draf ini
membaca butir V1 itu sebagai **pendalaman** dari versi V0, bukan pembuatan
ulang. Yang V0 akui belum dikerjakan
([`07`](07-BACKLOG-V0.md) blok status 5.x · 6.2, **K-34 · K-35(c) · K-45**)
menjadi bahan utamanya.

🔑 **Keluaran intelligence BUKAN event.** Pola dan prediksi tidak lulus uji
admisi `events` syarat 1 ([`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §3 —
pengguna tidak *melakukan* “pola terdeteksi”), dan `source`-nya bukan
`app·agent·integration·backfill`. Keduanya tabel milik `intelligence`
([`../arch/02`](../arch/02-BOUNDED-CONTEXT.md)), dibaca lewat pintu keluar
modul — **tidak** ditambahkan ke registry event.

**Penomoran sprint melanjutkan `07`** (Sprint 7–11), supaya rujukan
*“spec/0x N.k”* di commit tidak pernah ambigu.

---

## Sprint 7 — Gerbang V1 & Event System

| # | Tugas | Selesai bila |
|---|---|---|
| 7.1 | **Uji admisi `events` syarat 1 ditegakkan mesin** ([`../arch/06`](../arch/06-DATA-ARCHITECTURE.md) §3) — kini hanya syarat 3 (`source`) yang dijaga; syarat 1 tersirat dari registry tertutup | jenis event yang ditambahkan ke registry `events/kontrak.py` **tanpa** baris [`03`](03-EVENT-CONTRACTS.md) lengkap (kalimat *“yang dikenali pengguna”*, arti `idempotency_key`, `source` yang sah) → **CI merah**; mutasinya berbunyi |
| 7.2 | **Proyeksi terdaftar** — tiap proyeksi baru V1 mendaftar ke satu uji wipe-and-replay generik (perluasan 5.1) | proyeksi yang didaftarkan dibangun ulang dari nol dan **hasilnya sama**; proyeksi baru yang **tidak** didaftarkan → CI merah |
| 7.3 | **Tugas terjadwal per jam lokal pengguna** di `hvx.pekerja` (bukan proses/alat baru — **K-39**) | tugas *malam* berjalan **tepat sekali** per pengguna per hari lokal; dua pekerja serentak tidak menggandakan; pengguna di dua zona waktu diproses pada jam lokal masing-masing; ganti zona waktu tidak melewatkan atau menggandakan hari |
| 7.4 | **Putar ulang stream mati** (V0 3.3: *“belum punya alat”*) | event di stream mati diputar ulang per id; memutar ulang dua kali **tidak** menggandakan efek; event milik akun yang terhapus tidak diputar |

> **7.1 sebelum event baru apa pun, 7.2 sebelum proyeksi baru apa pun** — gerbang
> lebih dulu daripada yang dijaganya ([`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §1).

## Sprint 8 — Behavior Analytics

| # | Tugas | Selesai bila |
|---|---|---|
| 8.1 | Tabel **`behavior_daily`** — agregat harian per pengguna dari event (habit selesai/dilewati per habit · mood · energi · fokus) | dibangun ulang dari event, hasilnya sama (7.2); RLS + FK komposit + `GRANT` + anotasi **P-1 · P-2** — di [`01`](01-DATABASE-SCHEMA.md) **dan** migrasinya |
| 8.2 | **Tren berjendela** 7 & 28 hari per metrik (**K-35(c)**, ditunda V0) | tiap tren membawa `evidence_count`; di bawah minimum → `insufficient_data`, **bukan** angka; kata yang dipakai menggambarkan arah, tidak menilai pengguna (daftar kata ditolak di uji) |
| 8.3 | **Waktu laku** penyelesaian habit (V0 5.2: bagian hari dari waktu *catat*) | klien boleh mengirim waktu laku (`platform.WaktuBerzona`, tidak di masa depan); pola bagian hari memakai waktu laku bila ada dan **menyatakan sumbernya** bila tidak |
| 8.4 | `GET /v1/analytics/…` — tren & agregat untuk pengguna | tiap angka membawa **Why**: sumber, jendela, `evidence_count`; sumbu yang V1 tidak ukur → `not_measured` (**B-38**), bukan 0 |

## Sprint 9 — Pattern Detection

| # | Tugas | Selesai bila |
|---|---|---|
| 9.1 | Tabel **`patterns`** milik `intelligence` ([`../arch/02`](../arch/02-BOUNDED-CONTEXT.md)) menggantikan `memories(kind='behavioral')` dari **K-34** | pola V0 dipindah tanpa hilang (uji migrasi); pekerja pola tidak lagi menulis memori behavioral; K-34 dicabut dengan catatan kenapa |
| 9.2 | Jenis pola **Temporal** (hari · bagian hari · siklus mingguan) · **Behavioral** (rentetan · urutan habit A→B) · **Emotional** (asosiasi mood ↔ habit) — `54` §6 | tiap pola membawa `kind` · `confidence` · `evidence_count` · kalimat **asosiatif**; klaim kausal **ditolak mesin** (penjaga `tanpa_klaim_kausal` V0 diperluas); nol bukti → tidak ada pola |
| 9.3 | Pola **meluruh** — bukti berlawanan menurunkan keyakinan, pola tanpa dukungan kedaluwarsa | urutan event berlawanan → `confidence` turun lalu pola hilang; dibangun ulang dari nol hasilnya sama |
| 9.4 | Pengguna **melihat, mengoreksi, dan menghapus** pola tentang dirinya (`69` §43 *View · Edit · Delete*) | pola yang dihapus **tidak muncul lagi dari bukti yang sama** — hanya bukti baru yang bisa memunculkannya; koreksi tercatat sebagai umpan balik; `identity.audit` di transaksi yang sama |
| 9.5 | Coach agent memakai pola lewat **tool** (aturan 6 `05`), bukan baca langsung | jawaban yang memakai pola menyebut keyakinannya; pola ber-`evidence_count` rendah → agent **bertanya** (5.4) |

## Sprint 10 — Habit Prediction

| # | Tugas | Selesai bila |
|---|---|---|
| 10.1 | Tabel **`predictions`** — `{kind, subject, probability, horizon, confidence, evidence, model_version, made_at, resolves_at, outcome}` (`159` §9.19) | append-only kecuali `outcome`; `outcome` diisi tugas malam (7.3) saat jendelanya berakhir; spec/01 + migrasi + RLS bersama |
| 10.2 | **Prediksi penyelesaian habit besok** (horizon 1 hari) — model dasar **transparan** (laju per hari-dalam-minggu, bobot kekinian, prior), tanpa model terlatih | probabilitas 0–1 dengan `evidence`; bukti di bawah minimum → **tidak memprediksi** (Confidence Layer); tidak ada kalimat kepastian di teks mana pun (uji kosakata) |
| 10.3 | **Kalibrasi terukur** — *Prediction Calibration* (`163` §9.34) | perintah menghasilkan Brier score + tabel reliabilitas per `model_version` dari `outcome` tersimpan; `model_version` baru **ditolak** di uji bila Brier-nya pada data historis sintetis lebih buruk dari yang lama |
| 10.4 | Prediksi menjadi **komponen rekomendasi** (5.5) | `score_breakdown` memuat `prediction`; `scoring_version` naik ke `v2`; `rationale` menyebut peluang sebagai *“mungkin”*; rekomendasi lama `v1` tetap terbaca |

## Sprint 11 — Goal Engine & Weekly Review

| # | Tugas | Selesai bila |
|---|---|---|
| 11.1 | **Progres goal** dari milestone + habit tertaut (`55` §8–9: *“habit harus melayani tujuan”*) | progres 0–1 + rincian sumbernya; goal tanpa milestone & tanpa habit → `not_measured`, **bukan** 0 |
| 11.2 | Habit yang tidak melayani goal, dan goal tanpa habit, **dinyatakan** | terlihat di goal & dasbor; teksnya lolos uji kosakata tidak-menghakimi (8.2) |
| 11.3 | Goal **mungkin terlambat** — prediksi `goal_progress` (10.1) dari laju saat ini vs `target_date` | hanya untuk goal ber-`target_date` dengan bukti cukup; membawa `confidence`; tidak pernah *“pasti gagal”* |
| 11.4 | **Weekly Review disimpan** (**K-45**: V0 menghitungnya saat dibaca) — dibuat tugas Minggu 20:00 lokal (7.3) | satu snapshot per pengguna per minggu ISO lokal, tidak berubah sesudah dibuat; batch dua kali → satu snapshot; minggu tanpa data → snapshot *“data belum cukup”*; **tanpa notifikasi** (**A-28**) |
| 11.5 | Jawaban tinjauan memakai **tren · pola · prediksi** | *What changed* dari 8.2, *Why* dari pola 9.2 (asosiatif) — tanpa pola berkeyakinan, *Why* tetap **bertanya**; *What should change* dari rekomendasi; tiap jawaban membawa sumber |
| 11.6 | **Layar Flutter V1** — analitik, pola (lihat/koreksi/hapus), prediksi habit, progres goal, riwayat tinjauan | `flutter analyze --fatal-infos` + `flutter test` + layar diketuk lawan api hidup (smoke); `flutter build web` lulus (**H-29**) |

> Tiap sprint ditutup seperti V0: **AI Review tiga lensa** (keamanan · kontrak ·
> penegak buta) → gerbang penuh `ci_lokal.py --lapor-github` → PR → HUMAN REVIEW.

---

## 🛑 Butir milik pemilik yang menyentuh V1

Draf ini **tidak** memutuskannya. Tugas yang tersentuh dikerjakan dalam bentuk
yang tidak mendahului jawabannya:

| Butir | Yang ditanyakan | Bentuk V1 tanpa jawabannya |
|---|---|---|
| **A-39** | draf backlog ini disetujui sebagai cakupan V1? | tidak ada kode V1 |
| **#34** | ambang High/Med/Low Confidence Layer | hanya *nol/sedikit bukti → bertanya*, seperti V0 5.4; tidak ada label High/Med/Low |
| **A-28** | sistem proaktif, sejak versi berapa | tidak ada notifikasi atau nudge; tinjauan menunggu dibuka |
| **C-39** | hak menolak/mematikan inferensi perilaku dan prediksi · retensi `behavior_daily` · `patterns` · `predictions` | 9.4 hapus per pola saja; anotasi `@retention` diusulkan, ditandai **menunggu C-39** |
| **A-29** · **C-20** | horizon proyeksi; proyeksi sebagai kelas data | horizon V1 ≤ 1 minggu (10.2 · 11.3) |
| **B-38** · **A-19** | sumbu dasbor yang V0/V1 tidak ukur | `not_measured` |
| **#18** | penyedia model | model statistik transparan, tanpa LLM berbayar |

## Yang dibetulkan sambil menyusun (E-249)

- [`../arch/10`](../arch/10-URUTAN-IMPLEMENTASI.md) §2 baris T1 menulis
  *“event · pola · prediksi · weekly review”* — kehilangan **analitik**
  ([`../arch/01`](../arch/01-PETA-20-FASE.md)) dan **Goal Engine** (naskah
  `75` §58). ✅ Diselaraskan dengan enam butir pemilik.
- **Tetap terbuka, dikerjakan di tugasnya:** pemilik tabel `human_states`
  (`arch/02` → `intelligence`, [`06`](06-MODULE-BOUNDARIES.md) → `profile`) ·
  tabel `patterns` vs **K-34** (→ 9.1) · domain penerbit `intelligence` (`arch/02`
  tiga, `arch/07` lima — V1 tidak menambah event, lihat atas).

---

## Yang TIDAK ada di backlog ini

Kafka · Spark · ClickHouse · lakehouse (`67` §38) · **Human State model,
Behavior Model, Scenario Simulation** (V4 — `75`) · Fashion · Wardrobe ·
Fitness · Nutrition · input tidur/olahraga/makan (V2) · Agent Registry · SDK ·
MCP (V3) · **pengiriman notifikasi & nudge proaktif** (**A-28**, Phase 11) ·
**Engagement Prediction** (bertabrakan dengan larangan manipulasi —
[#71](../../issues/71)) · satu angka **Life Score** (`63` §28) · Monthly Life
Review · pola **Environmental** & **Social** (V1 tidak punya sumber datanya) ·
prediksi energi/mood (bukan butir V1 pemilik) · model ML terlatih · penyedia
model berbayar (**#18**).

Semuanya ada di naskah; tak satu pun butir V1 pemilik. Menambahkannya adalah
cara V1 berhenti menjadi 5 sprint.
