# 226 — §15.24–§15.29 Spatial SDK, Repository, API, Data Model, Event Model & Deployment

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.24 — Spatial SDK

> Developer bisa membuat aplikasi.

```
hv.spatial.map()
hv.spatial.locate()
hv.spatial.find_object()
hv.spatial.anchor_ui()
hv.spatial.track()
```

---

> 🛑 **Lima panggilan, dan tidak satu pun membawa `risk_level`, scope izin, atau
> penanda persetujuan — untuk data yang paling sensitif yang pernah dibuka ke
> pihak ketiga.**
>
> Ini kejadian **kedua** dari pola yang sama. **G-11** mencatat: tiga belas tool
> persepsi §10.26 tidak satu pun diberi `risk_level`, padahal
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) mewajibkan setiap tool punya
> `risk_level` dan `side_effects`. Di sini pola itu berulang pada permukaan yang
> **lebih terbuka**, karena SDK berarti kode orang lain.
>
> Yang dikembalikan tiap panggilan, dibaca apa adanya:
>
> | Panggilan | Yang sebenarnya diberikan |
> |---|---|
> | `hv.spatial.map()` | **denah rumah** pengguna |
> | `hv.spatial.locate()` | **posisi pengguna sekarang** |
> | `hv.spatial.find_object()` | letak benda — dan §15.5 menaruh `Person` di pohon objek yang sama |
> | `hv.spatial.track()` | **aliran posisi berkelanjutan** |
> | `hv.spatial.anchor_ui()` | menempatkan tampilan di ruang fisik (§15.22) |
>
> Usul **G-11** berlaku persis di sini dan tinggal diperluas: **aturan 6 spec/05
> — larangan scope untuk agent `third_party` — ditambah `spatial`, `location`,
> `people`, dan `csi`**, sebelum marketplace §14.15 dibuka. Butir itu sudah
> menyebut *"sebelum marketplace dibuka di Phase 14"*; Phase 14 sudah lewat.

> ⚠️ **`track()` adalah satu-satunya panggilan yang berlangganan, bukan
> bertanya** — dan langganan tidak punya bentuk pencabutan di API ini. §14.41
> menjadikan `CANCEL` dan `REVOKE` kata kerja protokol tingkat pertama; SDK ini
> tidak punya keduanya.

---

## §15.25 — Repository Structure

```
spatial-os/
├── runtime/          ├── slam/            ├── mapping/
├── localization/     ├── sensor-fusion/   ├── scene-graph/
├── object-tracking/  ├── human-tracking/  ├── gesture/
├── eye-tracking/     ├── xr-ui/           ├── anchors/
├── navigation/       ├── spatial-memory/  ├── spatial-reasoning/
├── aetherscan/       ├── safety/          ├── privacy/
├── sdk/              └── simulation/
```

---

> ⭐ **Dua puluh submodul, dan pembagiannya bersih** — tiap submodul memetakan
> ke satu bagian naskah, tanpa satu pun yang menduplikasi yang lain. Bandingkan
> `multimodal/` naskah 14 yang punya **lima folder menduplikasi pohon lain**.

> 🛑 **Tetapi `spatial-os/` adalah pohon tingkat-atas BARU — dan H-10 kini
> digerus untuk KELIMA kalinya.**
>
> Riwayatnya: naskah 5 §4 menetapkan monorepo **final** · naskah 9 menambah
> `research/` · naskah 10 `developer-platform/` · naskah 11 `data-platform/`
> (ketiganya = **E-66** / [#55](../../issues/55)) · naskah 16 menarik lima pohon
> keluar dari `intelligence/` (**E-101**) · naskah 18 menambah **enam** sekaligus
> (**E-121**) · naskah 19 menambah yang ini.
>
> Tujuh naskah berturut-turut menyentuh struktur repo. *"Final"* sudah berhenti
> berarti apa-apa, dan [#55](../../issues/55) menanyakan **aturan komposisi**
> justru supaya pertambahan berikutnya tidak perlu keputusan baru.

> 🛑 **Dan `safety/` + `privacy/` di dalam `spatial-os/` menjadikannya pohon
> keamanan KETIGA dan KEEMPAT.**
>
> Sudah ada `security/` (Phase 8) dan `agent-security/` (Phase 14) — **E-121**
> mencatat bahwa dua pohon saja sudah membuat aturan impor **§8.42** (*kode agent
> tidak boleh mengimpor `security/`*) menjadi ambigu. Empat membuatnya tidak bisa
> ditegakkan sama sekali: boleh atau tidak `spatial-os/safety/` mengimpor
> `security/`? Boleh atau tidak `spatial-os/sdk/` mengimpor
> `spatial-os/privacy/`?
>
> Batas keras yang harus ditegakkan CI ([`../spec/06`](../spec/06-MODULE-BOUNDARIES.md))
> tidak bisa punya empat sisi yang tidak diurutkan. Ini memperluas **E-121**;
> usulnya tetap sama dan makin mendesak: **satu `security/`, dengan yang lain
> sebagai submodul**, plus `governance/` yang sampai sekarang belum ada.

> ⭐ **`simulation/` di dalam `spatial-os/` adalah penempatan yang tepat** — dan
> ia harus mewarisi batas keras §12.16 (*simulation tidak boleh mengubah data
> dunia nyata*), yang di sini berarti: **simulasi spasial tidak boleh menulis ke
> peta yang dipakai `safety/`.**

---

## §15.26 — API

```
POST /v1/spatial/map          GET  /v1/spatial/scene
GET  /v1/spatial/objects      POST /v1/spatial/find-object
GET  /v1/spatial/location     POST /v1/spatial/anchors
GET  /v1/spatial/navigation   POST /v1/aetherscan/start
GET  /v1/aetherscan/occupancy POST /v1/xr/ui
```

---

> ⚠️ **`/v1/…` lagi, bukan `/api/v1`** — separuh kedua [#38](../../issues/38),
> naskah **keenam** berturut-turut. Lihat **E-126**.

> ⚠️ **`POST /v1/aetherscan/start` tidak punya `stop`.** Ia satu-satunya
> endpoint di seluruh API HumanVerse yang **menyalakan sensor** dan tidak punya
> pasangan yang mematikannya. §14.41 menjadikan `CANCEL` dan `REVOKE` kata kerja
> tingkat pertama justru untuk hal seperti ini, dan §15.23 menjanjikan *"user
> tetap kontrol"* — kontrol yang tidak punya endpoint bukan kontrol.

> ⚠️ **Tidak ada endpoint untuk policy ruangan §15.23**, padahal itu satu-satunya
> permukaan tempat pengguna menjalankan kendalinya. Sepuluh endpoint untuk
> membaca dan menulis ruang; nol untuk membatasinya.

---

## §15.27 — Data Model

```
rooms · floors · buildings
spatial_maps · point_clouds · meshes
objects · object_history · object_locations
people_tracks · gestures · eye_focus
anchors · navigation_paths
wifi_csi · occupancy_maps
scene_graphs · spatial_events
```

---

> ⭐ **`object_history` dan `object_locations` sebagai tabel terpisah dari
> `objects`** adalah yang membuat §15.8 (*"di mana terakhir saya melihat
> headset"*) bisa dijawab — riwayat butuh barisnya sendiri, bukan kolom
> `last_seen` yang ditimpa.

> 🛑 **Tetapi empat tabel di daftar ini bukan data relasional, dan volumenya
> berbeda ORDE dari apa pun yang pernah ada di repo ini.**
>
> Teknik yang sudah dua kali berbuah di sini adalah **menghitung volumenya,
> bukan membacanya**. `PersonDetected` pada 1 Hz = 86.400 baris/hari; §10.22
> menuntut 30 hari ⇒ **2,6 juta baris** untuk satu pengguna satu kamera.
>
> Yang sekarang datang jauh lebih besar:
>
> | Tabel | Sifatnya | Kenapa ia tidak muat |
> |---|---|---|
> | **`wifi_csi`** | matriks kompleks per subcarrier, **10–100 Hz** | ini data sinyal mentah, bukan kejadian; sehari saja mengalahkan seluruh `events` seumur produk |
> | **`point_clouds`** | ratusan ribu–jutaan titik **per pindaian** | biner besar; tidak pernah ditanya baris per baris |
> | **`meshes`** | geometri biner | sama |
> | **`people_tracks`** | posisi berkelanjutan **per orang** | berkembang dengan jumlah orang × waktu, bukan dengan aktivitas |
>
> Basis data V0 adalah **PostgreSQL + Redis** (**H-12**), dan `events` dirancang
> untuk puluhan kejadian manusia per hari dengan `UNIQUE (user_id,
> idempotency_key)`. Menaruh CSI dan point cloud di sana bukan soal ukuran disk;
> ia akan mengubah sifat seluruh sistem penyimpanan.
>
> Bentuk yang benar dan sudah punya preseden di §15.29 (*"edge melakukan
> processing sensitif"*): **CSI dan point cloud tidak pernah meninggalkan
> perangkat sebagai data mentah** — yang disimpan adalah keluarannya
> (`occupancy_maps`, `spatial_maps`, `objects`), dan yang mentah hidup di
> penyimpanan objek dengan retensi jam, bukan tahun. Itu sekaligus separuh
> jawaban untuk **C-22** dan **C-23**. Lihat **B-31** /
> [#107](../../issues/107).

> ⚠️ **`gestures` dan `eye_focus` sebagai tabel** berarti gerakan tangan dan
> arah pandangan **disimpan**, bukan hanya ditafsirkan lalu dibuang. §15.16
> menyatakan eye tracking *"bukan untuk mengambil keputusan sensitif"* — tetapi
> menyimpannya adalah keputusan tersendiri, dan retensinya tidak disebut di mana
> pun.

---

## §15.28 — Event Model

```
RoomScanned · MapUpdated · ObjectDetected · ObjectMoved · ObjectLost
PersonEntered · PersonExited · GestureRecognized
AnchorCreated · NavigationStarted · NavigationFinished
WiFiMotionDetected · OccupancyChanged
```

---

> ⚠️ **PascalCase lagi — pelanggaran [#38](../../issues/38) yang KEENAM
> berturut-turut** (E-70 · E-88 · E-98 · E-116 · naskah 18 · di sini). Lihat
> **E-126**.

> 🛑 **`PersonEntered` dan `PersonExited` adalah event tentang orang yang belum
> tentu punya akun.**
>
> Setiap event di HumanVerse sampai sekarang punya subjek yang jelas: `user_id`.
> Kedua event ini punya subjek yang **tidak bisa diberi `user_id`** — tamu,
> anak, tetangga yang terdeteksi menembus dinding (§15.4). Mereka masuk `events`
> dan `people_tracks` tanpa pernah menjadi pengguna.
>
> **C-10** ([#40](../../issues/40)) mengusulkan `scope IN ('user-owned',
> 'delegated', 'bystander')` sejak naskah 7; di sini `bystander` berhenti
> menjadi usulan dan menjadi **kolom yang harus ada sebelum event pertama
> ditulis**. Tanpa itu, satu-satunya cara menyimpannya adalah menempelkannya ke
> akun pemilik rumah — yang berarti data tentang orang lain disimpan sebagai
> data pemilik rumah.

> ⚠️ **Tujuh dari tiga belas event bisa terjadi tanpa penggunanya hadir.**
> `WiFiMotionDetected`, `OccupancyChanged`, `PersonEntered`, `PersonExited`,
> `ObjectMoved`, `ObjectLost`, `MapUpdated` — semuanya dipicu oleh dunia, bukan
> oleh perbuatan pengguna. Itu bukan salah, tapi ia menuntut aturan yang belum
> ada: **apa yang boleh memicu pemberitahuan ketika penggunanya tidak di rumah**,
> dan §14.26 Human Attention Firewall adalah tempatnya.

---

## §15.29 — Deployment

```
AR Glasses → Phone Edge AI → Spatial Runtime → Cloud Sync → HumanOS
→ Digital Twin
```

> **Edge** melakukan processing **sensitif**.
> **Cloud** melakukan reasoning **berat**.

---

> ⭐⭐⭐ **Dua kalimat itu adalah pernyataan privasi-oleh-arsitektur pertama
> dalam sembilan belas naskah, dan ia lebih kuat daripada kebijakan mana pun.**
>
> Seluruh perlindungan privasi di HumanVerse sampai sekarang berupa **aturan**:
> `purpose` (§8.10), `permissions` (§8.6), policy ruangan (§15.23). Aturan
> menjaga data yang **sudah dikirim**. Menaruh pemrosesan sensitif di perangkat
> berarti sebagian data **tidak pernah dikirim** — dan itu satu-satunya bentuk
> perlindungan yang tetap berlaku ketika terjadi kebocoran, penyitaan, atau
> permintaan aparat.
>
> Ia juga jawaban langsung untuk **B-31**: CSI dan point cloud diproses di
> tempat, yang naik hanya hasilnya.

> ⚠️ **Tapi "sensitif" tidak didefinisikan — kata pengganti KELIMA di naskah
> ini** (*unrelated* §8.15 · *sembarangan* §14.45 · *bukti yang cukup* §15.10 ·
> *keputusan sensitif* §15.16 · di sini). Dan justru di sini ia paling mudah
> diganti dengan sesuatu yang tegas, karena daftarnya pendek dan diketahui:
> **CSI mentah, point cloud, citra kamera, audio, `eye_focus`, dan
> `people_tracks` tidak meninggalkan perangkat.** Enam nama mengalahkan satu
> kata sifat.

> ⚠️ **`Cloud Sync` tanpa arah.** Naik saja, atau turun juga? Kalau peta ruang
> disinkronkan ke perangkat lain, §15.20 (ruang bersama) dan **C-23** (policy
> ruangan) berlaku pada salinan yang sudah berada di luar rumah — dan policy
> yang hanya ditegakkan di perangkat asal tidak ikut tersalin.
