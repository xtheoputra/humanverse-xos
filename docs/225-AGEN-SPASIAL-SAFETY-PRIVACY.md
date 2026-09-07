# 225 — §15.21–§15.23 Spatial Agents, Spatial Safety & Spatial Privacy

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.21 — Spatial Agents

> Agent baru muncul.

| Agent | Fungsi |
|---|---|
| Navigator | Navigasi |
| Finder | Cari objek |
| Mapper | Scan ruang |
| Interior | Tata ruang |
| Safety | Zona aman |
| AetherScan | WiFi sensing |

---

> ⚠️ **Enam agent baru — dan hitungan agent kini melewati lima puluh.**
>
> §11.4 memberi 25 berhierarki · **E-95** mencatat tujuh yang muncul di contoh
> tanpa terdaftar · **G-13** ([#89](../../issues/89)) menambah dua belas dari
> Phase 12 · naskah 18 menambah team dan agent federasi · enam di sini.
> Sementara itu **B-12** memperingatkan ratusan agent pada satu graf, dan naskah
> 5 §58 sudah menulis *"jangan langsung 50 agent"*.
>
> ⭐ Kriteria yang **G-13** minta sudah bisa dipakai di sini, dan hasilnya tajam:
> **service** kalau deterministik, tidak memanggil tool, tidak menulis apa pun,
> tidak butuh identitas untuk jejak audit; **agent** kalau memutuskan di antara
> pilihan, memanggil tool lewat gateway, dan punya `risk_level` di atas R0.
>
> | | Vonis dengan kriteria G-13 |
> |---|---|
> | `Mapper` · `AetherScan` | **service** — keduanya mengubah sensor jadi data, deterministik, tidak memutuskan apa pun |
> | `Finder` | **service** — kueri atas Spatial Memory |
> | `Safety` | **bukan agent, dan bukan service biasa** — ia governance (lihat di bawah) |
> | `Navigator` · `Interior` | **agent** — keduanya memilih di antara pilihan |
>
> Dua dari enam. Itu pola yang sama dengan G-13 (sepuluh dari dua belas
> kemungkinan service).

> 🛑 **`Safety` sebagai AGENT SEJAJAR bertentangan dengan §14.44, yang ditulis
> satu naskah lalu.**
>
> §14.44 menetapkan: *"Governance **tidak boleh menjadi agent biasa** yang dapat
> dipengaruhi oleh action agents."* Di tabel ini `Safety` berdiri di baris yang
> sama dengan `Interior` dan `Navigator` — yaitu persis sebagai agent biasa,
> dapat dipanggil, dapat dinegosiasi, dapat kalah suara.
>
> Ini pengulangan keberatan yang saya catat untuk **Risk Agent §14.13**, dan
> kali ini taruhannya lebih tinggi karena §15.13 menyatakan fase ini *"membuka
> jalan menuju robotika"*. Yang perlu ditulis satu kalimat: **`Safety` adalah
> komponen governance yang menjaga rantai §15.22, bukan peserta di dalamnya.**

> ⚠️ **`Interior` (tata ruang) adalah satu-satunya agent di daftar ini yang
> menyarankan MENGUBAH rumah orang.** Ia karena itu agent pertama yang
> keluarannya menyentuh selera dan uang sekaligus, dan ia perlu `risk_level`
> serta batas yang jelas — terutama karena §14.23 baru saja membuka *marketplace
> commission* sebagai model pendapatan. Saran tata ruang yang menguntungkan
> pihak yang menjual perabotnya adalah bentuk konflik kepentingan yang belum
> pernah dibahas.

---

## §15.22 — Spatial Safety

> Harus ada **boundary**.

```
Spatial Action → Collision Check → Human Detection → Safety Zone
→ Permission → Execute
```

Contoh:

> AR **tidak menampilkan objek yang menutupi jalan** secara berbahaya.

---

> ⭐⭐ **`Human Detection` sebagai langkah tersendiri di rantai keselamatan
> adalah hal yang benar dan tidak selalu dilakukan.** Memeriksa tabrakan dengan
> perabot dan memeriksa keberadaan manusia adalah dua pertanyaan berbeda, dan
> memisahkannya berarti yang kedua tidak bisa terlewat karena yang pertama sudah
> lulus.

> 🛑🛑 **Tetapi rantai ini tidak punya `Risk` dan tidak punya `Confirmation` —
> dan ia berakhir di `Execute`.**
>
> Bandingkan tiga rantai yang sudah ada:
>
> | Rantai | Gerbang |
> |---|---|
> | §11.14 Action Gateway | 9, termasuk `Risk`, `Consent`, `Rate Limit`, **`Confirmation`** |
> | §14.20 Agent Security Mesh | 11, tetapi **kehilangan** `Consent`, `Rate Limit`, `Confirmation` (**E-117**) |
> | **§15.22 Spatial Safety** | **5**, punya `Permission`, **tanpa `Risk` maupun `Confirmation`** |
>
> Ini rantai **kelima** yang berakhir di tindakan tanpa titik di mana manusia
> bisa menahan, setelah empat yang **E-117** ([#93](../../issues/93)) catat di
> naskah 18. Lima kali di dua naskah berturut-turut bukan kelalaian penulisan.
>
> **Yang membuat rantai INI berbeda dari empat sebelumnya: ia akan mewarisi
> robot.** Penutup naskah menyatakan Phase 16 = *Robotics & Embodied
> Intelligence*, dan bahwa *"robot tidak bisa bergerak dengan aman tanpa
> SpatialOS ... yang sudah dibangun di fase ini."* Rantai keselamatan tanpa
> `Risk` yang diwarisi benda bergerak adalah kesalahan yang mahal diperbaiki
> setelah ada perangkat kerasnya.
>
> **H-15** sudah memberi aturannya (otomatis sampai R2, konfirmasi wajib mulai
> R3) dan **H-21** sudah memberi definisi R4 (`DENY`, *irreversible*). Keduanya
> tinggal dipasang. Lihat **E-124** / [#106](../../issues/106).

> ⚠️ **Contohnya tentang RENDER, rantainya tentang ACTION.** *"AR tidak
> menampilkan objek yang menutupi jalan"* adalah keselamatan **tampilan**;
> `Spatial Action → … → Execute` adalah keselamatan **tindakan**. Keduanya
> dibutuhkan dan keduanya berbeda — yang pertama menjaga penglihatan orang, yang
> kedua menjaga apa yang boleh terjadi di ruangan. Satu rantai lima langkah
> tidak bisa menjadi keduanya, dan ketika Phase 16 datang, perbedaannya menjadi
> perbedaan antara widget yang menghalangi dan benda yang menabrak.

> ⚠️ **`Safety Zone` tidak pernah didefinisikan** — siapa yang menggambarnya,
> apakah pengguna atau sistem, dan apa yang terjadi kalau seseorang berdiri di
> dalamnya. Ia satu-satunya langkah di rantai ini yang tidak punya padanan di
> bagian mana pun.

---

## §15.23 — Spatial Privacy

> Setiap ruangan punya **policy**.

```yaml
bedroom:
  camera: false
  audio: false

living_room:
  object_tracking: true
```

> **User tetap mengontrol.**

---

> ⭐⭐ **Policy per RUANGAN adalah gagasan yang benar, dan ia baru.** Sampai
> sekarang seluruh model izin HumanVerse berdimensi *siapa* dan *data apa*
> (§8.6, §14.20 `Memory Scope` / `Data Scope`). Ruangan menambahkan sumbu
> **tempat**, dan itu sumbu yang benar-benar dipahami orang: *"kamar tidur
> tidak"* adalah kalimat yang bisa diucapkan siapa pun tanpa membaca dokumen.

> 🛑🛑🛑 **Tetapi contohnya mematikan dua sensor yang butuh garis pandang, dan
> membiarkan hidup satu-satunya sensor yang menembus dinding.**
>
> `bedroom: camera:false, audio:false`. Yang **tidak** disebut: **WiFi
> sensing**. Dan §15.4 menyatakan AetherScan dapat melakukan `occupancy
> detection`, `motion detection`, dan — di daftar masa depan — **`breathing
> detection`** serta **`through-wall sensing`**.
>
> Rangkaiannya bisa ditelusuri baris per baris di dalam naskah ini sendiri:
>
> | Bagian | Yang dinyatakan |
> |---|---|
> | §15.23 | kamar tidur: kamera mati, mikrofon mati |
> | §15.4 | AetherScan tidak butuh keduanya — ia membaca WiFi CSI |
> | §15.4 | dan ia **menembus dinding**, jadi ia bahkan tidak perlu berada di dalam kamar |
> | §15.10 | `Sleeping` ada di daftar aktivitas yang dilacak |
> | §15.4 | `breathing detection` = laju napas, tanda vital |
> | §15.27 | `wifi_csi` dan `occupancy_maps` punya tabelnya sendiri |
>
> Artinya: **pengguna yang mematikan kamera dan mikrofon di kamar tidurnya tetap
> terpantau tidur dan bernapas.** Ia akan mengira sudah mematikan pemantauan,
> karena itulah yang dijanjikan kalimat *"user tetap kontrol"*.
>
> Ini bukan celah implementasi; ini **bentuk policy-nya**. Daftar `camera` dan
> `audio` adalah daftar **perangkat**, sementara yang perlu dikendalikan adalah
> **kemampuan**. Selama policy ditulis per-perangkat, setiap sensor baru
> otomatis diizinkan sampai seseorang ingat menambahkannya.
>
> Bentuk yang benar sudah dipakai di tempat lain di repo ini: **`deny` sebagai
> daftar eksplisit** (§14.21) dan **default deny** (§14.37, R4 §11.15). Untuk
> ruangan, itu berarti: **policy ruangan menyebut kemampuan yang DIIZINKAN, dan
> apa pun yang tidak disebut ditolak** — sehingga sensor yang belum ada ketika
> policy ditulis tidak otomatis mendapat izin.
>
> Dan satu aturan tambahan yang tidak bisa diturunkan dari yang lain: **ruangan
> yang menolak sebuah kemampuan menolaknya juga dari luar ruangan itu.**
> Through-wall sensing membuat batas ruangan berhenti menjadi batas teknis;
> hanya aturan yang bisa mengembalikannya. Lihat **C-23** /
> [#104](../../issues/104).

> ⚠️ **`living_room: object_tracking: true` juga melacak MANUSIA**, karena §15.5
> menaruh `Person` di pohon objek yang sama dengan `Sofa`. Sakelar yang namanya
> mengatakan "objek" tetapi cakupannya termasuk orang adalah sakelar yang
> menyesatkan orang yang menyalakannya. Pemisahan `object_tracking` dan
> `people_tracking` perlu ada di policy, dan §15.27 sudah memberi dua tabel
> terpisah (`objects`, `people_tracks`) — jadi bahannya ada.

> ⚠️ **Dan "user" mana, kalau rumahnya berisi beberapa orang?** Satu peta, satu
> policy, beberapa penghuni — dan hanya satu dari mereka yang punya akun.
> Ini pertanyaan yang harus dijawab pemilik sebelum satu baris kode: lihat
> **A-31** / [#105](../../issues/105).
