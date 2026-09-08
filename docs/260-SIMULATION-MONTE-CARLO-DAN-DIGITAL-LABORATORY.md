# 260 — §19.13–§19.15 Scientific Simulation, Monte Carlo Laboratory & Digital Laboratory

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.13 — Scientific Simulation Engine

> **Simulation sebelum eksperimen.**
>
> Domain: `physics · biology · chemistry · materials · AI · robotics ·
> economics · behavior`

```
Model → Parameters → Simulation → Output
```

---

> ⭐⭐⭐ **"Simulation sebelum eksperimen" adalah urutan wajib yang sudah
> ditetapkan naskah 20 untuk perangkat keras, dan di sini ia berlaku untuk
> penelitian.**
>
> §16.26 memberi `Code → Simulation → Safety Test → Hardware` sebagai urutan
> yang tidak boleh dibalik — dicatat sebagai butir **F** karena ia satu-satunya
> yang mencegah cedera fisik. Prinsip yang sama diterapkan di sini punya alasan
> tambahan yang khas penelitian: **eksperimen mahal, lambat, dan sebagiannya
> tidak bisa diulang.** Menjalankan yang murah lebih dulu bukan penghematan
> melainkan cara memilih eksperimen mana yang layak dijalankan sama sekali.

> 🛑 **Tetapi satu pipeline empat langkah untuk delapan domain menyembunyikan
> perbedaan yang lebih besar daripada persamaannya.**
>
> `Model → Parameters → Simulation → Output` berlaku secara bentuk untuk
> kedelapannya, dan **tidak berlaku secara arti**:
>
> | Domain | Modelnya berdiri di atas | Keluarannya bisa dipercaya sejauh |
> |---|---|---|
> | `physics`, `chemistry`, `materials` | hukum yang diketahui | presisi parameternya |
> | `biology` | model yang disederhanakan | kesesuaian dengan sistem hidup |
> | `economics`, `behavior` | asumsi tentang orang | **asumsinya sendiri** |
>
> Simulasi fisika yang salah biasanya salah karena angkanya; **simulasi
> perilaku yang salah salah karena premisnya**, dan ia akan tetap menghasilkan
> keluaran yang rapi. Menaruh `behavior` sederet dengan `physics` berarti
> keduanya akan diperlakukan sama oleh §19.2 (`Simulation → Evaluation`) dan
> oleh §19.14.
>
> ⭐ Yang perlu ditulis satu baris: **tiap domain membawa tingkat kesahihan
> modelnya**, dan keluaran simulasi tidak pernah naik menjadi `Evidence` §19.6
> tanpa menyebutkannya. Bahannya ada — §19.9 `Assumptions` dan §19.12
> `Confounders` adalah tempat yang tepat untuk menyimpannya.

> ⚠️ **`simulations/` di §19.30 adalah pohon simulasi KEENAM di repo ini**
> (`spatial-os/` · `robotics/` · `health-bio/` · `global-intelligence/` ·
> Phase 12 · di sini). Lihat **E-145** / [#138](../../issues/138).

---

## §19.14 — Monte Carlo Laboratory

```
Parameter → 1000 Simulations → Distribution
```

> Output: `uncertainty · sensitivity · robustness`

---

> ⭐⭐⭐⭐ **Ini bentuk yang §18.10 SEHARUSNYA punya — dan ia memperbaiki
> kekurangan yang tercatat satu naskah lalu tanpa menyebutnya.**
>
> §18.10 memberi tiga skenario berprobabilitas: `31 % · 46 % · 23 %`, berjumlah
> tepat seratus. Itu dicatat sebagai masalah: **menjumlahkan ke seratus
> menyatakan bahwa ketiga skenario menghabiskan kemungkinan**, dan menghapus
> kemungkinan keempat yang tidak terpikirkan — justru yang paling mahal.
>
> `Distribution` tidak punya masalah itu. Ia tidak menuntut daftar skenario yang
> lengkap, ia tidak memaksa jumlah, dan **ekornya terlihat**. Untuk pertanyaan
> yang jawabannya benar-benar tidak diketahui, sebaran adalah bentuk yang jujur
> dan tiga angka bernama adalah bentuk yang menenangkan.

> ⭐⭐ **Dan tiga keluarannya menjawab tiga pertanyaan yang berbeda, bukan satu
> pertanyaan tiga kali.**
>
> `uncertainty` = *seberapa lebar jawabannya* · `sensitivity` = **parameter mana
> yang paling menggerakkannya** · `robustness` = *apakah kesimpulannya bertahan
> ketika asumsinya digoyang*.
>
> Yang kedua paling berguna dan paling jarang dilaporkan: ia memberitahu
> peneliti **variabel mana yang layak diukur dengan teliti** dan mana yang
> boleh ditaksir — yaitu keputusan yang menentukan biaya seluruh eksperimen,
> diambil sebelum eksperimennya ada. Ia juga memberi §19.11 `sample
> considerations` dasar berangka yang bagian itu belum punya.

> ⚠️ **Tetapi `1000` adalah satu-satunya angka di seluruh naskah ini, dan ia
> muncul tanpa alasan.** Berapa iterasi yang dibutuhkan ditentukan oleh sebaran
> yang dicari dan ketelitian yang diinginkan — seribu terlalu banyak untuk
> sebagian kasus dan jauh terlalu sedikit untuk ekor yang jarang, yang justru
> tempat risiko tinggal. **A-32** sudah mencatat pola ini di naskah 20 (fase
> tanpa satu pun angka); di sini kebalikannya — satu angka tanpa turunannya.

> ⚠️ **Monte Carlo mengukur ketidakpastian DI DALAM model, bukan ketidakpastian
> TENTANG model.** Seribu simulasi dari model yang keliru menghasilkan sebaran
> yang sempit dan salah — dan sebaran sempit terbaca sebagai keyakinan tinggi.
> Ini kekeliruan yang §18.24 sudah punya obatnya: **`Probability` dipisahkan
> dari `Confidence`**. Bentuk itu berlaku persis di sini, dan belum dipakai.

---

## §19.15 — Digital Laboratory

> **Future integration:** `robotic pipette · liquid handler · microscope ·
> sensor network · experiment scheduler`
>
> **HumanVerse mengirimkan protocol ke lab automation.**

---

> ⭐⭐ **Menandainya sebagai *"future integration"* adalah pilihan yang benar,
> dan ia satu-satunya bagian di naskah ini yang diberi tanda waktu.** Pemilik
> memisahkan apa yang dibangun sekarang dari apa yang datang nanti — kebiasaan
> yang §17.53 mulai (urutan MVP yang berbeda dari daftar lengkap) dan yang
> mencegah seluruh fase dibangun sekaligus.

> 🛑🛑🛑 **Tetapi ini satu-satunya tempat di dua puluh tiga naskah di mana
> HumanVerse MENGGERAKKAN materi fisik atas dasar kesimpulannya sendiri — dan
> ketiga pengaman yang seharusnya berdiri di sana tidak ada satu pun.**
>
> `robotic pipette` dan `liquid handler` memindahkan zat. `experiment
> scheduler` menjalankannya **tanpa orang menunggui**. Rantainya, kalau
> disambung dari §19.2, berbunyi:
>
> ```
> Hypothesis (mesin) → Experiment Planning (mesin) → protocol → lab automation
> ```
>
> Tiga hal yang absen:
>
> 1. **`ACTION GATEWAY` / `GOVERNANCE MESH`** — §14.69 menetapkan keduanya
>    sebagai lapisan wajib antara kecerdasan dan dunia. Ini naskah **KELIMA
>    berturut-turut** yang menggambar jalur ke dunia tanpa keduanya.
> 2. **`Confirmation`** — **H-15** menetapkan konfirmasi manusia wajib mulai
>    R3, dan *"menjalankan protokol kimia tanpa orang di ruangan"* adalah
>    kandidat R4 yang lebih jelas daripada membuka kunci pintu (§16.13,
>    **E-130**/[#111](../../issues/111)).
> 3. **§19.22 Ethics Review** — ada di naskah ini, menyebut dirinya *"komponen
>    wajib"*, dan tidak berdiri di jalur ini.
>
> 🔴 **Dan yang menjadikannya kelas tersendiri: §19.23 menamai `Biosecurity` dan
> `Dangerous Capability` sebagai kategori risikonya sendiri.** Fase yang
> menyebut dua kata itu adalah fase yang tahu ia bisa menghasilkan protokol yang
> tidak boleh dijalankan — dan di sinilah protokol berubah menjadi perbuatan.
> Lihat **C-29** / [#131](../../issues/131).
>
> ⚠️ Ia juga bertegangan langsung dengan pengaman pembuka naskah 22:
> *"HumanVerse tidak mengontrol dunia."* Sebuah pipet robotik adalah kendali
> atas dunia dalam arti yang paling harfiah. Itu tidak berarti bagian ini salah
> — ia berarti **batas naskah 22 perlu dinyatakan ulang di sini**, dengan
> perkecualian yang eksplisit dan gerbangnya.

> ⚠️ **Dan §19.34 memasukkan `mendukung lab automation di masa depan` ke
> Definition of Done, sementara §19.33 tidak punya milestone untuknya.**
> Kriteria selesai yang tidak punya milestone tidak akan pernah diperiksa — ini
> pengulangan **B-33** ([#116](../../issues/116)) dan **G-17**
> ([#121](../../issues/121)) untuk ketiga kalinya. Lihat **G-18** / [#137](../../issues/137).
