# 180 — §11.15–§11.18 Risk Model, Autonomy Levels, Autonomy Budget & Guardrails

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.15 — Risk Model

> Kita sudah memiliki **R0–R4**. Sekarang kita integrasikan dengan agency.

| Tingkat | Isi | Perlakuan |
|---|---|---|
| **R0** Informational | read public information | tidak perlu confirmation |
| **R1** Low impact | create personal note · update habit · create reminder | biasanya **autonomous** |
| **R2** Moderate | send low-risk message · modify schedule · purchase low-value item | **policy-dependent** |
| **R3** High impact | financial transaction · important communication · account changes · sensitive data sharing | **human confirmation** |
| **R4** Critical | irreversible · high financial impact · high safety impact | **DENY** |

---

> ⭐⭐⭐ **R4 = `DENY` sebagai bawaan adalah pengetatan nyata atas §8.17**, yang
> hanya mewajibkan konfirmasi di R3/R4. Di sini tingkat tertinggi **tidak bisa
> dikonfirmasi** — ia ditolak, dan menaikkannya harus jadi tindakan tersendiri.
> Itu sejalan dengan [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) yang
> menyatakan **V0 tidak punya satu pun tool level 3 atau 4**.

> ⭐⭐ **Dan definisi R4 berubah dari "berdampak besar" menjadi
> "irreversible"** — sumbu yang §11.27 jadikan mesin tersendiri. Itu jawaban
> yang lebih tepat untuk pertanyaan *"kenapa transaksi finansial berbahaya"*:
> bukan karena nilainya, melainkan karena **tidak bisa ditarik**.

> ⚠️ **Tetapi kalibrasi E-67 tetap berdiri: `update habit` masih R1.**
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) memberi `habit.complete` dan
> `memory.write` **risk 2** dengan default `ask`. Butir **E-67** /
> [#60](../../issues/60) mencatat bahwa dengan konfirmasi mulai R3, setiap
> tulisan ke data pengguna di V0 berjalan senyap.
>
> ⭐ **Naskah ini menjawabnya dari sumbu lain, bukan dengan menaikkan
> angkanya:** manifest §11.5 memberi `habit-coach` **`autonomy.max_level: L2`**
> — L2 adalah *Prepare*, bukan *Execute*. Jadi agent habit boleh menyiapkan,
> dan manusia yang menjalankan. Risiko tetap R1; **otonominyalah yang
> membatasi**.
>
> Itu desain yang lebih baik daripada usul saya (menaikkan angka risikonya),
> tapi konsekuensinya harus ditulis: **risk gate spec/05 sekarang perlu
> memeriksa `autonomy.max_level`, bukan hanya `risk_level`.** Tanpa itu,
> gerbangnya melihat separuh dari yang menentukan.

> ⚠️ **`purchase low-value item` di R2 tanpa satu angka pun.** Naskah 12 §8.18
> menempatkan `travel-agent purchase` di **R4**; di sini pembelian tersebar di
> R2 (nilai kecil), R3 (transaksi finansial), dan R4 (dampak finansial besar) —
> spektrum yang masuk akal, tapi *"low-value"* tidak pernah didefinisikan.
>
> ⭐ Yang menyelamatkannya: **§11.17 memberi `purchases: { amount_limit: 0 }`
> sebagai bawaan.** Nol berarti tidak ada pembelian sama sekali sampai pengguna
> menaikkannya secara sadar. Jadi *"low-value"* sebenarnya sudah punya angka —
> angkanya adalah **apa pun yang ditetapkan pengguna di `amount_limit`**, dan
> itu sebaiknya ditulis sebagai definisinya, bukan dibiarkan sebagai kata sifat.

---

## §11.16 — Autonomy Levels

```
L0 — Observe
L1 — Recommend
L2 — Prepare
L3 — Ask Confirmation
L4 — Execute within Boundaries
```

| | Contoh |
|---|---|
| **L0** | *"Anda punya meeting pukul 09:00."* |
| **L1** | *"Saya menyarankan berangkat pukul 08:15."* |
| **L2** | *"Saya sudah menyiapkan reminder."* |
| **L3** | *"Bolehkah saya menambahkan reminder?"* |
| **L4** | *"Saya otomatis menambahkan reminder sesuai aturan yang Anda izinkan."* |

---

> ⭐⭐⭐ **Ini menutup E-77 / [#67](../../issues/67) — tabrakan penomoran paling
> berbahaya dari lima belas naskah.**
>
> Kelima tingkat **identik dengan §9.26 naskah 13** (Information · Recommendation
> · Prepare action · Ask confirmation · Bounded autonomy). Dua naskah, daftar
> yang sama tanpa bergeser.
>
> Yang menyelesaikannya bukan daftarnya, melainkan **§11.15 yang membuka
> dengan *"kita sudah memiliki R0–R4"* lalu memberi tangga ini secara
> terpisah** — dan §11.5 menaruh keduanya di satu berkas:
>
> ```yaml
> risk_level: R1          # risiko AKSI
> autonomy:
>   max_level: L2         # kewenangan AGENT
> ```
>
> Butir E-77 mencatat bahwa *"agent ini Level 4"* berarti **"selalu minta
> izin"** dengan naskah 12 dan **"boleh jalan sendiri"** dengan naskah 13.
> Dengan huruf yang berbeda, kalimat itu tidak bisa lagi salah dibaca: `R4`
> ditolak, `L4` berjalan dalam batas. Lihat **H-21**.

> ⭐ **Lima contoh kalimatnya menunjukkan bahwa tangga ini tentang siapa yang
> bertindak, bukan seberapa berbahaya.** Aksi yang sama — menambahkan reminder
> — muncul di L2, L3, dan L4 dengan tiga kalimat berbeda. Itu bukti bahwa
> kedua sumbu memang tegak lurus.

> ⚠️ **Aturan pengikat kedua sumbu belum ditulis sebagai tabel**, meskipun ia
> bisa dibaca dari §11.15. Yang tersirat:
>
> | Risiko | Otonomi tertinggi yang wajar |
> |---|---|
> | R0 · R1 | L4 — berjalan dalam batas |
> | R2 | tergantung policy (L2–L4) |
> | R3 | **L3** — selalu bertanya |
> | R4 | **ditolak** — tidak ada L |
>
> Empat baris, dan tanpanya kedua kolom di manifest bisa diisi bebas dan
> bertentangan (`risk_level: R4` + `autonomy.max_level: L4`). Aturan validasi
> yang perlu ditambahkan ke [`../spec/05`](../spec/05-AGENT-CONTRACTS.md).

---

## §11.17 — Autonomy Budget

```yaml
autonomy_budget:
  calendar:
    create_event: 20/day
  notification:
    send: 10/day
  purchases:
    amount_limit: 0
```

> Agent tidak boleh melakukan **unlimited actions**.

---

## §11.18 — Financial / Resource Guardrails

> Tidak hanya uang. Agency dapat memiliki budget:

```
Money · API calls · Compute · Notifications · Messages
Time · Device actions · Storage
```

```
Agent → Budget Engine → Remaining Budget?
        ├── YES → execute
        └── NO  → stop
```

---

> ⭐⭐⭐ **Ini mekanisme paling langsung untuk menahan biaya di lima belas
> naskah, dan ia menjawab tiga butir sekaligus.**
>
> | Butir | Bagaimana budget menjawabnya |
> |---|---|
> | **B-2** paket Free harus nyaris tidak memanggil model besar | `API calls` dan `Compute` sebagai anggaran per agent |
> | **H-6** biaya inferensi berlipat | agent yang habis anggarannya **berhenti**, bukan melambat |
> | **A-27** model biaya diakui, nol fase pendapatan | biaya jadi **terbatas dari desain**, bukan bergantung pendapatan |
>
> Yang membuatnya berbeda dari Cost Engine naskah 4 §48: Cost Engine
> **mengukur**; Budget Engine **menghentikan**. Dan §11.14 menempatkannya
> sebagai gerbang, bukan laporan.

> ⭐ **`Notifications: 10/day` adalah pengaman yang tidak biasa dan tepat.**
> Ia membatasi bukan biaya melainkan **perhatian pengguna** — dan ia pasangan
> alami untuk Interruption Manager §11.43. Menganggap perhatian orang sebagai
> sumber daya terbatas yang punya anggaran adalah keputusan desain yang jarang
> dibuat, dan ia sejalan dengan *"Do Nothing adalah kemampuan penting"* §11.44.

> ⭐ **`Time` sebagai anggaran** — agent yang boleh menjadwalkan hanya sekian
> jam hidup seseorang per minggu. Untuk sistem yang menjadwalkan belajar,
> olahraga, dan tidur sekaligus, itu satu-satunya pertahanan terhadap **konflik
> §11.22** yang terjadi karena setiap agent optimis sendiri-sendiri.

> ⚠️ **Anggaran butuh pemilik, periode, dan cara mengisi ulang** — dan ketiganya
> belum ada. `20/day` menyiratkan reset harian; `amount_limit: 0` tidak punya
> periode sama sekali (batas per transaksi, per hari, atau seumur hidup?).
> Ditambah: siapa yang boleh menaikkannya, dan apakah menaikkan anggaran
> sendiri termasuk aksi yang butuh konfirmasi. Kalau agent bisa menaikkan
> anggarannya sendiri, seluruh mekanisme ini kosong.
