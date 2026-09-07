# 200 — Life Graph, Capability & Permission Layer (naskah ketujuhbelas)

> Merekam **§13.8–§13.10**.
> 🛑 **Berkas ini memuat temuan terberat dari naskah ketujuh belas.** Lihat
> catatan di §13.10.

---

## §13.8 — Life Graph

> Ini akan menjadi salah satu fitur paling unik.

Seluruh aspek kehidupan direpresentasikan sebagai graph:

```
                     HUMAN
                       │
       ┌───────────────┼───────────────┐
       │               │               │
     HEALTH          CAREER          FINANCE
       │               │               │
     ENERGY          SKILLS          CAPITAL
       │               │               │
       └───────────────┼───────────────┘
                       │
                     GOALS
                       │
                    PROJECTS
                       │
                     TASKS
                       │
                    ACTIONS
                       │
                    OUTCOMES
```

Kemudian:

```
Life Graph
     +
Digital Twin
     +
World Model
```

menjadi **Personal Life Model**.

> 🛑 **Graf ketiga untuk benda yang sama, dan model graf adalah salah satu dari
> empat butir yang masih MENGUNCI Engineering Spec.** **E-16..E-18** menanyakan
> model graf mana yang berlaku; sekarang ada *Human Knowledge Graph* (naskah
> awal), *Personal Skill Graph* (§13.7), dan *Life Graph* (§13.8) — ditambah
> *Personal Life Model* sebagai gabungan tiga benda lain.
>
> Yang membuat butir ini mendesak: skema basis data tidak bisa ditulis sampai
> ada satu jawaban. Naskah ini menambah simpul, bukan menutup pertanyaan.

> ⚠️ **`ENERGY` muncul sebagai simpul graf, dan §13.15 memberinya anggaran
> berangka.** **A-19** mencatat kini ada **lima** model angka pengguna dan tak
> satu pun berumus; energi dengan anggaran harian 100 (§13.15) menjadikannya
> **enam**, dan ia juga tanpa rumus. A-19 termasuk empat butir yang mengunci
> Engineering Spec.

---

## §13.9 — Personal Capability System

HumanOS harus mengetahui: *"Apa yang bisa dilakukan AI ini?"*

```yaml
capability:
  id:
  name:
  description:
  risk_level:
  required_permissions:
  required_tools:
  allowed_agents:
```

Contoh:

```
calendar.read
calendar.create
calendar.modify

email.read
email.draft
email.send

shopping.search
shopping.prepare

device.read
device.control
```

> ⭐⭐ **`shopping` berhenti di `prepare`, dan tidak ada `shopping.purchase`.**
> Itu persis tangga L: **L2 Prepare** boleh, eksekusi tidak. Daftar contoh ini
> menegakkan batas yang benar tanpa menyebut tangganya — pengaman yang terpasang
> di data, bukan di prosa.
>
> ⚠️ Tetapi `email.send` **ada**, dan `device.control` **ada**. Keduanya melewati
> `prepare`. Kalau `shopping` sengaja berhenti di `prepare`, dua yang lain
> seharusnya punya alasan tertulis kenapa tidak.

> ⚠️ **`capability` tidak punya `purpose`.** Objek ini menentukan apa yang boleh
> dilakukan dan oleh agent mana (`allowed_agents`), jadi ia berada persis di
> jalur yang §8 minta bisa diaudit *untuk keperluan apa*.

---

## §13.10 — HumanOS Permission Layer

User bisa mengatur:

| Kemampuan | Setelan di naskah |
|---|---|
| AI dapat melihat kalender | ✓ |
| AI dapat membuat jadwal | ✓ |
| AI dapat mengirim email | ✗ |
| **AI dapat membeli sesuatu** | **Ask Every Time** |
| **AI dapat mengontrol device** | **Ask Every Time** |

Jadi:

```
Capability
    ↓
Permission
    ↓
Policy
    ↓
Risk
    ↓
Action
```

> 🛑🛑🛑 **PENGAMAN NASKAH 15 TERGERUS — "Ask Every Time" untuk pembelian
> membatalkan dua batas sekaligus.**
>
> Ini temuan terberat naskah ketujuh belas, dan ia berada di **layar izin** —
> yaitu satu-satunya tempat yang benar-benar dilihat dan disetel pengguna.
>
> **Batas pertama yang dibatalkan — R4 = DENY.** §11.15 (naskah 15) menaikkan
> tingkat tertinggi dari *"wajib konfirmasi"* menjadi **`DENY`**, dan mengubah
> definisinya dari *"berdampak besar"* menjadi **`irreversible`**. Catatan
> naskah itu eksplisit:
>
> > *"Di sini tingkat tertinggi **tidak bisa dikonfirmasi** — ia ditolak, dan
> > menaikkannya harus jadi tindakan tersendiri."*
>
> *"Ask Every Time"* adalah **tepat konstruksi yang ditolak §11.15**: ia
> mengembalikan tingkat tertinggi menjadi sesuatu yang bisa dilewati dengan satu
> ketukan. Pembelian dan kontrol perangkat adalah dua contoh paling jelas dari
> *irreversible* dan *high safety impact* — keduanya definisi R4.
>
> **Batas kedua yang dibatalkan — `amount_limit: 0`.** §11.17 memberi
> `purchases: { amount_limit: 0 }` sebagai **bawaan**. Nol berarti *tidak ada
> pembelian sama sekali* sampai pengguna menaikkannya secara sadar. Layar izin
> §13.10 tidak memuat satu angka pun — hanya ✓ / ✗ / *Ask Every Time*. Bawaan
> "nol" tidak punya tempat untuk dinyatakan, sehingga pengguna yang memilih
> *"Ask Every Time"* mengira ia sudah membatasi, padahal ia baru saja
> **menghapus batas nominal**.
>
> **Kenapa ini kelas yang berbeda dari empat penggerusan sebelumnya:** yang
> sebelumnya terjadi di dokumen arsitektur, dan bisa diperbaiki dengan menulis
> ulang satu bagian. Yang ini adalah **kontrak dengan pengguna**. Begitu layar
> ini dibangun, ia menjadi apa yang orang percayai tentang sistemnya.
>
> Yang minimum harus diputuskan sebelum satu baris kode: apakah **R4 tetap
> `DENY`** dan layar izin hanya boleh menampilkan tingkat sampai R3 — atau
> §11.15 dicabut dan alasannya ditulis. Dua-duanya sah; yang tidak sah adalah
> membiarkan keduanya berdiri.

> ⚠️ **Urutan rantainya terbalik dari naskah 15.** §13.10 menulis
> `Capability → Permission → Policy → Risk → Action`; §11.37 menempatkan **policy
> sebagai gerbang terakhir sebelum eksekusi**, sesudah risiko dinilai. Di sini
> `Risk` justru berada **sesudah** `Policy`, sehingga kebijakan diputuskan
> sebelum risikonya diketahui. Kemungkinan besar ini urutan penulisan, bukan
> urutan eksekusi — tapi rantai lima kotak seperti ini akan disalin apa adanya
> ke kode.

> ⭐ **`email.send` diberi ✗ sebagai bawaan.** Itu konsisten dengan R3
> (*important communication* → konfirmasi manusia) dan lebih ketat, karena ✗
> berarti mati sama sekali. Layar ini karena itu **tidak seragam arahnya**: satu
> baris lebih ketat dari tangga R, dua baris lebih longgar. Ketidakseragaman itu
> sendiri petunjuk bahwa layar ini disusun dari intuisi, bukan diturunkan dari
> §11.15.
