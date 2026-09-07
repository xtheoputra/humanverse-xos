# 161 — §9.24–§9.26 Decision Intelligence, Personal Utility Model & Agency

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.24 — Layer 10: Decision Intelligence

> Recommendation dan decision harus **dipisahkan**.

| | Bunyinya |
|---|---|
| **Recommendation** | *"Saya menyarankan A."* |
| **Decision Intelligence** | *"Mari kita bandingkan A, B, dan C."* |

Contoh:

```
Career Option A          Career Option B
Salary:    8/10          Salary:    9/10
Learning:  9/10          Learning:  6/10
Risk:      4/10          Risk:      7/10
Network:   6/10          Network:   8/10
```

> Kemudian **user memilih**.

---

> ⭐⭐ **Ini penerapan paling jelas dari janji "decision support, bukan
> pengambil keputusan" (naskah 4 §27).** Perbedaan antara *menyarankan* dan
> *membandingkan* bukan gaya bahasa — ia perbedaan siapa yang memutuskan.
> Sebuah tabel empat baris menyerahkan penilaian kepada orangnya; satu kalimat
> saran mengambilnya.
>
> Untuk keputusan besar (karier, pindah kota, keuangan), bentuk **tabel
> perbandingan** semestinya jadi bawaan, dan saran tunggal jadi pengecualian
> yang harus diminta.

> ⚠️ **Skala `8/10` adalah skala keenam.** Yang sudah berjalan: persen (naskah
> 2) · 100 poin (naskah 3) · 0–1 (naskah 5) · persen confidence & `A` huruf
> (naskah 12) · dan kini **x/10**. Usul di [#32](../../issues/32) tidak
> berubah: simpan **0–1**, tampilkan apa saja — `8/10` adalah `0.8` yang
> ditampilkan.

> ⚠️ **`Risk: 4/10` berarti "risiko lebih rendah lebih baik", sementara tiga
> baris lain berarti "lebih tinggi lebih baik".** Satu tabel dengan dua arah
> tanpa penanda akan salah dibaca — dan lebih berbahaya lagi, salah dijumlahkan
> oleh §9.25. Setiap dimensi butuh arahnya sendiri (`higher_is_better`).

---

## §9.25 — Personal Utility Model

> Setiap user memiliki prioritas berbeda.

```
Utility =
 0.30 Career Growth
+0.25 Income
+0.20 Learning
+0.15 Stability
+0.10 Work-Life Balance
```

Bobot ini dapat dipelajari dari:

```
explicit preferences + actual decisions + feedback
```

> Tetapi **user harus dapat mengubahnya**.

---

> ⭐ **Bobot berjumlah tepat 1,00** (0,30+0,25+0,20+0,15+0,10). Diperiksa
> karena dua sistem skoring sebelumnya juga berjumlah rapi (**F**) — dan yang
> ini benar.

> 🛑 **Ini karakterisasi yang lebih dalam daripada Identity Memory.**
> **C-13** mempersoalkan sistem yang menyimpulkan **apa yang seseorang
> lakukan** dan menyimpannya permanen. Utility Model menyimpulkan **apa yang
> seseorang hargai** — dan memakainya untuk membandingkan pilihan karier.
>
> Bedanya nyata: *"User berkomitmen pada latihan beban"* bisa dibantah dengan
> menunjuk data. *"Anda menghargai Income 0,25 dan Work-Life Balance 0,10"*
> adalah pernyataan tentang nilai hidup seseorang, disimpulkan dari
> keputusan-keputusan yang mungkin diambil dalam keadaan terpaksa. Orang yang
> menerima lembur karena butuh uang tidak dengan sendirinya *menghargai* uang
> di atas keluarga.
>
> ⭐ **Naskah menyelamatkannya dengan satu kalimat: *"Tetapi user harus dapat
> mengubahnya."*** Itu tepat — dan itu persis `Edit` yang **hilang** dari
> Privacy Center §8.36 (**E-74** / [#64](../../issues/64)). Bobot utility
> menjadi **kandidat pertama yang wajib bisa disunting pengguna**, dan
> sekarang ada dua bagian naskah yang menuntutnya sementara antarmukanya belum
> punya tempat.
>
> Tiga hal yang perlu ditulis: bobot harus **terlihat** sebelum dipakai, boleh
> **diubah**, dan sistem harus mengatakan bahwa ia **menebak** — bukan
> menampilkannya sebagai profil yang sudah pasti. Lihat **C-16** /
> [#71](../../issues/71).

---

## §9.26 — Layer 11: Agency

> Sekarang HumanVerse tidak hanya berpikir. Ia dapat:

```
Observe · Recommend · Ask · Plan · Execute · Verify · Learn
```

Tetapi **autonomy bertingkat**:

```
Level 0    Information
Level 1    Recommendation
Level 2    Prepare action
Level 3    Ask confirmation
Level 4    Bounded autonomy
```

> Untuk tindakan berisiko tinggi, kembali ke **Fase 8 Security/Risk Engine**.

---

> 🛑🛑 **Ini tabrakan penomoran paling berbahaya di tiga belas naskah: dua
> tangga 0–4, sumbu berbeda, dan artinya TERBALIK di ujung atas.**
>
> | Nomor | Naskah 12 §8.16 — **risiko aksi** | Naskah 13 §9.26 — **otonomi AI** |
> |---|---|---|
> | 0 | Informational | Information |
> | 1 | Low impact | Recommendation |
> | 2 | Moderate | Prepare action |
> | 3 | High impact → **wajib konfirmasi** | **Ask confirmation** |
> | 4 | Critical → **wajib konfirmasi** | **Bounded autonomy** — bertindak sendiri |
>
> Perhatikan baris terakhir. Di naskah 12, **Level 4 adalah yang paling wajib
> bertanya**. Di naskah 13, **Level 4 adalah yang paling boleh tidak
> bertanya** — ia satu tingkat *di atas* "ask confirmation".
>
> Artinya kalimat *"agent ini Level 4"* berarti **"selalu minta izin"** kalau
> dibaca dengan naskah 12, dan **"boleh jalan sendiri"** kalau dibaca dengan
> naskah 13. Itu bukan kebingungan dokumentasi; itu kesalahan yang, kalau
> masuk ke kode, membalik arah keselamatan.
>
> Keduanya sah sebagai konsep — risiko dan otonomi memang dua sumbu berbeda,
> dan memisahkannya adalah kemajuan. Yang tidak boleh adalah **memakai
> penomoran yang sama untuk keduanya**. Usul: otonomi memakai huruf
> (`A0`–`A4`), risiko tetap `R0`–`R4`, dan aturan pengikatnya ditulis satu
> baris — *"otonomi tertinggi yang diizinkan = fungsi dari risiko aksi"*,
> bukan dua angka yang berdiri sendiri. Lihat **E-77** / [#67](../../issues/67).

> ⭐ **`Verify` adalah kata kerja yang belum pernah ada di daftar mana pun.**
> Observe · Recommend · Ask · Plan · Execute · **Verify** · Learn — memeriksa
> bahwa aksi benar-benar berhasil sebelum belajar darinya. Tanpa itu, feedback
> loop §9.35 belajar dari aksi yang mungkin gagal diam-diam. Ia juga yang
> paling dekat dengan *Human Override* yang **tidak datang** di Fase 8
> (**G-8** / [#65](../../issues/65)) — tapi `Verify` memeriksa hasil, bukan
> membatalkan aksi; keduanya masih berbeda.

> ⚠️ **"Bounded autonomy" tidak menyebutkan batasnya.** Itu justru satu-satunya
> hal yang membuat istilah ini berarti sesuatu: batas apa, ditetapkan siapa,
> dan dicabut bagaimana. §8.18 punya tempat untuk itu (`policy`), dan §8.35
> punya tombol matinya (Kill Switch) — tetapi §9.26 tidak menunjuk keduanya
> selain lewat satu kalimat penutup. Untuk V0 pertanyaan ini belum mendesak:
> tidak ada satu pun tool V0 yang berisiko di atas level 2.
