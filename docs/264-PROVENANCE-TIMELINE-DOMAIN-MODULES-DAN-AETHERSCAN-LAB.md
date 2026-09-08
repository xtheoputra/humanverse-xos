# 264 — §19.26–§19.29 Scientific Provenance, Research Timeline, Domain Modules & AetherScan Lab

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.26 — Scientific Provenance

```
Insight → Evidence → Paper → Dataset → Experiment → Model → Agent
```

---

> ⭐⭐ **Tiga mata rantai di tengah — `Paper`, `Dataset`, `Experiment` — adalah
> yang benar untuk domain ini, dan mereka bukan sekadar penamaan ulang.**
>
> Sebuah kesimpulan ilmiah bisa salah di tiga tempat yang berbeda: **makalahnya**
> keliru, **datanya** keliru, atau **percobaannya** dijalankan dengan cara yang
> keliru. Menamai ketiganya sebagai mata rantai terpisah berarti ketiganya harus
> dicatat, dan penarikan kembali salah satu bisa merambat ke kesimpulan yang
> berdiri di atasnya — yang persis dibutuhkan §19.7 dan §19.19.

> 🛑🛑 **Tetapi rantai ini KEHILANGAN dua mata rantai yang justru menjadikan
> §18.21 istimewa — `Transformation` dan `Policy`.**
>
> | | §18.21 (naskah 22) | §19.26 (naskah 23) |
> |---|---|---|
> | | Insight → Evidence → Source → **Transformation** → Model → Agent → **Policy** | Insight → Evidence → Paper → Dataset → Experiment → Model → Agent |
>
> Keduanya tujuh mata. Yang hilang tepat dua yang dicatat sebagai alasan §18.21
> berbintang empat:
>
> - **`Transformation`** — *"mata rantai yang hampir selalu hilang, dan yang
>   paling sering menjadi tempat kesalahan"*. Di Phase 19 ia bahkan lebih
>   dibutuhkan: antara naskah asli dan simpul graf ada OCR, penguraian, deteksi
>   bagian, dan ekstraksi entitas (§19.4, tujuh langkah) — dan **B-37** / [#134](../../issues/134) mencatat
>   tidak satu pun diverifikasi. Kesalahan yang lahir di situ tidak terlihat
>   pada `Paper` maupun pada `Model`.
> - **`Policy`** — *"belum pernah ada di rantai provenance mana pun di repo
>   ini"*, dan ia yang menjawab **"atas dasar aturan apa ini boleh sampai ke
>   saya"**. Untuk fase yang punya §19.22 (Ethics) dan §19.23 (`Biosecurity`,
>   `Dangerous Capability`), justru inilah tempat ia paling berguna.
>
> ⇒ Ini pola **daftar yang menyusut antar-naskah** yang sudah berulang (**H-8**,
> `Edit` di **E-74**, empat direktori **E-129**): sesuatu yang benar di satu
> naskah tidak otomatis terbawa ke naskah berikutnya. ⭐ Perbaikannya nol biaya
> — **satu rantai sembilan mata** yang memuat keduanya, sebab tak ada yang
> bertentangan di antara dua daftar ini. Lihat **E-146** / [#135](../../issues/135).

---

## §19.27 — Research Timeline

```
Idea → Hypothesis → Literature → Experiment → Simulation → Analysis
   → Writing → Publication
```

> HumanVerse menjadi **project manager penelitian**.

---

> ⭐⭐ **Menjadikan penelitian sebagai lini masa yang punya keadaan adalah
> gagasan yang benar dan jarang dibangun.** Yang menghabiskan waktu peneliti
> bukan berpikir melainkan **melacak di mana tiap utusan berada** — dan
> §19.31 memberi tabel `research_timeline` dan `research_projects` untuk itu.

> 🛑🛑 **Tetapi urutan delapan langkah ini BERTENTANGAN dengan dua bagian lain
> di naskah yang sama — dan keduanya membalik urutan, bukan menggeser.**
>
> **(1) `Hypothesis` sebelum `Literature`.** §19.2 memberi kebalikannya:
>
> ```
> Question → Literature Retrieval → Evidence Extraction → Knowledge Graph
>    → Gap Detection → Hypothesis Generation
> ```
>
> §19.2 menempatkan hipotesis **sesudah** bukti, celah, dan graf — dan itu yang
> dicatat sebagai kekuatan terbesarnya: novelty diperiksa **sebelum** hipotesis
> dibuat. §19.27 menempatkan hipotesis di langkah kedua, **sebelum literatur
> dibaca sama sekali**.
>
> Bedanya bukan gaya. Hipotesis yang lahir sebelum literatur akan mengarahkan
> pembacaan literaturnya — itu bentuk paling murni dari bias konfirmasi, dan
> §19.9 (`Bukan mengarang`) serta §19.8 (Gap Detection) keduanya kehilangan
> gunanya kalau jawabannya sudah ada sebelum pencarian dimulai.
>
> **(2) `Experiment` sebelum `Simulation`.** §19.13 membuka dengan kalimat
> **"Simulation sebelum eksperimen"** — prinsip yang sama dengan §16.26
> (`Code → Simulation → Safety Test → Hardware`), yang naskah 20 tetapkan
> sebagai urutan wajib dan yang dicatat sebagai satu-satunya yang mencegah
> cedera fisik. §19.27 membaliknya.
>
> Dan pembalikan itu paling berat justru di tempat §19.15 hidup: **menjalankan
> eksperimen fisik lebih dulu, lalu mensimulasikannya**, adalah urutan yang
> menjadikan simulasi sebagai penjelasan setelah kejadian alih-alih penyaring
> sebelum kejadian.
>
> ⇒ Tiga rantai untuk satu proses (§19.2 · §19.13 · §19.27), dua di antaranya
> saling membalik. Ini bentuk **E-141** ([#130](../../issues/130)) — empat urutan
> untuk satu tangga cakupan — pada sumbu proses. ⭐ Yang benar sudah jelas dan
> ditulis naskah ini sendiri: **§19.2 adalah urutannya**, dan §19.27 seharusnya
> lini masa **status** dari rantai yang sama, bukan rantai kedua.

> ⚠️ **Dan tidak ada `Ethics Review` maupun `Peer Review` di lini masa** —
> padahal §19.22 menyebut dirinya wajib dan §19.21 ada di naskah yang sama.
> `Publication` berdiri sebagai langkah terakhir tanpa satu pemeriksaan pun di
> antaranya. Lihat **C-29** / [#131](../../issues/131).

---

## §19.28 — Domain Modules

| Domain | Modul | | Domain | Modul |
|---|---|---|---|---|
| AI | ML Lab | | Physics | Physics Lab |
| Robotics | **Robot Lab** | | Biology | Bio Lab |
| Medicine | **Health Lab** | | Economics | Econ Lab |
| Materials | Material Lab | | Climate | **Climate Lab** |

---

> ⭐ **Modul per domain adalah pengakuan yang benar bahwa metode penelitian
> tidak seragam.** Protokol biologi, materi, dan ekonomi menuntut struktur
> variabel, ukuran, dan kontrol yang berbeda — dan §19.12 tidak bisa
> mewakilinya sendirian.

> 🛑 **Tetapi tiga dari delapan modul menduplikasi FASE yang sudah ada, bukan
> menambah domain baru.**
>
> | Modul | Sudah ada sebagai |
> |---|---|
> | `Health Lab` | **Phase 17** seluruhnya (`health-bio/`, 56 bagian) |
> | `Robot Lab` | **Phase 16** seluruhnya (`robotics/`, 35 bagian) |
> | `Climate Lab` | `Climate Agent` §18.18, dan `climate` sebagai sumber §18.4 |
>
> Ini bukan tumpang tindih nama melainkan tumpang tindih **isi**: sebuah *"Health
> Lab"* yang merancang eksperimen kesehatan berdiri di atas data yang §17.4 dan
> §17.5 atur dengan sangat ketat, sementara §19.3 menaruh `Disease` dan `Gene`
> di graf riset tanpa aturan yang setara.
>
> ⭐ Dan §19.1 — bagian *"Posisi dalam Arsitektur HumanVerse"* — **kosong**,
> sehingga tidak ada satu tempat pun di naskah ini yang menyatakan hubungan
> keduanya. Bagian yang kosong itu justru bagian yang menjawab ini
> (**G-18** / [#137](../../issues/137)).

---

## §19.29 — AetherScan Research Lab

```
WiFi CSI → Signal Processing → Occupancy → Pose Research
   → Digital Twin → Simulation → Paper
```

---

> 🛑🛑 **AetherScan NAIK PANGKAT LAGI — satu naskah sesudah ia diturunkan, dan
> kali ini ia mendapat direktori di dalam pohon inti.**
>
> §18.13 menyatakan: *"AetherScan nantinya dapat menjadi salah satu **spatial
> sensing provider**, bukan bagian inti HumanVerse."* Itu dicatat sebagai butir
> **F** berbintang empat, dengan alasan yang masih saya pegang: ia **keputusan
> pemilik yang MENGURANGI cakupan** — jenis yang paling jarang muncul di repo
> yang setiap naskahnya menambah satu fase.
>
> Satu naskah kemudian, §19.30 memberi **`scientific-discovery/labs/aetherscan/`**
> — direktori bernama, sederet dengan `ai/`, `robotics/`, `bio/`, dan
> `materials/` — dan §19.29 memberinya pipeline tujuh langkah tersendiri.
>
> ⇒ **Ini pelajaran H-8 dalam bentuk terbaliknya.** H-8 mencatat: sesuatu yang
> **dipulihkan** satu naskah bisa **hilang lagi** di naskah berikutnya. Di sini:
> sesuatu yang **diturunkan** satu naskah **kembali naik** di naskah berikutnya.
> ⇒ Aturan yang sama berlaku pada keduanya: **keputusan yang memperkecil cakupan
> juga perlu diperiksa ulang di naskah berikutnya** — ia tidak lebih tahan
> daripada keputusan yang memperbesar.
>
> ⚠️ Saya mencatat ini juga sebagai koreksi atas penilaian saya sendiri: butir
> **F** itu ditulis sebagai penutupan, dan ternyata belum tertutup. Lihat
> **E-147** / [#136](../../issues/136).

> ⭐ **Yang benar-benar bagus tetap ada di pipeline-nya:** `Occupancy` berdiri
> **sebelum** `Pose Research`, dan itu urutan penelitian yang jujur — menghitung
> keberadaan orang jauh lebih mudah dan lebih dulu terpecahkan daripada
> memperkirakan postur. Sebuah rencana riset yang menaruh yang mudah lebih dulu
> menghasilkan hasil yang bisa diterbitkan lebih awal, dan itu yang menopang
> sisanya.

> 🛑 **Tetapi rantai ini menyentuh C-22 tanpa menyebutnya.** `WiFi CSI → Pose`
> adalah penginderaan tubuh manusia tanpa perangkat yang dikenakan dan tanpa
> garis pandang. **C-22** ([#102](../../issues/102)) sudah menandai
> `breathing detection` sebagai Level 3–4, dan **B-31**
> ([#107](../../issues/107)) menandai `wifi_csi` sebagai deret waktu yang
> membanjiri basis data. Di sini keduanya kembali sebagai **program penelitian**,
> dengan `Paper` di ujungnya — yang berarti datanya dikumpulkan dari orang
> sungguhan, di ruangan sungguhan.
>
> §19.22 memeriksa `human subjects` dan `consent`; §19.23 memberi `Human
> Subjects` sebagai kategori. **Keduanya ada, dan tidak satu pun berdiri di
> rantai ini** — lihat **C-29**. Ini contoh paling konkret di seluruh naskah
> tentang mengapa penjadwalan `S19.10` menjadi masalah: laboratorium yang
> pertama kali dipakai pemiliknya sendiri adalah yang mengumpulkan data tubuh
> manusia.
