# 115 — Pillar 1: Behavior Foundation Model (BFM)

> Berkas ini merekam kata pemilik apa adanya (naskah kesembilan, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

> Ini adalah model khusus untuk memahami **pola perilaku pengguna**.
>
> ## Tujuannya: memprediksi pola, bukan menghakimi pengguna.

---

## Input & Output

| Input | Output |
|---|---|
| Habit history | Habit completion probability |
| Sleep | Best intervention timing |
| Mood | Pattern summary |
| Workout | Confidence score |
| Calendar | |
| Context | |

---

## Contoh

```
Goal: Workout 4x/week

Prediction:
  Friday workout completion: 34%

Reason:
  - Sleep debt
  - Late office schedule
  - Historical pattern
```

> **Catatan pemilik:** ini adalah **estimasi probabilistik** berdasarkan data
> pengguna, **bukan kepastian**.

---

## Struktur model

```
Behavior Encoder
        │
        ▼
Time Series Encoder
        │
        ▼
Context Fusion
        │
        ▼
Prediction Head
        │
        ▼
Confidence Estimator
```

> ⭐ **Confidence Estimator sebagai lapisan terakhir model**, bukan tempelan di
> lapisan aplikasi — ini penerapan Confidence Layer (naskah 5 §19) yang paling
> dalam sejauh ini.

---

## Dataset internal

```
behavior_events      mood_events
habit_events         calendar_events
sleep_events         context_snapshots
```

---

## Evaluasi

| Metric | Target |
|---|---|
| Precision | tinggi |
| Recall | tinggi |
| Calibration | baik |
| False Alarm | rendah |

---

> ⭐ **`Calibration` adalah metrik yang paling tepat untuk model ini** dan baru
> pertama kali muncul di sembilan naskah. Kalau model berkata *"34 %"*, maka
> dari seratus kejadian serupa kira-kira 34 yang benar terjadi. Tanpa
> kalibrasi, angka probabilitas hanya hiasan.
>
> ⚠️ Keempat target masih kata sifat (*tinggi*, *baik*, *rendah*), belum angka.
> Untuk model yang keluarannya dipakai mengatur pengingat orang, **False Alarm
> yang \"rendah\"** perlu batas yang bisa gagal — kalau tidak, tidak ada versi
> model yang pernah bisa ditolak.
>
> 🛑 **Keenam dataset di atas belum ada satu pun.** `behavior_events` dan
> `habit_events` baru terisi setelah V0 dipakai; `sleep_events` dan
> `calendar_events` **tidak ada di V0 sama sekali** (tidak ada integrasi tidur
> maupun kalender); `context_snapshots` belum pernah punya tabel. Lihat butir
> **B-21** dan **E-58**.
