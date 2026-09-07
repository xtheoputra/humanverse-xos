# 229 — §16.5–§16.8 Humanoid Intelligence, Locomotion, Motion Planning & Manipulation

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.5 — Humanoid Intelligence

Kemampuan: **berjalan · mengambil objek · membuka pintu · membawa barang ·
mengikuti manusia · memahami gesture.**

```
Human Goal → World Model → Motion Planner → Joint Controller → Execution
```

> ⚠️ Angka lepas `5` di bagian ini. Lihat **G-16** / [#113](../../issues/113).

---

> 🛑 **`membuka pintu` mengubah seluruh model keamanan berbasis ruangan menjadi
> saran.**
>
> §15.23 memberi policy per ruangan (`bedroom: camera:false`); §16.19 memberinya
> bentuk yang lebih kuat (`child_room: restricted:true`). Keduanya berdiri di
> atas satu asumsi diam-diam: **batas ruangan adalah batas nyata.**
>
> Sebuah humanoid yang bisa membuka pintu meniadakan asumsi itu secara fisik —
> sebagaimana `through-wall sensing` (§15.4) meniadakannya secara sinyal
> (**C-22** / [#102](../../issues/102)). Dua fase berturut-turut memperkenalkan
> kemampuan yang menembus batas yang fase itu sendiri pakai sebagai pengaman.
>
> Yang perlu ditulis satu kalimat, dan bentuknya sudah ada di §16.19:
> **`restricted: true` berarti robot tidak masuk, bukan robot tidak diizinkan
> masuk** — perbedaannya adalah antara aturan di perangkat lunak dan penolakan
> di pengendali gerak, dan hanya yang kedua yang bertahan ketika perangkat
> lunaknya salah.

> ⚠️ **`mengikuti manusia` adalah kemampuan yang paling mudah salah dipakai.**
> Ia berguna (membawakan belanjaan) dan menakutkan (mesin yang mengikuti orang
> di rumahnya sendiri) dengan kode yang persis sama. Yang membedakan cuma
> **siapa yang memulai dan siapa yang bisa menghentikan** — dan §16.20 memberi
> `Emergency Stop`, tetapi tidak ada bagian yang menyatakan bahwa orang yang
> **diikuti** berhak menghentikannya, terutama kalau ia bukan pemilik akun
> (**A-31** / [#105](../../issues/105)).

---

## §16.6 — Locomotion Engine

| Robot | Locomotion |
|---|---|
| Humanoid | Biped |
| Dog Robot | Quadruped |
| Mobile Robot | Wheels |
| Drone | Flight |
| Robot Arm | Fixed |

> Planner harus **memilih model yang sesuai.**

---

> ⭐ **Menjadikan lokomosi sebagai properti yang dipilih planner, bukan sebagai
> cabang kode, adalah yang membuat abstraksi §16.3 bertahan.** Tanpa tabel ini,
> `robot.move_to()` akan berarti hal yang berbeda untuk tiap tubuh dan
> abstraksinya bocor pada pemakaian pertama.

> ⚠️ **`Fixed` untuk Robot Arm berarti `move_to()` tidak punya arti yang sama
> untuknya** — lengan tidak berpindah, ia menjangkau. Dan `Flight` berarti drone
> punya sumbu ketiga yang tidak dimiliki empat lainnya, plus **kegagalan yang
> tidak bisa berhenti di tempat**: robot beroda yang mati berhenti; drone yang
> mati jatuh. §16.20 `Emergency Stop` karena itu **tidak bisa berarti hal yang
> sama untuk kelimanya**, dan naskah tidak menyebutnya.

---

## §16.7 — Motion Planning Engine

> Motion Planning menjadi **salah satu komponen terbesar.**

```
Target → Obstacle Map → Trajectory → Collision Check → Optimization
→ Execution
```

Teknologi yang cocok: **MoveIt · OMPL · RRT\* · CHOMP · TrajOpt**

---

> ⭐⭐⭐ **Naskah KEDUA berturut-turut yang menyebut pustaka yang sudah ada
> alih-alih merancang komponen baru — dan kali ini di tiga tempat sekaligus.**
>
> §15.6 menyebut lima pustaka SLAM; naskah ini menyebut lima pustaka motion
> planning (§16.7), empat simulator (§16.26), dan **ROS2** sebagai lapisan
> kompatibilitas (§16.22) dengan kalimat *"HumanVerse tidak menggantikan ROS"*.
>
> Ini kebiasaan yang layak dicatat sebagai keberhasilan tersendiri: dua puluh
> naskah pertama nyaris seluruhnya merancang sendiri, dan dua naskah terakhir
> berhenti melakukannya persis di dua bidang yang paling matang di luar sana.
> Untuk fase yang punya risiko fisik, memakai pustaka yang sudah diuji ribuan
> orang **juga keputusan keselamatan**, bukan hanya penghematan.

> ⚠️ **`Optimization` sesudah `Collision Check` adalah urutan yang berbahaya
> kalau dibaca harfiah.** Lintasan yang sudah lulus pemeriksaan tabrakan lalu
> dioptimalkan (dipendekkan, dipercepat, dihaluskan) **berubah** — dan
> perubahannya bisa membawanya kembali menyentuh rintangan.
>
> Urutan yang benar dan lazim: optimasi lebih dulu, atau **pemeriksaan tabrakan
> diulang setelah optimasi**. Ini bukan soal gaya penulisan: ia satu-satunya
> tempat di naskah ini di mana urutan langkah menentukan apakah pengamannya
> bekerja.

---

## §16.8 — Manipulation Engine

Robot harus memahami: **grasp point · force · orientation · friction · object
geometry.**

```
Reach → Align → Grasp → Lift → Carry → Release
```

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16**.

---

> ⭐⭐ **`force` dan `friction` di daftar yang harus dipahami robot menunjukkan
> naskah ini tahu bahwa memegang benda adalah soal fisika, bukan soal
> koordinat.** Itu pembedaan yang sering dilewatkan, dan ia yang membuat §16.23
> (*"Handle slippery → adjust force"*) masuk akal.

> 🛑 **Tetapi `force` tidak punya batas atas di mana pun di naskah ini — dan itu
> satu-satunya angka yang benar-benar menentukan apakah seseorang terluka.**
>
> Enam keadaan `Reach → … → Release` menggambarkan **urutan**, bukan **batas**.
> Robot yang menggenggam terlalu kuat memecahkan gelas; yang menggenggam jari
> seseorang dengan gaya yang sama melukainya. Standar robotika kolaboratif nyata
> menyatakan batas ini dalam newton dan diuji per bagian tubuh — dan naskah ini,
> yang menyebut lima pustaka planning dan empat simulator, tidak menyebut satu
> pun angka gaya.
>
> Ini bentuk paling tajam dari **E-112** (*Definition of Done tanpa angka*):
> §16.35 memberi *"memanipulasi objek"* sebagai kriteria selesai, dan kriteria
> itu terpenuhi oleh robot yang aman maupun yang berbahaya. Lihat **A-32** /
> [#112](../../issues/112).

> ⚠️ **Tidak ada keadaan untuk GAGAL.** Enam keadaan semuanya jalur sukses:
> benda yang terlepas saat `Carry`, genggaman yang meleset saat `Grasp`, dan
> benda yang lebih berat dari perkiraan tidak punya tempat. Bandingkan §16.20
> yang punya `WARNING → STOP → RECOVERY` — mesin keadaan keselamatan punya jalur
> gagal; mesin keadaan manipulasi tidak. Ini pola **G-14** (*didaftarkan
> lengkap, jalur gagalnya jatuh*) pada benda fisik.
