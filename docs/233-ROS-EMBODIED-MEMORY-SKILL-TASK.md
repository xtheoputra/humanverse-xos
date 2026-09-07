# 233 — §16.22–§16.25 ROS Integration, Embodied Memory, Skill Library & Task Composer

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.22 — ROS Integration

> Gunakan **ROS2** sebagai compatibility layer. **HumanVerse tidak menggantikan
> ROS.**

```
HumanVerse → ROS Adapter → ROS2 → Robot
```

> ⚠️ Angka lepas `6` di bagian ini. Lihat **G-16** / [#113](../../issues/113).

---

> ⭐⭐⭐ **"HumanVerse tidak menggantikan ROS" adalah kalimat yang menghemat
> pekerjaan paling banyak di seluruh fase ini, dan ia yang KETIGA dari
> kebiasaan baru yang layak dicatat.**
>
> Dua puluh naskah nyaris seluruhnya merancang sendiri. Dua naskah terakhir
> berhenti melakukannya di empat tempat: SLAM (§15.6), motion planning (§16.7),
> simulator (§16.26), dan ROS2 di sini. Untuk fase dengan risiko fisik, memakai
> tumpukan yang sudah diuji ribuan orang **juga keputusan keselamatan**, bukan
> hanya penghematan.

> 🛑🛑 **Tetapi diagram ini membuka jalur yang melewati Safety Kernel — dan
> itulah bentuk fisik dari "agent tidak boleh bypass gateway" §11.14.**
>
> `HumanVerse → ROS Adapter → ROS2 → Robot` menempatkan **ROS2 lebih dekat ke
> robot daripada HumanVerse**. Artinya siapa pun yang bisa berbicara ke ROS2
> bisa menggerakkan robot **tanpa melewati** Safety Kernel §16.18, Safe Zones
> §16.19, maupun Emergency Controller §16.20 — semuanya berada di sisi
> HumanVerse dari adapter.
>
> Ini bukan kemungkinan teoretis. Lapisan komunikasi ROS2 pada konfigurasi
> bawaan menerima peserta baru di jaringan yang sama tanpa autentikasi kuat;
> perangkat keras robot umumnya juga membawa pengendali dan alat diagnostik
> pabrikan yang berbicara langsung ke lapisan itu. Sebuah rumah dengan robot
> berarti simpul ROS di jaringan rumah.
>
> Tiga hal yang perlu ditulis, dan ketiganya satu baris:
>
> 1. **Safety Kernel berjalan DI BAWAH adapter**, di sisi robot — bukan di sisi
>    HumanVerse. Perintah gerak apa pun, dari mana pun, melewatinya.
> 2. **ROS2 dijalankan pada domain terisolasi dengan keamanan dinyalakan**;
>    tidak ada peserta yang boleh bergabung dari jaringan umum.
> 3. **Emergency Stop tidak boleh berupa pesan ROS biasa** — ia harus punya
>    jalur yang tidak bisa didahului oleh lalu lintas lain.
>
> Lihat **B-32** / [#110](../../issues/110).

---

## §16.23 — Embodied Memory

> Robot **mengingat pengalaman.**

```
Task:      Open Door
Attempt 1  Success
Attempt 2  Handle slippery
Future     Adjust force
```

> Ini menjadi **Procedural Memory.**

---

> ⭐⭐ **Menyambungkannya ke `Procedural Memory` yang sudah ada adalah pilihan
> yang tepat, dan itu jarang terjadi di repo ini.** Enam jenis memory **H-16**
> (working · episodic · semantic · procedural · behavioral · preference)
> ditetapkan di naskah 5 §17 dan diulang tanpa berubah di §9.7. `Procedural` —
> *cara melakukan sesuatu* — adalah tempat yang benar untuk pengalaman motorik,
> dan naskah ini memakainya alih-alih membuat jenis ketujuh. Setelah lima
> hitungan memory yang berbeda-beda, itu layak dicatat.

> 🛑 **Tetapi baris `Future: Adjust force` adalah sistem yang menulis parameter
> KESELAMATAN FISIK untuk dirinya sendiri.**
>
> §14.49 sudah memperkenalkan bentuk ini pada Agent Team Memory (*"Known issue:
> Analyst terlalu mahal → Future: use cheaper Analyst"*), dan saya catat waktu
> itu bahwa **`Future` adalah usul sampai disetujui, bukan setelan yang sudah
> berlaku**. Di sana yang berubah adalah pilihan agent. Di sini yang berubah
> adalah **gaya yang dikeluarkan sebuah lengan mesin** — dan §16.8 tidak
> memberinya batas atas, sementara §16.20 hanya mendeteksi gaya yang **tak
> terduga**, bukan gaya yang direncanakan terlalu besar.
>
> Rangkaiannya bisa dibaca dalam tiga baris naskah ini sendiri: robot mencatat
> gagangnya licin → menyimpulkan perlu gaya lebih besar → **menaikkan gayanya
> sendiri** → gaya yang lebih besar itu kini "terduga", jadi pengaman §16.20
> tidak berbunyi.
>
> Butir **H-7** sudah memberi bentuk jawabannya untuk self-improving agent:
> simpan **metadata**, beri **rollback otomatis**. Untuk parameter fisik
> dibutuhkan satu lagi: **batas keras yang tidak bisa dinaikkan oleh
> pembelajaran** — pembelajaran boleh bergerak di dalam pagar, tidak boleh
> memindahkan pagarnya.

> ⚠️ **`Attempt 2: Handle slippery` juga sebuah kesimpulan, bukan pengamatan.**
> Yang diamati adalah *genggaman gagal*; *gagang licin* adalah salah satu dari
> beberapa sebab (tangan salah posisi, pintu terkunci, gaya kurang). Tangga
> **`Observed ≠ Predicted ≠ Simulated ≠ Certain`** (naskah 16) berlaku persis di
> sini, dan memori prosedural yang menyimpan sebab yang salah akan mengulang
> koreksi yang salah setiap kali.

---

## §16.24 — Skill Library

Reusable skills: **Pick · Place · Push · Pull · Open · Close · Carry ·
Navigate · Follow · Wait**

```
Goal → Skill Composition → Execution
```

---

> ⭐⭐⭐ **`Wait` sebagai skill yang setara dengan `Pick` dan `Carry` adalah
> detail kecil yang menyatakan sikap keselamatan seluruh fase ini.**
>
> Pustaka keterampilan biasanya berisi hal yang **dilakukan** robot. Menaruh
> *menunggu* di dalamnya berarti tidak melakukan apa-apa adalah tindakan yang
> bisa dipilih, direncanakan, dan disusun — bukan kegagalan merencanakan. Itu
> sejalan dengan `Robot slows → Wait` (§16.11), `Stop?` sebagai keluaran yang
> setara (§14.63), dan degradasi yang berakhir di diam (§14.35).

> ⭐ **Sepuluh keterampilan, semuanya kata kerja fisik yang bisa diuji** — dan
> itu membuat §16.26 (*simulation-first*) bisa dijalankan: tiap skill punya
> kriteria berhasil yang bisa diperagakan di simulator.

> ⚠️ **Tidak ada skill untuk MEMBATALKAN.** `Open`/`Close` dan `Pick`/`Place`
> berpasangan, tetapi tidak ada `Undo`, `Release`, atau `Return`. §16.3
> menyebut `robot.release(...)` di antarmuka; ia tidak muncul di pustaka
> keterampilan. Untuk fase yang menyentuh benda milik orang, **kemampuan
> mengembalikan keadaan** adalah keterampilan tersendiri — dan **H-21**
> mendefinisikan R4 sebagai *irreversible*, yang berarti keterbalikan adalah
> besaran yang dipakai gerbang, bukan kenyamanan.

> ⚠️ **`Follow` mewarisi keberatan §16.5**: berguna dan menakutkan dengan kode
> yang sama, dan yang membedakan hanya siapa yang bisa menghentikannya.

---

## §16.25 — Task Composer

> Task kompleks dibangun dari skill.

```
"Bring me coffee"
Navigate → Find Cup → Grasp → Carry → Deliver
```

---

> ⭐⭐ **Komposisi dari keterampilan yang sudah teruji adalah cara paling aman
> menyusun perilaku baru**, karena tiap bagiannya sudah lulus §16.26 sebelum
> digabung. Ia juga bentuk yang sama dengan `Skill Composition` §16.24 dan
> dengan `Task Decomposition` §14.46 — satu pola yang kini dipakai konsisten di
> tiga fase.

> ⚠️ **Tapi `Find Cup` dan `Deliver` bukan skill di §16.24.** Sepuluh skill di
> sana adalah `Pick · Place · Push · Pull · Open · Close · Carry · Navigate ·
> Follow · Wait`; rantai ini memakai dua kata kerja yang tidak ada di daftar.
>
> Kalau `Find` dan `Deliver` adalah komposisi lagi (`Navigate` + `observe`;
> `Navigate` + `Place`), sebaiknya ditulis begitu — karena seluruh nilai pustaka
> keterampilan terletak pada **daftarnya tertutup**. Ini pola **G-14**
> (*didaftarkan lengkap, dipakai sebagian lain*) yang muncul untuk ketiga
> kalinya dalam tiga naskah.

> 🛑 **Dan `Deliver` ke seseorang adalah tindakan pertama di fase ini yang
> menyentuh orang secara langsung.** Menyerahkan cangkir berisi cairan panas ke
> tangan manusia menuntut deteksi tangan, batas gaya, dan pelepasan yang tepat
> waktu — tiga hal yang tidak punya angka di naskah ini (**A-32** /
> [#112](../../issues/112)), dan yang §16.18 lewati tanpa `Confirmation`.
>
> Contoh yang dipilih naskah ini — *"Bring me coffee"* — karena itu justru
> contoh yang paling menuntut: ia berakhir dengan robot yang menyentuh
> penggunanya sambil membawa sesuatu yang bisa melukai.
