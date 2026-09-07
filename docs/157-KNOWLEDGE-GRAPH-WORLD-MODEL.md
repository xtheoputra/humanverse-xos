# 157 — §9.10–§9.14 Knowledge System, Human Knowledge Graph, World Model & Counterfactual

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.10 — Layer 5: Knowledge System

**Personal Knowledge**

```
User
 ├── goals
 ├── habits
 ├── preferences
 ├── relationships
 └── experiences
```

**General Knowledge**

```
Science · Technology · Fashion · Fitness · Career · Finance · Travel · Culture
```

**Situational Knowledge**

```
weather · events · prices · availability · trends
```

> Ketiganya harus dapat **digabungkan**.

---

> ⭐⭐ **Pembagian tiga ini menutup sebagian besar E-49 / [#41](../../issues/41).**
> Layer 40 naskah 7 memisahkan *Memory = pengalaman pengguna* dari
> *Knowledge = pengetahuan dunia*, tetapi konsekuensinya tidak pernah ditulis.
> Di sini ketiganya punya nama, dan konsekuensinya menjadi jelas:
>
> | | Terhapus saat akun dihapus? | Butuh izin per pengguna? | Koleksi Qdrant |
> |---|---|---|---|
> | **Personal** | ✅ ya | ✅ ya | per pengguna |
> | **General** | ❌ tidak | ❌ tidak | bersama |
> | **Situational** | ❌ tidak (tapi kedaluwarsa) | ❌ tidak | bersama, ber-TTL |
>
> Tiga kolom itu belum pernah ditulis di dua belas naskah, tetapi ketiganya
> **mengikuti langsung** dari pembagian ini. *Situational* adalah kategori
> ketiga yang belum pernah ada dan ia memang berbeda: ia bukan milik pengguna,
> tetapi juga tidak abadi seperti pengetahuan umum.
>
> ⚠️ Yang tetap harus dijaga: ketiganya **tidak boleh tercampur di koleksi
> vektor yang sama**, karena hanya yang pertama yang ikut terhapus (**C-9**).

---

## §9.11 — Human Knowledge Graph

> Sekarang graph menjadi bagian dari **reasoning**.

```
User
 │
 ├── has_goal → Career Growth
 │                    │
 │                    └── requires → AI Skill
 │
 ├── habit → Study AI
 │                 │
 │                 └── improves → AI Skill
 │
 └── sleep pattern
          │
          └── influences → Study consistency
```

> AI dapat melihat **hubungan antar-domain**, bukan hanya data per tabel.

---

> ⭐ **Rantai `Goal → requires → Skill ← improves ← Habit` adalah contoh
> pertama yang menunjukkan kenapa graf dibutuhkan sama sekali.** Ia menjawab
> pertanyaan yang tidak bisa dijawab tabel mana pun: *"kebiasaan mana yang
> benar-benar menggerakkan tujuan saya"* — jalurnya melewati dua relasi dan dua
> domain. Selama dua belas naskah, graf selalu digambarkan tapi tidak pernah
> ditunjukkan gunanya.

> 🛑 **`influences` kembali — padahal naskah 9 sudah membuangnya, dan itu
> dicatat sebagai kabar baik.** Butir **E-55**: Pillar 3 naskah 9 memakai
> `improves`, `supports`, `blocks`, `related_to`, `frequently_used` dan
> **membuang `causes`, `influences`, `predicts`** — sejalan dengan naskah 4 §7
> yang melarang menulis relasi kausal untuk data observasional.
>
> `sleep pattern → influences → Study consistency` adalah klaim kausal yang
> ditulis sebagai **sisi graf permanen**. Dan §9.17 di naskah yang sama
> menuntut Observation → Correlation → Hypothesis → **Causal evidence** →
> Conclusion sebelum boleh menyimpulkan sebab.
>
> Keduanya hanya bisa hidup bersama dengan satu syarat yang belum ditulis:
>
> > Sisi kausal wajib membawa `evidence` dan `confidence`, dan hanya lahir dari
> > rantai §9.17 — tidak pernah dari pengamatan berurutan.
>
> Tanpa itu, graf akan memuat sebab-akibat yang tidak pernah diuji, dan setiap
> reasoning di atasnya mewarisi kesalahan itu. Ini juga daftar node/relasi
> **kelima** (**E-17**, **E-18**, **E-55**). Lihat **E-81**.

> ⚠️ **Neo4j ada di V4** (§7.0 naskah 11). Untuk V0, rantai `Goal → Skill ←
> Habit` masih bisa dijalankan dengan `goals.parent_id` dan tabel penghubung —
> itu yang sudah dicatat saat menutup [#7](../../issues/7). Graf penuh tidak
> menghalangi V0; contoh di atas menunggu V4.

---

## §9.12 — Layer 6: World Model

> HumanVerse tidak hanya memahami *"Apa yang terjadi?"* tetapi juga:
>
> ## "Apa yang mungkin terjadi jika kondisi berubah?"

```
Current:      Study 1 hour/day
Scenario A:   Study 2 hours/day
Scenario B:   Study 3 hours/day
Scenario C:   Study 1 hour + project
```

World Model membuat simulasi:

```
State → Action → Transition → Future State
```

---

## §9.13 — Personal World Model

Merepresentasikan:

```
Goals · Resources · Constraints · Habits · Skills · Preferences
Environment · Behavior patterns
```

Kemudian:

```
Current State → Possible Action → Simulation → Potential Outcomes
```

> Tetapi hasil harus disebut **scenario projection**, bukan *"prediksi masa
> depan pasti"*.

---

> ⭐ **Disiplin bahasa ini dipegang di naskah keenam berturut-turut.**
> *"scenario simulation, bukan ramalan"* (naskah 4 §26), *"decision support,
> bukan pengambil keputusan"* (§27), dan sekarang *scenario projection*. Ini
> salah satu dari sedikit hal yang tidak pernah goyah.

---

## §9.14 — Counterfactual Engine

> *"Apa yang mungkin berbeda jika saya tidur 1 jam lebih lama?"*
> *"Bagaimana jika saya belajar AI 5 jam per minggu selama 6 bulan?"*

```
Observed Reality
       │
       ▼
Counterfactual Generator
       │
       ├── Scenario A
       ├── Scenario B
       └── Scenario C
              │
              ▼
          Simulator
              │
              ▼
       Outcome Comparison
```

---

> 🛑 **Counterfactual Engine menjanjikan jawaban yang §9.17 melarang
> memberikannya.**
>
> Pertanyaan *"apa yang berbeda jika saya tidur 1 jam lebih lama"* adalah
> pertanyaan **kausal murni** — ia menanyakan akibat dari sebuah intervensi
> yang tidak terjadi. Menjawabnya menuntut model transisi yang tahu bahwa tidur
> **menyebabkan** perubahan fokus, dan sebesar apa.
>
> Tetapi §9.17 di naskah yang sama menetapkan bahwa sebab hanya boleh
> disimpulkan setelah *"repeated controlled experiments"*, dan **B-16**/**C-8**
> sudah mencatat bahwa eksperimen n-of-1 14 hari tanpa kelompok kontrol mudah
> salah simpul. Sumber data untuk `Transition` **tidak ada**, dan naskah tidak
> menyebutkan dari mana ia datang.
>
> Ada tiga jalan keluar, dan yang mana dipilih harus ditulis:
>
> | Jalan | Konsekuensi |
> |---|---|
> | Transisi dari **eksperimen pengguna sendiri** (Experiment Engine) | paling benar, paling lambat — butuh berbulan-bulan per hubungan |
> | Transisi dari **pengetahuan umum** (*tidur memengaruhi fokus*) | cepat, tapi itu rata-rata populasi yang dijual sebagai jawaban personal |
> | Hanya **membandingkan skenario secara relatif**, tanpa angka absolut | paling jujur, dan cukup untuk sebagian besar pertanyaan |
>
> Yang ketiga layak dipertimbangkan lebih dulu: *"Skenario B menuntut 3× waktu
> Skenario A"* tidak butuh model kausal sama sekali, dan sudah berguna.
> Lihat **B-24** / [#70](../../issues/70).

> ⚠️ **Counterfactual tentang masa lalu punya beban yang berbeda dari skenario
> masa depan.** *"Bagaimana jika saya belajar 5 jam/minggu"* adalah rencana.
> *"Apa yang berbeda jika saya tidur 1 jam lebih lama"* — ditanyakan tentang
> minggu yang sudah lewat — adalah **penyesalan yang dihitung**. Untuk sistem
> yang berjanji tidak menilai penggunanya (naskah 4, prinsip penutup), jawaban
> seperti *"Anda akan menyelesaikan 40 % lebih banyak"* adalah kalimat yang
> merugikan meski benar. Bertaut **C-8** / [#23](../../issues/23).
