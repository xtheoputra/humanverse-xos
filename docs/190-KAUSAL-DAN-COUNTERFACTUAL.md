# 190 — §12.5–§12.7 Causal Intelligence, Causal Graph & Counterfactual Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.5 — Causal Intelligence

> HumanVerse harus membedakan:

```
Observation → Correlation → Hypothesis → Causal Evidence → Causal Conclusion
```

Contoh:

| Tingkat | Isinya |
|---|---|
| Observation | Tidur 5 jam → performa belajar turun |
| Correlation | Ada hubungan antara *sleep duration* dan *study performance* |
| Hypothesis | Kurang tidur **mungkin** menyebabkan performa turun |
| Causal evidence | Eksperimen/pengujian menunjukkan hubungan **konsisten** |
| Conclusion | Ada **bukti yang lebih kuat** bahwa sleep duration berpengaruh |

> **Jangan langsung mengubah korelasi menjadi sebab-akibat.**

---

> ⭐⭐ **Rantai lima langkah ini identik dengan naskah 4 §36 dan naskah 13
> §9.17 — tiga naskah, tanpa bergeser.** Salah satu dari sedikit daftar yang
> tidak pernah berubah di enam belas naskah.
>
> ⭐ Dan bahasanya **melunak di tempat yang tepat**: naskah 13 §9.17 menulis
> *"Repeated controlled experiments"* — istilah yang saya catat lebih kuat dari
> kenyataannya, karena kontrol sejati tidak mungkin pada manusia yang hidup.
> Di sini: *"Eksperimen/pengujian menunjukkan hubungan **konsisten**"* dan
> kesimpulannya *"ada **bukti yang lebih kuat**"* — bukan *"terbukti"*.
> Konsistensi teramati adalah klaim yang bisa ditepati; kontrol tidak.

---

## §12.6 — Causal Graph

```
Sleep → Energy → Focus → Study Quality → Learning Outcome

Workload → Stress → Sleep Quality → Energy → Exercise
```

> Kemudian HumanVerse bisa bertanya: *Jika workload berkurang 20 %, apa yang
> mungkin terjadi?* — **bukan menjawab dengan kepastian, tetapi menjalankan
> simulation**.

---

> ⭐ **Rantai `Sleep → Energy → Focus` cocok dengan urutan naskah 3 dan naskah
> 9 Pillar 7** (`Sleep → Energy → Workout → Mood → Productivity`) — dan butir
> **E-16** mencatat bahwa dua naskah memakai urutan itu melawan satu yang
> memakai urutan lama. **Sekarang tiga lawan satu.** Praktis tertutup;
> [#7](../../issues/7) tinggal konfirmasi.

> ⭐⭐ **Rantai kedua adalah lingkaran, dan itu penting.** `Workload → Stress →
> Sleep Quality → Energy → Exercise` — dan olahraga memengaruhi stres, yang
> memengaruhi tidur. Graf kausal kehidupan **bukan pohon**, ia punya umpan
> balik. Itu yang membuat simulasi (§12.12) diperlukan: rantai berumpan balik
> tidak bisa dihitung sekali jalan, ia harus dijalankan.
>
> ⚠️ Dan itu juga yang perlu dijaga: graf kausal dengan siklus bisa
> **berputar tak berujung** dalam simulasi. Batas iterasi dan kriteria
> konvergensi perlu ada — sama seperti *bounded retry* §11.25 untuk agent.

> 🛑 **Kekuatan panahnya tidak punya sumber — dan `20 %` menuntutnya.**
> Pertanyaan *"jika workload berkurang 20 %, apa yang mungkin terjadi"* hanya
> bisa dijawab kalau sistem tahu **sebesar apa** workload memengaruhi stres,
> dan stres memengaruhi tidur. Panah tanpa angka hanya bisa menjawab arah
> (*"stres kemungkinan turun"*), bukan besaran.
>
> ⭐ Jawabannya ada di naskah ini — §12.20 — dan itu yang menutup **B-24** /
> [#70](../../issues/70): kekuatan panah dipelajari dari **galat prediksinya
> sendiri**. Lihat berkas [`194`](194-VERSIONING-REPLAY-LEARNING-LOOP.md).

---

## §12.7 — Counterfactual Engine

> Memungkinkan pertanyaan: *"Bagaimana kalau saya melakukan X?"*

```
Current:              Counterfactual:
Study    = 1 h/day    Study    = 2 h/day
Exercise = 4×/week    Exercise = 3×/week
Sleep    = 6 hours    Sleep    = 7 hours
```

Engine membuat **Scenario A · B · C**, lalu membandingkan:

```
Goal Progress · Energy · Stress · Time
Risk · Cost · Sustainability · Expected Outcome
```

---

> ⭐⭐⭐ **Delapan dimensi perbandingan menjawab keberatan utama B-24 /
> [#70](../../issues/70) — dan `Sustainability` adalah yang paling berharga.**
>
> Butir itu mencatat tiga jalan keluar untuk counterfactual, dan yang ketiga
> (*"hanya membandingkan skenario secara relatif, tanpa angka absolut"*) saya
> sebut paling jujur dan sudah cukup berguna. Delapan dimensi di atas adalah
> persis itu: **perbandingan antar-skenario**, bukan ramalan hasil.
>
> `Sustainability` khususnya. Sebuah rencana bisa unggul di *Goal Progress* dan
> tetap salah karena tidak bisa dipertahankan — dan itu justru kegagalan paling
> umum dari rencana yang dibuat mesin. Tidak ada satu pun dari enam belas
> naskah sebelumnya yang punya kata untuk itu.

> ⭐ **Contoh counterfactualnya *maju*, bukan mundur.** Saya catat di
> [#70](../../issues/70) bahwa counterfactual tentang **masa lalu** (*"apa yang
> berbeda jika saya tidur 1 jam lebih lama minggu lalu"*) adalah **penyesalan
> yang dihitung** — merugikan meski benar, untuk sistem yang berjanji tidak
> menilai penggunanya.
>
> Contoh di §12.7 seluruhnya tentang perubahan **ke depan**: *study 1 → 2 jam*,
> *sleep 6 → 7 jam*. Itu perencanaan, bukan penyesalan. Bedanya tidak
> dinyatakan, tapi pilihannya benar — dan sebaiknya dijadikan aturan:
> **counterfactual maju ditawarkan sistem; counterfactual mundur hanya dijawab
> bila ditanya, dan tanpa angka.**

> ⚠️ **`Cost` sebagai dimensi perbandingan belum jelas biaya siapa** — biaya
> uang bagi pengguna, atau biaya komputasi bagi sistem (§11.18 `Budget
> Engine`)? Keduanya sah dan keduanya perlu; namanya sebaiknya dibedakan.
