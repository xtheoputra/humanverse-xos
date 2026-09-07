# 183 — §11.28–§11.31 Human Approval Center, Transparency, Agent Memory & Learning

> Berkas ini merekam kata pemilik apa adanya (naskah kelimabelas, 7 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §11.28 — Human Approval Center

> HumanVerse membutuhkan satu UI: **Action Center**

```
Pending Actions

┌───────────────────────────────┐
│ Add calendar event            │
│ AI Study — 19:30              │
│ Risk: Low                     │
│                               │
│ [Approve] [Reject] [Edit]     │
└───────────────────────────────┘
```

Untuk high-risk, tampilkan: **What · Why · Agent · Data Used · Impact · Cost ·
Reversible?**

---

> ⭐⭐⭐ **`[Edit]` — kata yang hilang sejak naskah 12, kembali di tombol
> ketiga.**
>
> Butir **E-74** ([#64](../../issues/64)) melacak `Edit` yang hilang dari
> Privacy Center §8.36: naskah 4 §43 memberi *View · Edit · Export · Delete ·
> Revoke*; naskah 12 memberi delapan kata kerja **tanpa satu pun cara
> memperbaiki**. Sejak itu empat hal menunggu tempatnya — kesimpulan Identity
> Memory, bobot utility §9.25, kesimpulan Understanding Engine, dan pengamatan
> sensor yang konsisten salah.
>
> Di sini `Edit` berdiri sejajar dengan Approve dan Reject, dan §11.10 sudah
> menyatakan rencana wajib `editable`. Dua preseden dalam satu naskah.
>
> ⚠️ Tapi keduanya untuk **aksi dan rencana** — hal yang belum terjadi.
> Yang masih belum punya tombol adalah **kesimpulan tentang diri pengguna**,
> yang sudah terlanjur tersimpan. Itu tetap [#64](../../issues/64).

> ⭐⭐ **Tujuh baris untuk high-risk adalah bentuk paling lengkap dari
> penjelasan aksi di lima belas naskah** — dan tiga di antaranya belum pernah
> ada di daftar mana pun: **Impact**, **Cost**, dan **Reversible?**
>
> `Cost` khususnya: pengguna melihat berapa biaya sebuah aksi **sebelum**
> menyetujuinya. Itu menutup jarak antara Budget Engine §11.18 (yang menghentikan
> agent) dan pengguna (yang selama ini tidak pernah melihat angkanya).
>
> `Reversible?` menjadikan §11.27 terlihat di antarmuka — pengguna diberi
> tahu apa yang bisa dibatalkan **sebelum** memutuskan, bukan setelah.

> ⚠️ **"Pending Actions" menyiratkan aksi yang menunggu tanpa batas waktu.**
> Sebuah reminder yang disetujui tiga hari kemudian sudah tidak berguna. Setiap
> aksi tertunda butuh **kedaluwarsa**, dan apa yang terjadi saat lewat
> (dibatalkan diam-diam, atau ditanyakan lagi) perlu ditulis.

---

## §11.29 — Agent Transparency

> Jangan tampilkan chain-of-thought mentah.

```
Action:      Schedule study session
Reason:      Fits your available time and current goal.
Data used:   Calendar · Goal · Recent study history
Confidence:  0.89
```

---

> ⭐ **Bentuk ini identik dengan §8.24 dan §10.25** — *Action/Reason/Data
> used/Confidence* sejajar dengan *Recommendation/Evidence/Observation/Source/
> Confidence*. Tiga naskah, satu bentuk. Salah satu dari sedikit hal yang tidak
> bergeser, dan ia memperkuat usul di [#64](../../issues/64): `rationale` di
> `audit_logs` sebaiknya **rantai berstruktur**, bukan teks bebas.

> ⚠️ **`Confidence: 0.89` adalah angka ketiga tanpa ambang.** §8.24 memberi
> `0.72`, §9.15 memberi `0.71`, §10.24 memberi `0.97` vs `0.38`. Enam naskah
> mewajibkan mekanismenya; **nol memberi ambangnya** ([#34](../../issues/34)).
> Untuk aksi, ambang itu lebih mendesak daripada untuk kesimpulan: sistem yang
> **bertindak** pada keyakinan 0,4 berbeda dari sistem yang **menyarankan**
> pada keyakinan 0,4.

---

## §11.30 — Agent Memory

```
Agent → Memory Policy → Allowed Memory
```

**Fashion Agent**

```
CAN READ:     ✓ wardrobe  ✓ style preferences  ✓ fashion history
CANNOT READ:  ✗ financial data  ✗ private conversations
              ✗ unrelated documents
```

---

> ⭐ **Konsisten dengan §8.15 dan dengan `memory.read`/`memory.write` yang
> kembali di §11.5.** Tiga larangannya juga memetakan ke tiga scope yang
> [`../spec/05`](../spec/05-AGENT-CONTRACTS.md) aturan 6 larang untuk agent
> `third_party` (`journal`, `finance`, `health`).

> ⚠️ **`private conversations` menyentuh jurnal tanpa menamainya** — sama
> seperti `private documents` §11.6. Setelah **G-9** (naskah 12 nol kali
> menyebut jurnal), ini kali kedua jurnal dijaga lewat kata pengganti.
> Menamainya lebih baik: kata pengganti tidak bisa ditegakkan validator.

---

## §11.31 — Agent Learning

> Agent **tidak boleh** langsung mengubah behavior model berdasarkan satu
> tindakan.

```
Action → Outcome → Feedback → Evidence → Preference Update → Model Update
```

Contoh — rekomendasi *white sneakers*, user **rejected**. Tidak berarti *user
tidak suka white sneakers*. **Butuh repeated evidence.**

---

> ⭐⭐ **Ini kali keempat berturut-turut prinsip anti-karakterisasi muncul, dan
> kali ini pada penolakan.**
>
> | Naskah | Bentuknya |
> |---|---|
> | 13 §9.4 | *Preference ≠ permanent identity* |
> | 13 §9.35 | *"jangan langsung menyimpulkan **User malas**"* |
> | 14 §10.6 | *"jangan langsung: **User sedang malas**"* dari kamera |
> | **15 §11.31** | *"rejected ≠ tidak suka"* |
>
> Empat naskah, empat konteks, satu arah. Ini prinsip paling stabil di seluruh
> proyek — lebih stabil daripada daftar agent, manifest, atau penomoran mana
> pun.

> ⭐ **`Evidence` sebagai langkah terpisah antara Feedback dan Preference
> Update** adalah gerbang yang sama dengan `Importance Scoring` §9.8: tidak
> semua umpan balik naik menjadi perubahan preferensi.

> ⚠️ **Tapi ada asimetri yang belum ditulis, dan ia menentukan.** Menolak
> sesuatu **satu kali** bisa berarti tujuh hal (§9.35: waktu, energi,
> kesulitan, konteks, lingkungan, konflik tujuan) — jadi butuh bukti berulang.
> Menerima sesuatu satu kali juga tidak berarti banyak.
>
> Yang **tidak** simetris: pengguna yang menolak hal yang sama **sepuluh kali**
> sudah jelas, dan sistem yang tetap menyarankannya adalah sistem yang tidak
> mendengarkan. §9.4 menyebut *"What does the user **avoid**?"* sebagai sinyal
> tersendiri, dan tabel `recommendation_feedback`
> [`../spec/01`](../spec/01-DATABASE-SCHEMA.md) mencatat penerimaan — penolakan
> berulang perlu dibedakan dari **ketiadaan data**, atau agent akan mengulang
> saran yang sudah ditolak.
>
> Aturan yang bisa ditulis sekarang: **bukti untuk berhenti menyarankan lebih
> murah daripada bukti untuk mulai menyarankan.** Salah arah lebih mahal di
> satu sisi.
