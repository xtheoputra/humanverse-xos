# 189 — §12.3–§12.4 Human World Model & Temporal World Model

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §12.3 — Human World Model

> Digital Twin menggambarkan **manusia**. World Model menggambarkan **dunia
> tempat manusia berada**.

```
User
 ├── Home ── Bedroom · Desk · Wardrobe
 ├── Work ── Office · Team · Projects
 ├── University ── Thesis
 ├── Social
 ├── Finance
 └── Environment ── Weather · Traffic · Events
```

World Model harus memahami: **entities · relationships · resources ·
constraints · states · events · temporal changes · dependencies ·
uncertainty**

---

> ⭐⭐ **Pemisahan twin/world adalah pembagian yang benar dan belum pernah
> ditegaskan.** Naskah 13 §9.13 memberi *Personal World Model* yang mencampur
> keduanya (Goals · Resources · Constraints · Habits · Skills · Preferences ·
> Environment · Behavior patterns) — separuhnya tentang orangnya, separuhnya
> tentang dunianya. Di sini: **twin = orangnya, world = tempatnya**, dan
> keduanya punya siklus hidup berbeda (twin berubah per hari, ruangan tidak).

> ⭐ **Pohon `Home → Bedroom → Desk → Wardrobe` cocok persis dengan hierarki
> spasial §10.18** (`World → Building → Floor → Room → Object`). Itu bukan
> kebetulan — ia lapisan yang sama, dilihat dari sisi hidup pengguna, bukan
> dari sisi sensor. ⭐ Dan `Wardrobe` sebagai simpul dunia menyambungkan
> Wardrobe Graph §10.7 ke World Model tanpa perlu struktur baru.

> ⚠️ **`uncertainty` sebagai sifat World Model, bukan hanya sifat kesimpulan.**
> Itu benar dan baru: sistem tidak hanya tidak yakin pada **taksirannya**, ia
> juga tidak yakin pada **dunianya** — apakah rapat itu masih jadi, apakah
> lemari masih berisi yang dulu terlihat. Yang perlu ditulis: bagaimana
> ketidakpastian dunia merambat ke ketidakpastian simulasi (§12.15).

> ⚠️ **`Team`, `Social`, dan `Thesis` memuat orang lain.** `Work → Team` adalah
> rekan kerja; `Social` adalah relasi. Ini permukaan keenam menuju **C-10**
> ([#40](../../issues/40)) setelah kamera, mikrofon, dokumen, graf spasial, dan
> RF sensing — dan yang ini paling terang: World Model **memang dirancang**
> untuk menyimpan orang lain sebagai entitas, karena tanpa itu ia tidak
> menggambarkan dunia siapa pun.
>
> Aturan yang dibutuhkan sama seperti usul di [#40](../../issues/40): orang
> lain boleh ada sebagai **entitas berperan** (*"rekan tim"*, *"pembimbing"*)
> tanpa identitas, riwayat, atau atribut yang disimpulkan.

---

## §12.4 — Temporal World Model

> HumanVerse perlu memahami bahwa dunia **berubah terhadap waktu**.

```
Monday → Work → Gym → Low energy → Poor study performance
Friday → High workload → High cognitive load → Low motivation
```

Sehingga HumanVerse dapat menemukan:

```
time → event → state → behavior → outcome
```

---

> ⭐ **Rantai lima langkah itu adalah bentuk yang bisa diuji.** Ia memisahkan
> apa yang **terjadi** (event) dari apa yang **dirasakan** (state) dan apa yang
> **dilakukan** (behavior) — tiga hal yang di naskah-naskah awal sering
> tercampur menjadi satu angka. Dan ia cocok dengan `change points` §9.16:
> yang layak disimpan adalah **titik peralihannya**, bukan tiap pengukuran.

> 🛑 **Tapi kedua contoh itu adalah urutan, bukan sebab — dan bagian berikutnya
> justru memperingatkannya.** *"Monday → Work → Gym → Low energy → Poor study
> performance"* dibaca sebagai rantai sebab-akibat, padahal ia deret waktu.
> §12.5 di naskah yang sama menuntut Observation → Correlation → Hypothesis →
> **Causal Evidence** → Conclusion sebelum boleh menyimpulkan sebab.
>
> Ini pola yang sama persis dengan **E-81** ([#7](../../issues/7)): §9.11
> mengembalikan sisi `influences` ke graf sementara §9.17 menuntut bukti
> kausal. Dua naskah berturut-turut menggambar rantai kausal di satu bagian dan
> melarangnya di bagian berikutnya.
>
> Yang menyelesaikannya sudah ada dan tinggal ditulis sebagai aturan: **panah
> di Temporal World Model adalah `followed_by`, bukan `causes`** — dan hanya
> §12.5/§12.6 yang boleh mengubahnya jadi sisi kausal, setelah bukti.
> `causal_edges` di §12.28 adalah tabel terpisah dari `world_events`, jadi
> pemisahannya sudah ada di skema; yang kurang hanya kalimatnya.

> ⚠️ **Deteksi pola mingguan (*Monday*, *Friday*) butuh berminggu-minggu data,
> dan pola musiman butuh setahun** — sama seperti catatan di §9.16. Untuk V0
> yang bisa dijalankan hanya `trend` dan pola mingguan sederhana. Bertaut
> **B-1** (cold start) dan **B-21** ([#48](../../issues/48)).
