# 05 — Technology Stack Final

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menjawab butir *“technology stack final”* naskah 24, dan menemukan satu
> ketidakcocokan yang belum pernah tercatat: **`spec/` berganti bahasa backend
> tanpa menyebutnya** (§2).

---

## §1 Yang sudah dikunci pemilik — tidak diputuskan ulang

| | Keputusan | Sumber | Status |
|---|---|---|---|
| ADR-001 | **Flutter** untuk lintas-platform | §L23 naskah 7 | 🔒 dikunci |
| ADR-002 | **PostgreSQL** basis data utama | idem | 🔒 |
| ADR-003 | **Qdrant** memori vektor | idem | 🔒 |
| ADR-004 | **LangGraph** orkestrasi | idem | 🔒 — *“pertama kalinya pustaka orkestrasi dikunci”* |
| A-10 | **empat** penyimpanan, bukan enam — ClickHouse & Kafka dibuang | naskah 5 | 🔒 |
| — | **Neo4j** graf — **V2**, tidak menyentuh V0 | [`../spec/README.md`](../spec/README.md) | 🔒 |
| — | **Redis** antrean & cache; Kafka hanya bila skalanya menuntut | naskah 5 | 🔒 |
| — | **V0: Docker Compose** → Cloud VM → Kubernetes | naskah 5 §32 | 🔒 |
| — | **MCP** untuk tool | naskah 2 | 🔒 |

⚠️ **ADR-001 menutup sebagian A-11, tidak seluruhnya.** `apps/desktop/` dan
`apps/admin/` belum punya teknologi, dan **B-5** (Flutter untuk web berat &
kurang ramah SEO) belum dijawab. Diselesaikan di §4.

---

## §2 🔴🔴 Temuan: bahasa backend berganti di `spec/`, dan tidak ada satu baris pun yang mencatatnya

**Ini memblokir Sprint 0 tugas 0.3 — kerangka `apps/api`.**

| Sumber | Menyatakan |
|---|---|
| [`../docs/05`](../docs/05-ARSITEKTUR.md) — naskah **1** | **FastAPI** sebagai *Backend*, dua kali: di tabel teknologi **dan** di diagram arsitektur |
| `README.md` akar, tabel Tumpukan teknologi | *“Backend — **FastAPI** · 12 microservice”* |
| ADR-004 | **LangGraph** — pustakanya **Python lebih dulu** |
| [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) | `index.ts` · `routes.ts` · `service.ts` · `repository.ts` · `events.ts` · `types.ts`, lint `no-restricted-imports`, `madge --circular` |
| [`../spec/07`](../spec/07-BACKLOG-V0.md) tugas 0.6 | **`npm test`** |

**Pemeriksaannya tegas:**

```
grep -rl "FastAPI" docs/                        →  1 berkas  (docs/05, naskah 1)
grep -rlo "Node.js|NestJS|Express|Golang" docs/ →  0 berkas
```

🛑 **FastAPI adalah satu-satunya kerangka backend yang pernah dinamai dalam 24
naskah. Node.js, NestJS, Express, dan Go: nol kali.** Namun dua dari delapan
berkas `spec/` ditulis untuk TypeScript/Node — **tanpa satu kalimat pun yang
menyatakan pergantiannya, apalagi alasannya.**

> 💡 Ini bentuk lain dari pola yang sudah tercatat berkali-kali di repo ini:
> **sebuah klaim berhenti benar tanpa memberi tahu pembacanya.** Bedanya, yang
> ini berhenti benar di berkas yang seluruh tugasnya adalah **memberi tahu
> pembacanya apa yang harus dikoding.**

### 🔧 K-13 · Backend = **Python + FastAPI**

| | |
|---|---|
| **Keputusan** | Backend HumanVerse XOS ditulis dalam **Python** dengan **FastAPI**. [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) dan [`../spec/07`](../spec/07-BACKLOG-V0.md) **diselaraskan**, bukan dibiarkan berbeda. |
| **Bukti** | (a) satu-satunya kerangka yang pernah dinamai pemilik, di **dua** tempat pada naskah pertama; (b) **ADR-004 LangGraph** — pustaka yang **sudah dikunci** — Python lebih dulu; (c) **enam dari dua puluh fase natively Python**: Phase 10 (persepsi) · 12 (simulasi) · **16 (ROS 2 — `rclpy`/`rclcpp`, tidak ada klien Node yang didukung resmi)** · 17 (bio) · 19 (sains) · sebagian 5 & 9; (d) Qdrant, model serving, federated learning — semuanya berpusat Python. |
| **Bacaan yang DITOLAK** | *“`spec/` sudah ditulis untuk TypeScript, jadi TypeScript yang menang.”* 🛑 **Ditolak dengan alasan yang membalik arahnya:** `spec/` tidak pernah **memutuskan** bahasa — ia **mengasumsikannya**, diam-diam, di dua berkas. Asumsi yang tidak pernah dinyatakan tidak bisa mengalahkan keputusan yang dinyatakan dua kali. ⇒ aturan pengutamaan [`README.md`](README.md) butir 2 (*“untuk V0, `spec/` menang”*) **tidak berlaku di sini**, sebab ia berlaku atas **bentuk** — kolom, payload, endpoint — bukan atas hal yang `spec/` tak pernah nyatakan. |
| **Yang TIDAK berubah** | Seluruh isi `spec/01`–`05` (23 tabel · ERD · 22 event · endpoint · manifest) **bebas bahasa** dan tidak disentuh. Yang berubah hanya nama berkas modul dan nama perkakasnya. |
| **Biaya** | **Nol baris kode** — belum ada satu pun. Ini kesempatan terakhir biaya itu nol. |
| **Cara membalikkan** | Ganti tabel padanan di bawah. Selama belum ada kode, biayanya tetap nol; sesudah Sprint 0 selesai, biayanya seluruh Sprint 0. |

**Padanan yang dijalankan di `spec/`:**

| `spec/` sebelumnya | Menjadi |
|---|---|
| `index.ts` | `__init__.py` — pintu keluar publik modul |
| `routes.ts` · `service.ts` · `repository.ts` · `events.ts` · `types.ts` | `routes.py` · `service.py` · `repository.py` · `events.py` · `schemas.py` |
| `npm test` | `pytest` |
| lint `no-restricted-imports` | **`import-linter`** (kontrak layer & forbidden) |
| `madge --circular` | `import-linter` kontrak `independence` |

⭐ **`import-linter` menggantikan DUA perkakas sekaligus**, dan itu keuntungan
yang tidak disengaja: batas modul (`spec/06` aturan 1–4) dan **batas keras B-1 &
B-2** ([`04`](04-DEPENDENCY-GRAPH.md)) menjadi **satu berkas kontrak** yang
dibaca satu perintah CI. Lihat [`11`](11-PENEGAKAN.md).

---

## §3 Pemilihan berdasarkan POLA AKSES, bukan berdasarkan fase

Aturan yang menghasilkan §4, dan yang menutup empat issue penyimpanan sekaligus
([#74](../../issues/74) · [#107](../../issues/107) · [#119](../../issues/119) ·
[#127](../../issues/127)):

> 🔑 **PostgreSQL menyimpan apa yang seorang manusia akan kenali sebagai sebuah
> catatan. Apa pun yang tercuplik pada laju yang tidak dihasilkan manusia tidak
> pernah menyentuhnya — ia mencapai PostgreSQL hanya sebagai RINGKASAN.**

Aritmetikanya sudah ada di naskah, tinggal disambungkan:

| Sumber | Laju | Per 30 hari, satu pengguna |
|---|---|---|
| `habit.completed` | belasan/hari | ~400 baris |
| `PersonDetected` @ 1 Hz | 86.400/hari | **2,6 juta baris** — satu kamera |
| `wifi_csi` @ 10–100 Hz | 864.000–8,6 juta/hari | **1–2 orde lebih besar lagi**, dan tiap sampel sebuah matriks |

⭐ **Jawabannya sudah ditulis pemilik sendiri, dua kali** — §10.10 (*5 bingkai →
1 event*) dan §10.11 (*5.400 pembacaan → 1 kalimat*). Yang tidak pernah
dilakukan hanyalah **menyambungkannya ke §10.30** (tabel `events`).

---

## §4 Tumpukan final

| Lapisan | Pilihan | Status |
|---|---|---|
| **Backend** | **Python 3.12 + FastAPI** | 🔧 **K-13** §2 |
| Orkestrasi AI | **LangGraph** | 🔒 ADR-004 |
| Tool | **MCP** | 🔒 |
| Aplikasi | **Flutter** — mobile & web | 🔒 ADR-001 |
| `apps/admin/` | **Flutter web yang sama**, satu toolchain | 🔧 lihat bawah |
| Halaman publik ber-SEO | **di luar `apps/`** — situs statis tersendiri | 🔧 menjawab **B-5** |
| Basis data utama | **PostgreSQL 16** | 🔒 ADR-002 |
| Deret waktu & aliran sensor | **TimescaleDB** (ekstensi PostgreSQL) | 🔧 §5 |
| Vektor | **Qdrant** | 🔒 ADR-003 |
| Graf | **Neo4j** — **V2**, bukan V0 | 🔒 |
| Cache & antrean | **Redis 7** (Streams) | 🔒 |
| Lakehouse / data mentah | **object storage + Parquet** | 🔧 §5 |
| Model router | **agnostik penyedia**, biaya per komponen per agent (§14.24) | 🔧 §6 |
| Infra V0 | **Docker Compose** | 🔒 |
| Infra V2+ | Kubernetes · Terraform · ArgoCD · Vault | 🔒 |
| Observability | OpenTelemetry · Prometheus · Grafana · Loki · Tempo | 🔒 |
| Batas modul & impor | **`import-linter`** | 🔧 §2 |
| Uji | **`pytest`** + cakupan ≥ 70 % | 🔧 §2 |

### 🔧 `apps/admin/` dan B-5 — dua jawaban, bukan satu

**B-5** mencatat Flutter-untuk-web berat dan kurang ramah SEO. Itu **benar**,
tetapi hanya berlaku bagi halaman yang **harus ditemukan mesin pencari**.

| Permukaan | Butuh SEO? | Pilihan |
|---|---|---|
| aplikasi pengguna (login diperlukan) | ❌ | **Flutter web** — berat itu dibayar sekali, sesudah login |
| `apps/admin/` | ❌ | **Flutter web yang sama** — satu toolchain, satu design system |
| halaman pemasaran / dokumentasi publik | ✅ | **di luar `apps/`**, situs statis |

⇒ B-5 berhenti menjadi risiko arsitektur dan menjadi **aturan penempatan**.
`apps/desktop/` tetap terbuka — tidak ada satu pun kebutuhan yang menuntutnya
sebelum V5.

---

## §5 Empat kelas penyimpanan

Terperinci di [`06`](06-DATA-ARCHITECTURE.md); di sini pilihan teknologinya.

| Kelas | Isi | Teknologi | Kenapa bukan PostgreSQL biasa |
|---|---|---|---|
| **K1 · Catatan** | 247 nama tabel yang seorang manusia kenali sebagai baris | PostgreSQL 16 | — |
| **K2 · Deret waktu** | biometrik, telemetri robot, pembacaan sensor teragregasi | **TimescaleDB** | hypertable + retensi + agregat berkelanjutan; **tetap PostgreSQL**, jadi `JOIN` ke K1 tidak hilang |
| **K3 · Aliran mentah** | `wifi_csi` · point cloud · bingkai · audio | **object storage + Parquet**, dan **tidak pernah meninggalkan perangkat sebagai mentah** (§15.29) | tiap sampel sebuah matriks; menaruhnya di baris relasional adalah kesalahan berorde besaran |
| **K4 · Turunan** | vektor · graf · feature store | Qdrant · Neo4j (V2) · Parquet | bisa dibangun ulang; kehilangannya bukan kehilangan data |

> 🔧 **TimescaleDB dipilih karena ia ekstensi, bukan basis data kelima.** A-10
> sudah memutuskan **empat** penyimpanan, bukan enam — menambah basis data
> keenam akan membatalkannya. Ekstensi PostgreSQL tidak menambah proses, tidak
> menambah backup terpisah, dan tidak menambah satu pun daur operasional.
> **Cara membalikkan:** kalau laju tulis melewati kemampuan satu PostgreSQL,
> pindahkan K2 ke basis data deret waktu tersendiri — K1 tidak ikut pindah.

---

## §6 Yang **tidak bisa** diputuskan sekarang — dan pemicunya

> 🔑 **Menuliskan pilihan tanpa hal yang akan memakainya berarti menebak.**
> Yang ditulis di sini bukan pilihannya, melainkan **kriteria** dan **kapan
> pilihan itu harus dibuat** — supaya ia tidak terlupa seperti empat permintaan
> pemilik sebelumnya ([`../docs/PETA-FASE.md`](../docs/PETA-FASE.md)).

| Pilihan | Kandidat di naskah | Kriteria pemutus | **Pemicu — diputuskan sebelum…** |
|---|---|---|---|
| **Simulator fisika** (§16.26) | Isaac Sim · Gazebo · Webots · MuJoCo | 🛑 **kesetiaan KONTAK** — keempatnya tidak setara, dan kontak adalah sisi yang menentukan apakah `Safety Test` berarti | tugas pertama `embodiment/` |
| **SLAM** (§15.6) | ARKit · ARCore · OpenVSLAM · ORB-SLAM3 · RTAB-Map | **lisensi** dan **penguncian platform** — perbedaannya besar dan tidak bisa dibatalkan murah | tugas pertama `spatial/` |
| **Penyedia LLM** | — | biaya per komponen per agent (§14.24) + **arah `risk`**: untuk > R2 yang benar justru yang lebih mahal (§11.54) | 🛑 menyentuh **A-6** ([#18](../../issues/18)) — tarif & bagi hasil, **milik pemilik** |
| **Kafka menggantikan Redis Streams** | naskah 5 | — | **pemicu terukur:** ketika sebuah consumer kedua yang independen perlu memutar ulang riwayat **lebih lama daripada retensi Redis**. Bukan angka throughput — itu yang biasanya salah diperkirakan |
| **Neo4j** | naskah 2–5 | — | **V2** — sudah ditetapkan, tidak menyentuh V0 |

⚠️ **Baris pertama dan kedua punya sifat yang sama dan patut disebut:**
keduanya adalah pilihan yang **mahal dibatalkan** dan **berada di fase yang
menyentuh badan orang**. Untuk keduanya, memilih terlambat lebih murah daripada
memilih salah.

---

## §7 ⭐ Memakai yang sudah ada — dan kenapa itu keputusan keselamatan

Naskah 19 dan 20 melakukan sesuatu yang tidak terjadi pada delapan belas naskah
sebelumnya: **menyebut pustaka yang sudah ada alih-alih merancang sendiri.**

| § | Yang dipakai |
|---|---|
| §15.6 | ARKit · ARCore · OpenVSLAM · ORB-SLAM3 · RTAB-Map |
| §16.7 | MoveIt · OMPL · RRT\* · CHOMP · TrajOpt |
| §16.14 | MQTT · Matter · Zigbee · Thread · BLE |
| §16.22 | **“HumanVerse tidak menggantikan ROS”** |
| §16.26 | Isaac Sim · Gazebo · Webots · MuJoCo |

> 🔑 **Untuk fase yang berisiko fisik, memakai tumpukan yang sudah diuji ribuan
> orang ADALAH keputusan keselamatan** — bukan penghematan waktu. Perencana
> lintasan yang ditulis sendiri akan diuji oleh satu tim; OMPL sudah diuji oleh
> dua dekade robot yang menabrak sesuatu.

🔧 **Aturan yang diturunkan darinya, berlaku untuk seluruh repo:**
**tidak ada komponen yang menyentuh keselamatan fisik ditulis sendiri kalau ada
pustaka mapan yang melakukannya** — dan kalau ditulis sendiri, alasannya masuk
ADR beserta apa yang membuatnya tidak bisa memakai yang ada.

---

## §8 Pemeriksaan yang harus lulus

| Pemeriksaan | Hasil |
|---|---|
| Bahasa backend dinyatakan | ✅ **Python + FastAPI** (K-13) — sebelumnya tidak pernah, di kedua lapis |
| Berkas `spec/` yang menyalahi K-13 | **NIHIL** sesudah penyelarasan §2 |
| Jumlah penyimpanan | **4** — A-10 dipertahankan; TimescaleDB **ekstensi**, bukan yang kelima |
| Pilihan yang ditunda tanpa pemicu | **NIHIL** — kelimanya punya pemicu di §6 |
| ADR yang dibatalkan berkas ini | **NIHIL** — keempatnya dipertahankan |
| Keputusan yang menyentuh uang/hukum | **NIHIL** — penyedia LLM ditandai milik pemilik ([#18](../../issues/18)) |
