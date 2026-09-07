# 155 — §9.4–§9.6 Behavior & Preference, Human State & Context Engine

> Berkas ini merekam kata pemilik apa adanya (naskah ketigabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §9.4 — Layer 1: Behavior & Preference Intelligence

> Berasal dari fase 5 dan 7. HumanVerse harus mengetahui:

```
What does the user do?
What does the user prefer?
What does the user avoid?
What does the user repeatedly choose?
What changes over time?
```

**Behavior Model**

```
Observed behavior
      ↓
Patterns
      ↓
Behavior representation
```

**Preference Model**

```
Choices + Feedback + Context + History
      ↓
Preference representation
```

Penting:

> ## Preference ≠ permanent identity.

Contoh: user biasanya suka **coffee**, tetapi ketika **late night**
preferensinya mungkin berubah. Maka:

```
Preference(user, item, context, time)
```

lebih tepat daripada:

```
User likes item
```

---

> ⭐⭐ **Ini jawaban langsung untuk C-13 / [#50](../../issues/50), dan ia datang
> dari pemilik sendiri.** Naskah 9 Pillar 4 menetapkan *Identity Memory*
> sebagai **permanen** dengan contoh *"User is consistently committed to
> strength training"* — klaim tentang **siapa** seseorang, disimpan selamanya.
> Butir C-13 mengusulkan agar ia tidak permanen.
>
> `Preference(user, item, context, time)` melakukan lebih dari itu: ia membuat
> preferensi **bukan sifat orang** melainkan **fungsi dari konteks dan waktu**.
> Sebuah preferensi tidak bisa "permanen" kalau salah satu argumennya adalah
> waktu. Digabung dengan decay §9.9, klaim permanen naskah 9 gugur.
>
> ⚠️ Yang **belum** ada dari usul C-13: pengguna bisa **melihat dan membantah**
> kesimpulan itu. Itu `Edit` yang hilang dari Privacy Center — **E-74** /
> [#64](../../issues/64).

> ⚠️ **`avoid` adalah sinyal yang belum pernah punya tempat.** *"What does the
> user avoid?"* bukan sekadar kebalikan dari *prefer*: menolak sekali berbeda
> dari tidak pernah memilih. Tabel `recommendation_feedback` di
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) mencatat penerimaan; penolakan
> berulang perlu dibedakan dari ketiadaan data — kalau tidak, agent akan terus
> menyarankan hal yang sudah ditolak sepuluh kali.

---

## §9.5 — Layer 2: Human State Representation

**Human State Vector:**

```
Energy
Focus
Mood
Stress
Motivation
Physical readiness
Cognitive load
Social energy
Financial pressure
Goal momentum
```

> Representasinya **bukan angka absolut**:

```json
{
  "energy":     { "value": 0.64, "confidence": 0.78 },
  "focus":      { "value": 0.41, "confidence": 0.62 },
  "motivation": { "value": 0.72, "confidence": 0.70 }
}
```

> Jadi HumanVerse **selalu menyimpan value + confidence**. Ini sangat penting.

---

> ⭐⭐ **Bentuk `{value, confidence}` per field adalah jawaban penyimpanan yang
> dicari A-19 / [#2](../../issues/2) sejak naskah 4.** `human_states.metrics`
> dibuat `jsonb` di [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) justru supaya
> daftar field boleh berubah tanpa migrasi — dan bentuk di atas muat langsung.
> Lebih dari itu: ia menaikkan **H-14** (Confidence Layer) dari *"setiap
> kesimpulan"* menjadi *"setiap field, satu per satu"*, yang lebih ketat.

> 🛑 **HumanState versi ketiga: 8 → 7 → 10 field, dan `mood` kembali.**
>
> | | Field |
> |---|---|
> | naskah 4 §14 | energy · **mood** · focus · stress · motivation · socialEnergy · physicalReadiness · cognitiveLoad — **8** |
> | naskah 5 §14 | sama, **tanpa `mood`** — **7** |
> | naskah 13 §9.5 | delapan naskah 4 **+ financial pressure + goal momentum** — **10** |
>
> Butir **E-34** mencatat hilangnya `mood` sebagai kemungkinan besar
> **disengaja dan benar**: mood punya event sendiri (`mood.logged`) dan tabel
> sendiri (`mood_entries`) — ia **dilaporkan pengguna**, bukan **ditaksir
> sistem**. Sekarang ia ditaksir lagi.
>
> Keduanya bisa hidup bersama, tetapi hanya kalau ditulis bahwa keduanya
> **benda berbeda**:
>
> ```
> mood_entries.value          → yang DIKATAKAN pengguna     (fakta)
> human_states.metrics.mood   → yang DITAKSIR sistem        (taksiran + confidence)
> ```
>
> Dan yang kedua tidak boleh ditampilkan sebagai yang pertama. Lihat **E-80**.

> ⚠️ **`Financial pressure` adalah field paling sensitif yang pernah masuk
> HumanState** — ia taksiran tentang tekanan keuangan seseorang, disimpan
> harian. Klasifikasi data naskah 11 menempatkan *financial behavior* di
> **Level 3**, dan §8.12 naskah 12 menuntut proteksi lebih kuat untuk data
> finansial. Sebuah field turunan membawa sensitivitas sumbernya; ia tidak
> menjadi biasa hanya karena sudah jadi angka 0–1.

---

## §9.6 — Layer 3: Context Engine

State tidak cukup. Kita perlu tahu:

```
WHO · WHEN · WHERE · WHAT · WHY · WITH WHOM · UNDER WHAT CONDITIONS
```

Context:

```
Time · Location · Weather · Calendar · Activity · Environment
Social context · Goals · Recent events · Historical patterns
```

Contoh:

```
User:
Energy 0.42

Context:
Monday · 07:30 · Rain · Poor sleep · Important meeting at 10:00
```

Rekomendasi terbaik mungkin bukan *"Workout berat"*, melainkan:

> *"Workout ringan 20 menit pagi ini, kemudian simpan energi untuk meeting."*

---

> ⭐ **Contoh ini adalah pembelaan terbaik untuk seluruh arsitektur.** Ia
> menunjukkan sesuatu yang tidak bisa dicapai satu panggilan LLM di atas satu
> tabel: keputusannya berubah bukan karena datanya berubah, melainkan karena
> **ada rapat jam 10**. Itu argumen §9.2 dalam satu kalimat.

> ⚠️ **B-14 (kegagalan senyap) belum tertutup, tapi obatnya sudah ada di
> naskah ini.** Sepuluh sinyal konteks berarti sepuluh cara pipeline bisa mati
> diam-diam; rekomendasi tetap keluar, hanya jadi salah.
>
> §9.32 mewajibkan setiap inference membawa `confidence` dan `sources`, dan
> §9.33 melarang AI terlalu yakin di bawah ambang. Itu **membuat kegagalan
> tidak lagi senyap** — asalkan satu aturan ditulis, dan ia belum ditulis:
>
> > **Sinyal yang hilang harus MENURUNKAN `confidence`, bukan diabaikan.**
>
> Tanpa aturan itu, sistem yang kehilangan data tidur akan tetap melaporkan
> `energy: {value: 0.64, confidence: 0.78}` seolah tidak terjadi apa-apa.
> Lihat [#26](../../issues/26).

> ⚠️ **Weather dan Calendar adalah tool, bukan sumber data internal** (**H-11**),
> dan keduanya **tidak ada di V0** ([`../spec/05`](../spec/05-AGENT-CONTRACTS.md)
> menempatkan `weather.get` dan `calendar.get` di registry V2). Context Engine
> versi V0 karena itu berjalan di atas empat sinyal, bukan sepuluh: waktu,
> aktivitas, goals, dan recent events. Itu bukan masalah — tapi contoh di atas
> tidak bisa dijalankan sampai V2.
