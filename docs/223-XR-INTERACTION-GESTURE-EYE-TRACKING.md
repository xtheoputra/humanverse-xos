# 223 — §15.14–§15.16 XR Interaction Layer, Gesture Engine & Eye Tracking

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.14 — XR Interaction Layer

Interface utama: **Voice · Gesture · Eye Tracking · Hand Tracking · Controller ·
Spatial Pointer**

> Semua menjadi bagian **HumanOS**.

---

> ⭐ **"Semua menjadi bagian HumanOS" adalah kalimat penempatan yang benar.**
> Enam cara masuk ini bukan fitur SpatialOS melainkan **modalitas antarmuka**,
> dan §13 sudah punya rumahnya. Itu mencegah HumanOS dan SpatialOS menumbuhkan
> dua lapisan antarmuka yang bersaing — pola yang sudah terjadi pada `security/`
> vs `agent-security/` (**E-121**).

> ⚠️ **Enam modalitas, dan tidak satu pun punya cara membatalkan.** Papan tik
> punya Escape, layar sentuh punya menjauhkan jari, suara punya diam. Gesture
> dan eye tracking **tidak punya keadaan "tidak sedang memerintah"** kecuali
> dinyatakan — mata selalu melihat sesuatu, tangan selalu di suatu posisi.
>
> Itu bukan soal kenyamanan: §15.15 memetakan `Grab → Pick` dan `Pinch →
> Select`, dan §14.60 membangun seluruh Approval Center di atas gagasan bahwa
> persetujuan adalah tindakan **sengaja**. Persetujuan yang bisa diberikan
> dengan tidak sengaja bukan persetujuan. Yang perlu ditulis: **aksi di atas R2
> tidak pernah dikonfirmasi lewat gesture atau tatapan saja.**

> ⚠️ Naskah menaruh angka lepas **`5`** di bagian ini. Lihat **G-15** /
> [#103](../../issues/103).

---

## §15.15 — Gesture Engine

> Gesture dikenali menjadi **intent**.

| Gesture | Intent |
|---|---|
| Pinch | Select |
| Swipe | Next |
| Grab | Pick |
| Point | Focus |
| Wave | Dismiss |

```
Hand Tracking → Gesture Recognition → Intent → Action
```

---

> ⭐⭐ **Memisahkan `Gesture` dari `Intent` adalah pemisahan yang benar dan
> jarang dibuat.** Gerakan tangan adalah **pengamatan**; maksudnya adalah
> **tafsiran**. Menaruh keduanya di dua kolom berarti tafsirannya bisa salah
> tanpa merusak rekamannya — dan itu sejajar dengan tangga *Observed ≠ Predicted*
> naskah 16, serta dengan `Gesture Recognition` yang berdiri sebagai langkah
> tersendiri di pipeline.

> 🛑 **Tetapi rantainya `Intent → Action` tanpa satu gerbang pun — dan lima
> gerakan ini adalah gerakan sehari-hari.**
>
> `Wave` adalah cara orang menyapa; `Point` adalah cara orang menunjuk sesuatu
> kepada orang lain; `Grab` adalah cara orang mengambil gelas. Sistem yang
> memetakan keduanya ke `Dismiss`, `Focus`, dan `Pick` akan menerima perintah
> dari orang yang tidak sedang memerintah — dan §15.10 melacak **semua orang di
> ruangan**, bukan hanya penggunanya.
>
> Yang hilang di rantai ini persis yang hilang di empat rantai naskah 18
> (**E-117** / [#93](../../issues/93)): tidak ada `Policy`, `Risk`, atau
> `Confirmation` antara `Intent` dan `Action`. Untuk gesture, ditambah satu yang
> khas: **tidak ada pemeriksaan SIAPA yang menggerakkan tangan.**
>
> Bahan penutupnya sudah ada: §15.10 `zona interaksi` bisa menjadi syarat
> (perintah hanya diterima dari orang di zona itu), dan §11.14 Action Gateway
> sudah menjadi tempat yang benar untuk `Intent` bermuara — bukan langsung ke
> `Action`.

---

## §15.16 — Eye Tracking Intelligence

Eye tracking digunakan untuk: **focus detection · attention estimation ·
interface optimization · accessibility.**

> **Bukan untuk mengambil keputusan sensitif secara otomatis.**

---

> ⭐⭐⭐ **Kalimat penutupnya adalah pengaman yang ditulis pemilik sendiri, dan
> ia yang paling tepat sasaran di seluruh naskah ini.**
>
> Eye tracking adalah teknologi yang godaannya paling besar: ia mengukur
> **perhatian**, dan perhatian adalah hal yang paling dekat dengan keinginan
> tanpa pernah menjadi keinginan. Menyatakan lebih dulu bahwa ia **bukan** dasar
> keputusan sensitif menutup pemakaian yang paling merugikan sebelum ada yang
> membangunnya. ⭐ Dan `accessibility` di daftar pemakaiannya menyebut satu-satunya
> kelompok yang eye tracking-nya benar-benar mengubah hidup.

> ⚠️ **Tapi "keputusan sensitif" tidak didefinisikan — kata pengganti keempat
> di naskah ini** (setelah *"unrelated"* §8.15, *"sembarangan"* §14.45, *"bukti
> yang cukup"* §15.10). Bahannya sudah ada dan berupa tangga: **R3 ke atas**
> (**H-15**) sudah menjadi definisi "sensitif" yang bisa ditegakkan di gerbang.
> Satu penggantian kata menutupnya.

> 🛑 **`attention estimation` menabrak Human Attention Firewall §14.26, dan
> arahnya berbahaya.**
>
> §14.25 menjadikan **perhatian manusia sebagai sumber daya yang dianggarkan**,
> sejajar dengan CPU dan token; §14.26 memasang firewall yang memutuskan apa
> yang boleh menembus ke perhatian orangnya. Sampai naskah 18, perhatian adalah
> sesuatu yang sistem **belanjakan tanpa bisa mengukurnya**.
>
> Eye tracking membuatnya **terukur**. Itu memperbaiki firewall — anggaran yang
> bisa diukur bisa ditegakkan — dan sekaligus membuka pemakaian yang berlawanan:
> antarmuka yang dioptimalkan terhadap perhatian yang terukur adalah antarmuka
> yang **belajar menarik perhatian lebih baik**. `interface optimization` di
> daftar yang sama tidak menyatakan ke arah mana ia mengoptimalkan.
>
> Ini bentuk baru dari keberatan **§14.58** (`Human Intervention Rate` sebagai
> metrik yang turun baik karena sistem membaik maupun karena sistem berhenti
> bertanya): **metrik perhatian yang dijadikan target akan dioptimalkan, dan
> arah yang menguntungkan produk berlawanan dengan arah yang menguntungkan
> penggunanya.** Yang perlu ditulis satu kalimat: *attention estimation dipakai
> untuk MENGURANGI gangguan, tidak pernah untuk menaikkan keterlibatan.*

> ⚠️ Naskah menaruh angka lepas **`5`** di bagian ini juga. Lihat **G-15**.
