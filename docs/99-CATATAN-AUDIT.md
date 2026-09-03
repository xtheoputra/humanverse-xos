# 99 — Catatan Audit & Keputusan Terbuka

> ⚠️ **Berkas ini BUKAN kata pemilik.** Isinya catatan, keraguan, dan
> pertanyaan dari sisi teknis. Sengaja dipisah supaya berkas `01`–`77` tetap
> murni merekam visi pemilik.
>
> Cara pakai: kalau pemilik memutuskan sebuah butir, keputusannya **naik** ke
> berkas visi yang sesuai, lalu butirnya turun ke bagian **H**.

> 📌 **Butir terbuka di berkas ini sudah jadi 30 GitHub Issue** dalam 3
> milestone. Baca issue-nya, jangan analisis ulang naskahnya.

Diperbarui: 3 September 2026 · Mencakup **lima naskah**:
**1 HumanOS** · **2 HumanVerse X** · **3 Phase 2 Enterprise Blueprint** ·
**4 Phase 3 AI-Native Human Ecosystem** · **5 Blueprint Engineering v1.0**.

| Bagian | Isi | Jumlah |
|---|---|---|
| [H](#h-sudah-diputuskan--ditutup) | **Sudah diputuskan / ditutup** | 14 |
| [A](#a-perlu-jawaban-pemilik) | Pertanyaan yang memblokir | 16 |
| [B](#b-risiko-teknis) | Risiko teknis | 17 |
| [C](#c-risiko-hukum--kepatuhan) | Risiko hukum & kepatuhan | 9 |
| [D](#d-celah-yang-belum-tertutup) | Celah yang belum tertutup | 5 |
| [E](#e-ketidakcocokan-antar-naskah) | **Ketidakcocokan antar-naskah** | 40 |
| [F](#f-yang-sudah-saya-periksa-dan-ternyata-benar) | Sudah diperiksa, ternyata benar | 19 |
| [G](#g-lubang-di-naskah-3-sendiri) | Lubang di naskah 3 sendiri | 3 |

---

## H. Sudah diputuskan / ditutup

Naskah keempat, naskah kelima, dan keputusan pemilik 3 September 2026 menutup
butir-butir ini. ⚠️ **H-8 dibatalkan** — lihat barisnya.

| # | Butir lama | Keputusan |
|---|---|---|
| **H-1** | **A-7 — nama resmi** | ✅ **`HumanVerse XOS`.** Diputuskan pemilik 3 Sep 2026; folder sudah diganti nama. ⚠️ Sisa pekerjaan: berkas naskah masih menulis *HumanOS* / *HumanVerse X*, dan **C-5 (cek merek & domain) tetap terbuka** — sekarang justru mendesak. |
| **H-2** | **A-2 — mana MVP-nya** | ✅ **V0 HumanVerse Foundation, target 4–6 minggu.** Auth · Profile · Goals · Habits · Daily Check-in · Mood · Journal · AI Coach · Basic Memory · Dashboard, dengan 4 agent (Orchestrator, Habit, Coach, Memory). Lihat [`75`](75-URUTAN-PEMBANGUNAN-V0-V6.md). Ini daftar tertutup pertama dalam empat naskah. |
| **H-3** | **D — manifest tidak pernah ditunjukkan** | ✅ Naskah 4 §11 memberi **manifest nyata pertama** (FashionAgent: purpose, capabilities, tools, memory read/write, risk_level). Lihat [`56`](56-AGENT-FACTORY.md). |
| **H-4** | **D — tidak ada jalan keluar data** | ✅ §43 Privacy Center: **View · Edit · Export · Delete · Revoke**, ditegaskan "first-class feature, bukan halaman legal". Lihat [`69`](69-PRIVACY-CENTER-VAULT-AUDIT.md). Tabrakannya dengan Immutable Log jadi butir baru **C-9**. |
| **H-5** | **B-7 — beban operasional** | ✅ **Diakui dan dilunakkan pemilik sendiri.** §58 memperingatkan over-engineering, §51 "untuk V0 jangan langsung Kubernetes — mulai Docker Compose", §38 "jangan langsung memakai semuanya pada V1". Risikonya tidak hilang, tapi tidak lagi diabaikan. |
| **H-6** | **B-8 — biaya inferensi berlipat** | ✅ §48 AI Cost Engine + §49 Model Router. Lihat [`71`](71-COST-ENGINE-DAN-MODEL-ROUTER.md). |
| **H-7** | **B-13 — self-improving agent sulit diaudit** | ✅ Sebagian. §45 menyimpan **audit metadata**, bukan chain-of-thought mentah; §47 memberi versi agent + skor + **automatic rollback**. Self-Improving Agents sendiri tidak diulang di naskah 4. |
| **H-8** | ~~E-5 — Grooming hilang di naskah 3~~ | ❌ **DIBATALKAN.** Grooming sempat kembali di registry naskah 4, lalu **hilang lagi** di daftar 22 agent naskah 5. Butir **E-5** dibuka kembali sebagai **E-35**. Ini pengingat: satu naskah memulihkan sesuatu bukan berarti sudah tetap. |
| **H-9** | **A-1 — angka liar di judul** | ✅ Artefak salin-tempel. Naskah 4 masih menyisakan angka `6` yang menempel di dua judul — juga dibuang dari dokumen rapi. |
| **H-10** | **E-27 — dua struktur repo** | ✅ Naskah 5 §4 **menggabungkan keduanya**: monorepo naskah 2 (`apps/ services/ agents/`) ditambah berkas wajib AI coding agent dari naskah 4 (`AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`, `SECURITY.md`), dan `adr/` menjadi `docs/decisions/`. Lihat [`83`](83-STRUKTUR-REPO-FINAL.md). |
| **H-11** | **E-2 / E-28 — Weather & Calendar: tool atau agent** | ✅ **Tool.** §13 menyebut "Calendar Tool" dan §14 mendaftarkan `weather.get`, `calendar.get`, `wardrobe.search`, `trend.search` di blok `tools:` manifest. Tidak ada WeatherAgent di daftar 22 agent. |
| **H-12** | **A-10 — Kafka *dan* Redis Streams sekaligus?** | ✅ **Empat penyimpanan, bukan enam.** §5 menetapkan PostgreSQL · Qdrant · Neo4j · Redis; **Kafka dan ClickHouse hilang**, antrean pindah ke Redis. Lihat **E-36**. |
| **H-13** | **A-18 — Phase 1/2/3 atau V0–V6** | ✅ **V0–V6.** Naskah 5 memakai tangga V dari awal sampai akhir (§1, §33) dan **tidak menyebut Phase 1/2/3 satu kali pun**. Phase 1–3 menjadi sejarah penyusunan, bukan rencana kerja. ⚠️ Butuh satu konfirmasi lisan dari pemilik sebelum dokumen lama diberi tanda. |
| **H-14** | **B-15 / B-1 — angka taksiran yang terlihat seperti fakta** | ✅ Mekanismenya ada: **Confidence Layer** §19 mewajibkan setiap kesimpulan membawa `confidence`, `evidence_count`, dan `last_updated`, dengan aturan *low confidence → **ask user***. Itu sekaligus jawaban cold start (**B-1**). ⚠️ Ambang High/Medium/Low dan cara menghitung `confidence` belum ada. Lihat [`90`](90-DIGITAL-TWIN-DAN-CONFIDENCE.md). |

---

## A. Perlu jawaban pemilik

Diurutkan dari yang paling menghambat.
**A-1, A-2, A-7, A-10, dan A-18 sudah pindah ke H.**

| # | Pertanyaan | Kenapa penting |
|---|---|---|
| **A-19** | ⚠️ **Sekarang LIMA model angka pengguna — memburuk, bukan membaik.** *Human Genome of Behavior* 6 skor · *Profile Engine* 5 atribut · *HumanState* **7 field** (naskah 5 membuang `mood`) · *Human Dashboard* 7 batang · *DigitalTwin* 8 model. Tidak satu pun saling merujuk, tidak satu pun punya rumus. | Ini akan **mengunci skema basis data** — tabel `profiles`, `memories`, dan state harian bergantung padanya. **Confidence Layer (H-14) menjawab cara MENYAJIKAN angka, bukan angka mana yang dipakai.** Engineering Spec tidak bisa ditulis sebelum ini dipilih. Lihat **E-34**. |
| **A-17** | ⚠️ **Diperjelas dan makin berat.** Naskah 5 §32 memecah V0 jadi **7 sprint** (Foundation → Identity → Human Core → Memory → AI → Intelligence → Product), dan §29 **menambah dua fitur V0** (Activity Tracking, Recommendation) — sementara targetnya tetap **4–6 minggu**. | 7 sprint dalam 4–6 minggu ≈ **4–6 hari per sprint**, termasuk Sprint 0 (repo, Docker, CI/CD) dan Sprint 4 (AI Gateway + Model Router + 3 agent). Ini klaim jadwal, bukan arsitektur — dan sekarang cakupannya bertambah tanpa waktunya bertambah. Lihat **E-40**. |
| **A-20** | 🆕 **Mental Wellness dan Lifestyle: dibuang atau ditunda?** Registry §12 berisi 14 agent dan **memulihkan** Grooming, Nutrition, Productivity — tetapi **Mental Wellness dan Lifestyle tetap tanpa agent** (padahal Lifestyle muncul lagi di §56). | Menyempitkan **A-8** dari empat modul jadi dua. Mental Wellness punya beban hukum tertinggi (**C-3**) — kalau memang dibuang, hapus dari `03-MODUL.md` supaya dokumen tidak berbohong. |
| **A-22** | 🆕 **Sampai level risiko berapa agent boleh bertindak otomatis?** §16 memberi Level 0–4 dan mewajibkan konfirmasi eksplisit di Level 4. Level 2 dan 3 belum ditetapkan default-nya. | *"Act selalu di bawah kontrol pengguna"* adalah janji pembuka naskah 4. Tanpa default yang tertulis, janji itu tidak bisa diuji. |
| **A-21** | 🆕 **Experiment Engine: berapa hari minimum, dan kapan sistem menolak menyimpulkan?** §35 memberi contoh 14 hari tanpa kelompok kontrol. | §36 sudah memisahkan Observation → Correlation → Hypothesis → Evidence → Conclusion. Yang belum ada adalah **ambangnya**. Lihat **B-16** dan **C-8**. |
| **A-13** | **Berapa lama menulis ~460 spesifikasi, dan siapa?** ⚠️ **Sebagian terjawab** oleh §53–§55. | Yang belum terjawab: apakah ~460 dokumen memang masih perlu ditulis semua, setelah [`77`](77-LANGKAH-BERIKUTNYA-BLUEPRINT-V1.md) meminta **satu** Blueprint Engineering v1.0 sebagai gantinya. |
| **A-8** | **Empat modul hilang di naskah 2 dan 3.** ⚠️ **Sebagian terjawab** — Nutrition dan Productivity kembali punya agent di §12. | Sisanya jadi **A-20**. |
| **A-14** | **Janji privasi ditunda.** ⚠️ **Sekarang eksplisit, bukan lagi tersirat.** §41/§42 menempatkan On-device AI dan Federated ML di **V5**, sementara §43/§44 menaikkan Privacy Center + Data Vault sebagai first-class sejak awal. | Artinya **V0–V4 tetap diproses di cloud**. Keputusan besar yang sekarang tertulis, tapi belum pernah dinyatakan ke calon pengguna. Kaitannya dengan **A-4**. |
| **A-4** | **Model AI cloud atau lokal?** | §40 menjawab arsitekturnya (LLM umum + model khusus + memori pengguna), tapi belum menjawab **data pengguna boleh keluar ke pihak ketiga atau tidak**. |
| **A-15** | **Marketplace pihak ketiga menyentuh data hidup pengguna. Model izinnya apa?** ⚠️ **Sebagian terjawab** — §11 `risk_level`, §14 memory policy per agent, §15 permission engine, §16 risk level. | Yang masih kosong justru bagian paling mahal: **proses review agent pihak ketiga, sandbox, perjanjian pemroses data, dan jalur banding**. |
| **A-12** | **Mana dokumen pertama?** ⚠️ **Berubah bentuk** — §77 meminta **Blueprint Engineering v1.0**, satu dokumen besar, bukan lima dokumen. | Usul saya tetap: **Knowledge Graph Ontology** jadi bab pertama blueprint, karena empat naskah memakai model graf dan model angka yang berbeda (**E-16**…**E-18**, **A-19**). |
| **A-16** | **Data Governance jadi Layer sendiri atau tidak?** ⚠️ **Isinya sudah ada** di §43–§45 dan sebagai kolom *Governance* di §56. | Tinggal memutuskan tempatnya. Lihat **G-3**. |
| **A-3** | Pasar & bahasa awal: Indonesia dulu, atau global sejak awal? | Contoh konteks di §2 memakai **Jakarta** — satu-satunya petunjuk di empat naskah, dan itu terlalu tipis untuk jadi keputusan. |
| **A-5** | Sumber data untuk **Trend Engine** dari mana? | §22 menjawab "Public Sources" dan memberi rumus, tapi **tidak menyebut satu sumber pun**. Bobot komponen dan definisi *User Relevance* juga kosong. |
| **A-11** | `apps/desktop/` dan `apps/admin-dashboard/` teknologinya apa? | Belum terjawab di empat naskah. |
| **A-6** | Tangga harga: **Team = "Family"** di atas **Elite = "Digital Twin"**. Sengaja? | [`76`](76-HUMANVERSE-ECONOMY.md) menambah pertanyaan baru: **bagi hasil** dengan developer dan partner di HumanVerse Economy. |

---

## B. Risiko teknis

| # | Catatan |
|---|---|
| B-12 | **Ratusan agen pada satu graf.** Tanpa aturan kepemilikan simpul dan penyelesaian konflik, graf akan saling menimpa. §13 memberi protocol antar-agent yang *authenticated, logged, traceable, permission-controlled* — itu mengatur **percakapan**, bukan **tulisan ke graf**. Risiko ini masih utuh; dilunakkan oleh §58 (jangan langsung 50 agent). |
| B-14 | 🆕 **Context Engine harus hidup terus-menerus.** §2–§3 menuntut Real-Time + Historical + Predicted Context untuk setiap permintaan — pipeline yang tidak pernah tidur, menyentuh cuaca, kalender, lokasi, dan wearable. Belum ada **perilaku cadangan** ketika salah satu sinyal mati, dan kegagalannya akan senyap: rekomendasi tetap keluar, hanya jadi salah. |
| B-15 | ⚠️ **Sebagian terjawab → H-14.** **Tujuh** angka HumanState (naskah 5 membuang `mood`) tanpa satu pun rumus — tapi Confidence Layer §19 kini mewajibkan setiap taksiran membawa `confidence` + `evidence_count`, jadi masalah "terlihat seperti fakta" punya jalan keluar. Yang tersisa: rumusnya sendiri, dan ambang High/Medium/Low. `"energy": 0.62` terlihat presisi padahal estimasi. §4 sudah menyebutnya "model internal", tapi antarmuka yang menampilkannya sebagai angka desimal akan tetap dibaca sebagai fakta. Sama persis dengan 6 skor Behavior Genome. |
| B-16 | 🆕 **Eksperimen n-of-1 mudah salah simpul.** 14 hari, tanpa kelompok kontrol, dengan cuaca, beban kerja, dan musim sebagai perancu. §36 sudah memisahkan Observation → Conclusion; yang belum ada adalah **ambang statistik dan kalimat penolakan** ketika data tidak cukup. Lihat **A-21**. |
| B-17 | 🆕 **Wardrobe Vision: kesalahan menular.** §20 "kamera melihat 12 shirts" berarti deteksi objek per helai pakaian. Salah hitung sekali akan mengendap di **Wardrobe Graph** dan meracuni setiap rekomendasi outfit sesudahnya. Perlu jalur koreksi manual sejak versi pertama. |
| B-1 | ⚠️ **Sebagian terjawab → H-14** (`evidence_count: 0` → sistem **bertanya**, bukan menebak). **Cold start Digital Twin & Profile Engine.** Prediksi 14–30 hari, *Chronotype*, *Motivation*, dan kini 8 field HumanState semuanya butuh riwayat berbulan-bulan. Pengguna hari pertama tidak punya apa-apa. §26 memperparah dengan simulasi 30/90/365 hari. |
| B-10 | **Evaluator butuh kebenaran acuan.** §47 menambah 8 metrik (Accuracy, Relevance, Personalization, Consistency, Safety, Latency, Cost, User Satisfaction) — tapi **"akurat terhadap apa"** masih tidak ditetapkan. *Automatic Rollback* berbahaya kalau skornya sekadar model menilai model. |
| B-9 | **Guardrail = titik gagal tunggal.** ⚠️ Membaik: §17 menambah Safety Classifier + Risk Engine + Policy Engine berlapis, dan §14 menegakkan batas di **lapisan memory**. Tapi dengan agent pihak ketiga, penegakan tetap harus ada di lapisan data. |
| B-11 | **SDK 5 bahasa = beban dukungan berlipat lima.** Dilunakkan: §58 memindahkan Developer SDK ke **V6**. |
| B-3 | **Akurasi pindai makanan.** Galat besar untuk masakan bersantan dan porsi tak baku. Ekspektasi dijaga sejak antarmuka. |
| B-4 | **Screen Time.** iOS tidak memberi rincian per aplikasi ke pihak ketiga. Fitur ini harus berbeda bentuk di iOS dan Android. |
| B-5 | **Flutter untuk Web.** Berat dan kurang ramah SEO. Kalau Discovery Feed diharapkan ditemukan lewat mesin pencari, web-nya kemungkinan perlu teknologi lain. |
| B-6 | **Wearable.** Tiap ekosistem (Apple Health, Google Fit, Garmin, Fitbit) punya izin dan proses persetujuannya sendiri. §18 menaikkan taruhannya dengan menjadikan Wearable dan Sensor kanal input resmi. |
| B-2 | **Biaya inferensi lintas modul.** Paket Free (Habit + Mood) harus dirancang supaya nyaris tidak memanggil model besar. Sekarang punya alatnya: §49 Model Router. |
| B-7 | ✅ **Beban operasional** — lihat **H-5**. Tidak hilang, tapi sudah diakui dan dijadwalkan bertahap. |
| B-8 | ✅ **Biaya inferensi berlipat** — lihat **H-6**. |
| B-13 | ✅ **Self-improving sulit diaudit** — lihat **H-7**. |

---

## C. Risiko hukum & kepatuhan

| # | Catatan |
|---|---|
| C-7 | **Marketplace agen pihak ketiga.** Begitu orang lain bisa menulis agent yang membaca data tidur, keuangan, dan foto tubuh, Anda menjadi **pemroses data untuk pihak ketiga**. §14–§16 memberi fondasi teknisnya; **beban hukumnya belum disentuh sama sekali**. Dilunakkan karena §58 memindahkannya ke V3/V6. |
| C-8 | 🆕 **Experiment Engine mendekati riset kesehatan mandiri.** Menyusun hipotesis tidur → fokus → produktivitas, menjalankannya 14 hari pada satu manusia, lalu menyimpulkan, secara bentuk adalah *self-experimentation*. Bahasa keluarannya harus tetap asosiatif (§7), dan sistem **tidak boleh menyarankan eksperimen yang menyangkut obat, puasa ekstrem, atau pembatasan tidur**. |
| C-9 | 🆕 **Hak hapus vs jejak audit.** §43 menjanjikan **Delete**; §45 AI Audit Trail dan *Immutable Log* (naskah 2) menyimpan jejak keputusan. Harus ditulis sejak awal: **apa yang tetap tersimpan setelah pengguna menghapus**, berapa lama, dan dalam bentuk apa. |
| C-1 | **Data biometrik.** Foto wajah, bentuk tubuh, warna kulit adalah kategori data khusus (GDPR Pasal 9; BIPA di Illinois). §20 menjadikan **kamera sebagai antarmuka utama** — permukaannya melebar, bukan menyempit. §41 (proses lokal bila perangkat mampu) meredakan sebagian, tapi baru ada di V5. |
| C-2 | **Batas medis.** ✅ **Diperkuat** — §17 menulis lugas: AI boleh tracking dan edukasi umum, **tidak boleh berpura-pura menjadi dokter**. Tetap perlu dijaga karena *Chronotype*, *Stress*, dan 8 field HumanState mudah dibaca sebagai nasihat medis. |
| C-3 | **Mental Wellness.** Perlu jalur eskalasi bila pengguna menuliskan sesuatu yang menandakan krisis. ⚠️ **Journal masuk V0** — risikonya datang di versi pertama, sementara Mental Wellness tidak punya agent (**A-20**). |
| C-4 | **Finance Behavior.** ✅ **Diperkuat** — §17: boleh analisis perilaku finansial, **jangan menjanjikan return investasi**. |
| C-6 | **`CoffeePurchased` sebagai event** dan tool Maps/Lokasi. Butuh jalur izin eksplisit — §15 sekarang menyediakannya (*Allow once* / *Allow while using* / *Deny*). |
| C-5 | **Nama & merek.** ⚠️ **Sekarang mendesak.** Nama sudah diputuskan `HumanVerse XOS` (**H-1**), tetapi ketersediaan merek, domain, dan nama paket **belum dicek**. Ini satu-satunya butir C yang bisa membatalkan keputusan H-1. |

---

## D. Celah yang belum tertutup

**Tiga celah tertutup oleh naskah 4** — manifest (**H-3**), jalan keluar data
(**H-4**), dan contoh skema event konkret. Naskah 5 memperkecil sisanya lagi,
tapi menambah satu celah baru (ambang confidence). Sisanya:

- Belum ada **rumus** untuk satu pun dari **lima** model angka pengguna: 6 skor
  Behavior Genome, 5 atribut Profile Engine, **7 field HumanState**, 7 batang
  Human Dashboard, dan 8 model DigitalTwin. Confidence Layer (**H-14**) memberi
  cara menyajikan ketidakpastiannya, **bukan** rumusnya. Lihat **A-19**.
- Belum ada **ambang** untuk Confidence Layer — batas High/Medium/Low, dan cara
  menghitung `confidence` serta `evidence_count` itu sendiri.
- Belum ada **cara masuknya data**: manual, wearable, izin OS, atau ketiganya.
  §18 menyebut delapan kanal input, tapi tidak satu pun mekanismenya.
- Belum ada **rencana offline** — padahal Daily Check-in dan Journal masuk V0,
  dan habit dicatat kapan saja.
- **Skema event sudah punya 21 nama, belum punya kontrak.** Naskah 5 §7
  mendaftar 21 event (`sleep.*`, `habit.*`, `mood.logged`, `journal.created`,
  `workout.*`, `meal.logged`, `outfit.*`, `purchase.created`, `goal.*`,
  `learning.*`, `meeting.*`, `travel.*`) dengan bentuk payload yang tetap —
  kemajuan besar dari satu contoh di naskah 4. Yang **masih belum ada**:
  **versi skema**, **urutan & idempotensi**, dan **consumer mana yang wajib**.
- Belum ada **bobot** di rumus Trend Score §22, dan *User Relevance* tidak
  didefinisikan.

---

## E. Ketidakcocokan antar-naskah

### E.1 — Model graf: tiga naskah, tiga model berbeda

Ini kelompok temuan paling serius, karena **seluruh produk berdiri di atas graf ini**.

| # | Temuan |
|---|---|
| **E-16** | **Arah sebab-akibat berbeda.** Naskah 1: `Tidur → Mood → Produktivitas → Olahraga`. Naskah 3 (Layer 8): `Sleep → Energy → Workout → Mood → Productivity → Career`. Urutan **Mood** dan **Workout terbalik**. ⚠️ **Naskah 4 §7 mengubah pertanyaannya**: keduanya seharusnya tidak ditulis sebagai *causal* sama sekali, melainkan sebagai *Causal Hypothesis* yang diuji per pengguna. Keputusan yang tersisa: **arah mana yang jadi hipotesis awal.** |
| **E-17** | **Daftar node tidak lengkap.** Naskah 2 menetapkan 10 node. Rantai Layer 8 memakai **Energy**, **Productivity**, **Career** yang tidak ada di daftar itu. Naskah 4 menambah lagi: **Goal**, **Milestone**, **Project**, **Skill**, **Wardrobe item**, **Experiment**. |
| **E-18** | **Dua set relasi yang terputus.** Naskah 2 memakai relasi **kausal** (`improves`, `causes`, `influences`, `blocks`, `predicts`). Ontology naskah 3 memakai relasi **struktural** (`hasHabit`, `prefersStyle`, …). Naskah 4 §9 menambah set **ketiga**: `Goal → Habit → Behavior → Outcome`. Belum ada aturan bagaimana ketiganya hidup dalam satu graf. |
| **E-11** | **Ontology tidak memuat Habit sebagai domain** — padahal `hasHabit` adalah relasinya, dan Habit adalah sinyal **terberat** di mesin rekomendasi (25 %). Ontology juga menambah **Identity**, **Travel**, **Hobby** yang tidak pernah jadi modul. |

### E.2 — Daftar yang berubah antar naskah

| # | Temuan |
|---|---|
| **E-35** | 🆕 **Daftar agent berubah untuk KEEMPAT kalinya — dan Grooming hilang lagi.** Naskah 5 §12 mendaftar **22 agent** (12 inti + 10 domain). Dibanding registry 14 di naskah 4: **HealthAgent, GroomingAgent, ProductivityAgent, EntertainmentAgent, dan ResearchAgent hilang**; **WardrobeAgent dan TrendAgent muncul**; dan 12 agent sistem (Planner, Behavior, Context, Goal, Evaluation, **Safety**, Personalization, …) masuk daftar untuk pertama kalinya. ⚠️ **Health dan Lifestyle adalah *domain* di §3 tapi tidak punya agent di §12.** Ini membatalkan **H-8**. |
| **E-34** | 🆕 **Model pengguna bergeser lagi di dalam naskah 5.** *HumanState* turun dari **8 field jadi 7** — **`mood` keluar**; itu kemungkinan besar benar dan disengaja (mood punya event `mood.logged` dan tabel `mood_entries` sendiri — **dilaporkan pengguna**, bukan **ditaksir sistem**), tapi belum pernah dinyatakan. *DigitalTwin* tetap 8 model tetapi **`SocialModel` diganti `LifestyleModel`**. Lihat **A-19**. |
| **E-37** | 🆕 **Tiga sistem skoring rekomendasi yang tidak sepadan.** Naskah 2: bobot persen berjumlah **100 %**. Naskah 3: Outfit Score berjumlah **100 poin**. Naskah 5 §11: *Recommendation Score* sebagai **rata-rata 0–1**. Tabel `recommendations` di V0 harus menyimpan salah satunya. Rumus §11 juga menyebut **7 komponen** sementara contohnya memakai **5** (*Occasion Fit* dan *Availability* tidak muncul), dan **belum ada bobot**. |
| **E-39** | 🆕 **Memory: jenis atau nama scope?** §17 memberi **6 jenis** (Working, Episodic, Semantic, Behavioral, Preferences, Procedural) dengan contoh untuk empat di antaranya — hitungan kelima setelah 3 / 5 / 7 / nama. Tapi manifest §14 tetap memakai **nama scope** (`fashion_preferences`, `wardrobe`, `outfit_history`). Belum dijelaskan apakah nama itu lapisan di atas jenis, atau penggantinya. Tabel `memories` butuh salah satunya sebagai kolom. |
| **E-40** | 🆕 **V0 bertambah dua fitur, waktunya tidak.** Naskah 4 memberi 10 butir V0; naskah 5 §29 memberi **12** — tambahannya **Activity Tracking** dan **Recommendation**, sementara target tetap 4–6 minggu. Sprint 5 bahkan menambah *Personalization*. Ini pelebaran MVP yang terjadi dalam satu hari. Lihat **A-17**. |
| **E-38** | 🆕 **`PreparationAgent` tidak ada di daftar 22 agent.** Ia muncul di alur Orchestrator §13 sebagai langkah nyata. Naskah 5 bertabrakan dengan dirinya sendiri — pola yang sama seperti **E-25** di naskah 4. |
| **E-36** | 🆕 **Penyimpanan menyusut dari 6 jadi 4 — ini kabar baik, dicatat supaya tidak dikira kelalaian.** **Kafka dan ClickHouse hilang** dari naskah 5; antrean pindah ke Redis. Sejalan dengan "jangan langsung 100 microservices" (§1) dan "jangan langsung Kubernetes" (naskah 4 §51). Menutup **A-10** → **H-12**, dan menyelesaikan **E-8** ke arah yang lebih sederhana. |
| **E-41** | 🆕 **Billing muncul entah dari mana.** §3 mendaftarkan `Billing` sebagai domain platform — tidak pernah ada di empat naskah sebelumnya, dan tidak punya pasangan di enam paket harga naskah 1 maupun bagi hasil marketplace naskah 4. Lihat **A-6**. |
| **E-24** | 🆕 **Jumlah agent: 12 modul → 8 agent → 14 agent.** Naskah 1 punya 12 modul manusia, naskah 2 memberi agent kepada 8, **naskah 4 §12 mendaftar 14** — memulihkan Grooming/Nutrition/Productivity dan menambah **Travel, Entertainment, Research** yang tidak pernah jadi modul. Yang tetap tanpa agent: **Mental Wellness** dan **Lifestyle** (**A-20**). |
| **E-25** | 🆕 **Naskah 4 bertabrakan dengan dirinya sendiri.** Agent Registry §12 berisi 14 agent; Final Agent Ecosystem §56 mendaftar 8 di kolom HUMAN DOMAIN — **memuat Lifestyle yang tidak ada di registry**, dan **membuang Habit, Grooming, Fitness, Nutrition, Productivity, Entertainment, Research** yang ada di registry. |
| **E-26** | 🆕 **Dua roadmap yang isinya bergeser.** Naskah 2: V1 *Core AI* · V2 *Specialist Agents* · V3 *Digital Twin* · V4 *Predictive Human*. Naskah 4: V1 *Behavior Intelligence* · V2 *Lifestyle AI* · V3 *Multi-Agent Platform* · V4 *Digital Twin*, ditambah **V6 Ecosystem**. Nomor versi yang sama menunjuk isi yang berbeda — ini akan mengacaukan setiap percakapan tentang "kita di V berapa". Lihat **A-18**. |
| **E-27** | ✅ **Ditutup** oleh naskah 5 §4 — lihat **H-10**. ~~Dua struktur repo.~~ Naskah 2 [`11-STRUKTUR-REPO.md`](11-STRUKTUR-REPO.md) memberi monorepo `apps/ services/ agents/ …`. Naskah 4 §52 memberi `/docs /architecture /agents /contracts /prompts /adr /tests` plus wajib `AGENTS.md`, `ARCHITECTURE.md`, `CONTRIBUTING.md`. Keduanya masuk akal; belum ada yang menyatakan mana yang dipakai. |
| **E-28** | ✅ **Ditutup: TOOL** — lihat **H-11**. ~~Weather: tool atau agent.~~ **E-2** hampir ditutup ketika naskah 3 memunculkan Calendar dan Weather sebagai **MCP tool**. Naskah 4 §13 justru memakai **`WeatherAgent`** sebagai contoh utama komunikasi antar-agent, lengkap dengan pesan `"to": "WeatherAgent"`. Butir ini kembali terbuka. |
| **E-29** | 🆕 **Digital Twin: tiga horizon.** 30 hari (naskah 1) · 14 hari (naskah 2) · **30/90/365 hari** (naskah 4 §26). |
| **E-30** | 🆕 **Kategori tren hilang di naskah 4.** §22 memberi rumus skor tapi **tidak menyebut satu kategori pun**, sehingga tiga daftar berbeda dari **E-12** tetap tidak terselesaikan. |
| **E-31** | 🆕 **Tiga gagasan naskah 1 menghilang di naskah 4.** *Avatar* hanya tersisa sebagai kanal output §18; ***Discovery Feed*** dan ***Human Genome of Behavior* (6 skor)** tidak disebut sama sekali — padahal Behavior Genome termasuk yang paling sering dikutip di naskah 1. |
| **E-32** | 🆕 **"Agent Factory" kini punya tiga makna.** Naskah 2: seluruh platform sebagai *"The Ultimate AI Agent Factory"*. Naskah 3 (Phase 3): AI yang **menciptakan agent baru secara otomatis**. Naskah 4 §10: **pipeline generator** yang dijalankan manusia (Specification → Capability → Tools → Prompt → Memory → Evaluation → Security → Deployment). Makna ketiga paling konkret dan paling tidak berbahaya. |
| **E-33** | 🆕 **Memory: sekarang ada model keempat.** 3 jenis (Memory Agent) · 5 jenis (naskah 2) · 7 jenis (naskah 3) · dan naskah 4 §14 yang tidak memakai *jenis* sama sekali melainkan **memory bernama** (`fashion_preferences`, `wardrobe`, `outfit_feedback`) dengan izin read/write per agent. Model keempat ini paling bisa diimplementasikan — tapi tetap harus dipilih. |
| **E-6** | **Memory: TIGA taksonomi berbeda.** Memory Agent 3 jenis · naskah 2 lima · naskah 3 tujuh. Hanya *Episodic* yang muncul di ketiganya. Lihat **E-33**. |
| **E-12** | **Kategori tren: tiga daftar berbeda.** Naskah 1 punya 12 dengan **Skincare**; naskah 2 hanya 7; naskah 3 punya 12 tetapi Skincare **diganti Perfume**. |
| **E-13** | **MCP Tool: tabel ≠ folder.** Tabel kategori punya **Finance/Budget** yang tidak punya folder; folder punya **`travel/`** yang tidak ada di tabel. ⚠️ Naskah 4 memunculkan **TravelAgent** — menguatkan bahwa `travel/` memang disengaja. |
| **E-21** | **Workflow "Besok meeting" berbeda isi.** Naskah 2: Planner → Memory → Fashion → Calendar → Health. Naskah 3: Planner → Calendar → Weather → Fashion → Health → Reminder. **Memory hilang** di versi kedua. |
| **E-23** | **PromptOps tidak menutupi semua agen.** `prompts/` punya 7 subfolder — tidak ada habit, learning, trend, memory, reasoning, atau guardrail. ⚠️ Dengan registry 14 agent (§12), jaraknya melebar jadi 7 berbanding 14. |

### E.3 — Istilah dan tempat yang bertabrakan

| # | Temuan |
|---|---|
| **E-14** | **Dua sistem skoring dengan bobot bertabrakan.** Mesin rekomendasi umum memberi **Cuaca 5 %**; Decision Engine memberi **Cuaca 20** untuk outfit. Hubungan keduanya belum ditetapkan, dan keduanya sama-sama berjumlah 100. |
| **E-15** | **Model profil yang belum disambungkan.** *Human Genome of Behavior* 6 skor vs *Profile Engine* 5 atribut — keduanya mengklaim "semua agent memakai profil yang sama". ⚠️ Naskah 4 menambah dua lagi; sekarang jadi butir **A-19**. |
| **E-22** | **Tool Registry ada di tiga tempat.** Sebagai service di AgentOS, sebagai folder `agent-os/tools/`, dan sebagai folder `tools/` mandiri di Layer 10. Naskah 4 §58 menambah *Tool Registry* lagi sebagai isi V3. |
| **E-4** | **Trend Agent punya dua atasan** — sub-agent Fashion sekaligus agen mandiri Layer 3, lalu Layer 17 sendiri. ⚠️ Naskah 4 §22 menjadikannya *engine*, bukan agent — dan **TrendAgent tidak ada di registry §12**. |
| **E-1** | Pohon repo punya `retrieval-agent/` dan `evaluator-agent/`, tapi Layer 2 hanya menjelaskan 4 agen inti. Dua folder ini tak pernah dijelaskan. |
| **E-3** | Habit, Trend, dan Learning punya agen tapi **tidak punya layanan backend**. |
| **E-7** | Digital Twin: **30 hari** (naskah 1) vs **14 hari** (naskah 2). Lihat **E-29**. |
| **E-10** | Bobot rekomendasi tidak memuat sinyal Finance, Social, Learning, atau Career — padahal keempatnya punya agen. |
| **E-2** | ⚠️ **Terbuka lagi** — lihat **E-28**. |
| **E-20** | **"Agent Factory" dipakai dua arti** — sekarang tiga. Lihat **E-32**. |
| **E-8** | 4 basis data → 6 basis data. Penambahan wajar, bukan tabrakan. Tidak perlu tindakan. |
| **E-9** | Social: *"teman dekat"* vs *"ibu"*. Perbedaan kecil, dicatat agar tidak dikira salah salin. |
| **E-5** | ❌ **Dibuka lagi** — Grooming kembali di naskah 4, hilang lagi di naskah 5. Lihat **E-35**. |

---

## F. Yang sudah saya periksa dan ternyata benar

- ✅ **Bobot mesin rekomendasi berjumlah tepat 100 %** (20+15+25+10+5+25).
- ✅ **Outfit Score berjumlah tepat 100** (25+20+20+20+15).
- ✅ **Master Documentation berjumlah tepat 160** — 35+18+15+12+12+12+10+10+10+10+8+8.
- ✅ **Pohon repo konsisten dengan lapisan agen.**
- ✅ **Roadmap V0–V5 berurutan masuk akal.**
- ✅ **Prinsip "bukan trading" dan "bukan aplikasi bank"** konsisten di semua naskah.
- ✅ **Prinsip "prediksi bukan kepastian"** dipegang konsisten — diperkuat lagi
  di naskah 4: §26 *"scenario simulation, bukan ramalan"*, §27 *"decision
  support, bukan pengambil keputusan"*.
- ✅ **Tidak ada butir naskah yang hilang saat dirapikan** — istilah kunci dari
  keempat naskah dicek ulang satu per satu.
- ✅ **Agent Registry §12 berisi tepat 14 agent** seperti yang tertulis.
- ✅ **Risk Engine §16 punya 5 tingkat (0–4)** dan contohnya naik konsisten:
  informasi → rekomendasi → aksi reversibel → aksi berdampak → high-impact.
- ✅ **Naskah 4 menolak over-engineering secara eksplisit di tiga tempat
  terpisah** (§38, §51, §58) — konsisten, bukan sekali lewat.
- ✅ **Penolakan "satu angka Life Score" (§28) sejalan dengan prinsip penutup**
  (*"jangan menilai manusia baik atau buruk"*). Dua bagian berbeda, satu sikap.
- ✅ **Batas health dan finance di §17 sama persis dengan prinsip naskah 1**
  (`07-PRINSIP.md`) — tidak ada pelonggaran diam-diam di sepanjang empat naskah.

**Diperiksa di naskah kelima:**

- ✅ **Aritmetika Recommendation Score benar** — rata-rata lima nilai contoh
  (0,80 + 0,95 + 0,92 + 0,90 + 0,87) ÷ 5 = **0,888 → 0,89**, persis seperti
  yang ditulis. (Komponennya yang kurang, bukan hitungannya — lihat **E-37**.)
- ✅ **Daftar agent §12 berjumlah tepat 22** — 12 inti + 10 domain, penomoran
  1–22 berurutan tanpa lompatan.
- ✅ **V0 database berisi 19 tabel**, dan **`permissions`, `consents`, serta
  `audit_logs` sudah ada sejak V0** — privasi tidak ditunda ke fase belakang.
  Ini konsisten dengan §43 Privacy Center di naskah 4.
- ✅ **Sprint 0–6 berurutan masuk akal** — fondasi → identity → human core →
  memory → AI → intelligence → produk. Tidak ada sprint yang bergantung pada
  hasil sprint sesudahnya.
- ✅ **"Popular ≠ suitable for the user" (§21) konsisten** dengan *Personal
  Trend Score = Trend Score × User Relevance* di naskah 4 §22.
- ✅ **Sepuluh agent pengembangan (§28) sengaja terpisah dari 22 agent produk
  (§12)** — sempat saya kira daftar yang bertabrakan, ternyata dua ekosistem
  berbeda: satu membangun produk, satu berjalan di dalam produk.

---

## G. Lubang di naskah 3 sendiri

| # | Temuan |
|---|---|
| **G-1** | **Layer 14 terpotong di tengah tabel.** Yang terbaca hanya `Accuracy 95%` lalu `Latency` — tanpa angka target. ⚠️ Naskah 4 §47 memberi **8 metrik evaluasi** yang jauh lebih lengkap; lubang naskah 3 tetap dicatat, tapi sudah ada penggantinya. Dicatat di [`39-L14-EVALUATION-FRAMEWORK.md`](39-L14-EVALUATION-FRAMEWORK.md). |
| **G-2** | **Layer 15 dan Layer 16 tidak pernah muncul.** Satu lapisan tanpa nomor (*Profile Engine*) dan dua nomor tanpa lapisan. Disimpan apa adanya di [`40-TANPA-NOMOR-PROFILE-ENGINE.md`](40-TANPA-NOMOR-PROFILE-ENGINE.md). |
| **G-3** | **Data Governance dijanjikan tapi tidak ditulis.** ⚠️ **Isinya sekarang ada** — §43 Privacy Center, §44 Personal Data Vault, §45 AI Audit Trail, dan *Governance* sebagai komponen SYSTEM di §56. Yang tersisa hanya keputusan penempatan (**A-16**). |
