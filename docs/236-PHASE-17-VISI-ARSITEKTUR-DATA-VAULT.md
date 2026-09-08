# 236 — §17.1–§17.5 Visi, Arsitektur, Health Data Sources, Klasifikasi & Health Vault

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Prinsip pembuka

> **HumanVerse tidak boleh menjadi "AI dokter yang serba tahu".**
>
> HumanVerse harus menjadi **Personal Health Intelligence System** yang
> mengumpulkan data, memahami pola, mendeteksi perubahan, membantu pengguna
> memahami kondisi mereka, melakukan simulasi gaya hidup, dan membantu
> **koordinasi dengan profesional kesehatan**.

---

> ⭐⭐⭐ **Ini pengaman pemilik yang KETUJUH berturut-turut — dan yang pertama
> diletakkan di KALIMAT PEMBUKA, bukan di penutup bagian.**
>
> Enam sebelumnya (§8.46 · §11.63 · §12 · §13.32 · §14.64 · §15.10/§15.16 ·
> §16.12) semuanya datang **sesudah** kemampuannya digambarkan. Di sini
> batasannya ditetapkan **sebelum** satu bagian pun ditulis, dan seluruh naskah
> lalu dibangun di dalamnya.
>
> Perbedaannya bukan gaya penulisan. Batasan yang datang belakangan harus
> melawan rancangan yang sudah jadi; batasan yang datang lebih dulu **membentuk**
> rancangannya. Buktinya terlihat di seluruh naskah ini: §17.7 (*State ≠
> diagnosis*), §17.16 (*indikator, bukan membaca pikiran*), §17.20 (*bukan
> prediksi penyakit*), §17.27 (*tidak mengambil alih keputusan klinis*), dan
> penutupnya (*jangan langsung dibuat sebagai "medical AI"*). Lima pengulangan
> dari satu prinsip yang sama, di lima tempat yang berbeda.

> ⭐ **Dan kata "koordinasi dengan profesional kesehatan" menempatkan sistem ini
> pada peran yang benar sejak awal: penghubung, bukan pengganti.**

---

## §17.1 — Visi

> Phase 17 membuat HumanVerse mampu membangun **Personal Health Digital Twin.**
>
> Bukan sekadar *"Heart rate kamu 82."* Tetapi:
>
> *"Dalam 30 hari terakhir, ketika durasi tidurmu turun, recovery dan aktivitas
> harianmu cenderung ikut turun."*
>
> Perbedaannya adalah **raw data → context → pattern → intelligence.**

---

> ⭐⭐ **Contoh pembandingnya dipilih dengan tepat, dan kata yang menyelamatkannya
> adalah "cenderung".**
>
> Kalimat itu menyatakan **hubungan yang teramati** tanpa mengklaim sebab. Ia
> juga menyebut **jendela waktunya** (30 hari), yang berarti pembacanya tahu
> seberapa banyak bukti yang ada di baliknya. Bandingkan gaya kalimat yang
> berulang di naskah-naskah sebelumnya (*"Anda akan menyelesaikan 40 % lebih
> banyak"*, **B-24**) — di sini tidak ada angka akibat yang dikarang.

> ⚠️ **Tapi "cenderung ikut turun" tetap perlu dua hal yang belum disebut di
> sini: berapa kali itu terjadi, dan seberapa kuat.** §17.9 memberi jawabannya
> (empat tingkat bukti) dan §17.40 memberi bentuk penyajiannya
> (*Evidence · Confidence · Limitations*), jadi bahannya ada — tinggal
> dinyatakan bahwa **tiap kalimat pola membawa jumlah kejadian dan kekuatannya.**

---

## §17.2 — Arsitektur Utama

```
HUMAN → Health Data Sources
        ├── Wearables / Sensors
        ├── Medical Records
        └── Lifestyle Data
              ↓
        Health Data Gateway
              ↓
        Health Data Engine
        ├── Health Knowledge Graph
        └── Health Memory
              ↓
        Health Digital Twin
              ↓
        Bio Intelligence
        ├── Monitoring  ├── Prediction  └── Simulation
              ↓
        Decision Intelligence → Recommendation → HUMAN
```

---

> ⭐⭐⭐ **Diagram arsitektur ini ADA dan LENGKAP — dan itu perbaikan nyata
> setelah dua naskah berturut-turut kehilangan bagiannya.**
>
> **G-15** ([#103](../../issues/103)) mencatat §15.1 *"Arsitektur Besar
> SpatialOS"* kosong; **G-16** ([#113](../../issues/113)) mencatat §16.33
> *"Integrasi dengan HumanVerse"* kosong. Naskah ini memberi arsitektur
> pembukanya **dan** empat bagian integrasi terisi penuh (§17.47–§17.50).
> Pola dua naskah tidak berlanjut.

> ⭐⭐ **Rantainya berbentuk LINGKARAN: `HUMAN → … → HUMAN`.** Manusia adalah
> sumber datanya dan penerima hasilnya — dan tidak ada cabang yang keluar ke
> pihak lain di dalam diagram ini. Untuk fase yang menangani data paling
> sensitif, arsitektur yang tertutup pada dirinya sendiri adalah bawaan yang
> benar; §17.27 (integrasi klinis) lalu menjadi **jalan keluar yang harus dibuka
> sengaja**, bukan lubang yang harus ditutup.

> ⚠️ **`Health Data Gateway` sebagai satu-satunya pintu masuk adalah bentuk yang
> benar — tapi diagram ini tidak menunjukkan gerbang di jalur KELUAR.** Antara
> `Decision Intelligence` dan `Recommendation` tidak ada `Safety` maupun `Risk`,
> padahal §17.38 memberi Health Safety Kernel yang lengkap. Kemungkinan besar
> ia diasumsikan berada di dalam `Decision Intelligence` — tapi rantai yang
> digambar lengkap akan dibangun seperti yang digambar, dan itu pelajaran yang
> sudah tujuh kali muncul (**E-117** · **E-124** · **E-130**).

---

## §17.3 — Health Data Sources

**Wearables** — smartwatch · fitness tracker · heart-rate monitor · sleep
tracker · smart ring. Data: `heart rate · HRV · steps · activity · sleep ·
calories · respiratory metrics · temperature · SpO₂ jika perangkat menyediakan
· workout data`.

**Smartphone** — activity · movement · screen time · location · sleep-related
patterns · interaction patterns.

> Tetapi semua harus berdasarkan **permission**.

**Lifestyle** — makanan · olahraga · tidur · pekerjaan · belajar · stressors ·
social activity · travel · routines.

> Ini penting karena **kesehatan tidak hanya berasal dari biometrik**.

---

> ⭐⭐ **"SpO₂ jika perangkat menyediakan" adalah satu klausa kecil yang
> menyatakan sikap yang benar terhadap sensor.**
>
> Ia mengakui bahwa **kemampuan perangkat berbeda-beda**, dan karenanya sistem
> tidak boleh mengasumsikan sinyal yang mungkin tidak ada. Itu prasyarat untuk
> §17.32 (`quality`) dan untuk **B-14** ([#26](../../issues/26)) — kegagalan
> senyap ketika satu sinyal mati. ⚠️ Yang perlu menyusul: **aturan yang sama
> berlaku untuk SEMUA sinyal**, bukan hanya SpO₂ — HRV, suhu, dan respirasi
> semuanya opsional pada sebagian besar perangkat.

> ⭐ **"Kesehatan tidak hanya berasal dari biometrik"** adalah kalimat yang
> membedakan naskah ini dari produk kebugaran mana pun, dan ia yang membuat
> Phase 9 (Behavior Model) dan Phase 12 (Life Simulation) punya alasan berada di
> bawah fase ini.

> 🛑 **Tapi `location` dan `screen time` dari ponsel adalah data yang paling
> jauh dari kesehatan dan paling dekat dengan pengawasan.** *"Semua harus
> berdasarkan permission"* benar dan tidak cukup: **C-3**
> ([#21](../../issues/21)) sudah mencatat bahwa izin yang diminta ketika
> fiturnya membutuhkan akan selalu diberikan. Yang membedakan di sini adalah
> **`purpose`** (§8.10) — dan §17.4 memang mewajibkannya per data. Yang perlu
> ditulis: **lokasi masuk Health Vault hanya untuk tujuan yang dinyatakan
> (misalnya konteks olahraga), tidak sebagai riwayat perjalanan.**

---

## §17.4 — Health Data Classification

```
PUBLIC → PERSONAL → SENSITIVE → HEALTH-SENSITIVE → HIGHLY-SENSITIVE
```

Health data harus memiliki:

```yaml
data:
  owner:      purpose:     sensitivity:
  source:     timestamp:   retention:
  consent:    processing_location:
```

---

> ⭐⭐⭐ **Delapan field itu adalah metadata data paling lengkap di dua puluh satu
> naskah — dan `processing_location` belum pernah ada di mana pun.**
>
> `owner` menjawab **C-10** ([#40](../../issues/40)) untuk kelas data ini;
> `purpose` menegakkan §8.10; `retention` menjawab bagian dari **C-9**
> ([#22](../../issues/22)); `consent` per data menjawab **B-22**/#59.
> Dan **`processing_location`** menjadikan janji §17.31 (*on-device*) sebagai
> **field yang bisa diperiksa**, bukan niat arsitektur — sesuatu yang §15.29 dan
> §16.21 belum punya.

> 🛑 **Tetapi tangga lima tingkat ini adalah taksonomi sensitivitas KEDUA, dan
> ia bertabrakan dengan §8.16 yang punya EMPAT.**
>
> §8.16 memberi **Level 1–4** dan menempatkan data kesehatan di Level 3–4;
> §7.2 memberi contohnya. Tangga baru ini memakai **nama**, bukan angka, dan
> punya lima anak tangga. Tidak ada pemetaan di antara keduanya.
>
> Akibatnya konkret: aturan yang sudah ditulis memakai angka — larangan scope
> untuk agent `third_party` ([`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> aturan 6), **G-11** (tool persepsi menyentuh Level 3 dan kandidat Level 4),
> **C-22** ([#102](../../issues/102), `breathing detection` sebagai Level 3–4).
> Semuanya berhenti bisa dievaluasi begitu ada dua tangga.
>
> Ini pola **E-77** (dua tangga 0–4 dengan arti berlawanan) yang sudah ditutup
> sebagai **H-21**, muncul lagi pada sumbu yang berbeda. Perbaikannya murah
> sekarang: **satu tangga, dan `HEALTH-SENSITIVE`/`HIGHLY-SENSITIVE` menjadi
> Level 3 dan Level 4** — atau pemetaan eksplisit satu baris. Lihat **E-133** /
> [#117](../../issues/117).

---

## §17.5 — Health Data Vault

```
Personal Data Vault
└── Health Vault
    ├── Biometrics  ├── Activity      ├── Sleep
    ├── Nutrition   ├── Medical Records └── Health Insights
```

> User dapat: **melihat data · export · delete · revoke access · melihat siapa
> yang mengakses.**

---

> ⭐⭐⭐ **"Melihat siapa yang mengakses" adalah kemampuan KELIMA yang belum
> pernah ada di daftar Privacy Center mana pun — dan ia yang paling sulit
> ditambahkan belakangan.**
>
> **H-4** menutup *"tidak ada jalan keluar data"* dengan §43: **View · Edit ·
> Export · Delete · Revoke**. Naskah ini mengganti `Edit` dengan **`melihat
> siapa yang mengakses`** — dan yang kedua menuntut sesuatu yang jauh lebih
> dalam: **setiap pembacaan dicatat**, bukan hanya setiap penulisan. §17.43
> memberinya tabel (`health_access_logs`) dan §17.41 memberi bentuk catatannya.
>
> Untuk data kesehatan itu bukan kemewahan: pertanyaan yang benar-benar
> ditanyakan orang bukan *"apa yang kalian simpan"* melainkan **"siapa saja yang
> sudah melihatnya"** — dan itu pertanyaan yang **A-30**
> ([#92](../../issues/92)) dan §14.33 juga coba jawab dari sisi graf.

> ⚠️ **Tapi `Edit` hilang dari daftar, dan itu penggerusan yang sudah tercatat
> dua kali** (**E-74** — naskah 12 membuang `Edit` dari Privacy Center; §14.60
> mengembalikannya sebagai tombol persetujuan). Untuk data kesehatan, `Edit`
> justru paling dibutuhkan: **catatan tidur yang salah karena jam tangan
> terpasang longgar hanya bisa diperbaiki penggunanya**, dan §17.19 menuntut
> sistem membedakan *sensor anomaly* dari *human anomaly* — koreksi manusia
> adalah sumber kebenaran termurah untuk pembedaan itu.

> ⚠️ **`Health Insights` disimpan di dalam vault yang sama dengan data
> mentahnya.** Itu benar untuk penyimpanan, tetapi keduanya punya sifat berbeda
> pada penghapusan: menghapus data mentah tidak otomatis menghapus kesimpulan
> yang sudah ditarik darinya. **C-9** ([#22](../../issues/22)) berlaku di sini
> dalam bentuk yang paling tajam — dan §17.29 `deletion: enabled` belum
> menyatakan yang mana.
