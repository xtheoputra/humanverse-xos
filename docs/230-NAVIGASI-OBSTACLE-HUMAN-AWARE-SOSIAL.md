# 230 — §16.9–§16.12 Navigation, Obstacle Intelligence, Human-Aware Navigation & Social Robotics

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.9 — Navigation Engine

> Navigation menggunakan **hasil Phase 15.**

Input: **SLAM · Scene Graph · AetherScan · LiDAR · Camera**

```
Current Position → Goal Position → Path Planning → Obstacle Avoidance
→ Movement
```

---

> ⭐⭐⭐ **Ini pertama kalinya sebuah fase memakai keluaran fase sebelumnya
> secara langsung dan disebutkan namanya, bukan mengulanginya dengan nama
> baru.**
>
> Pola yang berulang di repo ini adalah setiap naskah membangun ulang daftar
> yang sudah ada — agent 5×, manifest 6×, Human State 4×, Digital Twin 4×, pohon
> repo tujuh naskah berturut-turut. Di sini `SLAM`, `Scene Graph`, dan
> `AetherScan` dipakai apa adanya dari Phase 15. Itu perilaku yang layak dicatat
> sebagai keberhasilan, dan ia juga yang membuat kalimat *"Phase 15 adalah
> fondasi langsung untuk Phase 16"* bukan sekadar klaim.

> 🛑 **Tetapi mewarisi Phase 15 berarti mewarisi lubangnya — dan dua di antaranya
> kini berpindah dari layar ke roda.**
>
> | Lubang Phase 15 | Akibatnya untuk AR | Akibatnya untuk robot |
> |---|---|---|
> | `MOVING_TO` = prediksi diperlakukan sebagai pengukuran (§15.11) | panah menunjuk salah | **menghindar ke arah yang salah** |
> | `Person` di pohon objek yang sama dengan `Sofa` (§15.5) | orang tercatat seperti sofa | orang **diperlakukan** seperti sofa |
>
> Keduanya sudah tercatat di **E-124** ([#106](../../issues/106)) sebagai
> perkiraan; naskah ini menjadikannya nyata, karena `Scene Graph` adalah masukan
> `Obstacle Avoidance`. ⭐ Yang menyelamatkan sebagian: §16.10 **memisahkan
> `human` sebagai jenis rintangan tersendiri** — lihat di bawah.

---

## §16.10 — Obstacle Intelligence

Jenis obstacle: **static · dynamic · human · pet · furniture · temporary.**

> **Prioritas keselamatan tertinggi diberikan pada manusia.**

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16** / [#113](../../issues/113).

---

> ⭐⭐⭐ **Satu kalimat itu memperbaiki lubang terbesar yang Phase 15
> tinggalkan.**
>
> §15.5 menaruh `Person` di pohon objek yang sama dengan `Sofa`, `Table`, dan
> `Lamp`, dan saya catat bahwa untuk robot itu berarti orang **diperlakukan**
> seperti sofa. §16.10 menolaknya secara eksplisit: `human` adalah jenis
> tersendiri, dan ia mendapat **prioritas keselamatan tertinggi**.
>
> Ini persis bentuk perbaikan yang paling berguna — bukan penjelasan, melainkan
> **peringkat**. Sebuah perencana gerak yang harus memilih antara menyerempet
> kursi dan menyerempet orang punya jawaban yang tertulis.

> ⚠️ **Tapi `pet` berdiri di daftar tanpa peringkat.** Hewan bergerak tak
> terduga seperti manusia, berukuran seperti perabot, dan tidak bisa diminta
> minggir. Ia satu-satunya jenis di daftar yang perlakuannya benar-benar tidak
> bisa disimpulkan dari kelima lainnya — dan di rumah, ia yang paling sering
> berada di lantai tepat di jalur robot.
>
> ⚠️ Dan **`temporary`** tidak punya definisi: tas yang ditaruh sebentar, atau
> rintangan yang terdeteksi lalu hilang? Keduanya menuntut perilaku berlawanan —
> yang pertama dihindari dan diingat, yang kedua **tidak boleh diingat** supaya
> peta tidak terisi hantu.

---

## §16.11 — Human-Aware Navigation

> Robot **tidak hanya menghindari tabrakan.** Ia memahami: **personal space ·
> walking direction · waiting behavior · social navigation.**

```
Person walking → Predict trajectory → Robot slows → Wait → Continue
```

---

> ⭐⭐⭐ **`Robot slows → Wait` adalah keputusan desain terbaik di naskah ini,
> dan alasannya bukan kesopanan melainkan keselamatan.**
>
> Rantai ini menetapkan bahwa ketika sistem **tidak yakin** apa yang akan
> dilakukan seseorang, jawabannya adalah **melambat dan berhenti** — bukan
> menghitung jalur pintas yang lebih cerdas. Itu sikap yang sama dengan
> *"tidak boleh mengarang data"* §14.35 (degradasi berakhir di **diam**, bukan
> di karangan), dipindahkan ke gerak.
>
> Ia juga satu-satunya tempat di naskah ini di mana **`Predict trajectory` yang
> salah tidak berbahaya** — karena tindakan yang menyusulnya adalah berhenti.
> Bandingkan §16.9, di mana prediksi yang salah berarti menghindar ke arah yang
> salah. Perbedaannya cuma satu: **prediksi dipakai untuk berhenti, bukan untuk
> memilih jalur.** Itu aturan yang layak ditulis sebagai aturan, bukan
> dibiarkan sebagai contoh.

> ⚠️ **`personal space` tidak punya angka**, dan ia salah satu dari sedikit
> besaran di fase ini yang benar-benar berbeda antarbudaya dan antarorang.
> Sebuah robot yang memakai satu angka untuk semua orang akan terasa mengancam
> bagi sebagian dan lamban bagi sebagian lain. Bagian dari **A-32** /
> [#112](../../issues/112).

---

## §16.12 — Social Robotics Layer

Interaksi: **eye contact · voice · gesture · facial expression · proxemics.**

> Tetapi ekspresi robot harus tetap **transparan, bukan berpura-pura memiliki
> emosi manusia.**

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16**.

---

> ⭐⭐⭐ **Kalimat itu adalah pengaman yang ditulis pemilik sendiri, dan ia yang
> KEENAM berturut-turut** (§8.46 · §11.63 · §12 · §13.32 · §14.64 · §15.10 ·
> §15.16 · di sini). Kebiasaan menutup bagian berisiko dengan **batasan**, bukan
> dengan janji, sudah cukup konsisten untuk disebut sebagai sifat proyek ini.
>
> Dan di sini ia mengenai godaan yang paling besar di seluruh robotika sosial:
> **wajah yang tersenyum menjual lebih baik.** Robot yang berpura-pura punya
> perasaan mendapatkan kepercayaan yang tidak ia layak dapatkan — dan
> kepercayaan itulah yang dipakai ketika ia meminta sesuatu.
>
> Ia juga senapas dengan tiga hal yang sudah ditetapkan lebih dulu:
> *"trust score bukan security boundary"* (§14.10, tiga kali), *"jangan menilai
> baik atau buruk"* (naskah 4), dan `Observed ≠ Certain` (naskah 16).

> ⚠️ **Tapi "transparan" perlu satu bentuk yang bisa diperiksa, bukan sekadar
> niat** — dan ini kata pengganti keenam di dua naskah terakhir (*unrelated*
> §8.15 · *sembarangan* §14.45 · *bukti yang cukup* §15.10 · *keputusan
> sensitif* §15.16 · *sensitif* §15.29 · di sini).
>
> Bentuk yang bisa ditegakkan dan sudah punya preseden: **robot tidak pernah
> memakai kata ganti orang pertama untuk perasaan** (*"saya senang"*), dan
> ekspresi wajahnya menyatakan **keadaan sistem**, bukan emosi — *sedang
> mendengar*, *tidak yakin*, *menunggu izin*. Yang ketiga itu justru berguna:
> `confidence` yang selama dua puluh naskah hanya berupa angka di API akhirnya
> punya permukaan yang bisa dilihat orang.

> ⚠️ **`eye contact` dan `facial expression` menuntut kamera yang mengarah ke
> wajah orang, terus-menerus** — dan itu menyentuh **C-17**
> ([#75](../../issues/75)) dan **C-23** ([#104](../../issues/104)) sekaligus:
> policy ruangan §15.23 mematikan `camera`, sementara robot **membawa kameranya
> sendiri masuk ruangan**. Policy yang terpasang pada ruangan tidak otomatis
> berlaku pada perangkat yang berjalan masuk. Lihat **C-24** /
> [#114](../../issues/114).
