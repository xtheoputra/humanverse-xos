# 173 — §10.27–§10.29 Privacy Architecture, On-Device Intelligence & Model Router

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.27 — Privacy Architecture

> Multimodal layer merupakan salah satu bagian **paling sensitif**. Terutama:
> **Camera · Microphone · Location · Wearable · Home Sensors · Documents ·
> Voice · Video**

Maka **Permission + Consent + Purpose + Retention + Encryption + Access
Control** harus menjadi **mandatory**.

```
Camera Permission          Microphone
├── Never                  ├── Never
├── Once                   ├── Once
├── While using            └── While using
└── Always
```

---

> ⭐ **Enam kewajiban itu adalah Fase 8 yang dipanggil kembali dengan benar** —
> dan `Purpose` termasuk di dalamnya, yang berarti **B-22** / [#59](../../issues/59)
> berlaku penuh pada data persepsi. ⚠️ Tapi blok `privacy` di objek kanonik
> §10.3 hanya punya `classification` dan `retention`; `purpose` tidak ada di
> sana. Daftar di sini dan skema di §10.3 harus disamakan.

> 🛑 **`Always` adalah opsi izin yang tidak pernah ada di empat belas naskah —
> dan ia justru ditambahkan karena fitur naskah ini membutuhkannya.**
>
> | Sumber | Pilihan |
> |---|---|
> | naskah 4 §15 | *Allow once* · *Allow while using* · *Deny* |
> | naskah 12 §8.37 | `Camera: Ask` |
> | **naskah 14 §10.27** | Never · Once · While using · **Always** |
>
> *"While using"* berarti kamera hidup saat aplikasi dibuka. Tetapi §10.11
> mengukur **90 menit** duduk, §10.25 mengukur **118 menit**, dan §10.22
> menuntut pengulangan **30 hari** — tak satu pun bisa dicapai dengan *while
> using*. Fitur-fitur itu **hanya berjalan pada `Always`**.
>
> Jadi opsi paling invasif tidak muncul sebagai pilihan tambahan; ia muncul
> sebagai **prasyarat**. Itu perlu dinyatakan terbuka, karena pengguna yang
> memilih *While using* akan mendapati separuh fitur diam tanpa penjelasan.

> ⭐ **Mikrofon TIDAK mendapat `Always` — dan itu kemungkinan besar disengaja
> dan benar.** Mikrofon yang selalu hidup adalah garis yang berbeda di mata
> hampir semua orang. ⚠️ Tapi asimetrinya perlu ditulis sebagai keputusan,
> bukan dibiarkan tampak seperti kelalaian daftar — dan §10.9 menyebut suara
> sebagai *"interface utama"*, yang menuntut wake word (§10.28) yang sendiri
> menuntut mikrofon mendengar terus-menerus di perangkat.
>
> Jalan keluarnya sudah ada di §10.28: **wake word diproses di perangkat, dan
> tidak ada yang keluar sampai ia terpicu.** Itu perbedaan antara *mendengar*
> dan *merekam*, dan ia harus dinyatakan supaya asimetri ini masuk akal.

> ⚠️ **Location tidak punya daftar izin sendiri**, padahal ia disebut di baris
> pertama sebagai salah satu yang paling sensitif, ada di Level 3 klasifikasi
> data, punya event `LocationChanged` (§10.30), dan bisa disimpulkan lewat
> jalur lain tanpa izin lokasi (`Acoustic Scene Classification` §10.8, `GPS`
> §10.20, `spatial.locate()` §10.26).

> ⚠️ **`Home Sensors` menyebut rumah untuk pertama kalinya sebagai kategori.**
> Rumah bukan milik satu orang. Lihat **C-17** / [#75](../../issues/75).

---

## §10.28 — On-Device Intelligence

> Tidak semua data harus dikirim ke cloud.

```
Device                          Cloud
├── Lightweight Vision          ├── Advanced Reasoning
├── Wake Word                   ├── Long-term Memory
├── VAD                         ├── Knowledge
├── Basic OCR                   └── Large Models
├── Sensor Processing
└── Privacy Filtering
```

Prinsip:

> ## Process locally whenever practical.

---

> ⭐⭐⭐ **Ini pembagian on-device/cloud paling konkret di empat belas naskah,
> dan ia mengubah bentuk A-4/A-14 / [#6](../../issues/6).**
>
> Butir **A-14** mencatat bahwa naskah 4 §41/§42 menempatkan On-device AI dan
> Federated ML di **V5**, sehingga **V0–V4 tetap diproses di cloud** — sebuah
> keputusan besar yang belum pernah dinyatakan ke calon pengguna. Butir
> **C-15** menambahkan bahwa §8.13 menyebut privacy-preserving AI sebagai
> *"differentiator"* tanpa menyebut versinya.
>
> Enam butir di kolom Device menjawabnya dengan pembagian yang bisa dibangun.
> **`Privacy Filtering` di perangkat** khususnya: itu berarti penyaringan
> terjadi **sebelum** apa pun meninggalkan alat.
>
> 🛑 **Dan untuk kamera serta mikrofon, ini bukan optimasi — ini prasyarat.**
> Mengirim bingkai kamera rumah mentah ke cloud untuk dianalisis adalah persis
> hal yang tidak boleh dilakukan sistem seperti ini. Artinya §10.5–§10.11
> **tidak bisa dibangun sebelum §10.28 ada**, bukan sesudahnya. Urutan itu
> perlu ditulis, karena §10.37 menempatkan Vision di **M10.2** dan
> tidak menempatkan on-device di milestone mana pun.

> ⚠️ **On-device menuntut aplikasi di perangkat, dan itu belum ada.** Tidak ada
> aplikasi mobile, dan V0 tidak memuatnya. Jadi seluruh kolom Device menunggu
> sesuatu yang belum dijadwalkan — yang membuat pertanyaan **A-14** (*kapan
> janji privasi ditepati*) tetap terbuka meski bentuknya kini jauh lebih jelas.

---

## §10.29 — Model Router

> HumanVerse membutuhkan **modality-aware model routing**.

```
Input → Modality Detection → Task Classification → Model Router
```

| Tugas | Model |
|---|---|
| OCR | OCR model |
| Object detection | Vision model |
| Speech | ASR model |
| Reasoning | LLM |
| Embedding | Embedding model |
| 3D | Spatial model |

> Tidak semua masalah harus diberikan kepada LLM. Ini akan menghemat **Cost ·
> Latency · Energy**.

---

> ⭐⭐ **Model Router KEMBALI — dan itu menjawab separuh E-79 /
> [#69](../../issues/69).**
>
> Butir itu mencatat bahwa pohon `intelligence/` §9.38 membuang empat folder
> monorepo naskah 5, dan **`model-router/`** yang paling berat: ia jawaban
> **B-2**/**H-6** (biaya inferensi berlipat), dan naskah 13 justru memperkuat
> kebutuhannya lewat §9.2 dan tiga jalur §9.20 — lalu menghapus foldernya.
>
> §10.29 mengembalikannya sebagai bagian, dan §10.34 memberinya folder
> `multimodal/model-router/`. Kalimat penutupnya sama persis dengan semangat
> §9.2: *"tidak semua masalah harus diberikan kepada LLM"*.
>
> ⚠️ **Tapi sekarang ada dua perutean yang berbeda, dan hanya satu yang punya
> rumah:**
>
> | | Memilih berdasarkan | Sumber |
> |---|---|---|
> | **Modality routing** | jenis masukan — gambar → vision, suara → ASR | §10.29 ✅ punya folder |
> | **Effort routing** | berat pertanyaan — *Fast · Cognitive · High-stakes* | §9.20 ❌ tidak punya folder |
>
> Keduanya perlu, dan keduanya menghemat biaya lewat jalan berbeda:
> yang pertama mencegah LLM dipakai untuk pekerjaan yang bukan miliknya; yang
> kedua mencegah LLM besar dipakai untuk pertanyaan yang ringan.
>
> Menempatkan router di bawah `multimodal/` juga janggal, karena tabel §10.29
> sendiri memuat baris **`Reasoning → LLM`** — yang tidak multimodal sama
> sekali. Tempat yang benar kemungkinan besar bersama Cost Engine (naskah 4
> §48–§49), bukan di dalam salah satu konsumennya. Sisa **E-79** tetap terbuka:
> `behavior-model/`, `preference-model/`, dan `personalization/` masih hilang.

> ⭐ **`Energy` sebagai biaya yang dihitung adalah yang pertama kali disebut.**
> Empat belas naskah menghitung Cost dan Latency; energi baru muncul di sini —
> dan ia relevan justru karena §10.28 memindahkan pekerjaan ke perangkat, di
> mana baterai adalah anggaran yang nyata.
