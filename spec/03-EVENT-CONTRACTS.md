# 03 — Event Contracts

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).
> Menutup tiga celah bagian **D** audit: versi skema, urutan, dan idempotensi.

---

## Envelope

Setiap event memakai amplop yang sama. Yang berbeda hanya `payload`.

```json
{
  "id":              "018f...",
  "event_type":      "habit.completed",
  "schema_version":  1,
  "user_id":         "u_123",
  "occurred_at":     "2026-09-03T06:30:00Z",
  "recorded_at":     "2026-09-03T06:30:04Z",
  "source":          "app",
  "idempotency_key": "habit:9c2f:2026-09-03",
  "subject_type":    "habit",
  "subject_id":      "9c2f...",
  "payload":         { "status": "done", "tier_used": 0 }
}
```

| Field | Aturan |
|---|---|
| `event_type` | `<domain>.<past_tense_verb>`, huruf kecil. Sekali dipakai, **tidak pernah** diganti nama. |
| `schema_version` | Naik hanya saat perubahan **melanggar** kontrak. Menambah field opsional **tidak** menaikkannya. |
| `occurred_at` | Kapan kejadian **terjadi** menurut pengguna. Boleh masa lalu. |
| `recorded_at` | Kapan server menerimanya. **Selalu** `>= occurred_at` kecuali jam klien salah. |
| `idempotency_key` | Dibuat **klien**, deterministik. Unik per pengguna. |
| `source` | `app` · `agent` · `integration` · `backfill` |

---

## Tiga aturan yang menentukan

**1 · Idempotensi.** Kunci dibuat dari isi yang menentukan identitas kejadian,
bukan dari waktu kirim:

```
habit.completed   →  habit:<habit_id>:<for_date>
mood.logged       →  mood:<user_id>:<occurred_at menit>
journal.created   →  journal:<journal_id>
goal.completed    →  goal:<goal_id>
```

Kirim ulang menghasilkan `UNIQUE` violation yang **ditelan sebagai sukses**,
bukan galat. Ini yang membuat aplikasi luring aman menyinkron ulang.

**2 · Urutan.** Consumer **tidak boleh** mengandalkan urutan datang. Urutan
kebenaran adalah `occurred_at`; `recorded_at` hanya untuk memantau
keterlambatan. Event yang datang terlambat (backfill mingguan dari wearable)
harus tetap benar hasilnya.

**3 · Versi.** Consumer wajib mengabaikan field yang tidak dikenalnya.
Perubahan yang melanggar kontrak **menerbitkan `event_type` baru**
(`workout.completed.v2`), bukan menaikkan versi diam-diam.

---

## 22 event — 21 dari naskah 5 §7 + 1 usulan

Tanda ✅ = dipakai V0. Sisanya kontraknya ditulis sekarang, implementasinya
menyusul — supaya nama dan bentuknya tidak berubah nanti.

| Event | V0 | Payload |
|---|---|---|
| `habit.created` | ✅ | `{title, period, target_count}` |
| `habit.completed` | ✅ | `{status, tier_used?, note?}` |
| `habit.skipped` | ✅ | `{reason?}` |
| `mood.logged` | ✅ | `{valence, label?}` |
| `journal.created` | ✅ | `{word_count}` — **isi jurnal tidak pernah masuk event** |
| `goal.created` | ✅ | `{title, domain?, target_date?}` |
| `goal.completed` | ✅ | `{days_taken}` |
| `checkin.logged` | ✅ | `{energy?, focus?, sleep_hours?}` |
| `sleep.started` | | `{}` |
| `sleep.completed` | | `{duration_minutes, quality?}` |
| `workout.started` | | `{exercise_type}` |
| `workout.completed` | | `{duration, exercise_type}` |
| `meal.logged` | | `{meal_type, items[]}` |
| `outfit.selected` | | `{outfit_id}` |
| `outfit.worn` | | `{outfit_id, occasion?}` |
| `purchase.created` | | `{category, amount_minor, currency}` |
| `learning.started` | | `{subject}` |
| `learning.completed` | | `{subject, duration}` |
| `meeting.started` | | `{calendar_ref?}` |
| `meeting.completed` | | `{duration}` |
| `travel.started` | | `{destination?}` |
| `travel.completed` | | `{duration}` |

> `checkin.logged` **saya tambahkan** — Daily Check-in ada di V0 tetapi tidak
> punya event di daftar 21 naskah 5 §7. Tanpa itu, Behavior Engine tidak
> melihat salah satu sinyal harian paling padat. 🔧

> **`journal.created` sengaja hanya membawa `word_count`.** Isi jurnal tinggal
> di `journal_entries` yang tunduk pada permission scope. Event mengalir ke
> banyak consumer; menaruh isi jurnal di sana berarti membocorkannya ke semua
> yang mendengarkan.

---

## Consumer V0

| Consumer | Mendengarkan | Wajib? |
|---|---|---|
| **Behavior projector** | semua | ✅ wajib — kegagalannya menahan event |
| **Habit streak** | `habit.*` | ✅ wajib |
| **Memory extractor** | `journal.created`, `mood.logged` | boleh gagal & diulang |
| **Recommendation trigger** | `checkin.logged`, `habit.skipped` | boleh gagal |
| **Analytics** | semua | boleh gagal |

> Consumer yang "boleh gagal" wajib **idempoten**, karena akan diulang.
> Di V0 antreannya Redis Streams dengan consumer group; Kafka baru bila
> skalanya menuntut (naskah 5 §5).
