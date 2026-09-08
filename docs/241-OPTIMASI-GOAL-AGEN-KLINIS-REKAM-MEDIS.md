# 241 — §17.23–§17.28 Optimization, Goal Engine, Health Agents, Research Agent, Clinical Integration & Medical Records

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.23 — Personalized Health Optimization

> Bukan: *"Maximum health."* Tetapi:
>
> **Health + Career + Fitness + Social + Time + Money + User Preferences**
>
> Karena **kehidupan nyata penuh trade-off.**

---

> ⭐⭐⭐ **Ini menjawab keberatan terberat yang saya catat terhadap Phase 12 —
> dan menjawabnya dengan menolak fungsi tujuan yang salah, bukan dengan
> memperbaikinya.**
>
> Butir **C-20** ([#85](../../issues/85)) mencatat bahwa §12.22 *Life
> Optimization Engine* menaikkan taruhan **C-16** ([#71](../../issues/71)):
> model utilitas yang bobotnya **disimpulkan** berhenti dipakai untuk
> **membandingkan** (§9.24) dan mulai dipakai untuk **memaksimalkan**. Dan saya
> catat satu akibat khususnya: *"`maximize expected_goal_utility` dengan
> kesehatan sebagai **batas** akan selalu mendorong sampai tepat di batas."*
>
> §17.23 menolak persis bentuk itu. `Health` bukan batas melainkan **salah satu
> suku**, berdampingan dengan `Time` dan `Money` — dan kalimat *"kehidupan nyata
> penuh trade-off"* mengakui bahwa memaksimalkan satu sumbu berarti mengorbankan
> yang lain. Untuk fase kesehatan, godaan terbesarnya justru menjadikan
> kesehatan sebagai satu-satunya yang dimaksimalkan.

> 🛑 **Tetapi syarat C-16 belum terpenuhi: `User Preferences` adalah SUKU, bukan
> BOBOT yang dikonfirmasi.**
>
> Tiga syarat **C-16** ([#71](../../issues/71)) berbunyi: optimasi **tidak
> dijalankan atas bobot yang disimpulkan — hanya atas bobot yang dikonfirmasi
> pengguna**. Tujuh suku di sini tidak menyebut dari mana bobotnya datang, dan
> `User Preferences` sebagai suku ketujuh justru menyiratkan bahwa preferensi
> adalah **satu masukan di antara tujuh**, bukan **yang menentukan enam
> lainnya**.
>
> Perbaikannya satu kalimat dan tidak menghilangkan apa pun: **tujuh suku itu
> punya bobot, dan bobotnya milik pengguna** — disimpulkan sebagai usul,
> berlaku hanya setelah dikonfirmasi, dan bisa diubah kapan saja. §9.25 sudah
> menuntut *"user harus dapat mengubahnya"*; §14.60 sudah memberi tombol
> `Edit`-nya.

---

## §17.24 — Health Goal Engine

```
Goal → Milestone → Training Plan → Weekly Target → Daily Action
```

```
Improve endurance → 8-week program → 3 sessions/week → Today's session
```

---

> ⭐⭐ **Lima tingkat dari niat sampai tindakan hari ini, dan tiap tingkat bisa
> diperiksa sendiri.** Ini bentuk yang sama dengan `Task Composer` §16.25 dan
> `Skill Composition` §16.24 — satu pola dipakai konsisten di tiga fase, dan
> konsistensi semacam itu jarang di repo ini.

> ⚠️ **`8-week program` adalah angka pertama yang muncul tanpa sumber.**
> Delapan minggu berasal dari mana — kondisi awal pengguna, tujuan, atau aturan
> umum? Ini bentuk **B-1**/**B-26** yang khas: *success criteria* dan jadwal
> yang tidak menyatakan dasarnya akan dioptimalkan sistem apa pun isinya.
> §12.14 *Assumption Engine* adalah tempat yang benar untuk menyatakannya.

---

## §17.25 — Health Agent Ecosystem

| Agent | Fungsi |
|---|---|
| Health Intelligence Agent | koordinasi |
| Sleep · Fitness · Nutrition · Recovery · Wellbeing Agent | domain |
| Health Data Agent | data |
| Preventive Agent | pattern/anomaly |
| Health Research Agent | evidence |
| **Health Safety Agent** | **safety** |

> **Health Safety Agent berada di governance layer, bukan menjadi agen yang
> mengejar tujuan sendiri.**

---

> ⭐⭐⭐⭐ **Kalimat itu memperbaiki keberatan yang saya catat DUA KALI — dan
> memperbaikinya tanpa diminta.**
>
> §14.13 memberi veto kepada *"Risk **Agent**"* sementara §14.44 menetapkan
> *"governance tidak boleh menjadi agent biasa"*; saya catat bahwa dua bagian
> naskah yang sama menyebut benda yang sama dengan dua bentuk yang saling
> meniadakan. §15.21 mengulanginya: `Safety` berdiri di baris tabel yang sama
> dengan `Interior` dan `Navigator` — persis sebagai agent biasa
> ([#89](../../issues/89)).
>
> §17.25 menyatakannya secara langsung, di baris yang sama dengan agent-nya:
> **berada di governance layer, bukan mengejar tujuan sendiri.** Itu bukan
> sekadar penegasan — ia berarti Health Safety Agent tidak terdaftar sebagai
> peer, tidak bisa dipanggil agent lain, dan tidak ikut negosiasi §14.14.
>
> ⭐ Dan `Health Research Agent` yang terpisah dari agent domain adalah
> pemisahan kedua yang benar: **yang mencari bukti tidak sama dengan yang
> memakai bukti** — sejalan dengan `Evaluator`/`Verifier` §14.16, tetapi kali
> ini di luar jalur kepentingan.

> ⚠️ **Sepuluh agent baru, dan hitungannya kini jauh melewati enam puluh.**
> 25 berhierarki §11.4 · tujuh di contoh tanpa terdaftar (**E-95**) · dua belas
> Phase 12 (**G-13**/[#89](../../issues/89)) · enam Phase 15 · sepuluh di sini.
> Kriteria **G-13** berlaku lagi: `Health Data Agent` dan `Preventive Agent`
> keduanya deterministik dan tidak memanggil tool — **service**, bukan agent.

---

## §17.26 — Health Research Agent

```
Question → Evidence Retrieval → Source Evaluation → Evidence Ranking
→ Answer → Uncertainty
```

Harus membedakan: **Established evidence · Emerging evidence · Weak evidence ·
Unknown.**

---

> ⭐⭐⭐ **`Unknown` sebagai kategori KEEMPAT yang setara adalah yang membuat
> tiga lainnya berarti.**
>
> Sebuah sistem yang hanya punya tingkatan *kuat/sedang/lemah* akan selalu
> menemukan sesuatu untuk dikatakan. `Unknown` memberinya izin untuk menjawab
> **"belum diketahui"** — dan untuk pertanyaan kesehatan, itu jawaban yang benar
> lebih sering daripada yang nyaman diakui.
>
> Ia juga pasangan langsung dari §14.35 (*"tidak boleh mengarang data"*): di
> sana kekosongan data berakhir di diam, di sini kekosongan **bukti** berakhir
> di *Unknown*.

> ⭐⭐ **Dan empat tingkat ini adalah yang §17.9 butuhkan.** Graf pengetahuan
> kesehatan membedakan `Observed / Correlation / Hypothesis / Causal evidence`;
> Research Agent membedakan kekuatan buktinya. Keduanya bertemu di satu aturan
> yang tinggal ditulis: **kenaikan sebuah relasi menjadi `Causal evidence` hanya
> lewat agent ini**, dan `Weak`/`Unknown` tidak pernah menaikkan apa pun.

> ⚠️ **`Evidence Retrieval` dari mana?** Naskah tidak menyebut satu pun sumber —
> berbeda dari §15.6, §16.7, §16.14, dan §16.22 yang menyebut pustaka dan
> protokol nyata. Untuk bukti kesehatan, sumbernya menentukan segalanya, dan
> pilihan itu berbentuk ADR. Ditambah: **bukti berubah**, jadi jawaban yang
> disimpan perlu tanggal dan versi sumbernya — §17.41 sudah menuntut *which
> model, which version*.

---

## §17.27 — Clinical Integration Layer

```
HumanVerse → Health Data Exchange → Healthcare Provider → Clinician
```

> Dengan **consent eksplisit.** HumanVerse **tidak mengambil alih keputusan
> klinis.**

---

> ⭐⭐ **Menandainya "untuk masa depan" dan meletakkannya di belakang consent
> eksplisit adalah dua keputusan yang benar** — dan §17.53 mengeluarkannya dari
> jalur MVP, yang konsisten.

> 🛑 **Tetapi "Health Data Exchange" adalah satu-satunya tempat di empat naskah
> terakhir di mana standar nyata TIDAK disebut — padahal justru di sini standar
> hampir wajib secara hukum.**
>
> §15.6 menyebut lima pustaka SLAM; §16.7 lima pustaka planning; §16.14 lima
> protokol IoT; §16.22 ROS2; §16.26 empat simulator. Kebiasaan itu berhenti
> tepat di tempat pertukaran data kesehatan, yang di hampir semua yurisdiksi
> punya standar dan kewajiban tersendiri — bentuk berkas, penyandian istilah
> medis, jejak audit, dan siapa yang boleh menjadi penerima.
>
> Ditambah tiga hal yang tidak disebut sama sekali: **data kesehatan adalah
> kategori khusus** dengan dasar hukum pemrosesan sendiri; **pengiriman lintas
> negara** punya aturannya sendiri (dan `processing_location` §17.4 adalah field
> yang tepat untuk menegakkannya); dan **penerima di sisi klinis punya kewajiban
> yang berbeda** dari HumanVerse. Lihat **C-26** / [#118](../../issues/118).

---

## §17.28 — Medical Record Intelligence

Dokumen: **laboratory reports · prescriptions · clinical notes · imaging
reports · health documents.**

```
Document → OCR → Structure → Entity Extraction → Medical Knowledge Mapping
→ Timeline
```

> Informasi medis harus tetap memiliki **provenance.**

---

> ⭐⭐ **`provenance` sebagai syarat adalah hal yang benar dan konsisten dengan
> §17.4 (`source`) serta §17.41.** Untuk dokumen medis ia lebih penting lagi:
> nilai laboratorium tanpa tanggal dan laboratorium asalnya bisa menyesatkan
> meski angkanya benar.

> 🛑 **Tetapi rantai enam langkah ini adalah tempat paling berbahaya untuk
> halusinasi di seluruh proyek, dan ia tidak punya satu pun langkah
> verifikasi.**
>
> `Entity Extraction` dan `Medical Knowledge Mapping` dari catatan klinis
> berarti mengubah teks bebas menjadi istilah medis berkode. Kesalahan di sini
> tidak terlihat seperti kesalahan: ia menghasilkan istilah yang **valid**,
> masuk ke `medical_records` (§17.43), lalu ikut ke `Timeline` §17.8 dan menjadi
> masukan model lain — sementara §17.19 hanya membedakan *sensor anomaly* dari
> *human anomaly*, bukan **kesalahan ekstraksi**.
>
> Dan naskah ini punya obatnya di bagian lain: §17.36 memberi metrik evaluasi
> lengkap (sensitivity, specificity, kalibrasi, **subgroup performance**) untuk
> `health_models` — tetapi pipeline ekstraksi ini **tidak terdaftar sebagai
> model**, jadi tidak ada yang mewajibkannya diukur.
>
> Tiga hal yang perlu ditulis, dan semuanya sudah punya preseden di repo ini:
> **(1)** pipeline ini terdaftar di `health_models` §17.35 dan tunduk §17.36;
> **(2)** hasil ekstraksi menyimpan **kutipan sumbernya** (potongan teks asli),
> tidak hanya istilah hasilnya — `provenance` yang bisa dibuka; **(3)** dokumen
> medis yang diekstraksi **ditandai belum terverifikasi sampai penggunanya
> mengonfirmasi**, karena ia satu-satunya yang memegang aslinya. Lihat
> **C-26** / [#118](../../issues/118).

> ⚠️ **`imaging reports` disebut, `imaging` tidak.** Membaca **laporan**
> pencitraan adalah pekerjaan teks; membaca **citranya** adalah pekerjaan yang
> sama sekali lain dan diatur sebagai alat kesehatan di banyak yurisdiksi.
> Naskah dengan tepat hanya menyebut laporannya — dan batas itu layak ditulis
> sebagai batas, bukan dibiarkan sebagai pilihan kata.
