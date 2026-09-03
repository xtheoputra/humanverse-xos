# 120 — Pillar 10–12: Adaptive Intervention, Explainability & Experiment Framework

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## Pillar 10 — Adaptive Intervention Research

> Ini salah satu **eksperimen utama**.

Reminder jam 18:00. Kalau user sedang meeting, AI mengubah:

```
Meeting ends
     ↓
Energy check
     ↓
Reminder
```

Kita mengukur:

```
completion · annoyance · timing quality
```

> ⭐ **`annoyance` sebagai metrik resmi** adalah salah satu keputusan paling
> sehat di sembilan naskah. Ia adalah metrik penjaga (*guardrail*) yang selama
> ini hilang dari Layer 34: *completion* bisa dinaikkan dengan mengganggu orang
> lebih sering, dan hanya *annoyance* yang bisa menghentikannya.
>
> ⚠️ Bagaimana `annoyance` diukur belum ditulis. Yang bisa diukur tanpa
> bertanya: pengingat ditutup tanpa dibaca, notifikasi dimatikan, aplikasi
> dibuka lalu langsung ditutup.

---

## Pillar 11 — AI Explainability Lab

> Setiap rekomendasi harus bisa dijelaskan.

Contoh — *Tidur lebih awal*:

```
Sleep decreased this week.
Workout completion decreased.
Morning energy declined.

Confidence: Medium
```

> Jangan hanya: **"AI thinks."**

> ⭐ Perhatikan `Confidence: Medium` ikut ditampilkan **kepada pengguna**, bukan
> hanya disimpan. Konsisten dengan aturan Confidence Layer: *low confidence →
> tanya pengguna*.
>
> ℹ️ Bentuk ini sudah punya tempatnya: kolom `rationale jsonb` dan
> `confidence` di tabel `recommendations`
> ([`../spec/01`](../spec/01-DATABASE-SCHEMA.md)), dan ikut di setiap balasan
> AI di [`../spec/04`](../spec/04-API-CONTRACTS.md).

---

## Pillar 12 — Human Experiment Framework

> **User menjadi ilmuwan bagi dirinya sendiri.**

```
Hypothesis:  Earlier sleep may improve focus.
Durasi:      14 hari
Variable:    Sleep · Focus · Mood

Output:      Observation · Trend · Confidence
```

> ## Bukan klaim ilmiah universal.

> ⭐ Kalimat penutup itu penting, dan keluarannya sudah dipilih dengan benar:
> **Observation, Trend, Confidence** — tidak ada kata *Conclusion* maupun
> *Proof*. Bandingkan dengan naskah 4 §36 yang masih memuat *Conclusion* di
> rantainya.
>
> ⚠️ Butir **A-21** tetap terbuka: **14 hari tanpa kelompok kontrol** dan
> dengan perancu (musim, beban kerja, motivasi awal) belum punya **ambang**
> kapan sistem menolak menyimpulkan. `Confidence` di keluaran adalah tempat
> yang tepat untuk ambang itu — angkanya yang belum ada.
