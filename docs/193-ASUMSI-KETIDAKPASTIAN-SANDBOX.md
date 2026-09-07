# 193 — §12.14–§12.16 Assumption Engine, Uncertainty Engine & Simulation Sandbox

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.14 — Assumption Engine

> Ini **wajib**. Setiap simulasi harus menyimpan:

```yaml
assumptions:
  - sleep remains stable
  - workload remains similar
  - user maintains 80% consistency
  - no major external disruption
```

> ## Simulation without assumptions is misleading.

---

> ⭐⭐⭐ **Ini bagian terpenting di seluruh naskah, dan ia menutup separuh
> B-24 / [#70](../../issues/70).**
>
> Butir itu mencatat: *Counterfactual Engine menjanjikan jawaban yang causal
> reasoning di naskah yang sama melarang* — karena model transisi tidak punya
> sumber, dan menjawab *"apa yang berbeda jika saya tidur 1 jam lebih lama"*
> menuntut tahu **sebesar apa** tidur memengaruhi fokus.
>
> Assumption Engine tidak menghapus tuntutan itu. Ia melakukan sesuatu yang
> lebih berguna: **membuat yang dipinjam menjadi terlihat.** Sebuah simulasi
> yang bersandar pada *"beban kerja tetap"* dan mengatakannya bukan lagi klaim
> tentang masa depan — ia klaim bersyarat, dan syaratnya bisa dibantah
> penggunanya.
>
> Kalimat *"simulation without assumptions is misleading"* juga menetapkan
> bahwa ini **bukan fitur tambahan**: simulasi tanpa asumsi tersimpan tidak
> boleh ditampilkan sama sekali.

> ⭐ **Keempat contoh asumsinya jujur tentang hal yang berbeda-beda:** dua
> tentang dunia (*workload*, *external disruption*), satu tentang tubuh
> (*sleep*), dan satu tentang **penggunanya sendiri** (*maintains 80 %
> consistency*). Yang terakhir paling sering dilanggar dan paling jarang
> disebut — dan menyebutnya di depan lebih baik daripada menyalahkan
> penggunanya di belakang (§9.35: *"jangan langsung menyimpulkan User malas"*).

> ⚠️ **Asumsi ditulis sebagai kalimat bebas.** Untuk bisa **diperiksa**
> belakangan — apakah *"workload remains similar"* memang terjadi — ia perlu
> bentuk yang bisa dievaluasi mesin, bukan hanya dibaca manusia. §12.19
> *Decision Replay* menuntut persis itu: untuk tahu kenapa proyeksi meleset,
> sistem harus bisa memeriksa **asumsi mana yang tidak berlaku**.
>
> Bentuk yang cukup: `{ attribute: "workload", expected: "stable",
> tolerance: 0.2 }` — tiga field, dan `simulation_assumptions` §12.28 sudah
> punya tabelnya.

---

## §12.15 — Uncertainty Engine

```
Expected:           72
Probability:        0.67
Confidence:         0.71
Uncertainty:        Medium
Main uncertainty:   Workload variability
```

---

> ⭐⭐ **`Main uncertainty` adalah field yang paling berguna dan belum pernah
> ada di enam belas naskah.** Ia menjawab pertanyaan yang tidak bisa dijawab
> oleh angka mana pun: **apa yang paling mungkin membuat ini salah.**
>
> Untuk pengguna, itu jauh lebih berguna daripada `Uncertainty: Medium` —
> karena ia bisa ditindaklanjuti. *"Ketidakpastian utama: variabilitas beban
> kerja"* memberi tahu apa yang harus diperhatikan, dan apa yang harus
> dikabarkan ke sistem kalau berubah.

> ⭐ **`probability` dan `confidence` tetap terpisah** — sesuai §9.19, dan
> pembedaannya masih benar: *"kemungkinan 67 %, keyakinan 71 %"* berbeda dari
> *"kemungkinan 67 %, keyakinan 20 %"*. Yang kedua yang harus memicu **tanya
> pengguna** (**H-14**).

> 🛑 **`Uncertainty: Medium` adalah pita — dan ambangnya tetap tidak ada.**
> Ini naskah **ketujuh** yang mewajibkan mekanisme keyakinan tanpa memberi
> ambangnya ([#34](../../issues/34)): §8.24 `0.72` · §9.15 `0.71` · §9.33
> *"if confidence < threshold"* · §10.24 `0.97` vs `0.38` · §11.29 `0.89` ·
> §12.1 `0.84` · dan sekarang `Medium`.
>
> ⭐ Tapi *"Medium"* justru menunjukkan bahwa **pita itu memang dibutuhkan** —
> seseorang di naskah ini sudah menerjemahkan angka menjadi kata, hanya belum
> menuliskan batasnya. Usul saya di #34 tetap: **≥0,75 dinyatakan · 0,50–0,74
> bentuk *may* · <0,50 jadi pertanyaan** — dan untuk proyeksi, satu baris
> tambahan: **ketidakpastian tinggi ⇒ tampilkan rentang saja, tanpa nilai
> tengah.**

---

## §12.16 — Simulation Sandbox

```
REAL WORLD → DIGITAL TWIN SNAPSHOT → SIMULATION SANDBOX
                                     ├── Scenario A
                                     ├── Scenario B
                                     └── Scenario C
                                          ↓
                                      COMPARE → DECISION
```

> **Simulation tidak boleh mengubah data dunia nyata.**

---

> ⭐⭐⭐ **Satu kalimat, dan ia batas arsitektur yang paling mudah dilanggar
> tanpa disadari.**
>
> Simulasi yang berjalan di atas twin hidup akan **menulis balik** tanpa ada
> yang bermaksud begitu: memperbarui `confidence`, menambah memori, memicu
> event. Snapshot memutusnya — simulasi berjalan di atas salinan, dan salinan
> tidak punya jalan pulang.
>
> Ini sejajar dengan dua batas keras lain yang sudah ada: *"agent tidak boleh
> bypass gateway"* (§11.14) dan *"tidak ada modul agent yang boleh mengimpor
> `security/`"* (§8.42). Ketiganya perlu ditegakkan **CI**, bukan diniatkan —
> [`../spec/06`](../spec/06-MODULE-BOUNDARIES.md) sudah punya mekanismenya.

> ⚠️ **"Sandbox" kini EMPAT makna** (perluasan **E-72** dan catatan §11.34):
>
> | Sumber | Artinya |
> |---|---|
> | DP-L14 naskah 10 | sandbox **pengujian** — data palsu, saat developer membangun |
> | §8.29 naskah 12 | sandbox **runtime** — tool/jaringan/memori dibatasi di produksi |
> | §11.34 naskah 15 | **gerbang sertifikasi** — tahap sebelum produksi |
> | **§12.16 naskah 16** | **sandbox simulasi** — snapshot, tidak menulis ke dunia nyata |
>
> Keempatnya perlu dan berbeda. Nama yang membedakan: **sandbox-uji ·
> sandbox-jalan · jalur sertifikasi · sandbox-simulasi**. Lihat **E-105**.

> ⚠️ **Snapshot berarti salinan seluruh Digital Twin per simulasi**, dan §12.1
> memberinya 18 komponen. Kalau tiap pertanyaan menghasilkan satu snapshot,
> `twin_snapshots` (§12.28) akan tumbuh secepat pemakaian — dan §12.9 pohon
> skenario mengalikannya lagi. Retensi snapshot perlu ditetapkan sejak awal
> (§7.26: *raw pendek, agregat panjang*), dan ia masuk hitungan **C-9**:
> snapshot adalah salinan lengkap data pribadi.
