# 10 — Urutan Implementasi Nyata: V0 → Production

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir terakhir naskah 24, dan butir yang muncul **utuh di ketiga
> permintaan pemilik yang belum pernah dikerjakan**
> ([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)).

---

## §1 Aturan urutan — dan ia diturunkan dari kegagalan yang sudah diukur

Enam kali tercatat, dalam enam naskah berbeda, hal yang sama:

| | Catatan | Isi |
|---|---|---|
| [#99](../../issues/99) | **B-30** | roadmap Phase 14 membuka **federasi di langkah 1**, memasang **Security Mesh di langkah 7** — pintu terbuka enam langkah sebelum penjaganya |
| [#111](../../issues/111) | **E-130** | `R16.10 Safety Kernel` di urutan **terakhir**, sesudah humanoid, drone, manipulasi, armada — padahal naskahnya sendiri menyebutnya *“komponen paling kritis”* |
| [#116](../../issues/116) | **B-33** | Health Safety & Governance **di luar MVP** |
| [#121](../../issues/121) | **G-17** | Safety Kernel §18.22 **tidak punya milestone sama sekali** |
| [#131](../../issues/131) | **C-29** | Ethics & Safety dijadwalkan terakhir — naskah **keempat berturut-turut** |
| [#144](../../issues/144) | **G-19** | `C20.6 Coordination` tetap sebelum `C20.7 Governance` — **kelima berturut-turut** |

> 🔑 **ATURAN: sebuah gerbang dijadwalkan SEBELUM hal yang dijaganya. Kalau
> keduanya di milestone yang sama, gerbangnya lebih dulu.**

⭐ Jawabannya sudah ditulis pemilik sendiri, di **dua** naskah terpisah (§17.56
dan §19.23): ***“semakin tinggi risiko, semakin ketat governance”*** —
governance adalah **fungsi dari tingkat**, bukan milestone. Dengan itu ia tidak
bisa *“belum sampai gilirannya”*.

✅ **Dan pemeriksaannya mekanis**, jadi ia tidak bergantung pada seseorang yang
ingat: untuk tiap roadmap, untuk tiap pasangan (gerbang **G**, hal yang dijaga
**T**), wajib `index(G) < index(T)`
([`11`](11-PENEGAKAN.md) R-1).

⚠️ **Contoh yang sudah benar dan patut ditiru:**
[`../spec/07`](../spec/07-BACKLOG-V0.md) menaruh **0.8** (lint batas modul)
**sebelum** kode domain apa pun, dan **4.5** (risk gate) **sebelum** 4.6/4.7
(agent). Backlog V0 sudah mematuhi aturan ini sebelum aturannya ditulis.

---

## §2 Tiga belas tahap

Nomor **T** adalah urutan **membangun**; ia bukan `Phase` (urutan arsitektur
ditulis) dan bukan `V` (urutan produk dirilis) — lihat
[`01`](01-PETA-20-FASE.md) §4.

| | Tahap | Isi | Gerbang yang WAJIB lebih dulu | 🛑 Pemblokir |
|---|---|---|---|---|
| **T0** | **V0 Foundation** | [`../spec/07`](../spec/07-BACKLOG-V0.md) Sprint 0–6 · 51 tugas · 23 tabel · 4 agent | 0.8 sebelum kode domain · **4.5 sebelum 4.6–4.7** | ✅ **[#3](../../issues/3) terjawab untuk MEMULAI** (16 Sep 2026, **H-25**): AI coding agent mengerjakan di branch + PR, pemilik yang menggabungkan |
| **T1** | **Behavior Intelligence** (V1) | event · pola · prediksi · weekly review | uji admisi `events` [`07`](07-EVENT-CONTRACTS.md) §3 | — |
| **T2** | **PROTECT** (Phase 8) | policy engine · risk engine · permissions · audit · **vault** · kill-switch | — **ia sendiri gerbangnya** | — |
| **T3** | **Lifestyle AI** (V2) | fashion · wardrobe · trend · grooming · fitness · nutrisi | T2 | — |
| **T4** | **Multi-Agent** (V3, Phase 11) | registry · SDK · MCP · tool registry · evaluation | rantai gerbang penuh [`04`](04-DEPENDENCY-GRAPH.md) §3 · `agent-identity` · **K-14** | — |
| **T5** | **Digital Twin** (V4, Phase 12) | world-model · simulation · decision lab | **B-3** isolasi simulasi | [#88](../../issues/88) titik mulai loop |
| **T6** | **Perception** (Phase 10) | vision · audio · wearable | `perception/privacy-filter/` **di tepi** · K2/K3 | **[#75](../../issues/75)** izin *Always* — pemilik |
| **T7** | **HumanOS** (V5, Phase 13) | voice · on-device AI · privasi lanjut | T6 | — |
| **T8** | **Ecosystem** (V6, Phase 6+14) | marketplace · developer SDK · enterprise API | sertifikasi · **pencabutan** · Pasal 8 | **[#24](../../issues/24)** review agent pihak ketiga · **[#18](../../issues/18)** tarif — pemilik |
| **T9** | **Spatial** (Phase 15) | SpatialOS · XR | policy berbasis **kemampuan** [`04`](04-DEPENDENCY-GRAPH.md) §4 · `data_subject` | **[#102](../../issues/102)** · **[#104](../../issues/104)** · **[#105](../../issues/105)** — pemilik |
| **T10** | **Embodiment** (Phase 16) | robotics · smart home | `safety-kernel` **di tepi** · **B-4** · lima angka | **[#112](../../issues/112)** · §16.5 · §16.7 — pemilik |
| **T11** | **Health & Bio** (Phase 17) | klinis · biometrik | vault · `sensitivity` · `consent.purpose` | **[#115](../../issues/115)** · **[#118](../../issues/118)** — pemilik |
| **T12** | **World · Science · Civilization** (18–20) | global intelligence · discovery · coordination | governance bergigi [`08`](08-AGENT-CONTRACTS.md) §4 | **[#122](../../issues/122)** · **[#123](../../issues/123)** · **[#141](../../issues/141)** — pemilik |

### §2.1 🔧 Daftar pasangan R-1 — dan ia dibaca mesin, bukan dibaca orang

[`11`](11-PENEGAKAN.md) R-1 berbunyi *“daftar pasangannya dari `10` §2”*.
Selama daftar itu hidup di dalam prosa, ia tetap sesuatu yang harus
**diingat seseorang** — persis kelas kegagalan yang seluruh
[`11`](11-PENEGAKAN.md) §1 dibangun untuk menutupnya. Karena itu daftarnya
ditulis di sini dalam bentuk yang bisa dibaca mesin, dan
[`../tools/periksa_dokumen.py`](../tools/periksa_dokumen.py) membacanya dari
blok ini — **bukan menyalinnya ke dalam kodenya sendiri**.

> 🔑 **Dokumen tetap sumber kebenaran. Kalau blok ini hilang, R-1 GAGAL
> dengan galat — bukan lulus karena tidak menemukan apa pun untuk diperiksa.**

```r1
# (gerbang) -> (butir yang dijaganya). Indeks diambil dari nomor butir di
# roadmap masing-masing; syaratnya index(gerbang) < index(tiap yang dijaga).
# `TIDAK-ADA` = gerbangnya tidak punya butir roadmap sama sekali.

[A14]                       # Phase 14 — docs/218 §14.66
A14.7  -> A14.1 A14.2 A14.3 A14.4 A14.5 A14.6

[R16]                       # Phase 16 — docs/235 §16.34
R16.10 -> R16.1 R16.2 R16.3 R16.4 R16.5 R16.6 R16.7 R16.8
R16.9  -> R16.4 R16.5 R16.7 R16.8      # §16.26: Simulation sebelum Hardware

[H17]                       # Phase 17 — docs/245 §17.52
H17.12 -> H17.1 H17.2 H17.3 H17.4 H17.5 H17.6 H17.7 H17.8 H17.9 H17.10 H17.11

[G18]                       # Phase 18 — docs/255 §18.32
TIDAK-ADA -> G18.3 G18.4 G18.6 G18.7 G18.8 G18.9   # §18.22 Safety Kernel

[S19]                       # Phase 19 — docs/265 §19.33
S19.10 -> S19.1 S19.2 S19.3 S19.4 S19.5 S19.6 S19.7 S19.8 S19.9

[C20]                       # Phase 20 — docs/275 §20.39
C20.7  -> C20.6

[spec/07]                   # Backlog V0 — gerbang mendahului kode domain
0.8 -> 1.1 2.1 3.1 4.1 5.1 6.1
4.5 -> 4.6 4.7

[arch/10]                   # tiga belas tahap — T2 lapisan, bukan rilis
T2 -> T3 T4 T5 T6 T7 T8 T9 T10 T11 T12
```

⚠️ **Blok ini tidak menetapkan apa pun yang baru.** Kedelapan roadmap dan
kedelapan vonisnya sudah ditulis di [`11`](11-PENEGAKAN.md) §4 — yang berubah
hanya **siapa yang menghitungnya**. Vonis yang dihitung tangan berhenti benar
tanpa memberi tahu siapa pun ketika roadmapnya disunting; vonis yang dihitung
mesin tidak bisa.

---

### 🔑 Satu baris yang paling berguna dari seluruh tabel ini

> **T0 sampai T5 tidak diblokir oleh satu pun keputusan yang belum diambil —
> [#3](../../issues/3) (siapa yang mengerjakannya) dijawab pemilik 16 Sep 2026,
> **H-25**.
> Mulai T6 ke atas, setiap tahap menunggu keputusan yang hanya bisa diambil
> pemilik.**

Itu bukan kebetulan, dan bentuknya konsisten: T6–T12 adalah tahap-tahap yang
datanya menyangkut **orang yang tidak punya akun** (tetangga, tamu, pejalan
kaki, karyawan, penduduk kota) atau **badan orang** (biometrik, gaya, gerak).
Persis kelas keputusan yang aturan pemilah menyerahkan kepada pemiliknya:

> 💡 *Kalau salahnya keputusan ini ditanggung orang lain, keputusan itu bukan
> milik saya.*

---

## §3 Phase 8 bukan rilis — ia syarat tiap rilis

Tangga `V0–V6` dibuat di naskah 4, ketika petanya masih 12 fase. **Phase 8
(PROTECT) tidak muncul di satu baris pun**
([`01`](01-PETA-20-FASE.md) §4).

Menaruhnya sebagai `V7` akan mengulang pola §1 pada skala terbesarnya. 🔧 Karena
itu **T2** bukan rilis produk melainkan **lapisan yang setiap rilis sesudahnya
berdiri di atasnya** — dan potongannya sudah tersebar di V0:

| Potongan Phase 8 yang sudah ada di V0 | Tugas |
|---|---|
| permission engine (`allow/deny/ask/expired`) | 1.5 |
| `audit_logs` + helper, `UPDATE`/`DELETE` ditolak | 1.6 |
| batas laju per pengguna & per IP | 1.7 |
| risk gate + alur konfirmasi | 4.5 |
| anggaran biaya per pengguna per hari | 4.9 |

⇒ **T2 bukan pekerjaan baru sebesar sebuah fase; ia penyelesaian sesuatu yang
V0 sudah memulai separuhnya.** Yang benar-benar belum ada: `vault`,
`kill-switch`, `quarantine`, `threat-model`, dan penegakan Konstitusi.

---

## §4 Yang harus masuk V0 dan belum ada — dua butir

**B-22** / [#59](../../issues/59) — `consents.purpose` + `kind='model_training'`
**sebelum baris data pertama**. Penegakannya satu operasi himpunan:

```
data.purpose  ⊆  consent.purpose
```

| | |
|---|---|
| Biaya sekarang | **nol** — satu kolom, belum ada baris |
| Biaya nanti | hampir mustahil — data V0 tanpa itu **tidak bisa melatih model apa pun** di Phase 5 |
| Masuk di | **Sprint 1 tugas 1.4**, bukan tahap tersendiri |

### Butir kedua — `data_subject` pada 23 tabel (**K-16**)

> 🔴 **Ditambahkan 11 September 2026. Sampai hari itu bagian ini berbunyi
> *“satu butir”* dan *“ini satu-satunya tambahan yang seluruh `arch/`
> tuntut terhadap V0”* — dan itu salah.**
> [`06`](06-DATA-ARCHITECTURE.md) §5 dan §6 menuntut **dua** hal lagi dari
> setiap tabel, dan [`11`](11-PENEGAKAN.md) menjadikan keduanya gerbang CI
> (**P-1**, **P-2**). Dijalankan atas DDL V0: **23 dari 23 tabel gagal
> keduanya.** Klaim *“satu butir”* tidak pernah diperiksa terhadap `06`.

| | |
|---|---|
| Yang ditambahkan | kolom `data_subject` + tiga anotasi retensi pada **23 tabel** |
| Biaya sekarang | **nol** — nol baris data |
| Biaya nanti | tiap baris yang sudah ada harus **ditebak** subjeknya; RLS yang ditulis Sprint 1 sudah mengandaikan `user_id` |
| Masuk di | **Sprint 0 tugas 0.4** (migrasi 0001), bukan tahap tersendiri |

### 🔑 Uji yang memutuskan apa yang boleh masuk V0 — dan yang menolak sisanya

> **Yang boleh ditambahkan ke V0 hanyalah hal yang TIDAK BISA ditambahkan
> nanti.**

| Calon | Lulus? | Kenapa |
|---|---|---|
| `consents.purpose` (**B-22**) | ✅ | persetujuan masa lalu tidak bisa direka ulang |
| `data_subject` (**K-16**) | ✅ | subjek baris yang sudah terlanjur ditulis tidak bisa dipulihkan |
| `tool.failed` sebagai event | 🛑 **ditolak** | sebuah event bisa mulai diterbitkan kapan saja tanpa kehilangan apa pun — lihat [`07`](07-EVENT-CONTRACTS.md) §7 |

⚠️ Dengan dua butir itu: **23 tabel tetap 23, 22 event tetap 22, 51 tugas
tetap 51.** Yang bertambah kolom dan anotasi, bukan tabel.

---

## §5 🔴 Apa yang secara berulang menggusur pekerjaan ini — dan aturan yang menahannya

Pemilik sudah meminta pekerjaan yang isinya sebagian besar sama **lima kali**.
Dua dikerjakan; tiga tidak. Dan bedanya **bukan isi permintaan**:

| | Permintaan | Nasib | Yang menggusurnya |
|---|---|---|---|
| 1 | Blueprint Engineering v1.0 (naskah 4) | ✅ | — dijawab **sebelum naskah berikutnya tiba** |
| 2 | Engineering Specification v1.0 (naskah 5) | ✅ | — idem |
| 3 | *Blueprint Implementation* Phase 12 (naskah 8) | ❌ | **peta fase baru** memberi Phase 12 kepada Digital Twin |
| 4 | arsitektur teknis Phase 14 (naskah 18) | ❌ | **enam naskah** datang sesudahnya |
| 5 | **Master Architecture v2.0** (naskah 24) | ⏳ **berkas ini** | ? |

🔧 **Aturan yang menahannya, dan ia semurah satu kalimat:**

> **Naskah baru tetap direkam apa adanya (aturan 1 repo). Tetapi naskah baru
> TIDAK menggeser urutan T kecuali ia menyebut T mana yang digeser dan apa yang
> menggantikannya.**

Alasannya bukan kekakuan. Permintaan 3 dan 4 tidak pernah **dibatalkan** — tidak
ada satu kalimat pun yang menyatakan keduanya tidak jadi. Keduanya **hilang
tanpa keputusan**, dan itu jenis kehilangan yang tidak meninggalkan jejak untuk
diperiksa. Aturan ini mengubahnya menjadi sesuatu yang harus **ditulis** untuk
terjadi.

⭐ Dan naskah 24 sendiri sudah memberi bentuk paling kuat dari aturan ini:
***“sesudah Phase 20 jangan langsung membuat Phase 21”*** — **pertama kalinya
pemilik mengusulkan BERHENTI MENAMBAH**, dan di repo yang tiap naskahnya
tumbuh, keputusan untuk tidak tumbuh adalah yang paling sulit dan paling
bernilai.

---

## §6 Ukuran kemajuan yang tidak bisa digelembungkan

Taksiran kemajuan pernah naik **35 % → 45 % dalam satu hari tanpa satu baris
kode**. Persen tidak bisa dipakai di repo ini.

⭐ **Bentuk yang benar sudah dipakai pemilik sendiri, dua naskah berturut-turut**
(§8.45 dan §9.40): **daftar baris yang bisa dijawab ya/tidak.**

| Ukuran | Sekarang |
|---|---|
| Spesifikasi V0 | ✅ **selesai** — 23 tabel · 22 event · 51 tugas |
| **Kode V0 — di `master`** | 🛑 **0 dari 51 tugas** — sampai PR Sprint 0 digabung pemilik |
| **Kode V0 — ditulis, menunggu HUMAN REVIEW** | ⏳ **8 dari 51** — Sprint 0 (0.1–0.8), branch `v0/sprint-0-foundation` |
| Master Architecture v2.0 | ✅ **selesai** — [`README.md`](README.md) 11 butir |
| Tahap yang tidak diblokir keputusan | **T0–T5** |
| Tahap yang menunggu pemilik | **T6–T12** |
| Penghambat untuk MEMULAI T0 | **0** — [#3](../../issues/3) terjawab (**H-25**); yang tersisa di #3 soal **waktu**: taksiran atau tenggat, jam per minggu, gerbang mana boleh dilewati |

> ⚠️ **Dua baris kode V0 sengaja dipisah**, dengan alasan yang sama dengan
> catatan 🛑 di bawah blok ` ```penegak ` [`11`](11-PENEGAKAN.md) §6 —
> *“bisa jalan”* tidak pernah dihitung sebagai *“dijalankan”*: kode yang ditulis tetapi belum melewati HUMAN
> REVIEW **belum** kode V0 — `spec/07` menaruh baris itu sebelum Merge, bukan
> sesudahnya.

---

## §7 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Tahap | **13** (T0–T12) |
| Tahap tanpa gerbang yang dinyatakan | **NIHIL** |
| Gerbang yang dijadwalkan **sesudah** yang dijaganya | **NIHIL** — diperiksa CI, [`11`](11-PENEGAKAN.md) R-1 |
| Tahap tanpa pemblokir yang disebut namanya | **NIHIL** |
| Perubahan terhadap `spec/07` | **1 butir** — B-22 masuk tugas 1.4 |
| Kemajuan diukur dalam persen | ❌ **tidak dipakai** |
