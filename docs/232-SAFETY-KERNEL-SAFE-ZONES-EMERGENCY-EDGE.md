# 232 — §16.18–§16.21 Robot Safety Kernel, Safe Zones, Emergency Controller & Edge AI Runtime

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §16.18 — Robot Safety Kernel

> Ini adalah komponen **paling kritis.**

```
Action → Safety Kernel → Collision → Human Detection → Emergency Rules
→ Execute
```

> **Emergency Stop memiliki prioritas tertinggi.**

---

> ⭐⭐ **Menyebutnya "kernel" tepat, dan menyatakan Emergency Stop berprioritas
> tertinggi adalah pernyataan yang bisa ditegakkan.** Ia berarti tidak ada
> lapisan di atasnya yang boleh menunda, membujuk, atau menimbang ulang —
> sejajar dengan **R4 = `DENY` bawaan** (**H-21**) dan dengan *"agent tidak
> boleh bypass gateway"* §11.14.

> 🛑🛑 **Tetapi rantai ini tetap tidak punya `Risk` maupun `Confirmation` —
> dan kata "risk" TIDAK MUNCUL SATU KALI PUN di seluruh naskah kedua puluh.**
>
> Bandingkan empat rantai yang sudah ada:
>
> | Rantai | Gerbang |
> |---|---|
> | §11.14 Action Gateway | **9**, termasuk `Risk`, `Consent`, `Rate Limit`, **`Confirmation`** |
> | §14.20 Agent Security Mesh | **11**, kehilangan `Consent`, `Rate Limit`, `Confirmation` (**E-117**) |
> | §15.22 Spatial Safety | **5**, punya `Permission`, tanpa `Risk`/`Confirmation` (**E-124**) |
> | **§16.18 Robot Safety Kernel** | **5**, punya `Emergency Rules`, **tanpa `Risk`, `Confirmation`, maupun `Permission`** |
>
> Butir **E-124** ([#106](../../issues/106)) memperkirakan ini satu naskah lalu:
> *"rantai keselamatan tanpa `Risk` yang diwarisi benda bergerak adalah
> kesalahan yang mahal diperbaiki setelah ada perangkat kerasnya."* Naskah ini
> mewarisinya utuh, dan **membuang `Permission` juga**.
>
> ⭐ Yang **ditambahkan** naskah ini nyata dan berharga: `Emergency Rules`
> ditambah mesin keadaan §16.20 memberi HumanVerse **pengaman reaktif pertama**
> di dua puluh naskah — sesuatu yang menghentikan tindakan **yang sedang
> berlangsung**. Semua pengaman sebelumnya berjalan sebelum tindakan dimulai.
>
> Tetapi reaktif bukan pengganti preventif. `Emergency Rules` menjawab *"ada
> yang salah, hentikan"*; `Risk` dan `Confirmation` menjawab *"ini tidak boleh
> dimulai tanpa orangnya tahu"* — dan untuk aksi tak-terbalikkan (membuka kunci
> §16.13, mengangkat benda di atas seseorang, drone lepas landas) yang kedua
> yang menentukan. Lihat **E-130** / [#111](../../issues/111).

---

## §16.19 — Safe Zones

```yaml
kitchen:
  speed: slow

stairs:
  autonomous: false

child_room:
  restricted: true
```

> Robot mengikuti **policy lokasi.**

---

> ⭐⭐⭐ **Ini bentuk yang BENAR dari policy ruangan — dan ia memperbaiki cacat
> §15.23 tanpa diminta.**
>
> Butir **C-23** ([#104](../../issues/104)) mencatat bahwa `bedroom: {camera:
> false, audio: false}` adalah daftar **perangkat**, sehingga setiap sensor baru
> otomatis diizinkan sampai ada yang ingat menambahkannya — dan WiFi sensing
> yang menembus dinding lolos begitu saja.
>
> §16.19 menulis **kemampuan**, bukan perangkat: `speed`, `autonomous`,
> `restricted`. Ketiganya berlaku pada robot mana pun, yang sudah ada maupun
> yang belum dibuat. Itu persis bentuk yang C-23 usulkan, muncul satu naskah
> kemudian di tempat yang berbeda.
>
> ⭐ Dan ketiganya berjenjang dengan baik: `speed: slow` membatasi **cara**,
> `autonomous: false` membatasi **siapa yang memutuskan**, `restricted: true`
> membatasi **keberadaan**. Tiga tingkat pembatasan, bukan satu sakelar.

> ⚠️ **Tetapi bentuknya masih daftar IZIN yang disebutkan, bukan default deny.**
> Ruangan yang tidak terdaftar tidak punya batasan sama sekali — dan sebuah
> rumah punya lebih banyak ruangan daripada yang akan ditulis orang. Usul C-23
> tetap berlaku: **apa pun yang tidak disebut ditolak**, atau setidaknya
> mewarisi bawaan yang ketat.

> ⚠️ **`autonomous: false` tidak menyatakan apa yang terjadi sebagai
> gantinya.** Robot berhenti di kaki tangga, menunggu manusia, atau menolak
> tugasnya? Untuk tangga jawabannya menentukan keselamatan, dan ia satu-satunya
> nilai di blok ini yang tidak bisa disimpulkan.
>
> ⚠️ Dan **`child_room: restricted: true` adalah aturan perangkat lunak yang
> harus bertahan terhadap §16.5 — humanoid yang bisa MEMBUKA PINTU.** Perbedaan
> antara *"robot tidak diizinkan masuk"* dan *"robot tidak bisa masuk"* adalah
> perbedaan antara aturan di perencana dan penolakan di pengendali gerak, dan
> hanya yang kedua bertahan ketika perangkat lunaknya salah.
>
> ⚠️ **Siapa yang menulis blok ini** tetap tidak dijawab — **A-31**
> ([#105](../../issues/105)) dalam bentuk yang lebih tajam, karena
> `child_room` menurut definisi adalah ruangan milik orang yang **tidak punya
> akun**.

---

## §16.20 — Emergency Controller

```
NORMAL → WARNING → STOP → RECOVERY → RESUME
```

Trigger: **human too close · unexpected force · sensor failure ·
communication loss.**

---

> ⭐⭐⭐ **Mesin keadaan ini adalah pengaman terbaik yang pernah masuk ke
> HumanVerse, dan alasannya bukan isinya melainkan BENTUKNYA.**
>
> Butir **F** sudah mencatat prinsip yang sama untuk §13.36: *sebuah state
> machine tidak bisa "lupa" melewati state*. Di sini ia dipakai pada hal yang
> paling membutuhkannya. Dan `RECOVERY` sebagai keadaan tersendiri sebelum
> `RESUME` berarti **berhenti tidak otomatis berarti boleh jalan lagi** — pola
> yang sama dengan `QUARANTINE → FORENSICS → EVALUATION → RESTORE` (§14.29).

> ⭐⭐ **`unexpected force` sebagai pemicu adalah satu-satunya tempat di naskah
> ini yang mengakui bahwa robot bisa MENYENTUH sesuatu yang tidak seharusnya.**
> Ia juga jawaban parsial untuk keberatan §16.8 (`force` tanpa batas atas):
> gaya yang tak terduga menghentikan gerakan. ⚠️ Tapi *"tak terduga"* adalah
> perbandingan terhadap perkiraan, bukan terhadap batas keselamatan — sebuah
> genggaman yang **direncanakan** terlalu kuat tidak pernah tak terduga.
> Keduanya dibutuhkan: batas mutlak **dan** deteksi kejutan.

> ⚠️ **`battery depleted` tidak ada di daftar pemicu**, padahal §16.16
> menampilkan `battery` di dasbor. Lengan yang kehabisan daya saat mengangkat
> melepaskan bebannya — itu kegagalan yang bisa diperkirakan dan karenanya bisa
> dicegah, tidak seperti tiga pemicu lainnya.
>
> ⚠️ **`STOP` tidak berarti hal yang sama untuk lima jenis lokomosi §16.6.**
> Robot beroda yang berhenti diam; humanoid yang berhenti bisa jatuh; **drone
> yang berhenti jatuh**. Mesin keadaan satu jalur tidak bisa menjadi ketiganya,
> dan §16.15 sudah menunjukkan jawabannya untuk drone: rantainya berakhir di
> `Landing`.

---

## §16.21 — Edge AI Runtime

> Sebagian besar kontrol robot harus berjalan di **edge.**

```
Robot → Edge AI → Cloud
```

**Edge:** motion · obstacle · **emergency**
**Cloud:** reasoning · planning kompleks · learning

---

> ⭐⭐⭐ **Menaruh `emergency` di edge adalah keputusan arsitektur yang paling
> penting di seluruh naskah ini, dan ia konsisten dengan pemicunya sendiri.**
>
> §16.20 mendaftarkan **`communication loss`** sebagai pemicu darurat. Sebuah
> pengaman darurat yang berjalan di cloud akan **mati justru pada pemicunya
> sendiri** — putus jaringan berarti kehilangan kemampuan berhenti pada saat
> yang sama ia dibutuhkan. Menaruhnya di edge menutup lingkaran itu.
>
> Ini juga kelanjutan langsung dari §15.29 (*"edge melakukan processing
> sensitif"*), dan bersama-sama keduanya membentuk prinsip yang pantas ditulis
> sekali untuk seluruh proyek: **apa pun yang harus tetap bekerja ketika
> segalanya gagal, berjalan di tempat yang paling dekat dengan dunia.**
>
> ⭐ Pembagiannya juga benar pada sumbu waktu: `motion` dan `obstacle` adalah
> milidetik, `reasoning` dan `learning` adalah detik sampai hari. Sumbu itu
> tidak pernah dinyatakan, tetapi pembagiannya mengikutinya dengan tepat.

> ⚠️ **Konsekuensinya belum ditulis: kalau `emergency` ada di edge, maka Safety
> Kernel §16.18 juga harus.** Naskah tidak menyatakan di mana kernel itu
> berjalan — dan kalau ia di cloud sementara pemicunya di edge, ada dua pengaman
> yang bisa tidak sepakat. Satu kalimat cukup: **Safety Kernel dan Emergency
> Controller berjalan di edge, dan robot tidak menerima perintah gerak dari
> jalur lain.**
>
> Kalimat itu sekaligus menutup lubang yang §16.22 buka: **ROS2 dapat
> memerintah robot secara langsung, di bawah adapter.** Lihat **B-32** /
> [#110](../../issues/110).
