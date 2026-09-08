# 244 — §17.42–§17.46 Event Architecture, Database, API, Repository & Health Intelligence Runtime

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.42 — Health Event Architecture

```
SleepStarted · SleepEnded · SleepQualityChanged
HeartRateRecorded · HRVRecorded
WorkoutStarted · WorkoutCompleted
RecoveryChanged
NutritionLogged · MealDetected
StressIndicatorChanged
HealthAnomalyDetected
HealthInsightGenerated · HealthRecommendationCreated
HealthConsentGranted · HealthConsentRevoked
```

---

> ⭐⭐⭐ **`HealthConsentGranted` dan `HealthConsentRevoked` sebagai event adalah
> yang membuat §17.5 (*"melihat siapa yang mengakses"*) dan §17.29
> (`retention: user_controlled`) bisa dibuktikan, bukan hanya dijanjikan.**
>
> Persetujuan yang hanya berupa baris di tabel bisa berubah tanpa jejak.
> Persetujuan sebagai **peristiwa** meninggalkan kapan ia diberikan, kapan
> dicabut, dan urutannya — dan itulah satu-satunya cara menjawab *"apakah data
> ini boleh dipakai pada saat ia dipakai"*, bukan hanya *"apakah ia boleh
> sekarang"*.
>
> ⭐ `HealthInsightGenerated` dan `HealthRecommendationCreated` sebagai event
> terpisah juga benar: kesimpulan dan saran adalah dua hal berbeda, dan yang
> kedua yang berakibat.

> 🛑 **Tetapi `SleepEnded` BENTROK LAGI dengan `spec/03` — dan ini persis
> tabrakan yang E-116 catat empat naskah lalu.**
>
> **E-116** mencatat bahwa §13.12 memberi 15 event PascalCase yang **delapan di
> antaranya sudah ada di [`../spec/03`](../spec/03-EVENT-CONTRACTS.md)**, dan
> tiga bukan sekadar beda huruf melainkan **kata kerja berbeda untuk kejadian
> yang sama**: `sleep.completed` ↔ **`SleepEnded`** · `meeting.completed` ↔
> `MeetingEnded` · `mood.logged` ↔ `MoodChanged`.
>
> `SleepEnded` muncul lagi di sini, tidak berubah. Artinya pelanggaran
> [#38](../../issues/38) yang **kedelapan** berturut-turut bukan hanya soal
> huruf: ia mengulang **tabrakan kosakata yang sudah diidentifikasi dengan
> namanya**, pada event yang sudah punya kontrak tertulis. Kalau keduanya
> dikodekan, satu malam tidur menghasilkan **dua event berbeda**. Lihat
> **E-135**.

> ⚠️ **`MealDetected` menyiratkan deteksi otomatis**, sementara `NutritionLogged`
> menyiratkan pencatatan manual. Keduanya wajar, tetapi §17.14 hanya menyebut
> jalur `food photo` dan `food log` — tidak ada bagian yang menjelaskan **dari
> mana `MealDetected` datang**. Kalau ia dari sensor atau pola, ia kesimpulan,
> dan **§17.7 menuntutnya dibedakan dari pengukuran.**

---

## §17.43 — Database

```
health_profiles · health_goals
biometric_measurements · heart_rate_measurements · hrv_measurements
sleep_sessions · activity_records · workout_sessions · training_loads
nutrition_logs · hydration_logs · recovery_states · stress_indicators
health_events · health_anomalies · health_insights · health_recommendations
medical_documents · medical_records
health_models · health_predictions · health_simulations
health_consents · health_access_logs
```

---

> ⭐⭐ **`health_consents` dan `health_access_logs` sebagai tabel tersendiri**
> adalah yang membuat §17.5 dan §17.29 punya tempat. **`health_access_logs`
> khususnya: ia satu-satunya tabel di seluruh repo yang mencatat PEMBACAAN.**

> ⭐ **`health_models`, `health_predictions`, dan `health_simulations` sebagai
> tabel** berarti keluaran model disimpan dengan model yang menghasilkannya —
> prasyarat untuk `Which model, which version` §17.41.

> 🛑 **Tetapi tiga tabel di daftar ini adalah deret waktu berfrekuensi tinggi,
> dan naskah menaruhnya sederet dengan `health_goals`.**
>
> `biometric_measurements` · `heart_rate_measurements` · `hrv_measurements` —
> ketiganya tumbuh dengan **waktu × frekuensi sensor**, bukan dengan perbuatan
> pengguna. Detak jantung yang dicatat tiap detik = **86.400 baris/hari** untuk
> satu orang satu sinyal; dengan lima sinyal dan retensi tahunan itu ratusan
> juta baris per pengguna.
>
> Pembandingnya sudah dua kali dipakai di repo ini: **§10.22** (`PersonDetected`
> 1 Hz ⇒ 2,6 juta baris/30 hari) dan **B-31** ([#107](../../issues/107),
> `wifi_csi` dan `point_clouds`). Basis data V0 adalah **PostgreSQL + Redis**
> (**H-12**).
>
> ⭐ Dan obatnya ada di naskah ini juga, di §17.34: **`Raw Data → Features →
> Models`**. Yang disimpan jangka panjang adalah **fitur** (`resting_hr`,
> `hrv_baseline` — satu angka per hari), sementara sinyal mentah hidup di
> perangkat dengan retensi jam (§17.31). Yang perlu ditulis: **ketiga tabel itu
> menyimpan agregat, bukan sampel mentah.** Lihat **B-34** /
> [#119](../../issues/119).

> ⚠️ **`health_insights` dan `health_recommendations` disimpan permanen tanpa
> aturan kedaluwarsa.** Kesimpulan kesehatan berumur — saran yang benar enam
> bulan lalu bisa keliru sekarang, dan §17.36 `drift` mengakui modelnya berubah.
> Bertaut **C-9** ([#22](../../issues/22)) dan catatan §17.29.

---

## §17.44 — API

```
POST /v1/health/data          GET  /v1/health/state
GET  /v1/health/sleep · activity · recovery
POST /v1/health/nutrition
GET  /v1/health/insights · anomalies
POST /v1/health/simulations · goals
GET  /v1/health/twin
POST /v1/health/consent       DELETE /v1/health/consent
```

---

> ⭐⭐⭐ **`POST` dan `DELETE /v1/health/consent` sebagai pasangan lengkap — dan
> ini perbaikan nyata atas dua naskah sebelumnya.**
>
> §15.26 memberi `POST /v1/aetherscan/start` **tanpa** pasangan yang
> menghentikannya, dan §15.26 maupun §16.29 sama-sama tidak punya endpoint untuk
> policy yang membatasi. Di sini pencabutan persetujuan punya alamatnya sendiri,
> dan itu satu-satunya cara `revoke access` §17.5 bisa dilakukan pengguna.

> ⚠️ **Tapi tidak ada endpoint untuk membaca maupun mengubah `health` policy
> §17.29**, dan tidak ada untuk `health_access_logs` — padahal *"melihat siapa
> yang mengakses"* adalah salah satu dari lima hak yang §17.5 janjikan. Tiga
> naskah berturut-turut memberi banyak endpoint untuk **bertindak** dan sedikit
> untuk **membatasi atau memeriksa**.

> ⚠️ **`/v1/…` lagi, bukan `/api/v1`** — separuh kedua [#38](../../issues/38),
> naskah **kedelapan** berturut-turut. Lihat **E-135**.

---

## §17.45 — Repository

```
health-bio/
├── data/ (ingestion · normalization · quality · integration)
├── biometrics/ (heart · hrv · sleep · respiratory · temperature)
├── activity/ · fitness/ · recovery/ · nutrition/ · hydration/
├── wellbeing/ · stress/
├── digital-twin/ · timeline/ · knowledge-graph/
├── intelligence/ (anomaly · forecasting · pattern · recommendation)
├── simulation/ · preventive/ · research/
├── medical/ (documents · records · integrations)
├── models/ (registry · training · serving)
├── agents/
├── safety/ · privacy/ · consent/ · audit/
├── edge/ · federated-learning/ └── sdk/
```

---

> ⭐⭐ **`consent/` dan `audit/` sebagai direktori tingkat pertama di dalam
> pohon ini** menunjukkan keduanya diperlakukan sebagai komponen, bukan sebagai
> lapisan lintas yang dititipkan. Untuk fase ini itu tepat.

> 🛑 **Tetapi `health-bio/` adalah pohon tingkat-atas KETUJUH kali H-10
> tergerus, dan empat direktori di dalamnya MENDUPLIKASI pohon yang sudah ada.**
>
> | Di dalam `health-bio/` | Sudah ada sebagai pohon tingkat-atas |
> |---|---|
> | `research/` (dan §17.51 memperluasnya) | `research/` — naskah 9 |
> | `simulation/` | `spatial-os/simulation/` · `robotics/simulation/` · Phase 12 |
> | `models/` | `intelligence/` · `data-platform/` |
> | `agents/` | `agents/` — naskah 2 |
>
> Ditambah `safety/` dan `privacy/` yang menjadikan pohon keamanan **tujuh**:
> `security/` · `agent-security/` · `spatial-os/safety/` ·
> `spatial-os/privacy/` · `robotics/safety/` · dan dua di sini. **E-127** dan
> **E-129** ([#109](../../issues/109)) sudah mencatat bahwa empat saja membuat
> aturan impor **§8.42** tidak punya satu sisi.
>
> **Sembilan naskah berturut-turut menyentuh struktur repo**, dan
> [#55](../../issues/55) menanyakan **aturan komposisi** justru supaya
> pertambahan berikutnya tidak perlu keputusan baru. Phase 18 sudah diumumkan.
> Lihat **E-134** / [#120](../../issues/120).

---

## §17.46 — Health Intelligence Runtime

```
Health Intelligence Runtime
├── Data Context   ├── Health Memory  ├── Health Twin
├── Bio Models     ├── Behavior Model ├── Risk Engine
├── Simulation     ├── Evidence Engine └── Safety Kernel
```

> Kemudian terhubung ke **Cognitive Runtime.**

---

> ⭐⭐⭐ **`Risk Engine`, `Evidence Engine`, dan `Safety Kernel` berada DI DALAM
> runtime, bukan di sampingnya — dan itu yang membuat §17.38 tidak bisa
> dilewati.**
>
> Sebuah gerbang yang berdiri di luar runtime bisa dilewati oleh komponen yang
> memanggil model langsung; gerbang yang menjadi bagian runtime tidak. Ini pola
> yang benar dan ia menjawab kekhawatiran **B-32** ([#110](../../issues/110)) —
> di Phase 16, Safety Kernel berada di sisi HumanVerse dari adapter ROS sehingga
> bisa dilewati. Di sini ia di dalam.
>
> ⭐ Dan `Behavior Model` dari Phase 9 muncul di daftar yang sama dengan
> `Bio Models` — itu penerapan kalimat §17.3 (*"kesehatan tidak hanya berasal
> dari biometrik"*) di tingkat runtime.

> ⚠️ **`Risk Engine` di sini vs `Risk Engine` §8.17 — apakah sama?** §8.17
> adalah mesin risiko **aksi** (`R0–R4`, **H-21**); yang ini menilai risiko
> **kesehatan** (tujuh kategori §17.38). Dua mesin dengan nama yang sama di
> runtime yang berbeda akan tertukar dalam kode. Bertaut catatan §17.18 dan
> usulnya: **satu diberi nama lain.**

> ⚠️ **"Health Intelligence Runtime" di sini vs "HealthOS" di §17.55** — dua
> nama untuk benda yang sama, di naskah yang sama, dan yang kedua sejajar dengan
> `HumanOS` dan `SpatialOS` secara penamaan. Setelah *"HumanOS"* dengan tiga
> arti (**E-114**) dan `WorkOS` yang muncul sekali di §15.19 lalu tidak pernah
> disebut lagi, ini calon berikutnya. Lihat **E-136**.
