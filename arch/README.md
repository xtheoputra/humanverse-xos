# HumanVerse Master Architecture v2.0

> ⚠️ **Berkas di folder ini BUKAN kata pemilik.** Ini hasil kerja engineering
> yang diturunkan dari **24 naskah** di [`../docs/`](../docs/00-DAFTAR-ISI.md)
> dan dari **delapan sensus** yang mengukurnya. Berkas naskah tetap murni;
> setiap hal yang **saya putuskan sendiri** ditandai **🔧 usulan** — pemilik
> boleh membatalkannya, dan tiap butir menyebutkan cara membalikkannya.

Menjawab permintaan penutup naskah 24
([`../docs/275`](../docs/275-ROADMAP-ARSITEKTUR-FINAL-PETA-20-FASE-DAN-MASTER-ARCHITECTURE.md)
L166) dan [#139](../../issues/139):

> *“Setelah Phase 20 kita **tidak langsung membuat Phase 21**. Langkah
> profesional berikutnya adalah membuat **HumanVerse Master Architecture
> v2.0**: menyatukan Phase 1–20, menghapus overlap antar-modul, menentukan
> bounded context final, dependency graph, technology stack final, monorepo
> final, deployment topology, data architecture, event contracts, agent
> contracts, dan urutan implementasi nyata dari V0 → production.”*

---

## Sebelas butir yang diminta, dan di mana masing-masing dijawab

| Butir pemilik | Berkas | Yang berubah dari “kalimat” menjadi “daftar” |
|---|---|---|
| menyatukan Phase 1–20 | [`01`](01-PETA-20-FASE.md) | 20 baris, satu nama + satu kata kerja masing-masing; **satu celah jujur** (Phase 1) |
| bounded context final | [`02`](02-BOUNDED-CONTEXT.md) | **17 konteks**, tiap konteks memiliki kosakatanya sendiri |
| menghapus overlap antar-modul · monorepo final | [`03`](03-MONOREPO-FINAL.md) | **54 nama** ≥3 pohon divonis satu per satu: naik · tinggal · ganti nama |
| dependency graph | [`04`](04-DEPENDENCY-GRAPH.md) | arah panah antar-konteks + **enam batas keras** yang bisa dijalankan CI |
| technology stack final | [`05`](05-TECHNOLOGY-STACK.md) | pilihan per **pola akses**, bukan per fase; yang belum bisa dipilih diberi **pemicunya** |
| data architecture | [`06`](06-DATA-ARCHITECTURE.md) | **247 nama tabel** → 4 kelas penyimpanan; **19 definisi ganda** diselesaikan |
| event contracts | [`07`](07-EVENT-CONTRACTS.md) | satu amplop; **domain = konteks**; aturan apa yang **bukan** event |
| agent contracts | [`08`](08-AGENT-CONTRACTS.md) | **59 nama** diuji K-5 → agent atau service; Konstitusi §20.16 diberi penegak |
| deployment topology | [`09`](09-DEPLOYMENT-TOPOLOGY.md) | V0 → produksi, dan **aturan tepi**: apa yang tak boleh meninggalkan perangkat |
| urutan implementasi V0 → production | [`10`](10-URUTAN-IMPLEMENTASI.md) | dua rencana didamaikan; **gerbang mendahului yang dijaganya** |
| — (pelajaran repo ini sendiri) | [`11`](11-PENEGAKAN.md) | **25 pemeriksaan CI**; aturan tanpa penegak tidak dihitung selesai |

⚠️ Butir **kontrak API** tidak disebut naskah 24 — celah itu sudah dicatat di
[`../docs/PETA-FASE.md`](../docs/PETA-FASE.md) dan diisi dari tempat lain:
[`../spec/04`](../spec/04-API-CONTRACTS.md) untuk V0, dan
[`04`](04-DEPENDENCY-GRAPH.md) §5 untuk aturan rutenya di luar V0.

---

## Aturan pengutamaan — tiga lapis dokumen, dan mana yang menang

Repo ini kini punya tiga lapis, dan tanpa aturan ini ketiganya akan
dibaca sebagai tiga jawaban untuk satu pertanyaan.

| Lapis | Isi | Mengikat |
|---|---|---|
| [`../docs/`](../docs/00-DAFTAR-ISI.md) | 24 naskah pemilik + audit + sensus | **tidak mengikat kode** — ia **bukti**, bukan kontrak |
| [`../spec/`](../spec/README.md) | Engineering Spec v1.0, **cakupan V0** | **bentuk**: kolom, tipe, payload, endpoint |
| `arch/` (berkas ini) | Master Architecture v2.0, **cakupan Phase 1–20** | **nama & batas**: modul mana, konteks mana, boleh mengimpor apa |

**🔧 Aturan:**

1. **`arch/` mengikat NAMA dan BATAS. `spec/` mengikat BENTUK.**
   `arch/` menyatakan bahwa `habits` milik konteks `human-core`; `spec/01`
   menyatakan kolom tabel `habits`. Keduanya tidak pernah menjawab pertanyaan
   yang sama.
2. **Untuk V0, `spec/` menang.** Kalau `arch/` bertentangan dengan `spec/`
   tentang V0, **`arch/` yang salah** dan diperbaiki — `spec/` sudah diperiksa
   terhadap DDL, `arch/` belum.
3. **Naskah tidak pernah menang atas keduanya, dan tidak pernah diubah.**
   Naskah merekam kata pemilik apa adanya (aturan 1 repo ini). Kalau naskah dan
   `arch/` berbeda, yang ditulis adalah **tabel padanan**, bukan suntingan —
   persis cara [K-3](../docs/KEPUTUSAN-DIDELEGASIKAN.md) menangani 127 nama
   event.

> 🛑 **Aturan 3 punya biaya yang harus disebut:** pembaca yang membuka naskah
> Phase 16 akan menemukan `robotics/planning/`, sementara `arch/03` menamainya
> `robotics/motion-planning/`. Itu **disengaja**. Menyunting naskah akan
> menghapus bukti bahwa tabrakannya pernah ada — dan bukti itu satu-satunya
> alasan tabrakannya bisa ditemukan.

---

## Apa yang v2.0 gantikan

| Digantikan | Oleh | Alasan |
|---|---|---|
| peta fase **v1** — §10.41, 15 fase | [`01`](01-PETA-20-FASE.md) | Phase 15 ternyata SpatialOS, bukan Global Intelligence ([#101](../../issues/101)) |
| peta fase **v2** — terbuka-ujung | [`01`](01-PETA-20-FASE.md) | naskah 23 menyatakan Phase 20 terakhir; peta tanpa ujung melahirkan rujukan ke rencana yang tak bisa dibuka ([#132](../../issues/132)) |
| “monorepo final” (H-10) sebagai **klaim** | [`03`](03-MONOREPO-FINAL.md) | ia tergerus **sepuluh kali**; yang kurang bukan keputusan, melainkan **aturan komposisi** |
| hitungan tabel **99** | [`06`](06-DATA-ARCHITECTURE.md) | himpunannya **247**; hitungannya berhenti dipelihara di Phase 12 |
| daftar agent **“> 40”** | [`08`](08-AGENT-CONTRACTS.md) | himpunannya **59**, dan 44 di antaranya hanya pernah disebut sekali |

⚠️ **Yang TIDAK digantikan:** [`../spec/`](../spec/README.md) seluruhnya.

### Apa yang berubah di V0 — tiga hal, dan ketiganya bukan keputusan baru

Angka-angkanya tidak bergeser: **23 tabel tetap 23 · 22 event tetap 22 · 51
tugas tetap 51 · 12 modul tetap 12 · 4 agent tetap 4.** Yang berubah adalah tiga
**penerapan keputusan yang sudah diambil dan tidak pernah sampai ke `spec/`**:

| | Perubahan | Menerapkan keputusan |
|---|---|---|
| 1 | [`../spec/01`](../spec/01-DATABASE-SCHEMA.md): `agents.risk_level` → **`max_risk`**, `requires_confirmation` **dihapus** | [#52](../../issues/52) (`requires_confirmation` pindah ke Policy Engine) + **H-21**/[#67](../../issues/67) + **E-119**/[#97](../../issues/97) |
| 2 | [`../spec/07`](../spec/07-BACKLOG-V0.md) 1.4: `consents.purpose` + `kind='model_training'` | **B-22**/[#59](../../issues/59) — *sebelum baris data pertama* |
| 3 | `spec/07` 4.3: tiga entri tool `kind: agent` | **K-14** ([`08`](08-AGENT-CONTRACTS.md) §2) |

➕ Dan satu perubahan **bentuk**, bukan isi: bahasa backend dinyatakan
(**K-13**, [`05`](05-TECHNOLOGY-STACK.md) §2) ⇒ `spec/06` dan `spec/07` memakai
`.py`/`pytest`/`import-linter`. Nol tabel, nol event, nol tugas berubah
karenanya.

> 🔑 **Ketiganya punya bentuk yang sama, dan itu temuan tersendiri:** sebuah
> keputusan diambil, ditutup sebagai issue, lalu **tidak pernah diterapkan pada
> berkas yang paling berkepentingan** — persis pelajaran [#38](../../issues/38)
> (*janji di issue tertutup tidak punya penjaga*). Ketiganya ditemukan bukan
> dengan membaca issue, melainkan dengan **membandingkan `spec/` dengan
> keputusan yang mengaku sudah berlaku atasnya**.

---

## Yang v2.0 **tidak** putuskan

Batas yang sama dengan
[`../docs/KEPUTUSAN-DIDELEGASIKAN.md`](../docs/KEPUTUSAN-DIDELEGASIKAN.md), dan
alasannya satu kalimat:

> 💡 **Kalau SALAHNYA keputusan ini ditanggung ORANG LAIN — pengguna, penerima
> pesan, atau pemilik uangnya — keputusan itu bukan milik saya.**

| Tetap milik pemilik | Yang v2.0 lakukan sebagai gantinya |
|---|---|
| [#3](../../issues/3) siapa mengerjakan V0 | [`10`](10-URUTAN-IMPLEMENTASI.md) memberi urutannya, bukan orangnya |
| [#20](../../issues/20) merek & domain | — |
| [#34](../../issues/34) ambang confidence | [`06`](06-DATA-ARCHITECTURE.md) menyediakan **tempatnya** (`model_version`, `evidence_count`) supaya angkanya bisa diganti tanpa migrasi |
| **seluruh butir C** (hukum & privasi) | v2.0 menyediakan **mekanisme yang menegakkan apa pun yang pemilik putuskan** — mis. policy ruangan berbasis **kemampuan** ([`04`](04-DEPENDENCY-GRAPH.md) §4), bukan memutuskan apakah sensor tembus dinding boleh dibangun |
| §16.5 · §16.7 rantai humanoid | [`08`](08-AGENT-CONTRACTS.md) menandainya sebagai **satu-satunya dua rantai yang tersisa tanpa gerbang**, tanpa memilih gerbangnya |
| [#4](../../issues/4) Mental Wellness | cakupan produk |

**Nol butir C diputuskan di seluruh `arch/`.**

---

## Cara membaca berkas ini kalau waktunya sedikit

| Kalau Anda ingin… | Buka |
|---|---|
| tahu apa yang dikerjakan berikutnya | [`10`](10-URUTAN-IMPLEMENTASI.md) |
| menulis baris kode pertama | [`../spec/07`](../spec/07-BACKLOG-V0.md) Sprint 0, lalu [`11`](11-PENEGAKAN.md) |
| menambah modul baru | [`03`](03-MONOREPO-FINAL.md) §2 (uji naik-turun) |
| menambah tabel baru | [`06`](06-DATA-ARCHITECTURE.md) §2 (empat kelas penyimpanan) |
| menambah event baru | [`07`](07-EVENT-CONTRACTS.md) §3 (uji admisi) |
| menambah agent baru | [`08`](08-AGENT-CONTRACTS.md) §2 (tiga uji K-5) |
| tahu kenapa sesuatu diputuskan begitu | tiap berkas punya bagian **BACAAN YANG DITOLAK** |
