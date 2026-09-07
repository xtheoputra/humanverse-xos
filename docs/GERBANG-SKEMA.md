# Gerbang Skema — apa yang sebenarnya masih mengunci Engineering Spec

> ⚠️ **Bukan kata pemilik.** Berkas ini menyusun ulang butir yang sudah ada di
> [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md) menjadi bentuk yang bisa
> **diputuskan**, bukan menambah temuan baru.
>
> Disusun 7 September 2026, sesudah naskah 18.

---

## Kenapa berkas ini ada

`README.md` menyebut **empat butir** yang mengunci Engineering Spec *"karena
keempatnya menentukan skema basis data"*. Daftar itu **sudah tidak akurat** —
satu di antaranya sudah ditutup, dan satu lagi praktis tertutup, sementara dua
sisanya justru **memburuk**.

Selisih itu penting: pekerjaan yang tampak terhalang empat pintu sebenarnya
terhalang dua.

| Butir | Kata `README` | Keadaan sebenarnya di berkas audit |
|---|---|---|
| **E-39** memory: jenis atau nama scope | mengunci | ✅ **SUDAH DITUTUP** naskah 13 → **H-16**. Jawabannya **tiga sumbu tegak lurus**: `kind` · `scope` · `tier` |
| **E-16** arah sebab-akibat | mengunci | ✅ **Praktis tertutup** — `Sleep → Energy → Focus` §12.6 cocok dengan naskah 3 dan naskah 9; kini **tiga lawan satu** |
| **E-17 / E-18** node & relasi graf | mengunci | 🛑 **masih terbuka** |
| **A-19** model angka pengguna | mengunci | 🛑 **masih terbuka, dan MEMBURUK** — kini **enam**, bukan lima |
| **E-37** skala skoring | mengunci | 🛑 **masih terbuka, dan MEMBURUK** — Phase 13 menambah tabrakan skala **di dalam satu naskah** |

---

## Gerbang 1 — A-19: enam model angka pengguna, nol rumus

**Pertanyaannya satu kalimat:** angka mana yang kanonik untuk menggambarkan
keadaan seorang pengguna, dan bagaimana ia dihitung?

Yang sudah ada, tak satu pun saling merujuk dan tak satu pun berumus:

| # | Model | Bentuk |
|---|---|---|
| 1 | *Human Genome of Behavior* | 6 skor |
| 2 | *Profile Engine* | 5 atribut |
| 3 | **`HumanState`** | 7 field (naskah 5 membuang `mood`) |
| 4 | *Human Dashboard* | 7 batang |
| 5 | `DigitalTwin` | 8 model |
| 6 | **Energy Budget** §13.15 | anggaran harian 100, biaya per aktivitas |

Yang keenam datang dari naskah 17 dan **lebih berbahaya daripada lima
sebelumnya**, karena ia satu-satunya yang **menolak pekerjaan**: kalau angkanya
salah, penjadwal akan menolak sesuatu yang sebenarnya sanggup dikerjakan, dan
penggunanya mematikan fiturnya.

**Usul:** jadikan **`HumanState`** satu-satunya yang disimpan — ia satu-satunya
yang sudah punya bentuk tetap dan sudah dipakai lintas naskah — dan perlakukan
lima lainnya sebagai **tampilan turunan**, bukan tabel. Setiap angka turunan
wajib membawa `confidence`, sesuai **B-15/B-1** yang sudah ditutup.

**Yang harus ditulis bersamaan:** satu rumus untuk `HumanState`, sekalipun
sederhana. Angka tanpa produsen adalah utang yang bunganya dibayar saat
pengguna pertama bertanya *"kenapa angkanya segitu?"*.

---

## Gerbang 2 — E-17 / E-18: node dan relasi graf

**Pertanyaannya dua kalimat:** simpul apa saja yang ada di graf, dan kosakata
relasi mana yang berlaku?

**E-17 — daftar node.** Naskah 2 menetapkan **10 node**. Rantai Layer 8 memakai
`Energy`, `Productivity`, `Career` yang tidak ada di daftar itu. Naskah 4
menambah `Goal`, `Milestone`, `Project`, `Skill`, `Wardrobe item`. Naskah 17
menambah **Life Graph** dengan `HEALTH`/`CAREER`/`FINANCE` → `GOALS` →
`PROJECTS` → `TASKS` → `ACTIONS` → `OUTCOMES`.

**E-18 — kosakata relasi, tiga set yang terputus:**

| Set | Contoh | Sifat |
|---|---|---|
| Naskah 2 | `improves` · `causes` · `influences` · `blocks` · `predicts` | **kausal** |
| Naskah 3 (ontology) | `hasHabit` · `prefersStyle` | **struktural** |
| Naskah 4 §9 | set ketiga | — |

**Usul:** keduanya bukan pilihan yang saling meniadakan — mereka **dua jenis
sisi di graf yang sama**. Relasi struktural (`hasHabit`) menjawab *"apa yang
dimiliki pengguna"*; relasi kausal (`improves`) menjawab *"apa memengaruhi
apa"*. Simpan sebagai **satu tabel sisi dengan kolom `kind`**, persis pola yang
sudah dipakai dan diterima untuk memory di **H-16** (`kind`/`scope`/`tier`).

Kalau pola itu sudah dipilih sekali dan berhasil, memakainya lagi lebih murah
daripada memilih salah satu set dan membuang yang lain.

---

## Gerbang 3 — E-37: skala skoring yang tidak sepadan

**Pertanyaannya satu kalimat:** skor disimpan dalam skala apa?

| Sumber | Skala |
|---|---|
| Naskah 2 | bobot persen, berjumlah **100 %** |
| Naskah 3 | *Outfit Score* berjumlah **100 poin** |
| Naskah 5 §11 | *Recommendation Score* **rata-rata 0–1** |

Naskah 17 memburukkannya dengan cara baru: **energi ditulis tiga skala di dalam
satu naskah** — `Energy > 0.7` (§13.11), `Daily Energy = 100` (§13.15), dan
`Energy 72%` di layar utama (§13.29). Itu **E-115**.

**Usul:** **`0–1`**, dan alasannya bukan selera:

1. §12.21 sudah membuktikan bobot **berjumlah tepat 1,00** (0,30+0,25+0,20+0,15+0,10) dan §9.25 sepakat — jadi skala itu sudah dipakai benar di dua tempat.
2. Persen dan poin adalah **cara menampilkan**, bukan cara menyimpan. `0,72` bisa ditampilkan sebagai `72 %`; `72 poin` tidak bisa dikembalikan jadi rasio tanpa tahu pembaginya.
3. Ia satu-satunya skala yang bisa bersanding dengan `confidence` tanpa membingungkan — keduanya `0–1`.

⚠️ Catatan yang tidak boleh hilang: rumus §11 menyebut **7 komponen** sementara
contohnya memakai **5** (*Occasion Fit* dan *Availability* tidak muncul), dan
belum ada bobot. Memilih skala **tidak** menyelesaikan itu.

---

## Yang TIDAK ada di berkas ini

**A-17** — V0 bertambah 2 fitur jadi 12 sementara waktunya tetap 4–6 minggu.
Itu keputusan **cakupan**, bukan keputusan **skema**; ia tidak menghalangi satu
baris DDL pun. Ia tetap terbuka dan tetap penting, tapi ia bukan gerbang yang
sama.

---

## Ringkasnya

Dua gerbang tertutup atau praktis tertutup. **Tiga pertanyaan tersisa**, dan
ketiganya bisa dijawab tanpa naskah baru:

1. **`HumanState` jadi satu-satunya yang disimpan?** (A-19)
2. **Satu tabel sisi dengan kolom `kind`?** (E-17/E-18)
3. **Skor disimpan `0–1`?** (E-37)

Ketiganya sudah punya pola yang terbukti di repo ini sendiri — `kind`/`scope`/`tier`
dari H-16, dan bobot berjumlah 1,00 dari §12.21. Tidak ada yang perlu ditemukan;
yang perlu hanya diputuskan.
