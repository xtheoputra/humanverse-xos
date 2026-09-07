# 224 — §15.17–§15.20 Spatial UI, Notifications, Workspace & Collaborative XR

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.17 — Spatial UI Framework

> UI berubah menjadi **objek 3D**.

Widget: **Calendar · Goals · AI Chat · Navigation · Notifications ·
Spatial Notes**

> ⚠️ Naskah menulis *"Contoh:"* lalu **tidak memberi contohnya** — hanya angka
> lepas `6`. Contoh tampilan yang dijanjikan **tidak ada di naskah**; sengaja
> tidak ditambal. Lihat **G-15** / [#103](../../issues/103).

---

> ⭐ **Enam widget, dan lima di antaranya sudah punya rumah** — `Calendar`,
> `Goals`, `AI Chat`, `Navigation`, dan `Notifications` semuanya fitur yang ada
> sejak V0 atau Phase 13. Ini bukan fase yang menambah fitur; ia **memindahkan
> fitur yang sudah ada ke permukaan baru**. Untuk fase sebesar ini, itu kabar
> baik: permukaannya yang baru, bukan produknya.
>
> ⭐ `Spatial Notes` satu-satunya yang benar-benar baru, dan ia masuk akal — nota
> yang menempel pada tempat adalah hal yang tidak bisa dilakukan layar.

> ⚠️ **UI sebagai objek 3D berarti UI punya POSISI — dan posisi berarti ia bisa
> menghalangi.** §15.22 menyebutnya (*"AR tidak menampilkan objek yang menutupi
> jalan secara berbahaya"*), tetapi §15.17 tidak menyebut satu pun batasan
> penempatan. Widget yang menempel di depan tangga adalah kelas bahaya yang
> tidak ada padanannya di antarmuka datar, dan aturannya perlu ada di tempat
> widget didefinisikan, bukan hanya di bagian keselamatan.

---

## §15.18 — Spatial Notifications

Alih-alih popup biasa:

```
User enters kitchen → Reminder appears near coffee machine
```

> Context-aware notification lebih **alami**.

---

> ⭐⭐⭐ **Ini penerapan pertama `Attention Budget` §14.25 pada permukaan nyata,
> dan bentuknya benar: notifikasi tidak MENGEJAR orangnya, ia MENUNGGU di
> tempat.**
>
> Pemberitahuan yang muncul ketika seseorang memasuki dapur tidak menyela apa
> pun — ia memakai perhatian yang **sudah** ada di sana. Bandingkan
> `10 agents × 5 notifications/day = 50 interruptions` yang §14.25 pakai untuk
> menunjukkan pagu per-agent sudah berhenti berarti apa-apa. Notifikasi spasial
> mengubah sumbunya: bukan *berapa kali*, melainkan *di mana dan kapan yang
> sudah tepat*.
>
> Ia juga memberi `LATER` dan `DIGEST` (§14.26) sesuatu yang selama ini tidak
> mereka punya: **tempat untuk menunggu**.

> ⚠️ **Tetapi ruangan yang bisa memicu notifikasi juga bisa membocorkannya.**
> Pengingat yang muncul dekat mesin kopi terlihat oleh siapa pun yang ada di
> dapur — dan §15.20 menjadikan ruang bisa dibagikan. Antarmuka datar punya
> privasi bawaan karena layarnya menghadap satu orang; AR tidak.
>
> Yang perlu ditulis, dan bahannya sudah ada di §15.23: **notifikasi membawa
> tingkat sensitivitas, dan yang di atas Level 2 tidak dirender di ruang bersama
> maupun ketika `people_count > 1`** — §15.4 sudah menghitung jumlah orang.

---

## §15.19 — Spatial Workspace

Konsep: **infinite monitors · 3D dashboard · floating documents · AI companion ·
collaborative workspace.**

> Ini menjadi **HumanVerse WorkOS**.

---

> 🛑 **"HumanVerse WorkOS" adalah nama produk BARU yang muncul dalam satu
> kalimat, tanpa tempat di peta fase mana pun.**
>
> Repo ini sudah punya riwayat panjang dengan nama yang bercabang: *"HumanOS"*
> kini punya **tiga** arti (**E-114**), *"sandbox"* punya **empat** (**E-105**),
> *"KILL"* punya **tiga** (**E-120**). `WorkOS` adalah calon berikutnya — ia
> berdiri sejajar dengan `HumanOS` dan `SpatialOS` secara penamaan, tetapi tidak
> pernah disebut lagi di 13 bagian sesudahnya, tidak punya direktori di §15.25,
> tidak punya endpoint di §15.26, dan tidak punya butir di §15.32.
>
> Kemungkinan besar ia **sebutan untuk sekumpulan widget**, bukan sistem operasi
> ketiga. Kalau begitu, sebaiknya ditulis begitu — karena satu kalimat yang
> menyebut "OS" akan dibaca sebagai janji arsitektur oleh orang yang membangunnya.

> ⚠️ **`collaborative workspace` di sini dan §15.20 `Collaborative XR` adalah hal
> yang sama, disebut dua kali dengan dua nama, di dua bagian berurutan.**

---

## §15.20 — Collaborative XR

> Beberapa pengguna bisa **berbagi ruang virtual**.

Use case: **meeting · belajar · desain · remote collaboration.**

> ⚠️ Naskah menulis *"Contoh:"* lalu hanya menaruh angka lepas `6` — contohnya
> **tidak ada di naskah**. Lihat **G-15**.

---

> 🛑 **Ruang bersama adalah tempat pertama di fase ini di mana peta rumah
> seseorang bisa terlihat orang lain — dan tidak ada satu kalimat pun tentang
> apa yang dibagikan.**
>
> Sebuah sesi XR bersama bisa berarti dua hal yang sangat berbeda:
>
> | Yang dibagikan | Akibatnya |
> |---|---|
> | **Ruang virtual bersama** (papan, dokumen, avatar) | wajar, dan itu yang dimaksud oleh empat *use case* |
> | **Peta ruang fisik salah satu peserta** | orang lain melihat denah rumah, letak perabot, dan **§15.10 melacak siapa saja yang ada di dalamnya** |
>
> Naskah tidak menyatakan yang mana. Dan karena §15.5 menjadikan `Person`
> sebagai simpul di peta yang sama dengan `Sofa`, bawaan yang paling mungkin
> adalah keduanya ikut.
>
> Ini menabrak tiga butir yang sudah terbuka sekaligus: **C-10**
> ([#40](../../issues/40)) — model izin belum punya kata untuk data orang lain;
> **C-19** ([#81](../../issues/81)) — orang ketiga yang tidak pernah menyetujui
> apa pun; dan **A-30** ([#92](../../issues/92)) — aturan naik memori dari
> Personal ke Team. Rapat kerja yang menampilkan ruang tamu seseorang adalah
> memori spasial yang **naik ke tingkat Team tanpa ada yang menaikkannya**.
>
> Yang minimum perlu ditulis: **ruang bersama bawaannya adalah ruang virtual
> netral**; berbagi peta fisik adalah tindakan tersendiri, per sesi, dan
> **tidak pernah membawa `people_tracks`**.

> ⚠️ **Dan orang yang berada di ruangan itu bukan peserta rapat.** Anggota
> keluarga yang lewat di belakang bukan pihak dalam sesi kolaborasi, tetapi
> berada di dalam data yang dibagikan. Ini bentuk paling langsung dari
> `bystander` yang [#40](../../issues/40) usulkan sejak naskah 7 — dan di sini
> ia bukan lagi soal basis data, melainkan soal siapa yang terlihat orang lain.
