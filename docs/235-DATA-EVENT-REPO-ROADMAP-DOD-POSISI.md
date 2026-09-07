# 235 — §16.30–§16.35 Data Model, Event Model, Repository, Integrasi, Roadmap, DoD & Posisi

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.30–§16.31 — Data Model & Event Model

```
robots · robot_states · robot_batteries · robot_tasks
joints · actuators · grippers
missions · trajectories · navigation_paths
iot_devices · iot_events
drone_missions
robot_skills · robot_memories
emergency_events · safety_zones
```

Event baru:

```
RobotStarted · RobotStopped · RobotMoved · RobotArrived
ObjectGrasped · ObjectReleased
ObstacleDetected · HumanDetected
EmergencyStop · RecoveryStarted
BatteryLow
MissionCompleted · MissionFailed
```

---

> ⭐⭐⭐ **`emergency_events` dan `safety_zones` punya TABEL — dan itu perbaikan
> nyata atas dua naskah sebelumnya.**
>
> Butir **G-14** mencatat pola *"didaftarkan lengkap, diskemakan sebagian"* di
> naskah 18: `Attention Budget` dan `Autonomy Contract` sama-sama disebut
> *"sangat penting"* dan sama-sama **tanpa tabel**. Butir **C-23** mencatat hal
> yang sama untuk policy ruangan naskah 19. Di sini keselamatan akhirnya punya
> tempat menyimpan: zona tersimpan, dan setiap penghentian darurat
> meninggalkan baris.

> ⭐⭐ **`MissionFailed` berdampingan dengan `MissionCompleted`, dan
> `RecoveryStarted` dengan `EmergencyStop`.** Naskah 18 hanya melahirkan **tiga**
> event dari tujuh tindakan watchdog dan **tidak punya `AgentRestored`**
> (**G-14**); di sini jalur gagal dan jalur pulih keduanya punya event sejak
> awal. Jejak audit yang hanya merekam keberhasilan tidak bisa menjawab apa pun
> setelah kecelakaan.

> 🛑 **`trajectories` mewarisi B-31 dalam bentuk yang lebih berat.** Sebuah
> lintasan bukan satu baris melainkan **deret posisi sendi terhadap waktu** —
> untuk lengan enam sendi pada 100–1000 Hz, satu gerakan sepuluh detik saja
> sudah puluhan ribu sampel. `joints` dan `actuators` sebagai tabel menyiratkan
> hal yang sama.
>
> Butir **B-31** ([#107](../../issues/107)) sudah menetapkan bentuk jawabannya
> untuk `wifi_csi` dan `point_clouds`: **yang mentah tidak meninggalkan
> perangkat; yang disimpan adalah keluarannya**, dengan retensi jam bukan tahun.
> Untuk robot ada satu pengecualian yang harus ditulis: **lintasan di sekitar
> `emergency_events` disimpan penuh** — itu satu-satunya data yang bisa
> menjelaskan sebuah kecelakaan, dan §14.29 sudah menetapkan prinsipnya
> (*"tidak langsung dihapus, ini penting untuk audit"*).

> 🛑 **`HumanDetected` adalah event tentang orang yang belum tentu punya akun —
> sama seperti `PersonEntered`/`PersonExited` §15.28.** **C-10**
> ([#40](../../issues/40)) mengusulkan `bystander` sejak naskah 7; dua naskah
> berturut-turut kini menulis event yang **tidak bisa diberi `user_id`**. Untuk
> robot, barisnya juga menjadi bukti hukum kalau terjadi cedera — jadi ia tidak
> bisa sekadar tidak disimpan. Lihat **C-24** / [#114](../../issues/114).

> ⚠️ **PascalCase lagi — pelanggaran [#38](../../issues/38) yang KETUJUH
> berturut-turut** (E-70 · E-88 · E-98 · E-116 · naskah 18 · naskah 19 · di
> sini). Lihat **E-132**.

> ⚠️ **`BatteryLow` ada sebagai event, tetapi tidak ada di daftar pemicu
> darurat §16.20** — padahal lengan yang kehabisan daya saat mengangkat
> melepaskan bebannya. Event ada, tindakannya tidak.

---

## §16.32 — Repository Structure

```
robotics/
├── runtime/      ├── ros/          ├── locomotion/   ├── manipulation/
├── navigation/   ├── obstacle/     ├── fleet/        ├── smart-home/
├── iot/          ├── drone/        ├── edge/         ├── simulation/
├── safety/       ├── skills/       ├── sdk/          └── testing/
```

---

> 🛑 **Ini pohon KEDUA untuk hal yang sama di dalam satu naskah — §16.1 sudah
> memberi `robotics-platform/` dengan isi yang berbeda.**
>
> | | §16.1 `robotics-platform/` | §16.32 `robotics/` |
> |---|---|---|
> | jumlah | 13 | 16 |
> | **hanya di §16.1** | `embodiment/` · `perception/` · `planning/` · `drivers/` | — |
> | **hanya di §16.32** | — | `obstacle/` · `fleet/` · `smart-home/` · `iot/` · `drone/` · `skills/` · `testing/` |
>
> Empat yang hilang bukan yang kecil: **`embodiment/`** (§16.2 menyebutnya *inti
> Phase 16*), **`planning/`** (§16.7 *salah satu komponen terbesar*),
> **`perception/`** (dasar §16.9–§16.11), dan **`drivers/`** — satu-satunya
> tempat kode khusus perangkat keras bisa hidup, dan karenanya satu-satunya yang
> membuat prinsip *"robot adalah hardware, HumanVerse adalah intelligence
> layer"* (§16.1) bisa ditegakkan alih-alih diniatkan.
>
> Ini pengulangan **E-111** persis (naskah 17: dua pohon `human-os/`, tiga
> direktori hilang tanpa penampung). Lihat **E-129** /
> [#109](../../issues/109).

> 🛑 **Dan `safety/` di dalamnya menjadikan pohon keamanan KELIMA.** Sudah ada
> `security/` (Fase 8) · `agent-security/` (Fase 14) · `spatial-os/safety/` dan
> `spatial-os/privacy/` (Fase 15) — **E-127** mencatat empat sudah membuat
> aturan impor **§8.42** tidak punya satu sisi. Lima menjadikannya tidak bisa
> dinyatakan sama sekali.
>
> ⭐ Dan pohon tingkat-atas ini juga menggerus **H-10** untuk **keenam** kalinya
> — delapan naskah berturut-turut menyentuh struktur repo
> ([#55](../../issues/55)).

> ⭐ **`testing/` sebagai direktori tingkat pertama** adalah satu-satunya di
> seluruh repo yang memberinya tempat sendiri, dan untuk fase ini itu tepat:
> §16.26 menjadikan uji sebagai gerbang menuju perangkat keras, bukan
> pelengkap.

---

## §16.33 — Integrasi dengan HumanVerse

> 🛑 **BAGIAN INI KOSONG DI NASKAH.** Judulnya ada; isinya tidak — tidak ada
> diagram, tidak ada daftar, tidak ada kalimat.
>
> **Sengaja tidak ditambal.** Lihat **G-16** / [#113](../../issues/113).
>
> Ini **naskah kedua berturut-turut** yang kehilangan bagian integrasinya:
> §15.1 *"Arsitektur Besar SpatialOS"* juga kosong. Dua fase yang seluruh
> nilainya terletak pada **bagaimana ia menyambung ke yang sudah ada**, dan
> keduanya kehilangan persis bagian yang menjelaskan sambungannya.
>
> Yang hilang di sini khususnya mahal karena Phase 16 adalah fase pertama yang
> **memakai keluaran fase lain sebagai masukan langsung**: §16.9 mengambil SLAM,
> Scene Graph, dan AetherScan dari Phase 15; §16.23 menulis ke Procedural Memory
> dari Phase 9; §16.13 memakai `Home Policy`; §16.4 memakai Digital Twin.
> Empat sambungan yang nyata, dan tidak ada satu bagian pun yang menyatakan
> arah, batas, maupun gerbangnya.

---

## §16.34 — Roadmap Implementasi

| Milestone | Fokus | | Milestone | Fokus |
|---|---|---|---|---|
| **R16.1** | Robotics Runtime | | **R16.6** | Smart Home |
| **R16.2** | Motion Planning | | **R16.7** | Drone |
| **R16.3** | Navigation | | **R16.8** | Fleet Management |
| **R16.4** | Manipulation | | **R16.9** | Simulation |
| **R16.5** | Humanoid | | **R16.10** | Safety Kernel |

---

> 🛑🛑 **`R16.10 Safety Kernel` ADA DI URUTAN TERAKHIR — sesudah humanoid,
> drone, manipulasi, dan armada.**
>
> Ini pengulangan **B-30** ([#99](../../issues/99)) yang lebih berat. Di naskah
> 18, federasi dibuka di `A14.1` dan Security Mesh dipasang di `A14.7` — pintu
> terbuka enam langkah sebelum penjaganya. Di sini yang dibangun lebih dulu
> bukan pintu melainkan **mesin yang bergerak di dekat orang**, dan penjaganya
> dijadwalkan **sesudah semuanya**.
>
> Naskah ini sendiri menyebut Safety Kernel *"komponen paling kritis"* (§16.18).
> Sebuah komponen paling kritis yang dijadwalkan terakhir akan lahir sebagai
> lapisan yang ditempelkan pada sistem yang sudah bekerja tanpanya — dan
> pengaman yang ditempelkan belakangan adalah pengaman yang bisa dilepas.
>
> ⭐ `R16.9 Simulation` juga berada **sesudah** lima milestone yang menggerakkan
> robot, padahal §16.26 menetapkan `Code → Simulation → Safety Test → Hardware`
> sebagai urutan wajib. Dua milestone yang menjadi prasyarat semua yang lain
> justru dijadwalkan paling belakang.
>
> Urutan yang lebih aman memakai bahan yang sama dan tidak menunda apa pun yang
> berguna: **`Safety Kernel` dan `Simulation` menjadi R16.1–R16.2**, lalu
> Runtime, Navigation, Manipulation; **Humanoid dan Drone paling akhir** karena
> keduanya paling mungkin melukai. Lihat **E-130** / [#111](../../issues/111).

> ⚠️ **Huruf milestone berganti lagi: `S15.x` → `R16.x`.** Riwayatnya kini
> `S8.x` · `C1–C10` · `M10.x` · `T12.x` · `A14.x`+`M14.x` · `S15.x` · `R16.x` —
> **enam huruf untuk dua benda**. ⭐ Tapi tujuh dari delapan membawa nomor
> fasenya, jadi arahnya tetap membaik; tinggal memilih satu huruf. Lihat
> **E-131**.

---

## §16.35 — Definition of Done

> Phase 16 selesai ketika HumanVerse mampu: mengendalikan berbagai jenis robot ·
> navigasi aman · memanipulasi objek · berinteraksi dengan manusia · mengelola
> smart home · mengelola IoT · mengendalikan drone · multi-robot coordination ·
> **menguji semua perilaku di simulasi sebelum deployment** · **menjalankan
> Safety Kernel dengan emergency stop dan policy berbasis zona.**

---

> ⭐⭐ **Dua kriteria terakhir adalah yang terbaik di daftar ini**, dan keduanya
> menyebut **mekanisme**, bukan kemampuan: *menguji di simulasi sebelum
> deployment* dan *menjalankan Safety Kernel*. Keduanya bisa diperiksa dengan
> melihat sistemnya, bukan dengan menilai hasilnya — dan naskah 18 mengakhiri
> daftarnya dengan cara yang sama (empat jaminan penutup §14.68).

> 🛑 **Tetapi sepuluh kriteria, NOL angka — dan ini kejadian KEEMPAT, di fase
> yang paling membutuhkannya.**
>
> **E-112** mencatat naskah 17 (21 kriteria, nol angka), §14.68 (31 kriteria,
> nol angka), §15.32 (10 kriteria, nol angka). Ketiganya bisa dibela dengan
> alasan bahwa isinya sulit diukur.
>
> Yang ini tidak bisa. *"Navigasi aman"* dan *"memanipulasi objek"* terpenuhi
> oleh robot yang aman **maupun** oleh robot yang berbahaya, dan yang
> membedakan keduanya adalah bilangan yang tidak ditulis di mana pun:
>
> | Besaran | Kenapa ia menentukan |
> |---|---|
> | **jarak henti** pada kecepatan penuh | menentukan apakah `Robot slows → Wait` §16.11 sempat bekerja |
> | **latensi reaksi** dari deteksi ke penghentian | `Emergency Stop` yang tiba 800 ms terlambat bukan emergency stop |
> | **batas gaya** genggaman dan tumbukan | satu-satunya besaran yang menentukan apakah seseorang terluka (§16.8) |
> | **personal space** minimum | §16.11 memakainya tanpa angka |
> | **kecepatan maksimum** per zona | §16.19 menulis `speed: slow` tanpa satuan |
>
> §15.12 sudah membuktikan naskah-naskah ini **bisa** memberi target berangka
> (UWB 10–30 cm, WiFi RTT 1–2 m). Untuk Phase 16, angka-angka itu bukan
> kelengkapan dokumen melainkan **definisi keselamatannya**. Lihat **A-32** /
> [#112](../../issues/112).

---

## Posisi HumanVerse Setelah Phase 16

> HumanVerse berkembang dari **AI digital** menjadi **Embodied Intelligence
> Platform.**

```
Human → HumanOS → SpatialOS → Digital Twin → Embodied Intelligence
→ Robot Platform → Physical World
```

> Fondasi ini menjadi prasyarat langsung untuk **Phase 17 — Human Health & Bio
> Intelligence**, karena Health Digital Twin akan menggabungkan data wearable,
> biometrik, gaya hidup, dan perilaku menjadi sistem kesehatan preventif yang
> terintegrasi dengan HumanOS.

---

> 🛑🛑 **Phase 17 diumumkan — dan ini naskah KEDUA BERTURUT-TURUT yang
> memperpanjang peta, sehingga pertanyaan #101 kini punya jawabannya sendiri.**
>
> Butir **E-123** ([#101](../../issues/101)) menanyakan tiga hal ketika naskah
> 19 mengumumkan Phase 16: ke mana perginya *Global Intelligence Platform*,
> petanya kini berapa fase, dan berapa lagi yang sudah direncanakan.
>
> Naskah 20 menjawab yang ketiga dengan perbuatan: **petanya terbuka-ujung.**
> Dua naskah berturut-turut masing-masing menambah satu fase di kalimat
> penutupnya, dan tidak satu pun menyebut §10.41 maupun menyatakan bahwa peta
> lama diganti.
>
> Konsekuensinya praktis dan bisa segera dipakai: **berhenti mencatat "peta
> bertahan" sebagai keberhasilan**, dan **beri versi pada peta fase** —
> `v1` (15 fase, §10.41) dan `v2` (terbuka-ujung, naskah 19–20) hidup
> berdampingan, tiap dokumen menyebut yang dipakainya, seperti `scoring_version`
> di DDL. Itu menghentikan penggerusan diam-diam tanpa membekukan rencananya.
> Lihat **E-128** / [#108](../../issues/108).

> ⚠️ **Dan Phase 17 yang diumumkan adalah fase paling sensitif dari semuanya.**
> *Health Digital Twin* menggabungkan **wearable, biometrik, gaya hidup, dan
> perilaku** — yaitu data Level 3–4 (§8.16) di keempat sumbernya sekaligus.
> Tiga butir sudah menunggu di sana sebelum naskahnya ditulis: **C-20**
> ([#85](../../issues/85), proyeksi kesehatan sebagai kelas data yang paling
> diinginkan pihak ketiga), **C-22** ([#102](../../issues/102), `breathing
> detection` sudah menjadikan tanda vital terukur tanpa perangkat), dan larangan
> §8.10 atas *insurance scoring*. ⭐ Kabar baiknya: ketiganya **sudah tercatat
> sebelum naskahnya datang**, jadi ia bisa dibaca dengan pertanyaan yang sudah
> siap.

> ⭐⭐ **Rantai posisinya sendiri konsisten**: `Human` tetap di puncak, sejalan
> dengan §14.36 (`Human ↑ Governance ↑ Agent Ecosystem`). ⚠️ Tapi seperti
> §15.32, **`GOVERNANCE MESH` dan `ACTION GATEWAY` kembali tidak muncul** —
> dua naskah berturut-turut menggambar jalur dari kecerdasan ke dunia fisik
> tanpa melewati keduanya, dan kali ini ujungnya bukan tampilan melainkan
> **`Physical World`**.
