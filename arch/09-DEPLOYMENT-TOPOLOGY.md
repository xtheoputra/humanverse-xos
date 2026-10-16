# 09 — Deployment Topology

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“deployment topology”* naskah 24 — butir yang muncul **utuh di
> ketiga permintaan** pemilik yang belum pernah dikerjakan
> ([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)).

---

## §1 V0 — satu proses, dan itu keputusan yang sudah diambil

```
docker compose
├── api          FastAPI, satu proses, 12 modul          ← spec/06
├── postgres     PostgreSQL 16
└── redis        Redis 7 — sesi, cache, Streams
```

**V0 punya satu pengguna nyata: pemiliknya.** Memecahnya jadi service berarti
membayar biaya jaringan, deploy, dan penelusuran sebelum ada yang memakainya
([`../spec/06`](../spec/06-MODULE-BOUNDARIES.md)). Yang dijaga sejak awal bukan
proses terpisah, melainkan **batas yang tidak boleh dilanggar**.

⚠️ Qdrant masuk di **Sprint 3** (tugas 3.5), sebagai kontainer keempat.

---

## §2 Jalur tumbuh — dipicu UKURAN, bukan tanggal

> 🔑 **Setiap langkah punya pemicu yang bisa diukur.** Jadwal yang ditulis dalam
> minggu akan meleset; pemicu yang ditulis dalam angka tidak bisa meleset — ia
> hanya belum tercapai.

| Tahap | Bentuk | **Pemicu pindah ke tahap berikutnya** |
|---|---|---|
| **D0** | `docker compose` di satu mesin | — |
| **D1** | satu Cloud VM, compose yang sama | ada pengguna **selain pemiliknya** |
| **D2** | VM + **PostgreSQL terkelola** (backup, PITR) | data yang **hilangnya tidak bisa dibuat ulang** sudah ada, yaitu sejak `journal_entries` baris pertama |
| **D3** | api dipisah dari worker (proses berbeda, kode sama) | pekerjaan latar mulai **menunda respons HTTP** — p95 naik saat batch jalan |
| **D4** | Kubernetes | ≥ **3** komponen dengan **profil skala berbeda** ⁽¹⁾ |
| **D5** | tepi + cloud | fase pertama yang menyentuh dunia fisik — **Phase 15** |

⁽¹⁾ bukan *“banyak pengguna”*. Yang membuat Kubernetes berguna adalah komponen
yang perlu **diskalakan berbeda satu sama lain**; sampai itu terjadi ia hanya
menambah lapisan.

🛑 **Yang TIDAK dipakai sampai pemicunya terpenuhi:** Kafka (pemicu di
[`05`](05-TECHNOLOGY-STACK.md) §6) · Neo4j (V2) · service mesh · multi-region.
Menambahkannya lebih awal adalah cara paling cepat membuat 4–6 minggu menjadi
4–6 bulan.

### §2.1 🔒 Web, dan gratis — kata pemilik **H-29** (8 Okt 2026)

> *“kedepannya, aplikasi ini dapat dijalankan juga di web gratis ya, vercel
> atau apapun itu”* — pemilik, 8 Okt 2026 ([`../docs/99`](../docs/99-CATATAN-AUDIT.md) **H-29**).

**Yang mengikat, tiga baris:**

| | Arti | Akibat |
|---|---|---|
| **web** | aplikasi web = **target `web` proyek Flutter yang sama** ([`03`](03-MONOREPO-FINAL.md) E-176, [`05`](05-TECHNOLOGY-STACK.md) §4) | tidak ada basis kode web kedua |
| **gratis** | penerapan web **tanpa tagihan** — sejalan **H-26** (*“jangan ada tagihan”*); penyedia **tidak** dipatok (*“vercel atau apapun itu”*) | jalur berbayar tidak dipilih agent; jalur yang **meminta kartu** walau gratis = keputusan pemilik (risiko tagihan) |
| **kedepannya** | **bukan** tugas V0 — 51 tugas [`../spec/07`](../spec/07-BACKLOG-V0.md) tidak bertambah | jatuh di **D1** (pengguna selain pemiliknya); D1–D2 di tabel atas kini wajib punya **jalur gratis** |

**Diukur hari ini** (`v0/sprint-6-product` 17d0959): `flutter build web --release`
**berhasil** — 45 dtk, `build/web` 41 MB berkas statis. Alamat api lewat
`--dart-define=HVX_API=…`; api sudah menerima asal lain lewat `HVX_CORS_ORIGINS`
(asal persis, tanpa `*`); ekspor 6.4 sudah punya jalur unduh peramban
(`simpan_berkas_web.dart`). **Aplikasinya siap web; yang belum siap adalah
tempat menjalankan api-nya secara gratis.**

| Komponen | Yang ia butuhkan | Hosting statis / fungsi serverless gratis |
|---|---|---|
| aplikasi Flutter web | berkas statis | ✅ penyedia mana pun (Vercel · Cloudflare Pages · Netlify · …) |
| api (FastAPI) | HTTP; SSE percakapan selama satu giliran (4.8); cek peran saat mulai (B-40) | ⚠️ bisa sebagai fungsi, tetapi batas durasi memotong SSE panjang, dan tiap instans membuka koneksi PostgreSQL sendiri → butuh *pooler* |
| **pekerja** (`hvx.pekerja`) | proses **hidup terus**: relay tiap 1 dtk, `XREADGROUP BLOCK`, penyelaras 2 dtk, sapuan hapus akun tiap 5 mnt | ❌ **tidak bisa di fungsi serverless** — tanpa pekerja, event tak sampai ke konsumen (memori, proyektor, rekomendasi) dan akun yang minta dihapus **tidak pernah terhapus** (6.5 — janji kepada pengguna) |
| PostgreSQL 16 | RLS · peran `hvx_app`/`hvx_pekerja` · fungsi `SECURITY DEFINER` · login migrasi terpisah | ⚠️ layanan terkelola gratis harus mengizinkan **membuat peran dan fungsi**; api **menolak mulai** sebagai superuser/`BYPASSRLS` — syarat yang dicek per penyedia, bukan dilonggarkan |
| Redis 7 | skrip Lua (sesi · batas laju · ekspor sekali pakai) · Streams + grup konsumen | ⚠️ cek `EVAL` + `XREADGROUP`; kuota perintah paket gratis lawan pekerja yang berputar tiap detik |
| Qdrant | pencarian memori semantik | opsional — tanpa `HVX_QDRANT_URL` memori tetap di PostgreSQL |

🔴 **Yang bertabrakan — ditulis sekarang supaya tidak ditemukan sesudah ada data:**

1. Paket gratis yang **menidurkan atau menghapus basis data menganggur**
   bertabrakan dengan pemicu **D2** (jurnal = data yang hilangnya tak bisa dibuat
   ulang) dan **H-27**. Cadangan yang **dipulihkan sungguhan** (§5 aturan 5)
   adalah syarat sebelum pengguna kedua, bukan sesudahnya.
2. Jurnal (Level 3) dan mood (data kesehatan jiwa, **K-46**) di penyedia pihak
   ketiga, kemungkinan di luar Indonesia — **C-36**, milik pemilik.
3. Syarat paket gratis berubah lebih cepat daripada dokumen ini — mis. paket
   Hobby Vercel hanya untuk penggunaan **pribadi non-komersial** (sejauh yang
   diketahui Juni 2026). Produk yang dijual mengubah syaratnya → **#18** (tarif).
   **Cek ulang syarat tiap penyedia saat D1 dipicu.**

**Dua bentuk — tidak dipilih sekarang, dipilih saat D1 dipicu:**

| | Bentuk | Untung | Harga |
|---|---|---|---|
| **W-a** | aplikasi web di hosting statis gratis **+ satu mesin gratis** menjalankan `docker compose` yang **sama** | §5 aturan 1 utuh (satu artefak); kode tidak berubah | mesin gratis yang tahan lama jarang ada, dan yang ada sering meminta kartu |
| **W-b** | aplikasi web + api di fungsi serverless gratis + PostgreSQL/Redis/Qdrant terkelola gratis | tiap bagian dikelola penyedianya | **pekerja tetap butuh proses hidup terus** di tempat lain; lima penyedia, lima syarat, lima cara mati |

---

## §3 `deploy` — atribut, bukan folder

[`03`](03-MONOREPO-FINAL.md) §5 membuang empat folder `edge/` dan
menggantinya dengan satu runtime + satu atribut per modul:

```yaml
deploy: edge | cloud | both
```

> 🔑 **Aturan penempatan, satu kalimat:**
> **Apa pun yang harus tetap bekerja ketika segalanya gagal, berjalan paling
> dekat dengan dunia.**

Ia bukan preferensi; ia turunan dari pemicunya sendiri:

🛑 **§16.20 mendaftarkan `communication loss` sebagai salah satu pemicu
darurat.** Pengaman darurat yang hidup di cloud akan **mati justru pada
pemicunya**. Sebuah pengaman yang tidak hadir pada salah satu pemicunya sendiri
bukan pengaman.

| Modul | `deploy` | Kenapa |
|---|---|---|
| `embodiment/safety-kernel/` | **edge** | milidetik, dan **wajib** hidup saat jaringan putus |
| `embodiment/drivers/` · `locomotion/` · `manipulation/` | **edge** | mereka **adalah** perangkat kerasnya |
| `perception/capture/` · `privacy-filter/` · `summarizer/` | **edge** | §15.29 — lihat §4 |
| `spatial/slam/` · `localization/` | **edge** | kandungan waktu-nyata; petanya boleh disinkron |
| `security/policy-engine/` | **both** | salinan tepi memakai policy terakhir yang tersinkron, dan **default deny** kalau basi |
| `agents/*` · `intelligence/*` · `simulation/*` | **cloud** | tidak ada yang menjadi berbahaya kalau ia berhenti |
| `governance/*` | **cloud** | keputusan, bukan refleks |

⚠️ **Baris `security/policy-engine/` adalah yang paling mudah salah.** Salinan
tepi yang gagal terbuka (*fail-open*) akan menjadi jalan pintas terhadap seluruh
[`04`](04-DEPENDENCY-GRAPH.md) §3. Karena itu: policy tepi punya **umur**, dan
policy yang lewat umurnya berarti **tolak**, bukan **izinkan**.

---

## §4 Yang tidak pernah meninggalkan perangkat

§15.29 menyatakan *“Edge melakukan processing sensitif”* — **privasi oleh
ARSITEKTUR pertama di repo ini**. Semua perlindungan sebelumnya berupa
**aturan**, dan aturan menjaga data yang **sudah dikirim**.

⚠️ Kata *“sensitif”* tidak bisa ditegakkan. 🔧 Ia diganti daftar:

| Tidak pernah keluar sebagai mentah | Yang keluar sebagai gantinya |
|---|---|
| `wifi_csi` | `presence.count`, dan hanya kalau policy ruangan mengizinkan |
| point cloud | scene graph teranonimkan |
| bingkai kamera | kejadian yang lulus uji admisi [`07`](07-EVENT-CONTRACTS.md) §3 |
| audio mentah | transkrip **atau** tidak sama sekali |
| `eye_focus` | agregat, tidak per-objek |
| `people_tracks` | `presence.count` |

⭐ Dan ini sekaligus **separuh jawaban** untuk [#102](../../issues/102) dan
[#104](../../issues/104): apa yang tidak pernah dikirim tidak bisa bocor,
tidak bisa disubpoena, dan tidak bisa dipakai ulang untuk tujuan lain.
🛑 Separuh yang lain — **apakah sensor itu dibangun sama sekali** — tetap milik
pemilik.

---

## §5 Aturan yang berlaku di semua tahap

| # | Aturan | Kenapa |
|---|---|---|
| 1 | **satu artefak, banyak konfigurasi** | citra yang berbeda per lingkungan berarti yang diuji bukan yang dijalankan |
| 2 | **migrasi naik DAN turun** diuji di CI | [`../spec/07`](../spec/07-BACKLOG-V0.md) 0.4 sudah menuntutnya; itu juga [K-9](../docs/KEPUTUSAN-DIDELEGASIKAN.md) |
| 3 | **rahasia tidak pernah di repo** | — |
| 4 | **`/health` menyebut ketergantungannya** (`db`, `redis`, `qdrant`) | `spec/07` 0.3 |
| 5 | **rollback adalah jalur yang diuji**, bukan yang diharapkan | Pasal 5 Konstitusi berlaku bagi sistemnya sendiri, bukan hanya bagi agent |

> 🔑 **Aturan 5 layak dieja.** Repo ini sudah mencatat `Rollback` **hilang** dari
> Safety Kernel satu naskah sesudah ia diberikan ([#91](../../issues/91)).
> Kalau *Reversibility* adalah pasal konstitusi bagi agent, ia tidak bisa
> menjadi hal yang belum pernah dicoba bagi deploy-nya.

---

## §6 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Tahap deployment | **6** (D0–D5), tiap tahap punya **pemicu terukur** |
| Tahap tanpa pemicu | **NIHIL** |
| Aplikasi bisa dibangun untuk web (**H-29**) | ✅ diukur 8 Okt 2026 (`flutter build web`) — ⚠️ **belum dijaga gerbang**: impor yang hanya ada di perangkat (`dart:io`) bisa mematahkannya tanpa ada yang merah |
| Jalur **gratis** untuk D1–D2 (**H-29** · **H-26**) | ⏳ W-a / W-b dipilih saat D1 dipicu; pekerja wajib punya proses hidup terus di keduanya |
| Folder `edge/` di pohon | **1** (`platform/edge/`) — turun dari 4 |
| Modul tanpa `deploy` | ditolak CI — [`11`](11-PENEGAKAN.md) P-5 |
| Pengaman ber-`deploy: cloud` yang pemicunya `communication loss` | **NIHIL** |
| Policy tepi yang gagal-terbuka | **NIHIL** — basi berarti tolak |
| Data K3 yang meninggalkan perangkat sebagai mentah | ditolak CI — P-6 |
