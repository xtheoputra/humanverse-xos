# 171 — §10.21–§10.23 Human State Multimodal, Perception → Behavior & Multimodal Memory

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.21 — Human State dari Multimodal Data

```
Wearable + Activity + Calendar + Voice + Interaction + Environment
        ↓
Human State

Energy       0.62  ± confidence 0.78
Focus        0.71  ± confidence 0.65
Stress       0.41  ± confidence 0.51
SocialEnergy 0.35  ± confidence 0.57
```

> Jangan menganggap ini sebagai fakta absolut. Lebih tepat: **Estimated
> State**.

---

> ⭐⭐ **Ini bentuk `{value, confidence}` §9.5 yang dipertahankan utuh satu
> naskah kemudian** — dan itu jarang terjadi di repo ini, di mana daftar
> berubah hampir setiap naskah. Empat field yang muncul adalah bagian dari
> sepuluh field §9.5, bukan daftar baru; ini contoh, bukan revisi.
>
> Istilah **`Estimated State`** juga tambahan yang berguna: ia memberi nama
> pada apa yang selama ini hanya berupa peringatan di catatan audit
> (**B-15**). Nama yang benar lebih mengikat daripada catatan kaki.

> ⭐ **Enam sumber di kiri semuanya sekarang punya jalur.** `Voice` dan
> `Interaction` adalah yang baru — dan `Interaction` menarik karena ia bukan
> sensor: ia perilaku pengguna **terhadap aplikasinya sendiri**. Itu sumber
> yang selalu tersedia, tidak butuh izin perangkat, dan sudah ada di V0
> (`ai_conversations`, `recommendation_feedback`).
>
> ⚠️ Tapi ia juga kerabat dekat `Engagement Prediction` (**§9.19**,
> [#71](../../issues/71)): menyimpulkan keadaan seseorang dari seberapa sering
> ia membuka aplikasi adalah langkah pendek menuju mengoptimalkan seberapa
> sering ia membukanya.

> ⚠️ **`Stress 0.41` adalah taksiran tentang kesehatan mental.** Batas **C-2**
> (AI tidak boleh berpura-pura jadi dokter) berlaku, dan **C-3** (**A-20** —
> Mental Wellness dibuang atau ditunda) belum terjawab. Naskah 12 lewat tanpa
> menyebut jurnal maupun krisis (**G-9** / [#21](../../issues/21)); naskah ini
> menambahkan **taksiran stres dari kamera, suara, dan wearable** tanpa
> menyebut keduanya juga.

---

## §10.22 — Perception → Behavior

```
Perception → Observation → Event → Behavior Pattern → Behavior Model
```

Contoh:

```
Camera → Sitting detected → Activity Event → Repeated over 30 days
→ Pattern Detection
```

> Barulah Behavior Engine dapat menemukan pola.

---

> ⭐ **"Barulah" adalah kata yang tepat.** Ia menegakkan aturan §9.8 (satu kali
> bukan preferensi, dua puluh kali baru) pada jalur persepsi: satu deteksi
> bukan perilaku. Itu pertahanan terhadap karakterisasi tergesa, dan ia
> konsisten dengan tiga naskah sebelumnya.

> 🛑 **Tetapi "repeated over 30 days" berarti kamera menyala tiga puluh hari.**
> Digabung dengan opsi izin **`Always`** §10.27, ini adalah pemantauan
> berkelanjutan — bukan analisis atas foto yang dikirim. Lihat **C-17** /
> [#75](../../issues/75).

> 🛑 **Dan pengulangan tidak memperbaiki kesalahan sistematis — ia
> memperkuatnya.** Butir **B-17** mencatat satu salah hitung Wardrobe meracuni
> rekomendasi sesudahnya. Di sini polanya menjadi struktural:
>
> | Jenis kesalahan | Nasibnya di bawah §10.22 |
> |---|---|
> | **acak** — kamera sesekali salah baca | ✅ tersaring, karena butuh pengulangan |
> | **sistematis** — sudut pasang kamera membuat berdiri terbaca duduk | 🛑 **diperkuat**, karena berulang setiap hari |
>
> Konsolidasi berbasis frekuensi (§9.8) adalah pertahanan yang baik terhadap
> yang pertama dan **tidak berdaya sama sekali** terhadap yang kedua. Bedanya
> belum pernah ditulis, dan tanpa jalur koreksi manusia (yaitu `Edit` yang
> hilang, **E-74** / [#64](../../issues/64)) tidak ada yang menghentikannya.
> Lihat **B-25** / [#77](../../issues/77).

---

## §10.23 — Multimodal Memory

```
Multimodal Memory
├── Text Memory      ├── Document Memory
├── Image Memory     ├── Spatial Memory
├── Video Memory     ├── Sensor Memory
├── Audio Memory     └── Cross-Modal Memory
```

Contoh — user pernah mengirim image outfit. HumanVerse menyimpan:

```
Outfit: Black shirt · Dark jeans · White sneakers
```

plus **visual embedding**. Beberapa bulan kemudian:

> *"Apa outfit yang pernah saya pakai dengan sepatu ini?"*

```
Image similarity + Wardrobe graph + Episodic memory
```

---

> ⭐⭐ **Ini bukan taksonomi memory kesekian — ini sumbu keempat, dan ia
> konsisten dengan H-16.** Butir itu menetapkan tiga sumbu tegak lurus:
> `kind` (6 jenis) · `scope` (izin & pengambilan) · `tier` (kompresi). Delapan
> baris di atas adalah **`modality`**, dan ia tegak lurus terhadap ketiganya:
>
> ```
> kind      episodic          ← memori tentang satu kejadian
> scope     wardrobe          ← siapa boleh membacanya
> tier      episode           ← seberapa dipadatkan
> modality  image             ← dalam bentuk apa ia disimpan
> ```
>
> Contoh di naskah membuktikannya sendiri: *"outfit yang pernah saya pakai"*
> adalah **episodic** (kind) di **wardrobe** (scope) berbentuk **image**
> (modality). Empat sumbu, satu baris.
>
> ⚠️ Setelah lima hitungan yang saling bertabrakan (3/5/7/nama/6), penting
> menandai bahwa yang ini **tidak** bertabrakan — supaya tidak dikira
> taksonomi keenam dan ditutup salah.

> ⭐ **`Cross-Modal Memory` adalah satu-satunya yang bukan modality** — ia
> tautan antar-modality. Itu yang membuat pertanyaan di contoh bisa dijawab:
> menghubungkan foto sepatu dengan catatan teks tentang outfit. Ia lebih tepat
> dibaca sebagai **relasi**, bukan jenis penyimpanan, dan tempatnya mungkin di
> graf.

> ⚠️ **Memori bergambar mengubah beban hapus akun.** `memories.embedding_id`
> di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) menunjuk Qdrant; sekarang
> ada berkas gambar di object storage, embedding visual, dan turunan lain —
> tiga tempat, bukan satu. §8.38 sudah memuat `Object Storage`; yang belum:
> **berkas asli yang dirujuk banyak memori** (satu foto lemari melahirkan
> sepuluh memori item). Menghapus satu memori tidak boleh menghapus fotonya
> kalau memori lain masih memakainya — dan menghapus akun harus menghapus
> keduanya.
