# 258 — §19.7–§19.9 Contradiction Detection, Research Gap Detection & Hypothesis Generation

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.7 — Contradiction Detection

> Paper A: *"Method X improves accuracy."* · Paper B: *"Method X does not
> improve accuracy."*

```
Claims → Semantic Comparison → Contradiction → Evidence Review
```

> Status: `supported · contradicted · unresolved · mixed evidence`

---

> ⭐⭐⭐⭐ **`mixed evidence` sebagai status KELIMA yang berdiri sendiri adalah
> penyempurnaan nyata atas §18.23 — dan ia menutup kekurangan yang saya sendiri
> tidak lihat satu naskah lalu.**
>
> §18.23 memberi `UNRESOLVED` dan itu dicatat sebagai butir **F** berbintang
> lima: pertama kalinya sistem boleh **berhenti tanpa jawaban**. Tetapi
> `UNRESOLVED` mencampur dua keadaan yang berbeda secara mendasar:
>
> | | Artinya | Yang harus dilakukan |
> |---|---|---|
> | **`unresolved`** | belum cukup bukti untuk memutuskan | **cari bukti lagi** |
> | **`mixed evidence`** | bukti yang cukup, dan ia **memang terbelah** | **jangan cari lagi — laporkan pembelahannya** |
>
> Perbedaan itu menentukan tindakan yang berlawanan, dan menyatukannya akan
> membuat sistem terus mencari untuk pertanyaan yang jawabannya *"tergantung"*.
> Di sains, kelas kedua itu bukan pengecualian melainkan keadaan biasa.

> ⭐⭐ **Dan `Evidence Review` ditaruh SESUDAH `Contradiction`, bukan
> sebelumnya.** Urutan itu berarti sistem **mendeteksi dulu, menilai kemudian**
> — sehingga pertentangan tidak hilang di tahap penyaringan karena salah satu
> sumbernya kebetulan berperingkat rendah. Sistem yang menilai lebih dulu akan
> menyembunyikan pertentangan dengan membuang pihak yang lemah, dan justru
> pertentangan itu informasinya.

> ⚠️ **Tetapi ini mesin kontradiksi KEDUA, dan kosakata statusnya berbeda dari
> yang pertama.** §18.23 memberi `Conflict detected` + `UNRESOLVED`; §19.7
> memberi empat status bernama. Keduanya akan menilai klaim yang sama ketika
> sebuah temuan ilmiah masuk World Model. Bersama `Evidence Ranking` yang kini
> bertiga (**E-146** / [#135](../../issues/135)), ini kelas mesin yang sama diimplementasikan dua kali
> dengan kosakata berbeda. ⭐ Yang benar: **empat status §19.7 menjadi
> kosakata tunggalnya** — ia lebih kaya, dan §18.23 tinggal memakainya.

> ⚠️ **`Semantic Comparison` sebagai satu-satunya langkah pembanding
> menyembunyikan kesulitan sebenarnya.** *"Method X improves accuracy"* dan
> *"Method X does not improve accuracy"* hanya bertentangan **kalau keduanya
> berbicara tentang tugas, data, dan ukuran yang sama** — dan §19.5 sudah
> mencatat bahwa `Result: 92%` diambil tanpa konteksnya. Dua klaim yang berbeda
> ruang lingkupnya akan terbaca sebagai pertentangan, dan itu jenis positif
> palsu yang paling merusak kepercayaan pada mesin seperti ini. Prasyaratnya
> ada di §19.12 (`Independent`/`Dependent Variable`, `Control`) — ia tinggal
> dipakai di sini.

---

## §19.8 — Research Gap Detection

> AI mencari: `area kurang diteliti · hubungan belum diuji · dataset belum
> tersedia · metode belum dibandingkan`
>
> Contoh: *"Belum banyak studi yang menggabungkan WiFi sensing dengan Digital
> Twin untuk monitoring indoor."*

---

> ⭐⭐⭐ **Empat jenis celah itu bukan satu hal yang dipecah empat — keempatnya
> ditemukan dengan cara yang berbeda, dan itu yang membuat daftarnya berguna.**
>
> `hubungan belum diuji` ditemukan dari **struktur graf** (dua simpul tanpa tepi
> di antaranya, padahal keduanya terhubung ke simpul yang sama);
> `metode belum dibandingkan` dari **matriks metode × dataset yang berlubang**;
> `dataset belum tersedia` dari **`limitation` yang §19.5 ekstrak**;
> `area kurang diteliti` dari kerapatan. Empat cara, satu keluaran — dan
> masing-masing bisa diperiksa benar-salahnya secara terpisah.

> 🛑🛑 **Tetapi celah tidak bisa dibedakan dari kegagalan yang tidak
> diterbitkan — dan mesin ini akan menunjuk ke sana dengan percaya diri.**
>
> *"Belum banyak studi yang menggabungkan A dengan B"* punya dua sebab yang
> tidak bisa dibedakan dari literatur saja:
>
> 1. **belum ada yang mencoba** — celah sungguhan, layak diteliti;
> 2. **sudah dicoba, hasilnya nol, dan tidak terbit** — bukan celah, melainkan
>    jawaban yang tidak sampai ke rak.
>
> Yang kedua adalah bias publikasi, dan ia **sistematis, bukan acak**: hasil nol
> jauh lebih jarang terbit daripada hasil positif. ⇒ Mesin yang membaca
> literatur terbit dan menyimpulkan *"belum diteliti"* akan **paling percaya
> diri justru di tempat yang sudah terbukti buntu**, dan mengarahkan orang ke
> sana. Untuk sebuah fitur yang naskahnya sebut *"sangat penting"* dan yang
> memberi masukan langsung ke §19.9, itu bukan kekurangan kecil.
>
> ⭐ Bahan penawarnya ada di naskah ini dan tinggal disambungkan: §19.4 sudah
> menarik **`datasets` dan `code repositories`** — percobaan yang gagal sering
> meninggalkan jejak di sana meski papernya tak pernah ada; **`registry
> pra-registrasi`** dan **preprint** (`arXiv` sudah di daftar) memuat hasil nol
> jauh lebih sering daripada jurnal. Yang perlu dinyatakan minimum: **celah
> dilaporkan dengan alasan mengapa ia dianggap celah**, dan `absence of
> evidence` tidak pernah disajikan sebagai `evidence of absence`. Lihat
> **B-37** / [#134](../../issues/134).

> ⭐ **Contohnya sendiri jujur pada dirinya:** *"Belum **banyak** studi"* —
> bukan *"belum ada"*. Pilihan kata yang benar, dan yang menunjukkan pemiliknya
> sadar batasnya. Yang perlu dilakukan tinggal menjadikannya aturan, bukan
> kebetulan gaya menulis.

---

## §19.9 — Hypothesis Generation Engine

> **Bukan mengarang.**

```
Evidence → Knowledge Graph → Pattern → Hypothesis Candidates → Ranking
```

> Output: `Hypothesis` · `Confidence` · `Novelty` · `Evidence` · `Assumptions`

---

> ⭐⭐⭐⭐ **`Assumptions` sebagai keluaran yang berdiri sendiri adalah hal
> terbaik di bagian ini, dan belum pernah ada di dua puluh tiga naskah.**
>
> Sebuah hipotesis selalu berdiri di atas hal-hal yang dianggap benar tanpa
> diuji — dan **hipotesis yang gugur biasanya gugur karena asumsinya, bukan
> karena isinya**. Menyuruh mesin menuliskan asumsinya berarti bagian yang
> paling mungkin salah menjadi **bagian yang paling terlihat**, dan orang yang
> membacanya bisa membantah di tempat yang benar.
>
> Ia juga menyambung langsung ke §19.11: asumsi adalah tempat `confounders`
> §19.12 bersembunyi, dan eksperimen yang dirancang tanpa mengetahuinya akan
> menguji hal yang salah.

> ⭐⭐ **Dan `Evidence` dibawa bersama hipotesisnya** — bukan hipotesis dulu,
> pembenaran kemudian. Itu yang menjadikan *"bukan mengarang"* bisa diperiksa
> alih-alih dijanjikan: hipotesis tanpa daftar bukti **tidak bisa dibentuk** oleh
> pipeline ini.

> ⚠️ **Tetapi `Novelty` diwarisi langsung dari §19.8, berikut titik butanya.**
> Skor kebaruan dihitung dari *"belum ada di literatur"* — dan §19.8 tidak bisa
> membedakan itu dari *"sudah dicoba dan gagal"*. ⇒ **Hipotesis yang paling
> tinggi skor `Novelty`-nya justru yang paling mungkin sudah terbukti buntu.**
> Dua bagian berurutan, dan kekeliruan yang satu memperkuat yang lain alih-alih
> saling mengoreksi.
>
> ⭐ Yang menahannya sebagian: `Evidence` dan `Assumptions` dibawa serta, jadi
> pembacanya punya bahan untuk curiga. Yang perlu ditambahkan: **`Novelty` dan
> `Confidence` tidak boleh dijumlahkan menjadi satu peringkat** — hipotesis yang
> *baru* dan hipotesis yang *didukung bukti* adalah dua daftar yang berbeda, dan
> `Ranking` yang menggabungkannya akan menaikkan yang baru-tapi-lemah ke atas.
> Bentuk yang benar sudah dipakai §18.20 (**Trust Vector**, menolak satu angka)
> dan §17.36 (*"accuracy saja tidak cukup"*).

> ⚠️ **`Pattern` sebagai satu-satunya jembatan dari graf ke hipotesis
> mengembalikan pertanyaan yang tangga kausal jawab.** Pola dalam graf adalah
> korelasi struktural; hipotesis adalah klaim tentang **sebab**. §18.9 memberi
> lima tingkat, §17.9 memberi empat (**E-138** / [#124](../../issues/124)), dan
> §19.10 satu bagian kemudian memberi `abductive reasoning` — yang justru
> mekanisme yang benar untuk lompatan ini. Ketiganya belum saling menyebut.
