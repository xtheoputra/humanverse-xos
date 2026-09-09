# 04 — API Contracts (V0)

> ⚠️ **Bukan kata pemilik** — lihat [`README.md`](README.md).

REST, JSON, awalan **`/v1`**. Autentikasi `Authorization: Bearer <access_token>`.

> 🔧 **Diselaraskan 9 September 2026 (dari `/api/v1`).** Ini menuntaskan janji
> yang tercatat di komentar penutup [#38](../../issues/38) — *“yang menyimpang
> justru `spec/04` yang saya tulis `/api/v1/…`; itu bagian saya, akan
> diselaraskan”* — dan janji itu tidak pernah dijalankan. Standar penamaan
> pemilik sendiri ([`../docs/101`](../docs/101-L22-ENGINEERING-STANDARDS.md)
> Layer 22) menetapkan `/v1/fashion/outfits`, dan sensus atas seluruh `docs/`
> menemukan **111 rute `/v1/…` di 12 naskah, dan NOL `/api/v1`**.
> Endpoint di bawah ditulis tanpa awalan, jadi hanya baris ini yang berubah.

---

## Aturan lintas endpoint

| Hal | Aturan |
|---|---|
| Waktu | ISO-8601 UTC dengan `Z`. Tanggal lokal pengguna sebagai `YYYY-MM-DD`. |
| Id | uuid string. **Klien boleh membuat id sendiri** (dukungan luring). |
| Tulis | `POST`/`PATCH` menerima header `Idempotency-Key`; kunci yang sama mengembalikan hasil yang sama. |
| Halaman | `?limit=` (maks 100) + `?cursor=`; balasan memuat `next_cursor`. |
| Galat | `{ "error": { "code", "message", "details"? } }` |
| Kode | `400` bentuk salah · `401` belum masuk · `403` izin ditolak · `404` · `409` bentrok · `422` aturan bisnis · `429` batas laju |

---

## Identity

```
POST   /auth/register        { email, password, display_name, timezone }  → 201 { user, tokens }
POST   /auth/login           { email, password }                          → 200 { user, tokens }
POST   /auth/refresh         { refresh_token }                            → 200 { tokens }
POST   /auth/logout                                                       → 204
GET    /me                                                                → 200 { user, profile }
PATCH  /me/profile           { display_name?, timezone?, locale?, preferences? }
DELETE /me                   { password }        → 202 { deletion_scheduled_at }
POST   /me/restore                               → 200   (batal hapus, dalam 30 hari)
```

---

## Goals & habits

```
GET    /goals                ?status=active&cursor=
POST   /goals                { id?, title, description?, domain?, parent_id?, target_date? }
GET    /goals/{id}                            → memuat milestones[]
PATCH  /goals/{id}           { title?, status?, target_date? }
DELETE /goals/{id}                            → 204 (soft delete)

POST   /goals/{id}/milestones { title, position?, due_date? }
PATCH  /milestones/{id}       { status?, title?, due_date? }

GET    /habits               ?status=active
POST   /habits               { id?, title, period, target_count, schedule?, goal_id?, adaptive_tiers? }
PATCH  /habits/{id}
DELETE /habits/{id}

POST   /habits/{id}/completions  { for_date, status, tier_used?, note? }   → 201
DELETE /habits/{id}/completions/{for_date}                                 → 204
GET    /habits/{id}/streak       → { current, longest, completion_rate_30d }
```

> `POST .../completions` memakai `UNIQUE (habit_id, for_date)`. Kirim ulang
> tanggal yang sama mengembalikan **200 dengan baris yang sudah ada**, bukan
> `409` — pencatatan habit dari perangkat luring harus selalu aman diulang.

---

## Catatan harian

```
GET    /checkins             ?from=&to=
PUT    /checkins/{for_date}  { energy?, focus?, sleep_hours?, note? }   → upsert
GET    /moods                ?from=&to=&cursor=
POST   /moods                { id?, valence, label?, note?, occurred_at? }
GET    /journal              ?from=&to=&cursor=      → tanpa body, hanya ringkasan
GET    /journal/{id}                                 → dengan body
POST   /journal              { id?, title?, body, occurred_at? }
PATCH  /journal/{id}
DELETE /journal/{id}
GET    /activities           ?kind=&from=&to=&cursor=
POST   /activities           { id?, kind, occurred_at, duration_seconds?, payload? }
```

> `GET /journal` **tidak** mengembalikan `body`. Daftar jurnal sering dimuat
> di layar ringkasan; mengirim seluruh isi tulisan pribadi ke sana adalah
> kebocoran yang tidak perlu.

---

## AI

```
GET    /conversations                    ?cursor=
POST   /conversations                    { title? }
GET    /conversations/{id}/messages      ?cursor=
POST   /conversations/{id}/messages      { content }   → 202, balasan lewat stream
GET    /conversations/{id}/stream        → SSE: token, tool_call, done
```

Balasan `POST /messages`:

```json
{
  "message_id": "…",
  "agent_run_id": "…",
  "status": "processing"
}
```

Peristiwa SSE `done`:

```json
{
  "content": "…",
  "confidence": 0.71,
  "rationale": ["Tidur 5j 40m tiga malam terakhir", "Workout terlewat 2x"],
  "agent_run_id": "…",
  "cost_usd": 0.0021
}
```

> `confidence` dan `rationale` ikut di **setiap** balasan AI, bukan hanya
> rekomendasi — itu penerapan Confidence Layer (§19) dan Explainable AI
> (naskah 4 §29) di lapisan API, bukan sekadar di basis data.

---

## Rekomendasi

```
GET    /recommendations              ?status=pending&domain=
POST   /recommendations/{id}/feedback { action, reason?, outcome? }   → 201
POST   /recommendations/{id}/shown                                    → 204
```

---

## Privacy Center

```
GET    /privacy/summary      → apa yang diketahui sistem, per kategori + jumlah baris
GET    /privacy/permissions  → izin per agent
PUT    /privacy/permissions/{subject_id}/{scope}  { action, decision, expires_at? }
POST   /privacy/export       → 202 { export_id }   (async, tautan sekali pakai)
GET    /privacy/export/{id}  → 200 { status, download_url?, expires_at? }
DELETE /privacy/data/{category}                    → 202
```

> Ini menerjemahkan layar Privacy Center naskah 5 §26 menjadi endpoint.
> **`GET /privacy/summary` sengaja mengembalikan jumlah baris, bukan isinya** —
> layar itu untuk menjawab *"apa yang kamu tahu tentang saya"*, dan jawabannya
> harus bisa dibaca tanpa menumpahkan seluruh data ke layar.
