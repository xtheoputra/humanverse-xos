# 261 — §19.16–§19.18 Research Agent Ecosystem, Multi-Agent Scientific Debate & Statistics Intelligence

> Berkas ini merekam kata pemilik apa adanya (naskah kedua puluh tiga, 8 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §19.16 — Research Agent Ecosystem

| Agent | Fungsi | | Agent | Fungsi |
|---|---|---|---|---|
| Literature | membaca paper | | Statistics | analisis |
| Citation | analisis sitasi | | Writing | drafting |
| Hypothesis | hipotesis | | **Reviewer** | **kritik** |
| Experiment | protocol | | **Ethics** | **etika** |
| Simulation | simulasi | | **Reproducibility** | **validasi** |

---

> ⭐⭐⭐ **Tiga dari sepuluh agent bertugas MEMERIKSA delapan yang lain — dan itu
> struktur yang belum pernah ada di dua puluh tiga naskah.**
>
> `Reviewer`, `Ethics`, dan `Reproducibility` tidak menghasilkan apa pun untuk
> pipeline; mereka **menolak** keluaran agent lain. Semua daftar agent
> sebelumnya di repo ini (22 agent naskah 5, dua belas §12.29 — **G-13**) berisi
> agent yang **memproduksi**: coach, habit, memory, calendar. Ini pertama
> kalinya sebuah daftar memasukkan peran yang keberhasilannya diukur dari apa
> yang **tidak** lolos.
>
> ⭐ Dan `Reproducibility Agent` sebagai peran tersendiri — bukan bagian dari
> `Reviewer` — mengakui bahwa *"apakah ini benar"* dan *"apakah ini bisa
> diulang"* adalah dua pemeriksaan berbeda, dan yang kedua bisa dijawab tanpa
> memahami isinya.

> 🛑 **Tetapi `Ethics Agent` berdiri SEDERET dengan `Writing Agent`, sementara
> §19.22 menyebut Ethics Governance *"komponen wajib"*.**
>
> Sebuah pemeriksa yang menjadi **saudara** dari yang diperiksanya bukan
> gerbang — ia peserta. Agent sejajar dipanggil ketika orkestratornya memilih
> memanggil; gerbang dilewati karena tidak ada jalan lain. Bedanya menentukan:
> pada rantai §19.2 (sepuluh langkah, tanpa satu pun gerbang), `Ethics Agent`
> tidak punya tempat yang mewajibkannya dipanggil.
>
> ⭐ Bentuk yang benar sudah ada di repo ini dan dicatat sebagai butir **F**:
> **§17.46 menaruh Safety Kernel, Risk Engine, dan Evidence Check DI DALAM
> runtime**, bukan di sampingnya — sehingga komponen yang memanggil model
> langsung tetap tidak bisa melewatinya (bandingkan **B-32**/[#110](../../issues/110),
> tempat Safety Kernel berada di sisi yang salah dari adapter ROS).
> Lihat **C-29** / [#131](../../issues/131).

> ⚠️ **Sepuluh agent baru juga menambah daftar yang sudah beberapa kali berubah
> jumlahnya** — 22 (naskah 5) · 12 (§12.29, **G-13**) · sepuluh di sini, tanpa
> ada yang menyatakan apakah ini tambahan atau daftar tersendiri. Dan §19.31
> memberi tabel `scientific_agents` **terpisah** dari registri agent yang sudah
> ada, yang berarti jawabannya sudah diambil secara diam-diam: dua daftar.

---

## §19.17 — Multi-Agent Scientific Debate

```
Hypothesis → Agent A · Agent B · Agent C → Debate
   → Consensus → Remaining Disagreement
```

> Output menunjukkan **area yang masih diperdebatkan**.

---

> ⭐⭐⭐⭐⭐ **`Remaining Disagreement` sebagai keluaran yang berdiri SESUDAH
> `Consensus` menutup separuh G-17 — dan ia persis bentuk yang diusulkan satu
> naskah lalu.**
>
> **G-17** ([#121](../../issues/121)) mencatat bahwa `consensus` (§18.32 G18.8)
> menarik berlawanan dengan `UNRESOLVED` (§18.23): keduanya memakan masukan yang
> sama — sumber yang tidak sepakat — dan yang satu **mempertahankan**
> ketidaksepakatan sementara yang lain **menghapusnya**. Usul yang ditulis di
> sana:
>
> > *"Konsensus hanya menyatukan hal yang sumbernya sepakat; ketidaksepakatan
> > naik ke pengguna sebagai ketidaksepakatan."*
>
> §19.17 melakukannya, dan lebih baik daripada usulnya: bukan memilih antara
> konsensus **atau** ketidaksepakatan, melainkan **mengeluarkan keduanya**.
> Yang disepakati bisa dipakai; yang tidak tetap terlihat. Itu bentuk yang
> membuat debat bernilai — sebab **nilai sebuah debat justru di bagian yang
> tidak selesai**, dan skema yang hanya melaporkan konsensus akan membuang
> tepat bagian itu.
>
> ⚠️ Yang perlu menyusul: **hal yang sama diberlakukan pada G18.8**, yang sampai
> sekarang hanya punya `consensus`. Bentuknya sudah ada di naskah ini; ia
> tinggal dipakai di sana.

> ⭐⭐ **Dan tiga agent, bukan dua** — jumlah yang membuat *"tidak sepakat"*
> punya bentuk yang lebih kaya daripada *"bertentangan"*. Dua agent hanya bisa
> setuju atau tidak; tiga bisa terbelah 2–1, dan pembelahan itu informasinya
> sendiri. Sejalan dengan §19.7 yang memberi `mixed evidence` sebagai status
> tersendiri.

> ⚠️ **Tetapi tidak ada yang menyatakan agent-agent itu BERBEDA dalam hal apa.**
> Debat antara tiga contoh model yang sama, dengan bobot yang sama, atas bukti
> yang sama, akan menghasilkan kesepakatan yang **tidak berarti apa-apa** — ia
> mengukur kestabilan model, bukan kekuatan bukti. §18.18 sudah menyatakan
> prinsipnya (*"bukan satu AI yang mengetahui semuanya"*, **spesialisasi
> menciptakan tempat pemeriksaan**); yang perlu di sini: **peserta debat berbeda
> pada sesuatu yang bisa disebutkan** — bukti yang berbeda, domain yang berbeda,
> atau posisi yang ditugaskan.

---

## §19.18 — Statistics Intelligence

> Fitur: `hypothesis testing · confidence intervals · **effect size** ·
> Bayesian inference · regression · survival analysis · clustering`
>
> **AI menjelaskan hasil dalam bahasa manusia.**

---

> ⭐⭐⭐ **`effect size` berdiri sederet dengan `hypothesis testing`, dan itu
> pasangan yang benar untuk kekeliruan yang paling sering terjadi di sains.**
>
> Uji hipotesis menjawab *"apakah efeknya mungkin nol"*; ukuran efek menjawab
> **"seberapa besar efeknya"** — dan hanya yang kedua menentukan apakah temuan
> itu berarti. Dengan sampel yang cukup besar, efek yang sangat kecil akan lolos
> uji; dengan sampel kecil, efek besar bisa tidak lolos. Sistem yang melaporkan
> yang pertama tanpa yang kedua akan **memberi lampu hijau pada temuan yang
> tidak berguna**, dan menahan yang berguna.
>
> Ini bentuk yang sama dengan §17.36 (*"accuracy saja tidak cukup"*) dan §18.20
> (Trust Vector menolak satu angka). **Tiga naskah berturut-turut menolak metrik
> tunggal** — itu kebiasaan, bukan kebetulan.

> ⭐ **`survival analysis` juga bukan pelengkap daftar.** Ia satu-satunya alat di
> sini yang menangani **data yang belum selesai** — subjek yang belum mengalami
> kejadiannya sampai pengamatan berhenti. Memasukkannya berarti pemiliknya tahu
> bahwa membuang kasus yang belum selesai adalah salah satu cara termudah
> menghasilkan angka yang salah.

> 🛑 **Tetapi §19.33 tidak punya milestone untuk Statistics Intelligence,
> sementara §19.34 MENUNTUT `melakukan analisis statistik` sebagai kriteria
> selesai.** `S19.7` adalah *Simulation Lab*; statistik tidak disebut di sepuluh
> milestone mana pun. Ini satu dari **empat** butir DoD tanpa milestone di
> naskah ini. Lihat **G-18** / [#137](../../issues/137).

> 🛑 **Dan `AI menjelaskan hasil dalam bahasa manusia` adalah tempat angka yang
> BENAR berubah menjadi kalimat yang SALAH — dan bagian ini tidak memberinya
> satu batas pun.**
>
> Terjemahan yang keliru di sini punya bentuk yang bisa diprediksi:
> *"tidak signifikan"* menjadi *"tidak ada efek"* · selang kepercayaan menjadi
> *"kemungkinan 95 % bahwa…"* · korelasi menjadi kalimat bersebab · `p = 0,06`
> menjadi *"mendekati signifikan"*. Semuanya terdengar wajar, semuanya salah,
> dan **semuanya lebih mudah dibaca daripada versi yang benar** — itulah
> sebabnya ia terjadi.
>
> ⭐ Naskah ini punya obatnya di dua tempat, keduanya belum disambungkan ke
> sini: §17.7 memberi bentuk *"bukan X, melainkan Y"* dengan **kalimat
> penggantinya ditulis** (*"pola yang konsisten dengan"*, bukan *"Anda
> menderita"*), dan §19.20 sudah memberlakukan larangan pada keluaran untuk
> sitasi. Yang perlu: **daftar kalimat terlarang beserta penggantinya**, di
> tempat statistik diterjemahkan — bukan prinsip, melainkan pasangan kata.
