# 242 — §17.29–§17.34 Health Privacy, Federated Intelligence, On-Device AI, Data Quality, Bio Signal & Feature Store

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.29 — Health Privacy Architecture

```yaml
health:
  default_access: deny
  sharing:        explicit_consent
  retention:      user_controlled
  export:         enabled
  deletion:       enabled
```

Dan:

```
Agent → Permission → Purpose → Policy → Health Data
```

> Bukan: `Agent → Database`

---

> ⭐⭐⭐⭐ **`default_access: deny` adalah bentuk yang C-23 minta sejak naskah 19,
> dan ia akhirnya ditulis pemilik sendiri.**
>
> Butir **C-23** ([#104](../../issues/104)) mencatat bahwa policy ruangan §15.23
> berbentuk **daftar perangkat yang dimatikan**, sehingga setiap sensor baru
> otomatis diizinkan sampai ada yang ingat menambahkannya. Usulnya: *policy
> menyebut yang DIIZINKAN, apa pun yang tidak disebut ditolak.*
>
> §17.29 menulis persis itu, untuk kelas data yang paling membutuhkannya. Ia
> juga sejalan dengan tiga bentuk yang sudah ada: `deny` eksplisit §14.21 ·
> lima larangan bawaan §14.37 · **R4 = `DENY`** (**H-21**).

> ⭐⭐⭐ **Dan rantai `Agent → Permission → Purpose → Policy → Health Data`,
> dengan `Bukan: Agent → Database` ditulis di bawahnya, adalah penegasan
> arsitektur yang paling jelas di dua puluh satu naskah.**
>
> Ia mengulang **H-19** ([#62](../../issues/62)) — *agent tidak mengambil data
> sama sekali; Context Engine yang membangun paketnya* — untuk kelas data
> kesehatan, dan menambahkan `Purpose` sebagai langkah tersendiri di antara izin
> dan kebijakan. Itu menjadikan §8.10 (*purpose limitation*) sebagai **gerbang
> berjalan**, bukan aturan tertulis.
>
> ⚠️ Yang perlu menyusul satu kalimat, dan **B-22**/[#59](../../issues/59) sudah
> memberi bentuknya: penegakan `purpose` adalah satu operasi himpunan —
> **`data.purpose ⊆ consent.purpose`**.

> ⚠️ **`deletion: enabled` belum menyatakan apa yang ikut terhapus.** Vault
> §17.5 menyimpan `Health Insights` di samping data mentahnya; menghapus yang
> mentah tidak otomatis menghapus kesimpulan yang sudah ditarik. **C-9**
> ([#22](../../issues/22)) berlaku di sini pada bentuknya yang paling tajam, dan
> jawabannya cuma perlu satu baris: **insight yang kehilangan sumbernya ikut
> terhapus, atau ditandai tidak lagi punya dasar.**

---

## §17.30 — Federated Health Intelligence

```
User Device → Local Training → Privacy Protection → Aggregated Model
```

> Data individual **tidak harus dikirim ke server.**
>
> Dapat dikombinasikan dengan: **federated learning · differential privacy ·
> secure aggregation.**

---

> ⭐⭐⭐ **Ini jalan keluar untuk B-22 yang belum pernah ada — dan ia
> menyelesaikannya tanpa meminta persetujuan tambahan atas data mentah.**
>
> Butir **B-22** / [#59](../../issues/59) mencatat bahwa `purpose limitation`
> §8.10 bisa mengunci Research Lab: data V0 yang dikumpulkan dengan
> `purpose: [personalization]` tidak bisa melatih model apa pun di Phase 5 tanpa
> menanyakan ulang persetujuan setiap pengguna, mundur ke belakang.
>
> Pembelajaran terfederasi mengubah pertanyaannya: yang dikirim bukan datanya,
> melainkan **perubahan model**. Itu tidak menghapus kebutuhan persetujuan —
> ikut serta tetap keputusan pengguna — tetapi ia membuat persetujuan itu jauh
> lebih mudah diberikan, karena yang diminta bukan lagi *"kirimkan data
> kesehatanmu"*.
>
> ⚠️ Yang tetap berlaku dari **B-22**: **`consents.kind = 'model_training'`
> sebagai persetujuan tersendiri**, dan aturan bahwa **menolaknya tidak
> mengurangi layanan**. Federasi mengubah biayanya, bukan haknya.

> ⚠️ **Tiga teknik disebut sebagai "dapat dikombinasikan", padahal hanya
> gabungan ketiganya yang memberi jaminan.** Federated learning sendirian
> **tidak** menjamin privasi — pembaruan model bisa membocorkan data
> pelatihannya. Yang memberi jaminan adalah *differential privacy* (dengan
> anggaran yang dinyatakan) dan *secure aggregation*. Kata *"dapat"* membuat
> ketiganya terbaca opsional; yang benar: **federated learning tanpa keduanya
> tidak boleh disebut pelindung privasi.**

---

## §17.31 — On-Device Health AI

```
Wearable → Edge AI → Health Signal → Privacy Filter → Cloud Intelligence
```

Contoh: **activity classification · basic anomaly detection · sensor quality ·
private voice processing.**

---

> ⭐⭐⭐ **Naskah KETIGA berturut-turut yang menaruh pemrosesan sensitif di
> perangkat — dan yang ini menambahkan langkah yang dua sebelumnya tidak
> punya: `Privacy Filter`.**
>
> §15.29 menyatakan *"edge melakukan processing sensitif"*; §16.21 menaruh
> `emergency` di edge. Keduanya menyatakan **di mana** sesuatu berjalan.
> §17.31 menambahkan **apa yang boleh lewat**: sebuah penyaring berdiri di
> antara sinyal dan cloud.
>
> Tiga naskah berturut-turut dengan prinsip yang sama sudah cukup untuk
> dituliskan sekali sebagai aturan proyek — dan **`processing_location` §17.4
> adalah field yang membuatnya bisa diperiksa**, bukan hanya diniatkan.

> ⭐⭐ **`private voice processing` di daftar contohnya menjawab langsung
> keberatan §17.16**, tempat `Voice signals` menjadi masukan Stress
> Intelligence. Yang perlu ditulis: **jurnal ikut di daftar yang sama** —
> §14.21 sudah menetapkan `deny: private.journal`, dan §17.16 memakainya sebagai
> masukan.

> ⚠️ **`Privacy Filter` tidak punya isi.** Ia satu-satunya komponen di rantai
> ini yang seluruh nilainya terletak pada aturannya, dan aturannya tidak ada.
> Daftar yang bisa langsung ditulis, dan semuanya sudah disebut di naskah ini:
> **sinyal mentah PPG/ECG · rekaman suara · teks jurnal · citra makanan · lokasi
> tidak melewati filter** — yang naik adalah keluarannya.

---

## §17.32 — Health Data Quality Engine

> Ini **wajib**, karena **wearable bisa salah.**

```
Raw Sensor → Validation → Calibration → Missing Data → Outlier Detection
→ Quality Score
```

```yaml
heart_rate:
  value: 82
  confidence: 0.93
  quality: 0.97
  source: smartwatch
```

---

> ⭐⭐⭐ **"Wearable bisa salah" ditulis sebagai ALASAN sebuah komponen ada, dan
> itu sikap yang membedakan sistem kesehatan dari produk kebugaran.**
>
> Contoh empat medannya juga tepat: `value` · `confidence` · `quality` ·
> `source` — dan **`confidence` terpisah dari `quality`** adalah pembedaan yang
> benar. *Quality* menyatakan seberapa baik **pengukurannya**; *confidence*
> seberapa yakin sistem pada **kesimpulannya**. Sinyal berkualitas tinggi bisa
> menghasilkan kesimpulan berkeyakinan rendah, dan sebaliknya.
>
> Ini juga melengkapi empat besaran yang naskah 16 rapikan (`value ·
> confidence · quality · volatility`): tiga di antaranya muncul di sini, dan
> `source` menggantikan `volatility` — yang masuk akal, karena laju peluruhan
> berbeda-beda per jenis sinyal biologis dan sebaiknya melekat pada jenisnya,
> bukan pada tiap pengukuran.

> ⭐⭐ **`Calibration` sebagai langkah di dalam pipeline** adalah yang **B-25**
> minta: kalibrasi sensor terhadap laporan pengguna, sehingga sensor yang
> *konsisten salah* tidak menjadi pola yang meyakinkan. Digabung dengan
> `Subjective Feedback` §17.11 dan pembedaan *sensor anomaly* §17.19, tiga
> bagian naskah ini menutup butir itu bersama-sama.

---

## §17.33–§17.34 — Bio Signal Processing & Bio Feature Store

```
Raw Signal → Filtering → Noise Removal → Feature Extraction → Signal Quality
→ Model
```

Sinyal: **PPG · accelerometer · gyroscope · temperature · ECG bila perangkat
menyediakan · respiratory signals.**

Feature: `resting_hr · hrv_baseline · sleep_duration · sleep_consistency ·
activity_load · recovery_score · training_load`

```
Raw Data → Features → Models
```

---

> ⭐⭐⭐ **Pemisahan `Raw Data → Features → Models` adalah satu-satunya
> arsitektur yang membuat B-34 bisa diselesaikan — dan naskah menulisnya
> sendiri.**
>
> Sinyal mentah PPG dan akselerometer berjalan pada puluhan sampai ratusan hertz;
> `resting_hr` dan `hrv_baseline` adalah **satu angka per hari**. Menyatakan
> keduanya sebagai lapisan yang berbeda berarti yang disimpan jangka panjang
> adalah lapisan kedua, dan yang mentah bisa hidup pendek di perangkat —
> persis bentuk yang §17.31 sediakan dan yang **B-31**
> ([#107](../../issues/107)) usulkan untuk CSI dan point cloud.
>
> Yang perlu ditulis satu baris: **sinyal mentah tidak masuk basis data pusat;
> retensinya jam, dan tempatnya perangkat.** Tanpa itu, `biometric_measurements`
> dan `hrv_measurements` §17.43 akan menampung deret waktu berfrekuensi tinggi
> di penyimpanan yang sama dengan `health_goals`. Lihat **B-34** /
> [#119](../../issues/119).

> ⭐ **"ECG bila perangkat menyediakan"** mengulang sikap yang benar dari §17.3
> (`SpO₂ jika perangkat menyediakan`) — dan untuk ECG ia lebih penting lagi,
> karena perangkat yang menyediakannya umumnya diatur sebagai alat kesehatan dan
> membawa kewajibannya sendiri.

> ⚠️ **`hrv_baseline` dan `resting_hr` adalah BASELINE yang §17.19 pakai, dan
> keduanya butuh waktu untuk terbentuk.** Feature store adalah tempat yang benar
> untuk menyimpan **sejak kapan** sebuah baseline berlaku dan **dari berapa
> banyak hari** ia dihitung — dua angka yang menentukan apakah *"deviasi dari
> baseline"* berarti apa-apa pada minggu pertama.

> ⚠️ **`recovery_score` dan `training_load` berada di feature store**, padahal
> keduanya **keluaran model** (§17.11, §17.12), bukan fitur turunan langsung.
> Menyimpan keluaran model sebagai masukan model lain adalah hal yang lazim dan
> berbahaya: kalau model recovery diperbarui, seluruh riwayat fitur berubah
> artinya. §17.35 sudah mewajibkan `version` per model — yang perlu ditambahkan:
> **fitur yang berasal dari model membawa versi model yang menghasilkannya.**
