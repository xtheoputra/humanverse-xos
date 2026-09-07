# 158 — §9.15–§9.17 Understanding Engine, Temporal Understanding & Causal Reasoning

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.15 — Layer 7: Understanding Engine

> Bagian yang mengubah **raw data menjadi meaning**.

```
Input:   Events · Memory · Context · Knowledge · Behavior · State
Output:  Situation Understanding
```

Contoh:

```
Observed:
Sleep ↓   Workout ↑   Study ↓   Stress ↑

Understanding:
User may be experiencing
high cognitive/physical load.

Confidence:
0.71
```

Perhatikan kata **may**, bukan *"User definitely stressed"*.

---

> ⭐⭐ **Satu kata `may` melakukan pekerjaan yang tidak dilakukan seluruh
> Confidence Layer.** Butir **B-15** mencatat masalahnya: `"energy": 0.62`
> tetap dibaca sebagai fakta meskipun ia taksiran, karena **angkanya presisi**.
> Menambahkan `confidence: 0.71` di sebelahnya tidak menolong — pembaca melihat
> dua angka, bukan satu keraguan.
>
> Yang menolong adalah **bahasanya**. *"User may be experiencing"* memindahkan
> ketidakpastian dari angka ke kalimat, di tempat yang benar-benar dibaca
> orang. Itu perbaikan nyata atas H-14, dan sebaiknya jadi aturan tertulis:
> **setiap kesimpulan turunan disajikan sebagai kemungkinan, bukan keadaan.**

> ⚠️ **Understanding Engine adalah komponen paling mudah salah dan paling
> sulit diuji.** *"High cognitive/physical load"* dari empat panah adalah
> lompatan tafsir; empat panah yang sama juga cocok dengan *"sedang mengejar
> tenggat"*, *"sedang sakit"*, atau *"pekan ujian"*. §9.34 memberi metrik
> `Reasoning Quality`, tapi tidak ada kebenaran acuan untuk menilainya —
> masalah **B-10** yang sama.

---

## §9.16 — Temporal Understanding

> HumanVerse harus memahami **waktu**. Bukan hanya:

```
Sleep = 6 hours
```

tetapi:

```
Sleep ↓ for 5 consecutive days
```

dan:

```
Study ↓ after workload ↑
```

**Temporal Pattern Engine** mendeteksi:

```
trend · seasonality · cycles · change points · recurring patterns
```

---

> ⭐⭐ **`change points` adalah butir yang paling berguna dan belum pernah
> disebut.** Titik perubahan menjawab pertanyaan yang tidak bisa dijawab
> rata-rata: *"kapan sesuatu mulai berbeda"*. Ia juga yang membuat **decay
> §9.9 bisa dijalankan dengan benar** — preferensi tidak luruh perlahan
> seragam, ia sering berubah pada satu titik (pindah kerja, punya anak, pindah
> kota). Mendeteksi titik itu lebih tepat daripada peluruhan eksponensial.

> ⚠️ **`Study ↓ after workload ↑` adalah urutan, bukan sebab — dan bagian
> berikutnya justru memperingatkannya.** Menempatkan contoh ini di bawah
> "temporal understanding" benar; yang perlu dijaga adalah ia **tidak boleh
> menyeberang** menjadi sisi `influences` di graf (**E-81**) tanpa melewati
> rantai §9.17.

> ⚠️ **Deteksi pola musiman butuh riwayat setahun.** `seasonality` dan
> `cycles` tidak bisa dihitung dari data satu bulan. Untuk V0, yang bisa
> dijalankan hanya `trend` dan `recurring patterns` mingguan. Bertaut **B-1**
> (cold start) dan **B-21** / [#48](../../issues/48).

---

## §9.17 — Causal Reasoning

> Jangan langsung:

```
X happened, then Y happened
Therefore: X caused Y
```

HumanVerse harus membedakan:

```
Observation → Correlation → Hypothesis → Causal evidence → Conclusion
```

Contoh:

```
Observation:  Sleep decreased.
Observation:  Focus decreased.
Hypothesis:   Sleep may influence focus.
Evidence:     Repeated controlled experiments.
Confidence:   Moderate.
```

> Ini membuat HumanVerse lebih **ilmiah**.

---

> ⭐ **Rantai lima langkah ini konsisten dengan naskah 4 §36** (Observation →
> Correlation → Hypothesis → Evidence → Conclusion) — sama persis, dua naskah
> terpisah delapan naskah. Salah satu dari sedikit daftar yang **tidak
> berubah**.

> 🛑 **Tetapi ambangnya masih belum ada — naskah kelima berturut-turut.**
> Butir **A-21** / **B-16** / **C-8** ([#23](../../issues/23)) menanyakan hal
> yang sama sejak naskah 4: berapa hari minimum, dan **kapan sistem menolak
> menyimpulkan**. Yang ada di sini:
>
> | Ditulis | Belum ditulis |
> |---|---|
> | *"Repeated controlled experiments"* | berapa kali "repeated" |
> | `Confidence: Moderate` | Moderate itu berapa |
> | rantai lima langkah | apa yang terjadi kalau berhenti di langkah 2 |
>
> Yang terakhir paling penting dan paling mudah ditulis: **korelasi yang tidak
> pernah naik ke hipotesis teruji tidak boleh keluar sebagai kalimat sebab
> apa pun**, termasuk yang berbunyi lunak. §9.33 memberi bentuk kalimatnya.

> ⚠️ **"Repeated controlled experiments" pada satu orang adalah klaim besar.**
> Kontrol yang benar menuntut mengubah satu hal sambil menahan yang lain —
> tidak mungkin pada manusia yang hidup: cuaca, beban kerja, dan musim berjalan
> terus (**B-16**). Yang bisa dijalankan sebenarnya *repeated observation under
> varied conditions*, bukan *controlled experiment*. Bedanya penting justru
> karena kalimat ini yang membuat sistem *"lebih ilmiah"* — dan istilah yang
> lebih kuat dari kenyataannya membuatnya kurang ilmiah, bukan lebih.
>
> Batas yang sudah ditetapkan **C-8** tetap berlaku: sistem tidak boleh
> menyarankan eksperimen yang menyangkut obat, puasa ekstrem, atau pembatasan
> tidur — dan justru contoh di bagian ini adalah **tidur**.
