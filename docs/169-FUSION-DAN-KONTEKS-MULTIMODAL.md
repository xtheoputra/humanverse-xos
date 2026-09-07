# 169 — §10.16–§10.17 Multimodal Fusion & Multimodal Context Engine

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.16 — Multimodal Fusion

**Early Fusion** — data digabung sejak awal:

```
Image + Audio + Text → Joint Model
```

**Late Fusion** — setiap modality diproses sendiri:

```
Image → Vision Model
Audio → Audio Model
Text  → LLM
        ↓
      Fusion
```

**Intermediate Fusion** — feature masing-masing modality digabung:

```
Image → Features
Audio → Features
Text  → Features
        ↓
   Fusion Layer
```

**Hybrid Fusion** — HumanVerse menggunakan semuanya berdasarkan kebutuhan.

> Ini yang saya rekomendasikan.

---

> ⚠️ **"Menggunakan semuanya berdasarkan kebutuhan" bukan keputusan — ia
> penundaan keputusan.** Dan penundaannya wajar pada tahap ini; yang perlu
> dicatat adalah bahwa **aturan pemilihannya belum ada**, dan tanpa aturan itu
> tiga jalur akan dibangun tiga kali oleh tiga orang dengan hasil berbeda.
>
> Aturan yang biasanya benar, dan bisa ditulis sekarang dalam tiga baris:
>
> | Fusion | Dipakai ketika |
> |---|---|
> | **Late** | modality **saling melengkapi** — foto outfit + cuaca + kalender. Ini yang paling sering, dan paling murah |
> | **Intermediate** | modality **menggambarkan hal yang sama** — video + audio dari satu kejadian |
> | **Early** | hanya bila ada model tunggal yang memang dilatih multimodal |
>
> **Late Fusion adalah bawaan yang benar untuk HumanVerse**, karena hampir
> semua contoh di naskah ini (§10.15, §10.17) menggabungkan sumber yang tidak
> sinkron waktunya — kalender besok, cuaca hari ini, foto tadi. Data yang tidak
> sinkron tidak bisa difusikan lebih awal.

> ⚠️ **Early Fusion menuntut model yang dilatih sendiri**, dan itu menyentuh
> **B-21** / [#48](../../issues/48) (Research Lab tidak bisa mulai sebelum V0
> mengumpulkan data) serta **B-22** / [#59](../../issues/59) (`purpose:
> model_training` harus ditanyakan sejak awal). Melatih model multimodal di
> atas foto dan suara pengguna adalah bentuk pelatihan yang **paling** butuh
> persetujuan terpisah.

---

## §10.17 — Multimodal Context Engine

> Perception **tidak boleh berdiri sendiri**.

```
Image:       Person wearing jacket
Weather:     32°C
Calendar:    Outdoor event
Location:    Jakarta
Preference:  Dislikes heavy clothing
```

Context Engine menghasilkan **Current Context**, sehingga recommendation
engine dapat mengatakan:

> *"Jaket tersebut mungkin kurang sesuai untuk kondisi saat ini."*

Jadi:

```
Perception + Context + Memory + Preference = Understanding
```

---

> ⭐⭐ **Contoh ini adalah bantahan paling ringkas terhadap "computer vision
> saja sudah cukup".** Penglihatan melihat jaket. Yang membuat jawabannya
> berguna adalah **empat hal yang tidak terlihat di gambar**: suhu, acara,
> kota, dan preferensi. Model penglihatan terbaik di dunia tidak bisa sampai ke
> kalimat itu.
>
> Ia juga memperagakan tangga §10.5 dengan benar: *"person wearing jacket"*
> adalah **Perception**; *"mungkin kurang sesuai"* adalah **Inference** — dan
> bahasanya berubah sesuai tingkatnya.

> ⭐ **Jakarta muncul lagi.** Naskah 4 §2 memakai Jakarta sebagai satu-satunya
> petunjuk pasar; **A-3** / [#9](../../issues/9) mencatat itu terlalu tipis
> untuk jadi keputusan. Sekarang ia muncul kedua kalinya, dan kali ini dengan
> konsekuensi teknis: *32°C* dan *"dislikes heavy clothing"* adalah kombinasi
> tropis. Masih bukan keputusan, tapi dua petunjuk lebih baik dari satu.

> ⚠️ **Persamaan `Perception + Context + Memory + Preference = Understanding`
> menghilangkan satu suku yang §9.15 punya.** Understanding Engine naskah 13
> menerima **enam** masukan: *Events · Memory · Context · Knowledge · Behavior ·
> State*. Di sini: empat, dan **`Knowledge` serta `State` hilang**, sementara
> `Perception` masuk.
>
> Kemungkinan besar ini penyederhanaan untuk contoh, bukan revisi — tapi
> persamaan yang ditulis dengan tanda sama dengan akan dikutip sebagai
> definisi. Yang lengkap tetap §9.15, **ditambah** `Perception` sebagai
> masukan ketujuh.

> ⚠️ **Weather dan Calendar keduanya tool V2** ([`../spec/05`](../spec/05-AGENT-CONTRACTS.md)),
> dan Location belum punya izin maupun sumber di V0. Contoh ini menggambarkan
> V2+.
