# 243 — §17.35–§17.41 Model Registry, Evaluation, Bias Engine, Safety Kernel, Emergency, Explainability & Audit

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.35 — Health Model Registry

```
Health Model Registry
├── Sleep · Activity · Recovery
├── Nutrition · Anomaly · Forecasting
```

Setiap model: **version · training_data · metrics · bias · limitations ·
approval · deployment.**

---

> ⭐⭐⭐ **`limitations` dan `approval` sebagai FIELD WAJIB di registry adalah dua
> hal yang tidak pernah ada di manifest mana pun sepanjang dua puluh satu
> naskah.**
>
> Manifest agent sudah enam versi (**H-22**, **E-110**) dan tidak satu pun
> pernah memuat *apa yang model ini tidak bisa lakukan* maupun *siapa yang
> menyetujui pemakaiannya*. Untuk model kesehatan keduanya wajib: sebuah model
> tidur yang dilatih pada satu jenis jam tangan punya batas yang harus terbawa
> ke mana pun keluarannya pergi.
>
> ⭐ `approval` juga yang membuat §17.25 (*Health Safety Agent di governance
> layer*) punya sesuatu untuk dilakukan: menyetujui adalah tindakan governance,
> dan ia sekarang punya tempat di skema.

> ⚠️ **Pipeline ekstraksi rekam medis §17.28 TIDAK terdaftar di sini** —
> padahal ia model yang keluarannya paling sulit diperiksa. Enam model terdaftar
> semuanya bekerja pada sinyal; yang bekerja pada **teks klinis** tidak ada.
> Lihat **C-26** / [#118](../../issues/118).

---

## §17.36 — Health Model Evaluation

Metric: **sensitivity · specificity · precision · recall · calibration · false
positive · false negative · subgroup performance · robustness · drift.**

> Untuk sistem kesehatan, **accuracy saja tidak cukup.**

---

> ⭐⭐⭐⭐ **Ini daftar metrik evaluasi model yang PERTAMA dan satu-satunya di
> seluruh repo — dan isinya benar, termasuk yang biasanya dilupakan.**
>
> Dua puluh naskah sebelumnya memakai kata *accuracy* dan *confidence* tanpa
> pernah menyebut satu metrik yang bisa dihitung. Di sini ada sepuluh, dan tiga
> di antaranya adalah yang membedakan evaluasi serius dari evaluasi
> formalitas:
>
> | Metrik | Kenapa ia yang menentukan |
> |---|---|
> | **calibration** | model yang mengatakan *"70 % yakin"* harus benar sekitar 70 % dari waktu. Tanpa kalibrasi, seluruh `confidence` di dua puluh satu naskah adalah hiasan — dan **B-10**/**§9.34** sudah menuntutnya |
> | **false negative** | untuk deteksi kesehatan, yang terlewat lebih mahal daripada yang salah alarm — dan hampir tidak pernah muncul di dasbor produk |
> | **drift** | tubuh berubah, perangkat berganti, musim berganti. Model yang benar tahun lalu tidak otomatis benar sekarang |
>
> ⭐ Dan kalimat *"accuracy saja tidak cukup"* adalah penolakan langsung terhadap
> satu-satunya angka yang biasanya dilaporkan. Untuk kejadian yang jarang,
> akurasi tinggi bisa dicapai dengan tidak pernah mendeteksi apa pun.

> ⚠️ **Yang belum ada: ambangnya.** Sepuluh metrik tanpa satu nilai minimum
> berarti semua model lolos. Ini pola **E-112** (*Definition of Done tanpa
> angka*) dan **A-32** ([#112](../../issues/112), lima besaran keselamatan robot
> tanpa angka) pada sumbu ketiga. ⭐ Bedanya: di sini bahannya sudah lengkap —
> tinggal satu nilai minimum per metrik per model, dan `approval` §17.35 adalah
> tempat memeriksanya.

---

## §17.37 — Health Bias Engine

Harus mengevaluasi apakah model bekerja berbeda pada: **age groups · sex ·
device types · activity levels · data availability.**

> **Jangan membuat model yang terlihat bagus secara agregat tetapi buruk pada
> kelompok tertentu.**

---

> ⭐⭐⭐⭐ **Ini bagian yang paling saya tidak duga ada, dan ia menutup keberatan
> yang belum pernah saya tulis karena belum ada tempatnya.**
>
> Model kesehatan yang dilatih pada data yang tidak seimbang gagal secara
> sistematis pada kelompok yang kurang terwakili — dan gagalnya **tidak
> terlihat** pada angka agregat. Untuk sinyal optik seperti PPG, perbedaan
> perangkat dan karakteristik fisik penggunanya berpengaruh nyata, dan
> `device types` di daftar ini mengakuinya.
>
> ⭐ **`data availability` sebagai sumbu bias adalah yang paling tajam dan
> paling jarang dipikirkan:** orang yang perangkatnya sering lepas, yang tidak
> tidur dengan jam tangan, atau yang tidak mencatat makanannya akan **selalu**
> mendapat kesimpulan yang lebih lemah. Sistem lalu bekerja paling baik untuk
> orang yang paling patuh mengumpulkan data — dan itu bukan kelompok yang acak.
>
> Ia juga melengkapi `subgroup performance` §17.36: yang satu metrik, yang lain
> daftar sumbu yang harus diperiksa.

---

## §17.38 — Health Safety Kernel

```
Health AI → Safety Classifier → Risk Engine → Evidence Check → Policy
→ Response
```

Kategori: **INFO · TRACKING · WELLNESS · LOW-RISK GUIDANCE ·
CLINICAL-RELEVANT · URGENT · EMERGENCY.**

> Semakin tinggi risikonya, semakin kuat **escalation.**

---

> ⭐⭐⭐⭐ **`Risk Engine` KEMBALI ke rantai — untuk pertama kalinya sejak §11.14,
> setelah TUJUH rantai berturut-turut kehilangannya.**
>
> Butir **E-117** ([#93](../../issues/93)) mencatat empat rantai Phase 14 tanpa
> titik tahan; **E-124** ([#106](../../issues/106)) menambahkan §15.22;
> **E-130** ([#111](../../issues/111)) menambahkan §16.18 dan §16.13, dan
> mencatat bahwa **kata "risk" tidak muncul satu kali pun di seluruh naskah 20**.
>
> §17.38 mengembalikannya, dan menambahkan sesuatu yang belum pernah ada:
> **`Evidence Check` sebagai gerbang.** Sebuah keluaran kesehatan tidak lolos
> kalau buktinya tidak memadai — dan §17.26 (empat tingkat bukti, termasuk
> `Unknown`) adalah yang memberinya isi.
>
> ⭐⭐ **Tujuh kategori dengan escalation berjenjang** juga menyelesaikan hal
> yang `Confirmation` sendirian tidak bisa: untuk keluaran **informasi**,
> pertanyaan yang benar bukan *"boleh atau tidak"* melainkan **seberapa keras
> ini boleh disampaikan dan ke mana ia harus diteruskan**. Tangga
> `INFO → EMERGENCY` menjawab itu, dan §17.39 memberi ujungnya.
>
> Ini rantai keselamatan terbaik di seluruh dua puluh satu naskah.

> ⚠️ **Yang masih perlu:** batas antar-kategori (apa yang menjadikan sesuatu
> `CLINICAL-RELEVANT` alih-alih `WELLNESS`), dan **siapa yang berhak
> memindahkannya** — karena menurunkan kategori adalah cara termudah membuat
> peringatan berhenti muncul. `approval` §17.35 dan Health Safety Agent §17.25
> adalah tempat yang benar untuk menjawabnya.

---

## §17.39 — Emergency Escalation

```
Potential Emergency → Safety Verification → User Alert → Emergency Guidance
→ Emergency Contact / Service
```

> Tindakan eksternal harus mengikuti **izin, hukum, dan konfigurasi pengguna.**

---

> ⭐⭐⭐ **`Safety Verification` SEBELUM `User Alert` adalah urutan yang benar,
> dan ia melindungi dari kerugian yang paling mungkin terjadi.**
>
> Peringatan darurat palsu bukan gangguan kecil: ia menakuti orang, dan
> peringatan palsu yang berulang mengajari orang mengabaikan yang sungguhan.
> Memverifikasi lebih dulu adalah bentuk `false positive` §17.36 yang ditegakkan
> di runtime, bukan hanya diukur.
>
> ⭐ Dan `User Alert` mendahului `Emergency Contact / Service` — **orangnya tahu
> lebih dulu sebelum orang lain tahu**. Untuk sistem yang bisa menghubungi pihak
> luar atas nama seseorang, itu urutan yang menentukan.

> ⚠️ **Tetapi rantai ini berakhir pada tindakan yang menyentuh PIHAK KETIGA, dan
> kalimat penutupnya menyerahkannya pada tiga hal sekaligus.** *"Izin, hukum,
> dan konfigurasi pengguna"* — ketiganya benar, dan ketiganya belum punya
> bentuk. Butir **C-19** ([#81](../../issues/81)) dan **C-21**
> ([#95](../../issues/95)) sudah mencatat bahwa penerima pesan agent tidak pernah
> menyetujui apa pun; di sini penerimanya adalah kontak darurat atau layanan
> darurat, dan **kesalahan punya biaya nyata bagi keduanya**.
>
> Yang minimum perlu diputuskan: **kontak darurat didaftarkan lebih dulu dan
> tahu bahwa ia terdaftar** · **layanan darurat tidak pernah dihubungi otomatis
> tanpa keputusan yang dinyatakan di muka** · dan `Safety Verification` punya
> ambangnya sendiri, bukan ambang yang sama dengan §17.38.
>
> ⚠️ **Dan ini rantai untuk darurat MEDIS.** Risiko kesehatan mental §17.17
> bukan hal yang sama, dan memakai jalur ini untuknya bisa memperburuk. Lihat
> **C-25** / [#115](../../issues/115).

---

## §17.40 — Health Explainability

```
Insight → Evidence → Confidence → Limitations → Recommended Next Step
```

> **Insight:** Recovery Anda lebih rendah dari baseline.
> **Evidence:** tidur lebih pendek + aktivitas tinggi.
> **Confidence:** sedang.
> **Limitasi:** data wearable tidak menggambarkan seluruh kondisi tubuh.
> **Saran:** pertimbangkan recovery day.

---

> ⭐⭐⭐⭐ **Ini contoh keluaran terlengkap di seluruh repo — dan `Limitasi` yang
> menyatakan batas ALATNYA SENDIRI adalah kalimat yang hampir tidak pernah
> ditulis produk mana pun.**
>
> *"Data wearable tidak menggambarkan seluruh kondisi tubuh"* mengakui, di dalam
> keluaran yang dibaca pengguna, bahwa sistemnya melihat sebagian kecil saja.
> Itu penerapan paling jujur dari `Observed ≠ Certain` (naskah 16), dan ia
> muncul di permukaan tempat orang benar-benar membacanya — bukan di
> dokumentasi.
>
> Lima baris ini juga menjadikan §17.18 (`Human Explanation` sebagai langkah
> pipeline) punya bentuk konkret, dan ia lebih lengkap dari kartu persetujuan
> §14.60 karena memuat **batas**, bukan hanya risiko dan keterbalikan.

> ⚠️ **`Confidence: sedang` adalah label, sementara §14.62 sudah memberi angka
> (`confidence < 0.6`) dan §17.32 menyimpan `0.93`.** Tiga bentuk untuk satu
> besaran — angka di penyimpanan, ambang berupa angka di kontrak otonomi, label
> di antarmuka. Menampilkan label kepada pengguna benar; yang perlu ditulis
> adalah **pemetaannya**, karena tanpa itu *"sedang"* akan berarti hal berbeda
> di tiap layar. Bertaut [#34](../../issues/34).

---

## §17.41 — Health Audit Trail

Catat: **Who · What · Why · Which data · Which model · Which version · Which
agent · Which policy · Which recommendation.**

---

> ⭐⭐⭐ **Sembilan kolom, dan `Which model` + `Which version` adalah dua yang
> §14.56 belum punya — keduanya wajib untuk kesehatan.**
>
> §14.56 sudah memberi *who initiated · who delegated · which capability · which
> policy · which risk*, dan saya catat bahwa mencatat **aturan yang berlaku**
> adalah yang membedakan jejak yang bisa dipertanggungjawabkan dari jejak yang
> hanya bisa dibaca.
>
> Model dan versinya menambahkan sumbu yang khas fase ini: ketika sebuah
> rekomendasi ternyata salah, pertanyaannya bukan hanya *"aturan mana yang
> mengizinkannya"* melainkan **"model versi berapa yang menghasilkannya, dan
> apakah model itu masih dipakai"**. Tanpa versi, satu perbaikan model membuat
> seluruh riwayat berhenti bisa dijelaskan.
>
> ⭐ Digabung `health_access_logs` §17.43 dan *"melihat siapa yang mengakses"*
> §17.5, ini satu-satunya tempat di repo di mana **pembacaan** dicatat, bukan
> hanya penulisan.

> ⚠️ **Yang belum ada: berapa lama jejak ini disimpan, dan apakah ia ikut
> terhapus.** §17.29 memberi `retention: user_controlled` dan
> `deletion: enabled` untuk data kesehatan; jejak audit biasanya justru yang
> **tidak boleh** dihapus. Itu persis tabrakan yang **C-9**
> ([#22](../../issues/22)) buka sejak naskah 4, dan Phase 17 adalah tempat ia
> paling mahal dibiarkan terbuka.
