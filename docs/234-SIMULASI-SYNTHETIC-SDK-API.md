# 234 — §16.26–§16.29 Simulation-First Development, Synthetic Training, Robot SDK & API

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.26 — Simulation-First Development

> **Sebelum robot bergerak.**

```
Code → Simulation → Safety Test → Hardware
```

Tools: **NVIDIA Isaac Sim · Gazebo · Webots · MuJoCo**

> ⚠️ Angka lepas `7` di bagian ini. Lihat **G-16** / [#113](../../issues/113).

---

> ⭐⭐⭐ **Ini keputusan keselamatan terpenting di seluruh naskah, dan ia yang
> paling mudah ditegakkan CI dari semua yang pernah ditulis di repo ini.**
>
> `Code → Simulation → Safety Test → Hardware` adalah **urutan wajib**, dan
> urutan wajib bisa dijadikan gerbang: tidak ada artefak yang boleh diturunkan
> ke perangkat keras tanpa jejak lulus simulasi dan uji keselamatan. Bandingkan
> tiga batas keras yang sudah tercatat perlu ditegakkan CI (*agent tidak boleh
> bypass gateway* §11.14 · *kode agent tidak boleh impor `security/`* §8.42 ·
> *simulation tidak boleh mengubah data dunia nyata* §12.16) — yang ini
> **keempat**, dan satu-satunya yang mencegah cedera fisik.
>
> ⭐ `Safety Test` sebagai langkah **terpisah** dari `Simulation` juga benar:
> berjalan di simulator berarti kodenya jalan; lulus uji keselamatan berarti
> kodenya jalan **dengan benar ketika keadaan buruk**. Dua pertanyaan berbeda,
> dan hanya yang kedua menjawab §16.20.

> ⚠️ **Batas §12.16 perlu dibalik arahnya di sini.** Aturan lama: *simulasi
> tidak boleh mengubah data dunia nyata.* Aturan yang dibutuhkan Phase 16:
> **simulasi tidak boleh DILEWATI** — dan keduanya perlu ditulis, karena yang
> pertama menjaga data sementara yang kedua menjaga orang.

> ⚠️ **Empat simulator, dan mereka tidak setara untuk `Safety Test`.** MuJoCo
> kuat pada dinamika kontak (yang menentukan `force` §16.8); Isaac Sim kuat pada
> persepsi sintetis (§16.27); Gazebo dan Webots pada integrasi ROS. Memilih satu
> untuk semua akan lemah di salah satu sisi, dan **sisi yang paling penting di
> sini adalah kontak**, karena di situlah orang terluka.

---

## §16.27 — Synthetic Training

> Robot belajar di simulasi: ribuan variasi **ruangan · pencahayaan · posisi
> objek · obstacle**. Ini **mempercepat training.**

---

> ⭐⭐ **Data sintetis menyelesaikan masalah yang tidak bisa diselesaikan cara
> lain: mengumpulkan ribuan variasi ruangan nyata berarti memfilmkan ribuan
> rumah orang.** Butir **C-17** ([#75](../../issues/75)) dan **C-23**
> ([#104](../../issues/104)) keduanya berakar pada pengumpulan data di dalam
> rumah; melatih di simulator memindahkan sebagian besar kebutuhan itu keluar
> dari rumah orang sama sekali.
>
> Ia juga penawar untuk **B-22** (*purpose limitation bisa mengunci Research
> Lab*): data sintetis tidak punya `purpose` yang harus disetujui siapa pun.

> 🛑 **Tetapi empat variasi yang disebut semuanya soal PENAMPILAN, bukan soal
> PERILAKU — dan yang berbahaya ada di kelompok kedua.**
>
> *Ruangan, pencahayaan, posisi objek, obstacle* melatih robot mengenali dunia.
> Yang tidak disebut: **manusia yang bergerak tak terduga**, anak yang berlari,
> orang yang jatuh, hewan, lantai licin, dan benda yang lebih berat dari
> perkiraan. §16.10 mendaftarkan `human`, `pet`, dan `dynamic` sebagai jenis
> rintangan; §16.27 tidak melatih satupun.
>
> Konsekuensinya langsung: **`Safety Test` §16.26 hanya bisa menguji apa yang
> disimulasikan.** Sebuah rangkaian uji tanpa manusia yang berperilaku buruk
> akan meluluskan robot yang berbahaya, dan meluluskannya dengan meyakinkan.
> Bertaut **A-32** / [#112](../../issues/112).

> ⚠️ **Jurang simulasi-ke-nyata tidak disebut sama sekali.** Perilaku yang
> sempurna di simulator gagal di dunia karena gesekan, keterlambatan sensor, dan
> lentur mekanis — dan §16.8 justru menyebut `friction` sebagai hal yang harus
> dipahami robot. Menyebutnya sekali sudah cukup untuk mencegah *"lulus
> simulasi"* dibaca sebagai *"aman"*.

---

## §16.28 — Robot SDK

```
hv.robot.move(...)     hv.robot.grasp(...)
hv.robot.navigate(...) hv.robot.observe(...)
hv.robot.stop(...)
```

---

> ⭐ **`hv.robot.stop(...)` ada di sini**, meskipun tidak ada di antarmuka
> §16.3. Untuk SDK yang dipakai orang lain, itu metode yang paling wajib ada —
> tapi ketidakcocokan kedua daftar perlu diselesaikan, dan yang benar adalah
> **§16.3 yang ditambahi**, bukan sebaliknya.

> 🛑🛑 **Lima panggilan yang MENGGERAKKAN MESIN FISIK, dibuka ke pengembang
> pihak ketiga, tanpa satu pun `risk_level`, scope izin, atau penanda
> persetujuan.**
>
> Ini kejadian **ketiga** dari pola yang sama, dan tiap kali taruhannya naik:
>
> | | Yang dibuka | Kalau disalahgunakan |
> |---|---|---|
> | **G-11** — 13 tool persepsi §10.26 | kamera, mikrofon | data pribadi terbaca |
> | §15.24 Spatial SDK | denah rumah, posisi pengguna | tempat tinggal terpetakan |
> | **§16.28 Robot SDK** | **gerak, genggaman, navigasi** | **orang terluka** |
>
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) sudah mewajibkan setiap tool
> punya `risk_level` dan `side_effects`, dan aturan 6-nya melarang scope
> tertentu untuk agent `third_party`. Usul yang sudah dua kali dicatat berlaku
> lagi, dan sekarang mendesak: **tambahkan `robot`, `motion`, `manipulation`,
> dan `iot.lock` ke daftar scope terlarang untuk pihak ketiga**, dan
> `hv.robot.grasp()` tidak pernah dipanggil tanpa melewati Safety Kernel.
>
> ⚠️ **Dan `stop()` sebagai panggilan SDK biasa tidak cukup**: penghentian
> darurat tidak boleh mengantre di belakang panggilan lain dari SDK yang sama.
> §16.20 menjadikannya prioritas tertinggi; §16.28 menjadikannya baris kelima.

---

## §16.29 — API

```
POST /v1/robot/tasks    POST /v1/robot/move    POST /v1/robot/grasp
GET  /v1/robot/state    GET  /v1/robot/battery
POST /v1/robot/emergency-stop
GET  /v1/robot/fleet
```

---

> ⭐⭐ **`POST /v1/robot/emergency-stop` sebagai endpoint tersendiri adalah
> perbaikan nyata atas §15.26**, yang memberi `POST /v1/aetherscan/start` tanpa
> pasangan yang menghentikannya. Di sini penghentian punya alamat.

> ⚠️ **Tapi endpoint darurat lewat HTTP mewarisi seluruh kelemahan HTTP**:
> antrean, batas waktu, dan **hilang ketika jaringan putus** — yang justru
> pemicu darurat nomor empat di §16.20. Ini memperkuat §16.21: **penghentian
> darurat yang sesungguhnya ada di edge**, dan endpoint ini adalah kenyamanan,
> bukan pengaman. Sebaiknya ditulis begitu, supaya tidak ada yang mengandalkannya.

> ⚠️ **Tidak ada endpoint untuk `safety_zones`**, padahal §16.19 menjadikannya
> satu-satunya permukaan tempat pengguna membatasi robot — dan §16.30 memberinya
> tabel. Ini pengulangan persis dari §15.26 yang juga tidak punya endpoint untuk
> policy ruangan: **dua fase berturut-turut memberi banyak endpoint untuk
> bertindak dan nol untuk membatasi.**

> ⚠️ **`/v1/…` lagi, bukan `/api/v1`** — separuh kedua [#38](../../issues/38),
> naskah **ketujuh** berturut-turut. Lihat **E-132**.
