# 11 — Penegakan

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Berkas ini tidak diminta naskah 24. Ia ada karena pelajaran repo ini sendiri,
> yang sudah muncul lebih dari sepuluh kali: **aturan yang dinyatakan tetapi
> tidak dijaga akan dilanggar, dan pelanggarannya baru ditemukan berkas-berkas
> kemudian.**

---

## §1 Kenapa berkas ini ada

| Aturan yang pernah dinyatakan | Berapa kali dilanggar sesudahnya |
|---|---|
| nama event `domain.verb` ([#38](../../issues/38)) | **128 nama**, sembilan dari sembilan naskah yang punya model event |
| monorepo final (**H-10**) | **sepuluh kali** |
| *“kode agent tidak boleh mengimpor `security/`”* (§8.42) | 🛑 tak pernah bisa **dinyatakan** — ada 19 pohon keamanan |
| `risk_level` ada di skema manifest | **13 tool persepsi** tanpa satu pun mengisinya |
| `Rollback` di daftar kendali (§11.61) | **hilang satu naskah kemudian** (§13.34) |
| awalan API `/v1` | janji di komentar penutup [#38](../../issues/38), **tak pernah dijalankan** sampai [K-8](../docs/KEPUTUSAN-DIDELEGASIKAN.md) |

> 🔑 **Pola tunggalnya:** semuanya adalah aturan yang **benar**, ditulis oleh
> orang yang **serius**, dan tidak satu pun punya sesuatu yang berkata *tidak*
> ketika dilanggar.
>
> 💡 **Karena itu satu baris tambahan berlaku untuk seluruh `arch/`: sebuah
> aturan di folder ini tidak dihitung SELESAI sampai barisnya ada di tabel §3.**

---

## §2 Kapan tiap pemeriksaan dipasang

| Kelompok | Dipasang di | Butuh kode? |
|---|---|---|
| **B** batas keras (6) | Sprint 0 tugas **0.8**, diperluas | sebagian — B-3·B-4·B-5 menyusul bersama modulnya |
| **M** modul & nama (4) | Sprint 0 **0.7 · 0.8** | ya |
| **P** penyimpanan & migrasi (6) | Sprint 0 **0.4** (alat migrasi) | ya |
| **E** event (4) | Sprint 3 **3.1**; **E-1 · E-2 bisa jalan SEKARANG atas `docs/`** | sebagian |
| **A** agent & tool (3) | Sprint 4 **4.2** (validasi manifest) | ya |
| **G** governance (1) | **sekarang** — atas tabel [`08`](08-AGENT-CONTRACTS.md) §4 | ❌ |
| **R** roadmap (1) | **sekarang** — atas tiap roadmap di `docs/` & `arch/` | ❌ |

⭐ **Empat pemeriksaan bisa dijalankan hari ini, dengan nol baris kode
produksi**: **E-1**, **E-2**, **G-1**, **R-1**. Keempatnya membaca dokumen, dan
dokumenlah yang selama ini menjadi tempat aturan dilanggar tanpa ketahuan.

---

## §3 Dua puluh lima pemeriksaan

### B · Batas keras — [`04`](04-DEPENDENCY-GRAPH.md) §2

| # | Memeriksa | Caranya | Gagal berarti |
|---|---|---|---|
| **B-1** | kode agent tidak mengimpor `security/` | `import-linter` kontrak `forbidden`: `agents.*` ✗→ `security.*` | Control Plane dan Data Plane menyatu |
| **B-2** | tidak ada jalur keluar selain Action Gateway | `forbidden`: modul mana pun ✗→ klien HTTP/SDK eksternal, kecuali `platform.gateway` | seluruh rantai gerbang menjadi opsional |
| **B-3** | simulasi tidak menulis ke penyimpanan nyata | `forbidden`: `simulation.*` ✗→ `*.repository`; ditambah uji integrasi yang menjalankan skenario dan memastikan **nol** baris berubah | *“bagaimana kalau”* menjadi *“sudah terjadi”* |
| **B-4** | `Code → Simulation → Safety Test → Hardware` | artefak biner untuk `embodiment/drivers/` **hanya dibangun** dari commit yang punya laporan `Safety Test` hijau untuk commit itu | kode yang belum pernah disimulasikan menggerakkan benda di dekat orang |
| **B-5** | kebijakan lokal hanya memperketat | tiap berkas policy diuji terhadap Konstitusi: himpunan izinnya wajib **⊆** himpunan izin induknya | Konstitusi berhenti menjadi lapisan tertinggi |
| **B-6** | tepat satu pohon `security/` | hitung direktori bernama `security`/`safety`/`privacy`/`consent`/`audit`/`permissions`/`policies`/`trust`/`compliance`/`ethics` di tingkat atas → **wajib 1** | B-1 tidak bisa dinyatakan |

> ⚠️ **B-4 sengaja menempel pada ARTEFAK, bukan pada PR.** Gerbang yang menempel
> pada PR bisa dilewati dengan menggabungkan lewat jalan lain; gerbang yang
> menempel pada artefak berarti **binernya tidak pernah ada**.

### M · Modul & nama — [`03`](03-MONOREPO-FINAL.md)

| # | Memeriksa | Caranya |
|---|---|---|
| **M-1** | tidak ada impor melingkar | `import-linter` kontrak `independence` |
| **M-2** | impor hanya lewat pintu keluar modul | `forbidden` ke `*.internal.*`; hanya `__init__.py` yang publik |
| **M-3** | modul domain tidak saling mengimpor | `independence` atas `services.*` — komunikasi lewat event |
| **M-4** | tidak ada nama direktori “telanjang” dari kamus tabrakan | daftar dari [`02`](02-BOUNDED-CONTEXT.md) §4; sebuah direktori bernama `simulation`/`state`/`planning`/`registry`/`graph` **di luar pemilik sahnya** = gagal |

### P · Penyimpanan & migrasi — [`06`](06-DATA-ARCHITECTURE.md) · [`09`](09-DEPLOYMENT-TOPOLOGY.md)

| # | Memeriksa | Gagal berarti |
|---|---|---|
| **P-1** | tiap `CREATE TABLE` punya `@retention`, `@who-can-set`, `@on-delete` | tabel tanpa retensi — sudah tercatat **empat kali** |
| **P-2** | tiap tabel punya kolom `data_subject` | tidak bisa dibedakan baris pengguna dari baris orang yang tak punya akun |
| **P-3** | tidak ada `user_id` yang nullable | RLS `user_id = current_user` **meloloskan `NULL`** pada sebagian konfigurasi |
| **P-4** | tabel `sensitivity >= 3` diakses hanya lewat `security/vault/` | keuangan mendapat perlindungan berbeda dari kesehatan **karena ada yang lupa** |
| **P-5** | tiap modul menyatakan `deploy: edge \| cloud \| both` | pengaman berakhir di cloud dan mati pada pemicunya sendiri |
| **P-6** | data kelas **K3** tidak punya jalur keluar perangkat | CSI mentah dan point cloud meninggalkan rumah |

### E · Event — [`07`](07-EVENT-CONTRACTS.md)

| # | Memeriksa | Caranya |
|---|---|---|
| **E-1** | segmen pertama `event_type` ada di registry domain | daftar 39 domain [`07`](07-EVENT-CONTRACTS.md) §2; **bisa jalan sekarang atas `docs/`** |
| **E-2** | format dua segmen, huruf kecil, kata kerja lampau | regex; **bisa jalan sekarang** |
| **E-3** | tidak ada `source='sensor'` di `events` | grep DDL + uji admisi |
| **E-4** | tiap kata kerja pengubah keadaan punya kembaran kegagalan/pemulihan | daftar pasangan wajib [`07`](07-EVENT-CONTRACTS.md) §6 |

### A · Agent & tool — [`08`](08-AGENT-CONTRACTS.md)

| # | Memeriksa | Gagal berarti |
|---|---|---|
| **A-1** | satu angka tidak dipakai untuk `R` **dan** `L` | `risk: R2` sebagai properti agent membalik **H-21** |
| **A-2** | tiap tool di `tools:` punya `risk_level <= max_risk` | manifest bisa berbohong tentang apa yang bisa dilakukannya |
| **A-3** | agent yang memanggil agent lain punya entri `kind: agent` di tool registry | sisi pohon eksekusi tidak melewati gerbang — **K-14** |

### G · Governance

| # | Memeriksa |
|---|---|
| **G-1** | tiap pasal Konstitusi §20.16 punya **≥ 1** penegak di tabel [`08`](08-AGENT-CONTRACTS.md) §4. Pasal tanpa penegak = gagal; pasal yang penegaknya **sebagian** wajib menyebutkan bagian yang tidak bisa diperiksa mesin |

### R · Roadmap

| # | Memeriksa |
|---|---|
| **R-1** | untuk tiap roadmap, tiap pasangan (gerbang **G**, hal yang dijaga **T**): `index(G) < index(T)`. Daftar pasangannya dari [`10`](10-URUTAN-IMPLEMENTASI.md) §2 |

---

## §4 🔴 Apa yang R-1 temukan kalau dijalankan atas roadmap yang SUDAH ada

Dijalankan hari ini, tanpa kode, atas roadmap di `docs/`:

| Roadmap | Pasangan | Hasil |
|---|---|---|
| `A14.x` Phase 14 | federasi (A14.1) ← Security Mesh (A14.7) | 🛑 **GAGAL** — [#99](../../issues/99) |
| `R16.x` Phase 16 | humanoid · drone · manipulasi ← `R16.10` Safety Kernel | 🛑 **GAGAL** — [#111](../../issues/111) |
| `H17.x` Phase 17 | seluruh MVP ← `H17.12` Health Safety (**di luar MVP**) | 🛑 **GAGAL** — [#116](../../issues/116) |
| Phase 18 | §18.30 Query Engine ← §18.22 Safety Kernel (**tanpa milestone**) | 🛑 **GAGAL** — [#121](../../issues/121) |
| `S19.x` Phase 19 | Digital Laboratory ← `S19.10` Ethics & Safety | 🛑 **GAGAL** — [#131](../../issues/131) |
| `C20.x` Phase 20 | `C20.6` Coordination ← `C20.7` Governance | 🛑 **GAGAL** — [#144](../../issues/144) |
| **`../spec/07` Sprint 0–6** | kode domain ← 0.8 lint; agent (4.6–4.7) ← 4.5 risk gate | ✅ **LULUS** |
| **`arch/10` T0–T12** | tiap tahap ← gerbangnya | ✅ **LULUS** |

> 🔑 **Enam roadmap gagal, dua lulus — dan yang lulus keduanya ditulis sebagai
> pekerjaan engineering, bukan sebagai peta fase.** Itu perbedaan yang lebih
> berguna daripada menyalahkan naskah mana pun: roadmap yang ditulis untuk
> **dikerjakan** menaruh gerbangnya lebih dulu; roadmap yang ditulis untuk
> **menggambarkan** menaruh yang paling menarik lebih dulu.

⚠️ Keenam kegagalan itu **sudah punya issue** dan **tetap milik pemilik** —
mengurutkan ulang roadmap fase adalah keputusan cakupan. Yang berubah karena
R-1: ia berhenti menjadi enam catatan terpisah di enam berkas, dan menjadi
**satu pemeriksaan yang berbunyi setiap kali roadmap baru ditulis**.

---

## §5 Yang penegakan ini **tidak** bisa lakukan

Ditulis supaya tidak ada yang mengira daftar §3 lebih kuat daripada yang
sebenarnya.

| Tidak terjaga | Kenapa | Tempatnya |
|---|---|---|
| apakah sebuah penjelasan **menyesatkan** (Pasal 8) | penilaian, bukan pola | `evaluation/red-team/` |
| apakah `social cohesion 0.68` **berarti** apa pun | angka tanpa rumus tetap lolos tipe | [#145](../../issues/145) — pemilik |
| apakah **batas gaya** robot cukup rendah | butuh angka yang belum ada | [#112](../../issues/112) — pemilik |
| apakah pengulangan **memperkuat kesalahan sistematis** | kamera salah sudut salah **setiap hari**, lalu naik pangkat jadi *pola* | [#77](../../issues/77) **B-25** — butuh rancangan deteksi bias |
| apakah `bystander` **boleh ada** | hukum | [#40](../../issues/40) · [#76](../../issues/76) — pemilik |

> 💡 **Pola yang sama pada kelimanya:** yang tidak bisa diperiksa mesin adalah
> yang menuntut **penilaian tentang akibat pada orang lain** — dan itu tepat
> kelas keputusan yang aturan pemilah serahkan kepada pemiliknya. Kebetulan itu
> bukan kebetulan.

---

## §6 Pemeriksaan yang harus lulus

| | Hasil |
|---|---|
| Jumlah pemeriksaan | **25** |
| Batas keras tanpa penegak | **NIHIL** — 6 dari 6 |
| Aturan 🔧 di `arch/` tanpa baris di §3 | **NIHIL** |
| Pemeriksaan yang bisa jalan tanpa kode | **4** — E-1 · E-2 · G-1 · R-1 |
| Perkakas yang dibutuhkan | **1** — `import-linter` menangani B-1·B-2·B-3, M-1·M-2·M-3 |
| Roadmap yang lulus R-1 | **2 dari 8** — dan keduanya ditulis untuk dikerjakan |
