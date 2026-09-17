# 06 — Data Architecture

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“data architecture”* naskah 24. Menutup
> [#74](../../issues/74) (**E-89**) · [#107](../../issues/107) (**B-31**) ·
> [#119](../../issues/119) (**B-34**) · [#127](../../issues/127) (**B-35**) ·
> [#151](../../issues/151) (**E-156**); memberi mekanisme bagi
> [#128](../../issues/128) (**A-33**) dan [#145](../../issues/145) (**B-38**).

---

## §1 Skema ditulis untuk HIMPUNAN, dan himpunannya 247

Hitungan tabel dicatat sebagai **penjumlahan berjalan** dan **berhenti
dipelihara di Phase 12**:

```
23 (V0) + 20 (Fase 8) + 16 (Fase 10) + 14 (Fase 11) + 26 (§12.28) = 99
```

Aritmetikanya benar. Yang salah: **delapan fase sesudahnya menambah tabel dan
tak satu pun masuk hitungan.** Himpunan sesungguhnya **247 nama**, dan
**139 di antaranya lahir sesudah Phase 12**
([`../docs/SENSUS-TABEL.md`](../docs/SENSUS-TABEL.md)).

⭐ **Dan kabar baik yang menentukan seluruh berkas ini:** belum ada satu baris
kode pun, jadi **tidak satu pun dari 247 nama sudah mengunci migrasi.** Itu
keadaan yang tidak akan bertahan setelah baris pertama ditulis.

---

## §2 Uji admisi — sebuah nama tabel masuk kelas mana

> 🔑 **PostgreSQL menyimpan apa yang seorang manusia akan kenali sebagai sebuah
> catatan. Apa pun yang tercuplik pada laju yang tidak dihasilkan manusia tidak
> pernah menyentuhnya — ia mencapai PostgreSQL hanya sebagai RINGKASAN.**

```
untuk tiap nama tabel N:
  1. Apakah satu barisnya dihasilkan oleh KEPUTUSAN atau KEJADIAN manusia?
     ya   → K1 (PostgreSQL)                    contoh: habit_completions
  2. Apakah ia deret waktu bertanda waktu, laju < ~1 Hz, dan masih ber-JOIN
     ke K1?
     ya   → K2 (TimescaleDB)                   contoh: heart_rate_samples
  3. Apakah tiap sampelnya sebuah MATRIKS/BINGKAI, atau lajunya ≥ ~1 Hz?
     ya   → K3 (object storage, Parquet)       contoh: wifi_csi, point_clouds
            ⇒ dan ia TIDAK PERNAH meninggalkan perangkat sebagai mentah (§15.29)
  4. Apakah ia bisa dibangun ulang dari 1–3?
     ya   → K4 (turunan: Qdrant · Neo4j · feature store)
```

| Kelas | Teknologi | Retensi bawaan | Kehilangannya berarti |
|---|---|---|---|
| **K1** Catatan | PostgreSQL 16 | **wajib dinyatakan per tabel** — §5 | kehilangan data |
| **K2** Deret waktu | TimescaleDB (ekstensi) | ringkas otomatis; mentah dibuang | kehilangan detail, bukan fakta |
| **K3** Aliran mentah | object storage + Parquet | **jam, bukan hari** | ~nihil — ringkasannya sudah di K1/K2 |
| **K4** Turunan | Qdrant · Neo4j · Parquet | dibangun ulang | **nihil** — bisa dihitung ulang |

### 🔴 Aritmetika yang menjadikan aturan ini bukan selera

| Sumber | Laju | 30 hari · 1 pengguna |
|---|---|---|
| `habit.completed` | belasan/hari | **~400 baris** |
| `PersonDetected` @ 1 Hz | 86.400/hari | **2,6 juta baris** — satu kamera |
| `wifi_csi` @ 10–100 Hz | 0,86–8,6 juta/hari | **26–260 juta**, tiap sampel sebuah matriks |

⇒ Menaruh baris ketiga di tabel `events` — yang dirancang untuk **puluhan
kejadian manusia per hari**, dengan `UNIQUE (user_id, idempotency_key)` —
adalah kesalahan **berorde besaran**, bukan kesalahan gaya.

⭐ **Jawabannya sudah ditulis pemilik sendiri, dua kali:** §10.10 (*5 bingkai →
1 event*) dan §10.11 (*5.400 pembacaan → 1 kalimat*). Yang tidak pernah
dilakukan hanyalah menyambungkannya ke §10.30.

---

## §3 Uji admisi `events` — menutup [#74](../../issues/74)

Tabel `events` adalah **sumber kebenaran perilaku** (`spec/README` prinsip 3).
Kalau ia menerima aliran sensor, ia berhenti bisa menjadi itu.

> 🔑 **`events` hanya menerima kejadian yang BERMAKNA BAGI MANUSIA.**
> Sebuah baris masuk hanya bila ketiganya benar:

| | Syarat | Kalau tidak |
|---|---|---|
| 1 | pengguna bisa **mengenalinya** kalau ditunjukkan (*“Anda menyelesaikan lari 06.30”*) | ia pengukuran, bukan kejadian → K2/K3 |
| 2 | ia punya **`idempotency_key` yang bermakna** — pengiriman ulang berarti hal yang sama | untuk aliran bingkai, `idempotency_key` kehilangan arti |
| 3 | `source` termuat dalam `CHECK` yang ada — **`app · agent · integration · backfill`** ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)) | 🛑 `sensor` **tidak** ditambahkan — lihat bawah |

🛑 **`source='sensor'` sengaja TIDAK ditambahkan ke `events`.** Menambahkannya
akan membuat uji ini bisa dilewati dengan satu nilai enum. Aliran sensor masuk
lewat `perception/summarizer/`, dan yang diterbitkannya adalah kejadian yang
sudah **lulus syarat 1**, dengan `confidence` + `evidence_count`, sebab ia
memang kesimpulan. Ditegakkan **E-3** atas DDL sejak 16 Sep 2026.

> 🔴 **E-162 — dikoreksi 16 Sep 2026, dan koreksinya membuka satu pertanyaan
> yang sengaja tidak dijawab di sini.** Baris 3 semula menulis himpunan
> `manual · inferred · integration · agent` — itu himpunan
> **`activities.source`** (ditambah `agent`), bukan `events.source`. Paragraf
> di atas juga semula menyuruh *summarizer* menerbitkan dengan
> **`source='inferred'`** — nilai yang **`CHECK` `events` sungguhan akan
> tolak**. Ditemukan saat E-3 membaca `CHECK` itu dari DDL untuk pertama
> kalinya, bukan dari kalimat yang menggambarkannya.
>
> ⚠️ **Nilai `source` bagi kejadian hasil ringkasan sensor belum diputuskan.**
> Dua jalan, keduanya murah dan keduanya bisa ditambahkan nanti (lulus uji
> K-16 sebagai *bukan untuk V0*): menambah `inferred` ke `CHECK` `events`,
> atau menerbitkan sebagai `agent`. Diputuskan di tugas pertama
> `perception/summarizer/` (**T6**) — yang pemblokirnya
> [#75](../../issues/75) milik pemilik.

---

## §4 Sembilan belas nama berdefinisi ganda — diselesaikan

[K-4](../docs/KEPUTUSAN-DIDELEGASIKAN.md): kalau nama sudah ada di
[`../spec/01`](../spec/01-DATABASE-SCHEMA.md), definisi `spec/01` berlaku;
kalau tidak, **fase paling awal** yang kanonik. Fase berikutnya boleh
**menambah kolom**, tidak boleh **mendefinisikan ulang**.

| Nama | Didefinisikan di | **Bentuk kanonik** | **Konteks pemilik** |
|---|---|---|---|
| `users` · `permissions` · `consents` · `audit_logs` | V0 · P8 | **`spec/01`** | `identity` |
| `agents` · `agent_runs` | V0 · P11 | **`spec/01`** | `agents` |
| `agent_capabilities` | **P8 · 11 · 14 · 18** | **Phase 8** | `agents` |
| `agent_trust_scores` | **P8 · 11 · 14 · 18** | **Phase 8** | `agents` |
| `agent_versions` · `agent_messages` | P11 · 14 | **Phase 11** | `agents` |
| `world_entities` · `world_events` · `world_relationships` · `world_states` | P12 · 18 | **Phase 12** | `world-model` |
| `policies` · `sessions` | P8 · 20 | **Phase 8** | `security` · `identity` |
| `navigation_paths` | P15 · 16 | **Phase 15** | `spatial` |
| `spatial_maps` | **P10 · 15** | **Phase 10** | **`spatial`** ⚠️ |
| `simulations` | P19 · 20 | **Phase 19** | `simulation` |

> ⚠️ **Baris `spatial_maps` memperlihatkan bahwa dua pertanyaan berbeda sedang
> dijawab, dan keduanya perlu.** K-4 memutuskan **BENTUK** (definisi Phase 10
> yang lebih dulu); bounded context memutuskan **PEMILIK** (`spatial`, bukan
> `perception`). Sebuah tabel bisa berbentuk seperti yang ditulis fase A dan
> dimiliki modul yang lahir di fase B — itu bukan konflik, itu dua sumbu.
> 💡 Aturannya sama dengan aturan pengutamaan [`README.md`](README.md):
> **`arch/` mengikat nama & batas, `spec/` mengikat bentuk.**

🛑 **`agent_capabilities` dan `agent_trust_scores` adalah yang paling penting
dari sembilan belas.** Keduanya menentukan **apa yang boleh dilakukan sebuah
agent**; empat definisi berarti empat kemungkinan bentuk kolom untuk pertanyaan
yang gerbang risiko bacakan setiap kali agent bertindak.

⚠️ **Nama tabel tetap JAMAK.** Aturan tunggal/jamak
[`03`](03-MONOREPO-FINAL.md) §7 berlaku bagi **direktori**, bukan tabel —
`spec/01` memakai bentuk jamak dan tidak diubah.

---

## §5 Retensi — tidak ada tabel tanpa pernyataan

Tabel tanpa retensi sudah tercatat **empat kali**
([#127](../../issues/127) · [#145](../../issues/145)), sementara §20.13 memberi
**PENGGUNA** kendali *“How long”*. Kendali yang tidak punya tempat untuk
disimpan bukan kendali.

🔧 **Aturan: setiap tabel menyatakan tiga hal, dan migrasi tanpa ketiganya
ditolak CI** ([`11`](11-PENEGAKAN.md) P-1):

```sql
-- @retention   : 24 months | forever | 90 days | until-account-deleted
-- @who-can-set : system | user | law
-- @on-delete   : hard | anonymise | keep-metadata-only | not-applicable
```

> 🔧 **`not-applicable` ditambahkan 11 September 2026**, saat aturan ini
> dipasang pada 23 tabel V0 ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)).
> Tiga nilai pertama semuanya menjawab *“apa yang terjadi pada baris ini
> ketika sebuah AKUN dihapus”* — dan katalog sistem (`agents`,
> `agent_tools`, `data_subject='system'`) **tidak punya akun untuk
> dihapus**. Memaksanya memilih salah satu dari tiga berarti menulis
> jawaban yang tidak benar supaya kolomnya terisi.
> 💡 **Kosakata yang tidak punya nilai untuk “tidak berlaku” akan
> mengumpulkan kebohongan kecil di baris-baris yang tidak cocok.**

| Nilai `who-can-set` | Artinya | Contoh |
|---|---|---|
| `user` | pengguna boleh memendekkan **dan** memperpanjang | `journal_entries` |
| `system` | tetap; pengguna boleh **memendekkan**, tidak memperpanjang | `agent_runs` |
| `law` | 🛑 **tidak bisa diubah siapa pun** — dan siapa yang menetapkannya **bukan keputusan saya** | `emergency_events` |

### Tiga tabel yang retensinya bukan soal kerapian

| Tabel | Kenapa |
|---|---|
| `audit_logs` | **C-9** ([#22](../../issues/22)) — hak hapus lawan jejak yang tidak boleh diubah. Jalan keluarnya sudah ada di `spec/README` prinsip 5: jejak menyimpan **metadata**, bukan isi ⇒ hard-delete isi tidak merusak jejak |
| `emergency_events` | 🛑 barisnya adalah **bukti hukum kalau terjadi cedera** ([#114](../../issues/114)). Ia tidak bisa sekadar tidak disimpan, dan tidak bisa dipendekkan pengguna |
| `world_observations` | 🔴 tumbuh *waktu × frekuensi × seluruh dunia* dan **tidak dibagi per pengguna** ⇒ **nol pembatas alami** (**H-12**). Lihat §6 |

---

## §6 🔴 Prinsip V0 *“tidak ada tabel tanpa `user_id`”* tidak bertahan melewati Phase 15

`spec/README` prinsip 6 menyatakan: *tidak ada tabel tanpa `user_id` kecuali
katalog sistem* — menyiapkan Row-Level Security. Prinsip itu **benar untuk V0**
dan **patah** pada fase pertama yang datanya tentang **tempat**, bukan orang:

| Tabel | Subjeknya | `user_id`? |
|---|---|---|
| `people_tracks` · `PersonEntered`/`PersonExited` (§15.28) | orang di dalam rumah — **belum tentu punya akun** | ❌ |
| `HumanDetected` (§16.31) | orang di dekat robot | ❌ |
| `world_observations` (§18.28) | dunia | ❌ |

🔧 **Perluasan prinsip 6, bukan penggantinya:**

> **Setiap tabel wajib punya `data_subject`. Kalau `data_subject = 'user'`, maka
> `user_id` WAJIB TIDAK NULL. Kalau tidak, `user_id` TIDAK BOLEH ADA sama
> sekali — bukan `NULL`.**

> ⚠️ **Dipertajam 11 September 2026: `data_subject` adalah sifat BARIS,
> bukan tetapan TABEL — dan contoh tandingannya sudah ada di dalam V0.**
> `audit_logs` memuat baris yang pelakunya pengguna **dan** baris yang
> pelakunya sistem (`actor_type IN ('user','agent','system','admin')`).
> Untuk tabel semacam itu aturan di atas tidak bisa ditegakkan sebagai
> `NOT NULL` pada kolom; ia ditegakkan sebagai **CHECK**:
>
> ```sql
> CHECK ((data_subject = 'user') = (user_id IS NOT NULL))
> ```
>
> 💡 Aturan aslinya sudah ditulis dalam bentuk BARIS (*“kalau
> `data_subject = 'user'`, maka…”*); yang keliru adalah menganggapnya
> bisa diwujudkan di tingkat kolom. Ditemukan **P-3**
> ([`11`](11-PENEGAKAN.md)) — dan hanya karena §6 dijalankan atas tabel
> yang SUDAH ADA, bukan atas tabel Phase 15 yang menjadi alasannya
> ditulis.

```
data_subject : 'user' | 'bystander' | 'world' | 'system'
```

> ⚠️ **Namanya `data_subject`, bukan `subject_type` — dan itu bukan selera.**
> Amplop event [`../spec/03`](../spec/03-EVENT-CONTRACTS.md) **sudah** memakai
> `subject_type`, dengan arti lain: *jenis entitas* yang diacu event
> (`"habit"`, `"goal"`). Memakai kata yang sama untuk *siapa yang datanya* akan
> menambah satu baris lagi ke kamus tabrakan [`02`](02-BOUNDED-CONTEXT.md) §4 —
> di berkas yang tugasnya menghapusnya.
> 💡 Tertangkap dengan memeriksa nama usulan terhadap `spec/` **sebelum**
> menulisnya, bukan sesudah. Itu pemeriksaan yang murah dan layak diulang untuk
> tiap nama kolom baru.

| Kenapa bukan `user_id NULL` | |
|---|---|
| `NULL` berarti *“belum diisi”* | dan itu **arti yang sudah dipakai** untuk hal lain |
| baris `bystander` akan tampak seperti baris pengguna yang datanya kurang | ⇒ suatu hari seseorang akan “melengkapinya” |
| Row-Level Security tidak bisa dibedakan | policy `user_id = current_user` **meloloskan `NULL`** pada sebagian konfigurasi |

> 🔧 **RLS V0 kini nyata, bukan rencana** (17 Sep 2026, keputusan pemilik
> **H-27**). Kebijakannya membandingkan `user_id` dengan
> `app_current_user_id()` — pengguna yang dilayani **transaksi**, bukan
> `current_user` basis data — dan fungsi itu memulangkan `NULL` kalau tidak
> diisi, sehingga kebijakan tidak meloloskan satu baris pun. Bentuk lengkap:
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) §10–§11.

> 💡 **Ini bentuk lain dari pertanyaan yang menghasilkan K-10 dan K-12:**
> *apa yang dipulangkan medan ini ketika ia tidak berlaku — dan apakah nilai itu
> SUDAH PUNYA ARTI LAIN?* `NULL` sudah punya arti lain. Kolom yang absen tidak.

🛑 **Yang TETAP milik pemilik:** apakah baris `bystander` boleh ada sama sekali
([#40](../../issues/40) **C-10**, [#76](../../issues/76) **C-18**,
[#105](../../issues/105) **A-31**) — orang itu tidak punya akun, tidak
menyetujui apa pun, dan tidak bisa tahu. Berkas ini hanya memastikan bahwa
kalau ia ada, ia **tidak menyamar sebagai pengguna**.

### `world_observations` — satu-satunya tabel tanpa pembatas alami

🔧 Setiap tabel `data_subject='world'` **wajib** punya kunci partisi selain
waktu (`region_id`, `source_id`, atau `topic`) **dan** batas atas laju tulis
yang dinyatakan. Tanpa itu ia bukan tabel; ia aliran yang menyamar sebagai
tabel — dan tempatnya K2/K3, bukan K1.

---

## §7 Vault berdasarkan SENSITIVITAS, bukan berdasarkan domain

**Mekanisme untuk [#128](../../issues/128) (A-33).**

§17.5 memberi **Health Vault** yang lengkap. §18.28 memasukkan **data keuangan
pribadi** tanpa vault, tanpa `sensitivity`, dan tanpa satu tabel pun — padahal
§8.16 menaruh keuangan **sekelas kesehatan** (Level 3–4).

🔧 **Vault bukan fitur Phase 17. Ia kemampuan `security/vault/`, dan yang
memicunya adalah KLASIFIKASI, bukan nama domain:**

```
sensitivity: 1 | 2 | 3 | 4        ← wajib pada setiap tabel
level ≥ 3  ⇒  security/vault/ :  enkripsi per-pengguna
                                  akses lewat audit trail
                                  tidak pernah masuk context package
                                    tanpa scope eksplisit
```

⇒ Kesehatan, keuangan, jurnal, biometrik, dan `csi` mendapat perlindungan yang
sama **karena tingkatnya sama** — bukan karena ada yang ingat menuliskannya
untuk masing-masing.

⚠️ **G-6** ([#57](../../issues/57)) mencatat Level 4 *“Highly Sensitive”*
**tanpa satu contoh pun**, dan
[#117](../../issues/117) mencatat **dua tangga sensitivitas** (lima nama §17.4
lawan empat angka §8.16) tanpa pemetaan. 🔧 Yang berlaku di sini: **empat angka
§8.16**, sebab ia yang sudah dipakai kolom. Pemetaan lima-nama → empat-angka
ditulis di `security/compliance/`, dan **contoh untuk Level 4 tetap milik
pemilik** — ia menentukan apa yang tidak boleh keluar dari negara pengguna.

---

## §8 Perubahan untuk V0: satu, dan ia keputusan lama

| | |
|---|---|
| Tabel V0 | **23**, tidak berubah — [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) |
| Kelas penyimpanan V0 | **K1 saja** (+ Redis untuk sesi/antrean, K4 Qdrant di Sprint 3) |
| K2 dipakai sejak | Phase 10 / V5 |
| K3 dipakai sejak | Phase 15 |
| Kolom baru yang dituntut berkas ini untuk V0 | **`retention` sebagai komentar migrasi** — nol kolom, nol migrasi |
| Kolom yang **berubah** | **1** — `agents.risk_level` → `max_risk`, `requires_confirmation` dihapus. Bukan keputusan baru: [#52](../../issues/52) + **H-21** + **E-119**, tiga keputusan yang tidak pernah sampai ke DDL |

⚠️ Satu-satunya hal yang **harus** masuk V0 dan belum ada:
**`consents.purpose` + `kind='model_training'`** — **B-22**
([#59](../../issues/59)). Penegakannya satu operasi himpunan:

```
data.purpose  ⊆  consent.purpose
```

Biayanya **nol sekarang** dan hampir mustahil nanti: data V0 yang dikumpulkan
tanpa itu **tidak bisa melatih model apa pun** di Phase 5.

---

## §9 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Nama tabel diketahui | **247** — bukan 99 |
| Nama berdefinisi ganda tanpa vonis | **NIHIL** — 19 dari 19, §4 |
| Kelas penyimpanan | **4**, dan uji admisinya mekanis (§2) |
| `source='sensor'` di `events` | ❌ **sengaja tidak ada** |
| Tabel tanpa `retention` | ditolak CI — [`11`](11-PENEGAKAN.md) P-1 |
| Tabel tanpa `data_subject` | **NIHIL** — 23 dari 23 tabel V0, dipasang **K-16** 11 Sep 2026; ditolak CI — P-2 ✅ **jalan** |
| Tabel tanpa tiga anotasi retensi | **NIHIL** — 23 dari 23; ditolak CI — P-1 ✅ **jalan** |
| `user_id` nullable tanpa penjaga | **NIHIL** — `audit_logs` memakai CHECK §6; ditolak CI — P-3 ✅ **jalan** |
| Tabel `user_id NULL` | ditolak CI — P-3; kolomnya absen, bukan null |
| Tabel `sensitivity ≥ 3` di luar vault | ditolak CI — P-4 |
| Tabel V0 | **23**, tidak berubah |
