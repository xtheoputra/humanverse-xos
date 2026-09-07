# 221 — §15.8–§15.11 Spatial Memory, Object Tracking, Human Tracking & Scene Graph

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.8 — Spatial Memory

> Ini salah satu fitur **paling menarik**.

HumanVerse mengingat: **lokasi terakhir objek · lokasi favorit · jalur yang
sering dilalui · perubahan ruangan.**

```
Yesterday   Wallet   Living Room Table
Today       Keys     Kitchen Counter
```

Query: *"Di mana terakhir saya melihat headset?"*

> Spatial Memory: *"Sekitar pukul **22:15 kemarin**, headset terakhir terlihat
> di meja kerja."*

---

> ⭐⭐⭐ **Jawaban contohnya membawa WAKTU dan kata "sekitar" — dan keduanya
> benar.**
>
> *"Sekitar pukul 22:15"* menyatakan ketidakpastian **di dalam kalimatnya**,
> bukan sebagai angka `confidence` yang disembunyikan di API. Itu bentuk yang
> **E-74** minta dan yang §12.15 sediakan tempatnya, muncul di permukaan tempat
> pengguna benar-benar membacanya. Sistem yang menjawab *"22:15"* tanpa
> "sekitar" berbohong dengan presisi.

> 🛑 **Tetapi "jalur yang sering dilalui" adalah jenis data yang berbeda dari
> tiga lainnya, dan naskah tidak membedakannya.**
>
> Lokasi dompet adalah fakta tentang **benda**. Jalur yang sering dilalui adalah
> **pola gerak seseorang di dalam rumahnya sendiri** — jam berapa ia ke dapur,
> berapa kali ia bangun malam, berapa lama ia di kamar mandi. Digabung dengan
> §15.10 (`Sleeping`, `Exercising`) dan §15.4 (`breathing detection`), yang
> tersimpan bukan lagi peta melainkan **rutinitas tubuh**.
>
> Dan **§14.22 baru saja memberi memori sumbu `level`**: `Personal → Agent →
> Team → Organization → Public`. Butir **A-30** ([#92](../../issues/92))
> menanyakan apa yang membuat memori naik — dan Spatial Memory adalah contoh
> yang membuat salah satu dari tiga jawabannya **jelas tidak bisa dipakai**:
> memori spasial rumah seseorang tidak boleh pernah naik ke tingkat organisasi
> "menurut kebijakan organisasi". Itu memperkuat usul **(b)** di butir itu.

> ⚠️ **`lokasi favorit` tidak punya definisi.** Favorit menurut frekuensi, durasi,
> atau pernyataan penggunanya? Ini pola **B-26** (*success criteria* tanpa
> bentuk) pada benda baru: apa pun yang dipilih akan dioptimalkan sistem, dan
> ketiganya mengukur hal yang berbeda.

---

## §15.9 — Object Tracking

```
Detected → Identified → Tracked → Remembered → Updated → Archived
```

```yaml
object:
  id:
  category:
  position:
  velocity:
  confidence:
  last_seen:
```

---

> ⭐⭐ **`Archived` sebagai keadaan akhir — bukan `Deleted` — adalah pilihan yang
> sejalan dengan §14.29** (*agent tidak langsung dihapus, ini penting untuk
> audit*). Objek yang hilang dari pandangan belum tentu hilang dari rumah, dan
> riwayatnya yang menjawab *"di mana terakhir saya melihatnya"*.

> ⭐ **`last_seen` ada, dan itu yang membuat §15.8 mungkin.** Ia juga field yang
> hilang dari sistem koordinat §15.7 — di sini ia muncul, jadi bahannya ada,
> tinggal dinaikkan ke definisi bersama.

> ⚠️ **Enam keadaan, tetapi tidak ada keadaan untuk *"pernah ada, sekarang
> tidak"* yang berbeda dari `Archived`.** §15.28 memberi event `ObjectLost` —
> jadi kejadiannya diakui, tetapi tidak punya padanan di daur hidup. Ini pola
> **G-14** yang baru saja tercatat di naskah 18: daftar keadaan dan daftar event
> tidak sepanjang satu sama lain, dan yang jatuh adalah yang menandai kegagalan.

> ⚠️ **`category` tanpa daftar nilai.** Objek yang bisa dilacak menentukan
> seberapa jauh fitur ini boleh pergi — `wallet` dan `keys` tidak sama dengan
> `medication`, `alcohol`, atau `document`. Daftar tertutup lebih baik daripada
> kategori bebas, dan alasannya sama dengan **spec/05** aturan 6 (larangan scope
> untuk agent `third_party`).

---

## §15.10 — Human Tracking

> **Bukan sekadar mendeteksi manusia.** Sistem memahami: posisi · arah berjalan
> · aktivitas · gesture · zona interaksi.

Contoh aktivitas:

```
Standing   Walking   Sitting   Working
Cooking    Exercising          Sleeping
```

> Tetapi **jangan menyimpulkan aktivitas sensitif tanpa bukti yang cukup.**

---

> ⭐⭐ **Kalimat penutup itu adalah pengaman yang ditulis pemilik sendiri, dan
> ia yang kelima berturut-turut** (§8.46 · §11.63 · §12 · §13.32 · §14.64).
> Kebiasaan menutup bagian berisiko dengan batasan, bukan dengan janji, layak
> dicatat sebagai keberhasilan tersendiri.

> 🛑 **Tetapi "bukti yang cukup" adalah kata pengganti yang tidak bisa ditegakkan
> — dan ini kejadian KETIGA dari pola yang sama persis.**
>
> | Naskah | Kata yang melunakkan | Butir |
> |---|---|---|
> | §8.15 | *"access **unrelated** health data"* | siapa yang memutuskan "unrelated"? |
> | §14.45 | *"tidak boleh mengubah control plane **sembarangan**"* | **E-121** |
> | §15.10 | *"aktivitas sensitif tanpa bukti yang **cukup**"* | di sini |
>
> Ketiganya adalah **batas keras yang dilunakkan satu kata sifat**, dan
> ketiganya akan lolos apa pun yang terjadi, karena setiap kesimpulan yang
> diambil akan dianggap punya bukti yang cukup.
>
> Bahan untuk menggantinya sudah ada dan berupa angka: §14.62 menetapkan
> `confidence < 0.6` sebagai syarat eskalasi. Bentuk yang bisa ditegakkan:
> **daftar tertutup aktivitas yang ditandai sensitif**, dan untuk daftar itu
> ambang `confidence` yang jauh lebih tinggi plus larangan menyimpulkannya dari
> satu sensor saja.

> 🛑 **`Sleeping` ada di daftar contoh — dan ia satu-satunya yang terjadi di
> kamar tidur.** §15.23 memberi `bedroom: camera:false, audio:false`, tetapi
> tidak mematikan WiFi sensing — dan WiFi sensing adalah persis cara mendeteksi
> tidur tanpa kamera (§15.4 `breathing detection`). Aktivitas ini karena itu
> **tetap bisa disimpulkan di ruangan yang penggunanya kira sudah ia matikan**.
> Lihat **C-23** / [#104](../../issues/104).

> ⚠️ **Dan orang yang dilacak belum tentu penggunanya.** *"Estimasi jumlah
> orang"* (§15.4) berarti tamu, keluarga, anak, pekerja rumah tangga — semuanya
> masuk `people_tracks` (§15.27) tanpa pernah menyetujui apa pun. Ini **C-10**
> ([#40](../../issues/40)) dan **C-18** ([#76](../../issues/76)) pada bentuk
> yang paling langsung: model izin masih hanya punya kata `user-owned`.

---

## §15.11 — Spatial Scene Graph

> Ruangan menjadi **graph**.

Relationship: **`ON` · `NEXT_TO` · `INSIDE` · `FACING` · `BEHIND` · `MOVING_TO`**

> Ini menjadi dasar **reasoning spasial**.

---

> ⭐⭐⭐ **Enam relasi, semuanya GEOMETRIS dan bisa diperiksa — tidak satu pun
> kausal atau tafsiran.** `A ON B` benar atau salah; ia tidak perlu dibuktikan
> lewat rantai eksperimen seperti `influences` di Human Knowledge Graph
> (**E-81** / [#7](../../issues/7)).
>
> Ini graf **ketiga** di HumanVerse, dan ketiganya kini punya sifat yang jelas:
>
> | Graf | Isi | Sifat relasi |
> |---|---|---|
> | Human Knowledge Graph | hidup pengguna | **kausal** — dan itu yang membuat E-81 terbuka |
> | Agent Relationship Graph §14.33 | sistemnya | struktural |
> | **Spatial Scene Graph** §15.11 | ruangnya | **geometris** |
>
> Dua yang terakhir aman justru karena relasinya bisa diukur. Yang perlu ditulis
> sekali, dan berlaku untuk ketiganya: **ketiga graf tidak disimpan di satu
> tempat**, karena hak hapus (**C-9**) berlaku penuh pada yang pertama, sebagian
> pada yang ketiga (manusia di dalamnya), dan tidak pada yang kedua.

> ⚠️ **`MOVING_TO` bukan relasi geometris — ia PREDIKSI.** Lima relasi lain
> menyatakan keadaan sekarang yang bisa diukur; `MOVING_TO` menyatakan **niat
> atau tujuan**, dan menyimpulkannya dari vektor kecepatan adalah tebakan.
> Untuk `Person`, itu tebakan tentang **ke mana seseorang hendak pergi**.
>
> Ia sebaiknya membawa `confidence` seperti objek §15.5 — atau, lebih baik,
> dipisahkan namanya: `HEADING` (terukur, dari `velocity`) berbeda dari
> `MOVING_TO` (tujuan, disimpulkan). Tangga §10.5 dan prinsip naskah 16
> (*Observed ≠ Predicted ≠ Simulated ≠ Certain*) sudah menyediakan kosakatanya.
