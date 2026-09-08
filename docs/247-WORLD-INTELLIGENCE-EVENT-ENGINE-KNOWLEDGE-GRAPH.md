# 247 — §18.4–§18.6 World Intelligence Engine, World Event Engine & World Knowledge Graph

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh dua, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §18.4 — World Intelligence Engine

> Komponen pertama adalah **World Intelligence Engine**. Fungsinya memahami
> dunia secara dinamis.

Data: `news · scientific publications · economic indicators · financial markets ·
weather · climate · transportation · geopolitics · technology · social trends ·
public datasets · government data · industry data · internet knowledge ·
satellite/geospatial data · IoT data · sensor networks`.

```
RAW WORLD DATA → INGESTION → NORMALIZATION → ENTITY EXTRACTION
   → EVENT EXTRACTION → RELATION EXTRACTION → TEMPORAL ANALYSIS
   → CONTEXTUALIZATION → WORLD KNOWLEDGE GRAPH → WORLD MODEL → INTELLIGENCE
```

---

> ⭐⭐ **Pipeline sebelas langkah ini adalah rantai pemrosesan paling rinci di
> dua puluh dua naskah, dan urutannya benar.** `NORMALIZATION` sebelum
> `ENTITY EXTRACTION`, `RELATION EXTRACTION` sesudah entitas ada,
> `TEMPORAL ANALYSIS` sebagai langkah tersendiri alih-alih atribut yang
> dititipkan — semuanya urutan yang memang harus begitu. `CONTEXTUALIZATION`
> sebagai langkah terpisah sebelum graf juga tepat: fakta yang sama berarti
> berbeda tergantung tempat dan waktunya.

> 🛑🛑 **Tetapi tujuh belas sumber itu adalah kelas hukum yang berbeda-beda, dan
> pipeline-nya tidak punya satu pun gerbang lisensi.**
>
> `news` dan `scientific publications` hampir seluruhnya berhak cipta dan
> sebagian besar terkunci di balik syarat layanan yang melarang penambangan
> otomatis. `internet knowledge` adalah nama untuk *"apa saja"*. `government
> data` dan `public datasets` **bervariasi per yurisdiksi** dan sebagian
> mewajibkan atribusi. `satellite/geospatial` sering berlisensi komersial per
> citra.
>
> ⭐ Bahannya sebenarnya sudah ada di naskah ini: **§18.16 mewajibkan `license`
> sebagai salah satu dari tujuh field pada setiap knowledge.** Yang hilang cuma
> penyambungannya — `INGESTION` tidak menyebut lisensi, dan §18.28 memberi
> `knowledge_sources` tanpa menyatakan bahwa lisensi diperiksa **sebelum**
> data dipakai, bukan dicatat sesudahnya.
>
> Ini menjadi mendesak karena §18.19 membuka **Intelligence Marketplace**:
> begitu turunan dari data ini dijual, pertanyaannya berhenti menjadi soal
> penggunaan wajar. Lihat **C-27** / [#122](../../issues/122).

> 🛑 **Dan skalanya tidak disebut satu kali pun, di basis data yang sudah
> ditandai kewalahan satu naskah lalu.**
>
> **B-34** ([#119](../../issues/119)) mencatat tiga tabel biometrik tumbuh
> dengan *waktu × frekuensi sensor* — ratusan juta baris per pengguna.
> `world_observations` (§18.28) tumbuh dengan **waktu × frekuensi × seluruh
> dunia**, dan ia **tidak dibagi per pengguna**, jadi ia tidak punya pembatas
> alami sama sekali. Basis data V0 tetap PostgreSQL + Redis (**H-12**).
>
> ⭐ Obatnya, seperti pada B-34, sudah ditulis naskah ini sendiri: §18.7
> membedakan `Trend`, `Change Point`, dan `Cycle` — ketiganya **agregat**.
> Yang perlu dinyatakan: **World Model menyimpan keadaan dan perubahan, bukan
> setiap pengamatan mentah**; sumber mentah tetap di sisi penyedianya dan yang
> disimpan adalah rujukan + ringkasannya. Lihat **B-35** / [#127](../../issues/127).

> ⚠️ **`social trends` adalah satu-satunya sumber di daftar ini yang isinya
> orang.** Enam belas lainnya mengukur benda, harga, cuaca, atau dokumen; yang
> satu ini mengukur perilaku manusia dalam agregat — dan agregat perilaku pada
> skala kota bisa dikembalikan ke individu jauh lebih sering daripada yang
> diperkirakan. Ia layak diberi tingkat sensitivitasnya sendiri, bukan berdiri
> sederet dengan `weather`.

---

## §18.5 — World Event Engine

> HumanVerse perlu memiliki pemahaman terhadap **event**, bukan hanya dokumen.

> Dokumen: *"Oil prices rise 8 %"* menjadi:

```yaml
event:      OilPriceChanged
entity:     Oil
change:     +8%
time:       T
location:   Global
confidence: 0.94
sources:    [...]
```

> Event lain: `CompanyAcquired · ProductLaunched · EarthquakeDetected ·
> StormFormed · PolicyChanged · InterestRateChanged · MarketMoved ·
> ResearchPublished · TechnologyReleased · DiseaseOutbreakReported ·
> SupplyChainDisrupted · TrafficChanged · FlightCancelled`

---

> ⭐⭐⭐ **`confidence` dan `sources` ada DI DALAM event, bukan ditempelkan
> belakangan — dan itu perbedaan yang menentukan.**
>
> Sebuah event yang membawa sumbernya sendiri bisa ditarik kembali ketika
> sumbernya dibantah; event yang kehilangan sumbernya di langkah pertama tidak
> akan pernah bisa. §18.23 (Information Integrity) dan §18.21 (Provenance)
> keduanya **hanya bisa bekerja** kalau field ini ada sejak awal, dan naskah ini
> menaruhnya sejak awal. Bandingkan §13.12 yang memberi lima belas event tanpa
> satu pun membawa keyakinan atau asal.

> ⭐ **Pemisahan `entity` dari `event` juga benar.** *"Oil"* sebagai entitas yang
> hidup lintas peristiwa memungkinkan §18.6 menghubungkan peristiwa yang menyebut
> hal yang sama dengan kata yang berbeda — dan itu tepat yang dilakukan
> `entity-resolution` di §18.27.

> 🛑 **Tetapi penamaannya PascalCase — pelanggaran
> [#38](../../issues/38) yang KESEMBILAN berturut-turut.**
>
> [`spec/03-EVENT-CONTRACTS.md`](../spec/03-EVENT-CONTRACTS.md) menetapkan
> `domain.verb` huruf kecil (`sleep.completed`, `mood.logged`,
> `habit.created`). Riwayat pelanggarannya: E-70 · E-88 · E-98 · E-116 ·
> naskah 18 · E-126 · E-132 · **E-135** (§17.42 `SleepEnded`) · di sini.
>
> Bedanya dengan naskah 21: di sana tabrakannya soal **kosakata** (`SleepEnded`
> lawan `sleep.completed` untuk kejadian yang sama, dan kalau keduanya dikodekan
> satu malam tidur menghasilkan dua event). Di sini tiga belas nama itu
> **semuanya domain baru** — jadi tidak ada tabrakan makna, hanya tabrakan
> bentuk. Itu justru membuatnya **murah diperbaiki sekarang**:
> `world.oil_price_changed`, `world.company_acquired`, dan seterusnya, sebelum
> satu pun ditulis di kode. Lihat **E-140**.

> ⚠️ **`DiseaseOutbreakReported` dan `EarthquakeDetected` bukan event sekelas
> `ProductLaunched`.** Ketiganya berdiri di satu daftar, tetapi dua yang pertama
> memicu §18.25 (Early Warning) dan menyentuh keselamatan orang. Kata kerjanya
> sendiri sudah menunjukkan perbedaannya — *`Reported`* (ada yang melaporkan)
> lawan *`Detected`* (sistem menyimpulkan) — dan perbedaan itu layak menjadi
> field, bukan pilihan kata. Lihat **C-28** / [#123](../../issues/123).

---

## §18.6 — World Knowledge Graph

```
Company ── operates_in → Country      Country ── imports → Commodity
        ── produces → Product                 ── exports → Product
        ── depends_on → Supplier              ── regulates → Industry
        ── employs → Human                    ── affected_by → Event

Event ── affects → Market · Company · City
      ── potentially_affects → Human
```

> Ini memungkinkan **reasoning lintas domain**.

---

> ⭐⭐ **`potentially_affects` yang dibedakan dari `affects` adalah pengakuan
> yang benar, dan ia diletakkan tepat di tempat paling penting: relasi menuju
> `Human`.**
>
> Tiga relasi `affects` menuju pasar, perusahaan, dan kota — hal-hal yang
> dampaknya bisa diukur. Yang menuju manusia diberi kata yang lebih lemah. Itu
> bukan kebetulan, dan ia sejalan dengan prinsip pembukanya.

> 🛑🛑 **Tetapi kedua relasi itu tidak membawa tingkat bukti — padahal naskah
> ini sendiri memberi tangganya di §18.9, dan naskah 21 sudah memberinya di
> §17.9.**
>
> **E-81** ([#7](../../issues/7)) adalah butir tertua di repo ini: relasi
> `influences` kembali berulang kali tanpa bukti kausal. §17.9 **menutupnya**
> dengan empat tingkat (`Observed relationship · Correlation · Hypothesis ·
> Causal evidence`) dan aturan tegas: hanya tingkat keempat yang boleh menjadi
> dasar rekomendasi.
>
> Di sini tangga itu **tidak melekat pada tepi grafnya**. `Event → affects →
> Market` adalah satu tepi tanpa atribut; tidak ada tempat untuk menyatakan
> apakah ia teramati, terkorelasi, hipotesis, atau berbukti. Akibatnya konkret:
> **§18.10 (Global Simulation) membaca graf ini** untuk merambatkan dampak, dan
> rambatan yang tidak tahu kekuatan tepinya akan memperlakukan dugaan sama
> dengan bukti.
>
> ⭐ Perbaikannya kecil dan sudah berpreseden: **tiap tepi membawa `evidence_level`
> (§18.9), `confidence`, dan `sources`** — persis tiga hal yang §18.5 sudah
> lekatkan pada event. Yang perlu dilakukan cuma memberlakukannya pada tepi juga.
> Lihat **E-138** / [#124](../../issues/124).

> ⚠️ **`Company ── employs → Human` menaruh orang sungguhan di dalam graf
> dunia.** Enam relasi lain menghubungkan benda, negara, dan komoditas; yang ini
> menghubungkan majikan dengan pekerja. Sekali tepi itu ada, pertanyaan
> *"peristiwa apa yang memengaruhi orang ini"* bisa dijawab **oleh siapa pun
> yang bisa membaca graf** — dan §18.14 (Federated Intelligence) memang
> membagikan pola lintas simpul. Yang perlu ditulis: **graf dunia tidak memuat
> simpul orang; ia berhenti di organisasi, dan penautan ke individu terjadi di
> sisi pribadi**, tempat §17.4 dan Personal Data Vault berlaku. Itu juga
> mempertahankan bentuk **H-19** ([#62](../../issues/62)): agent tidak menarik
> data sendiri, Context Engine yang menyusunnya.
