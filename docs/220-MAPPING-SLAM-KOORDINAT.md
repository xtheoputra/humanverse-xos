# 220 — §15.5–§15.7 Spatial Mapping, SLAM & Spatial Coordinate System

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan belas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §15.5 — Spatial Mapping Engine

> Tujuan: **membuat Digital Twin ruang.**

```
Living Room
├── Sofa
├── Table
├── TV
├── Lamp
└── Person
```

Semua memiliki koordinat 3D.

```json
{
  "id": "obj_table",
  "position": [1.2, 0.8, 0.4],
  "rotation": [0, 90, 0],
  "confidence": 0.94
}
```

---

> ⭐⭐⭐ **`confidence: 0.94` ada di objek pertama yang pernah ditunjukkan fase
> ini — dan itu bukan kebetulan, itu kebiasaan yang sudah lima naskah.**
>
> **H-14** menetapkan tiap taksiran membawa `confidence`; §12.13 menambahkan
> rentang; §14.62 akhirnya memberi ambang pertamanya (`< 0.6`). Di sini ia
> muncul pada benda fisik tanpa diminta. Untuk fitur "di mana dompet saya",
> `confidence` adalah bedanya antara panah AR dan tebakan.

> 🛑 **Tapi `Person` berdiri di dalam daftar yang sama dengan `Sofa`, `Table`,
> dan `Lamp` — dan itu bukan detail penulisan.**
>
> Seluruh sisa naskah memperlakukan keduanya sebagai satu jenis: §15.9 memberi
> `Object lifecycle` yang berakhir di `Archived`, §15.11 memberi relasi
> `ON`/`INSIDE`/`BEHIND` tanpa membedakan, §15.27 memberi `objects` dan
> `people_tracks` sebagai dua tabel tetapi §15.5 menggabungkannya dalam satu
> pohon.
>
> Perbedaannya bukan filosofis, melainkan **operasional**: sofa tidak punya hak
> hapus (**C-9** / [#22](../../issues/22)), tidak bisa menarik persetujuan
> (§8.9), tidak bisa menjadi *bystander* (**C-10** / [#40](../../issues/40)),
> dan tidak peduli disimpan selamanya. Manusia ketiganya. Satu kalimat
> menutupnya: **`Person` bukan `Object`; ia simpul dengan aturan penyimpanan,
> retensi, dan penghapusan sendiri.**

---

## §15.6 — SLAM Engine

> Gunakan konsep: **Simultaneous Localization and Mapping**

```
Camera + IMU + LiDAR → Visual-Inertial SLAM → 3D Map → Device Localization
```

Bisa menggunakan: **ARKit · ARCore · OpenVSLAM · ORB-SLAM3 · RTAB-Map**.

---

> ⭐⭐⭐ **Ini pertama kalinya dalam sembilan belas naskah sebuah bagian
> menyebut PUSTAKA YANG SUDAH ADA alih-alih merancang komponen baru.**
>
> Lima nama, semuanya nyata, dua di antaranya milik platform (ARKit/ARCore) dan
> tiga sumber terbuka. Bandingkan dengan pola yang berulang di naskah-naskah
> sebelumnya, tempat setiap kemampuan mendapat kotaknya sendiri di dalam
> arsitektur. SLAM adalah bidang berumur tiga dekade dengan implementasi matang;
> menuliskannya sebagai **pilihan pustaka**, bukan sebagai modul yang akan
> ditulis sendiri, adalah keputusan yang menghemat pekerjaan paling banyak di
> seluruh fase ini.
>
> ⚠️ Yang perlu menyusul: **pilih satu**, dan catat alasannya. Kelimanya punya
> lisensi, kebutuhan sensor, dan sifat yang sangat berbeda — ARKit/ARCore
> mengunci ke platform dan tidak berjalan di server; ORB-SLAM3 dan OpenVSLAM
> punya riwayat lisensi yang perlu diperiksa sebelum dipakai di produk berbayar.
> Ini keputusan yang bentuknya ADR, dan `docs/decisions/` sudah ada tempatnya
> (**H-10**).

> ⚠️ **`Camera + IMU + LiDAR` di sini vs delapan sensor §15.3.** SLAM memakai
> tiga; `Sensor Fusion` memakai delapan. Keduanya masuk akal — SLAM punya
> kebutuhan sendiri — tetapi hubungan keduanya tidak ditulis: apakah SLAM
> **bagian dari** Sensor Fusion, atau **konsumen** hasilnya? §15.2 menaruh
> `Sensor Fusion → Localization → Mapping` sebagai tiga langkah berurutan, yang
> menyiratkan SLAM ada di dua langkah terakhir; §15.6 menggambarkannya sebagai
> jalur sendiri langsung dari sensor. Satu kalimat cukup.

> ⚠️ Naskah menaruh angka lepas **`6`** di bagian ini dan di §15.5. Lihat
> **G-15** / [#103](../../issues/103).

---

## §15.7 — Spatial Coordinate System

> Gunakan **unified coordinate**.

```
Global → Building → Floor → Room → Object
```

```yaml
building:
  id: home
room:
  id: living_room
object:
  id: table
position:
  x: 1.2
  y: 0.8
  z: 0.4
```

> Ini memudahkan semua agent berbicara tentang lokasi.

---

> ⭐⭐⭐ **Kalimat penutupnya menyebut alasan yang benar, dan ia alasan
> arsitektur, bukan kenyamanan.**
>
> Sistem koordinat bersama adalah **kosakata**, dan tanpa kosakata bersama
> setiap agent akan menemukan miliknya sendiri — persis pola yang sudah terjadi
> lima kali di repo ini (**lima skema penomoran bertabrakan**, tiga arti
> "HumanOS", empat makna "sandbox", tiga arti "KILL"). Menetapkannya **sebelum**
> ada agent spasial yang menulis kode adalah cara termurah untuk tidak
> mengulanginya, dan §15.21 baru akan memperkenalkan enam agent baru.

> ⚠️ **Tapi hierarki lima tingkat itu melewatkan tingkat yang paling dibutuhkan
> fitur unggulannya sendiri: WAKTU.**
>
> Pertanyaan pembuka fase ini adalah *"di mana saya meletakkan dompet
> **kemarin**"*, dan §15.8 menjawab *"sekitar pukul 22:15 kemarin"*. Sebuah
> koordinat tanpa cap waktu tidak bisa menjawab itu — dan contoh YAML di atas
> tidak punya satu pun field waktu, sementara §15.9 `object state` punya
> `last_seen` dan §15.27 punya tabel `object_history` dan `object_locations`.
>
> Artinya jawabannya ada, tetapi **bukan di sistem koordinat** — dan karena
> §15.7 adalah bagian yang menetapkan kosakata bersama, ketiadaan waktu di
> sinilah yang akan membuat tiap agent menemukan caranya sendiri. Yang
> dibutuhkan satu baris: **koordinat selalu berpasangan dengan `timestamp` dan
> `confidence`** — keduanya sudah ada di tempat lain, tinggal dinaikkan ke
> definisi.

> ⚠️ **`Global → Building → Floor → Room` mengasumsikan bangunan.** Contoh
> pemakaian di luar ruangan (§15.12 mendaftarkan GPS dengan target 3–10 m) tidak
> punya `Building` maupun `Room`. Bukan kesalahan — tapi aturan untuk simpul
> yang kosong perlu ditulis, karena kalau tidak, tiap agent akan memilih
> penanda kosongnya sendiri.
