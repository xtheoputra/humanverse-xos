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
| Tulis | `POST`/`PATCH` **domain** menerima header `Idempotency-Key` — `[A-Za-z0-9_.:=-]{1,128}`, telanjang atau sebagai sf-string bertanda kutip (`"…"`, bentuk draf IETF; keduanya kunci yang sama). Kunci yang sama mengembalikan hasil yang sama — status **pertama** dan sumber daya yang ditulisnya **dibaca ulang saat itu**, bertanda `Idempotent-Replayed: true`; sumber daya yang sudah dihapus → `404`. Kunci yang sama dengan permintaan **lain** → `422 idempotency_key_reused`; saat permintaan pertama masih berjalan → `409 idempotency_in_progress` + `Retry-After`. Hanya hasil 2xx yang diingat (24 jam, **rujukan** — bukan isi: E-171), kuncinya **milik pengguna** — kunci yang sama dari dua pengguna tidak saling memutar ulang — dan tiap pengguna paling banyak **1.000 kunci baru per 24 jam** (`429`, [K-24](../docs/KEPUTUSAN-DIDELEGASIKAN.md)). **Tidak** untuk `/auth/*`: jawabannya memuat token, dan memutar ulang jawaban berarti menyimpan token mentah ([K-21](../docs/KEPUTUSAN-DIDELEGASIKAN.md)) — `refresh` yang diulang dengan token yang sama tetap **pemakaian ulang**. `PATCH /me/profile` idempoten dengan sendirinya. ✅ **Diterapkan Sprint 2 (E-165)**: `platform.Idempoten`, dan `tests/unit/test_idempotensi_terpasang.py` menolak rute tulis domain yang tidak menerimanya |
| Halaman | `?limit=` (maks 100, bawaan 50) + `?cursor=`; balasan `{ items, next_cursor }` — `next_cursor` `null` di halaman terakhir. Kursor **keyset** `(waktu, id)`, opak bagi klien, dan milik **daftar asalnya**; kursor rusak — atau dari daftar lain — → `400 invalid_cursor`. Daftar tanpa `?cursor=` di bawah ini membalas `{ items }`, dan ukurannya dibatasi **saat menulis** (goal · milestone · habit — K-24), tidak pernah dipotong diam-diam |
| Saringan `status` | tanpa `?status=` = **semua** status yang belum dihapus; `?status=active` di contoh bukan bawaan |
| Galat | `{ "error": { "code", "message", "details"? } }` |
| Kode | `400` bentuk salah · `401` belum masuk · `403` izin ditolak · `404` · `409` bentrok · `413` badan terlalu besar · `422` aturan bisnis · `429` batas laju |
| Bentuk masukan | **Ketat**, tidak dikoersi (E-170): bilangan bulat hanya angka JSON bulat (bukan `true`, `"3"`, `3.0`); boolean hanya `true`/`false`; tanggal hanya string `YYYY-MM-DD`; waktu hanya string ISO-8601 **berzona**; kolom desimal (`sleep_hours`) angka JSON, masuk dan keluar. Tanggal dan waktu di badan, kueri, **dan** jalur: `1900-01-01` … `2999-12-31` (waktu: dalam UTC). Selainnya → `400` |
| Ukuran badan | paling besar **1 MiB** → selainnya `413 payload_too_large`, sebelum autentikasi dan sebelum badan dibaca (K-24) |
| Batas laju | `429 rate_limited` **selalu** dengan header `Retry-After` (detik bulat). Empat kunci: per IP di seluruh `/v1/*` (IPv6 per /64) · per pengguna di rute bersesi · `register` + `login` per IP · `login` **gagal** per akun (batas laju, bukan penguncian — **B-42**). Angkanya variabel `HVX_RATE_LIMIT_*` — [`../apps/api`](../apps/api/README.md) |
| Galat validasi | `400 invalid_request`; `details` hanya `loc` · `msg` · `type` — **masukan tidak pernah dipantulkan** (sandi yang salah bentuk tidak dikirim balik). `loc` hanya memuat nama yang **dinyatakan api** — kunci tak dikenal dari klien menjadi `*` — dan `msg` bawaan dipakai hanya untuk jenis galat yang pesannya tidak mengutip masukan; selainnya `Nilai tidak sah.` (E-174) |

---

## Identity

```
POST   /auth/register        { email, password, display_name, timezone, consents }  → 201 { user, tokens }
POST   /auth/login           { email, password }                          → 200 { user, tokens }
POST   /auth/refresh         { refresh_token }                            → 200 { tokens }
POST   /auth/logout                                                       → 204
GET    /me                                                                → 200 { user, profile }
PATCH  /me/profile           { display_name?, timezone?, locale?, preferences? }
DELETE /me                   { password }        → 202 { deletion_scheduled_at }   ⏳ 6.5
POST   /me/restore                               → 200   (batal hapus, dalam 30 hari)   ⏳ 6.5
```

> ⏳ **`DELETE /me` dan `POST /me/restore` bukan bagian Sprint 1** — keduanya
> pintu masuk alur hapus akun enam tahap, tugas [`07`](07-BACKLOG-V0.md) 6.5.
> Semula tidak ditandai, jadi kontrak ini tampak menjanjikan rute yang tidak
> ada (tinjauan Sprint 1). Alur itu wajib mencabut semua sesi pengguna
> (`PenyimpanSesi.cabut_semua`): status akun hanya dibaca saat masuk dan saat
> penyegaran, jadi token akses yang sudah terbit hidup sampai kedaluwarsanya.

> 🔧 **`consents` ditambahkan 17 Sep 2026 (E-164), saat tugas 1.1 ditulis.**
> [`07`](07-BACKLOG-V0.md) 1.4 menuntut persetujuan dicatat **saat daftar** —
> termasuk `purpose` dan `kind='model_training'` — tetapi badan pendaftaran di
> atas tidak punya tempat untuk jawabannya:
>
> ```
> consents: { policy_version, terms: true, privacy: true,
>             model_training?: { granted, data_scopes[] } }   ← tidak dikirim = DITOLAK
> ```
>
> `terms` dan `privacy` wajib `true`. `model_training` persetujuan **tersendiri**
> yang ditolak tanpa mengurangi layanan ([#59](../../issues/59)); `granted: true`
> wajib menyebut `data_scopes`. Ketiga jawaban tercatat — penolakan juga.
> Teks kebijakan dan kosakata `purpose` tetap milik pemilik (#59 butir 2).

| Rute | Galat yang dijanjikan |
|---|---|
| `register` | `400` bentuk salah — sandi di luar **15–128** karakter, timezone bukan nama IANA, medan tak dikenal · `409 email_taken` · `422 consent_required` · `422 password_rejected` + `details.reason` (`context` · `repetitive` · `sequential`) · `429` |
| `login` | `401 invalid_credentials` — **sama persis** untuk sandi salah dan email tak terdaftar · `403 account_not_active` · `429` per IP, dan per akun sesudah jatah login gagalnya habis — juga dengan sandi yang benar, juga bagi email tak terdaftar, dan bagi tiap ejaan yang basis data anggap email yang sama (huruf besar-kecil, juga Unicode: `vİctim@` = `victim@`) |
| `refresh` | `401 invalid_refresh_token` — token segar **berotasi**; token bekas yang dipakai lagi **mencabut seluruh sesi**; akun yang tidak lagi `active` → sesinya dicabut |
| rute bersesi | `401 unauthenticated` + `WWW-Authenticate: Bearer` — token palsu, kedaluwarsa, dan dicabut dijawab sama · `429` per pengguna |
| `PATCH /me/profile` | `400` untuk medan tak dikenal dan `null` eksplisit — tidak diabaikan diam-diam |

---

## Goals & habits

```
GET    /goals                ?status=active&limit=&cursor=      → { items, next_cursor }
POST   /goals                { id?, title, description?, domain?, parent_id?, target_date? }   → 201
GET    /goals/{id}                            → memuat milestones[]
GET    /goals/{id}/tree                       → goal + children[] bersarang — satu kueri   🔧 2.1
PATCH  /goals/{id}           { title?, status?, target_date? }
DELETE /goals/{id}                            → 204 (soft delete)

POST   /goals/{id}/milestones { id?, title, position?, due_date? }   → 201
PATCH  /milestones/{id}       { status?, title?, due_date? }

GET    /habits               ?status=active&for_date=     → { items }; dengan for_date, tiap habit membawa day{}   🔧 2.2
POST   /habits               { id?, title, period, target_count, schedule?, goal_id?, adaptive_tiers? }
PATCH  /habits/{id}
DELETE /habits/{id}

POST   /habits/{id}/completions  { for_date, status, tier_used?, note? }   → 201
DELETE /habits/{id}/completions/{for_date}                                 → 204
GET    /habits/{id}/streak       → { current, longest, completion_rate_30d }
```

> 🔧 **`GET /goals/{id}/tree` ditambahkan 24 Sep 2026 (E-168), saat tugas 2.1
> ditulis.** [`07`](07-BACKLOG-V0.md) 2.1 menuntut *“pohon goal 3 tingkat terbaca
> dalam satu query”*, tetapi tidak satu rute pun di atas yang mengembalikan
> pohon — `GET /goals/{id}` hanya memuat milestone, dan klien yang ingin pohon
> terpaksa meminta goal satu per satu (N+1 lewat jaringan, bukan lewat basis
> data). Kini satu rute, satu CTE rekursif; kedalaman paling banyak **10
> tingkat**, ditegakkan **saat menulis** (`422 goal_tree_too_deep`) supaya
> pohon tidak pernah dipotong diam-diam saat dibaca.
>
> | Rute | Galat yang dijanjikan |
> |---|---|
> | `POST /goals` | `409 already_exists` (`id` buatan klien yang sudah ada) · `422 parent_not_found` (induk tidak ada, terhapus, atau milik pengguna lain — ketiganya sama; juga induk yang **sedang** dihapus serentak — E-172) · `422 goal_tree_too_deep` · `422 goal_limit_reached` (1.000 goal hidup per pengguna — K-24) · `400` bila `parent_id == id` |
> | `PATCH /goals/{id}` | `400` untuk medan di luar tiga di atas — **`parent_id` tidak bisa diubah**, jadi lingkaran tidak bisa terbentuk · `status: achieved` mengisi `achieved_at`, status lain mengosongkannya |
> | `DELETE /goals/{id}` | anak goal naik menjadi **akar** — sama dengan hapus-keras `spec/01` (`ON DELETE SET NULL (parent_id)`) — dan habit yang menautnya **dilepas** (`goal_id` → `null`, sama dengan `ON DELETE SET NULL (goal_id)`; E-172). Menghapus goal yang sudah dihapus → `404`: goal itu tidak ada lagi |
> | `…/milestones` · `/milestones/{id}` | `404` untuk goal terhapus; `status: done` mengisi `completed_at`; `id` buatan klien yang sudah ada → `409 already_exists`; `422 milestone_limit_reached` (100 per goal — K-24) |

> 🔧 **Bentuk habit yang ditegakkan (spec/07 2.2, 24 Sep 2026)** — semula hanya
> tersirat di contoh `spec/01`:
>
> | Medan | Aturan | Kenapa |
> |---|---|---|
> | `target_count` | `day` → tepat **1** · `week` → 1–7 · `month` → 1–31 | satu tanggal satu penyelesaian (`UNIQUE (habit_id, for_date)`): *“3× sehari”* tidak bisa dicatat, *“8× seminggu”* tidak pernah terpenuhi |
> | `schedule` | `{ weekdays?: [1..7] unik & terurut (ISO, 1 = Senin), time?: "HH:MM" }`; `weekdays` **hanya** untuk `period: day` | habit mingguan dihitung per periode, bukan per hari |
> | `adaptive_tiers` | paling banyak 5: `[{ label, minutes? }]`, indeks 0 = versi penuh (naskah 4 §34) | |
> | `PATCH` | paduan `period` × `target_count` × `schedule` diperiksa terhadap **baris tersimpan** → `422 invalid_habit` | badan `{period: "day"}` sah sendiri, tidak sah untuk habit `week`/3 |
> | `goal_id` | goal tidak ada / **dihapus** / milik pengguna lain → `422 goal_not_found` | FK komposit saja tidak melihat hapus-lunak — goal terhapus dulu bisa ditaut (E-172) |
> | jumlah | paling banyak **500** habit hidup per pengguna → `422 habit_limit_reached` (K-24) | `GET /habits` membalas SEMUANYA — dulu memotong di 500 tanpa tanda |
> | `DELETE` | hapus-lunak; menghapus habit yang sudah dihapus → `404` | beda dengan `DELETE …/completions/{for_date}`, yang menunjuk **keadaan** tanggal itu, bukan sumber daya |

> `POST .../completions` memakai `UNIQUE (habit_id, for_date)`. Kirim ulang
> tanggal yang sama mengembalikan **200 dengan baris yang sudah ada**, bukan
> `409` — pencatatan habit dari perangkat luring harus selalu aman diulang.
>
> 🔧 **Ditegakkan 24 Sep 2026 (spec/07 2.3):** baris lama dikembalikan **apa
> adanya**, dan **sebelum** aturan apa pun diperiksa ulang — ulangan identik
> sesudah tier habit dikurangi tetap `200`, bukan `422` (E-173); ulangan tidak
> menimpa; mengganti status berarti `DELETE` lalu `POST`. Habit `archived`
> tetap menerima catatan — pencatatan mundur untuk hari sebelum diarsipkan. `DELETE …/completions/{for_date}` juga idempoten (`204` walau tanggal
> itu tidak tercatat). `for_date` adalah tanggal lokal **perangkat**, jadi
> batasnya bukan zona profil: tanggal ditolak (`422 for_date_in_future`) hanya
> bila **belum terjadi di mana pun di Bumi** (UTC+14). `tier_used` bilangan
> bulat ≥ 0 yang wajib di dalam `adaptive_tiers` habit itu — di luarnya
> **selalu** `422 invalid_tier`, berapa pun angkanya (E-170: dulu `3` menjadi
> `422`, `7` menjadi `400`) — dan tidak boleh menyertai `skipped` (`400`).
>
> 🔧 **Arti `GET /habits/{id}/streak` (spec/07 2.4, 24 Sep 2026)** — semula
> hanya nama medan:
>
> | | |
> |---|---|
> | satuan | **periode** habit: hari · minggu ISO (Senin–Minggu) · bulan kalender. Periode **terpenuhi** bila tanggal `done`/`partial` di dalamnya ≥ `target_count` |
> | tanggal | **`for_date`** apa adanya — tidak pernah diturunkan dari `completed_at`, dan tidak digeser saat pengguna pindah zona |
> | hari ini | menurut `profiles.timezone` **saat ini**, dari jam basis data; periode yang belum berakhir tidak memutus rentetan; `for_date` sesudah hari ini (perangkat di zona lebih timur) tetap dihitung |
> | `skipped` | netral — tidak menambah, tidak memutus, tidak masuk penyebut. **Per kejadian**: tiap `skipped` memaafkan satu kali dari target periodenya — minggu bertarget 2 dengan satu `done` + satu `skipped` dimaafkan, bukan gagal (E-173) |
> | `schedule.weekdays` | hari di luarnya bukan hari habit itu — dilewati |
> | `current` · `longest` | periode terpenuhi berturut-turut — yang masih hidup · yang terpanjang |
> | `completion_rate_30d` | periode terpenuhi ÷ periode jatuh tempo yang bersinggungan dengan 30 hari terakhir — **`null`** bila belum ada satu pun yang jatuh tempo. **Awal habit** = tanggal lokal habit dibuat: periode yang dimulai sebelumnya hanya dihitung bila **terpenuhi** (catatan mundur dihargai; hari sebelum habit ada tidak menjadi "gagal" — E-173) |
> | `paused` | riwayat jeda tidak disimpan (spec/01 tidak punya kolomnya): masa jeda dihitung seperti hari biasa — batas yang diakui |
>
> ⚠️ Menyeberang garis tanggal ke timur melompati satu tanggal kalender;
> rentetan harian putus di sana kecuali tanggal itu dicatat mundur (`for_date`
> boleh tanggal lampau).

---

## Catatan harian

```
GET    /checkins             ?from=&to=
PUT    /checkins/{for_date}  { energy?, focus?, sleep_hours?, note? }   → upsert: 201 baru · 200 diganti
GET    /moods                ?from=&to=&limit=&cursor=     → { items, next_cursor }
POST   /moods                { id?, valence, label?, note?, occurred_at? }   → 201
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
>
> 🔧 **`PATCH` dan `DELETE /journal/{id}` menjangkau memorinya (spec/07 3.6).**
> Tiap jurnal melahirkan satu memori episodik (scope `journal_raw`). Menyunting
> jurnal mengganti isi memori itu, dan menghapusnya **mengosongkan** memori itu
> — keduanya di transaksi yang sama dengan jurnalnya; titik vektornya
> diselaraskan pekerja sesudah commit. `DELETE` sendiri tetap hapus-lunak
> (`deleted_at`): isi jurnal tersimpan sampai akun dihapus — **C-31**, milik
> pemilik.

> 🔧 **`PUT /checkins/{for_date}` = GANTI, bukan tambal (spec/07 2.5, 24 Sep
> 2026).** Badan adalah check-in tanggal itu: medan yang tidak dikirim menjadi
> kosong — dua `PUT` yang sama selalu menghasilkan baris yang sama, apa pun
> isinya sebelumnya (idempoten dengan sendirinya; `Idempotency-Key` tidak
> dijanjikan untuk `PUT`) — termasuk `updated_at`: `PUT` yang identik dengan
> baris tersimpan tidak menulis apa pun (E-176). Satu pernyataan `INSERT … ON CONFLICT (user_id,
> for_date) DO UPDATE` — `PUT` serentak tidak bisa menyisipkan baris kedua.
> `sleep_hours` angka JSON dengan satu angka desimal (`numeric(3,1)`): `7.25`
> **ditolak** `400`, tidak dibulatkan diam-diam; `"7.5"` (string) juga `400`, dan
> jawabannya angka `7.5`, bukan string (E-170). `for_date` mengikuti aturan penyelesaian habit
> (`422 for_date_in_future` hanya bila belum terjadi di mana pun).
> `GET /checkins`: `from` dan `to` dikirim **bersama** (inklusif, paling lebar
> 366 tanggal, terbaru dulu); tanpa keduanya — 31 check-in terakhir.
>
> 🔧 **`GET /habits?for_date=` ditambahkan 24 Sep 2026 (E-169), saat 2.2 dan
> 2.7 ditulis.** 2.2 menuntut *“tier turun saat energi rendah”*, dan layar 2.7
> menandai habit selesai **hari ini** — tidak satu rute pun yang menjawab
> *“habit mana yang sudah selesai tanggal ini, dan tier mana yang disarankan”*
> tanpa N+1 permintaan. Dengan `for_date`, tiap habit membawa
> `day: { for_date, completion, energy, suggested_tier }` — `energy` ikut
> sebagai **alasan** tier yang disarankan (Explainable AI naskah 4 §29).
> Pemetaan energi → tier: **K-23** (naskah 4 §34).
>
> 🔧 **Mood (spec/07 2.6, 24 Sep 2026).** `occurred_at` **wajib berzona waktu**
> (`2026-09-24T06:30` tanpa zona adalah jam yang berbeda di tiap negara → `400`),
> boleh lampau, dan tidak boleh lebih dari 5 menit di depan jam basis data
> (`422 occurred_at_in_future`). `GET /moods`: `from` inklusif, `to`
> **eksklusif**, keduanya berzona; kursor keyset `(occurred_at, id)` — mood yang
> dicatat mundur masuk di tempatnya tanpa menggeser halaman berikutnya.

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
PUT    /privacy/permissions/{subject_type}/{subject_id}/{scope}  { action, decision, expires_at? }
POST   /privacy/export       → 202 { export_id }   (async, tautan sekali pakai)
GET    /privacy/export/{id}  → 200 { status, download_url?, expires_at? }
DELETE /privacy/data/{category}                    → 202
```

> 🔧 **`{subject_type}` ditambahkan 17 Sep 2026 (E-163), saat mesin izin 1.5
> ditulis.** Kunci unik `permissions` di [`01`](01-DATABASE-SCHEMA.md) adalah
> `(user_id, subject_type, subject_id, scope, action)`. Nama agent
> (`^[a-z][a-z0-9-]{2,39}$`, [`05`](05-AGENT-CONTRACTS.md)) dan id integrasi
> bisa sama — tanpa `subject_type`, `PUT` tidak bisa menunjuk satu baris.
> `decision: ask` = kembali bertanya. Rutenya datang bersama layar 6.4.
>
> Ini menerjemahkan layar Privacy Center naskah 5 §26 menjadi endpoint.
> **`GET /privacy/summary` sengaja mengembalikan jumlah baris, bukan isinya** —
> layar itu untuk menjawab *"apa yang kamu tahu tentang saya"*, dan jawabannya
> harus bisa dibaca tanpa menumpahkan seluruh data ke layar.
