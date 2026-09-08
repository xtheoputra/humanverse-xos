# 269 — §20.10–§20.13 Collective Intelligence, Distributed AI Network, Privacy-Preserving & Data Sovereignty

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh empat, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §20.10 — Collective Intelligence Layer

> `Human Intelligence + AI Intelligence + Scientific Intelligence +
> Organizational Intelligence + Collective Experience → Collective Intelligence`
>
> Tujuannya **bukan membuat semua orang berpikir sama**. Justru:
> **menggabungkan perspektif berbeda tanpa menghilangkan disagreement.**

---

> ⭐⭐⭐⭐⭐ **Kalimat itu menutup sisa terakhir G-17 — dan kini prinsipnya
> muncul di TIGA tempat berturut-turut.**
>
> **G-17** ([#121](../../issues/121)) mencatat `consensus` (§18.32 G18.8) menarik
> berlawanan dengan `UNRESOLVED` (§18.23), dan mengusulkan: *"konsensus hanya
> menyatukan hal yang sumbernya sepakat; ketidaksepakatan naik ke pengguna
> sebagai ketidaksepakatan."*
>
> | Naskah | Bentuknya |
> |---|---|
> | 23 | §19.17 `Consensus → **Remaining Disagreement**` sebagai keluaran |
> | **24** | **§20.10 sebagai PRINSIP**, dan **§20.28 sebagai DIREKTORI** (`collective-intelligence/disagreement/`) |
>
> Yang ketiga paling menentukan: **sebuah direktori bernama `disagreement/`
> menjadikan ketidaksepakatan sesuatu yang punya kode, bukan sesuatu yang
> disebut di paragraf.** Naskah 23 memberi bentuknya, naskah 24 memberinya
> tempat. ⇒ Bagian **G18.8** tetap satu-satunya yang belum diperbaiki.

> ⚠️ **Tetapi `Collective Experience` sebagai masukan kelima adalah kategori
> yang belum punya bentuk.** Empat lainnya punya sumber yang jelas (manusia,
> model, literatur §19, organisasi). Yang kelima adalah **pengalaman orang
> banyak** — dan tidak ada di seluruh repo yang menyatakan dari mana ia diambil,
> siapa yang menyumbang, atau apakah penyumbangnya tahu. §20.12 mengatur
> perjalanannya; yang belum ada adalah **apa ia sebenarnya**.

---

## §20.11 — Distributed AI Network

```
HumanVerse Core → Personal AI · Org AI · City AI → Local Node (masing-masing)
```

> Tiap node dapat memiliki: `local memory · local models · local agents ·
> **local policy** · local data`

---

> ⭐⭐⭐ **Menolak pemusatan untuk KEDUA kalinya, dan kali ini sampai ke tingkat
> node.** §18.14 menolaknya sebagai keputusan arsitektur; §20.11 memberi
> bentuknya. Simpul yang menyimpan memori, model, dan datanya sendiri
> menjadikan `processing_location` §17.4 bisa ditegakkan, bukan diniatkan.

> 🛑 **Tetapi `local policy` menciptakan pertanyaan yang §20.16 tidak bisa
> hindari: kebijakan siapa yang menang ketika dua node berbeda.**
>
> §20.16 menetapkan **Agent Constitution** sebagai *"governance layer
> tertinggi"* dengan sepuluh pasal. §20.11 memberi tiap node kebijakannya
> sendiri. Keduanya bisa hidup bersama **hanya kalau dinyatakan mana yang tidak
> bisa dilonggarkan secara lokal** — misalnya: kebijakan lokal boleh
> **memperketat**, tidak pernah **melonggarkan**, dan sepuluh pasal Konstitusi
> adalah lantai yang tidak bisa ditembus dari bawah.
>
> Tanpa aturan itu, `City AI` dengan `local policy` sendiri adalah jalan keluar
> yang sah dari Konstitusi — dan itu bentuk yang sama dengan **B-32**
> ([#110](../../issues/110)), tempat Safety Kernel berada di sisi yang salah dari
> adapter. Lihat **E-150** / [#140](../../issues/140).

---

## §20.12 — Privacy-Preserving Civilization Intelligence

> **Ini wajib.** Raw personal data **tidak boleh** menjadi bahan bakar
> centralized intelligence **secara default**.
>
> `Federated Learning · **Differential Privacy** · **Secure Aggregation** ·
> Data Minimization · Pseudonymization · Local Processing ·
> Confidential Computing`

```
PERSONAL DATA → LOCAL PROCESSING → AGGREGATED SIGNAL → FEDERATED NETWORK → GLOBAL MODEL
```

---

> ⭐⭐⭐⭐ **Tujuh mekanisme BERNAMA — dan dua di antaranya menjawab langsung
> B-36, yang ditulis dua naskah lalu.**
>
> **B-36** ([#126](../../issues/126)) mencatat §18.14 membagikan `model updates`
> dan `anonymous signals` **tanpa ambang peserta minimum maupun anggaran
> privasi**, dengan alasan: pembaruan model membawa jejak data yang melatihnya,
> dan *"anonim bukan sifat sebuah berkas"*. Usulnya: ambang jumlah peserta,
> **batas anggaran privasi**, dan `model updates` diperlakukan sebagai data.
>
> §20.12 memberi **`Differential Privacy`** (yang justru mekanisme anggaran
> privasi) dan **`Secure Aggregation`** (yang mewajibkan ambang peserta secara
> kriptografis). ⇒ **Kedua mekanisme yang diminta, disebut dengan namanya.**
>
> Ini kebiasaan yang sudah dua kali dicatat sebagai butir **F**: **memakai yang
> sudah ada alih-alih menamai kategori** (lima pustaka SLAM §15.6, ROS2 §16.22,
> sembilan sumber nyata §19.4).

> ⚠️ **Yang belum: satu pun ANGKA.** Privasi diferensial tanpa `epsilon` adalah
> nama tanpa jaminan — dan `epsilon` yang longgar memberi perlindungan yang
> hampir nol sambil tetap boleh disebut *differential privacy*. Begitu juga
> `Secure Aggregation` tanpa ambang peserta minimum. ⇒ **#126 belum bisa
> ditutup**; yang berubah adalah ia berhenti menjadi pertanyaan arsitektur dan
> menjadi pertanyaan parameter. Itu kemajuan besar, dan bukan penutupan.

> 🛑 **Dan kata *"secara default"* adalah satu-satunya kata di bagian ini yang
> membuka jalur lain — tanpa menyatakan jalurnya.**
>
> *"Tidak boleh … secara default"* berarti ada keadaan bukan-default. Siapa yang
> mengubahnya, atas dasar apa, dan apakah penggunanya tahu? Untuk bagian yang
> dibuka dengan **"Ini wajib"**, dua kata itu melemahkan seluruh kalimatnya.
> ⭐ Bentuk yang benar sudah ada di repo: §17.29 `default_access: deny` — dan
> yang membuatnya bekerja bukan kata *default*, melainkan bahwa **jalur
> pengecualiannya ditulis**.

---

## §20.13 — Human Data Sovereignty

> Setiap manusia mempunyai **Personal Data Vault**. Phase 20 menambahkan
> **Data Sovereignty Layer** — pengguna mengontrol: `Who · What · Why · When ·
> Where · **How long**`

---

> ⭐⭐⭐ **Enam sumbu ini adalah kendali paling lengkap yang pernah diberikan,
> dan `Why` adalah yang membedakannya dari daftar izin biasa.**
>
> **H-4** menutup *"tidak ada jalan keluar data"* dengan `View · Edit · Export ·
> Delete · Revoke` — kelimanya tentang **data**. §17.5 menambahkan *"melihat
> siapa yang mengakses"* — tentang **pembacaan**. Enam sumbu ini tentang
> **syarat akses**, dan `Why` menjadikannya penegakan `purpose` §8.10 di tangan
> penggunanya sendiri: izin yang diberikan untuk satu tujuan berhenti berlaku
> untuk tujuan lain, **dan pemiliknya bisa melihat tujuannya**.
>
> ⭐ `Where` juga menjadikan `processing_location` §17.4 sebagai **pilihan
> pengguna**, bukan hanya field yang bisa diperiksa — dan itu satu-satunya cara
> janji §20.11 (local node) berarti sesuatu bagi orang yang tidak membaca
> arsitektur.

> ⚠️ **Tetapi `How long` — retensi — dikendalikan pengguna, sementara tabel yang
> menyimpan datanya tidak punya kolomnya.**
>
> **B-35** ([#127](../../issues/127)) mencatat §18.28 tanpa satu pun kolom
> retensi; §19.31 juga; dan **§20.29 mengulanginya** — tiga puluh tabel, nol
> retensi. Sebuah kendali yang tidak punya tempat penyimpanan tidak bisa
> ditegakkan, dan **C-9** ([#22](../../issues/22)) sudah mencatat bentuk
> tajamnya: menghapus data mentah tidak otomatis menghapus kesimpulan yang
> ditarik darinya. Untuk `Civilization Twin` yang dibangun dari agregat, itu
> pertanyaan yang paling sulit dan paling perlu dijawab sebelum kode.

> ⚠️ **Dan kedaulatan ini berlaku untuk `Human` — tidak untuk `Family`,
> `Community`, atau `City`**, yang §20.6 jadikan tingkat kembaran. Enam sumbu
> mengandaikan **satu orang yang memutuskan untuk dirinya**; tidak ada bentuk
> untuk data yang menyangkut beberapa orang sekaligus. Lihat **C-30** / [#141](../../issues/141).
