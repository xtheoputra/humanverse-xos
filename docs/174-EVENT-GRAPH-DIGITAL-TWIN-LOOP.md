# 174 — §10.30–§10.33 Event Architecture, Human Graph, Digital Twin & Cognitive Loop

> Berkas ini merekam kata pemilik apa adanya (naskah keempatbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §10.30 — Multimodal Event Architecture

Tambahkan event baru:

```
ImageCaptured            ObjectDetected        LocationChanged
VideoCaptured            PersonDetected        SensorReadingReceived
AudioCaptured            ActivityDetected      WearableReadingReceived
SpeechDetected           GestureDetected       SpatialMapUpdated
DocumentUploaded         SceneChanged
```

Kemudian:

```
Event Bus → Context Engine → Behavior Engine → Memory → Cognitive Runtime
```

---

> 🛑 **Empat belas nama, dan semuanya PascalCase — konvensi KETIGA setelah
> keputusan #38 ditutup dua naskah lalu.**
>
> [#38](../../issues/38) menetapkan `<domain>.<past_tense_verb>`, huruf kecil,
> **sekali dipakai tidak pernah diganti** ([`../spec/03`](../spec/03-EVENT-CONTRACTS.md)).
> Sejak itu: naskah 12 §8.26 menulis prosa (*"Authentication Failed"*,
> **E-70** / [#63](../../issues/63)), dan sekarang PascalCase.
>
> Yang ini justru **paling mudah diperbaiki** karena hampir semuanya sudah
> berbentuk `<benda><KataKerja>`:
>
> | Naskah 14 | Dua segmen |
> |---|---|
> | `ImageCaptured` | `image.captured` |
> | `SpeechDetected` | `speech.detected` |
> | `PersonDetected` | `person.detected` |
> | `SceneChanged` | `scene.changed` |
> | `LocationChanged` | `location.changed` |
> | `SpatialMapUpdated` | `spatial_map.updated` |
> | `SensorReadingReceived` | `sensor.reading_received` |
>
> Nama event **tidak boleh diganti setelah dipakai**, jadi ini harus selesai
> sebelum baris pertama. Lihat **E-88**.
>
> 🔴 **Tabel di atas DIGANTIKAN [K-15](KEPUTUSAN-DIDELEGASIKAN.md)
> (11 Sep 2026) — dibiarkan berdiri karena ia buktinya, bukan karena ia
> berlaku.** Ketujuh padanannya memakai aturan *“kata pertama → domain”*, dan
> dijalankan terhadap registry domain [`../arch/07`](../arch/07-EVENT-CONTRACTS.md)
> §2 **tak satu pun lolos**: `image` · `speech` · `person` · `scene` ·
> `location` · `sensor` bukan domain terdaftar, dan `spatial_map` bahkan
> memakai garis bawah **di dalam segmen domain**. Yang berlaku sekarang ada di
> [`../spec/03`](../spec/03-EVENT-CONTRACTS.md): ketujuhnya menjadi
> `perception.*`, kecuali `SpatialMapUpdated` → `spatial.map_updated`.
>
> 💡 **Dan usul ini sendiri pernah mengotori pengukuran.** `spatial_map.updated`
> sempat terhitung sebagai nama yang “sudah sesuai format” di percobaan pertama
> [`SENSUS-EVENT.md`](SENSUS-EVENT.md) — padahal ia usul saya, bukan kata
> pemilik. Catatan audit yang berdiri berdampingan dengan naskah akan terbaca
> sebagai naskah oleh alat mana pun yang tidak diajari membedakannya.

> 🛑🛑 **Dan yang lebih berat daripada namanya: event ini tidak muat di tabel
> `events`.**
>
> Tiga hal, semuanya bisa diperiksa terhadap [`../spec/01`](../spec/01-DATABASE-SCHEMA.md):
>
> **1 · `source` tidak punya nilainya.**
> `CHECK (source IN ('app','agent','integration','backfill'))` — tidak ada
> `sensor` maupun `device`. Setiap event persepsi akan ditolak constraint.
>
> **2 · Volumenya tiga sampai empat orde lebih besar.**
> Event manusia (`habit.completed`, `mood.logged`) muncul puluhan kali per
> hari. `PersonDetected` dari satu kamera pada 1 Hz adalah **86.400 kejadian
> per hari**; §10.22 menuntut **30 hari**. Satu pengguna, satu kamera, satu
> jenis event ≈ **2,6 juta baris** — di tabel yang punya `UNIQUE (user_id,
> idempotency_key)`, artinya 2,6 juta entri indeks juga.
>
> **3 · `idempotency_key` kehilangan artinya.**
> Kunci dibuat dari isi yang menentukan identitas kejadian
> ([`../spec/03`](../spec/03-EVENT-CONTRACTS.md) aturan 1) — `habit:<id>:<tanggal>`.
> Untuk aliran bingkai, satu-satunya yang membedakan adalah waktunya, sehingga
> kuncinya menjadi stempel waktu dan **tidak menghentikan duplikasi apa pun**.
>
> ⭐ **Jawabannya sudah ada di naskah ini sendiri, hanya tidak disambungkan.**
> §10.10 mengubah **lima bingkai jadi satu event** (*"Person picked up
> object"*), dan §10.11 mengubah **5.400 pembacaan jadi satu kalimat**
> (*"stable seated state for ~90 minutes"*). Itu agregasi temporal, dan itulah
> yang seharusnya masuk bus.
>
> Aturan yang mengikuti: **`events` hanya menerima kejadian yang bermakna bagi
> manusia; pembacaan mentah tinggal di lapisan persepsi (§7.10 lakehouse /
> §7.13 feature store) dan tidak pernah menyeberang.** Itu juga sejalan dengan
> §7.26 (*raw pendek, agregat panjang*). Lihat **E-89** /
> [#74](../../issues/74).

---

## §10.31 — Multimodal Human Graph

```
Human    ──wears──────────→  Clothing
Human    ──located_in─────→  Room
Object   ──located_on─────→  Desk
Human    ──interacts_with→  Object
Voice    ──belongs_to─────→  Conversation
Document ──contains───────→  Entity
```

---

> ⭐ **Enam relasi ini semuanya `Perception` pada tangga §10.5 — terukur, bukan
> disimpulkan.** Itu membuatnya jenis relasi paling aman yang pernah masuk graf,
> dan ia kontras tajam dengan `influences` yang kembali di §9.11 tanpa bukti
> kausal (**E-81** / [#7](../../issues/7)).
>
> Daftar node/relasi graf ini yang **keenam**, tapi kali ini penambahannya
> tidak menghapus apa pun dan tidak bertabrakan dengan yang lama — ia lapisan
> spasial/persepsi di atas graf yang sudah ada.

> ⚠️ **`Human ──located_in──→ Room` adalah baris yang paling berat di seluruh
> naskah.** Ia merekam **siapa ada di mana** sebagai fakta graf yang bertahan.
> Kalau `Human` di sini bisa berarti orang selain penggunanya (dan §10.19
> mendaftarkan `Humans` jamak di satu adegan), graf HumanVerse mulai menyimpan
> keberadaan orang yang tidak pernah menyetujui apa pun. Lihat **C-17** /
> [#75](../../issues/75).

> ⚠️ **`Voice ──belongs_to──→ Conversation`** menyiratkan sidik suara yang
> bertahan antar-sesi — itulah yang membuat *Speaker Diarization* (§10.8)
> berguna lintas waktu. Sidik suara adalah **data biometrik** sama seperti
> wajah (**C-1**), dan ia belum pernah disebut sebagai kategori khusus.

---

## §10.32 — Multimodal Digital Twin

```
Digital Twin
├── Identity     ├── State      ├── Decision
├── Behavior     ├── Skills     │
├── Preference   ├── Social     └── Perception
├── Goals                           ├── Visual
                                    ├── Audio
                                    ├── Spatial
                                    ├── Sensor
                                    └── Environmental
```

> Digital Twin = **Behavioral Model + State Model + Context Model + Perception
> Model**. Tetap **bukan mind-reading atau clone manusia**.

---

> ⭐ **Delapan komponen pertama identik dengan naskah 4 §25** — Identity ·
> Behavior · Preference · Goal · State · Skill · **Social** · Decision. Butir
> **E-34** mencatat naskah 5 menukar `SocialModel` → `LifestyleModel`; di sini
> **Social kembali dan Lifestyle hilang lagi**.
>
> Itu menyelesaikan separuh E-34 ke arah naskah 4: dua naskah memakai *Social*,
> satu memakai *Lifestyle*. ⚠️ Tapi ia juga mengulang pola **H-8** — sebuah
> daftar yang berubah, kembali, lalu mungkin berubah lagi. Dicatat sebagai
> kecenderungan, belum sebagai keputusan.

> ⭐ **"Tetap bukan mind-reading atau clone manusia" — naskah kelima berturut-
> turut memegang batas itu**, dan kali ini justru ketika sistemnya paling
> mendekati kesan sebaliknya. Menyebutnya di tempat yang paling menggoda untuk
> melebih-lebihkan adalah tanda disiplin, bukan basa-basi.

---

## §10.33 — Multimodal Cognitive Loop

```
WORLD → PERCEPTION → OBSERVATION → CONTEXT → MEMORY → UNDERSTANDING
→ REASONING → PREDICTION → DECISION → RECOMMENDATION → ACTION
→ FEEDBACK → LEARNING ──→ kembali ke PERCEPTION
```

> Ini mulai membentuk **closed-loop intelligence**.

---

> ⭐ **`WORLD` di puncak adalah perubahan yang benar dari §9.1.** Loop naskah
> 13 dimulai dari `HUMAN → OBSERVATION`; di sini dunia mendahului manusia, dan
> `PERCEPTION` disisipkan sebelum `OBSERVATION`. Itu tepat sesuai tangga
> §10.5: persepsi adalah pembacaan, observasi adalah hasilnya.

> ⚠️ **"Closed-loop" adalah istilah yang membawa beban.** Loop tertutup berarti
> keluaran sistem memengaruhi masukan berikutnya **tanpa manusia di
> tengahnya** — dan itulah yang §9.35 dan **C-13** peringatkan: rekomendasi
> yang lahir dari kesimpulan keliru menghasilkan data yang seolah
> membenarkannya.
>
> Yang menahan loop ini tetap terbuka justru ada di dalamnya:
> **`RECOMMENDATION` sebelum `ACTION`** — manusia memilih di antara keduanya
> (§9.24, §8.17). Itu sebaiknya digambar, karena diagram yang menyambungkan
> `DECISION → RECOMMENDATION → ACTION` tanpa penanda terlihat otomatis penuh.
> Bertaut **E-77** / [#67](../../issues/67): otonomi Level 4 (*bounded
> autonomy*) adalah persis titik di mana loop ini benar-benar tertutup.
