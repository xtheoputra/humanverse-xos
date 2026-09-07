# 231 — §16.13–§16.17 Smart Home, IoT Mesh, Drone, Fleet Management & Multi-Robot Coordination

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.13 — Smart Home Intelligence

> HumanVerse menjadi **pusat rumah pintar.**

Perangkat: **lampu · AC · TV · pintu · kamera · speaker · vacuum · sensor.**

```
Intent → Home Policy → Permission → Device
```

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16** / [#113](../../issues/113).

---

> ⭐ **Rantai ini punya `Home Policy` SEBELUM `Permission`, dan urutan itu
> benar.** Kebijakan rumah membatasi apa yang boleh ada sama sekali; izin
> membatasi siapa yang boleh melakukannya. Yang pertama tidak bisa dicabut oleh
> yang kedua — sejalan dengan §14.44 (governance di luar jalur kepentingan).

> 🛑 **Tetapi `pintu` berdiri di daftar yang sama dengan `lampu`, dan rantainya
> tidak punya `Risk` maupun `Confirmation`.**
>
> Delapan perangkat itu tidak sekelas:
>
> | Perangkat | Kalau salah |
> |---|---|
> | lampu · AC · TV · speaker | menjengkelkan, batal dalam satu ketukan |
> | vacuum · sensor | menjengkelkan |
> | **kamera** | menyalakan pemantauan di ruangan yang policy-nya mematikannya (**C-23**) |
> | **pintu** | **membuka kunci rumah** — dan itu tidak bisa dibatalkan setelah seseorang masuk |
>
> **H-15** menetapkan konfirmasi manusia wajib mulai **R3**; **H-21**
> mendefinisikan **R4 = `DENY` bawaan, irreversible**. Membuka kunci pintu
> adalah kandidat R4 yang paling jelas di seluruh dua puluh naskah — dan rantai
> §16.13 melewatkannya dengan `Permission` saja.
>
> Ini rantai **ketujuh** yang berakhir di tindakan tanpa `Risk` maupun
> `Confirmation`. Lihat **E-130** / [#111](../../issues/111).

---

## §16.14 — IoT Mesh

```
HumanOS → Edge Hub → IoT Mesh
                      ├── Light   ├── Camera
                      ├── Lock    ├── Sensor
                      └── Speaker
```

Protokol: **MQTT · Matter · Zigbee · Thread · BLE**

---

> ⭐⭐ **`Edge Hub` sebagai satu-satunya jalan menuju IoT Mesh adalah bentuk yang
> benar, dan ia mengulang pola yang sudah tiga kali dipakai dengan tepat di repo
> ini:** Context Engine §9.31 (agent tidak mengambil data sendiri), Action
> Gateway §11.14 (agent tidak memanggil tool sendiri), Robot Interface §16.3.
> Satu pintu berarti satu tempat memasang aturan — dan §16.21 menaruh pintu itu
> di **edge**, sehingga ia tetap bekerja ketika jaringan putus.

> ⭐ **Lima protokol nyata, bukan protokol karangan sendiri** — naskah kedua
> berturut-turut yang memakai yang sudah ada (§15.6, §16.7, §16.22, §16.26).
> ⚠️ Yang perlu menyusul: **pilih satu sebagai jalur utama.** Matter dan Zigbee
> punya model keamanan dan proses onboarding yang sangat berbeda; mendukung
> lima berarti membangun lima jalur kepercayaan.

> 🛑 **`Lock` muncul lagi di sini, di daftar yang sama dengan `Light`.** Ini
> kedua kalinya dalam dua bagian berurutan bahwa kunci pintu diperlakukan
> sebagai perangkat biasa. Yang perlu ditulis satu baris, dan bahannya sudah
> ada sejak §8.16: **tiap perangkat IoT membawa `risk_level`** — sehingga
> `Light` R0 dan `Lock` R4 lewat gerbang yang sama tetapi tidak berakhir sama.

---

## §16.15 — Drone Intelligence

Kemampuan: **inspection · mapping · search · delivery ringan · monitoring.**

```
Mission → Flight Plan → Obstacle Check → Execution → Landing
```

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16**.

---

> ⭐ **Rantai ini satu-satunya di naskah yang berakhir di keadaan aman
> (`Landing`), bukan di `Execute`.** Untuk benda terbang itu benar dan penting:
> drone yang berhenti tidak diam di tempat, ia jatuh — jadi rencana yang tidak
> memuat pendaratan adalah rencana yang tidak selesai.

> 🛑 **Tetapi drone adalah satu-satunya dari delapan tubuh §16.1 yang diatur
> hukum penerbangan, dan naskah tidak menyebutnya sama sekali.**
>
> Di hampir semua yurisdiksi: pendaftaran perangkat, batas ketinggian, larangan
> terbang di atas orang, zona larangan di sekitar bandara dan fasilitas
> tertentu, dan aturan **siapa yang boleh menjadi pilot bertanggung jawab**.
> Yang terakhir itu berbenturan langsung dengan seluruh gagasan Phase 16:
> penerbangan otonom umumnya tetap menuntut **orang yang bertanggung jawab**,
> dan sistem tidak bisa menjadi orang itu.
>
> Ditambah `monitoring` dan `inspection` sebagai kemampuan: drone yang memantau
> di luar batas properti adalah **C-22** ([#102](../../issues/102)) dalam bentuk
> yang bahkan tidak butuh menembus dinding. Lihat **C-24** /
> [#114](../../issues/114).

> ⚠️ **`Obstacle Check` sekali, di depan.** §16.7 dan §16.11 memeriksa terus
> selama gerakan; rantai ini memeriksa saat merencanakan. Untuk benda yang
> bergerak cepat di ruang terbuka, rintangan yang muncul setelah rencana disusun
> justru kasus yang biasa.

---

## §16.16–§16.17 — Fleet Management & Multi-Robot Coordination

Dashboard: **battery · tasks · locations · health · utilization.**

```
Task → Coordinator → Robot A / Robot B / Robot C
```

Pembagian tugas: **transport · lifting · inspection · cleaning.**

> ⚠️ Angka lepas `6` di §16.16. Lihat **G-16**.

---

> 🛑 **`lifting` oleh beberapa robot bersama adalah §14.31 dalam bentuk fisik —
> dan ini kelas bahaya yang tidak bisa dilihat oleh pemeriksa mana pun yang
> menilai satu robot pada satu waktu.**
>
> §14.31 memperagakannya dengan izin: agent A yang hanya boleh **membaca** dan
> agent B yang hanya boleh **menulis** menghasilkan eksfiltrasi, meski keduanya
> lolos gerbangnya masing-masing. §14.40 mengulanginya dengan uang. Di sini ia
> menjadi beban: dua robot yang masing-masing mengangkat setengah beban aman
> **berhenti aman kalau salah satunya melepas**, dan tidak ada Safety Kernel
> per-robot yang melihat itu.
>
> Naskah 18 sudah menyediakan namanya (*Cross-Agent Security*, §14.31) dan
> hukumnya (**§14.64**: *"more agents must not automatically mean more
> autonomy"*, karena `collective risk > individual risk`). Yang belum ada di
> sini: **`Coordinator` tidak punya Safety Kernel sendiri.** §16.18 memasang
> kernel pada `Action`, yaitu per robot; tindakan bersama tidak punya tempat
> diperiksa.
>
> Ini juga alasan **B-29** ([#96](../../issues/96)) berlaku di sini: `utilization`
> di dasbor §16.16 adalah metrik yang **naik ketika robot lebih sibuk**, dan
> keselamatan tidak muncul di daftar lima metrik itu sama sekali.

> ⭐ **`health` di dasbor adalah satu-satunya metrik yang menunjuk ke pemeliharaan
> alih-alih ke keluaran**, dan ia yang membuat Digital Twin robot §16.4 punya
> pembaca. ⚠️ Tapi `battery` juga soal keselamatan, bukan hanya soal ketersediaan:
> §16.20 mendaftarkan `communication loss` sebagai pemicu darurat dan **tidak
> mendaftarkan baterai habis** — padahal lengan yang kehabisan daya saat
> mengangkat sesuatu melepaskannya.
