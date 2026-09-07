# 210 — §14.11–§14.14 Collective Intelligence, Deliberation, Consensus & Negotiation

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.11 — Collective Intelligence Engine

*"Haruskah saya pindah pekerjaan?"* — **jangan hanya menggunakan satu agent**.

```
                Question
      ┌─────────────┼─────────────┐
   Career        Finance      Lifestyle
    Agent         Agent         Agent
      └─────────────┼─────────────┘
              Simulation
              Decision Engine
              Human Decision
```

---

> ⭐ **`Human Decision` sebagai simpul terakhir — bukan `Decision`.** Rantainya
> berakhir pada orangnya, bukan pada mesinnya. Konsisten dengan §9.24
> (*"mari kita bandingkan A, B, dan C"*), §12.11 (dua belas langkah berakhir di
> `Recommendation`), dan §11.63 (*"manusia pemegang kendali"*).

---

## §14.12 — Debate / Deliberation Engine

> Agent **tidak harus selalu setuju**.

```
Career Agent:      "Pindah pekerjaan"
Finance Agent:     "Jangan dulu"
Risk Agent:        "Risiko tinggi"
Simulation Agent:  "Scenario B menghasilkan utility lebih tinggi"
        ↓
Conflict Detection → Evidence Comparison → Constraint Analysis
→ Deliberation → Consensus / Disagreement
```

Keluarannya:

```
Recommendation:     MOVE
Confidence:         0.71
Disagreement:       Finance Agent vs Career Agent
Main uncertainty:   Income stability
```

> Ini jauh lebih kuat daripada sekadar *"AI menyarankan Anda pindah."*

---

> ⭐⭐⭐ **Menampilkan `Disagreement` sebagai bagian dari jawaban adalah salah
> satu keputusan desain terbaik di delapan belas naskah.**
>
> Sistem multi-agent biasanya menyembunyikan perselisihan: ia menjalankan
> beberapa penilai, menggabungkan skornya, dan mengeluarkan satu angka. Yang
> hilang adalah justru informasi paling berguna bagi orang yang harus
> memutuskan — **di mana letak ketidaksepakatannya**.
>
> *"Finance Agent vs Career Agent"* memberi tahu pengguna persis apa yang harus
> ia timbang sendiri. Itu **decision support** dalam arti sebenarnya, dan ia
> memperluas `Main uncertainty` §12.15 dari *"apa yang mungkin membuat ini
> salah"* menjadi *"siapa yang tidak setuju, dan tentang apa"*.

> ⚠️ **`Confidence: 0.71` untuk keputusan pindah kerja adalah angka yang paling
> menuntut ambang** — dan ambangnya baru datang di §14.62 (`escalate_when:
> confidence < 0.6`), yang berlaku untuk **autonomy contract**, bukan untuk
> rekomendasi. Untuk keputusan sebesar ini, 0,71 semestinya memicu bentuk
> **may** §9.15 dan bukan kata `MOVE` dalam huruf besar. Lihat
> [#34](../../issues/34).

---

## §14.13 — Consensus Engine

> Consensus **tidak berarti voting sederhana**. Gunakan: Evidence · Confidence ·
> Expertise · Historical Performance · Risk · User Preferences

```
Career Agent      0.82        Simulation Agent  0.79
Finance Agent     0.74        Risk Agent        0.91
Lifestyle Agent   0.68
```

> Tetapi **Risk Agent mungkin memiliki veto power** untuk kategori tertentu.

---

> ⭐⭐ **Veto untuk Risk Agent adalah penerapan §14.3 (Governance Mesh di luar
> jalur kepentingan) di tingkat keputusan.** Tanpa veto, keamanan hanyalah satu
> suara di antara lima — dan lima agent yang optimis bisa mengalahkan satu
> agent yang benar. Dengan veto, keamanan **bukan peserta**, ia **batas**.
>
> Ini juga sejalan dengan §11.4 (*"Governance layer bukan agent biasa — ia
> harus berada di luar jalur kepentingan agent yang melakukan action"*).

> ⚠️ **"Untuk kategori tertentu" tidak didefinisikan** — dan itu satu-satunya
> hal yang membuat veto bisa ditegakkan. Kategori yang wajar sudah punya nama
> di naskah lain: **R3 ke atas** (§11.15), **aksi tidak reversibel** (§11.27),
> dan **data Level 3–4** (§7.2). Tiga baris, dan veto berhenti jadi kebijakan
> yang bergantung pada penilaian.

> ⚠️ **Lima angka tanpa satuan.** `0.82` untuk Career Agent — itu keyakinan
> agent pada pendapatnya, atau seberapa besar agent itu setuju dengan
> rekomendasi? Dua tafsir menghasilkan konsensus yang berbeda. Dan
> menggabungkan lima angka jadi satu keputusan adalah persis langkah yang
> §14.12 tolak dengan menampilkan `Disagreement`.

---

## §14.14 — Agent Negotiation Engine

```
Travel Agent:  Need $700 budget
Budget Agent:  Maximum $500
Travel Agent:  Can reduce hotel quality
Budget Agent:  Approved
Travel Agent:  New itinerary = $480
```

```
Proposal → Constraints → Counter Proposal → Evaluation → Agreement
```

> Tetapi negotiation engine tetap tunduk pada **Policy · Permission · Risk ·
> Budget · Human Approval**.

---

> ⭐ **Ini negosiasi sungguhan, bukan penyelesaian kendala.** Bandingkan §11.21,
> yang saya catat sebagai *constraint resolution* berpakaian negosiasi: empat
> agent menyumbang batasan, satu langkah menyelesaikannya, tidak ada yang
> mengalah.
>
> Di sini ada **tawar-menawar nyata**: Travel Agent mengubah usulannya
> (*"can reduce hotel quality"*) setelah ditolak. Itu perilaku yang berbeda dan
> lebih kuat — tetapi juga jauh lebih sulit diaudit, karena hasilnya bergantung
> pada urutan dan jumlah putaran.
>
> ⚠️ Dua batas yang belum ada dan keduanya satu baris: **jumlah putaran
> maksimum**, dan **siapa yang mengalah kalau tidak ada kesepakatan**. Tanpa
> yang pertama, dua agent bisa bernegosiasi tanpa henti (yang §11.24 pantau
> sebagai *infinite loop*, tapi hanya setelah terjadi). Tanpa yang kedua,
> kegagalan negosiasi tidak punya jalan keluar selain naik ke manusia — yang
> mungkin memang jawabannya, dan sebaiknya ditulis begitu.

> ⭐ **Perhatikan siapa yang mengalah di contoh: Travel Agent menurunkan
> kualitas hotel, Budget Agent tidak menaikkan pagu.** Itu arah yang benar —
> anggaran adalah batas, bukan posisi tawar. Dan itu konsisten dengan
> `purchases: { amount_limit: 0 }` §11.17 sebagai bawaan yang hanya pengguna
> boleh naikkan.
