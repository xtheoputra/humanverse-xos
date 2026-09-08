# 253 — §18.22–§18.25 Safety Kernel, Information Integrity, Global Risk & Early Warning

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.22 — Global Intelligence Safety Kernel

> Ini menjadi sangat penting.
>
> ```
> World Data → Validation → Provenance → Safety → Policy → Reasoning → Insight
> ```

> Sistem harus mencegah: `misinformation · manipulated data · fabricated
> sources · malicious agents · poisoned knowledge · prompt injection ·
> coordinated manipulation · unsafe autonomous decisions`

---

> ⭐⭐⭐⭐ **Ini rantai keselamatan pertama di repo ini yang berdiri di jalur
> MASUK sebuah mesin penalaran — dan ia menjawab, dalam bentuk, separuh H-18
> yang masih terbuka.**
>
> **H-18** ditutup oleh §9.29 yang menaruh `POLICY_CHECK` sebelum
> `DECISION`/`ACTION` — keselamatan jalur **keluar**. Yang tercatat masih
> menganga adalah keselamatan jalur **masuk**: apa pun yang masuk langsung dari
> `RECEIVED` ke `UNDERSTANDING`, dan itu jalur yang dilewati jurnal (separuh
> **C-3**/[#21](../../issues/21)). §8.20 memberi tiga langkah
> (`Content Classifier → Untrusted Context → Policy Boundary`); rantai ini
> memberi **enam**, dan menaruh `Provenance` di antaranya.
>
> ⭐ `Provenance` sebagai **gerbang**, bukan catatan, adalah yang membedakannya:
> data yang tidak bisa menyebutkan asalnya **berhenti di situ**, sebelum
> penalaran menyentuhnya. Untuk sistem yang menelan `internet knowledge`
> (§18.4), itu satu-satunya pertahanan yang bekerja sebelum tahu isinya benar
> atau salah.
>
> ⚠️ Tapi bentuknya ada, penerapannya belum: **rantai ini melindungi World
> Data, bukan jurnal.** Lubang asli H-18 tetap terbuka di tempat aslinya — dan
> kini terbukti bahwa bentuk penutupnya bisa dibangun.

> ⭐⭐ **Delapan ancaman yang didaftar adalah daftar ancaman paling nyata di dua
> puluh dua naskah**, dan tiga di antaranya belum pernah disebut sama sekali:
> `poisoned knowledge` (racun yang ditanam agar dipelajari nanti),
> `coordinated manipulation` (banyak sumber yang tampak bebas padahal satu), dan
> `prompt injection` — yang terakhir khususnya, sebab §18.4 memasukkan teks dari
> internet ke pipeline yang berujung pada penalaran.

> 🛑🛑 **Tetapi rantai ini berhenti di `Insight`, dan pipeline yang benar-benar
> dipakai pengguna (§18.30) TIDAK MELEWATINYA.**
>
> §18.30 memberi: `Question → Intent → Personal Context → World Context →
> Knowledge Retrieval → World Model → Reasoning → Simulation →
> Personal Relevance → Answer` — sepuluh langkah, **tanpa `Safety`, `Policy`,
> maupun `Risk`**. Dan §18.10 berakhir di `Personal Scenario`, juga tanpa.
>
> Ini pola yang sudah tercatat empat kali (**E-117**/[#93](../../issues/93) ·
> **E-124**/[#106](../../issues/106) · **E-130**/[#111](../../issues/111)) —
> **tetapi dengan satu perbedaan yang penting dan menguntungkan**: di tiga kasus
> sebelumnya gerbangnya memang **tidak ada**. Di sini gerbangnya **ada, di
> naskah yang sama, dua belas bagian sebelumnya** — ia hanya tidak dipasang di
> jalurnya.
>
> ⇒ Ini masalah **perkabelan, bukan rancangan**, dan karenanya jauh lebih murah:
> `Reasoning` di §18.30 adalah `Reasoning` yang sama di §18.22, jadi yang perlu
> dinyatakan cuma bahwa **tidak ada jalan menuju `Answer` yang tidak melewati
> `Safety → Policy`.** Lihat **E-143** / [#125](../../issues/125).

---

## §18.23 — Information Integrity Engine

> `Source Verification · Cross Source Validation · Contradiction Detection ·
> Claim Verification · Temporal Consistency · Entity Consistency ·
> Evidence Ranking · Manipulation Detection`

> Contoh: Source A *"Event happened."* · Source B *"Event did not happen."* ·
> Source C *"Event happened yesterday."*
>
> HumanVerse **tidak boleh langsung memilih A.** Ia harus menghasilkan:
>
> ```
> Conflict detected.  Current confidence: 0.61  Status: UNRESOLVED
> ```

---

> ⭐⭐⭐⭐⭐ **`UNRESOLVED` sebagai KELUARAN yang sah adalah hal terbaik di naskah
> ini, dan belum pernah ada satu kali pun dalam dua puluh dua naskah.**
>
> Setiap mekanisme keyakinan sebelumnya di repo ini berakhir dengan **memilih**:
> Confidence Layer §19 memberi jawaban dengan angka rendah lalu *ask user*;
> `Evidence Ranking` §17.26 mengurutkan; §17.9 menentukan tingkat mana yang
> boleh jadi dasar rekomendasi. Semuanya menghasilkan jawaban. Bagian ini
> mengizinkan sistem **berhenti tanpa jawaban** dan menyatakan bahwa itu
> keadaan akhir yang sah.
>
> Itu penting justru karena berlawanan dengan tekanan produk: sistem yang boleh
> berkata *"sumbernya bertentangan, saya belum tahu"* akan terasa kurang pintar
> dan **jauh lebih layak dipercaya** — sebab pengguna akhirnya bisa membedakan
> hal yang sistem ketahui dari hal yang sistem karang. Ini padanan sempurna dari
> §17.19 `missing data` sebagai kategori tersendiri (**B-14**/[#26](../../issues/26)):
> ketiadaan yang terlihat, bukan ketiadaan yang menyamar sebagai normal.
>
> ⭐ Dan contohnya dipilih dengan cermat: Source C **tidak membantah** A, ia
> menggeser waktunya. Ketiga sumber bisa benar sekaligus. Itu memaksa
> `Temporal Consistency` menjadi pemeriksaan tersendiri — dan memang ia ada di
> daftar delapan.

> ⚠️ **Sisa yang perlu ditulis: apa yang terjadi SESUDAH `UNRESOLVED`.**
> Konflik yang tidak pernah selesai akan menumpuk. Yang belum ada: siapa atau
> apa yang meninjaunya, berapa lama ia bertahan sebelum kedaluwarsa, dan apakah
> ia **menghalangi** kesimpulan hilir yang bergantung padanya — yang terakhir
> paling menentukan, sebab graf §18.6 akan tetap merambatkan tepi yang
> statusnya `UNRESOLVED` kecuali dinyatakan tidak boleh.

> ⚠️ **Dan `0.61` muncul lagi tanpa cara menghitungnya** — sumbu keempat di
> naskah ini yang berdesimal tanpa rumus (§18.5 `0.94`, §18.8 empat angka,
> §18.24 `0.42`/`0.74`, di sini). Bagian **D** sudah mencatat lima model angka
> pengguna tanpa rumus; ini menambah satu kelas lagi.

---

## §18.24 — Global Risk Intelligence

> World Model dapat menghasilkan: `Economic · Climate · Cyber · Infrastructure ·
> Supply Chain · Technology · Operational · Social · Personal Risk`
>
> Tetapi risk harus punya: `Probability · Impact · Confidence · Time Horizon ·
> Evidence`
>
> Contoh: `Probability: 0.42 · Impact: High · Confidence: 0.74 · Horizon: 90 days`

---

> ⭐⭐⭐⭐ **Memisahkan `Probability` dari `Confidence` adalah pembedaan yang
> paling sering dicampur di seluruh bidang ini, dan naskah ini memisahkannya
> dengan benar.**
>
> `Probability 0.42` berkata *"kalau dunia berjalan seperti model saya, ini
> terjadi empat kali dari sepuluh"*. `Confidence 0.74` berkata *"dan inilah
> seberapa besar saya percaya pada model itu"*. Sistem yang hanya punya satu
> angka tidak bisa membedakan **risiko yang dipahami dengan baik** dari
> **ketidaktahuan yang dibungkus angka** — padahal keduanya menuntut tindakan
> yang berbeda: yang pertama diambil keputusannya, yang kedua dicari datanya
> dulu.
>
> ⭐⭐ Ditambah `Time Horizon`: risiko tanpa jangka waktu tidak bisa
> ditindaklanjuti maupun dinilai benar-salahnya belakangan. **`Horizon: 90
> days` menjadikan klaim ini bisa diperiksa ketika 90 hari lewat** — dan itu
> satu-satunya cara sebuah mesin risiko bisa belajar dari dirinya sendiri.
> Belum ada mekanisme kalibrasi mana pun di repo ini yang punya syarat ini.

> 🛑 **Tetapi ini kosakata `Risk` yang KETIGA, dan ketiganya bernama sama di
> tempat yang berbeda.**
>
> | Tempat | Mengukur | Bentuk |
> |---|---|---|
> | §8.17 `Risk Engine` | risiko **aksi** | `R0–R4` ordinal (**H-21**) |
> | §17.38/§17.46 `Risk Engine` | **sinyal kesehatan** | tujuh kategori `INFO…EMERGENCY` |
> | **§18.24** | **risiko dunia** | probability · impact · confidence · horizon |
>
> **E-136** sudah mencatat dua yang pertama akan tertukar dalam kode dan
> mengusulkan `health_signal` untuk yang kedua. Yang ketiga ini paling berbeda
> bentuknya — ia bukan tangga sama sekali — sehingga menamainya `Risk` akan
> membuat kode yang menerima "risk" tidak tahu bentuk apa yang datang.
> Usul: `world_risk`, dan `Risk` tanpa awalan tetap milik §8.17 (risiko aksi),
> sebab itu yang dirujuk **H-15** dan [`spec/05`](../spec/05-AGENT-CONTRACTS.md).
> Lihat **E-141** / [#130](../../issues/130).

> ⚠️ **`Personal Risk` di daftar sembilan itu bukan sekelas delapan lainnya.**
> Delapan mengukur sistem; yang satu ini mengukur seseorang — dan ia adalah
> tempat *"pekerjaan Anda berisiko"* akan lahir. Ia menuntut bukan cuma
> `Evidence` melainkan aturan penyampaian seperti §17.38, dan `Impact: High`
> tanpa ambang tidak cukup untuk itu.

---

## §18.25 — Early Warning System

```
Signal → Anomaly → Pattern → Acceleration → Risk → Early Warning
```

> Contoh: `supply shortage signals → transport delays → inventory decline →
> price increase → risk escalation`
>
> HumanVerse dapat memberikan *"Early warning detected."* Bukan: *"This
> definitely will happen."*

---

> ⭐⭐⭐ **Perbedaan antara *"terdeteksi"* dan *"pasti terjadi"* ditulis sebagai
> pasangan yang eksplisit — bentuk yang sama dengan §17.7 (*"State ≠
> diagnosis"*) dan §17.16.**
>
> Pemilik tidak hanya melarang kalimat yang salah, ia **memberikan kalimat
> penggantinya**. Larangan tanpa pengganti akan diisi oleh siapa pun yang
> menulis salinan antarmukanya; larangan dengan pengganti bisa diperiksa.
> Ini kebiasaan ketiga naskah berturut-turut, dan ia jauh lebih berharga
> daripada pernyataan prinsip mana pun.

> ⭐⭐ **Rantai enam langkahnya juga mensyaratkan penumpukan bukti, bukan satu
> pemicu.** `Signal → Anomaly → Pattern → Acceleration` berarti satu
> penyimpangan tidak cukup: ia harus berulang menjadi pola, lalu pola itu harus
> mempercepat. Itu obat langsung untuk peringatan palsu, dan ia memakai persis
> bentuk yang §18.7 sediakan.

> 🛑🛑 **Tetapi rantainya berakhir dengan MENGELUARKAN peringatan, tanpa
> gerbang dan tanpa penerima yang ditentukan — dan dua dari event §18.5 adalah
> wabah dan gempa.**
>
> Sebuah peringatan **adalah tindakan**, bukan informasi netral: ia mengubah
> perilaku orang yang menerimanya. Peringatan yang salah tentang kelangkaan
> pasokan menyebabkan penimbunan yang **menciptakan** kelangkaan itu; peringatan
> yang salah tentang wabah atau bencana menyebabkan kepanikan, dan yang benar
> tetapi diabaikan menyebabkan hal yang lebih buruk. Di banyak yurisdiksi
> peringatan bencana dan kesehatan masyarakat adalah **kewenangan yang diatur**,
> bukan fitur produk.
>
> Yang tidak ada di §18.25: **siapa yang menerima** (satu pengguna? organisasi?
> kota?), **ambang mana yang memicu**, **apakah manusia meninjau sebelum
> keluar**, dan **apa yang terjadi ketika peringatannya keliru**.
>
> ⭐ Bahannya lengkap di repo ini dan tinggal disambungkan: §17.38 sudah
> memberi **tujuh kategori dengan escalation berjenjang** — bentuk yang tepat
> untuk menjawab *"seberapa keras ini disampaikan dan ke mana ia diteruskan"*;
> §18.24 memberi `Confidence` dan `Horizon` sebagai penentu ambangnya; **H-15**
> memberi aturan konfirmasi manusia. Usul minimum: **peringatan yang menyentuh
> keselamatan atau kesehatan publik tidak pernah keluar tanpa tinjauan manusia,
> dan tidak pernah keluar melampaui orang yang datanya memicunya.**
> Lihat **C-28** / [#123](../../issues/123).
