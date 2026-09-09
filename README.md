# HumanVerse XOS

> **AI-Native Human Development Platform**
> **One AI. Infinite Human Growth.**
> `Observe → Understand → Reason → Predict → Recommend → Act → Learn`

Bukan aplikasi *habit tracker* biasa. Seluruh domain kehidupan dihubungkan
menjadi satu **Human Knowledge Graph**, lalu di atasnya berdiri **AgentOS**,
**Memory Hierarchy**, **Context Engine**, **Behavior Engine**, **Decision
Engine**, dan **Digital Twin** — sebuah platform yang punya **runtime untuk
manusia + agent + data + knowledge + simulation + automation**.

> ✅ **Nama resmi diputuskan 3 September 2026: `HumanVerse XOS`.**
> Berkas naskah `01`–`77` tetap menulis nama versi masing-masing naskah
> (*HumanOS*, *HumanVerse X*) apa adanya. Lihat [`docs/10-IDENTITAS.md`](docs/10-IDENTITAS.md).

---

## Status proyek

| Hal | Keadaan |
|---|---|
| Tahap | **Spesifikasi engineering siap** — belum ada kode (disengaja) |
| Berkas kode | 0 |
| Repo git | privat `xtheoputra/humanverse-xos`, branch `master` |
| Dokumen | **272 berkas** di `docs/` (naskah + audit + 6 sensus + peta fase + keputusan + catatan sesi) + **8 berkas** di `spec/` |
| Naskah pemilik | **24** — terakhir: **Phase 20 Civilization Platform** (39 bagian) — **fase TERAKHIR** |
| Keputusan tertutup | **24 butir H** — nama · MVP · struktur repo · ambang konfirmasi · model memory · memory meluruh · gerbang policy · context package · peta 15 fase · dua tangga R/L · manifest dipulihkan · **model transisi belajar dari galat sendiri** · **monetisasi punya fase (Phase 14)**. 🛑 **H-20 PATAH, dan petanya TERBUKA-UJUNG** — **empat naskah berturut-turut masing-masing menambah satu fase** di kalimat penutupnya: naskah 19 → **Phase 16**, naskah 20 → **Phase 17**, naskah 21 → **Phase 18**, naskah 22 → **Phase 19 Civilization Intelligence**. ⭐ **Naskah 23 MEMBALIKKAN polanya sebagian** — ia mengubah Phase 19 menjadi *Scientific Discovery Engine*, memindahkan Civilization ke **Phase 20**, dan **mengumumkan perubahan itu beserta alasannya**: pertama kalinya dalam lima naskah, dan ia menyebut **Phase 20 sebagai fase TERAKHIR**. 🛑 Tapi ia menyandarkannya pada *“roadmap 20 fase yang sudah kita tetapkan sebelumnya”* — yang **tidak pernah ada** ([#132](../../issues/132), [#133](../../issues/133), [#101](../../issues/101), [#108](../../issues/108)). ⚠️ **H-13** ([#72](../../issues/72)) dan **H-11** ([#78](../../issues/78)) juga perlu ditinjau ulang |
| Keputusan terbuka | **26 pertanyaan A** · **39 risiko B** · **157 ketidakcocokan E** · **20 lubang G** — dan **8 butir K** sudah saya putuskan sendiri |
| Tanggal dokumen | 8 September 2026 |

> ⚠️ **Nol baris kode itu disengaja — dan penghambatnya terus berkurang.**
> Lima naskah sudah menjawab: **nama** (A-7), **MVP** (A-2), **struktur repo**
> (E-27), **Weather/Calendar = tool** (E-2/E-28), **empat penyimpanan bukan
> enam** (A-10), **V0–V6 sebagai rencana kanonik** (A-18), dan **Confidence
> Layer** untuk angka taksiran (B-15/B-1).
>
> ✅ **TIDAK ADA yang mengunci Engineering Spec.** Daftar "empat penghambat" di
> versi lama README ini **salah**, dan [`spec/README.md`](spec/README.md) sudah
> membantahnya sejak awal — lengkap dengan cara tiap butir ditangani di DDL:
> **#32** skala skor → `numeric(4,3) CHECK BETWEEN 0 AND 1` + `scoring_version` ·
> **#2** model angka → `metrics jsonb` + `model_version` (enam model boleh
> hidup berdampingan, tanpa migrasi) · **#7** model graf → **tidak menyentuh V0**,
> Neo4j baru di V2 · **#33** memory → **sudah ditutup** (`kind` + `scope`, plus
> `tier` dari H-16).
>
> 🛑 **Penghambat V0 yang sebenarnya cuma dua, dan keduanya bukan soal skema:**
> **[#3](../../issues/3)** (siapa mengerjakan 12 fitur dalam 4–6 minggu) dan
> **[#20](../../issues/20)** (cek merek, domain, nama paket).
>
> 🔑 Rekonsiliasi lengkap kedua dokumen ada di
> [`docs/GERBANG-SKEMA.md`](docs/GERBANG-SKEMA.md).

---

## 📌 Pekerjaan terbuka = GitHub Issues

**153 issue** dalam 3 milestone — **25 ditutup**. Baca issue-nya, jangan analisis
ulang naskahnya.

| Milestone | Isi | Issue |
|---|---|---|
| **M1 — Keputusan sebelum kode** | 34 terbuka, 6 ditutup | [#1](../../issues/1)–[#9](../../issues/9), [#38](../../issues/38), [#58](../../issues/58)–[#59](../../issues/59), [#72](../../issues/72), [#80](../../issues/80), [#90](../../issues/90)–[#93](../../issues/93), [#98](../../issues/98)–[#101](../../issues/101), [#103](../../issues/103), [#105](../../issues/105), [#108](../../issues/108), [#111](../../issues/111)–[#113](../../issues/113) |
| **M2 — Blueprint & Platform** | 68 terbuka, 17 ditutup | [#10](../../issues/10)–[#19](../../issues/19), [#26](../../issues/26)–[#37](../../issues/37), [#39](../../issues/39), [#41](../../issues/41)–[#45](../../issues/45), [#47](../../issues/47)–[#49](../../issues/49), [#51](../../issues/51), [#54](../../issues/54)–[#56](../../issues/56), [#60](../../issues/60)–[#70](../../issues/70), [#73](../../issues/73)–[#74](../../issues/74), [#77](../../issues/77)–[#79](../../issues/79), [#82](../../issues/82)–[#84](../../issues/84), [#87](../../issues/87)–[#89](../../issues/89), [#94](../../issues/94), [#96](../../issues/96)–[#97](../../issues/97), [#106](../../issues/106)–[#107](../../issues/107), [#109](../../issues/109)–[#110](../../issues/110) |
| **M3 — Sebelum ada pengguna nyata** | 26 terbuka, 2 ditutup | [#20](../../issues/20)–[#25](../../issues/25), [#40](../../issues/40), [#46](../../issues/46), [#50](../../issues/50), [#52](../../issues/52)–[#53](../../issues/53), [#57](../../issues/57), [#71](../../issues/71), [#75](../../issues/75)–[#76](../../issues/76), [#81](../../issues/81), [#85](../../issues/85)–[#86](../../issues/86), [#95](../../issues/95), [#102](../../issues/102), [#104](../../issues/104), [#114](../../issues/114) |

⚠️ **[#55](../../issues/55) meninjau ulang keputusan yang sudah ditutup:**
monorepo final (H-10) kini tergerus **SEPULUH kali** — tiga pohon dari naskah
9/10/11, **enam** dari naskah 18, **`spatial-os/`** (naskah 19), **`robotics/`**
(naskah 20), **`health-bio/`** (naskah 21, [#120](../../issues/120)), dan
**`global-intelligence/`** (naskah 22, [#129](../../issues/129)), dan
**`scientific-discovery/`** (naskah 23, [#138](../../issues/138)), dan
**`civilization-platform/`** (naskah 24, [#143](../../issues/143)) — sehingga pohon
keamanan menjadi **sebelas** (`security/` · `agent-security/` ·
`spatial-os/safety/` · `spatial-os/privacy/` · `robotics/safety/` ·
`health-bio/safety/` · `health-bio/privacy/` · `global-intelligence/security/` ·
`global-intelligence/privacy/` · `scientific-discovery/safety/` · `sovereignty/privacy/`) dan aturan impor
§8.42 tidak lagi bisa dinyatakan. **DUA BELAS naskah berturut-turut menyentuh
struktur repo.** 🔴 `governance/` muncul di naskah 22 — **di dalam pohon
fase** — lalu naskah 23 **tidak mewarisinya sama sekali**, memakai `ethics/` +
`safety/` sendiri: pembuktian langsung bahwa tata kelola yang hidup di satu fase
tidak diwarisi fase berikutnya ([#138](../../issues/138)).
🛑 Naskah 20 bahkan memberi struktur repo **dua kali di dalam satu naskah**
([#109](../../issues/109)).
Sprint 0 tugas 0.1 menunggu jawabannya.

🔴🔴 **Dan sekarang seluruhnya sudah DIHITUNG, bukan diingat** —
[`docs/SENSUS-MODUL.md`](docs/SENSUS-MODUL.md) ([#146](../../issues/146)):
**38 pohon repositori** di 36 dokumen · **424 nama direktori unik** ·
**128 (30 %) dipakai lebih dari satu pohon**. Sensus itu membalik dua angka
yang selama ini dipakai: `simulation/` dilacak lima naskah dan berhenti di
*“keenam kalinya”* — nyatanya **lima belas pohon**; dan yang paling banyak
diduplikasi bukan `simulation/` melainkan **`sdk/` di EMPAT BELAS pohon**, yang
**tidak pernah sekali pun dihitung**. 💡 Pelajarannya: menghitung *“ini yang ke
berapa”* satu per satu di berkas yang berbeda-beda **meleset ke bawah secara
sistematis** — yang dibutuhkan satu sensus, bukan catatan yang lebih rajin.

🔴🔴 **Peta fasenya juga diukur** — [`docs/PETA-FASE.md`](docs/PETA-FASE.md)
([#148](../../issues/148)): untuk `Phase` ada **tiga** peta, bukan dua, dan
kedua peta yang bisa diuji **gagal dengan cara yang persis sama** — benar untuk
fase-fase terdekat, meleset di ujung. Peta naskah 8 meramalkan 8 fase dan tepat
pada **empat yang terdekat**; §10.41 meramalkan 5 dan meleset pada **yang
terjauh**. ⇒ **jangkauan andal sebuah peta fase di repo ini ± 3–4 fase.**
⭐ Dan satu koreksi yang **memperkecil** pekerjaan: [#142](../../issues/142)
menyimpulkan *“Phase 1–8 belum pernah didaftar”* dari sebuah `grep` yang
menuntut huruf besar semua — pola itu **mustahil** cocok dengan *“Phase 5:
HumanVerse Research Lab”*. **Tujuh dari delapan fase sudah punya nama**, dan
sudah terkumpul di [`99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md) baris
17–20. Sisanya **satu nama (Phase 1) + tujuh kata kerja**, bukan delapan baris
kosong. 💡 *`grep` yang mengembalikan nol membuktikan “tidak ada yang berbentuk
ini”, bukan “tidak ada”.*

🔴🔴 **Nama event juga dihitung** — [`docs/SENSUS-EVENT.md`](docs/SENSUS-EVENT.md)
([#149](../../issues/149)). [#38](../../issues/38) sudah ditutup dengan format
`domain.verb`, dan pelanggarannya dicatat sampai *“kesepuluh”* — tetapi yang
dihitung selama ini **kejadian**, bukan **nama**. Sensus: **21 nama sesuai
lawan 128 nama PascalCase yang ditulis sesudah keputusan**. ⭐ Dan yang paling
menentukan: **ke-21 nama yang sesuai semuanya berasal dari naskah 5** — sejak
itu pemilik menamai 128 event baru dan **nol** memakai format yang dipilih.
Formatnya bukan diperdebatkan, ia tidak pernah dipakai lagi. 💰 Biayanya masih
nol karena belum ada kode — kecuali **tiga tabrakan kosakata**
(`sleep.completed`↔`SleepEnded` dan dua lainnya) yang tidak selesai hanya
dengan mengubah bentuk.

🔴🔴 **Daftar agent juga dihitung** — [`docs/SENSUS-AGENT.md`](docs/SENSUS-AGENT.md)
([#150](../../issues/150)). Jumlah agent selama ini ditaksir dengan
**penjumlahan** (*“> 40”* dari 25 + 7 + 12), yang mengabaikan dua daftar lebih
tua dan menganggap tak ada nama berulang. Himpunannya: **80 baris mentah → 59
nama unik**, **nol** muncul di semua daftar, dan **44 (75 %) hanya pernah
disebut sekali**. ⭐ Irisan ketiga registry umum — yang berisi 14, 22, dan 25
agent — tepat **enam**: `Career · Fashion · Habit · Learning · Social · Travel`,
**semuanya agent domain**. 💡 *Menjumlahkan daftar bukan menghitung himpunan —
dan yang menentukan bukan totalnya melainkan irisannya.*

🔴🔴 **Dan separuh kedua [#38](../../issues/38) ternyata terbalik arahnya.**
Sepuluh catatan menandai naskah sebagai *“`/v1/…` lagi, bukan `/api/v1`”* —
sensus: **111 rute `/v1/…` di 12 naskah, dan NOL `/api/v1`**, 92 di antaranya
persis bentuk yang ditetapkan **standar penamaan pemilik sendiri** (naskah 7
Layer 22, `/v1/fashion/outfits`). Naskahnya konsisten; yang menyimpang
`spec/04` — berkas saya. 🛑 Dan komentar yang **menutup** #38 sudah menuliskan
janjinya (*“itu bagian saya, akan diselaraskan”*) — janji itu tak pernah
dijalankan, sementara sepuluh catatan berikutnya menandai sisi yang tidak
dijanjikan berubah. ✅ **Diselesaikan: `spec/04` kini berawalan `/v1`** (satu
baris). 💡 *Janji perbaikan di komentar issue yang DITUTUP tidak punya penjaga —
tanyakan “ada janji tercatat di sini, siapa yang memeriksanya?”*

🔴🔴 **Jumlah tabel pun berhenti dipelihara delapan fase yang lalu** —
[`docs/SENSUS-TABEL.md`](docs/SENSUS-TABEL.md) ([#151](../../issues/151)).
Catatan **E-106** menjumlahkan `23+20+16+14+26 = 99`, dan **metodenya benar**
(tiap suku neto) — tetapi ia **berhenti di Phase 12**. Himpunannya
**247 nama tabel** di 14 dokumen; **139 di antaranya lahir sesudah Phase 12 dan
belum pernah masuk hitungan mana pun**. 🛑 Dan **`agent_capabilities` serta
`agent_trust_scores` didefinisikan EMPAT kali** (Phase 8·11·14·18) — untuk
tabel yang memegang kapabilitas dan kepercayaan agent, itu empat kemungkinan
bentuk kolom. ✅ Sensusnya divalidasi enam kali; yang terkuat: ia mereproduksi
sendiri pernyataan provenans [`spec/01`](spec/01-DATABASE-SCHEMA.md).

🛑🛑 **Dan satu temuan keselamatan yang lahir dari melacak SATU tindakan
melintasi empat tangga risiko** — [`docs/SENSUS-TANGGA.md`](docs/SENSUS-TANGGA.md)
([#152](../../issues/152)). *“Kirim pesan kepada orang lain”* adalah **level 3**
di naskah 4, **level 3** di naskah 5, dan **R3** di Phase 8 — lalu **R2** di
Phase 11 (*“send low-risk message”*). Ambangnya sudah ditutup sebagai **H-15**:
otomatis sampai R2, konfirmasi wajib mulai R3 — jadi **pemindahan itu melewati
ambangnya**. §11.15 bahkan menaruh pesan di **dua tingkat dalam satu tabel**,
dipisahkan hanya oleh kata sifat yang tak pernah didefinisikan. ⭐ Tetangganya
`purchase low-value item` punya cacat identik tetapi **diselamatkan**
`amount_limit: 0`; pesan tidak punya padanannya. ⇒ **Dari tiga kategori di baris
R2, yang tidak mendapat definisi maupun angka bawaan justru satu-satunya yang
punya orang lain di ujung penerimanya.**

⭐ **Dan satu sensus akhirnya membawa kabar BAIK** —
[`docs/SENSUS-RANTAI.md`](docs/SENSUS-RANTAI.md) ([#153](../../issues/153)).
Tujuh catatan melaporkan *"rantai tanpa gerbang"* tanpa pernah menyebut
penyebutnya. Sensus: **387 rantai**, **36 berakhir di tindakan**, dan
**20 di antaranya SUDAH punya gerbang**. Dari 16 yang ditandai, **10 bukan
cacat** (dekomposisi tujuan, pipeline CI, kill-switch, rantai provenans) dan
2 sudah tertangani. 🛑 **Tiga benar-benar baru, dan ketiganya menggerakkan
benda fisik**: §15.15 (*lambaian tangan menjadi tindakan tanpa satu simpul pun
di antaranya*), §16.5 (*tujuan manusia langsung ke kendali sendi*), §16.7
(*punya `Collision Check`, tetapi itu menjawab "aman secara fisik", bukan
"boleh dilakukan"*).

## 🔧 Delapan keputusan yang diambil sendiri — [`docs/KEPUTUSAN-DIDELEGASIKAN.md`](docs/KEPUTUSAN-DIDELEGASIKAN.md)

Atas permintaan pemilik (*"beri keputusan sendiri sesuai aturan"*, 9 Sep 2026),
delapan pertanyaan **engineering** diputuskan dan ditegakkan di `spec/` — tiap
butir dengan **bacaan yang ditolak** dan **cara membalikkannya**:

| | Keputusan | Ditegakkan di |
|---|---|---|
| **K-1** | Kapabilitas yang menyentuh **pihak ketiga** = minimum **R3** | `spec/05` aturan 7 + medan `reaches_third_party` |
| **K-2** | `world-model/` **menyimpan**, `simulation/` **menjalankan** | — |
| **K-3** | 127 nama event **dipadankan**; naskah **tidak** diubah | `spec/03` tabel padanan |
| **K-4** | Tabel berdefinisi ganda: `spec/01` menang, lalu fase terawal | `spec/01` |
| **K-5** | **Tiga uji** agent lawan service | `spec/05` |
| **K-6** | Tujuh **kata kerja** Phase 2–8 | — |
| **K-7** | §15.15 mendapat simpul `Permission` | — |
| **K-8** | Awalan API `/v1` | `spec/04` |

🛑 **Yang sengaja TIDAK saya putuskan:** [#139](../../issues/139) (waktu pemilik) ·
[#3](../../issues/3) (orang) · [#20](../../issues/20) (merek) · **seluruh butir C**
(hukum & privasi) · **§16.5 · §16.7** rantai humanoid · [#34](../../issues/34)
(butuh data nyata untuk dikalibrasi).

💡 **Aturan pemilahnya: kalau salahnya keputusan ini ditanggung orang lain —
pengguna, penerima pesan, atau pemilik uangnya — keputusan itu bukan milik saya.**

⚠️ **Nol dari delapan mengubah V0**: `spec/01` tetap 23 tabel, `spec/03` tetap
22 event V0, keempat agent V0 lulus ketiga uji K-5.

✅ **Ditutup:** [#1](../../issues/1) rencana kanonik → V0–V6 ·
[#8](../../issues/8) struktur repo · [#12](../../issues/12) Weather/Calendar = tool ·
[#17](../../issues/17) empat penyimpanan · [#10](../../issues/10) blueprint ·
[#31](../../issues/31) Engineering Specification · [#38](../../issues/38) nama event dua segmen ·
[#5](../../issues/5) ambang konfirmasi → **otomatis sampai R2, konfirmasi mulai R3** ·
[#52](../../issues/52) `risk_level` kembali & konfirmasi pindah ke Policy Engine ·
[#33](../../issues/33) memory = **tiga sumbu** `kind`/`scope`/`tier` ·
[#50](../../issues/50) Identity Memory **meluruh**, tidak permanen ·
[#42](../../issues/42) `POLICY_CHECK` masuk rantai percakapan ·
[#62](../../issues/62) agent tidak mengambil data — **context package** ·
[#66](../../issues/66) peta fase **diganti**: 12 → **15 fase**, Agency→P11, Digital Twin→P12,
Marketplace→P14 ·
[#67](../../issues/67) **dua tangga dipisahkan** — `risk_level: R1` + `autonomy.max_level: L2` ·
[#61](../../issues/61) manifest memulihkan `purpose` + `memory.read`/`write` ·
[#70](../../issues/70) model transisi punya sumber — **galat prediksinya sendiri**.

🛑 **Penghambat V0 yang tersisa — tiga:**
[#3](../../issues/3) 12 fitur & 7 sprint dalam 4–6 minggu ·
[#20](../../issues/20) cek merek ·
🆕 [#59](../../issues/59) **`consents.purpose` + `model_training` harus ada sebelum baris data
pertama** — §8.10 melarang memakai data di luar tujuan pemberiannya, jadi data V0 yang tidak
pernah menanyakannya **tidak bisa melatih model apa pun di Phase 5**. Biayanya nol sekarang,
hampir mustahil nanti.
*(#38 format nama event ✅ ditutup naskah 10 — dua segmen. #5 ambang konfirmasi ✅ ditutup
naskah 12 — R3 ke atas.)*
Yang masih menunggu jawaban tapi tidak menahan Sprint 0–4:
[#2](../../issues/2) model angka pengguna (menahan Sprint 5) ·
[#21](../../issues/21) eskalasi krisis Journal (menahan rilis ke orang lain — dan naskah 12
lewat tanpa menyebut jurnal sekali pun) ·
[#58](../../issues/58) berapa banyak Fase 8 & 9 masuk V0 (punya default aman: pakai 23 tabel yang
sudah ada) ·
🆕 [#67](../../issues/67) **dua tangga 0–4 yang terbalik di ujung atas** — otonomi “Level 4”
(bertindak sendiri) vs risiko “R4” (wajib konfirmasi); belum mengikat V0 karena tidak ada tool
di atas level 2, tapi harus diselesaikan sebelum tangga mana pun masuk basis data ·
🆕 [#72](../../issues/72) **rencana kanonik: V0–V6 atau Phase 1–15?** Naskah 13 & 14 tidak
menyebut tangga V sama sekali, dan **V0 tidak punya tempat di daftar 15 fase** — padahal V0
satu-satunya lingkup tertutup yang pernah ditetapkan. Ini H ketiga yang tergerus ·
[#75](../../issues/75) pemantauan berkelanjutan di dalam rumah — izin `Always`; belum mengikat V0
(tidak ada kamera), tapi on-device (§10.28) harus mendahului Vision ·
[#80](../../issues/80) V0 reaktif atau proaktif? — jawaban aman: **V0 reaktif** ·
🆕 [#86](../../issues/86) **sampai horizon berapa proyeksi boleh ditampilkan?** §12.13 memberi
sampai **5 tahun**, dan horizon 3–5 tahun **tidak pernah masuk loop belajar** — satu-satunya
keluaran yang tidak bisa dikalibrasi ·
🆕 [#85](../../issues/85) **proyeksi masa depan = kelas data baru** yang paling diinginkan pihak
ketiga; dan §12.22 memakai bobot utilitas yang **disimpulkan** untuk **memaksimalkan**, bukan
lagi membandingkan.

---

## 🔧 Engineering Specification v1.0 — [`spec/`](spec/README.md)

Lapisan **04** dari peta 14 lapisan naskah 6, dikerjakan penuh. **Bukan kata
pemilik** — sengaja di luar `docs/` supaya berkas naskah tetap murni.

| Berkas | Isi |
|---|---|
| [`spec/01-DATABASE-SCHEMA.md`](spec/01-DATABASE-SCHEMA.md) | DDL PostgreSQL — **23 tabel**, tipe, PK, FK, index, constraint, prosedur hapus akun |
| [`spec/02-ERD.md`](spec/02-ERD.md) | Relasi + 6 aturan kepemilikan data |
| [`spec/03-EVENT-CONTRACTS.md`](spec/03-EVENT-CONTRACTS.md) | Envelope, **versi · urutan · idempotensi**, 22 event, consumer |
| [`spec/04-API-CONTRACTS.md`](spec/04-API-CONTRACTS.md) | Endpoint REST V0 + Privacy Center |
| [`spec/05-AGENT-CONTRACTS.md`](spec/05-AGENT-CONTRACTS.md) | Manifest schema (6 aturan validasi), tool registry, risk gate |
| [`spec/06-MODULE-BOUNDARIES.md`](spec/06-MODULE-BOUNDARIES.md) | Batas modul + 6 aturan yang **ditegakkan CI** |
| [`spec/07-BACKLOG-V0.md`](spec/07-BACKLOG-V0.md) | **51 tugas** dalam 7 sprint, siap diberikan ke AI coding agent |

**Tiga issue pengunci ternyata tidak perlu diputuskan sekarang** — skemanya
menampung kedua kemungkinan tanpa biaya:

| Issue | Cara ditangani |
|---|---|
| [#33](../../issues/33) memory: jenis atau scope | **keduanya** — `kind` untuk pengambilan, `scope` untuk izin |
| [#32](../../issues/32) tiga skala skor | simpan **0–1** + `scoring_version` + `score_breakdown` |
| [#2](../../issues/2) lima model angka pengguna | `human_states.metrics jsonb`, bukan kolom tetap |
| [#7](../../issues/7) model graf | **tidak menyentuh V0** — Neo4j baru masuk V2 |

> ⚠️ Menunda bukan menjawab. Selama #2 belum dipilih, tidak ada yang bisa
> **menghitung** angkanya — tabelnya hanya siap menampungnya.

---

## ⭐ MVP sudah ada namanya: V0 — HumanVerse Foundation

Untuk pertama kalinya dalam empat naskah, ada **daftar tertutup** yang bisa
dikerjakan. Target pemilik: **4–6 minggu**.

```
Authentication · Profile · Goals · Habits · Daily Check-in
Mood · Journal · AI Coach · Basic Memory · Dashboard

Agent:  Orchestrator · HabitAgent · CoachAgent · MemoryAgent
```

Selengkapnya: [`docs/75-URUTAN-PEMBANGUNAN-V0-V6.md`](docs/75-URUTAN-PEMBANGUNAN-V0-V6.md)

---

## Dua puluh empat naskah

```
  NASKAH 1   HumanOS — visi & 12 modul manusia          berkas 01–07
     │
  NASKAH 2   HumanVerse X — arsitektur eksekusi         berkas 10–22
     │       monorepo · 3 lapis agen · roadmap V0–V5
     │
  NASKAH 3   Phase 2 Enterprise Multi-Agent Platform    berkas 30–46
     │       Layer 6–20 · AgentOS · SDK · Marketplace
     │       160 dokumen engineering
     │
  NASKAH 4   Phase 3 AI-Native Human Ecosystem          berkas 50–77
     │       58 bagian · V0–V6 · HumanVerse Economy
     │       "arsitektur boleh besar, implementasinya bertahap"
     │
  NASKAH 5   Blueprint Engineering v1.0                 berkas 80–97
     │       34 bagian · monorepo final · 22 agent · 7 sprint V0
     │       "berhenti menambah visi/fitur"
     │
  NASKAH 6   Peta 14 lapisan engineering               berkas 98
     │       Operating Model · "jangan lompat ke fitur baru lagi"
     │       └──► lapisan 04 dikerjakan → spec/
     │
  NASKAH 7   Phase 4 Enterprise Operating System       berkas 100–112
     │       Layer 21–50 · standards · design system · AI Ops
     │
  NASKAH 8   Peta Phase 5–12                            berkas 113
     │       ≈380 dokumen tersisa · taksiran kemajuan 45 %
     │
  NASKAH 9   Phase 5 — HumanVerse Research Lab         berkas 114–122
     │       15 research pillar · BFM · memory compression
     │
  NASKAH 10  Phase 6 — Developer Platform              berkas 123–131
     │       25 layer · OAuth · SDK 7 bahasa · marketplace
     │
  NASKAH 11  Phase 7 — Data & AI Infrastructure        berkas 132–141
     │       event platform · lakehouse · feature store
     │       deletion engine · 18 deliverable (1 "Future")
     │
  NASKAH 12  Phase 8 — AI Safety, Security & Privacy   berkas 142–153
     │       46 bagian · identity · consent · data vault
     │       risk policy R0–R4 · kill switch · privacy center
     │
  NASKAH 13  Phase 9 — Intelligence & Cognitive Arch.  berkas 154–164
     │       41 bagian · memory 6 jenis · decay & konsolidasi
     │       cognitive runtime · POLICY_CHECK
     │
  NASKAH 14  Phase 10 — Multimodal Intelligence        berkas 165–175
     │       persepsi: vision · audio · spatial
     │       peta 15 fase (menggantikan peta naskah 8)
     │
  NASKAH 15  Phase 11 — Agentic Intelligence & Agency  berkas 176–187
     │       64 bagian · Action Gateway · dua tangga R & L
     │       budget · multi-agent · "autonomy must be earned"
     │
  NASKAH 16  Phase 12 — Digital Twin & World Simulation berkas 188–197
     │       31 bagian · assumption engine · learning loop
     │       "Observed ≠ Certain"
     │
  NASKAH 17  Phase 13 — HumanOS, Personal AI OS        berkas 198–206
     │       40 bagian · Attention OS · Approval Center
     │       state machine · app/agent/plugin
     │
  NASKAH 18  Phase 14 — Autonomous Intelligence &      berkas 207–218
     │       Collective Agent Ecosystem
     │       69 bagian (terpanjang) · federasi · agent team
     │       governance mesh · agent economy · L5 + autonomy contract
     │       "More agents must not automatically mean more autonomy"
     │
  NASKAH 19  Phase 15 — Spatial Intelligence &         berkas 219–227
     │       XR Universe
     │       32 bagian · SpatialOS · SLAM · scene graph
     │       spatial memory · AetherScan · XR · gesture/eye tracking
     │       "The world becomes an interface."
     │       ⚠️ mengumumkan Phase 16 → peta 15 fase patah (#101)
     │
  NASKAH 20  Phase 16 — Robotics & Embodied            berkas 228–235
             Intelligence
             35 bagian · HRP · SLAM/ROS2 · motion planning
             manipulasi · smart home/IoT · drone · fleet
             safety kernel · safe zones · simulation-first
             "Intelligence becomes embodied." — satu AI, banyak tubuh
             ⚠️ mengumumkan Phase 17 → peta terbuka-ujung (#108)
     │
  NASKAH 21  Phase 17 — Human Health & Bio             berkas 236–245
             Intelligence
             56 bagian · Health Digital Twin · Health Vault
             tidur/recovery · nutrisi · stress · anomali & forecast
             rekam medis · federasi · model registry · bias engine
             ⭐ Health Safety Kernel — rantai pertama dengan Risk
                DAN Evidence Check; metrik evaluasi model PERTAMA
             "HumanVerse tidak boleh menjadi AI dokter yang serba tahu."
             🛑 Safety & Governance di LUAR MVP ([#116](../../issues/116))
     │
  NASKAH 22  Phase 18 — Global Intelligence Network    berkas 246–255
             34 bagian · World Model · World Knowledge Graph
             HINP · federasi knowledge/agent · collective intelligence
             trust vector · provenance · global risk · early warning
             organization & city intelligence · marketplace
             ⭐⭐ `UNRESOLVED` sebagai KELUARAN yang sah (§18.23) —
                pertama kalinya sistem boleh berhenti tanpa jawaban
             "HumanVerse tidak mengontrol dunia."
             🛑 Safety Kernel §18.22 TANPA milestone ([#121](../../issues/121))
             🛑 `productivity` atas `People` = larangan §8.10 ([#122](../../issues/122))
             ⚠️ mengumumkan Phase 19 → perpanjangan KEEMPAT (#101)
     │
  NASKAH 23  Phase 19 — Scientific Discovery           berkas 256–265
             Engine (SDE)
             34 bagian · Research Knowledge Graph · evidence ranking
             gap detection · hypothesis · experiment planner
             Monte Carlo · reproducibility · writing & peer review
             ethics & safety · model registry · lab automation
             ⭐⭐ §19.17 `Remaining Disagreement` MENUTUP separuh
                [#121](../../issues/121) — usul satu naskah lalu, dipakai
             ⭐⭐ *“sitasi harus nyata, tidak boleh mengarang referensi”*
             "From consuming knowledge to creating knowledge."
             🛑 Ethics & Safety milestone TERAKHIR, di fase yang menamai
                Biosecurity & menggerakkan materi fisik ([#131](../../issues/131))
             🛑 “roadmap 20 fase” yang dirujuknya tidak pernah ada ([#132](../../issues/132))
             ⭐ mengumumkan Phase 20 sebagai fase TERAKHIR — ujung pertama
                yang dinyatakan sejak §10.41 ([#133](../../issues/133))
     │
  NASKAH 24  Phase 20 — Civilization Platform          berkas 266–275
             39 bagian · Civilization KG/State/Twin · simulasi & skenario
             collective intelligence · distributed AI · privasi & kedaulatan
             identity · governance · impact · resilience · crisis
             resource · sustainability · CivilizationOS · marketplace
             ⭐⭐ **AGENT CONSTITUTION** — sepuluh pasal; tiga menutup
                butir lama (Reversibility/H-21 · No unauthorized
                autonomy · Human override/H-15), dan **konstitusi
                tidak punya nomor urut**
             ⭐⭐ **§20.35 memisahkan ANALYSIS dari ACTION** — gerbang
                yang dicari lima naskah, akhirnya digambar
             "Human sovereignty over machine autonomy."
             🛑 lima jalur di naskah yang sama tak melewatinya ([#140](../../issues/140))
             🛑 peta 20 fase cuma 12 baris; Phase 1–8 nihil ([#142](../../issues/142))
             ⭐⭐⭐ **USUL: jangan buat Phase 21 — buat MASTER
                ARCHITECTURE v2.0** ([#139](../../issues/139))
```

> ℹ️ Penomoran berkas melewati 99. `99-CATATAN-AUDIT.md` tetap di tempatnya
> sebagai berkas audit; naskah 7 memakai `100`–`112`.
>
> ℹ️ **Peta dokumen di bawah baru mencakup naskah 1–11.** Untuk naskah 12–18
> (`142`–`235`), daftar berkas per naskah ada di
> [`docs/SESSION-LOG.md`](docs/SESSION-LOG.md) — satu entri per sesi.

---

## Aturan berkas dokumen

1. Berkas `01`–`275` merekam **kata pemilik apa adanya**. Susunannya dirapikan,
   isinya tidak ditambah-tambahi. Bagian yang hilang di naskah **ditandai
   sebagai hilang**, bukan ditambal.
2. Setiap keraguan, koreksi, risiko, atau usulan dari pihak lain (termasuk AI)
   masuk ke `99-CATATAN-AUDIT.md` — **tidak pernah disisipkan** ke berkas visi.
3. Kalau pemilik memutuskan sesuatu, keputusan itu **naik** ke berkas visi yang
   sesuai, lalu butirnya turun ke bagian **H** di berkas audit.
4. Tujuh berkas **bukan** rekaman naskah:
   [`00-DAFTAR-ISI.md`](docs/00-DAFTAR-ISI.md) (dibangun dari isi direktori),
   [`99-CATATAN-AUDIT.md`](docs/99-CATATAN-AUDIT.md),
   [`GERBANG-SKEMA.md`](docs/GERBANG-SKEMA.md),
   [`SENSUS-MODUL.md`](docs/SENSUS-MODUL.md),
   [`SENSUS-EVENT.md`](docs/SENSUS-EVENT.md),
   [`SENSUS-AGENT.md`](docs/SENSUS-AGENT.md),
   [`SENSUS-TABEL.md`](docs/SENSUS-TABEL.md),
   [`SENSUS-TANGGA.md`](docs/SENSUS-TANGGA.md),
   [`SENSUS-RANTAI.md`](docs/SENSUS-RANTAI.md) dan
   [`PETA-FASE.md`](docs/PETA-FASE.md) (ketujuhnya pengukuran — tidak
   memutuskan apa pun),
   [`KEPUTUSAN-DIDELEGASIKAN.md`](docs/KEPUTUSAN-DIDELEGASIKAN.md) (keputusan
   yang saya ambil sendiri, tiap butir bisa dibatalkan), dan
   [`SESSION-LOG.md`](docs/SESSION-LOG.md).

---

## Peta dokumen

> 📚 **Daftar lengkap ada di [`docs/00-DAFTAR-ISI.md`](docs/00-DAFTAR-ISI.md)** —
> **263 berkas**, berurutan, dikelompokkan per naskah, masing-masing dengan
> keterangan isi dan jumlah barisnya.

Bagian ini dulu memuat daftar berkas, tetapi berhenti dipelihara di berkas
`141` (naskah 11) — ia hanya mencakup **126 dari 263** berkas. Daftar induk
menggantikannya, dan dibangun ulang dari isi direktori sehingga tidak bisa
tertinggal lagi.

| Yang dijamin daftar induk | |
|---|---|
| Tiap berkas `docs/` muncul **tepat satu kali** | ✅ 263 = 263 |
| Nomor ganda | ✅ nihil |
| Berkas terdaftar tapi tidak ada | ✅ nihil |
| Berkas ada tapi tidak terdaftar | ✅ nihil |
| Nomor tak terpakai (`8–9`, `23–29`, `47–49`, `78–79`) | ✅ semuanya di batas antar-naskah, dijelaskan di Lampiran A |

### Aturan penomoran

- `01`–`99` dua digit, `100`–`275` tiga digit. Urutan abjad sebuah `ls`
  **tidak** sama dengan urutan nomor (`10`, `100`, `101`, `11`, `99`) — pakai
  daftar induk untuk urutan yang benar.
- Nama berkas **sengaja tidak dinomori ulang**: 34 GitHub Issue yang sudah
  terbit menaut berkas dua digit, dan penomoran ulang akan mematahkan tautan
  di isi issue tersebut.
- Tiap blok naskah menempati rentangnya sendiri, dengan celah di antaranya.

## Arsitektur sekilas

```
   ┌────────────────────────────────────────────────────────┐
   │  LAYER 1 · Supreme Orchestrator                        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 2 · Planner · Memory · Reasoning · Guardrail     │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 3 · Health · Habit · Fashion · Trend · Career    │
   │            Finance · Learning · Social                  │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 6 · AgentOS                                      │
   │  Registry · Scheduler · Queue · Workflow · Tools        │
   │  Memory Manager · Event Bus · Policy Engine            │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 7–9 · Ontology · Knowledge Graph · Memory        │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 10–14 · Tools · Workflow · Decision · PromptOps  │
   │                Evaluation                               │
   ├────────────────────────────────────────────────────────┤
   │  LAYER 17–20 · Trend · Marketplace · SDK · Simulation   │
   └────────────────────────────────────────────────────────┘
```

Naskah 4 menyusunnya ulang dari sudut lain:

```
                     HUMANVERSE XOS
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
    HUMAN CORE        AI RUNTIME        DATA CORE
        │                 │                 │
    Behavior          Orchestrator      PostgreSQL
    Goals             Agents            Vector DB
    Memory            Tools             Graph
    Context           Evaluation        Analytics
```

---

## 12 Modul manusia (naskah 1) vs 14 Agent (naskah 4)

```
NASKAH 1 — 12 modul               NASKAH 4 — Agent Registry §12
 1. Habit Intelligence            Health · Habit · Fashion · Grooming
 2. Lifestyle Intelligence        Fitness · Nutrition · Learning · Career
 3. Fashion AI                    Finance · Social · Travel · Productivity
 4. Grooming AI                   Entertainment · Research
 5. Fitness Intelligence
 6. Nutrition Intelligence        Baru      : Travel, Entertainment, Research
 7. Mental Wellness               Kembali   : Grooming, Nutrition, Productivity
 8. Productivity Intelligence     Masih nol : Mental Wellness, Lifestyle
 9. Learning Intelligence
10. Career Intelligence
11. Social Intelligence
12. Finance Behavior
```

> ⚠️ **Mental Wellness dan Lifestyle masih belum punya agent** di tiga naskah
> berturut-turut — dan *Journal* justru masuk V0. Lihat butir **A-20** dan
> **C-3**.

---

## Tumpukan teknologi

| Lapisan | Teknologi |
|---|---|
| Aplikasi | Flutter (mobile & web) · desktop & admin-dashboard **belum ditetapkan** |
| Backend | FastAPI · 12 microservice |
| AgentOS | Registry · Scheduler · Task Queue · Workflow · Tool Registry · Memory Manager · Event Bus · Policy Engine |
| AI | LangGraph · MCP · Tool Calling · **Model Router** (small/medium/large) |
| Data | **PostgreSQL · Qdrant · Neo4j · Redis** — naskah 5 membuang ClickHouse & Kafka |
| Event | Event Bus; antrean di **Redis** (Kafka baru bila skalanya menuntut) |
| Infra | **V0: Docker Compose** → Cloud VM → Kubernetes · ArgoCD · Terraform · Vault |
| Observability | OpenTelemetry · Prometheus · Grafana · Loki · Tempo · Sentry · **Agent Health** |
| Keamanan | OAuth · RBAC · Vault · AES-256 · TLS · Immutable Log · Permission Engine · Risk Engine |
| Privasi | Privacy Center · Personal Data Vault · On-device AI (V5) · Federated ML (V5) |
| SDK | Python · TypeScript · Flutter · Kotlin · Swift — **ditunda ke V6** |

---

## Tangga versi (naskah 4)

```
  V0  Foundation            ── auth, profile, goals, habits, mood, journal,
   │                           AI coach, memory, dashboard · 4–6 minggu
  V1  Behavior Intelligence ── event, analytics, pattern, prediksi, weekly review
   │
  V2  Lifestyle AI          ── fashion, wardrobe, trend, grooming, fitness, nutrisi
   │
  V3  Multi-Agent Platform  ── registry, SDK, MCP, tool registry, evaluation
   │
  V4  Digital Twin          ── human state, model perilaku, simulasi, decision lab
   │
  V5  HumanOS               ── voice, vision, wearable, on-device AI, privasi lanjut
   │
  V6  HumanVerse Ecosystem  ── developer SDK, marketplace, enterprise API
```

---

## Prinsip penutup pemilik

> **Jangan membuat HumanVerse menjadi mesin yang menilai apakah seseorang
> "manusia yang baik" atau "manusia yang buruk".**
>
> ## Manusia tetap menjadi pusat sistem.
