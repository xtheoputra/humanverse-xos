# 172 — §10.24–§10.26 Perception Confidence, Provenance & Multimodal Agent Tools

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.24 — Perception Confidence Engine

```
Observation
├── Value       ├── Timestamp
├── Confidence  ├── Quality
├── Source      └── Uncertainty
```

```json
{ "observation": "person_detected", "confidence": 0.97,
  "source": "camera", "quality": 0.94 }
```

Tetapi:

```json
{ "observation": "person_is_tired", "confidence": 0.38 }
```

> Maka Cognitive Runtime **tidak boleh memperlakukan keduanya sama**.

---

> ⭐⭐ **Dua contoh berdampingan ini adalah argumen terkuat untuk ambang
> confidence yang belum ditetapkan sejak naskah 5.** `0,97` dan `0,38` bukan
> sekadar dua angka berbeda — keduanya berada di tingkat berbeda pada tangga
> §10.5: yang pertama **Perception**, yang kedua **Inference**. Dan
> `person_is_tired` juga menyentuh **C-2** (jangan berpura-pura jadi dokter).
>
> Butir **H-14** dan [#34](../../issues/34) meminta ambang High/Medium/Low
> sejak naskah 5; ini naskah **keenam** yang mewajibkan mekanismenya tanpa
> memberi angkanya. Usul yang sudah saya tulis di #34 tetap berlaku, dengan
> satu tambahan dari naskah ini: **ambangnya berbeda per tingkat** — sebuah
> Inference pada 0,60 tidak sama layak-nyatanya dengan Perception pada 0,60.

> ⭐ **`Uncertainty` sebagai field terpisah dari `confidence`** melengkapi
> pembedaan §9.19 (`probability` vs `confidence`). Tiga besaran, tiga
> pertanyaan berbeda — dan repo ini sekarang punya ketiganya, yang jarang.
> ⚠️ Tapi ketiganya juga **belum pernah didefinisikan berdampingan**; kalau
> tidak ditulis sekali, mereka akan diisi sembarang.

---

## §10.25 — Perception Provenance

> Setiap informasi harus dapat **ditelusuri**.

```
Recommendation → Reasoning → Inference → Observation → Source
```

Contoh:

```
Recommendation:  Take a break
Evidence:        Long continuous activity
Observation:     Desk occupancy = 118 min
Source:          Camera + activity sensor
Confidence:      0.81
```

> Ini penting untuk **auditability**.

---

> ⭐⭐⭐ **Ini mengembalikan apa yang §8.25 hilangkan — separuh dari E-75 /
> [#64](../../issues/64).**
>
> Naskah 4 §45 menyimpan *"audit metadata **dan alasan ringkas yang dapat
> diverifikasi**"*; dua belas field §8.25 memuat metadata-nya dan **tidak satu
> pun alasan**, sehingga jejak audit bisa menjawab *apa* yang diputuskan tapi
> tidak pernah **kenapa**. Butir **H-7** (self-improving agent sulit diaudit)
> ditutup justru atas dasar §45.
>
> Rantai lima langkah di atas adalah alasan yang tersimpan — dan lebih baik
> daripada kalimat bebas, karena ia **berantai sampai ke sumbernya**:
>
> ```
> "Take a break"  ← kenapa?
> "Long continuous activity"  ← dari mana?
> "Desk occupancy = 118 min"  ← diukur apa?
> "Camera + activity sensor"  ← seberapa yakin?  0.81
> ```
>
> Empat pertanyaan, empat jawaban tersimpan. Itu yang dibutuhkan `rationale`
> di `audit_logs`, dan bentuknya sekarang jelas: **bukan teks bebas, melainkan
> rantai berstruktur**.
>
> ⚠️ Yang tersisa dari #64 tetap terbuka: `Edit` di Privacy Center — cara
> pengguna **membantah** rantai itu, bukan hanya membacanya.

> ⚠️ **`Desk occupancy = 118 min` adalah contoh provenance yang baik dan contoh
> privasi yang berat sekaligus.** Ia hanya bisa ada kalau kamera menyala dua
> jam. Provenance justru **membuat pemantauannya terlihat** — pengguna yang
> membaca rantai ini akan tahu persis apa yang diukur, dan itu bagus. Tapi
> ia juga bukti tertulis bahwa pemantauannya terjadi. Lihat **C-17** /
> [#75](../../issues/75).

---

## §10.26 — Multimodal Agent Tools

```
vision.detect_objects()      document.extract()
vision.analyze_scene()       document.summarize()
audio.transcribe()           sensor.read()
audio.detect_events()        sensor.aggregate()
video.analyze()              spatial.locate()
video.track()                spatial.map()
                             spatial.query()
```

Tetapi tools harus masuk melalui:

```
Tool Request → Permission → Privacy → Risk → Policy → Execution
```

---

> ⭐ **`Privacy` sebagai langkah tersendiri adalah tambahan atas §8.21**, yang
> hanya punya `Tool Validator → Permission → Risk → Policy`. Untuk tool yang
> menyentuh kamera dan mikrofon, pemeriksaan privasi memang berbeda dari
> pemeriksaan izin: yang satu bertanya *"boleh tidak"*, yang lain
> *"klasifikasinya apa dan berapa lama disimpan"*.
>
> ⚠️ `Tool Validator` §8.21 justru hilang dari rantai ini — langkah yang
> memeriksa bahwa permintaannya sendiri berbentuk sah sebelum izin diperiksa.
> Rantai lengkapnya semestinya gabungan keduanya.

> 🛑 **Tiga belas tool baru, dan tidak satu pun diberi `risk_level`.**
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) mewajibkan setiap tool punya
> `risk_level` dan `side_effects`; sembilan tool V0 semuanya risk 0–2.
>
> Tool persepsi akan menjadi **tool pertama yang menyentuh data Level 3 dan
> kandidat Level 4** (wajah, suara, isi rumah). Di tangga risiko §8.16 mereka
> tidak jelas duduk di mana: membaca kamera bukan "aksi berdampak" karena tidak
> mengubah apa pun di dunia — tapi ia **membuka data paling sensitif yang
> dimiliki sistem**.
>
> Itu memperlihatkan lubang di tangga risiko itu sendiri: **ia mengukur akibat
> aksi, bukan sensitivitas data yang disentuh.** `habit.complete` (menulis satu
> baris) adalah risk 2; `vision.analyze_scene()` (membaca isi ruang tidur
> seseorang) tidak punya angka sama sekali. Lihat **G-11** dan
> [#77](../../issues/77).

> ⚠️ **`sensor.aggregate()` dan `spatial.query()` adalah tool baca yang
> hasilnya turunan** — dan turunan membawa sensitivitas sumbernya. Agregat dari
> data lokasi tetap data lokasi. Aturan 6 [`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> melarang agent `third_party` meminta scope `journal`, `finance`, `health`;
> daftar itu perlu ditambah **`camera`, `audio`, `location`, `spatial`** sebelum
> marketplace dibuka (Phase 14).
