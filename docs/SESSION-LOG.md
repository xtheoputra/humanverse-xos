# Catatan Sesi

> Ringkasan tiap sesi kerja. Yang terbaru di atas.

---

## Sesi 6 — 3 September 2026

**Naskah kedelapan direkam — peta Phase 5–12, dan satu angka bertabrakan 10×.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Peta Phase 5–12** + taksiran kemajuan 45 % → berkas `113` |
| Dokumen total | 99 → **100** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### Yang diperiksa dan benar

- **Aritmetika delapan fase benar**: 50+40+50+30+30+40+40+100 = **380**, tepat
  di dalam rentang "300–500 dokumen".
- **"Tidak ingin memperpanjang hanya demi panjang"** — pertama kalinya dalam
  delapan naskah pemilik membatasi dirinya sendiri sebelum diminta.
- **Bias Detection** dan **Human Override** benar-benar baru. *Human Override*
  khususnya adalah pasangan yang selama ini hilang dari janji *"Act di bawah
  kontrol pengguna"*: yang ditulis baru **izin sebelum** aksi, belum
  **pembatalan sesudah**.

### Tiga temuan

- **E-51** — Phase 5 berbeda **sepuluh kali lipat** antara dua naskah: naskah 7
  menulis *500+ spesifikasi*, naskah 8 menulis *50+ dokumen*. Aritmetika naskah
  8 sendiri membuktikan 50+ yang benar (total 380), tapi butuh konfirmasi.
- **E-52** — **Multi-Agent Collective Intelligence hilang** dari Phase 5.
  Itu justru riset di balik janji pembuka naskah 2: *"ratusan AI Agent bekerja
  secara bersamaan"*.
- **E-53** — Phase 8, 11, dan 12 **sebagian mengulang** yang sudah ditulis.
  Phase 12 (*Event Schema, Agent Contracts, Sprint Backlog, CI/CD, Docker*)
  adalah pekerjaan yang **sudah selesai untuk V0** di `spec/` — bedanya hanya
  skala (23 tabel vs 100+, ~40 endpoint vs 500+).

### 🔧 Koreksi hitungan saya sendiri

Sesi lalu saya menulis "lewat **900 dokumen**". Itu **terlalu besar** — saya
menjumlahkan lingkup yang tumpang tindih. Naskah 8 memberi angka yang lebih
tepat: **380** untuk delapan fase tersisa, dan sebagiannya mengulang yang sudah
ada. Butir **A-24** diperbaiki.

### Dua risiko baru

- **C-12** — *Company Wellness* (Phase 9) berarti **pemberi kerja** menyentuh
  data kesehatan pekerja. Berbeda dari *Coaches* karena ada ketimpangan
  kekuasaan: persetujuan kepada atasan tidak pernah sepenuhnya bebas.
- **B-19** — Phase 10 (*Email Automation*, *Cross-App Actions*) adalah **ujian
  pertama** janji kendali manusia. Itu Risk Level 3, tingkat yang sengaja tidak
  punya satu pun tool di V0.

---

## Sesi 5 — 3 September 2026

**Naskah ketujuh direkam — dan lubang naskah 3 terulang persis.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Phase 4 Enterprise OS**, Layer 21–50 + teaser Phase 5 |
| Dokumen ditambah | **13 berkas** (`100`–`112`) |
| Dokumen total | 86 → **99** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### ⚠️ Dua lubang, bentuknya sama seperti naskah 3

| Naskah 3 | Naskah 7 |
|---|---|
| Layer 14 terpotong di tengah tabel (**G-1**) | Layer 44 terpotong di tengah tabel (**G-4**) |
| Layer 15/16 hilang + fragmen tanpa judul (**G-2**) | Layer 45 hilang + fragmen *"jangan lompat ke Kubernetes"* (**G-5**) |

Dua naskah panjang, dua tabel terpotong di tempat yang sama macamnya.
Kemungkinan besar batas salin-tempel. **Ditandai hilang, tidak ditambal.**

### Yang paling berguna dari naskah ini

- **Layer 40: Memory ≠ Knowledge.** *Memory = pengalaman pengguna, Knowledge =
  pengetahuan dunia.* Menjelaskan kekaburan lama *Semantic Memory*, dan punya
  konsekuensi nyata: pengetahuan dunia tidak ikut terhapus saat akun dihapus.
- **Layer 50: empat fondasi** — rumusan visi paling tajam dari tujuh naskah,
  dan tiga dari empat sudah punya bentuk teknis di V0.
- **Layer 34:** *"Jangan mengoptimalkan manipulasi; optimalkan pengalaman
  pengguna"* — ditulis di baris yang sama dengan *retention* dan *engagement*.
- **ADR-004** mengunci LangGraph; disebut sejak naskah 2, baru sekarang jadi
  keputusan.

### Delapan ketidakcocokan baru (E-43..E-50)

Yang paling mendesak: **E-43** — format nama event **tiga segmen**
(`fashion.outfit.selected`) bertabrakan dengan **dua segmen** di naskah 5 §7
(21 event, semuanya dua segmen). **Nama event tidak boleh diganti setelah
dipakai**, jadi harus dipilih sebelum Sprint 3.

Juga: **E-48** dua daftar persona di dua lapisan berdampingan (hanya *Student*
yang sama), dan **E-45** rantai percakapan 9 langkah yang melewatkan
Safety/Risk.

### Hitungan yang perlu diperhatikan

Phase 5 menambah **500+ spesifikasi riset**. Total: 100 → 160 → 300+ →
14 lapisan → +500 = lewat **900 dokumen**, dengan **0 baris kode**
(butir **A-24**).

---

## Sesi 4 — 3 September 2026

**Naskah keenam direkam — lalu lapisan 04 dikerjakan: Engineering Spec v1.0.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Peta 14 lapisan engineering + Operating Model** → berkas `98` |
| Hasil kerja baru | **`spec/`** — 8 berkas, **bukan kata pemilik** |
| Dokumen total | 85 → **86** di `docs/`, + 8 di `spec/` |
| Berkas kode | tetap **0** |

### Isi `spec/`

23 tabel PostgreSQL dengan DDL lengkap · ERD + 6 aturan kepemilikan data ·
22 event dengan versi/urutan/idempotensi · endpoint REST V0 + Privacy Center ·
manifest agent dengan 6 aturan validasi + risk gate · batas modul yang
ditegakkan CI · **51 tugas** dalam 7 sprint.

### Temuan terbesar sesi ini

**Tiga issue yang saya kira memblokir ternyata tidak perlu diputuskan sekarang** —
skemanya bisa menampung kedua kemungkinan tanpa biaya:

| Issue | Ternyata |
|---|---|
| #33 memory: jenis atau scope | **keduanya** — menjawab pertanyaan berbeda (`kind` = pengambilan, `scope` = izin) |
| #32 tiga skala skor | simpan **0–1** — 100-poin & persen lossless ke sini, sebaliknya tidak |
| #2 lima model angka | `metrics jsonb`, bukan 7 kolom tetap |
| #7 model graf | **tidak menyentuh V0** — Neo4j baru V2 |

Artinya **V0 bisa dimulai sekarang**; penghambat nyata tinggal #3 (waktu) dan
#20 (merek). ⚠️ Tapi menunda bukan menjawab — selama #2 belum dipilih, tidak
ada yang bisa **menghitung** angkanya.

### Cacat yang ditemukan dari menulis spesifikasi (E-42)

Daftar 19 tabel V0 naskah 5 §31 **tidak cukup untuk arsitektur V0 sendiri**:
tidak ada `events` (padahal §30 menggambar *Event System* sebagai lapisan wajib
dan §7 berkata *"setiap aktivitas menjadi event"*), dan `agent_runs` menunjuk
tabel `agents` yang tidak ada. Ditemukan hanya karena mencoba menulis DDL-nya —
tidak terlihat saat membaca naskah.

---

## Sesi 3 — 3 September 2026

**Blueprint Engineering v1.0 direkam — lima butir ditutup, satu dibatalkan.**

| Hal | Hasil |
|---|---|
| Naskah baru | **Blueprint Engineering v1.0**, 34 bagian |
| Dokumen ditambah | **18 berkas** (`80`–`97`) |
| Dokumen total | 67 → **85 berkas** di `docs/` |
| Berkas kode | tetap **0** |

### Yang naskah 5 tutup

| # | Butir | Jawaban |
|---|---|---|
| H-10 | E-27 struktur repo | Monorepo final — **menggabungkan** struktur naskah 2 dan naskah 4 |
| H-11 | E-2/E-28 Weather & Calendar | **Tool**, bukan agent |
| H-12 | A-10 Kafka vs Redis Streams | **Empat penyimpanan**: PostgreSQL · Qdrant · Neo4j · Redis |
| H-13 | A-18 Phase vs V0–V6 | **V0–V6** — Phase 1/2/3 tidak disebut sekali pun |
| H-14 | B-15/B-1 angka taksiran & cold start | **Confidence Layer** — `confidence` + `evidence_count`, low → tanya pengguna |

### ❌ Yang dibatalkan

**H-8 gugur.** GroomingAgent yang kembali di naskah 4 **hilang lagi** di daftar
22 agent naskah 5, bersama HealthAgent, ProductivityAgent, EntertainmentAgent,
dan ResearchAgent. Satu naskah memulihkan sesuatu bukan berarti sudah tetap.

### Yang naskah 5 buka (E-34..E-41)

- **A-19 memburuk**: kini **lima** model angka pengguna, HumanState turun jadi
  7 field (`mood` keluar), DigitalTwin tukar Social → Lifestyle.
- **E-37** tiga sistem skoring dengan skala berbeda (100 % · 100 poin · 0–1).
- **E-39** memory: 6 jenis (§17) vs nama scope (§14) — tabel `memories` butuh
  salah satunya.
- **E-40** V0 bertambah jadi **12 fitur**, targetnya tetap 4–6 minggu, dan
  §32 memecahnya jadi **7 sprint** ≈ 4–6 hari per sprint.
- **E-38** `PreparationAgent` di §13 tidak ada di daftar 22 agent.
- **E-41** `Billing` muncul sebagai domain platform tanpa pernah dibahas.

### Langkah berikutnya menurut pemilik

**Engineering Specification v1.0** — schema PostgreSQL lengkap, ERD, event
contract, API endpoint, Agent Registry schema, MCP Tool Registry, permission
schema, prompt architecture, Docker Compose, CI/CD, backlog task V0.
Lihat [`97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md`](97-LANGKAH-BERIKUTNYA-ENGINEERING-SPEC.md).

---

## Sesi 2 — 3 September 2026

**Naskah keempat direkam · nama diputuskan · repo dibuat.**

| Hal | Hasil |
|---|---|
| Nama proyek | ✅ **HumanVerse XOS** diputuskan pemilik (menutup **A-7**) |
| Folder | `E:\xtheoputra\HumanOS AI` → `E:\xtheoputra\HumanVerse XOS` |
| Naskah baru | **Phase 3 — AI-Native Human Ecosystem**, 58 bagian |
| Dokumen ditambah | **28 berkas** (`50`–`77`) |
| Dokumen total | 38 → **67 berkas** di `docs/` (termasuk berkas ini) |
| Berkas kode | tetap **0** (disengaja) |
| Git | diinisialisasi, repo privat dibuat, di-push |

### Yang naskah 4 tutup

- **A-2 (MVP)** → **V0 HumanVerse Foundation**, 10 fitur + 4 agent, 4–6 minggu.
- **A-7 (nama)** → HumanVerse XOS.
- Manifest agent pertama (§11), jalan keluar data (§43), contoh event (§37).
- Beban operasional (B-7) dan biaya inferensi (B-8) diakui & dijadwalkan
  bertahap oleh pemilik sendiri (§38, §48, §49, §51, §58).

### Yang naskah 4 buka

- **A-17** siapa yang mengerjakan V0 dalam 4–6 minggu
- **A-18** Phase 1/2/3 atau V0–V6 sebagai rencana kanonik
- **A-19** empat model angka pengguna yang saling terpisah
- **A-20** Mental Wellness & Lifestyle: dibuang atau ditunda
- **A-21 / A-22** ambang eksperimen · level risiko yang boleh otomatis
- 10 ketidakcocokan baru (**E-24**…**E-33**), termasuk naskah 4 yang
  bertabrakan dengan dirinya sendiri (**E-25**)

### Langkah berikutnya menurut pemilik

**Blueprint Engineering v1.0** — repo final, 100+ modul, seluruh schema, event
schema, API contract, permission model, urutan task untuk AI coding agent.
Lihat [`77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md`](77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md).

---

## Sesi 1 — 3 September 2026

Tiga naskah pemilik (HumanOS · HumanVerse X · Phase 2 Blueprint) direkam
menjadi **39 berkas**, nol baris kode. Disiplin dokumen ditetapkan: berkas
naskah merekam kata pemilik apa adanya, semua keraguan masuk
[`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).
