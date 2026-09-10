# 08 — Agent Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“agent contracts”* naskah 24. Melanjutkan
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) dan
> [K-5](../docs/KEPUTUSAN-DIDELEGASIKAN.md); menutup
> [#97](../../issues/97) (**E-119**) dan bagian **G-14** dari
> [#98](../../issues/98); memberi penegak bagi sepuluh pasal §20.16.

---

## §1 Lima puluh sembilan nama, dan yang mana benar-benar agent

Daftar agent ditulis **lima kali**; jumlahnya ditaksir dengan **penjumlahan**
(*“> 40”*). Himpunannya **59**, dan angkanya yang menentukan:

| | |
|---|---|
| nama unik | **59** |
| muncul di **semua** daftar | **NIHIL** |
| muncul di ketiga registry umum (L1·L2·L3) | **6** — `Career` · `Fashion` · `Habit` · `Learning` · `Social` · `Travel` |
| muncul di **satu** daftar saja | **44 — 75 %** |

🔧 **Aturan bawaan, dan alasannya sama dengan
[K-12](../docs/KEPUTUSAN-DIDELEGASIKAN.md):**

> **Sebuah nama BUKAN agent sampai ada manifest yang lulus ketiga uji K-5.
> Bawaannya `service`, bukan `agent`.**

| Bacaan yang DITOLAK | *“59 nama itu daftar agent; tinggal dibuatkan manifestnya.”* |
|---|---|
| **Kenapa ditolak** | §12.29 — satu-satunya peringatan semacam itu dalam 24 naskah — berbunyi *“jangan membuat semuanya sebagai autonomous agent; sebagian lebih baik sebagai deterministic/model services”*. Sebuah nama yang muncul **sekali** dan tidak pernah dijelaskan lagi tidak bisa diuji, dan yang tidak bisa diuji tidak boleh masuk registry: `risk_level` per-agent kehilangan arti kalau peringkas teks dan pengirim pesan duduk di daftar yang sama |
| **Ke sisi mana kelalaian jatuh** | ke `service` — yang **tidak** punya kewenangan memilih tool, jadi tidak butuh gerbang dan tidak bisa menyalahgunakannya |

⇒ **6 agent yang stabil, 53 kandidat yang harus membuktikan diri.**

---

## §2 🔴 Menguji K-5 pada empat agent V0 — dan menemukan satu lubang

[`../spec/05`](../spec/05-AGENT-CONTRACTS.md) menutup bagiannya dengan
*“Keempat agent V0 lulus ketiga uji.”* Kalimat itu **dinyatakan, tidak
diperiksa**. Memeriksanya murah, dan hasilnya mengubah salah satu aturannya.

| Agent V0 | (a) >1 langkah | (b) memilih tool saat jalan | (c) bisa dihentikan, jejak lanjutable | Vonis |
|---|---|---|---|---|
| `coach-agent` | ✅ | ✅ 7 tool | ✅ `agent_runs` | **agent** |
| `habit-agent` | ✅ | ✅ 3 tool | ✅ | **agent** |
| `memory-agent` | ✅ | ⚠️ 2 tool, dan pemakaiannya **hampir selalu tetap** | ✅ | ⚠️ **perbatasan** — §2.2 |
| **`orchestrator-agent`** | ✅ | 🛑 **`tools: —`** (nol tool) | ✅ `parent_run_id` | 🛑 **GAGAL uji (b)** |

### 2.1 🛑 Lubangnya bukan di orchestrator — melainkan di kata *“tool”*

`orchestrator-agent` **memilih**; yang dipilihnya **agent lain**, bukan tool.
Uji (b) berbunyi *“memilih di antara beberapa **tool***”. Dibaca apa adanya,
komponen paling berkuasa di V0 **tidak lulus** menjadi agent.

Dan akibatnya lebih berat daripada perkara istilah:

> 🛑 **Kalau memanggil agent lain BUKAN pemanggilan tool, maka sisi-sisi pohon
> eksekusi (`parent_run_id`) tidak pernah melewati risk gate.** Gerbang memeriksa
> tool; orchestrator tidak memanggil tool; maka **tepat di puncak pohon** ada
> simpul yang mendistribusikan pekerjaan tanpa satu gerbang pun melihat ke mana
> ia mendistribusikannya. Itu **B-2** ([`04`](04-DEPENDENCY-GRAPH.md)) yang
> bocor di satu-satunya tempat yang melihat seluruh pohon.

🔧 **K-14 · Memanggil agent lain ADALAH pemanggilan tool.**

| | |
|---|---|
| **Keputusan** | Setiap agent yang bisa dipanggil agent lain **wajib terdaftar di tool registry** dengan `kind: agent`. `risk_level` entri itu = **`max_risk` agent yang dipanggil**. Pemanggilannya melewati rantai gerbang [`04`](04-DEPENDENCY-GRAPH.md) §3 seperti tool lain. |
| **Bukti** | `orchestrator-agent` punya `tools: —` di [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) dan `parent_run_id` di [`../spec/07`](../spec/07-BACKLOG-V0.md) 4.6 ⇒ ia memanggil sesuatu yang tidak tercatat sebagai apa pun yang bisa digerbang. |
| **Bacaan yang DITOLAK** | *“Longgarkan uji (b) menjadi ‘memilih di antara beberapa tool **atau agent**’.”* **Ditolak** — itu memperbaiki definisinya tetapi **membiarkan lubang gerbangnya**. Orchestrator akan lulus sebagai agent dan tetap memanggil tanpa gerbang. |
| **Akibat untuk V0** | `orchestrator-agent` mendapat `tools: [agent.coach, agent.habit, agent.memory]`, ketiganya `kind: agent`. **Nol tabel baru, nol event baru.** |
| **Cara membalikkan** | Longgarkan uji (b) dan terima bahwa sisi pohon eksekusi tidak digerbang. |

> 💡 **Ini kasus ketiga yang terasa sepele — dan justru itu yang menguji
> aturannya.** Dua agent pertama lulus dengan mudah, dan kalau pemeriksaannya
> berhenti di sana, K-5 akan tampak selesai.

### 2.2 `memory-agent` — perbatasan, dan pertanyaan yang memutuskannya

Ia punya dua tool (`memory.search`, `memory.write`) dan pemakaiannya mengikuti
jalur tetap: ekstraksi → tulis; permintaan → cari. Itu **pipeline**, bukan
pilihan.

🔧 **Pertanyaan yang memutuskan, dijawab saat Sprint 3–4 ditulis:**
*apakah ia memutuskan **apakah** sebuah memori layak ditulis, atau selalu
menulis apa pun yang dihasilkan ekstraktor?*

| Jawaban | Vonis |
|---|---|
| ia memutuskan (menilai kelayakan, bisa memilih tidak menulis) | **agent** |
| ia selalu menulis keluaran ekstraktor | **service** — dan ekstraksinya tetap jalan, hanya tanpa manifest agent |

⚠️ Yang **tidak** berubah dalam kedua kasus: larangan membaca `journal_raw`.
Itu aturan scope, bukan aturan agent.

---

## §3 Manifest v2 — empat medan yang belum ada, dan kenapa masing-masing perlu

[`../spec/05`](../spec/05-AGENT-CONTRACTS.md) tetap berlaku. Yang ditambahkan
di sini hanya berlaku **di luar V0**, kecuali disebutkan lain.

```yaml
max_risk:  R2               # 🔧 pengganti `risk_level` sebagai properti AGENT
autonomy:
  max_level: L2             # tangga otonomi, TERPISAH dari R
  kill_condition:           # 🔧 dari 11 unsur Autonomy Contract §14.62
    - budget_exceeded
    - confidence < 0.6 for 3 consecutive runs
deploy:    cloud            # 🔧 edge | cloud | both
```

| Medan | Menggantikan / menambah | Kenapa |
|---|---|---|
| **`max_risk`** | `risk_level` pada **agent** | **E-119** ([#97](../../issues/97)): `R` adalah risiko **AKSI**, `L` otonomi **AGENT**. Travel Planner membaca kalender (R0–R1) dan memesan hotel dengan uang (R3) — **satu angka tidak bisa menjadi keduanya**. `max_risk` adalah **pagu**, dan pagu bisa benar untuk agent yang aksinya beragam |
| **`autonomy.max_level`** | — | **H-21** ([#67](../../issues/67)): dua tangga hidup berdampingan di satu manifest |
| **`kill_condition`** | — | **G-14**: 11 unsur kontrak, **6** yang diskemakan. ⚠️ `escalate_when` **bukan** penggantinya — eskalasi **memanggil manusia**, kill condition **berhenti tanpa menunggu** |
| **`deploy`** | — | [`03`](03-MONOREPO-FINAL.md) §5: “berjalan di tepi” adalah atribut, bukan folder |

### 🔧 Aturan validasi 3 ditulis ulang — dan menjadi jauh lebih kuat

| | Sekarang di `spec/05` | Menjadi |
|---|---|---|
| aturan 3 | *`risk_level >= 3` wajib punya isi `requires_confirmation`* | **setiap tool di `tools:` wajib punya `risk_level <= max_risk`** |

Alasannya dua, dan keduanya sudah tercatat:

1. **[#52](../../issues/52) sudah memindahkan `requires_confirmation` ke Policy
   Engine** — jadi aturan lama memeriksa medan yang seharusnya tidak lagi ada di
   manifest. Konsekuensi itu dicatat dan belum pernah dijalankan.
2. Aturan baru membuat manifest **tidak bisa berbohong**: agent yang menyatakan
   `max_risk: R1` sambil mendaftarkan `hotel.book` (R3) **ditolak saat
   registrasi**, bukan ditemukan saat ia memesan hotel.

⇒ **Konfirmasi tidak lagi dinyatakan di manifest sama sekali.** Ia turunan dari
`R` lewat tabel gerbang [`04`](04-DEPENDENCY-GRAPH.md) §3 — satu tempat, satu
tafsir.

---

## §4 Konstitusi §20.16 — sepuluh pasal, dan siapa yang menegakkannya

§20.16 menetapkan Konstitusi sebagai *“governance layer tertinggi”* dan
**tidak** menyatakan tiga hal: **siapa yang memeriksa**, **apa akibat
pelanggaran**, dan **apakah kebijakan lokal bisa melonggarkannya**. Ketiganya
dijawab di sini.

> ⭐ **Bentuk “konstitusi” itu sendiri menyelesaikan pola yang sudah muncul lima
> kali** (*keselamatan dijadwalkan sesudah yang dijaganya* —
> [#99](../../issues/99) · [#111](../../issues/111) · [#116](../../issues/116) ·
> [#121](../../issues/121) · [#131](../../issues/131)): **konstitusi tidak punya
> nomor urut.** Ia berlaku pada semua yang datang sesudahnya, **termasuk yang
> dibangun lebih dulu**.

| Pasal | Ditegakkan oleh | Mesin? |
|---|---|---|
| **1** Human sovereignty | `CONFIRMATION` wajib mulai R3 + `OVERRIDE` selama aksi | ✅ |
| **2** Least privilege | validasi scope (`spec/05` aturan 2·6·9) + `max_risk` (§3) | ✅ |
| **3** Transparency | tiap keluaran agent wajib membawa `rationale` + `confidence` | ✅ |
| **4** Auditability | gerbang `AUDIT` + `agent_runs` + **kembaran event** ([`07`](07-EVENT-CONTRACTS.md) §6) | ✅ |
| **5** Reversibility | R4 = `DENY` (*irreversible*) + `Rollback` di enam kata kerja override | ✅ |
| **6** Safety | rantai gerbang [`04`](04-DEPENDENCY-GRAPH.md) §3 + `evaluation.gates.safety ≥ 0.95` | ✅ |
| **7** Privacy | context package + vault `sensitivity ≥ 3` + policy **deny-by-default** | ✅ |
| **8** No deceptive behavior | ⚠️ **sebagian** — lihat bawah | ⚠️ |
| **9** No unauthorized autonomy | `autonomy.max_level` + **B-2** + kontrak hanya boleh **memperketat** (**B-5**) | ✅ |
| **10** Human override | gerbang `OVERRIDE`: Pause · Resume · Cancel · Revoke · Kill · **Rollback** | ✅ |

### Tiga jawaban yang §20.16 tinggalkan

| | Pertanyaan | 🔧 Jawaban |
|---|---|---|
| 1 | **siapa memeriksa, kapan** | Konstitusi **bukan gerbang kesebelas**. Ia **pemeriksa rantai gerbangnya**: tiap pasal wajib punya ≥1 penegak di tabel di atas, dan **CI menolak pasal tanpa penegak** ([`11`](11-PENEGAKAN.md) G-1). Konstitusi yang diperiksa saat runtime akan menjadi satu panggilan lagi yang bisa dilewati; konstitusi yang diperiksa saat **build** tidak bisa |
| 2 | **akibat pelanggaran** | registrasi **ditolak** · sertifikasi **dicabut** · `status: disabled` · event `constitution.violation_detected` (dan kembaran `constitution.violation_resolved`) |
| 3 | **bisakah policy lokal melonggarkan** | 🛑 **Tidak** — **B-5** [`04`](04-DEPENDENCY-GRAPH.md) §2. Kebijakan lokal hanya **memperketat** |

### 🛑 Pasal 8 — yang paling sulit, dan bagian yang tetap bisa ditegakkan

Sembilan pasal lain membatasi **apa yang boleh dilakukan** agent; Pasal 8
membatasi **bagaimana ia boleh menyampaikan**. Sistem yang mematuhi sembilan
pasal pertama tetapi boleh menyesatkan penyampaiannya bisa memperoleh
persetujuan untuk hal yang tidak dipahami penggunanya — dan dengan itu **Pasal 1
dan 10 kehilangan artinya**.

🔧 **Empat bagian yang bisa diperiksa mesin sekarang:**

| Aturan | Menutup |
|---|---|
| pesan keluar kepada **pihak ketiga** wajib membawa penanda bahwa penulisnya agent, diambil dari `agents/agent-identity/` | **C-19** ([#81](../../issues/81)) — penerima tidak bisa tahu |
| agent **tidak memakai kata ganti orang pertama untuk perasaan**; ekspresi menyatakan **keadaan sistem** (*sedang mendengar*, *tidak yakin*, *menunggu izin*) | §16.12 *“ekspresi robot transparan, bukan berpura-pura punya emosi manusia”* |
| **dilarang mengarang data** — rantai degradasi berakhir di kalimat `"No current data"`, bukan tebakan | §14.35; menutup bentuk terburuk **B-14** ([#26](../../issues/26)) |
| **sitasi wajib nyata** — setiap rujukan lulus langkah verifikasi sebelum ditampilkan | §19.20; [#134](../../issues/134) mencatat larangannya ada tapi **nol langkah menegakkannya** |

⚠️ **Sisanya tidak bisa diperiksa mesin**, dan itu dinyatakan apa adanya: apakah
sebuah penjelasan menyesatkan adalah penilaian. Tempatnya di
`evaluation/red-team/`, bukan di validator.

---

## §5 Apa yang **tetap** milik pemilik

| Butir | Kenapa |
|---|---|
| §16.5 · §16.7 — gerbang rantai humanoid | benda yang bisa melukai orang; gerbang yang tepat bukan keputusan gaya |
| [#112](../../issues/112) — lima angka keselamatan fisik (jarak henti · latensi reaksi · **batas gaya** · personal space · kecepatan per zona) | 🛑 **ketiadaan angka di sini ADALAH definisi keselamatan**. Menebaknya lebih buruk daripada membiarkannya terbuka |
| [#95](../../issues/95) — agent menandatangani kontrak, menghubungi pelanggan | kecakapan hukum ada pada orang/badan; siapa yang terikat bukan pertanyaan teknis |
| [#34](../../issues/34) — ambang confidence | butuh data nyata untuk dikalibrasi |
| [#18](../../issues/18) — tarif, bagi hasil, penyedia model | uang |

⭐ Yang **bisa** dinyatakan tanpa memutuskannya, dan sudah: §16.20 hanya
mendeteksi gaya yang **tak terduga**, bukan gaya yang **direncanakan** terlalu
besar — dan §16.23 menutup lingkarannya (robot menaikkan gayanya sendiri,
sehingga gaya baru itu kini “terduga”). ⇒ apa pun angkanya, ia harus berupa
**batas keras yang tidak bisa dinaikkan oleh pembelajaran**. Itu bentuknya,
bukan nilainya.

---

## §6 🛑 Nol perubahan untuk V0 — kecuali satu baris

| | |
|---|---|
| Agent V0 | **4**, tidak berubah |
| Tool V0 | **9**, tidak berubah; ditambah **3 entri `kind: agent`** (K-14) |
| Tabel baru | **NIHIL** |
| Kolom yang berubah | **1** — `agents.max_risk` menggantikan `risk_level`; `requires_confirmation` dihapus |
| `orchestrator-agent` | `max_risk` naik **R0 → R2** — akibat langsung aturan 3 baru, sebab ia memanggil `agent.habit` (R2) |
| Event baru | **NIHIL** |
| Aturan validasi | 3 **ditulis ulang** (§3), 8 lainnya tidak berubah |

---

## §7 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Nama agent yang diketahui | **59** — bukan “> 40” |
| Nama tanpa manifest yang masuk registry | **NIHIL** — bawaan `service` |
| Agent V0 yang diuji K-5 | **4 dari 4** — bukan dinyatakan, diperiksa |
| Agent yang memanggil agent tanpa entri tool | ditolak CI — [`11`](11-PENEGAKAN.md) A-3 |
| Manifest dengan tool `risk_level > max_risk` | ditolak CI — A-2 |
| Satu angka dipakai untuk R **dan** L | ditolak CI — A-1 |
| Pasal Konstitusi tanpa penegak | **1 dari 10 sebagian** (Pasal 8) — dinyatakan, tidak disembunyikan |
| `requires_confirmation` di manifest | **NIHIL** — turunan dari R |
