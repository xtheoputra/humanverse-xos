# 237 — §17.6–§17.9 Health Digital Twin, Bio State Vector, Health Timeline & Health Knowledge Graph

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh satu, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §17.6 — Health Digital Twin

> Ini **inti Phase 17.**

```
Health Twin
├── Physical State    ├── Activity State   ├── Sleep State
├── Recovery State    ├── Nutrition State  ├── Fitness State
├── Behavioral State  ├── Stress Indicators
├── Health History    └── Health Goals
```

Setiap state mempunyai: **value · confidence · source · timestamp ·
uncertainty.**

> ⚠️ Angka lepas `7` di bagian ini — artefak salin-tempel, gejala **H-9**.

---

> ⭐⭐ **Lima field per state, dan `source` di antaranya adalah yang membuat
> §17.19 mungkin.** Membedakan *sensor anomaly* dari *human anomaly* menuntut
> tahu **dari mana angka itu datang**; tanpa `source`, keduanya terlihat sama.

> ⚠️ **`confidence` DAN `uncertainty` berdampingan adalah dua penyandian untuk
> satu fakta** — pola yang sama dengan `Risk: R2` + `Reversible: Yes` (**E-122**).
> Keduanya bisa berbeda suatu saat, dan yang mana dipercaya tidak ditulis.
>
> Yang mungkin dimaksud, dan sebaiknya dinyatakan: `confidence` = seberapa yakin
> sistem pada **nilainya**; `uncertainty` = **rentangnya** (§12.13 sudah memberi
> `confidence interval`). Kalau itu maksudnya, namanya sebaiknya `value_range`
> atau `interval` — karena dua kata yang berlawanan arti akan dibaca sebagai
> pengulangan, lalu salah satunya berhenti diisi.

> ⚠️ **`Health Goals` di dalam Twin mencampur dua hal yang berbeda: KEADAAN dan
> KEINGINAN.** Delapan state pertama adalah pengukuran; `Health Goals` adalah
> pernyataan pengguna. Menyimpannya di benda yang sama berarti *"twin"* berhenti
> berarti *"salinan keadaan"* — dan §17.21 menyimulasikan **atas** twin, jadi
> tujuan yang ikut masuk simulasi bisa terbaca sebagai keadaan awal.

---

## §17.7 — Human Bio State Vector

```yaml
bio_state:
  heart:   sleep:      recovery:   activity:
  mobility: respiratory: nutrition: hydration:
  fitness: fatigue:    stress:
```

> Namun: **State ≠ diagnosis.**
>
> `fatigue_score = 0.72` tidak berarti *"Anda menderita penyakit X"*, tetapi
> *"Data saat ini menunjukkan pola yang konsisten dengan peningkatan fatigue."*

---

> ⭐⭐⭐ **"State ≠ diagnosis" adalah tiga kata yang menyelamatkan seluruh fase
> ini — dan pemilik memberi contoh terjemahannya, bukan hanya prinsipnya.**
>
> Kebanyakan pengaman di dokumen mana pun berhenti pada aturan. Di sini aturannya
> disusul **kalimat pengganti yang bisa langsung dipakai antarmuka**: *"pola yang
> konsisten dengan"* alih-alih *"Anda menderita"*. Itu perbedaan antara kebijakan
> dan implementasi, dan ia diberikan gratis.
>
> Ia juga satu-satunya cara larangan §8.10 (*insurance scoring*, *employment
> scoring*) bisa bertahan: skor yang **tidak** mengklaim diagnosis lebih sulit
> dijual sebagai penilaian — meski, seperti **C-20** ([#85](../../issues/85))
> catat, ia tidak menghilangkan keberadaan datanya.

> ⚠️ **Sebelas medan, dan `fatigue` serta `stress` berdiri di daftar yang sama
> dengan `heart` dan `respiratory` — padahal keduanya jenis lain.**
> Detak jantung **diukur**; kelelahan **disimpulkan**. Menaruh keduanya dalam
> satu vektor dengan bentuk yang sama membuat perbedaan itu hilang tepat di
> tempat penyimpanan — dan tangga naskah 16 (`Observed ≠ Predicted ≠ Simulated ≠
> Certain`) sudah menyediakan kosakatanya. Satu field `kind: measured | derived`
> menutupnya.

> ⚠️ **Ini model angka pengguna yang KEENAM**, setelah *Human Genome of
> Behavior* (6 skor) · *Profile Engine* (5 atribut) · *HumanState* (7 medan) ·
> *Human Dashboard* (7 batang) · *DigitalTwin* (8 model) — lihat **A-19**
> ([#2](../../issues/2)). ⭐ Bedanya: yang ini **tidak mengklaim menggantikan**
> yang lain, ia sumbu biologis di sampingnya, dan §17.48 menyatakannya
> (`Life Twin` + `Health Twin`). Itu penyelesaian yang lebih baik daripada
> penggantian keenam.

---

## §17.8 — Health Timeline

```
06:30 Wake · 07:00 Breakfast · 08:00 Work
12:00 Lunch · 18:00 Workout · 22:30 Sleep
```

Ditambah: **sleep duration · HRV · heart rate · activity · mood · nutrition ·
stress indicators.** Kemudian HumanVerse mencari **hubungan temporal.**

---

> ⭐⭐⭐ **Timeline adalah struktur yang benar untuk pertanyaan yang benar-benar
> ditanyakan orang tentang tubuhnya — dan ia satu-satunya yang bisa membedakan
> "sebelum" dari "sesudah".**
>
> Korelasi antar-angka tidak punya arah; urutan waktu punya. Menyimpan segalanya
> sebagai deret waktu bersama adalah prasyarat untuk §17.9 (empat tingkat bukti)
> dan untuk satu-satunya bentuk sebab yang bisa disimpulkan tanpa eksperimen:
> **sesuatu yang selalu mendahului**.
>
> Ia juga yang membuat contoh §17.1 (*"ketika durasi tidurmu turun…"*) bisa
> diperiksa ulang alih-alih dipercaya.

> ⚠️ **`mood` masuk timeline tanpa disebut dari mana ia datang.** Sembilan
> sinyal lain punya sumber (perangkat atau catatan pengguna); `mood` tidak ada
> di `bio_state` §17.7, tidak ada di daftar wearable §17.3, dan tidak ada di
> §17.43. Kalau ia **dilaporkan sendiri**, ia sinyal paling berharga di daftar
> ini dan perlu tempat; kalau ia **disimpulkan** dari suara atau teks, ia
> menyentuh §17.16 dan menuntut pengaman yang sama.
>
> ⚠️ Ditambah catatan lama: `mood` sudah **keluar-masuk** model keadaan pengguna
> tiga kali (**E-102**). Di sini ia muncul lagi, di tempat keempat.

---

## §17.9 — Health Knowledge Graph

```
Sleep → Recovery → Energy → Workout → Fitness
Workout → Recovery → Sleep → Energy → Productivity
```

Tetapi graph harus membedakan:

```
Observed relationship
Correlation
Hypothesis
Causal evidence
```

> **Jangan langsung menganggap correlation sebagai causation.**

---

> ⭐⭐⭐⭐ **Ini menutup keberatan tertua di seluruh repo — E-81
> ([#7](../../issues/7)) — dan menutupnya dengan cara yang lebih baik daripada
> yang saya usulkan.**
>
> **E-16** (naskah 1 vs 3) mencatat dua urutan sebab yang berbeda untuk rantai
> tidur–mood–produktivitas. **E-81** mencatat bahwa `influences` kembali ke
> Human Knowledge Graph **tanpa bukti kausal**, dan bahwa naskah 4 sudah
> menyarankan menuliskannya sebagai *Causal Hypothesis* alih-alih sebagai sebab.
> Butir itu sudah terbuka sejak naskah pertama, dan setiap graf berikutnya
> menghindarinya dengan memakai relasi yang tidak kausal sama sekali (§14.33
> struktural, §15.11 geometris).
>
> §17.9 tidak menghindar. Ia **memberi empat tingkat** — dan empat, bukan dua,
> adalah yang membuatnya bisa dipakai:
>
> | Tingkat | Artinya | Boleh dipakai untuk |
> |---|---|---|
> | **Observed relationship** | terlihat bersama di data pengguna ini | menjelaskan |
> | **Correlation** | terukur, dengan kekuatan | menampilkan pola |
> | **Hypothesis** | diusulkan, belum diuji | mengusulkan eksperimen |
> | **Causal evidence** | ada buktinya | dasar rekomendasi |
>
> Dan kalimat penutupnya menyatakan larangannya secara langsung. Untuk graf yang
> menghubungkan tidur dengan produktivitas seseorang, **perbedaan antara tingkat
> 2 dan tingkat 4 adalah perbedaan antara pengamatan dan nasihat medis.**

> ⭐⭐ **Dua rantai contohnya juga tidak sama, dan itu disengaja atau
> beruntung — keduanya benar.** Rantai pertama `Sleep → Recovery → Energy →
> Workout → Fitness`; kedua `Workout → Recovery → Sleep → Energy →
> Productivity`. `Recovery` muncul di kedua rantai dengan **arah masuk yang
> berbeda** — dari tidur dan dari latihan. Itu justru gambaran yang benar:
> pemulihan punya lebih dari satu sebab, dan graf yang memaksa satu urutan
> tunggal (seperti **E-16** yang terbuka sejak naskah 1) tidak bisa
> menyatakannya.

> ⚠️ **Yang belum ada: siapa yang menaikkan sebuah relasi dari `Hypothesis` ke
> `Causal evidence`, dan atas dasar apa.** §9.17 menetapkan sebab hanya boleh
> disimpulkan setelah *repeated controlled experiments*; **B-16**/**C-8**
> mencatat eksperimen n-of-1 empat belas hari tanpa kelompok kontrol mudah salah
> simpul. ⭐ Bahannya sudah ada di naskah ini: §17.26 *Health Research Agent*
> punya `Evidence Ranking` dan membedakan *established / emerging / weak /
> unknown* — jadi yang dibutuhkan satu kalimat: **kenaikan tingkat hanya lewat
> Evidence Engine, tidak pernah oleh model yang memakainya.**
