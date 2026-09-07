# 213 — §14.23–§14.26 Agent Economy, Billing, Resource Economy & Attention Firewall

> Berkas ini merekam kata pemilik apa adanya (naskah kedelapanbelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §14.23 — Agent Economy

**Actors:** Users · Developers · Agent Creators · Tool Providers · Model
Providers · Organizations · Partners

**Revenue model bisa:**

```
Agent subscription       Enterprise licensing
Usage-based pricing      API usage
Marketplace commission   Agent team subscription
                         Developer platform
```

> Namun pembayaran/action tetap masuk: **Financial Policy · Permission · Risk
> Engine**

---

> ⭐⭐⭐ **Ini menutup A-27 / [#73](../../issues/73) — butir yang saya buka dua
> naskah lalu sebagai *"proyek dengan model biaya yang diakui dan nol fase
> pendapatan"*.**
>
> Butir **E-86** mencatat bahwa peta 15 fase §10.41 membuang *Subscription* dan
> *Revenue Platform* tanpa rumah baru, sementara **H-6** mengakui biaya
> inferensi berlipat, **B-2** menuntut paket Free nyaris tidak memanggil model
> besar, dan **E-41** mencatat `Billing` muncul entah dari mana.
>
> Tujuh model pendapatan di atas memberi jawabannya, dan **Phase 14 adalah
> rumahnya**. Ditambah §14.17–§14.18 yang mengembalikan Enterprise, dua blok
> yang hilang dari peta kini keduanya punya tempat. Dicatat sebagai **H-24**.
>
> ⚠️ Yang tetap terbuka dari **A-6** ([#18](../../issues/18)): **angkanya** —
> tangga harga, dan bagi hasil dengan developer. Tujuh model adalah bentuk,
> bukan tarif.

---

## §14.24 — Agent Billing

```
Research Agent
LLM:      $0.14
Search:   $0.08
Database: $0.02
Total:    $0.24
```

Orchestrator dapat memilih **Cheap Agent vs Premium Agent** berdasarkan
**quality · risk · latency · budget**.

---

> ⭐⭐ **Biaya per agent yang dirinci per komponen adalah yang membuat pilihan
> itu bisa dibuat mesin.** Bandingkan `Average Cost: $0.08` §11.32 — satu angka
> agregat; di sini tiga baris yang menunjukkan **di mana** biayanya.
>
> Dan pilihan *cheap vs premium* adalah Model Router (§9.20 · §10.29 · §11.54)
> yang naik satu tingkat: bukan lagi memilih **model**, melainkan memilih
> **agent**. Sumbu keempat untuk router yang sudah punya tiga (effort ·
> modality · risk).

> ⚠️ **`risk` sebagai kriteria memilih agent murah vs mahal perlu arah yang
> jelas.** Untuk aksi berisiko tinggi, yang benar adalah **agent yang lebih
> mahal dan lebih terverifikasi** — sejalan dengan §11.54 (*high-risk decision
> → multiple-model verification*). Kalau tidak dinyatakan, penghematan akan
> mengalir ke tempat yang paling tidak boleh dihemat.

---

## §14.25 — Agent Resource Economy

Agent memakai: **CPU · GPU · Memory · Tokens · API calls · Network · Storage ·
Human attention**

> Human attention **sangat penting**:
>
> ```
> 10 agents × 5 notifications/day = 50 interruptions
> ```
>
> Itu buruk. Maka Collective Intelligence harus memiliki **Attention Budget**.

---

> ⭐⭐⭐ **Perhitungan itu adalah argumen terkuat di seluruh naskah, dan ia
> hanya perkalian.**
>
> Anggaran `notification: send: 10/day` §11.17 ditetapkan ketika sistemnya
> punya satu lapisan agent. Dengan dua puluh lima agent berhierarki (§11.4),
> tujuh yang muncul di contoh (**E-95**), dua belas dari Phase 12 (**G-13**),
> dan kini team serta agent federasi — **pagu per agent berhenti berarti
> apa-apa**.
>
> Yang dibutuhkan adalah pagu **per manusia**, dibagi ke seluruh ekosistem —
> dan §14.25 menyebutnya `Attention Budget`. Itu perubahan jenis, bukan
> derajat: perhatian menjadi **sumber daya bersama yang langka**, sejajar
> dengan token dan uang.
>
> Ini juga yang menjawab kekhawatiran saya di **A-28** ([#80](../../issues/80)):
> begitu sistem boleh memulai sendiri, jumlah agent menentukan seberapa sering
> ia memulai.

> ⭐ **`Human attention` berdiri di daftar yang sama dengan CPU dan GPU** —
> dan menempatkannya di sana, bukan di bagian antarmuka, adalah keputusan
> desain yang benar. Sumber daya yang dianggarkan akan dihitung; yang tidak
> akan dihabiskan.

---

## §14.26 — Human Attention Firewall

```
Agent Output → Importance → Urgency → Confidence → Goal relevance
→ Risk → Attention cost → Interruption Manager
→ NOW / LATER / DIGEST / SILENT / ASK
```

> Evolusi dari **Attention OS Phase 13**.

---

> ⭐⭐ **Kata "firewall" tepat, dan bukan sekadar gaya bahasa.** Yang dijaga
> bukan aliran data melainkan **arah sebaliknya**: apa yang boleh keluar dari
> sistem menuju perhatian orangnya. Tidak ada satu pun agent yang boleh
> menembusnya langsung — itu batas keras yang sejajar dengan *"agent tidak
> boleh bypass gateway"* §11.14 dan *"simulation tidak boleh mengubah data
> dunia nyata"* §12.16.
>
> Tiga batas keras sekarang, dan **ketiganya perlu ditegakkan CI**
> ([`../spec/06`](../spec/06-MODULE-BOUNDARIES.md)), bukan diniatkan.

> ⭐ **Lima keluaran, dan `DIGEST` adalah yang belum ada di §11.43** (yang
> punya *Notify now · Notify later · Silent · Ask permission*). Ringkasan
> berkala adalah jawaban yang tepat untuk banyak agent yang masing-masing punya
> sesuatu yang **berguna tapi tidak mendesak** — dan tanpa `DIGEST`, semuanya
> jatuh ke `LATER` yang akhirnya menumpuk jadi gangguan yang sama.

> ⚠️ **`Confidence` sebagai masukan, lagi tanpa ambang** — naskah kedelapan
> berturut-turut ([#34](../../issues/34)). ⭐ Tapi §14.62 akhirnya memberi angka
> pertama (`escalate_when: confidence < 0.6`); lihat berkas
> [`218`](218-REPO-DATA-EVENT-ROADMAP-DOD.md).
