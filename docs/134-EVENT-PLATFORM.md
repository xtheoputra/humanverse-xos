# 134 — §7.3–§7.5 Event Streaming, Envelope & Schema Registry

> Berkas ini merekam kata pemilik apa adanya (naskah kesebelas, 3 Sep 2026).
> Koreksi dan keraguan ada di [`99-CATATAN-AUDIT.md`](99-CATATAN-AUDIT.md).

---

## §7.3 — Event Streaming Platform

```
User
 ├── habit.completed      ├── outfit.selected
 ├── workout.completed    ├── goal.created
 ├── mood.logged          └── journal.created
 ├── sleep.completed
```

```
habit.completed
      │
      ├── Analytics
      ├── Behavior Model
      ├── Recommendation
      ├── Notification
      └── Memory
```

> Satu event dapat digunakan **banyak sistem tanpa coupling langsung**.

> ✅ Ketujuh event **dua segmen** — memperkuat penutupan **#38**. Tiga naskah
> berturut-turut sekarang memakai format yang sama.

---

## §7.4 — Canonical Event Envelope

```json
{
  "event_id": "evt_123",
  "event_type": "habit.completed",
  "version": 1,
  "occurred_at": "2026-09-03T08:00:00Z",
  "actor":    { "type": "user", "id": "user_123" },
  "source":   { "service": "habit-service" },
  "data":     { "habit_id": "habit_456" },
  "metadata": { "correlation_id": "corr_789" }
}
```

> Kenapa penting? **Karena 5 tahun kemudian kita masih harus memahami event
> lama.** Maka `event_type` + `schema_version` harus **selalu** ada.

---

> ⭐ **`actor: { type, id }` adalah perbaikan nyata.** Naskah 5 dan spesifikasi
> V0 memakai `user_id` datar, yang diam-diam mengandaikan setiap event berasal
> dari manusia. Dengan `actor.type`, event yang dihasilkan **agent** bisa
> dibedakan dari event yang dihasilkan **orang** — dan itu justru yang paling
> dibutuhkan begitu agent mulai menulis (aturan E di
> [`../spec/02`](../spec/02-ERD.md)) dan begitu Behavior Model belajar dari
> event (kalau tidak dibedakan, model akan belajar dari tebakannya sendiri).
>
> ⭐ `metadata.correlation_id` juga baru, dan itu yang menyambungkan satu
> permintaan pengguna dengan seluruh pohon eksekusi agent
> (`agent_runs.parent_run_id`).
>
> ⚠️ **Tetapi dua field hilang** dibanding [`../spec/03`](../spec/03-EVENT-CONTRACTS.md):
>
> | Field | Gunanya |
> |---|---|
> | `idempotency_key` | mencegah event ganda saat aplikasi luring menyinkron ulang |
> | `recorded_at` | membedakan *kapan terjadi* dari *kapan masuk sistem* — wajib untuk data susulan dari wearable |
>
> Keduanya ditambahkan justru untuk menutup celah bagian **D**. Envelope
> terbaik adalah gabungan keduanya. Lihat butir **E-65**.
>
> ⚠️ Nama field juga bergeser: `data` (di sini) vs `payload` (naskah 5 & spec),
> dan `version` vs `schema_version` — padahal kalimat penjelasnya sendiri
> menyebut **`schema_version`**.

---

## §7.5 — Event Schema Registry

```
events/
├── habit/     ├── created.v1 · completed.v1 · skipped.v1
├── health/    ├── sleep.completed.v1 · workout.completed.v1
├── lifestyle/ ├── outfit.selected.v1 · purchase.created.v1
└── goals/     └── created.v1 · completed.v1
```

Setiap schema memiliki:

```
owner · version · compatibility · producer · consumers · sensitivity
```

> ⭐ **`sensitivity` di metadata schema mengikat §7.2 ke pipeline** — itu yang
> membuat klasifikasi data bukan sekadar dokumen. Dan **`compatibility`**
> adalah field yang membuat janji *Backward-compatible* (naskah 10) bisa
> diperiksa mesin.
>
> ⚠️ `consumers` yang ditulis di schema berarti produser harus tahu siapa
> pemakainya — kebalikan dari semangat *"tanpa coupling langsung"* di §7.3.
> Lebih aman kalau daftar itu **dihasilkan** dari langganan, bukan ditulis
> tangan.
