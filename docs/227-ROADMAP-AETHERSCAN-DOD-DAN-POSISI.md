# 227 — §15.30–§15.32 Roadmap, Integrasi AetherScan, Definition of Done & Posisi HumanVerse

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.30 — Roadmap Implementasi

> Saya membagi Phase 15 menjadi **10 milestone besar**.

| Milestone | Fokus |
|---|---|
| **S15.1** | Sensor Fusion |
| **S15.2** | SLAM |
| **S15.3** | Spatial Mapping |
| **S15.4** | Indoor Positioning |
| **S15.5** | Spatial Memory |
| **S15.6** | Scene Graph |
| **S15.7** | XR Interaction |
| **S15.8** | AetherScan Integration |
| **S15.9** | Spatial Agents |
| **S15.10** | Collaborative XR |

---

> ⭐⭐ **Urutannya benar: fondasi geometri dulu, interaksi belakangan, ruang
> bersama paling akhir.** `S15.10 Collaborative XR` di ujung adalah kebalikan
> dari kesalahan yang **B-30** ([#99](../../issues/99)) catat di naskah 18, di
> mana federasi dibuka enam langkah sebelum penjaganya. Di sini hal yang paling
> membuka data ke orang lain justru dibangun terakhir.

> ⭐ **Awalan `S15.x` membawa nomor fasenya sendiri** — persis bentuk yang saya
> usulkan untuk mengakhiri lima skema penomoran yang bertabrakan. ⚠️ Tapi
> **hurufnya berganti lagi**: naskah 12 `S8.x` · naskah 13 `C1–C10` · naskah 14
> `M10.x` · naskah 16 `T12.x` · naskah 18 **`A14.x` (workstream) + `M14.x`
> (milestone)** · naskah 19 **`S15.x` (milestone)**.
>
> Jadi "milestone" ditulis `M14.x` di satu naskah dan `S15.x` di naskah
> berikutnya, sementara `S` sebelumnya berarti *sprint*. Empat huruf untuk dua
> benda. Lihat **E-125**.

> 🛑 **Sepuluh milestone, dan `safety/` maupun `privacy/` tidak ada satu pun di
> antaranya** — padahal §15.25 memberi keduanya direktori dan §15.22–§15.23
> memberi keduanya bagian tersendiri.
>
> Ini pola **G-14** yang baru saja tercatat di naskah 18 (*didaftarkan lengkap,
> diskemakan sebagian*), muncul pada roadmap: **dua puluh submodul di repo,
> sepuluh milestone, dan yang jatuh adalah keselamatan dan privasi.**
>
> Akibatnya bukan teoretis. `S15.8 AetherScan Integration` dijadwalkan sebagai
> milestone tersendiri, sementara policy ruangan yang membatasinya (**C-23** /
> [#104](../../issues/104)) tidak dijadwalkan sama sekali — jadi urutan bawaan
> yang dihasilkan daftar ini adalah **sensor yang menembus dinding dibangun
> sebelum sakelar yang mematikannya.**

---

## §15.31 — Integrasi dengan AetherScan

> Ini menurut saya akan menjadi salah satu **keunggulan unik HumanVerse**.

> ⚠️ Naskah menulis *"Arsitektur gabungan:"* lalu **tidak memberi
> arsitekturnya** — bagiannya berhenti di situ. Sengaja tidak ditambal; lihat
> **G-15** / [#103](../../issues/103).

Dengan integrasi ini HumanVerse dapat memakai kombinasi **WiFi sensing
(AetherScan) · kamera · LiDAR · UWB · IMU** untuk membangun **persistent 3D
Digital Twin** yang jauh lebih kuat dibanding mengandalkan satu sensor saja.

---

> ⭐ **Klaim "keunggulan unik" ini yang paling bisa dipertahankan di seluruh
> HumanVerse** — bukan karena WiFi sensing baru, melainkan karena
> **menggabungkannya dengan Digital Twin yang sudah ada** (Phase 12) dan dengan
> memori berlapis (Phase 9 & 14) adalah kombinasi yang tidak dimiliki produk
> sensing mana pun. Sebagian besar klaim keunggulan di naskah-naskah sebelumnya
> berupa cakupan; yang ini berupa **gabungan yang sudah dibangun**.

> 🛑 **Tetapi kata `persistent` adalah kata yang paling berat di kalimat itu, dan
> ia lewat tanpa dibahas.**
>
> *Persistent 3D Digital Twin* berarti peta rumah beserta isinya **disimpan
> terus-menerus**, bukan dihitung ulang saat dibutuhkan. Digabung dengan §15.10
> (`Sleeping`), §15.8 (*jalur yang sering dilalui*), dan §15.4 (*breathing
> detection*, *through-wall sensing*), yang tersimpan permanen bukan denah
> melainkan **rutinitas tubuh penghuninya, termasuk penghuni yang bukan
> pengguna**.
>
> Tiga butir yang sudah terbuka berlaku sekaligus dan tidak satu pun terjawab di
> sini: **C-9** ([#22](../../issues/22)) hak hapus · **C-10**
> ([#40](../../issues/40)) data orang lain · **C-18**
> ([#76](../../issues/76)) RF sensing menangkap orang yang tidak bisa
> menyadarinya. Ditambah yang baru: **C-22** ([#102](../../issues/102)) dan
> **C-23** ([#104](../../issues/104)).
>
> ⭐ Dan penawarnya sudah ada di naskah ini juga, di §15.29: *"edge melakukan
> processing sensitif."* Yang perlu ditulis adalah menyambungkan keduanya —
> **persistent berlaku untuk geometri ruangan, tidak untuk jejak manusia.**
> Perabot boleh diingat selamanya; orang tidak.

---

## §15.32 — Definition of Done

Phase 15 selesai ketika HumanVerse mampu:

```
✓ Memetakan ruang 3D                  ✓ Mengetahui posisi pengguna
✓ Mengingat lokasi objek              ✓ Menggabungkan berbagai sensor
✓ Menjalankan AetherScan              ✓ Menampilkan UI AR kontekstual
✓ Melakukan reasoning spasial         ✓ Mendukung gesture & eye tracking
✓ Menjalankan navigasi indoor         ✓ Menyinkronkan Spatial Digital Twin
                                         dengan HumanOS
```

---

> 🛑 **Sepuluh kriteria, NOL angka — dan naskah ini sendiri sudah membuktikan
> ia bisa memberi angka, dua puluh bagian sebelumnya.**
>
> §15.12 memberi lima target yang bisa diuji dengan meteran di lantai (UWB
> **10–30 cm**, WiFi RTT **1–2 m**). Di sini *"mengetahui posisi pengguna"*
> berdiri tanpa satu bilangan pun — dan ia kriteria yang sama.
>
> Ini **E-112** yang berulang untuk ketiga kalinya: naskah 17 (21 kriteria, nol
> angka) · §14.68 naskah 18 (31 kriteria, nol angka) · di sini. Bedanya, dua
> yang pertama bisa dibela dengan alasan bahwa isinya sulit diukur; fase ini
> **penuh dengan hal yang justru mudah diukur** — akurasi posisi, latensi
> render, kecepatan pemetaan ruangan, tingkat kesalahan pengenalan gesture.
> Naskahnya punya angkanya; DoD-nya tidak memakainya.

> 🛑 **Dan tidak ada satu pun kriteria tentang KESELAMATAN atau PRIVASI** —
> sementara §14.68 mengakhiri daftarnya dengan empat jaminan (*human governance
> · auditability · reversibility · kill/revoke*).
>
> Ini pola yang sama dengan §15.30: `safety/` dan `privacy/` punya direktori,
> punya bagian naskah, tetapi tidak punya milestone dan tidak punya kriteria
> selesai. Dalam fase yang memperkenalkan sensor tembus dinding, itu ketiadaan
> yang paling perlu diisi. Empat kriteria yang bisa langsung ditambahkan dan
> semuanya bisa diuji:
>
> - policy ruangan **menolak kemampuan yang tidak disebut** (**C-23**),
> - CSI dan point cloud **tidak pernah meninggalkan perangkat** (**B-31**),
> - rantai §15.22 **memuat `Risk` dan `Confirmation`** (**E-124**),
> - `people_tracks` punya **retensi dan jalur hapus** (**C-9** / **C-10**).

---

## Posisi HumanVerse Setelah Phase 15

> Arsitektur HumanVerse berubah dari **AI yang memahami kehidupan** menjadi
> **AI yang memahami kehidupan sekaligus ruang fisik tempat kehidupan itu
> berlangsung.**

```
Human → HumanOS → SpatialOS → Digital Twin → World Model
→ AetherScan → XR Universe
```

> Dan Phase 15 ini menjadi **fondasi langsung untuk Phase 16 — Robotics &
> Embodied Intelligence**, karena robot tidak bisa bergerak dengan aman tanpa
> **SpatialOS, Scene Graph, SLAM, dan World Model** yang sudah dibangun di fase
> ini.

---

> 🛑🛑🛑 **Dua kalimat penutup ini mematahkan H-20 — satu-satunya sumbu
> penomoran yang bertahan lima naskah berturut-turut.**
>
> Peta kanonik §10.41, yang direkam di [`175`](175-REPO-API-DB-ROADMAP-DOD.md),
> menetapkan **lima belas fase** dan menamai yang terakhir:
>
> | Fase | Isi menurut §10.41 | Yang benar-benar datang |
> |---|---|---|
> | 13 | HumanOS | ✅ naskah 17 |
> | 14 | Ecosystem & Marketplace | ✅ naskah 18 (memuat marketplace §14.15) |
> | **15** | **Global Intelligence Platform** | ❌ **Spatial Intelligence & XR Universe** |
> | — | *tidak ada* | ⚠️ **Phase 16 — Robotics & Embodied Intelligence** |
>
> Dua hal terjadi sekaligus, dan keduanya di kalimat penutup: **isi Phase 15
> diganti**, dan **petanya berhenti berjumlah lima belas**.
>
> Butir **F** di berkas audit mencatat lima kali berturut-turut bahwa peta 15
> fase bertahan — §10.41 · §11.64 · §12.31 · naskah 17 · §14.69. Itu **satu
> sumbu stabil di antara lima yang bertabrakan**, dan nilainya justru karena ia
> stabil.
>
> Ini bukan alasan untuk menolak Phase 15 sebagaimana ditulis: SpatialOS masuk
> akal, urutannya masuk akal, dan *Global Intelligence Platform* memang tidak
> pernah punya isi selain namanya. Yang dibutuhkan adalah **keputusan, bukan
> penyesuaian diam-diam** — karena peta yang bisa bertambah tanpa diumumkan
> berhenti menjadi rencana dan kembali menjadi daftar keinginan, dan itu persis
> keadaan yang **H-13**/[#72](../../issues/72) coba akhiri.
>
> Tiga pertanyaan yang harus dijawab pemilik: **ke mana perginya *Global
> Intelligence Platform*** (dibuang, digeser ke 17, atau ternyata bagian dari
> 14)? **Apakah petanya kini 16 fase, atau terbuka-ujung?** Dan **berapa fase
> lagi yang sudah direncanakan** — karena jawaban "belum tahu" pun berguna, ia
> mengubah cara membaca setiap "peta fase" di dokumen ini. Lihat **E-123** /
> [#101](../../issues/101).

> ⭐⭐ **Terlepas dari itu, kalimat tentang Phase 16 adalah alasan terbaik untuk
> membangun Phase 15 dengan benar — dan sebaiknya dibaca sebagai peringatan,
> bukan sebagai janji.**
>
> *"Robot tidak bisa bergerak dengan aman tanpa SpatialOS, Scene Graph, SLAM,
> dan World Model."* Kalimat itu benar, dan pembalikannya juga benar: **robot
> yang bergerak di atas SpatialOS yang salah akan salah dengan cara yang
> berbahaya.** Tiga hal di fase ini karena itu berhenti menjadi catatan
> kerapian dan menjadi prasyarat keselamatan:
>
> | Butir | Untuk AR | Untuk robot |
> |---|---|---|
> | §15.22 tanpa `Risk`/`Confirmation` (**E-124**) | widget menghalangi pandangan | benda bergerak tanpa gerbang |
> | `MOVING_TO` = prediksi diperlakukan sebagai ukuran (§15.11) | panah menunjuk salah | menghindar ke arah salah |
> | `Person` = `Object` (§15.5) | orang tercatat seperti sofa | orang **diperlakukan** seperti sofa |
>
> Ketiganya murah diperbaiki sekarang, dan mahal setelah ada perangkat keras.

> ⭐ **Rantai posisi akhirnya juga menyatakan sesuatu yang benar:** `Human`
> tetap di **paling atas**, sejalan dengan §14.36 (`Human ↑ Governance ↑ Agent
> Ecosystem`). ⚠️ Tapi **`GOVERNANCE MESH` dan `ACTION GATEWAY` hilang dari
> rantai ini**, padahal §14.69 menaruh keduanya sebagai lapisan wajib sebelum
> dunia luar. Rantai Phase 15 pergi langsung `SpatialOS → Digital Twin →
> AetherScan → XR Universe` tanpa melewati keduanya — konsisten dengan §15.22
> yang juga tidak memuat `Risk`. Lihat **E-124**.
