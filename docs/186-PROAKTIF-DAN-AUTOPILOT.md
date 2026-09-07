# 186 — §11.42–§11.47 Proactive Intelligence, Notification, Initiative, Goal Autopilot & Loop

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.42 — Proactive Intelligence

> Bukan hanya *"User bertanya → AI menjawab"*, tetapi:

```
Observe → Detect Relevant Situation → Evaluate Importance
→ Decide Whether To Interrupt → Recommend / Act
```

Contoh:

```
Calendar:  Meeting 09:00
Location:  Current position far away
Traffic:   High
Time:      08:15
```

> *"Jika Anda berangkat dalam 10 menit, estimasi perjalanan saat ini membuat
> waktu kedatangan cukup ketat."*

---

> ⭐⭐ **`Decide Whether To Interrupt` sebagai langkah tersendiri — sebelum
> `Recommend / Act` — adalah keputusan desain yang jarang dibuat.** Sebagian
> besar sistem proaktif menghitung *apa yang berguna* lalu mengirimkannya.
> Di sini ada satu langkah yang khusus memutuskan **apakah mengganggu itu
> layak**, dan itu yang membedakan asisten dari pemberitahuan.
>
> ⭐ Kalimat contohnya juga tepat: *"membuat waktu kedatangan cukup ketat"* —
> tidak menyuruh, tidak memastikan, tidak menghitung terlambat berapa menit.
> Bentuk **may** §9.15, dipegang di naskah keempat berturut-turut.

> 🛑 **Ini pembalikan arah paling besar dari lima belas naskah, dan ia menuntut
> tiga hal yang belum ada.**
>
> Sampai sekarang HumanVerse **menjawab**. Contoh di atas berarti sistem
> **memulai** — dan untuk sampai ke sana ia harus, pada jam 08:15 tanpa
> diminta, mengetahui kalender, **lokasi terkini**, dan lalu lintas.
>
> | Yang dibutuhkan | Keadaannya |
> |---|---|
> | pemantauan lokasi berjalan terus | ❌ izin lokasi tidak pernah didaftarkan (§10.27 hanya kamera & mikrofon — **E-93**) |
> | infrastruktur push notification | ❌ tidak ada; menuntut aplikasi di perangkat, yang belum ada |
> | sistem yang berjalan tanpa permintaan | 🆕 §11.41, komponen pertama yang begitu |
>
> Ini juga **C-17 dari sisi lain**: butir itu tentang kamera yang menyala terus;
> ini tentang **lokasi** yang dipantau terus. Bedanya, yang ini tidak butuh
> kamera sama sekali. Lihat **A-28** / [#80](../../issues/80).

---

## §11.43 — Notification Intelligence

> AI tidak boleh mengganggu terus-menerus. Bangun **Interruption Manager**.

Menghitung: **Importance · Urgency · Confidence · Current Activity · User
Preference · Notification Fatigue** → *Notify now · Notify later · Silent · Ask
permission*

---

> ⭐⭐ **`Notification Fatigue` sebagai masukan yang dihitung** — bukan sebagai
> keluhan pengguna belakangan. Digabung dengan anggaran `notification: send:
> 10/day` §11.17, perhatian pengguna diperlakukan sebagai **sumber daya
> terbatas dengan pagu**, sama seperti uang dan token.
>
> ⭐ Dan `Current Activity` berarti Interruption Manager membaca Human State
> §9.5 — kalau `focus` tinggi, jangan mengganggu. Itu pemakaian kedua dari
> HumanState untuk mengubah keputusan (yang pertama §11.8).

> ⚠️ **`Confidence` sebagai masukan menuntut ambang, dan ini tempat paling
> mendesak untuk itu.** Memberi tahu seseorang berdasarkan dugaan 0,4 lebih
> merugikan daripada diam — karena kesalahan proaktif tidak bisa ditarik, dan
> ia menghabiskan kepercayaan lebih cepat daripada apa pun.
> [#34](../../issues/34) sekarang punya alasan produk, bukan hanya alasan
> arsitektur.

---

## §11.44 — Agent Initiative Score

Berdasarkan: **Potential Benefit · Urgency · Confidence · Risk · User
Preference · Interruption Cost**

```
Benefit tinggi + Urgency tinggi + Confidence tinggi + Risk rendah → Notify now
Benefit rendah + Urgency rendah + Interruption cost tinggi        → Do nothing
```

> ## Do Nothing adalah kemampuan penting bagi agent.

---

> ⭐⭐⭐ **Kalimat itu layak dicetak dan ditempel.** Sistem yang dinilai dari
> seberapa banyak ia melakukan sesuatu akan selalu melakukan terlalu banyak;
> menjadikan *tidak melakukan apa-apa* sebagai **kemampuan**, bukan kegagalan,
> mengubah arah seluruh optimasi.
>
> Ia juga penangkal langsung untuk `Engagement Prediction` (§9.19,
> [#71](../../issues/71)) — satu-satunya metrik yang melayani produk, bukan
> pengguna. Dua gagasan itu tarik-menarik, dan naskah ini memihak yang benar.

> ⚠️ **`Initiative Score` adalah angka tanpa rumus yang ke sekian.** Yang
> berjalan sekarang: `probability` · `confidence` · `uncertainty` · `quality`
> (§10.24) · Trust Score · Security grade · `Correction Rate` · dan ini.
> Butir **B-15** tentang angka pengguna; polanya kini merambat ke angka sistem.
>
> ⭐ Bedanya: yang ini punya arah yang jelas (`Interruption Cost` mengurangi,
> `Urgency` menambah), dan **kesalahannya murah** — salah diam lebih baik
> daripada salah mengganggu. Untuk V0 satu aturan sederhana sudah cukup:
> *jangan pernah menyela dua kali dalam sejam, dan jangan sama sekali di bawah
> confidence 0,7.*

---

## §11.45 — Goal Autopilot

*"Saya ingin meningkatkan kemampuan AI."*

```
Goal → Assess Current Skill → Identify Gap → Create Learning Roadmap
→ Create Projects → Schedule Sessions → Monitor Progress → Adapt Plan
→ Evaluate
```

> Human tetap memegang kontrol.

---

> ⚠️ **`Assess Current Skill` adalah penilaian tentang seseorang, dan ia
> kerabat dekat C-16.** Butir itu mempersoalkan Personal Utility Model yang
> menyimpulkan *apa yang seseorang hargai*; ini menyimpulkan **seberapa mampu
> seseorang**.
>
> Bedanya: kemampuan bisa diuji, nilai hidup tidak. Jadi ini lebih bisa
> dibantah — asalkan pengguna **melihat** penilaiannya dan bisa mengubahnya.
> Preseden `[Edit]` §11.28 dan `editable` §11.10 sudah ada di naskah yang sama;
> tinggal diberlakukan di sini. Bertaut [#71](../../issues/71) dan
> [#64](../../issues/64).

---

## §11.46–§11.47 — Life Operating Loop & Agentic Feedback Loop

```
GOAL → PLAN → EXECUTE → OBSERVE → MEASURE → REFLECT → ADAPT → REPLAN
```

```
PERCEIVE → UNDERSTAND → REASON → PLAN → POLICY → ACT → VERIFY
→ OBSERVE → EVALUATE → LEARN → UPDATE PLAN
```

---

> ⭐⭐ **`POLICY` berdiri di dalam loop utama, di antara PLAN dan ACT.** Itu
> yang membedakan loop ini dari loop kognitif §9.1 dan loop multimodal §10.33 —
> keselamatan bukan lapisan di sekeliling, melainkan **satu langkah yang harus
> dilewati setiap putaran**. Sejalan dengan `POLICY_CHECK` §9.29 yang menutup
> **E-45** ([#42](../../issues/42)).

> ⭐ **`MEASURE` dan `REFLECT` sebagai dua langkah berbeda** di §11.46 — yang
> satu mengumpulkan angka, yang lain menafsirkannya. Sebagian besar sistem
> menggabungkan keduanya dan menghasilkan tafsir yang tidak bisa diperiksa.

> ⚠️ **Loop ketiga dalam tiga naskah, dan ketiganya berbeda panjang** (§9.1
> tiga belas langkah · §10.33 empat belas · §11.46 delapan · §11.47 sebelas).
> Semuanya menggambarkan hal yang sama dengan potongan berbeda — pola **E-47**
> (lapisan evaluasi) di sumbu loop. Satu tempat kanonik akan menolong; kandidat
> terbaik adalah **§11.47**, karena ia satu-satunya yang memuat `POLICY` dan
> `VERIFY` sekaligus.
