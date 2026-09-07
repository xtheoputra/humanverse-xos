# 163 — §9.32–§9.36 Confidence, Uncertainty Engine, Cognitive Evaluation, Feedback Loop & Self-Evaluation

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.32 — Cognitive Confidence System

> Setiap inference harus memiliki:

```
value · confidence · source · timestamp
```

Misalnya:

```json
{
  "state": "low_energy",
  "confidence": 0.74,
  "sources": [ "sleep", "activity", "self_report" ]
}
```

> Jadi HumanVerse **tidak berpura-pura tahu**.

---

> ⭐⭐ **`sources` adalah field yang menaikkan H-14 satu tingkat.** Confidence
> Layer naskah 5 mewajibkan `confidence` + `evidence_count` — *berapa banyak*
> bukti. `sources` menjawab **bukti dari mana**, dan itu yang membuat dua hal
> mungkin sekaligus:
>
> 1. **Pengguna bisa menilai sendiri.** *"Kesimpulan ini dari data tidur,
>    aktivitas, dan laporan Anda sendiri"* bisa dibantah orangnya; angka
>    `0,74` tidak bisa.
> 2. **Kegagalan senyap jadi terlihat.** Kalau `sources` seharusnya berisi tiga
>    dan hanya berisi satu, itu terbaca — jawaban untuk **B-14** /
>    [#26](../../issues/26). ⚠️ Asalkan satu aturan ditulis: **berkurangnya
>    sumber wajib menurunkan `confidence`.**

> ⭐ `self_report` sebagai sumber yang **disebut terpisah** dari data terukur
> adalah pembedaan yang benar, dan ia menyelesaikan kekaburan `mood` di
> **E-80**: yang dilaporkan pengguna dan yang ditaksir sistem tidak pernah
> tercampur menjadi satu angka tanpa jejak.

---

## §9.33 — Uncertainty Engine

> Jika `confidence < threshold`, AI **tidak boleh terlalu yakin**.

Contoh:

> *"I think your workload may be contributing to lower study consistency, but
> I don't have enough evidence to say that confidently."*

> Ini merupakan karakteristik penting dari AI yang benar-benar matang.

---

> ⭐⭐ **Kalimat itu adalah "kalimat penolakan" yang diminta B-16 sejak naskah
> 4** — dan ia melakukan tiga hal sekaligus yang jarang dilakukan bersamaan:
> menyampaikan dugaannya, menyebut dasarnya, dan **menyatakan bahwa dasarnya
> belum cukup**. Sistem yang diam saja tidak membantu; sistem yang yakin
> menyesatkan. Ini yang ketiga.

> 🛑 **Tapi `threshold` masih belum punya angka — naskah kelima berturut-turut.**
> Butir **H-14** dan [#34](../../issues/34) menanyakan ambang High/Medium/Low
> sejak naskah 5. Yang sudah ada sekarang: mekanismenya di **enam** tempat
> (§9.5, §9.15, §9.19, §9.32, §9.33, dan §8.24), contoh angka **dua** kali
> (`0,72` di §8.24, `0,71`/`0,74` di sini), dan **nol ambang**.
>
> Ini sudah cukup untuk memilih tanpa naskah baru. Usul konkret:
>
> | Pita | Perilaku |
> |---|---|
> | ≥ 0,75 | boleh dinyatakan sebagai kesimpulan (*"tidur Anda memang lebih pendek"*) |
> | 0,50–0,74 | wajib memakai bentuk **may** §9.15 |
> | < 0,50 | **tidak boleh keluar sebagai kesimpulan** — jadi pertanyaan ke pengguna (H-14) |
>
> Angka mana pun boleh, asalkan ditulis. Yang tidak boleh adalah membiarkan
> tiap komponen memilih sendiri, karena `confidence` dipakai lintas enam
> tempat dan pita yang berbeda akan membuat sistem terdengar yakin di satu
> layar dan ragu di layar lain untuk kesimpulan yang sama.

---

## §9.34 — Cognitive Evaluation

> Kita evaluasi bukan hanya LLM. Kita evaluasi **seluruh cognitive pipeline**.

```
Context Accuracy · Memory Relevance · Retrieval Precision
Reasoning Quality · Prediction Calibration · Planning Success
Recommendation Acceptance · Decision Quality · User Satisfaction
Safety · Latency · Cost
```

---

> ⭐⭐⭐ **`Prediction Calibration` menjawab B-10 / [#27](../../issues/27) —
> butir yang menggantung sejak naskah 4.**
>
> B-10 mempersoalkan bahwa delapan metrik evaluasi naskah 4 (Accuracy,
> Relevance, …) tidak pernah menetapkan **"akurat terhadap apa"**, dan bahwa
> *Automatic Rollback* berbahaya kalau skornya sekadar model menilai model.
>
> Kalibrasi tidak butuh kebenaran acuan tentang jawaban yang benar. Ia hanya
> butuh **hasil yang teramati**: dari semua hal yang sistem katakan
> berpeluang 70 %, apakah kira-kira 70 % benar-benar terjadi? Untuk
> `Probability of habit completion tomorrow = 0.68` (§9.18), jawabannya datang
> **besok**, dari `habit_completions` yang sudah ada di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md).
>
> Itu kebenaran acuan yang **dihasilkan sistem sendiri tanpa penilai manusia
> dan tanpa model menilai model** — persis yang dicari B-10. Dan ia bisa
> dijalankan sejak V0, karena habit adalah fitur V0.
>
> ⚠️ Cakupannya terbatas pada yang **bisa diverifikasi**: prediksi, bukan
> pemahaman. `Reasoning Quality` dan `Decision Quality` tetap tanpa acuan.

> ⚠️ **Ini lapisan evaluasi keempat (E-47).** Layer 14 naskah 3 · §23 naskah 5
> · Layer 35 naskah 7 · dan sekarang §9.34. Bedanya: tiga yang pertama
> mengevaluasi **agent/LLM**, yang ini mengevaluasi **pipeline**. Itu alasan
> yang sah untuk berdiri sendiri — tapi empat daftar metrik yang saling
> tumpang tindih tetap perlu satu tempat kanonik. Lihat **E-82**.

> ⚠️ **`Recommendation Acceptance` adalah metrik yang bisa menyesatkan kalau
> dikejar.** Rekomendasi paling mudah diterima adalah yang paling mudah
> dilakukan — dan menaikkan angka ini berarti sistem belajar menyarankan hal
> yang gampang, bukan hal yang berguna. Ia harus dibaca berpasangan dengan
> hasil nyata (§9.35), tidak pernah sendirian. Kerabat dekat
> `Engagement Prediction` (**§9.19**).

---

## §9.35 — Cognitive Feedback Loop

```
Recommendation → User Choice → Real Outcome → Evaluation
→ Preference Update → Behavior Model Update → Future Recommendation
```

Contoh — AI menyarankan *"Study AI 45 menit malam ini"*, user **tidak
melakukan**. Jangan langsung menyimpulkan:

```
"User malas."
```

Sistem mencari:

```
Why? Time? Energy? Difficulty? Context? Environment? Goal conflict?
```

Kemudian model diperbaiki.

---

> ⭐⭐ **"Jangan langsung menyimpulkan 'User malas'" adalah prinsip
> anti-karakterisasi yang sama dengan §9.4, diterapkan pada kegagalan.** Dan
> ia menyentuh titik terlemah dari seluruh loop belajar: **ketiadaan aksi
> adalah sinyal yang paling ambigu**. Tidak mengerjakan sesuatu bisa berarti
> tujuh hal, dan enam di antaranya bukan tentang orangnya.
>
> Ini juga pengaman terhadap kesalahan yang paling merusak di sistem seperti
> ini: model yang menyimpulkan sifat dari kegagalan akan menurunkan
> ekspektasinya, memberi saran yang lebih mudah, lalu menemukan bukti bahwa
> orang itu memang hanya sanggup yang mudah. **C-13** menyebut pola ini
> "menguatkan dirinya sendiri".
>
> ⚠️ Yang belum ada: **dari mana jawaban "Why?" datang.** Enam kemungkinan itu
> tidak bisa dibedakan dari data yang ada — satu-satunya yang tahu adalah
> penggunanya. Artinya loop ini menuntut **bertanya**, dan bertanya terlalu
> sering adalah cara tercepat membuat orang berhenti memakai aplikasi.
> `Real Outcome` juga tidak punya sumber untuk sebagian besar rekomendasi:
> sistem tahu habit selesai atau tidak, tapi tidak tahu apakah 45 menit belajar
> itu **berguna**.

---

## §9.36 — Self-Evaluation Layer

> Sebelum memberikan rekomendasi penting:

```
Candidate Answer
      ↓
Evidence Check
      ↓
Context Check
      ↓
Consistency Check
      ↓
Safety Check
      ↓
Confidence Check
      ↓
Final Answer
```

> AI dapat menyadari *"Saya tidak memiliki cukup data"* dan meminta informasi
> tambahan.

---

> ⭐ **`Consistency Check` belum pernah ada, dan ia yang paling dibutuhkan
> arsitektur ini.** Dengan sepuluh field state, enam jenis memory, graf, world
> model, dan prediksi berjalan bersamaan, **jawaban bisa bertentangan dengan
> dirinya sendiri**: menyarankan latihan berat sambil melaporkan
> `physical_readiness` rendah. Tidak ada komponen lain yang memeriksa itu.

> ⚠️ **Ini rantai keluaran kedua, dan keduanya berakhir di "Final".**
>
> | | §8.22 naskah 12 | §9.36 naskah 13 |
> |---|---|---|
> | Menjaga | **kebocoran** — PII, lokasi, finansial | **kebenaran** — bukti, konsistensi, keyakinan |
> | Rantai | Safety → Privacy → Policy → PII | Evidence → Context → Consistency → Safety → Confidence |
> | Berakhir | `Final Response` | `Final Answer` |
>
> Keduanya perlu dan tidak saling menggantikan — tapi belum ada aturan
> komposisi. Urutan yang masuk akal: **§9.36 dulu** (apakah jawaban ini benar
> dan cukup didukung), **§8.22 sesudahnya** (apakah aman dikirim). Memeriksa
> kebocoran pada jawaban yang akhirnya dibatalkan adalah pekerjaan sia-sia;
> sebaliknya tidak. Lihat **E-83**.

> ⚠️ **"Rekomendasi penting" tidak didefinisikan.** Kalau rantai tujuh langkah
> ini hanya berjalan untuk sebagian jawaban, yang menentukan sebagian itu
> adalah `Intent Classifier` (§9.21) — dan seperti dicatat di sana, salah
> memilih berarti melewati pemeriksaan sepenuhnya. Aturan bawaannya harus:
> **ragu ⇒ jalankan rantainya**, bukan sebaliknya.
