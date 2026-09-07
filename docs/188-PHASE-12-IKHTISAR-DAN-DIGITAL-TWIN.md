# 188 — Phase 12: Digital Twin & World Simulation (ikhtisar, §12.1–§12.2)

> Berkas ini merekam kata pemilik apa adanya (naskah keenambelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Penomoran

Bagian dinomori berawalan fase — `12.1`–`12.31` — seperti naskah 14 dan 15.
Berkas rapi memakainya apa adanya sebagai **`§12.1`–`§12.31`**.

---

## Posisi pemilik

| Fase | Kemampuan |
|---|---|
| 10 | **Perception** — melihat dunia |
| 9 | **Cognition** — memahami & berpikir |
| 11 | **Agency** — bertindak |
| **12** | **Simulation** — *memperkirakan konsekuensi sebelum bertindak* |

```
REAL HUMAN → MULTIMODAL PERCEPTION → HUMAN STATE
→ MEMORY + KNOWLEDGE GRAPH → DIGITAL TWIN → WORLD MODEL
→ CAUSAL MODEL → SCENARIO GENERATOR → SIMULATION ENGINE
→ COUNTERFACTUAL ENGINE → FUTURE STATE PROJECTION
→ DECISION INTELLIGENCE → AGENT ACTION → REAL WORLD
→ OBSERVATION → DIGITAL TWIN UPDATE
```

---

> ⭐⭐ **Kalimat *"memperkirakan konsekuensi sebelum bertindak"* menempatkan
> Phase 12 di tempat yang benar dalam urutan.** Ia berdiri **sebelum** Agency
> di alur eksekusi, meskipun datang **sesudah** Agency di urutan naskah. Itu
> konsisten dengan §11.11 *Plan Verification* (rencana diperiksa sebelum
> dijalankan) dan §11.16 L2 *Prepare* — keduanya menuntut sesuatu yang bisa
> menilai rencana sebelum ada yang terjadi. Simulasi adalah benda itu.

---

## §12.1 — Personal Digital Twin

> Digital Twin **bukan** berarti membuat *"salinan kesadaran manusia"*. Yang
> dibuat adalah **model komputasional probabilistik** tentang keadaan, pola,
> preferensi, tujuan, sumber daya, batasan, dan perilaku seseorang.

```yaml
digital_twin:
  identity:            constraints:
  preferences:         resources:
  goals:               beliefs:
  skills:              decision_patterns:
  habits:              environment:
  behavior_patterns:
  financial_state:     career_state:
  learning_state:      lifestyle_state:
  social_state:        physical_state:
  emotional_state:
```

Setiap komponen memiliki: `value · confidence · source · timestamp ·
volatility`

```json
{
  "attribute":  "morning_productivity",
  "value":      0.78,
  "confidence": 0.84,
  "source":     "90_day_behavior_history",
  "volatility": 0.12
}
```

> Jadi Digital Twin tidak berkata *"Kamu pasti produktif pagi hari"*, tetapi:
> *"Berdasarkan 90 hari terakhir, probabilitas produktivitas tinggi pada pagi
> hari sekitar 78 %, dengan confidence 84 %."*

---

> ⭐⭐⭐ **`volatility` adalah field baru yang menjawab pertanyaan terbuka di
> B-20 / [#49](../../issues/49).**
>
> Butir itu mencatat bahwa §9.9 memberi rumus peluruhan
> (`Strength(t) = Initial × Decay(t) + Reinforcement`) **tanpa bentuk
> `Decay(t)`** — dan saya menulis: *"paruh waktu berapa? Preferensi fashion dan
> preferensi makanan hampir pasti tidak sama."*
>
> `volatility` **adalah laju peluruhan per atribut**. `morning_productivity`
> dengan `volatility: 0.12` berubah pelan; preferensi mode akan jauh lebih
> tinggi. Satu field, dan pertanyaan yang menggantung tiga naskah punya
> jawabannya.
>
> Ia juga melengkapi empat besaran yang sudah ada dan sekarang akhirnya
> berpasangan rapi:
>
> ```
> value        apa nilainya
> confidence   seberapa yakin sistem pada nilai itu        (§9.32)
> quality      seberapa baik pengukurannya                 (§10.20)
> volatility   seberapa cepat ia berubah                   (§12.1)
> ```

> ⭐⭐ **`constraints` dan `resources` akhirnya punya rumah.** Saya catat di
> berkas [`162`](162-COGNITIVE-ORCHESTRATOR-DAN-RUNTIME.md) bahwa `constraints`
> adalah satu-satunya field context package §9.31 yang **belum pernah punya
> sumber** di tiga belas naskah — padahal ia yang membuat rekomendasi
> realistis (*saran belajar 3 jam/hari kepada orang yang bekerja dua sif adalah
> saran yang salah, bukan saran yang ambisius*). Sekarang keduanya komponen
> Digital Twin, dan §12.22 memakainya sebagai batasan optimasi.

> ⭐ **`beliefs` dan `decision_patterns` belum pernah ada.** Yang kedua
> menarik: ia memodelkan **bagaimana** seseorang memutuskan, bukan **apa** yang
> ia putuskan — dan itu yang membuat simulasi keputusan §12.11 bisa
> memperkirakan pilihan orangnya, bukan pilihan yang optimal secara umum.

> 🛑 **Daftar komponen Digital Twin versi KEEMPAT — dan `Perception` hilang
> setelah satu naskah.**
>
> | Naskah | Komponen |
> |---|---|
> | 4 §25 | Identity · Behavior · Preference · Goal · State · Skill · **Social** · Decision — **8** |
> | 5 | sama, `Social` → `Lifestyle` (**E-34**) |
> | 14 §10.32 | delapan naskah 4 **+ Perception** (Visual/Audio/Spatial/Sensor/Environmental) — **9** |
> | **16 §12.1** | **18 komponen**, dan **`Perception` tidak ada** |
>
> Butir **E-92** mencatat `Social` kembali dan `Lifestyle` hilang lagi di
> naskah 14. Sekarang keduanya ada (`social_state`, `lifestyle_state`) — itu
> penyelesaian yang baik — tetapi **lapisan Perception yang baru ditambahkan
> satu naskah sebelumnya menghilang tanpa disebut**. Pola yang sama dengan
> **H-8**. Lihat **E-103** / [#87](../../issues/87).

---

## §12.2 — Twin State Engine

```
Energy          0.62      Social Energy   0.36
Focus           0.71      Goal Momentum   0.81
Motivation      0.55      Cognitive Load  0.68
Stress          0.43      Physical Ready  0.74
```

Diperbarui dari: **wearable · calendar · sleep · activity · journal · voice ·
location · behavior · tasks · environment · historical patterns**

```
Digital Twin(t) → Digital Twin(t+1) → Digital Twin(t+2)
```

---

> 🛑 **Human State versi KEEMPAT: 8 → 7 → 10 → 8, dan `mood` keluar untuk
> kedua kalinya.**
>
> | Naskah | Field | `mood` |
> |---|---|---|
> | 4 §14 | 8 | ✅ ada |
> | 5 §14 | 7 | ❌ keluar (**E-34** — kemungkinan disengaja: mood **dilaporkan**, bukan ditaksir) |
> | 13 §9.5 | **10** | ✅ **kembali** (**E-80**) + `financial pressure` + `goal momentum` |
> | **16 §12.2** | **8** | ❌ **keluar lagi**, dan `financial pressure` juga hilang |
>
> Delapan field §12.2 adalah sepuluh field §9.5 **minus `mood` dan minus
> `financial pressure`**.
>
> ⭐ Keduanya kemungkinan besar **benar dibuang**, dan alasannya sudah pernah
> saya tulis: `mood` punya event dan tabel sendiri (**dilaporkan pengguna**,
> bukan ditaksir sistem), dan `financial pressure` adalah field paling sensitif
> yang pernah masuk HumanState (Level 3 klasifikasi data).
>
> ⚠️ Tapi setelah empat kali berubah tanpa satu pun perubahan dinyatakan,
> daftar ini perlu ditetapkan sekali. `human_states.metrics` dibuat `jsonb`
> justru supaya ini tidak menghalangi kode — tapi **A-19** ([#2](../../issues/2))
> menanyakan *angka mana yang dipakai*, dan jawabannya masih berubah tiap
> naskah. Lihat **E-102**.

> ⭐ **Sebelas sumber pembaruan, dan `journal` termasuk.** Ini pertama kalinya
> jurnal disebut dengan namanya sejak naskah 11 — naskah 12 melewatkannya
> sepenuhnya (**G-9**), naskah 15 menjaganya lewat kata pengganti. ⚠️ Tapi
> menyebutnya sebagai **sumber taksiran keadaan** membuka pertanyaan yang
> **C-3** ([#21](../../issues/21)) ajukan: kalau jurnal dipakai menaksir
> `Stress`, apa yang terjadi ketika isinya menandakan krisis? Jalur eskalasinya
> masih belum ada.

> ⚠️ **`location` sebagai sumber rutin** — dan izin lokasi tetap tidak pernah
> didaftarkan (**E-93**). Lihat [#80](../../issues/80).
