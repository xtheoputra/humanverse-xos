# 217 — §14.42–§14.50 Delegation, Attenuation, Governance Mesh, Control Plane & Collective Runtime

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.42 — Delegation

```
User → Orchestrator → Research Agent → Data Agent → Analysis Agent
→ Verifier
```

Tetapi delegation **tidak boleh memperluas permission**. Ini prinsip penting:

> ## Delegation cannot exceed the authority of the delegator.

Jika A hanya boleh **membaca** data, maka pada `A → B`, B juga tidak boleh
memperoleh **write/delete/send**.

---

> ⭐⭐⭐ **Ini kalimat yang saya tulis sebagai "aturan yang belum ditulis" di
> berkas [`181`](181-MULTI-AGENT.md) — dan ia datang dalam bentuk yang lebih
> baik daripada yang saya usulkan.**
>
> Usul saya berbunyi *"lingkup pesan tidak boleh lebih luas daripada lingkup
> pengirimnya"* — aturan tentang **field di dalam pesan**, yang berarti
> penegakannya bergantung pada field itu diisi benar. Rumusan pemilik tidak
> menyebut pesan sama sekali: ia aturan tentang **kewenangan**, jadi ia tetap
> berlaku lewat jalur apa pun — pesan, panggilan langsung, tool, atau protokol
> federasi §14.41.
>
> Itu juga yang membuat hilangnya `authorization.scope` dari amplop §14.7
> (berkas [`209`](209-PROTOKOL-KONTRAK-DISCOVERY-TRUST.md)) **bukan kemunduran**:
> yang dibuang adalah field, yang datang adalah invarian.

> ⭐ **Rantainya berakhir di `Verifier`, bukan di `Analysis Agent`.** Delegasi
> lima tingkat yang ujungnya adalah pemeriksa berarti hasil terdalam tidak
> langsung naik sebagai jawaban. Itu sejalan dengan §11.1 `VERIFY → OBSERVE`
> dan dengan `Verifier` sebagai peran tetap di dalam team (§14.16).

---

## §14.43 — Capability Attenuation

```
Parent Capability → Reduced Capability → Child Agent
```

```
Parent:  calendar.read + calendar.write
Child:   calendar.read
```

Bukan otomatis `calendar.read + calendar.write`. Ini penting untuk **security
architecture**.

---

> ⭐⭐⭐ **Ini prinsip object-capability yang benar, dan ia melengkapi §14.42
> pada sisi yang berbeda.** §14.42 melarang **naik**; §14.43 menetapkan bahwa
> yang wajar adalah **turun**. Bersama `delegation.max_depth: 2` (§14.55),
> ketiganya membuat rantai delegasi **terbatas panjangnya dan menyempit di tiap
> langkah** — dan itulah yang membuat pencarian jalur §14.32 punya ujung.

> ⚠️ **Tetapi yang memilih kapabilitas mana yang diturunkan adalah agent
> INDUKNYA — dan tidak ada apa pun yang mewajibkan ia menyempit.**
>
> Meneruskan **seluruh** kapabilitasnya tidak melanggar §14.42 (tidak melebihi
> kewenangan pendelegasi) dan tidak melanggar §14.43 (attenuation *boleh*,
> bukan *harus*). Contohnya memperlihatkan penyempitan; aturannya tidak
> menuntutnya.
>
> Yang menutupnya, dan sudah ada bahannya: **kapabilitas anak dipotong ke apa
> yang manifest anak itu sendiri minta** (§14.55 sudah punya blok
> `capabilities:` untuk tiap agent), sehingga irisan — bukan induk — yang
> menentukan. Dengan itu penyempitan menjadi sifat sistem, bukan kebaikan hati
> agent induk.

---

## §14.44 — Agent Governance Mesh

```
              Governance Mesh
                    │
 ┌──────────┬───────┼───────┬──────────┐
 ▼          ▼       ▼       ▼          ▼
Identity  Policy   Risk  Permission  Audit
 ▼          ▼       ▼       ▼          ▼
             Agent Ecosystem
```

> Governance **tidak boleh menjadi agent biasa** yang dapat dipengaruhi oleh
> action agents.

---

> ⭐⭐⭐ **Ini pernyataan KELIMA tentang governance di luar jalur kepentingan
> (§11.4 · §14.3 · §14.13 · §14.16 · di sini) — dan yang pertama menyebut
> bentuk yang dilarang, bukan hanya sifat yang diinginkan.**
>
> *"Bukan agent biasa"* bisa ditegakkan; *"harus independen"* tidak. Ia berarti:
> tidak terdaftar di `agents` sebagai peer, tidak bisa dipanggil lewat
> `POST /v1/agent-messages`, tidak ikut negosiasi §14.14, dan tidak punya
> kepentingan pada hasil. Itu daftar yang bisa diperiksa CI.
>
> ⭐ Kelima komponennya juga persis **Control Plane #4** dari §8.42 · §11.51 ·
> §13.34 — Identity · Policy · Risk · Permission — ditambah **`Audit`** sebagai
> yang kelima. Menaruh Audit di dalam governance, bukan di sampingnya, adalah
> pilihan yang benar: catatan yang bisa dipengaruhi yang dicatatnya bukan
> catatan.

> ⚠️ **Tapi §14.13 memberi veto kepada "Risk **Agent**", dan Risk ada di dalam
> mesh ini.** Dua bagian dari naskah yang sama menyebut benda yang sama dengan
> dua bentuk yang saling meniadakan: kalau Risk adalah agent, ia bisa
> dipengaruhi; kalau ia komponen governance, ia bukan peserta debat §14.11.
>
> Yang paling masuk akal, dan cukup satu kalimat: **Risk adalah komponen
> governance yang MENAMPILKAN DIRI sebagai peserta di ruang debat, tetapi tidak
> terdaftar sebagai agent dan tidak bisa dipanggil agent lain.** Vetonya sah
> justru karena ia bukan peer.

---

## §14.45 — Control Plane vs Agent Data Plane

| Control Plane | Data Plane |
|---|---|
| Agent Registry · Identity · Policy · Permission · Risk · Budget · Credentials · Deployment · Trust · Governance | Agent Runtime · Inference · Tool Calls · Memory Retrieval · Execution · Communication |

> Agent data plane **tidak boleh mengubah control plane sembarangan**.

---

> ⭐⭐ **Sepuluh berbanding enam, dan `Budget` serta `Trust` di sisi kontrol
> adalah penempatan yang benar.** Anggaran yang bisa diubah oleh yang
> membelanjakannya bukan anggaran; skor kepercayaan yang bisa ditulis oleh yang
> dinilai bukan skor. Keduanya dihitung **dari** peristiwa data plane, tetapi
> disimpan dan ditegakkan di control plane.

> 🛑 **Satu kata merusak batasnya: "sembarangan".**
>
> §8.42 menulis aturan sejenis tanpa keringanan — *kode agent tidak boleh
> mengimpor `security/`* — dan itu bisa ditegakkan satu baris di CI. *"Tidak
> boleh mengubah control plane **sembarangan**"* tidak bisa ditegakkan sama
> sekali: setiap perubahan yang lolos akan dianggap tidak sembarangan.
>
> Batas keras yang dilunakkan adverbia adalah batas yang hilang. Bertaut dengan
> struktur repositori §14.51 yang memecah `security/` dan `agent-security/`
> menjadi dua pohon, sehingga aturan impor §8.42 kini tidak jelas berlaku ke
> yang mana. Lihat **E-121**.

---

## §14.46 — Collective Cognitive Runtime

Phase 9 punya *Cognitive Runtime*; Phase 14 menambahkan **Collective Cognitive
Runtime**:

```
Problem → Intent → Context → Problem Decomposition → Agent Selection
→ Task Allocation → Parallel Execution → Agent Communication
→ Evidence Aggregation → Conflict Resolution → Simulation
→ Decision → Action → Verification
```

---

> ⭐⭐ **`Evidence Aggregation` sebelum `Conflict Resolution` sebelum
> `Simulation` adalah urutan yang benar, dan ia jarang dibuat benar.**
> Mengumpulkan bukti dulu berarti perselisihan dinilai di atas bahan yang sama;
> menyimulasikan sesudahnya berarti yang diuji adalah keputusan yang sudah
> melewati perselisihan, bukan usul mentah. Ini §12 yang dipasang di tempat yang
> tepat pada alur kolektif.

> 🛑 **Tetapi `POLICY_CHECK` HILANG — dan itu justru langkah yang butir H-18
> tutup, persis di tempat yang saya usulkan.**
>
> Mesin keadaan kognitif §9.29 menaruh `POLICY_CHECK` **setelah `PLANNING` dan
> sebelum `DECISION`/`ACTION`**, ditambah `REQUIRES_CONFIRMATION` sebagai
> keadaan tersendiri. Rantai kolektif di atas melompat `Simulation → Decision →
> Action` tanpa keduanya.
>
> Ini rantai **keempat** di Phase 14 yang berakhir di tindakan tanpa titik di
> mana kebijakan diperiksa atau manusia bisa menahan — setelah §14.20 (kehilangan
> `Consent`, `Rate Limit`, `Confirmation`), §14.37, dan §14.38. Empat kali bukan
> kelalaian penulisan; itu pola. Lihat **E-117** / [#93](../../issues/93).

---

## §14.47 — Collective Learning

```
Outcome → Evaluation → Agent Performance → Team Performance
→ Communication Quality → Prediction Error → Policy Evaluation → Learning
```

> HumanVerse belajar bukan hanya **agent mana yang bagus**, tetapi:
> **kombinasi agent mana yang bagus untuk masalah tertentu.**

---

> ⭐⭐⭐ **Perbedaan antara "agent mana" dan "kombinasi mana" adalah perbedaan
> antara menilai bagian dan menilai sistem — dan hampir semua sistem multi-agent
> hanya melakukan yang pertama.**
>
> Ia juga satu-satunya cara §14.31 bisa dijawab dari data: kerentanan yang lahir
> dari **gabungan** agent hanya akan terlihat pada metrik yang mengukur
> gabungan.
>
> ⭐ `Policy Evaluation` di dalam lingkaran belajar berarti **kebijakan ikut
> dinilai**, bukan hanya agent. Kebijakan yang terlalu ketat terlihat sebagai
> pekerjaan yang tidak selesai; yang terlalu longgar sebagai insiden. Tidak ada
> naskah sebelumnya yang menaruh kebijakan di dalam umpan balik.

> ⚠️ **`Prediction Error` mewarisi masalah B-27 dalam bentuk baru: kombinasi
> yang belum pernah dipakai tidak punya galat.** Untuk agent tunggal, cold start
> selesai setelah beberapa pemakaian; untuk **kombinasi**, jumlah yang harus
> dipelajari tumbuh cepat sekali — dua puluh agent memberi ratusan pasangan dan
> ribuan tripel. Praktisnya: pembelajaran kombinasi hanya akan pernah menutupi
> segelintir team yang sering dipakai, dan itu **justru alasan §14.15 (team
> siap pakai) masuk akal** — team yang tetap adalah kombinasi yang bisa
> terkalibrasi.

---

## §14.48 — Agent Team Optimization

```
Problem A: Research + Analyst + Verifier
Problem B: Planner + Coder + QA + Security
Problem C: Travel + Budget + Weather
```

**Optimal Agent Team** dibangun berdasarkan: **task · complexity · risk ·
budget · deadline · quality requirement**.

---

> ⭐⭐ **Ini tempat pertama di delapan belas naskah di mana OPTIMASI benar-benar
> pantas dipakai — dan perbedaannya perlu dinyatakan.**
>
> Butir **C-16** dan **C-20** menolak optimasi bukan karena optimasi buruk,
> melainkan karena yang dioptimalkan di sana adalah **hidup seseorang** dengan
> bobot yang **disimpulkan**, bukan dikonfirmasi. Di sini yang dioptimalkan
> adalah **susunan mesin**, bobotnya diberikan oleh permintaan
> (`deadline`, `budget`, `quality requirement`), dan salahnya bisa dibatalkan.
>
> Kalau perbedaan itu tidak ditulis, dua hal yang berlawanan akan tampak seperti
> satu kebijakan yang tidak konsisten.

> ⚠️ **`risk` di daftar ini harus berarti "risiko menentukan komposisi", bukan
> "risiko bisa ditukar dengan kecepatan".** Untuk R3 ke atas, `Security` dan
> `Verifier` bukan anggota opsional yang dibuang ketika `deadline` mendesak —
> dan Problem B yang memuat keduanya sebaiknya jadi aturan, bukan contoh.

---

## §14.49 — Agent Team Memory

```
Team → Outcome → Performance → Memory
```

```
Team:         Research + Analyst + Verifier
Success:      94%
Known issue:  Analyst terlalu mahal
Future:       Use cheaper Analyst for low-risk research
```

---

> ⭐⭐⭐ **Ini pertama kalinya sistem menuliskan pelajaran TENTANG DIRINYA
> SENDIRI dalam kalimat, lengkap dengan rencana perubahan.** Bentuknya persis
> bentuk ADR: keadaan, masalah yang diketahui, keputusan berikutnya. Sampai
> sekarang semua pembelajaran di HumanVerse berupa angka; ini berupa **alasan**,
> dan alasan bisa dibaca manusia.

> 🛑 **Justru karena bisa dibaca, ia harus bisa DIBANTAH — karena baris `Future`
> adalah kebijakan yang ditulis sistem untuk dirinya sendiri.**
>
> *"Use cheaper Analyst for low-risk research"* akan mengubah perilaku tanpa ada
> orang yang memutuskannya. Butir **H-7** sudah mencatat bahwa self-improving
> agent sulit diaudit, dan jawabannya waktu itu: simpan **metadata** dan beri
> **rollback otomatis** (§47 naskah 4). Keduanya berlaku di sini, ditambah satu
> yang khas: **`Future` adalah usul sampai disetujui, bukan setelan yang sudah
> berlaku** — dan §14.60 sudah punya tempat untuk menampilkannya.
>
> ⚠️ Dan `Success: 94%` mewarisi **B-26**: *success criteria* tidak pernah
> didefinisikan bentuknya. Sembilan puluh empat persen dari apa — tugas selesai,
> tugas benar, atau pengguna puas? Ketiganya berbeda, dan angka yang tidak
> menyatakan penyebutnya akan dipakai seolah menyatakan ketiganya.

---

## §14.50 — Collective Intelligence Score

```
Individual Agent Performance + Communication + Coordination
+ Conflict Resolution + Outcome Quality + Safety + Cost + Latency
        ↓
Collective Intelligence Score
```

---

> ⭐ **Mengukur kecerdasan kolektif — bukan hanya keluarannya — adalah gagasan
> yang benar, dan `Conflict Resolution` sebagai komponen menunjukkan
> pengukurnya paham bahwa perselisihan adalah bagian dari bekerja, bukan
> kegagalan.**

> 🛑 **Tetapi `Safety` sebagai SUKU PENJUMLAHAN adalah kesalahan bentuk, dan ia
> membatalkan hukum yang naskah ini sendiri tetapkan dua puluh bagian
> kemudian.**
>
> §14.64 menyatakan *"More agents must not automatically mean more autonomy"*
> karena `collective risk > individual risk`. Sebuah skor yang **menjumlahkan**
> keselamatan dengan tujuh hal lain melakukan persis kebalikannya: team yang
> cepat, murah, dan terkoordinasi baik dapat mencapai skor yang sama dengan team
> yang aman — dan kalau skor itu dipakai memilih team (§14.48) atau menaikkan
> otonomi (§14.61), sistem akan bergerak ke arah yang salah tanpa ada yang
> melanggar aturan.
>
> Bentuk yang benar sudah dipakai di tempat lain di HumanVerse: **keselamatan
> adalah gerbang, bukan suku.** Risk Engine §8.17 tidak menjumlahkan risiko
> dengan manfaat; ia **menolak**. Skor kolektif sebaiknya berbentuk *skor
> kinerja × syarat keselamatan terpenuhi*, atau tidak dihitung sama sekali untuk
> team yang punya pelanggaran kebijakan.
>
> ⚠️ Ditambah kemunculan **keenam** masalah arah: `Cost` dan `Latency` kecil
> lebih baik, enam sisanya besar lebih baik — dan kali ini ia bukan kriteria
> seleksi melainkan **penjumlahan sungguhan**, jadi salah arah langsung menjadi
> angka yang salah. Lihat **B-29** / [#96](../../issues/96).
